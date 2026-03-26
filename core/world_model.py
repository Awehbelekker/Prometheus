"""
PROMETHEUS World Model
=======================
A simplified persistent representation of the market state that
integrates outputs from all subsystems:

  - Current REGIME (from HMM detector)
  - CORRELATIONS (from StatArb engine)
  - PERFORMANCE by strategy / symbol (from dead-end memory + trade history)
  - POSITION EXPOSURE (from broker)
  - KEY LEVELS (support/resistance from recent price action)

This is the "World Model" layer from the Opus AGI prompt, but
stripped to what actually delivers value in a live trading system.
No simulated physics or multi-dimensional state spaces — just
the information a trader needs to make a decision.

Updated every trading cycle. Persisted to SQLite so it survives restarts.
Other systems query the World Model instead of each re-computing
market state independently.
"""

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path("prometheus_learning.db")


@dataclass
class WorldState:
    """Snapshot of the market world at a point in time."""

    # Regime
    regime: str = "unknown"  # LOW_VOL_TRENDING / HIGH_VOL_CHOPPY / CRISIS_RISK_OFF
    regime_confidence: float = 0.0
    regime_strategy_weights: Dict[str, float] = field(default_factory=dict)

    # Broad market context
    sp500_trend: str = "neutral"  # bullish / bearish / neutral
    vix_level: float = 0.0
    market_breadth: float = 0.5  # 0 = all stocks down, 1 = all stocks up

    # Portfolio context
    portfolio_value: float = 0.0
    cash_available: float = 0.0
    open_positions: int = 0
    total_exposure_pct: float = 0.0  # % of portfolio in positions

    # Performance snapshot
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    win_rate_7d: float = 0.0
    best_strategy_7d: str = ""
    worst_strategy_7d: str = ""

    # Symbol-level intel
    symbol_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # e.g. {"BTC/USD": {"trend": "up", "support": 95000, "resistance": 100000, ...}}

    # Cross-asset
    correlations: Dict[str, float] = field(default_factory=dict)
    # e.g. {"BTC-ETH": 0.85, "SPY-QQQ": 0.92, ...}

    # Timestamps
    updated_at: str = ""
    cycle_count: int = 0


