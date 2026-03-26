"""
PROMETHEUS Paper Trading Monitor & Reporter
=============================================
Automated performance monitoring and reporting for shadow (paper) trades.

Capabilities:
  - Reads shadow_trade_history, shadow_sessions, shadow_position_tracking
    from prometheus_learning.db
  - Computes per-session and per-symbol performance metrics
  - Generates structured reports (JSON dict or text summary)
  - Tracks win-rate, PnL, Sharpe, max-drawdown, avg hold-time, AI voter
    attribution, and symbol-level breakdowns
  - Provides a continuous monitor loop that checks for new closed trades
"""

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

LEARNING_DB = Path("prometheus_learning.db")
REPORTS_DIR = Path("paper_trading_reports")

TRADING_DAYS_PER_YEAR = 252


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class SymbolMetrics:
    symbol: str
    total_trades: int
    closed_trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    avg_pnl_pct: float
    best_trade_pct: float
    worst_trade_pct: float
    avg_hold_minutes: float
    asset_class: str


@dataclass
class SessionReport:
    session_id: str
    config_name: str
    started_at: str
    last_active: str
    starting_capital: float
    current_capital: float
    total_return_pct: float
    total_trades: int
    closed_trades: int
    open_positions: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    avg_pnl_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    profit_factor: float
    avg_hold_minutes: float
    top_ai_voters: List[str]
    symbol_breakdown: List[SymbolMetrics]
    report_generated: str


@dataclass
class AggregateReport:
    total_sessions: int
    active_sessions: int
    all_time_trades: int
    all_time_closed: int
    all_time_win_rate: float
    all_time_pnl: float
    best_session: str
    worst_session: str
    avg_sharpe: float
    avg_max_drawdown: float
    top_symbols: List[str]
    top_ai_voters: List[str]
    sessions: List[SessionReport]
    report_generated: str


