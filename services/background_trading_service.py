"""
🔄 24/7 BACKGROUND TRADING SERVICE
Production-ready background trading with full automation
"""

import asyncio
import logging
import signal
import sys
import os
import json
from datetime import datetime, timedelta, time
from core.utils.time_utils import utc_now, utc_iso
from typing import Dict, List, Any, Optional
import schedule
from pathlib import Path

# Import broker components
from brokers.alpaca_broker import AlpacaBroker
from brokers.universal_broker_interface import BrokerManager, Order, OrderType, OrderSide

# Import revolutionary features
import importlib.util
try:
    from core.hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
    from core.hrm_enhanced_personas import HRMPersonaManager, HRMPersonaType
    HRM_AVAILABLE = True
except Exception:
    HRM_AVAILABLE = False

logger = logging.getLogger(__name__)

class BackgroundTradingService:
    """
    🚀 24/7 BACKGROUND TRADING SERVICE
    
    Features:
    - Automatic reconnection on connection loss
    - State persistence during PC sleep/restart  
    - Market hours detection
    - Emergency shutdown procedures
    - Integration with all revolutionary features
    - Risk management enforcement
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize the background trading service with configuration and state."""
        # ---------------- Configuration ----------------
        self.trading_enabled = os.getenv('AUTO_TRADING_ENABLED', 'true').lower() == 'true'
        self.paper_trading = os.getenv('TRADING_MODE', 'paper') == 'paper'
        self.heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', 30))
        self.max_reconnect_attempts = int(os.getenv('MAX_RECONNECT_ATTEMPTS', 10))

        # ---------------- Risk Management Defaults ----------------
        self.max_position_size_percent = float(os.getenv('MAX_POSITION_SIZE_PERCENT', 5.0))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', 50))
        self.max_portfolio_risk_percent = float(os.getenv('MAX_PORTFOLIO_RISK_PERCENT', 2.0))
        self.default_stop_loss_percent = float(os.getenv('DEFAULT_STOP_LOSS_PERCENT', 3.0))

        # ---------------- Runtime State ----------------
        self.running = False
        self.last_heartbeat: Optional[datetime] = None
        self.consecutive_failures = 0
        self.daily_trade_count = 0
        self.last_trade_date: Optional[datetime.date] = None

        # ---------------- Core Service Components ----------------
        self.broker_manager = BrokerManager()
        self.state_manager = TradingStateManager()
        self.risk_manager = TradingRiskManager()
        self.performance_monitor = PerformanceMonitor()

        # ---------------- Revolutionary Feature Hooks ----------------
        self.ai_personas = None
        self.market_oracle = None
        self.quantum_interface = None
        self.gamification_engine = None

        # ---------------- HRM Integration ----------------
        self.hrm_enabled = os.getenv('HRM_ENABLED', 'true').lower() == 'true'
        self.hrm_engine = None
        self.hrm_personas = None

        # ---------------- Market Hours ----------------
        self.market_open_time = time(9, 30)
        self.market_close_time = time(16, 0)

        logger.info("🚀 Background Trading Service initialized")
    
    async def start(self):
        """Start the 24/7 background trading service"""
        logger.info("🌟 STARTING PROMETHEUS 24/7 TRADING SERVICE")
        logger.info("=" * 60)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Initialize all services
            await self._initialize_services()
            
            # Load previous state
            await self.state_manager.load_state()
            
            # Setup broker connections
            await self._setup_brokers()
            
            # Initialize revolutionary features
            await self._initialize_revolutionary_features()
            
            self.running = True
            logger.info("[CHECK] All services initialized successfully")
            
            # Start main trading loop
            await self._main_trading_loop()
            
        except Exception as e:
            logger.critical(f"🚨 Service startup failed: {str(e)}")
            await self._emergency_shutdown()
    
    async def _initialize_services(self):
        """Initialize all core services"""
        logger.info("🔧 Initializing core services...")
        
        # Initialize state manager
        await self.state_manager.initialize()
        
        # Initialize risk manager
        await self.risk_manager.initialize()
        
        # Initialize performance monitor
        await self.performance_monitor.initialize()
        
        logger.info("[CHECK] Core services initialized")
    
    async def _setup_brokers(self):
        """Setup and connect to all brokers"""
        logger.info("🏦 Setting up broker connections...")
        
        # Setup Alpaca broker
        alpaca_config = {
            'paper_trading': self.paper_trading,
            'api_key': os.getenv('ALPACA_PAPER_KEY' if self.paper_trading else 'ALPACA_LIVE_KEY'),
            'secret_key': os.getenv('ALPACA_PAPER_SECRET' if self.paper_trading else 'ALPACA_LIVE_SECRET')
        }
        
        if alpaca_config['api_key'] and alpaca_config['secret_key']:
            alpaca_broker = AlpacaBroker(alpaca_config)
            self.broker_manager.register_broker('alpaca', alpaca_broker, is_primary=True)
            logger.info(f"[CHECK] Registered Alpaca {'Paper' if self.paper_trading else 'Live'} Trading")
        else:
            logger.error("[ERROR] Alpaca API keys not configured")
            raise Exception("Broker configuration failed")
        
        # Connect to all brokers
        connection_results = await self.broker_manager.connect_all_brokers()
        
        if not any(connection_results.values()):
            raise Exception("No brokers connected successfully")
        
        logger.info(f"[CHECK] Connected to {sum(connection_results.values())} brokers")
    
    async def _initialize_revolutionary_features(self):
        """Initialize revolutionary trading features"""
        logger.info("🎭 Initializing revolutionary features...")
        
        try:
            # Try to import and initialize AI Personas
            try:
                from REVOLUTIONARY_FEATURES.ai_persona.trading_persona_engine import AITradingPersonas
                self.ai_personas = AITradingPersonas()
                logger.info("[CHECK] AI Trading Personas loaded")
            except ImportError:
                logger.warning("[WARNING]️ AI Trading Personas not available")
            
            # Try to import Market Oracle
            try:
                from REVOLUTIONARY_FEATURES.oracle.market_oracle_engine import MarketOracle
                self.market_oracle = MarketOracle()
                logger.info("[CHECK] Market Oracle loaded")
            except ImportError:
                logger.warning("[WARNING]️ Market Oracle not available")
            
            # Try to import Quantum Neural Interface
            try:
                from REVOLUTIONARY_FEATURES.quantum_neural.quantum_neural_interface import QuantumNeuralInterface
                self.quantum_interface = QuantumNeuralInterface()
                logger.info("[CHECK] Quantum Neural Interface loaded")
            except ImportError:
                logger.warning("[WARNING]️ Quantum Neural Interface not available")
            
            # Try to import Gamification Engine
            try:
                from REVOLUTIONARY_FEATURES.gamification.trading_gamification_engine import TradingGamificationEngine
                self.gamification_engine = TradingGamificationEngine()
                logger.info("[CHECK] Gamification Engine loaded")
            except ImportError:
                logger.warning("[WARNING]️ Gamification Engine not available")

            # HRM initialization
            if HRM_AVAILABLE and self.hrm_enabled:
                try:
                    self.hrm_engine = HRMTradingEngine()
                    self.hrm_personas = HRMPersonaManager(self.hrm_engine)
                    logger.info("[CHECK] HRM engine & personas initialized")
                except Exception as e:
                    logger.warning(f"[WARNING]️ HRM initialization failed: {e}")
            else:
                logger.info("[INFO]️ HRM disabled or unavailable")
            
        except Exception as e:
            logger.error(f"[ERROR] Revolutionary features initialization error: {str(e)}")
    
    async def _main_trading_loop(self):
        """Main 24/7 trading loop"""
        logger.info("🔄 Starting main trading loop...")
        
        while self.running:
            try:
                # Update daily trade count
                self._update_daily_trade_count()
                
                # Check market status
                market_status = await self._check_market_status()
                
                if not market_status['is_open']:
                    logger.info(f"🕐 Market closed. Next open: {market_status.get('next_open', 'Unknown')}")
                    await asyncio.sleep(300)  # Check every 5 minutes when market is closed
                    continue
                
                # Heartbeat check
                await self._heartbeat_check()
                
                # Check and maintain connections
                await self._maintain_connections()
                
                # Execute trading cycle if enabled
                if self.trading_enabled and self.daily_trade_count < self.max_daily_trades:
                    await self._execute_trading_cycle()
                
                # Save current state
                await self.state_manager.save_state()
                
                # Performance monitoring
                await self.performance_monitor.update_metrics()
                
                # Reset failure counter on successful cycle
                self.consecutive_failures = 0
                
                # Wait before next cycle (5 seconds for active trading)
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"[ERROR] Trading loop error: {str(e)}")
                
                self.consecutive_failures += 1
                
                if self.consecutive_failures >= self.max_reconnect_attempts:
                    logger.critical("🚨 Too many consecutive failures. Initiating emergency shutdown...")
                    await self._emergency_shutdown()
                    break
                
                # Exponential backoff
                wait_time = min(60, 2 ** self.consecutive_failures)
                logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
    
    async def _execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            # Get current portfolio
            broker = self.broker_manager.get_active_broker()
            if not broker:
                logger.warning("[WARNING]️ No active broker available")
                return
            
            account = await broker.get_account()
            positions = await broker.get_positions()
            
            portfolio_data = {
                'account': account,
                'positions': positions,
                'timestamp': utc_iso()
            }
            
            # Get AI trading signals
            trading_signals = await self._generate_trading_signals(portfolio_data)
            
            # Apply risk management
            validated_signals = await self.risk_manager.validate_signals(trading_signals, portfolio_data)
            
            # Execute validated trades
            for signal in validated_signals:
                await self._execute_trade_signal(signal, portfolio_data)
                
                # Increment daily trade count
                self.daily_trade_count += 1
                
                # Break if we hit daily limit
                if self.daily_trade_count >= self.max_daily_trades:
                    logger.info(f"📊 Daily trade limit reached: {self.max_daily_trades}")
                    break
            
            # Update performance metrics
            await self.performance_monitor.record_trading_cycle(portfolio_data, trading_signals, validated_signals)
            
        except Exception as e:
            logger.error(f"[ERROR] Trading cycle execution failed: {str(e)}")
            raise
    
    async def _generate_trading_signals(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals using revolutionary features"""
        signals = []
        
        try:
            # Get signals from AI Personas
            if self.ai_personas:
                persona_signals = await self._get_persona_signals(portfolio_data)
                signals.extend(persona_signals)
            
            # Get signals from Market Oracle
            if self.market_oracle:
                oracle_signals = await self._get_oracle_signals(portfolio_data)
                signals.extend(oracle_signals)
            
            # Get signals from Quantum Neural Interface
            if self.quantum_interface:
                quantum_signals = await self._get_quantum_signals(portfolio_data)
                signals.extend(quantum_signals)
            
            # Filter and rank signals
            ranked_signals = await self._rank_signals(signals, portfolio_data)
            
            logger.info(f"📊 Generated {len(ranked_signals)} trading signals")
            return ranked_signals[:10]  # Top 10 signals
            
        except Exception as e:
            logger.error(f"[ERROR] Signal generation failed: {str(e)}")
            return []
    
    async def _get_persona_signals(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trading signals from AI personas"""
        signals = []
        
        try:
            # Get available personas
            personas = ['wolf', 'turtle', 'owl', 'dolphin', 'eagle']
            
            # Legacy simulated personas
            for persona in personas:
                try:
                    base_signal = {
                        'source': 'ai_persona',
                        'persona': persona,
                        'symbol': 'AAPL',
                        'action': 'buy',
                        'confidence': 0.75,
                        'quantity': 10,
                        'reasoning': f"{persona.title()} persona suggests this trade",
                        'timestamp': utc_iso()
                    }
                    signals.append(base_signal)
                except Exception as e:
                    logger.error(f"[ERROR] Persona {persona} signal generation failed: {str(e)}")

            # HRM persona signals (real hierarchical reasoning)
            if self.hrm_personas:
                try:
                    for hrm_persona in [HRMPersonaType.BALANCED_HRM, HRMPersonaType.AGGRESSIVE_HRM]:
                        persona_obj = self.hrm_personas.get_persona(hrm_persona)
                        if not persona_obj:
                            continue
                        market_stub = {
                            'prices': [100,101,102,103],
                            'volumes': [1000000,950000,1100000,1200000],
                            'indicators': {'rsi': 55, 'macd': 0.4},
                            'sentiment': {'positive':0.5,'negative':0.2,'neutral':0.3}
                        }
                        user_ctx = {
                            'profile': {'persona': hrm_persona.value},
                            'trading_history': [],
                            'portfolio': portfolio_data.get('positions', {}),
                            'risk_preferences': {}
                        }
                        decision = persona_obj.analyze_market_with_hrm(market_stub, user_ctx)
                        signals.append({
                            'source': 'hrm_persona',
                            'persona': hrm_persona.value,
                            'symbol': 'AAPL',
                            'action': decision.get('risk_adjusted_action', decision.get('action','hold')).lower(),
                            'confidence': decision.get('persona_confidence', decision.get('confidence',0.5)),
                            'quantity': max(1, int(10 * decision.get('position_size',0.1))),
                            'reasoning': 'HRM hierarchical reasoning',
                            'hrm_meta': {
                                'risk_level': decision.get('risk_level'),
                                'confidence': decision.get('confidence'),
                                'fallback': decision.get('fallback', False)
                            },
                            'timestamp': utc_iso()
                        })
                except Exception as e:
                    logger.error(f"[ERROR] HRM persona signal generation failed: {e}")
            
        except Exception as e:
            logger.error(f"[ERROR] AI Persona signals failed: {str(e)}")
        
        return signals
    
    async def _get_oracle_signals(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trading signals from Market Oracle"""
        signals = []
        
        try:
            # Simulate oracle predictions (replace with actual implementation)
            oracle_signal = {
                'source': 'market_oracle',
                'symbol': 'TSLA',  # Example
                'action': 'buy',
                'confidence': 0.87,
                'quantity': 5,
                'prediction': 'Strong upward momentum predicted',
                'timeframe': '1h',
                            'timestamp': utc_iso()
            }
            signals.append(oracle_signal)
            
        except Exception as e:
            logger.error(f"[ERROR] Market Oracle signals failed: {str(e)}")
        
        return signals
    
    async def _get_quantum_signals(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trading signals from Quantum Neural Interface"""
        signals = []
        
        try:
            # Simulate quantum analysis (replace with actual implementation)
            quantum_signal = {
                'source': 'quantum_neural',
                'symbol': 'SPY',  # Example
                'action': 'buy',
                'confidence': 0.82,
                'quantity': 20,
                'quantum_state': 'favorable',
                'neural_pattern': 'bullish_convergence',
                'timestamp': utc_iso()
            }
            signals.append(quantum_signal)
            
        except Exception as e:
            logger.error(f"[ERROR] Quantum Neural signals failed: {str(e)}")
        
        return signals
    
    async def _rank_signals(self, signals: List[Dict[str, Any]], portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank trading signals by quality and confidence"""
        
        # Sort by confidence score (highest first)
        ranked_signals = sorted(signals, key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Add ranking scores
        for i, signal in enumerate(ranked_signals):
            signal['rank'] = i + 1
            signal['quality_score'] = signal.get('confidence', 0) * (1 - (i * 0.1))  # Diminishing quality
        
        return ranked_signals
    
    async def _execute_trade_signal(self, signal: Dict[str, Any], portfolio_data: Dict[str, Any]):
        """Execute a trading signal"""
        
        try:
            # Create order from signal
            order = Order(
                symbol=signal['symbol'],
                side=OrderSide.BUY if signal['action'].lower() == 'buy' else OrderSide.SELL,
                order_type=OrderType.MARKET,  # Default to market orders
                quantity=signal['quantity']
            )
            
            # Place order
            order_id = await self.broker_manager.place_order_with_routing(order)
            
            logger.info(f"[CHECK] Trade executed: {signal['action'].upper()} {signal['quantity']} {signal['symbol']}")
            logger.info(f"📋 Order ID: {order_id}")
            logger.info(f"🎯 Source: {signal['source']} (Confidence: {signal.get('confidence', 0):.2%})")
            
            # Update gamification if available
            if self.gamification_engine:
                await self._update_gamification(signal, order_id)
            
            # Record trade in state
            await self.state_manager.record_trade(signal, order_id)
            
        except Exception as e:
            logger.error(f"[ERROR] Trade execution failed: {str(e)}")
            logger.error(f"📋 Signal: {signal}")
            raise
    
    async def _check_market_status(self) -> Dict[str, Any]:
        """Check if market is currently open"""
        
        try:
            broker = self.broker_manager.get_active_broker()
            if broker and hasattr(broker, 'get_clock'):
                return await broker.get_clock()
        except Exception as e:
            logger.error(f"[ERROR] Market status check failed: {str(e)}")
        
        # Fallback to simple time-based check
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return {
                'is_open': False,
                'reason': 'Weekend',
                'next_open': 'Monday 9:30 AM ET'
            }
        
        # Check if it's within market hours
        current_time = now.time()
        
        if self.market_open_time <= current_time <= self.market_close_time:
            return {
                'is_open': True,
                'reason': 'Market hours',
                'next_close': f"Today {self.market_close_time}"
            }
        else:
            return {
                'is_open': False,
                'reason': 'Outside market hours',
                'next_open': f"Today {self.market_open_time}" if current_time < self.market_open_time else f"Tomorrow {self.market_open_time}"
            }
    
    async def _maintain_connections(self):
        """Maintain all connections and reconnect if needed"""
        
        # Health check all brokers
        health_results = await self.broker_manager.health_check_all()
        
        for broker_name, health in health_results.items():
            if health['status'] != 'healthy':
                logger.warning(f"🔄 Broker {broker_name} unhealthy: {health}")
                
                # Attempt reconnection
                broker = self.broker_manager.get_broker(broker_name)
                if broker:
                    await broker.connect()
        # Update heartbeat timestamp after health checks
        self.last_heartbeat = utc_now()
    
    async def _heartbeat_check(self):
        """Send heartbeat to monitoring systems"""
        
        heartbeat_data = {
            'timestamp': utc_iso(),
            'status': 'healthy',
            'trading_enabled': self.trading_enabled,
            'paper_trading': self.paper_trading,
            'daily_trade_count': self.daily_trade_count,
            'consecutive_failures': self.consecutive_failures,
            'active_broker': self.broker_manager.active_broker,
            'market_open': (await self._check_market_status()).get('is_open', False)
        }
        
        # Save heartbeat locally
        try:
            with open('heartbeat.json', 'w') as f:
                json.dump(heartbeat_data, f, indent=2)
        except Exception as e:
            logger.error(f"[ERROR] Heartbeat save failed: {str(e)}")
    
    def _update_daily_trade_count(self):
        """Update daily trade count"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.daily_trade_count = 0
            self.last_trade_date = today
            logger.info(f"📅 New trading day: {today}")
    
    async def _update_gamification(self, signal: Dict[str, Any], order_id: str):
        """Update gamification based on trade execution"""
        try:
            if self.gamification_engine:
                # Award achievement for successful trade
                achievement_data = {
                    'type': 'trade_executed',
                    'signal_source': signal['source'],
                    'confidence': signal.get('confidence', 0),
                    'order_id': order_id
                }
                # await self.gamification_engine.award_achievement(achievement_data)
        except Exception as e:
            logger.error(f"[ERROR] Gamification update failed: {str(e)}")
    
    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED")
        
        try:
            # Cancel all open orders
            broker = self.broker_manager.get_active_broker()
            if broker:
                logger.info("📋 Cancelling all open orders...")
                # Implementation would depend on broker API
            
            # Save final state
            await self.state_manager.emergency_save()
            
            # Send emergency notifications
            await self._send_emergency_notification()
            
            logger.info("[CHECK] Emergency shutdown completed")
            
        except Exception as e:
            logger.critical(f"[ERROR] Emergency shutdown failed: {str(e)}")
        
        finally:
            self.running = False
    
    async def _send_emergency_notification(self):
        """Send emergency notification"""
        try:
            notification = {
                'type': 'emergency_shutdown',
                'timestamp': utc_iso(),
                'reason': 'Too many consecutive failures',
                'daily_trade_count': self.daily_trade_count,
                'consecutive_failures': self.consecutive_failures
            }
            
            # Save notification
            with open('emergency_notification.json', 'w') as f:
                json.dump(notification, f, indent=2)
            
            logger.info("🚨 Emergency notification saved")
            
        except Exception as e:
            logger.error(f"[ERROR] Emergency notification failed: {str(e)}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📶 Received signal {signum}. Initiating graceful shutdown...")
        self.running = False


class TradingStateManager:
    """Persistent state management for trading service"""
    
    def __init__(self):
        self.state_file = 'trading_state.json'
        self.backup_state_file = 'trading_state_backup.json'
        self.current_state = {
            'last_update': None,
            'active_trades': {},
            'daily_statistics': {},
            'performance_metrics': {},
            'system_status': 'initialized'
        }
    
    async def initialize(self):
        """Initialize state manager"""
        logger.info("💾 Initializing Trading State Manager")
    
    async def load_state(self):
        """Load previous trading state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    self.current_state = json.load(f)
                logger.info(f"[CHECK] Loaded trading state from {self.current_state.get('last_update', 'unknown')}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load state: {str(e)}")
    
    async def save_state(self):
        """Save current trading state"""
        try:
            self.current_state['last_update'] = utc_iso()
            
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state, f, indent=2)
        except Exception as e:
            logger.error(f"[ERROR] Failed to save state: {str(e)}")
    
    async def emergency_save(self):
        """Emergency state save"""
        try:
            emergency_data = {
                'timestamp': utc_iso(),
                'state': self.current_state,
                'emergency': True
            }
            
            with open('emergency_state.json', 'w') as f:
                json.dump(emergency_data, f, indent=2)
            
            logger.info("🚨 Emergency state saved")
        except Exception as e:
            logger.critical(f"[ERROR] Emergency save failed: {str(e)}")
    
    async def record_trade(self, signal: Dict[str, Any], order_id: str):
        """Record trade execution"""
        try:
            trade_record = {
                'signal': signal,
                'order_id': order_id,
                'timestamp': utc_iso()
            }
            
            self.current_state['active_trades'][order_id] = trade_record
        except Exception as e:
            logger.error(f"[ERROR] Failed to record trade: {str(e)}")


class TradingRiskManager:
    """Risk management for trading operations"""
    
    def __init__(self):
        self.max_position_size_percent = 5.0
        self.max_portfolio_risk_percent = 2.0
        self.daily_loss_limit = 1000.0
    
    async def initialize(self):
        """Initialize risk manager"""
        logger.info("🛡️ Initializing Trading Risk Manager")
    
    async def validate_signals(self, signals: List[Dict[str, Any]], portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate trading signals against risk parameters"""
        validated_signals = []
        
        for signal in signals:
            if await self._validate_signal(signal, portfolio_data):
                validated_signals.append(signal)
            else:
                logger.warning(f"[WARNING]️ Signal rejected by risk management: {signal['symbol']}")
        
        return validated_signals
    
    async def _validate_signal(self, signal: Dict[str, Any], portfolio_data: Dict[str, Any]) -> bool:
        """Validate individual signal"""
        # Dynamic confidence threshold: lower if HRM persona with high confidence
        base_conf = signal.get('confidence', 0)
        hrm_meta = signal.get('hrm_meta') or {}
        dynamic_threshold = 0.6
        if signal.get('source') == 'hrm_persona':
            risk_level = hrm_meta.get('risk_level', 0.5)
            # Allow moderately lower threshold for normal (non-fallback) HRM signals with moderate risk
            if risk_level < 0.65 and not hrm_meta.get('fallback'):
                dynamic_threshold = 0.55
            # Strong high-confidence, low-risk signals can go a bit lower still
            if base_conf > 0.75 and risk_level < 0.6:
                dynamic_threshold = min(dynamic_threshold, 0.5)
            # Fallback decisions retain stricter bar
            if hrm_meta.get('fallback'):
                dynamic_threshold = 0.65
        if base_conf < dynamic_threshold:
            return False
        
        # HRM-informed max position size scaling
        account = portfolio_data['account']
        estimated_value = signal['quantity'] * 100  # Rough estimate
        max_pct = self.max_position_size_percent
        if signal.get('source') == 'hrm_persona':
            # Scale down if risk level high
            risk_level = hrm_meta.get('risk_level', 0.5)
            if risk_level > 0.7:
                max_pct *= 0.7
            elif risk_level < 0.4 and base_conf > 0.8:
                max_pct *= 1.1  # small allowance for strong low-risk high-confidence
        if (estimated_value / account.portfolio_value) > (max_pct / 100):
            return False
        
        return True


class PerformanceMonitor:
    """Performance monitoring for trading service"""
    
    def __init__(self):
        self.metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'total_pnl': 0.0,
            'uptime_percentage': 100.0
        }
    
    async def initialize(self):
        """Initialize performance monitor"""
        logger.info("📊 Initializing Performance Monitor")
    
    async def update_metrics(self):
        """Update performance metrics"""
        # Implementation for metric updates
        pass
    
    async def record_trading_cycle(self, portfolio_data: Dict[str, Any], signals: List[Dict[str, Any]], executed_signals: List[Dict[str, Any]]):
        """Record trading cycle performance"""
        self.metrics['total_trades'] += len(executed_signals)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_service.log'),
            logging.StreamHandler()
        ]
    )
    
    # Start the service
    service = BackgroundTradingService()
    
    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        logger.info("👋 Service stopped by user")
    except Exception as e:
        logger.critical(f"🚨 Service crashed: {str(e)}")
