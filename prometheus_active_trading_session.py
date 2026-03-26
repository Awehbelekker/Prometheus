#!/usr/bin/env python3
"""
PROMETHEUS Active Trading Session
More aggressive trading with lower thresholds for R 10,000 capital
Real paper trading with actual trade execution
"""

import asyncio
import os
import sys
import json
import time
import sqlite3
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict
import logging
import pandas as pd
# NOTE: random import REMOVED - was causing 15% of trades to be random gambling

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import AI Intelligence Engines
try:
    from core.universal_reasoning_engine import UniversalReasoningEngine
    UNIVERSAL_REASONING_AVAILABLE = True
except Exception as e:
    UNIVERSAL_REASONING_AVAILABLE = False

try:
    from hybrid_ai_trading_engine import HybridAIEngine
    HYBRID_AI_AVAILABLE = True
except Exception as e:
    HYBRID_AI_AVAILABLE = False

try:
    from core.unified_ai_provider import UnifiedAIProvider
    UNIFIED_AI_AVAILABLE = True
except Exception as e:
    UNIFIED_AI_AVAILABLE = False

# Import AI Attribution Tracker for learning from trade outcomes
try:
    from core.ai_attribution_tracker import AIAttributionTracker
    AI_ATTRIBUTION_AVAILABLE = True
except Exception as e:
    AI_ATTRIBUTION_AVAILABLE = False

# Import 4 additional AI systems (Phase 3: Missing AI Integration)
try:
    from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
    MARKET_ORACLE_AVAILABLE = True
except Exception as e:
    MARKET_ORACLE_AVAILABLE = False

try:
    from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
    AGENT_COORDINATOR_AVAILABLE = True
except Exception as e:
    AGENT_COORDINATOR_AVAILABLE = False

try:
    from core.continuous_learning_engine import ContinuousLearningEngine, LearningMode
    CONTINUOUS_LEARNING_AVAILABLE = True
except Exception as e:
    CONTINUOUS_LEARNING_AVAILABLE = False

try:
    from core.ai_learning_engine import AILearningEngine
    AI_LEARNING_AVAILABLE = True
except Exception as e:
    AI_LEARNING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Asset class detection for TIME_EXIT (crypto vs stock)
CRYPTO_SYMBOLS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'DOT-USD', 'BNB-USD', 'XRP-USD', 'LINK-USD']

def _is_crypto_symbol(symbol: str) -> bool:
    """Detect if a symbol is crypto (for time exit logic)"""
    return symbol in CRYPTO_SYMBOLS or '-USD' in symbol

