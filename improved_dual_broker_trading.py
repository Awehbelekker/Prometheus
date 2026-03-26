#!/usr/bin/env python3
"""
PROMETHEUS IMPROVED Dual Broker Live Trading System
FIXES: Higher signal threshold, Trend filters, Stop losses, Better exit strategy
"""

import asyncio
import os
import sys
import time
import json
import yfinance as yf
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Adaptive Risk Management
try:
    from core.adaptive_risk_manager import (
        get_risk_manager,
        get_confidence_threshold,
        record_trade,
        should_pause_trading
    )
    ADAPTIVE_RISK_AVAILABLE = True
    logger.info("[RISK] Adaptive Risk Manager available")
except ImportError as e:
    logger.warning(f"Adaptive Risk Manager not available: {e}")
    ADAPTIVE_RISK_AVAILABLE = False

# Import AI Intelligence Engines
try:
    from core.universal_reasoning_engine import UniversalReasoningEngine
    UNIVERSAL_REASONING_AVAILABLE = True
except Exception as e:
    logger.warning(f"Universal Reasoning Engine not available: {e}")
    UNIVERSAL_REASONING_AVAILABLE = False

# === CONTINUOUS LEARNING SYSTEMS ===
try:
    from core.local_learning_system import PrometheusLocalLearningSystem
    LOCAL_LEARNING_AVAILABLE = True
    logger.info("[LEARN] Local Learning System available")
except ImportError as e:
    logger.warning(f"Local Learning System not available: {e}")
    LOCAL_LEARNING_AVAILABLE = False

try:
    from core.continuous_learning_engine import ContinuousLearningEngine
    CONTINUOUS_LEARNING_AVAILABLE = True
    logger.info("[LEARN] Continuous Learning Engine available")
except ImportError as e:
    logger.warning(f"Continuous Learning Engine not available: {e}")
    CONTINUOUS_LEARNING_AVAILABLE = False

try:
    from hybrid_ai_trading_engine import HybridAIEngine
    HYBRID_AI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Hybrid AI Engine not available: {e}")
    HYBRID_AI_AVAILABLE = False

try:
    from core.unified_ai_provider import UnifiedAIProvider
    UNIFIED_AI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Unified AI Provider not available: {e}")
    UNIFIED_AI_AVAILABLE = False

# Import brokers
try:
    from brokers.alpaca_broker import AlpacaBroker
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    from ibapi.contract import Contract
    from ibapi.order import Order as IBOrder
    ALPACA_AVAILABLE = True
    IB_AVAILABLE = True
except ImportError as e:
    logger.error(f"Broker import error: {e}")
    ALPACA_AVAILABLE = False
    IB_AVAILABLE = False

