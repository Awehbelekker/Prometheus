#!/usr/bin/env python3
"""
PROMETHEUS Dual Broker Live Trading System
Full AI Brain + IB (U21922116) + Alpaca Live Trading
WITH ADAPTIVE RISK MANAGEMENT - Dynamic confidence thresholds
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

class FinalDualBrokerTradingSystem:
    """PROMETHEUS Dual Broker Live Trading System with Full AI Brain"""
    
    def __init__(self):
        self.alpaca_broker: Optional[AlpacaBroker] = None
        self.ib_broker: Optional[InteractiveBrokersBroker] = None
        self.alpaca_trades_today = 0
        self.ib_trades_today = 0
        self.ib_account = os.getenv('IB_ACCOUNT', "U21922116")  # From .env
        
        # Capital allocation
        self.ib_capital = 251.58  # IB account balance
        self.alpaca_capital = 122.48  # Alpaca account balance
        self.total_capital = self.ib_capital + self.alpaca_capital  # $374.06
        self.max_position_size = self.total_capital * 0.02  # 2% per trade = $7.48
        
        # Session tracking
        self.session_id = f"live_dual_broker_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.positions = {}
        self.market_data_cache = {}
        
        # Initialize AI Intelligence Engines (THE BRAIN)
        self.ai_brain_active = False
        self.universal_reasoning = None
        self.hybrid_ai = None
        self.unified_ai = None
        self.orchestrator = None
        self.enhanced_data_cache = {}
        
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
        
        # Initialize Real-World Data Orchestrator
        try:
            from core.real_world_data_orchestrator import RealWorldDataOrchestrator
            self.orchestrator = RealWorldDataOrchestrator()
            logger.info("✅ Real-World Data Orchestrator initialized")
        except Exception as e:
            logger.warning(f"Orchestrator init error: {e}")
            self.orchestrator = None
        
    async def initialize(self):
        """Initialize the dual broker system"""
        logger.info("="*80)
        logger.info("🚀 PROMETHEUS LIVE DUAL BROKER TRADING SYSTEM")
        logger.info("="*80)
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"AI Brain: {'ACTIVE ✅' if self.ai_brain_active else 'INACTIVE ❌'}")
        logger.info("")
        logger.info("💰 CAPITAL ALLOCATION:")
        logger.info(f"   IB Account {self.ib_account}: ${self.ib_capital:.2f}")
        logger.info(f"   Alpaca Account: ${self.alpaca_capital:.2f}")
        logger.info(f"   Total Capital: ${self.total_capital:.2f}")
        logger.info(f"   Max Position Size (2%): ${self.max_position_size:.2f}")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*80)

        logger.info("[CONNECTING] Establishing broker connections...")
        await self._setup_brokers()
        if not self.alpaca_broker and not self.ib_broker:
            raise Exception("No brokers initialized. Cannot start trading.")
        
        # Can proceed with just Alpaca if IB fails
        if self.alpaca_broker and not self.ib_broker:
            logger.warning("[SYSTEM] Running with Alpaca only (IB unavailable)")

    async def _setup_brokers(self):
        """Setup both brokers with correct configuration - with TIMEOUTS to prevent hanging"""
        
        # Setup Alpaca broker FIRST (more reliable)
        if ALPACA_AVAILABLE:
            alpaca_config = {
                'paper_trading': os.getenv('ALPACA_PAPER_TRADING', 'false').lower() == 'true',
                'api_key': os.getenv('ALPACA_LIVE_KEY', os.getenv('ALPACA_API_KEY')),
                'secret_key': os.getenv('ALPACA_LIVE_SECRET', os.getenv('ALPACA_SECRET_KEY'))
            }
            if alpaca_config['api_key'] and alpaca_config['secret_key']:
                self.alpaca_broker = AlpacaBroker(alpaca_config)
                logger.info("[ALPACA] Testing connection...")
                try:
                    if await asyncio.wait_for(self.alpaca_broker.connect(), timeout=10):
                        account = await self.alpaca_broker.get_account()
                        logger.info(f"[ALPACA] Connected - Account: {account.account_id}")
                        logger.info(f"[ALPACA] Balance: ${account.equity:.2f}")
                        logger.info(f"[ALPACA] Buying Power: ${account.buying_power:.2f}")
                    else:
                        logger.error("[ALPACA] Failed to connect to Alpaca.")
                        self.alpaca_broker = None
                except asyncio.TimeoutError:
                    logger.error("[ALPACA] Connection timeout after 10s")
                    self.alpaca_broker = None
            else:
                logger.warning("[ALPACA] Alpaca API keys not configured. Skipping Alpaca connection.")

        # Setup Interactive Brokers with TIMEOUT to prevent hanging
        if IB_AVAILABLE:
            ib_config = {
                'host': os.getenv('IB_HOST', '127.0.0.1'),
                'port': int(os.getenv('IB_PORT', '4002')),  # Port 4002 for LIVE trading
                'client_id': int(os.getenv('IB_CLIENT_ID', '7')),  # Use client ID 7
                'paper_trading': False  # Force live trading
            }
            
            self.ib_broker = InteractiveBrokersBroker(ib_config)
            logger.info(f"[IB] Connecting to IB Gateway with CORRECT account: {self.ib_account}")
            
            try:
                # 15 second timeout for IB connection
                connected = await asyncio.wait_for(self.ib_broker.connect(), timeout=15)
                if connected:
                    logger.info("[IB] Connected successfully!")
                    
                    # Wait for connection to stabilize (with timeout)
                    await asyncio.sleep(2)
                    
                    # Request next valid order ID
                    self.ib_broker.client.reqIds(1)
                    await asyncio.sleep(1)
                    
                    if hasattr(self.ib_broker, 'next_order_id') and self.ib_broker.next_order_id:
                        logger.info(f"[IB] Next valid order ID: {self.ib_broker.next_order_id}")
                    else:
                        logger.warning("[IB] No order ID received")
                    
                    # Request account data for the CORRECT account
                    logger.info(f"[IB] Requesting account data for: {self.ib_account}")
                    self.ib_broker.client.reqAccountSummary(9001, self.ib_account, "$LEDGER")
                    await asyncio.sleep(1)
                    
                    # Request positions for the CORRECT account
                    self.ib_broker.client.reqPositions()
                    await asyncio.sleep(1)
                    
                    # Log any errors
                    if hasattr(self.ib_broker, 'wrapper') and hasattr(self.ib_broker.wrapper, 'errors'):
                        for error in self.ib_broker.wrapper.errors:
                            logger.error(f"[IB ERROR] {error}")
                        self.ib_broker.wrapper.errors.clear()
                    
                    logger.info(f"[IB] Using CORRECT account: {self.ib_account}")
                else:
                    logger.error("[IB] Failed to connect to Interactive Brokers.")
                    self.ib_broker = None
            except asyncio.TimeoutError:
                logger.error("[IB] Connection timeout after 15s - continuing without IB")
                self.ib_broker = None
            except Exception as e:
                logger.error(f"[IB] Connection error: {e} - continuing without IB")
                self.ib_broker = None
        else:
            logger.warning("[IB] Interactive Brokers API not available. Skipping IB connection.")

        logger.info(f"[CONNECTIONS] Alpaca: {'CONNECTED' if self.alpaca_broker else 'NOT CONNECTED'}")
        logger.info(f"[CONNECTIONS] IB: {'CONNECTED' if self.ib_broker else 'NOT CONNECTED'}")
        logger.info(f"[CONNECTIONS] IB Account: {self.ib_account}")
        
        # Initialize adaptive risk manager
        if ADAPTIVE_RISK_AVAILABLE:
            self.risk_manager = get_risk_manager()
            status = self.risk_manager.get_status()
            logger.info(f"[RISK] Adaptive Risk Manager: ACTIVE")
            logger.info(f"[RISK] Historical trades: {status['total_trades_all_time']}")
            logger.info(f"[RISK] Overall win rate: {status['overall_win_rate']:.0%}")

    async def run_trading_loop(self):
        """Run the trading loop with ADAPTIVE risk management"""
        cycle = 0
        while True:
            cycle += 1
            logger.info(f"[TRADING CYCLE {cycle}] {datetime.now().strftime('%H:%M:%S')}")
            logger.info("-" * 60)
            
            # Check if we should pause (drawdown protection)
            if ADAPTIVE_RISK_AVAILABLE:
                should_pause, reason = should_pause_trading()
                if should_pause:
                    logger.warning(f"[RISK] TRADING PAUSED: {reason}")
                    logger.info("[RISK] Waiting 30 minutes before resuming...")
                    await asyncio.sleep(1800)
                    continue

            signals = await self._generate_trading_signals()
            if not signals:
                logger.info("[AI] No trading signals generated. Waiting for next cycle.")
            else:
                logger.info(f"[AI] Generated {len(signals)} dual-broker signals")
                await self._execute_dual_broker_trades(signals)

            await self._dual_broker_status_check()
            logger.info(f"[WAIT] Waiting 5 minutes for next cycle...")
            await asyncio.sleep(300)  # Wait for 5 minutes

    async def _generate_trading_signals(self) -> List[Dict[str, Any]]:
        """Generate AI-powered trading signals across all asset classes"""
        logger.info("[AI BRAIN] Analyzing markets with Universal Reasoning Engine...")
        
        # Multi-asset watchlist
        watchlist = {
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'META'],
            'crypto': ['ETHUSD', 'BTCUSD', 'SOLUSD'],
        }
        
        signals = []
        
        # Analyze stocks for IB
        for symbol in watchlist['stocks']:
            try:
                market_data = await self._get_market_data(symbol)
                if market_data:
                    decision = await self._ai_reasoning_decision(symbol, market_data, 'stock')
                    if decision and decision['action'] != 'HOLD':
                        signals.append(decision)
            except Exception as e:
                logger.warning(f"Error analyzing {symbol}: {e}")
        
        # Analyze crypto for Alpaca
        for symbol in watchlist['crypto']:
            try:
                market_data = await self._get_market_data(symbol)
                if market_data:
                    decision = await self._ai_reasoning_decision(symbol, market_data, 'crypto')
                    if decision and decision['action'] != 'HOLD':
                        signals.append(decision)
            except Exception as e:
                logger.warning(f"Error analyzing {symbol}: {e}")
        
        logger.info(f"[AI BRAIN] Generated {len(signals)} high-confidence signals")
        return signals
    
    async def _get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get enhanced market data with technical analysis"""
        try:
            # Convert crypto symbols for yfinance
            yf_symbol = symbol if not symbol.endswith('USD') else f"{symbol[:3]}-USD"
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='5d', interval='5m')
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
            
            volume_current = float(hist['Volume'].iloc[-1])
            volume_avg = float(hist['Volume'].mean())
            volume_ratio = volume_current / volume_avg if volume_avg > 0 else 1.0
            
            # Calculate RSI-like indicator
            closes = hist['Close'].values
            if len(closes) > 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14
                rs = avg_gain / avg_loss if avg_loss > 0 else 100
                rsi_like = rs / (1 + rs)
            else:
                rsi_like = 0.5
            
            return {
                'symbol': symbol,
                'price': current_price,
                'momentum_5min': momentum,
                'volume_ratio': volume_ratio,
                'rsi_like': rsi_like,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.warning(f"Market data error for {symbol}: {e}")
            return None
    
    async def _ai_reasoning_decision(self, symbol: str, market_data: dict, asset_type: str) -> Optional[Dict[str, Any]]:
        """Use AI brain for intelligent trading decisions"""
        try:
            price = market_data.get('price', 0)
            if price <= 0:
                return None
            
            momentum = market_data.get('momentum_5min', 0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            rsi_like = market_data.get('rsi_like', 0.5)
            
            # Try Universal Reasoning first
            if self.universal_reasoning:
                try:
                    context_data = {
                        'symbol': symbol,
                        'market_data': market_data,
                        'capital_available': self.max_position_size,
                        'asset_type': asset_type
                    }
                    result = self.universal_reasoning.make_ultimate_decision(context_data)
                    
                    if result and result.get('action') and result.get('action') != 'HOLD':
                        # Calculate quantity based on asset type
                        if asset_type == 'crypto':
                            quantity = round(self.max_position_size / price, 4)  # 4 decimals for crypto
                        else:
                            quantity = max(1, int(self.max_position_size / price))  # Whole shares for stocks
                        
                        return {
                            'symbol': symbol,
                            'action': result.get('action', 'HOLD'),
                            'quantity': quantity,
                            'confidence': result.get('confidence', 0.7),
                            'reason': f"🧠 {result.get('reasoning', 'AI analysis')}",
                            'type': asset_type,
                            'ai_decision': True
                        }
                except Exception as e:
                    logger.warning(f"Universal Reasoning failed for {symbol}: {e}")
            
            # Fallback to mathematical analysis
            buy_score = 0
            if momentum > 0.01: buy_score += 2
            if volume_ratio > 1.5: buy_score += 1
            if rsi_like < 0.3: buy_score += 1  # Oversold
            
            if buy_score >= 3:
                if asset_type == 'crypto':
                    quantity = round(self.max_position_size / price, 4)
                else:
                    quantity = max(1, int(self.max_position_size / price))
                
                return {
                    'symbol': symbol,
                    'action': 'BUY',
                    'quantity': quantity,
                    'confidence': 0.6,
                    'reason': 'Mathematical fallback analysis',
                    'type': asset_type,
                    'ai_decision': False
                }
            
            return None  # HOLD
            
        except Exception as e:
            logger.error(f"AI decision error for {symbol}: {e}")
            return None

    async def _execute_dual_broker_trades(self, signals: List[Dict[str, Any]]):
        """Execute trades on appropriate brokers"""
        logger.info(f"[DUAL BROKER] Executing {len(signals)} trades...")
        alpaca_trades = 0
        ib_trades = 0

        alpaca_tasks = []
        ib_tasks = []

        for signal in signals:
            if signal['type'] == 'crypto' and self.alpaca_broker:
                alpaca_tasks.append(self._execute_alpaca_trade(signal))
                alpaca_trades += 1
            elif signal['type'] == 'stock' and self.ib_broker:
                ib_tasks.append(self._execute_ib_trade_final(signal))
                ib_trades += 1
            else:
                logger.warning(f"[WARNING] No suitable broker for signal: {signal['symbol']} ({signal['type']})")

        logger.info(f"[DUAL BROKER] Alpaca trades: {alpaca_trades}")
        logger.info(f"[DUAL BROKER] IB trades: {ib_trades}")

        if alpaca_tasks:
            logger.info("[ALPACA] Executing crypto trades...")
            await asyncio.gather(*alpaca_tasks)
        if ib_tasks:
            logger.info("[IB] Executing stock trades...")
            await asyncio.gather(*ib_tasks)

    async def _execute_alpaca_trade(self, signal: Dict[str, Any]):
        """Execute a trade on Alpaca"""
        try:
            logger.info(f"[ALPACA] Executing {signal['action']} order for {signal['symbol']}")
            order = await self.alpaca_broker.place_order(
                symbol=signal['symbol'],
                qty=signal['quantity'],
                side=signal['action'].lower(),
                order_type='market',
                time_in_force='gtc'
            )
            if order and order.status in ['new', 'filled', 'partially_filled']:
                logger.info(f"[ALPACA SUCCESS] Order placed: {order.id}")
                logger.info(f"   Symbol: {order.symbol}")
                logger.info(f"   Side: {order.side}")
                logger.info(f"   Qty: {order.qty}")
                logger.info(f"   Status: {order.status}")
                self.alpaca_trades_today += 1
            else:
                logger.error(f"[ALPACA ERROR] Order failed: {order.status if order else 'Unknown'}")
                if order and order.body:
                    logger.error(f"   Response: {order.body}")
        except Exception as e:
            logger.error(f"[ALPACA ERROR] Error placing Alpaca order for {signal['symbol']}: {e}")

    def _create_stock_contract(self, symbol: str) -> Contract:
        """Create stock contract for IB"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract

    def _create_ib_order(self, action: str, quantity: int) -> IBOrder:
        """Create IB order with FIXED configuration"""
        order = IBOrder()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        order.account = self.ib_account  # Use CORRECT account
        return order

    async def _execute_ib_trade_final(self, signal: Dict[str, Any]):
        """Execute a trade on Interactive Brokers with FINAL FIXED configuration"""
        if not self.ib_broker or not self.ib_broker.connected:
            logger.error(f"[IB ERROR] IB not connected for {signal['symbol']}")
            return

        try:
            logger.info(f"[IB] Executing {signal['action']} order for {signal['symbol']} on account {self.ib_account}")
            
            # Create contract using our method
            contract = self._create_stock_contract(signal['symbol'])
            
            # Create order using our method
            order = self._create_ib_order(signal['action'].upper(), int(signal['quantity']))
            
            # Ensure next_order_id is available
            if not hasattr(self.ib_broker, 'next_order_id') or self.ib_broker.next_order_id is None:
                self.ib_broker.client.reqIds(1)
                await asyncio.sleep(1)
                if not hasattr(self.ib_broker, 'next_order_id') or self.ib_broker.next_order_id is None:
                    logger.error("[IB ERROR] Could not get next valid order ID from IB.")
                    return

            order_id = self.ib_broker.next_order_id
            self.ib_broker.client.placeOrder(order_id, contract, order)
            self.ib_broker.next_order_id += 1  # Increment for next order

            # Wait for order status update
            await asyncio.sleep(2)
            
            logger.info(f"[IB SUCCESS] Order placed: {order_id}")
            logger.info(f"   Symbol: {signal['symbol']}")
            logger.info(f"   Action: {signal['action']}")
            logger.info(f"   Quantity: {signal['quantity']}")
            logger.info(f"   Account: {self.ib_account}")
            logger.info(f"   Order Type: {order.orderType}")
            
            self.ib_trades_today += 1
            
        except Exception as e:
            logger.error(f"[IB ERROR] Error placing IB order for {signal['symbol']}: {e}")

    async def _dual_broker_status_check(self):
        """Print status of both brokers"""
        logger.info("="*80)
        logger.info("FINAL DUAL BROKER STATUS CHECK")
        logger.info("="*80)

        if self.alpaca_broker:
            account = await self.alpaca_broker.get_account()
            logger.info(f"[ALPACA] Status: {'CONNECTED' if self.alpaca_broker.connected else 'DISCONNECTED'}")
            logger.info(f"   Account: {account.account_id}")
            logger.info(f"   Balance: ${account.equity:.2f}")
            logger.info(f"   Buying Power: ${account.buying_power:.2f}")
            logger.info(f"   Trades Today: {self.alpaca_trades_today}")
        else:
            logger.info("[ALPACA] Status: NOT CONNECTED")

        if self.ib_broker:
            logger.info(f"[IB] Status: {'CONNECTED' if self.ib_broker.connected else 'DISCONNECTED'}")
            logger.info(f"   Host: {self.ib_broker.host}:{self.ib_broker.port}")
            logger.info(f"   Client ID: {self.ib_broker.client_id}")
            logger.info(f"   Account: {self.ib_account}")
            # Fetch IB account info properly using get_account()
            try:
                ib_account = await self.ib_broker.get_account()
                logger.info(f"   Balance: ${ib_account.portfolio_value:,.2f}")
                logger.info(f"   Buying Power: ${ib_account.buying_power:,.2f}")
                logger.info(f"   Cash: ${ib_account.cash:,.2f}")
            except Exception as ib_err:
                logger.warning(f"   Balance: Unable to fetch ({ib_err})")
            logger.info(f"   Trades Today: {self.ib_trades_today}")
            
            # Display IB positions
            if hasattr(self.ib_broker, 'positions_data') and self.ib_broker.positions_data:
                logger.info(f"   Positions: {len(self.ib_broker.positions_data)}")
            else:
                logger.info("   Positions: 0")
        else:
            logger.info("[IB] Status: NOT CONNECTED")

        logger.info("="*80)
        logger.info(f"[CYCLE RESULTS]")
        logger.info(f"   Alpaca Trades: {self.alpaca_trades_today}")
        logger.info(f"   IB Trades: {self.ib_trades_today}")
        logger.info(f"   Total Trades: {self.alpaca_trades_today + self.ib_trades_today}")

async def main():
    """Main function"""
    system = FinalDualBrokerTradingSystem()
    try:
        await system.initialize()
        await system.run_trading_loop()
    except KeyboardInterrupt:
        logger.info("Trading system stopped by user")
    except Exception as e:
        logger.critical(f"PROMETHEUS Final Dual Broker System encountered a critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