# ---------------------------------------------------------------------------
# Core monitor class
# ---------------------------------------------------------------------------
class PaperTradingMonitor:
    """
    Reads shadow-trading data from prometheus_learning.db and produces
    structured performance reports.
    """

    def __init__(self, db_path: str = str(LEARNING_DB)):
        self.db_path = db_path
        REPORTS_DIR.mkdir(exist_ok=True)
        logger.info(f"PaperTradingMonitor initialised (db={db_path})")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_session_report(self, session_id: str) -> Optional[SessionReport]:
        """Generate a detailed report for a single shadow session."""
        conn = self._connect()
        if conn is None:
            return None
        try:
            return self._build_session_report(conn, session_id)
        finally:
            conn.close()

    def generate_aggregate_report(self) -> AggregateReport:
        """Generate a report spanning all shadow sessions."""
        conn = self._connect()
        if conn is None:
            return self._empty_aggregate()
        try:
            return self._build_aggregate(conn)
        finally:
            conn.close()

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Return all currently-open shadow positions."""
        conn = self._connect()
        if conn is None:
            return []
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT symbol, entry_price, quantity, confidence,
                       ai_components, timestamp, target_price, stop_loss,
                       session_id, trade_id
                FROM shadow_trade_history
                WHERE status = 'OPEN'
                ORDER BY timestamp DESC
            """)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def save_report(self, report) -> str:
        """Persist a report to disk as JSON. Returns the file path."""
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        name = "aggregate" if isinstance(report, AggregateReport) else getattr(report, "session_id", "unknown")
        path = REPORTS_DIR / f"report_{name}_{ts}.json"
        with open(path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)
        logger.info(f"Report saved → {path}")
        return str(path)

    def get_status(self) -> Dict[str, Any]:
        conn = self._connect()
        if conn is None:
            return {"name": "Paper Trading Monitor", "active": False, "reason": "db_unavailable"}
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM shadow_trade_history")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='OPEN'")
            open_ct = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM shadow_sessions")
            sessions = cur.fetchone()[0]
            return {
                "name": "Paper Trading Monitor",
                "active": True,
                "total_shadow_trades": total,
                "open_positions": open_ct,
                "sessions": sessions,
                "reports_dir": str(REPORTS_DIR),
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _connect(self) -> Optional[sqlite3.Connection]:
        if not Path(self.db_path).exists():
            logger.warning(f"DB not found: {self.db_path}")
            return None
        try:
            return sqlite3.connect(self.db_path)
        except Exception as exc:
            logger.error(f"DB connect failed: {exc}")
            return None

    def _build_session_report(self, conn: sqlite3.Connection, session_id: str) -> Optional[SessionReport]:
        cur = conn.cursor()

        # Session metadata
        cur.execute("SELECT * FROM shadow_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        if row is None:
            return None
        cur.execute("PRAGMA table_info(shadow_sessions)")
        sess_cols = [c[1] for c in cur.fetchall()]
        sess = dict(zip(sess_cols, row))

        # All trades for this session
        cur.execute("""
            SELECT * FROM shadow_trade_history
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))
        trade_cols_desc = cur.description
        trade_cols = [c[0] for c in trade_cols_desc]
        trades = [dict(zip(trade_cols, r)) for r in cur.fetchall()]

        return self._compute_report(sess, trades)

    def _build_aggregate(self, conn: sqlite3.Connection) -> AggregateReport:
        cur = conn.cursor()

        # All sessions
        cur.execute("SELECT * FROM shadow_sessions ORDER BY started_at DESC")
        sess_cols_desc = cur.description
        sess_cols = [c[0] for c in sess_cols_desc]
        sessions_raw = [dict(zip(sess_cols, r)) for r in cur.fetchall()]

        # All trades
        cur.execute("SELECT * FROM shadow_trade_history ORDER BY timestamp")
        trade_cols_desc = cur.description
        trade_cols = [c[0] for c in trade_cols_desc]
        all_trades = [dict(zip(trade_cols, r)) for r in cur.fetchall()]

        # Group trades by session
        trades_by_session: Dict[str, list] = {}
        for t in all_trades:
            sid = t.get("session_id", "unknown")
            trades_by_session.setdefault(sid, []).append(t)

        session_reports: List[SessionReport] = []
        for sess in sessions_raw:
            sid = sess.get("session_id", "")
            trades = trades_by_session.get(sid, [])
            rpt = self._compute_report(sess, trades)
            if rpt:
                session_reports.append(rpt)

        # Aggregate stats
        closed = [t for t in all_trades if t.get("status") == "CLOSED" and t.get("pnl") is not None]
        total_pnl = sum(t["pnl"] for t in closed)
        wins = [t for t in closed if t["pnl"] > 0]
        win_rate = len(wins) / len(closed) if closed else 0.0

        # Top symbols by PnL
        sym_pnl: Dict[str, float] = {}
        for t in closed:
            sym_pnl[t["symbol"]] = sym_pnl.get(t["symbol"], 0) + t["pnl"]
        top_symbols = sorted(sym_pnl, key=sym_pnl.get, reverse=True)[:5]

        # Top AI voters (most frequently used)
        voter_counts: Dict[str, int] = {}
        for t in all_trades:
            comps = t.get("ai_components", "[]")
            try:
                names = json.loads(comps) if isinstance(comps, str) else comps
                for name in names:
                    voter_counts[name] = voter_counts.get(name, 0) + 1
            except Exception:
                pass
        top_voters = sorted(voter_counts, key=voter_counts.get, reverse=True)[:5]

        sharpes = [r.sharpe_ratio for r in session_reports if r.sharpe_ratio != 0]
        drawdowns = [r.max_drawdown_pct for r in session_reports if r.max_drawdown_pct != 0]

        best_sess = max(session_reports, key=lambda r: r.total_pnl).session_id if session_reports else ""
        worst_sess = min(session_reports, key=lambda r: r.total_pnl).session_id if session_reports else ""

        active = [s for s in sessions_raw if s.get("status") == "active"]

        return AggregateReport(
            total_sessions=len(sessions_raw),
            active_sessions=len(active),
            all_time_trades=len(all_trades),
            all_time_closed=len(closed),
            all_time_win_rate=round(win_rate, 4),
            all_time_pnl=round(total_pnl, 2),
            best_session=best_sess,
            worst_session=worst_sess,
            avg_sharpe=round(np.mean(sharpes), 3) if sharpes else 0.0,
            avg_max_drawdown=round(np.mean(drawdowns), 3) if drawdowns else 0.0,
            top_symbols=top_symbols,
            top_ai_voters=top_voters,
            sessions=session_reports,
            report_generated=datetime.utcnow().isoformat(),
        )

    def _compute_report(self, sess: dict, trades: list) -> Optional[SessionReport]:
        session_id = sess.get("session_id", "")
        starting_cap = float(sess.get("starting_capital", 100000))
        current_cap = float(sess.get("current_capital", starting_cap))

        closed = [t for t in trades if t.get("status") == "CLOSED" and t.get("pnl") is not None]
        open_trades = [t for t in trades if t.get("status") == "OPEN"]

        pnls = [float(t["pnl"]) for t in closed]
        pnl_pcts = [float(t["pnl_pct"]) for t in closed if t.get("pnl_pct") is not None]

        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        win_rate = len(wins) / len(pnls) if pnls else 0.0
        total_pnl = sum(pnls)
        avg_pnl_pct = np.mean(pnl_pcts) if pnl_pcts else 0.0

        # Sharpe from trade PnL %
        sharpe = 0.0
        if len(pnl_pcts) > 1:
            arr = np.array(pnl_pcts)
            mean_r = np.mean(arr)
            std_r = np.std(arr, ddof=1)
            if std_r > 0:
                sharpe = round((mean_r / std_r) * np.sqrt(TRADING_DAYS_PER_YEAR), 3)

        # Max drawdown from cumulative PnL
        max_dd = 0.0
        if pnls:
            cum = np.cumsum(pnls)
            peak = np.maximum.accumulate(cum)
            dd = (peak - cum) / np.where(peak == 0, 1, np.abs(peak))
            max_dd = round(float(np.max(dd)) * 100, 2)

        # Profit factor
        gross_win = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = round(gross_win / gross_loss, 2) if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)

        # Avg hold time
        hold_mins = []
        for t in closed:
            if t.get("timestamp") and t.get("exit_time"):
                try:
                    entry = datetime.fromisoformat(t["timestamp"])
                    exit_ = datetime.fromisoformat(t["exit_time"])
                    hold_mins.append((exit_ - entry).total_seconds() / 60)
                except Exception:
                    pass
        avg_hold = round(np.mean(hold_mins), 1) if hold_mins else 0.0

        # AI voter frequency
        voter_counts: Dict[str, int] = {}
        for t in trades:
            comps = t.get("ai_components", "[]")
            try:
                names = json.loads(comps) if isinstance(comps, str) else comps
                for name in names:
                    voter_counts[name] = voter_counts.get(name, 0) + 1
            except Exception:
                pass
        top_voters = sorted(voter_counts, key=voter_counts.get, reverse=True)[:5]

        # Per-symbol breakdown
        sym_trades: Dict[str, list] = {}
        for t in trades:
            sym_trades.setdefault(t.get("symbol", "?"), []).append(t)

        sym_metrics = []
        for sym, st in sorted(sym_trades.items()):
            s_closed = [t for t in st if t.get("status") == "CLOSED" and t.get("pnl") is not None]
            s_pnls = [float(t["pnl"]) for t in s_closed]
            s_pcts = [float(t["pnl_pct"]) for t in s_closed if t.get("pnl_pct") is not None]
            s_wins = [p for p in s_pnls if p > 0]
            sm = SymbolMetrics(
                symbol=sym,
                total_trades=len(st),
                closed_trades=len(s_closed),
                wins=len(s_wins),
                losses=len(s_pnls) - len(s_wins),
                win_rate=round(len(s_wins) / max(len(s_pnls), 1), 4),
                total_pnl=round(sum(s_pnls), 2),
                avg_pnl_pct=round(float(np.mean(s_pcts)), 3) if s_pcts else 0.0,
                best_trade_pct=round(max(s_pcts), 3) if s_pcts else 0.0,
                worst_trade_pct=round(min(s_pcts), 3) if s_pcts else 0.0,
                avg_hold_minutes=0.0,
                asset_class=st[0].get("asset_class", "unknown") if st else "unknown",
            )
            sym_metrics.append(sm)

        total_return = ((current_cap - starting_cap) / starting_cap * 100) if starting_cap else 0.0

        return SessionReport(
            session_id=session_id,
            config_name=sess.get("config_name", ""),
            started_at=sess.get("started_at", ""),
            last_active=sess.get("last_active", ""),
            starting_capital=starting_cap,
            current_capital=current_cap,
            total_return_pct=round(total_return, 2),
            total_trades=len(trades),
            closed_trades=len(closed),
            open_positions=len(open_trades),
            wins=len(wins),
            losses=len(losses),
            win_rate=round(win_rate, 4),
            total_pnl=round(total_pnl, 2),
            avg_pnl_pct=round(float(avg_pnl_pct), 3),
            sharpe_ratio=sharpe,
            max_drawdown_pct=max_dd,
            profit_factor=profit_factor,
            avg_hold_minutes=avg_hold,
            top_ai_voters=top_voters,
            symbol_breakdown=sym_metrics,
            report_generated=datetime.utcnow().isoformat(),
        )

    def _empty_aggregate(self) -> AggregateReport:
        return AggregateReport(
            total_sessions=0, active_sessions=0, all_time_trades=0,
            all_time_closed=0, all_time_win_rate=0, all_time_pnl=0,
            best_session="", worst_session="", avg_sharpe=0,
            avg_max_drawdown=0, top_symbols=[], top_ai_voters=[],
            sessions=[], report_generated=datetime.utcnow().isoformat(),
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_instance: Optional[PaperTradingMonitor] = None


def get_paper_monitor() -> PaperTradingMonitor:
    global _instance
    if _instance is None:
        _instance = PaperTradingMonitor()
    return _instance