class WorldModel:
    """
    Maintains and persists the World State.
    Updated each cycle by the trading pipeline.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.state = WorldState()
        self._init_db()
        self._load_last_state()
        logger.info("WorldModel initialized")

    def _init_db(self):
        """Create world model table if needed."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS world_model_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    cycle_count INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS world_model_symbol_intel (
                    symbol TEXT PRIMARY KEY,
                    support_level REAL DEFAULT 0,
                    resistance_level REAL DEFAULT 0,
                    trend TEXT DEFAULT 'neutral',
                    avg_daily_range_pct REAL DEFAULT 0,
                    volume_profile TEXT DEFAULT 'normal',
                    toxicity_score REAL DEFAULT 0,
                    best_strategy TEXT DEFAULT '',
                    worst_strategy TEXT DEFAULT '',
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _load_last_state(self):
        """Load the most recent world state from DB."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                row = conn.execute(
                    "SELECT state_json, cycle_count FROM world_model_state "
                    "ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if row:
                    data = json.loads(row[0])
                    for key, val in data.items():
                        if hasattr(self.state, key):
                            setattr(self.state, key, val)
                    self.state.cycle_count = row[1] or 0
                    logger.info(f"WorldModel restored: cycle {self.state.cycle_count}, regime={self.state.regime}")
        except Exception as exc:
            logger.debug(f"WorldModel load failed (first run?): {exc}")

    # ──────────────────────────────────────────────────────────────────────
    # Update methods (called by the trading pipeline each cycle)
    # ──────────────────────────────────────────────────────────────────────

    def update_regime(
        self,
        regime: str,
        confidence: float,
        strategy_weights: Optional[Dict[str, float]] = None,
    ):
        """Update regime from HMM detector."""
        self.state.regime = regime
        self.state.regime_confidence = confidence
        if strategy_weights:
            self.state.regime_strategy_weights = strategy_weights

    def update_portfolio(
        self,
        portfolio_value: float,
        cash: float,
        positions: int,
        exposure_pct: float,
    ):
        """Update portfolio context from broker."""
        self.state.portfolio_value = portfolio_value
        self.state.cash_available = cash
        self.state.open_positions = positions
        self.state.total_exposure_pct = exposure_pct

    def update_performance(
        self,
        daily_pnl: float = 0.0,
        weekly_pnl: float = 0.0,
        win_rate_7d: float = 0.0,
        best_strategy: str = "",
        worst_strategy: str = "",
    ):
        """Update performance metrics."""
        self.state.daily_pnl = daily_pnl
        self.state.weekly_pnl = weekly_pnl
        self.state.win_rate_7d = win_rate_7d
        self.state.best_strategy_7d = best_strategy
        self.state.worst_strategy_7d = worst_strategy

    def update_market_context(
        self,
        sp500_trend: str = "neutral",
        vix_level: float = 0.0,
        market_breadth: float = 0.5,
    ):
        """Update broad market context."""
        self.state.sp500_trend = sp500_trend
        self.state.vix_level = vix_level
        self.state.market_breadth = market_breadth

    def update_symbol_intel(
        self,
        symbol: str,
        support: float = 0.0,
        resistance: float = 0.0,
        trend: str = "neutral",
        avg_daily_range_pct: float = 0.0,
        volume_profile: str = "normal",
        toxicity_score: float = 0.0,
        best_strategy: str = "",
        worst_strategy: str = "",
    ):
        """Update per-symbol intelligence."""
        self.state.symbol_states[symbol] = {
            "support": support,
            "resistance": resistance,
            "trend": trend,
            "avg_daily_range_pct": avg_daily_range_pct,
            "volume_profile": volume_profile,
            "toxicity_score": toxicity_score,
            "best_strategy": best_strategy,
            "worst_strategy": worst_strategy,
        }

        # Also persist to dedicated table
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO world_model_symbol_intel
                    (symbol, support_level, resistance_level, trend,
                     avg_daily_range_pct, volume_profile, toxicity_score,
                     best_strategy, worst_strategy, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol, support, resistance, trend,
                    avg_daily_range_pct, volume_profile, toxicity_score,
                    best_strategy, worst_strategy, datetime.now().isoformat(),
                ))
                conn.commit()
        except Exception as exc:
            logger.debug(f"Symbol intel persist failed: {exc}")

    def update_correlations(self, correlations: Dict[str, float]):
        """Update cross-asset correlations."""
        self.state.correlations = correlations

    # ──────────────────────────────────────────────────────────────────────
    # Persist (call at end of each cycle)
    # ──────────────────────────────────────────────────────────────────────

    def save(self):
        """Persist current world state to DB."""
        self.state.cycle_count += 1
        self.state.updated_at = datetime.now().isoformat()

        try:
            state_json = json.dumps(asdict(self.state), default=str)
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO world_model_state (timestamp, state_json, cycle_count)
                    VALUES (?, ?, ?)
                """, (self.state.updated_at, state_json, self.state.cycle_count))

                # Keep only last 1000 snapshots to avoid DB bloat
                conn.execute("""
                    DELETE FROM world_model_state
                    WHERE id NOT IN (
                        SELECT id FROM world_model_state ORDER BY id DESC LIMIT 1000
                    )
                """)
                conn.commit()
        except Exception as exc:
            logger.error(f"WorldModel save failed: {exc}")

    # ──────────────────────────────────────────────────────────────────────
    # Query methods
    # ──────────────────────────────────────────────────────────────────────

    def get_state(self) -> WorldState:
        """Get current world state."""
        return self.state

    def get_regime(self) -> str:
        """Get current regime name."""
        return self.state.regime

    def get_strategy_weight(self, strategy: str) -> float:
        """Get regime-adjusted weight for a strategy."""
        return self.state.regime_strategy_weights.get(strategy, 1.0)

    def get_position_budget(self) -> float:
        """How much capital is available for new positions."""
        return self.state.cash_available

    def get_symbol_intel(self, symbol: str) -> Dict[str, Any]:
        """Get intelligence for a specific symbol."""
        return self.state.symbol_states.get(symbol, {})

    def is_portfolio_overexposed(self, max_exposure: float = 0.8) -> bool:
        """Check if portfolio is over-allocated."""
        return self.state.total_exposure_pct > max_exposure

    def get_summary(self) -> Dict[str, Any]:
        """Get a compact summary for logging."""
        return {
            "regime": self.state.regime,
            "regime_conf": f"{self.state.regime_confidence:.0%}",
            "portfolio": f"${self.state.portfolio_value:.2f}",
            "positions": self.state.open_positions,
            "exposure": f"{self.state.total_exposure_pct:.0%}",
            "daily_pnl": f"${self.state.daily_pnl:.2f}",
            "win_rate_7d": f"{self.state.win_rate_7d:.0%}",
            "cycle": self.state.cycle_count,
        }

    def get_status(self) -> Dict[str, Any]:
        """Return model status."""
        return {
            "name": "World Model",
            "active": True,
            "cycle_count": self.state.cycle_count,
            "regime": self.state.regime,
            "symbols_tracked": len(self.state.symbol_states),
            "last_update": self.state.updated_at or "never",
        }


# Singleton
_world_model: Optional[WorldModel] = None


def get_world_model() -> WorldModel:
    """Get or create the singleton world model."""
    global _world_model
    if _world_model is None:
        _world_model = WorldModel()
    return _world_model
