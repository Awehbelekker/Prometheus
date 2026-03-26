"""
AUTONOMOUS BROKER EXECUTOR
=========================
Connects the autonomous trading system to real brokers (Alpaca & IB).

This is the critical execution layer that actually places trades!
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result from broker execution"""
    success: bool
    order_id: Optional[str] = None
    filled_price: Optional[float] = None
    filled_qty: Optional[float] = None
    status: str = "pending"
    error_message: Optional[str] = None
    broker_name: str = "unknown"
    execution_time: datetime = None

class AutonomousBrokerExecutor:
    """
    Executes trades from autonomous system through real brokers
    """
    
    def __init__(self, 
                 use_alpaca: bool = True,
                 use_ib: bool = False,
                 paper_mode: bool = False):
        self.use_alpaca = use_alpaca
        self.use_ib = use_ib
        self.paper_mode = paper_mode
        
        # Broker instances
        self.alpaca_broker = None
        self.ib_broker = None
        
        # Track active orders
        self.active_orders = {}
        
        logger.info("🔌 Autonomous Broker Executor initialized")
        logger.info(f"   Alpaca: {'Enabled' if use_alpaca else 'Disabled'}")
        logger.info(f"   IB: {'Enabled' if use_ib else 'Disabled'}")
        logger.info(f"   Mode: {'PAPER TRADING' if paper_mode else 'LIVE TRADING'}")
    
    async def initialize_brokers(self) -> bool:
        """Initialize broker connections"""
        success = False
        
        # Initialize Alpaca
        if self.use_alpaca:
            try:
                from brokers.alpaca_broker import AlpacaBroker
                import os
                
                config = {
                    'api_key': os.getenv('ALPACA_API_KEY'),
                    'secret_key': os.getenv('ALPACA_SECRET_KEY'),
                    'paper_trading': self.paper_mode
                }
                
                self.alpaca_broker = AlpacaBroker(config)
                connected = await self.alpaca_broker.connect()
                
                if connected:
                    logger.info("✅ Alpaca broker connected")
                    success = True
                else:
                    logger.warning("⚠️ Alpaca broker connection failed")
                    
            except Exception as e:
                logger.error(f"❌ Error initializing Alpaca: {e}")
        
        # Initialize IB
        if self.use_ib:
            try:
                from brokers.interactive_brokers_broker import InteractiveBrokersBroker
                import os
                
                config = {
                    'host': os.getenv('IB_HOST', '127.0.0.1'),
                    'port': int(os.getenv('IB_PORT', 7497)),  # 7497 = paper
                    'client_id': 1
                }
                
                self.ib_broker = InteractiveBrokersBroker(config)
                connected = await self.ib_broker.connect()
                
                if connected:
                    logger.info("✅ IB broker connected")
                    success = True
                else:
                    logger.warning("⚠️ IB broker connection failed")
                    
            except Exception as e:
                logger.error(f"❌ Error initializing IB: {e}")
        
        return success
    
    def _select_broker(self, symbol: str):
        """Select appropriate broker for symbol"""
        # Crypto goes to Alpaca
        if 'USD' in symbol and symbol not in ['USD', 'USDJPY', 'EURUSD']:
            if symbol.replace('USD', '') in ['BTC', 'ETH', 'SOL', 'ADA', 'AVAX', 'DOGE', 'MATIC']:
                return self.alpaca_broker, 'Alpaca'
        
        # Forex goes to IB (if available)
        if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']:
            if self.ib_broker:
                return self.ib_broker, 'IB'
        
        # Stocks: prefer IB if available, else Alpaca
        if self.ib_broker:
            return self.ib_broker, 'IB'
        elif self.alpaca_broker:
            return self.alpaca_broker, 'Alpaca'
        
        return None, None
    
    async def execute_strategy(self, 
                               symbol: str,
                               strategy_type: str,
                               capital_allocated: float,
                               entry_price: float,
                               target_price: float,
                               stop_price: float) -> ExecutionResult:
        """
        Execute a single strategy by placing order with broker
        
        Args:
            symbol: Trading symbol
            strategy_type: Strategy type (momentum, scalp, swing)
            capital_allocated: Capital to use
            entry_price: Expected entry price
            target_price: Profit target price
            stop_price: Stop loss price
            
        Returns:
            ExecutionResult with order details
        """
        try:
            # Select broker
            broker, broker_name = self._select_broker(symbol)
            
            if not broker:
                logger.error(f"No broker available for {symbol}")
                return ExecutionResult(
                    success=False,
                    error_message="No broker available",
                    execution_time=datetime.now()
                )
            
            # Calculate quantity
            quantity = capital_allocated / entry_price
            
            # Round quantity appropriately
            if 'USD' in symbol and symbol.replace('USD', '') in ['BTC', 'ETH']:
                quantity = round(quantity, 6)  # Crypto precision
            else:
                quantity = int(quantity)  # Stocks must be whole shares
            
            if quantity <= 0:
                logger.warning(f"Quantity too small for {symbol}: {quantity}")
                return ExecutionResult(
                    success=False,
                    error_message="Quantity too small",
                    execution_time=datetime.now()
                )
            
            logger.info(f"📤 Placing {broker_name} order:")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Strategy: {strategy_type}")
            logger.info(f"   Quantity: {quantity}")
            logger.info(f"   Capital: ${capital_allocated:.2f}")
            
            # Place order with broker
            order = await broker.place_order(
                symbol=symbol,
                qty=quantity,
                side='buy',
                order_type='market',
                time_in_force='day'
            )
            
            if order:
                # Track order
                self.active_orders[order.id] = {
                    'symbol': symbol,
                    'strategy': strategy_type,
                    'quantity': quantity,
                    'target_price': target_price,
                    'stop_price': stop_price,
                    'entry_time': datetime.now()
                }
                
                logger.info(f"✅ Order placed successfully: {order.id}")
                
                return ExecutionResult(
                    success=True,
                    order_id=order.id,
                    filled_price=getattr(order, 'filled_avg_price', entry_price),
                    filled_qty=quantity,
                    status=order.status,
                    broker_name=broker_name,
                    execution_time=datetime.now()
                )
            else:
                logger.error(f"❌ Order placement failed for {symbol}")
                return ExecutionResult(
                    success=False,
                    error_message="Order placement failed",
                    broker_name=broker_name,
                    execution_time=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"❌ Error executing strategy for {symbol}: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e),
                execution_time=datetime.now()
            )
    
    async def check_order_status(self, order_id: str) -> Dict[str, Any]:
        """Check status of an order"""
        try:
            # Try Alpaca first
            if self.alpaca_broker:
                try:
                    order = await self.alpaca_broker.get_order(order_id)
                    return {
                        'order_id': order_id,
                        'status': order.status,
                        'filled_qty': getattr(order, 'filled_qty', 0),
                        'filled_price': getattr(order, 'filled_avg_price', 0)
                    }
                except:
                    pass
            
            # Try IB
            if self.ib_broker:
                try:
                    order = await self.ib_broker.get_order(order_id)
                    return {
                        'order_id': order_id,
                        'status': order.status,
                        'filled_qty': order.filled_qty,
                        'filled_price': order.avg_fill_price
                    }
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking order {order_id}: {e}")
            return None
    
    async def close_position(self, symbol: str, quantity: float) -> ExecutionResult:
        """Close a position"""
        try:
            broker, broker_name = self._select_broker(symbol)
            
            if not broker:
                return ExecutionResult(
                    success=False,
                    error_message="No broker available"
                )
            
            logger.info(f"📤 Closing position: {symbol} x {quantity}")
            
            order = await broker.place_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                order_type='market',
                time_in_force='day'
            )
            
            if order:
                logger.info(f"✅ Position closed: {order.id}")
                return ExecutionResult(
                    success=True,
                    order_id=order.id,
                    status=order.status,
                    broker_name=broker_name,
                    execution_time=datetime.now()
                )
            else:
                return ExecutionResult(
                    success=False,
                    error_message="Close order failed",
                    broker_name=broker_name
                )
                
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            # Try Alpaca first
            if self.alpaca_broker:
                account = await self.alpaca_broker.get_account()
                return {
                    'equity': float(account.equity),
                    'cash': float(account.cash),
                    'buying_power': float(account.buying_power),
                    'broker': 'Alpaca'
                }
            
            # Try IB
            if self.ib_broker:
                account = await self.ib_broker.get_account()
                return {
                    'equity': float(account.equity),
                    'cash': float(account.cash),
                    'buying_power': float(account.buying_power),
                    'broker': 'IB'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            'active_orders': len(self.active_orders),
            'alpaca_enabled': self.use_alpaca and self.alpaca_broker is not None,
            'ib_enabled': self.use_ib and self.ib_broker is not None,
            'paper_mode': self.paper_mode
        }

# Global instance (optional)
autonomous_broker_executor = None

async def get_broker_executor(paper_mode: bool = None) -> AutonomousBrokerExecutor:
    """Get or create broker executor — reads live/IB settings from environment"""
    global autonomous_broker_executor
    
    if autonomous_broker_executor is None:
        import os
        # Respect env flags set in .env
        if paper_mode is None:
            paper_mode = os.getenv('ALPACA_PAPER_TRADING', 'false').lower() in ('1', 'true', 'yes')
        ib_enabled = os.getenv('IB_LIVE_ENABLED', 'false').lower() in ('1', 'true', 'yes')

        logger.info(f"BrokerExecutor init: paper_mode={paper_mode}  ib_enabled={ib_enabled}")

        autonomous_broker_executor = AutonomousBrokerExecutor(
            use_alpaca=True,
            use_ib=ib_enabled,
            paper_mode=paper_mode
        )
        await autonomous_broker_executor.initialize_brokers()
    
    return autonomous_broker_executor