class PrometheusActiveTradingSession:
    """PROMETHEUS Active Trading Session - Aggressive Strategy"""
    
    def __init__(self):
        self.session_id = f"active_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.account_id = "DUN683505"
        self.starting_capital = 540.0  # USD equivalent of R 10,000

        # ═══════════════════════════════════════════════════════════════
        # AGGRESSIVE CONFIGURATION (Optimal from 10-year backtest)
        # Backtest result: 75.6% win rate, 2.42 Sharpe, 15.4% annual
        # ═══════════════════════════════════════════════════════════════
        self.position_size_pct = 0.12       # 12% of capital per position (AGGRESSIVE)
        self.max_position_size = self.starting_capital * self.position_size_pct  # $64.80
        self.max_daily_loss = self.starting_capital * 0.05  # 5% of capital ($27.00)
        self.max_daily_trades = 16          # 8 max positions × 2 (allows DCA adds)
        self.stop_loss_percent = 2.0        # 2% stop loss (AGGRESSIVE)
        self.take_profit_pct = 0.05         # 5% take profit (AGGRESSIVE)
        self.min_ai_score = 2               # Minimum AI score to trigger trade
        self.max_concurrent_positions = 8   # Max 8 open positions at once

        # ═══════════════════════════════════════════════════════════════
        # CIRCUIT BREAKER SETTINGS (NEW - Audit Fix)
        # ═══════════════════════════════════════════════════════════════
        self.max_consecutive_losses = 5  # Stop after 5 losses in a row
        self.consecutive_losses = 0      # Current loss streak
        self.circuit_breaker_triggered = False
        self.circuit_breaker_reason = None

        # ═══════════════════════════════════════════════════════════════
        # 6 AGGRESSIVE BACKTEST ENHANCEMENTS (Ported from shadow trading)
        # These produced 75.6% win rate / 2.42 Sharpe in 10-year backtest
        # ═══════════════════════════════════════════════════════════════

        # === ENHANCEMENT 1: TRAILING STOP ===
        self.trailing_stop_enabled = True
        self.trailing_stop_trigger = 0.02   # Activate at +2% profit
        self.trailing_stop_distance = 0.01  # Sell if drops 1% from high

        # === ENHANCEMENT 2: DCA ON DIPS ===
        self.dca_enabled = True
        self.dca_trigger_pct = -0.02   # Buy more if down 2%
        self.dca_max_adds = 2          # Max 2 DCA adds per position
        self.dca_position_pct = 0.05   # 5% of capital per DCA buy

        # === ENHANCEMENT 3: TIME-BASED EXIT ===
        self.time_exit_enabled = True
        self.max_hold_days_crypto = 3  # Exit crypto after 3 days if not profitable
        self.max_hold_days_stock = 7   # Exit stocks after 7 days if not profitable

        # === ENHANCEMENT 4: SCALE-OUT PROFITS ===
        self.scale_out_enabled = True
        self.scale_out_first_pct = 0.02   # Sell 50% at +2% (AGGRESSIVE config)
        self.scale_out_second_pct = 0.04  # Sell remaining at +4% (AGGRESSIVE config)

        # === ENHANCEMENT 5: CORRELATION FILTER ===
        self.correlation_filter_enabled = True
        self.max_correlated_positions = 2
        self.correlated_assets = {
            'BTC-USD': ['ETH-USD', 'SOL-USD', 'LINK-USD'],
            'ETH-USD': ['BTC-USD', 'SOL-USD'],
            'SOL-USD': ['BTC-USD', 'ETH-USD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'GOOGL': ['AAPL', 'MSFT'],
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
        self.position_highs: Dict[str, float] = {}       # Track highest price (trailing stop)
        self.position_entry_times: Dict[str, datetime] = {}  # Track entry time (time exit)
        self.scaled_positions: Dict[str, int] = {}        # Track scale-out level (0, 1, 2)
        self.dca_counts: Dict[str, int] = {}              # Track DCA buys per position

        # Database for position tracking persistence
        self.db_path = str(Path(__file__).parent / 'prometheus_learning.db')
        self._load_position_tracking()

        # Session tracking
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.positions = {}
        self.session_start = datetime.now()
        self.portfolio_value = self.starting_capital
        
        # Market data
        self.market_data_cache = {}
        
        # Initialize AI Intelligence Engines (THE BRAIN)
        self.ai_brain_active = False
        self.universal_reasoning = None
        self.hybrid_ai = None
        self.unified_ai = None

        # ═══════════════════════════════════════════════════════════════
        # AI ATTRIBUTION TRACKER - Learn from trade outcomes (Audit Fix HIGH-003)
        # ═══════════════════════════════════════════════════════════════
        self.ai_attribution_tracker = None
        if AI_ATTRIBUTION_AVAILABLE:
            try:
                self.ai_attribution_tracker = AIAttributionTracker()
                logger.info("🎯 AI Attribution Tracker initialized - Learning from trade outcomes")
            except Exception as e:
                logger.warning(f"AI Attribution Tracker init failed: {e}")

        # ═══════════════════════════════════════════════════════════════
        # PHASE 3: 4 Additional AI Systems (Missing from live trading)
        # ═══════════════════════════════════════════════════════════════
        self.market_oracle = None
        self.agent_coordinator = None
        self.continuous_learning = None
        self.ai_learning = None

        self._initialize_ai_brain()
    
    def _initialize_ai_brain(self):
        """Initialize the AI brain for true intelligence"""
        logger.info("🧠 Initializing PROMETHEUS AI Brain...")
        
        # Try Universal Reasoning Engine first (most powerful)
        if UNIVERSAL_REASONING_AVAILABLE:
            try:
                self.universal_reasoning = UniversalReasoningEngine()
                self.ai_brain_active = True
                logger.info("✅ Universal Reasoning Engine initialized (HRM + GPT-OSS + Quantum + Memory)")
            except Exception as e:
                logger.warning(f"Universal Reasoning initialization failed: {e}")
        
        # Try Hybrid AI Engine (free local + paid fallback)
        if HYBRID_AI_AVAILABLE and not self.ai_brain_active:
            try:
                self.hybrid_ai = HybridAIEngine()
                if self.hybrid_ai.check_gpt_oss_available():
                    self.ai_brain_active = True
                    logger.info("✅ Hybrid AI Engine initialized (GPT-OSS 20B local + OpenAI fallback)")
                else:
                    logger.warning("Hybrid AI Engine created but GPT-OSS not available")
            except Exception as e:
                logger.warning(f"Hybrid AI initialization failed: {e}")
        
        # Try Unified AI Provider (DeepSeek-R1 local)
        if UNIFIED_AI_AVAILABLE and not self.ai_brain_active:
            try:
                self.unified_ai = UnifiedAIProvider()
                self.ai_brain_active = True
                logger.info("✅ Unified AI Provider initialized (DeepSeek-R1 8B local)")
            except Exception as e:
                logger.warning(f"Unified AI initialization failed: {e}")
        
        if self.ai_brain_active:
            logger.info("🧠 AI BRAIN ACTIVE - True intelligence enabled")
        else:
            logger.warning("⚠️ AI BRAIN INACTIVE - Using mathematical fallback")
        self.enhanced_data_cache = {}  # Cache for 8 intelligence sources
        
        # Initialize Real-World Data Orchestrator
        try:
            from core.real_world_data_orchestrator import RealWorldDataOrchestrator
            self.orchestrator = RealWorldDataOrchestrator()
            logger.info("✅ Real-World Data Orchestrator initialized")
        except Exception as e:
            logger.warning(f"Orchestrator init error: {e}")
            self.orchestrator = None

        # ═══════════════════════════════════════════════════════════════
        # PHASE 3: Initialize 4 Additional AI Systems
        # ═══════════════════════════════════════════════════════════════

        # Market Oracle Engine (predictive analysis with RAGFlow)
        if MARKET_ORACLE_AVAILABLE:
            try:
                oracle_config = {
                    'ragflow_api_key': os.getenv('RAGFLOW_API_KEY', 'demo_key'),
                    'ragflow_base_url': os.getenv('RAGFLOW_BASE_URL', 'http://localhost:9380'),
                    'prediction_horizon': '24h',
                    'confidence_threshold': 0.72
                }
                self.market_oracle = MarketOracleEngine(oracle_config)
                logger.info("✅ Market Oracle Engine initialized (RAGFlow predictions)")
            except Exception as e:
                logger.warning(f"Market Oracle init failed: {e}")

        # Hierarchical Agent Coordinator (17 agents + 3 supervisors)
        if AGENT_COORDINATOR_AVAILABLE:
            try:
                self.agent_coordinator = HierarchicalAgentCoordinator()
                logger.info("✅ Hierarchical Agent Coordinator initialized (17 agents + 3 supervisors)")
            except Exception as e:
                logger.warning(f"Agent Coordinator init failed: {e}")

        # Continuous Learning Engine (learns from trade outcomes)
        if CONTINUOUS_LEARNING_AVAILABLE:
            try:
                self.continuous_learning = ContinuousLearningEngine(LearningMode.AGGRESSIVE)
                logger.info("✅ Continuous Learning Engine initialized (AGGRESSIVE mode)")
            except Exception as e:
                logger.warning(f"Continuous Learning init failed: {e}")

        # AI Learning Engine (pattern recognition)
        if AI_LEARNING_AVAILABLE:
            try:
                self.ai_learning = AILearningEngine()
                logger.info("✅ AI Learning Engine initialized (pattern recognition)")
            except Exception as e:
                logger.warning(f"AI Learning Engine init failed: {e}")
    
    async def _ai_reasoning_decision(self, symbol: str, market_data: dict, enhanced: dict) -> dict:
        """Use AI brain for intelligent trading decisions"""
        try:
            # Prepare context for AI
            price = market_data.get('price', 0)
            momentum = market_data.get('momentum_5min', 0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            rsi_like = market_data.get('rsi_like', 0.5)
            
            visual_patterns = enhanced.get('visual_patterns', [])
            sentiment = enhanced.get('sentiment', 0.5)
            news_sentiment = enhanced.get('news_sentiment', 0.5)
            social_sentiment = enhanced.get('social_sentiment', 0.5)
            risk_level = enhanced.get('risk_level', 0.5)
            
            # Build AI prompt
            prompt = f"""PROMETHEUS Trading Decision for {symbol}:

MARKET DATA:
- Current Price: ${price:.2f}
- Momentum (5min): {momentum:.2%}
- Volume Ratio: {volume_ratio:.2f}x average
- RSI-like: {rsi_like:.2f}

INTELLIGENCE SOURCES:
- Visual AI Patterns: {', '.join([p.get('pattern', 'None') for p in visual_patterns[:3]]) if visual_patterns else 'None detected'}
- Market Sentiment: {sentiment:.2f}
- News Sentiment: {news_sentiment:.2f}
- Social Sentiment: {social_sentiment:.2f}
- Risk Level: {risk_level:.2f}

Available Capital: ${self.max_position_size:.2f}
Daily Trades Used: {self.trades_today}/{self.max_daily_trades}

ANALYZE and provide trading decision:
1. Action: BUY, SELL, or HOLD
2. Confidence: 0-100%
3. Quantity: number of shares (max {int(self.max_position_size / price) if price > 0 else 0})
4. Reason: brief explanation
5. Risk Assessment: LOW/MEDIUM/HIGH

Format response as: ACTION|CONFIDENCE|QUANTITY|REASON|RISK"""

            # Try Universal Reasoning first
            if self.universal_reasoning:
                try:
                    context_data = {
                        'symbol': symbol,
                        'market_data': market_data,
                        'intelligence': enhanced,
                        'quantity': int(self.max_position_size / price) if price > 0 else 0
                    }
                    result = self.universal_reasoning.make_ultimate_decision(context_data)
                    if result and result.get('action'):
                        return {
                            'action': result.get('action', 'HOLD'),
                            'confidence': result.get('confidence', 0.7),
                            'quantity': result.get('quantity', 0),
                            'reason': f'🧠 Universal Reasoning: {result.get("reasoning", "Multi-source consensus")}',
                            'target_price': price * (1 + self.take_profit_pct) if result.get('action') == 'BUY' else price * (1 - self.take_profit_pct),
                            'stop_loss': price * (1 - self.stop_loss_percent / 100) if result.get('action') == 'BUY' else price * (1 + self.stop_loss_percent / 100),
                            'ai_decision': True,
                            'enhanced_intelligence': True
                        }
                except Exception as e:
                    logger.warning(f"Universal Reasoning failed: {e}")
            
            # Try Hybrid AI
            if self.hybrid_ai:
                try:
                    result = await self.hybrid_ai.analyze_market(symbol, {
                        'price': price,
                        'momentum': momentum,
                        'volume_ratio': volume_ratio,
                        'sentiment': sentiment,
                        'risk': risk_level
                    })
                    if result:
                        return self._parse_ai_response(result, price, symbol)
                except Exception as e:
                    logger.warning(f"Hybrid AI failed: {e}")
            
            # Try Unified AI (DeepSeek-R1)
            if self.unified_ai:
                try:
                    result = await self.unified_ai.generate_async(prompt, max_tokens=200, temperature=0.3)
                    if result.get('success'):
                        return self._parse_ai_response(result.get('response', ''), price, symbol)
                except Exception as e:
                    logger.warning(f"Unified AI failed: {e}")
            
            # If all AI fails, return None to use mathematical fallback
            return None
            
        except Exception as e:
            logger.error(f"AI reasoning error: {e}")
            return None
    
    def _parse_ai_response(self, response: str, price: float, symbol: str) -> dict:
        """Parse AI response into trading decision"""
        try:
            # Try structured format: ACTION|CONFIDENCE|QUANTITY|REASON|RISK
            if '|' in response:
                parts = response.split('|')
                if len(parts) >= 4:
                    action = parts[0].strip().upper()
                    confidence = float(parts[1].strip().replace('%', '')) / 100
                    quantity = int(parts[2].strip())
                    reason = parts[3].strip()
                    
                    if action not in ['BUY', 'SELL', 'HOLD']:
                        action = 'HOLD'
                    
                    max_shares = int(self.max_position_size / price) if price > 0 else 0
                    quantity = min(quantity, max_shares)
                    
                    return {
                        'action': action,
                        'confidence': min(0.95, max(0.5, confidence)),
                        'quantity': quantity if action != 'HOLD' else 0,
                        'reason': f'🧠 AI: {reason}',
                        'target_price': price * (1 + self.take_profit_pct) if action == 'BUY' else price * (1 - self.take_profit_pct),
                        'stop_loss': price * (1 - self.stop_loss_percent / 100) if action == 'BUY' else price * (1 + self.stop_loss_percent / 100),
                        'ai_decision': True,
                        'enhanced_intelligence': True
                    }
            
            # Try text parsing for BUY/SELL/HOLD keywords
            response_upper = response.upper()
            if 'BUY' in response_upper and 'NOT' not in response_upper:
                return {
                    'action': 'BUY',
                    'confidence': 0.7,
                    'quantity': max(1, int(self.max_position_size / price) // 2) if price > 0 else 0,
                    'reason': f'🧠 AI: {response[:100]}',
                    'target_price': price * (1 + self.take_profit_pct),
                    'stop_loss': price * (1 - self.stop_loss_percent / 100),
                    'ai_decision': True,
                    'enhanced_intelligence': True
                }
            elif 'SELL' in response_upper:
                if symbol in self.positions and self.positions[symbol]:
                    long_positions = [pos for pos in self.positions[symbol] if pos['action'] == 'BUY']
                    if long_positions:
                        return {
                            'action': 'SELL',
                            'confidence': 0.7,
                            'quantity': sum(pos['quantity'] for pos in long_positions),
                            'reason': f'🧠 AI: {response[:100]}',
                            'target_price': price * (1 - self.take_profit_pct),
                            'stop_loss': price * (1 + self.stop_loss_percent / 100),
                            'ai_decision': True,
                            'enhanced_intelligence': True
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"AI response parsing failed: {e}")
            return None
        
    async def initialize_ib_connection(self):
        """Initialize IB connection for order execution"""
        try:
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            import threading
            import time
            
            class ActiveIBWrapper(EWrapper):
                def __init__(self, session):
                    self.session = session
                    self.connected = False
                    self.next_order_id = None
                    self.market_data = {}  # Store live market data from IB
                    
                def error(self, reqId, errorCode, errorString):
                    if errorCode in [2104, 2107, 2158, 2106]:
                        logger.info(f"IB Info {errorCode}: {errorString}")
                    else:
                        logger.warning(f"IB Error {errorCode}: {errorString}")
                
                def nextValidId(self, orderId):
                    self.next_order_id = orderId
                    self.connected = True
                    logger.info(f"IB ready - Next order ID: {orderId}")
                
                def tickPrice(self, reqId, tickType, price, attrib):
                    """Receive real-time price data from IB"""
                    if reqId not in self.market_data:
                        self.market_data[reqId] = {}
                    # tickType: 1=bid, 2=ask, 4=last, 6=high, 7=low, 9=close
                    tick_names = {1: 'bid', 2: 'ask', 4: 'last', 6: 'high', 7: 'low', 9: 'close'}
                    if tickType in tick_names:
                        self.market_data[reqId][tick_names[tickType]] = price
                
                def tickSize(self, reqId, tickType, size):
                    """Receive real-time size data from IB"""
                    if reqId not in self.market_data:
                        self.market_data[reqId] = {}
                    # tickType: 0=bid_size, 3=ask_size, 5=last_size, 8=volume
                    tick_names = {0: 'bid_size', 3: 'ask_size', 5: 'last_size', 8: 'volume'}
                    if tickType in tick_names:
                        self.market_data[reqId][tick_names[tickType]] = size
            
            # Initialize connection
            self.ib_wrapper = ActiveIBWrapper(self)
            self.ib_client = EClient(self.ib_wrapper)
            
            # Get IB port from .env (4002 for live, 7497 for paper)
            ib_port = int(os.getenv('IB_PORT', '4002'))
            print(f"🔌 Connecting to IB Gateway on port {ib_port} for LIVE trading...")
            self.ib_client.connect("127.0.0.1", ib_port, 4)
            
            # Start API thread
            api_thread = threading.Thread(target=self.ib_client.run, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.ib_client.isConnected() and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.ib_client.isConnected():
                # Wait for ready signal
                start_time = time.time()
                while not self.ib_wrapper.connected and (time.time() - start_time) < 5:
                    await asyncio.sleep(0.1)
                
                print("[CHECK] IB connection ready for active trading")
                self.ib_req_id = 1000  # Start request ID counter for market data
                return True
            else:
                print("[ERROR] Failed to connect to IB Gateway")
                return False
                
        except Exception as e:
            logger.error(f"IB connection error: {e}")
            return False
    
    async def get_ib_market_data(self, symbol: str) -> dict:
        """Get real-time market data from IB Gateway (FREE with your broker!)"""
        try:
            if not hasattr(self, 'ib_client') or not self.ib_client.isConnected():
                return None
            
            from ibapi.contract import Contract
            
            # Create contract
            contract = Contract()
            contract.symbol = symbol.replace('-USD', '')  # Handle crypto format
            
            # Determine contract type
            if symbol.endswith('-USD') or symbol in ['BTC', 'ETH', 'SOL', 'ADA', 'DOGE', 'AVAX']:
                contract.secType = "CRYPTO"
                contract.exchange = "PAXOS"
                contract.currency = "USD"
            elif '=' in symbol:  # Forex
                contract.secType = "CASH"
                base = symbol.replace('=X', '')[:3]
                quote = symbol.replace('=X', '')[3:]
                contract.symbol = base
                contract.currency = quote
                contract.exchange = "IDEALPRO"
            else:  # Stock
                contract.secType = "STK"
                contract.exchange = "SMART"
                contract.currency = "USD"
            
            # Request market data
            req_id = self.ib_req_id
            self.ib_req_id += 1
            self.ib_wrapper.market_data[req_id] = {'symbol': symbol}
            
            self.ib_client.reqMktData(req_id, contract, "", False, False, [])
            
            # Wait for data (up to 2 seconds)
            for _ in range(20):
                await asyncio.sleep(0.1)
                data = self.ib_wrapper.market_data.get(req_id, {})
                if 'last' in data or 'bid' in data:
                    break
            
            # Cancel market data subscription
            self.ib_client.cancelMktData(req_id)
            
            data = self.ib_wrapper.market_data.get(req_id, {})
            if 'last' in data or 'bid' in data:
                price = data.get('last', data.get('bid', 0))
                logger.info(f"📡 IB LIVE: {symbol} = ${price:.2f}")
                return {
                    'price': price,
                    'bid': data.get('bid', price),
                    'ask': data.get('ask', price),
                    'volume': data.get('volume', 0),
                    'source': 'IB_GATEWAY'
                }
            return None
            
        except Exception as e:
            logger.debug(f"IB market data for {symbol} failed: {e}")
            return None
    
    async def get_enhanced_market_data(self, symbols):
        """Get enhanced market data - tries IB first, falls back to Yahoo Finance"""
        try:
            # Check if IB is connected
            ib_available = hasattr(self, 'ib_client') and hasattr(self, 'ib_wrapper') and self.ib_client.isConnected()
            
            if ib_available:
                print("📊 Fetching market data from IB Gateway (FREE broker data!)...")
            else:
                print("📊 Fetching market data from Yahoo Finance (IB not connected)...")
            
            market_data = {}
            ib_data_count = 0
            yf_data_count = 0
            
            for symbol in symbols:
                try:
                    # Try IB first if available
                    ib_price = None
                    if ib_available:
                        ib_data = await self.get_ib_market_data(symbol)
                        if ib_data and ib_data.get('price', 0) > 0:
                            ib_price = ib_data['price']
                            ib_data_count += 1
                    
                    # Get historical data from Yahoo for technical indicators
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d", interval="5m")
                    info = ticker.info
                    
                    if len(hist) < 20:
                        continue
                    
                    # Use IB price if available, otherwise Yahoo
                    if ib_price and ib_price > 0:
                        current_price = ib_price
                        data_source = "IB"
                    else:
                        current_price = hist['Close'].iloc[-1]
                        data_source = "YF"
                        yf_data_count += 1
                    
                    volume = hist['Volume'].iloc[-1]
                    
                    # Calculate technical indicators
                    # 1. Short-term momentum (5 periods)
                    momentum_5 = (current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]
                    
                    # 2. Volume momentum
                    avg_volume = hist['Volume'].tail(20).mean()
                    volume_ratio = volume / avg_volume
                    
                    # 3. Price volatility
                    volatility = hist['Close'].tail(20).std() / hist['Close'].tail(20).mean()
                    
                    # 4. Simple moving averages
                    sma_5 = hist['Close'].tail(5).mean()
                    sma_20 = hist['Close'].tail(20).mean()
                    sma_signal = (current_price - sma_5) / sma_5
                    
                    # 5. RSI-like momentum
                    price_changes = hist['Close'].diff().tail(14)
                    gains = price_changes.where(price_changes > 0, 0).mean()
                    losses = -price_changes.where(price_changes < 0, 0).mean()
                    rsi_like = gains / (gains + losses) if (gains + losses) > 0 else 0.5
                    
                    # Determine trend direction for pattern matching
                    trend_direction = 'sideways'
                    if current_price > sma_5 and sma_5 > sma_20:
                        trend_direction = 'up'
                    elif current_price < sma_5 and sma_5 < sma_20:
                        trend_direction = 'down'
                    
                    market_data[symbol] = {
                        'symbol': symbol,  # Include symbol for pattern matching
                        'price': float(current_price),
                        'volume': int(volume),
                        'momentum_5min': float(momentum_5),
                        'volume_ratio': float(volume_ratio),
                        'volatility': float(volatility),
                        'sma_signal': float(sma_signal),
                        'rsi_like': float(rsi_like),
                        'trend': trend_direction,  # Add trend for pattern matching
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 0),
                        'timestamp': datetime.now().isoformat(),
                        'data_source': data_source
                    }
                    
                    print(f"📈 {symbol}: ${current_price:.2f} | Mom: {momentum_5:.2%} | Vol: {volume_ratio:.1f}x | RSI: {rsi_like:.2f} [{data_source}]")
                    
                except Exception as e:
                    logger.warning(f"Error fetching enhanced data for {symbol}: {e}")
                    continue
            
            # Summary of data sources
            if ib_data_count > 0:
                print(f"📡 Data sources: {ib_data_count} from IB Gateway (FREE), {yf_data_count} from Yahoo Finance")
            
            self.market_data_cache.update(market_data)
            return market_data
            
        except Exception as e:
            logger.error(f"Enhanced market data error: {e}")
            return {}
    
    def _get_enhanced_intelligence(self, symbol: str) -> dict:
        """
        Get ALL 8 intelligence sources (same as learning engine)
        🧠 Visual AI + Sentiment + Risk + News + Social + Trends + Crypto
        Cache for 1 hour to reduce API calls
        """
        cache_key = f"{symbol}_{int(time.time() / 3600)}"
        if cache_key in self.enhanced_data_cache:
            return self.enhanced_data_cache[cache_key]
        
        enhanced_data = {}
        
        try:
            # 1. Visual AI Patterns (from 1,320 trained charts, 452 patterns)
            from core.visual_pattern_provider import VisualPatternProvider
            pattern_provider = VisualPatternProvider('visual_ai_patterns_cloud.json')
            patterns = pattern_provider.get_patterns_for_symbol(symbol)
            enhanced_data['visual_patterns'] = patterns
            enhanced_data['visual_pattern_count'] = len(patterns)
            
            # 2-4. Real-World Orchestrator (sentiment, risk, opportunity)
            # Store async task for later execution
            enhanced_data['orchestrator_context'] = {
                'symbols': [symbol],
                'timestamp': time.time(),
                'strategy': 'aggressive'
            } if self.orchestrator else None
            
            # Set default values (will be updated async in analysis)
            enhanced_data.update({
                'sentiment': 0.5, 'risk_level': 0.5, 'opportunity_score': 0.5,
                'news_sentiment': 0.5, 'social_sentiment': 0.5, 'social_volume': 0,
                'trend_score': 0.5, 'market_regime': 'unknown'
            })
            
            # PHASE 3: AI Learning Engine market insights
            if self.ai_learning:
                try:
                    insights = self.ai_learning.get_market_insights()
                    enhanced_data['ai_learning_patterns'] = insights.get('total_patterns', 0)
                    ai_sentiment = insights.get('market_sentiment', 'neutral')
                    if ai_sentiment == 'bullish':
                        enhanced_data['sentiment'] = min(1.0, enhanced_data['sentiment'] + 0.1)
                    elif ai_sentiment == 'bearish':
                        enhanced_data['sentiment'] = max(0.0, enhanced_data['sentiment'] - 0.1)
                except Exception as e:
                    logger.debug(f"AI Learning insights failed: {e}")

            logger.info(f"🧠 Enhanced Intelligence for {symbol}: "
                       f"Patterns={enhanced_data['visual_pattern_count']}, "
                       f"Sentiment={enhanced_data['sentiment']:.2f}, "
                       f"Risk={enhanced_data['risk_level']:.2f}")

        except Exception as e:
            logger.warning(f"Enhanced intelligence error for {symbol}: {e}")
            enhanced_data = {
                'visual_patterns': [], 'visual_pattern_count': 0,
                'sentiment': 0.5, 'risk_level': 0.5, 'opportunity_score': 0.5,
                'news_sentiment': 0.5, 'social_sentiment': 0.5, 'social_volume': 0,
                'trend_score': 0.5
            }
        
        self.enhanced_data_cache[cache_key] = enhanced_data
        return enhanced_data
    
    async def prometheus_aggressive_analysis(self, symbol, market_data):
        """🚀 PROMETHEUS FULL INTELLIGENCE ANALYSIS - 8 Data Sources + Visual AI"""
        try:
            # Get ALL 8 intelligence sources (Visual AI loaded here)
            enhanced = self._get_enhanced_intelligence(symbol)
            
            # Get Real-World Intelligence (async)
            if enhanced.get('orchestrator_context') and self.orchestrator:
                try:
                    global_intel = await self.orchestrator.generate_contextual_intelligence(
                        enhanced['orchestrator_context']
                    )
                    enhanced['sentiment'] = global_intel.overall_sentiment
                    enhanced['risk_level'] = global_intel.risk_level
                    enhanced['opportunity_score'] = global_intel.opportunity_score
                    enhanced['market_regime'] = global_intel.market_regime
                    enhanced['news_sentiment'] = global_intel.overall_sentiment
                    enhanced['social_sentiment'] = global_intel.overall_sentiment
                    enhanced['social_volume'] = len(global_intel.key_signals)
                    enhanced['trend_score'] = global_intel.opportunity_score
                    logger.info(f"✅ Real-World Intel: sentiment={global_intel.overall_sentiment:.2f}, "
                               f"risk={global_intel.risk_level:.2f}, regime={global_intel.market_regime}")
                except Exception as e:
                    logger.warning(f"Orchestrator error for {symbol}: {e}")
                    # Use fallback values already in enhanced dict
            
            price = market_data['price']
            momentum = market_data['momentum_5min']
            volume_ratio = market_data['volume_ratio']
            volatility = market_data['volatility']
            sma_signal = market_data['sma_signal']
            rsi_like = market_data['rsi_like']
            
            # Calculate position size based on price
            max_shares = int(self.max_position_size / price)
            
            # AGGRESSIVE PROMETHEUS AI Decision Logic
            decision = {
                'action': 'HOLD',
                'confidence': 0.5,
                'reason': 'No clear signal',
                'quantity': 0,
                'target_price': price,
                'stop_loss': price * (1 - self.stop_loss_percent / 100),
                'enhanced_intelligence': True
            }
            
            # Pre-fetch oracle prediction for use in both BUY and SELL scoring
            oracle_pred = None
            if self.market_oracle:
                try:
                    from revolutionary_features.oracle.market_oracle_engine import TimeFrame
                    oracle_pred = await self.market_oracle.generate_market_prediction(
                        symbol=symbol,
                        timeframe=TimeFrame.HOUR_1,
                        market_data={'current_price': price, 'momentum': momentum}
                    )
                except Exception as e:
                    logger.debug(f"Market Oracle pre-fetch failed for {symbol}: {e}")

            # ====== PHASE 4: ADAPTIVE WEIGHTS FROM LEARNING FEEDBACK LOOP ======
            ai_weights = {}
            if self.ai_attribution_tracker:
                try:
                    ai_weights = await self.ai_attribution_tracker.get_ai_system_weights()
                    if ai_weights:
                        logger.debug(f"📊 Adaptive weights loaded: {ai_weights}")
                except Exception as e:
                    logger.debug(f"Adaptive weights fetch failed: {e}")

            # BUY Signals (More Aggressive)
            buy_score = 0
            buy_reasons = []
            
            # 1. Momentum signals (lowered thresholds)
            if momentum > 0.005:  # 0.5% momentum (was 2%)
                buy_score += 2
                buy_reasons.append(f"Momentum: {momentum:.2%}")
            
            # 2. Volume confirmation
            if volume_ratio > 1.2:  # 20% above average volume
                buy_score += 1
                buy_reasons.append(f"Volume: {volume_ratio:.1f}x")
            
            # 3. SMA signal
            if sma_signal > 0.002:  # Above 5-period SMA
                buy_score += 1
                buy_reasons.append("Above SMA")
            
            # 4. RSI-like oversold
            if rsi_like < 0.3:  # Oversold condition
                buy_score += 2
                buy_reasons.append("Oversold")
            
            # 5. Low volatility (stable)
            if volatility < 0.02:  # Low volatility
                buy_score += 1
                buy_reasons.append("Low volatility")
            
            # ====== ENHANCED INTELLIGENCE BOOSTS ======

            # 6. Visual AI Patterns (1,352 patterns from trained charts)
            # NOTE: Visual patterns currently trained on STOCKS only
            # Crypto symbols (BTC, ETH, SOL) need chart training via CLOUD_VISION_TRAINING.py
            visual_patterns = enhanced.get('visual_patterns', [])
            bullish_patterns = [
                'Bull Flag', 'Ascending Triangle', 'Double Bottom',
                'Inverse Head and Shoulders', 'Cup and Handle', 'Bullish Engulfing',
                'Rising Wedge', 'Bullish Pennant', 'Morning Star', 'Hammer'
            ]
            for pattern in visual_patterns:
                pattern_name = pattern.get('pattern', '')
                pattern_confidence = pattern.get('confidence', 0.5)
                if any(bp.lower() in pattern_name.lower() for bp in bullish_patterns):
                    # Scale boost by pattern confidence (3-6 points)
                    boost = 3 + int(pattern_confidence * 3)
                    buy_score += boost  # 🚀 HUGE boost for visual confirmation
                    buy_reasons.append(f"👁️ Visual AI: {pattern_name} ({pattern_confidence:.0%})")
                    break
            
            # 7. Sentiment boost
            sentiment = enhanced.get('sentiment', 0.5)
            if sentiment > 0.7:
                buy_score += 2
                buy_reasons.append(f"😊 Positive sentiment: {sentiment:.2f}")
            elif sentiment > 0.6:
                buy_score += 1
                buy_reasons.append(f"Sentiment: {sentiment:.2f}")
            
            # 8. Opportunity score
            opportunity = enhanced.get('opportunity_score', 0.5)
            if opportunity > 0.8:
                buy_score += 2
                buy_reasons.append(f"🎯 High opportunity: {opportunity:.2f}")
            elif opportunity > 0.7:
                buy_score += 1
                buy_reasons.append(f"Opportunity: {opportunity:.2f}")
            
            # 9. News sentiment
            news_sentiment = enhanced.get('news_sentiment', 0.5)
            if news_sentiment > 0.6:
                buy_score += 1
                buy_reasons.append(f"📰 Positive news: {news_sentiment:.2f}")
            
            # 10. Social momentum
            social_sentiment = enhanced.get('social_sentiment', 0.5)
            social_volume = enhanced.get('social_volume', 0)
            if social_sentiment > 0.6 and social_volume > 100:
                buy_score += 1.5
                buy_reasons.append(f"📱 Social buzz: {social_sentiment:.2f} ({social_volume} mentions)")
            
            # 11. Trending
            trend_score = enhanced.get('trend_score', 0.5)
            if trend_score > 0.7:
                buy_score += 1
                buy_reasons.append(f"📈 Trending: {trend_score:.2f}")

            # ====== PHASE 3: MARKET ORACLE + AGENT COORDINATOR ======

            # 12. Market Oracle Prediction (RAGFlow-enhanced) - uses pre-fetched oracle_pred
            #     PHASE 4: Apply adaptive weight from learning feedback
            if oracle_pred:
                try:
                    from revolutionary_features.oracle.market_oracle_engine import MarketDirection
                    oracle_dir = oracle_pred.direction
                    oracle_conf = oracle_pred.confidence_percentage
                    oracle_weight = ai_weights.get('Market_Oracle', 1.0)
                    if oracle_dir in (MarketDirection.BULLISH, MarketDirection.STRONG_BULLISH):
                        boost = (2 + int(oracle_conf * 2)) * oracle_weight
                        buy_score += boost
                        buy_reasons.append(f"🔮 Oracle: {oracle_dir.value} ({oracle_conf:.0%}) [w={oracle_weight:.2f}]")
                    elif oracle_dir in (MarketDirection.BEARISH, MarketDirection.STRONG_BEARISH):
                        buy_score -= 1
                except Exception as e:
                    logger.debug(f"Market Oracle buy signal failed for {symbol}: {e}")

            # 13. Agent Coordinator Consensus (17 agents + 3 supervisors)
            #     PHASE 4: Apply adaptive weight from learning feedback
            if self.agent_coordinator:
                try:
                    agent_result = await self.agent_coordinator.coordinate_trading_decision(
                        market_conditions={
                            'symbol': symbol, 'price': price,
                            'momentum': momentum, 'volatility': volatility, 'rsi_like': rsi_like
                        },
                        engine_performance={
                            'consecutive_losses': self.consecutive_losses,
                            'daily_pnl': self.daily_pnl,
                            'trades_today': self.trades_today
                        },
                        target_return=self.take_profit_pct * 100
                    )
                    if agent_result and agent_result.get('confidence', 0) > 0.6:
                        agent_conf = agent_result.get('confidence', 0.5)
                        agent_weight = ai_weights.get('Hierarchical_Agents', 1.0)
                        boost = (1 + int(agent_conf * 2)) * agent_weight
                        buy_score += boost
                        buy_reasons.append(f"🤖 Agents: Confirmed ({agent_conf:.0%}) [w={agent_weight:.2f}]")
                except Exception as e:
                    logger.debug(f"Agent Coordinator failed for {symbol}: {e}")

            # SELL Signals
            sell_score = 0
            sell_reasons = []
            
            # 1. Negative momentum
            if momentum < -0.005:  # -0.5% momentum
                sell_score += 2
                sell_reasons.append(f"Negative momentum: {momentum:.2%}")
            
            # 2. Overbought
            if rsi_like > 0.7:
                sell_score += 2
                sell_reasons.append("Overbought")
            
            # 3. Below SMA
            if sma_signal < -0.002:
                sell_score += 1
                sell_reasons.append("Below SMA")
            
            # ====== ENHANCED INTELLIGENCE WARNINGS ======

            # 4. Visual AI Patterns (bearish)
            bearish_patterns = [
                'Head and Shoulders', 'Descending Triangle', 'Double Top',
                'Bear Flag', 'Falling Wedge', 'Bearish Engulfing',
                'Evening Star', 'Shooting Star', 'Dark Cloud Cover', 'Hanging Man'
            ]
            for pattern in visual_patterns:
                pattern_name = pattern.get('pattern', '')
                pattern_confidence = pattern.get('confidence', 0.5)
                if any(bp.lower() in pattern_name.lower() for bp in bearish_patterns):
                    # Scale warning by pattern confidence (3-6 points)
                    warning = 3 + int(pattern_confidence * 3)
                    sell_score += warning  # 🚨 HUGE warning from visual AI
                    sell_reasons.append(f"👁️ Visual AI Warning: {pattern_name} ({pattern_confidence:.0%})")
                    break
            
            # 5. Negative sentiment
            if sentiment < 0.3:
                sell_score += 2
                sell_reasons.append(f"😟 Negative sentiment: {sentiment:.2f}")
            elif sentiment < 0.4:
                sell_score += 1
                sell_reasons.append(f"Low sentiment: {sentiment:.2f}")
            
            # 6. High risk
            risk_level = enhanced.get('risk_level', 0.5)
            if risk_level > 0.7:
                sell_score += 2
                sell_reasons.append(f"⚠️ High risk: {risk_level:.2f}")

            # 7. Market Oracle bearish prediction (sell-side) - PHASE 4: adaptive weight
            if oracle_pred:
                try:
                    from revolutionary_features.oracle.market_oracle_engine import MarketDirection
                    oracle_dir = oracle_pred.direction
                    oracle_conf = oracle_pred.confidence_percentage
                    oracle_weight = ai_weights.get('Market_Oracle', 1.0)
                    if oracle_dir in (MarketDirection.BEARISH, MarketDirection.STRONG_BEARISH):
                        warning = (2 + int(oracle_conf * 2)) * oracle_weight
                        sell_score += warning
                        sell_reasons.append(f"🔮 Oracle: {oracle_dir.value} ({oracle_conf:.0%}) [w={oracle_weight:.2f}]")
                except Exception as e:
                    logger.debug(f"Market Oracle sell signal failed: {e}")

            # ====== AUTONOMOUS RISK BLOCK ======
            # If risk is EXTREMELY high, block all trades
            if risk_level > 0.85:
                logger.warning(f"🚫 RISK TOO HIGH for {symbol}: {risk_level:.2f} - BLOCKING TRADES")
                return {
                    'action': 'HOLD',
                    'confidence': 0.95,
                    'reason': f'🚫 RISK TOO HIGH ({risk_level:.2f}) - Autonomous block active',
                    'quantity': 0,
                    'target_price': price,
                    'stop_loss': price,
                    'enhanced_intelligence': True,
                    'risk_blocked': True
                }
            
            # ====== AI REASONING DECISION (PRIMARY) ======
            if self.ai_brain_active:
                ai_decision = await self._ai_reasoning_decision(symbol, market_data, enhanced)
                if ai_decision:
                    logger.info(f"🧠 AI Brain made decision for {symbol}: {ai_decision['action']} (confidence: {ai_decision['confidence']:.1%})")
                    return ai_decision
                else:
                    logger.info(f"⚠️ AI Brain returned no decision, using mathematical fallback")
            
            # ====== MATHEMATICAL FALLBACK (if AI fails or inactive) ======
            # Decision logic
            if buy_score >= self.min_ai_score and max_shares > 0:  # AGGRESSIVE: min_ai_score threshold
                confidence = min(0.9, 0.6 + (buy_score * 0.1))
                decision.update({
                    'action': 'BUY',
                    'confidence': confidence,
                    'reason': ' + '.join(buy_reasons),
                    'quantity': max_shares,
                    'target_price': price * (1 + self.take_profit_pct),  # 5% target (AGGRESSIVE)
                    'stop_loss': price * (1 - self.stop_loss_percent / 100)  # 2% stop (AGGRESSIVE)
                })

            elif sell_score >= self.min_ai_score and symbol in self.positions and self.positions[symbol]:
                # Check if we have position to sell
                long_positions = [pos for pos in self.positions[symbol] if pos['action'] == 'BUY']
                if long_positions:
                    total_shares = sum(pos['quantity'] for pos in long_positions)
                    confidence = min(0.9, 0.6 + (sell_score * 0.1))
                    decision.update({
                        'action': 'SELL',
                        'confidence': confidence,
                        'reason': ' + '.join(sell_reasons),
                        'quantity': total_shares,
                        'target_price': price * (1 - self.take_profit_pct),  # 5% target (AGGRESSIVE)
                        'stop_loss': price * (1 + self.stop_loss_percent / 100)  # 2% stop (AGGRESSIVE)
                    })

            # ═══════════════════════════════════════════════════════════════
            # RANDOM TRADING CODE REMOVED (Audit Fix CRIT-001)
            # Previous code executed 15% of trades randomly - pure gambling
            # Now all trades require actual analysis signals
            # ═══════════════════════════════════════════════════════════════

            return decision
            
        except Exception as e:
            logger.error(f"Aggressive analysis error for {symbol}: {e}")
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Analysis error', 'quantity': 0}
    
    async def execute_paper_trade(self, symbol, decision, market_data):
        """Execute paper trade with detailed tracking"""
        if decision['quantity'] == 0 or decision['action'] == 'HOLD':
            return None

        # ═══════════════════════════════════════════════════════════════
        # CIRCUIT BREAKER CHECKS (Audit Fix CRIT-001, HIGH-001)
        # ═══════════════════════════════════════════════════════════════
        if self.circuit_breaker_triggered:
            print(f"🛑 CIRCUIT BREAKER ACTIVE: {self.circuit_breaker_reason}")
            print("   Trading halted to protect capital. Reset session to continue.")
            return None

        if self.consecutive_losses >= self.max_consecutive_losses:
            self.circuit_breaker_triggered = True
            self.circuit_breaker_reason = f"Max consecutive losses reached ({self.max_consecutive_losses})"
            print(f"🛑 CIRCUIT BREAKER TRIGGERED: {self.circuit_breaker_reason}")
            return None

        if abs(self.daily_pnl) >= self.max_daily_loss and self.daily_pnl < 0:
            self.circuit_breaker_triggered = True
            self.circuit_breaker_reason = f"Max daily loss exceeded (${abs(self.daily_pnl):.2f})"
            print(f"🛑 CIRCUIT BREAKER TRIGGERED: {self.circuit_breaker_reason}")
            return None
        # ═══════════════════════════════════════════════════════════════

        # ═══════════════════════════════════════════════════════════════
        # ENHANCEMENT 5 & 6: ENTRY FILTERS (Ported from shadow trading)
        # ═══════════════════════════════════════════════════════════════
        if decision['action'] == 'BUY':
            if self._check_sentiment_filter():
                print(f"⏭️ {symbol}: Skipping BUY - Fed meeting day filter")
                return None
            if self._check_correlation_filter(symbol):
                print(f"⏭️ {symbol}: Skipping BUY - Correlation filter ({self.max_correlated_positions} max)")
                return None
            # Check max concurrent positions (AGGRESSIVE: 8 max)
            open_position_count = sum(
                1 for trades in self.positions.values()
                for t in trades if t.get('status') != 'CLOSED'
            )
            if open_position_count >= self.max_concurrent_positions:
                print(f"⏭️ {symbol}: Skipping BUY - Max concurrent positions ({self.max_concurrent_positions})")
                return None
        # ═══════════════════════════════════════════════════════════════

        price = market_data['price']
        trade_value = decision['quantity'] * price

        # Risk checks
        if trade_value > self.max_position_size:
            print(f"[WARNING]️ Trade size ${trade_value:.2f} exceeds max position ${self.max_position_size:.2f}")
            return None

        if self.trades_today >= self.max_daily_trades:
            print(f"[WARNING]️ Daily trade limit reached ({self.max_daily_trades})")
            return None
        
        # Create detailed trade record
        trade = {
            'trade_id': f"{self.session_id}_{self.trades_today + 1}",
            'symbol': symbol,
            'action': decision['action'],
            'quantity': decision['quantity'],
            'price': price,
            'value': trade_value,
            'timestamp': datetime.now().isoformat(),
            'reason': decision['reason'],
            'confidence': decision['confidence'],
            'target_price': decision['target_price'],
            'stop_loss': decision['stop_loss'],
            'market_data_snapshot': market_data,
            'ib_order_id': f"SIM_{self.trades_today + 1}",  # Simulated IB order ID
            'status': 'FILLED'
        }
        
        # Execute trade
        print(f"\n🚀 ACTIVE TRADE EXECUTED:")
        print(f"   Trade ID: {trade['trade_id']}")
        print(f"   {decision['action']} {decision['quantity']} shares of {symbol}")
        print(f"   Entry Price: ${price:.2f}")
        print(f"   Trade Value: ${trade_value:.2f}")
        print(f"   Target: ${decision['target_price']:.2f} (+{((decision['target_price']/price)-1)*100:.1f}%)")
        print(f"   Stop Loss: ${decision['stop_loss']:.2f} ({((decision['stop_loss']/price)-1)*100:.1f}%)")
        print(f"   Reason: {decision['reason']}")
        print(f"   Confidence: {decision['confidence']:.1%}")
        print(f"   IB Order ID: {trade['ib_order_id']}")
        
        # Update portfolio
        if decision['action'] == 'BUY':
            self.portfolio_value -= trade_value
            print(f"   💰 Cash Used: ${trade_value:.2f}")
        else:  # SELL
            self.portfolio_value += trade_value
            print(f"   💰 Cash Received: ${trade_value:.2f}")
        
        print(f"   📊 Portfolio Value: ${self.portfolio_value:.2f}")

        # Update tracking
        self.trades_today += 1

        # Store position
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)

        # ═══════════════════════════════════════════════════════════════
        # ENHANCEMENT TRACKING: Initialize tracking for new BUY positions
        # ═══════════════════════════════════════════════════════════════
        if decision['action'] == 'BUY':
            self.position_entry_times[symbol] = datetime.now()
            self.position_highs[symbol] = price
            if symbol not in self.scaled_positions:
                self.scaled_positions[symbol] = 0
            if symbol not in self.dca_counts:
                self.dca_counts[symbol] = 0
            self._save_position_tracking(symbol)

        # ═══════════════════════════════════════════════════════════════
        # AI ATTRIBUTION TRACKING - Record which AI systems contributed (Audit Fix HIGH-003)
        # ═══════════════════════════════════════════════════════════════
        if self.ai_attribution_tracker:
            try:
                # Determine which AI systems contributed to this decision
                ai_components = []
                vote_breakdown = {}

                # Check which AI brain was used
                if self.universal_reasoning:
                    ai_components.extend(['Universal_Reasoning', 'HRM', 'Quantum', 'Memory'])
                elif self.hybrid_ai:
                    ai_components.extend(['Hybrid_AI', 'GPT_OSS'])
                elif self.unified_ai:
                    ai_components.extend(['Unified_AI', 'DeepSeek_R1'])
                else:
                    ai_components.append('Mathematical_Fallback')

                # Add technical analysis if used
                if 'technical' in decision.get('reason', '').lower() or 'rsi' in decision.get('reason', '').lower():
                    ai_components.append('Technical_Analysis')

                # Add visual patterns if used
                if 'visual' in decision.get('reason', '').lower() or 'pattern' in decision.get('reason', '').lower():
                    ai_components.append('Visual_AI')

                # PHASE 4: Add Phase 3 AI systems to attribution tracking
                if self.market_oracle:
                    ai_components.append('Market_Oracle')
                if self.agent_coordinator:
                    ai_components.append('Hierarchical_Agents')
                if self.continuous_learning:
                    ai_components.append('Continuous_Learning')
                if self.ai_learning:
                    ai_components.append('AI_Learning')

                # Record the signal with attribution
                vote_breakdown[decision['action']] = decision['confidence']
                asyncio.create_task(
                    self.ai_attribution_tracker.record_signal(
                        symbol=symbol,
                        ai_components=ai_components,
                        vote_breakdown=vote_breakdown,
                        action=decision['action'],
                        confidence=decision['confidence'],
                        entry_price=price,
                        trade_id=trade['trade_id']
                    )
                )
                print(f"   🎯 AI Attribution recorded: {ai_components}")
            except Exception as e:
                logger.warning(f"AI Attribution recording failed: {e}")

        return trade

    def update_trade_pnl(self, trade_id: str, exit_price: float, pnl: float, symbol: str = None):
        """
        Update P/L for a trade and track circuit breaker metrics (Audit Fix CRIT-004)

        Args:
            trade_id: The trade ID to update
            exit_price: The actual exit price
            pnl: The profit/loss amount
            symbol: The trading symbol (for AI attribution)
        """
        # Update daily P/L
        self.daily_pnl += pnl

        # Track consecutive losses for circuit breaker
        if pnl < 0:
            self.consecutive_losses += 1
            print(f"   📉 Loss recorded: ${pnl:.4f} (Consecutive losses: {self.consecutive_losses}/{self.max_consecutive_losses})")
        else:
            self.consecutive_losses = 0  # Reset on winning trade
            print(f"   📈 Win recorded: ${pnl:.4f} (Loss streak reset)")

        # Check if circuit breaker should trigger
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.circuit_breaker_triggered = True
            self.circuit_breaker_reason = f"Max consecutive losses ({self.max_consecutive_losses})"
            print(f"🛑 CIRCUIT BREAKER TRIGGERED: {self.circuit_breaker_reason}")

        if self.daily_pnl <= -self.max_daily_loss:
            self.circuit_breaker_triggered = True
            self.circuit_breaker_reason = f"Max daily loss exceeded (${abs(self.daily_pnl):.2f})"
            print(f"🛑 CIRCUIT BREAKER TRIGGERED: {self.circuit_breaker_reason}")

        # ═══════════════════════════════════════════════════════════════
        # AI ATTRIBUTION OUTCOME - Record trade result for learning (Audit Fix HIGH-003)
        # ═══════════════════════════════════════════════════════════════
        if self.ai_attribution_tracker and symbol:
            try:
                # Calculate P/L percentage (estimate based on typical position size)
                pnl_pct = (pnl / self.max_position_size) * 100 if self.max_position_size > 0 else 0

                asyncio.create_task(
                    self.ai_attribution_tracker.record_outcome(
                        symbol=symbol,
                        pnl=pnl,
                        pnl_pct=pnl_pct,
                        trade_id=trade_id
                    )
                )
                print(f"   🎯 AI Attribution outcome recorded: P/L ${pnl:.4f} ({pnl_pct:.2f}%)")
            except Exception as e:
                logger.warning(f"AI Attribution outcome recording failed: {e}")

        # ═══════════════════════════════════════════════════════════════
        # PHASE 3: Continuous Learning Engine - Record trade outcome for learning
        # ═══════════════════════════════════════════════════════════════
        if self.continuous_learning and symbol:
            try:
                from core.continuous_learning_engine import TradingOutcome
                # Find the original trade entry for duration calculation
                entry_time = self.position_entry_times.get(symbol, datetime.now())
                duration = datetime.now() - entry_time

                outcome = TradingOutcome(
                    trade_id=trade_id,
                    timestamp=entry_time,
                    symbol=symbol,
                    action='SELL',  # outcomes are recorded on exit
                    entry_price=exit_price - (pnl / max(1, 1)),  # approximate
                    exit_price=exit_price,
                    quantity=1,  # not tracked here; approximation
                    profit_loss=pnl,
                    duration=duration,
                    market_conditions={},
                    model_confidence=0.7,
                    model_version="live_v2_aggressive",
                    features_used={},
                    risk_metrics={'exit_reason': 'pnl_update'}
                )
                asyncio.create_task(
                    self.continuous_learning.record_trading_outcome(outcome)
                )
                print(f"   🧠 Continuous Learning: Outcome recorded (duration: {duration})")
            except Exception as e:
                logger.warning(f"Continuous Learning feedback failed: {e}")

        print(f"   💰 Daily P/L: ${self.daily_pnl:.2f}")
        return pnl

    # ═══════════════════════════════════════════════════════════════
    # ENHANCEMENT 5 & 6: ENTRY FILTERS (Ported from shadow trading)
    # ═══════════════════════════════════════════════════════════════

    def _check_sentiment_filter(self) -> bool:
        """Check if today is a Fed meeting day - avoid new BUY trades"""
        if not self.sentiment_filter_enabled:
            return False
        today_str = datetime.now().strftime("%Y-%m-%d")
        if today_str in self.fed_days_2025_2026:
            logger.info(f"🗓️ SENTIMENT FILTER: Fed meeting day {today_str} - avoiding new trades")
            return True
        return False

    def _check_correlation_filter(self, symbol: str) -> bool:
        """Check if adding this symbol would exceed correlated position limits"""
        if not self.correlation_filter_enabled:
            return False
        correlated_symbols = self.correlated_assets.get(symbol, [])
        if not correlated_symbols:
            return False
        correlated_count = 0
        for corr_symbol in correlated_symbols:
            if corr_symbol in self.positions and self.positions[corr_symbol]:
                # Count only OPEN positions
                open_positions = [p for p in self.positions[corr_symbol] if p.get('status') != 'CLOSED']
                if open_positions:
                    correlated_count += 1
        # Also count this symbol's own open positions
        if symbol in self.positions:
            open_own = [p for p in self.positions[symbol] if p.get('status') != 'CLOSED']
            if open_own:
                correlated_count += 1
        if correlated_count >= self.max_correlated_positions:
            logger.info(f"🔗 CORRELATION FILTER: {symbol} blocked - {correlated_count} correlated positions")
            return True
        return False

    # ═══════════════════════════════════════════════════════════════
    # POSITION TRACKING PERSISTENCE (Database)
    # ═══════════════════════════════════════════════════════════════

    def _load_position_tracking(self):
        """Load position tracking from database on startup"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_position_tracking (
                    session_id TEXT,
                    symbol TEXT,
                    position_high REAL,
                    entry_time TEXT,
                    scaled_level INTEGER,
                    dca_count INTEGER,
                    updated_at TEXT,
                    PRIMARY KEY (session_id, symbol)
                )
            """)
            db.commit()
            cursor.execute("""
                SELECT symbol, position_high, entry_time, scaled_level, dca_count
                FROM live_position_tracking
                WHERE session_id = ?
            """, (self.session_id,))
            rows = cursor.fetchall()
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
            db.close()
            if rows:
                logger.info(f"💾 Loaded position tracking for {len(rows)} symbols")
        except Exception as e:
            logger.warning(f"⚠️ Could not load position tracking: {e}")

    def _save_position_tracking(self, symbol: str):
        """Save position tracking to database after updates"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO live_position_tracking
                (session_id, symbol, position_high, entry_time, scaled_level, dca_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.session_id,
                symbol,
                self.position_highs.get(symbol),
                self.position_entry_times.get(symbol, datetime.now()).isoformat() if symbol in self.position_entry_times else None,
                self.scaled_positions.get(symbol, 0),
                self.dca_counts.get(symbol, 0),
                datetime.now().isoformat()
            ))
            db.commit()
            db.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not save position tracking for {symbol}: {e}")

    def _delete_position_tracking(self, symbol: str):
        """Delete position tracking when position fully closed"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            cursor.execute("""
                DELETE FROM live_position_tracking
                WHERE session_id = ? AND symbol = ?
            """, (self.session_id, symbol))
            db.commit()
            db.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not delete position tracking for {symbol}: {e}")

    def _cleanup_position_tracking(self, symbol: str):
        """Clean up all tracking data when position fully closed"""
        if symbol in self.position_highs:
            del self.position_highs[symbol]
        if symbol in self.position_entry_times:
            del self.position_entry_times[symbol]
        if symbol in self.scaled_positions:
            del self.scaled_positions[symbol]
        if symbol in self.dca_counts:
            del self.dca_counts[symbol]
        self._delete_position_tracking(symbol)

    async def monitor_and_close_positions(self):
        """
        Monitor open positions with ALL 6 AGGRESSIVE ENHANCEMENTS.

        Ported from parallel_shadow_trading.py — these produced 75.6% win rate
        and 2.42 Sharpe ratio in 10-year backtesting.

        Exit conditions (in priority order):
        1. STOP LOSS (safety backstop)
        2. TRAILING STOP (lock in profits after +2%, sell if drops 1% from high)
        3. SCALE-OUT (sell 50% at +2%, remaining at +4%)
        4. TIME-BASED EXIT (3 days crypto, 7 days stocks if not profitable)
        5. TAKE PROFIT (target_price)
        6. DCA ON DIPS (buy more at -2%, max 2 adds)
        """
        import yfinance as yf

        if not self.positions:
            return

        # Count open positions
        open_count = sum(
            1 for trades in self.positions.values()
            for t in trades if t.get('status') != 'CLOSED'
        )
        if open_count == 0:
            return

        print(f"\n📊 Monitoring {open_count} open positions (6 AGGRESSIVE enhancements active)...")

        for symbol, trades in list(self.positions.items()):
            for trade in trades:
                if trade.get('status') == 'CLOSED':
                    continue

                # Get current market price
                try:
                    ticker = yf.Ticker(symbol)
                    current_price = ticker.fast_info.get('lastPrice') or ticker.fast_info.get('last_price')
                    if not current_price:
                        hist = ticker.history(period="1d", interval="1m")
                        current_price = float(hist['Close'].iloc[-1]) if not hist.empty else trade['price']
                except Exception as e:
                    logger.warning(f"Could not get current price for {symbol}: {e}")
                    current_price = trade['price']

                entry_price = trade['price']
                target_price = trade.get('target_price', entry_price * 1.05)
                stop_loss = trade.get('stop_loss', entry_price * 0.98)
                quantity = trade['quantity']
                action = trade['action']
                is_crypto = _is_crypto_symbol(symbol)

                # Calculate P/L
                if action == 'BUY':
                    pnl = (current_price - entry_price) * quantity
                    pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
                else:
                    pnl = (entry_price - current_price) * quantity
                    pnl_pct = (entry_price - current_price) / entry_price if entry_price > 0 else 0

                should_exit = False
                partial_exit = False
                partial_qty = 0
                exit_reason = ""

                # ═══════════════════════════════════════════════════════════
                # SAFETY BACKSTOP: Hard stop loss (always checked first)
                # ═══════════════════════════════════════════════════════════
                if action == 'BUY' and current_price <= stop_loss:
                    should_exit = True
                    exit_reason = f"STOP_LOSS @ ${current_price:.2f} (limit ${stop_loss:.2f})"
                elif action != 'BUY' and current_price >= stop_loss:
                    should_exit = True
                    exit_reason = f"STOP_LOSS @ ${current_price:.2f} (limit ${stop_loss:.2f})"

                # ═══════════════════════════════════════════════════════════
                # ENHANCEMENT 1: TRAILING STOP - Lock in profits
                # ═══════════════════════════════════════════════════════════
                if self.trailing_stop_enabled and not should_exit and action == 'BUY':
                    if symbol not in self.position_highs:
                        self.position_highs[symbol] = current_price
                    else:
                        self.position_highs[symbol] = max(self.position_highs[symbol], current_price)
                    high_price = self.position_highs[symbol]

                    if pnl_pct >= self.trailing_stop_trigger:
                        drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                        if drop_from_high >= self.trailing_stop_distance:
                            should_exit = True
                            high_pnl = (high_price - entry_price) / entry_price if entry_price > 0 else 0
                            exit_reason = f"TRAILING_STOP (peak +{high_pnl*100:.1f}%, now +{pnl_pct*100:.1f}%)"
                    self._save_position_tracking(symbol)

                # ═══════════════════════════════════════════════════════════
                # ENHANCEMENT 4: SCALE-OUT - Partial profit taking
                # ═══════════════════════════════════════════════════════════
                if self.scale_out_enabled and not should_exit and action == 'BUY':
                    scaled_level = self.scaled_positions.get(symbol, 0)

                    if pnl_pct >= self.scale_out_first_pct and scaled_level == 0:
                        partial_exit = True
                        partial_qty = max(1, int(quantity * 0.5))
                        self.scaled_positions[symbol] = 1
                        exit_reason = f"SCALE_OUT_1 (+{pnl_pct*100:.1f}%, selling {partial_qty} of {quantity})"
                        self._save_position_tracking(symbol)

                    elif pnl_pct >= self.scale_out_second_pct and scaled_level == 1:
                        should_exit = True
                        self.scaled_positions[symbol] = 2
                        exit_reason = f"SCALE_OUT_2 (+{pnl_pct*100:.1f}%, closing remaining)"

                # ═══════════════════════════════════════════════════════════
                # ENHANCEMENT 3: TIME-BASED EXIT (replaces 30-min hardcode)
                # ═══════════════════════════════════════════════════════════
                if self.time_exit_enabled and not should_exit and not partial_exit:
                    entry_time = self.position_entry_times.get(
                        symbol, datetime.fromisoformat(trade['timestamp'])
                    )
                    time_held = datetime.now() - entry_time
                    days_held = time_held.total_seconds() / 86400
                    max_days = self.max_hold_days_crypto if is_crypto else self.max_hold_days_stock

                    if days_held >= max_days and pnl_pct < self.scale_out_first_pct:
                        should_exit = True
                        exit_reason = f"TIME_EXIT ({days_held:.1f}d >= {max_days}d max, P/L: {pnl_pct*100:+.1f}%)"

                # ═══════════════════════════════════════════════════════════
                # TAKE PROFIT (target_price) — now checked after enhancements
                # ═══════════════════════════════════════════════════════════
                if not should_exit and not partial_exit:
                    if action == 'BUY' and current_price >= target_price:
                        should_exit = True
                        exit_reason = f"TAKE_PROFIT @ ${current_price:.2f} (target ${target_price:.2f})"
                    elif action != 'BUY' and current_price <= target_price:
                        should_exit = True
                        exit_reason = f"TAKE_PROFIT @ ${current_price:.2f} (target ${target_price:.2f})"

                # ═══════════════════════════════════════════════════════════
                # ENHANCEMENT 2: DCA ON DIPS - Buy more to average down
                # ═══════════════════════════════════════════════════════════
                if self.dca_enabled and pnl_pct <= self.dca_trigger_pct and not should_exit and not partial_exit and action == 'BUY':
                    dca_count = self.dca_counts.get(symbol, 0)
                    if dca_count < self.dca_max_adds:
                        dca_amount = self.portfolio_value * self.dca_position_pct
                        if dca_amount >= 5.0 and current_price > 0:  # Min $5 for DCA
                            dca_qty = max(1, int(dca_amount / current_price))
                            if dca_qty > 0:
                                old_qty = trade['quantity']
                                old_value = entry_price * old_qty
                                new_value = current_price * dca_qty
                                trade['quantity'] = old_qty + dca_qty
                                trade['price'] = (old_value + new_value) / trade['quantity']
                                self.dca_counts[symbol] = dca_count + 1
                                self.portfolio_value -= (current_price * dca_qty)
                                self._save_position_tracking(symbol)
                                print(f"   📥 DCA BUY #{dca_count+1}: {symbol} +{dca_qty} @ ${current_price:.2f} "
                                      f"(avg now ${trade['price']:.2f}, total qty: {trade['quantity']})")

                # ═══════════════════════════════════════════════════════════
                # EXECUTE EXIT (full or partial)
                # ═══════════════════════════════════════════════════════════
                if should_exit:
                    trade['exit_price'] = current_price
                    trade['exit_time'] = datetime.now().isoformat()
                    trade['pnl'] = pnl
                    trade['pnl_pct'] = pnl_pct * 100
                    trade['status'] = 'CLOSED'
                    trade['exit_reason'] = exit_reason

                    self.update_trade_pnl(trade['trade_id'], current_price, pnl, symbol)
                    self._cleanup_position_tracking(symbol)

                    emoji = "✅" if pnl > 0 else "❌"
                    print(f"\n{emoji} POSITION CLOSED: {symbol}")
                    print(f"   Entry: ${entry_price:.2f} → Exit: ${current_price:.2f}")
                    print(f"   P/L: ${pnl:.2f} ({pnl_pct*100:+.2f}%)")
                    print(f"   Reason: {exit_reason}")

                elif partial_exit and partial_qty > 0:
                    partial_pnl = (current_price - entry_price) * partial_qty
                    trade['quantity'] -= partial_qty
                    self.portfolio_value += (current_price * partial_qty)
                    self.update_trade_pnl(trade['trade_id'] + '_partial', current_price, partial_pnl, symbol)

                    print(f"\n📤 PARTIAL EXIT: {symbol}")
                    print(f"   Sold {partial_qty} @ ${current_price:.2f} (P/L: ${partial_pnl:.2f})")
                    print(f"   Remaining: {trade['quantity']} shares")
                    print(f"   Reason: {exit_reason}")

                else:
                    emoji = "📈" if pnl > 0 else "📉"
                    print(f"   {emoji} {symbol}: ${current_price:.2f} (P/L: ${pnl:.2f}, {pnl_pct*100:+.2f}%)")

    async def run_active_trading_strategies(self):
        """Run PROMETHEUS active trading strategies"""
        print("\n🧠 PROMETHEUS AUTONOMOUS TRADING - ALL ASSET CLASSES")
        print("=" * 50)
        
        # AUTONOMOUS MULTI-ASSET WATCHLIST - PROMETHEUS decides what to trade
        watchlist = [
            # Large cap stocks
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA',
            # Mid-large cap
            'AMD', 'META', 'NFLX', 'CRM', 'ADBE',
            # Volatile stocks
            'PLTR', 'RBLX', 'COIN',
            # CRYPTO - 24/7 opportunities (yfinance format)
            'BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD',
            'ADA-USD', 'DOGE-USD',  # MATIC-USD removed (delisted)
            # FOREX - 24/5 opportunities
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X'
        ]
        
        print(f"📊 Scanning {len(watchlist)} symbols across ALL asset classes:")
        print("   - Stocks (US equities)")
        print("   - Crypto (24/7 trading)")
        print("   - Forex (24/5 trading)")
        print("   PROMETHEUS will autonomously trade the most profitable opportunities\n")
        
        # Get enhanced market data
        market_data = await self.get_enhanced_market_data(watchlist)
        
        if not market_data:
            print("[ERROR] No market data available")
            return
        
        print(f"\n📊 Analyzing {len(market_data)} symbols with aggressive strategy...")
        
        # Analyze each symbol
        for symbol, data in market_data.items():
            if self.trades_today >= self.max_daily_trades:
                print(f"[WARNING]️ Daily trade limit reached ({self.max_daily_trades})")
                break
            
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Get aggressive AI decision
            decision = await self.prometheus_aggressive_analysis(symbol, data)
            
            print(f"🤖 AI Decision: {decision['action']} (Confidence: {decision['confidence']:.1%})")
            print(f"📝 Reason: {decision['reason']}")
            
            # Execute trade if decision is not HOLD
            if decision['action'] != 'HOLD':
                trade = await self.execute_paper_trade(symbol, decision, data)
                if trade:
                    print(f"[CHECK] Trade executed successfully")
                    
                    # Small delay between trades
                    await asyncio.sleep(1)
                else:
                    print(f"[ERROR] Trade not executed (risk limits)")
            else:
                print(f"⏸️ Holding position")
    
    async def generate_detailed_report(self):
        """Generate detailed session report"""
        session_duration = datetime.now() - self.session_start
        
        # Calculate detailed P&L
        total_invested = 0
        total_received = 0
        
        for symbol_positions in self.positions.values():
            for trade in symbol_positions:
                if trade['action'] == 'BUY':
                    total_invested += trade['value']
                else:
                    total_received += trade['value']
        
        pnl = self.portfolio_value - self.starting_capital
        pnl_percent = (pnl / self.starting_capital) * 100
        
        # Calculate trade statistics
        all_trades = []
        for positions in self.positions.values():
            all_trades.extend(positions)
        
        avg_confidence = sum(trade['confidence'] for trade in all_trades) / len(all_trades) if all_trades else 0
        
        report = {
            'session_info': {
                'session_id': self.session_id,
                'account_id': self.account_id,
                'session_start': self.session_start.isoformat(),
                'session_duration_minutes': round(session_duration.total_seconds() / 60, 2),
                'trading_mode': 'Active IB Paper Trading + Enhanced Yahoo Finance Data'
            },
            'capital_info': {
                'starting_capital_usd': self.starting_capital,
                'starting_capital_zar': 10000.0,
                'final_portfolio_value': self.portfolio_value,
                'total_invested': total_invested,
                'total_received': total_received,
                'total_pnl': pnl,
                'pnl_percent': pnl_percent
            },
            'trading_activity': {
                'trades_executed': self.trades_today,
                'symbols_analyzed': len(self.market_data_cache),
                'positions': self.positions,
                'avg_confidence': avg_confidence
            },
            'risk_parameters': {
                'max_position_size_usd': self.max_position_size,
                'max_daily_loss_usd': self.max_daily_loss,
                'max_daily_trades': self.max_daily_trades,
                'stop_loss_percent': self.stop_loss_percent
            },
            'market_data': self.market_data_cache,
            'performance_metrics': {
                'trades_per_hour': self.trades_today / max(session_duration.total_seconds() / 3600, 0.1),
                'avg_trade_size': (total_invested + total_received) / max(self.trades_today, 1),
                'capital_utilization': (total_invested / self.starting_capital) * 100,
                'success_rate': 'N/A (paper trading session)'
            }
        }
        
        # Save detailed report
        report_file = f"prometheus_active_report_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 DETAILED REPORT SAVED: {report_file}")
        return report
    
    async def run_session(self, duration_minutes=20):
        """Run complete active trading session with continuous monitoring"""
        print("🚀 PROMETHEUS ACTIVE TRADING SESSION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        ib_port = int(os.getenv('IB_PORT', '4002'))
        trading_mode = "IB LIVE Trading" if ib_port == 4002 else "IB Paper Trading"
        print(f"Account: {self.account_id} ({trading_mode})")
        print(f"Capital: ${self.starting_capital:.2f} USD (R 10,000 ZAR)")
        print(f"Max Position: ${self.max_position_size:.2f} ({self.position_size_pct*100:.0f}% of capital)")
        print(f"Max Daily Trades: {self.max_daily_trades} | Max Positions: {self.max_concurrent_positions}")
        print(f"Stop Loss: {self.stop_loss_percent}% | Take Profit: {self.take_profit_pct*100:.0f}%")
        print(f"Strategy: AGGRESSIVE (10yr backtest optimal: 75.6% WR, 2.42 Sharpe)")
        print(f"Enhancements: TRAILING_STOP, SCALE_OUT, TIME_EXIT, DCA, SENTIMENT, CORRELATION")
        print(f"Duration: {duration_minutes} minutes")
        print("=" * 60)
        
        # Initialize IB connection
        ib_connected = await self.initialize_ib_connection()
        if not ib_connected:
            print("[WARNING]️ IB connection failed, continuing with simulation only")
        
        # Run continuous trading loop for specified duration
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        scan_interval = 5  # Scan markets every 5 minutes
        cycle_count = 0
        
        print(f"\n⏰ Session running until {end_time.strftime('%H:%M:%S')}")
        print(f"🔄 Market scan interval: {scan_interval} minutes\n")
        
        while datetime.now() < end_time:
            cycle_count += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            remaining = (end_time - datetime.now()).total_seconds() / 60
            
            print(f"\n{'='*60}")
            print(f"🔄 CYCLE {cycle_count} | Elapsed: {elapsed:.1f}m | Remaining: {remaining:.1f}m")
            print(f"{'='*60}")
            
            # Run active trading strategies
            await self.run_active_trading_strategies()
            
            # Check if we should continue
            if datetime.now() >= end_time:
                break
            
            if self.trades_today >= self.max_daily_trades:
                print(f"\n⚠️  Daily trade limit reached ({self.max_daily_trades})")
                print(f"⏸️  Monitoring mode only for remaining {remaining:.1f} minutes")
                # Wait until session end
                wait_seconds = (end_time - datetime.now()).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                break
            
            # Wait for next scan interval (unless we're near end time)
            if datetime.now() < end_time:
                next_scan = min(scan_interval * 60, (end_time - datetime.now()).total_seconds())
                if next_scan > 0:
                    print(f"\n⏸️  Waiting {next_scan/60:.1f} minutes until next scan...")
                    await asyncio.sleep(next_scan)
        
        print(f"\n✅ Session duration complete: {cycle_count} market scan cycles")
        
        # Generate detailed report
        report = await self.generate_detailed_report()
        
        # Display comprehensive summary
        print("\n[CHECK] ACTIVE TRADING SESSION COMPLETE")
        print("=" * 50)
        print(f"📊 Trades Executed: {self.trades_today}")
        print(f"📈 Symbols Analyzed: {len(self.market_data_cache)}")
        print(f"💰 Final Portfolio: ${self.portfolio_value:.2f}")
        print(f"📊 Total P&L: ${report['capital_info']['total_pnl']:.2f} ({report['capital_info']['pnl_percent']:.2f}%)")
        print(f"💹 Capital Utilization: {report['performance_metrics']['capital_utilization']:.1f}%")
        print(f"🎯 Avg Confidence: {report['trading_activity']['avg_confidence']:.1%}")
        print(f"⏱️ Duration: {report['session_info']['session_duration_minutes']:.1f} minutes")
        print(f"📈 Trades/Hour: {report['performance_metrics']['trades_per_hour']:.1f}")
        
        # Show individual trades
        if self.trades_today > 0:
            print(f"\n📋 TRADE SUMMARY:")
            trade_num = 1
            for symbol, trades in self.positions.items():
                for trade in trades:
                    print(f"   {trade_num}. {trade['action']} {trade['quantity']} {symbol} @ ${trade['price']:.2f} - {trade['reason']}")
                    trade_num += 1
        
        # Disconnect from IB
        if hasattr(self, 'ib_client') and self.ib_client.isConnected():
            self.ib_client.disconnect()
            print("[CHECK] Disconnected from IB Gateway")
        
        return report

async def main():
    """Main function"""
    session = PrometheusActiveTradingSession()
    await session.run_session(duration_minutes=20)

if __name__ == "__main__":
    asyncio.run(main())
