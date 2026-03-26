#!/usr/bin/env python3
"""
 PROMETHEUS ULTIMATE TRADING LAUNCHER
Enterprise-Grade Autonomous Trading System

LIVE PERFORMANCE (All-Time, Dec 14, 2025 - Mar 11, 2026):
- Win Rate: 18/40 closed trades (45%)
- Total P&L: -$1.35 | Equity: ~$98.65
- Recent Period (Feb 16+): 14/16 wins (87.5%), +$1.36
- Scale-Out Strategy: 9/9 perfect (100%)
- Total Trades in DB: 608+ | Closed: 40

CURRENT MODE: LIVE TRADING + Shadow Learning
- Alpaca: LIVE trading (~$98.65 real capital)
- Interactive Brokers: Account U21922116 (LIVE on port 4002)
- Shadow Trading: $100K virtual capital (parallel learning system)
- All AI Systems: Fully autonomous (trading, learning, adapting)

CONFIGURATION:
- Alpaca: LIVE trading for stocks + crypto 24/7
- Risk Limits: $25 daily loss (~25% of ~$98.65), 15% position size, 10 max positions
- Adaptive Trading: 100% autonomous operation
- All Revolutionary Systems: Active and ready

DATA INTELLIGENCE SOURCES (NEW):
- Real-World Data Orchestrator: 1000+ global intelligence sources
- Google Trends: Search volume and trending analysis
- Reddit: WallStreetBets sentiment and ticker tracking
- CoinGecko Extended: Comprehensive crypto market data
- N8N Workflows: Automated news/social media monitoring
- Twitter/X: Real-time sentiment analysis
- News Feeds: Bloomberg, Reuters, CNBC, WSJ, etc.
- Economic Data: Federal Reserve, unemployment, inflation
- Weather/Environmental: Market impact analysis

SAFETY FEATURES:
- Real-time resource monitoring
- Automatic position sizing
- Dynamic stop losses
- Market regime detection
- Performance-based adaptation
"""

import sys
import os

# CRITICAL: Set UTF-8 encoding BEFORE any other imports to prevent emoji encoding errors on Windows
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
os.environ['PYTHONIOENCODING'] = 'utf-8'

if __name__ == "__main__":
    try:
        from gpu_detector import ensure_preferred_gpu_runtime
        ensure_preferred_gpu_runtime("launch_ultimate_prometheus_LIVE_TRADING")
    except Exception as exc:
        print(f"Runtime bootstrap check skipped: {exc}")

# Load .env BEFORE anything else reads environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)  # .env values only used if not already in env
except ImportError:
    pass  # dotenv not installed, rely on system env vars

import ast
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import psutil

# FastAPI imports for web API
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import timezone-aware market hours utility
try:
    from core.market_hours_utils import format_market_status, get_market_status, get_eastern_time
    MARKET_HOURS_UTILS_AVAILABLE = True
except ImportError:
    MARKET_HOURS_UTILS_AVAILABLE = False

# Import Advanced Risk Management (Kelly Criterion + Volatility Scaling + Drawdown Protection)
try:
    from advanced_risk_management import get_risk_manager
    ADVANCED_RISK_MANAGER_AVAILABLE = True
except ImportError:
    ADVANCED_RISK_MANAGER_AVAILABLE = False
    print("⚠️ Advanced Risk Manager not available - using fallback position sizing")

# Configure logging - use root logger directly (basicConfig is no-op if handlers already exist from imports)
_log_file_name = f'prometheus_live_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
_file_handler = logging.FileHandler(_log_file_name, encoding='utf-8')
_file_handler.setLevel(logging.INFO)
_stream_handler = logging.StreamHandler()
_stream_handler.setLevel(logging.INFO)
_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_file_handler.setFormatter(_log_formatter)
_stream_handler.setFormatter(_log_formatter)

_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)
# Remove any pre-existing handlers from imports (uvicorn, etc.)
for _h in _root_logger.handlers[:]:
    _root_logger.removeHandler(_h)
_root_logger.addHandler(_file_handler)
_root_logger.addHandler(_stream_handler)

logger = logging.getLogger(__name__)
logger.info(f"📝 Log file: {_log_file_name}")

_OPTIONAL_IMPORT_WARNINGS = os.getenv("PROMETHEUS_OPTIONAL_IMPORT_WARNINGS", "0").strip().lower() in ("1", "true", "yes", "on")


def _log_optional_unavailable(message: str) -> None:
    """Keep optional subsystem noise at INFO unless strict warnings are enabled."""
    if _OPTIONAL_IMPORT_WARNINGS:
        logger.warning(message)
    else:
        logger.info(message)

# TIER 1: CRITICAL SYSTEMS (Must initialize first)
try:
    from core.real_time_market_data import RealTimeMarketDataOrchestrator
    from core.ai_trading_intelligence import OpenAITradingIntelligence
    from core.advanced_trading_engine import AdvancedTradingEngine
    from core.persistent_memory import PersistentMemory
    from core.portfolio_persistence_layer import PortfolioPersistenceLayer
    from revolutionary_features.ai_learning.advanced_learning_engine import get_ai_learning_engine
    from core.continuous_learning_engine import ContinuousLearningEngine
    from core.persistent_trading_engine import persistent_trading_engine
    from core.ai_attribution_tracker import get_attribution_tracker, AIAttributionTracker
    TIER1_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Some Tier 1 systems unavailable: {e}")
    TIER1_AVAILABLE = False

# TIER 2: REVOLUTIONARY CORE
try:
    from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
    from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
    from core.hierarchical_reasoning import HierarchicalReasoningModel
    from revolutionary_master_engine import PrometheusRevolutionaryMasterEngine
    from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
    from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
    from core.chart_vision_analyzer import ChartVisionAnalyzer, get_chart_vision_analyzer
    from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
    TIER2_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Some Tier 2 systems unavailable: {e}")
    TIER2_AVAILABLE = False

# TIER 3: DATA INTELLIGENCE SOURCES
try:
    from core.real_world_data_orchestrator import RealWorldDataOrchestrator
    from core.google_trends_data_source import GoogleTrendsDataSource
    from core.reddit_data_source import RedditDataSource
    from core.coingecko_data_source import CoinGeckoDataSource
    from core.n8n_workflow_manager import N8NWorkflowManager
    from core.yahoo_finance_data_source import YahooFinanceDataSource
    DATA_SOURCES_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Some data intelligence sources unavailable: {e}")
    DATA_SOURCES_AVAILABLE = False

# MARKET INTELLIGENCE AGENTS
try:
    from core.market_intelligence_agents import (
        GapDetectionAgent,
        OpportunityScannerAgent,
        MarketResearchAgent
    )
    MARKET_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Market Intelligence Agents unavailable: {e}")
    MARKET_INTELLIGENCE_AVAILABLE = False

# LIVE BROKER SYSTEMS
try:
    from brokers.alpaca_broker import AlpacaBroker
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    from brokers.universal_broker_interface import Order, OrderSide, OrderType
    BROKERS_AVAILABLE = True
except ImportError as e:
    logger.error(f"CRITICAL: Broker systems unavailable: {e}")
    BROKERS_AVAILABLE = False

# PARALLEL SHADOW TRADING (autonomous learning)
try:
    from parallel_shadow_trading import PrometheusParallelShadowTrading
    SHADOW_TRADING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Shadow trading unavailable: {e}")
    SHADOW_TRADING_AVAILABLE = False

# MONITORING SYSTEMS
try:
    from core.advanced_monitoring import AdvancedMonitoringSystem
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# SHORT SELLING INTEGRATION
try:
    from enhanced_trading_logic import EnhancedTradingLogic
    SHORT_SELLING_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"SHORT selling module unavailable: {e}")
    SHORT_SELLING_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# AI SUBSYSTEM IMPORTS (HRM, DeepConf, ThinkMesh, Pretrained ML)
# ═══════════════════════════════════════════════════════════════
try:
    from core.hrm_official_integration import OfficialHRMTradingAdapter, get_official_hrm_adapter
    HRM_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"HRM adapter unavailable: {e}")
    HRM_AVAILABLE = False

try:
    from core.reasoning.official_deepconf_adapter import OfficialDeepConfAdapter, deepconf_trading_decision
    DEEPCONF_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"DeepConf adapter unavailable: {e}")
    DEEPCONF_AVAILABLE = False

try:
    from core.reasoning import ThinkMeshAdapter, ThinkMeshConfig
    THINKMESH_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"ThinkMesh adapter unavailable: {e}")
    THINKMESH_AVAILABLE = False

PRETRAINED_ML_AVAILABLE = len(list(Path("models_pretrained").glob("*_direction_model.pkl"))) > 0 if Path("models_pretrained").exists() else False

# RL Trading Agent
try:
    import torch
    from core.reinforcement_learning_trading import TradingRLAgent, ReinforcementLearningTrading
    RL_AGENT_AVAILABLE = Path("trained_models/rl_trading_agent.pt").exists()
except ImportError:
    RL_AGENT_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# PHASE 21 — NEW INTEGRATIONS
# ═══════════════════════════════════════════════════════════════

# LangGraph Trading Orchestrator
try:
    from core.langgraph_trading_orchestrator import LangGraphTradingOrchestrator
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"LangGraph unavailable: {e}")
    LANGGRAPH_AVAILABLE = False

# OpenBB Data Provider
try:
    from core.openbb_data_provider import OpenBBDataProvider
    OPENBB_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"OpenBB unavailable: {e}")
    OPENBB_AVAILABLE = False

# CCXT Exchange Bridge (107+ crypto exchanges)
try:
    from core.ccxt_exchange_bridge import CCXTExchangeBridge
    CCXT_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"CCXT unavailable: {e}")
    CCXT_AVAILABLE = False

# Gymnasium / Stable-Baselines3 RL
try:
    from core.gymnasium_trading_env import TradingGymEnv, SB3TradingAgent
    GYMNASIUM_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Gymnasium/SB3 unavailable: {e}")
    GYMNASIUM_AVAILABLE = False

# Mercury2 Diffusion LLM
try:
    from core.mercury2_adapter import Mercury2Adapter
    _test_m2 = Mercury2Adapter()
    MERCURY2_AVAILABLE = _test_m2.is_available()
    del _test_m2
except ImportError as e:
    _log_optional_unavailable(f"Mercury2 unavailable: {e}")
    MERCURY2_AVAILABLE = False

# Prometheus Cache (Redis + TTLCache fallback)
try:
    from core.redis_cache import get_cache as get_prometheus_cache
    CACHE_AVAILABLE = True
except ImportError as e:
    _log_optional_unavailable(f"Prometheus Cache unavailable: {e}")
    CACHE_AVAILABLE = False

# LlamaIndex SEC Filings RAG
LLAMAINDEX_AVAILABLE = False
try:
    from core.llamaindex_sec_analyzer import get_sec_analyzer
    _test_sec = get_sec_analyzer()
    LLAMAINDEX_AVAILABLE = _test_sec.is_available()
except Exception as e:
    _log_optional_unavailable(f"LlamaIndex SEC Analyzer unavailable: {e}")

# FinRL Portfolio Optimizer
FINRL_AVAILABLE = False
try:
    from core.finrl_portfolio_optimizer import get_finrl_optimizer
    _test_finrl = get_finrl_optimizer()
    FINRL_AVAILABLE = _test_finrl.is_available()
except Exception as e:
    _log_optional_unavailable(f"FinRL Portfolio Optimizer unavailable: {e}")

# OpenAI Trading Intelligence (GPT-4 / Anthropic Claude)
OPENAI_INTELLIGENCE_AVAILABLE = False
try:
    from core.ai_trading_intelligence import OpenAITradingIntelligence
    _test_oai = OpenAITradingIntelligence()
    if _test_oai.is_available():
        OPENAI_INTELLIGENCE_AVAILABLE = True
except Exception:
    pass


class PrometheusLiveTradingLauncher:
    """
     Ultimate PROMETHEUS Live Trading System
    Manages all 80+ systems with live broker connections
    """
    
    def __init__(self, standalone_mode=False):
        """
        Initialize PROMETHEUS Live Trading Launcher

        Args:
            standalone_mode: If True, creates its own FastAPI app (legacy mode)
                           If False, runs as library for integration (recommended)
        """
        self.logger = logging.getLogger(__name__)
        self.systems = {}
        self.system_health = {}
        self.failed_systems = []
        self.standalone_mode = standalone_mode
        self.start_time = datetime.now()

        # Supervised Learning Training Configuration
        self.trade_count_since_training = 0
        self.training_trigger_threshold = 100  # Run training every 100 trades
        self.last_training_time = None

        # ═══════════════════════════════════════════════════════════════════════════
        # 🎯 LEARNING FEEDBACK LOOP - AI System Weights Based on Performance
        # ═══════════════════════════════════════════════════════════════════════════
        # These weights are loaded from AI Attribution Tracker based on historical
        # performance. Top-performing AI systems get higher weights (up to 2.0x),
        # poor performers get lower weights (down to 0.5x).
        # ═══════════════════════════════════════════════════════════════════════════
        self.ai_system_weights = {}  # Will be loaded from database
        self.ai_weights_last_refresh = None
        self.ai_weights_refresh_interval = 3600  # Refresh weights every hour (seconds)
        self.last_learning_score_date = None  # Daily learning/adaptation score log guard

        # Live Trading Configuration
        self.live_mode = True
        self.ib_account = "U21922116"
        # IB Ports:
        #   TWS: 7496 = Paper Trading, 7497 = Live Trading
        #   Gateway: 4001 = Paper Trading, 4002 = Live Trading
        # Allow override via environment variable
        # Default to Gateway port 4002 since that's what's typically running
        self.ib_port = int(os.getenv('IB_PORT', '4002'))  # Default to 4002 (Gateway live)

        # Broker routing controls (safe defaults: legacy execution + shadow recommendations)
        self.autonomous_routing_enabled = os.getenv('AUTONOMOUS_ROUTING_ENABLED', 'false').strip().lower() in ('1', 'true', 'yes', 'on')
        self.routing_shadow_mode = os.getenv('ROUTING_SHADOW_MODE', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
        self.ib_min_allocation_pct = max(0.0, min(1.0, float(os.getenv('IB_MIN_ALLOCATION_PCT', '0.30') or 0.30)))
        self.alpaca_24hr_hard_override = os.getenv('ALPACA_24HR_HARD_OVERRIDE', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
        self.ib_regular_hours_bonus = float(os.getenv('IB_REGULAR_HOURS_BONUS', '0.20') or 0.20)
        self.routing_execution_counts = {'ib': 0, 'alpaca': 0}
        self._load_routing_stats()

        # Only create FastAPI app if running in standalone mode (legacy)
        if self.standalone_mode:
            self.logger.warning("[WARNING] Running in STANDALONE mode - creating separate FastAPI app")
            self.logger.warning("[WARNING] RECOMMENDED: Use integrated mode with unified_production_server.py")
            self.app = FastAPI(
                title="Prometheus Ultimate Trading System",
                description="ALL 80+ Revolutionary Systems with Live Trading",
                version="1.0.0"
            )

            # Add CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Setup API endpoints
            self._setup_api_endpoints()
        else:
            self.logger.info("[CHECK] Running in INTEGRATED mode - no separate API server")
            self.app = None

        # ═══════════════════════════════════════════════════════════════════════════
        #  OPTIMIZED TRADING PARAMETERS - Based on Backtesting Results
        # ═══════════════════════════════════════════════════════════════════════════
        # Source: backtest_optimization_20251214_211723.json
        # Best Config: TP10_SL03_POS05 (lowest drawdown, best capital preservation)
        # - Take Profit: 10% (optimal for risk-adjusted returns)
        # - Stop Loss: 3% (tight risk control)
        # - Position Size: 5% (conservative for lower drawdown)
        # ═══════════════════════════════════════════════════════════════════════════
        self.risk_limits = {
            'daily_loss_limit': 25,  # $25 max loss per day (~25% of ~$98.65 live account)
            'position_size_pct': 0.15,  # 15% of capital per position - INCREASED for small accounts ($100-500)
            'max_positions': 10,  # Maximum 10 concurrent positions — RECONCILED: matches Guardian & REM (was 15, but Guardian hard-capped at 10)
            'stop_loss_pct': 0.02,  # 2% stop loss — RECONCILED: matches Guardian default_stop_loss_pct (was 1.5%, triggering too often on noise)
            'max_portfolio_risk': 0.20,  # 20% max total portfolio risk
            'max_correlated_positions': 3,  # Max 3 correlated positions
            'max_drawdown_pct': 0.08,  # 8% max drawdown — RECONCILED: matches Guardian trailing_stop_pct (#1 Rank had -6.36% DD)
            'min_confidence': 0.70,  # 70% minimum confidence - LOWERED from 85% because Quantum+AgentCoordinator disabled (Mar 7 audit) reduced max achievable confidence by ~15-20%
            'take_profit_pct': 0.02,  # 2% take profit - ACHIEVABLE (max win was 1.12%, need room)
            'trailing_stop_pct': 0.01,  # 1% trailing stop - TIGHTER to protect gains
            'max_trades_per_hour': 30,  # Max 30 trades/hour - MORE TRADES for scalping
        }

        # ═══════════════════════════════════════════════════════════════════════════
        # 🚀 6 BACKTEST ENHANCEMENTS - These achieved 75.6% win rate in backtesting!
        # Source: backtest_enhanced_6_improvements.py, backtest_results_20260115_212427.json
        # ═══════════════════════════════════════════════════════════════════════════

        # === ENHANCEMENT 1: TRAILING STOP ===
        # Lock in profits by trailing the stop loss behind the highest price reached
        self.trailing_stop_enabled = True
        self.trailing_stop_trigger = 0.02  # Activate trailing stop at +2% profit
        self.trailing_stop_distance = 0.01  # Trail 1% behind the high (tighter for small gains)

        # === ENHANCEMENT 2: DCA ON DIPS (Dollar Cost Averaging) ===
        # Buy more when position drops to average down entry price
        self.dca_enabled = True
        self.dca_trigger_pct = -0.02  # Buy more at -2% (tighter for small accounts)
        self.dca_max_adds = 2  # Max 2 DCA buys per position
        self.dca_position_pct = 0.05  # 5% of capital per DCA buy

        # === ENHANCEMENT 3: TIME-BASED EXIT ===
        # Exit positions that haven't hit targets after max hold time
        self.time_exit_enabled = True
        self.max_hold_days_crypto = 3  # Exit crypto after 3 days (faster for volatility)
        self.max_hold_days_stock = 7  # Exit stocks after 7 days

        # === ENHANCEMENT 4: SCALE-OUT PROFITS ===
        # Sell partial positions at profit targets to lock in gains
        self.scale_out_enabled = True
        self.scale_out_first_pct = 0.015  # Sell 50% at +1.5% (achievable based on data)
        self.scale_out_second_pct = 0.03  # Sell remaining at +3%

        # === ENHANCEMENT 5: CORRELATION FILTER ===
        # Avoid overexposure to correlated assets
        self.correlation_filter_enabled = True
        self.correlated_assets = {
            'BTC/USD': ['ETH/USD', 'SOL/USD', 'LINK/USD'],
            'ETH/USD': ['BTC/USD', 'SOL/USD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'NVDA': ['AMD'],
            'AMD': ['NVDA'],
            'TSLA': ['RIVN', 'LCID'],
        }

        # === ENHANCEMENT 6: SENTIMENT/FED DAYS FILTER ===
        # Reduce trading on high-volatility Fed announcement days
        self.sentiment_filter_enabled = True
        self.fed_days_2025_2026 = [
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-11-05", "2025-12-17",
            "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
            "2026-07-29", "2026-09-16", "2026-11-04", "2026-12-16",
        ]

        # === POSITION TRACKING FOR ENHANCEMENTS ===
        self.position_highs = {}  # Track highest price for each position (trailing stop)
        self.position_entry_times = {}  # Track entry time for each position (time exit)
        self.scaled_positions = {}  # Track which positions have been scaled out
        self.dca_counts = {}  # Track DCA buys per position
        self.position_trade_ids = {}  # Track trade_id for AI attribution (P/L recording fix)

        # ═══════════════════════════════════════════════════════════════════════════
        # 💰 TRADING COST STRUCTURE - Used for cost-aware decision making
        # ═══════════════════════════════════════════════════════════════════════════
        self.trading_costs = {
            'alpaca': {
                'crypto': {
                    'maker_fee': 0.0015,    # 0.15% maker fee
                    'taker_fee': 0.0025,    # 0.25% taker fee (market orders)
                    'spread': 0.002,        # ~0.2% typical spread
                    'slippage': 0.001,      # ~0.1% slippage
                    'total_per_trade': 0.006,  # ~0.6% total cost per trade
                    'round_trip': 0.012,    # ~1.2% round trip (buy + sell)
                },
                'stocks': {
                    'commission': 0.0,      # $0 commission
                    'spread': 0.0002,       # ~0.02% spread (liquid stocks)
                    'slippage': 0.0005,     # ~0.05% slippage
                    'total_per_trade': 0.0007,  # ~0.07% total cost per trade
                    'round_trip': 0.0014,   # ~0.14% round trip
                },
            },
            'ib': {
                'stocks': {
                    'commission': 0.0035,   # $0.0035 per share (tiered)
                    'min_commission': 0.35, # $0.35 minimum
                    'spread': 0.0001,       # ~0.01% spread (very liquid)
                    'slippage': 0.0003,     # ~0.03% slippage
                    'total_per_trade': 0.001,  # ~0.1% total (varies by share price)
                    'round_trip': 0.002,    # ~0.2% round trip
                },
                'forex': {
                    'commission': 0.00002,  # 0.2 basis points
                    'spread': 0.0001,       # ~1 pip typical
                    'slippage': 0.00005,    # minimal slippage
                    'total_per_trade': 0.00035,  # ~0.035% total
                    'round_trip': 0.0007,   # ~0.07% round trip
                },
                'options': {
                    'commission': 0.65,     # $0.65 per contract
                    'spread': 0.02,         # ~2% spread (varies widely)
                    'slippage': 0.01,       # ~1% slippage
                    'total_per_trade': 0.03,  # ~3% total (expensive!)
                    'round_trip': 0.06,     # ~6% round trip
                },
            }
        }

        # Adaptive Trading State
        self.trading_style = "AGGRESSIVE"  # AGGRESSIVE: High-frequency 6-8% daily returns
        self.market_regime = "NORMAL"  # NORMAL, VOLATILE, TRENDING, RANGING
        self.performance_history = []

        # RECOVERY MODE: Trade rate limiting
        self.trades_this_hour = []  # Track trades with timestamps
        self.last_trade_time = None

        # ═══════════════════════════════════════════════════════════════
        # AI SUBSYSTEM INSTANCES (lazy-loaded on first use)
        # ═══════════════════════════════════════════════════════════════
        self._hrm_adapter = None
        self._deepconf_adapter = None
        self._thinkmesh_adapter = None
        self._pretrained_models = {}  # symbol -> (model, scaler)
        self._rl_agent = None  # PyTorch RL Trading Agent (lazy)
        self._rl_system = None  # ReinforcementLearningTrading wrapper (lazy)
        self._openai_intelligence = None  # OpenAI GPT-4 / Anthropic (lazy)

        # Initialize SHORT SELLING capability
        if SHORT_SELLING_AVAILABLE:
            self.enhanced_logic = EnhancedTradingLogic()
            self.logger.info(" SHORT SELLING capability enabled")
        else:
            self.enhanced_logic = None
            self.logger.warning(" SHORT SELLING capability not available")

        # Initialize learning database
        self.initialize_learning_database()

        # Reconcile stale pending rows before adaptive calibration so risk tuning
        # reflects active lifecycle health instead of historical stuck entries.
        self._reconcile_stale_pending_trades(max_age_hours=72)

        # Auto-adapt live risk parameters from recent execution health.
        self._adapt_live_risk_from_recent_outcomes()
        self.last_pending_reconcile_at = datetime.now()

        # ═══════════════════════════════════════════════════════════════════════════
        # 🛡️ DRAWDOWN GUARDIAN — Initialize at startup (not lazily)
        # Config derived from risk_limits to ensure single source of truth
        # ═══════════════════════════════════════════════════════════════════════════
        try:
            from core.drawdown_guardian import DrawdownGuardian
            self._guardian = DrawdownGuardian({
                "max_daily_loss_pct": 3.0,
                "max_weekly_loss_pct": 7.0,
                "trailing_stop_pct": self.risk_limits['max_drawdown_pct'] * 100,   # 8% — matches risk_limits
                "critical_dd_pct": 15.0,
                "default_stop_loss_pct": self.risk_limits['stop_loss_pct'] * 100,   # 2% — matches risk_limits
                "crypto_stop_loss_pct": 4.0,
                "max_single_pos": self.risk_limits['position_size_pct'] * 100,      # 15% — matches risk_limits
                "max_sector_exposure": 40.0,
                "max_positions_normal": self.risk_limits['max_positions'],           # 10 — matches risk_limits
                "max_positions_dd": 5,
                "max_positions_crisis": 3,
                "max_correlated": self.risk_limits['max_correlated_positions'],      # 3 — matches risk_limits
            })
            self.logger.info("🛡️ DrawdownGuardian initialized at startup — 10-layer protection active")
        except Exception as guardian_init_err:
            self._guardian = None
            self.logger.error(f"⚠️ DrawdownGuardian failed to initialize: {guardian_init_err}")

        # Resource Monitoring
        self.resource_alerts = {
            'memory_critical': 97.0,  # Alert if memory >97%
            'memory_warning': 95.0,   # Warning if memory >95%
            'disk_critical': 95.0,    # Alert if disk >95%
            'disk_warning': 90.0      # Warning if disk >90%
        }
        
        self.logger.info("=" * 80)
        self.logger.info(" PROMETHEUS ULTIMATE TRADING LAUNCHER")
        self.logger.info("=" * 80)
        self.logger.info(f"Mode: LIVE TRADING + Shadow Learning ($100K virtual parallel)")
        self.logger.info(f"Live Track Record: 18/40 wins (45%), ~$98.65 equity")
        self.logger.info(f"Recent (Feb 16+): 14/16 (87.5%) | Scale-Out: 9/9 | All AI autonomous")
        self.logger.info(f"IB Account: {self.ib_account}")
        self.logger.info(f"Risk Limits: {self.risk_limits}")
        self.logger.info("=" * 80)

    def initialize_learning_database(self):
        """Initialize the learning database with proper schema"""
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            # Create trade_history table with all required columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL,
                    broker TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning TEXT,
                    timestamp TEXT NOT NULL,
                    order_id TEXT,
                    status TEXT DEFAULT 'executed',
                    profit_loss REAL DEFAULT 0,
                    exit_price REAL,
                    exit_timestamp TEXT,
                    hold_duration_seconds INTEGER,
                    ai_confidence REAL,
                    exit_reason TEXT
                )
            """)

            # ═══════════════════════════════════════════════════════════════
            # 🔧 FIX: Add missing columns to existing trade_history tables
            # The P/L UPDATE in _persist_learning_outcome() needs exit_reason
            # and ai_confidence columns - without them the entire UPDATE fails
            # silently, leaving profit_loss=0 for all trades (the recording bug)
            # ═══════════════════════════════════════════════════════════════
            for col_def in [
                ("ai_confidence", "REAL"),
                ("exit_reason", "TEXT"),
            ]:
                try:
                    cursor.execute(f"ALTER TABLE trade_history ADD COLUMN {col_def[0]} {col_def[1]}")
                    self.logger.info(f"  Added missing column trade_history.{col_def[0]}")
                except sqlite3.OperationalError:
                    pass  # Column already exists

            # Create performance_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_profit_loss REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    average_profit REAL DEFAULT 0,
                    average_loss REAL DEFAULT 0,
                    sharpe_ratio REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    current_balance REAL DEFAULT 0
                )
            """)

            # Create learning_insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    symbol TEXT,
                    description TEXT NOT NULL,
                    confidence_impact REAL DEFAULT 0,
                    applied BOOLEAN DEFAULT 0
                )
            """)

            # Create position_tracking table for enhancement persistence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS position_tracking (
                    symbol TEXT PRIMARY KEY,
                    position_high REAL,
                    entry_time TEXT,
                    scaled_level INTEGER DEFAULT 0,
                    dca_count INTEGER DEFAULT 0,
                    trade_id TEXT,
                    updated_at TEXT
                )
            """)

            # Add trade_id column if it doesn't exist (migration for existing databases)
            try:
                cursor.execute("ALTER TABLE position_tracking ADD COLUMN trade_id TEXT")
            except:
                pass  # Column already exists

            db.commit()
            db.close()

            self.logger.info(" Learning database initialized with full schema")

            # Load existing position tracking data
            self._load_position_tracking()

        except Exception as e:
            self.logger.error(f"Failed to initialize learning database: {e}")

    def _adapt_live_risk_from_recent_outcomes(self) -> None:
        """Adapt confidence/position limits from recent trade lifecycle health.

        This calibration is intentionally conservative:
        - Tighten when pending backlog is high or realized win rate weakens.
        - Relax slightly only when closure rate and realized outcomes are healthy.
        """
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            # Use recent slice to detect current regime/engine health.
            recent = cursor.execute(
                """
                SELECT timestamp, profit_loss, exit_price, ai_confidence
                FROM trade_history
                WHERE COALESCE(LOWER(status), 'pending') NOT IN ('expired', 'reconciled', 'cancelled', 'rejected')
                ORDER BY timestamp DESC
                LIMIT 120
                """
            ).fetchall()
            db.close()

            if not recent:
                self.logger.info("[ADAPT] No recent trades found; keeping configured risk limits")
                return

            total = len(recent)
            closed = [r for r in recent if r[2] is not None]
            pending = total - len(closed)
            pending_ratio = pending / total if total else 0.0

            pnl_values = [r[1] for r in closed if r[1] is not None]
            wins = [p for p in pnl_values if p > 0]
            losses = [p for p in pnl_values if p < 0]
            decisive = len(wins) + len(losses)
            win_rate = (len(wins) / decisive) if decisive > 0 else None

            # Confidence distribution from executed signals (closed+pending).
            confidences = [r[3] for r in recent if r[3] is not None]
            conf_avg = (sum(confidences) / len(confidences)) if confidences else None

            old_min_conf = float(self.risk_limits.get('min_confidence', 0.70))
            old_pos_size = float(self.risk_limits.get('position_size_pct', 0.15))
            old_max_positions = int(self.risk_limits.get('max_positions', 10))

            new_min_conf = old_min_conf
            new_pos_size = old_pos_size
            new_max_positions = old_max_positions
            reasons: List[str] = []

            # 1) Pending backlog: tighten quickly when exits are lagging.
            if pending_ratio >= 0.55:
                new_min_conf = max(new_min_conf, 0.78)
                new_pos_size *= 0.75
                new_max_positions = min(new_max_positions, 6)
                reasons.append(f"high_pending={pending}/{total} ({pending_ratio:.0%})")
            elif pending_ratio >= 0.40:
                new_min_conf = max(new_min_conf, 0.74)
                new_pos_size *= 0.85
                new_max_positions = min(new_max_positions, 8)
                reasons.append(f"elevated_pending={pending}/{total} ({pending_ratio:.0%})")

            # 2) Realized quality: use only decisive closed trades.
            if win_rate is not None and decisive >= 8:
                if win_rate < 0.50:
                    new_min_conf = max(new_min_conf, 0.76)
                    new_pos_size *= 0.90
                    reasons.append(f"weak_winrate={win_rate:.0%} ({decisive} decisive)")
                elif win_rate > 0.65 and pending_ratio < 0.30:
                    new_min_conf = min(new_min_conf, 0.70)
                    new_pos_size *= 1.05
                    reasons.append(f"healthy_winrate={win_rate:.0%} ({decisive} decisive)")

            # 3) Keep threshold near observed confidence distribution.
            # If the engine confidence has compressed, do not set threshold unrealistically high.
            if conf_avg is not None:
                # Cap threshold to average+0.08, but never below 0.65.
                distribution_cap = max(0.65, min(0.88, conf_avg + 0.08))
                if new_min_conf > distribution_cap:
                    reasons.append(f"conf_distribution_cap={distribution_cap:.2f} (avg={conf_avg:.2f})")
                    new_min_conf = distribution_cap

            # Final safety clamps.
            new_min_conf = min(max(new_min_conf, 0.65), 0.88)
            new_pos_size = min(max(new_pos_size, 0.05), 0.18)
            new_max_positions = min(max(new_max_positions, 4), 12)

            self.risk_limits['min_confidence'] = round(new_min_conf, 3)
            self.risk_limits['position_size_pct'] = round(new_pos_size, 4)
            self.risk_limits['max_positions'] = int(new_max_positions)

            summary = (
                f"[ADAPT] total={total} closed={len(closed)} pending={pending} "
                f"pending_ratio={pending_ratio:.0%} "
                f"win_rate={(f'{win_rate:.0%}' if win_rate is not None else 'n/a')} "
                f"conf_avg={(f'{conf_avg:.2f}' if conf_avg is not None else 'n/a')}"
            )
            self.logger.info(summary)
            self.logger.info(
                "[ADAPT] min_confidence %.2f -> %.2f | position_size %.2f%% -> %.2f%% | max_positions %d -> %d",
                old_min_conf,
                self.risk_limits['min_confidence'],
                old_pos_size * 100,
                self.risk_limits['position_size_pct'] * 100,
                old_max_positions,
                self.risk_limits['max_positions'],
            )
            if reasons:
                self.logger.info(f"[ADAPT] reasons: {', '.join(reasons)}")

        except Exception as e:
            self.logger.warning(f"[ADAPT] Risk adaptation skipped due to error: {e}")

    def _reconcile_stale_pending_trades(self, max_age_hours: int = 72) -> int:
        """Mark very old pending records as expired to prevent lifecycle drift.

        This is a database reconciliation step only; it does not place broker orders.
        It prevents years-old unresolved rows from distorting adaptation logic.
        """
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            # Ensure optional lifecycle notes column exists for older schemas.
            try:
                cursor.execute("ALTER TABLE trade_history ADD COLUMN reconciliation_note TEXT")
            except sqlite3.OperationalError:
                pass

            cursor.execute(
                """
                UPDATE trade_history
                SET
                    status = 'expired',
                    exit_timestamp = COALESCE(exit_timestamp, datetime('now')),
                    exit_reason = COALESCE(exit_reason, 'stale_pending_timeout'),
                    reconciliation_note = COALESCE(reconciliation_note, 'Auto-expired by lifecycle reconciler')
                WHERE
                    exit_price IS NULL
                    AND COALESCE(LOWER(status), 'pending') IN ('pending', 'submitted', 'open')
                    AND (julianday('now') - julianday(replace(substr(timestamp, 1, 19), 'T', ' '))) >= (? / 24.0)
                """,
                (float(max_age_hours),),
            )

            updated = int(cursor.rowcount or 0)
            db.commit()
            db.close()

            if updated > 0:
                self.logger.info(
                    f"[RECONCILE] Marked {updated} stale pending trades as expired (age >= {max_age_hours}h)"
                )
            else:
                self.logger.info(f"[RECONCILE] No stale pending trades found (age >= {max_age_hours}h)")

            return updated

        except Exception as e:
            self.logger.warning(f"[RECONCILE] Stale pending reconciliation skipped due to error: {e}")
            return 0

    def calibrate_broker_parameters(self, historical_trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calibrate trading parameters based on historical trade data.
        
        Analyzes execution quality, slippage patterns, and market conditions to
        optimize broker-specific parameters.
        
        Args:
            historical_trades: List of previous trades with execution data
            
        Returns:
            Dictionary with calibrated parameters:
            - avg_slippage_pct: Average slippage observed
            - execution_quality_score: Overall execution quality (0-1)
            - optimal_position_size: Suggested position size
            - risk_adjustment_factor: Factor to adjust risk parameters
        """
        try:
            if not historical_trades:
                self.logger.warning("[CALIBRATION] No historical trades - using defaults")
                return {
                    'avg_slippage_pct': 0.0,
                    'execution_quality_score': 0.5,
                    'optimal_position_size': self.risk_limits['position_size_pct'],
                    'risk_adjustment_factor': 1.0
                }
            
            # Calculate slippage metrics
            slippages = []
            for trade in historical_trades:
                if 'entry_price' in trade and 'signal_price' in trade:
                    slippage = abs(trade['entry_price'] - trade['signal_price']) / trade['signal_price']
                    slippages.append(slippage)
            
            avg_slippage = sum(slippages) / len(slippages) if slippages else 0.0
            
            # Calculate execution quality
            total_trades = len(historical_trades)
            filled_trades = sum(1 for t in historical_trades if t.get('status') == 'filled')
            execution_quality = filled_trades / total_trades if total_trades > 0 else 0.5
            
            # Calculate win rate for position sizing
            winning_trades = sum(1 for t in historical_trades if t.get('profit_loss', 0) > 0)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0.5
            
            # Adjust position size based on win rate
            # Higher win rate = can trade larger positions
            # Lower win rate = need to trade smaller positions
            optimal_position_size = self.risk_limits['position_size_pct'] * (0.5 + win_rate)
            
            # Risk adjustment: if execution is poor or slippage is high, reduce risk
            risk_adjustment = 1.0
            if avg_slippage > 0.01:  # >1% slippage
                risk_adjustment *= 0.8
            if execution_quality < 0.8:  # <80% execution rate
                risk_adjustment *= 0.9
            
            calibrated = {
                'avg_slippage_pct': avg_slippage,
                'execution_quality_score': execution_quality,
                'optimal_position_size': optimal_position_size,
                'risk_adjustment_factor': risk_adjustment,
                'win_rate': win_rate,
                'total_trades_analyzed': total_trades
            }
            
            self.logger.info(f"[CALIBRATION] Broker Parameters Calibrated:")
            self.logger.info(f"  - Avg Slippage: {avg_slippage*100:.3f}%")
            self.logger.info(f"  - Execution Quality: {execution_quality*100:.1f}%")
            self.logger.info(f"  - Optimal Position Size: {optimal_position_size*100:.1f}%")
            self.logger.info(f"  - Risk Adjustment Factor: {risk_adjustment:.2f}")
            self.logger.info(f"  - Win Rate: {win_rate*100:.1f}%")
            self.logger.info(f"  - Trades Analyzed: {total_trades}")
            
            return calibrated
            
        except Exception as e:
            self.logger.error(f"[CALIBRATION] Error calibrating parameters: {e}")
            return {
                'avg_slippage_pct': 0.0,
                'execution_quality_score': 0.5,
                'optimal_position_size': self.risk_limits['position_size_pct'],
                'risk_adjustment_factor': 1.0
            }

    async def initialize_all_systems(self):
        """Initialize all 80+ systems in proper order"""
        print("\n" + "=" * 80)
        print("INITIALIZING ALL SYSTEMS")
        print("=" * 80)
        
        # Tier 1: Critical Systems
        await self._initialize_tier1_critical()
        
        # Tier 2: Revolutionary Core
        await self._initialize_tier2_revolutionary()

        # Tier 3: Data Intelligence Sources
        await self._initialize_tier3_data_sources()

        # Tier 4: Live Broker Connections
        await self._initialize_tier4_live_brokers()

        # Tier 5: Monitoring & Safety
        await self._initialize_tier5_monitoring()

        # Tier 6: Phase 21 — New AI Integrations
        await self._initialize_tier6_phase21_integrations()
        
        print("\n" + "=" * 80)
        print(f" INITIALIZATION COMPLETE")
        print(f"   Active Systems: {len(self.systems)}")
        print(f"   Failed Systems: {len(self.failed_systems)}")
        print("=" * 80)
    
    async def _initialize_tier1_critical(self):
        """Initialize Tier 1: Critical Trading Systems"""
        print("\n TIER 1: CRITICAL SYSTEMS")
        print("-" * 40)
        
        if not TIER1_AVAILABLE:
            print("   Tier 1 systems not fully available")
            return
        
        try:
            self.systems['market_data'] = RealTimeMarketDataOrchestrator()
            print("   Market Data Orchestrator")
            self.system_health['market_data'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize market_data: {e}")
            self.failed_systems.append('market_data')
        
        try:
            self.systems['ai_intelligence'] = OpenAITradingIntelligence()
            print("   AI Trading Intelligence")
            self.system_health['ai_intelligence'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize ai_intelligence: {e}")
            self.failed_systems.append('ai_intelligence')
        
        try:
            self.systems['trading_engine'] = AdvancedTradingEngine()
            print("   Advanced Trading Engine")
            self.system_health['trading_engine'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize trading_engine: {e}")
            self.failed_systems.append('trading_engine')
        
        try:
            self.systems['ai_learning'] = get_ai_learning_engine()
            print("   AI Learning Engine")
            self.system_health['ai_learning'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize ai_learning: {e}")
            self.failed_systems.append('ai_learning')
        
        try:
            self.systems['continuous_learning'] = ContinuousLearningEngine()
            print("   Continuous Learning Engine")
            self.system_health['continuous_learning'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize continuous_learning: {e}")
            self.failed_systems.append('continuous_learning')
        
        try:
            self.systems['persistent_trading'] = persistent_trading_engine
            print("   Persistent Trading Engine")
            self.system_health['persistent_trading'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize persistent_trading: {e}")
            self.failed_systems.append('persistent_trading')
    
    async def _initialize_tier2_revolutionary(self):
        """Initialize Tier 2: Revolutionary AI Systems"""
        print("\n TIER 2: REVOLUTIONARY CORE")
        print("-" * 40)

        if not TIER2_AVAILABLE:
            print("   Tier 2 systems not fully available")
            return

        try:
            self.systems['ai_consciousness'] = AIConsciousnessEngine()
            print("   AI Consciousness Engine (95% level)")
            self.system_health['ai_consciousness'] = 'AVAILABLE'
        except Exception as e:
            self.logger.error(f"Failed to initialize ai_consciousness: {e}")
            self.failed_systems.append('ai_consciousness')

        try:
            # Quantum Trading Engine requires config
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
            self.systems['quantum_trading'] = QuantumTradingEngine(quantum_config)
            print("   Quantum Trading Engine (50-qubit)")
            self.system_health['quantum_trading'] = 'AVAILABLE'
        except Exception as e:
            self.logger.error(f"Failed to initialize quantum_trading: {e}")
            self.failed_systems.append('quantum_trading')

        try:
            # Market Oracle Engine requires config
            oracle_config = {
                'ragflow_api_key': 'demo_key',
                'ragflow_base_url': 'http://localhost:9380',
                'prediction_horizon': '24h',
                'confidence_threshold': 0.72
            }
            self.systems['market_oracle'] = MarketOracleEngine(oracle_config)
            print("   Market Oracle Engine")
            self.system_health['market_oracle'] = 'AVAILABLE'
        except Exception as e:
            self.logger.error(f"Failed to initialize market_oracle: {e}")
            self.failed_systems.append('market_oracle')

        try:
            self.systems['gpt_oss'] = GPTOSSTradingAdapter()
            # Check if GPT-OSS backend is available
            gpt_oss_status = "✅ GPT-OSS Trading Adapter"
            if hasattr(self.systems['gpt_oss'], 'model_size'):
                model_size = getattr(self.systems['gpt_oss'], 'model_size', '20b')
                gpt_oss_status += f" (CPT-OSS {model_size})"
            print(f"   {gpt_oss_status}")
            self.system_health['gpt_oss'] = 'ACTIVE'
            self.logger.info("✅ CPT-OSS (GPT-OSS) initialized and ready for trading signals")
        except Exception as e:
            self.logger.error(f"Failed to initialize gpt_oss: {e}")
            self.failed_systems.append('gpt_oss')
            print(f"   ⚠️  GPT-OSS Trading Adapter (failed to initialize)")

        # Chart Vision Analyzer (llava:7b)
        try:
            chart_vision = ChartVisionAnalyzer()
            await chart_vision.initialize()
            if chart_vision.is_available():
                self.systems['chart_vision'] = chart_vision
                print(f"   ✅ Chart Vision Analyzer ({chart_vision.vision_model})")
                self.system_health['chart_vision'] = 'ACTIVE'
                self.logger.info(f"✅ Chart Vision Analyzer initialized - model: {chart_vision.vision_model}")
            else:
                print("   ⚠️  Chart Vision Analyzer (vision model not available)")
                self.system_health['chart_vision'] = 'UNAVAILABLE'
        except Exception as e:
            self.logger.error(f"Failed to initialize chart_vision: {e}")
            self.failed_systems.append('chart_vision')
            print(f"   ⚠️  Chart Vision Analyzer (failed to initialize)")

        # 🤖 HIERARCHICAL AGENT COORDINATOR - 17 Agents + 3 Supervisors
        try:
            self.systems['agent_coordinator'] = HierarchicalAgentCoordinator()
            print("   🤖 Hierarchical Agent Coordinator (17 agents + 3 supervisors)")
            self.system_health['agent_coordinator'] = 'ACTIVE'
            self.logger.info("✅ Agent Coordinator initialized - 17 execution agents + 3 supervisor agents")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent_coordinator: {e}")
            self.failed_systems.append('agent_coordinator')
            print(f"   ⚠️  Agent Coordinator (failed to initialize)")

    async def _initialize_tier3_data_sources(self):
        """Initialize Tier 3: Data Intelligence Sources"""
        print("\n TIER 3: DATA INTELLIGENCE SOURCES")
        print("-" * 40)

        if not DATA_SOURCES_AVAILABLE:
            print("   Data intelligence sources not fully available")
            return

        try:
            self.systems['real_world_data'] = RealWorldDataOrchestrator()
            print("   Real-World Data Orchestrator (1000+ sources)")
            self.system_health['real_world_data'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize real_world_data: {e}")
            self.failed_systems.append('real_world_data')

        try:
            self.systems['google_trends'] = GoogleTrendsDataSource()
            print("   Google Trends Data Source")
            self.system_health['google_trends'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize google_trends: {e}")
            self.failed_systems.append('google_trends')

        try:
            self.systems['reddit_data'] = RedditDataSource()
            print("   Reddit Data Source (WallStreetBets)")
            self.system_health['reddit_data'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize reddit_data: {e}")
            self.failed_systems.append('reddit_data')

        try:
            self.systems['coingecko_extended'] = CoinGeckoDataSource()
            print("   CoinGecko Extended Data Source")
            self.system_health['coingecko_extended'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize coingecko_extended: {e}")
            self.failed_systems.append('coingecko_extended')

        try:
            self.systems['yahoo_finance'] = YahooFinanceDataSource()
            print("   Yahoo Finance Data Source (FREE)")
            self.system_health['yahoo_finance'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize yahoo_finance: {e}")
            self.failed_systems.append('yahoo_finance')

        try:
            self.systems['n8n_workflows'] = N8NWorkflowManager()
            print("   N8N Workflow Manager (Automated Intelligence)")
            self.system_health['n8n_workflows'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize n8n_workflows: {e}")
            self.failed_systems.append('n8n_workflows')

        # Initialize Market Intelligence Agents
        await self._initialize_market_intelligence_agents()

    async def _initialize_market_intelligence_agents(self):
        """Initialize Market Intelligence Agents for gap detection and opportunity scanning"""
        print("\n 🔍 MARKET INTELLIGENCE AGENTS")
        print("-" * 40)

        if not MARKET_INTELLIGENCE_AVAILABLE:
            print("   ⚠️ Market Intelligence Agents not available")
            return

        try:
            self.systems['gap_detector'] = GapDetectionAgent(agent_id="prometheus_gap_detector")
            print("   🔍 Gap Detection Agent (price gaps > 2%)")
            self.system_health['gap_detector'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize gap_detector: {e}")
            self.failed_systems.append('gap_detector')

        try:
            self.systems['opportunity_scanner'] = OpportunityScannerAgent(agent_id="prometheus_opportunity_scanner")
            print("   🎯 Opportunity Scanner Agent (breakouts, momentum, volume)")
            self.system_health['opportunity_scanner'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize opportunity_scanner: {e}")
            self.failed_systems.append('opportunity_scanner')

        try:
            self.systems['market_researcher'] = MarketResearchAgent(agent_id="prometheus_market_researcher")
            print("   📊 Market Research Agent (regime detection, sentiment)")
            self.system_health['market_researcher'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize market_researcher: {e}")
            self.failed_systems.append('market_researcher')

        self.logger.info("✅ Market Intelligence Agents initialized")

    async def _initialize_tier4_live_brokers(self):
        """Initialize Tier 4: Live Broker Connections (Alpaca + IB)"""
        print("\n TIER 4: BROKER CONNECTIONS")
        print("-" * 40)

        if not BROKERS_AVAILABLE:
            print("   CRITICAL: Broker systems not available!")
            self.logger.error("Cannot proceed without broker systems")
            return

        # Initialize Alpaca LIVE Broker (Stocks + Crypto 24/7)
        try:
            # LIVE mode: prefer ALPACA_LIVE_KEY, fall back to other keys
            alpaca_api_key = (os.getenv('ALPACA_LIVE_KEY') or
                            os.getenv('ALPACA_LIVE_API_KEY') or 
                            os.getenv('ALPACA_API_KEY') or
                            os.getenv('APCA_API_KEY_ID') or
                            os.getenv('ALPACA_KEY'))
            
            alpaca_secret = (os.getenv('ALPACA_LIVE_SECRET') or
                           os.getenv('ALPACA_LIVE_SECRET_KEY') or 
                           os.getenv('ALPACA_SECRET_KEY') or
                           os.getenv('APCA_API_SECRET_KEY') or
                           os.getenv('ALPACA_SECRET'))
            
            alpaca_config = {
                'api_key': alpaca_api_key,
                'secret_key': alpaca_secret,
                'paper_trading': False  # LIVE trading
            }
            
            # Log which variables were found (without showing values)
            if alpaca_api_key:
                self.logger.info(f"✅ Alpaca API key found ({len(alpaca_api_key)} chars)")
            else:
                self.logger.warning("⚠️ Alpaca API key not found - checked: ALPACA_LIVE_KEY, ALPACA_LIVE_API_KEY, ALPACA_API_KEY, APCA_API_KEY_ID, ALPACA_KEY")
            
            if alpaca_secret:
                self.logger.info(f"✅ Alpaca secret key found ({len(alpaca_secret)} chars)")
            else:
                self.logger.warning("⚠️ Alpaca secret key not found - checked: ALPACA_LIVE_SECRET, ALPACA_LIVE_SECRET_KEY, ALPACA_SECRET_KEY, APCA_API_SECRET_KEY, ALPACA_SECRET")
            self.systems['alpaca_broker'] = AlpacaBroker(config=alpaca_config)
            await self.systems['alpaca_broker'].connect()
            print("   Alpaca Live Broker (Crypto 24/7)")
            self.system_health['alpaca_broker'] = 'ACTIVE'
        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca broker: {e}")
            self.failed_systems.append('alpaca_broker')

        # Initialize Interactive Brokers (Stocks during market hours)
        try:
            # Determine if paper or live based on port
            # TWS: 7496 = Paper, 7497 = Live
            # Gateway: 4001 = Paper, 4002 = Live
            is_paper = (self.ib_port in [7496, 4001])
            # Client ID: Use random ID (10-99) to avoid conflicts with TWS/other apps that use 0-5
            # Can override via IB_CLIENT_ID env var if specific ID needed
            import random
            default_client_id = random.randint(10, 99)
            ib_client_id = int(os.getenv('IB_CLIENT_ID', str(default_client_id)))
            ib_config = {
                'host': '127.0.0.1',
                'port': self.ib_port,  # 4002 = Gateway Live, 7497 = TWS Live
                'client_id': ib_client_id,  # Random ID (10-99) to avoid conflicts
                'paper_trading': is_paper,
                'account_id': self.ib_account  # U21922116
            }
            print(f"   Connecting to IB Gateway on port {self.ib_port} (client_id: {ib_client_id}, {'PAPER' if is_paper else 'LIVE'} trading)...")
            self.systems['ib_broker'] = InteractiveBrokersBroker(config=ib_config)
            connection_result = await self.systems['ib_broker'].connect()
            
            if connection_result and self.systems['ib_broker'].connected:
                print(f"   ✅ Interactive Brokers {'PAPER' if is_paper else 'LIVE'} Connected (Account: {self.ib_account})")
                self.system_health['ib_broker'] = 'ACTIVE'
            else:
                print(f"   ❌ Interactive Brokers connection FAILED")
                print(f"      Port {self.ib_port} not accessible - is IB Gateway running?")
                print(f"      Will retry connection automatically...")
                self.system_health['ib_broker'] = 'CONNECTING'
                self.failed_systems.append('ib_broker')
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize IB broker: {e}")
            print(f"   ❌ IB Broker Error: {str(e)}")
            print(f"      Check: Is IB Gateway running on port {self.ib_port}?")
            print(f"      Check: Are API connections enabled in IB Gateway?")
            self.failed_systems.append('ib_broker')
            self.system_health['ib_broker'] = 'FAILED'

        # ═══════════════════════════════════════════════════════════════
        # 🔄 PARALLEL SHADOW TRADER — autonomous virtual trading for learning
        # Runs alongside live trading: receives ALL signals, makes its own
        # decisions, and feeds results back so Prometheus learns continuously.
        # ═══════════════════════════════════════════════════════════════
        if SHADOW_TRADING_AVAILABLE:
            try:
                self.systems['shadow_trader'] = PrometheusParallelShadowTrading(
                    starting_capital=100_000.0,
                    max_position_pct=0.10,
                    config_name="live_parallel",
                )
                print("   🔄 Parallel Shadow Trader ($100K virtual — autonomous learning)")
                self.system_health['shadow_trader'] = 'ACTIVE'
                self.logger.info("✅ Shadow trader initialized: $100K virtual capital, autonomous learning active")
            except Exception as e:
                self.logger.error(f"Failed to initialize shadow trader: {e}")
                self.failed_systems.append('shadow_trader')
        else:
            print("   ⚠️  Shadow Trader (not available)")

        print("\n   LIVE TRADING ACTIVE + Shadow Learning ($100K virtual parallel)")
        print(f"   Live Track Record: 18/40 wins (45%), ~$98.65 equity | Recent: 14/16 (87.5%)")
        print(f"   Risk Limits: ${self.risk_limits['daily_loss_limit']} daily loss")
        print(f"   Position Size: {self.risk_limits['position_size_pct']*100}% per trade")
        print(f"   Max Positions: {self.risk_limits['max_positions']}")

    async def _initialize_tier5_monitoring(self):
        """Initialize Tier 5: Monitoring & Safety Systems"""
        print("\n TIER 5: MONITORING & SAFETY")
        print("-" * 40)

        if MONITORING_AVAILABLE:
            try:
                self.systems['monitoring'] = AdvancedMonitoringSystem()
                print("   Advanced Monitoring System")
                self.system_health['monitoring'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize monitoring: {e}")
                self.failed_systems.append('monitoring')

        print("   Resource Monitoring Active")
        print("   Risk Management Active")
        print("   Performance Tracking Active")

    async def _initialize_tier6_phase21_integrations(self):
        """Initialize Tier 6: Phase 21 — New AI Integrations (LangGraph, OpenBB, CCXT, Gymnasium, Mercury2, Cache)"""
        print("\n TIER 6: PHASE 21 NEW INTEGRATIONS")
        print("-" * 40)

        # 1. Prometheus Cache (initialize first — used by other systems)
        if CACHE_AVAILABLE:
            try:
                self.systems['prometheus_cache'] = get_prometheus_cache()
                backend = "Redis" if self.systems['prometheus_cache'].use_redis else "In-Memory"
                print(f"   Prometheus Cache ({backend} backend)")
                self.system_health['prometheus_cache'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize prometheus_cache: {e}")
                self.failed_systems.append('prometheus_cache')
        else:
            print("   Prometheus Cache (not available)")

        # 2. LangGraph Trading Orchestrator
        if LANGGRAPH_AVAILABLE:
            try:
                self.systems['langgraph'] = LangGraphTradingOrchestrator()
                print("   LangGraph Orchestrator (4-node decision graph)")
                self.system_health['langgraph'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize langgraph: {e}")
                self.failed_systems.append('langgraph')
        else:
            print("   LangGraph Orchestrator (not available)")

        # 3. OpenBB Data Provider
        if OPENBB_AVAILABLE:
            try:
                self.systems['openbb'] = OpenBBDataProvider()
                print("   OpenBB Data Provider (350+ datasets)")
                self.system_health['openbb'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize openbb: {e}")
                self.failed_systems.append('openbb')
        else:
            print("   OpenBB Data Provider (not available)")

        # 4. CCXT Exchange Bridge
        if CCXT_AVAILABLE:
            try:
                self.systems['ccxt_bridge'] = CCXTExchangeBridge()
                print("   CCXT Exchange Bridge (107+ crypto exchanges)")
                self.system_health['ccxt_bridge'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize ccxt_bridge: {e}")
                self.failed_systems.append('ccxt_bridge')
        else:
            print("   CCXT Exchange Bridge (not available)")

        # 5. Gymnasium / SB3 RL
        if GYMNASIUM_AVAILABLE:
            try:
                self.systems['gymnasium_sb3'] = {"env": TradingGymEnv, "agent": SB3TradingAgent}
                print("   Gymnasium/SB3 RL (PPO, A2C, DQN)")
                self.system_health['gymnasium_sb3'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize gymnasium_sb3: {e}")
                self.failed_systems.append('gymnasium_sb3')
        else:
            print("   Gymnasium/SB3 RL (not available)")

        # 6. Mercury2 Diffusion LLM
        if MERCURY2_AVAILABLE:
            try:
                self.systems['mercury2'] = Mercury2Adapter()
                print("   Mercury2 Diffusion LLM (1,009 tok/s)")
                self.system_health['mercury2'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize mercury2: {e}")
                self.failed_systems.append('mercury2')
        else:
            print("   Mercury2 LLM (needs API key: MERCURY_API_KEY)")

        # 7. LlamaIndex SEC Filings RAG
        if LLAMAINDEX_AVAILABLE:
            try:
                self.systems['sec_filings_rag'] = get_sec_analyzer()
                print("   LlamaIndex SEC Filings RAG (EDGAR pipeline)")
                self.system_health['sec_filings_rag'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize sec_filings_rag: {e}")
                self.failed_systems.append('sec_filings_rag')
        else:
            print("   LlamaIndex SEC Filings RAG (not available)")

        # 8. FinRL Portfolio Optimizer
        if FINRL_AVAILABLE:
            try:
                self.systems['finrl_optimizer'] = get_finrl_optimizer()
                print("   FinRL Portfolio Optimizer (DRL-based)")
                self.system_health['finrl_optimizer'] = 'ACTIVE'
            except Exception as e:
                self.logger.error(f"Failed to initialize finrl_optimizer: {e}")
                self.failed_systems.append('finrl_optimizer')
        else:
            print("   FinRL Portfolio Optimizer (not available)")

        all_tier6 = ['prometheus_cache', 'langgraph', 'openbb', 'ccxt_bridge', 'gymnasium_sb3', 'mercury2', 'sec_filings_rag', 'finrl_optimizer']
        active_count = sum(1 for s in all_tier6 if s in self.systems)
        print(f"\n   Phase 21 integrations: {active_count}/8 active")
        self.logger.info(f"Phase 21: {active_count}/8 new integrations initialized")

    async def monitor_resources(self):
        """Monitor system resources and alert if critical"""
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        if memory > self.resource_alerts['memory_critical']:
            self.logger.critical(f"CRITICAL: Memory usage at {memory}%!")
            return False
        elif memory > self.resource_alerts['memory_warning']:
            self.logger.warning(f"WARNING: Memory usage at {memory}%")

        if disk > self.resource_alerts['disk_critical']:
            self.logger.critical(f"CRITICAL: Disk usage at {disk}%!")
            return False
        elif disk > self.resource_alerts['disk_warning']:
            self.logger.warning(f"WARNING: Disk usage at {disk}%")

        return True

    async def adapt_trading_style(self):
        """
        🧠 AI-DRIVEN TRADING STYLE ADAPTATION
        Dynamically adapts trading style based on:
        - Market regime (from AI detection)
        - Recent performance trends
        - Market volatility
        - Win rate analysis
        - Drawdown status
        """
        # Detect market regime using AI
        self.market_regime = await self.detect_market_regime()

        style_factors = []
        style_scores = {'AGGRESSIVE': 0, 'BALANCED': 0, 'CONSERVATIVE': 0}

        # ═══════════════════════════════════════════════════════════════
        # 1. PERFORMANCE-BASED ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        if len(self.performance_history) > 5:
            recent_performance = self.performance_history[-10:] if len(self.performance_history) >= 10 else self.performance_history
            avg_performance = sum(recent_performance) / len(recent_performance)

            # Calculate win rate
            wins = sum(1 for p in recent_performance if p > 0)
            win_rate = wins / len(recent_performance)

            # Calculate max drawdown in recent trades
            cumulative = 0
            max_drawdown = 0
            peak = 0
            for p in recent_performance:
                cumulative += p
                if cumulative > peak:
                    peak = cumulative
                drawdown = peak - cumulative
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            # Performance scoring
            if avg_performance > 0.03 and win_rate > 0.55:
                style_scores['AGGRESSIVE'] += 2
                style_factors.append(f"StrongPerf({avg_performance:.1%},{win_rate:.0%}WR)")
            elif avg_performance > 0.01 and win_rate > 0.45:
                style_scores['AGGRESSIVE'] += 1
                style_scores['BALANCED'] += 1
                style_factors.append(f"GoodPerf({avg_performance:.1%})")
            elif avg_performance < -0.02 or win_rate < 0.35:
                style_scores['CONSERVATIVE'] += 2
                style_factors.append(f"WeakPerf({avg_performance:.1%},{win_rate:.0%}WR)")
            elif avg_performance < 0:
                style_scores['CONSERVATIVE'] += 1
                style_scores['BALANCED'] += 1
                style_factors.append(f"NegPerf({avg_performance:.1%})")
            else:
                style_scores['BALANCED'] += 1

            # Drawdown penalty
            if max_drawdown > 0.10:  # >10% drawdown
                style_scores['CONSERVATIVE'] += 2
                style_factors.append(f"HighDD({max_drawdown:.1%})")
            elif max_drawdown > 0.05:
                style_scores['CONSERVATIVE'] += 1
                style_factors.append(f"MedDD({max_drawdown:.1%})")

        # ═══════════════════════════════════════════════════════════════
        # 2. REGIME-BASED ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        if self.market_regime == 'TRENDING':
            style_scores['AGGRESSIVE'] += 2
            style_factors.append("TrendingMkt")
        elif self.market_regime == 'VOLATILE':
            style_scores['CONSERVATIVE'] += 2
            style_factors.append("VolatileMkt")
        elif self.market_regime == 'RANGING':
            style_scores['BALANCED'] += 1
            style_scores['CONSERVATIVE'] += 1
            style_factors.append("RangingMkt")
        else:  # NORMAL
            style_scores['BALANCED'] += 1

        # ═══════════════════════════════════════════════════════════════
        # 3. LEARNING DATABASE ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        try:
            import sqlite3
            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            # Get recent trade statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    AVG(profit_loss) as avg_pnl,
                    SUM(profit_loss) as total_pnl
                FROM trade_history
                WHERE timestamp > datetime('now', '-7 days')
            """)
            row = cursor.fetchone()
            db.close()

            if row and row[0] and row[0] > 5:
                total_trades = row[0]
                db_wins = row[1] or 0
                db_win_rate = db_wins / total_trades
                total_pnl = row[3] or 0

                if db_win_rate > 0.55 and total_pnl > 0:
                    style_scores['AGGRESSIVE'] += 1
                    style_factors.append(f"DB_WR({db_win_rate:.0%})")
                elif db_win_rate < 0.40 or total_pnl < -100:
                    style_scores['CONSERVATIVE'] += 1
                    style_factors.append(f"DB_Loss({total_pnl:.0f})")
        except Exception:
            pass

        # ═══════════════════════════════════════════════════════════════
        # 4. TIME-OF-DAY ANALYSIS
        # ═══════════════════════════════════════════════════════════════
        from datetime import datetime
        hour = datetime.now().hour

        # Market open/close volatility
        if 9 <= hour <= 10 or 15 <= hour <= 16:  # First/last hour
            style_scores['CONSERVATIVE'] += 1
            style_factors.append("HighVolHour")
        elif 11 <= hour <= 14:  # Midday calm
            style_scores['BALANCED'] += 1

        # ═══════════════════════════════════════════════════════════════
        # DETERMINE FINAL STYLE
        # ═══════════════════════════════════════════════════════════════
        # Get style with highest score
        self.trading_style = max(style_scores, key=style_scores.get)

        # Log the decision
        self.logger.info(f"🧠 AI TRADING STYLE ADAPTATION:")
        self.logger.info(f"   Scores: AGG={style_scores['AGGRESSIVE']} | BAL={style_scores['BALANCED']} | CON={style_scores['CONSERVATIVE']}")
        self.logger.info(f"   Factors: {', '.join(style_factors[:4])}")
        self.logger.info(f"   → Selected: {self.trading_style}")

        # Apply adaptations
        await self._apply_adaptations()

        # 🔧 AUTONOMOUS BASE PARAMETER ADAPTATION - Adjust base values based on account size & performance
        await self._adapt_base_parameters()

        self.logger.info(f"📊 Adaptations applied: Style={self.trading_style}, Regime={self.market_regime}")

    async def _adapt_base_parameters(self):
        """
        🔧 AUTONOMOUS BASE PARAMETER ADAPTATION
        Automatically adjusts base position_size_pct and take_profit_pct based on:
        - Account size (smaller accounts need larger position %)
        - Win rate (low win rate = need higher take profit to compensate)

        This allows PROMETHEUS to truly self-adapt, not just adjust multipliers.
        """
        try:
            # Get current equity from Alpaca
            alpaca_broker = self.systems.get('alpaca_broker')
            equity = 100.0  # Default

            if alpaca_broker:
                try:
                    account = await alpaca_broker.get_account()
                    equity = float(getattr(account, 'equity', 100))
                except Exception as e:
                    self.logger.debug(f"Could not get Alpaca equity: {e}")

            # ═══════════════════════════════════════════════════════════════
            # ADAPT POSITION SIZE BASED ON ACCOUNT SIZE
            # Smaller accounts need larger % to make meaningful trades
            # ═══════════════════════════════════════════════════════════════
            if equity < 500:
                new_position_size = 0.15  # 15% for very small accounts (<$500)
            elif equity < 2000:
                new_position_size = 0.10  # 10% for small accounts ($500-$2000)
            elif equity < 10000:
                new_position_size = 0.05  # 5% for medium accounts ($2000-$10000)
            else:
                new_position_size = 0.03  # 3% for large accounts (>$10000)

            # ═══════════════════════════════════════════════════════════════
            # ADAPT TAKE PROFIT BASED ON WIN RATE
            # Low win rate = need bigger wins to compensate for losses
            # ═══════════════════════════════════════════════════════════════
            win_rate = 0.5  # Default
            try:
                import sqlite3
                db = sqlite3.connect('prometheus_learning.db', timeout=10.0)
                cursor = db.cursor()
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins
                    FROM trade_history
                    WHERE profit_loss IS NOT NULL AND profit_loss != 0
                    AND timestamp > datetime('now', '-14 days')
                """)
                row = cursor.fetchone()
                db.close()

                if row and row[0] and row[0] > 5:  # Need at least 5 closed trades
                    total = row[0]
                    wins = row[1] or 0
                    win_rate = wins / total
            except Exception as e:
                self.logger.debug(f"Could not calculate win rate: {e}")

            # Adapt take profit based on win rate - REALISTIC VALUES based on actual trade data
            # Data shows: Max win was +1.12%, most trades between -3% and +1%
            # Need achievable targets that beat trading costs (~0.6% crypto, ~0.1% stocks)
            if win_rate < 0.30:
                new_take_profit = 0.025  # 2.5% - slightly higher target when losing often
            elif win_rate < 0.50:
                new_take_profit = 0.02   # 2% - balanced, achievable target
            else:
                new_take_profit = 0.015  # 1.5% - quick profits when winning consistently

            # ═══════════════════════════════════════════════════════════════
            # APPLY CHANGES (only if different)
            # ═══════════════════════════════════════════════════════════════
            old_pos_size = self.risk_limits['position_size_pct']
            old_take_profit = self.risk_limits['take_profit_pct']

            if old_pos_size != new_position_size or old_take_profit != new_take_profit:
                self.risk_limits['position_size_pct'] = new_position_size
                self.risk_limits['take_profit_pct'] = new_take_profit

                self.logger.info(f"🔧 AUTONOMOUS BASE PARAMETER ADAPTATION:")
                self.logger.info(f"   Account Equity: ${equity:.2f}")
                self.logger.info(f"   Win Rate (14d): {win_rate*100:.1f}%")
                self.logger.info(f"   Position Size: {old_pos_size*100:.1f}% → {new_position_size*100:.1f}%")
                self.logger.info(f"   Take Profit: {old_take_profit*100:.1f}% → {new_take_profit*100:.1f}%")

        except Exception as e:
            self.logger.error(f"Base parameter adaptation failed: {e}")

    def get_trading_cost(self, symbol: str, broker: str, trade_value: float) -> Dict[str, float]:
        """
        💰 COST-AWARE TRADING - Calculate actual trading costs for a trade

        Returns:
            Dict with 'per_trade', 'round_trip', 'min_profit_needed' costs
        """
        # Determine asset type from symbol
        is_crypto = '/' in symbol or symbol.endswith('USD') or symbol in [
            'BTC', 'ETH', 'SOL', 'DOGE', 'SHIB', 'AVAX', 'LINK', 'UNI', 'AAVE', 'CRV', 'PEPE'
        ]

        broker_lower = broker.lower() if broker else 'alpaca'

        if broker_lower == 'alpaca' or broker_lower == 'alpaca_broker':
            if is_crypto:
                costs = self.trading_costs['alpaca']['crypto']
            else:
                costs = self.trading_costs['alpaca']['stocks']
        elif broker_lower == 'ib' or broker_lower == 'interactive_brokers':
            costs = self.trading_costs['ib']['stocks']
        else:
            # Default to Alpaca stocks (lowest cost)
            costs = self.trading_costs['alpaca']['stocks']

        per_trade_cost = trade_value * costs['total_per_trade']
        round_trip_cost = trade_value * costs['round_trip']

        # Minimum profit needed to break even after costs
        min_profit_pct = costs['round_trip'] * 1.5  # Need 1.5x costs to be worthwhile

        return {
            'per_trade': per_trade_cost,
            'round_trip': round_trip_cost,
            'round_trip_pct': costs['round_trip'],
            'min_profit_pct': min_profit_pct,
            'asset_type': 'crypto' if is_crypto else 'stock',
            'broker': broker_lower
        }

    def is_trade_profitable_after_costs(self, symbol: str, broker: str,
                                         entry_price: float, current_price: float,
                                         quantity: float) -> Dict[str, Any]:
        """
        💰 Check if a trade would be profitable after accounting for trading costs

        Returns:
            Dict with 'is_profitable', 'gross_pnl', 'net_pnl', 'costs', 'recommendation'
        """
        trade_value = entry_price * quantity
        costs = self.get_trading_cost(symbol, broker, trade_value)

        # Calculate gross P/L
        gross_pnl = (current_price - entry_price) * quantity
        gross_pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0

        # Calculate net P/L after costs
        net_pnl = gross_pnl - costs['round_trip']
        net_pnl_pct = gross_pnl_pct - costs['round_trip_pct']

        # Determine if profitable
        is_profitable = net_pnl > 0

        # Recommendation
        if gross_pnl_pct < costs['min_profit_pct']:
            recommendation = 'HOLD'  # Not enough profit to cover costs
            reason = f"Gross {gross_pnl_pct*100:.2f}% < min needed {costs['min_profit_pct']*100:.2f}%"
        elif is_profitable:
            recommendation = 'SELL'  # Profitable after costs
            reason = f"Net profit ${net_pnl:.4f} ({net_pnl_pct*100:.2f}%)"
        else:
            recommendation = 'HOLD'  # Would lose money after costs
            reason = f"Would lose ${abs(net_pnl):.4f} after costs"

        return {
            'is_profitable': is_profitable,
            'gross_pnl': gross_pnl,
            'gross_pnl_pct': gross_pnl_pct,
            'net_pnl': net_pnl,
            'net_pnl_pct': net_pnl_pct,
            'costs': costs,
            'recommendation': recommendation,
            'reason': reason
        }

    def track_trading_costs(self, trade_data: Dict[str, Any], execution_data: Dict[str, Any],
                            session_daily_costs: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Track and accumulate trading costs across a trading session/day.
        
        Maintains detailed cost analytics to:
        - Monitor cumulative daily costs vs. budgets
        - Identify high-cost trading patterns
        - Optimize broker selection and trading behavior
        - Project profitability accounting for fees
        
        Args:
            trade_data: Trade execution details (symbol, quantity, entry_price, etc.)
            execution_data: Actual execution details (fill_price, timestamp, slippage, etc.)
            session_daily_costs: Existing daily cost tracking (will create if None)
            
        Returns:
            Updated cost tracking dictionary with:
            - total_costs: Sum of all costs for period
            - costs_by_type: Breakdown by fee type
            - costs_by_broker: Costs per broker
            - costs_by_symbol: Per-symbol cost tracking
            - daily_cost_vs_budget: Cost vs daily budget status
            - cost_metrics: Performance metrics
        """
        try:
            if session_daily_costs is None:
                session_daily_costs = {
                    'total_costs': 0.0,
                    'costs_by_type': {'commissions': 0.0, 'spreads': 0.0, 'slippage': 0.0, 'fees': 0.0},
                    'costs_by_broker': {},
                    'costs_by_symbol': {},
                    'trade_count': 0,
                    'total_trade_value': 0.0,
                    'avg_cost_per_trade': 0.0,
                    'daily_budget': 50.0,  # Default daily cost budget
                    'budget_used_pct': 0.0,
                    'high_cost_trades': [],  # Trades with costs > 0.5%
                    'period_start': None,
                    'trades_logged': []
                }
            
            # Extract trade details
            symbol = trade_data.get('symbol', 'UNKNOWN')
            broker = trade_data.get('broker', 'alpaca').lower()
            quantity = trade_data.get('quantity', 0)
            entry_price = trade_data.get('entry_price', 0)
            trade_value = entry_price * quantity
            
            # Extract execution details
            fill_price = execution_data.get('fill_price', entry_price)
            is_buy = execution_data.get('action', 'BUY').upper() == 'BUY'
            timestamp = execution_data.get('timestamp', None)
            
            # Calculate costs
            commission = execution_data.get('commission', 0.0)
            
            # Calculate spread cost (difference between limit and fill)
            limit_price = execution_data.get('limit_price', fill_price)
            spread_cost = abs(fill_price - limit_price) * quantity
            if not is_buy:
                spread_cost = abs(fill_price - limit_price) * quantity
            
            # Calculate slippage cost (difference from market price vs. fill)
            market_price = execution_data.get('market_price', fill_price)
            slippage = abs(fill_price - market_price)
            slippage_cost = slippage * quantity
            
            # Get expected costs from broker models
            expected_costs = self.get_trading_cost(symbol, broker, trade_value)
            
            # Total cost for this trade
            total_trade_cost = commission + spread_cost + slippage_cost
            cost_pct = total_trade_cost / trade_value if trade_value > 0 else 0
            
            # Update cost tracking
            session_daily_costs['total_costs'] += total_trade_cost
            session_daily_costs['costs_by_type']['commissions'] += commission
            session_daily_costs['costs_by_type']['spreads'] += spread_cost
            session_daily_costs['costs_by_type']['slippage'] += slippage_cost
            
            # Track by broker
            if broker not in session_daily_costs['costs_by_broker']:
                session_daily_costs['costs_by_broker'][broker] = {'total': 0.0, 'count': 0}
            session_daily_costs['costs_by_broker'][broker]['total'] += total_trade_cost
            session_daily_costs['costs_by_broker'][broker]['count'] += 1
            
            # Track by symbol
            if symbol not in session_daily_costs['costs_by_symbol']:
                session_daily_costs['costs_by_symbol'][symbol] = {'total': 0.0, 'count': 0}
            session_daily_costs['costs_by_symbol'][symbol]['total'] += total_trade_cost
            session_daily_costs['costs_by_symbol'][symbol]['count'] += 1
            
            # Track high-cost trades (>0.5% of trade value)
            if cost_pct > 0.005:
                session_daily_costs['high_cost_trades'].append({
                    'symbol': symbol,
                    'cost_pct': cost_pct,
                    'cost_amount': total_trade_cost,
                    'timestamp': timestamp
                })
            
            # Update trade count and value
            session_daily_costs['trade_count'] += 1
            session_daily_costs['total_trade_value'] += trade_value
            session_daily_costs['avg_cost_per_trade'] = (
                session_daily_costs['total_costs'] / session_daily_costs['trade_count']
                if session_daily_costs['trade_count'] > 0 else 0
            )
            
            # Calculate budget usage
            daily_budget = session_daily_costs.get('daily_budget', 50.0)
            session_daily_costs['budget_used_pct'] = (
                session_daily_costs['total_costs'] / daily_budget if daily_budget > 0 else 0
            )
            
            # Track trade details
            session_daily_costs['trades_logged'].append({
                'symbol': symbol,
                'broker': broker,
                'action': 'BUY' if is_buy else 'SELL',
                'quantity': quantity,
                'trade_value': trade_value,
                'commission': commission,
                'spread_cost': spread_cost,
                'slippage_cost': slippage_cost,
                'total_cost': total_trade_cost,
                'cost_pct': cost_pct,
                'timestamp': timestamp
            })
            
            # Logging
            if cost_pct > 0.01:  # >1% cost - noteworthy
                self.logger.warning(f"[COST] {symbol} @ {broker}: {cost_pct*100:.2f}% cost (${total_trade_cost:.4f}) - "
                                  f"Commission: ${commission:.4f}, Spread: ${spread_cost:.4f}, Slippage: ${slippage_cost:.4f}")
            else:
                self.logger.debug(f"[COST] {symbol} @ {broker}: {cost_pct*100:.2f}% cost")
            
            return session_daily_costs
            
        except Exception as e:
            self.logger.error(f"[COST] Error tracking trading costs: {e}")
            return session_daily_costs or {}

    async def detect_market_regime(self) -> str:
        """
        🧠 AI-DRIVEN MARKET REGIME DETECTION
        Analyzes multiple market indicators and AI systems to determine current regime:
        - VOLATILE: High volatility, unpredictable moves
        - TRENDING: Clear directional trend (bull or bear)
        - RANGING: Sideways movement, mean-reverting
        - NORMAL: Standard market conditions
        """
        try:
            regime_votes = {'VOLATILE': 0, 'TRENDING': 0, 'RANGING': 0, 'NORMAL': 0}
            confidence_scores = []
            analysis_sources = []

            # ═══════════════════════════════════════════════════════════════
            # 📊 MARKET RESEARCHER - Primary Regime Detection
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_researcher'):
                try:
                    researcher = self.systems['market_researcher']
                    # Get market intelligence for SPY (market proxy)
                    intel = await researcher.generate_market_intelligence(['SPY'])
                    if intel and hasattr(intel, 'market_regime'):
                        detected = intel.market_regime
                        # Map researcher regime to our regime types
                        regime_map = {
                            'TRENDING_BULL': 'TRENDING',
                            'TRENDING_BEAR': 'TRENDING',
                            'HIGH_VOLATILITY': 'VOLATILE',
                            'SIDEWAYS': 'RANGING',
                            'UNKNOWN': 'NORMAL'
                        }
                        mapped_regime = regime_map.get(detected, 'NORMAL')
                        regime_votes[mapped_regime] += 2.0  # High weight
                        confidence_scores.append(0.75)
                        analysis_sources.append(f'MarketResearcher({detected})')
                        self.logger.debug(f"MarketResearcher detected: {detected} -> {mapped_regime}")
                except Exception as e:
                    self.logger.debug(f"Market researcher regime detection failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📈 YAHOO FINANCE - Volatility & Trend Analysis
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('yahoo_finance'):
                try:
                    yf = self.systems['yahoo_finance']
                    # Get SPY historical data for regime detection
                    if hasattr(yf, 'get_historical_data_async'):
                        hist_data = await yf.get_historical_data_async('SPY', timeframe='1Day', limit=20)
                    elif hasattr(yf, 'get_historical_data'):
                        hist_data = yf.get_historical_data('SPY', timeframe='1Day', limit=20)
                    else:
                        hist_data = None

                    if hist_data and len(hist_data) >= 10:
                        import numpy as np
                        # Calculate returns
                        closes = [bar.get('close', bar.get('Close', 0)) for bar in hist_data if bar]
                        if len(closes) >= 10:
                            returns = np.diff(closes) / closes[:-1]
                            volatility = np.std(returns)
                            trend = (closes[-1] - closes[0]) / closes[0] if closes[0] > 0 else 0

                            # Volatility detection
                            if volatility > 0.025:  # >2.5% daily volatility
                                regime_votes['VOLATILE'] += 1.5
                                analysis_sources.append(f'YF_Volatility({volatility*100:.1f}%)')
                            elif volatility < 0.008:  # <0.8% daily volatility
                                regime_votes['RANGING'] += 1.0
                                analysis_sources.append(f'YF_LowVol({volatility*100:.1f}%)')

                            # Trend detection
                            if abs(trend) > 0.03:  # >3% move over period
                                regime_votes['TRENDING'] += 1.5
                                analysis_sources.append(f'YF_Trend({trend*100:+.1f}%)')
                            elif abs(trend) < 0.01:  # <1% move
                                regime_votes['RANGING'] += 1.0
                                analysis_sources.append(f'YF_Sideways({trend*100:+.1f}%)')

                            confidence_scores.append(0.7)
                except Exception as e:
                    self.logger.debug(f"Yahoo Finance regime analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🔮 MARKET ORACLE - AI Prediction for Regime
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_oracle'):
                try:
                    oracle = self.systems['market_oracle']
                    if hasattr(oracle, 'generate_prediction'):
                        prediction = await oracle.generate_prediction('SPY', '24h')
                        if prediction:
                            predicted_change = abs(prediction.predicted_change_percent)
                            oracle_confidence = prediction.confidence

                            # High predicted change = trending
                            if predicted_change > 2.0:
                                regime_votes['TRENDING'] += oracle_confidence * 1.2
                                analysis_sources.append(f'Oracle({prediction.predicted_change_percent:+.1f}%)')
                            # Low predicted change = ranging
                            elif predicted_change < 0.5:
                                regime_votes['RANGING'] += oracle_confidence * 0.8
                                analysis_sources.append('Oracle(sideways)')

                            confidence_scores.append(oracle_confidence)
                except Exception as e:
                    self.logger.debug(f"Oracle regime analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # ⚛️ QUANTUM ENGINE - Market State Detection
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('quantum_trading'):
                try:
                    quantum = self.systems['quantum_trading']
                    if hasattr(quantum, 'detect_arbitrage_opportunities'):
                        # Many arbitrage opportunities suggest volatile/ranging market
                        market_data = await self.fetch_market_data('SPY')
                        if market_data:
                            arb_result = await quantum.detect_arbitrage_opportunities(market_data)
                            if arb_result and arb_result.get('opportunities'):
                                # More opportunities = more volatility
                                opp_count = len(arb_result.get('opportunities', []))
                                if opp_count > 3:
                                    regime_votes['VOLATILE'] += 0.8
                                    analysis_sources.append(f'Quantum({opp_count} opps)')
                                    confidence_scores.append(arb_result.get('confidence', 0.6))
                except Exception as e:
                    self.logger.debug(f"Quantum regime analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🌍 REAL WORLD DATA - News & Sentiment Impact
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('real_world_data'):
                try:
                    orchestrator = self.systems['real_world_data']
                    if hasattr(orchestrator, 'get_comprehensive_intelligence'):
                        intel = await orchestrator.get_comprehensive_intelligence('SPY')
                        if intel:
                            sentiment = intel.get('overall_sentiment', 0)
                            # Extreme sentiment suggests trending
                            if abs(sentiment) > 0.5:
                                regime_votes['TRENDING'] += abs(sentiment) * 1.0
                                analysis_sources.append(f'DataIntel(sentiment={sentiment:+.2f})')
                            confidence_scores.append(abs(sentiment) * 0.8)
                except Exception as e:
                    self.logger.debug(f"Data intelligence regime analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🌐 CROSS-ASSET INTELLIGENCE (VIX, Gold, Bonds)
            # Proven in 50-year benchmark: +2.4% CAGR contribution
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.cross_asset_intelligence import get_cross_asset_intelligence
                xai = get_cross_asset_intelligence()
                _preliminary_regime = max(regime_votes, key=regime_votes.get)
                xai_result = xai.get_regime_adjustment(_preliminary_regime)
                xai_score = xai_result['composite_score']
                xai_vote = xai_result['regime_vote']
                xai_label = xai_result['regime_label']

                # Apply cross-asset regime vote
                if xai_vote > 0:
                    regime_votes['TRENDING'] += xai_vote
                elif xai_vote < 0:
                    regime_votes['VOLATILE'] += abs(xai_vote)

                confidence_scores.append(min(abs(xai_score), 1.0) * 0.8)
                analysis_sources.append(f'CrossAsset({xai_label},{xai_score:+.2f})')
                self.logger.info(f"   🌐 {xai.format_status()}")
            except Exception as e:
                self.logger.debug(f"Cross-asset intelligence failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📊 SYNTHESIZE FINAL REGIME
            # ═══════════════════════════════════════════════════════════════
            # Add base votes for NORMAL to prevent empty result
            regime_votes['NORMAL'] += 0.5

            # Get winning regime
            detected_regime = max(regime_votes, key=regime_votes.get)
            total_votes = sum(regime_votes.values())
            regime_confidence = regime_votes[detected_regime] / total_votes if total_votes > 0 else 0.5

            # Calculate average confidence
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

            self.logger.info(f"🎯 REGIME DETECTED: {detected_regime} (confidence: {regime_confidence:.1%})")
            self.logger.info(f"   Votes: VOLATILE={regime_votes['VOLATILE']:.1f}, TRENDING={regime_votes['TRENDING']:.1f}, "
                           f"RANGING={regime_votes['RANGING']:.1f}, NORMAL={regime_votes['NORMAL']:.1f}")
            self.logger.info(f"   Sources: {', '.join(analysis_sources) if analysis_sources else 'None'}")

            return detected_regime

        except Exception as e:
            self.logger.error(f"Regime detection failed: {e}")
            return "NORMAL"  # Safe fallback

    async def _get_ai_position_size(self, symbol: str, signal: Dict[str, Any], equity: float) -> float:
        """
        🎯 60/40 LEGACY-KELLY BLEND POSITION SIZING
        
        Benchmark-recommended blend of two proven approaches:
        - 60% Legacy heuristic (6 adjustment factors, proven in real data)
        - 40% Kelly Criterion (mathematically optimal, volatility-scaled)
        - VIX sourced from cross-asset intelligence → yfinance fallback
        
        Results (50-year benchmark on real S&P 500 data):
        - Legacy: 41.05% CAGR, Sharpe 3.275, Max DD -6.36%
        - Kelly:  41.66% CAGR, Sharpe 3.236, Max DD -7.08%
        - Shadow test: Kelly won 6-0 on live recent data
        - Blend captures strengths of both approaches
        """
        try:
            # ═══════════════════════════════════════════════════════════════
            # KELLY CRITERION (mathematically optimal) — store for blending
            # ═══════════════════════════════════════════════════════════════
            kelly_size_pct = None
            vix = 20.0  # Default
            if ADVANCED_RISK_MANAGER_AVAILABLE:
                try:
                    risk_manager = get_risk_manager()
                    
                    # Get VIX for volatility scaling (try multiple sources)
                    try:
                        from core.cross_asset_intelligence import get_cross_asset_intelligence
                        xai = get_cross_asset_intelligence()
                        vix_data = xai._get_data('vix')
                        if vix_data:
                            vix = vix_data.get('close', 20.0)
                    except Exception:
                        pass
                    if vix == 20.0:
                        try:
                            import yfinance as yf
                            vix_ticker = yf.Ticker("^VIX")
                            vix_hist = vix_ticker.history(period="1d")
                            if not vix_hist.empty:
                                vix = float(vix_hist['Close'].iloc[-1])
                                self.logger.debug(f"VIX from yfinance: {vix:.2f}")
                        except Exception:
                            pass
                    
                    # Get historical performance for Kelly calculation
                    historical_perf = None
                    try:
                        historical_perf = risk_manager.get_performance_stats()
                    except Exception:
                        pass
                    
                    # Calculate optimal position using Kelly Criterion
                    confidence = signal.get('confidence', 0.5)
                    position_dollars, metrics = risk_manager.calculate_optimal_position(
                        symbol=symbol,
                        confidence=confidence,
                        capital=equity,
                        vix=vix,
                        historical_performance=historical_perf
                    )
                    
                    # Convert to percentage (store for blending, don't return)
                    if position_dollars > 0 and equity > 0:
                        kelly_size_pct = position_dollars / equity
                        self.logger.debug(f"Kelly raw size for {symbol}: {kelly_size_pct*100:.2f}%")
                    
                except Exception as e:
                    self.logger.warning(f"Kelly Criterion failed, using legacy only: {e}")
            
            # ═══════════════════════════════════════════════════════════════
            # LEGACY HEURISTIC SIZING (always computed for 60/40 blend)
            # ═══════════════════════════════════════════════════════════════
            base_size = self.risk_limits['position_size_pct']  # 15% base
            size_multiplier = 1.0
            size_adjustments = []

            # ═══════════════════════════════════════════════════════════════
            # 1. CONFIDENCE-BASED SIZING (±50%)
            # ═══════════════════════════════════════════════════════════════
            confidence = signal.get('confidence', 0.5)
            if confidence >= 0.7:
                # High confidence = up to 50% larger position
                confidence_mult = 1.0 + (confidence - 0.5) * 1.0  # 0.7 conf = 1.2x
                size_multiplier *= confidence_mult
                size_adjustments.append(f"Confidence({confidence:.0%})={confidence_mult:.2f}x")
            elif confidence < 0.4:
                # Low confidence = up to 50% smaller position
                confidence_mult = 0.5 + confidence  # 0.3 conf = 0.8x
                size_multiplier *= confidence_mult
                size_adjustments.append(f"Confidence({confidence:.0%})={confidence_mult:.2f}x")

            # ═══════════════════════════════════════════════════════════════
            # 2. REGIME-BASED SIZING (benchmark-proven allocation model)
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.regime_exposure_manager import get_regime_exposure_manager
                rem = get_regime_exposure_manager()
                alloc_state = rem.get_current_state()
                regime_mult = alloc_state.size_scale
                size_multiplier *= regime_mult
                size_adjustments.append(f"RegimeAlloc({alloc_state.regime},{alloc_state.target_allocation:.0%})={regime_mult:.2f}x")
            except Exception:
                # Fallback to simple regime multipliers
                regime_multipliers = {
                    'VOLATILE': 0.6,
                    'TRENDING': 1.2,
                    'RANGING': 0.8,
                    'NORMAL': 1.0
                }
                regime_mult = regime_multipliers.get(self.market_regime, 1.0)
                size_multiplier *= regime_mult
                size_adjustments.append(f"Regime({self.market_regime})={regime_mult:.2f}x")

            # ═══════════════════════════════════════════════════════════════
            # 3. SYMBOL VOLATILITY (from Yahoo Finance)
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('yahoo_finance'):
                try:
                    yf = self.systems['yahoo_finance']
                    if hasattr(yf, 'get_historical_data_async'):
                        hist = await yf.get_historical_data_async(symbol, timeframe='1Day', limit=10)
                    elif hasattr(yf, 'get_historical_data'):
                        hist = yf.get_historical_data(symbol, timeframe='1Day', limit=10)
                    else:
                        hist = None

                    if hist and len(hist) >= 5:
                        import numpy as np
                        closes = [bar.get('close', bar.get('Close', 0)) for bar in hist if bar]
                        if len(closes) >= 5:
                            returns = np.diff(closes) / closes[:-1]
                            symbol_vol = np.std(returns)

                            # High volatility symbol = smaller position
                            if symbol_vol > 0.03:  # >3% daily volatility
                                vol_mult = 0.7
                                size_adjustments.append(f"SymbolVol({symbol_vol*100:.1f}%)=0.70x")
                            elif symbol_vol > 0.02:
                                vol_mult = 0.85
                                size_adjustments.append(f"SymbolVol({symbol_vol*100:.1f}%)=0.85x")
                            else:
                                vol_mult = 1.0
                            size_multiplier *= vol_mult
                except Exception as e:
                    self.logger.debug(f"Symbol volatility check failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 4. PORTFOLIO HEAT (current exposure across BOTH brokers)
            # ═══════════════════════════════════════════════════════════════
            try:
                num_positions = 0
                alpaca_broker = self.systems.get('alpaca_broker')
                ib_broker = self.systems.get('ib_broker')
                if alpaca_broker:
                    try:
                        alpaca_positions = await alpaca_broker.get_positions()
                        if alpaca_positions:
                            num_positions += len(alpaca_positions)
                    except Exception:
                        pass
                if ib_broker:
                    try:
                        ib_positions = await ib_broker.get_positions()
                        if ib_positions:
                            num_positions += len(ib_positions)
                    except Exception:
                        pass

                if num_positions > 0:
                    max_positions = self.risk_limits.get('max_positions', 15)

                    # More positions = smaller new positions
                    if num_positions >= max_positions * 0.8:  # 80%+ capacity
                        heat_mult = 0.5
                        size_adjustments.append(f"PortfolioHeat({num_positions}/{max_positions})=0.50x")
                    elif num_positions >= max_positions * 0.5:  # 50%+ capacity
                        heat_mult = 0.8
                        size_adjustments.append(f"PortfolioHeat({num_positions}/{max_positions})=0.80x")
                    else:
                        heat_mult = 1.0
                    size_multiplier *= heat_mult
            except Exception as e:
                self.logger.debug(f"Portfolio heat check failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 5. RECENT PERFORMANCE (from learning database)
            # ═══════════════════════════════════════════════════════════════
            try:
                import sqlite3
                db = sqlite3.connect('prometheus_learning.db')
                cursor = db.cursor()
                cursor.execute("""
                    SELECT profit_loss FROM trade_history
                    WHERE timestamp > datetime('now', '-7 days')
                    ORDER BY timestamp DESC LIMIT 10
                """)
                recent_trades = cursor.fetchall()
                db.close()

                if recent_trades:
                    wins = sum(1 for t in recent_trades if t[0] and t[0] > 0)
                    losses = len(recent_trades) - wins
                    win_rate = wins / len(recent_trades) if recent_trades else 0.5

                    # Losing streak = reduce size
                    if win_rate < 0.3:  # <30% win rate
                        perf_mult = 0.6
                        size_adjustments.append(f"RecentPerf({win_rate:.0%}WR)=0.60x")
                    elif win_rate < 0.4:
                        perf_mult = 0.8
                        size_adjustments.append(f"RecentPerf({win_rate:.0%}WR)=0.80x")
                    elif win_rate > 0.6:  # >60% win rate = slightly larger
                        perf_mult = 1.1
                        size_adjustments.append(f"RecentPerf({win_rate:.0%}WR)=1.10x")
                    else:
                        perf_mult = 1.0
                    size_multiplier *= perf_mult
            except Exception as e:
                self.logger.debug(f"Recent performance check failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 6. CROSS-ASSET INTELLIGENCE (VIX, Gold, Bonds overlay)
            # Proven in 50-year benchmark: boosts in risk-on, cuts in risk-off
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.cross_asset_intelligence import get_cross_asset_intelligence
                xai = get_cross_asset_intelligence()
                xai_adj = xai.get_regime_adjustment(self.market_regime or 'NORMAL')
                xai_scale = xai_adj['position_scale']
                size_multiplier *= xai_scale
                if abs(xai_scale - 1.0) > 0.01:
                    size_adjustments.append(f"CrossAsset({xai_adj['regime_label']})={xai_scale:.2f}x")
            except Exception as e:
                self.logger.debug(f"Cross-asset position sizing failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # CALCULATE FINAL POSITION SIZE (60/40 Legacy-Kelly Blend)
            # ═══════════════════════════════════════════════════════════════
            # Apply multiplier with safety bounds
            size_multiplier = max(0.25, min(2.0, size_multiplier))  # 25% to 200% of base

            legacy_size_pct = base_size * size_multiplier
            # Cap at max position size (10%)
            legacy_size_pct = min(legacy_size_pct, 0.10)

            # Blend Kelly + Legacy — regime-adaptive ratio
            if kelly_size_pct is not None:
                regime = getattr(self, 'market_regime', 'NORMAL') or 'NORMAL'
                regime = regime.upper()
                if regime in ('VOLATILE', 'BEAR'):
                    legacy_w, kelly_w = 0.40, 0.60  # Kelly stronger in bear/volatile
                elif regime in ('TRENDING', 'BULL'):
                    legacy_w, kelly_w = 0.70, 0.30  # Legacy stronger in trending/bull
                else:
                    legacy_w, kelly_w = 0.60, 0.40  # Default balanced blend
                final_size_pct = legacy_w * legacy_size_pct + kelly_w * kelly_size_pct
                final_size_pct = min(final_size_pct, 0.10)
                blend_label = f"BLEND({legacy_w:.0%} legacy {legacy_size_pct*100:.2f}% + {kelly_w:.0%} kelly {kelly_size_pct*100:.2f}% | regime={regime})"
            else:
                final_size_pct = legacy_size_pct
                blend_label = "LEGACY-ONLY (Kelly unavailable)"

            self.logger.info(f"🎯 AI POSITION SIZE for {symbol}: {final_size_pct*100:.2f}%")
            self.logger.info(f"   {blend_label}")
            self.logger.info(f"   Adjustments: {', '.join(size_adjustments) if size_adjustments else 'None'}")

            return final_size_pct

        except Exception as e:
            self.logger.error(f"AI position sizing failed: {e}")
            return self.risk_limits['position_size_pct']  # Safe fallback

    async def _apply_adaptations(self):
        """Apply trading style and regime adaptations (AI-enhanced)"""
        # First detect market regime using AI
        self.market_regime = await self.detect_market_regime()

        # Style multipliers (kept for compatibility, but AI sizing is primary)
        style_multipliers = {
            "AGGRESSIVE": 1.5,
            "BALANCED": 1.0,
            "CONSERVATIVE": 0.5
        }

        base_position_size = self.risk_limits['position_size_pct']
        adjusted_size = base_position_size * style_multipliers[self.trading_style]

        # Adjust stop losses based on AI-detected market regime
        regime_stop_adjustments = {
            "NORMAL": 1.0,
            "VOLATILE": 1.5,   # Wider stops in volatile markets
            "TRENDING": 0.8,   # Tighter stops in trending markets
            "RANGING": 1.2     # Wider stops in ranging markets
        }

        base_stop_loss = self.risk_limits['stop_loss_pct']
        adjusted_stop = base_stop_loss * regime_stop_adjustments[self.market_regime]

        # Store adjusted values for use
        self.adjusted_position_size = adjusted_size
        self.adjusted_stop_loss = adjusted_stop

        self.logger.info(f"📊 Adaptations Applied:")
        self.logger.info(f"   Style: {self.trading_style} | Regime: {self.market_regime}")
        self.logger.info(f"   Position Size: {adjusted_size*100:.2f}%")
        self.logger.info(f"   Stop Loss: {adjusted_stop*100:.2f}%")

    async def _get_ai_enhanced_watchlist(self) -> Dict[str, List[str]]:
        """
        🧠 AI-ENHANCED WATCHLIST GENERATION
        Combines base high-liquidity symbols with AI-discovered opportunities.

        Sources:
        - Opportunity Scanner: Breakouts, momentum, volume spikes
        - Gap Detector: Price gaps > 2%
        - Market Researcher: Regime-appropriate symbols
        - Learning Database: Remove underperformers
        """
        try:
            # ═══════════════════════════════════════════════════════════════
            # BASE WATCHLIST - High liquidity symbols (always included)
            # ═══════════════════════════════════════════════════════════════
            base_watchlist = {
                'stocks': [
                    # Tech Giants (high liquidity, extended hours)
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
                    # ETFs (high liquidity, low spreads)
                    'SPY', 'QQQ', 'IWM', 'DIA',
                    # Momentum Stocks
                    'AMD', 'NFLX', 'DIS', 'BA', 'JPM',
                ],
                'crypto': [
                    # Alpaca-supported crypto pairs
                    'BTC/USD', 'ETH/USD', 'SOL/USD', 'AVAX/USD', 'LINK/USD', 'UNI/USD',
                    'AAVE/USD', 'SUSHI/USD', 'CRV/USD', 'DOGE/USD', 'SHIB/USD', 'PEPE/USD',
                    'USDC/USD', 'USDT/USD',
                ],
                'forex': [
                    # Major pairs
                    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
                    # Cross pairs
                    'EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'GBPCHF',
                    'AUDJPY', 'CADJPY', 'EURAUD', 'EURCAD', 'GBPAUD',
                    'GBPCAD', 'AUDCAD', 'AUDCHF', 'CADCHF', 'NZDJPY',
                ]
            }

            ai_additions = {'stocks': [], 'crypto': [], 'forex': []}
            ai_removals = []
            ai_contributors = []

            # ═══════════════════════════════════════════════════════════════
            # 1. OPPORTUNITY SCANNER - Find breakouts, momentum, volume
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('opportunity_scanner'):
                try:
                    scanner = self.systems['opportunity_scanner']
                    if hasattr(scanner, 'scan_all_opportunities'):
                        opportunities = await scanner.scan_all_opportunities()
                    elif hasattr(scanner, 'find_opportunities'):
                        opportunities = await scanner.find_opportunities()
                    else:
                        opportunities = None

                    if opportunities:
                        ai_contributors.append('OpportunityScanner')
                        for opp in opportunities[:10]:  # Top 10 opportunities
                            symbol = opp.get('symbol', opp.get('ticker', ''))
                            if symbol and symbol not in base_watchlist['stocks']:
                                # Categorize by type
                                if '/' in symbol:
                                    if 'USD' in symbol:
                                        ai_additions['crypto'].append(symbol)
                                else:
                                    ai_additions['stocks'].append(symbol)
                        self.logger.info(f"🔍 OpportunityScanner found {len(opportunities)} opportunities")
                except Exception as e:
                    self.logger.debug(f"OpportunityScanner failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 2. GAP DETECTOR - Find price gaps > 2%
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('gap_detector'):
                try:
                    detector = self.systems['gap_detector']
                    if hasattr(detector, 'scan_for_gaps'):
                        gaps = await detector.scan_for_gaps(min_gap_pct=2.0)
                    elif hasattr(detector, 'detect_gaps'):
                        gaps = await detector.detect_gaps(min_gap_pct=2.0)
                    elif hasattr(detector, 'find_gaps'):
                        gaps = detector.find_gaps(min_gap_pct=2.0)
                    else:
                        gaps = None

                    if gaps:
                        ai_contributors.append('GapDetector')
                        for gap in gaps[:5]:  # Top 5 gaps
                            symbol = gap.get('symbol', gap.get('ticker', ''))
                            gap_pct = gap.get('gap_pct', gap.get('gap', 0))
                            if symbol and abs(gap_pct) >= 2.0:
                                if symbol not in base_watchlist['stocks']:
                                    ai_additions['stocks'].append(symbol)
                        self.logger.info(f"📊 GapDetector found {len(gaps)} gaps > 2%")
                except Exception as e:
                    self.logger.debug(f"GapDetector failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 3. MARKET RESEARCHER - Regime-appropriate symbols
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_researcher'):
                try:
                    researcher = self.systems['market_researcher']
                    regime = self.market_regime

                    if hasattr(researcher, 'get_regime_symbols'):
                        regime_symbols = await researcher.get_regime_symbols(regime)
                    elif hasattr(researcher, 'generate_market_intelligence'):
                        intel = await researcher.generate_market_intelligence()
                        regime_symbols = intel.get('recommended_symbols', []) if intel else []
                    elif hasattr(researcher, 'get_top_movers'):
                        regime_symbols = await researcher.get_top_movers(limit=10)
                    else:
                        regime_symbols = None

                    if regime_symbols:
                        ai_contributors.append('MarketResearcher')
                        for sym in regime_symbols[:10]:
                            symbol = sym if isinstance(sym, str) else sym.get('symbol', '')
                            if symbol and symbol not in base_watchlist['stocks']:
                                ai_additions['stocks'].append(symbol)
                        self.logger.info(f"📈 MarketResearcher suggests {len(regime_symbols)} symbols for {regime}")
                except Exception as e:
                    self.logger.debug(f"MarketResearcher failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 4. LEARNING DATABASE - Remove underperformers
            # ═══════════════════════════════════════════════════════════════
            try:
                import sqlite3
                db = sqlite3.connect('prometheus_learning.db')
                cursor = db.cursor()

                # Find symbols with >=10 CLOSED trades and <25% win rate in last 30 days
                # FIX: Was removing AAPL, NVDA, META etc. after only 3 trades (way too aggressive)
                # Now requires 10+ completed trades with actual P/L data before judging
                cursor.execute("""
                    SELECT symbol,
                           COUNT(*) as total_trades,
                           SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins
                    FROM trade_history
                    WHERE timestamp > datetime('now', '-30 days')
                      AND profit_loss != 0
                      AND exit_price IS NOT NULL
                    GROUP BY symbol
                    HAVING total_trades >= 10 AND (wins * 1.0 / total_trades) < 0.25
                """)
                underperformers = cursor.fetchall()
                db.close()

                if underperformers:
                    ai_contributors.append('LearningDB')
                    for row in underperformers:
                        symbol = row[0]
                        total = row[1]
                        wins = row[2]
                        win_rate = wins / total if total > 0 else 0
                        ai_removals.append(symbol)
                        self.logger.warning(f"⚠️ Removing underperformer: {symbol} ({win_rate:.0%} win rate from {total} trades)")
            except Exception as e:
                self.logger.debug(f"Learning DB check failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # BUILD FINAL WATCHLIST
            # ═══════════════════════════════════════════════════════════════
            enhanced_watchlist = {
                'stocks': list(set(base_watchlist['stocks'] + ai_additions['stocks'])),
                'crypto': list(set(base_watchlist['crypto'] + ai_additions['crypto'])),
                'forex': list(set(base_watchlist['forex'] + ai_additions['forex']))
            }

            # Remove underperformers
            for symbol in ai_removals:
                for category in enhanced_watchlist:
                    if symbol in enhanced_watchlist[category]:
                        enhanced_watchlist[category].remove(symbol)

            # Calculate stats
            base_count = sum(len(v) for v in base_watchlist.values())
            ai_added = sum(len(v) for v in ai_additions.values())
            final_count = sum(len(v) for v in enhanced_watchlist.values())

            self.logger.info(f"🧠 AI WATCHLIST ENHANCEMENT:")
            self.logger.info(f"   Base: {base_count} | AI Added: {ai_added} | Removed: {len(ai_removals)} | Final: {final_count}")
            self.logger.info(f"   Contributors: {', '.join(ai_contributors) if ai_contributors else 'Base only'}")
            if ai_additions['stocks']:
                self.logger.info(f"   📈 AI-added stocks: {', '.join(ai_additions['stocks'][:5])}")

            return enhanced_watchlist

        except Exception as e:
            self.logger.error(f"AI watchlist enhancement failed: {e}")
            # Fallback to base watchlist
            return {
                'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'SPY', 'QQQ', 'AMD'],
                'crypto': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD'],
                'forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
            }

    async def _get_combined_capital(self) -> Dict[str, Any]:
        """
        💰 DUAL-BROKER CAPITAL AGGREGATION
        Fetches equity, cash, and buying power from BOTH Alpaca and IB,
        then returns a combined view so position sizing uses total capital.
        """
        combined = {
            'total_equity': 0.0,
            'total_cash': 0.0,
            'total_buying_power': 0.0,
            'alpaca_equity': 0.0,
            'alpaca_cash': 0.0,
            'alpaca_buying_power': 0.0,
            'ib_equity': 0.0,
            'ib_cash': 0.0,
            'ib_buying_power': 0.0,
            'alpaca_connected': False,
            'ib_connected': False,
            'brokers_active': 0,
        }

        # Alpaca
        alpaca_broker = self.systems.get('alpaca_broker')
        if alpaca_broker and alpaca_broker.connected:
            try:
                acct = await alpaca_broker.get_account()
                combined['alpaca_equity'] = float(acct.equity)
                combined['alpaca_cash'] = float(acct.cash)
                combined['alpaca_buying_power'] = float(acct.buying_power)
                combined['alpaca_connected'] = True
                combined['brokers_active'] += 1
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get Alpaca account: {e}")

        # Interactive Brokers
        ib_broker = self.systems.get('ib_broker')
        if ib_broker and hasattr(ib_broker, 'connected') and ib_broker.connected:
            try:
                acct = await ib_broker.get_account()
                combined['ib_equity'] = float(acct.equity)
                combined['ib_cash'] = float(acct.cash)
                combined['ib_buying_power'] = float(acct.buying_power)
                combined['ib_connected'] = True
                combined['brokers_active'] += 1
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get IB account: {e}")

        # Totals
        combined['total_equity'] = combined['alpaca_equity'] + combined['ib_equity']
        combined['total_cash'] = combined['alpaca_cash'] + combined['ib_cash']
        combined['total_buying_power'] = combined['alpaca_buying_power'] + combined['ib_buying_power']

        self.logger.info(f"💰 Combined Capital: ${combined['total_equity']:.2f} equity "
                        f"(Alpaca=${combined['alpaca_equity']:.2f}, IB=${combined['ib_equity']:.2f}) | "
                        f"Idle Cash: ${combined['total_cash']:.2f}")

        return combined

    async def _sync_positions_from_ib(self):
        """
        🔄 POSITION SYNC: Sync internal database with IB's actual positions
        Mirrors _sync_positions_from_alpaca but for Interactive Brokers.
        """
        import sqlite3

        ib_broker = self.systems.get('ib_broker')
        if not ib_broker or not hasattr(ib_broker, 'connected') or not ib_broker.connected:
            return False

        try:
            positions = await ib_broker.get_positions()
            if positions is None:
                return False

            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS open_positions (
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL,
                    unrealized_pl REAL,
                    broker TEXT DEFAULT 'Alpaca',
                    opened_at TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (symbol, broker)
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM open_positions WHERE broker = 'IB'")
            old_count = cursor.fetchone()[0]

            cursor.execute("DELETE FROM open_positions WHERE broker = 'IB'")

            from datetime import datetime
            now = datetime.now().isoformat()

            for pos in positions:
                symbol = pos.symbol
                qty = abs(float(pos.quantity))
                entry_price = float(pos.avg_price)
                current_price = float(pos.market_value / qty) if qty > 0 else entry_price
                unrealized_pl = float(pos.unrealized_pnl)
                side = 'LONG' if float(pos.quantity) > 0 else 'SHORT'

                cursor.execute("""
                    INSERT INTO open_positions
                    (symbol, side, quantity, entry_price, current_price, unrealized_pl, broker, opened_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'IB', ?, ?)
                """, (symbol, side, qty, entry_price, current_price, unrealized_pl, now, now))

            db.commit()
            db.close()

            if old_count != len(positions):
                self.logger.info(f"🔄 IB Position sync: {old_count} → {len(positions)} positions")

            return True

        except Exception as e:
            self.logger.error(f"❌ IB Position sync failed: {e}")
            return False

    async def _check_ib_position_exits(self):
        """
        🎯 IB POSITION MONITOR: Check IB positions for exit conditions
        Uses the same logic as _check_position_exits but routes sells through IB broker.
        IB uses submit_order() for sells (no .sell() convenience method).
        """
        ib_broker = self.systems.get('ib_broker')
        if not ib_broker or not hasattr(ib_broker, 'connected') or not ib_broker.connected:
            return

        try:
            positions = await ib_broker.get_positions()
            if not positions:
                self.logger.info("📊 No IB positions to monitor")
                return

            self.logger.info(f"📊 🎯 IB POSITION MONITOR: Checking {len(positions)} IB position(s) for exits...")

            catastrophic_stop_loss_pct = 0.06
            max_take_profit_pct = 0.10
            stop_loss_pct = self.risk_limits.get('stop_loss_pct', 0.03)

            for pos in positions:
                symbol = pos.symbol
                qty = abs(float(pos.quantity))
                avg_price = float(pos.avg_price)
                unrealized_pnl = float(pos.unrealized_pnl)
                pnl_pct = float(pos.unrealized_pnl_percent) if hasattr(pos, 'unrealized_pnl_percent') and pos.unrealized_pnl_percent else (
                    unrealized_pnl / (avg_price * qty) if avg_price * qty > 0 else 0
                )
                current_price = avg_price * (1 + pnl_pct) if avg_price > 0 else 0

                self.logger.info(f"  [IB] {symbol}: qty={qty:.2f}, avg=${avg_price:.2f}, P/L=${unrealized_pnl:.2f} ({pnl_pct*100:.2f}%)")

                # Track highs and entry times
                ib_key = f"IB_{symbol}"
                if ib_key not in self.position_highs:
                    self.position_highs[ib_key] = current_price
                elif current_price > self.position_highs[ib_key]:
                    self.position_highs[ib_key] = current_price
                high_price = self.position_highs[ib_key]

                if ib_key not in self.position_entry_times:
                    from datetime import datetime as dt
                    self.position_entry_times[ib_key] = dt.now()

                drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                from datetime import datetime as dt
                entry_time = self.position_entry_times.get(ib_key, dt.now())
                days_held = (dt.now() - entry_time).days

                should_sell = False
                sell_reason = None
                sell_qty = qty

                # Safety backstops
                if pnl_pct <= -catastrophic_stop_loss_pct:
                    should_sell = True
                    sell_reason = f"🛑 IB CATASTROPHIC_STOP ({pnl_pct*100:.2f}%)"
                elif pnl_pct >= max_take_profit_pct:
                    should_sell = True
                    sell_reason = f"💰 IB BIG_WIN_LOCK ({pnl_pct*100:.2f}%)"
                # Trailing stop
                elif self.trailing_stop_enabled and pnl_pct >= self.trailing_stop_trigger:
                    if drop_from_high >= self.trailing_stop_distance:
                        should_sell = True
                        sell_reason = f"📈 IB TRAILING_STOP (dropped {drop_from_high*100:.1f}% from high)"
                    elif self.scale_out_enabled:
                        scaled_level = self.scaled_positions.get(ib_key, 0)
                        if pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                            should_sell = True
                            sell_reason = f"📊 IB SCALE_OUT_2 (+{pnl_pct*100:.1f}%)"
                            self.scaled_positions[ib_key] = 2
                        elif pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                            should_sell = True
                            sell_qty = int(qty * 0.5) or 1  # IB needs whole shares
                            self.scaled_positions[ib_key] = 1
                            sell_reason = f"📊 IB SCALE_OUT_1 (+{pnl_pct*100:.1f}%) - selling 50%"
                # Scale-out
                elif self.scale_out_enabled:
                    scaled_level = self.scaled_positions.get(ib_key, 0)
                    if pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                        should_sell = True
                        sell_qty = int(qty * 0.5) or 1
                        self.scaled_positions[ib_key] = 1
                        sell_reason = f"📊 IB SCALE_OUT_1 (+{pnl_pct*100:.1f}%)"
                    elif pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                        should_sell = True
                        sell_reason = f"📊 IB SCALE_OUT_2 (+{pnl_pct*100:.1f}%)"
                        self.scaled_positions[ib_key] = 2
                # Time exit
                elif self.time_exit_enabled and days_held >= self.max_hold_days_stock and pnl_pct < self.scale_out_first_pct:
                    should_sell = True
                    sell_reason = f"⏰ IB TIME_EXIT ({days_held}d held)"
                # Stop loss
                elif pnl_pct <= -stop_loss_pct:
                    should_sell = True
                    sell_reason = f"🛑 IB STOP_LOSS ({pnl_pct*100:.2f}%)"

                if should_sell:
                    self.logger.info(f"🚨 [IB] EXIT: {symbol} - {sell_reason}")
                    try:
                        # IB uses submit_order for sells
                        from brokers.broker_interface import Order, OrderSide, OrderType
                        sell_order = Order(
                            symbol=symbol,
                            quantity=sell_qty,
                            side=OrderSide.SELL,
                            order_type=OrderType.MARKET,
                            time_in_force='day'
                        )
                        result = await ib_broker.submit_order(sell_order)
                        if result:
                            profit_emoji = "💰" if pnl_pct > 0 else "🛑"
                            self.logger.info(f"{profit_emoji} ✅ [IB] SOLD {symbol}: {sell_qty} shares - {sell_reason}")
                            from datetime import datetime as dt
                            self.trades_this_hour.append(dt.now())
                            await self._record_learning_outcome(
                                symbol=symbol,
                                entry_price=avg_price,
                                exit_price=current_price,
                                quantity=sell_qty,
                                profit_loss=unrealized_pnl * (sell_qty / qty),
                                profit_pct=pnl_pct,
                                exit_reason=sell_reason,
                                broker='IB'
                            )
                            if sell_qty >= qty * 0.99:
                                self._cleanup_position_tracking(ib_key)
                        else:
                            self.logger.error(f"❌ [IB] Failed to sell {symbol}")
                    except Exception as e:
                        self.logger.error(f"❌ [IB] Exception selling {symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error in IB position monitoring: {e}")

    async def _sync_positions_from_alpaca(self):
        """
        🔄 POSITION SYNC: Sync internal database with Alpaca's actual positions
        This ensures the trading system always knows what positions it actually holds.
        Must be called before any trading decisions that rely on position state.
        """
        import sqlite3

        alpaca_broker = self.systems.get('alpaca_broker')
        if not alpaca_broker or not alpaca_broker.connected:
            self.logger.warning("⚠️ Position sync: Alpaca broker not connected")
            return False

        try:
            # Get ACTUAL Alpaca positions
            positions = await alpaca_broker.get_positions()

            if positions is None:
                self.logger.warning("⚠️ Position sync: Could not get Alpaca positions")
                return False

            # Connect to internal database
            db = sqlite3.connect('prometheus_learning.db')
            cursor = db.cursor()

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS open_positions (
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL,
                    unrealized_pl REAL,
                    broker TEXT DEFAULT 'Alpaca',
                    opened_at TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (symbol, broker)
                )
            """)

            # Get current internal position count
            cursor.execute("SELECT COUNT(*) FROM open_positions WHERE broker = 'Alpaca'")
            old_count = cursor.fetchone()[0]

            # Clear and resync all Alpaca positions
            cursor.execute("DELETE FROM open_positions WHERE broker = 'Alpaca'")

            from datetime import datetime
            now = datetime.now().isoformat()

            for pos in positions:
                symbol = pos.symbol
                qty = abs(float(pos.quantity))
                entry_price = float(pos.avg_price)
                current_price = float(pos.market_value / qty) if qty > 0 else entry_price
                unrealized_pl = float(pos.unrealized_pnl)
                side = 'LONG' if float(pos.quantity) > 0 else 'SHORT'

                cursor.execute("""
                    INSERT INTO open_positions
                    (symbol, side, quantity, entry_price, current_price, unrealized_pl, broker, opened_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'Alpaca', ?, ?)
                """, (symbol, side, qty, entry_price, current_price, unrealized_pl, now, now))

            db.commit()
            db.close()

            if old_count != len(positions):
                self.logger.info(f"🔄 Position sync: {old_count} → {len(positions)} positions (synced from Alpaca)")

            return True

        except Exception as e:
            self.logger.error(f"❌ Position sync failed: {e}")
            return False

    async def _get_ai_exit_decision(self, symbol: str, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 AI-DRIVEN EXIT DECISION ENGINE
        Consults ALL AI systems to make intelligent hold/sell decisions based on:
        - Market sentiment & news
        - Price momentum & technical indicators
        - Market regime (bull/bear/sideways)
        - Volume analysis
        - AI system consensus

        Returns: {'action': 'HOLD'|'SELL', 'confidence': float, 'reasoning': str, 'ai_contributors': list}
        """
        try:
            pnl_pct = position_data.get('pnl_pct', 0)
            entry_price = position_data.get('avg_price', 0)
            current_price = position_data.get('current_price', entry_price * (1 + pnl_pct))

            # Track AI votes and contributions
            exit_votes = {'HOLD': 0, 'SELL': 0}
            confidence_scores = []
            reasoning_parts = []
            ai_contributors = []

            # Get fresh market data for the position
            market_data = await self.fetch_market_data(symbol)
            if not market_data:
                market_data = {'price': current_price, 'volume': 0, 'change_percent': pnl_pct * 100}

            # ═══════════════════════════════════════════════════════════════
            # 📊 MOMENTUM ANALYSIS - Is the position still trending in our favor?
            # ═══════════════════════════════════════════════════════════════
            momentum = market_data.get('change_percent', 0)
            if pnl_pct > 0:  # We're profitable
                if momentum > 0.3:  # Still trending up
                    exit_votes['HOLD'] += 0.8
                    reasoning_parts.append(f"Momentum: +{momentum:.2f}% (trending up, HOLD)")
                elif momentum < -0.5:  # Reversing down
                    exit_votes['SELL'] += 0.7
                    reasoning_parts.append(f"Momentum: {momentum:.2f}% (reversing, SELL)")
                else:  # Neutral momentum
                    exit_votes['HOLD'] += 0.3
                    reasoning_parts.append(f"Momentum: {momentum:.2f}% (neutral)")
            else:  # We're losing
                if momentum > 0.5:  # Recovering
                    exit_votes['HOLD'] += 0.6
                    reasoning_parts.append(f"Momentum: +{momentum:.2f}% (recovering, HOLD)")
                elif momentum < -0.3:  # Getting worse
                    exit_votes['SELL'] += 0.8
                    reasoning_parts.append(f"Momentum: {momentum:.2f}% (declining, SELL)")
            ai_contributors.append('Momentum')

            # ═══════════════════════════════════════════════════════════════
            # 🔮 MARKET ORACLE - What does the AI predict for this symbol?
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_oracle'):
                try:
                    oracle = self.systems['market_oracle']
                    if hasattr(oracle, 'generate_prediction'):
                        prediction = await oracle.generate_prediction(symbol, '1h')
                        if prediction:
                            predicted_change = prediction.predicted_change_percent
                            oracle_confidence = prediction.confidence

                            if pnl_pct > 0:  # Profitable position
                                if predicted_change > 0.5:  # Price expected to rise more
                                    exit_votes['HOLD'] += oracle_confidence * 1.2
                                    reasoning_parts.append(f"Oracle: +{predicted_change:.1f}% predicted (HOLD for more)")
                                elif predicted_change < -0.5:  # Price expected to drop
                                    exit_votes['SELL'] += oracle_confidence * 1.2
                                    reasoning_parts.append(f"Oracle: {predicted_change:.1f}% predicted (SELL now)")
                            else:  # Losing position
                                if predicted_change > 1.0:  # Strong recovery expected
                                    exit_votes['HOLD'] += oracle_confidence * 0.8
                                    reasoning_parts.append(f"Oracle: +{predicted_change:.1f}% recovery predicted")
                                elif predicted_change < 0:  # More loss expected
                                    exit_votes['SELL'] += oracle_confidence * 1.0
                                    reasoning_parts.append(f"Oracle: {predicted_change:.1f}% - cut losses")

                            confidence_scores.append(oracle_confidence)
                            ai_contributors.append('Oracle')
                except Exception as e:
                    self.logger.debug(f"Oracle exit analysis failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📈 MARKET RESEARCHER - Regime & Sentiment Analysis
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_researcher'):
                try:
                    researcher = self.systems['market_researcher']
                    intel = await researcher.generate_market_intelligence([symbol])
                    if intel:
                        regime = intel.market_regime
                        sentiment = intel.sentiment_score

                        # Regime-based exit logic
                        if regime == 'TRENDING_BULL':
                            if pnl_pct > 0:
                                exit_votes['HOLD'] += 0.9  # Hold winners in bull market
                                reasoning_parts.append(f"Regime: BULL - hold winners")
                            else:
                                exit_votes['HOLD'] += 0.4  # Be patient with losers in bull
                                reasoning_parts.append(f"Regime: BULL - wait for recovery")
                        elif regime == 'TRENDING_BEAR':
                            if pnl_pct > 0:
                                exit_votes['SELL'] += 0.7  # Take profits in bear market
                                reasoning_parts.append(f"Regime: BEAR - lock in profits")
                            else:
                                exit_votes['SELL'] += 0.9  # Cut losses fast in bear
                                reasoning_parts.append(f"Regime: BEAR - cut losses")

                        # Sentiment-based logic
                        if sentiment > 0.3 and pnl_pct > 0:
                            exit_votes['HOLD'] += abs(sentiment) * 0.6
                            reasoning_parts.append(f"Sentiment: +{sentiment:.2f} (bullish)")
                        elif sentiment < -0.3:
                            exit_votes['SELL'] += abs(sentiment) * 0.6
                            reasoning_parts.append(f"Sentiment: {sentiment:.2f} (bearish)")

                        confidence_scores.append(abs(sentiment) if sentiment else 0.5)
                        ai_contributors.append('MarketResearcher')
                except Exception as e:
                    self.logger.debug(f"Market research exit analysis failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🤖 HIERARCHICAL AGENT COORDINATOR - Multi-Agent Consensus
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('agent_coordinator'):
                try:
                    coordinator = self.systems['agent_coordinator']
                    if hasattr(coordinator, 'coordinate_intelligent_trading'):
                        # Ask agents about this specific position
                        position_context = {
                            'symbol': symbol,
                            'position_pnl_pct': pnl_pct,
                            'entry_price': entry_price,
                            'current_price': current_price,
                            'action_type': 'EXIT_DECISION',
                            **market_data
                        }
                        agent_decisions = await coordinator.coordinate_intelligent_trading(position_context)
                        if agent_decisions:
                            for decision in agent_decisions:
                                if decision.symbol == symbol or decision.symbol in ['BTCUSD', symbol.replace('/', '')]:
                                    action = decision.action.upper()
                                    # Translate to exit decision
                                    if action == 'SELL':
                                        exit_votes['SELL'] += decision.confidence * 1.5
                                    elif action == 'BUY' or action == 'HOLD':
                                        exit_votes['HOLD'] += decision.confidence * 1.2
                                    confidence_scores.append(decision.confidence)
                                    ai_contributors.append(f'Agents({len(decision.metadata.get("participating_agents", []))})')
                                    reasoning_parts.append(f"Agents: {action} @ {decision.confidence:.0%}")
                except Exception as e:
                    self.logger.debug(f"Agent exit analysis failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📊 TECHNICAL ANALYSIS - RSI, Volume, Trends
            # ═══════════════════════════════════════════════════════════════
            tech_signal = await self._calculate_technical_indicators(symbol, market_data)
            if tech_signal:
                tech_action = tech_signal.get('action', 'HOLD')
                tech_confidence = tech_signal.get('confidence', 0.5)

                if tech_action == 'SELL':
                    exit_votes['SELL'] += tech_confidence * 0.8
                    reasoning_parts.append(f"Technical: {tech_signal.get('indicators', 'SELL signal')}")
                elif tech_action == 'BUY':
                    exit_votes['HOLD'] += tech_confidence * 0.7  # BUY signal = don't sell
                    reasoning_parts.append(f"Technical: {tech_signal.get('indicators', 'bullish')}")

                confidence_scores.append(tech_confidence)
                ai_contributors.append('Technical')

            # ═══════════════════════════════════════════════════════════════
            # 🎯 PROFIT TARGET INTELLIGENCE - Dynamic targets based on conditions
            # ═══════════════════════════════════════════════════════════════
            # Dynamic profit targets based on market conditions
            if pnl_pct >= 0.015:  # 1.5%+ profit
                # Check if we should hold for more or take profit
                if exit_votes['HOLD'] > exit_votes['SELL'] * 1.2:
                    reasoning_parts.append(f"ProfitTarget: {pnl_pct*100:.2f}% - AI says HOLD for more")
                else:
                    exit_votes['SELL'] += 0.5
                    reasoning_parts.append(f"ProfitTarget: {pnl_pct*100:.2f}% - AI says take profit")

            # ═══════════════════════════════════════════════════════════════
            # 🎯 SYNTHESIZE FINAL EXIT DECISION
            # ═══════════════════════════════════════════════════════════════
            total_votes = sum(exit_votes.values())
            if total_votes == 0:
                total_votes = 1  # Avoid division by zero

            # Determine final action
            final_action = 'SELL' if exit_votes['SELL'] > exit_votes['HOLD'] else 'HOLD'

            # Calculate confidence
            vote_confidence = max(exit_votes.values()) / total_votes
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            final_confidence = (vote_confidence * 0.6 + avg_confidence * 0.4)

            # Build comprehensive reasoning
            reasoning = f"[{len(ai_contributors)} AI systems] " + " | ".join(reasoning_parts[:5])

            self.logger.info(f"🧠 AI EXIT DECISION for {symbol}: {final_action} ({final_confidence:.1%}) - Votes: SELL={exit_votes['SELL']:.2f}, HOLD={exit_votes['HOLD']:.2f}")

            return {
                'action': final_action,
                'confidence': final_confidence,
                'reasoning': reasoning,
                'ai_contributors': ai_contributors,
                'vote_breakdown': exit_votes
            }

        except Exception as e:
            self.logger.error(f"Error in AI exit decision for {symbol}: {e}")
            # Fallback to simple logic
            return {
                'action': 'HOLD',
                'confidence': 0.5,
                'reasoning': f'AI unavailable - defaulting to HOLD',
                'ai_contributors': [],
                'vote_breakdown': {'HOLD': 1, 'SELL': 0}
            }

    def optimize_entry_exit_prices(self, symbol: str, market_data: Dict[str, Any], 
                                    current_price: float, position_data: Optional[Dict[str, Any]] = None,
                                    trade_type: str = 'ENTRY') -> Dict[str, Any]:
        """
        Optimize entry and exit prices using market microstructure analysis.
        
        Analyzes bid-ask spreads, liquidity, momentum, and volatility to recommend
        optimal execution prices that maximize fill probability while minimizing slippage.
        
        Args:
            symbol: Trading symbol
            market_data: Current market data with bid/ask/volume info
            current_price: Current market price
            position_data: Optional position info for exit optimization
            trade_type: 'ENTRY' or 'EXIT'
            
        Returns:
            Dictionary with optimized prices:
            - recommended_price: Best price to target
            - market_price: Current market price
            - limit_offset_bps: Suggested limit order offset in basis points
            - limit_price: Suggested limit price
            - execution_probability: Estimated probability of fill
            - urgency_level: 'LOW', 'MEDIUM', 'HIGH' (affects aggressiveness)
        """
        try:
            # Extract market microstructure data
            bid = market_data.get('bid', current_price * 0.9995)
            ask = market_data.get('ask', current_price * 1.0005)
            spread = (ask - bid) / current_price if current_price > 0 else 0.001
            
            volume = market_data.get('volume', 1000000)  # In shares/contracts
            volume_20d_avg = market_data.get('avg_volume_20d', volume)
            
            # Calculate liquidity score (0-1)
            # Higher liquidity = tighter spreads, more volume
            liquidity_score = min(volume / max(volume_20d_avg, 1) * 0.5, 1.0)
            liquidity_score = max(liquidity_score, 1.0 - spread / 0.01)  # Cap at 1.0
            
            # Get volatility metrics
            volatility = market_data.get('volatility', 0.02)  # Default 2% volatility
            momentum = market_data.get('change_percent', 0) / 100
            
            # Determine execution urgency
            urgency_level = 'LOW'
            if trade_type == 'ENTRY':
                # For entries: higher momentum = more urgent
                if abs(momentum) > 0.02:  # >2% move
                    urgency_level = 'HIGH'
                elif abs(momentum) > 0.01:  # >1% move
                    urgency_level = 'MEDIUM'
            else:
                # For exits: position P&L affects urgency
                if position_data:
                    pnl_pct = position_data.get('pnl_pct', 0)
                    if pnl_pct > 0.02:  # >2% profit - capture it
                        urgency_level = 'HIGH'
                    elif pnl_pct < -0.02:  # <-2% loss - exit now
                        urgency_level = 'HIGH'
            
            # Calculate optimal limit order offset based on:
            # - Spread (tighter spread = less offset needed)
            # - Liquidity (lower liquidity = more offset for better fill)
            # - Urgency (high urgency = offer better price)
            # - Volatility (higher volatility = need buffer)
            
            # Base offset: spread in basis points
            spread_bps = spread * 10000
            
            if trade_type == 'ENTRY':
                # For entries: we want to BUY
                # Use limit order on bid side for better execution if liquidity good
                if urgency_level == 'LOW':
                    # Patient entry: limit order inside the spread
                    limit_offset_bps = max(spread_bps * 0.3, 2)  # Inside spread or 2bps
                    recommended_price = bid + (spread / 3)  # 1/3 into the spread
                    recommended_price = bid  # Most conservative for buy
                elif urgency_level == 'MEDIUM':
                    # Normal entry: market order in tight market, limit in wide
                    limit_offset_bps = max(spread_bps * 0.7, 5)
                    recommended_price = (bid + ask) / 2  # Midpoint
                else:  # HIGH urgency
                    # Aggressive entry: willing to pay more
                    limit_offset_bps = spread_bps * 1.2
                    recommended_price = ask  # Pay the ask
            else:  # EXIT
                # For exits: we want to SELL
                # Use limit order on ask side for better exit
                if urgency_level == 'LOW':
                    # Patient exit: limit order inside the spread
                    limit_offset_bps = max(spread_bps * 0.3, 2)  # Inside spread or 2bps
                    recommended_price = ask - (spread / 3)  # 1/3 into the spread
                    recommended_price = ask  # Most conservative for sell
                elif urgency_level == 'MEDIUM':
                    # Normal exit: market order in tight market, limit in wide
                    limit_offset_bps = max(spread_bps * 0.7, 5)
                    recommended_price = (bid + ask) / 2  # Midpoint
                else:  # HIGH urgency
                    # Aggressive exit: willing to take less
                    limit_offset_bps = spread_bps * 1.2
                    recommended_price = bid  # Take the bid
            
            # Adjust limit price based on offset
            if trade_type == 'ENTRY':
                # For buy: limit price is below ask
                limit_price = ask - (ask * limit_offset_bps / 10000)
            else:
                # For sell: limit price is above bid
                limit_price = bid + (bid * limit_offset_bps / 10000)
            
            # Calculate execution probability
            # Higher liquidity and tighter limits = lower probability
            # Market orders would fill immediately, so execution_probability = 1.0
            execution_probability = min(
                0.95 + liquidity_score * 0.05,  # Bonus for liquidity
                1.0
            )
            
            # Adjust for urgency
            if urgency_level == 'HIGH':
                execution_probability = 0.95  # Market-like orders
            elif urgency_level == 'LOW':
                execution_probability *= 0.6  # Limit orders less likely
            
            result = {
                'recommended_price': round(recommended_price, 4),
                'market_price': current_price,
                'limit_offset_bps': round(limit_offset_bps, 1),
                'limit_price': round(limit_price, 4),
                'execution_probability': min(execution_probability, 1.0),
                'urgency_level': urgency_level,
                'spread_bps': round(spread_bps, 1),
                'liquidity_score': round(liquidity_score, 2),
                'volatility': round(volatility, 3),
                'momentum': round(momentum, 3)
            }
            
            self.logger.debug(f"[OPTIMIZE] {symbol} {trade_type}: Recommended={result['recommended_price']:.4f}, "
                            f"Limit={result['limit_price']:.4f}, P(Fill)={result['execution_probability']:.0%}, "
                            f"Urgency={urgency_level}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"[OPTIMIZE] Error optimizing prices for {symbol}: {e}")
            return {
                'recommended_price': current_price,
                'market_price': current_price,
                'limit_offset_bps': 5,
                'limit_price': current_price,
                'execution_probability': 0.9,
                'urgency_level': 'MEDIUM',
                'spread_bps': 2,
                'liquidity_score': 0.7,
                'volatility': 0.02,
                'momentum': 0.0
            }

    async def _check_position_exits(self):
        """
        🎯 POSITION MONITOR: Check all ACTUAL Alpaca positions for profit-taking and stop-loss exits
        This runs at the start of each trading cycle to lock in profits and limit losses
        Uses REAL Alpaca positions directly (not internal database)

        🧠 NOW WITH AI-DRIVEN DECISIONS: Uses full AI intelligence to decide whether to HOLD or SELL
        """
        self.logger.info("🔍 Position monitor starting...")

        alpaca_broker = self.systems.get('alpaca_broker')
        self.logger.info(f"🔍 Alpaca broker: {alpaca_broker}, connected: {alpaca_broker.connected if alpaca_broker else 'N/A'}")

        if not alpaca_broker or not alpaca_broker.connected:
            self.logger.warning("⚠️ Position monitor: Alpaca broker not connected")
            return

        try:
            # Get ACTUAL Alpaca positions directly from API
            self.logger.info("🔍 Fetching positions from Alpaca...")
            positions = await alpaca_broker.get_positions()  # MUST await async method!
            self.logger.info(f"🔍 Got {len(positions) if positions else 0} positions")

            if not positions:
                self.logger.info("📊 No open positions to monitor")
                return

            self.logger.info(f"📊 🎯 POSITION MONITOR: Checking {len(positions)} Alpaca position(s) for exits...")

            # Configuration for SAFETY BACKSTOPS ONLY (AI makes primary decisions)
            catastrophic_stop_loss_pct = 0.06  # 6% absolute stop loss - SAFETY ONLY
            max_take_profit_pct = 0.10  # 10% - lock in big wins regardless
            stop_loss_pct = self.risk_limits.get('stop_loss_pct', 0.02)  # 2% configurable stop loss — RECONCILED with Guardian

            positions_to_sell = []

            for pos in positions:
                symbol = pos.symbol
                qty = pos.quantity
                avg_price = pos.avg_price
                market_value = pos.market_value
                unrealized_pnl = pos.unrealized_pnl
                pnl_pct = pos.unrealized_pnl_percent
                current_price = avg_price * (1 + pnl_pct) if avg_price > 0 else 0

                self.logger.info(f"  {symbol}: qty={qty:.6f}, avg=${avg_price:.4f}, P/L=${unrealized_pnl:.2f} ({pnl_pct*100:.2f}%)")

                # Check exit conditions
                should_sell = False
                sell_reason = None
                sell_qty = qty  # Default to full position, may be partial for scale-out

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT TRACKING - Update position tracking data
                # ═══════════════════════════════════════════════════════════════

                # Track position high for trailing stop
                tracking_changed = False
                if symbol not in self.position_highs:
                    self.position_highs[symbol] = current_price
                    tracking_changed = True
                elif current_price > self.position_highs[symbol]:
                    self.position_highs[symbol] = current_price
                    tracking_changed = True
                high_price = self.position_highs[symbol]

                # Track entry time for time-based exit
                if symbol not in self.position_entry_times:
                    from datetime import datetime as dt
                    self.position_entry_times[symbol] = dt.now()
                    tracking_changed = True

                # Save tracking if changed
                if tracking_changed:
                    self._save_position_tracking(symbol)

                # Calculate drop from high (for trailing stop)
                drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0

                # Calculate days held (for time exit)
                from datetime import datetime as dt
                entry_time = self.position_entry_times.get(symbol, dt.now())
                days_held = (dt.now() - entry_time).days

                # Is this crypto or stock?
                is_crypto = '/' in symbol or symbol.endswith('USD')

                # ═══════════════════════════════════════════════════════════════
                # 🛡️ SAFETY BACKSTOPS - These override AI decisions
                # ═══════════════════════════════════════════════════════════════

                # 1. CATASTROPHIC STOP LOSS: Force sell if loss >= 6% (safety)
                if pnl_pct <= -catastrophic_stop_loss_pct:
                    should_sell = True
                    sell_reason = f"🛑 CATASTROPHIC_STOP ({pnl_pct*100:.2f}% <= -{catastrophic_stop_loss_pct*100:.0f}%) - SAFETY OVERRIDE"
                    self.logger.warning(f"⚠️ {symbol}: CATASTROPHIC STOP triggered - forcing sell!")

                # 2. BIG WIN LOCK: Force sell if profit >= 10% (lock in big wins)
                elif pnl_pct >= max_take_profit_pct:
                    should_sell = True
                    sell_reason = f"💰 BIG_WIN_LOCK ({pnl_pct*100:.2f}% >= {max_take_profit_pct*100:.0f}%) - locking profits"
                    self.logger.info(f"🎉 {symbol}: BIG WIN - locking in {pnl_pct*100:.2f}% profit!")

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 1: TRAILING STOP - Lock in profits
                # ═══════════════════════════════════════════════════════════════
                elif self.trailing_stop_enabled and pnl_pct >= self.trailing_stop_trigger:
                    # Position is profitable enough to activate trailing stop
                    if drop_from_high >= self.trailing_stop_distance:
                        should_sell = True
                        high_pnl = (high_price - avg_price) / avg_price if avg_price > 0 else 0
                        sell_reason = f"📈 TRAILING_STOP (was +{high_pnl*100:.1f}%, now +{pnl_pct*100:.1f}%, dropped {drop_from_high*100:.1f}%)"
                        self.logger.info(f"📈 {symbol}: TRAILING STOP - locking in profit before further drop!")
                    else:
                        self.logger.info(f"📈 {symbol}: Trailing active - high +{((high_price-avg_price)/avg_price)*100:.1f}%, current +{pnl_pct*100:.1f}%")

                        # FIX: Trailing stop didn't fire - still check scale-out instead of skipping
                        if self.scale_out_enabled:
                            scaled_level = self.scaled_positions.get(symbol, 0)
                            if pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                                should_sell = True
                                sell_reason = f"📊 SCALE_OUT_2 (+{pnl_pct*100:.1f}%) - selling remaining position"
                                self.scaled_positions[symbol] = 2
                                self._save_position_tracking(symbol)
                                self.logger.info(f"📊 {symbol}: SCALE OUT #2 - selling remaining at +{pnl_pct*100:.1f}%!")
                            elif pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                                should_sell = True
                                sell_qty = qty * 0.5  # Sell 50%
                                self.scaled_positions[symbol] = 1
                                self._save_position_tracking(symbol)
                                sell_reason = f"📊 SCALE_OUT_1 (+{pnl_pct*100:.1f}%) - selling 50% to lock gains"
                                self.logger.info(f"📊 {symbol}: SCALE OUT #1 - selling 50% at +{pnl_pct*100:.1f}%!")

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 4: SCALE-OUT - Partial profit taking
                # ═══════════════════════════════════════════════════════════════
                elif self.scale_out_enabled and not should_sell:
                    scaled_level = self.scaled_positions.get(symbol, 0)

                    # First scale-out at +1.5%
                    if pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                        should_sell = True
                        sell_qty = qty * 0.5  # Sell 50%
                        self.scaled_positions[symbol] = 1
                        self._save_position_tracking(symbol)  # Persist scale-out level
                        sell_reason = f"📊 SCALE_OUT_1 (+{pnl_pct*100:.1f}%) - selling 50% to lock gains"
                        self.logger.info(f"📊 {symbol}: SCALE OUT #1 - selling 50% at +{pnl_pct*100:.1f}%!")

                    # Second scale-out at +3%
                    elif pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                        should_sell = True
                        sell_reason = f"📊 SCALE_OUT_2 (+{pnl_pct*100:.1f}%) - selling remaining position"
                        self.scaled_positions[symbol] = 2
                        self._save_position_tracking(symbol)  # Persist scale-out level
                        self.logger.info(f"📊 {symbol}: SCALE OUT #2 - selling remaining at +{pnl_pct*100:.1f}%!")

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 3: TIME-BASED EXIT - Don't hold losers forever
                # ═══════════════════════════════════════════════════════════════
                elif self.time_exit_enabled and not should_sell:
                    max_days = self.max_hold_days_crypto if is_crypto else self.max_hold_days_stock
                    if days_held >= max_days and pnl_pct < self.scale_out_first_pct:
                        # Only time-exit if not profitable enough
                        should_sell = True
                        sell_reason = f"⏰ TIME_EXIT ({days_held}d >= {max_days}d max, P/L: {pnl_pct*100:+.1f}%)"
                        self.logger.info(f"⏰ {symbol}: TIME EXIT - held {days_held} days without hitting target")

                # ═══════════════════════════════════════════════════════════════
                # 🧠 AI-DRIVEN EXIT DECISION - Consult all AI systems
                # ═══════════════════════════════════════════════════════════════
                else:
                    # Prepare position data for AI
                    position_data = {
                        'symbol': symbol,
                        'quantity': qty,
                        'avg_price': avg_price,
                        'current_price': current_price,
                        'market_value': market_value,
                        'unrealized_pnl': unrealized_pnl,
                        'pnl_pct': pnl_pct
                    }

                    # Get AI decision
                    ai_decision = await self._get_ai_exit_decision(symbol, position_data)
                    ai_action = ai_decision.get('action', 'HOLD')
                    ai_confidence = ai_decision.get('confidence', 0.5)
                    ai_reasoning = ai_decision.get('reasoning', 'AI analysis')
                    ai_contributors = ai_decision.get('ai_contributors', [])

                    # ═══════════════════════════════════════════════════════════════
                    # 💰 COST-AWARE CHECK - Don't sell if costs eat the profit!
                    # ═══════════════════════════════════════════════════════════════
                    broker_name = 'Alpaca'  # Default broker
                    cost_analysis = self.is_trade_profitable_after_costs(
                        symbol=symbol,
                        broker=broker_name,
                        entry_price=avg_price,
                        current_price=current_price,
                        quantity=qty
                    )

                    # Log cost analysis
                    self.logger.debug(f"💰 {symbol} Cost Analysis: {cost_analysis['reason']}")

                    # AI says SELL with sufficient confidence (raised from 0.45 to 0.60 to avoid weak signals)
                    if ai_action == 'SELL' and ai_confidence >= 0.60:
                        # Check if profitable after costs (unless it's a loss cut)
                        if pnl_pct > 0 and not cost_analysis['is_profitable']:
                            # Would lose money after costs - override AI SELL
                            self.logger.warning(f"💰 {symbol}: AI says SELL but costs would eat profit!")
                            self.logger.warning(f"   Gross: ${cost_analysis['gross_pnl']:.4f} ({cost_analysis['gross_pnl_pct']*100:.2f}%)")
                            self.logger.warning(f"   Costs: ${cost_analysis['costs']['round_trip']:.4f}")
                            self.logger.warning(f"   Net: ${cost_analysis['net_pnl']:.4f} ({cost_analysis['net_pnl_pct']*100:.2f}%)")
                            self.logger.info(f"💰 {symbol}: HOLDING - need {cost_analysis['costs']['min_profit_pct']*100:.2f}% min profit")
                            # Don't sell - wait for more profit
                        else:
                            # Either profitable or cutting losses - proceed with sell
                            should_sell = True
                            if cost_analysis['is_profitable']:
                                sell_reason = f"🧠💰 AI_DECISION ({pnl_pct*100:.2f}% gross, {cost_analysis['net_pnl_pct']*100:.2f}% net) - {ai_reasoning[:60]}"
                            else:
                                sell_reason = f"🧠 AI_DECISION ({pnl_pct*100:.2f}%) - {ai_reasoning[:80]}"
                            self.logger.info(f"🧠 {symbol}: AI recommends SELL @ {ai_confidence:.0%} confidence [{', '.join(ai_contributors[:3])}]")

                    # AI says HOLD - respect the decision
                    elif ai_action == 'HOLD':
                        self.logger.info(f"🧠 {symbol}: AI recommends HOLD @ {ai_confidence:.0%} - {ai_reasoning[:50]}")

                        # But apply configurable stop loss as secondary safety (1.5%)
                        if pnl_pct <= -stop_loss_pct:
                            should_sell = True
                            sell_reason = f"🛑 STOP_LOSS ({pnl_pct*100:.2f}% <= -{stop_loss_pct*100:.0f}%) - despite AI HOLD"
                            self.logger.warning(f"⚠️ {symbol}: Stop loss override despite AI HOLD recommendation")

                if should_sell:
                    positions_to_sell.append({
                        'symbol': symbol,
                        'quantity': sell_qty,  # Use sell_qty for partial sells (scale-out)
                        'full_quantity': qty,  # Keep track of full position
                        'avg_price': avg_price,
                        'market_value': market_value,
                        'unrealized_pnl': unrealized_pnl,
                        'pnl_pct': pnl_pct,
                        'sell_reason': sell_reason
                    })
                    self.logger.info(f"    🚨 EXIT SIGNAL: {symbol} - {sell_reason}")

                # ═══════════════════════════════════════════════════════════════
                # 🚀 ENHANCEMENT 2: DCA ON DIPS - Buy more to average down
                # ═══════════════════════════════════════════════════════════════
                elif self.dca_enabled and pnl_pct <= self.dca_trigger_pct and not should_sell:
                    dca_count = self.dca_counts.get(symbol, 0)
                    if dca_count < self.dca_max_adds:
                        # Calculate DCA buy amount
                        try:
                            account = await alpaca_broker.get_account()
                            if account:
                                buying_power = float(account.buying_power) if hasattr(account, 'buying_power') else 0
                                dca_amount = buying_power * self.dca_position_pct

                                if dca_amount >= 10 and buying_power >= dca_amount:  # Min $10 DCA
                                    dca_qty = dca_amount / current_price if current_price > 0 else 0
                                    if dca_qty > 0:
                                        self.logger.info(f"📉 {symbol}: DCA OPPORTUNITY - down {pnl_pct*100:.1f}%, buying ${dca_amount:.2f} more (DCA #{dca_count + 1})")

                                        # Execute DCA buy via place_order (async)
                                        # FIX: .buy() method doesn't exist on AlpacaBroker; use place_order()
                                        dca_result = await alpaca_broker.place_order(symbol, dca_qty, side='buy')
                                        if dca_result:
                                            self.dca_counts[symbol] = dca_count + 1
                                            self._save_position_tracking(symbol)  # Persist DCA count
                                            self.logger.info(f"📉 ✅ DCA BUY #{dca_count + 1} for {symbol}: {dca_qty:.6f} @ ${current_price:.4f}")

                                            # Record DCA trade
                                            from datetime import datetime as dt
                                            self.trades_this_hour.append(dt.now())
                                        else:
                                            self.logger.warning(f"📉 ❌ DCA buy failed for {symbol}")
                        except Exception as dca_error:
                            self.logger.debug(f"DCA check error for {symbol}: {dca_error}")

            # Execute sell orders for positions that meet exit criteria
            sells_executed = 0
            for sell_pos in positions_to_sell:
                symbol = sell_pos['symbol']
                qty = sell_pos['quantity']
                sell_reason = sell_pos['sell_reason']
                pnl_pct = sell_pos['pnl_pct']

                self.logger.info(f"🔄 Executing SELL for {symbol}: {qty} shares - {sell_reason}")

                try:
                    # Execute sell order directly via Alpaca
                    result = alpaca_broker.sell(symbol, qty)

                    if result and result.get('success'):
                        profit_emoji = "💰" if pnl_pct > 0 else "🛑"
                        self.logger.info(f"{profit_emoji} ✅ SOLD {symbol}: {qty} shares at {pnl_pct*100:+.2f}% - {sell_reason}")
                        sells_executed += 1

                        # Record trade timestamp for rate limiting
                        from datetime import datetime as dt
                        self.trades_this_hour.append(dt.now())

                        # 🧠 LEARNING FEEDBACK: Feed outcome to learning engines
                        await self._record_learning_outcome(
                            symbol=symbol,
                            entry_price=sell_pos['avg_price'],
                            exit_price=result.get('filled_price', sell_pos['avg_price'] * (1 + pnl_pct)),
                            quantity=qty,
                            profit_loss=sell_pos['unrealized_pnl'],
                            profit_pct=pnl_pct,
                            exit_reason=sell_reason,
                            broker='Alpaca'
                        )

                        # 🧹 CLEANUP: Clear position tracking if fully sold
                        if sell_pos['quantity'] >= sell_pos.get('full_quantity', sell_pos['quantity']) * 0.99:
                            # Full position sold - clean up tracking
                            self._cleanup_position_tracking(symbol)
                    else:
                        error_msg = result.get('error', 'Unknown error') if result else 'No result'
                        self.logger.error(f"❌ Failed to sell {symbol}: {error_msg}")

                except Exception as e:
                    self.logger.error(f"❌ Exception selling {symbol}: {e}")

            if sells_executed > 0:
                self.logger.info(f"✅ Position monitor completed: {sells_executed}/{len(positions_to_sell)} sells executed")
            else:
                self.logger.info(f"📊 Position monitor: No exit conditions met for {len(positions)} positions")

        except Exception as e:
            self.logger.error(f"Error in position monitoring: {e}")

    def validate_trade_quality(self, trade_result: Dict[str, Any], signal_source: str = 'Unknown',
                               market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive trade quality validation and performance assessment.
        
        Validates execution quality, profitability, and consistency to:
        - Ensure trades meet minimum quality standards
        - Track AI system performance
        - Identify and suppress low-quality signals
        - Maintain execution discipline
        
        Args:
            trade_result: Actual trade execution results
            signal_source: Which AI system generated this signal (for tracking)
            market_context: Current market conditions context
            
        Returns:
            Trade quality assessment with:
            - quality_score: 0-100 score
            - is_acceptable: Whether trade meets quality standards
            - quality_issues: List of problems found
            - performance_metrics: How well trade executed
            - system_performance: Score for signal source
        """
        try:
            quality_issues = []
            quality_components = {}
            
            # Extract trade details
            symbol = trade_result.get('symbol', 'UNKNOWN')
            entry_price = trade_result.get('entry_price', 0)
            fill_price = trade_result.get('fill_price', entry_price)
            quantity = trade_result.get('quantity', 0)
            broker = trade_result.get('broker', 'unknown').lower()
            order_time = trade_result.get('order_time', 0)
            fill_time = trade_result.get('fill_time', 0)
            
            # Performance metrics
            execution_time = max(fill_time - order_time, 0) if order_time and fill_time else 60  # seconds
            execution_time_minutes = execution_time / 60
            
            # 1. EXECUTION QUALITY
            # ═════════════════════════════════════════════════════════════════
            # Compare fill price to entry price (should be close)
            entry_slippage_pct = abs(fill_price - entry_price) / entry_price if entry_price > 0 else 0
            
            if entry_slippage_pct > 0.005:  # >0.5% slippage
                quality_issues.append(f"High entry slippage: {entry_slippage_pct*100:.2f}%")
            
            # Score: lower slippage = higher score
            execution_quality = max(0, 100 - entry_slippage_pct * 10000)
            quality_components['execution'] = execution_quality
            
            # 2. FILL RATE
            # ═════════════════════════════════════════════════════════════════
            # Was the full quantity filled?
            fill_rate = trade_result.get('filled_qty', quantity) / quantity if quantity > 0 else 1.0
            
            if fill_rate < 1.0:
                quality_issues.append(f"Partial fill: {fill_rate*100:.1f}%")
            
            fill_rate_score = fill_rate * 100
            quality_components['fill_rate'] = fill_rate_score
            
            # 3. FILL TIME
            # ═════════════════════════════════════════════════════════════════
            # How long did it take to fill?
            # Fast fills (<5 seconds) are ideal
            # Slow fills (>30 seconds) might indicate issues
            
            if execution_time < 5:
                fill_time_score = 100
            elif execution_time < 30:
                fill_time_score = 100 - (execution_time - 5) * 2
            else:
                fill_time_score = 40 - (execution_time - 30) * 0.5
                quality_issues.append(f"Slow fill: {execution_time_minutes:.1f} minutes")
            
            fill_time_score = max(30, min(100, fill_time_score))
            quality_components['fill_time'] = fill_time_score
            
            # 4. TRADE ACCEPTABILITY
            # ═════════════════════════════════════════════════════════════════
            # Is there an order ID (confirmation)?
            if not trade_result.get('order_id'):
                quality_issues.append("Missing order ID")
            
            # Is the order status filled/completed?
            status = trade_result.get('status', 'unknown').lower()
            if status not in ['filled', 'completed', 'accepted']:
                quality_issues.append(f"Unexpected status: {status}")
            
            # 5. PROFITABILITY POTENTIAL
            # ═════════════════════════════════════════════════════════════════
            # Check if trade is likely to be profitable after costs
            trade_value = entry_price * quantity
            expected_costs = self.get_trading_cost(symbol, broker, trade_value)
            
            # For new trades, we can't know actual P&L yet
            # But we can check if signal timing was good
            if market_context:
                market_price = market_context.get('price', entry_price)
                market_momentum = market_context.get('momentum', 0)
                
                # Better if we bought near lows (for BUY) or near highs (for SELL)
                entry_alignment = market_context.get('price_percentile', 0.5)  # 0=lowest, 1=highest
                
                is_buy = trade_result.get('action', 'BUY').upper() == 'BUY'
                if is_buy and entry_alignment < 0.4:  # Bought in lower part of range - good
                    profitability_score = 90
                elif not is_buy and entry_alignment > 0.6:  # Sold in upper part - good
                    profitability_score = 90
                else:
                    profitability_score = 70
                
                quality_components['profitability'] = profitability_score
            else:
                quality_components['profitability'] = 75
            
            # 6. BROKER ALIGNMENT
            # ═════════════════════════════════════════════════════════════════
            # Did the trade go to the right broker?
            ordered_broker = trade_result.get('ordered_broker', 'unknown').lower()
            
            if ordered_broker != broker and ordered_broker != 'unknown':
                quality_issues.append(f"Broker mismatch: ordered {ordered_broker}, filled at {broker}")
                broker_score = 70
            else:
                broker_score = 95
            
            quality_components['broker'] = broker_score
            
            # 7. SIGNAL SOURCE TRACKING
            # ═════════════════════════════════════════════════════════════════
            # Track which AI system generated this signal
            system_performance = {
                'signal_source': signal_source,
                'trade_count': 1,
                'quality_score_for_system': quality_components,
                'issues': quality_issues
            }
            
            # FINAL SCORE
            # ═════════════════════════════════════════════════════════════════
            # Weighted average of components
            if quality_components:
                weights = {
                    'execution': 0.25,
                    'fill_rate': 0.20,
                    'fill_time': 0.15,
                    'profitability': 0.25,
                    'broker': 0.15
                }
                
                final_score = sum(
                    quality_components.get(key, 50) * weight
                    for key, weight in weights.items()
                )
            else:
                final_score = 60
            
            # Quality threshold - trades should score >70 to be acceptable
            is_acceptable = final_score >= 70 and len(quality_issues) < 3
            
            # Severe issues that reject trade
            severe_issues = [issue for issue in quality_issues if any(
                keyword in issue.lower() for keyword in ['broker mismatch', 'status', 'missing order']
            )]
            if severe_issues:
                is_acceptable = False
            
            result = {
                'quality_score': round(final_score, 1),
                'is_acceptable': is_acceptable,
                'quality_issues': quality_issues,
                'severe_issues': severe_issues,
                'performance_metrics': {
                    'execution_slippage_pct': round(entry_slippage_pct, 4),
                    'fill_rate': round(fill_rate, 3),
                    'fill_time_seconds': execution_time,
                    'fill_time_minutes': round(execution_time_minutes, 2)
                },
                'component_scores': quality_components,
                'system_performance': system_performance,
                'recommendation': 'ACCEPT' if is_acceptable else 'REVIEW'
            }
            
            # Logging
            if result['quality_score'] >= 80:
                self.logger.info(f"✅ [QUALITY] {symbol} from {signal_source}: Score {result['quality_score']:.0f} - EXCELLENT")
            elif result['quality_score'] >= 70:
                self.logger.info(f"✅ [QUALITY] {symbol} from {signal_source}: Score {result['quality_score']:.0f} - ACCEPTABLE")
            else:
                self.logger.warning(f"⚠️  [QUALITY] {symbol} from {signal_source}: Score {result['quality_score']:.0f} - POOR")
                for issue in quality_issues:
                    self.logger.warning(f"   - {issue}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"[QUALITY] Error validating trade quality: {e}")
            return {
                'quality_score': 50,
                'is_acceptable': False,
                'quality_issues': [f'Validation error: {str(e)}'],
                'severe_issues': [],
                'performance_metrics': {},
                'component_scores': {},
                'system_performance': {'signal_source': signal_source},
                'recommendation': 'REJECT'
            }

    async def run_trading_cycle(self):
        """Execute one complete trading cycle with AI analysis and trade execution"""
        try:
            self.logger.info(" Starting trading cycle...")

            # ═══════════════════════════════════════════════════════════════
            # 📊 REGIME-EXPOSURE MODEL UPDATE (proven in 50-year benchmark)
            # Updates smoothed allocation target based on current regime
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.regime_exposure_manager import get_regime_exposure_manager
                rem = get_regime_exposure_manager()

                # Get current regime + daily return for shock detection
                _rem_regime = self.market_regime or 'unknown'
                _rem_daily_return = 0.0
                _rem_equity = 0.0
                _rem_predicted = None

                try:
                    _rem_combined = await self._get_combined_capital()
                    _rem_equity = _rem_combined.get('total_equity', 0)
                except Exception:
                    pass

                # Get SPY daily return for shock detection
                try:
                    if self.systems.get('yahoo_finance'):
                        yf = self.systems['yahoo_finance']
                        if hasattr(yf, 'get_historical_data_async'):
                            _spy_hist = await yf.get_historical_data_async('SPY', timeframe='1Day', limit=2)
                        elif hasattr(yf, 'get_historical_data'):
                            _spy_hist = yf.get_historical_data('SPY', timeframe='1Day', limit=2)
                        else:
                            _spy_hist = None
                        if _spy_hist and len(_spy_hist) >= 2:
                            _c0 = _spy_hist[-2].get('close', _spy_hist[-2].get('Close', 0))
                            _c1 = _spy_hist[-1].get('close', _spy_hist[-1].get('Close', 0))
                            if _c0 > 0:
                                _rem_daily_return = (_c1 - _c0) / _c0
                except Exception:
                    pass

                # Get World Model prediction if available
                try:
                    from core.world_model import get_world_model
                    wm = get_world_model()
                    if hasattr(wm, 'predict_next_regime'):
                        _rem_predicted = wm.predict_next_regime()
                except Exception:
                    pass

                alloc_state = rem.update(
                    regime=_rem_regime,
                    daily_return=_rem_daily_return,
                    portfolio_equity=_rem_equity,
                    predicted_next_regime=_rem_predicted,
                )
                self.logger.info(
                    f"📊 Regime Allocation: {alloc_state.target_allocation:.0%} invested | "
                    f"size_scale={alloc_state.size_scale:.2f}x | "
                    f"max_pos={alloc_state.max_positions} | {alloc_state.reason}"
                )
                if alloc_state.is_shock:
                    self.logger.warning(f"⚡ MARKET SHOCK DETECTED — reducing exposure")

                # ── Cross-Asset Overlay on Regime-Exposure ──────────────
                try:
                    from core.cross_asset_intelligence import get_cross_asset_intelligence
                    xai = get_cross_asset_intelligence()
                    xai_adj = xai.get_regime_adjustment(self.market_regime or 'NORMAL')
                    xai_alloc_mult = xai_adj['allocation_multiplier']
                    if abs(xai_alloc_mult - 1.0) > 0.01:
                        # Adjust the smoothed allocation in the manager
                        rem.smoothed_alloc = max(0.0, min(1.0, rem.smoothed_alloc * xai_alloc_mult))
                        self.logger.info(
                            f"   🌐 Cross-asset overlay: {xai_alloc_mult:.2f}x "
                            f"→ alloc now {rem.smoothed_alloc:.0%} | {xai.format_status()}"
                        )
                except Exception as xai_err:
                    self.logger.debug(f"Cross-asset overlay failed: {xai_err}")

            except Exception as rem_err:
                self.logger.debug(f"Regime exposure update failed: {rem_err}")

            # Check broker connections and reconnect if needed
            broker_status = {}
            
            # Check Alpaca
            if 'alpaca_broker' in self.systems:
                alpaca_connected = self.systems['alpaca_broker'].is_available() if hasattr(self.systems['alpaca_broker'], 'is_available') else False
                broker_status['Alpaca'] = '✅ CONNECTED' if alpaca_connected else '❌ DISCONNECTED'
            else:
                broker_status['Alpaca'] = '❌ NOT INITIALIZED'
            
            # Check IB and attempt reconnection if needed
            if 'ib_broker' in self.systems and hasattr(self.systems['ib_broker'], 'check_connection'):
                # Reset retry counter each cycle so reconnection is always attempted
                if hasattr(self.systems['ib_broker'], 'connection_retry_count'):
                    self.systems['ib_broker'].connection_retry_count = 0
                ib_connected = await self.systems['ib_broker'].check_connection()
                if not ib_connected:
                    # Attempt fresh reconnection (create new client if needed)
                    self.logger.warning(f"⚠️  IB broker not connected on port {self.ib_port} - attempting reconnection...")
                    try:
                        # Reset the IB client objects for a clean reconnection
                        ib_broker = self.systems['ib_broker']
                        if hasattr(ib_broker, 'wrapper') and hasattr(ib_broker, 'client'):
                            try:
                                ib_broker.client.disconnect()
                            except:
                                pass
                            from ibapi.client import EClient
                            ib_broker.client = EClient(ib_broker.wrapper)
                        reconnect_result = await ib_broker.connect()
                        if reconnect_result and ib_broker.connected:
                            self.logger.info("✅ IB reconnection successful!")
                            self.system_health['ib_broker'] = 'ACTIVE'
                            broker_status['IB'] = '✅ CONNECTED (reconnected)'
                        else:
                            broker_status['IB'] = f'❌ DISCONNECTED (port {self.ib_port})'
                            self.logger.warning(f"   IB reconnection failed - check IB Gateway on port {self.ib_port}")
                    except Exception as e:
                        broker_status['IB'] = f'❌ CONNECTION ERROR'
                        self.logger.error(f"   IB reconnection error: {e}")
                else:
                    broker_status['IB'] = '✅ CONNECTED'
            elif 'ib_broker' in self.systems:
                broker_status['IB'] = '⚠️  NO CHECK METHOD'
            else:
                broker_status['IB'] = '❌ NOT INITIALIZED'
            
            # Display broker status
            self.logger.info(f"📊 Broker Status: {broker_status.get('Alpaca', 'UNKNOWN')} | {broker_status.get('IB', 'UNKNOWN')}")

            # 🔄 POSITION SYNC: Sync internal database with BOTH brokers' actual positions
            # This prevents "account is not allowed to short" errors from phantom positions
            await self._sync_positions_from_alpaca()
            await self._sync_positions_from_ib()

            # 🎯 POSITION MONITORING: Check existing positions for exit conditions (BOTH brokers)
            await self._check_position_exits()
            await self._check_ib_position_exits()

            # RECOVERY MODE: Check trade rate limit (max 3 trades/hour)
            from datetime import datetime, timedelta
            now = datetime.now()
            one_hour_ago = now - timedelta(hours=1)

            # Remove trades older than 1 hour
            self.trades_this_hour = [t for t in self.trades_this_hour if t > one_hour_ago]

            if len(self.trades_this_hour) >= self.risk_limits.get('max_trades_per_hour', 20):
                self.logger.info(f" Trade rate limit reached: {len(self.trades_this_hour)} trades in last hour")
                self.logger.info(f"   Next trade available in {int((self.trades_this_hour[0] + timedelta(hours=1) - now).total_seconds() / 60)} minutes")
                return

            # 💰 DUAL-BROKER CAPITAL CHECK: Log combined capital for visibility
            try:
                combined_cap = await self._get_combined_capital()
                self.logger.info(f"💰 Total Trading Capital: ${combined_cap['total_equity']:.2f} | "
                                f"Idle Cash: ${combined_cap['total_cash']:.2f} | "
                                f"Brokers Active: {combined_cap['brokers_active']}")
            except Exception as e:
                self.logger.debug(f"Combined capital check failed: {e}")

            # 🧠 AI-ENHANCED WATCHLIST - Combines base symbols with AI-discovered opportunities
            watchlist = await self._get_ai_enhanced_watchlist()

            # Check if market is open for stocks
            market_open = False
            if MARKET_HOURS_UTILS_AVAILABLE:
                try:
                    from core.market_hours_utils import is_market_open
                    market_open = is_market_open(include_extended_hours=False)
                except:
                    pass

            # Determine which symbols to trade
            symbols_to_analyze = []

            # Crypto trades 24/7 via Alpaca
            if self.systems.get('alpaca_broker'):
                symbols_to_analyze.extend(watchlist['crypto'])
                self.logger.info(f" Analyzing {len(watchlist['crypto'])} crypto symbols (24/7 trading)")

                # Alpaca 24-hour stocks (Sunday 8 PM ET - Friday 8 PM ET)
                # These stocks can trade outside regular market hours
                alpaca_24hr_stocks = [s for s in watchlist['stocks'] if self._is_alpaca_24hr_stock(s)]
                if alpaca_24hr_stocks:
                    symbols_to_analyze.extend(alpaca_24hr_stocks)
                    self.logger.info(f" Analyzing {len(alpaca_24hr_stocks)} Alpaca 24-hour stocks (extended hours)")

            # Forex trades 24/5 via IB (ONLY if IB is connected)
            ib_broker = self.systems.get('ib_broker')
            ib_connected = ib_broker and hasattr(ib_broker, 'connected') and ib_broker.connected

            if ib_connected:
                symbols_to_analyze.extend(watchlist['forex'])
                self.logger.info(f" Analyzing {len(watchlist['forex'])} forex pairs (24/5 trading via IB)")
            else:
                self.logger.info(f"⚠️ Skipping forex - IB Gateway not connected")

            # IB stocks only during regular market hours (and IB connected)
            if market_open and ib_connected:
                # Only add IB stocks that aren't already in Alpaca 24hr list
                ib_only_stocks = [s for s in watchlist['stocks'] if not self._is_alpaca_24hr_stock(s)]
                symbols_to_analyze.extend(ib_only_stocks)
                self.logger.info(f" Analyzing {len(ib_only_stocks)} IB stock symbols (market open)")
            elif not market_open:
                alpaca_24hr_count = len([s for s in watchlist['stocks'] if self._is_alpaca_24hr_stock(s)])
                forex_count = len(watchlist['forex']) if ib_connected else 0
                if alpaca_24hr_count > 0:
                    self.logger.info(f" Stock market closed - trading {len(watchlist['crypto'])} crypto + {alpaca_24hr_count} Alpaca 24hr stocks" + (f" + {forex_count} forex pairs" if forex_count > 0 else ""))
                else:
                    self.logger.info(f" Stock market closed - trading {len(watchlist['crypto'])} crypto" + (f" + {forex_count} forex pairs" if forex_count > 0 else ""))

            if not symbols_to_analyze:
                self.logger.info(" No symbols to analyze this cycle")
                return

            # Analyze each symbol
            trades_executed = 0
            for symbol in symbols_to_analyze:
                try:
                    # ═══════════════════════════════════════════════════════════════
                    # 📊 REGIME-EXPOSURE: Check position limit before analysis
                    # ═══════════════════════════════════════════════════════════════
                    try:
                        from core.regime_exposure_manager import get_regime_exposure_manager
                        _rem = get_regime_exposure_manager()
                        _rem_state = _rem.get_current_state()
                        if _rem_state.target_allocation <= 0.02:
                            self.logger.info(f"📊 Regime allocation near zero ({_rem_state.target_allocation:.0%}) — skipping new entries")
                            break
                    except Exception:
                        pass

                    # Get AI trading signal
                    signal = await self.get_ai_trading_signal(symbol)

                    if signal:
                        confidence = signal.get('confidence', 0)
                        action = signal.get('action', 'HOLD')

                        # Log all signals (even HOLD) for visibility
                        if action in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL']:
                            self.logger.info(f"📈 Signal: {symbol} → {action} (Confidence: {confidence*100:.1f}%)")
                            print(f"      {symbol}: {action} @ {confidence*100:.1f}% confidence")

                        # ═══════════════════════════════════════════════════════════════
                        # 🔄 SHADOW FEEDER — Send EVERY signal to shadow trader
                        # The shadow trader makes its OWN independent decision on
                        # whether to trade, ignoring live gates/capital constraints.
                        # This lets Prometheus learn from trades it would have missed.
                        # ═══════════════════════════════════════════════════════════════
                        shadow_trader = self.systems.get('shadow_trader')
                        if shadow_trader:
                            try:
                                # Normalise action for shadow: STRONG_BUY→BUY, STRONG_SELL→SELL
                                _shadow_action = action.replace('STRONG_', '') if action.startswith('STRONG_') else action
                                # Build lightweight market_data dict from the signal
                                _shadow_price = signal.get('entry_price', 0) or signal.get('price', 0) or signal.get('current_price', 0)
                                if not _shadow_price or _shadow_price <= 0:
                                    try:
                                        import yfinance as yf
                                        _t = yf.Ticker(symbol)
                                        _shadow_price = _t.fast_info.get('lastPrice') or _t.fast_info.get('last_price') or 0
                                    except Exception:
                                        _shadow_price = 0
                                if _shadow_price and _shadow_price > 0 and _shadow_action in ('BUY', 'SELL'):
                                    _shadow_qty = max(1, int((shadow_trader.current_capital * shadow_trader.max_position_pct) / _shadow_price))
                                    _shadow_decision = {
                                        'action': _shadow_action,
                                        'quantity': _shadow_qty,
                                        'confidence': confidence,
                                        'reason': signal.get('reasoning', 'live_signal_feed'),
                                        'ai_components': signal.get('ai_components', []),
                                    }
                                    _shadow_market = {
                                        'price': _shadow_price,
                                        'target_price': signal.get('target_price', _shadow_price * (1.02 if _shadow_action == 'BUY' else 0.98)),
                                        'stop_loss': signal.get('stop_loss', _shadow_price * (0.97 if _shadow_action == 'BUY' else 1.03)),
                                        'volume': signal.get('volume', 0),
                                    }
                                    _shadow_result = await shadow_trader.execute_shadow_trade(symbol, _shadow_decision, _shadow_market)
                                    if _shadow_result:
                                        self.logger.info(f"🔄 SHADOW TRADE: {_shadow_action} {symbol} @ ${_shadow_price:.2f} (confidence {confidence*100:.1f}%)")
                            except Exception as _shadow_err:
                                self.logger.debug(f"Shadow feed error for {symbol}: {_shadow_err}")

                        # Skip HOLD signals early — no point running 7 gate layers on non-trades
                        if action == 'HOLD':
                            continue

                        if confidence >= self.risk_limits['min_confidence']:
                            # ═══════════════════════════════════════════════════════════════
                            # 🚀 ENHANCEMENT 5: SENTIMENT FILTER - Check for Fed days
                            # ═══════════════════════════════════════════════════════════════
                            sentiment_check = self._check_sentiment_filter()
                            if not sentiment_check.get('should_trade', True):
                                self.logger.info(f"📅 SENTIMENT FILTER: Skipping {symbol} - {sentiment_check.get('reason', 'Event day')}")
                                print(f"      📅 Sentiment filter: {sentiment_check.get('reason')}")
                                continue

                            # ═══════════════════════════════════════════════════════════════
                            # 🚀 ENHANCEMENT 6: CORRELATION FILTER - Limit sector exposure
                            # ═══════════════════════════════════════════════════════════════
                            if action in ['BUY', 'STRONG_BUY']:  # Only check for buys
                                correlation_check = await self._check_correlation_filter(symbol)
                                if not correlation_check.get('should_trade', True):
                                    self.logger.info(f"🔗 CORRELATION FILTER: Skipping {symbol} - {correlation_check.get('reason', 'Sector maxed')}")
                                    print(f"      🔗 Correlation filter: {correlation_check.get('reason')}")
                                    continue

                            # 🧠 AI-DRIVEN TRADE TIMING CHECK
                            market_data = await self.fetch_market_data(symbol)
                            current_price = market_data.get('price', 0) if market_data else 0

                            timing_decision = await self._should_delay_entry(
                                symbol=symbol,
                                action=action,
                                confidence=confidence,
                                current_price=current_price,
                                market_data=market_data or {}
                            )

                            if not timing_decision['should_execute']:
                                delay_mins = timing_decision.get('suggested_delay_mins', 0)
                                delay_reason = timing_decision.get('delay_reason', 'Timing not optimal')
                                self.logger.info(f"⏳ AI TIMING: Skipping {symbol} - {delay_reason}")
                                print(f"      ⏳ Delay recommended for {symbol}: {delay_reason}")

                                # Store signal for later retry (optional future enhancement)
                                continue

                            # ═══════════════════════════════════════════════════════════════
                            # 🧪 CROSS-LEARNING GATE: Check shadow trading performance
                            # If shadow data for this symbol+action exists AND shows poor
                            # performance, block the live trade. If no shadow data exists,
                            # allow the trade (don't punish lack of shadow data).
                            # ═══════════════════════════════════════════════════════════════
                            shadow_check = await self._validate_against_shadow_results(symbol, action, confidence)
                            if not shadow_check.get('should_trade', True):
                                self.logger.warning(f"🧪 SHADOW GATE: Blocking {symbol} {action} - {shadow_check.get('reason', 'poor shadow performance')}")
                                print(f"      🧪 Shadow gate: {shadow_check.get('reason')}")
                                continue

                            # ═══════════════════════════════════════════════════════════════
                            # 💀 DEAD-END MEMORY: Have we failed this exact setup before?
                            # ═══════════════════════════════════════════════════════════════
                            try:
                                from core.dead_end_memory import get_dead_end_memory
                                dead_end = get_dead_end_memory()
                                blocked, block_reason = dead_end.should_block_trade(symbol, action=action)
                                if blocked:
                                    self.logger.warning(f"💀 DEAD-END BLOCK: {symbol} {action} - {block_reason}")
                                    print(f"      💀 Dead-end block: {block_reason[:60]}")
                                    continue
                            except Exception as de_err:
                                self.logger.debug(f"Dead-end memory check failed: {de_err}")

                            # ═══════════════════════════════════════════════════════════════
                            # 🛡️ DRAWDOWN GUARDIAN: 10-layer hard risk enforcement
                            # Guardian initialized at startup (__init__) — no lazy init needed
                            # ═══════════════════════════════════════════════════════════════
                            try:
                                if self._guardian:
                                    # Gather portfolio state for guardian
                                    _g_open_pos = {}
                                    _g_portfolio_val = 0
                                    _g_brokers_active = 0
                                    _g_regime = "unknown"
                                    try:
                                        _g_combined = await self._get_combined_capital()
                                        _g_portfolio_val = _g_combined.get('total_equity', 0)
                                        _g_brokers_active = _g_combined.get('brokers_active', 0)
                                    except Exception:
                                        pass
                                    try:
                                        alpaca_b = self.systems.get('alpaca_broker')
                                        if alpaca_b:
                                            _g_positions = await alpaca_b.get_positions()
                                            for _p in (_g_positions or []):
                                                _g_open_pos[_p.symbol] = {
                                                    "market_value": abs(float(getattr(_p, 'market_value', 0))),
                                                    "qty": float(getattr(_p, 'quantity', 0)),
                                                }
                                    except Exception:
                                        pass
                                    try:
                                        from core.hmm_regime_detector import get_regime_detector
                                        _rd = get_regime_detector()
                                        _rs = _rd.get_status()
                                        _g_regime = _rs.get("current_regime", "unknown")
                                    except Exception:
                                        pass

                                    # Get current price for this symbol
                                    _g_price = 0
                                    try:
                                        _g_md = await self.fetch_market_data(symbol)
                                        _g_price = _g_md.get('price', 0) if _g_md else 0
                                    except Exception:
                                        pass

                                    # Compute actual proposed position size (% of portfolio)
                                    _g_proposed_size_pct = self.risk_limits['position_size_pct']
                                    try:
                                        _g_proposed_size_pct = await self._get_ai_position_size(symbol, signal, _g_portfolio_val)
                                    except Exception:
                                        pass  # fallback to base risk_limits size

                                    # FIX: Convert percentage → units. Guardian.gate() expects
                                    # proposed_size in UNITS (shares/coins), not a fraction.
                                    # Without this, 0.15 × $0.50 = $0.075 → "Size too small".
                                    if _g_price > 0 and _g_portfolio_val > 0:
                                        _g_proposed_size = (_g_proposed_size_pct * _g_portfolio_val) / _g_price
                                    else:
                                        _g_proposed_size = 0

                                    # GATE CHECK — with actual position size in UNITS
                                    _g_approved, _g_adj_size, _g_reason = self._guardian.gate(
                                        symbol=symbol,
                                        action=action,
                                        proposed_size=_g_proposed_size,
                                        price=_g_price,
                                        confidence=confidence,
                                        portfolio_value=_g_portfolio_val,
                                        open_positions=_g_open_pos,
                                        regime=_g_regime,
                                        volatility_ratio=1.0,
                                        brokers_active=_g_brokers_active,
                                    )

                                    if not _g_approved:
                                        self.logger.warning(f"🛡️ GUARDIAN BLOCKED: {symbol} {action} — {_g_reason}")
                                        print(f"      🛡️ Guardian block: {_g_reason[:60]}")
                                        continue
                                    elif "adjusted" in _g_reason.lower():
                                        self.logger.info(f"🛡️ GUARDIAN: {symbol} {_g_reason}")
                                else:
                                    self.logger.warning("🛡️ Guardian not initialized — skipping gate check")
                            except Exception as guardian_err:
                                self.logger.debug(f"Guardian check failed: {guardian_err}")

                            # Execute trade
                            print(f"      → Executing {action} order...")
                            success = await self.execute_trade_from_signal(signal)
                            if success:
                                trades_executed += 1
                                # AGGRESSIVE MODE: Record trade timestamp for rate limiting
                                from datetime import datetime
                                self.trades_this_hour.append(datetime.now())
                                self.logger.info(f"✅ Trade executed for {symbol} ({len(self.trades_this_hour)}/20 this hour)")
                                print(f"      ✅ Trade EXECUTED for {symbol}")

                                # ═══════════════════════════════════════════════════════════════
                                # 🎯 AI ATTRIBUTION: Record signal ONLY for executed trades
                                # This fixes the 99.6% P/L recording gap - we only record
                                # signals that actually result in trades, with a unique trade_id
                                # that links the signal to its eventual outcome.
                                # ═══════════════════════════════════════════════════════════════
                                try:
                                    from core.ai_attribution_tracker import get_attribution_tracker
                                    trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}"

                                    # Store trade_id for later outcome recording
                                    self.position_trade_ids[symbol] = trade_id
                                    self._save_position_tracking(symbol)

                                    tracker = get_attribution_tracker()
                                    await tracker.record_signal(
                                        symbol=symbol,
                                        ai_components=signal.get('ai_components', []),
                                        vote_breakdown=signal.get('vote_breakdown', {}),
                                        action=signal.get('action', 'BUY'),
                                        confidence=signal.get('confidence', 0.5),
                                        entry_price=signal.get('entry_price', 0),
                                        trade_id=trade_id
                                    )
                                    self.logger.info(f"🎯 AI Attribution recorded for {symbol} (trade_id={trade_id})")
                                except Exception as attr_err:
                                    self.logger.warning(f"Attribution recording failed: {attr_err}")

                                # AGGRESSIVE MODE: Allow more trades per cycle for 6-8% daily returns
                                if trades_executed >= 10:  # Max 10 trades per cycle (aggressive)
                                    self.logger.info(" Max trades per cycle reached (10) - AGGRESSIVE MODE")
                                    print(f"   ⚠️  Max trades per cycle reached (10)")
                                    break
                        else:
                            # Log why trade wasn't executed
                            self.logger.debug(f"   Signal confidence {confidence*100:.1f}% below threshold {self.risk_limits['min_confidence']*100:.0f}%")

                    # Small delay between analyses
                    try:
                        await asyncio.sleep(0.5)  # Faster analysis for more opportunities
                    except Exception as e:
                        self.logger.error(f"Error in analysis delay: {e}")
                        continue

                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
                    continue

            # Display cycle summary
            if trades_executed > 0:
                self.logger.info(f"✅ Trading cycle complete: {trades_executed} trades executed")
                print(f"   ✅ Executed {trades_executed} trade(s) this cycle")
            else:
                self.logger.info(" Trading cycle complete: No high-confidence opportunities found")
                print(f"   ℹ️  No trades executed (signals below {self.risk_limits['min_confidence']*100:.0f}% confidence)")

            # ═══════════════════════════════════════════════════════════════
            # 🔄 SHADOW POSITION MONITOR — check exits for virtual trades
            # Runs every cycle so shadow positions hit TP / SL / trailing
            # and closed trades feed back into the learning DB.
            # ═══════════════════════════════════════════════════════════════
            shadow_trader = self.systems.get('shadow_trader')
            if shadow_trader:
                try:
                    _shadow_closed = await shadow_trader.monitor_positions()
                    if _shadow_closed:
                        _sw = sum(1 for t in _shadow_closed if t.pnl and t.pnl > 0)
                        _sl = len(_shadow_closed) - _sw
                        _spnl = sum(t.pnl for t in _shadow_closed if t.pnl)
                        self.logger.info(
                            f"🔄 SHADOW MONITOR: Closed {len(_shadow_closed)} trades "
                            f"(W:{_sw}/L:{_sl}, PnL: ${_spnl:+.2f}) | "
                            f"Open: {sum(len(v) for v in shadow_trader.open_positions.values())} | "
                            f"Capital: ${shadow_trader.current_capital:,.0f}"
                        )
                except Exception as _sm_err:
                    self.logger.debug(f"Shadow monitor error: {_sm_err}")

            # ═══════════════════════════════════════════════════════════════
            # 🌍 WORLD MODEL UPDATE - Persist market state snapshot
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.world_model import get_world_model
                from core.hmm_regime_detector import get_regime_detector
                wm = get_world_model()

                # Regime update
                try:
                    regime_det = get_regime_detector()
                    regime_state = await regime_det.detect_regime('SPY')
                    if regime_state:
                        wm.update_regime(
                            regime=regime_state.regime_name,
                            confidence=regime_state.probability,
                            strategy_weights=regime_state.strategy_weights,
                        )
                except Exception:
                    pass

                # Portfolio update
                try:
                    account = self.broker.get_account() if hasattr(self, 'broker') and self.broker else None
                    if account:
                        equity = float(getattr(account, 'equity', 0) or 0)
                        cash = float(getattr(account, 'cash', 0) or 0)
                        positions = len(self.broker.list_positions()) if hasattr(self.broker, 'list_positions') else 0
                        exposure = (equity - cash) / equity if equity > 0 else 0
                        wm.update_portfolio(equity, cash, positions, exposure)
                except Exception:
                    pass

                wm.save()
            except Exception as wm_err:
                self.logger.debug(f"World model update failed: {wm_err}")

            # ═══════════════════════════════════════════════════════════════
            # 🛡️ GUARDIAN: Check stop-losses & update equity tracking
            # ═══════════════════════════════════════════════════════════════
            try:
                if hasattr(self, '_guardian') and self._guardian:
                    # Get current prices fro all positions
                    _g_prices = {}
                    try:
                        alpaca_b = self.systems.get('alpaca_broker')
                        if alpaca_b:
                            _g_pos = await alpaca_b.get_positions()
                            for _p in (_g_pos or []):
                                _g_prices[_p.symbol] = float(getattr(_p, 'current_price', 0))
                    except Exception:
                        pass

                    # Check stops
                    if _g_prices:
                        triggered = self._guardian.check_stops(_g_prices)
                        for stop in triggered:
                            self.logger.warning(f"⚠️ STOP-LOSS TRIGGERED: SELL {stop['symbol']} — {stop['reason']}")
                            try:
                                alpaca_b = self.systems.get('alpaca_broker')
                                if alpaca_b:
                                    from models import Order, OrderSide, OrderType
                                    stop_order = Order(
                                        symbol=stop['symbol'],
                                        quantity=abs(stop['quantity']),
                                        side=OrderSide.SELL,
                                        order_type=OrderType.MARKET,
                                        time_in_force='gtc',
                                    )
                                    _sl_result = await alpaca_b.submit_order(stop_order)
                                    self.logger.info(f"🛡️ Stop-loss SELL executed: {stop['symbol']}")

                                    # FIX: Record learning outcome so trade_history gets exit data
                                    try:
                                        _sl_entry = stop.get('entry_price', 0)
                                        _sl_exit = stop.get('current_price', _sl_entry)
                                        _sl_qty = abs(stop['quantity'])
                                        _sl_pnl = (_sl_exit - _sl_entry) * _sl_qty if _sl_entry else 0
                                        _sl_pnl_pct = ((_sl_exit / _sl_entry) - 1) if _sl_entry else 0
                                        await self._record_learning_outcome(
                                            symbol=stop['symbol'],
                                            entry_price=_sl_entry,
                                            exit_price=_sl_exit,
                                            quantity=_sl_qty,
                                            profit_loss=_sl_pnl,
                                            profit_pct=_sl_pnl_pct,
                                            exit_reason=f"GUARDIAN_STOP: {stop['reason']}",
                                            broker='Alpaca'
                                        )
                                    except Exception as _sl_learn_err:
                                        self.logger.debug(f"Guardian learning record failed: {_sl_learn_err}")
                            except Exception as sl_err:
                                self.logger.error(f"Stop-loss execution failed: {sl_err}")

                    # Update equity tracking (broker-aware)
                    try:
                        _g_combined = await self._get_combined_capital()
                        _g_eq = _g_combined.get('total_equity', 0)
                        _g_ba = _g_combined.get('brokers_active', 0)
                        if _g_eq > 0:
                            self._guardian.update_pnl(0, _g_eq, brokers_active=_g_ba)
                    except Exception:
                        pass

                    # Daily/weekly/monthly P/L resets
                    from datetime import datetime as _dt
                    _now = _dt.now()
                    if _now.hour == 9 and _now.minute < 5:
                        self._guardian.reset_daily_pnl()
                    if _now.weekday() == 0 and _now.hour == 9 and _now.minute < 5:
                        self._guardian.reset_weekly_pnl()
                    if _now.day == 1 and _now.hour == 9 and _now.minute < 5:
                        self._guardian.reset_monthly_pnl()
            except Exception as g_cyc_err:
                self.logger.debug(f"Guardian cycle check failed: {g_cyc_err}")


        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")

    async def _get_ai_target_and_stop(self, symbol: str, action: str, current_price: float,
                                       confidence: float, market_data: Dict[str, Any]) -> Dict[str, float]:
        """
        🧠 AI-DRIVEN TARGET PRICE & STOP LOSS CALCULATION
        Dynamically calculates optimal target and stop levels based on:
        - Symbol volatility (higher vol = wider targets)
        - Market regime (trending = wider targets, ranging = tighter)
        - AI confidence (higher confidence = more aggressive targets)
        - Support/resistance levels (from technical analysis)
        - Historical price patterns
        """
        try:
            # Base percentages
            base_target_pct = 0.08  # 8% base target
            base_stop_pct = 0.03   # 3% base stop

            target_adjustments = []
            stop_adjustments = []
            target_mult = 1.0
            stop_mult = 1.0

            # ═══════════════════════════════════════════════════════════════
            # 1. VOLATILITY-BASED ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            symbol_volatility = market_data.get('volatility', 0.02)

            # Get more accurate volatility from Yahoo Finance if available
            if self.systems.get('yahoo_finance'):
                try:
                    yf = self.systems['yahoo_finance']
                    if hasattr(yf, 'get_historical_data_async'):
                        hist = await yf.get_historical_data_async(symbol, timeframe='1Day', limit=20)
                    elif hasattr(yf, 'get_historical_data'):
                        hist = yf.get_historical_data(symbol, timeframe='1Day', limit=20)
                    else:
                        hist = None

                    if hist and len(hist) >= 10:
                        import numpy as np
                        closes = [bar.get('close', bar.get('Close', 0)) for bar in hist if bar]
                        if len(closes) >= 10:
                            returns = np.diff(closes) / closes[:-1]
                            symbol_volatility = np.std(returns) * np.sqrt(252)  # Annualized
                except Exception:
                    pass

            # Adjust based on volatility
            if symbol_volatility > 0.50:  # Very high volatility (>50% annualized)
                vol_target_mult = 1.5  # 50% wider targets
                vol_stop_mult = 1.8    # 80% wider stops
                target_adjustments.append(f"HighVol({symbol_volatility:.0%})=1.5x")
                stop_adjustments.append(f"HighVol=1.8x")
            elif symbol_volatility > 0.30:  # High volatility
                vol_target_mult = 1.3
                vol_stop_mult = 1.5
                target_adjustments.append(f"MedVol({symbol_volatility:.0%})=1.3x")
                stop_adjustments.append(f"MedVol=1.5x")
            elif symbol_volatility < 0.15:  # Low volatility
                vol_target_mult = 0.7
                vol_stop_mult = 0.8
                target_adjustments.append(f"LowVol({symbol_volatility:.0%})=0.7x")
                stop_adjustments.append(f"LowVol=0.8x")
            else:
                vol_target_mult = 1.0
                vol_stop_mult = 1.0

            target_mult *= vol_target_mult
            stop_mult *= vol_stop_mult

            # ═══════════════════════════════════════════════════════════════
            # 2. REGIME-BASED ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            regime = self.market_regime

            if regime == 'TRENDING':
                # Trending markets = let winners run
                regime_target_mult = 1.4  # 40% wider targets
                regime_stop_mult = 0.9    # Tighter stops (protect gains)
                target_adjustments.append("Trending=1.4x")
                stop_adjustments.append("Trending=0.9x")
            elif regime == 'VOLATILE':
                # Volatile markets = quick profits, wide stops
                regime_target_mult = 0.8  # Take profits quicker
                regime_stop_mult = 1.5    # Wider stops to avoid whipsaws
                target_adjustments.append("Volatile=0.8x")
                stop_adjustments.append("Volatile=1.5x")
            elif regime == 'RANGING':
                # Ranging markets = tight targets at range boundaries
                regime_target_mult = 0.7
                regime_stop_mult = 1.0
                target_adjustments.append("Ranging=0.7x")
            else:  # NORMAL
                regime_target_mult = 1.0
                regime_stop_mult = 1.0

            target_mult *= regime_target_mult
            stop_mult *= regime_stop_mult

            # ═══════════════════════════════════════════════════════════════
            # 3. CONFIDENCE-BASED ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            if confidence >= 0.75:
                # High confidence = more aggressive targets
                conf_target_mult = 1.3
                conf_stop_mult = 0.85  # Tighter stops (more conviction)
                target_adjustments.append(f"HighConf({confidence:.0%})=1.3x")
                stop_adjustments.append(f"HighConf=0.85x")
            elif confidence >= 0.60:
                conf_target_mult = 1.15
                conf_stop_mult = 0.95
                target_adjustments.append(f"MedConf({confidence:.0%})=1.15x")
            elif confidence < 0.45:
                # Low confidence = conservative targets
                conf_target_mult = 0.7
                conf_stop_mult = 1.2  # Wider stops (less conviction)
                target_adjustments.append(f"LowConf({confidence:.0%})=0.7x")
                stop_adjustments.append(f"LowConf=1.2x")
            else:
                conf_target_mult = 1.0
                conf_stop_mult = 1.0

            target_mult *= conf_target_mult
            stop_mult *= conf_stop_mult

            # ═══════════════════════════════════════════════════════════════
            # 4. SUPPORT/RESISTANCE FROM TECHNICAL ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            support_level = None
            resistance_level = None

            if self.systems.get('yahoo_finance'):
                try:
                    yf = self.systems['yahoo_finance']
                    if hasattr(yf, 'get_historical_data_async'):
                        hist = await yf.get_historical_data_async(symbol, timeframe='1Day', limit=30)
                    elif hasattr(yf, 'get_historical_data'):
                        hist = yf.get_historical_data(symbol, timeframe='1Day', limit=30)
                    else:
                        hist = None

                    if hist and len(hist) >= 20:
                        highs = [bar.get('high', bar.get('High', 0)) for bar in hist if bar]
                        lows = [bar.get('low', bar.get('Low', 0)) for bar in hist if bar]

                        if highs and lows:
                            # Simple support/resistance from recent highs/lows
                            resistance_level = max(highs[-20:])
                            support_level = min(lows[-20:])

                            # Adjust target to not exceed resistance (for BUY)
                            if action == 'BUY' and resistance_level:
                                resistance_pct = (resistance_level - current_price) / current_price
                                if resistance_pct > 0 and resistance_pct < base_target_pct * target_mult:
                                    # Cap target at resistance
                                    target_mult = resistance_pct / base_target_pct * 0.95  # 95% of resistance
                                    target_adjustments.append(f"Resistance@{resistance_level:.2f}")

                            # Adjust stop to not exceed support (for BUY)
                            if action == 'BUY' and support_level:
                                support_pct = (current_price - support_level) / current_price
                                if support_pct > 0 and support_pct < base_stop_pct * stop_mult:
                                    # Set stop just below support
                                    stop_mult = support_pct / base_stop_pct * 1.05  # 5% below support
                                    stop_adjustments.append(f"Support@{support_level:.2f}")
                except Exception as e:
                    self.logger.debug(f"Support/resistance calculation failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 5. ASSET CLASS ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            if '/' in symbol:  # Crypto
                # Crypto is more volatile - wider targets
                target_mult *= 1.5
                stop_mult *= 1.5
                target_adjustments.append("Crypto=1.5x")
                stop_adjustments.append("Crypto=1.5x")
            elif symbol in ['SPY', 'QQQ', 'IWM', 'DIA']:  # ETFs
                # ETFs are less volatile - tighter targets
                target_mult *= 0.6
                stop_mult *= 0.7
                target_adjustments.append("ETF=0.6x")
                stop_adjustments.append("ETF=0.7x")

            # ═══════════════════════════════════════════════════════════════
            # CALCULATE FINAL TARGET AND STOP
            # ═══════════════════════════════════════════════════════════════
            # Apply bounds
            target_mult = max(0.3, min(2.5, target_mult))  # 30% to 250% of base
            stop_mult = max(0.5, min(2.5, stop_mult))      # 50% to 250% of base

            final_target_pct = base_target_pct * target_mult
            final_stop_pct = base_stop_pct * stop_mult

            # Cap at reasonable limits
            final_target_pct = min(0.20, final_target_pct)  # Max 20% target
            final_stop_pct = min(0.10, final_stop_pct)      # Max 10% stop

            # Calculate actual prices
            if action == 'BUY':
                target_price = current_price * (1 + final_target_pct)
                stop_loss = current_price * (1 - final_stop_pct)
            else:  # SELL (short)
                target_price = current_price * (1 - final_target_pct)
                stop_loss = current_price * (1 + final_stop_pct)

            self.logger.info(f"🎯 AI TARGET/STOP for {symbol}:")
            self.logger.info(f"   Target: ${target_price:.2f} ({final_target_pct*100:+.1f}%) | Adjustments: {', '.join(target_adjustments[:3])}")
            self.logger.info(f"   Stop: ${stop_loss:.2f} ({-final_stop_pct*100:.1f}%) | Adjustments: {', '.join(stop_adjustments[:3])}")

            return {
                'target_price': target_price,
                'stop_loss': stop_loss,
                'target_pct': final_target_pct,
                'stop_pct': final_stop_pct,
                'target_adjustments': target_adjustments,
                'stop_adjustments': stop_adjustments,
                'support_level': support_level,
                'resistance_level': resistance_level
            }

        except Exception as e:
            self.logger.error(f"AI target/stop calculation failed: {e}")
            # Fallback to fixed percentages
            if action == 'BUY':
                return {
                    'target_price': current_price * 1.08,
                    'stop_loss': current_price * 0.97,
                    'target_pct': 0.08,
                    'stop_pct': 0.03
                }
            else:
                return {
                    'target_price': current_price * 0.92,
                    'stop_loss': current_price * 1.03,
                    'target_pct': 0.08,
                    'stop_pct': 0.03
                }

    async def get_ai_trading_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        🚀 REVOLUTIONARY AI TRADING SIGNAL GENERATOR
        Combines ALL AI components for intelligent, autonomous trading decisions:
        - Market Oracle Engine (predictions & insights)
        - Quantum Trading Engine (arbitrage & optimization)
        - AI Consciousness Engine (market awareness)
        - Hierarchical Agent Coordinator (17 agents + 3 supervisors)
        - GPT-OSS/CPT-OSS (natural language analysis)
        - Real-World Data Orchestrator (1000+ intelligence sources)
        """
        try:
            # Get market data first
            market_data = await self.fetch_market_data(symbol)
            if not market_data:
                self.logger.debug(f"No market data for {symbol}")
                return None

            current_price = market_data.get('price', 0)
            if current_price <= 0:
                return None

            # ═══════════════════════════════════════════════════════════════
            # 🎯 LEARNING FEEDBACK LOOP - Load AI System Weights
            # ═══════════════════════════════════════════════════════════════
            # Refresh weights periodically (hourly) from AI Attribution Tracker
            # Top performers get higher weights (up to 2.0x), poor performers lower (0.5x)
            await self._refresh_ai_system_weights()

            # Track which AI components contributed
            ai_contributions = []
            signal_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            confidence_scores = []
            reasoning_parts = []

            # ═══════════════════════════════════════════════════════════════
            # 🔮 MARKET ORACLE ENGINE - Predictions & Divine Insights
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('market_oracle'):
                try:
                    oracle = self.systems['market_oracle']
                    if hasattr(oracle, 'generate_prediction'):
                        prediction = await oracle.generate_prediction(symbol, '24h')
                        if prediction:
                            oracle_action = 'BUY' if prediction.predicted_change_percent > 1.0 else \
                                          'SELL' if prediction.predicted_change_percent < -1.0 else 'HOLD'
                            # 🎯 LEARNING: Apply learned weight to Oracle
                            learned_weight = self._get_ai_weight('Oracle')
                            signal_votes[oracle_action] += prediction.confidence * 1.2 * learned_weight
                            confidence_scores.append(prediction.confidence)
                            reasoning_parts.append(f"Oracle: {prediction.predicted_change_percent:+.1f}% predicted")
                            ai_contributions.append('Oracle')
                            self.logger.info(f"🔮 Oracle prediction for {symbol}: {prediction.predicted_change_percent:+.1f}%")
                except Exception as e:
                    self.logger.debug(f"Oracle prediction failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # ⚛️ QUANTUM TRADING ENGINE - DISABLED (2026-03-07 AUDIT)
            # Reason: 10.1% win rate, -$781.90 total P/L across 24,814 signals.
            # Actively harmful to signal quality. Will re-enable only after
            # retraining produces >40% win rate on shadow trades.
            # ═══════════════════════════════════════════════════════════════
            # QUANTUM VOTER DISABLED — see audit report for data

            # ═══════════════════════════════════════════════════════════════
            # 🧠 AI CONSCIOUSNESS ENGINE - Market Awareness
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('ai_consciousness'):
                try:
                    consciousness = self.systems['ai_consciousness']
                    if hasattr(consciousness, 'analyze_market_awareness'):
                        awareness = await consciousness.analyze_market_awareness(symbol, market_data)
                        if awareness:
                            consciousness_action = awareness.get('recommended_action', 'HOLD')
                            # 🎯 LEARNING: Apply learned weight to Consciousness
                            learned_weight = self._get_ai_weight('Consciousness')
                            signal_votes[consciousness_action] += awareness.get('confidence', 0.6) * 1.1 * learned_weight
                            confidence_scores.append(awareness.get('confidence', 0.6))
                            reasoning_parts.append(f"Consciousness: {awareness.get('market_state', 'analyzing')}")
                            ai_contributions.append('Consciousness')
                except Exception as e:
                    self.logger.debug(f"Consciousness analysis failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🤖 HIERARCHICAL AGENT COORDINATOR - DISABLED (2026-03-07 AUDIT)
            # Reason: ALL Agents(N) variants show 0% win rate across 127 tracked
            # signals. Every single Agents trade lost money. The coordinator
            # adds pure noise to voting. Will re-enable after retraining.
            # ═══════════════════════════════════════════════════════════════
            # AGENT COORDINATOR VOTER DISABLED — see audit report for data

            # ═══════════════════════════════════════════════════════════════
            # 🌍 REAL-WORLD DATA ORCHESTRATOR - 1000+ Intelligence Sources
            # ═══════════════════════════════════════════════════════════════
            orchestrator = self.systems.get('data_orchestrator') or self.systems.get('real_world_data')
            if orchestrator:
                try:
                    if hasattr(orchestrator, 'get_comprehensive_intelligence'):
                        intel = await orchestrator.get_comprehensive_intelligence(symbol)
                        if intel:
                            sentiment = intel.get('overall_sentiment', 0)
                            sentiment_action = 'BUY' if sentiment > 0.2 else 'SELL' if sentiment < -0.2 else 'HOLD'
                            # 🎯 LEARNING: Apply learned weight to DataIntel
                            learned_weight = self._get_ai_weight('DataIntel')
                            signal_votes[sentiment_action] += abs(sentiment) * 0.8 * learned_weight
                            confidence_scores.append(abs(sentiment))
                            reasoning_parts.append(f"Intelligence: sentiment={sentiment:.2f}")
                            ai_contributions.append('DataIntel')
                            self.logger.info(f"🌍 Data intelligence for {symbol}: sentiment={sentiment:.2f}")
                except Exception as e:
                    self.logger.debug(f"Data orchestrator failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🧬 GPT-OSS / CPT-OSS - Natural Language Analysis
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('gpt_oss'):
                try:
                    gpt_oss = self.systems['gpt_oss']
                    if hasattr(gpt_oss, 'generate_trading_signal'):
                        result = await gpt_oss.generate_trading_signal(symbol, market_data)
                        if result and result.get('confidence', 0) > 0.5:
                            gpt_action = result.get('action', 'HOLD')
                            # 🎯 LEARNING: Apply learned weight to CPT-OSS
                            learned_weight = self._get_ai_weight('CPT-OSS')
                            signal_votes[gpt_action] += result.get('confidence', 0.5) * 1.3 * learned_weight
                            confidence_scores.append(result.get('confidence', 0.5))
                            reasoning_parts.append(f"CPT-OSS: {result.get('reasoning', 'AI analysis')[:30]}")
                            ai_contributions.append('CPT-OSS')
                            self.logger.info(f"🧬 CPT-OSS signal for {symbol}: {gpt_action}")
                except Exception as e:
                    self.logger.debug(f"GPT-OSS failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 👁️ CHART VISION ANALYSIS - Visual Pattern Recognition (llava)
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('chart_vision'):
                try:
                    import time as _tv
                    _vision_t0 = _tv.monotonic()
                    chart_vision = self.systems['chart_vision']

                    # --- Check cache first (fast path) ---
                    cached_result = chart_vision.get_cached(symbol)
                    if cached_result:
                        v_action = cached_result.get('recommendation', 'HOLD').upper()
                        if v_action not in ('BUY', 'SELL', 'HOLD'):
                            v_action = 'HOLD'
                        learned_weight = self._get_ai_weight('ChartVision')
                        signal_votes[v_action] += cached_result.get('confidence', 0.5) * 1.5 * learned_weight
                        confidence_scores.append(cached_result.get('confidence', 0.5))
                        patterns_str = ', '.join(cached_result.get('patterns', [])[:3]) or cached_result.get('trend', 'vision')
                        reasoning_parts.append(f"ChartVision: {patterns_str[:30]}")
                        ai_contributions.append('ChartVision')
                        self.logger.info(f"👁️ Chart Vision CACHED for {symbol}: {v_action} ({cached_result.get('trend', '?')})")
                    else:
                        # --- Build DataFrame from market_data ---
                        vision_df = None
                        if isinstance(market_data, dict) and 'prices' in market_data:
                            vision_df = pd.DataFrame(market_data['prices'])
                        elif isinstance(market_data, pd.DataFrame):
                            vision_df = market_data

                        # Fetch broker candles if needed
                        if vision_df is None or len(vision_df) < 10:
                            try:
                                _vb = self.systems.get('alpaca_broker') or self.systems.get('ib_broker')
                                if _vb:
                                    _vh = await _vb.get_historical_data(symbol, timeframe='1D', limit=60)
                                    if _vh and len(_vh) >= 10:
                                        vision_df = pd.DataFrame(_vh)
                                        self.logger.info(f"👁️ Vision: fetched {len(_vh)} broker candles for {symbol}")
                            except Exception as _vbe:
                                self.logger.debug(f"👁️ Vision: broker candle fetch failed for {symbol}: {_vbe}")

                        # Normalise column names so mplfinance can render
                        if vision_df is not None and len(vision_df) >= 10:
                            col_lower = {c: c.lower() for c in vision_df.columns}
                            need = {'open', 'high', 'low', 'close'}
                            has_ohlc = need.issubset(set(col_lower.values()))
                            if not has_ohlc:
                                # Try common broker column aliases
                                rename_map = {}
                                for c in vision_df.columns:
                                    cl = c.lower()
                                    if cl in ('o', 'open'):
                                        rename_map[c] = 'Open'
                                    elif cl in ('h', 'high'):
                                        rename_map[c] = 'High'
                                    elif cl in ('l', 'low'):
                                        rename_map[c] = 'Low'
                                    elif cl in ('c', 'close'):
                                        rename_map[c] = 'Close'
                                    elif cl in ('v', 'volume', 'vol'):
                                        rename_map[c] = 'Volume'
                                    elif cl in ('t', 'timestamp', 'time', 'date', 'datetime'):
                                        rename_map[c] = 'Date'
                                if rename_map:
                                    vision_df = vision_df.rename(columns=rename_map)

                        # --- Launch vision as a background task so it doesn't block ---
                        async def _run_vision(sym, df, cv):
                            try:
                                if df is not None and len(df) >= 10:
                                    return await cv.analyze_chart(sym, df)
                                else:
                                    _yf_sym = sym.replace('/', '-') if '/' in sym else sym
                                    return await cv.analyze_symbol(_yf_sym, period='1mo')
                            except Exception as e:
                                self.logger.debug(f"👁️ Vision background failed for {sym}: {e}")
                                return None

                        # Fire-and-forget: schedule the vision task, collect results next cycle
                        _vision_task_key = f"_vision_task_{symbol}"
                        prev_task = getattr(self, '_vision_bg_tasks', {}).get(symbol)
                        if prev_task and not prev_task.done():
                            # Previous analysis still running — don't stack another
                            self.logger.debug(f"👁️ Vision: analysis still pending for {symbol}")
                        else:
                            if not hasattr(self, '_vision_bg_tasks'):
                                self._vision_bg_tasks = {}
                            task = asyncio.create_task(_run_vision(symbol, vision_df, chart_vision))
                            self._vision_bg_tasks[symbol] = task

                            # If we can await quickly (<2s), grab the result now
                            try:
                                vision_result = await asyncio.wait_for(asyncio.shield(task), timeout=2.0)
                            except asyncio.TimeoutError:
                                # Will be picked up next cycle via cache
                                self.logger.info(f"👁️ Vision: running in background for {symbol} (will cache)")
                                vision_result = None

                            if vision_result and vision_result.get('confidence', 0) > 0.45:
                                v_action = vision_result.get('recommendation', 'HOLD').upper()
                                if v_action not in ('BUY', 'SELL', 'HOLD'):
                                    v_action = 'HOLD'
                                _vision_elapsed = _tv.monotonic() - _vision_t0
                                learned_weight = self._get_ai_weight('ChartVision')
                                signal_votes[v_action] += vision_result.get('confidence', 0.5) * 1.5 * learned_weight
                                confidence_scores.append(vision_result.get('confidence', 0.5))
                                patterns_str = ', '.join(vision_result.get('patterns', [])[:3]) or vision_result.get('trend', 'vision')
                                reasoning_parts.append(f"ChartVision: {patterns_str[:30]}")
                                ai_contributions.append('ChartVision')
                                self.logger.info(f"👁️ Chart Vision for {symbol}: {v_action} ({vision_result.get('trend', '?')}) [{_vision_elapsed:.1f}s]")
                except Exception as e:
                    self.logger.warning(f"👁️ Chart vision FAILED for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # �🔍 MARKET INTELLIGENCE AGENTS - Gap Detection & Opportunity Scanning
            # ═══════════════════════════════════════════════════════════════
            # Gap Detection Agent
            if self.systems.get('gap_detector'):
                try:
                    gap_agent = self.systems['gap_detector']
                    gaps = await gap_agent.scan_for_gaps([symbol])
                    if gaps:
                        gap = gaps[0]
                        gap_action = 'BUY' if gap.direction == 'up' else 'SELL'
                        # 🎯 LEARNING: Apply learned weight to GapDetector
                        learned_weight = self._get_ai_weight('GapDetector')
                        signal_votes[gap_action] += gap.opportunity_score * 1.1 * learned_weight
                        confidence_scores.append(gap.opportunity_score)
                        reasoning_parts.append(f"GapDetect: {gap.gap_percent:.1%} {gap.direction}")
                        ai_contributions.append('GapDetector')
                        self.logger.info(f"🔍 Gap detected for {symbol}: {gap.gap_percent:.1%} {gap.direction}")
                except Exception as e:
                    self.logger.debug(f"Gap detection failed for {symbol}: {e}")

            # Opportunity Scanner Agent
            if self.systems.get('opportunity_scanner'):
                try:
                    scanner = self.systems['opportunity_scanner']
                    opportunities = await scanner.scan_all_opportunities([symbol])
                    if opportunities:
                        best_opp = opportunities[0]
                        # 🎯 LEARNING: Apply learned weight to OpportunityScanner
                        learned_weight = self._get_ai_weight(f'OpportunityScanner({best_opp.opportunity_type.value})')
                        signal_votes['BUY'] += best_opp.score * best_opp.confidence * 1.2 * learned_weight
                        confidence_scores.append(best_opp.confidence)
                        reasoning_parts.append(f"OpportScan: {best_opp.opportunity_type.value} ({best_opp.score:.2f})")
                        ai_contributions.append(f'OpportunityScanner({best_opp.opportunity_type.value})')
                        self.logger.info(f"🎯 Opportunity detected for {symbol}: {best_opp.opportunity_type.value}")
                except Exception as e:
                    self.logger.debug(f"Opportunity scanning failed for {symbol}: {e}")

            # Market Research Agent (market regime & sentiment)
            # AUDIT BOOST: Best AI performer — 46% WR, +$369 P/L. Weight increased 2026-03-07.
            if self.systems.get('market_researcher'):
                try:
                    researcher = self.systems['market_researcher']
                    intel = await researcher.generate_market_intelligence([symbol])
                    if intel:
                        # 🎯 LEARNING: Apply learned weight to MarketResearcher
                        learned_weight = self._get_ai_weight('MarketResearcher')

                        # Use market regime and sentiment to influence signal
                        # AUDIT BOOST: multiplier raised from implicit 1.0 to 1.4x (best performer)
                        mr_boost = 1.4
                        regime_boost = 0
                        if intel.market_regime == 'TRENDING_BULL':
                            regime_boost = 0.3
                            signal_votes['BUY'] += regime_boost * mr_boost * learned_weight
                        elif intel.market_regime == 'TRENDING_BEAR':
                            regime_boost = 0.3
                            signal_votes['SELL'] += regime_boost * mr_boost * learned_weight

                        # Sentiment influence
                        if intel.sentiment_score > 0.3:
                            signal_votes['BUY'] += intel.sentiment_score * 0.5 * mr_boost * learned_weight
                        elif intel.sentiment_score < -0.3:
                            signal_votes['SELL'] += abs(intel.sentiment_score) * 0.5 * mr_boost * learned_weight

                        confidence_scores.append(abs(intel.sentiment_score))
                        reasoning_parts.append(f"MarketIntel: {intel.market_regime}, sentiment={intel.sentiment_score:.2f}")
                        ai_contributions.append('MarketResearcher')
                        self.logger.info(f"📊 Market intel for {symbol}: {intel.market_regime}, sentiment={intel.sentiment_score:.2f}")
                except Exception as e:
                    self.logger.debug(f"Market research failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🧠 HRM (Hierarchical Reasoning Model) - 27M-Param Deep Reasoning
            # ═══════════════════════════════════════════════════════════════
            if HRM_AVAILABLE:
                try:
                    if self._hrm_adapter is None:
                        self._hrm_adapter = get_official_hrm_adapter(
                            checkpoint_dir="hrm_checkpoints",
                            device="cpu",
                            use_ensemble=True
                        )
                    if self._hrm_adapter:
                        # Build proper HRMReasoningContext — fixes AttributeError from plain dict
                        from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
                        hrm_context = HRMReasoningContext(
                            market_data={
                                "symbol": symbol,
                                "price": current_price,
                                "change_percent": market_data.get("change_percent", 0),
                                "volume": market_data.get("volume", 0),
                                "rsi": market_data.get("rsi", 50),
                                "volatility": market_data.get("volatility", 0.01),
                                "momentum": market_data.get("momentum", 0),
                            },
                            user_profile={"role": "autonomous_trader"},
                            trading_history=[],
                            current_portfolio={
                                "positions": getattr(self, "positions", {}),
                                "cash": getattr(self, "portfolio_value", 1000),
                                "total_value": getattr(self, "portfolio_value", 1000),
                            },
                            risk_preferences={
                                "max_position_size": 0.15,
                                "stop_loss": 0.05,
                                "take_profit": 0.09,
                            },
                            # ARC checkpoint handles abstract pattern reasoning;
                            # swap to MAZE_LEVEL for path/sequence tasks once fine-tuned
                            reasoning_level=HRMReasoningLevel.ARC_LEVEL,
                        )
                        # HRM reason() is sync — run in threadpool
                        hrm_result = await asyncio.get_event_loop().run_in_executor(
                            None, self._hrm_adapter.reason, hrm_context
                        )
                        if hrm_result and hasattr(hrm_result, 'action'):
                            hrm_action = getattr(hrm_result, 'action', 'HOLD').upper()
                            hrm_conf = getattr(hrm_result, 'confidence', 0.5)
                        elif isinstance(hrm_result, dict):
                            hrm_action = hrm_result.get('action', hrm_result.get('recommendation', 'HOLD')).upper()
                            hrm_conf = hrm_result.get('confidence', 0.5)
                        else:
                            hrm_action = 'HOLD'
                            hrm_conf = 0.5
                        if hrm_action in ('BUY', 'SELL', 'HOLD') and hrm_conf > 0.4:
                            # Weight is 0.3 (honest placeholder) until market-sequence
                            # fine-tuning in Phase B replaces puzzle-game weights
                            learned_weight = self._get_ai_weight('HRM')
                            hrm_weight = 0.3 * learned_weight
                            signal_votes[hrm_action] += hrm_conf * hrm_weight
                            confidence_scores.append(hrm_conf)
                            reasoning_parts.append(f"HRM: {hrm_action} ({hrm_conf:.0%})")
                            ai_contributions.append('HRM')
                            self.logger.info(
                                f"HRM signal for {symbol}: {hrm_action} "
                                f"conf={hrm_conf:.0%} weight={hrm_weight:.2f} "
                                f"vote_contribution={hrm_conf * hrm_weight:.3f}"
                            )
                except Exception as e:
                    self.logger.warning(f"HRM reasoning failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🔬 DEEPCONF (Meta Research Confidence Calibration)
            # ═══════════════════════════════════════════════════════════════
            if DEEPCONF_AVAILABLE:
                try:
                    dc_result = await deepconf_trading_decision(
                        question=f"Should I {('buy' if market_data.get('change_percent', 0) < 0 else 'sell')} {symbol} at ${current_price:.2f}?",
                        market_data={
                            "symbol": symbol,
                            "price": current_price,
                            "change_pct": market_data.get("change_percent", 0),
                            "volume": market_data.get("volume", 0),
                        },
                        risk_params={"max_loss_pct": self.risk_limits.get("stop_loss_pct", 0.015)},
                        mode="quick"
                    )
                    if dc_result and dc_result.success:
                        # Parse DeepConf answer
                        dc_answer = dc_result.final_answer.upper() if dc_result.final_answer else ""
                        dc_conf = dc_result.confidence or 0.5
                        if "BUY" in dc_answer or "LONG" in dc_answer:
                            dc_action = "BUY"
                        elif "SELL" in dc_answer or "SHORT" in dc_answer:
                            dc_action = "SELL"
                        else:
                            dc_action = "HOLD"
                        if dc_conf > 0.45:
                            learned_weight = self._get_ai_weight('DeepConf')
                            # Blend: 70% DeepConf native confidence, 30% vote weight
                            blended_weight = dc_conf * 0.7 + 0.3
                            signal_votes[dc_action] += blended_weight * 1.0 * learned_weight
                            confidence_scores.append(dc_conf)
                            reasoning_parts.append(f"DeepConf: {dc_action} ({dc_conf:.0%})")
                            ai_contributions.append('DeepConf')
                            self.logger.info(f"🔬 DeepConf signal for {symbol}: {dc_action} ({dc_conf:.0%})")
                except Exception as e:
                    self.logger.debug(f"DeepConf reasoning failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🌐 THINKMESH (Multi-Backend Enhanced Reasoning)
            # ═══════════════════════════════════════════════════════════════
            if THINKMESH_AVAILABLE:
                try:
                    if self._thinkmesh_adapter is None:
                        self._thinkmesh_adapter = ThinkMeshAdapter(enabled=True)
                    if self._thinkmesh_adapter and self._thinkmesh_adapter.is_available():
                        # Build required ThinkMeshConfig (was missing — caused TypeError)
                        from core.reasoning.thinkmesh_adapter import ThinkMeshConfig, ReasoningStrategy, BackendType
                        _tm_config = ThinkMeshConfig(
                            backend=BackendType.OPENAI,
                            model_name="gpt-4o-mini",
                            strategy=ReasoningStrategy.SELF_CONSISTENCY,
                            parallel_paths=4,
                            wall_clock_timeout_s=10,
                            max_total_tokens=1000,
                            require_final_answer=True,
                            custom_verifier_pattern=r"(BUY|SELL|HOLD)",
                        )
                        _tm_prompt = (
                            f"Analyze this trading signal and respond with exactly one word — "
                            f"BUY, SELL, or HOLD.\n"
                            f"Symbol: {symbol}  Price: ${current_price:.2f}  "
                            f"Change: {market_data.get('change_percent', 0):.2f}%  "
                            f"RSI: {market_data.get('rsi', 50):.0f}  "
                            f"Volume: {market_data.get('volume', 0):,.0f}"
                        )
                        tm_result = await self._thinkmesh_adapter.reason(
                            _tm_prompt, _tm_config,
                            context={"symbol": symbol, "price": current_price}
                        )
                        if tm_result:
                            # Fix: result field is 'content', not 'answer'
                            tm_text = ""
                            tm_conf = 0.5
                            if hasattr(tm_result, 'content'):
                                tm_text = (tm_result.content or "").upper()
                                tm_conf = getattr(tm_result, 'confidence', 0.5)
                            elif isinstance(tm_result, dict):
                                tm_text = str(tm_result.get('content', tm_result.get('answer', ''))).upper()
                                tm_conf = tm_result.get('confidence', 0.5)

                            if "BUY" in tm_text or "LONG" in tm_text or "BULLISH" in tm_text:
                                tm_action = "BUY"
                            elif "SELL" in tm_text or "SHORT" in tm_text or "BEARISH" in tm_text:
                                tm_action = "SELL"
                            else:
                                tm_action = "HOLD"

                            if tm_conf > 0.40:
                                learned_weight = self._get_ai_weight('ThinkMesh')
                                signal_votes[tm_action] += tm_conf * 1.0 * learned_weight
                                confidence_scores.append(tm_conf)
                                reasoning_parts.append(f"ThinkMesh: {tm_action} ({tm_conf:.0%})")
                                ai_contributions.append('ThinkMesh')
                                backend = getattr(tm_result, 'backend_used', 'unknown')
                                self.logger.info(
                                    f"ThinkMesh signal for {symbol}: {tm_action} "
                                    f"conf={tm_conf:.0%} backend={backend}"
                                )
                except Exception as e:
                    self.logger.warning(f"ThinkMesh reasoning failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📈 PRETRAINED ML (sklearn GradientBoosting/RandomForest)
            # ═══════════════════════════════════════════════════════════════
            if PRETRAINED_ML_AVAILABLE:
                try:
                    symbol_upper = symbol.upper().replace("/", "-").replace("USD", "").rstrip("-")
                    if symbol_upper not in self._pretrained_models:
                        import pickle
                        model_path = Path(f"models_pretrained/{symbol_upper}_direction_model.pkl")
                        scaler_path = Path(f"models_pretrained/{symbol_upper}_direction_scaler.pkl")
                        if model_path.exists() and scaler_path.exists():
                            with open(model_path, "rb") as f:
                                _ml_model = pickle.load(f)
                            with open(scaler_path, "rb") as f:
                                _ml_scaler = pickle.load(f)
                            self._pretrained_models[symbol_upper] = (_ml_model, _ml_scaler)
                        else:
                            self._pretrained_models[symbol_upper] = None

                    ml_pair = self._pretrained_models.get(symbol_upper)
                    if ml_pair:
                        import numpy as np
                        ml_model, ml_scaler = ml_pair

                        # ──── REAL FEATURES (replaces placeholder values) ────
                        # Uses MLFeatureEngine to compute the same 11 features
                        # used during training: RSI, MACD, macd_signal, bb_upper,
                        # bb_lower, sma_20, ema_12, volume_ratio, daily_return,
                        # price_vs_sma20, volatility.
                        from core.ml_feature_engine import get_feature_engine
                        _feat_engine = get_feature_engine()
                        _ml_features = await _feat_engine.compute_features(
                            symbol, current_price=current_price, market_data=market_data
                        )
                        if _ml_features is not None:
                            features = _ml_features.reshape(1, -1)  # shape (1, 11)
                        else:
                            # Fallback: use market_data hints (still better than all-zeros)
                            _change = market_data.get('change_percent', 0)
                            _vol = market_data.get('volume', 1)
                            _avg_vol = market_data.get('avg_volume', _vol) or _vol
                            features = np.array([[
                                50.0, 0.0, 0.0, 0.0, current_price,
                                current_price, current_price, current_price,
                                _vol / _avg_vol if _avg_vol > 0 else 1.0,
                                _change, 0.0,
                            ]])
                            self.logger.warning(f"⚠️ ML features fallback for {symbol} — yfinance data unavailable")

                        features_scaled = ml_scaler.transform(features)
                        ml_pred = ml_model.predict(features_scaled)[0]
                        # Prediction: 1=BUY, -1=SELL, 0=HOLD
                        if hasattr(ml_model, 'predict_proba'):
                            ml_proba = ml_model.predict_proba(features_scaled)[0]
                            ml_conf = float(max(ml_proba))
                        else:
                            ml_conf = 0.60

                        if ml_pred == 1:
                            ml_action = "BUY"
                        elif ml_pred == -1:
                            ml_action = "SELL"
                        else:
                            ml_action = "HOLD"

                        if ml_conf > 0.45:
                            learned_weight = self._get_ai_weight('PretrainedML')
                            signal_votes[ml_action] += ml_conf * 0.8 * learned_weight
                            confidence_scores.append(ml_conf)
                            reasoning_parts.append(f"ML({symbol_upper}): {ml_action} ({ml_conf:.0%})")
                            ai_contributions.append(f'PretrainedML({symbol_upper})')
                            self.logger.info(f"📈 Pretrained ML for {symbol}: {ml_action} ({ml_conf:.0%})")
                except Exception as e:
                    self.logger.debug(f"Pretrained ML failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🤖 RL TRADING AGENT - PyTorch Actor-Critic (weight 0.9x)
            # ═══════════════════════════════════════════════════════════════
            if RL_AGENT_AVAILABLE:
                try:
                    # Lazy-load RL agent
                    if self._rl_agent is None:
                        _rl_model_path = Path("trained_models/rl_trading_agent.pt")
                        if _rl_model_path.exists():
                            _rl_instance = TradingRLAgent(state_dim=50, action_dim=3, hidden_dim=128)
                            _rl_ckpt = torch.load(str(_rl_model_path), map_location='cpu', weights_only=False)
                            if isinstance(_rl_ckpt, dict) and 'policy_state_dict' in _rl_ckpt:
                                _rl_instance.policy_network.load_state_dict(_rl_ckpt['policy_state_dict'])
                                _rl_instance.value_network.load_state_dict(_rl_ckpt['value_state_dict'])
                                # Move to GPU (DirectML) if available
                                try:
                                    from gpu_detector import get_device_for_inference
                                    _rl_device = get_device_for_inference()
                                    _rl_instance.policy_network.to(_rl_device)
                                    _rl_instance.value_network.to(_rl_device)
                                except Exception:
                                    _rl_device = 'cpu'
                                _rl_instance.eval()
                                self._rl_agent = _rl_instance
                                self._rl_system = ReinforcementLearningTrading(state_dim=50)
                                self._rl_system.agent = self._rl_agent
                                self.logger.info(f"🤖 RL Agent loaded: {sum(p.numel() for p in self._rl_agent.parameters())} params")
                            elif hasattr(_rl_ckpt, 'eval'):
                                _rl_ckpt.eval()
                                self._rl_agent = _rl_ckpt
                                self._rl_system = ReinforcementLearningTrading(state_dim=50)
                                self._rl_system.agent = self._rl_agent

                    if self._rl_agent is not None and self._rl_system is not None:
                        # Build market state for RL
                        _rl_market = {
                            'price': current_price,
                            'volume': market_data.get('volume', 0),
                            'indicators': {
                                'rsi': market_data.get('rsi', 50),
                                'macd': market_data.get('macd', 0),
                                'volatility': market_data.get('volatility', 0.01),
                            }
                        }
                        _rl_portfolio = {
                            'total_value': getattr(self, 'portfolio_value', 1000),
                            'positions': getattr(self, 'positions', {}),
                        }
                        _rl_decision = self._rl_system.make_rl_decision(_rl_market, _rl_portfolio, {'symbol': symbol})
                        rl_action = _rl_decision.get('action', 'HOLD')
                        rl_conf = _rl_decision.get('confidence', 0.0)

                        if rl_conf > 0.45 and rl_action != 'HOLD':
                            learned_weight = self._get_ai_weight('RLAgent')
                            signal_votes[rl_action] += rl_conf * 0.9 * learned_weight
                            confidence_scores.append(rl_conf)
                            reasoning_parts.append(f"RLAgent: {rl_action} ({rl_conf:.0%})")
                            ai_contributions.append('RLAgent')
                            self.logger.info(f"🤖 RL Agent signal for {symbol}: {rl_action} ({rl_conf:.0%})")
                except Exception as e:
                    self.logger.debug(f"RL Agent failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🧠 OPENAI INTELLIGENCE - GPT-4 Trading Signals (weight 1.2x)
            # ═══════════════════════════════════════════════════════════════
            if OPENAI_INTELLIGENCE_AVAILABLE:
                try:
                    # Lazy-load OpenAI Intelligence
                    if self._openai_intelligence is None:
                        self._openai_intelligence = self.systems.get('ai_intelligence')
                        if self._openai_intelligence is None:
                            self._openai_intelligence = OpenAITradingIntelligence()

                    if self._openai_intelligence and self._openai_intelligence.is_available():
                        oai_result = await self._openai_intelligence.generate_trading_signal(symbol, market_data)
                        if oai_result and oai_result.get('action') and oai_result.get('confidence', 0) > 0.50:
                            oai_action = oai_result['action'].upper()
                            oai_conf = float(oai_result['confidence'])
                            if oai_action in ('BUY', 'SELL'):
                                learned_weight = self._get_ai_weight('OpenAI_GPT4')
                                signal_votes[oai_action] += oai_conf * 1.2 * learned_weight
                                confidence_scores.append(oai_conf)
                                _oai_reasoning = oai_result.get('reasoning', '')[:60]
                                reasoning_parts.append(f"GPT4: {oai_action} ({oai_conf:.0%}) {_oai_reasoning}")
                                ai_contributions.append('OpenAI_GPT4')
                                self.logger.info(f"🧠 OpenAI GPT-4 signal for {symbol}: {oai_action} ({oai_conf:.0%})")
                except Exception as e:
                    self.logger.debug(f"OpenAI Intelligence failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📊 TECHNICAL ANALYSIS FALLBACK - Real Indicators
            # ═══════════════════════════════════════════════════════════════
            # Always run technical analysis as baseline (reduced weight due to underperformance)
            try:
                tech_signal = await self._calculate_technical_indicators(symbol, market_data)
                if tech_signal:
                    # 🎯 LEARNING: Apply learned weight to Technical (underperforming in backtest)
                    learned_weight = self._get_ai_weight('Technical')
                    signal_votes[tech_signal['action']] += tech_signal['confidence'] * 0.5 * learned_weight
                    confidence_scores.append(tech_signal['confidence'])
                    reasoning_parts.append(f"Technical: {tech_signal['indicators']}")
                    ai_contributions.append('Technical')
            except Exception as e:
                self.logger.debug(f"Technical analysis failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📐 STATISTICAL ARBITRAGE ENGINE - Pure Math Signals
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.statarb_engine import get_statarb_engine
                statarb = get_statarb_engine()
                statarb_signal = await statarb.get_best_signal(symbol)
                if statarb_signal and statarb_signal.action != 'HOLD' and statarb_signal.confidence > 0.50:
                    sa_action = statarb_signal.action
                    sa_conf = statarb_signal.confidence
                    # StatArb gets high base weight — this is the mathematical edge
                    signal_votes[sa_action] += sa_conf * 1.5
                    confidence_scores.append(sa_conf)
                    reasoning_parts.append(
                        f"StatArb({statarb_signal.strategy}): {sa_action} ({sa_conf:.0%}) "
                        f"z={statarb_signal.z_score:.1f} edge={statarb_signal.edge_estimate:.1f}%"
                    )
                    ai_contributions.append(f'StatArb_{statarb_signal.strategy}')
                    self.logger.info(
                        f"📐 StatArb signal for {symbol}: {sa_action} ({sa_conf:.0%}) "
                        f"strategy={statarb_signal.strategy} z={statarb_signal.z_score:.2f}"
                    )
            except Exception as e:
                self.logger.debug(f"StatArb engine failed for {symbol}: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🌊 HMM REGIME DETECTOR - Adjust weights by market regime
            # ═══════════════════════════════════════════════════════════════
            try:
                from core.hmm_regime_detector import get_regime_detector
                regime_det = get_regime_detector()
                # Use SPY as broad market regime proxy
                regime_state = await regime_det.detect_regime('SPY')
                if regime_state:
                    reasoning_parts.append(f"Regime: {regime_state.regime_name} ({regime_state.probability:.0%})")
                    ai_contributions.append('RegimeDetector')
                    self.logger.info(
                        f"🌊 Regime for {symbol}: {regime_state.regime_name} "
                        f"(p={regime_state.probability:.0%}, trend={regime_state.trend_strength:+.2f})"
                    )
            except Exception as e:
                self.logger.debug(f"Regime detector failed: {e}")
                regime_state = None

            # ═══════════════════════════════════════════════════════════════
            # 🎯 SYNTHESIZE FINAL SIGNAL - Weighted Consensus
            # ═══════════════════════════════════════════════════════════════
            if not ai_contributions:
                self.logger.warning(f"⚠️ No AI components contributed for {symbol} - using conservative HOLD")
                return {
                    'symbol': symbol,
                    'action': 'HOLD',
                    'confidence': 0.3,
                    'reasoning': 'No AI components available',
                    'target_price': current_price,
                    'stop_loss': current_price * 0.97,
                    'timestamp': datetime.now(),
                    'ai_components': []
                }

            # Determine winning action by weighted vote
            final_action = max(signal_votes, key=signal_votes.get)
            total_votes = sum(signal_votes.values())

            # Calculate confidence from votes and individual scores
            vote_confidence = signal_votes[final_action] / total_votes if total_votes > 0 else 0.5
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            final_confidence = (vote_confidence * 0.6 + avg_confidence * 0.4)  # Weighted average

            # CONSERVATIVE MODE: Small agreement bonus only when 3+ AI systems agree
            # FIX: Was inflating ALL signals by up to +20%, producing fake high-confidence trades
            if len(ai_contributions) >= 3:
                agreement_bonus = min(0.05, (len(ai_contributions) - 2) * 0.02)  # Max 5% bonus, only for 3+ systems
                final_confidence = min(0.95, final_confidence + agreement_bonus)

            # No artificial confidence floor - let weak signals stay weak so min_confidence filters them
            # FIX: Was forcing all non-HOLD signals to 0.40, defeating the min_confidence gate

            # ═══════════════════════════════════════════════════════════════
            # 🎯 LEARNING FEEDBACK: Apply symbol performance multiplier
            # Boost confidence for historically profitable symbols
            # Reduce confidence for historically unprofitable symbols
            # ═══════════════════════════════════════════════════════════════
            symbol_multiplier = await self._get_symbol_performance_multiplier(symbol)
            if symbol_multiplier != 1.0:
                old_confidence = final_confidence
                final_confidence = min(0.95, final_confidence * symbol_multiplier)
                self.logger.debug(f"🎯 Symbol learning: {symbol} {old_confidence:.1%} → {final_confidence:.1%} ({symbol_multiplier:.1f}x)")

            # Build comprehensive reasoning
            reasoning = f"[{len(ai_contributions)} AI systems] " + " | ".join(reasoning_parts[:4])

            self.logger.info(f"🎯 FINAL SIGNAL for {symbol}: {final_action} ({final_confidence:.1%}) from {ai_contributions}")

            # 🧠 AI-DRIVEN TARGET PRICE & STOP LOSS
            ai_levels = await self._get_ai_target_and_stop(
                symbol=symbol,
                action=final_action,
                current_price=current_price,
                confidence=final_confidence,
                market_data=market_data
            )

            signal = {
                'symbol': symbol,
                'action': final_action,
                'confidence': final_confidence,
                'reasoning': reasoning,
                'target_price': ai_levels['target_price'],
                'stop_loss': ai_levels['stop_loss'],
                'target_pct': ai_levels.get('target_pct', 0.08),
                'stop_pct': ai_levels.get('stop_pct', 0.03),
                'support_level': ai_levels.get('support_level'),
                'resistance_level': ai_levels.get('resistance_level'),
                'timestamp': datetime.now(),
                'ai_components': ai_contributions,
                'vote_breakdown': signal_votes,
                'entry_price': current_price,  # Store for learning feedback
                'market_data': {  # Store market context for learning
                    'price': current_price,
                    'volume': market_data.get('volume', 0),
                    'volatility': market_data.get('volatility', 0.02),
                    'price_change_24h': market_data.get('change_percent', 0)
                }
            }

            # Store signal prediction for later learning comparison
            await self._store_signal_prediction(signal)

            # NOTE: AI ATTRIBUTION is now recorded AFTER successful trade execution
            # (see _run_continuous_trading_cycle) to avoid recording signals that
            # don't result in trades. This fixes the 99.6% P/L recording gap.

            return signal

        except Exception as e:
            self.logger.error(f"Error getting AI signal for {symbol}: {e}")
            return None

    async def _refresh_ai_system_weights(self) -> Dict[str, float]:
        """
        🎯 LEARNING FEEDBACK LOOP - Refresh AI system weights from performance data

        This method loads adaptive weights from the AI Attribution Tracker based on
        historical performance. Called periodically (every hour) to update weights.

        Returns:
            Dict of AI system names to weight multipliers (0.5 to 2.0)
        """
        try:
            # Check if refresh is needed
            current_time = datetime.now()
            if (self.ai_weights_last_refresh and
                (current_time - self.ai_weights_last_refresh).total_seconds() < self.ai_weights_refresh_interval):
                return self.ai_system_weights  # Use cached weights

            # Get weights from AI Attribution Tracker
            tracker = get_attribution_tracker()
            self.ai_system_weights = await tracker.get_ai_system_weights(min_signals=5, period_days=30)
            self.ai_weights_last_refresh = current_time

            if self.ai_system_weights:
                self.logger.info(f"🎯 LEARNING FEEDBACK: Loaded {len(self.ai_system_weights)} AI system weights")
                # Log top 3 and bottom 3
                sorted_weights = sorted(self.ai_system_weights.items(), key=lambda x: x[1], reverse=True)
                if len(sorted_weights) >= 3:
                    top3 = sorted_weights[:3]
                    bottom3 = sorted_weights[-3:]
                    self.logger.info(f"   📈 TOP: {', '.join(f'{k}={v:.2f}x' for k,v in top3)}")
                    self.logger.info(f"   📉 LOW: {', '.join(f'{k}={v:.2f}x' for k,v in bottom3)}")
                # 💾 Persist weight snapshot for historical tracking
                try:
                    tracker.persist_weight_snapshot(self.ai_system_weights, period_days=30)
                except Exception as _snap_err:
                    self.logger.debug(f"Weight snapshot persist failed: {_snap_err}")
            else:
                self.logger.info("🎯 LEARNING FEEDBACK: No AI weights available yet (need more trade outcomes)")

            return self.ai_system_weights

        except Exception as e:
            self.logger.warning(f"Could not refresh AI system weights: {e}")
            return self.ai_system_weights

    def _get_ai_weight(self, ai_system: str) -> float:
        """
        Get the learned weight for a specific AI system.
        Returns 1.0 (neutral) if no weight data available.

        Common AI system names:
        - 'Oracle', 'Quantum', 'Consciousness', 'Technical', 'MarketResearcher'
        - 'Agents(N)', 'DataIntel', 'CPT-OSS', 'GapDetector', 'OpportunityScanner'
        """
        if not self.ai_system_weights:
            return 1.0

        # Direct match
        if ai_system in self.ai_system_weights:
            return self.ai_system_weights[ai_system]

        # Handle Agents(N) pattern - match any Agents entry
        if ai_system.startswith('Agents('):
            for key, weight in self.ai_system_weights.items():
                if key.startswith('Agents('):
                    return weight

        # Handle OpportunityScanner variants
        if 'OpportunityScanner' in ai_system:
            for key, weight in self.ai_system_weights.items():
                if 'OpportunityScanner' in key:
                    return weight

        # FIX: Return cautious weight for unknown systems instead of neutral 1.0
        # Unknown = no performance data = should not get full influence
        return 0.5  # Cautious weight for unknown/untracked systems

    # ═══════════════════════════════════════════════════════════════════════════
    # 🎯 LEARNING FEEDBACK LOOP - Symbol Performance Learning
    # ═══════════════════════════════════════════════════════════════════════════

    async def _get_symbol_performance_multiplier(self, symbol: str) -> float:
        """
        Get a confidence multiplier based on historical symbol performance.

        This complements AI system weights (which AI performs best) with
        symbol-specific learning (which symbols perform best).

        Returns:
            0.7 to 1.3 multiplier based on historical win rate
            - Win rate > 60%: 1.3x (boost confidence)
            - Win rate 40-60%: 1.0x (neutral)
            - Win rate < 40%: 0.7x (reduce confidence)
            - Insufficient data: 1.0x (neutral)
        """
        try:
            import sqlite3
            db_path = 'prometheus_learning.db'

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get symbol performance from last 30 days
            cursor.execute("""
                SELECT
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(profit_loss) as total_pnl
                FROM trade_history
                WHERE symbol = ?
                AND exit_time >= datetime('now', '-30 days')
            """, (symbol,))

            result = cursor.fetchone()
            conn.close()

            if result and result[0] >= 3:  # Need at least 3 trades
                total_trades, wins, total_pnl = result
                win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

                if win_rate >= 60:
                    multiplier = 1.3
                    self.logger.debug(f"📈 Symbol {symbol}: {win_rate:.0f}% win rate → 1.3x boost")
                elif win_rate >= 40:
                    multiplier = 1.0
                else:
                    multiplier = 0.7
                    self.logger.debug(f"📉 Symbol {symbol}: {win_rate:.0f}% win rate → 0.7x reduction")

                return multiplier

            return 1.0  # Insufficient data

        except Exception as e:
            self.logger.debug(f"Symbol performance lookup failed: {e}")
            return 1.0

    async def _calculate_technical_indicators(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Calculate real technical indicators for baseline analysis - AGGRESSIVE MODE"""
        try:
            current_price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            change_percent = market_data.get('change_percent', 0)

            # Get historical data if available
            historical = market_data.get('historical', [])

            if len(historical) >= 14:
                # Calculate RSI
                gains = []
                losses = []
                for i in range(1, min(15, len(historical))):
                    change = historical[i].get('close', 0) - historical[i-1].get('close', 0)
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))

                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0.001
                rs = avg_gain / avg_loss if avg_loss > 0 else 100
                rsi = 100 - (100 / (1 + rs))

                # RSI-based signal with MACD confirmation
                # TUNED: RSI 22/78 extreme + 30/70 with MACD confirmation = higher accuracy
                # Calculate MACD for confirmation
                _macd_bullish = False
                _macd_bearish = False
                if len(historical) >= 26:
                    # Simple MACD: EMA12 - EMA26 direction
                    _closes = [h.get('close', 0) for h in historical[-26:]]
                    _ema12 = sum(_closes[-12:]) / 12
                    _ema26 = sum(_closes) / 26
                    _macd_val = _ema12 - _ema26
                    # Previous MACD for crossover detection
                    _closes_prev = [h.get('close', 0) for h in historical[-27:-1]] if len(historical) >= 27 else _closes
                    _ema12_p = sum(_closes_prev[-12:]) / 12 if len(_closes_prev) >= 12 else _ema12
                    _ema26_p = sum(_closes_prev[-26:]) / 26 if len(_closes_prev) >= 26 else _ema26
                    _macd_prev = _ema12_p - _ema26_p
                    _macd_bullish = _macd_val > _macd_prev  # MACD rising
                    _macd_bearish = _macd_val < _macd_prev  # MACD falling

                if rsi < 22:  # Extreme oversold — no confirmation needed
                    return {'action': 'BUY', 'confidence': 0.80, 'indicators': f'RSI={rsi:.0f} (extreme oversold)'}
                elif rsi > 78:  # Extreme overbought — no confirmation needed
                    return {'action': 'SELL', 'confidence': 0.80, 'indicators': f'RSI={rsi:.0f} (extreme overbought)'}
                elif rsi < 30 and _macd_bullish:  # Oversold + MACD rising = confirmed BUY
                    return {'action': 'BUY', 'confidence': 0.70, 'indicators': f'RSI={rsi:.0f} + MACD bullish (confirmed oversold)'}
                elif rsi > 70 and _macd_bearish:  # Overbought + MACD falling = confirmed SELL
                    return {'action': 'SELL', 'confidence': 0.70, 'indicators': f'RSI={rsi:.0f} + MACD bearish (confirmed overbought)'}
                elif rsi < 30:  # Oversold but no MACD confirm — lower confidence
                    return {'action': 'BUY', 'confidence': 0.55, 'indicators': f'RSI={rsi:.0f} (oversold, no MACD confirm)'}
                elif rsi > 70:  # Overbought but no MACD confirm — lower confidence
                    return {'action': 'SELL', 'confidence': 0.55, 'indicators': f'RSI={rsi:.0f} (overbought, no MACD confirm)'}

            # Price momentum signals - require stronger moves to trigger
            # FIX: Was 0.5% threshold → too noisy. Raised to 1.5% for meaningful moves
            if change_percent > 1.5:  # Up 1.5%+ = bullish momentum
                confidence = min(0.70, 0.50 + change_percent / 10)
                return {'action': 'BUY', 'confidence': confidence, 'indicators': f'Momentum +{change_percent:.2f}%'}
            elif change_percent < -1.5:  # Down 1.5%+ = bearish momentum
                confidence = min(0.70, 0.50 + abs(change_percent) / 10)
                return {'action': 'SELL', 'confidence': confidence, 'indicators': f'Momentum {change_percent:.2f}%'}

            # Volume analysis fallback - require stronger volume spike
            avg_volume = market_data.get('avg_volume', volume)
            if volume > avg_volume * 2.0 and abs(change_percent) > 0.5:  # FIX: Was 1.3x with buy-only bias
                # High volume + price movement = potential momentum
                action = 'BUY' if change_percent > 0 else 'SELL'
                return {'action': action, 'confidence': 0.55, 'indicators': f'High volume {action.lower()} ({volume/avg_volume:.1f}x vol)'}

            # QUIET MARKET: No signal - HOLD until real opportunity appears
            # NOTE: Random signal injection REMOVED (was gambling with 15% random BUY/SELL)
            return {'action': 'HOLD', 'confidence': 0.35, 'indicators': 'Neutral technicals - waiting for real signal'}

        except Exception as e:
            self.logger.debug(f"Technical indicator calculation failed: {e}")
            return None

    async def fetch_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time market data for a symbol"""
        try:
            # Determine which broker to use
            broker = None

            # ═══════════════════════════════════════════════════════════════
            # 🔄 NORMALIZE CRYPTO SYMBOLS: Convert LINKUSD → LINK/USD
            # Alpaca positions come as LINKUSD but APIs need LINK/USD format
            # ═══════════════════════════════════════════════════════════════
            crypto_bases = ['BTC', 'ETH', 'SOL', 'LINK', 'AVAX', 'AAVE', 'DOGE', 'PEPE',
                           'UNI', 'SUSHI', 'CRV', 'ADA', 'DOT', 'MATIC', 'ATOM', 'XRP',
                           'LTC', 'BCH', 'SHIB', 'NEAR', 'FTM', 'ALGO', 'XLM', 'VET']

            # If symbol is like LINKUSD (no slash) and ends with USD, convert to LINK/USD
            if '/' not in symbol and symbol.endswith('USD'):
                base = symbol[:-3]  # Remove 'USD' suffix
                if base in crypto_bases:
                    symbol = f"{base}/USD"
                    self.logger.debug(f"🔄 Normalized crypto symbol: {symbol[:-4]}USD → {symbol}")

            # Define forex pairs that should use IB, not Alpaca
            forex_pairs = {
                'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
                'EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'GBPCHF', 'AUDJPY', 'CADJPY',
                'EURAUD', 'EURCAD', 'GBPAUD', 'GBPCAD', 'AUDCAD', 'AUDCHF', 'CADCHF', 'NZDJPY'
            }

            if symbol in forex_pairs:  # Forex pairs - use IB only
                broker = self.systems.get('ib_broker')
            elif '/' in symbol:  # Crypto - use Alpaca
                broker = self.systems.get('alpaca_broker')
            else:  # Stocks - prefer Alpaca, fallback to IB
                broker = self.systems.get('alpaca_broker') or self.systems.get('ib_broker')

            if broker:
                try:
                    # Get market data from broker (correct method name)
                    market_data = await broker.get_market_data(symbol)
                    if market_data and market_data.get('price', 0) > 0:
                        self.logger.debug(f" Got market data for {symbol} from broker: ${market_data.get('price'):.2f}")
                        return market_data
                except Exception as e:
                    self.logger.debug(f"Broker real-time data failed for {symbol}: {e}")

            # Fallback 1: Try Yahoo Finance (FREE and RELIABLE)
            if self.systems.get('yahoo_finance'):
                try:
                    data = await self.systems['yahoo_finance'].get_real_time_data_async(symbol)
                    if data and data.get('price', 0) > 0:
                        self.logger.info(f" Got market data for {symbol} from Yahoo Finance: ${data.get('price'):.2f}")
                        return data
                except Exception as e:
                    self.logger.debug(f"Yahoo Finance fallback failed for {symbol}: {e}")

            # Fallback 2: Try market data orchestrator
            if self.systems.get('market_data'):
                try:
                    data = await self.systems['market_data'].get_real_time_data(symbol)
                    if data and data.get('price', 0) > 0:
                        return {
                            'symbol': symbol,
                            'price': data.get('price', 0),
                            'volume': data.get('volume', 0),
                            'timestamp': datetime.now()
                        }
                except Exception as e:
                    self.logger.debug(f"Market data orchestrator fallback failed for {symbol}: {e}")

            # Fallback 3: Try historical data (use most recent bar)
            if broker:
                try:
                    historical = await broker.get_historical_data(symbol, timeframe='1Min', limit=1)
                    if historical and len(historical) > 0:
                        latest_bar = historical[-1]
                        self.logger.info(f" Got market data for {symbol} from historical: ${latest_bar.get('close'):.2f}")
                        return {
                            'symbol': symbol,
                            'price': latest_bar.get('close', 0),
                            'volume': latest_bar.get('volume', 0),
                            'timestamp': latest_bar.get('timestamp', datetime.now())
                        }
                except Exception as e:
                    self.logger.debug(f"Historical data fallback failed for {symbol}: {e}")

            # Fallback 4: Try Yahoo Finance historical
            if self.systems.get('yahoo_finance'):
                try:
                    historical = await self.systems['yahoo_finance'].get_historical_data_async(symbol, timeframe='1Min', limit=1)
                    if historical and len(historical) > 0:
                        latest_bar = historical[-1]
                        self.logger.info(f" Got market data for {symbol} from Yahoo historical: ${latest_bar.get('close'):.2f}")
                        return {
                            'symbol': symbol,
                            'price': latest_bar.get('close', 0),
                            'volume': latest_bar.get('volume', 0),
                            'timestamp': latest_bar.get('timestamp', datetime.now())
                        }
                except Exception as e:
                    self.logger.debug(f"Yahoo Finance historical fallback failed for {symbol}: {e}")

            self.logger.warning(f" All market data sources failed for {symbol}")
            return None

        except Exception as e:
            self.logger.error(f"Error fetching market data for {symbol}: {e}")
            return None

    async def _get_ai_order_type(self, symbol: str, action: str, confidence: float,
                                  current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 AI-DRIVEN ORDER TYPE SELECTION
        Intelligently selects between MARKET and LIMIT orders based on:
        - Signal urgency (high confidence = MARKET for fast execution)
        - Symbol volatility (high volatility = LIMIT to avoid slippage)
        - Spread analysis (wide spread = LIMIT for better price)
        - Liquidity (low volume = LIMIT to minimize market impact)
        - Time of day (market open/close = LIMIT due to volatility)
        """
        try:
            order_factors = []
            # Score system: positive = MARKET, negative = LIMIT
            market_score = 0

            # ═══════════════════════════════════════════════════════════════
            # 1. URGENCY BASED ON CONFIDENCE
            # ═══════════════════════════════════════════════════════════════
            if confidence >= 0.80:
                market_score += 3  # Very high confidence = market order for speed
                order_factors.append(f"HighConf({confidence:.0%})=MARKET+3")
            elif confidence >= 0.65:
                market_score += 1
                order_factors.append(f"MedConf({confidence:.0%})=MARKET+1")
            elif confidence < 0.45:
                market_score -= 2  # Low confidence = no rush, use limit
                order_factors.append(f"LowConf({confidence:.0%})=LIMIT+2")

            # ═══════════════════════════════════════════════════════════════
            # 2. VOLATILITY ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            volatility = market_data.get('volatility', 0.02)

            if volatility > 0.50:  # Very high volatility
                market_score -= 3  # Use LIMIT to avoid slippage
                order_factors.append(f"HighVol({volatility:.0%})=LIMIT+3")
            elif volatility > 0.30:
                market_score -= 2
                order_factors.append(f"MedVol({volatility:.0%})=LIMIT+2")
            elif volatility < 0.15:
                market_score += 1  # Low volatility = safe for market order
                order_factors.append(f"LowVol({volatility:.0%})=MARKET+1")

            # ═══════════════════════════════════════════════════════════════
            # 3. VOLUME/LIQUIDITY ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)

            if avg_volume > 0:
                volume_ratio = volume / avg_volume
                if volume_ratio < 0.3:  # Low volume day
                    market_score -= 2  # LIMIT to minimize market impact
                    order_factors.append(f"LowVol({volume_ratio:.0%})=LIMIT+2")
                elif volume_ratio > 1.5:  # High volume day
                    market_score += 1  # Safe for market order
                    order_factors.append(f"HighVol({volume_ratio:.0%})=MARKET+1")

            # ═══════════════════════════════════════════════════════════════
            # 4. SPREAD ANALYSIS (bid-ask spread)
            # ═══════════════════════════════════════════════════════════════
            bid = market_data.get('bid', current_price * 0.999)
            ask = market_data.get('ask', current_price * 1.001)

            if bid > 0 and ask > 0:
                spread_pct = (ask - bid) / current_price
                if spread_pct > 0.005:  # Wide spread (>0.5%)
                    market_score -= 2
                    order_factors.append(f"WideSpread({spread_pct:.2%})=LIMIT+2")
                elif spread_pct > 0.002:  # Moderate spread
                    market_score -= 1
                    order_factors.append(f"ModSpread({spread_pct:.2%})=LIMIT+1")
                else:  # Tight spread (<0.2%)
                    market_score += 1
                    order_factors.append(f"TightSpread({spread_pct:.2%})=MARKET+1")

            # ═══════════════════════════════════════════════════════════════
            # 5. TIME OF DAY ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            from datetime import datetime
            hour = datetime.now().hour
            minute = datetime.now().minute

            # Market open (9:30-10:00) and close (15:30-16:00) are volatile
            if (hour == 9 and minute >= 30) or (hour == 10 and minute < 15):
                market_score -= 2  # Opening volatility
                order_factors.append("MarketOpen=LIMIT+2")
            elif (hour == 15 and minute >= 30) or hour == 16:
                market_score -= 2  # Closing volatility
                order_factors.append("MarketClose=LIMIT+2")
            elif 11 <= hour <= 14:  # Midday calm
                market_score += 1
                order_factors.append("MiddayCalm=MARKET+1")

            # ═══════════════════════════════════════════════════════════════
            # 6. ASSET CLASS ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            if '/' in symbol:  # Crypto
                market_score -= 1  # Crypto tends to be more volatile
                order_factors.append("Crypto=LIMIT+1")
            elif symbol in ['SPY', 'QQQ', 'IWM', 'DIA']:  # Liquid ETFs
                market_score += 2  # Very liquid = safe for market
                order_factors.append("LiquidETF=MARKET+2")

            # ═══════════════════════════════════════════════════════════════
            # DETERMINE ORDER TYPE AND LIMIT PRICE
            # ═══════════════════════════════════════════════════════════════
            if market_score >= 2:
                order_type = 'MARKET'
                limit_price = None
            else:
                order_type = 'LIMIT'
                # Calculate limit price with slight improvement
                if action in ['BUY', 'STRONG_BUY']:
                    # For BUY: limit at or slightly below current price
                    improvement = min(0.002, max(0.0005, volatility * 0.05))  # 0.05%-0.2%
                    limit_price = round(current_price * (1 - improvement), 2)
                else:  # SELL
                    # For SELL: limit at or slightly above current price
                    improvement = min(0.002, max(0.0005, volatility * 0.05))
                    limit_price = round(current_price * (1 + improvement), 2)

            self.logger.info(f"🧠 AI ORDER TYPE for {symbol}: {order_type}")
            self.logger.info(f"   Score: {market_score} | Factors: {', '.join(order_factors[:4])}")
            if limit_price:
                self.logger.info(f"   Limit Price: ${limit_price:.2f} (current: ${current_price:.2f})")

            return {
                'order_type': order_type,
                'limit_price': limit_price,
                'market_score': market_score,
                'factors': order_factors
            }

        except Exception as e:
            self.logger.warning(f"AI order type selection failed: {e} - using MARKET")
            return {
                'order_type': 'MARKET',
                'limit_price': None,
                'market_score': 0,
                'factors': ['Fallback']
            }

    async def _validate_against_shadow_results(self, symbol: str, action: str, confidence: float) -> Dict[str, Any]:
        """
        🧪 CROSS-LEARNING GATE: Validate live trade against shadow trading results.
        
        Queries shadow_trade_history for matching symbol+action trades.
        If shadow data shows consistently poor results, blocks the live trade.
        If no shadow data exists, allows the trade (don't penalize missing data).
        
        Returns:
            Dict with 'should_trade', 'reason', 'shadow_win_rate', 'shadow_trades'
        """
        try:
            import sqlite3
            db = sqlite3.connect('prometheus_learning.db', timeout=10.0)
            cursor = db.cursor()
            
            # Check if shadow_trade_history table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='shadow_trade_history'
            """)
            if not cursor.fetchone():
                db.close()
                return {'should_trade': True, 'reason': 'No shadow table yet'}
            
            # Get shadow performance for this symbol+action in last 7 days
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                    AVG(profit_loss) as avg_pnl,
                    SUM(profit_loss) as total_pnl
                FROM shadow_trade_history
                WHERE symbol = ? 
                  AND action = ?
                  AND timestamp > datetime('now', '-7 days')
                  AND exit_price IS NOT NULL
            """, (symbol, action))
            row = cursor.fetchone()
            db.close()
            
            if not row or not row[0] or row[0] < 3:
                # Not enough shadow data — allow the trade
                shadow_count = row[0] if row and row[0] else 0
                return {
                    'should_trade': True,
                    'reason': f'Insufficient shadow data ({shadow_count} trades)',
                    'shadow_trades': shadow_count,
                    'shadow_win_rate': None
                }
            
            total_trades = row[0]
            wins = row[1] or 0
            avg_pnl = row[2] or 0
            total_pnl = row[3] or 0
            win_rate = wins / total_trades
            
            # Block if: 3+ shadow trades AND <20% win rate AND negative total P/L
            if win_rate < 0.20 and total_pnl < 0:
                return {
                    'should_trade': False,
                    'reason': f'Shadow says NO: {symbol} {action} has {win_rate:.0%} WR across {total_trades} shadow trades (P/L: ${total_pnl:.2f})',
                    'shadow_trades': total_trades,
                    'shadow_win_rate': win_rate,
                    'shadow_avg_pnl': avg_pnl
                }
            
            # Allow but log warning if mediocre performance
            if win_rate < 0.40:
                self.logger.info(f"🧪 Shadow caution: {symbol} {action} has {win_rate:.0%} WR ({total_trades} trades)")
            
            return {
                'should_trade': True,
                'reason': f'Shadow OK: {win_rate:.0%} WR across {total_trades} trades',
                'shadow_trades': total_trades,
                'shadow_win_rate': win_rate,
                'shadow_avg_pnl': avg_pnl
            }
            
        except Exception as e:
            self.logger.debug(f"Shadow validation error: {e}")
            # On error, allow the trade (don't block due to DB issues)
            return {'should_trade': True, 'reason': f'Shadow check error: {e}'}

    async def _should_delay_entry(self, symbol: str, action: str, confidence: float,
                                   current_price: float, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 AI-DRIVEN TRADE TIMING OPTIMIZATION
        Analyzes whether to execute immediately or delay entry for better price based on:
        - Intraday patterns (avoid volatile open/close)
        - Price momentum (wait for pullback on BUY, bounce on SELL)
        - Volume confirmation (wait for volume spike)
        - Support/resistance proximity (better entry near levels)
        - Recent price action (overbought/oversold conditions)
        """
        try:
            timing_factors = []
            # Negative score = delay recommended, Positive = execute now
            execute_score = 0
            delay_reason = None
            suggested_delay_mins = 0

            # ═══════════════════════════════════════════════════════════════
            # 1. TIME OF DAY ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            from datetime import datetime
            hour = datetime.now().hour
            minute = datetime.now().minute

            # Avoid first 15 minutes of market open (extreme volatility)
            if hour == 9 and minute < 45:
                execute_score -= 3
                timing_factors.append("AvoidOpen(-3)")
                delay_reason = "Market opening volatility - wait 15 min"
                suggested_delay_mins = max(suggested_delay_mins, 45 - minute)
            # Avoid last 15 minutes of trading (closing volatility)
            elif hour == 15 and minute >= 45:
                execute_score -= 2
                timing_factors.append("AvoidClose(-2)")
                delay_reason = "Market closing volatility"
                suggested_delay_mins = 0  # Don't wait, market will close
            # Midday is calmer - good for entries
            elif 11 <= hour <= 14:
                execute_score += 2
                timing_factors.append("MiddayCalm(+2)")
            # 10-11 AM often has follow-through
            elif hour == 10:
                execute_score += 1
                timing_factors.append("MorningMomentum(+1)")

            # ═══════════════════════════════════════════════════════════════
            # 2. MOMENTUM/OVERBOUGHT-OVERSOLD ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            price_change = market_data.get('change_percent', 0)

            if action in ['BUY', 'STRONG_BUY']:
                # For BUY: wait if already up big (overbought)
                if price_change > 0.03:  # Up >3% already
                    execute_score -= 2
                    timing_factors.append(f"Overbought({price_change:.1%})(-2)")
                    delay_reason = "Price already up significantly - wait for pullback"
                    suggested_delay_mins = max(suggested_delay_mins, 15)
                elif price_change < -0.02:  # Down >2% - may be oversold
                    execute_score += 2
                    timing_factors.append(f"Oversold({price_change:.1%})(+2)")
                elif -0.01 <= price_change <= 0.01:  # Relatively flat
                    execute_score += 1
                    timing_factors.append("FlatPrice(+1)")
            else:  # SELL
                # For SELL: wait if already down big (oversold bounce possible)
                if price_change < -0.03:  # Down >3% already
                    execute_score -= 2
                    timing_factors.append(f"Oversold({price_change:.1%})(-2)")
                    delay_reason = "Price already down significantly - wait for bounce"
                    suggested_delay_mins = max(suggested_delay_mins, 15)
                elif price_change > 0.02:  # Up >2% - good time to sell
                    execute_score += 2
                    timing_factors.append(f"Overbought({price_change:.1%})(+2)")

            # ═══════════════════════════════════════════════════════════════
            # 3. VOLUME CONFIRMATION
            # ═══════════════════════════════════════════════════════════════
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume) or volume

            if avg_volume > 0 and volume > 0:
                volume_ratio = volume / avg_volume
                if volume_ratio < 0.5:  # Very low volume
                    execute_score -= 2
                    timing_factors.append(f"LowVolume({volume_ratio:.0%})(-2)")
                    delay_reason = "Low volume - wait for volume confirmation"
                    suggested_delay_mins = max(suggested_delay_mins, 10)
                elif volume_ratio > 1.5:  # High volume confirmation
                    execute_score += 2
                    timing_factors.append(f"HighVolume({volume_ratio:.0%})(+2)")
                elif volume_ratio > 1.0:
                    execute_score += 1
                    timing_factors.append(f"GoodVolume({volume_ratio:.0%})(+1)")

            # ═══════════════════════════════════════════════════════════════
            # 4. CONFIDENCE URGENCY
            # ═══════════════════════════════════════════════════════════════
            if confidence >= 0.80:
                execute_score += 3  # High confidence = execute now
                timing_factors.append(f"HighConf({confidence:.0%})(+3)")
            elif confidence >= 0.65:
                execute_score += 1
                timing_factors.append(f"GoodConf({confidence:.0%})(+1)")
            elif confidence < 0.45:
                execute_score -= 1  # Low confidence = no rush
                timing_factors.append(f"LowConf({confidence:.0%})(-1)")

            # ═══════════════════════════════════════════════════════════════
            # 5. CRYPTO 24/7 ADJUSTMENT
            # ═══════════════════════════════════════════════════════════════
            if '/' in symbol:  # Crypto
                # No market hours concern for crypto
                if hour < 6 or hour > 22:  # Low activity hours
                    execute_score -= 1
                    timing_factors.append("CryptoLowActivity(-1)")
                else:
                    execute_score += 1  # Normal crypto hours
                    timing_factors.append("CryptoActive(+1)")

            # ═══════════════════════════════════════════════════════════════
            # DETERMINE RECOMMENDATION
            # ═══════════════════════════════════════════════════════════════
            should_execute = execute_score >= 0

            # Cap delay at 30 minutes
            suggested_delay_mins = min(30, suggested_delay_mins)

            self.logger.info(f"🧠 AI TRADE TIMING for {symbol}:")
            self.logger.info(f"   Score: {execute_score} | Execute: {'NOW' if should_execute else 'DELAY'}")
            self.logger.info(f"   Factors: {', '.join(timing_factors[:4])}")
            if not should_execute and delay_reason:
                self.logger.info(f"   ⏳ Delay Reason: {delay_reason}")

            return {
                'should_execute': should_execute,
                'execute_score': execute_score,
                'delay_reason': delay_reason,
                'suggested_delay_mins': suggested_delay_mins if not should_execute else 0,
                'timing_factors': timing_factors
            }

        except Exception as e:
            self.logger.warning(f"AI trade timing failed: {e} - executing immediately")
            return {
                'should_execute': True,
                'execute_score': 0,
                'delay_reason': None,
                'suggested_delay_mins': 0,
                'timing_factors': ['Fallback']
            }

    def _check_sentiment_filter(self) -> Dict[str, Any]:
        """
        🚀 ENHANCEMENT 5: SENTIMENT FILTER
        Avoid trading on high-impact event days (Fed meetings, major economic releases)
        """
        if not self.sentiment_filter_enabled:
            return {'should_trade': True, 'reason': 'Filter disabled'}

        try:
            from datetime import datetime
            today = datetime.now()
            month = today.month
            day = today.day
            weekday = today.weekday()  # 0=Monday

            # Known 2026 Fed Meeting Dates (typically Tues-Wed)
            # These are approximations - in production, use economic calendar API
            fed_meeting_dates = [
                (1, 28), (1, 29),   # Jan 2026
                (3, 17), (3, 18),   # Mar 2026
                (5, 5), (5, 6),     # May 2026
                (6, 16), (6, 17),   # Jun 2026
                (7, 28), (7, 29),   # Jul 2026
                (9, 15), (9, 16),   # Sep 2026
                (11, 3), (11, 4),   # Nov 2026
                (12, 15), (12, 16)  # Dec 2026
            ]

            # Check if today is a Fed meeting day
            if (month, day) in fed_meeting_dates:
                self.logger.info(f"📅 SENTIMENT FILTER: Fed meeting day - reducing risk")
                return {
                    'should_trade': False,
                    'reason': 'Fed meeting day - high volatility expected',
                    'reduce_position': 0.5  # Halve position sizes
                }

            # Jobs report (typically first Friday of month)
            if weekday == 4 and day <= 7:  # First Friday
                self.logger.info(f"📅 SENTIMENT FILTER: Jobs report Friday - cautious mode")
                return {
                    'should_trade': True,
                    'reason': 'Jobs report day - reduced position',
                    'reduce_position': 0.7
                }

            # CPI release (typically mid-month Tuesday/Wednesday)
            if 10 <= day <= 15 and weekday in [1, 2]:
                # Could be CPI day
                return {
                    'should_trade': True,
                    'reason': 'Potential CPI release - cautious',
                    'reduce_position': 0.8
                }

            return {'should_trade': True, 'reason': 'No major events', 'reduce_position': 1.0}

        except Exception as e:
            self.logger.debug(f"Sentiment filter error: {e}")
            return {'should_trade': True, 'reason': 'Filter error', 'reduce_position': 1.0}

    async def _check_correlation_filter(self, symbol: str) -> Dict[str, Any]:
        """
        🚀 ENHANCEMENT 6: CORRELATION FILTER
        Limit correlated positions to avoid concentration risk
        """
        if not self.correlation_filter_enabled:
            return {'should_trade': True, 'reason': 'Filter disabled'}

        try:
            # Define sector/correlation groups
            sector_groups = {
                'TECH': ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'AMZN', 'NVDA', 'AMD', 'INTC', 'CRM', 'ORCL'],
                'FINANCE': ['JPM', 'BAC', 'GS', 'MS', 'WFC', 'C', 'V', 'MA', 'AXP'],
                'HEALTH': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABBV', 'LLY', 'BMY', 'AMGN'],
                'ENERGY': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'OXY', 'MPC'],
                'CONSUMER': ['WMT', 'PG', 'KO', 'PEP', 'COST', 'HD', 'NKE', 'MCD'],
                'CRYPTO': ['BTC/USD', 'ETH/USD', 'SOL/USD', 'LINK/USD', 'DOGE/USD', 'AVAX/USD'],
                'CRYPTO_ALT': ['BTCUSD', 'ETHUSD', 'SOLUSD', 'LINKUSD', 'DOGEUSD', 'AVAXUSD']
            }

            # Find which group the symbol belongs to
            symbol_sector = None
            for sector, symbols in sector_groups.items():
                if symbol in symbols or symbol.upper() in symbols:
                    symbol_sector = sector
                    break

            if not symbol_sector:
                # Unknown sector, allow trade
                return {'should_trade': True, 'reason': 'Uncorrelated symbol'}

            # Count existing positions in the same sector
            alpaca_broker = self.systems.get('alpaca_broker')
            if not alpaca_broker:
                return {'should_trade': True, 'reason': 'No broker to check positions'}

            try:
                positions = alpaca_broker.get_positions()
            except:
                return {'should_trade': True, 'reason': 'Could not fetch positions'}

            if not positions:
                return {'should_trade': True, 'reason': 'No existing positions'}

            # Count positions in same sector
            sector_symbols = sector_groups.get(symbol_sector, [])
            sector_position_count = 0
            sector_value = 0.0

            for pos in positions:
                pos_symbol = pos.symbol if hasattr(pos, 'symbol') else str(pos)
                if pos_symbol in sector_symbols or pos_symbol.upper() in sector_symbols:
                    sector_position_count += 1
                    try:
                        sector_value += float(pos.market_value) if hasattr(pos, 'market_value') else 0
                    except:
                        pass

            # Limit: Max 3 positions per sector, max 30% portfolio in one sector
            MAX_SECTOR_POSITIONS = 3
            MAX_SECTOR_PCT = 0.30

            if sector_position_count >= MAX_SECTOR_POSITIONS:
                self.logger.info(f"🔗 CORRELATION FILTER: {symbol_sector} sector already has {sector_position_count} positions")
                return {
                    'should_trade': False,
                    'reason': f'{symbol_sector} sector maxed ({sector_position_count}/{MAX_SECTOR_POSITIONS})',
                    'sector': symbol_sector,
                    'sector_count': sector_position_count
                }

            # Check sector % (need account equity)
            try:
                account = await alpaca_broker.get_account()  # FIX: get_account() is async
                equity = float(account.equity) if hasattr(account, 'equity') else 0
                if equity > 0 and sector_value / equity > MAX_SECTOR_PCT:
                    self.logger.info(f"🔗 CORRELATION FILTER: {symbol_sector} sector at {sector_value/equity*100:.1f}% of portfolio")
                    return {
                        'should_trade': False,
                        'reason': f'{symbol_sector} sector overweight ({sector_value/equity*100:.0f}%>{MAX_SECTOR_PCT*100:.0f}%)',
                        'sector': symbol_sector,
                        'sector_pct': sector_value / equity
                    }
            except:
                pass

            return {
                'should_trade': True,
                'reason': f'{symbol_sector}: {sector_position_count}/{MAX_SECTOR_POSITIONS} positions OK',
                'sector': symbol_sector,
                'sector_count': sector_position_count
            }

        except Exception as e:
            self.logger.debug(f"Correlation filter error: {e}")
            return {'should_trade': True, 'reason': 'Filter error'}

    async def execute_trade_from_signal(self, signal: Dict[str, Any]) -> bool:
        """Execute a trade based on AI signal"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            confidence = signal['confidence']

            # Determine broker with policy-based routing
            broker = None
            alpaca_broker = self.systems.get('alpaca_broker')
            ib_broker = self.systems.get('ib_broker')

            if self.autonomous_routing_enabled:
                broker, broker_name, route_meta = await self._select_broker_for_symbol(symbol, alpaca_broker, ib_broker)
                self.logger.info(
                    f"[ROUTER] live={route_meta.get('selected')} symbol={symbol} "
                    f"reason={route_meta.get('reason')} ib_cash=${route_meta.get('ib_cash', 0):.2f} "
                    f"alpaca_cash=${route_meta.get('alpaca_cash', 0):.2f} "
                    f"ib_share={route_meta.get('ib_allocation_share', 0):.2f}"
                )
            else:
                broker, broker_name, route_meta = await self._select_legacy_broker_for_symbol(symbol, alpaca_broker, ib_broker)
                if self.routing_shadow_mode:
                    _, _, shadow_meta = await self._select_broker_for_symbol(symbol, alpaca_broker, ib_broker)
                    self.logger.info(
                        f"[ROUTER_SHADOW] symbol={symbol} live={route_meta.get('selected')} "
                        f"shadow={shadow_meta.get('selected')} reason={shadow_meta.get('reason')}"
                    )

            if not broker:
                self.logger.error(f"No broker available for {symbol}")
                return False

            if broker_name == 'IB':
                self.routing_execution_counts['ib'] = self.routing_execution_counts.get('ib', 0) + 1
            else:
                self.routing_execution_counts['alpaca'] = self.routing_execution_counts.get('alpaca', 0) + 1
            self._persist_routing_stats()

            # Only execute BUY or SELL signals
            if action not in ['BUY', 'STRONG_BUY', 'SELL', 'STRONG_SELL']:
                self.logger.info(f" Signal is HOLD for {symbol} - no trade")
                return False

            # Get COMBINED equity across both brokers for position sizing
            combined = await self._get_combined_capital()
            equity = combined.get('total_equity', 0)
            if equity == 0:
                # Fallback to single broker equity
                account = await broker.get_account()
                equity = float(account.equity)
            self.logger.info(f"📊 Combined equity for sizing: ${equity:.2f} (Alpaca: ${combined.get('alpaca_equity', 0):.2f} + IB: ${combined.get('ib_equity', 0):.2f})")

            if equity == 0:
                self.logger.error(f"Cannot determine account equity for {symbol}")
                return False

            # Get current price
            market_data = await self.fetch_market_data(symbol)
            if not market_data:
                self.logger.error(f"Cannot get price for {symbol}")
                return False

            current_price = market_data.get('price', 0)
            if current_price == 0:
                self.logger.error(f"Invalid price for {symbol}")
                return False

            # 🧠 AI-DRIVEN POSITION SIZING for BUY orders
            ai_position_size_pct = self.risk_limits['position_size_pct']  # Default
            if action in ['BUY', 'STRONG_BUY']:
                try:
                    ai_position_size_pct = await self._get_ai_position_size(symbol, signal, equity)
                    self.logger.info(f"🧠 Using AI position size: {ai_position_size_pct*100:.2f}% for {symbol}")
                except Exception as e:
                    self.logger.warning(f"AI position sizing failed, using default: {e}")

            #  USE ENHANCED TRADING LOGIC FOR SHORT SELLING
            if self.enhanced_logic:
                trade_details = self.enhanced_logic.determine_order_details(
                    symbol=symbol,
                    action=action,
                    current_price=current_price,
                    equity=equity,
                    position_size_pct=ai_position_size_pct,  # Use AI-calculated size
                    broker_name=broker_name
                )

                if not trade_details['should_trade']:
                    self.logger.info(f" No trade needed for {symbol} - {trade_details['position_action']}")
                    return False

                order_side = trade_details['order_side']
                quantity = trade_details['quantity']
                position_action = trade_details['position_action']
                position_side = trade_details['position_side']

                self.logger.info(f" Position Action: {position_action} | Position Side: {position_side}")
            else:
                # FALLBACK: Original logic (LONG only) with AI position sizing
                order_side = OrderSide.BUY if action in ['BUY', 'STRONG_BUY'] else OrderSide.SELL
                trade_amount = equity * ai_position_size_pct  # Use AI-calculated size
                quantity = trade_amount / current_price
                position_action = "OPEN_LONG" if order_side == OrderSide.BUY else "CLOSE_LONG"
                position_side = "LONG"

            # 🚫 PREVENT SHORTING ON ALPACA (not allowed)
            if position_action in ['OPEN_SHORT', 'ADD_SHORT'] and broker_name == 'Alpaca':
                self.logger.warning(f"⚠️ Alpaca does not allow shorting - SKIPPING {position_action} for {symbol}")
                return False

            # FOR CLOSE/SELL ORDERS: Get ACTUAL position from broker to avoid balance mismatches
            if position_action in ['CLOSE_LONG', 'CLOSE_SHORT']:
                self.logger.info(f"🔍 Getting ACTUAL broker position for {symbol} (CLOSE order)")
                try:
                    actual_position = await broker.get_position(symbol)

                    if actual_position:
                        # Use exact available quantity from broker (no rounding!)
                        actual_qty = abs(float(actual_position.quantity))
                        if actual_qty > 0:
                            self.logger.info(f"📊 Using ACTUAL broker quantity: {actual_qty} {symbol} (was: {quantity})")
                            quantity = actual_qty
                        else:
                            self.logger.warning(f"⚠️ Broker position quantity is 0 for {symbol} - SKIPPING TRADE")
                            return False
                    else:
                        # NO POSITION EXISTS - Cannot sell what we don't have!
                        self.logger.warning(f"⚠️ No broker position found for {symbol} - SKIPPING SELL (would cause short error)")
                        # Sync internal DB to remove phantom position
                        await self._sync_positions_from_alpaca()
                        return False
                except Exception as e:
                    self.logger.warning(f"Could not get actual position for {symbol}: {e} - SKIPPING TRADE")
                    return False

            # Round quantity appropriately
            if '/' in symbol:  # Crypto
                quantity = round(quantity, 6)
            else:  # Stock - Alpaca supports fractional shares
                # For Alpaca, use fractional shares (round to 4 decimal places)
                if broker_name == 'Alpaca':
                    quantity = round(quantity, 4)
                    # Minimum $1 notional value for Alpaca
                    min_notional = 1.0
                    if quantity * current_price < min_notional:
                        quantity = round(min_notional / current_price, 4)
                else:
                    # For IB, use whole shares
                    quantity = int(quantity)
                    if quantity == 0:
                        quantity = 1  # Minimum 1 share for IB

            if quantity <= 0:
                self.logger.warning(f"Quantity too small for {symbol}")
                return False

            self.logger.info(f" Executing {order_side.value.upper()} order: {quantity} {symbol} @ ${current_price:.2f} via {broker_name}")
            self.logger.info(f"   Confidence: {confidence:.1%} | Reasoning: {signal.get('reasoning', 'N/A')[:100]}")

            # 🧠 AI-DRIVEN ORDER TYPE SELECTION
            ai_order_decision = await self._get_ai_order_type(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                market_data=market_data
            )

            selected_order_type = OrderType.MARKET if ai_order_decision['order_type'] == 'MARKET' else OrderType.LIMIT
            limit_price = ai_order_decision.get('limit_price')

            # Create Order object with AI-selected order type
            order_obj = Order(
                symbol=symbol,
                quantity=quantity,
                side=order_side,
                order_type=selected_order_type,
                limit_price=limit_price,  # None for MARKET orders
                time_in_force='gtc'  # Good till cancelled (works for crypto 24/7)
            )

            self.logger.info(f"   🧠 Order Type: {selected_order_type.value} (score: {ai_order_decision['market_score']})")

            # Submit order using correct method
            order_result = await broker.submit_order(order_obj)

            if order_result:
                self.logger.info(f" Order placed successfully: {order_result.broker_order_id}")

                # Convert Order object to dict for database recording
                order_dict = {
                    'id': order_result.broker_order_id,
                    'symbol': order_result.symbol,
                    'quantity': order_result.quantity,
                    'price': order_result.filled_price or current_price,
                    'side': order_result.side.value,
                    'status': order_result.status.value
                }

                # Record trade in learning database
                await self.record_trade_in_database(signal, order_dict, broker_name)

                #  RECORD POSITION TRACKING FOR SHORT SELLING
                if self.enhanced_logic:
                    self.enhanced_logic.record_trade_execution(
                        symbol=symbol,
                        position_action=position_action,
                        position_side=position_side,
                        quantity=quantity,
                        price=current_price,
                        broker_name=broker_name
                    )
                    self.logger.info(f" Position tracking updated: {position_action} {position_side}")

                # ═══════════════════════════════════════════════════════════════
                # 🛡️ GUARDIAN: Register stop-loss for new position
                # ═══════════════════════════════════════════════════════════════
                try:
                    if hasattr(self, '_guardian') and self._guardian and order_side.value.upper() == 'BUY':
                        stop_info = self._guardian.set_stop_loss(symbol, current_price, quantity)
                        self.logger.info(f"🛡️ STOP SET: {symbol} stop=${stop_info['stop_price']:.2f} "
                                        f"({stop_info['stop_pct']:.1f}%) risk=${stop_info['risk_amount']:.2f}")
                except Exception as gse:
                    self.logger.debug(f"Guardian stop-loss registration failed: {gse}")

                # ── Auto-learning trigger: supervised learning every 50 trades ──
                self.trade_count_since_training += 1
                if self.trade_count_since_training >= self.training_trigger_threshold:
                    self.trade_count_since_training = 0
                    self.logger.info(f"🎓 Auto-learning: {self.training_trigger_threshold}-trade threshold reached — triggering supervised learning")
                    try:
                        from agent_learning_manager import train_on_trade as _ailt
                        _ailt({}, {})
                    except ImportError:
                        self.logger.debug("agent_learning_manager not available for auto-learning")
                    except Exception as _al_err:
                        self.logger.debug(f"Auto-learning non-critical error: {_al_err}")

                return True
            else:
                self.logger.error(f" Order failed for {symbol}")
                return False

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False

    async def record_trade_in_database(self, signal: Dict[str, Any], order: Dict[str, Any], broker: str):
        """Record trade in learning database with full details"""
        try:
            import sqlite3

            # Use WAL mode and timeout to prevent database locking issues
            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA busy_timeout=30000")
            cursor = db.cursor()

            # Calculate total value
            quantity = order.get('quantity', 0)
            price = order.get('filled_avg_price') or order.get('price', 0)
            total_value = quantity * price if price > 0 else 0

            # Get confidence value (ensure it's a valid number)
            confidence_value = signal.get('confidence', 0.5)
            if confidence_value is None:
                confidence_value = 0.5

            # Insert into trade_history with all fields (FIXED: include both confidence and ai_confidence)
            cursor.execute("""
                INSERT INTO trade_history
                (symbol, action, quantity, price, total_value, broker, confidence, ai_confidence,
                 reasoning, timestamp, order_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal['symbol'],
                signal['action'],
                quantity,
                price,
                total_value,
                broker,
                confidence_value,  # Required NOT NULL confidence column
                confidence_value,  # ai_confidence column (same value)
                signal.get('reasoning', '')[:500] if signal.get('reasoning') else '',
                datetime.now().isoformat(),
                order.get('id') or order.get('order_id', 'unknown'),
                order.get('status', 'executed')
            ))

            db.commit()

            # Also update performance metrics
            cursor.execute("""
                INSERT INTO performance_metrics
                (timestamp, total_trades, current_balance)
                VALUES (?, 1, ?)
            """, (
                datetime.now().isoformat(),
                total_value
            ))

            db.commit()
            db.close()

            self.logger.info(f" Trade recorded in learning database: {signal['symbol']} {signal['action']} @ ${price:.2f}")

            # Increment trade counter and check for automatic training trigger
            self.trade_count_since_training += 1
            if self.trade_count_since_training >= self.training_trigger_threshold:
                await self._trigger_automatic_training()

        except Exception as e:
            self.logger.warning(f"Could not record trade in database: {e}")

    async def _trigger_automatic_training(self):
        """Trigger automatic supervised learning training after threshold trades"""
        try:
            self.logger.info(f"🧠 Triggering automatic supervised learning training (after {self.trade_count_since_training} trades)")

            from train_prometheus_supervised import SupervisedLearningPipeline

            pipeline = SupervisedLearningPipeline()
            metrics = pipeline.run_training(min_trades=10)

            if metrics:
                self.logger.info(f"✅ Training complete: {metrics.success_rate:.1%} success rate, {metrics.improvement_pct:.1f}% improvement")
                self.logger.info(f"🎯 Optimal confidence threshold: {metrics.optimal_confidence_threshold:.2f}")

            # Reset counter
            self.trade_count_since_training = 0
            self.last_training_time = datetime.now()

        except Exception as e:
            self.logger.warning(f"⚠️ Automatic training failed: {e}")

    async def _store_signal_prediction(self, signal: Dict[str, Any]):
        """Store AI signal prediction for later learning comparison"""
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            db.execute("PRAGMA journal_mode=WAL")
            cursor = db.cursor()

            # Create predictions table if not exists
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

            cursor.execute("""
                INSERT INTO signal_predictions
                (timestamp, symbol, action, confidence, entry_price, target_price, stop_loss,
                 ai_components, vote_breakdown, reasoning, market_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal['timestamp'].isoformat() if hasattr(signal['timestamp'], 'isoformat') else str(signal['timestamp']),
                signal['symbol'],
                signal['action'],
                self._apply_confidence_calibration(signal['confidence']),
                signal.get('entry_price', 0),
                signal.get('target_price', 0),
                signal.get('stop_loss', 0),
                str(signal.get('ai_components', [])),
                str(signal.get('vote_breakdown', {})),
                signal.get('reasoning', ''),
                str(signal.get('market_data', {}))
            ))

            db.commit()
            db.close()

            self.logger.debug(f"📝 Signal prediction stored: {signal['symbol']} {signal['action']}")

        except Exception as e:
            self.logger.warning(f"Could not store signal prediction: {e}")

    def _cleanup_position_tracking(self, symbol: str):
        """
        🧹 CLEANUP POSITION TRACKING
        Called when a position is fully closed to clear tracking dictionaries and database
        """
        cleaned = []

        if symbol in self.position_highs:
            del self.position_highs[symbol]
            cleaned.append("position_highs")

        if symbol in self.position_entry_times:
            del self.position_entry_times[symbol]
            cleaned.append("position_entry_times")

        if symbol in self.scaled_positions:
            del self.scaled_positions[symbol]
            cleaned.append("scaled_positions")

        if symbol in self.dca_counts:
            del self.dca_counts[symbol]
            cleaned.append("dca_counts")

        if symbol in self.position_trade_ids:
            del self.position_trade_ids[symbol]
            cleaned.append("position_trade_ids")

        # Also delete from database
        try:
            import sqlite3
            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            db.execute("DELETE FROM position_tracking WHERE symbol = ?", (symbol,))
            db.commit()
            db.close()
            cleaned.append("database")
        except Exception as e:
            self.logger.warning(f"Could not delete position tracking from database: {e}")

        if cleaned:
            self.logger.debug(f"🧹 Cleaned up tracking for {symbol}: {', '.join(cleaned)}")

    def _load_position_tracking(self):
        """
        📥 LOAD POSITION TRACKING FROM DATABASE
        Called on startup to restore position tracking data that survives restarts
        """
        try:
            import sqlite3
            from datetime import datetime as dt

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            cursor = db.cursor()

            cursor.execute("SELECT symbol, position_high, entry_time, scaled_level, dca_count, trade_id FROM position_tracking")
            rows = cursor.fetchall()

            loaded_count = 0
            for row in rows:
                symbol, position_high, entry_time, scaled_level, dca_count, trade_id = row

                if position_high is not None:
                    self.position_highs[symbol] = position_high

                if entry_time is not None:
                    try:
                        self.position_entry_times[symbol] = dt.fromisoformat(entry_time)
                    except:
                        self.position_entry_times[symbol] = dt.now()

                if scaled_level is not None:
                    self.scaled_positions[symbol] = scaled_level

                if dca_count is not None:
                    self.dca_counts[symbol] = dca_count

                if trade_id is not None:
                    self.position_trade_ids[symbol] = trade_id

                loaded_count += 1

            db.close()

            if loaded_count > 0:
                self.logger.info(f"📥 Loaded position tracking for {loaded_count} symbols from database")
                self.logger.info(f"   position_highs: {list(self.position_highs.keys())}")
                self.logger.info(f"   position_entry_times: {list(self.position_entry_times.keys())}")
                self.logger.info(f"   scaled_positions: {list(self.scaled_positions.keys())}")
                self.logger.info(f"   dca_counts: {list(self.dca_counts.keys())}")
                self.logger.info(f"   position_trade_ids: {list(self.position_trade_ids.keys())}")

        except Exception as e:
            self.logger.warning(f"Could not load position tracking from database: {e}")

    def _save_position_tracking(self, symbol: str):
        """
        💾 SAVE POSITION TRACKING TO DATABASE
        Called when tracking data is updated to persist it for restart survival
        """
        try:
            import sqlite3
            from datetime import datetime as dt

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            cursor = db.cursor()

            # Get current values for this symbol
            position_high = self.position_highs.get(symbol)
            entry_time = self.position_entry_times.get(symbol)
            entry_time_str = entry_time.isoformat() if entry_time else None
            scaled_level = self.scaled_positions.get(symbol, 0)
            dca_count = self.dca_counts.get(symbol, 0)
            trade_id = self.position_trade_ids.get(symbol)

            # Upsert (INSERT OR REPLACE) the tracking data
            cursor.execute("""
                INSERT OR REPLACE INTO position_tracking
                (symbol, position_high, entry_time, scaled_level, dca_count, trade_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                position_high,
                entry_time_str,
                scaled_level,
                dca_count,
                trade_id,
                dt.now().isoformat()
            ))

            db.commit()
            db.close()

        except Exception as e:
            self.logger.warning(f"Could not save position tracking to database: {e}")

    async def _record_learning_outcome(self, symbol: str, entry_price: float, exit_price: float,
                                        quantity: float, profit_loss: float, profit_pct: float,
                                        exit_reason: str, broker: str):
        """
        🧠 LEARNING FEEDBACK LOOP
        Feed trade outcomes to both learning engines for continuous improvement
        """
        try:
            self.logger.info(f"🧠 Recording learning outcome for {symbol}: P/L={profit_loss:+.2f} ({profit_pct*100:+.2f}%)")

            # Get the original signal prediction for this trade
            original_prediction = await self._get_original_prediction(symbol)

            # Calculate actual trade duration from position entry times
            from datetime import timedelta
            entry_time = self.position_entry_times.get(symbol)
            if entry_time:
                trade_duration = datetime.now() - entry_time
            else:
                trade_duration = timedelta(hours=1)  # Fallback if entry time not tracked

            # Determine if prediction was correct
            _pred_action = original_prediction.get('action', 'HOLD')
            was_correct = (_pred_action in ['BUY', 'STRONG_BUY'] and profit_loss > 0) or \
                         (_pred_action in ['SELL', 'STRONG_SELL'] and profit_loss > 0) or \
                         (_pred_action == 'HOLD' and abs(profit_pct or 0.0) < 1.0)  # HOLD correct if price barely moved (<1%)

            # ═══════════════════════════════════════════════════════════════
            # 📊 CONTINUOUS LEARNING ENGINE - Statistical Learning
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('continuous_learning'):
                try:
                    from core.continuous_learning_engine import TradingOutcome

                    outcome = TradingOutcome(
                        trade_id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}",
                        timestamp=datetime.now(),
                        symbol=symbol,
                        action=original_prediction.get('action', 'BUY'),
                        entry_price=entry_price,
                        exit_price=exit_price,
                        quantity=quantity,
                        profit_loss=profit_loss,
                        duration=trade_duration,
                        market_conditions=original_prediction.get('market_data', {}),
                        model_confidence=original_prediction.get('confidence', 0.5),
                        model_version='prometheus_v1',
                        features_used={'ai_components': original_prediction.get('ai_components', [])},
                        risk_metrics={'profit_pct': profit_pct, 'exit_reason': exit_reason}
                    )

                    await self.systems['continuous_learning'].record_trading_outcome(outcome)
                    self.logger.info(f"✅ Continuous learning recorded: {symbol}")

                except Exception as e:
                    self.logger.warning(f"Continuous learning recording failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🧬 ADVANCED AI LEARNING ENGINE - Pattern Recognition
            # ═══════════════════════════════════════════════════════════════
            if self.systems.get('ai_learning'):
                try:
                    trade_data = {
                        'symbol': symbol,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'quantity': quantity,
                        'profit_loss': profit_loss,
                        'profit_pct': profit_pct,
                        'exit_reason': exit_reason,
                        'broker': broker,
                        'volatility': original_prediction.get('market_data', {}).get('volatility', 0.02),
                        'volume': original_prediction.get('market_data', {}).get('volume', 0),
                        'price_change_24h': original_prediction.get('market_data', {}).get('price_change_24h', 0)
                    }

                    prediction_data = {
                        'action': original_prediction.get('action', 'HOLD'),
                        'confidence': original_prediction.get('confidence', 0.5),
                        'target_price': original_prediction.get('target_price', 0),
                        'stop_loss': original_prediction.get('stop_loss', 0),
                        'ai_components': original_prediction.get('ai_components', []),
                        'vote_breakdown': original_prediction.get('vote_breakdown', {})
                    }

                    actual_outcome = {
                        'pnl': profit_loss,
                        'pnl_pct': profit_pct,
                        'success': profit_loss > 0,
                        'was_prediction_correct': was_correct,
                        'exit_reason': exit_reason
                    }

                    learning_instance = await self.systems['ai_learning'].learn_from_trade(
                        trade_data=trade_data,
                        prediction_data=prediction_data,
                        actual_outcome=actual_outcome
                    )

                    self.logger.info(f"✅ AI learning recorded: {symbol} (learning_value={learning_instance.learning_value:.3f})")

                except Exception as e:
                    self.logger.warning(f"AI learning recording failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📈 RECORD OUTCOME IN DATABASE - For Long-term Analysis
            # ═══════════════════════════════════════════════════════════════
            await self._persist_learning_outcome(symbol, entry_price, exit_price, profit_loss,
                                                  profit_pct, was_correct, original_prediction, exit_reason)

            # ═══════════════════════════════════════════════════════════════
            # 🎯 AI ATTRIBUTION TRACKER - Record Outcome for AI Leaderboard
            # Uses trade_id to match outcome with the signal that created this trade
            # ═══════════════════════════════════════════════════════════════
            try:
                tracker = get_attribution_tracker()
                # Get the trade_id we stored when the trade was executed
                trade_id = self.position_trade_ids.get(symbol)
                await tracker.record_outcome(
                    symbol=symbol,
                    pnl=profit_loss,
                    pnl_pct=profit_pct,
                    trade_id=trade_id
                )
                if trade_id:
                    self.logger.info(f"🎯 AI Attribution outcome recorded for {symbol} (trade_id={trade_id})")
                else:
                    self.logger.debug(f"🎯 AI Attribution outcome recorded for {symbol} (no trade_id)")
            except Exception as attr_err:
                self.logger.debug(f"Attribution outcome recording skipped: {attr_err}")

            # Log learning summary
            emoji = "🎓" if was_correct else "📚"
            self.logger.info(f"{emoji} Learning complete for {symbol}: prediction_correct={was_correct}, "
                           f"P/L={profit_loss:+.2f} ({profit_pct*100:+.2f}%)")

        except Exception as e:
            self.logger.error(f"Error recording learning outcome: {e}")

    async def _get_original_prediction(self, symbol: str) -> Dict[str, Any]:
        """Retrieve the original AI prediction for a symbol"""
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            cursor = db.cursor()

            # Get most recent unprocessed prediction for this symbol
            cursor.execute("""
                SELECT action, confidence, entry_price, target_price, stop_loss,
                       ai_components, vote_breakdown, reasoning, market_data
                FROM signal_predictions
                WHERE symbol = ? AND outcome_recorded = 0
                ORDER BY timestamp DESC LIMIT 1
            """, (symbol,))

            row = cursor.fetchone()
            db.close()

            if row:
                return {
                    'action': row[0],
                    'confidence': row[1],
                    'entry_price': row[2],
                    'target_price': row[3],
                    'stop_loss': row[4],
                    'ai_components': ast.literal_eval(row[5]) if row[5] else [],
                    'vote_breakdown': ast.literal_eval(row[6]) if row[6] else {},
                    'reasoning': row[7],
                    'market_data': ast.literal_eval(row[8]) if row[8] else {}
                }

            return {'action': 'HOLD', 'confidence': 0.5, 'ai_components': [], 'market_data': {}}

        except Exception as e:
            self.logger.warning(f"Could not retrieve original prediction: {e}")
            return {'action': 'HOLD', 'confidence': 0.5, 'ai_components': [], 'market_data': {}}

    @staticmethod
    def _normalize_symbol_variants(symbol: str):
        """Return list of symbol format variants to match DB entries.
        Alpaca positions use 'BTCUSD', signals may use 'BTC/USD'."""
        variants = [symbol]
        # BTCUSD -> BTC/USD
        if '/' not in symbol and symbol.endswith('USD') and len(symbol) > 3:
            variants.append(symbol[:-3] + '/USD')
        # BTC/USD -> BTCUSD
        if '/' in symbol:
            variants.append(symbol.replace('/', ''))
        return list(dict.fromkeys(variants))  # dedupe, preserve order

    async def _persist_learning_outcome(self, symbol: str, entry_price: float, exit_price: float,
                                         profit_loss: float, profit_pct: float, was_correct: bool,
                                         original_prediction: Dict[str, Any], exit_reason: str = 'UNKNOWN'):
        """Persist learning outcome to database for long-term analysis"""
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            db.execute("PRAGMA journal_mode=WAL")
            cursor = db.cursor()

            # Create learning outcomes table if not exists
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

            cursor.execute("""
                INSERT INTO learning_outcomes
                (timestamp, symbol, predicted_action, predicted_confidence, entry_price, exit_price,
                 profit_loss, profit_pct, was_correct, ai_components, learning_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                symbol,
                original_prediction.get('action', 'HOLD'),
                original_prediction.get('confidence', 0.5),
                entry_price,
                exit_price,
                profit_loss,
                profit_pct,
                1 if was_correct else 0,
                str(original_prediction.get('ai_components', [])),
                f"Prediction correct: {was_correct}"
            ))

            # Mark the original prediction as processed
            cursor.execute("""
                UPDATE signal_predictions
                SET outcome_recorded = 1
                WHERE symbol = ? AND outcome_recorded = 0
            """, (symbol,))

            # ═══════════════════════════════════════════════════════════════
            # 💰 UPDATE TRADE_HISTORY WITH ACTUAL PROFIT/LOSS
            # This is CRITICAL for supervised learning to work with real outcomes
            #
            # FIX: Must target BUY rows only — SELL orders also get inserted
            # into trade_history (via record_trade_in_database), so the old
            # query would match the SELL row (most recent) instead of the
            # original BUY row, setting exit_price = entry_price = $0 P/L.
            # ═══════════════════════════════════════════════════════════════

            # Calculate actual hold duration from trade_history timestamp
            # FIX: Try all symbol format variants (BTCUSD vs BTC/USD)
            sym_variants = self._normalize_symbol_variants(symbol)
            placeholders = ','.join('?' * len(sym_variants))

            hold_secs = 3600  # fallback
            cursor.execute(f"""
                SELECT timestamp FROM trade_history
                WHERE symbol IN ({placeholders}) AND action = 'BUY'
                AND (exit_price IS NULL OR profit_loss = 0)
                ORDER BY timestamp DESC LIMIT 1
            """, sym_variants)
            _entry_row = cursor.fetchone()
            if _entry_row and _entry_row[0]:
                try:
                    _entry_ts = datetime.fromisoformat(_entry_row[0])
                    hold_secs = int((datetime.now() - _entry_ts).total_seconds())
                except Exception:
                    pass

            cursor.execute(f"""
                UPDATE trade_history
                SET profit_loss = ?,
                    exit_price = ?,
                    exit_timestamp = ?,
                    hold_duration_seconds = ?,
                    exit_reason = ?
                WHERE action = 'BUY'
                AND (exit_price IS NULL OR profit_loss = 0)
                AND id = (
                    SELECT id FROM trade_history
                    WHERE symbol IN ({placeholders}) AND action = 'BUY'
                    AND (exit_price IS NULL OR profit_loss = 0)
                    ORDER BY timestamp DESC LIMIT 1
                )
            """, [
                profit_loss,
                exit_price,
                datetime.now().isoformat(),
                hold_secs,
                exit_reason,
            ] + sym_variants)

            rows_updated = cursor.rowcount
            if rows_updated > 0:
                self.logger.info(f"💰 Trade history updated with P/L: {symbol} ${profit_loss:+.2f} ({profit_pct*100:+.2f}%) [Exit: {exit_reason}]")
            else:
                self.logger.debug(f"📝 No open trade found to update for {symbol} (tried: {sym_variants})")

            db.commit()
            db.close()

            self.logger.debug(f"📊 Learning outcome persisted to database: {symbol}")

        except Exception as e:
            self.logger.warning(f"Could not persist learning outcome: {e}")

    def _calculate_learning_progress_score(self) -> Dict[str, Any]:
        """
        Calculate a daily learning/adaptation score from persisted outcomes.

        Score range: 0-100 based on the last 7 days of data.
        """
        try:
            import sqlite3

            db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
            cursor = db.cursor()

            # Learning outcomes tracked in the dedicated outcomes table.
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END)
                FROM learning_outcomes
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            outcomes_row = cursor.fetchone() or (0, 0)
            outcomes_7d = outcomes_row[0] or 0
            correct_7d = outcomes_row[1] or 0
            accuracy_7d = (correct_7d / outcomes_7d) if outcomes_7d > 0 else 0.0

            # Closed trades in the same lookback for realized adaptation signal.
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)
                FROM trade_history
                WHERE exit_timestamp IS NOT NULL
                  AND exit_timestamp >= datetime('now', '-7 days')
            """)
            closed_row = cursor.fetchone() or (0, 0)
            closed_7d = closed_row[0] or 0
            wins_7d = closed_row[1] or 0
            win_rate_7d = (wins_7d / closed_7d) if closed_7d > 0 else 0.0

            # Prediction coverage: how much the system is collecting data to learn from.
            cursor.execute("""
                SELECT COUNT(*)
                FROM signal_predictions
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            predictions_7d = (cursor.fetchone() or (0,))[0] or 0

            db.close()

            # Normalize components to a stable 0-100 score.
            # - Accuracy quality (40%)
            # - Realized trade quality (35%)
            # - Data volume/coverage (25%, saturates at 200 predictions/week)
            accuracy_component = min(100.0, max(0.0, accuracy_7d * 100.0))
            win_rate_component = min(100.0, max(0.0, win_rate_7d * 100.0))
            coverage_component = min(100.0, (predictions_7d / 200.0) * 100.0)

            score = (
                accuracy_component * 0.40 +
                win_rate_component * 0.35 +
                coverage_component * 0.25
            )

            return {
                'score': round(score, 2),
                'accuracy_7d_pct': round(accuracy_7d * 100.0, 2),
                'win_rate_7d_pct': round(win_rate_7d * 100.0, 2),
                'predictions_7d': int(predictions_7d),
                'outcomes_7d': int(outcomes_7d),
                'closed_trades_7d': int(closed_7d),
            }

        except Exception as e:
            self.logger.warning(f"Could not calculate learning progress score: {e}")
            return {
                'score': 0.0,
                'accuracy_7d_pct': 0.0,
                'win_rate_7d_pct': 0.0,
                'predictions_7d': 0,
                'outcomes_7d': 0,
                'closed_trades_7d': 0,
            }

    async def _log_daily_learning_progress(self):
        """Log a once-per-day learning/adaptation progress summary."""
        metrics = self._calculate_learning_progress_score()
        score = metrics.get('score', 0.0)

        if score >= 80:
            grade = 'A'
        elif score >= 65:
            grade = 'B'
        elif score >= 50:
            grade = 'C'
        else:
            grade = 'D'

        self.logger.info("=" * 70)
        self.logger.info(f"DAILY LEARNING PROGRESS | SCORE={score:.2f}/100 | GRADE={grade}")
        self.logger.info(
            f"7D accuracy={metrics.get('accuracy_7d_pct', 0.0):.2f}% | "
            f"7D win_rate={metrics.get('win_rate_7d_pct', 0.0):.2f}% | "
            f"7D predictions={metrics.get('predictions_7d', 0)} | "
            f"7D outcomes={metrics.get('outcomes_7d', 0)} | "
            f"7D closed_trades={metrics.get('closed_trades_7d', 0)}"
        )
        self.logger.info("=" * 70)

    def _is_alpaca_24hr_stock(self, symbol: str) -> bool:
        """Check if stock supports Alpaca 24-hour trading"""
        # Alpaca 24-hour trading supported stocks
        # Trading hours: Sunday 8 PM ET - Friday 8 PM ET
        ALPACA_24HR_STOCKS = {
            # Tech Giants
            'AAPL',   # Apple
            'MSFT',   # Microsoft
            'GOOGL',  # Google
            'GOOG',   # Google (Class C)
            'AMZN',   # Amazon
            'META',   # Meta/Facebook
            'NVDA',   # NVIDIA
            'TSLA',   # Tesla
            'NFLX',   # Netflix
            'AMD',    # AMD

            # Major ETFs
            'SPY',    # S&P 500 ETF
            'QQQ',    # Nasdaq 100 ETF
            'IWM',    # Russell 2000 ETF
            'DIA',    # Dow Jones ETF
            'VOO',    # Vanguard S&P 500 ETF

            # Other Popular Stocks
            'COIN',   # Coinbase
            'PLTR',   # Palantir
            'BABA',   # Alibaba
            'CRM',    # Salesforce
            'ORCL',   # Oracle
            'INTC',   # Intel
            'MU',     # Micron
            'QCOM',   # Qualcomm
        }

        return symbol.upper() in ALPACA_24HR_STOCKS

    def _extract_account_cash(self, account: Any) -> float:
        """Extract account cash from account objects with varying field names."""
        if not account:
            return 0.0

        candidates = []
        for attr in ('cash', 'buying_power', 'buyingPower', 'total_cash_value', 'available_funds'):
            try:
                value = getattr(account, attr, None)
                if value is not None:
                    candidates.append(value)
            except Exception:
                continue

        if isinstance(account, dict):
            for key in ('cash', 'buying_power', 'buyingPower', 'total_cash_value', 'available_funds'):
                if key in account:
                    candidates.append(account.get(key))

        for value in candidates:
            try:
                numeric = float(value)
                if numeric >= 0:
                    return numeric
            except Exception:
                continue

        return 0.0

    async def _get_broker_cash_balances(self, alpaca_broker: Any, ib_broker: Any) -> Dict[str, float]:
        """Fetch latest cash balances for routing decisions."""
        balances = {'ib_cash': 0.0, 'alpaca_cash': 0.0}

        try:
            if ib_broker:
                # Keep IB routing healthy: if the session dropped, try reconnecting
                # before evaluating cash-based broker selection.
                if not getattr(ib_broker, 'connected', False):
                    try:
                        await ib_broker.connect()
                    except Exception as reconnect_err:
                        self.logger.debug(f"IB reconnect attempt failed during routing: {reconnect_err}")
                ib_account = await ib_broker.get_account()
                balances['ib_cash'] = self._extract_account_cash(ib_account)
        except Exception as e:
            self.logger.debug(f"Could not get IB cash: {e}")

        try:
            if alpaca_broker:
                alp_account = await alpaca_broker.get_account()
                balances['alpaca_cash'] = self._extract_account_cash(alp_account)
        except Exception as e:
            self.logger.debug(f"Could not get Alpaca cash: {e}")

        return balances

    def _get_ib_allocation_share(self) -> float:
        """Return realized share of routed trades sent to IB."""
        ib_count = self.routing_execution_counts.get('ib', 0)
        alpaca_count = self.routing_execution_counts.get('alpaca', 0)
        total = ib_count + alpaca_count
        if total <= 0:
            return 0.0
        return ib_count / total

    def _load_routing_stats(self):
        """Load persisted router execution counts so allocation share survives restarts."""
        try:
            import sqlite3
            db = sqlite3.connect('prometheus_learning.db', timeout=10.0)
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routing_policy_stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    ib_count INTEGER DEFAULT 0,
                    alpaca_count INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            """)
            cursor.execute("SELECT ib_count, alpaca_count FROM routing_policy_stats WHERE id = 1")
            row = cursor.fetchone()
            if row:
                self.routing_execution_counts['ib'] = int(row[0] or 0)
                self.routing_execution_counts['alpaca'] = int(row[1] or 0)
            else:
                cursor.execute(
                    "INSERT INTO routing_policy_stats (id, ib_count, alpaca_count, updated_at) VALUES (1, 0, 0, ?)",
                    (datetime.now().isoformat(),)
                )
            db.commit()
            db.close()
        except Exception as e:
            self.logger.debug(f"Could not load routing stats: {e}")

    def _persist_routing_stats(self):
        """Persist router execution counts for gradual autonomous adaptation across restarts."""
        try:
            import sqlite3
            db = sqlite3.connect('prometheus_learning.db', timeout=10.0)
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS routing_policy_stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    ib_count INTEGER DEFAULT 0,
                    alpaca_count INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO routing_policy_stats (id, ib_count, alpaca_count, updated_at)
                VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    ib_count = excluded.ib_count,
                    alpaca_count = excluded.alpaca_count,
                    updated_at = excluded.updated_at
            """, (
                int(self.routing_execution_counts.get('ib', 0)),
                int(self.routing_execution_counts.get('alpaca', 0)),
                datetime.now().isoformat(),
            ))
            db.commit()
            db.close()
        except Exception as e:
            self.logger.debug(f"Could not persist routing stats: {e}")

    def _is_regular_market_hours_open(self) -> bool:
        """Return True only during US regular market hours."""
        if not MARKET_HOURS_UTILS_AVAILABLE:
            return False
        try:
            from core.market_hours_utils import is_market_open
            return bool(is_market_open(include_extended_hours=False))
        except Exception:
            return False

    async def _select_legacy_broker_for_symbol(self, symbol: str, alpaca_broker: Any, ib_broker: Any):
        """Current production routing behavior preserved for safe fallback."""
        if '/' in symbol:
            return alpaca_broker, 'Alpaca', {'selected': 'Alpaca', 'reason': 'crypto_alpaca_only', 'ib_cash': 0.0, 'alpaca_cash': 0.0}

        if self._is_alpaca_24hr_stock(symbol):
            return alpaca_broker, 'Alpaca', {'selected': 'Alpaca', 'reason': 'alpaca_24hr_hard_override', 'ib_cash': 0.0, 'alpaca_cash': 0.0}

        balances = await self._get_broker_cash_balances(alpaca_broker, ib_broker)
        ib_cash = balances['ib_cash']
        alpaca_cash = balances['alpaca_cash']

        if ib_broker and ib_cash > alpaca_cash and ib_cash > 10:
            return ib_broker, 'IB', {'selected': 'IB', 'reason': 'legacy_cash_compare', 'ib_cash': ib_cash, 'alpaca_cash': alpaca_cash}
        if alpaca_broker and alpaca_cash > 0:
            return alpaca_broker, 'Alpaca', {'selected': 'Alpaca', 'reason': 'legacy_cash_compare', 'ib_cash': ib_cash, 'alpaca_cash': alpaca_cash}

        broker = ib_broker or alpaca_broker
        broker_name = 'IB' if ib_broker else 'Alpaca'
        return broker, broker_name, {'selected': broker_name, 'reason': 'legacy_fallback', 'ib_cash': ib_cash, 'alpaca_cash': alpaca_cash}

    async def _select_broker_for_symbol(self, symbol: str, alpaca_broker: Any, ib_broker: Any):
        """Autonomous policy-based routing with guardrails and IB allocation floor."""
        if '/' in symbol:
            return alpaca_broker, 'Alpaca', {'selected': 'Alpaca', 'reason': 'crypto_capability', 'ib_cash': 0.0, 'alpaca_cash': 0.0, 'ib_allocation_share': self._get_ib_allocation_share()}

        balances = await self._get_broker_cash_balances(alpaca_broker, ib_broker)
        ib_cash = balances['ib_cash']
        alpaca_cash = balances['alpaca_cash']
        is_24hr_symbol = self._is_alpaca_24hr_stock(symbol)

        ib_share = self._get_ib_allocation_share()

        # Preserve strict behavior only when explicitly enabled.
        if is_24hr_symbol and self.alpaca_24hr_hard_override:
            return alpaca_broker, 'Alpaca', {
                'selected': 'Alpaca',
                'reason': 'alpaca_24hr_hard_override',
                'ib_cash': ib_cash,
                'alpaca_cash': alpaca_cash,
                'ib_allocation_share': ib_share,
            }

        if ib_broker and ib_cash > 10 and ib_share < self.ib_min_allocation_pct:
            return ib_broker, 'IB', {
                'selected': 'IB',
                'reason': 'ib_allocation_floor',
                'ib_cash': ib_cash,
                'alpaca_cash': alpaca_cash,
                'ib_allocation_share': ib_share,
            }

        # Cost-aware score (lower estimated cost gets higher score), plus cash readiness.
        ib_cost = self.trading_costs.get('ib', {}).get('stocks', {}).get('total_per_trade', 0.001)
        alpaca_cost = self.trading_costs.get('alpaca', {}).get('stocks', {}).get('total_per_trade', 0.0007)
        ib_score = (1.0 - ib_cost) + min(ib_cash / 1000.0, 1.0)
        alpaca_score = (1.0 - alpaca_cost) + min(alpaca_cash / 1000.0, 1.0)

        if self._is_regular_market_hours_open():
            # Prefer IB during regular hours without hard-locking all orders to IB.
            ib_score += self.ib_regular_hours_bonus

        if is_24hr_symbol:
            alpaca_score += 0.15

        if ib_broker and ib_cash > 10 and ib_score > alpaca_score:
            return ib_broker, 'IB', {
                'selected': 'IB',
                'reason': 'autonomous_score',
                'ib_cash': ib_cash,
                'alpaca_cash': alpaca_cash,
                'ib_allocation_share': ib_share,
            }

        if alpaca_broker and alpaca_cash > 0:
            return alpaca_broker, 'Alpaca', {
                'selected': 'Alpaca',
                'reason': 'autonomous_score',
                'ib_cash': ib_cash,
                'alpaca_cash': alpaca_cash,
                'ib_allocation_share': ib_share,
            }

        broker = ib_broker or alpaca_broker
        broker_name = 'IB' if ib_broker else 'Alpaca'
        return broker, broker_name, {
            'selected': broker_name,
            'reason': 'autonomous_fallback',
            'ib_cash': ib_cash,
            'alpaca_cash': alpaca_cash,
            'ib_allocation_share': ib_share,
        }

    async def run_forever(self):
        """Main trading loop - runs continuously"""
        print("\n" + "=" * 80)
        print(" PROMETHEUS LIVE TRADING ACTIVE")
        print("=" * 80)

        # Display timezone-aware market status
        if MARKET_HOURS_UTILS_AVAILABLE:
            try:
                print("\n" + format_market_status())
                print()
            except Exception as e:
                self.logger.warning(f"Could not display market status: {e}")

        print(f"Trading Style: {self.trading_style}")
        print(f"Market Regime: {self.market_regime}")
        print(f"Systems Active: {len([s for s in self.system_health.values() if s == 'ACTIVE'])}")
        
        # Display broker and AI status
        alpaca_status = '✅ CONNECTED' if 'alpaca_broker' in self.systems and self.systems.get('alpaca_broker') else '❌ NOT CONNECTED'
        ib_status = '✅ CONNECTED' if ('ib_broker' in self.systems and 
                                     self.systems.get('ib_broker') and 
                                     hasattr(self.systems['ib_broker'], 'connected') and
                                     self.systems['ib_broker'].connected) else f'❌ NOT CONNECTED (port {self.ib_port})'
        # Get detailed CPT-OSS status
        gpt_oss_status = '❌ NOT AVAILABLE'
        if 'gpt_oss' in self.systems and self.systems.get('gpt_oss'):
            try:
                model_size = getattr(self.systems['gpt_oss'], 'model_size', '20b')
                gpt_oss_status = f"✅ ACTIVE (CPT-OSS {model_size})"
            except:
                gpt_oss_status = '✅ ACTIVE'
        
        # Check backend server status
        backend_status = '❌ NOT RUNNING'
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex(('127.0.0.1', 8000)) == 0:
                backend_status = '✅ RUNNING (port 8000)'
            elif sock.connect_ex(('127.0.0.1', 8001)) == 0:
                backend_status = '✅ RUNNING (port 8001)'
            sock.close()
        except:
            pass
        
        print(f"\n📊 System Status:")
        print(f"   Alpaca: {alpaca_status}")
        print(f"   IB: {ib_status}")
        print(f"   CPT-OSS: {gpt_oss_status}")
        print(f"   Backend: {backend_status}")
        print("=" * 80)

        cycle = 0
        while True:
            try:
                cycle += 1

                # Daily learning/adaptation proof point (logged once per calendar day).
                today = datetime.now().date()
                if self.last_learning_score_date != today:
                    await self._log_daily_learning_progress()
                    self.last_learning_score_date = today

                # Keep lifecycle data fresh during long-running sessions.
                # Reconcile stale pending rows at most once per hour.
                if (datetime.now() - getattr(self, 'last_pending_reconcile_at', datetime.min)).total_seconds() >= 3600:
                    self._reconcile_stale_pending_trades(max_age_hours=72)
                    self.last_pending_reconcile_at = datetime.now()

                # Monitor resources
                resources_ok = await self.monitor_resources()
                if not resources_ok:
                    self.logger.critical("Resource limits exceeded - pausing trading")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue

                # Adapt trading style every 60 seconds
                await self.adapt_trading_style()

                #  RUN TRADING CYCLE - ANALYZE MARKETS AND EXECUTE TRADES
                await self.run_trading_cycle()

                # Health check
                active_systems = len([s for s in self.system_health.values() if s == 'ACTIVE'])

                # Show both local and Eastern time
                local_time = datetime.now().strftime('%H:%M:%S')
                if MARKET_HOURS_UTILS_AVAILABLE:
                    try:
                        eastern_time = get_eastern_time()
                        time_display = f"{local_time} (ET: {eastern_time.strftime('%I:%M:%S %p')})"
                    except:
                        time_display = local_time
                else:
                    time_display = local_time

                # Display broker status
                alpaca_status = '✅' if 'alpaca_broker' in self.systems and self.systems.get('alpaca_broker') else '❌'
                ib_status = '✅' if ('ib_broker' in self.systems and 
                                   self.systems.get('ib_broker') and 
                                   hasattr(self.systems['ib_broker'], 'connected') and
                                   self.systems['ib_broker'].connected) else '❌'
                
                # Get detailed CPT-OSS status
                gpt_oss_detail = '❌ NOT AVAILABLE'
                if 'gpt_oss' in self.systems and self.systems.get('gpt_oss'):
                    try:
                        model_size = getattr(self.systems['gpt_oss'], 'model_size', '20b')
                        gpt_oss_detail = f"✅ ACTIVE (CPT-OSS {model_size})"
                    except:
                        gpt_oss_detail = '✅ ACTIVE'
                
                # Check backend server
                backend_status = '❌ NOT RUNNING'
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    if sock.connect_ex(('127.0.0.1', 8000)) == 0:
                        backend_status = '✅ RUNNING (port 8000)'
                    elif sock.connect_ex(('127.0.0.1', 8001)) == 0:
                        backend_status = '✅ RUNNING (port 8001)'
                    sock.close()
                except:
                    pass
                
                print(f"\n{'='*80}")
                print(f"🔄 TRADING CYCLE {cycle} - {time_display}")
                print(f"{'='*80}")
                print(f"   Health: {active_systems} systems active")
                print(f"   Brokers: Alpaca {alpaca_status} | IB {ib_status} (port {self.ib_port})")
                print(f"   CPT-OSS: {gpt_oss_detail}")
                print(f"   Backend: {backend_status}")
                print(f"{'='*80}")

                # Sleep for 30 seconds before next cycle - faster execution for more opportunities
                await asyncio.sleep(30)

            except KeyboardInterrupt:
                print("\n\n Shutdown requested...")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(30)  # Faster recovery for more opportunities

        print("\n" + "=" * 80)
        print(" PROMETHEUS LIVE TRADING STOPPED")
        print("=" * 80)

    def _setup_api_endpoints(self):
        """Setup FastAPI endpoints for web interface (STANDALONE MODE ONLY)"""
        if not self.standalone_mode or not self.app:
            self.logger.warning("[WARNING] _setup_api_endpoints called but not in standalone mode")
            return

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "systems_active": len([s for s in self.system_health.values() if s == 'ACTIVE']),
                "total_systems": len(self.system_health)
            }
        
        @self.app.get("/api/revolutionary/engines/status")
        async def get_revolutionary_engines_status():
            """Get status of all revolutionary engines"""
            return {
                "success": True,
                "engines": {
                    "crypto": "active" if self.systems.get('crypto_engine') else "not_initialized",
                    "options": "active" if self.systems.get('options_engine') else "not_initialized", 
                    "advanced": "active" if self.systems.get('advanced_engine') else "not_initialized",
                    "market_maker": "active" if self.systems.get('market_maker') else "not_initialized",
                    "master": "active" if self.systems.get('master_engine') else "not_initialized"
                },
                "total_engines": 5,
                "available_engines": len([e for e in self.systems.values() if e]),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/ai/analyze")
        async def analyze_with_ai(request: dict):
            """AI analysis endpoint using GPT-OSS fallback"""
            try:
                from force_real_gpt_oss import RealGPTOSS
                
                prompt = request.get("prompt", "")
                if not prompt:
                    raise HTTPException(status_code=400, detail="Prompt is required")
                
                gpt_oss = RealGPTOSS()
                response = gpt_oss.generate(prompt, max_tokens=500, temperature=0.7)
                
                return {
                    "success": True,
                    "analysis": response,
                    "model_used": "gpt-oss-fallback",
                    "response_time_ms": response.get("processing_time", 0) * 1000,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "fallback_available": True
                }
        
        @self.app.get("/api/trading/status")
        async def get_trading_status():
            """Get overall trading system status"""
            return {
                "success": True,
                "trading": {
                    "active": self.live_mode,
                    "mode": "live_trading" if self.live_mode else "paper_trading",
                    "engines_available": len([e for e in self.systems.values() if e]),
                    "ai_analysis": True,
                    "market_data": True,
                    "broker_connections": {
                        "interactive_brokers": "connected" if self.systems.get('ib_broker') else "disconnected",
                        "alpaca": "connected" if self.systems.get('alpaca_broker') else "disconnected"
                    }
                },
                "performance": {
                    "ram_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "response_time_ms": "<50"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/portfolio/value")
        async def get_portfolio_value():
            """Get portfolio value and positions"""
            try:
                # Get real portfolio data from brokers
                alpaca = self.systems.get('alpaca_broker')
                total_value = 0.0
                cash_balance = 0.0
                positions_list = []
                unrealized_pnl = 0.0

                if alpaca:
                    try:
                        account = await alpaca.get_account()
                        cash_balance = float(account.cash) if hasattr(account, 'cash') else 0.0
                        total_value = float(account.equity) if hasattr(account, 'equity') else cash_balance
                        positions = await alpaca.get_positions()
                        for pos in positions:
                            unrealized_pnl += float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0.0
                            positions_list.append({
                                'symbol': pos.symbol if hasattr(pos, 'symbol') else 'Unknown',
                                'qty': float(pos.qty) if hasattr(pos, 'qty') else 0,
                                'market_value': float(pos.market_value) if hasattr(pos, 'market_value') else 0,
                                'unrealized_pl': float(pos.unrealized_pl) if hasattr(pos, 'unrealized_pl') else 0,
                            })
                    except Exception as broker_err:
                        self.logger.debug(f"Portfolio fetch error: {broker_err}")

                invested_value = total_value - cash_balance
                return {
                    "success": True,
                    "portfolio": {
                        "total_value": round(total_value, 2),
                        "invested_value": round(invested_value, 2),
                        "cash_balance": round(cash_balance, 2),
                        "unrealized_pnl": round(unrealized_pnl, 2),
                        "total_return_pct": round((unrealized_pnl / total_value * 100) if total_value > 0 else 0.0, 2),
                        "positions": positions_list
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    def get_alpaca_broker(self):
        """Get Alpaca broker instance for external use"""
        return self.systems.get('alpaca_broker')

    def get_ib_broker(self):
        """Get Interactive Brokers broker instance for external use"""
        return self.systems.get('ib_broker')

    def get_system_status(self):
        """Get comprehensive system status for external monitoring"""
        return {
            "live_mode": self.live_mode,
            "ib_account": self.ib_account,
            "systems": {name: "active" if system else "inactive"
                       for name, system in self.systems.items()},
            "system_health": self.system_health,
            "failed_systems": self.failed_systems,
            "risk_limits": self.risk_limits,
            "trading_style": self.trading_style,
            "market_regime": self.market_regime,
            "trades_this_hour": len(self.trades_this_hour),
            "standalone_mode": self.standalone_mode
        }

    def get_broker_status(self):
        """Get broker connection status for external monitoring"""
        return {
            "alpaca": {
                "connected": bool(self.systems.get('alpaca_broker')),
                "broker": "alpaca"
            },
            "interactive_brokers": {
                "connected": bool(self.systems.get('ib_broker')),
                "account": self.ib_account,
                "port": self.ib_port,
                "broker": "interactive_brokers"
            }
        }


async def main(standalone_mode=True):
    """
    Main entry point - runs trading system

    Args:
        standalone_mode: If True, creates separate FastAPI app on port 8001 (LEGACY)
                        If False, runs as library for integration (RECOMMENDED)
    """
    launcher = PrometheusLiveTradingLauncher(standalone_mode=standalone_mode)

    # Initialize all systems
    await launcher.initialize_all_systems()

    # Check if critical systems are available
    if not launcher.systems.get('alpaca_broker'):
        logger.error("CRITICAL: No broker connections available!")
        logger.error("Cannot proceed with live trading")
        return launcher  # Return launcher even if brokers not connected (for integration)

    # Only start web server if in standalone mode
    if standalone_mode and launcher.app:
        import threading

        def run_web_server():
            uvicorn.run(launcher.app, host="0.0.0.0", port=8001, log_level="info")

        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()

        print("\n" + "=" * 80)
        print("[WARNING] PROMETHEUS STANDALONE MODE (LEGACY)")
        print("=" * 80)
        print("[WARNING] WARNING: Running separate API server on port 8001")
        print("[WARNING] RECOMMENDED: Use unified_production_server.py instead")
        print("=" * 80)
        print("Web API: http://localhost:8001")
        print("Health: http://localhost:8001/health")
        print("Docs: http://localhost:8001/docs")
        print("Revolutionary Engines: http://localhost:8001/api/revolutionary/engines/status")
        print("AI Analysis: http://localhost:8001/api/ai/analyze")
        print("Trading Status: http://localhost:8001/api/trading/status")
        print("Portfolio: http://localhost:8001/api/portfolio/value")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("[CHECK] PROMETHEUS INTEGRATED MODE")
        print("=" * 80)
        print("[CHECK] Trading system initialized - no separate API server")
        print("[CHECK] Use unified_production_server.py for API endpoints")
        print("=" * 80)

    # Return launcher for integration mode
    return launcher


async def run_standalone():
    """Run in standalone mode with separate API server (LEGACY)"""
    launcher = await main(standalone_mode=True)
    if launcher:
        # Run trading system forever
        await launcher.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(run_standalone())
    except KeyboardInterrupt:
        print("\n\n Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

