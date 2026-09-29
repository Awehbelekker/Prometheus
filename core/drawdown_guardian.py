#!/usr/bin/env python3
"""
PROMETHEUS Drawdown Guardian
==============================
The HARD enforcement layer that prevents catastrophic losses.

This is the final gate before ANY trade executes. It cannot be overridden
by AI systems, voting, or confidence scores.

Protection Layers:
  1. Circuit Breaker    — halts ALL trading if daily/weekly loss exceeds limit
  2. Equity Trailing Stop — tracks high-water mark, reduces size on drawdown
  3. Regime Gate          — blocks new longs in crisis regime, new shorts in bull
  4. Max Open Positions   — hard cap that tightens during drawdown
  5. Correlation Guard    — blocks trades that increase portfolio concentration
  6. Position Size Cap    — prevents oversized single positions
  7. Sector Exposure      — limits sector concentration
  8. Volatility Scaler    — shrinks position size when VIX/ATR is elevated
  9. Confidence Filter    — blocks weak signals, halves marginal ones
  10. Position Stop-Loss  — enforces hard stops on every position
"""

import sqlite3
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import deque

logger = logging.getLogger("core.drawdown_guardian")


class DrawdownGuardian:
    """
    Hard risk enforcement layer. Every trade must pass through gate() before execution.

    Returns: (approved: bool, adjusted_size: float, reason: str)
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logger

        # ── Circuit Breaker Limits ──
        self.max_daily_loss_pct = self.config.get("max_daily_loss_pct", 3.0)
        self.max_weekly_loss_pct = self.config.get("max_weekly_loss_pct", 7.0)
        self.max_monthly_loss_pct = self.config.get("max_monthly_loss_pct", 12.0)
        self.cooldown_minutes = self.config.get("cooldown_minutes", 60)

        # ── Equity Trailing Stop ──
        self.trailing_stop_pct = self.config.get("trailing_stop_pct", 8.0)
        self.critical_dd_pct = self.config.get("critical_dd_pct", 15.0)

        # ── Position Stop-Loss ──
        self.default_stop_loss_pct = self.config.get("default_stop_loss_pct", 2.0)
        self.max_stop_loss_pct = self.config.get("max_stop_loss_pct", 5.0)
        self.crypto_stop_loss_pct = self.config.get("crypto_stop_loss_pct", 4.0)

        # ── Correlation Guard ──
        self.max_sector_exposure_pct = self.config.get("max_sector_exposure", 40.0)
        self.max_single_position_pct = self.config.get("max_single_pos", 15.0)
        self.max_correlated_positions = self.config.get("max_correlated", 3)

        # ── Volatility Scaling ──
        self.vol_scale_threshold = self.config.get("vol_scale_threshold", 1.5)
        self.vol_scale_factor = self.config.get("vol_scale_factor", 0.5)
        self.vix_crisis_level = self.config.get("vix_crisis", 30.0)

        # ── Max Positions ──
        self.max_positions_normal = self.config.get("max_positions_normal", 10)
        self.max_positions_drawdown = self.config.get("max_positions_dd", 5)
        self.max_positions_crisis = self.config.get("max_positions_crisis", 3)

        # ── State ──
        self.high_water_mark = 0.0
        self.current_equity = 0.0
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.monthly_pnl = 0.0
        self.circuit_breaker_tripped = False
        self.circuit_breaker_until = None
        self.current_regime = "unknown"
        self.trade_log: deque = deque(maxlen=1000)
        self._lock = threading.Lock()

        # ── Multi-broker awareness ──
        # Track how many brokers were active when HWM was set so we can
        # proportionally adjust HWM when a broker goes offline instead of
        # treating the equity drop as a real loss.
        self.last_brokers_active = 0
        self.hwm_brokers_active = 0  # brokers active when HWM was last set
        self.per_broker_equity = {}  # e.g. {'alpaca': 99, 'ib': 248}

        # Sector mapping for correlation guard
        self.sector_map = {
            "AAPL": "tech", "MSFT": "tech", "GOOGL": "tech", "META": "tech",
            "AMZN": "tech", "NVDA": "tech", "AMD": "tech", "INTC": "tech",
            "CRM": "tech", "NFLX": "tech",
            "JPM": "finance", "BAC": "finance", "V": "finance",
            "UNH": "health", "COST": "consumer", "HD": "consumer",
            "DIS": "consumer", "WMT": "consumer", "PYPL": "fintech",
            "TSLA": "auto", "COIN": "crypto_equity",
            "QQQ": "index_tech", "SPY": "index_broad", "DIA": "index_broad",
            "IWM": "index_small",
            "BTC/USD": "crypto", "BTCUSD": "crypto",
            "ETH/USD": "crypto", "ETHUSD": "crypto",
            "SOL/USD": "crypto", "SOLUSD": "crypto",
            "ADA/USD": "crypto", "DOT/USD": "crypto",
            "MATIC/USD": "crypto", "AVAX/USD": "crypto",
            "BNB/USD": "crypto", "UNI/USD": "crypto",
            "CRV/USD": "crypto", "CRVUSD": "crypto",
            "USDT/USD": "stablecoin", "USDTUSD": "stablecoin",
            "USDC/USD": "stablecoin", "USDCUSD": "stablecoin",
            # ── Additional cryptos (prevent "other" sector pile-up) ──
            "DOGE/USD": "crypto_meme", "DOGEUSD": "crypto_meme",
            "SHIB/USD": "crypto_meme", "SHIBUSD": "crypto_meme",
            "PEPE/USD": "crypto_meme", "PEPEUSD": "crypto_meme",
            "LINK/USD": "crypto_defi", "LINKUSD": "crypto_defi",
            "AAVE/USD": "crypto_defi", "AAVEUSD": "crypto_defi",
            "SUSHI/USD": "crypto_defi", "SUSHIUSD": "crypto_defi",
            "ALGO/USD": "crypto_l1", "ALGOUSD": "crypto_l1",
            "ATOM/USD": "crypto_l1", "ATOMUSD": "crypto_l1",
            "NEAR/USD": "crypto_l1", "NEARUSD": "crypto_l1",
            "FTM/USD": "crypto_l1", "FTMUSD": "crypto_l1",
            "XRP/USD": "crypto_payments", "XRPUSD": "crypto_payments",
            "XLM/USD": "crypto_payments", "XLMUSD": "crypto_payments",
            "LTC/USD": "crypto_payments", "LTCUSD": "crypto_payments",
            "BCH/USD": "crypto_payments", "BCHUSD": "crypto_payments",
        }

        # Correlation pairs (symbols that move together)
        self.correlated_groups = [
            {"AAPL", "MSFT", "GOOGL", "META", "QQQ"},
            {"NVDA", "AMD", "INTC"},
            {"BTC/USD", "BTCUSD", "ETH/USD", "ETHUSD", "SOL/USD", "COIN"},
            {"SPY", "QQQ", "DIA", "IWM"},
            {"JPM", "BAC", "V"},
        ]

        # Database — use persistent connection for :memory:, file path otherwise
        self.db_path = self.config.get("db_path", "prometheus_learning.db")
        self._persistent_conn = None
        if self.db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:")
        self._init_db()
        self._load_state()

        self.logger.info(
            f"DrawdownGuardian initialized: "
            f"daily_limit=-{self.max_daily_loss_pct}%, "
            f"weekly=-{self.max_weekly_loss_pct}%, "
            f"trailing_stop=-{self.trailing_stop_pct}%, "
            f"position_stop=-{self.default_stop_loss_pct}%"
        )

    def _get_conn(self):
        """Get DB connection — reuses persistent conn for :memory:"""
        if self._persistent_conn:
            return self._persistent_conn
        return sqlite3.connect(self.db_path)

    def _close_conn(self, conn):
        """Close connection only if it's not the persistent one"""
        if conn is not self._persistent_conn:
            conn.close()

    def _init_db(self):
        """Create guardian tables"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS guardian_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    high_water_mark REAL,
                    current_equity REAL,
                    daily_pnl REAL,
                    weekly_pnl REAL,
                    monthly_pnl REAL,
                    drawdown_pct REAL,
                    circuit_breaker_active INTEGER DEFAULT 0,
                    regime TEXT,
                    hwm_brokers_active INTEGER DEFAULT 0,
                    last_brokers_active INTEGER DEFAULT 0
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS guardian_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT,
                    proposed_action TEXT,
                    proposed_size REAL,
                    block_reason TEXT,
                    protection_layer TEXT,
                    market_conditions TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS guardian_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT,
                    original_size REAL,
                    adjusted_size REAL,
                    adjustment_reason TEXT,
                    protection_layer TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS position_stops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_price REAL NOT NULL,
                    stop_pct REAL NOT NULL,
                    quantity REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    triggered INTEGER DEFAULT 0,
                    triggered_at TEXT
                )
            """)

            # Add broker tracking columns if they don't exist (migration)
            try:
                cur.execute("ALTER TABLE guardian_state ADD COLUMN hwm_brokers_active INTEGER DEFAULT 0")
            except Exception:
                pass  # column already exists
            try:
                cur.execute("ALTER TABLE guardian_state ADD COLUMN last_brokers_active INTEGER DEFAULT 0")
            except Exception:
                pass  # column already exists

            conn.commit()
            self._close_conn(conn)
        except Exception as e:
            self.logger.error(f"Guardian DB init failed: {e}")

    def _load_state(self):
        """Load last known state from DB."""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT high_water_mark, current_equity, daily_pnl, weekly_pnl, monthly_pnl,
                       circuit_breaker_active, regime, hwm_brokers_active, last_brokers_active
                FROM guardian_state ORDER BY id DESC LIMIT 1
            """)
            row = cur.fetchone()
            self._close_conn(conn)

            if row:
                self.high_water_mark = row[0] or 0
                self.current_equity = row[1] or 0
                self.daily_pnl = row[2] or 0
                self.weekly_pnl = row[3] or 0
                self.monthly_pnl = row[4] or 0
                self.circuit_breaker_tripped = bool(row[5])
                self.current_regime = row[6] or "unknown"
                self.hwm_brokers_active = row[7] or 0
                self.last_brokers_active = row[8] or 0
                self.logger.info(
                    f"📊 Guardian loaded state: HWM=${self.high_water_mark:.2f}, "
                    f"equity=${self.current_equity:.2f}, "
                    f"drawdown={((self.high_water_mark - self.current_equity) / self.high_water_mark * 100) if self.high_water_mark > 0 else 0:.1f}%, "
                    f"brokers_at_hwm={self.hwm_brokers_active}, last_brokers={self.last_brokers_active}"
                )
        except Exception as e:
            self.logger.debug(f"No prior guardian state: {e}")

    # ══════════════════════════════════════════════════════
    # DEPOSIT / WITHDRAWAL DETECTION
    # ══════════════════════════════════════════════════════

    def _detect_and_handle_capital_change(self, portfolio_value: float, brokers_active: int = 0):
        """
        Detect deposits, withdrawals, or BROKER DISCONNECTIONS and adjust HWM.

        Key insight (March 2026): When IB disconnects, total_equity drops from
        ~$347 (IB+Alpaca) to ~$99 (Alpaca only). That's NOT a 71% loss — it's
        a broker going offline. We detect this by comparing brokers_active to
        hwm_brokers_active: if fewer brokers are reporting, we scale HWM down
        proportionally instead of treating it as a drawdown.
        """
        if self.current_equity <= 0 or portfolio_value <= 0:
            return

        # ── Broker disconnect/reconnect detection ──
        if brokers_active > 0 and self.hwm_brokers_active > 0:
            if brokers_active < self.last_brokers_active:
                # A broker just went OFFLINE — scale HWM to only count remaining brokers
                old_hwm = self.high_water_mark
                # Proportional scaling: if we had 2 brokers and now have 1,
                # HWM should reflect only the connected broker's share
                scale = portfolio_value / self.current_equity if self.current_equity > 0 else 1.0
                self.high_water_mark = max(portfolio_value, self.high_water_mark * scale)
                self.current_equity = portfolio_value
                self.hwm_brokers_active = brokers_active
                self.last_brokers_active = brokers_active
                # Clear circuit breaker — this wasn't a real loss
                self.circuit_breaker_tripped = False
                self.circuit_breaker_until = None
                self._save_state()
                self.logger.warning(
                    f"🔌 BROKER OFFLINE: {self.last_brokers_active + (self.last_brokers_active - brokers_active)}→{brokers_active} brokers. "
                    f"HWM scaled: ${old_hwm:.2f}→${self.high_water_mark:.2f}. "
                    f"Equity: ${self.current_equity:.2f}. NOT a real loss."
                )
                return

            elif brokers_active > self.last_brokers_active:
                # A broker just came BACK ONLINE — treat like a deposit
                old_hwm = self.high_water_mark
                self.high_water_mark = portfolio_value
                self.current_equity = portfolio_value
                self.hwm_brokers_active = brokers_active
                self.last_brokers_active = brokers_active
                self.daily_pnl = 0.0
                self.weekly_pnl = 0.0
                self.monthly_pnl = 0.0
                self.circuit_breaker_tripped = False
                self.circuit_breaker_until = None
                self._save_state()
                self.logger.info(
                    f"🔌 BROKER RECONNECTED: now {brokers_active} brokers active. "
                    f"HWM reset: ${old_hwm:.2f}→${portfolio_value:.2f}. "
                    f"P/L counters cleared."
                )
                return

        # Update broker tracking
        if brokers_active > 0:
            self.last_brokers_active = brokers_active
            if portfolio_value >= self.high_water_mark:
                self.hwm_brokers_active = brokers_active

        equity_jump = portfolio_value - self.current_equity
        equity_jump_pct = equity_jump / self.current_equity if self.current_equity > 0 else 0

        # Detect deposit: >25% jump OR >$50 absolute increase
        is_deposit = (equity_jump_pct > 0.25 and equity_jump > 20) or equity_jump > 50

        # Detect withdrawal: equity dropped >25% in a single update
        # (not from trading — that would be gradual)
        is_withdrawal = equity_jump_pct < -0.25 and equity_jump < -50

        if is_deposit:
            old_hwm = self.high_water_mark
            self.high_water_mark = portfolio_value
            self.current_equity = portfolio_value
            self.daily_pnl = 0.0
            self.weekly_pnl = 0.0
            self.monthly_pnl = 0.0
            self.circuit_breaker_tripped = False
            self.circuit_breaker_until = None
            self._save_state()
            self.logger.info(
                f"💰 DEPOSIT DETECTED: equity ${self.current_equity:.2f} → ${portfolio_value:.2f} "
                f"(+${equity_jump:.2f} / +{equity_jump_pct*100:.1f}%). "
                f"HWM reset: ${old_hwm:.2f} → ${portfolio_value:.2f}. "
                f"P/L counters and circuit breaker cleared."
            )

        elif is_withdrawal:
            old_hwm = self.high_water_mark
            ratio = portfolio_value / self.current_equity if self.current_equity > 0 else 1.0
            self.high_water_mark = max(portfolio_value, self.high_water_mark * ratio)
            self.current_equity = portfolio_value
            self.daily_pnl = 0.0
            self.weekly_pnl = 0.0
            self.monthly_pnl = 0.0
            self.circuit_breaker_tripped = False
            self.circuit_breaker_until = None
            self._save_state()
            self.logger.info(
                f"💸 WITHDRAWAL DETECTED: equity ${self.current_equity:.2f} → ${portfolio_value:.2f} "
                f"(-${abs(equity_jump):.2f}). HWM adjusted: ${old_hwm:.2f} → ${self.high_water_mark:.2f}"
            )

    def reset_hwm(self, new_equity: float = None):
        """
        Manually reset HWM to current equity (or a specific value).
        Use after deposits, account resets, or when HWM is stale.
        """
        with self._lock:
            if new_equity and new_equity > 0:
                self.high_water_mark = new_equity
                self.current_equity = new_equity
            else:
                self.high_water_mark = self.current_equity

            self.daily_pnl = 0.0
            self.weekly_pnl = 0.0
            self.monthly_pnl = 0.0
            self.circuit_breaker_tripped = False
            self.circuit_breaker_until = None
            self._save_state()
            self.logger.info(
                f"🔄 HWM manually reset to ${self.high_water_mark:.2f}, "
                f"all P/L counters cleared, circuit breaker released"
            )

    # ══════════════════════════════════════════════════════
    # MAIN GATE — Every trade must pass through this
    # ══════════════════════════════════════════════════════

    def gate(
        self,
        symbol: str,
        action: str,
        proposed_size: float,
        price: float,
        confidence: float = 0.5,
        portfolio_value: float = 0.0,
        open_positions: Optional[Dict[str, Dict]] = None,
        regime: str = "unknown",
        volatility_ratio: float = 1.0,
        brokers_active: int = 0,
    ) -> Tuple[bool, float, str]:
        """
        The HARD gate. Returns (approved, adjusted_size, reason).

        If approved=False, the trade MUST NOT execute.
        If adjusted_size < proposed_size, the size was reduced for safety.
        """
        with self._lock:
            self.current_regime = regime
            open_positions = open_positions or {}

            # Update equity tracking — detect deposits/withdrawals/broker disconnects first
            if portfolio_value > 0:
                self._detect_and_handle_capital_change(portfolio_value, brokers_active)
                self.current_equity = portfolio_value
                if portfolio_value > self.high_water_mark:
                    self.high_water_mark = portfolio_value
                    if brokers_active > 0:
                        self.hwm_brokers_active = brokers_active

            reasons = []
            adjusted_size = proposed_size

            # ── Layer 1: Circuit Breaker ──
            blocked, reason = self._check_circuit_breaker()
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "circuit_breaker")
                return False, 0.0, f"CIRCUIT BREAKER: {reason}"

            # ── Layer 2: Equity Trailing Stop ──
            blocked, size_mult, reason = self._check_trailing_stop()
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "trailing_stop")
                return False, 0.0, f"TRAILING STOP: {reason}"
            if size_mult < 1.0:
                old_size = adjusted_size
                adjusted_size *= size_mult
                reasons.append(f"trailing_dd->{size_mult:.0%} size")
                self._log_adjustment(symbol, old_size, adjusted_size, reason, "trailing_stop")

            # ── Layer 3: Regime Gate ──
            blocked, reason = self._check_regime_gate(action, regime)
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "regime_gate")
                return False, 0.0, f"REGIME BLOCK: {reason}"

            # ── Layer 4: Max Positions ──
            blocked, reason = self._check_max_positions(action, open_positions, regime)
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "max_positions")
                return False, 0.0, f"MAX POSITIONS: {reason}"

            # ── Layer 5: Correlation Guard ──
            blocked, reason = self._check_correlation(symbol, action, open_positions)
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "correlation_guard")
                return False, 0.0, f"CORRELATION: {reason}"

            # ── Layer 6: Single Position Size Cap ──
            if portfolio_value > 0 and price > 0:
                position_value = adjusted_size * price
                position_pct = (position_value / portfolio_value) * 100
                if position_pct > self.max_single_position_pct:
                    old_size = adjusted_size
                    max_value = portfolio_value * (self.max_single_position_pct / 100)
                    adjusted_size = max_value / price
                    reasons.append(f"capped {position_pct:.0f}%->{self.max_single_position_pct:.0f}% of portfolio")
                    self._log_adjustment(symbol, old_size, adjusted_size,
                                         f"Position {position_pct:.1f}% exceeds {self.max_single_position_pct}% cap",
                                         "position_cap")

            # ── Layer 7: Sector Exposure Check ──
            blocked, reason = self._check_sector_exposure(symbol, action, price, adjusted_size,
                                                          portfolio_value, open_positions)
            if blocked:
                self._log_block(symbol, action, proposed_size, reason, "sector_exposure")
                return False, 0.0, f"SECTOR LIMIT: {reason}"

            # ── Layer 8: Volatility Scaling ──
            if volatility_ratio > self.vol_scale_threshold:
                old_size = adjusted_size
                scale = max(0.25, 1.0 - (volatility_ratio - 1.0) * self.vol_scale_factor)
                adjusted_size *= scale
                reasons.append(f"vol_scale {volatility_ratio:.1f}x->{scale:.0%} size")
                self._log_adjustment(symbol, old_size, adjusted_size,
                                     f"Volatility {volatility_ratio:.1f}x normal",
                                     "volatility_scale")

            # ── Layer 9: Confidence Filter ──
            if confidence < 0.55:
                self._log_block(symbol, action, proposed_size,
                                f"Confidence {confidence:.1%} below 55% minimum", "confidence")
                return False, 0.0, f"LOW CONFIDENCE: {confidence:.1%} < 55%"
            elif confidence < 0.65:
                old_size = adjusted_size
                adjusted_size *= 0.5
                reasons.append(f"low_conf {confidence:.1%}->50% size")

            # ── Layer 10: Minimum Size Check ──
            # Require at least $10 per trade (or 2% of portfolio, whichever is larger)
            # Prevents spread erosion on tiny positions that can never overcome transaction costs
            min_trade_value = max(10.0, portfolio_value * 0.02) if portfolio_value > 0 else 10.0
            trade_value = adjusted_size * price if price > 0 else 0
            if adjusted_size <= 0 or (price > 0 and trade_value < min_trade_value):
                return False, 0.0, f"Size too small: ${trade_value:.2f} < ${min_trade_value:.2f} minimum"

            # ── Layer 11: Minimum Hold Time (anti-churn) ──
            # Prevent exits within 1 hour of entry — eliminates spread erosion from rapid cycling
            if action.lower() in ('sell', 'close') and open_positions:
                MIN_HOLD_SECONDS = 3600  # 1 hour
                pos = (open_positions.get(symbol)
                       or open_positions.get(symbol.replace('/USD', 'USD'))
                       or open_positions.get(symbol.replace('USD', '/USD')))
                if pos:
                    opened_at = (pos.get('opened_at') or pos.get('entry_time')
                                 or pos.get('open_time') or pos.get('created_at'))
                    if opened_at:
                        try:
                            from datetime import datetime as _dt
                            opened_dt = (_dt.fromisoformat(str(opened_at).replace('Z', ''))
                                         if isinstance(opened_at, str) else opened_at)
                            age_sec = (_dt.now() - opened_dt).total_seconds()
                            if age_sec < MIN_HOLD_SECONDS:
                                remaining_min = (MIN_HOLD_SECONDS - age_sec) / 60
                                self._log_block(symbol, action, proposed_size,
                                                f"Hold time {age_sec/60:.0f}min < 60min minimum",
                                                "min_hold_time")
                                return False, 0.0, f"MIN_HOLD: {age_sec/60:.0f}min held, {remaining_min:.0f}min remaining"
                        except Exception:
                            pass  # unparseable timestamp — allow the sell

            # ── Layer 12: Asset Class PnL Gate ──
            # If 7-day crypto PnL is negative, require higher confidence and halve size
            if action.lower() == 'buy':
                sector = self.sector_map.get(symbol, 'other')
                if sector in ('crypto', 'crypto_meme'):
                    try:
                        import sqlite3 as _sql
                        from pathlib import Path as _Path
                        _db = _Path(__file__).parent.parent / "prometheus_learning.db"
                        if _db.exists():
                            _conn = _sql.connect(str(_db), timeout=3)
                            _row = _conn.execute("""
                                SELECT SUM(pnl) FROM live_trade_outcomes
                                WHERE (symbol LIKE '%USD%' OR symbol LIKE '%BTC%'
                                       OR symbol LIKE '%ETH%' OR symbol LIKE '%SOL%')
                                AND captured_at > datetime('now', '-7 days')
                            """).fetchone()
                            _conn.close()
                            if _row and _row[0] is not None and _row[0] < 0:
                                crypto_7d_pnl = _row[0]
                                if confidence < 0.70:
                                    self._log_block(symbol, action, proposed_size,
                                                    f"Crypto 7d PnL ${crypto_7d_pnl:.0f}, confidence {confidence:.0%} < 70%",
                                                    "crypto_pnl_gate")
                                    return False, 0.0, (f"CRYPTO_GATE: 7d crypto PnL ${crypto_7d_pnl:.0f}, "
                                                        f"need 70% confidence (have {confidence:.0%})")
                                old_size = adjusted_size
                                adjusted_size *= 0.5
                                reasons.append(f"crypto_gate(7d PnL ${crypto_7d_pnl:.0f})->50% size")
                                self._log_adjustment(symbol, old_size, adjusted_size,
                                                     f"Crypto PnL gate: 7d ${crypto_7d_pnl:.0f}",
                                                     "crypto_pnl_gate")
                    except Exception:
                        pass  # never block on DB error

            # Compose reason
            if reasons:
                reason_str = f"APPROVED (adjusted: {', '.join(reasons)})"
            else:
                reason_str = "APPROVED"

            return True, adjusted_size, reason_str

    # ══════════════════════════════════════════════════════
    # Layer implementations
    # ══════════════════════════════════════════════════════

    def _check_circuit_breaker(self) -> Tuple[bool, str]:
        """Check if circuit breaker is tripped"""
        now = datetime.now()

        # Check cooldown
        if self.circuit_breaker_tripped and self.circuit_breaker_until:
            if now < self.circuit_breaker_until:
                remaining = (self.circuit_breaker_until - now).total_seconds() / 60
                return True, f"Cooling down, {remaining:.0f}min remaining"
            else:
                self.circuit_breaker_tripped = False
                self.circuit_breaker_until = None
                self.logger.info("Circuit breaker cooldown expired, trading resumed")

        # Check daily loss
        if self.current_equity > 0 and self.daily_pnl < 0:
            daily_loss_pct = abs(self.daily_pnl) / self.current_equity * 100
            if daily_loss_pct >= self.max_daily_loss_pct:
                self._trip_circuit_breaker(f"Daily loss {daily_loss_pct:.1f}% >= {self.max_daily_loss_pct}%")
                return True, f"Daily loss limit hit: -{daily_loss_pct:.1f}%"

        # Check weekly loss
        if self.current_equity > 0 and self.weekly_pnl < 0:
            weekly_loss_pct = abs(self.weekly_pnl) / self.current_equity * 100
            if weekly_loss_pct >= self.max_weekly_loss_pct:
                self._trip_circuit_breaker(f"Weekly loss {weekly_loss_pct:.1f}% >= {self.max_weekly_loss_pct}%")
                return True, f"Weekly loss limit hit: -{weekly_loss_pct:.1f}%"

        return False, ""

    def _trip_circuit_breaker(self, reason: str):
        """Trip the circuit breaker"""
        self.circuit_breaker_tripped = True
        self.circuit_breaker_until = datetime.now() + timedelta(minutes=self.cooldown_minutes)
        self.logger.warning(f"CIRCUIT BREAKER TRIPPED: {reason} -- "
                            f"Trading halted for {self.cooldown_minutes} minutes")
        self._save_state()

    def _check_trailing_stop(self) -> Tuple[bool, float, str]:
        """Check equity drawdown from high water mark"""
        if self.high_water_mark <= 0 or self.current_equity <= 0:
            return False, 1.0, ""

        dd_pct = ((self.high_water_mark - self.current_equity) / self.high_water_mark) * 100

        if dd_pct >= self.critical_dd_pct:
            return True, 0.0, f"Critical drawdown: -{dd_pct:.1f}% from HWM ${self.high_water_mark:.2f}"

        if dd_pct >= self.trailing_stop_pct:
            severity = (dd_pct - self.trailing_stop_pct) / (self.critical_dd_pct - self.trailing_stop_pct)
            size_mult = max(0.25, 0.50 - severity * 0.25)
            return False, size_mult, f"Drawdown -{dd_pct:.1f}% -> size {size_mult:.0%}"

        if dd_pct >= self.trailing_stop_pct * 0.5:
            return False, 0.80, f"Drawdown warning -{dd_pct:.1f}% -> size 80%"

        return False, 1.0, ""

    def _check_regime_gate(self, action: str, regime: str) -> Tuple[bool, str]:
        """Block trades that go against the current regime.
        
        Only hard-block in true CRISIS. In high_vol/choppy, the volatility
        scaler (Layer 8) already reduces position sizes, and mean-reversion
        opportunities exist. Hard-blocking loses learning data.
        """
        regime_lower = regime.lower() if regime else ""

        # Only block in true crisis — not choppy/high_vol
        if "crisis" in regime_lower:
            if action.upper() == "BUY":
                return True, f"Regime is '{regime}' -- new BUY positions blocked (crisis only)"

        return False, ""

    def _check_max_positions(self, action: str, open_positions: Dict, regime: str) -> Tuple[bool, str]:
        """Enforce maximum simultaneous positions based on current conditions"""
        if action.upper() == "SELL":
            return False, ""

        num_positions = len(open_positions)
        regime_lower = regime.lower() if regime else ""

        if "crisis" in regime_lower:
            max_pos = self.max_positions_crisis
        elif any(k in regime_lower for k in ["drawdown", "high_vol", "choppy"]):
            max_pos = self.max_positions_drawdown
        else:
            max_pos = self.max_positions_normal

        if num_positions >= max_pos:
            return True, f"{num_positions} positions open (max={max_pos} in {regime} regime)"

        return False, ""

    def _check_correlation(self, symbol: str, action: str, open_positions: Dict) -> Tuple[bool, str]:
        """Block trades that increase concentration in correlated assets"""
        if action.upper() == "SELL":
            return False, ""

        sym_clean = symbol.replace("/", "").replace("-", "")

        for group in self.correlated_groups:
            group_clean = {s.replace("/", "").replace("-", "") for s in group}
            if sym_clean in group_clean or symbol in group:
                count = 0
                for pos_sym in open_positions.keys():
                    pos_clean = pos_sym.replace("/", "").replace("-", "")
                    if pos_clean in group_clean or pos_sym in group:
                        count += 1

                if count >= self.max_correlated_positions:
                    return True, (f"Already {count} positions in correlated group "
                                  f"{sorted(list(group))[:3]}... (max={self.max_correlated_positions})")

        return False, ""

    def _check_sector_exposure(self, symbol: str, action: str, price: float,
                               size: float, portfolio_value: float,
                               open_positions: Dict) -> Tuple[bool, str]:
        """Check sector concentration"""
        if action.upper() == "SELL" or portfolio_value <= 0 or price <= 0:
            return False, ""

        sector = self._get_sector(symbol)
        if not sector or sector == "stablecoin":
            return False, ""

        sector_value = size * price
        for pos_sym, pos_data in open_positions.items():
            if self._get_sector(pos_sym) == sector:
                pos_val = abs(float(pos_data.get("market_value", 0)))
                sector_value += pos_val

        sector_pct = (sector_value / portfolio_value) * 100

        if sector_pct > self.max_sector_exposure_pct:
            return True, (f"Sector '{sector}' would be {sector_pct:.0f}% of portfolio "
                          f"(max {self.max_sector_exposure_pct:.0f}%)")

        return False, ""

    def _get_sector(self, symbol: str) -> str:
        """Get sector for a symbol"""
        clean = symbol.replace("/", "").replace("-", "")
        return self.sector_map.get(symbol, self.sector_map.get(clean, "other"))

    # ══════════════════════════════════════════════════════
    # Position Stop-Loss Management
    # ══════════════════════════════════════════════════════

    def set_stop_loss(self, symbol: str, entry_price: float, quantity: float,
                      custom_stop_pct: Optional[float] = None) -> Dict:
        """
        Calculate and register a stop-loss for a new position.
        Returns stop price and details.
        """
        is_crypto = any(tag in symbol.upper() for tag in ["USD", "BTC", "ETH", "SOL", "ADA", "DOT"])

        if custom_stop_pct:
            stop_pct = min(custom_stop_pct, self.max_stop_loss_pct)
        elif is_crypto:
            stop_pct = self.crypto_stop_loss_pct
        else:
            stop_pct = self.default_stop_loss_pct

        stop_price = entry_price * (1 - stop_pct / 100)

        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO position_stops (symbol, entry_price, stop_price, stop_pct, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, entry_price, stop_price, stop_pct, quantity))
            conn.commit()
            self._close_conn(conn)
        except Exception as e:
            self.logger.error(f"Failed to register stop-loss: {e}")

        self.logger.info(f"Stop-loss set: {symbol} entry=${entry_price:.2f} "
                         f"stop=${stop_price:.2f} ({stop_pct:.1f}%)")

        return {
            "symbol": symbol,
            "entry_price": entry_price,
            "stop_price": stop_price,
            "stop_pct": stop_pct,
            "quantity": quantity,
            "risk_amount": (entry_price - stop_price) * quantity,
        }

    def check_stops(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check all active stops against current prices. Returns list of triggered stops."""
        triggered = []

        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, symbol, entry_price, stop_price, stop_pct, quantity
                FROM position_stops
                WHERE triggered = 0
            """)
            stops = cur.fetchall()

            for stop_id, symbol, entry, stop_price, stop_pct, qty in stops:
                current = current_prices.get(symbol)
                if current and current <= stop_price:
                    loss = (current - entry) * qty
                    cur.execute("""
                        UPDATE position_stops 
                        SET triggered = 1, triggered_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), stop_id))

                    triggered.append({
                        "symbol": symbol,
                        "entry_price": entry,
                        "stop_price": stop_price,
                        "current_price": current,
                        "quantity": qty,
                        "loss": loss,
                        "action": "SELL",
                        "reason": f"Stop-loss triggered: ${current:.2f} <= ${stop_price:.2f} (-{stop_pct:.1f}%)",
                    })

                    self.logger.warning(f"STOP TRIGGERED: {symbol} at ${current:.2f} "
                                        f"(stop=${stop_price:.2f}, loss=${loss:.2f})")

            conn.commit()
            self._close_conn(conn)

        except Exception as e:
            self.logger.error(f"Stop check error: {e}")

        return triggered

    # ══════════════════════════════════════════════════════
    # P/L Tracking (called by trading engine)
    # ══════════════════════════════════════════════════════

    def update_pnl(self, trade_pnl: float, portfolio_value: float, brokers_active: int = 0):
        """Called after each trade execution to track running P/L"""
        with self._lock:
            self.daily_pnl += trade_pnl
            self.weekly_pnl += trade_pnl
            self.monthly_pnl += trade_pnl

            # Detect broker connect/disconnect (e.g. IB flicker) before updating equity
            if portfolio_value > 0:
                self._detect_and_handle_capital_change(portfolio_value, brokers_active)

            self.current_equity = portfolio_value

            if portfolio_value > self.high_water_mark:
                self.high_water_mark = portfolio_value
                if brokers_active > 0:
                    self.hwm_brokers_active = brokers_active

            self._save_state()

    def reset_daily_pnl(self):
        """Call at start of each trading day"""
        with self._lock:
            self.daily_pnl = 0.0
            self._save_state()

    def reset_weekly_pnl(self):
        """Call at start of each trading week"""
        with self._lock:
            self.weekly_pnl = 0.0
            self._save_state()

    def reset_monthly_pnl(self):
        """Call at start of each month"""
        with self._lock:
            self.monthly_pnl = 0.0
            self._save_state()

    def _save_state(self):
        """Persist current state"""
        try:
            dd_pct = 0.0
            if self.high_water_mark > 0:
                dd_pct = ((self.high_water_mark - self.current_equity) / self.high_water_mark) * 100

            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO guardian_state
                (timestamp, high_water_mark, current_equity, daily_pnl, weekly_pnl, monthly_pnl,
                 drawdown_pct, circuit_breaker_active, regime, hwm_brokers_active, last_brokers_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                self.high_water_mark, self.current_equity,
                self.daily_pnl, self.weekly_pnl, self.monthly_pnl,
                dd_pct, int(self.circuit_breaker_tripped), self.current_regime,
                self.hwm_brokers_active, self.last_brokers_active
            ))
            conn.commit()
            self._close_conn(conn)
        except Exception as e:
            self.logger.error(f"State save failed: {e}")

    def _log_block(self, symbol: str, action: str, size: float, reason: str, layer: str):
        """Log a blocked trade"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO guardian_blocks
                (timestamp, symbol, proposed_action, proposed_size, block_reason, protection_layer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), symbol, action, size, reason, layer))
            conn.commit()
            self._close_conn(conn)
        except Exception as e:
            self.logger.error(f"Block log failed: {e}")

        self.logger.info(f"BLOCKED: {action} {size:.4f} {symbol} -- {layer}: {reason}")

    def _log_adjustment(self, symbol: str, old: float, new: float, reason: str, layer: str):
        """Log a size adjustment"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO guardian_adjustments
                (timestamp, symbol, original_size, adjusted_size, adjustment_reason, protection_layer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), symbol, old, new, reason, layer))
            conn.commit()
            self._close_conn(conn)
        except Exception as e:
            pass

    # ══════════════════════════════════════════════════════
    # Status / Reporting
    # ══════════════════════════════════════════════════════

    def get_status(self) -> Dict[str, Any]:
        """Full guardian status"""
        dd_pct = 0.0
        if self.high_water_mark > 0 and self.current_equity > 0:
            dd_pct = ((self.high_water_mark - self.current_equity) / self.high_water_mark) * 100

        blocks_today = 0
        adjustments_today = 0
        active_stops = 0
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM guardian_blocks
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            blocks_today = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*) FROM guardian_adjustments
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            adjustments_today = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM position_stops WHERE triggered = 0")
            active_stops = cur.fetchone()[0]

            self._close_conn(conn)
        except Exception:
            pass

        return {
            "high_water_mark": round(self.high_water_mark, 2),
            "current_equity": round(self.current_equity, 2),
            "drawdown_pct": round(dd_pct, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "weekly_pnl": round(self.weekly_pnl, 2),
            "monthly_pnl": round(self.monthly_pnl, 2),
            "circuit_breaker_active": self.circuit_breaker_tripped,
            "circuit_breaker_until": self.circuit_breaker_until.isoformat() if self.circuit_breaker_until else None,
            "current_regime": self.current_regime,
            "blocks_today": blocks_today,
            "adjustments_today": adjustments_today,
            "active_stops": active_stops,
            "limits": {
                "daily_loss": f"-{self.max_daily_loss_pct}%",
                "weekly_loss": f"-{self.max_weekly_loss_pct}%",
                "trailing_stop": f"-{self.trailing_stop_pct}%",
                "critical_dd": f"-{self.critical_dd_pct}%",
                "position_stop": f"-{self.default_stop_loss_pct}%",
                "max_single_pos": f"{self.max_single_position_pct}%",
                "max_sector": f"{self.max_sector_exposure_pct}%",
            }
        }
