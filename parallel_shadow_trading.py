#!/usr/bin/env python3
"""
🔄 PROMETHEUS PRODUCTION-GRADE PARALLEL SHADOW TRADING SYSTEM
===============================================================
Real AI-Powered Shadow Trading with Full PROMETHEUS Integration

PURPOSE:
- Run REAL PROMETHEUS AI decision-making in parallel with live trading
- Execute paper trades using same AI logic as live trading (no random trades!)
- Track which AI components generate the most profitable signals
- Compare shadow vs live decisions to identify missed opportunities
- Feed performance data back to learning engines for continuous improvement

ASSET CLASSES SUPPORTED:
- Stocks (equities) - Market hours trading
- ETFs (SPY, QQQ, etc.) - Market hours trading
- Crypto (BTC-USD, ETH-USD, etc.) - 24/7 trading
- Forex (EURUSD=X, GBPUSD=X, etc.) - 24/5 trading
- Options (via Polygon/CBOE) - Market hours
- Futures (via IB Gateway) - Extended hours

AI SYSTEMS INTEGRATED:
1. HRM Official Integration (sapientinc/HRM checkpoints)
2. Universal Reasoning Engine (ensemble of HRM, GPT-OSS, Quantum, Memory, Patterns)
3. Visual Pattern Provider (1,445 patterns from Cloud Vision)
4. Market Oracle Engine (predictive analysis with RAGFlow)
5. Quantum Trading Engine (50 qubits portfolio optimization)
6. GPT-OSS Engine (language understanding)
7. Hierarchical Agent Coordinator (17 execution agents + 3 supervisors)
8. Market Intelligence Agents (Gap Detection, Opportunity Scanner, Research)

LEARNING SYSTEMS CONNECTED:
- ContinuousLearningEngine - Real-time model improvement
- AILearningEngine - Pattern recognition and recommendations
- AI Attribution Tracker - Signal profitability tracking
- Knowledge Base - Persistent learning storage

METRICS TRACKED:
- Win rate, profit factor, Sharpe ratio
- AI attribution (which AI made which decision)
- Shadow vs Live comparison
- Per-symbol and per-asset-class performance
- Market regime adaptation
"""

import asyncio
import json
import logging
import time
import os
import math
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import yfinance as yf

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== ASSET CLASS DEFINITIONS ====================

class AssetClass(Enum):
    """Supported asset classes for shadow trading"""
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    FOREX = "forex"
    OPTIONS = "options"
    FUTURES = "futures"


# Asset class detection patterns
CRYPTO_SYMBOLS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'DOT-USD', 'BNB-USD', 'XRP-USD', 'LINK-USD']
FOREX_SYMBOLS = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X', 'USDCHF=X', 'NZDUSD=X']
ETF_SYMBOLS = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'XLF', 'XLE', 'XLK', 'XLV', 'GLD', 'SLV', 'USO', 'TLT', 'HYG']


def detect_asset_class(symbol: str) -> AssetClass:
    """Detect asset class from symbol format"""
    if symbol in CRYPTO_SYMBOLS or '-USD' in symbol:
        return AssetClass.CRYPTO
    elif symbol in FOREX_SYMBOLS or '=X' in symbol:
        return AssetClass.FOREX
    elif symbol in ETF_SYMBOLS:
        return AssetClass.ETF
    elif '/' in symbol or symbol.startswith('O:'):  # Options format
        return AssetClass.OPTIONS
    elif symbol.startswith('ES') or symbol.startswith('NQ') or symbol.startswith('CL'):
        return AssetClass.FUTURES
    else:
        return AssetClass.STOCK


def is_tradeable_now(symbol: str) -> bool:
    """Check if a symbol can be traded right now based on market hours.
    
    - Crypto/Forex: 24/7
    - US Stocks/ETFs/Options/Futures: Mon-Fri 9:30-16:00 ET (with 15 min buffer)
    """
    asset_class = detect_asset_class(symbol)
    if asset_class in (AssetClass.CRYPTO, AssetClass.FOREX):
        return True  # 24/7 markets
    
    # US market hours check (Eastern Time)
    from zoneinfo import ZoneInfo
    et_now = datetime.now(ZoneInfo("America/New_York"))
    
    # Weekends are closed
    if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    
    # Market open: 9:30 ET, close: 16:00 ET
    market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= et_now <= market_close


# Default multi-asset watchlist for maximum training data
DEFAULT_MULTI_ASSET_WATCHLIST = [
    # Stocks (Large Cap)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX', 'CRM',
    # ETFs
    'SPY', 'QQQ', 'IWM', 'DIA',
    # Crypto (24/7 trading)
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD',
    # Forex (24/5 trading)
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X'
]


@dataclass
class ShadowTrade:
    """Record of a shadow trade"""
    trade_id: str
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL
    quantity: int
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    reason: str
    ai_components: List[str]  # Which AI systems contributed
    asset_class: str = 'stock'  # Asset class for categorization
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    status: str = 'OPEN'  # OPEN, CLOSED
    exit_reason: Optional[str] = None
    live_comparison: Optional[Dict] = None  # How did live trading handle this?
    market_conditions: Optional[Dict] = None  # Market state at trade time


