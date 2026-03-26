"""
PROMETHEUS Dead-End Memory & Trade Rejection Logger
=====================================================
Tracks WHY trades were rejected or failed, so the system doesn't
repeat the same mistakes.  This is the "self-verification" layer
from the Opus prompt, but grounded in actual trading outcomes.

Records:
  - Rejected trades and the reasons
  - Failed trades with loss amounts
  - Common failure patterns per symbol/strategy
  - Automatically computes a "toxicity score" per symbol/strategy combo

The trading pipeline queries this before entering a trade:
  "Has this exact setup failed before? How many times? What was the avg loss?"

If the dead-end score is high enough, the trade is blocked.
"""

import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

DB_PATH = Path("prometheus_learning.db")


class DeadEndMemory:
    """
    Persistent memory of trade rejections and failures.
    Uses SQLite for durability across restarts.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
        logger.info(f"DeadEndMemory initialized: {self.db_path}")

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dead_end_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL DEFAULT 'unknown',
                    action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    outcome TEXT NOT NULL DEFAULT 'rejected',
                    pnl_pct REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 0.0,
                    z_score REAL DEFAULT 0.0,
                    regime TEXT DEFAULT '',
                    market_data_json TEXT DEFAULT '{}',
                    created_at REAL DEFAULT (strftime('%%s', 'now'))
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dead_end_symbol
                ON dead_end_memory (symbol, strategy, outcome)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dead_end_recent
                ON dead_end_memory (created_at DESC)
            """)
            conn.commit()

    # ──────────────────────────────────────────────────────────────────────
    # Recording
    # ──────────────────────────────────────────────────────────────────────

    def record_rejection(
        self,
        symbol: str,
        action: str,
        reason: str,
        strategy: str = "unknown",
        confidence: float = 0.0,
        z_score: float = 0.0,
        regime: str = "",
        market_data: Optional[Dict] = None,
    ):
        """Record a trade that was REJECTED before execution."""
        self._insert(
            symbol=symbol,
            action=action,
            reason=reason,
            strategy=strategy,
            outcome="rejected",
            pnl_pct=0.0,
            confidence=confidence,
            z_score=z_score,
            regime=regime,
            market_data=market_data,
        )
        logger.debug(f"Dead-end: rejected {action} {symbol} ({strategy}) — {reason}")

    def record_failure(
        self,
        symbol: str,
        action: str,
        reason: str,
        pnl_pct: float,
        strategy: str = "unknown",
        confidence: float = 0.0,
        z_score: float = 0.0,
        regime: str = "",
        market_data: Optional[Dict] = None,
    ):
        """Record a trade that was EXECUTED but LOST money."""
        self._insert(
            symbol=symbol,
            action=action,
            reason=reason,
            strategy=strategy,
            outcome="loss",
            pnl_pct=pnl_pct,
            confidence=confidence,
            z_score=z_score,
            regime=regime,
            market_data=market_data,
        )
        logger.debug(f"Dead-end: loss {action} {symbol} ({strategy}) — {pnl_pct:+.2f}% — {reason}")

    def record_stop_loss(
        self,
        symbol: str,
        action: str,
        pnl_pct: float,
        strategy: str = "unknown",
        regime: str = "",
    ):
        """Record a stop-loss hit."""
        self._insert(
            symbol=symbol,
            action=action,
            reason="stop_loss_hit",
            strategy=strategy,
            outcome="stop_loss",
            pnl_pct=pnl_pct,
            regime=regime,
        )

    def _insert(self, **kwargs):
        """Insert a record."""
        market_data = kwargs.pop("market_data", None) or {}
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO dead_end_memory
                    (timestamp, symbol, strategy, action, reason, outcome,
                     pnl_pct, confidence, z_score, regime, market_data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    kwargs.get("symbol", ""),
                    kwargs.get("strategy", "unknown"),
                    kwargs.get("action", ""),
                    kwargs.get("reason", ""),
                    kwargs.get("outcome", "rejected"),
                    kwargs.get("pnl_pct", 0.0),
                    kwargs.get("confidence", 0.0),
                    kwargs.get("z_score", 0.0),
                    kwargs.get("regime", ""),
                    json.dumps(market_data),
                ))
                conn.commit()
        except Exception as exc:
            logger.error(f"DeadEndMemory insert failed: {exc}")

    # ──────────────────────────────────────────────────────────────────────
    # Querying — should I avoid this trade?
    # ──────────────────────────────────────────────────────────────────────

    def get_toxicity_score(
        self,
        symbol: str,
        strategy: str = "unknown",
        action: str = "",
        lookback_hours: int = 168,  # 7 days
    ) -> Dict[str, Any]:
        """
        Compute a toxicity score for a symbol/strategy combo.

        Returns:
            {
                "score": 0.0-1.0 (higher = more toxic / avoid),
                "reject_count": N,
                "loss_count": N,
                "avg_loss_pct": -X.X,
                "total_loss_pct": -X.X,
                "recent_pattern": "string",
                "recommendation": "proceed" | "caution" | "block",
            }
        """
        cutoff = time.time() - (lookback_hours * 3600)
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                # Get all records for this symbol/strategy in window
                query = """
                    SELECT outcome, pnl_pct, reason, action, confidence
                    FROM dead_end_memory
                    WHERE symbol = ? AND created_at > ?
                """
                params: list = [symbol, cutoff]
                if strategy != "unknown":
                    query += " AND strategy = ?"
                    params.append(strategy)
                if action:
                    query += " AND action = ?"
                    params.append(action)

                rows = conn.execute(query, params).fetchall()

            if not rows:
                return {
                    "score": 0.0, "reject_count": 0, "loss_count": 0,
                    "avg_loss_pct": 0.0, "total_loss_pct": 0.0,
                    "recent_pattern": "no history",
                    "recommendation": "proceed",
                }

            reject_count = sum(1 for r in rows if r["outcome"] == "rejected")
            loss_rows = [r for r in rows if r["outcome"] in ("loss", "stop_loss")]
            loss_count = len(loss_rows)
            losses = [r["pnl_pct"] for r in loss_rows if r["pnl_pct"] < 0]
            avg_loss = float(sum(losses) / len(losses)) if losses else 0.0
            total_loss = float(sum(losses))

            # Toxicity formula:
            # - Each rejection adds 0.05
            # - Each loss adds 0.10
            # - Each stop-loss adds 0.15
            # - Larger losses amplify score
            score = 0.0
            score += reject_count * 0.05
            score += loss_count * 0.10
            stop_loss_count = sum(1 for r in rows if r["outcome"] == "stop_loss")
            score += stop_loss_count * 0.15
            # Loss magnitude amplifier
            if avg_loss < -2.0:
                score += 0.2
            elif avg_loss < -1.0:
                score += 0.1

            score = min(1.0, score)

            # Recommendation
            if score >= 0.6:
                rec = "block"
            elif score >= 0.3:
                rec = "caution"
            else:
                rec = "proceed"

            # Recent pattern
            recent_reasons = [r["reason"] for r in rows[-5:]]
            pattern = ", ".join(set(recent_reasons))

            return {
                "score": score,
                "reject_count": reject_count,
                "loss_count": loss_count,
                "stop_loss_count": stop_loss_count,
                "avg_loss_pct": avg_loss,
                "total_loss_pct": total_loss,
                "recent_pattern": pattern,
                "recommendation": rec,
            }

        except Exception as exc:
            logger.error(f"DeadEndMemory query failed: {exc}")
            return {
                "score": 0.0, "reject_count": 0, "loss_count": 0,
                "avg_loss_pct": 0.0, "total_loss_pct": 0.0,
                "recent_pattern": "error",
                "recommendation": "proceed",
            }

    def should_block_trade(
        self,
        symbol: str,
        strategy: str = "unknown",
        action: str = "",
        block_threshold: float = 0.6,
    ) -> Tuple[bool, str]:
        """
        Quick check: should this trade be blocked?
        Returns (blocked: bool, reason: str).
        """
        tox = self.get_toxicity_score(symbol, strategy, action)
        if tox["score"] >= block_threshold:
            return True, (
                f"Dead-end block: toxicity={tox['score']:.2f}, "
                f"{tox['loss_count']} losses (avg {tox['avg_loss_pct']:.1f}%), "
                f"{tox['reject_count']} rejections — {tox['recent_pattern']}"
            )
        return False, ""

    # ──────────────────────────────────────────────────────────────────────
    # Analytics
    # ──────────────────────────────────────────────────────────────────────

    def get_worst_symbols(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most toxic symbols."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                rows = conn.execute("""
                    SELECT symbol,
                           COUNT(*) as total,
                           SUM(CASE WHEN outcome IN ('loss','stop_loss') THEN 1 ELSE 0 END) as losses,
                           AVG(CASE WHEN pnl_pct < 0 THEN pnl_pct ELSE NULL END) as avg_loss,
                           SUM(CASE WHEN pnl_pct < 0 THEN pnl_pct ELSE 0 END) as total_loss
                    FROM dead_end_memory
                    GROUP BY symbol
                    ORDER BY total_loss ASC
                    LIMIT ?
                """, (limit,)).fetchall()
                return [
                    {
                        "symbol": r[0], "total_events": r[1],
                        "losses": r[2], "avg_loss": r[3] or 0,
                        "total_loss": r[4] or 0,
                    }
                    for r in rows
                ]
        except Exception as exc:
            logger.error(f"DeadEndMemory analytics failed: {exc}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Return memory status."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                total = conn.execute("SELECT COUNT(*) FROM dead_end_memory").fetchone()[0]
                losses = conn.execute(
                    "SELECT COUNT(*) FROM dead_end_memory WHERE outcome IN ('loss','stop_loss')"
                ).fetchone()[0]
                rejections = conn.execute(
                    "SELECT COUNT(*) FROM dead_end_memory WHERE outcome = 'rejected'"
                ).fetchone()[0]
            return {
                "name": "Dead-End Memory",
                "active": True,
                "total_records": total,
                "losses_recorded": losses,
                "rejections_recorded": rejections,
            }
        except Exception:
            return {"name": "Dead-End Memory", "active": False}


# Singleton
_dead_end_memory: Optional[DeadEndMemory] = None


def get_dead_end_memory() -> DeadEndMemory:
    """Get or create the singleton dead-end memory."""
    global _dead_end_memory
    if _dead_end_memory is None:
        _dead_end_memory = DeadEndMemory()
    return _dead_end_memory