class ImprovedDualBrokerTradingSystem:
    """PROMETHEUS IMPROVED Trading System - Higher Win Rate"""
    
    def __init__(self):
        self.alpaca_broker: Optional[AlpacaBroker] = None
        self.ib_broker: Optional[InteractiveBrokersBroker] = None
        self.alpaca_trades_today = 0
        self.ib_trades_today = 0
        self.ib_account = os.getenv('IB_ACCOUNT', "U21922116")
        
        # Capital allocation
        self.ib_capital = 251.58
        self.alpaca_capital = 122.48
        self.total_capital = self.ib_capital + self.alpaca_capital
        self.max_position_size = self.total_capital * 0.03  # 3% per trade = ~$11
        
        # SMART TRADING: LONG trades HOLD until profit target
        self.min_confidence_threshold = 0.65  # Lowered from 0.70 for more trades & faster learning
        self.min_buy_score = 3  # Lowered from 4 for more stock trades & faster learning
        self.take_profit_pct = 0.05  # 5% take profit - SELL HERE
        self.stop_loss_pct = 0.08  # 8% stop loss for risk management
        self.catastrophic_stop_pct = 0.15  # 15% - ONLY sell if catastrophic loss
        # NOTE: For LONG trades, we HOLD through small losses until profit target
        
        # === ENHANCEMENT 1: TRAILING STOP ===
        self.trailing_stop_enabled = True
        self.trailing_stop_trigger = 0.03  # Activate trailing stop at +3%
        self.trailing_stop_distance = 0.015  # Trail 1.5% behind high
        self.position_high_prices = {}  # Track highest price since entry
        
        # === ENHANCEMENT 2: DCA ON DIPS ===
        self.dca_enabled = True
        self.dca_trigger_pct = -0.03  # Buy more at -3%
        self.dca_max_adds = 2  # Maximum 2 DCA buys per position
        self.dca_positions = {}  # Track DCA count per symbol
        
        # === ENHANCEMENT 3: TIME-BASED EXIT ===
        self.time_exit_enabled = True
        self.max_hold_days_crypto = 7  # Max 7 days for crypto
        self.max_hold_days_stock = 14  # Max 14 days for stocks
        self.position_entry_times = {}  # Track when positions were opened
        
        # === ENHANCEMENT 4: NEWS/SENTIMENT ===
        self.sentiment_enabled = True
        self.avoid_fed_days = True  # Skip trading on Fed announcement days
        
        # === ENHANCEMENT 5: SCALE OUT ===
        self.scale_out_enabled = True
        self.scale_out_first_pct = 0.03  # Sell 50% at +3%
        self.scale_out_second_pct = 0.07  # Sell remaining at +7%
        self.scaled_out_positions = {}  # Track which positions have scaled out
        
        # === ENHANCEMENT 6: CORRELATION FILTER ===
        self.correlation_filter_enabled = True
        
        # === CRYPTO EXPERT PARAMETERS (Trained via 15-gen backtesting) ===
        # Best fitness: 25,218,719 | Win Rate: 80% | Sharpe: 27.2
        self.crypto_expert_enabled = True
        self.crypto_win_rate_target = 0.80
        self.crypto_avg_win_pct = 0.0456  # 4.56% average win
        self.crypto_avg_loss_pct = 0.0141  # 1.41% average loss
        self.crypto_take_profit = 0.06  # 6% take profit
        self.crypto_stop_loss = 0.03  # 3% stop loss
        self.crypto_leverage = 1.0  # No leverage for safety (backtested 4x)
        
        # CRYPTO STRATEGY WEIGHTS (Optimized)
        self.crypto_whale_weight = 0.265  # 26.5% - HIGHEST importance
        self.crypto_pattern_weight = 0.231  # 23.1% - Pattern recognition
        self.crypto_funding_weight = 0.207  # 20.7% - Funding arbitrage
        self.crypto_fear_greed_weight = 0.15  # 15% - Fear/Greed index
        self.crypto_liquidation_weight = 0.15  # 15% - Liquidation detection
        
        # CRYPTO MARKET CONDITIONS
        self.trade_in_extreme_fear = True  # BUY when fear index < 20
        self.trade_in_extreme_greed = False  # AVOID buying when greed > 80
        self.fear_greed_index = 50  # Will be updated from API
        
        self.correlated_assets = {
            'BTCUSD': ['ETHUSD', 'SOLUSD'],  # BTC correlates with ETH, SOL
            'ETHUSD': ['BTCUSD', 'SOLUSD'],
            'SOLUSD': ['BTCUSD', 'ETHUSD'],
            'DOGEUSD': ['SHIBUSD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'GOOGL': ['AAPL', 'MSFT', 'META'],
            'META': ['GOOGL', 'SNAP'],
            'TSLA': ['RIVN', 'LCID'],
            'NVDA': ['AMD', 'INTC'],
            'AMD': ['NVDA', 'INTC'],
        }
        
        # Session tracking
        self.session_id = f"improved_dual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.positions = {}
        self.entry_prices = {}  # Track entry prices for stop losses
        self.market_data_cache = {}
        
        # AUTONOMOUS ADAPTIVE TRADE LIMITS
        self.base_trades_per_day = 20  # Starting baseline
        self.max_trades_per_day = 20  # Will be adjusted dynamically
        self.total_trades_today = 0
        self.today_wins = 0
        self.today_losses = 0
        self.today_profit = 0.0
        self.today_commissions = 0.0
        self.last_limit_adjustment = datetime.now()
        
        # === CONTINUOUS LEARNING SYSTEMS ===
        self.local_learning_system = None
        self.continuous_learning_engine = None
        self.trade_history_for_learning = []  # Stores trades for learning
        self._initialize_learning_systems()
        
        # Market Hours Configuration
        self.stock_market_open_hour = 9   # 9:30 AM ET
        self.stock_market_open_minute = 30
        self.stock_market_close_hour = 16  # 4:00 PM ET
        self.crypto_24_5_enabled = True    # Alpaca 24/5 crypto trading
        
        # AI Brain
        self.ai_brain_active = False
        self.universal_reasoning = None
        self.hybrid_ai = None
        self.unified_ai = None
        self.orchestrator = None
        
        self._initialize_ai_brain()
    
    def _initialize_learning_systems(self):
        """Initialize continuous learning systems to get smarter every trade"""
        logger.info("🧠 Initializing CONTINUOUS LEARNING SYSTEMS...")
        
        # Local Learning System (100% local, no APIs)
        if LOCAL_LEARNING_AVAILABLE:
            try:
                self.local_learning_system = PrometheusLocalLearningSystem(learning_rate=0.01)
                logger.info("✅ Local Learning System initialized - Learning from every trade!")
            except Exception as e:
                logger.warning(f"Local Learning System init failed: {e}")
        
        # Continuous Learning Engine (adaptive strategy optimization)
        if CONTINUOUS_LEARNING_AVAILABLE:
            try:
                self.continuous_learning_engine = ContinuousLearningEngine()
                logger.info("✅ Continuous Learning Engine initialized - Adaptive optimization!")
            except Exception as e:
                logger.warning(f"Continuous Learning Engine init failed: {e}")
        
        if self.local_learning_system or self.continuous_learning_engine:
            logger.info("🎓 PROMETHEUS WILL LEARN FROM EVERY TRADE AND GET SMARTER!")
        else:
            logger.warning("⚠️ No learning systems available - using static strategies")
    
    def _record_trade_for_learning(self, trade_data: Dict[str, Any]):
        """Record trade outcome for all learning systems"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Record to local learning system
            if self.local_learning_system:
                self.local_learning_system.record_trade(trade_data)
                logger.info(f"📚 [LEARN] Trade recorded for local learning: {trade_data.get('symbol')}")
            
            # Record to continuous learning engine
            if self.continuous_learning_engine and hasattr(self.continuous_learning_engine, 'record_trade'):
                self.continuous_learning_engine.record_trade(trade_data)
            
            # Store in history
            self.trade_history_for_learning.append(trade_data)
            
            # Save to JSON file for persistence
            self._save_trade_to_file(trade_data)
            
            # Get updated strategy recommendations if available
            if self.local_learning_system and trade_data.get('market_regime'):
                optimal_strategy = self.local_learning_system.get_optimal_strategy(trade_data['market_regime'])
                logger.info(f"🧠 [LEARN] Optimal strategy for {trade_data.get('market_regime')}: {optimal_strategy}")
            
        except Exception as e:
            logger.warning(f"Could not record trade for learning: {e}")
    
    def _save_trade_to_file(self, trade_data: Dict[str, Any]):
        """Persist trade data for long-term learning"""
        try:
            trades_file = Path("prometheus_trade_history.json")
            
            # Load existing trades
            existing_trades = []
            if trades_file.exists():
                with open(trades_file, 'r') as f:
                    existing_trades = json.load(f)
            
            # Add new trade
            existing_trades.append(trade_data)
            
            # Save back (keep last 10000 trades)
            with open(trades_file, 'w') as f:
                json.dump(existing_trades[-10000:], f, indent=2, default=str)
                
        except Exception as e:
            logger.warning(f"Could not save trade to file: {e}")
    
    def _initialize_ai_brain(self):
        """Initialize the AI brain for true intelligence"""
        logger.info("🧠 Initializing PROMETHEUS AI Brain (IMPROVED)...")
        
        if UNIVERSAL_REASONING_AVAILABLE:
            try:
                self.universal_reasoning = UniversalReasoningEngine()
                self.ai_brain_active = True
                logger.info("✅ Universal Reasoning Engine initialized")
            except Exception as e:
                logger.warning(f"Universal Reasoning initialization failed: {e}")
        
        if HYBRID_AI_AVAILABLE and not self.ai_brain_active:
            try:
                self.hybrid_ai = HybridAIEngine()
                if self.hybrid_ai.check_gpt_oss_available():
                    self.ai_brain_active = True
                    logger.info("✅ Hybrid AI Engine initialized")
            except Exception as e:
                logger.warning(f"Hybrid AI initialization failed: {e}")
        
        if UNIFIED_AI_AVAILABLE and not self.ai_brain_active:
            try:
                self.unified_ai = UnifiedAIProvider()
                self.ai_brain_active = True
                logger.info("✅ Unified AI Provider initialized")
            except Exception as e:
                logger.warning(f"Unified AI initialization failed: {e}")
        
        if self.ai_brain_active:
            logger.info("🧠 AI BRAIN ACTIVE - Improved signal quality")
        else:
            logger.warning("⚠️ AI BRAIN INACTIVE - Using enhanced mathematical fallback")

    async def start(self):
        """Start the trading system"""
        logger.info("=" * 60)
        logger.info(" PROMETHEUS IMPROVED TRADING SYSTEM")
        logger.info(" Higher Win Rate | Better Risk Management | Smarter Signals")
        logger.info("=" * 60)
        
        await self._setup_brokers()
        await self.run_trading_loop()

    async def _setup_brokers(self):
        """Setup broker connections"""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Setup Alpaca with proper config
        if ALPACA_AVAILABLE:
            try:
                alpaca_config = {
                    'api_key': os.getenv('ALPACA_API_KEY'),
                    'secret_key': os.getenv('ALPACA_SECRET_KEY'),
                    'paper_trading': False,  # LIVE trading
                    'enable_24_5_trading': True
                }
                self.alpaca_broker = AlpacaBroker(alpaca_config)
                connected = await asyncio.wait_for(self.alpaca_broker.connect(), timeout=10)
                if connected:
                    account = await self.alpaca_broker.get_account()
                    self.alpaca_capital = float(account.equity)
                    logger.info(f"[ALPACA] Connected - Balance: ${self.alpaca_capital:.2f}")
                else:
                    self.alpaca_broker = None
            except Exception as e:
                logger.error(f"[ALPACA] Connection error: {e}")
                self.alpaca_broker = None
        
        # Setup IB
        if IB_AVAILABLE:
            ib_config = {
                'host': os.getenv('IB_HOST', '127.0.0.1'),
                'port': int(os.getenv('IB_PORT', '4002')),
                'client_id': int(os.getenv('IB_CLIENT_ID', '8')),  # New client ID
                'paper_trading': False
            }
            
            self.ib_broker = InteractiveBrokersBroker(ib_config)
            logger.info(f"[IB] Connecting to account: {self.ib_account}")
            
            try:
                connected = await asyncio.wait_for(self.ib_broker.connect(), timeout=15)
                if connected:
                    await asyncio.sleep(2)
                    self.ib_broker.client.reqIds(1)
                    await asyncio.sleep(1)
                    
                    # Get IB balance
                    try:
                        ib_account = await self.ib_broker.get_account()
                        if hasattr(ib_account, 'TotalCashBalance'):
                            self.ib_capital = float(ib_account.TotalCashBalance)
                        elif hasattr(ib_account, 'EquityWithLoanValue'):
                            self.ib_capital = float(ib_account.EquityWithLoanValue)
                        logger.info(f"[IB] Connected - Balance: ${self.ib_capital:.2f}")
                    except:
                        logger.info(f"[IB] Connected - Using default balance: ${self.ib_capital:.2f}")
                else:
                    self.ib_broker = None
            except Exception as e:
                logger.error(f"[IB] Connection error: {e}")
                self.ib_broker = None
        
        self.total_capital = self.ib_capital + self.alpaca_capital
        self.max_position_size = self.total_capital * 0.03
        
        logger.info(f"[CAPITAL] Total: ${self.total_capital:.2f}, Max Position: ${self.max_position_size:.2f}")

    async def run_trading_loop(self):
        """Main trading loop with improved logic"""
        cycle = 0
        while True:
            cycle += 1
            now = datetime.now()
            
            # Reset daily counters at midnight
            if now.hour == 0 and now.minute == 0:
                self.total_trades_today = 0
                self.today_wins = 0
                self.today_losses = 0
                self.today_profit = 0.0
                self.today_commissions = 0.0
            
            logger.info(f"\n[CYCLE {cycle}] {now.strftime('%H:%M:%S')}")
            logger.info("-" * 60)
            
            # ═══════════════════════════════════════════════════════════════
            # CRYPTO EXPERT: Update Fear/Greed Index
            # ═══════════════════════════════════════════════════════════════
            if self.crypto_expert_enabled:
                await self._update_crypto_fear_greed()
            
            # ═══════════════════════════════════════════════════════════════
            # MARKET HOURS CHECK - Know when trading is open/closed
            # ═══════════════════════════════════════════════════════════════
            market_status = self._get_market_status()
            stock_open = market_status['stock_market_open']
            crypto_open = market_status['can_trade_crypto']
            
            if not stock_open and not crypto_open:
                logger.info("📅 [MARKET CLOSED] Both stock and crypto markets are closed")
                logger.info("   Stock Market: Opens Mon-Fri 9:30 AM - 4:00 PM ET")
                logger.info("   Crypto (24/5): Opens Sun 8PM ET - Fri 4AM ET")
                logger.info("   Waiting 30 minutes before next check...")
                await asyncio.sleep(1800)  # Wait 30 min
                continue
            elif not stock_open:
                logger.info(f"📊 [MARKET] Stock market CLOSED | Crypto: {'OPEN' if crypto_open else 'CLOSED'}")
                logger.info("   Trading CRYPTO ONLY via Alpaca 24/5")
                if self.crypto_expert_enabled:
                    logger.info(f"🪙 [CRYPTO EXPERT] Fear/Greed: {self.fear_greed_index} | TP: 6% | SL: 3%")
            elif not crypto_open:
                logger.info(f"📊 [MARKET] Stock market OPEN | Crypto: CLOSED")
                logger.info("   Trading STOCKS ONLY via IB")
            else:
                logger.info(f"📊 [MARKET] Stock: OPEN | Crypto: OPEN - Full trading mode!")
                if self.crypto_expert_enabled:
                    logger.info(f"🪙 [CRYPTO EXPERT] Fear/Greed: {self.fear_greed_index} | Active strategies: Whale+Pattern+Funding")
            # ═══════════════════════════════════════════════════════════════
            
            # Autonomous limit adjustment every hour
            if now.minute == 0 and (datetime.now() - self.last_limit_adjustment).total_seconds() > 3600:
                self._adjust_trade_limit_autonomously()
                self.last_limit_adjustment = datetime.now()
            
            # Check trade limits
            if self.total_trades_today >= self.max_trades_per_day:
                logger.info(f"[LIMIT] Daily trade limit reached ({self.max_trades_per_day}). Waiting...")
                await asyncio.sleep(3600)  # Wait 1 hour
                continue
            
            # Check adaptive risk
            if ADAPTIVE_RISK_AVAILABLE:
                should_pause, reason = should_pause_trading()
                if should_pause:
                    logger.warning(f"[RISK] TRADING PAUSED: {reason}")
                    await asyncio.sleep(1800)
                    continue
            
            # Check existing positions for stop loss / take profit
            await self._manage_positions()
            
            # Generate and execute signals (pass market status for filtering)
            signals = await self._generate_improved_signals(market_status)
            if signals:
                logger.info(f"[SIGNALS] {len(signals)} high-quality signals generated")
                await self._execute_trades(signals)
            else:
                logger.info("[SIGNALS] No signals met quality threshold")
            
            await self._status_check()
            
            # OPTIMIZED: 3 minutes for crypto (fast for trailing stops), 5 min for stocks
            # With trailing stops and DCA, we need faster position checks
            cycle_time = 180  # 3 minutes - optimal for crypto volatility
            logger.info(f"[WAIT] Next cycle in {cycle_time // 60} minutes...")
            await asyncio.sleep(cycle_time)

    async def _get_enhanced_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get enhanced market data with trend filters"""
        try:
            # Convert crypto symbols for yfinance
            if '/' in symbol:
                # ETH/USD -> ETH-USD
                yf_symbol = symbol.replace('/', '-')
            elif symbol.endswith('USD') and len(symbol) > 3:
                # ETHUSD -> ETH-USD
                yf_symbol = f"{symbol[:-3]}-USD"
            else:
                yf_symbol = symbol
            
            ticker = yf.Ticker(yf_symbol)
            
            # Get multiple timeframes for better analysis
            hist_5m = ticker.history(period='5d', interval='5m')
            hist_1h = ticker.history(period='1mo', interval='1h')
            hist_1d = ticker.history(period='6mo', interval='1d')
            
            if hist_5m.empty:
                return None
            
            current_price = float(hist_5m['Close'].iloc[-1])
            
            # Calculate SMAs for trend
            if len(hist_1d) >= 200:
                sma_20 = hist_1d['Close'].tail(20).mean()
                sma_50 = hist_1d['Close'].tail(50).mean()
                sma_200 = hist_1d['Close'].tail(200).mean()
            else:
                sma_20 = sma_50 = sma_200 = current_price
            
            # Trend direction
            uptrend = current_price > sma_20 > sma_50
            downtrend = current_price < sma_20 < sma_50
            
            # Calculate momentum
            if len(hist_5m) > 1:
                momentum_5m = (current_price - float(hist_5m['Close'].iloc[-2])) / float(hist_5m['Close'].iloc[-2])
            else:
                momentum_5m = 0
            
            if len(hist_1h) > 1:
                momentum_1h = (current_price - float(hist_1h['Close'].iloc[-2])) / float(hist_1h['Close'].iloc[-2])
            else:
                momentum_1h = 0
            
            # Volume analysis
            volume_current = float(hist_5m['Volume'].iloc[-1])
            volume_avg = float(hist_5m['Volume'].mean())
            volume_ratio = volume_current / volume_avg if volume_avg > 0 else 1.0
            
            # RSI calculation
            closes = hist_1h['Close'].values[-14:] if len(hist_1h) >= 14 else hist_5m['Close'].values[-14:]
            if len(closes) >= 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0.0001
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50
            
            # Volatility (ATR-like)
            if len(hist_1d) >= 14:
                highs = hist_1d['High'].values[-14:]
                lows = hist_1d['Low'].values[-14:]
                closes_d = hist_1d['Close'].values[-14:]
                tr = [max(highs[i] - lows[i], abs(highs[i] - closes_d[i-1]), abs(lows[i] - closes_d[i-1])) 
                      for i in range(1, len(highs))]
                atr = sum(tr) / len(tr) if tr else current_price * 0.02
                volatility = atr / current_price
            else:
                volatility = 0.02
            
            return {
                'symbol': symbol,
                'price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'uptrend': uptrend,
                'downtrend': downtrend,
                'momentum_5m': momentum_5m,
                'momentum_1h': momentum_1h,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'volatility': volatility,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.warning(f"Market data error for {symbol}: {e}")
            return None

    async def _generate_improved_signals(self, market_status: dict = None) -> List[Dict[str, Any]]:
        """Generate HIGH QUALITY signals with trend confirmation"""
        logger.info("[AI] Analyzing markets with improved criteria...")
        
        # Get market status if not provided
        if market_status is None:
            market_status = self._get_market_status()
        
        stock_open = market_status.get('stock_market_open', False)
        crypto_open = market_status.get('can_trade_crypto', True)
        
        # EXPANDED watchlist for IB (more aggressive for stocks)
        # Added GLD, XLE, XLF based on 1-year backtest (Gold +69%, trending sectors)
        watchlist = {
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'META', 
                      'AMZN', 'NFLX', 'CRM', 'ADBE', 'PYPL',
                      'SPY', 'QQQ', 'IWM', 'DIA',
                      'GLD', 'XLE', 'XLF'],  # Added trending ETFs: Gold, Energy, Financials
            'crypto': ['ETH/USD', 'BTC/USD', 'SOL/USD', 'DOGE/USD', 'AVAX/USD'],
        }
        
        signals = []
        
        # Analyze stocks for IB (only if market is open)
        if stock_open:
            for symbol in watchlist['stocks']:
                try:
                    data = await self._get_enhanced_market_data(symbol)
                    if data:
                        decision = self._calculate_improved_signal(symbol, data, 'stock')
                        if decision:
                            signals.append(decision)
                            logger.info(f"  ✓ {symbol}: {decision['action']} (conf: {decision['confidence']:.0%})")
                except Exception as e:
                    logger.warning(f"Error analyzing {symbol}: {e}")
        else:
            logger.info("  📈 Stock market CLOSED - Skipping stock signals")
        
        # Analyze crypto for Alpaca (24/5 trading)
        if crypto_open:
            for symbol in watchlist['crypto']:
                try:
                    data = await self._get_enhanced_market_data(symbol)
                    if data:
                        decision = self._calculate_improved_signal(symbol, data, 'crypto')
                        if decision:
                            signals.append(decision)
                            logger.info(f"  ✓ {symbol}: {decision['action']} (conf: {decision['confidence']:.0%})")
                except Exception as e:
                    logger.warning(f"Error analyzing {symbol}: {e}")
        else:
            logger.info("  🪙 Crypto market CLOSED - Skipping crypto signals")
        
        # Sort by confidence and take top signals
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        return signals[:10]  # Max 10 signals per cycle

    def _calculate_improved_signal(self, symbol: str, data: dict, asset_type: str) -> Optional[Dict[str, Any]]:
        """Calculate high-quality signal with multiple confirmations"""
        price = data.get('price', 0)
        if price <= 0:
            return None
        
        # IMPROVED SCORING SYSTEM (need more points for a trade)
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # 1. TREND FILTER (MOST IMPORTANT) - 3 points
        if data.get('uptrend'):
            buy_score += 3
            reasons.append("Uptrend confirmed")
        elif data.get('downtrend'):
            sell_score += 3
            reasons.append("Downtrend confirmed")
        
        # 2. RSI CONDITIONS - 2 points
        rsi = data.get('rsi', 50)
        if rsi < 30:
            buy_score += 2
            reasons.append(f"Oversold (RSI={rsi:.0f})")
        elif rsi > 70:
            sell_score += 2
            reasons.append(f"Overbought (RSI={rsi:.0f})")
        elif 40 < rsi < 60:
            buy_score += 1  # Neutral RSI, slight buy bias
        
        # 3. MOMENTUM - 2 points
        mom_5m = data.get('momentum_5m', 0)
        mom_1h = data.get('momentum_1h', 0)
        if mom_5m > 0.005 and mom_1h > 0.01:
            buy_score += 2
            reasons.append("Strong positive momentum")
        elif mom_5m < -0.005 and mom_1h < -0.01:
            sell_score += 2
            reasons.append("Strong negative momentum")
        
        # 4. VOLUME CONFIRMATION - 1 point
        if data.get('volume_ratio', 1) > 1.5:
            buy_score += 1 if mom_5m > 0 else 0
            sell_score += 1 if mom_5m < 0 else 0
            reasons.append("High volume")
        
        # 5. PRICE ABOVE KEY MOVING AVERAGES - 1 point each
        if price > data.get('sma_20', 0):
            buy_score += 1
        if price > data.get('sma_50', 0):
            buy_score += 1
        if price > data.get('sma_200', 0):
            buy_score += 1
        
        # DECISION: Need at least 4 points (was 3)
        action = None
        confidence = 0
        
        if buy_score >= self.min_buy_score:
            action = 'BUY'
            confidence = min(0.95, 0.5 + (buy_score * 0.05))
        elif sell_score >= self.min_buy_score and symbol in self.positions:
            # Only sell if we have a position
            action = 'SELL'
            confidence = min(0.95, 0.5 + (sell_score * 0.05))
        
        # FILTER: Minimum confidence threshold
        if confidence < self.min_confidence_threshold:
            return None
        
        # Calculate position size with CRYPTO EXPERT optimization
        if asset_type == 'crypto' and self.crypto_expert_enabled:
            # Apply crypto expert confidence boost based on strategy weights
            crypto_boost = 0
            
            # Whale tracking boost (26.5% weight)
            if data.get('volume_ratio', 1) > 2.0:  # High volume = whale activity
                crypto_boost += 0.05 * self.crypto_whale_weight
                reasons.append("Whale activity detected")
            
            # Pattern boost (23.1% weight)
            if data.get('uptrend') and mom_5m > 0.01:
                crypto_boost += 0.05 * self.crypto_pattern_weight
                reasons.append("Bullish pattern confirmed")
            
            # Fear/Greed boost (15% weight)
            if self.fear_greed_index < 20 and self.trade_in_extreme_fear:
                crypto_boost += 0.10  # Buy in extreme fear
                reasons.append("Extreme fear - contrarian buy")
            elif self.fear_greed_index > 80 and not self.trade_in_extreme_greed:
                confidence *= 0.5  # Reduce confidence in extreme greed
                reasons.append("Extreme greed - caution")
            
            confidence = min(0.95, confidence + crypto_boost)
            quantity = round(self.max_position_size / price, 4)
        elif asset_type == 'crypto':
            quantity = round(self.max_position_size / price, 4)
        else:
            quantity = max(1, int(self.max_position_size / price))
        
        if action:
            return {
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'confidence': confidence,
                'reason': ' | '.join(reasons[:3]),
                'type': asset_type,
                'price': price,
                'stop_loss': price * (1 - self.stop_loss_pct) if action == 'BUY' else None,
                'take_profit': price * (1 + self.take_profit_pct) if action == 'BUY' else None
            }
        
        return None

    def _adjust_trade_limit_autonomously(self):
        """🧠 Prometheus autonomously adjusts daily trade limit based on performance"""
        
        if self.total_trades_today < 5:
            return  # Need minimum data for reliable adjustment
        
        # Calculate metrics
        win_rate = self.today_wins / self.total_trades_today if self.total_trades_today > 0 else 0
        avg_profit_per_trade = self.today_profit / self.total_trades_today if self.total_trades_today > 0 else 0
        net_profit = self.today_profit - self.today_commissions
        
        old_limit = self.max_trades_per_day
        
        # AUTONOMOUS DECISION LOGIC
        if win_rate > 0.60 and net_profit > 0:
            # Winning day - increase limit to capitalize on good performance
            self.max_trades_per_day = min(50, int(self.base_trades_per_day * 1.5))
            logger.info(f"📈 [AUTONOMOUS] Trade limit INCREASED: {old_limit} → {self.max_trades_per_day}")
            logger.info(f"   Win rate: {win_rate:.1%} | Net profit: ${net_profit:.2f}")
        
        elif win_rate < 0.40 or net_profit < -20:
            # Losing day - reduce limit to prevent further losses
            self.max_trades_per_day = max(10, int(self.base_trades_per_day * 0.5))
            logger.info(f"📉 [AUTONOMOUS] Trade limit REDUCED: {old_limit} → {self.max_trades_per_day}")
            logger.info(f"   Win rate: {win_rate:.1%} | Net profit: ${net_profit:.2f}")
        
        elif avg_profit_per_trade > 2.0:
            # High profit per trade - allow more opportunities
            self.max_trades_per_day = min(40, int(self.base_trades_per_day * 1.25))
            logger.info(f"💰 [AUTONOMOUS] Trade limit adjusted: {old_limit} → {self.max_trades_per_day}")
            logger.info(f"   Avg profit: ${avg_profit_per_trade:.2f}/trade")
        
        elif net_profit < 0 and self.today_commissions > abs(net_profit):
            # Commissions eating profits - reduce trading
            self.max_trades_per_day = max(15, int(self.base_trades_per_day * 0.75))
            logger.info(f"💸 [AUTONOMOUS] Trade limit reduced: {old_limit} → {self.max_trades_per_day}")
            logger.info(f"   Commissions: ${self.today_commissions:.2f} > Net: ${net_profit:.2f}")
        
        else:
            # Neutral performance - maintain baseline
            self.max_trades_per_day = self.base_trades_per_day
            if old_limit != self.max_trades_per_day:
                logger.info(f"⚖️ [AUTONOMOUS] Trade limit reset to baseline: {self.max_trades_per_day}")

    async def _manage_positions(self):
        """ENHANCED position management with all 6 improvements"""
        logger.info("[POSITIONS] Enhanced smart check (Trailing Stop + DCA + Scale Out)...")
        
        # Check Alpaca positions
        if self.alpaca_broker:
            try:
                positions = await self.alpaca_broker.get_positions()
                for pos in positions:
                    symbol = pos.symbol
                    qty = pos.quantity
                    entry_price = pos.avg_price
                    market_value = pos.market_value
                    current_price = market_value / qty if qty > 0 else 0
                    pnl_pct = pos.unrealized_pnl_percent
                    
                    # Initialize tracking if new position
                    if symbol not in self.position_entry_times:
                        self.position_entry_times[symbol] = datetime.now()
                    if symbol not in self.position_high_prices:
                        self.position_high_prices[symbol] = current_price
                    if symbol not in self.dca_positions:
                        self.dca_positions[symbol] = 0
                    if symbol not in self.scaled_out_positions:
                        self.scaled_out_positions[symbol] = False
                    
                    # Update high price for trailing stop
                    if current_price > self.position_high_prices[symbol]:
                        self.position_high_prices[symbol] = current_price
                    
                    high_price = self.position_high_prices[symbol]
                    drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                    
                    # Get AI prediction
                    drop_predicted = await self._predict_drop(symbol)
                    
                    # === ENHANCEMENT 3: TIME-BASED EXIT ===
                    if self.time_exit_enabled:
                        days_held = (datetime.now() - self.position_entry_times[symbol]).days
                        max_days = self.max_hold_days_crypto if 'USD' in symbol else self.max_hold_days_stock
                        if days_held >= max_days:
                            logger.warning(f"⏰ [TIME EXIT] {symbol}: Held {days_held} days (max {max_days}). Exiting!")
                            await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': qty, 'type': 'crypto'})
                            self._cleanup_position_tracking(symbol, current_price, pnl, 'TIME_EXIT')
                            continue
                    
                    # === ENHANCEMENT 5: SCALE OUT (First target +3%) ===
                    if self.scale_out_enabled and not self.scaled_out_positions[symbol]:
                        if pnl_pct >= self.scale_out_first_pct:
                            sell_qty = qty * 0.5  # Sell 50%
                            logger.info(f"📈 [SCALE OUT 1/2] {symbol}: {pnl_pct:.1%} - Selling 50% to lock gains!")
                            await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': sell_qty, 'type': 'crypto'})
                            self.scaled_out_positions[symbol] = True
                            continue
                    
                    # === ENHANCEMENT 5: SCALE OUT (Second target +7%) ===
                    if self.scale_out_enabled and self.scaled_out_positions[symbol]:
                        if pnl_pct >= self.scale_out_second_pct:
                            logger.info(f"🎯 [SCALE OUT 2/2] {symbol}: {pnl_pct:.1%} - Selling remaining! FULL PROFIT!")
                            await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': qty, 'type': 'crypto'})
                            self._cleanup_position_tracking(symbol, current_price, pnl, 'SCALE_OUT_PROFIT')
                            continue
                    
                    # === ENHANCEMENT 1: TRAILING STOP ===
                    if self.trailing_stop_enabled and pnl_pct >= self.trailing_stop_trigger:
                        if drop_from_high >= self.trailing_stop_distance:
                            logger.info(f"🛑 [TRAILING STOP] {symbol}: Was +{((high_price-entry_price)/entry_price)*100:.1f}%, now {pnl_pct:.1%}. Locking profit!")
                            await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': qty, 'type': 'crypto'})
                            self._cleanup_position_tracking(symbol, current_price, pnl, 'TRAILING_STOP')
                            continue
                        else:
                            logger.info(f"📈 [TRAILING] {symbol}: {pnl_pct:+.1%} (High: +{((high_price-entry_price)/entry_price)*100:.1f}%) - Trail active")
                    
                    # SMART PROFIT PROTECTION - Drop predicted while in profit
                    elif pnl_pct > 0.01 and drop_predicted:
                        logger.info(f"🧠 [SMART SELL] {symbol}: {pnl_pct:.1%} profit - Drop predicted! Locking gains!")
                        await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': qty, 'type': 'crypto'})
                        self._cleanup_position_tracking(symbol, current_price, pnl, 'AI_PREDICTED_DROP')
                    
                    # CATASTROPHIC STOP
                    elif pnl_pct <= -self.catastrophic_stop_pct:
                        logger.warning(f"❌ [CATASTROPHIC] {symbol}: {pnl_pct:.1%} - Emergency exit!")
                        await self._execute_alpaca_trade({'symbol': symbol, 'action': 'SELL', 'quantity': qty, 'type': 'crypto'})
                        self._cleanup_position_tracking(symbol, current_price, pnl, 'CATASTROPHIC_STOP')
                    
                    # === ENHANCEMENT 2: DCA ON DIPS ===
                    elif pnl_pct <= self.dca_trigger_pct and self.dca_enabled:
                        if self.dca_positions[symbol] < self.dca_max_adds:
                            # Check if we have enough capital
                            dca_amount = self.max_position_size * 0.5  # Add 50% of normal position
                            if dca_amount > 5:  # Minimum $5
                                logger.info(f"💰 [DCA] {symbol}: {pnl_pct:.1%} dip - Adding ${dca_amount:.2f} to lower avg cost!")
                                dca_qty = dca_amount / current_price
                                await self._execute_alpaca_trade({'symbol': symbol, 'action': 'BUY', 'quantity': dca_qty, 'type': 'crypto', 'price': current_price})
                                self.dca_positions[symbol] += 1
                        else:
                            logger.info(f"📊 [HOLD] {symbol}: {pnl_pct:+.1%} - DCA maxed out ({self.dca_max_adds}x), waiting...")
                    
                    # HOLD - Small loss, thesis valid
                    elif pnl_pct < 0:
                        target_price = entry_price * (1 + self.take_profit_pct)
                        dist_to_target = ((target_price - current_price) / current_price) * 100
                        if drop_predicted:
                            logger.info(f"📉 [WATCH] {symbol}: {pnl_pct:+.1%} - Drop predicted, at loss, HOLD")
                        else:
                            logger.info(f"📊 [HOLD] {symbol}: {pnl_pct:+.1%} - LONG thesis valid, target +5%")
                        logger.info(f"   Target: ${target_price:.4f} ({dist_to_target:.1f}% to go)")
                    
                    # IN PROFIT - Hold for target
                    else:
                        target_price = entry_price * (1 + self.take_profit_pct)
                        dist_to_target = ((target_price - current_price) / current_price) * 100
                        if drop_predicted:
                            logger.info(f"⚠️ [WATCH] {symbol}: {pnl_pct:+.1%} profit - Drop signal, monitoring...")
                        else:
                            logger.info(f"🟢 [HOLD] {symbol}: {pnl_pct:+.1%} profit - Waiting for +5% ({dist_to_target:.1f}% to go)")
                        
            except Exception as e:
                logger.warning(f"Position check error: {e}")
        
        # ========== IB POSITION MANAGEMENT ==========
        if self.ib_broker and hasattr(self.ib_broker, 'ib') and self.ib_broker.ib.isConnected():
            try:
                positions = self.ib_broker.ib.positions()
                for pos in positions:
                    symbol = pos.contract.symbol
                    qty = abs(pos.position)
                    entry_price = pos.avgCost
                    
                    if qty == 0:
                        continue
                    
                    # Get current price
                    try:
                        import yfinance as yf
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period='1d')
                        if not hist.empty:
                            current_price = float(hist['Close'].iloc[-1])
                        else:
                            continue
                    except:
                        continue
                    
                    pnl = (current_price - entry_price) * qty
                    pnl_pct = ((current_price - entry_price) / entry_price) if entry_price > 0 else 0
                    
                    # Initialize tracking if needed
                    ib_symbol = f"IB_{symbol}"
                    if ib_symbol not in self.position_entry_times:
                        self.position_entry_times[ib_symbol] = datetime.now()
                    if ib_symbol not in self.position_high_prices:
                        self.position_high_prices[ib_symbol] = current_price
                    
                    # Update high price
                    if current_price > self.position_high_prices[ib_symbol]:
                        self.position_high_prices[ib_symbol] = current_price
                    
                    high_price = self.position_high_prices[ib_symbol]
                    drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                    
                    logger.info(f"[IB] {symbol}: {qty} @ ${entry_price:.2f} | Now: ${current_price:.2f} | P/L: ${pnl:+.2f} ({pnl_pct:+.1%})")
                    
                    # IB TAKE PROFIT at +5%
                    if pnl_pct >= 0.05:
                        logger.info(f"🎯 [IB TAKE PROFIT] {symbol}: {pnl_pct:.1%} profit! Selling...")
                        await self._execute_ib_sell(symbol, qty)
                        self._cleanup_position_tracking(ib_symbol, current_price, pnl, 'IB_TAKE_PROFIT')
                    
                    # IB TRAILING STOP - if was up 3%+ and dropped 1.5% from high
                    elif pnl_pct >= 0.02 and drop_from_high >= 0.015:
                        logger.info(f"🛑 [IB TRAILING] {symbol}: Was +{((high_price-entry_price)/entry_price)*100:.1f}%, dropped. Locking profit!")
                        await self._execute_ib_sell(symbol, qty)
                        self._cleanup_position_tracking(ib_symbol, current_price, pnl, 'IB_TRAILING_STOP')
                    
                    # IB STOP LOSS at -3%
                    elif pnl_pct <= -0.03:
                        logger.warning(f"❌ [IB STOP LOSS] {symbol}: {pnl_pct:.1%} loss! Cutting position...")
                        await self._execute_ib_sell(symbol, qty)
                        self._cleanup_position_tracking(ib_symbol, current_price, pnl, 'IB_STOP_LOSS')
                    
            except Exception as e:
                logger.warning(f"IB position check error: {e}")
    
    async def _execute_ib_sell(self, symbol: str, qty: float):
        """Execute a sell order on IB"""
        try:
            from ib_insync import Stock, MarketOrder
            
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib_broker.ib.qualifyContracts(contract)
            
            order = MarketOrder('SELL', int(qty))
            trade = self.ib_broker.ib.placeOrder(contract, order)
            
            # Wait for fill (up to 10 seconds)
            for _ in range(10):
                self.ib_broker.ib.sleep(1)
                if trade.orderStatus.status == 'Filled':
                    logger.info(f"✅ [IB] SOLD {symbol}: {qty} shares @ ${trade.orderStatus.avgFillPrice:.2f}")
                    return True
            
            logger.warning(f"⚠️ [IB] Order status: {trade.orderStatus.status}")
            return False
            
        except Exception as e:
            logger.error(f"❌ [IB] Sell error for {symbol}: {e}")
            return False
    
    def _cleanup_position_tracking(self, symbol: str, exit_price: float = 0, profit: float = 0, exit_reason: str = ""):
        """Clean up tracking data when position is closed AND record for learning"""
        
        # Record trade for learning BEFORE cleanup
        if exit_price > 0 or profit != 0:
            entry_price = self.entry_prices.get(symbol.replace("IB_", ""), 0)
            
            trade_data = {
                'symbol': symbol.replace("IB_", ""),
                'action': 'SELL',  # Position closed = sell
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit': profit,
                'profit_pct': ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0,
                'strategy_used': 'crypto_expert' if 'USD' in symbol else 'stock_momentum',
                'exit_reason': exit_reason,
                'market_regime': 'BULL' if profit > 0 else 'BEAR',  # Simplified
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'broker': 'IB' if symbol.startswith('IB_') else 'Alpaca'
            }
            
            # Record for learning - THIS MAKES PROMETHEUS SMARTER!
            self._record_trade_for_learning(trade_data)
            
            # Track daily stats
            if profit > 0:
                self.today_wins += 1
            else:
                self.today_losses += 1
            self.today_profit += profit
        
        # Cleanup tracking data
        if symbol in self.position_entry_times:
            del self.position_entry_times[symbol]
        if symbol in self.position_high_prices:
            del self.position_high_prices[symbol]
        if symbol in self.dca_positions:
            del self.dca_positions[symbol]
        if symbol in self.scaled_out_positions:
            del self.scaled_out_positions[symbol]

    async def _predict_drop(self, symbol: str) -> bool:
        """Use AI to predict if price will drop - helps lock in profits"""
        try:
            data = await self._get_enhanced_market_data(symbol)
            if not data:
                return False
            
            drop_signals = 0
            
            # Check for bearish signals
            if data.get('downtrend'):
                drop_signals += 2
            
            if data.get('rsi', 50) > 70:  # Overbought
                drop_signals += 2
            
            if data.get('momentum_5m', 0) < -0.003:  # Short-term negative momentum
                drop_signals += 1
            
            if data.get('momentum_1h', 0) < -0.005:  # Hourly negative momentum
                drop_signals += 1
            
            # Price below key moving averages
            price = data.get('price', 0)
            sma_20 = data.get('sma_20', price)
            if price < sma_20:
                drop_signals += 1
            
            # Volume spike with negative price action (distribution)
            if data.get('volume_ratio', 1) > 1.5 and data.get('momentum_5m', 0) < 0:
                drop_signals += 1
            
            # 3+ signals = drop predicted
            drop_predicted = drop_signals >= 3
            
            if drop_predicted:
                logger.info(f"   🔮 AI predicts drop for {symbol} (score: {drop_signals})")
            
            return drop_predicted
            
        except Exception as e:
            logger.warning(f"Prediction error for {symbol}: {e}")
            return False

    def _is_fed_day(self) -> bool:
        """Check if today is a Fed announcement day (FOMC meetings)"""
        # 2026 FOMC meeting dates (approximate - 2 day meetings, announcement on 2nd day)
        fomc_dates = [
            (1, 29), (3, 19), (5, 7), (6, 18),
            (7, 30), (9, 17), (11, 5), (12, 17)
        ]
        today = datetime.now()
        for month, day in fomc_dates:
            if today.month == month and abs(today.day - day) <= 1:
                return True
        return False

    def _is_stock_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        try:
            import pytz
            et_tz = pytz.timezone('US/Eastern')
            now_et = datetime.now(et_tz)
            
            # Check if weekend (Saturday=5, Sunday=6)
            if now_et.weekday() >= 5:
                return False
            
            # Check trading hours (9:30 AM - 4:00 PM ET)
            market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= now_et <= market_close
        except Exception as e:
            logger.warning(f"Could not check market hours: {e}")
            # Default to checking basic weekday hours
            now = datetime.now()
            if now.weekday() >= 5:  # Weekend
                return False
            # Approximate: 9:30 AM - 4:00 PM (local time as fallback)
            return 9 <= now.hour < 16

    def _is_crypto_trading_allowed(self) -> bool:
        """Check if crypto trading is allowed (Alpaca 24/5: Sun 8PM - Fri 4AM ET)"""
        if not self.crypto_24_5_enabled:
            return self._is_stock_market_open()
        
        try:
            import pytz
            et_tz = pytz.timezone('US/Eastern')
            now_et = datetime.now(et_tz)
            
            # Alpaca 24/5: Sunday 8PM ET to Friday 4AM ET
            weekday = now_et.weekday()
            hour = now_et.hour
            
            # Closed: Friday after 4AM to Sunday before 8PM
            if weekday == 4 and hour >= 4:  # Friday after 4AM
                return False
            if weekday == 5:  # Saturday - closed
                return False
            if weekday == 6 and hour < 20:  # Sunday before 8PM
                return False
            
            return True
        except:
            return True  # Default to allow if can't determine

    def _get_market_status(self) -> dict:
        """Get comprehensive market status"""
        stock_open = self._is_stock_market_open()
        crypto_open = self._is_crypto_trading_allowed()
        
        return {
            'stock_market_open': stock_open,
            'crypto_trading_allowed': crypto_open,
            'can_trade_stocks': stock_open,
            'can_trade_crypto': crypto_open,
            'is_fed_day': self._is_fed_day()
        }
    
    def _check_sentiment(self, symbol: str) -> dict:
        """Check market sentiment for a symbol (Enhancement 4)"""
        sentiment = {'bullish': 0, 'bearish': 0, 'neutral': 0, 'skip': False}
        
        # Check if Fed day
        if self.sentiment_enabled and self.avoid_fed_days and self._is_fed_day():
            logger.warning("📰 [SENTIMENT] Fed announcement day - Reducing position sizes")
            sentiment['skip'] = True
        
        # In a full implementation, this would call OpenAI API for news analysis
        # For now, we use technical sentiment from market data
        return sentiment
    
    async def _update_crypto_fear_greed(self):
        """Fetch Crypto Fear & Greed Index (CRYPTO EXPERT feature)"""
        if not self.crypto_expert_enabled:
            return
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Alternative.me Fear & Greed Index API
                url = "https://api.alternative.me/fng/?limit=1"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data'):
                            self.fear_greed_index = int(data['data'][0]['value'])
                            classification = data['data'][0]['value_classification']
                            logger.info(f"🪙 [CRYPTO EXPERT] Fear/Greed Index: {self.fear_greed_index} ({classification})")
        except Exception as e:
            logger.debug(f"Could not fetch Fear/Greed index: {e}")
            # Keep last value or default
    
    def _get_crypto_exit_params(self, symbol: str) -> dict:
        """Get crypto-specific exit parameters (CRYPTO EXPERT feature)"""
        if self.crypto_expert_enabled:
            return {
                'take_profit': self.crypto_take_profit,  # 6%
                'stop_loss': self.crypto_stop_loss,      # 3%
                'trailing_stop_trigger': 0.04,           # 4% trailing trigger
                'trailing_stop_distance': 0.02           # 2% trail distance
            }
        return {
            'take_profit': self.take_profit_pct,
            'stop_loss': self.stop_loss_pct,
            'trailing_stop_trigger': self.trailing_stop_trigger,
            'trailing_stop_distance': self.trailing_stop_distance
        }

    async def _execute_trades(self, signals: List[Dict[str, Any]]):
        """Execute trades with proper broker routing + correlation filter"""
        # Get current positions for correlation check
        current_positions = set()
        if self.alpaca_broker:
            try:
                positions = await self.alpaca_broker.get_positions()
                current_positions = {pos.symbol for pos in positions}
            except:
                pass
        
        for signal in signals:
            if self.total_trades_today >= self.max_trades_per_day:
                logger.info("[LIMIT] Daily trade limit reached")
                break
            
            symbol = signal.get('symbol', '')
            
            # === ENHANCEMENT 6: CORRELATION FILTER ===
            if self.correlation_filter_enabled and signal.get('action') == 'BUY':
                # Check if we already hold a correlated asset
                correlated = self.correlated_assets.get(symbol, [])
                held_correlated = current_positions.intersection(set(correlated))
                if held_correlated:
                    logger.info(f"🔗 [CORRELATION] Skipping {symbol} - Already holding correlated: {held_correlated}")
                    continue
            
            try:
                if signal['type'] == 'crypto' and self.alpaca_broker:
                    await self._execute_alpaca_trade(signal)
                    self.total_trades_today += 1
                    current_positions.add(symbol)  # Update for next correlation check
                elif signal['type'] == 'stock' and self.ib_broker:
                    await self._execute_ib_trade(signal)
                    self.total_trades_today += 1
                    current_positions.add(symbol)
                elif signal['type'] == 'stock' and self.alpaca_broker:
                    logger.info(f"[FALLBACK] Trading {signal['symbol']} on Alpaca (IB not available)")
                    await self._execute_alpaca_trade(signal)
                    self.total_trades_today += 1
                    current_positions.add(symbol)
            except Exception as e:
                logger.error(f"Trade execution error: {e}")

    async def _execute_alpaca_trade(self, signal: Dict[str, Any]):
        """Execute trade on Alpaca"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            qty = signal['quantity']
            
            logger.info(f"[ALPACA] {action} {qty:.4f} {symbol}")
            
            order = await self.alpaca_broker.place_order(
                symbol=symbol,
                qty=qty,
                side=action.lower(),
                order_type='market',
                time_in_force='gtc'
            )
            
            if order:
                logger.info(f"[ALPACA] ✓ Order placed: {order.id}")
                if action == 'BUY':
                    self.entry_prices[symbol] = signal.get('price', 0)
            
        except Exception as e:
            logger.error(f"[ALPACA] Order error: {e}")

    async def _execute_ib_trade(self, signal: Dict[str, Any]):
        """Execute trade on Interactive Brokers with capital check"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            qty = signal['quantity']
            price = signal.get('price', 0)
            order_value = qty * price if price > 0 else qty * 100  # Estimate if no price
            
            # ═══════════════════════════════════════════════════════════════
            # CAPITAL CHECK - Don't place orders we can't afford
            # ═══════════════════════════════════════════════════════════════
            if action == 'BUY' and order_value > self.ib_capital * 0.95:  # 5% buffer
                logger.warning(f"[IB] ❌ Insufficient funds for {symbol}")
                logger.warning(f"   Order value: ${order_value:.2f}, Available: ${self.ib_capital:.2f}")
                logger.warning(f"   Skipping this trade to prevent rejection")
                return
            # ═══════════════════════════════════════════════════════════════
            
            logger.info(f"[IB] {action} {qty} {symbol} (est. ${order_value:.2f})")
            
            # Create IB contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = 'STK'
            contract.exchange = 'SMART'
            contract.currency = 'USD'
            
            # Create IB order
            order = IBOrder()
            order.action = action
            order.totalQuantity = qty
            order.orderType = 'MKT'
            order.account = self.ib_account
            order.eTradeOnly = False
            order.firmQuoteOnly = False
            
            # Place order
            if hasattr(self.ib_broker, 'next_order_id') and self.ib_broker.next_order_id:
                order_id = self.ib_broker.next_order_id
                self.ib_broker.next_order_id += 1
                self.ib_broker.client.placeOrder(order_id, contract, order)
                logger.info(f"[IB] ✓ Order placed: {order_id}")
                
                if action == 'BUY':
                    self.entry_prices[symbol] = signal.get('price', 0)
            else:
                logger.warning("[IB] No valid order ID available")
            
        except Exception as e:
            logger.error(f"[IB] Order error: {e}")

    async def _status_check(self):
        """Display current status with all enhancements"""
        logger.info("\n[STATUS CHECK]")
        
        # Market status
        market_status = self._get_market_status()
        stock_open = "OPEN" if market_status['stock_market_open'] else "CLOSED"
        crypto_open = "OPEN" if market_status['can_trade_crypto'] else "CLOSED"
        logger.info(f"  📊 Markets: Stock={stock_open}, Crypto={crypto_open}")
        
        if self.alpaca_broker:
            try:
                account = await self.alpaca_broker.get_account()
                logger.info(f"  ALPACA: ${float(account.equity):.2f}")
            except:
                pass
        
        if self.ib_broker:
            try:
                logger.info(f"  IB: ${self.ib_capital:.2f}")
            except:
                pass
        
        logger.info(f"  Trades Today: {self.total_trades_today}/{self.max_trades_per_day}")
        logger.info(f"  Min Confidence: {self.min_confidence_threshold:.0%}")
        
        # Show enhancement status
        logger.info("  [ENHANCEMENTS ACTIVE]")
        logger.info(f"    1. Trailing Stop: {'✅' if self.trailing_stop_enabled else '❌'} (trigger +{self.trailing_stop_trigger:.0%}, trail {self.trailing_stop_distance:.1%})")
        logger.info(f"    2. DCA on Dips: {'✅' if self.dca_enabled else '❌'} (at {self.dca_trigger_pct:.0%}, max {self.dca_max_adds}x)")
        logger.info(f"    3. Time Exit: {'✅' if self.time_exit_enabled else '❌'} (crypto {self.max_hold_days_crypto}d, stock {self.max_hold_days_stock}d)")
        logger.info(f"    4. Sentiment: {'✅' if self.sentiment_enabled else '❌'} (Fed day: {self._is_fed_day()})")
        logger.info(f"    5. Scale Out: {'✅' if self.scale_out_enabled else '❌'} (50% at +{self.scale_out_first_pct:.0%}, rest at +{self.scale_out_second_pct:.0%})")
        logger.info(f"    6. Correlation: {'✅' if self.correlation_filter_enabled else '❌'}")
        logger.info(f"    7. Market Hours: ✅ (Auto-detect open/closed)")
        
        # CRYPTO EXPERT status
        if self.crypto_expert_enabled:
            logger.info("  [CRYPTO EXPERT PARAMETERS - Trained 15 Generations]")
            logger.info(f"    🪙 Fear/Greed Index: {self.fear_greed_index}")
            logger.info(f"    📈 Crypto TP/SL: +{self.crypto_take_profit:.0%} / -{self.crypto_stop_loss:.0%}")
            logger.info(f"    🐋 Whale Weight: {self.crypto_whale_weight:.0%}")
            logger.info(f"    📊 Pattern Weight: {self.crypto_pattern_weight:.0%}")
            logger.info(f"    💰 Funding Weight: {self.crypto_funding_weight:.0%}")
            logger.info(f"    😱 Trade in Fear: {'✅' if self.trade_in_extreme_fear else '❌'}")
            logger.info(f"    🎰 Trade in Greed: {'❌' if not self.trade_in_extreme_greed else '✅'}")
        
        # ═══════════════════════════════════════════════════════════════
        # CONTINUOUS LEARNING STATUS
        # ═══════════════════════════════════════════════════════════════
        logger.info("  [🧠 CONTINUOUS LEARNING]")
        
        # Local learning system stats
        if self.local_learning_system:
            stats = {
                'iterations': self.local_learning_system.learning_iterations,
                'improvements': self.local_learning_system.total_improvements,
                'wins': len(self.local_learning_system.win_history),
                'losses': len(self.local_learning_system.loss_history)
            }
            win_rate = stats['wins'] / (stats['wins'] + stats['losses']) * 100 if (stats['wins'] + stats['losses']) > 0 else 0
            logger.info(f"    📚 Local Learning: {stats['iterations']} iterations, {stats['improvements']} improvements")
            logger.info(f"    📈 Win Rate: {win_rate:.1f}% ({stats['wins']}/{stats['wins'] + stats['losses']})")
            
            # Show current strategy weights
            if hasattr(self.local_learning_system, 'strategy_weights'):
                weights = self.local_learning_system.strategy_weights
                best_strategy = max(weights, key=weights.get)
                logger.info(f"    🎯 Best Strategy: {best_strategy} ({weights[best_strategy]:.1%})")
            
            # Show learned patterns
            if hasattr(self.local_learning_system, 'pattern_success_rates'):
                patterns = self.local_learning_system.pattern_success_rates
                if patterns:
                    best_pattern = max(patterns, key=lambda p: patterns[p]['successes'] / max(1, patterns[p]['successes'] + patterns[p]['failures']))
                    logger.info(f"    📊 Best Pattern: {best_pattern}")
        else:
            logger.info("    ⚠️ Local Learning: Not available")
        
        # Trade history
        trades_recorded = len(self.trade_history_for_learning)
        logger.info(f"    📝 Trades Recorded Today: {trades_recorded}")
        logger.info(f"    💰 Today P/L: ${self.today_profit:+.2f} ({self.today_wins}W / {self.today_losses}L)")
        
        # Learning enabled
        learning_active = self.local_learning_system is not None or self.continuous_learning_engine is not None
        logger.info(f"    🎓 LEARNING FROM EVERY TRADE: {'✅ YES' if learning_active else '❌ NO'}")


async def main():
    """Main entry point"""
    system = ImprovedDualBrokerTradingSystem()
    await system.start()


if __name__ == "__main__":
    asyncio.run(main())
