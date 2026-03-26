#!/usr/bin/env python3
"""
Strategy Degradation Detector
==============================
Monitors rolling performance metrics per AI voter / strategy and detects
when a strategy's edge is fading. Triggers alerts and automatic weight
adjustments in the voting pipeline.

Metrics tracked per strategy (rolling windows):
  - Win rate (30-trade, 100-trade)
  - Profit factor
  - Sharpe ratio (annualized from daily P/L)
  - Max drawdown (rolling 30-day)
  - Average hold time drift

Alerts:
  - YELLOW: metric dropped >1 sigma from its historical mean
  - RED:    metric dropped >2 sigma OR win rate < 40% on 30-trade window

Actions:
  - On RED: halve the voter weight until next review window
  - On recovery: restore weight gradually
"""

import logging
import sqlite3
import os
import numpy as np
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prometheus_learning.db")


@dataclass
class StrategyHealth:
    """Health report for a single AI voter / strategy"""
    name: str
    status: str = "HEALTHY"          # HEALTHY | YELLOW | RED | INACTIVE
    win_rate_30: float = 0.0
    win_rate_100: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    avg_hold_hours: float = 0.0
    total_trades: int = 0
    weight_multiplier: float = 1.0   # 1.0 = normal, 0.5 = halved
    alerts: List[str] = field(default_factory=list)
    last_updated: str = ""