@dataclass
class ShadowPerformanceMetrics:
    """Performance metrics for shadow trading"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    pnl_history: List[float] = field(default_factory=list)
    ai_attribution: Dict[str, Dict] = field(default_factory=dict)
    # Per-asset class metrics
    asset_class_performance: Dict[str, Dict] = field(default_factory=dict)


class PrometheusParallelShadowTrading:
    """
    🔄 Production-Grade Parallel Shadow Trading System

    Runs the same AI decision-making as live trading but executes paper trades only.
    Compares shadow decisions with live trading to identify missed opportunities
    and continuously improves PROMETHEUS through learning feedback.
    """

    def __init__(self, starting_capital: float = 100000.0, max_position_pct: float = 0.10,
                 session_id: str = None, config_name: str = "default",
                 strategy_config: Dict = None):
        """
        Initialize Shadow Trading System with database persistence and multi-session support.

        Args:
            starting_capital: Initial capital for shadow trading
            max_position_pct: Maximum position size as percentage of capital
            session_id: Unique session identifier (auto-generated if None)
            config_name: Configuration name for this session (e.g., "aggressive", "conservative")
            strategy_config: Optional dict to override default parameters for multi-strategy comparison
                Keys: ai_weights, min_confidence, min_score, trailing_stop_trigger, trailing_stop_distance,
                      dca_enabled, dca_trigger_pct, dca_max_adds, time_exit_enabled, max_hold_days_stock,
                      max_hold_days_crypto, scale_out_enabled, scale_out_first_pct, scale_out_second_pct,
                      target_pct, stop_loss_pct, max_trades_per_day
        """
        self.strategy_config = strategy_config or {}
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        self.max_position_pct = self.strategy_config.get('max_position_pct', max_position_pct)
        self.session_start = datetime.now()

        # Session identification for multi-session support
        self.session_id = session_id or f"shadow_{self.session_start.strftime('%Y%m%d_%H%M%S')}_{config_name}"
        self.config_name = config_name

        # Database path (same as live trading for unified learning)
        self.db_path = "prometheus_learning.db"

        # Trading state
        self.shadow_trades: List[ShadowTrade] = []
        self.open_positions: Dict[str, List[ShadowTrade]] = defaultdict(list)
        self.metrics = ShadowPerformanceMetrics()
        self.trades_today = 0
        self.max_trades_per_day = 50  # Increased for multi-asset trading
        self.running = False

        # Results directory
        self.results_dir = Path("shadow_trading_results")
        self.results_dir.mkdir(exist_ok=True)

        # AI Systems (initialized lazily)
        self._hrm_adapter = None
        self._universal_reasoning = None
        self._visual_patterns = None
        self._market_oracle = None
        self._quantum_engine = None
        self._gpt_oss = None
        self._agent_coordinator = None
        self._ai_attribution_tracker = None

        # Phase 21 AI Voters (new integrations)
        self._langgraph_orchestrator = None
        self._mercury2_adapter = None
        self._sec_analyzer = None

        # Learning Systems (NEW - for full learning integration)
        self._continuous_learning_engine = None
        self._ai_learning_engine = None

        # NEW: AI Consciousness + RL Agent + Revolutionary Engines (2026-03-08 UPDATE)
        self._ai_consciousness = None
        self._rl_agent = None
        self._revolutionary_engines = None

        # Knowledge Base for persistent learning
        self.knowledge_base_dir = Path("shadow_trading_results/knowledge_base")
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)

        # Live trading comparison
        self.live_decisions: Dict[str, Dict] = {}  # symbol -> latest live decision

        # Initialize database tables and load persisted state
        self._init_shadow_database()
        self._load_shadow_position_tracking()
        self._load_open_shadow_trades()

        # ═══════════════════════════════════════════════════════════════════════════
        # 🚀 6 BACKTEST ENHANCEMENTS - Same as live trading for fair comparison
        # ═══════════════════════════════════════════════════════════════════════════

        # === ENHANCEMENT 1: TRAILING STOP ===
        self.trailing_stop_enabled = self.strategy_config.get('trailing_stop_enabled', True)
        self.trailing_stop_trigger = self.strategy_config.get('trailing_stop_trigger', 0.03)   # was 0.02 → 0.03 (3% before trailing activates)
        self.trailing_stop_distance = self.strategy_config.get('trailing_stop_distance', 0.015) # was 0.01 → 0.015 (1.5% drop from high triggers exit)

        # === ENHANCEMENT 2: DCA ON DIPS ===
        self.dca_enabled = self.strategy_config.get('dca_enabled', True)
        self.dca_trigger_pct = self.strategy_config.get('dca_trigger_pct', -0.03)  # was -0.02 → -0.03 (3% dip before DCA)
        self.dca_max_adds = self.strategy_config.get('dca_max_adds', 2)
        self.dca_position_pct = self.strategy_config.get('dca_position_pct', 0.05)

        # === ENHANCEMENT 3: TIME-BASED EXIT ===
        self.time_exit_enabled = self.strategy_config.get('time_exit_enabled', True)
        self.max_hold_days_crypto = self.strategy_config.get('max_hold_days_crypto', 5)   # was 3 → 5 days
        self.max_hold_days_stock = self.strategy_config.get('max_hold_days_stock', 14)    # was 7 → 14 days

        # === ENHANCEMENT 4: SCALE-OUT PROFITS ===
        self.scale_out_enabled = self.strategy_config.get('scale_out_enabled', True)
        self.scale_out_first_pct = self.strategy_config.get('scale_out_first_pct', 0.015)
        self.scale_out_second_pct = self.strategy_config.get('scale_out_second_pct', 0.03)

        # === AI DECISION PARAMETERS (configurable for multi-strategy) ===
        # 2026-03-08: Updated weights to include AI Consciousness, RL Agent, Revolutionary Engines
        self.ai_decision_weights = self.strategy_config.get('ai_weights', {
            'AI_Consciousness': 0.18,      # NEW: Fine-tuned consciousness engine
            'RL_Agent': 0.16,              # NEW: Reinforcement learning agent
            'Revolutionary': 0.14,         # NEW: Revolutionary crypto/options/market-maker engines
            'HRM': 0.12,
            'Universal_Reasoning': 0.10,
            'Visual_Patterns': 0.08,
            'Quantum': 0.05,               # Reduced (disabled due to poor performance)
            'Technical': 0.08,
            'Agents': 0.04,                # Reduced (disabled due to 0% win rate)
            'Fed_NLP': 0.05,
            'ML_Regime': 0.08
        })
        self.min_decision_confidence = self.strategy_config.get('min_confidence', 0.65)
        self.min_decision_score = self.strategy_config.get('min_score', 0.25)
        self.target_pct = self.strategy_config.get('target_pct', 0.05)       # was 0.03 → 0.05 (5% target)
        self.stop_loss_pct = self.strategy_config.get('stop_loss_pct', 0.05)  # was 0.03 → 0.05 (5% stop loss)

        # === FAST-FEEDBACK LEARNING ADAPTATION ===
        # Trigger temporary de-risking when recent shadow performance deteriorates.
        self.shadow_risk_guard_enabled = self.strategy_config.get('shadow_risk_guard_enabled', True)
        self.shadow_risk_window_trades = int(self.strategy_config.get('shadow_risk_window_trades', 12))
        self.shadow_risk_min_loss_streak = int(self.strategy_config.get('shadow_risk_min_loss_streak', 4))
        self.shadow_risk_max_win_rate_pct = float(self.strategy_config.get('shadow_risk_max_win_rate_pct', 40.0))
        self.shadow_risk_min_pnl_pct = float(self.strategy_config.get('shadow_risk_min_pnl_pct', -1.0))
        self._last_shadow_risk_adapt_at = None
        self._shadow_risk_cooldown_minutes = int(self.strategy_config.get('shadow_risk_cooldown_minutes', 30))

        # === ENHANCEMENT 5: CORRELATION FILTER ===
        self.correlation_filter_enabled = True
        self.max_correlated_positions = 2
        self.correlated_assets = {
            'BTC-USD': ['ETH-USD', 'SOL-USD', 'LINK-USD'],
            'ETH-USD': ['BTC-USD', 'SOL-USD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'NVDA': ['AMD'],
            'AMD': ['NVDA'],
            'TSLA': ['RIVN', 'LCID'],
        }

        # === ENHANCEMENT 6: SENTIMENT/FED DAYS FILTER ===
        self.sentiment_filter_enabled = True
        self.fed_days_2025_2026 = [
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-11-05", "2025-12-17",
            "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
            "2026-07-29", "2026-09-16", "2026-11-04", "2026-12-16",
        ]

        # === POSITION TRACKING FOR ENHANCEMENTS ===
        self.position_highs: Dict[str, float] = {}  # Track highest price (trailing stop)
        self.position_entry_times: Dict[str, datetime] = {}  # Track entry time (time exit)
        self.scaled_positions: Dict[str, int] = {}  # Track scale-out level (0, 1, 2)
        self.dca_counts: Dict[str, int] = {}  # Track DCA buys per position

        logger.info("🔄 PROMETHEUS Parallel Shadow Trading System initialized")
        logger.info(f"   Session ID: {self.session_id}")
        logger.info(f"   Config Name: {self.config_name}")
        logger.info(f"   Starting Capital: ${starting_capital:,.2f}")
        logger.info(f"   Max Position Size: {max_position_pct*100:.0f}% (${starting_capital * max_position_pct:,.2f})")
        logger.info(f"   Multi-Asset Support: Stocks, ETFs, Crypto, Forex")
        logger.info(f"   🚀 6 Enhancements: TRAILING_STOP, DCA, TIME_EXIT, SCALE_OUT, CORRELATION, SENTIMENT")
        logger.info(f"   💾 Database Persistence: ENABLED")

    # ==================== DATABASE PERSISTENCE ====================

    def _init_shadow_database(self):
        """
        Initialize shadow trading database tables.
        Creates tables for position tracking, trade history, sessions, and live comparison.
        """
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            # Table 1: Shadow Position Tracking (mirrors live trading position_tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shadow_position_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    position_high REAL,
                    entry_time TEXT,
                    scaled_level INTEGER DEFAULT 0,
                    dca_count INTEGER DEFAULT 0,
                    updated_at TEXT,
                    UNIQUE(session_id, symbol)
                )
            """)

            # Table 2: Shadow Trade History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shadow_trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    trade_id TEXT NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    target_price REAL,
                    stop_loss REAL,
                    confidence REAL,
                    reason TEXT,
                    ai_components TEXT,
                    asset_class TEXT DEFAULT 'stock',
                    exit_price REAL,
                    exit_time TEXT,
                    pnl REAL,
                    pnl_pct REAL,
                    status TEXT DEFAULT 'OPEN',
                    exit_reason TEXT,
                    market_conditions TEXT,
                    live_comparison TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_shadow_trade_session ON shadow_trade_history(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_shadow_trade_symbol ON shadow_trade_history(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_shadow_trade_status ON shadow_trade_history(status)")

            # Table 3: Shadow Sessions (track multiple parallel sessions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shadow_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL UNIQUE,
                    config_name TEXT NOT NULL,
                    starting_capital REAL NOT NULL,
                    current_capital REAL NOT NULL,
                    max_position_pct REAL NOT NULL,
                    started_at TEXT NOT NULL,
                    last_active TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    config_json TEXT,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0
                )
            """)

            # Table 4: Live vs Shadow Comparison
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_shadow_comparison (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    live_decision TEXT,
                    shadow_decision TEXT,
                    live_confidence REAL,
                    shadow_confidence REAL,
                    divergence_type TEXT,
                    live_entry_price REAL,
                    shadow_entry_price REAL,
                    live_exit_price REAL,
                    shadow_exit_price REAL,
                    live_pnl REAL,
                    shadow_pnl REAL,
                    hypothetical_difference REAL,
                    notes TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comparison_session ON live_shadow_comparison(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comparison_symbol ON live_shadow_comparison(symbol)")

            db.commit()

            # Register this session
            cursor.execute("""
                INSERT OR REPLACE INTO shadow_sessions
                (session_id, config_name, starting_capital, current_capital, max_position_pct, started_at, last_active, status, config_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
            """, (
                self.session_id,
                self.config_name,
                self.starting_capital,
                self.current_capital,
                self.max_position_pct,
                self.session_start.isoformat(),
                datetime.now().isoformat(),
                json.dumps(self._get_config_dict())
            ))
            db.commit()
            db.close()

            logger.info(f"💾 Shadow database initialized: 4 tables created/verified")
            logger.info(f"   Session registered: {self.session_id}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize shadow database: {e}")

    def _get_config_dict(self) -> Dict:
        """Get current configuration as dictionary for storage"""
        return {
            'trailing_stop_enabled': self.trailing_stop_enabled if hasattr(self, 'trailing_stop_enabled') else True,
            'trailing_stop_trigger': self.trailing_stop_trigger if hasattr(self, 'trailing_stop_trigger') else 0.02,
            'trailing_stop_distance': self.trailing_stop_distance if hasattr(self, 'trailing_stop_distance') else 0.01,
            'dca_enabled': self.dca_enabled if hasattr(self, 'dca_enabled') else True,
            'dca_trigger_pct': self.dca_trigger_pct if hasattr(self, 'dca_trigger_pct') else -0.02,
            'dca_max_adds': self.dca_max_adds if hasattr(self, 'dca_max_adds') else 2,
            'time_exit_enabled': self.time_exit_enabled if hasattr(self, 'time_exit_enabled') else True,
            'scale_out_enabled': self.scale_out_enabled if hasattr(self, 'scale_out_enabled') else True,
            'correlation_filter_enabled': self.correlation_filter_enabled if hasattr(self, 'correlation_filter_enabled') else True,
            'sentiment_filter_enabled': self.sentiment_filter_enabled if hasattr(self, 'sentiment_filter_enabled') else True,
            'max_position_pct': self.max_position_pct,
            'starting_capital': self.starting_capital,
        }

    def _load_shadow_position_tracking(self):
        """Load position tracking from database on startup"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                SELECT symbol, position_high, entry_time, scaled_level, dca_count
                FROM shadow_position_tracking
                WHERE session_id = ?
            """, (self.session_id,))

            rows = cursor.fetchall()
            loaded_count = 0

            for row in rows:
                symbol, position_high, entry_time, scaled_level, dca_count = row
                if position_high is not None:
                    self.position_highs[symbol] = position_high
                if entry_time is not None:
                    self.position_entry_times[symbol] = datetime.fromisoformat(entry_time)
                if scaled_level is not None:
                    self.scaled_positions[symbol] = scaled_level
                if dca_count is not None:
                    self.dca_counts[symbol] = dca_count
                loaded_count += 1

            db.close()

            if loaded_count > 0:
                logger.info(f"💾 Loaded position tracking for {loaded_count} symbols from database")

        except Exception as e:
            logger.warning(f"⚠️ Could not load position tracking: {e}")

    def _save_shadow_position_tracking(self, symbol: str):
        """Save position tracking to database after updates"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO shadow_position_tracking
                (session_id, symbol, position_high, entry_time, scaled_level, dca_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                symbol,
                self.position_highs.get(symbol),
                self.position_entry_times.get(symbol).isoformat() if symbol in self.position_entry_times else None,
                self.scaled_positions.get(symbol, 0),
                self.dca_counts.get(symbol, 0),
                datetime.now().isoformat()
            ))

            db.commit()
            db.close()
            logger.debug(f"💾 Position tracking saved for {symbol}")

        except Exception as e:
            logger.warning(f"⚠️ Could not save position tracking for {symbol}: {e}")

    def _load_open_shadow_trades(self):
        """Load open shadow trades from database on startup - INCLUDING orphaned trades from previous sessions"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            # Load ALL open trades from ANY session (not just current)
            # This prevents orphaning trades when server restarts with new session_id
            cursor.execute("""
                SELECT trade_id, timestamp, symbol, action, quantity, entry_price,
                       target_price, stop_loss, confidence, reason, ai_components,
                       asset_class, market_conditions, session_id
                FROM shadow_trade_history
                WHERE status = 'OPEN' AND entry_price > 0
            """)

            rows = cursor.fetchall()
            loaded_count = 0
            adopted_count = 0

            for row in rows:
                (trade_id, timestamp, symbol, action, quantity, entry_price,
                 target_price, stop_loss, confidence, reason, ai_components,
                 asset_class, market_conditions, original_session_id) = row

                trade = ShadowTrade(
                    trade_id=trade_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    symbol=symbol,
                    action=action,
                    quantity=int(quantity),
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    confidence=confidence,
                    reason=reason or "",
                    ai_components=json.loads(ai_components) if ai_components else [],
                    asset_class=asset_class or 'stock',
                    market_conditions=json.loads(market_conditions) if market_conditions else None,
                    status='OPEN'
                )

                # Adopt orphaned trades from previous sessions into current session
                if original_session_id != self.session_id:
                    cursor.execute("""
                        UPDATE shadow_trade_history SET session_id = ? WHERE trade_id = ?
                    """, (self.session_id, trade_id))
                    adopted_count += 1

                self.shadow_trades.append(trade)
                self.open_positions[symbol].append(trade)
                loaded_count += 1

            if adopted_count > 0:
                db.commit()
                logger.info(f"Adopted {adopted_count} orphaned trades from previous sessions")

            db.close()

            if loaded_count > 0:
                logger.info(f"Loaded {loaded_count} open shadow trades from database")

        except Exception as e:
            logger.warning(f"⚠️ Could not load open shadow trades: {e}")

    def _save_shadow_trade(self, trade: ShadowTrade):
        """Save a shadow trade to database"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO shadow_trade_history
                (session_id, trade_id, timestamp, symbol, action, quantity, entry_price,
                 target_price, stop_loss, confidence, reason, ai_components, asset_class,
                 exit_price, exit_time, pnl, pnl_pct, status, exit_reason, market_conditions, live_comparison)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                trade.trade_id,
                trade.timestamp.isoformat(),
                trade.symbol,
                trade.action,
                trade.quantity,
                trade.entry_price,
                trade.target_price,
                trade.stop_loss,
                trade.confidence,
                trade.reason,
                json.dumps(trade.ai_components),
                trade.asset_class,
                trade.exit_price,
                trade.exit_time.isoformat() if trade.exit_time else None,
                trade.pnl,
                trade.pnl_pct,
                trade.status,
                trade.exit_reason,
                json.dumps(trade.market_conditions) if trade.market_conditions else None,
                json.dumps(trade.live_comparison) if trade.live_comparison else None
            ))

            db.commit()
            db.close()
            logger.debug(f"💾 Shadow trade saved: {trade.trade_id}")

        except Exception as e:
            logger.warning(f"⚠️ Could not save shadow trade {trade.trade_id}: {e}")

    def _delete_shadow_position_tracking(self, symbol: str):
        """Delete position tracking from database when position fully closed"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                DELETE FROM shadow_position_tracking
                WHERE session_id = ? AND symbol = ?
            """, (self.session_id, symbol))

            db.commit()
            db.close()
            logger.debug(f"💾 Position tracking deleted for {symbol}")

        except Exception as e:
            logger.warning(f"⚠️ Could not delete position tracking for {symbol}: {e}")

    def _update_session_metrics(self):
        """Update session metrics in database"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                UPDATE shadow_sessions
                SET current_capital = ?,
                    last_active = ?,
                    total_trades = ?,
                    winning_trades = ?,
                    total_pnl = ?,
                    win_rate = ?
                WHERE session_id = ?
            """, (
                self.current_capital,
                datetime.now().isoformat(),
                self.metrics.total_trades,
                self.metrics.winning_trades,
                self.metrics.total_pnl,
                self.metrics.win_rate,
                self.session_id
            ))

            db.commit()
            db.close()

        except Exception as e:
            logger.warning(f"⚠️ Could not update session metrics: {e}")

    def _store_shadow_signal_prediction(self, trade: ShadowTrade):
        """Store shadow signal into signal_predictions so outcomes can be matched quickly."""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signal_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    confidence REAL,
                    entry_price REAL,
                    target_price REAL,
                    stop_loss REAL,
                    ai_components TEXT,
                    vote_breakdown TEXT,
                    reasoning TEXT,
                    market_data TEXT,
                    outcome_recorded INTEGER DEFAULT 0
                )
            """)

            market_data_json = json.dumps(trade.market_conditions) if trade.market_conditions else "{}"
            ai_components_json = json.dumps(trade.ai_components or [])
            reasoning = f"SHADOW::{trade.reason or 'N/A'}"

            cursor.execute("""
                INSERT INTO signal_predictions
                (timestamp, symbol, action, confidence, entry_price, target_price, stop_loss,
                 ai_components, vote_breakdown, reasoning, market_data, outcome_recorded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                trade.timestamp.isoformat(),
                trade.symbol,
                trade.action,
                trade.confidence,
                trade.entry_price,
                trade.target_price,
                trade.stop_loss,
                ai_components_json,
                json.dumps({"source": "shadow", "trade_id": trade.trade_id}),
                reasoning,
                market_data_json,
            ))

            db.commit()
            db.close()
        except Exception as e:
            logger.debug(f"Could not store shadow signal prediction: {e}")

    def _mark_signal_outcome_recorded(self, trade: ShadowTrade):
        """Mark one matching unrecorded prediction as completed when a shadow trade closes."""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            symbol_variants = [trade.symbol]
            if '/' in trade.symbol:
                symbol_variants.append(trade.symbol.replace('/', ''))
            if trade.symbol.endswith('-USD'):
                symbol_variants.append(trade.symbol.replace('-USD', '/USD'))
                symbol_variants.append(trade.symbol.replace('-USD', 'USD'))
            if trade.symbol.endswith('USD') and '/' not in trade.symbol and '-' not in trade.symbol:
                symbol_variants.append(trade.symbol[:-3] + '/USD')

            # Preserve order while removing duplicates.
            symbol_variants = list(dict.fromkeys(symbol_variants))
            placeholders = ",".join("?" * len(symbol_variants))
            exit_ts = trade.exit_time.isoformat() if trade.exit_time else datetime.now().isoformat()

            cursor.execute(f"""
                SELECT id
                FROM signal_predictions
                WHERE symbol IN ({placeholders})
                  AND outcome_recorded = 0
                  AND timestamp <= ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, symbol_variants + [exit_ts])
            row = cursor.fetchone()

            if row:
                cursor.execute("UPDATE signal_predictions SET outcome_recorded = 1 WHERE id = ?", (row[0],))

            db.commit()
            db.close()
        except Exception as e:
            logger.debug(f"Could not mark signal outcome recorded: {e}")

    def _persist_shadow_learning_outcome(self, trade: ShadowTrade):
        """Write closed shadow outcomes into learning_outcomes immediately."""
        try:
            if trade.status != 'CLOSED' or trade.exit_price is None or trade.pnl is None or trade.pnl_pct is None:
                return

            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    predicted_action TEXT,
                    predicted_confidence REAL,
                    entry_price REAL,
                    exit_price REAL,
                    profit_loss REAL,
                    profit_pct REAL,
                    was_correct INTEGER,
                    ai_components TEXT,
                    learning_notes TEXT
                )
            """)

            was_correct = 1 if (trade.pnl or 0) > 0 else 0
            notes = f"SHADOW outcome | trade_id={trade.trade_id} | exit_reason={trade.exit_reason or 'UNKNOWN'}"

            cursor.execute("""
                INSERT INTO learning_outcomes
                (timestamp, symbol, predicted_action, predicted_confidence, entry_price, exit_price,
                 profit_loss, profit_pct, was_correct, ai_components, learning_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                (trade.exit_time or datetime.now()).isoformat(),
                trade.symbol,
                trade.action,
                trade.confidence,
                trade.entry_price,
                trade.exit_price,
                trade.pnl,
                float(trade.pnl_pct) / 100.0,
                was_correct,
                json.dumps(trade.ai_components or []),
                notes,
            ))

            db.commit()
            db.close()
        except Exception as e:
            logger.debug(f"Could not persist shadow learning outcome: {e}")

    def _record_risk_adaptation_event(self, metric: str, old_value: float, new_value: float, reason: str):
        """Persist adaptation events for auditability and post-mortems."""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_adaptation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric TEXT,
                    old_value REAL,
                    new_value REAL,
                    reason TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO risk_adaptation_log (timestamp, metric, old_value, new_value, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), metric, old_value, new_value, reason))

            db.commit()
            db.close()
        except Exception as e:
            logger.debug(f"Could not record risk adaptation event: {e}")

    def _maybe_trigger_shadow_risk_adaptation(self):
        """Temporarily de-risk when recent shadow trade quality deteriorates."""
        if not self.shadow_risk_guard_enabled:
            return

        if self._last_shadow_risk_adapt_at is not None:
            minutes_since = (datetime.now() - self._last_shadow_risk_adapt_at).total_seconds() / 60.0
            if minutes_since < self._shadow_risk_cooldown_minutes:
                return

        closed = [t for t in self.shadow_trades if t.status == 'CLOSED' and t.pnl is not None]
        if len(closed) < self.shadow_risk_window_trades:
            return

        window = closed[-self.shadow_risk_window_trades:]
        wins = sum(1 for t in window if (t.pnl or 0) > 0)
        losses = sum(1 for t in window if (t.pnl or 0) <= 0)
        win_rate_pct = (wins / len(window)) * 100.0
        pnl_sum = sum(float(t.pnl or 0.0) for t in window)
        pnl_pct = (pnl_sum / self.starting_capital) * 100.0 if self.starting_capital else 0.0
        recent_loss_streak = 0
        for t in reversed(window):
            if (t.pnl or 0) <= 0:
                recent_loss_streak += 1
            else:
                break

        if not (
            win_rate_pct <= self.shadow_risk_max_win_rate_pct
            and pnl_pct <= self.shadow_risk_min_pnl_pct
            and recent_loss_streak >= self.shadow_risk_min_loss_streak
        ):
            return

        reason = (
            f"Shadow de-risk trigger: win_rate={win_rate_pct:.1f}% over last {len(window)} trades, "
            f"window_pnl={pnl_pct:.2f}%, loss_streak={recent_loss_streak}"
        )

        old_conf = self.min_decision_confidence
        new_conf = min(0.90, old_conf + 0.03)
        if new_conf > old_conf:
            self.min_decision_confidence = new_conf
            self._record_risk_adaptation_event("min_decision_confidence", old_conf, new_conf, reason)

        old_pos = self.max_position_pct
        new_pos = max(0.03, old_pos * 0.85)
        if new_pos < old_pos:
            self.max_position_pct = new_pos
            self._record_risk_adaptation_event("max_position_pct", old_pos, new_pos, reason)

        old_stop = self.stop_loss_pct
        new_stop = max(0.015, old_stop * 0.90)
        if new_stop < old_stop:
            self.stop_loss_pct = new_stop
            self._record_risk_adaptation_event("stop_loss_pct", old_stop, new_stop, reason)

        self._last_shadow_risk_adapt_at = datetime.now()
        logger.warning(
            "🛡️ SHADOW RISK ADAPTATION APPLIED | "
            f"min_conf: {old_conf:.3f}->{self.min_decision_confidence:.3f}, "
            f"max_pos: {old_pos:.3f}->{self.max_position_pct:.3f}, "
            f"stop_loss: {old_stop:.3f}->{self.stop_loss_pct:.3f}"
        )

    def _record_live_shadow_comparison(self, symbol: str, live_decision: str, shadow_decision: str,
                                        live_confidence: float = None, shadow_confidence: float = None,
                                        live_entry: float = None, shadow_entry: float = None,
                                        live_exit: float = None, shadow_exit: float = None,
                                        live_pnl: float = None, shadow_pnl: float = None,
                                        notes: str = None):
        """Record a comparison between live and shadow decisions"""
        try:
            # Determine divergence type
            if live_decision == shadow_decision:
                divergence_type = "MATCH"
            elif live_decision == "BUY" and shadow_decision == "HOLD":
                divergence_type = "LIVE_AGGRESSIVE"
            elif live_decision == "HOLD" and shadow_decision == "BUY":
                divergence_type = "SHADOW_AGGRESSIVE"
            elif live_decision == "SELL" and shadow_decision == "HOLD":
                divergence_type = "LIVE_EARLY_EXIT"
            elif live_decision == "HOLD" and shadow_decision == "SELL":
                divergence_type = "SHADOW_EARLY_EXIT"
            else:
                divergence_type = "OPPOSITE"

            # Calculate hypothetical difference
            hypothetical_difference = None
            if shadow_pnl is not None and live_pnl is not None:
                hypothetical_difference = shadow_pnl - live_pnl

            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO live_shadow_comparison
                (timestamp, session_id, symbol, live_decision, shadow_decision,
                 live_confidence, shadow_confidence, divergence_type,
                 live_entry_price, shadow_entry_price, live_exit_price, shadow_exit_price,
                 live_pnl, shadow_pnl, hypothetical_difference, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                self.session_id,
                symbol,
                live_decision,
                shadow_decision,
                live_confidence,
                shadow_confidence,
                divergence_type,
                live_entry,
                shadow_entry,
                live_exit,
                shadow_exit,
                live_pnl,
                shadow_pnl,
                hypothetical_difference,
                notes
            ))

            db.commit()
            db.close()

            if divergence_type != "MATCH":
                logger.info(f"📊 Live/Shadow Divergence: {symbol} - {divergence_type}")
                if hypothetical_difference is not None:
                    logger.info(f"   Hypothetical difference: ${hypothetical_difference:+.2f}")

        except Exception as e:
            logger.warning(f"⚠️ Could not record comparison for {symbol}: {e}")

    # ==================== SESSION MANAGEMENT ====================

    @classmethod
    def list_all_sessions(cls, db_path: str = "prometheus_learning.db") -> List[Dict]:
        """List all shadow trading sessions from database"""
        sessions = []
        try:
            db = sqlite3.connect(db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                SELECT session_id, config_name, starting_capital, current_capital,
                       started_at, last_active, status, total_trades, winning_trades,
                       total_pnl, win_rate
                FROM shadow_sessions
                ORDER BY started_at DESC
            """)

            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'config_name': row[1],
                    'starting_capital': row[2],
                    'current_capital': row[3],
                    'started_at': row[4],
                    'last_active': row[5],
                    'status': row[6],
                    'total_trades': row[7],
                    'winning_trades': row[8],
                    'total_pnl': row[9],
                    'win_rate': row[10],
                    'pnl_pct': ((row[3] - row[2]) / row[2] * 100) if row[2] > 0 else 0
                })

            db.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not list sessions: {e}")

        return sessions

    @classmethod
    def get_session_comparison(cls, db_path: str = "prometheus_learning.db") -> Dict:
        """Compare performance across all shadow sessions"""
        sessions = cls.list_all_sessions(db_path)

        if not sessions:
            return {'error': 'No sessions found'}

        comparison = {
            'total_sessions': len(sessions),
            'active_sessions': len([s for s in sessions if s['status'] == 'ACTIVE']),
            'best_performing': None,
            'worst_performing': None,
            'by_config': {},
            'sessions': sessions
        }

        # Find best/worst performing
        if sessions:
            sorted_by_pnl = sorted(sessions, key=lambda x: x.get('total_pnl', 0), reverse=True)
            comparison['best_performing'] = sorted_by_pnl[0]
            comparison['worst_performing'] = sorted_by_pnl[-1]

        # Group by config_name
        for session in sessions:
            config = session['config_name']
            if config not in comparison['by_config']:
                comparison['by_config'][config] = {
                    'sessions': [],
                    'avg_pnl': 0,
                    'avg_win_rate': 0
                }
            comparison['by_config'][config]['sessions'].append(session)

        # Calculate averages per config
        for config, data in comparison['by_config'].items():
            if data['sessions']:
                data['avg_pnl'] = sum(s.get('total_pnl', 0) for s in data['sessions']) / len(data['sessions'])
                data['avg_win_rate'] = sum(s.get('win_rate', 0) for s in data['sessions']) / len(data['sessions'])

        return comparison

    @classmethod
    def resume_session(cls, session_id: str, db_path: str = "prometheus_learning.db") -> 'PrometheusParallelShadowTrading':
        """Resume a previous session from database"""
        try:
            db = sqlite3.connect(db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                SELECT config_name, starting_capital, current_capital, max_position_pct, config_json
                FROM shadow_sessions
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Session {session_id} not found")

            config_name, starting_capital, current_capital, max_position_pct, config_json = row

            # Create instance with same session_id (will load existing data)
            instance = cls(
                starting_capital=starting_capital,
                max_position_pct=max_position_pct,
                session_id=session_id,
                config_name=config_name
            )

            # Restore current capital
            instance.current_capital = current_capital

            # Restore config if available
            if config_json:
                try:
                    config = json.loads(config_json)
                    for key, value in config.items():
                        if hasattr(instance, key):
                            setattr(instance, key, value)
                except:
                    pass

            db.close()

            logger.info(f"📂 Resumed session: {session_id}")
            logger.info(f"   Config: {config_name}")
            logger.info(f"   Capital: ${current_capital:,.2f}")

            return instance

        except Exception as e:
            logger.error(f"❌ Could not resume session {session_id}: {e}")
            raise

    def end_session(self, status: str = "COMPLETED"):
        """End this session and mark it in database"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                UPDATE shadow_sessions
                SET status = ?,
                    last_active = ?,
                    current_capital = ?,
                    total_trades = ?,
                    winning_trades = ?,
                    total_pnl = ?,
                    win_rate = ?
                WHERE session_id = ?
            """, (
                status,
                datetime.now().isoformat(),
                self.current_capital,
                self.metrics.total_trades,
                self.metrics.winning_trades,
                self.metrics.total_pnl,
                self.metrics.win_rate,
                self.session_id
            ))

            db.commit()
            db.close()

            logger.info(f"📝 Session ended: {self.session_id} (status: {status})")

        except Exception as e:
            logger.warning(f"⚠️ Could not end session: {e}")

    # ==================== CONFIGURATION PRESETS ====================

    # Predefined configurations for A/B testing
    CONFIG_PRESETS = {
        'conservative': {
            'description': 'Lower risk, tighter stops, less aggressive enhancements',
            'max_position_pct': 0.05,  # 5%
            'trailing_stop_trigger': 0.015,  # +1.5%
            'trailing_stop_distance': 0.005,  # 0.5%
            'dca_enabled': False,  # No averaging down
            'dca_max_adds': 0,
            'scale_out_first_pct': 0.01,  # +1%
            'scale_out_second_pct': 0.02,  # +2%
            'max_correlated_positions': 1,
        },
        'moderate': {
            'description': 'Balanced risk/reward, standard enhancements',
            'max_position_pct': 0.10,  # 10%
            'trailing_stop_trigger': 0.02,  # +2%
            'trailing_stop_distance': 0.01,  # 1%
            'dca_enabled': True,
            'dca_max_adds': 1,
            'scale_out_first_pct': 0.015,  # +1.5%
            'scale_out_second_pct': 0.03,  # +3%
            'max_correlated_positions': 2,
        },
        'aggressive': {
            'description': 'Higher risk, wider stops, more aggressive DCA',
            'max_position_pct': 0.15,  # 15%
            'trailing_stop_trigger': 0.03,  # +3%
            'trailing_stop_distance': 0.015,  # 1.5%
            'dca_enabled': True,
            'dca_max_adds': 3,
            'dca_trigger_pct': -0.03,  # -3%
            'scale_out_first_pct': 0.02,  # +2%
            'scale_out_second_pct': 0.05,  # +5%
            'max_correlated_positions': 3,
        },
        'scalping': {
            'description': 'Quick exits, tight stops, no DCA',
            'max_position_pct': 0.08,  # 8%
            'trailing_stop_trigger': 0.008,  # +0.8%
            'trailing_stop_distance': 0.003,  # 0.3%
            'dca_enabled': False,
            'scale_out_enabled': False,  # No scale-out, all or nothing
            'max_hold_days_crypto': 1,  # Exit next day
            'max_hold_days_stock': 1,
        },
        'swing_trader': {
            'description': 'Longer holds, wider targets, patient',
            'max_position_pct': 0.12,  # 12%
            'trailing_stop_trigger': 0.05,  # +5%
            'trailing_stop_distance': 0.02,  # 2%
            'dca_enabled': True,
            'dca_max_adds': 2,
            'scale_out_first_pct': 0.03,  # +3%
            'scale_out_second_pct': 0.06,  # +6%
            'max_hold_days_crypto': 7,  # Hold up to a week
            'max_hold_days_stock': 14,  # Hold up to 2 weeks
        },
        'no_enhancements': {
            'description': 'Baseline - no enhancements, just TP/SL',
            'trailing_stop_enabled': False,
            'dca_enabled': False,
            'time_exit_enabled': False,
            'scale_out_enabled': False,
            'correlation_filter_enabled': False,
            'sentiment_filter_enabled': False,
        }
    }

    @classmethod
    def create_with_preset(cls, preset_name: str, starting_capital: float = 100000.0,
                          session_id: str = None) -> 'PrometheusParallelShadowTrading':
        """
        Create a shadow trading instance with a predefined configuration preset.

        Args:
            preset_name: Name of preset (conservative, moderate, aggressive, scalping, swing_trader, no_enhancements)
            starting_capital: Initial capital
            session_id: Optional custom session ID

        Returns:
            Configured PrometheusParallelShadowTrading instance
        """
        if preset_name not in cls.CONFIG_PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(cls.CONFIG_PRESETS.keys())}")

        config = cls.CONFIG_PRESETS[preset_name]

        # Create instance
        instance = cls(
            starting_capital=starting_capital,
            max_position_pct=config.get('max_position_pct', 0.10),
            session_id=session_id,
            config_name=preset_name
        )

        # Apply all config values
        for key, value in config.items():
            if key != 'description' and hasattr(instance, key):
                setattr(instance, key, value)

        logger.info(f"🔧 Created session with preset: {preset_name}")
        logger.info(f"   {config.get('description', 'No description')}")

        return instance

    @classmethod
    def create_ab_test_sessions(cls, starting_capital: float = 100000.0) -> Dict[str, 'PrometheusParallelShadowTrading']:
        """
        Create multiple shadow trading sessions for A/B testing all presets.

        Returns:
            Dictionary of preset_name -> instance
        """
        sessions = {}
        for preset_name in cls.CONFIG_PRESETS.keys():
            sessions[preset_name] = cls.create_with_preset(
                preset_name=preset_name,
                starting_capital=starting_capital
            )

        logger.info(f"🧪 Created {len(sessions)} A/B test sessions")
        return sessions

    def apply_custom_config(self, config: Dict):
        """Apply a custom configuration dictionary to this session"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"   Set {key} = {value}")

        # Update config in database
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                UPDATE shadow_sessions
                SET config_json = ?
                WHERE session_id = ?
            """, (json.dumps(self._get_config_dict()), self.session_id))

            db.commit()
            db.close()

            logger.info(f"🔧 Custom config applied and saved")

        except Exception as e:
            logger.warning(f"⚠️ Could not save custom config: {e}")

    # ==================== AI SYSTEM INITIALIZATION ====================

    def _init_hrm(self):
        """Initialize HRM Official Integration"""
        if self._hrm_adapter is None:
            try:
                from core.hrm_official_integration import get_official_hrm_adapter
                self._hrm_adapter = get_official_hrm_adapter()
                logger.info("✅ HRM Official Integration loaded")
            except Exception as e:
                logger.warning(f"⚠️ HRM not available: {e}")
        return self._hrm_adapter

    def _init_universal_reasoning(self):
        """Initialize Universal Reasoning Engine"""
        if self._universal_reasoning is None:
            try:
                from core.universal_reasoning_engine import UniversalReasoningEngine
                self._universal_reasoning = UniversalReasoningEngine()
                logger.info("✅ Universal Reasoning Engine loaded")
            except Exception as e:
                logger.warning(f"⚠️ Universal Reasoning not available: {e}")
        return self._universal_reasoning

    def _init_visual_patterns(self):
        """Initialize Visual Pattern Provider"""
        if self._visual_patterns is None:
            try:
                from core.visual_pattern_provider import get_visual_pattern_provider
                self._visual_patterns = get_visual_pattern_provider()
                logger.info(f"✅ Visual Pattern Provider loaded ({len(self._visual_patterns.patterns)} patterns)")
            except Exception as e:
                logger.warning(f"⚠️ Visual Patterns not available: {e}")
        return self._visual_patterns

    def _init_market_oracle(self):
        """Initialize Market Oracle Engine"""
        if self._market_oracle is None:
            try:
                from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
                # Market Oracle Engine requires config (same as live trading)
                oracle_config = {
                    'ragflow_api_key': os.getenv('RAGFLOW_API_KEY', 'demo_key'),
                    'ragflow_base_url': os.getenv('RAGFLOW_BASE_URL', 'http://localhost:9380'),
                    'prediction_horizon': '24h',
                    'confidence_threshold': 0.72
                }
                self._market_oracle = MarketOracleEngine(oracle_config)
                logger.info("✅ Market Oracle Engine loaded")
            except Exception as e:
                logger.warning(f"⚠️ Market Oracle not available: {e}")
        return self._market_oracle

    def _init_quantum_engine(self):
        """Initialize Quantum Trading Engine"""
        if self._quantum_engine is None:
            try:
                from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
                # Quantum Trading Engine requires config (same as live trading)
                quantum_config = {
                    'portfolio': {
                        'max_qubits': 50,
                        'optimization_level': 'high'
                    },
                    'risk': {
                        'max_risk_qubits': 20
                    },
                    'arbitrage': {
                        'detection_sensitivity': 0.001
                    }
                }
                self._quantum_engine = QuantumTradingEngine(quantum_config)
                logger.info("✅ Quantum Trading Engine loaded")
            except Exception as e:
                logger.warning(f"⚠️ Quantum Engine not available: {e}")
        return self._quantum_engine

    def _init_gpt_oss(self):
        """Initialize GPT-OSS Trading Adapter"""
        if self._gpt_oss is None:
            try:
                from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
                self._gpt_oss = GPTOSSTradingAdapter()
                logger.info("✅ GPT-OSS Engine loaded")
            except Exception as e:
                logger.warning(f"⚠️ GPT-OSS not available: {e}")
        return self._gpt_oss

    def _init_agent_coordinator(self):
        """Initialize Hierarchical Agent Coordinator"""
        if self._agent_coordinator is None:
            try:
                from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
                self._agent_coordinator = HierarchicalAgentCoordinator()
                logger.info("✅ Hierarchical Agent Coordinator loaded")
            except Exception as e:
                logger.warning(f"⚠️ Agent Coordinator not available: {e}")
        return self._agent_coordinator

    def _init_ai_attribution(self):
        """Initialize AI Attribution Tracker"""
        if self._ai_attribution_tracker is None:
            try:
                from core.ai_attribution_tracker import AIAttributionTracker
                self._ai_attribution_tracker = AIAttributionTracker()
                logger.info("✅ AI Attribution Tracker loaded")
            except Exception as e:
                logger.warning(f"⚠️ AI Attribution not available: {e}")
        return self._ai_attribution_tracker

    # ==================== PHASE 21 AI SYSTEM INITIALIZATION ====================

    def _init_langgraph(self):
        """Initialize LangGraph multi-step trade orchestrator"""
        if self._langgraph_orchestrator is None:
            try:
                from core.langgraph_trading_orchestrator import get_langgraph_orchestrator
                self._langgraph_orchestrator = get_langgraph_orchestrator()
                if self._langgraph_orchestrator and self._langgraph_orchestrator.graph:
                    logger.info("\u2705 LangGraph Trading Orchestrator loaded")
                else:
                    self._langgraph_orchestrator = None
                    logger.warning("\u26a0\ufe0f LangGraph graph not compiled (set LANGGRAPH_ORCHESTRATION=true)")
            except Exception as e:
                logger.warning(f"\u26a0\ufe0f LangGraph not available: {e}")
        return self._langgraph_orchestrator

    def _init_mercury2(self):
        """Initialize Mercury2 diffusion LLM for fast signal generation"""
        if self._mercury2_adapter is None:
            try:
                from core.mercury2_adapter import Mercury2Adapter
                m2 = Mercury2Adapter()
                if m2.is_available():
                    self._mercury2_adapter = m2
                    logger.info("\u2705 Mercury2 Diffusion LLM loaded")
                else:
                    logger.warning("\u26a0\ufe0f Mercury2 not available (no API key)")
            except Exception as e:
                logger.warning(f"\u26a0\ufe0f Mercury2 not available: {e}")
        return self._mercury2_adapter

    def _init_sec_analyzer(self):
        """Initialize LlamaIndex SEC Filings RAG analyzer"""
        if self._sec_analyzer is None:
            try:
                from core.llamaindex_sec_analyzer import get_sec_analyzer
                sa = get_sec_analyzer()
                if sa.is_available():
                    self._sec_analyzer = sa
                    logger.info("\u2705 LlamaIndex SEC Filings RAG loaded")
                else:
                    logger.warning("\u26a0\ufe0f SEC Filings RAG not available")
            except Exception as e:
                logger.warning(f"\u26a0\ufe0f SEC Filings RAG not available: {e}")
        return self._sec_analyzer

    def _init_continuous_learning(self):
        """Initialize Continuous Learning Engine for trading outcome learning"""
        if self._continuous_learning_engine is None:
            try:
                from core.continuous_learning_engine import ContinuousLearningEngine, LearningMode
                self._continuous_learning_engine = ContinuousLearningEngine(LearningMode.BALANCED)
                logger.info("✅ Continuous Learning Engine loaded (BALANCED mode)")
            except Exception as e:
                logger.warning(f"⚠️ Continuous Learning not available: {e}")
        return self._continuous_learning_engine

    def _init_ai_learning(self):
        """Initialize AI Learning Engine for pattern recognition"""
        if self._ai_learning_engine is None:
            try:
                from core.ai_learning_engine import AILearningEngine
                self._ai_learning_engine = AILearningEngine()
                logger.info("✅ AI Learning Engine loaded")
            except Exception as e:
                logger.warning(f"⚠️ AI Learning Engine not available: {e}")
        return self._ai_learning_engine

    # ==================== 2026-03-08: LATEST AI INTEGRATIONS ====================

    def _init_ai_consciousness(self):
        """Initialize AI Consciousness Engine - Latest fine-tuned model"""
        if self._ai_consciousness is None:
            try:
                from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
                self._ai_consciousness = AIConsciousnessEngine()
                logger.info("✅ AI Consciousness Engine loaded (LATEST FINE-TUNED MODEL)")
            except Exception as e:
                logger.warning(f"⚠️ AI Consciousness not available: {e}")
        return self._ai_consciousness

    def _init_rl_agent(self):
        """Initialize Reinforcement Learning Agent - Latest trained model"""
        if self._rl_agent is None:
            try:
                from core.rl_trading_agent import get_rl_agent
                self._rl_agent = get_rl_agent()
                logger.info("✅ RL Trading Agent loaded (LATEST TRAINED MODEL)")
            except Exception as e:
                logger.warning(f"⚠️ RL Agent not available: {e}")
        return self._rl_agent

    def _init_revolutionary_engines(self):
        """Initialize Revolutionary Trading Engines (crypto, options, market maker)"""
        if self._revolutionary_engines is None:
            try:
                # Try importing revolutionary engines
                engines = {}
                try:
                    from revolutionary_crypto_engine import PrometheusRevolutionaryCryptoEngine
                    engines['crypto'] = PrometheusRevolutionaryCryptoEngine()
                except:
                    pass
                try:
                    from revolutionary_options_engine import PrometheusRevolutionaryOptionsEngine
                    engines['options'] = PrometheusRevolutionaryOptionsEngine()
                except:
                    pass
                try:
                    from revolutionary_market_maker import PrometheusRevolutionaryMarketMaker
                    engines['market_maker'] = PrometheusRevolutionaryMarketMaker()
                except:
                    pass
                
                if engines:
                    self._revolutionary_engines = engines
                    logger.info(f"✅ Revolutionary Engines loaded: {list(engines.keys())}")
                else:
                    logger.warning("⚠️ No Revolutionary Engines available")
            except Exception as e:
                logger.warning(f"⚠️ Revolutionary Engines not available: {e}")
        return self._revolutionary_engines

    async def initialize_all_ai_systems(self):
        """Initialize all AI systems for shadow trading"""
        logger.info("\n" + "="*60)
        logger.info("INITIALIZING PROMETHEUS AI SYSTEMS FOR SHADOW TRADING")
        logger.info("="*60)

        systems_loaded = []

        # Core AI Systems
        if self._init_hrm():
            systems_loaded.append("HRM")
        if self._init_universal_reasoning():
            systems_loaded.append("Universal Reasoning")
        if self._init_visual_patterns():
            systems_loaded.append("Visual Patterns")
        if self._init_market_oracle():
            systems_loaded.append("Market Oracle")
        if self._init_quantum_engine():
            systems_loaded.append("Quantum Engine")
        if self._init_gpt_oss():
            systems_loaded.append("GPT-OSS")
        if self._init_agent_coordinator():
            systems_loaded.append("Agent Coordinator")
        if self._init_ai_attribution():
            systems_loaded.append("AI Attribution")

        # Phase 21 AI Voters
        if self._init_langgraph():
            systems_loaded.append("LangGraph Orchestrator")
        if self._init_mercury2():
            systems_loaded.append("Mercury2 LLM")
        if self._init_sec_analyzer():
            systems_loaded.append("SEC Filings RAG")

        # Learning Systems (NEW)
        if self._init_continuous_learning():
            systems_loaded.append("Continuous Learning")
        if self._init_ai_learning():
            systems_loaded.append("AI Learning")

        # 2026-03-08: LATEST AI MODELS (Fine-tuned & Trained)
        if self._init_ai_consciousness():
            systems_loaded.append("AI Consciousness (LATEST)")
        if self._init_rl_agent():
            systems_loaded.append("RL Agent (LATEST)")
        if self._init_revolutionary_engines():
            systems_loaded.append("Revolutionary Engines")

        logger.info(f"\n\u2705 Loaded {len(systems_loaded)} AI systems: {', '.join(systems_loaded)}")
        return systems_loaded

    # ==================== MARKET DATA ====================

    async def get_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch real market data for ALL asset classes"""
        market_data = {}

        for symbol in symbols:
            try:
                # Detect asset class for this symbol
                asset_class = detect_asset_class(symbol)

                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="5m")

                if hist.empty:
                    logger.debug(f"No data for {symbol} ({asset_class.value})")
                    continue

                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-13]) if len(hist) > 13 else current_price

                # Calculate metrics
                momentum = (current_price - prev_close) / prev_close if prev_close > 0 else 0

                # Volume analysis
                avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else hist['Volume'].mean()
                current_volume = hist['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

                # Price volatility
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() if len(returns) > 0 else 0.01

                # SMA signal
                sma_5 = hist['Close'].rolling(window=5).mean().iloc[-1] if len(hist) >= 5 else current_price
                sma_signal = (current_price - sma_5) / sma_5 if sma_5 > 0 else 0

                # RSI-like indicator
                gains = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
                losses = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0.001
                rsi_like = gains / (gains + losses) if (gains + losses) > 0 else 0.5

                # Asset-class specific adjustments
                position_multiplier = 1.0
                if asset_class == AssetClass.CRYPTO:
                    position_multiplier = 0.5  # Smaller positions for volatile crypto
                elif asset_class == AssetClass.FOREX:
                    position_multiplier = 2.0  # Larger positions for forex (smaller moves)

                market_data[symbol] = {
                    'price': current_price,
                    'momentum_5min': momentum,
                    'volume_ratio': volume_ratio,
                    'volatility': volatility,
                    'sma_signal': sma_signal,
                    'rsi_like': rsi_like,
                    'prev_close': prev_close,
                    'high': float(hist['High'].iloc[-1]),
                    'low': float(hist['Low'].iloc[-1]),
                    'volume': current_volume,
                    'timestamp': datetime.now().isoformat(),
                    # NEW: Asset class info for learning
                    'asset_class': asset_class.value,
                    'position_multiplier': position_multiplier,
                    'trend_strength': abs(momentum) * 100  # Normalized trend strength
                }

            except Exception as e:
                logger.debug(f"Failed to get market data for {symbol}: {e}")

        return market_data

    # ==================== AI DECISION MAKING ====================

    async def make_ai_decision(self, symbol: str, market_data: Dict) -> Dict:
        """
        Make trading decision using ALL PROMETHEUS AI systems.
        This mirrors the live trading decision logic exactly.
        """
        price = market_data.get('price', 0)
        if price <= 0:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Invalid price', 'quantity': 0}

        # Track which AI systems contribute to this decision
        ai_components = []
        decision_scores = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        reasons = []

        # Calculate max position size
        max_position_value = self.current_capital * self.max_position_pct
        max_shares = int(max_position_value / price)

        # Get per-system weights from strategy config (11 voters, sum ~1.0)
        w_hrm = self.ai_decision_weights.get('HRM', 0.16)
        w_universal = self.ai_decision_weights.get('Universal_Reasoning', 0.14)
        w_visual = self.ai_decision_weights.get('Visual_Patterns', 0.09)
        w_quantum = self.ai_decision_weights.get('Quantum', 0.09)
        w_technical = self.ai_decision_weights.get('Technical', 0.10)
        w_agents = self.ai_decision_weights.get('Agents', 0.07)
        w_fed_nlp = self.ai_decision_weights.get('Fed_NLP', 0.07)
        w_ml_regime = self.ai_decision_weights.get('ML_Regime', 0.07)
        # Phase 21 voters
        w_langgraph = self.ai_decision_weights.get('LangGraph', 0.08)
        w_mercury2 = self.ai_decision_weights.get('Mercury2', 0.07)
        w_sec_filings = self.ai_decision_weights.get('SEC_Filings', 0.06)

        # ==================== 1. HRM DECISION ====================
        if self._hrm_adapter:
            try:
                from core.hrm_official_integration import get_hrm_decision
                hrm_result = get_hrm_decision(symbol, {
                    'price': price,
                    'momentum': market_data.get('momentum_5min', 0),
                    'volume_ratio': market_data.get('volume_ratio', 1.0)
                })
                if hrm_result:
                    ai_components.append('HRM')
                    action = hrm_result.get('action', 'HOLD')
                    confidence = hrm_result.get('confidence', 0.5)
                    decision_scores[action] += confidence * w_hrm
                    reasons.append(f"HRM: {action} ({confidence:.0%})")
            except Exception as e:
                logger.debug(f"HRM decision failed: {e}")

        # ==================== 2. UNIVERSAL REASONING ====================
        if self._universal_reasoning:
            try:
                context = {
                    'symbol': symbol,
                    'market_data': market_data,
                    'intelligence': {'visual_patterns': [], 'sentiment': 0.5}
                }
                result = self._universal_reasoning.make_ultimate_decision(context)
                if result:
                    ai_components.append('Universal_Reasoning')
                    action = result.get('action', 'HOLD')
                    confidence = result.get('confidence', 0.5)
                    decision_scores[action] += confidence * w_universal
                    reasons.append(f"Universal: {action} ({confidence:.0%})")
            except Exception as e:
                logger.debug(f"Universal Reasoning failed: {e}")

        # ==================== 3. VISUAL PATTERNS ====================
        if self._visual_patterns:
            try:
                patterns = self._visual_patterns.get_patterns_for_symbol(symbol)
                if patterns:
                    ai_components.append('Visual_Patterns')
                    bullish = ['bull flag', 'ascending', 'double bottom', 'cup and handle']
                    bearish = ['head and shoulders', 'descending', 'double top', 'bear flag']

                    for p in patterns:
                        pattern_name = p.get('pattern', '').lower()
                        conf = p.get('confidence', 0.5)

                        if any(bp in pattern_name for bp in bullish):
                            decision_scores['BUY'] += conf * w_visual
                            reasons.append(f"Visual: {p.get('pattern')} bullish")
                            break
                        elif any(bp in pattern_name for bp in bearish):
                            decision_scores['SELL'] += conf * w_visual
                            reasons.append(f"Visual: {p.get('pattern')} bearish")
                            break
            except Exception as e:
                logger.debug(f"Visual patterns failed: {e}")

        # ==================== 4. QUANTUM ENGINE ====================
        if self._quantum_engine:
            try:
                # Quantum portfolio optimization
                quantum_result = self._quantum_engine.optimize_position(
                    symbol=symbol,
                    current_price=price,
                    portfolio_value=self.current_capital
                )
                if quantum_result:
                    ai_components.append('Quantum')
                    opt_action = quantum_result.get('action', 'HOLD')
                    opt_conf = quantum_result.get('confidence', 0.5)
                    decision_scores[opt_action] += opt_conf * w_quantum
                    reasons.append(f"Quantum: {opt_action} ({opt_conf:.0%})")
            except Exception as e:
                logger.debug(f"Quantum engine failed: {e}")

        # ==================== 5. TECHNICAL ANALYSIS (Built-in) ====================
        ai_components.append('Technical_Analysis')
        momentum = market_data.get('momentum_5min', 0)
        rsi_like = market_data.get('rsi_like', 0.5)
        volume_ratio = market_data.get('volume_ratio', 1.0)

        tech_score = 0
        if momentum > 0.005 and volume_ratio > 1.2:
            tech_score = 0.7
            decision_scores['BUY'] += tech_score * w_technical
            reasons.append(f"Tech: Momentum + Volume")
        elif momentum < -0.005 and rsi_like > 0.7:
            tech_score = 0.7
            decision_scores['SELL'] += tech_score * w_technical
            reasons.append(f"Tech: Overbought reversal")
        elif rsi_like < 0.3:
            tech_score = 0.6
            decision_scores['BUY'] += tech_score * (w_technical * 0.67)
            reasons.append(f"Tech: Oversold")

        # ==================== 6. MARKET INTELLIGENCE AGENTS ====================
        if self._agent_coordinator:
            try:
                agent_result = await self._agent_coordinator.coordinate_analysis(symbol, market_data)
                if agent_result:
                    ai_components.append('Market_Intelligence')
                    consensus = agent_result.get('consensus', 'HOLD')
                    agent_conf = agent_result.get('confidence', 0.5)
                    decision_scores[consensus] += agent_conf * w_agents
                    reasons.append(f"Agents: {consensus}")
            except Exception as e:
                logger.debug(f"Agent coordinator failed: {e}")

        # ==================== 7. FED NLP POLICY SIGNAL ====================
        try:
            from core.fed_nlp_analyzer import FedNLPAnalyzer
            fed_analyzer = FedNLPAnalyzer()
            fed_signal = fed_analyzer.get_latest_signal()
            if fed_signal and fed_signal.get('tone_score') is not None:
                ai_components.append('Fed_NLP')
                tone = fed_signal['tone_score']  # -1.0 (hawkish) to +1.0 (dovish)
                fed_conf = min(abs(tone), 1.0) * 0.8 + 0.2  # map to 0.2-1.0 confidence

                if tone > 0.2:
                    # Dovish = bullish for stocks (rate cuts expected)
                    decision_scores['BUY'] += fed_conf * w_fed_nlp
                    reasons.append(f"Fed NLP: Dovish ({tone:+.2f})")
                elif tone < -0.2:
                    # Hawkish = bearish/cautious (rate hikes expected)
                    decision_scores['SELL'] += fed_conf * w_fed_nlp * 0.6
                    decision_scores['HOLD'] += fed_conf * w_fed_nlp * 0.4
                    reasons.append(f"Fed NLP: Hawkish ({tone:+.2f})")
                else:
                    # Neutral - slight HOLD bias
                    decision_scores['HOLD'] += 0.3 * w_fed_nlp
                    reasons.append(f"Fed NLP: Neutral ({tone:+.2f})")
        except Exception as e:
            logger.debug(f"Fed NLP voter failed: {e}")

        # ==================== 8. ML REGIME DETECTOR ====================
        try:
            from core.ml_regime_detector import MLRegimeDetector
            regime_detector = MLRegimeDetector()
            regime_result = regime_detector.predict_regime()
            if regime_result and regime_result.get('regime'):
                ai_components.append('ML_Regime')
                regime = regime_result['regime']  # BULL, BEAR, VOLATILE, SIDEWAYS
                regime_conf = regime_result.get('confidence', 0.5)

                if regime == 'BULL':
                    # Bull regime favors buying
                    decision_scores['BUY'] += regime_conf * w_ml_regime
                    reasons.append(f"Regime: BULL ({regime_conf:.0%})")
                elif regime == 'BEAR':
                    # Bear regime favors selling/holding
                    decision_scores['SELL'] += regime_conf * w_ml_regime * 0.6
                    decision_scores['HOLD'] += regime_conf * w_ml_regime * 0.4
                    reasons.append(f"Regime: BEAR ({regime_conf:.0%})")
                elif regime == 'VOLATILE':
                    # Volatile = reduce exposure, favor HOLD
                    decision_scores['HOLD'] += regime_conf * w_ml_regime * 0.7
                    decision_scores['SELL'] += regime_conf * w_ml_regime * 0.3
                    reasons.append(f"Regime: VOLATILE ({regime_conf:.0%})")
                elif regime == 'SIDEWAYS':
                    # Sideways = mean reversion, mild HOLD
                    decision_scores['HOLD'] += regime_conf * w_ml_regime * 0.6
                    decision_scores['BUY'] += regime_conf * w_ml_regime * 0.2
                    decision_scores['SELL'] += regime_conf * w_ml_regime * 0.2
                    reasons.append(f"Regime: SIDEWAYS ({regime_conf:.0%})")
        except Exception as e:
            logger.debug(f"ML Regime voter failed: {e}")

        # ==================== 9. LANGGRAPH MULTI-STEP ORCHESTRATOR ====================
        if self._langgraph_orchestrator:
            try:
                lg_result = self._langgraph_orchestrator.make_decision(
                    symbol=symbol,
                    price=price,
                    volume=market_data.get('volume_ratio', 1.0),
                    indicators={
                        'momentum': market_data.get('momentum_5min', 0),
                        'rsi': market_data.get('rsi_like', 0.5),
                        'volume_ratio': market_data.get('volume_ratio', 1.0),
                    }
                )
                if lg_result and lg_result.get('action'):
                    ai_components.append('LangGraph')
                    lg_action = lg_result['action'].upper()
                    if lg_action not in decision_scores:
                        lg_action = 'HOLD'
                    lg_conf = lg_result.get('confidence', 0.5)
                    decision_scores[lg_action] += lg_conf * w_langgraph
                    reasons.append(f"LangGraph: {lg_action} ({lg_conf:.0%})")
            except Exception as e:
                logger.debug(f"LangGraph voter failed: {e}")

        # ==================== 10. MERCURY2 DIFFUSION LLM ====================
        if self._mercury2_adapter:
            try:
                m2_prompt = (
                    f"Trading signal for {symbol}: price=${price:.2f}, "
                    f"momentum={market_data.get('momentum_5min', 0):.4f}, "
                    f"RSI={market_data.get('rsi_like', 0.5):.2f}, "
                    f"volume_ratio={market_data.get('volume_ratio', 1.0):.2f}. "
                    f"Respond with ONLY one word: BUY, SELL, or HOLD."
                )
                m2_raw = self._mercury2_adapter.generate(m2_prompt, max_tokens=10)
                if m2_raw:
                    m2_text = m2_raw.strip().upper()
                    m2_action = 'HOLD'
                    if 'BUY' in m2_text:
                        m2_action = 'BUY'
                    elif 'SELL' in m2_text:
                        m2_action = 'SELL'
                    ai_components.append('Mercury2')
                    decision_scores[m2_action] += 0.6 * w_mercury2
                    reasons.append(f"Mercury2: {m2_action}")
            except Exception as e:
                logger.debug(f"Mercury2 voter failed: {e}")

        # ==================== 11. SEC FILINGS RAG (Fundamentals) ====================
        if self._sec_analyzer:
            try:
                # Only query SEC for stocks (not crypto/forex)
                asset_class = market_data.get('asset_class', 'stock')
                if asset_class in ('stock', 'etf', None):
                    sec_result = self._sec_analyzer.query(
                        symbol, "Is the company financially healthy? Revenue trend and risk factors. Answer: bullish, bearish, or neutral."
                    )
                    if sec_result and sec_result.get('success'):
                        sec_text = sec_result.get('answer', '').lower()
                        sec_action = 'HOLD'
                        if 'bullish' in sec_text or 'strong revenue' in sec_text or 'healthy' in sec_text:
                            sec_action = 'BUY'
                        elif 'bearish' in sec_text or 'declining' in sec_text or 'risk' in sec_text:
                            sec_action = 'SELL'
                        ai_components.append('SEC_Filings')
                        decision_scores[sec_action] += 0.6 * w_sec_filings
                        reasons.append(f"SEC: {sec_action}")
            except Exception as e:
                logger.debug(f"SEC Filings voter failed: {e}")

        # ==================== 2026-03-08: LATEST AI MODELS ====================

        # Get weights for new AI systems
        w_consciousness = self.ai_decision_weights.get('AI_Consciousness', 0.18)
        w_rl_agent = self.ai_decision_weights.get('RL_Agent', 0.16)
        w_revolutionary = self.ai_decision_weights.get('Revolutionary', 0.14)

        # ==================== AI CONSCIOUSNESS ENGINE ====================
        if self._ai_consciousness:
            try:
                if hasattr(self._ai_consciousness, 'analyze_market_awareness'):
                    awareness = self._ai_consciousness.analyze_market_awareness(symbol, market_data)
                    if awareness:
                        cons_action = awareness.get('recommended_action', 'HOLD')
                        cons_conf = awareness.get('confidence', 0.6)
                        ai_components.append('AI_Consciousness')
                        decision_scores[cons_action] += cons_conf * 1.1 * w_consciousness  # 1.1x multiplier for proven fine-tuned model
                        reasons.append(f"Consciousness: {awareness.get('market_state', 'analyzing')}")
            except Exception as e:
                logger.debug(f"AI Consciousness voter failed: {e}")

        # ==================== RL TRADING AGENT ====================
        if self._rl_agent:
            try:
                if hasattr(self._rl_agent, 'get_action'):
                    # Create state vector for RL agent
                    state = {
                        'price': price,
                        'momentum': market_data.get('momentum_5min', 0),
                        'rsi': market_data.get('rsi_like', 0.5),
                        'volume_ratio': market_data.get('volume_ratio', 1.0),
                        'volatility': market_data.get('volatility', 0.01)
                    }
                    rl_result = self._rl_agent.get_action(symbol, state)
                    if rl_result:
                        rl_action = rl_result.get('action', 'HOLD')
                        rl_conf = rl_result.get('confidence', 0.6)
                        ai_components.append('RL_Agent')
                        decision_scores[rl_action] += rl_conf * 1.15 * w_rl_agent  # 1.15x multiplier for trained RL model
                        reasons.append(f"RL Agent: {rl_action} ({rl_conf:.0%})")
            except Exception as e:
                logger.debug(f"RL Agent voter failed: {e}")

        # ==================== REVOLUTIONARY ENGINES ====================
        if self._revolutionary_engines:
            try:
                asset_class = market_data.get('asset_class', 'stock')
                rev_signal = None
                
                # Route to appropriate engine based on asset class
                if asset_class in ('crypto', 'cryptocurrency') and 'crypto' in self._revolutionary_engines:
                    crypto_engine = self._revolutionary_engines['crypto']
                    if hasattr(crypto_engine, 'analyze_crypto_opportunity'):
                        rev_signal = crypto_engine.analyze_crypto_opportunity(symbol, market_data)
                elif asset_class in ('options', 'option') and 'options' in self._revolutionary_engines:
                    options_engine = self._revolutionary_engines['options']
                    if hasattr(options_engine, 'analyze_options_opportunity'):
                        rev_signal = options_engine.analyze_options_opportunity(symbol, market_data)
                elif 'market_maker' in self._revolutionary_engines:
                    mm_engine = self._revolutionary_engines['market_maker']
                    if hasattr(mm_engine, 'get_market_making_signal'):
                        rev_signal = mm_engine.get_market_making_signal(symbol, price)
                
                if rev_signal:
                    rev_action = rev_signal.get('action', 'HOLD')
                    rev_conf = rev_signal.get('confidence', 0.6)
                    ai_components.append('Revolutionary')
                    decision_scores[rev_action] += rev_conf * 1.2 * w_revolutionary  # 1.2x multiplier for specialized engines
                    reasons.append(f"Revolutionary: {rev_action} ({rev_conf:.0%})")
            except Exception as e:
                logger.debug(f"Revolutionary Engines voter failed: {e}")

        # ==================== FINAL DECISION ====================
        # Find highest scoring action
        best_action = max(decision_scores, key=decision_scores.get)
        best_score = decision_scores[best_action]

        # Calculate overall confidence (normalized)
        total_score = sum(decision_scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.5

        # Apply minimum confidence threshold (configurable per strategy)
        if confidence < self.min_decision_confidence or best_score < self.min_decision_score:
            best_action = 'HOLD'
            confidence = 0.5

        # Determine quantity
        quantity = 0
        if best_action == 'BUY':
            quantity = max_shares
        elif best_action == 'SELL':
            # Check if we have positions to sell
            if symbol in self.open_positions and self.open_positions[symbol]:
                quantity = sum(t.quantity for t in self.open_positions[symbol])
            else:
                best_action = 'HOLD'
                quantity = 0

        # Calculate target and stop loss (configurable per strategy)
        target_price = price * (1 + self.target_pct) if best_action == 'BUY' else price * (1 - self.target_pct)
        stop_loss = price * (1 - self.stop_loss_pct) if best_action == 'BUY' else price * (1 + self.stop_loss_pct)

        return {
            'action': best_action,
            'confidence': min(0.95, max(0.5, confidence)),
            'quantity': quantity,
            'reason': ' | '.join(reasons[:5]) if reasons else 'No strong signals',
            'target_price': target_price,
            'stop_loss': stop_loss,
            'ai_components': ai_components,
            'decision_scores': decision_scores
        }

    # ==================== TRADE EXECUTION ====================

    async def execute_shadow_trade(self, symbol: str, decision: Dict, market_data: Dict) -> Optional[ShadowTrade]:
        """Execute a shadow (paper) trade with full asset class and learning support"""
        if decision['action'] == 'HOLD' or decision['quantity'] == 0:
            return None

        price = market_data.get('price', 0)
        if price <= 0:
            return None

        # ═══════════════════════════════════════════════════════════════
        # � DUPLICATE ENTRY PREVENTION - Skip BUY if position already open
        # ═══════════════════════════════════════════════════════════════
        if decision['action'] == 'BUY' and symbol in self.open_positions and self.open_positions[symbol]:
            logger.debug(f"⏭️ {symbol}: Skipping BUY - already have open position ({len(self.open_positions[symbol])} trades)")
            return None

        # ═══════════════════════════════════════════════════════════════
        # �🚀 ENHANCEMENT 5 & 6: ENTRY FILTERS - Check before new BUY trades
        # ═══════════════════════════════════════════════════════════════
        if decision['action'] == 'BUY':
            # Check sentiment filter (Fed meeting days)
            if self._check_sentiment_filter():
                logger.info(f"⏭️ {symbol}: Skipping BUY - Fed meeting day filter")
                return None

            # Check correlation filter
            if self._check_correlation_filter(symbol):
                logger.info(f"⏭️ {symbol}: Skipping BUY - Correlation filter")
                return None

        # Get asset class
        asset_class = market_data.get('asset_class', detect_asset_class(symbol).value)
        trade_id = f"SHADOW_{asset_class.upper()}_{symbol}_{int(time.time())}"

        trade = ShadowTrade(
            trade_id=trade_id,
            timestamp=datetime.now(),
            symbol=symbol,
            action=decision['action'],
            quantity=decision['quantity'],
            entry_price=price,
            target_price=decision['target_price'],
            stop_loss=decision['stop_loss'],
            confidence=decision['confidence'],
            reason=decision['reason'],
            ai_components=decision.get('ai_components', []),
            asset_class=asset_class,  # NEW: Store asset class
            market_conditions={  # NEW: Store market conditions for learning
                'volatility': market_data.get('volatility', 0),
                'volume_ratio': market_data.get('volume_ratio', 1),
                'momentum': market_data.get('momentum_5min', 0),
                'rsi_like': market_data.get('rsi_like', 0.5),
                'trend_strength': market_data.get('trend_strength', 0)
            }
        )

        # Record the trade
        self.shadow_trades.append(trade)
        self.open_positions[symbol].append(trade)
        self.trades_today += 1

        # 💾 Save trade to database for persistence
        self._save_shadow_trade(trade)
        self._store_shadow_signal_prediction(trade)

        # Initialize position tracking for enhancements
        if decision['action'] == 'BUY':
            self.position_highs[symbol] = price  # Start tracking high
            self.position_entry_times[symbol] = datetime.now()  # Track entry time
            self.scaled_positions[symbol] = 0  # No scale-out yet
            self.dca_counts[symbol] = 0  # No DCA yet
            # 💾 Save position tracking to database
            self._save_shadow_position_tracking(symbol)

        # Track AI attribution
        if self._ai_attribution_tracker:
            try:
                await self._ai_attribution_tracker.record_signal(
                    symbol=symbol,
                    ai_components=trade.ai_components,
                    vote_breakdown=decision.get('decision_scores', {}),
                    action=trade.action,
                    confidence=trade.confidence,
                    entry_price=price,
                    trade_id=trade_id
                )
            except Exception as e:
                logger.debug(f"AI attribution recording failed: {e}")

        logger.info(f"\n🔄 SHADOW TRADE EXECUTED:")
        logger.info(f"   Trade ID: {trade_id}")
        logger.info(f"   Asset Class: {asset_class.upper()}")
        logger.info(f"   {trade.action} {trade.quantity} units of {symbol}")
        logger.info(f"   Entry: ${price:.2f}")
        logger.info(f"   Target: ${trade.target_price:.2f} | Stop: ${trade.stop_loss:.2f}")
        logger.info(f"   Confidence: {trade.confidence:.1%}")
        logger.info(f"   AI Systems: {', '.join(trade.ai_components)}")
        logger.info(f"   Reason: {trade.reason[:80]}...")

        return trade

    # ==================== POSITION MONITORING ====================

    async def monitor_positions(self) -> List[ShadowTrade]:
        """Monitor open positions and close when exit conditions are met"""
        closed_trades = []

        for symbol, trades in list(self.open_positions.items()):
            if not trades:
                continue

            # Get current price
            try:
                ticker = yf.Ticker(symbol)
                current_price = ticker.fast_info.get('lastPrice') or ticker.fast_info.get('last_price')
                if not current_price:
                    hist = ticker.history(period="1d", interval="1m")
                    current_price = float(hist['Close'].iloc[-1]) if not hist.empty else None
            except:
                current_price = None

            if not current_price:
                continue

            for trade in trades[:]:  # Copy list to allow modification
                if trade.status == 'CLOSED':
                    continue

                # Check exit conditions
                should_exit = False
                exit_reason = ""
                partial_exit = False
                partial_qty = 0

                # Calculate P/L for this position
                pnl_pct = (current_price - trade.entry_price) / trade.entry_price if trade.entry_price > 0 else 0

                # Is this crypto or stock?
                is_crypto = trade.asset_class == 'crypto' or symbol in CRYPTO_SYMBOLS

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 1: TRAILING STOP - Lock in profits
                # ═══════════════════════════════════════════════════════════════
                if self.trailing_stop_enabled:
                    # Track position high
                    if symbol not in self.position_highs:
                        self.position_highs[symbol] = current_price
                    else:
                        self.position_highs[symbol] = max(self.position_highs[symbol], current_price)
                    high_price = self.position_highs[symbol]

                    # Check trailing stop trigger
                    if pnl_pct >= self.trailing_stop_trigger:
                        drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                        if drop_from_high >= self.trailing_stop_distance:
                            should_exit = True
                            high_pnl = (high_price - trade.entry_price) / trade.entry_price if trade.entry_price > 0 else 0
                            exit_reason = f"TRAILING_STOP (was +{high_pnl*100:.1f}%, now +{pnl_pct*100:.1f}%)"

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 4: SCALE-OUT - Partial profit taking
                # ═══════════════════════════════════════════════════════════════
                if self.scale_out_enabled and not should_exit:
                    scaled_level = self.scaled_positions.get(symbol, 0)

                    # First scale-out at +1.5%
                    if pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                        partial_exit = True
                        partial_qty = trade.quantity * 0.5  # Sell 50%
                        self.scaled_positions[symbol] = 1
                        exit_reason = f"SCALE_OUT_1 (+{pnl_pct*100:.1f}%)"
                        self._save_shadow_position_tracking(symbol)  # 💾 Persist scale-out

                    # Second scale-out at +3%
                    elif pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                        should_exit = True
                        self.scaled_positions[symbol] = 2
                        exit_reason = f"SCALE_OUT_2 (+{pnl_pct*100:.1f}%)"
                        self._save_shadow_position_tracking(symbol)  # 💾 Persist scale-out

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 3: TIME-BASED EXIT - Don't hold losers forever
                # ═══════════════════════════════════════════════════════════════
                if self.time_exit_enabled and not should_exit and not partial_exit:
                    time_held = datetime.now() - trade.timestamp
                    days_held = time_held.days
                    max_days = self.max_hold_days_crypto if is_crypto else self.max_hold_days_stock

                    if days_held >= max_days and pnl_pct < self.scale_out_first_pct:
                        should_exit = True
                        exit_reason = f"TIME_EXIT ({days_held}d >= {max_days}d max)"

                # ═══════════════════════════════════════════════════════════════
                # STANDARD EXIT CONDITIONS (Target/Stop)
                # ═══════════════════════════════════════════════════════════════
                if not should_exit and not partial_exit:
                    if trade.action == 'BUY':
                        if current_price >= trade.target_price:
                            should_exit = True
                            exit_reason = "TARGET_HIT"
                        elif current_price <= trade.stop_loss:
                            should_exit = True
                            exit_reason = "STOP_LOSS"
                    else:  # SELL
                        if current_price <= trade.target_price:
                            should_exit = True
                            exit_reason = "TARGET_HIT"
                        elif current_price >= trade.stop_loss:
                            should_exit = True
                            exit_reason = "STOP_LOSS"

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 2: DCA ON DIPS - Buy more to average down
                # ═══════════════════════════════════════════════════════════════
                if self.dca_enabled and pnl_pct <= self.dca_trigger_pct and not should_exit:
                    dca_count = self.dca_counts.get(symbol, 0)
                    if dca_count < self.dca_max_adds:
                        # Calculate DCA buy amount
                        dca_amount = self.current_capital * self.dca_position_pct
                        if dca_amount >= 100:  # Min $100 DCA for shadow
                            dca_qty = dca_amount / current_price if current_price > 0 else 0
                            if dca_qty > 0:
                                # Execute shadow DCA
                                trade.quantity += dca_qty
                                # Update average price
                                old_value = trade.entry_price * (trade.quantity - dca_qty)
                                new_value = current_price * dca_qty
                                trade.entry_price = (old_value + new_value) / trade.quantity
                                self.dca_counts[symbol] = dca_count + 1
                                # 💾 Persist DCA to database
                                self._save_shadow_position_tracking(symbol)
                                self._save_shadow_trade(trade)  # Update trade with new quantity/avg price
                                logger.info(f"📉 {symbol}: SHADOW DCA #{dca_count+1} - added {dca_qty:.4f} @ ${current_price:.2f}")

                if should_exit or partial_exit:
                    if partial_exit:
                        # Partial exit (scale-out) - reduce position
                        exit_qty = trade.quantity * 0.5
                        partial_pnl = (current_price - trade.entry_price) * exit_qty
                        partial_pnl_pct = pnl_pct * 100

                        # Update capital with partial profit
                        self.current_capital += partial_pnl
                        trade.quantity -= exit_qty

                        logger.info(f"\n📊 SHADOW SCALE-OUT:")
                        logger.info(f"   {symbol}: Sold 50% @ ${current_price:.2f}")
                        logger.info(f"   Partial P/L: ${partial_pnl:.2f} ({partial_pnl_pct:+.2f}%)")
                        logger.info(f"   Remaining: {trade.quantity:.4f} units")
                    else:
                        # Full exit - close the position
                        trade.exit_price = current_price
                        trade.exit_time = datetime.now()
                        trade.exit_reason = exit_reason
                        trade.status = 'CLOSED'

                        # Calculate P/L
                        if trade.action == 'BUY':
                            trade.pnl = (current_price - trade.entry_price) * trade.quantity
                            trade.pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                        else:
                            trade.pnl = (trade.entry_price - current_price) * trade.quantity
                            trade.pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100

                        # Update capital
                        self.current_capital += trade.pnl

                        # Remove from open positions
                        self.open_positions[symbol].remove(trade)
                        closed_trades.append(trade)

                        # Clean up position tracking
                        self._cleanup_position_tracking(symbol)

                        # 💾 Save closed trade to database and update session metrics
                        self._save_shadow_trade(trade)
                        self._persist_shadow_learning_outcome(trade)
                        self._mark_signal_outcome_recorded(trade)
                        self.calculate_metrics()  # Recalculate totals before persisting
                        self._update_session_metrics()
                        self._maybe_trigger_shadow_risk_adaptation()

                        # Update AI attribution (existing records + new shadow entries)
                        if self._ai_attribution_tracker:
                            try:
                                await self._ai_attribution_tracker.record_outcome(
                                    symbol=trade.symbol,
                                    pnl=trade.pnl,
                                    pnl_pct=trade.pnl_pct,
                                    trade_id=trade.trade_id
                                )
                            except:
                                pass
                            # Also create NEW attribution entries from shadow outcomes
                            # so shadow results feed into weight calculations
                            try:
                                await self._ai_attribution_tracker.record_shadow_outcome(
                                    symbol=trade.symbol,
                                    pnl=trade.pnl,
                                    pnl_pct=trade.pnl_pct,
                                    ai_components=trade.ai_components or [],
                                    confidence=trade.confidence,
                                    entry_price=trade.entry_price,
                                    action=trade.action,
                                )
                            except Exception:
                                pass

                        # Feed to Continuous Learning Engine (NEW)
                        if self._continuous_learning_engine:
                            try:
                                from core.continuous_learning_engine import TradingOutcome
                                outcome = TradingOutcome(
                                    trade_id=trade.trade_id,
                                    timestamp=trade.timestamp,
                                    symbol=trade.symbol,
                                    action=trade.action,
                                    entry_price=trade.entry_price,
                                    exit_price=trade.exit_price,
                                    quantity=trade.quantity,
                                    profit_loss=trade.pnl,
                                    duration=(trade.exit_time - trade.timestamp).total_seconds(),
                                    market_conditions=trade.market_conditions or {},
                                    model_confidence=trade.confidence,
                                    model_version="shadow_v2_multiasset_enhanced",
                                    features_used=trade.market_conditions or {},
                                    risk_metrics={'volatility': (trade.market_conditions or {}).get('volatility', 0), 'exit_reason': exit_reason}
                                )
                                self._continuous_learning_engine.record_trading_outcome(outcome)
                                logger.debug(f"📚 Trade recorded to Continuous Learning: {trade.trade_id}")
                            except Exception as e:
                                logger.debug(f"Continuous learning recording failed: {e}")

                        emoji = "✅" if trade.pnl > 0 else "❌"
                        logger.info(f"\n{emoji} SHADOW POSITION CLOSED:")
                        logger.info(f"   {symbol}: {trade.action}")
                        logger.info(f"   Asset Class: {trade.asset_class.upper()}")
                        logger.info(f"   Entry: ${trade.entry_price:.2f} → Exit: ${current_price:.2f}")
                        logger.info(f"   P/L: ${trade.pnl:.2f} ({trade.pnl_pct:+.2f}%)")
                        logger.info(f"   Reason: {exit_reason}")

        return closed_trades

    # ==================== ENHANCEMENT HELPER METHODS ====================

    def _cleanup_position_tracking(self, symbol: str):
        """
        🧹 CLEAN UP POSITION TRACKING
        Called when a position is fully closed to clear tracking data
        Also deletes from database for persistence
        """
        if symbol in self.position_highs:
            del self.position_highs[symbol]
        if symbol in self.position_entry_times:
            del self.position_entry_times[symbol]
        if symbol in self.scaled_positions:
            del self.scaled_positions[symbol]
        if symbol in self.dca_counts:
            del self.dca_counts[symbol]

        # Also delete from database
        self._delete_shadow_position_tracking(symbol)
        logger.debug(f"🧹 Cleaned up tracking for {symbol} (memory + database)")

    def _check_sentiment_filter(self) -> bool:
        """
        🗓️ ENHANCEMENT 6: SENTIMENT/FED DAYS FILTER
        Returns True if trading should be avoided (Fed meeting day)
        """
        if not self.sentiment_filter_enabled:
            return False

        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in self.fed_days_2025_2026:
            logger.info(f"🗓️ SENTIMENT FILTER: Fed meeting day {today_str} - avoiding new trades")
            return True
        return False

    def _check_correlation_filter(self, symbol: str) -> bool:
        """
        🔗 ENHANCEMENT 5: CORRELATION FILTER
        Returns True if trading should be avoided (too many correlated positions)
        """
        if not self.correlation_filter_enabled:
            return False

        # Get correlated assets for this symbol
        correlated_symbols = self.correlated_assets.get(symbol, [])
        if not correlated_symbols:
            return False

        # Count how many correlated positions we have
        correlated_count = 0
        for corr_symbol in correlated_symbols:
            if corr_symbol in self.open_positions and self.open_positions[corr_symbol]:
                correlated_count += 1

        # Add self if we already have this symbol
        if symbol in self.open_positions and self.open_positions[symbol]:
            correlated_count += 1

        if correlated_count >= self.max_correlated_positions:
            logger.info(f"🔗 CORRELATION FILTER: {symbol} blocked - already have {correlated_count} correlated positions")
            return True
        return False

    # ==================== METRICS CALCULATION ====================

    def calculate_metrics(self) -> ShadowPerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        closed_trades = [t for t in self.shadow_trades if t.status == 'CLOSED']

        if not closed_trades:
            return self.metrics

        # Basic counts
        self.metrics.total_trades = len(closed_trades)
        self.metrics.winning_trades = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
        self.metrics.losing_trades = sum(1 for t in closed_trades if t.pnl and t.pnl <= 0)

        # P/L metrics
        pnls = [t.pnl for t in closed_trades if t.pnl is not None]
        self.metrics.pnl_history = pnls
        self.metrics.total_pnl = sum(pnls)

        # Win rate
        if self.metrics.total_trades > 0:
            self.metrics.win_rate = (self.metrics.winning_trades / self.metrics.total_trades) * 100

        # Average win/loss
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        self.metrics.avg_win = sum(wins) / len(wins) if wins else 0
        self.metrics.avg_loss = sum(losses) / len(losses) if losses else 0

        # Profit factor
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0.001
        self.metrics.profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

        # Sharpe ratio (annualized, assuming daily returns)
        if len(pnls) > 1:
            returns = [p / self.starting_capital for p in pnls]
            avg_return = sum(returns) / len(returns)
            std_return = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns))
            if std_return > 0:
                self.metrics.sharpe_ratio = (avg_return / std_return) * math.sqrt(252)  # Annualized

        # Max drawdown
        cumulative = 0
        peak = 0
        max_dd = 0
        for pnl in pnls:
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = (peak - cumulative) / self.starting_capital if peak > 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown
        self.metrics.max_drawdown = max_dd * 100

        # AI Attribution
        ai_performance = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total_pnl': 0})
        for trade in closed_trades:
            if trade.pnl is not None:
                for ai in trade.ai_components:
                    if trade.pnl > 0:
                        ai_performance[ai]['wins'] += 1
                    else:
                        ai_performance[ai]['losses'] += 1
                    ai_performance[ai]['total_pnl'] += trade.pnl

        self.metrics.ai_attribution = dict(ai_performance)

        # Per-Asset Class Performance (NEW)
        asset_class_perf = defaultdict(lambda: {'trades': 0, 'wins': 0, 'total_pnl': 0, 'win_rate': 0})
        for trade in closed_trades:
            if trade.pnl is not None:
                ac = trade.asset_class or 'stock'
                asset_class_perf[ac]['trades'] += 1
                asset_class_perf[ac]['total_pnl'] += trade.pnl
                if trade.pnl > 0:
                    asset_class_perf[ac]['wins'] += 1

        # Calculate win rates per asset class
        for ac, stats in asset_class_perf.items():
            if stats['trades'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['trades']) * 100

        self.metrics.asset_class_performance = dict(asset_class_perf)

        return self.metrics

    def print_status_report(self):
        """Print comprehensive status report"""
        metrics = self.calculate_metrics()

        logger.info("\n" + "="*60)
        logger.info("PROMETHEUS SHADOW TRADING STATUS REPORT")
        logger.info("="*60)
        logger.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Capital
        logger.info("CAPITAL")
        logger.info(f"   Starting: ${self.starting_capital:,.2f}")
        logger.info(f"   Current:  ${self.current_capital:,.2f}")
        logger.info(f"   P/L:      ${self.current_capital - self.starting_capital:+,.2f} ({((self.current_capital/self.starting_capital)-1)*100:+.2f}%)")

        # Trade stats
        logger.info("TRADE STATISTICS")
        logger.info(f"   Total Trades:    {metrics.total_trades}")
        logger.info(f"   Winning Trades:  {metrics.winning_trades}")
        logger.info(f"   Losing Trades:   {metrics.losing_trades}")
        logger.info(f"   Win Rate:        {metrics.win_rate:.1f}%")
        logger.info(f"   Profit Factor:   {metrics.profit_factor:.2f}")
        logger.info(f"   Sharpe Ratio:    {metrics.sharpe_ratio:.2f}")
        logger.info(f"   Max Drawdown:    {metrics.max_drawdown:.2f}%")

        # P/L details
        logger.info("PROFIT/LOSS")
        logger.info(f"   Total P/L:    ${metrics.total_pnl:+,.2f}")
        logger.info(f"   Avg Win:      ${metrics.avg_win:+,.2f}")
        logger.info(f"   Avg Loss:     ${metrics.avg_loss:+,.2f}")

        # Per-Asset Class Performance (NEW)
        if metrics.asset_class_performance:
            logger.info("ASSET CLASS PERFORMANCE")
            for ac, stats in sorted(metrics.asset_class_performance.items(),
                                   key=lambda x: x[1]['total_pnl'], reverse=True):
                logger.info(f"   {ac.upper():10} Trades: {stats['trades']:3} | "
                      f"Win Rate: {stats['win_rate']:5.1f}% | P/L: ${stats['total_pnl']:+8.2f}")

        # AI Attribution
        if metrics.ai_attribution:
            logger.info("AI ATTRIBUTION (by profitability)")
            sorted_ai = sorted(metrics.ai_attribution.items(),
                             key=lambda x: x[1]['total_pnl'], reverse=True)
            for ai, stats in sorted_ai[:8]:
                total = stats['wins'] + stats['losses']
                wr = (stats['wins'] / total * 100) if total > 0 else 0
                logger.info(f"   {ai:25} Win Rate: {wr:5.1f}% | P/L: ${stats['total_pnl']:+8.2f}")

        # Open positions
        total_open = sum(len(trades) for trades in self.open_positions.values())
        if total_open > 0:
            logger.info(f"OPEN POSITIONS: {total_open}")
            for symbol, trades in self.open_positions.items():
                for t in trades:
                    logger.info(f"   {symbol} ({t.asset_class}): {t.action} {t.quantity} @ ${t.entry_price:.2f}")

        logger.info("="*60)


    # ==================== SESSION PERSISTENCE ====================

    def save_session(self, filepath: str = None):
        """Save current session to JSON file"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"shadow_trading_results/shadow_session_{timestamp}.json"

        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Convert trades to dict
        trades_data = []
        for trade in self.shadow_trades:
            trades_data.append({
                'trade_id': trade.trade_id,
                'timestamp': trade.timestamp.isoformat(),
                'symbol': trade.symbol,
                'action': trade.action,
                'quantity': trade.quantity,
                'entry_price': trade.entry_price,
                'target_price': trade.target_price,
                'stop_loss': trade.stop_loss,
                'confidence': trade.confidence,
                'reason': trade.reason,
                'ai_components': trade.ai_components,
                'asset_class': trade.asset_class,  # NEW
                'market_conditions': trade.market_conditions,  # NEW
                'exit_price': trade.exit_price,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'exit_reason': trade.exit_reason,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct,
                'status': trade.status
            })

        session_data = {
            'session_start': self.session_start.isoformat(),
            'starting_capital': self.starting_capital,
            'current_capital': self.current_capital,
            'trades': trades_data,
            'metrics': {
                'total_trades': self.metrics.total_trades,
                'winning_trades': self.metrics.winning_trades,
                'losing_trades': self.metrics.losing_trades,
                'win_rate': self.metrics.win_rate,
                'profit_factor': self.metrics.profit_factor,
                'sharpe_ratio': self.metrics.sharpe_ratio,
                'max_drawdown': self.metrics.max_drawdown,
                'total_pnl': self.metrics.total_pnl,
                'ai_attribution': self.metrics.ai_attribution,
                'asset_class_performance': self.metrics.asset_class_performance  # NEW
            }
        }

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        logger.info(f"💾 Session saved to {filepath}")
        return filepath

    @classmethod
    def load_session(cls, filepath: str) -> 'PrometheusParallelShadowTrading':
        """Load a previous session from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        instance = cls(starting_capital=data['starting_capital'])
        instance.current_capital = data['current_capital']
        instance.session_start = datetime.fromisoformat(data['session_start'])

        # Restore trades
        for t in data['trades']:
            trade = ShadowTrade(
                trade_id=t['trade_id'],
                timestamp=datetime.fromisoformat(t['timestamp']),
                symbol=t['symbol'],
                action=t['action'],
                quantity=t['quantity'],
                entry_price=t['entry_price'],
                target_price=t['target_price'],
                stop_loss=t['stop_loss'],
                confidence=t['confidence'],
                reason=t['reason'],
                ai_components=t['ai_components'],
                asset_class=t.get('asset_class', 'stock'),  # NEW with fallback
                market_conditions=t.get('market_conditions'),  # NEW
                exit_price=t['exit_price'],
                exit_time=datetime.fromisoformat(t['exit_time']) if t['exit_time'] else None,
                exit_reason=t['exit_reason'],
                pnl=t['pnl'],
                pnl_pct=t['pnl_pct'],
                status=t['status']
            )
            instance.shadow_trades.append(trade)
            if trade.status == 'OPEN':
                instance.open_positions[trade.symbol].append(trade)

        logger.info(f"📂 Session loaded from {filepath} ({len(instance.shadow_trades)} trades)")
        return instance

    # ==================== LIVE TRADING COMPARISON ====================

    async def compare_with_live_trading(self, live_trades: List[Dict]) -> Dict:
        """Compare shadow trading decisions with live trading decisions"""
        comparison = {
            'shadow_only_trades': [],  # Trades shadow made but live didn't
            'live_only_trades': [],    # Trades live made but shadow didn't
            'matching_trades': [],     # Same decisions
            'divergent_trades': [],    # Opposite decisions
            'shadow_outperformed': 0,
            'live_outperformed': 0,
            'missed_opportunities': []
        }

        shadow_symbols = {t.symbol for t in self.shadow_trades}
        live_symbols = {t.get('symbol') for t in live_trades}

        # Find shadow-only trades
        for trade in self.shadow_trades:
            if trade.symbol not in live_symbols:
                comparison['shadow_only_trades'].append({
                    'symbol': trade.symbol,
                    'action': trade.action,
                    'pnl': trade.pnl,
                    'ai_components': trade.ai_components
                })
                if trade.pnl and trade.pnl > 0:
                    comparison['missed_opportunities'].append(trade.symbol)

        # Find live-only trades
        for trade in live_trades:
            if trade.get('symbol') not in shadow_symbols:
                comparison['live_only_trades'].append(trade)

        # Calculate performance comparison
        shadow_pnl = sum(t.pnl for t in self.shadow_trades if t.pnl)
        live_pnl = sum(t.get('pnl', 0) for t in live_trades)

        if shadow_pnl > live_pnl:
            comparison['shadow_outperformed'] = shadow_pnl - live_pnl
        else:
            comparison['live_outperformed'] = live_pnl - shadow_pnl

        return comparison

    def record_live_decision(self, symbol: str, decision: str, confidence: float,
                             entry_price: float = None, ai_components: List[str] = None):
        """
        Record a live trading decision for real-time comparison.
        Call this from live trading whenever a decision is made.

        Args:
            symbol: Trading symbol
            decision: BUY, SELL, or HOLD
            confidence: Confidence level (0-1)
            entry_price: Entry price if executing
            ai_components: Which AI systems contributed
        """
        self.live_decisions[symbol] = {
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'confidence': confidence,
            'entry_price': entry_price,
            'ai_components': ai_components or []
        }

        # Check if shadow has a different decision for this symbol
        shadow_decision = "HOLD"
        shadow_confidence = 0
        shadow_entry = None

        # Check open shadow positions
        if symbol in self.open_positions and self.open_positions[symbol]:
            shadow_decision = self.open_positions[symbol][0].action
            shadow_confidence = self.open_positions[symbol][0].confidence
            shadow_entry = self.open_positions[symbol][0].entry_price

        # Record comparison if decisions differ
        if decision != shadow_decision:
            self._record_live_shadow_comparison(
                symbol=symbol,
                live_decision=decision,
                shadow_decision=shadow_decision,
                live_confidence=confidence,
                shadow_confidence=shadow_confidence,
                live_entry=entry_price,
                shadow_entry=shadow_entry,
                notes=f"Real-time divergence at {datetime.now().strftime('%H:%M:%S')}"
            )

    def record_live_exit(self, symbol: str, exit_price: float, pnl: float, exit_reason: str = None):
        """
        Record a live trading exit for comparison.
        Call this from live trading when positions are closed.
        """
        # Find corresponding shadow trade
        shadow_pnl = None
        shadow_entry = None

        for trade in self.shadow_trades:
            if trade.symbol == symbol and trade.status == 'CLOSED':
                shadow_pnl = trade.pnl
                shadow_entry = trade.entry_price
                break

        if shadow_pnl is not None:
            self._record_live_shadow_comparison(
                symbol=symbol,
                live_decision="EXIT",
                shadow_decision="EXIT",
                live_exit=exit_price,
                shadow_exit=shadow_entry,  # Shadow's exit price
                live_pnl=pnl,
                shadow_pnl=shadow_pnl,
                notes=f"Exit comparison - {exit_reason or 'unknown'}"
            )

    def get_divergence_summary(self) -> Dict:
        """Get summary of all divergences between live and shadow trading"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                SELECT divergence_type, COUNT(*) as count,
                       AVG(hypothetical_difference) as avg_diff
                FROM live_shadow_comparison
                WHERE session_id = ?
                GROUP BY divergence_type
            """, (self.session_id,))

            summary = {
                'total_divergences': 0,
                'by_type': {},
                'total_hypothetical_impact': 0
            }

            for row in cursor.fetchall():
                divergence_type, count, avg_diff = row
                summary['by_type'][divergence_type] = {
                    'count': count,
                    'avg_impact': avg_diff or 0
                }
                summary['total_divergences'] += count
                if avg_diff:
                    summary['total_hypothetical_impact'] += avg_diff * count

            # Get symbols with most divergences
            cursor.execute("""
                SELECT symbol, COUNT(*) as count
                FROM live_shadow_comparison
                WHERE session_id = ?
                GROUP BY symbol
                ORDER BY count DESC
                LIMIT 10
            """, (self.session_id,))

            summary['top_divergent_symbols'] = [
                {'symbol': row[0], 'divergences': row[1]}
                for row in cursor.fetchall()
            ]

            db.close()
            return summary

        except Exception as e:
            logger.warning(f"⚠️ Could not get divergence summary: {e}")
            return {'error': str(e)}

    # ==================== LEARNING FEEDBACK ====================

    async def feed_to_learning_engine(self):
        """Feed shadow trading results to PROMETHEUS learning engines"""
        if not self.shadow_trades:
            return

        # Prepare learning data
        learning_data = {
            'session_id': f"shadow_{self.session_start.strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'win_rate': self.metrics.win_rate,
                'profit_factor': self.metrics.profit_factor,
                'sharpe_ratio': self.metrics.sharpe_ratio
            },
            'ai_performance': self.metrics.ai_attribution,
            'asset_class_performance': self.metrics.asset_class_performance,  # NEW
            'trades': []
        }

        for trade in self.shadow_trades:
            if trade.status == 'CLOSED' and trade.pnl is not None:
                learning_data['trades'].append({
                    'symbol': trade.symbol,
                    'asset_class': trade.asset_class,  # NEW
                    'action': trade.action,
                    'confidence': trade.confidence,
                    'ai_components': trade.ai_components,
                    'pnl': trade.pnl,
                    'pnl_pct': trade.pnl_pct,
                    'success': trade.pnl > 0,
                    'market_conditions': trade.market_conditions  # NEW
                })

        # Try to feed to AI attribution tracker
        if self._ai_attribution_tracker:
            try:
                await self._ai_attribution_tracker.update_from_session(learning_data)
                logger.info("📚 Learning data fed to AI Attribution Tracker")
            except Exception as e:
                logger.debug(f"AI attribution update failed: {e}")

        # Feed patterns to AI Learning Engine (NEW)
        if self._ai_learning_engine:
            try:
                winning_trades = [t for t in self.shadow_trades if t.status == 'CLOSED' and t.pnl and t.pnl > 0]
                losing_trades = [t for t in self.shadow_trades if t.status == 'CLOSED' and t.pnl and t.pnl <= 0]

                # Extract winning patterns for learning
                for trade in winning_trades[-20:]:  # Last 20 winning trades
                    if trade.market_conditions:
                        from core.ai_learning_engine import MarketPattern
                        pattern = MarketPattern(
                            pattern_type=f"winning_{trade.asset_class}",
                            confidence=trade.confidence,
                            indicators=trade.market_conditions,
                            timeframe="5min",
                            symbol=trade.symbol,
                            detected_at=trade.timestamp
                        )
                        await self._ai_learning_engine.record_market_pattern(pattern)

                logger.info(f"📚 {len(winning_trades)} winning patterns fed to AI Learning Engine")
            except Exception as e:
                logger.debug(f"AI Learning Engine feed failed: {e}")

        # Trigger Continuous Learning update (NEW)
        if self._continuous_learning_engine:
            try:
                self._continuous_learning_engine.perform_learning_update()
                logger.info("📚 Continuous Learning update triggered")
            except Exception as e:
                logger.debug(f"Continuous Learning update failed: {e}")

        # Save learning data to file for offline analysis
        os.makedirs("shadow_trading_results/learning", exist_ok=True)
        filepath = f"shadow_trading_results/learning/learning_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w') as f:
            json.dump(learning_data, f, indent=2)

        logger.info(f"📚 Learning data saved to {filepath}")

        # Save to knowledge base (NEW)
        await self._save_to_knowledge_base(learning_data)

    async def _save_to_knowledge_base(self, learning_data: Dict):
        """Save learnings to knowledge base for persistent cross-session learning"""
        try:
            # Extract key insights
            insights = {
                'session_id': learning_data['session_id'],
                'timestamp': learning_data['timestamp'],
                'summary': {
                    'total_trades': len(learning_data['trades']),
                    'winning_rate': learning_data['metrics']['win_rate'],
                    'profit_factor': learning_data['metrics']['profit_factor']
                },
                'best_ai_systems': [],
                'best_asset_classes': [],
                'winning_patterns': [],
                'lessons_learned': []
            }

            # Find best AI systems
            if learning_data.get('ai_performance'):
                sorted_ai = sorted(learning_data['ai_performance'].items(),
                                  key=lambda x: x[1].get('total_pnl', 0), reverse=True)
                insights['best_ai_systems'] = [ai for ai, _ in sorted_ai[:3]]

            # Find best asset classes
            if learning_data.get('asset_class_performance'):
                sorted_ac = sorted(learning_data['asset_class_performance'].items(),
                                  key=lambda x: x[1].get('total_pnl', 0), reverse=True)
                insights['best_asset_classes'] = [ac for ac, _ in sorted_ac[:3]]

            # Extract winning patterns
            winning_trades = [t for t in learning_data['trades'] if t.get('success')]
            for trade in winning_trades[:10]:
                if trade.get('market_conditions'):
                    insights['winning_patterns'].append({
                        'asset_class': trade.get('asset_class', 'stock'),
                        'conditions': trade['market_conditions'],
                        'ai_components': trade.get('ai_components', [])
                    })

            # Save to knowledge base
            kb_filepath = self.knowledge_base_dir / f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(kb_filepath, 'w') as f:
                json.dump(insights, f, indent=2)

            logger.info(f"📖 Knowledge base updated: {kb_filepath}")

        except Exception as e:
            logger.debug(f"Knowledge base save failed: {e}")


    # ==================== MAIN TRADING LOOP ====================

    async def run_shadow_trading(
        self,
        watchlist: List[str],
        interval_seconds: int = 60,
        max_iterations: int = None,
        report_interval: int = 10
    ):
        """
        Main shadow trading loop.

        Args:
            watchlist: List of symbols to trade
            interval_seconds: Seconds between trading iterations
            max_iterations: Max number of iterations (None = run forever)
            report_interval: Print status report every N iterations
        """
        logger.info("\n" + "="*60)
        logger.info("🚀 PROMETHEUS SHADOW TRADING SYSTEM STARTING")
        logger.info("="*60)
        logger.info(f"Watchlist: {', '.join(watchlist)}")
        logger.info(f"Starting Capital: ${self.starting_capital:,.2f}")
        logger.info(f"Trading Interval: {interval_seconds} seconds")
        logger.info(f"Max Iterations: {max_iterations or 'Unlimited'}")
        logger.info("="*60 + "\n")

        # Initialize AI systems
        await self.initialize_all_ai_systems()

        iteration = 0
        self.running = True

        try:
            while self.running:
                iteration += 1
                logger.info(f"\n--- Iteration {iteration} | {datetime.now().strftime('%H:%M:%S')} ---")

                # Check max iterations
                if max_iterations and iteration > max_iterations:
                    logger.info("Max iterations reached. Stopping.")
                    break

                # Check daily trade limit
                if self.trades_today >= self.max_trades_per_day:
                    logger.info(f"Daily trade limit ({self.max_trades_per_day}) reached. Waiting for next day.")
                    await asyncio.sleep(interval_seconds)
                    continue

                # ALWAYS monitor existing positions first (even during market close)
                # This ensures crypto positions are monitored 24/7 and stale positions get cleaned up
                if any(trades for trades in self.open_positions.values()):
                    closed_trades = await self.monitor_positions()
                    if closed_trades:
                        logger.info(f"Closed {len(closed_trades)} positions")

                # 1. Fetch market data for all symbols (filtered by market hours)
                active_watchlist = [s for s in watchlist if is_tradeable_now(s)]
                if not active_watchlist:
                    logger.info("No symbols tradeable right now (market closed). Waiting...")
                    await asyncio.sleep(interval_seconds)
                    continue
                
                market_data = await self.get_market_data(active_watchlist)

                if not market_data:
                    logger.warning("No market data available. Waiting...")
                    await asyncio.sleep(interval_seconds)
                    continue

                # 2. Make AI decisions for each symbol
                for symbol, data in market_data.items():
                    # Skip if we already have position in this symbol
                    if symbol in self.open_positions and self.open_positions[symbol]:
                        continue

                    # Get AI decision
                    decision = await self.make_ai_decision(symbol, data)

                    # Execute shadow trade if not HOLD
                    if decision['action'] != 'HOLD':
                        await self.execute_shadow_trade(symbol, decision, data)
                    
                    # Small delay to prevent event loop starvation (CPU was hitting 100%)
                    await asyncio.sleep(0.1)  # 100ms between symbols

                # 3. Print periodic status report
                if iteration % report_interval == 0:
                    self.print_status_report()
                    self.save_session()  # Auto-save every report interval

                # 4. Feed learning data periodically
                if iteration % (report_interval * 5) == 0:
                    await self.feed_to_learning_engine()

                # Wait for next iteration
                await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("\n⚠️ Shadow trading interrupted by user")
        except Exception as e:
            logger.error(f"Shadow trading error: {e}")
        finally:
            # Final save and report (graceful shutdown - avoid async calls during event loop teardown)
            try:
                logger.info("\n" + "="*60)
                logger.info("SHADOW TRADING SESSION ENDING")
                logger.info("="*60)
            except Exception:
                pass  # Logger may fail during shutdown
            
            # Try to print status report (may fail if Python is shutting down)
            try:
                self.print_status_report()
            except Exception as e:
                try:
                    logger.info(f"Could not print final status report: {e}")
                except Exception:
                    pass  # Even logger may fail during shutdown
            
            # DO NOT await in finally block - event loop may be closed
            # Learning data was already fed periodically during the loop
            
            # Try to save session (synchronous operation, safer during shutdown)
            try:
                filepath = self.save_session()
                try:
                    logger.info(f"\n✅ Session saved to: {filepath}")
                    logger.info("Goodbye!")
                except Exception:
                    pass  # Logger may fail
            except Exception as e:
                try:
                    logger.error(f"Could not save session: {e}")
                except Exception:
                    pass  # Even error logging may fail during shutdown

    def stop(self):
        """Stop the shadow trading loop"""
        self.running = False
        logger.info("Stop signal received. Will stop after current iteration.")


# ==================== MAIN EXECUTION ====================

# Default multi-asset watchlist string for CLI
DEFAULT_WATCHLIST_STR = ','.join(DEFAULT_MULTI_ASSET_WATCHLIST)


def main():
    """Main entry point for shadow trading"""
    import argparse

    parser = argparse.ArgumentParser(description='PROMETHEUS Shadow Trading System - Multi-Asset AI Trading')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Starting capital (default: 100000)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Trading interval in seconds (default: 60)')
    parser.add_argument('--iterations', type=int, default=None,
                       help='Max iterations (default: unlimited)')
    parser.add_argument('--watchlist', type=str, default=DEFAULT_WATCHLIST_STR,
                       help=f'Comma-separated list of symbols (default: multi-asset watchlist with stocks, ETFs, crypto, forex)')
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to session file to resume')
    parser.add_argument('--stocks-only', action='store_true',
                       help='Use stocks-only watchlist (AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,AMD,NFLX,CRM)')
    parser.add_argument('--crypto-only', action='store_true',
                       help='Use crypto-only watchlist (BTC-USD,ETH-USD,SOL-USD,ADA-USD,AVAX-USD,DOGE-USD,XRP-USD,DOT-USD)')

    args = parser.parse_args()

    # Parse watchlist
    if args.stocks_only:
        watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX', 'CRM']
    elif args.crypto_only:
        watchlist = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'AVAX-USD', 'DOGE-USD', 'XRP-USD', 'DOT-USD']
    else:
        watchlist = [s.strip().upper() for s in args.watchlist.split(',')]

    # Create or resume session
    if args.resume:
        shadow = PrometheusParallelShadowTrading.load_session(args.resume)
    else:
        shadow = PrometheusParallelShadowTrading(starting_capital=args.capital)

    # Log asset class breakdown
    asset_breakdown = {}
    for symbol in watchlist:
        ac = detect_asset_class(symbol).value
        asset_breakdown[ac] = asset_breakdown.get(ac, 0) + 1
    logger.info(f"📊 Watchlist asset breakdown: {asset_breakdown}")

    # Run the trading loop
    # Python 3.13 compatibility: Use manual event loop to avoid asyncio.run() issues
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(shadow.run_shadow_trading(
            watchlist=watchlist,
            interval_seconds=args.interval,
            max_iterations=args.iterations
        ))
    except KeyboardInterrupt:
        logger.info("⚠️ Shadow trading interrupted by user")
    finally:
        try:
            loop.close()
        except:
            pass


if __name__ == '__main__':
    main()