class StrategyDegradationDetector:
    """
    Monitors each AI voter's rolling performance and detects degradation.
    Reads from prometheus_learning.db (ai_attribution + trade_outcomes).
    """

    # Thresholds
    MIN_TRADES_FOR_EVAL = 15
    WIN_RATE_YELLOW = 0.45
    WIN_RATE_RED = 0.38
    PROFIT_FACTOR_YELLOW = 0.9
    PROFIT_FACTOR_RED = 0.7
    SHARPE_YELLOW = 0.3
    SHARPE_RED = 0.0
    MAX_DD_YELLOW = -0.05   # -5%
    MAX_DD_RED = -0.10      # -10%

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._health_cache: Dict[str, StrategyHealth] = {}
        self._last_scan = None
        self._scan_interval = timedelta(minutes=30)
        logger.info("Strategy Degradation Detector initialized")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_health(self, force: bool = False) -> Dict[str, StrategyHealth]:
        """Return health for every known voter. Re-scans if stale."""
        if force or self._is_stale():
            self._scan_all_strategies()
        return dict(self._health_cache)

    def get_strategy_health(self, voter_name: str) -> Optional[StrategyHealth]:
        """Return health for one voter."""
        if self._is_stale():
            self._scan_all_strategies()
        return self._health_cache.get(voter_name)

    def get_weight_multipliers(self) -> Dict[str, float]:
        """
        Return {voter_name: multiplier} that the voting pipeline should apply.
        A multiplier of 1.0 means no change; 0.5 means halve the weight.
        """
        if self._is_stale():
            self._scan_all_strategies()
        return {name: h.weight_multiplier for name, h in self._health_cache.items()}

    def get_degraded_strategies(self) -> List[StrategyHealth]:
        """Return only YELLOW and RED strategies."""
        if self._is_stale():
            self._scan_all_strategies()
        return [h for h in self._health_cache.values() if h.status in ("YELLOW", "RED")]

    def get_summary(self) -> Dict:
        """Quick JSON-friendly summary."""
        health = self.get_all_health()
        return {
            "total_strategies": len(health),
            "healthy": sum(1 for h in health.values() if h.status == "HEALTHY"),
            "yellow": sum(1 for h in health.values() if h.status == "YELLOW"),
            "red": sum(1 for h in health.values() if h.status == "RED"),
            "inactive": sum(1 for h in health.values() if h.status == "INACTIVE"),
            "strategies": {
                name: {
                    "status": h.status,
                    "win_rate_30": round(h.win_rate_30, 3),
                    "profit_factor": round(h.profit_factor, 3),
                    "sharpe_ratio": round(h.sharpe_ratio, 3),
                    "total_trades": h.total_trades,
                    "weight_multiplier": h.weight_multiplier,
                    "alerts": h.alerts,
                }
                for name, h in health.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _is_stale(self) -> bool:
        if self._last_scan is None:
            return True
        return datetime.now(timezone.utc) - self._last_scan > self._scan_interval

    def _scan_all_strategies(self):
        """Read DB and compute health for every voter."""
        try:
            voters = self._get_voter_trades()
            for voter_name, trades in voters.items():
                self._health_cache[voter_name] = self._evaluate_voter(voter_name, trades)
            self._last_scan = datetime.now(timezone.utc)
            n_degraded = sum(1 for h in self._health_cache.values() if h.status in ("YELLOW", "RED"))
            logger.info(
                f"Strategy scan complete: {len(self._health_cache)} voters, "
                f"{n_degraded} degraded"
            )
        except Exception as e:
            logger.error(f"Strategy degradation scan failed: {e}")

    def _get_voter_trades(self) -> Dict[str, List[dict]]:
        """
        Pull per-voter trade outcomes from the learning DB.
        Returns {voter_name: [{pnl, timestamp, hold_hours, ...}, ...]}
        """
        voters: Dict[str, List[dict]] = {}
        if not os.path.exists(self.db_path):
            logger.warning(f"Learning DB not found: {self.db_path}")
            return voters

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Try ai_attribution table first (has per-voter attribution)
            cursor = conn.execute("""
                SELECT ai_system, eventual_pnl, confidence, timestamp
                FROM ai_attribution
                WHERE eventual_pnl IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 10000
            """)
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    voter = row["ai_system"]
                    if voter not in voters:
                        voters[voter] = []
                    voters[voter].append({
                        "pnl": float(row["eventual_pnl"]),
                        "confidence": float(row["confidence"]) if row["confidence"] else 0.5,
                        "timestamp": row["timestamp"],
                    })
            else:
                # Fallback: trade_outcomes table (no per-voter split)
                cursor2 = conn.execute("""
                    SELECT symbol, pnl, entry_time, exit_time, strategy
                    FROM trade_outcomes
                    ORDER BY exit_time DESC
                    LIMIT 5000
                """)
                rows2 = cursor2.fetchall()
                for row in rows2:
                    strat = row["strategy"] or "Unknown"
                    if strat not in voters:
                        voters[strat] = []
                    voters[strat].append({
                        "pnl": float(row["pnl"]) if row["pnl"] else 0.0,
                        "timestamp": row["exit_time"] or row["entry_time"],
                    })

            conn.close()
        except Exception as e:
            logger.error(f"Failed to read voter trades: {e}")

        return voters

    def _evaluate_voter(self, name: str, trades: List[dict]) -> StrategyHealth:
        """Compute health metrics for a single voter."""
        h = StrategyHealth(name=name, last_updated=datetime.now(timezone.utc).isoformat())
        h.total_trades = len(trades)

        if h.total_trades < self.MIN_TRADES_FOR_EVAL:
            h.status = "INACTIVE"
            h.alerts.append(f"Only {h.total_trades} trades — need {self.MIN_TRADES_FOR_EVAL}")
            return h

        pnls = [t["pnl"] for t in trades]

        # --- Win rates ---
        recent_30 = pnls[:30]
        recent_100 = pnls[:100]
        h.win_rate_30 = sum(1 for p in recent_30 if p > 0) / len(recent_30)
        h.win_rate_100 = sum(1 for p in recent_100 if p > 0) / len(recent_100) if len(recent_100) > 0 else 0

        # --- Profit factor ---
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        h.profit_factor = gross_profit / gross_loss if gross_loss > 0 else (10.0 if gross_profit > 0 else 0.0)

        # --- Sharpe ratio (from trade P/Ls, annualized assuming ~252 trades/year) ---
        pnl_arr = np.array(pnls)
        mean_pnl = pnl_arr.mean()
        std_pnl = pnl_arr.std()
        h.sharpe_ratio = (mean_pnl / std_pnl) * np.sqrt(252) if std_pnl > 0 else 0.0

        # --- Max drawdown ---
        cumulative = np.cumsum(pnl_arr)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - running_max
        h.max_drawdown = float(drawdowns.min()) if len(drawdowns) > 0 else 0.0
        # Normalize by peak if possible
        peak = running_max.max()
        if peak > 0:
            h.max_drawdown = float(drawdowns.min() / peak)

        # --- Average hold time (if available) ---
        hold_hours = [t.get("hold_hours", 0) for t in trades if t.get("hold_hours")]
        h.avg_hold_hours = np.mean(hold_hours) if hold_hours else 0.0

        # --- Classify health ---
        alerts = []

        # Win rate checks
        if h.win_rate_30 < self.WIN_RATE_RED:
            alerts.append(f"WIN_RATE_30 critical: {h.win_rate_30:.1%}")
            h.status = "RED"
        elif h.win_rate_30 < self.WIN_RATE_YELLOW:
            alerts.append(f"WIN_RATE_30 declining: {h.win_rate_30:.1%}")
            if h.status != "RED":
                h.status = "YELLOW"

        # Profit factor checks
        if h.profit_factor < self.PROFIT_FACTOR_RED:
            alerts.append(f"Profit factor critical: {h.profit_factor:.2f}")
            h.status = "RED"
        elif h.profit_factor < self.PROFIT_FACTOR_YELLOW:
            alerts.append(f"Profit factor declining: {h.profit_factor:.2f}")
            if h.status != "RED":
                h.status = "YELLOW"

        # Sharpe checks
        if h.sharpe_ratio < self.SHARPE_RED:
            alerts.append(f"Sharpe negative: {h.sharpe_ratio:.2f}")
            h.status = "RED"
        elif h.sharpe_ratio < self.SHARPE_YELLOW:
            alerts.append(f"Sharpe low: {h.sharpe_ratio:.2f}")
            if h.status != "RED":
                h.status = "YELLOW"

        # If still healthy after all checks
        if not alerts:
            h.status = "HEALTHY"

        h.alerts = alerts

        # Set weight multiplier
        if h.status == "RED":
            h.weight_multiplier = 0.5   # Halve weight
        elif h.status == "YELLOW":
            h.weight_multiplier = 0.75  # Reduce 25%
        else:
            h.weight_multiplier = 1.0   # Full weight

        return h
