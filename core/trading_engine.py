import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import timedelta, datetime
from core.utils.time_utils import utc_now
from decimal import Decimal
import uuid
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

@dataclass
class Order:
    """Trading order with all necessary information"""
    id: str
    user_id: int
    account_id: int
    symbol: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    limit_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal('0')
    filled_price: Optional[Decimal] = None
    commission: Decimal = Decimal('0')
    fees: Decimal = Decimal('0')
    created_at: datetime = None
    updated_at: datetime = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    broker_order_id: Optional[str] = None
    broker_trade_id: Optional[str] = None
    strategy_id: Optional[str] = None
    ai_agent_id: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = utc_now()
        if self.updated_at is None:
            self.updated_at = utc_now()

@dataclass
class Position:
    """Current position in a symbol"""
    symbol: str
    quantity: Decimal
    average_price: Decimal
    current_price: Optional[Decimal] = None
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Decimal = Decimal('0')
    total_pnl: Decimal = Decimal('0')
    market_value: Optional[Decimal] = None
    side: str = "long"  # long or short
    is_open: bool = True

class RiskManager:
    """Risk management system for trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_position_size = Decimal(str(config.get('max_position_size', 15000)))  # 15% increase for live trading
        self.max_daily_loss = Decimal(str(config.get('max_daily_loss', 1500)))  # 50% increase
        self.max_portfolio_risk = Decimal(str(config.get('max_portfolio_risk', 0.03)))  # 3% (1.5x increase)
        self.max_single_position_risk = Decimal(str(config.get('max_single_position_risk', 0.15)))  # 15% (3x increase)
        
    async def validate_order(self, order: Order, account_balance: Decimal,
                           current_positions: Dict[str, Position]) -> Tuple[bool, str]:
        """Validate if an order meets risk requirements"""
        try:
            # Ensure we have a valid price for validation
            if not order.price or order.price <= 0:
                return False, "Order price is required for risk validation"

            # Ensure quantity is positive
            if order.quantity <= 0:
                return False, "Order quantity must be positive"

            # Check if order would exceed max position size
            position_value = order.quantity * order.price
            if position_value > self.max_position_size:
                return False, f"Order value ${position_value:,.2f} exceeds max position size ${self.max_position_size:,.2f}"

            # Check if order would exceed account balance for buy orders
            if order.side == OrderSide.BUY:
                required_capital = position_value
                if required_capital > account_balance:
                    return False, f"Insufficient balance. Required: ${required_capital:,.2f}, Available: ${account_balance:,.2f}"

            # Check for existing position and calculate new total exposure
            existing_position = current_positions.get(order.symbol)
            if existing_position:
                existing_value = existing_position.quantity * existing_position.current_price
                if order.side == OrderSide.BUY:
                    new_total_value = existing_value + position_value
                else:  # SELL
                    new_total_value = max(Decimal('0'), existing_value - position_value)

                if new_total_value > self.max_position_size:
                    return False, f"Combined position value ${new_total_value:,.2f} would exceed max position size ${self.max_position_size:,.2f}"

            # Check portfolio risk
            total_exposure = self._calculate_total_exposure(current_positions, order)
            max_portfolio_exposure = account_balance * self.max_portfolio_risk
            if total_exposure > max_portfolio_exposure:
                return False, f"Order would exceed portfolio risk limit. Exposure: ${total_exposure:,.2f}, Limit: ${max_portfolio_exposure:,.2f}"

            # Check single position risk
            position_risk = position_value / account_balance
            if position_risk > self.max_single_position_risk:
                return False, f"Order would exceed single position risk limit. Risk: {position_risk:.2%}, Limit: {self.max_single_position_risk:.2%}"

            # Additional validation for large orders
            if position_value > account_balance * Decimal('0.5'):  # More than 50% of account
                return False, f"Order size too large. Cannot risk more than 50% of account balance in single trade"

            # Check daily loss limit (simplified - would need actual P&L tracking)
            daily_loss_estimate = position_value * Decimal('0.1')  # Assume max 10% loss
            if daily_loss_estimate > self.max_daily_loss:
                return False, f"Potential daily loss ${daily_loss_estimate:,.2f} exceeds limit ${self.max_daily_loss:,.2f}"

            return True, "Order validated successfully"

        except Exception as e:
            logger.error(f"Risk validation error: {e}")
            return False, f"Risk validation error: {str(e)}"
    
    def _calculate_total_exposure(self, positions: Dict[str, Position], new_order: Order) -> Decimal:
        """Calculate total portfolio exposure including new order"""
        total_exposure = Decimal('0')
        
        # Add existing positions
        for position in positions.values():
            if position.is_open:
                total_exposure += position.market_value or Decimal('0')
        
        # Add new order if it's a buy
        if new_order.side == OrderSide.BUY:
            total_exposure += new_order.quantity * (new_order.price or Decimal('0'))
        
        return total_exposure
    
    async def check_daily_loss_limit(self, account_id: int, daily_pnl: Decimal) -> Tuple[bool, str]:
        """Check if daily loss limit has been reached"""
        if daily_pnl < -self.max_daily_loss:
            return False, f"Daily loss limit exceeded. Loss: {daily_pnl}, Limit: {self.max_daily_loss}"
        return True, "Daily loss limit check passed"

class PortfolioManager:
    """Portfolio management and tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def calculate_portfolio_value(self, positions: Dict[str, Position], 
                                     cash_balance: Decimal) -> Dict[str, Any]:
        """Calculate current portfolio value and metrics"""
        try:
            total_market_value = cash_balance
            total_unrealized_pnl = Decimal('0')
            total_realized_pnl = Decimal('0')
            
            for position in positions.values():
                if position.is_open and position.market_value:
                    total_market_value += position.market_value
                    total_unrealized_pnl += position.unrealized_pnl
                    total_realized_pnl += position.realized_pnl
            
            total_pnl = total_unrealized_pnl + total_realized_pnl
            pnl_percentage = (total_pnl / (total_market_value - total_pnl)) * 100 if total_market_value > total_pnl else Decimal('0')
            
            return {
                'total_market_value': total_market_value,
                'cash_balance': cash_balance,
                'total_unrealized_pnl': total_unrealized_pnl,
                'total_realized_pnl': total_realized_pnl,
                'total_pnl': total_pnl,
                'pnl_percentage': pnl_percentage,
                'position_count': len([p for p in positions.values() if p.is_open])
            }
            
        except Exception as e:
            logger.error(f"Portfolio calculation error: {e}")
            return {
                'total_market_value': cash_balance,
                'cash_balance': cash_balance,
                'total_unrealized_pnl': Decimal('0'),
                'total_realized_pnl': Decimal('0'),
                'total_pnl': Decimal('0'),
                'pnl_percentage': Decimal('0'),
                'position_count': 0
            }
    
    async def update_position(self, symbol: str, order: Order, 
                            current_positions: Dict[str, Position]) -> Position:
        """Update position after order execution"""
        try:
            if symbol not in current_positions:
                current_positions[symbol] = Position(
                    symbol=symbol,
                    quantity=Decimal('0'),
                    average_price=Decimal('0')
                )
            
            position = current_positions[symbol]
            
            if order.side == OrderSide.BUY:
                # Add to position
                total_quantity = position.quantity + order.filled_quantity
                total_cost = (position.quantity * position.average_price) + (order.filled_quantity * order.filled_price)
                
                if total_quantity > 0:
                    position.average_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.side = "long"
                
            elif order.side == OrderSide.SELL:
                # Reduce position
                if position.quantity >= order.filled_quantity:
                    # Calculate realized P&L
                    realized_pnl = (order.filled_price - position.average_price) * order.filled_quantity
                    position.realized_pnl += realized_pnl
                    
                    position.quantity -= order.filled_quantity
                    
                    if position.quantity == 0:
                        position.is_open = False
                        position.average_price = Decimal('0')
                else:
                    # Short selling (not implemented in this basic version)
                    logger.warning(f"Short selling not implemented for {symbol}")
            
            return position
            
        except Exception as e:
            logger.error(f"Position update error: {e}")
            raise

# Add quantum trading integration
from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine

class TradingEngine:
    """Main trading engine that coordinates all trading operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.risk_manager = RiskManager(config.get('risk', {}))
        self.portfolio_manager = PortfolioManager(config.get('portfolio', {}))
        
        # Initialize quantum trading engine
        quantum_config = config.get('quantum', {
            'portfolio': {'max_qubits': 50, 'optimization_level': 'high'},
            'risk': {'max_risk_qubits': 20},
            'arbitrage': {'detection_sensitivity': 0.001}
        })
        self.quantum_engine = QuantumTradingEngine(quantum_config)
        
        self.active_orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.order_history: List[Order] = []
        
    async def place_order(self, order_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Place a new trading order with optional quantum optimization"""
        try:
            # Create order object
            order = Order(
                id=str(uuid.uuid4()),
                user_id=order_data['user_id'],
                account_id=order_data['account_id'],
                symbol=order_data['symbol'],
                side=OrderSide(order_data['side']),
                quantity=Decimal(str(order_data['quantity'])),
                order_type=OrderType(order_data['order_type']),
                price=Decimal(str(order_data.get('price', 0))) if order_data.get('price') else None,
                stop_price=Decimal(str(order_data.get('stop_price', 0))) if order_data.get('stop_price') else None,
                limit_price=Decimal(str(order_data.get('limit_price', 0))) if order_data.get('limit_price') else None,
                strategy_id=order_data.get('strategy_id'),
                ai_agent_id=order_data.get('ai_agent_id'),
                notes=order_data.get('notes'),
                metadata=order_data.get('metadata', {})
            )
            
            # Check if quantum optimization is requested
            use_quantum = order_data.get('use_quantum_optimization', False)
            
            if use_quantum:
                # Apply quantum optimization to the order
                quantum_result = await self._apply_quantum_optimization(order)
                if quantum_result.get('success'):
                    order.metadata['quantum_optimization'] = quantum_result
                    order.notes = f"Quantum optimized: {quantum_result.get('confidence', 0):.2f} confidence"
            
            # Get account balance and positions
            account_balance = await self._get_account_balance(order.account_id)
            current_positions = await self._get_positions(order.account_id)

            # For market orders, get current price for risk validation
            if order.order_type == OrderType.MARKET and not order.price:
                market_price = await self._get_market_price(order.symbol)
                if market_price:
                    order.price = market_price
                else:
                    order.status = OrderStatus.REJECTED
                    order.notes = f"Unable to get market price for {order.symbol}"
                    self.order_history.append(order)
                    return False, f"Unable to get market price for {order.symbol}", None

            # Risk validation
            is_valid, message = await self.risk_manager.validate_order(
                order, account_balance, current_positions
            )
            
            if not is_valid:
                order.status = OrderStatus.REJECTED
                order.notes = f"Risk validation failed: {message}"
                self.order_history.append(order)
                return False, message, None
            
            # Store order
            self.active_orders[order.id] = order
            self.order_history.append(order)
            
            # Execute order based on type
            if order.order_type == OrderType.MARKET:
                success, message = await self._execute_market_order(order)
            elif order.order_type == OrderType.LIMIT:
                success, message = await self._execute_limit_order(order)
            elif order.order_type == OrderType.STOP:
                success, message = await self._execute_stop_order(order)
            else:
                success, message = False, f"Unsupported order type: {order.order_type}"
            
            if success:
                # Update position
                await self.portfolio_manager.update_position(
                    order.symbol, order, current_positions
                )
                
                # Remove from active orders if fully filled
                if order.status == OrderStatus.FILLED:
                    if order.id in self.active_orders:
                        del self.active_orders[order.id]
            
            return success, message, order.id
            
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return False, f"Order placement error: {str(e)}", None
    
    async def _execute_market_order(self, order: Order) -> Tuple[bool, str]:
        """Execute a market order"""
        try:
            # Get current market price
            current_price = await self._get_market_price(order.symbol)
            if not current_price:
                order.status = OrderStatus.REJECTED
                return False, f"Unable to get market price for {order.symbol}"
            
            # Fill order at market price
            order.filled_price = current_price
            order.filled_quantity = order.quantity
            order.status = OrderStatus.FILLED
            order.filled_at = utc_now()
            order.updated_at = utc_now()
            
            # Calculate fees and commission
            order.commission = self._calculate_commission(order)
            order.fees = self._calculate_fees(order)
            
            logger.info(f"Market order executed: {order.symbol} {order.side.value} {order.quantity} @ {order.filled_price}")
            return True, "Market order executed successfully"
            
        except Exception as e:
            logger.error(f"Market order execution error: {e}")
            order.status = OrderStatus.REJECTED
            return False, f"Market order execution error: {str(e)}"
    
    async def _execute_limit_order(self, order: Order) -> Tuple[bool, str]:
        """Execute a limit order"""
        try:
            current_price = await self._get_market_price(order.symbol)
            if not current_price:
                return False, f"Unable to get market price for {order.symbol}"
            
            # Check if limit conditions are met
            if order.side == OrderSide.BUY and current_price <= order.limit_price:
                # Buy limit order - price is at or below limit
                order.filled_price = current_price
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
                order.filled_at = utc_now()
            elif order.side == OrderSide.SELL and current_price >= order.limit_price:
                # Sell limit order - price is at or above limit
                order.filled_price = current_price
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
                order.filled_at = utc_now()
            else:
                # Limit not met, keep order active
                return True, "Limit order placed, waiting for conditions"
            
            if order.status == OrderStatus.FILLED:
                order.updated_at = utc_now()
                order.commission = self._calculate_commission(order)
                order.fees = self._calculate_fees(order)
                logger.info(f"Limit order executed: {order.symbol} {order.side.value} {order.quantity} @ {order.filled_price}")
                return True, "Limit order executed successfully"
            
            return True, "Limit order placed"
            
        except Exception as e:
            logger.error(f"Limit order execution error: {e}")
            order.status = OrderStatus.REJECTED
            return False, f"Limit order execution error: {str(e)}"
    
    async def _execute_stop_order(self, order: Order) -> Tuple[bool, str]:
        """Execute a stop order"""
        try:
            current_price = await self._get_market_price(order.symbol)
            if not current_price:
                return False, f"Unable to get market price for {order.symbol}"
            
            # Check if stop conditions are met
            if order.side == OrderSide.SELL and current_price <= order.stop_price:
                # Stop loss triggered
                order.filled_price = current_price
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
                order.filled_at = utc_now()
            elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                # Stop buy triggered
                order.filled_price = current_price
                order.filled_quantity = order.quantity
                order.status = OrderStatus.FILLED
                order.filled_at = utc_now()
            else:
                # Stop not triggered, keep order active
                return True, "Stop order placed, waiting for conditions"
            
            if order.status == OrderStatus.FILLED:
                order.updated_at = utc_now()
                order.commission = self._calculate_commission(order)
                order.fees = self._calculate_fees(order)
                logger.info(f"Stop order executed: {order.symbol} {order.side.value} {order.quantity} @ {order.filled_price}")
                return True, "Stop order executed successfully"
            
            return True, "Stop order placed"
            
        except Exception as e:
            logger.error(f"Stop order execution error: {e}")
            order.status = OrderStatus.REJECTED
            return False, f"Stop order execution error: {str(e)}"
    
    async def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """Cancel an active order"""
        try:
            if order_id not in self.active_orders:
                return False, f"Order {order_id} not found or not active"
            
            order = self.active_orders[order_id]
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = utc_now()
            order.updated_at = utc_now()
            
            # Remove from active orders
            del self.active_orders[order_id]
            
            logger.info(f"Order cancelled: {order_id}")
            return True, "Order cancelled successfully"
            
        except Exception as e:
            logger.error(f"Order cancellation error: {e}")
            return False, f"Order cancellation error: {str(e)}"
    
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an order"""
        try:
            # Check active orders first
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
            else:
                # Check order history
                order = next((o for o in self.order_history if o.id == order_id), None)
            
            if not order:
                return None
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': float(order.quantity),
                'order_type': order.order_type.value,
                'status': order.status.value,
                'price': float(order.price) if order.price else None,
                'filled_quantity': float(order.filled_quantity),
                'filled_price': float(order.filled_price) if order.filled_price else None,
                'commission': float(order.commission),
                'fees': float(order.fees),
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
                'filled_at': order.filled_at.isoformat() if order.filled_at else None,
                'cancelled_at': order.cancelled_at.isoformat() if order.cancelled_at else None,
                'notes': order.notes
            }
            
        except Exception as e:
            logger.error(f"Get order status error: {e}")
            return None
    
    async def get_portfolio_summary(self, account_id: int) -> Dict[str, Any]:
        """Get portfolio summary for an account"""
        try:
            account_balance = await self._get_account_balance(account_id)
            positions = await self._get_positions(account_id)
            
            portfolio_data = await self.portfolio_manager.calculate_portfolio_value(
                positions, account_balance
            )
            
            # Add position details
            position_details = []
            for symbol, position in positions.items():
                if position.is_open:
                    position_details.append({
                        'symbol': symbol,
                        'quantity': float(position.quantity),
                        'average_price': float(position.average_price),
                        'current_price': float(position.current_price) if position.current_price else None,
                        'market_value': float(position.market_value) if position.market_value else None,
                        'unrealized_pnl': float(position.unrealized_pnl),
                        'realized_pnl': float(position.realized_pnl),
                        'total_pnl': float(position.total_pnl),
                        'side': position.side
                    })
            
            return {
                **portfolio_data,
                'positions': position_details,
                'active_orders': len(self.active_orders)
            }
            
        except Exception as e:
            logger.error(f"Portfolio summary error: {e}")
            return {
                'total_market_value': 0,
                'cash_balance': 0,
                'total_unrealized_pnl': 0,
                'total_realized_pnl': 0,
                'total_pnl': 0,
                'pnl_percentage': 0,
                'position_count': 0,
                'positions': [],
                'active_orders': 0
            }
    
    async def _apply_quantum_optimization(self, order: Order) -> Dict[str, Any]:
        """Apply quantum optimization to trading order"""
        try:
            # Get market data for quantum optimization
            market_data = await self._get_market_data_for_quantum(order.symbol)
            
            # Execute quantum trade optimization
            quantum_result = await self.quantum_engine.execute_quantum_trade({
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side.value,
                'quantity': float(order.quantity),
                'order_type': order.order_type.value,
                'price': float(order.price) if order.price else None
            })
            
            return quantum_result
            
        except Exception as e:
            logger.error(f"Quantum optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_market_data_for_quantum(self, symbol: str) -> Dict[str, Any]:
        """Get market data for quantum optimization using real market data"""
        try:
            from core.real_time_market_data import market_data_orchestrator
            
            # Get real market data
            real_data = await market_data_orchestrator.get_live_stock_data(symbol)
            
            if real_data:
                # Calculate volatility from real price movements
                volatility = abs(real_data.change_percent) / 100 if real_data.change_percent else 0.2
                
                # Estimate liquidity based on volume (normalized)
                liquidity = min(1.0, max(0.3, real_data.volume / 10000000)) if real_data.volume else 0.7
                
                return {
                    'symbol': symbol,
                    'price': real_data.price,
                    'volume': real_data.volume,
                    'volatility': volatility,
                    'liquidity': liquidity,
                    'timestamp': real_data.timestamp.isoformat().replace('+00:00','Z'),
                    'source': real_data.source,
                    'real_data': True
                }
            else:
                # Fallback to reasonable defaults if real data unavailable
                base_price = await self._get_market_price(symbol)
                return {
                    'symbol': symbol,
                    'price': float(base_price),
                    'volume': 5000000,  # Conservative volume
                    'volatility': 0.25,  # Moderate volatility
                    'liquidity': 0.8,    # Good liquidity
                    'timestamp': utc_now().isoformat().replace('+00:00','Z'),
                    'source': 'fallback',
                    'real_data': False
                }
        except Exception as e:
            logger.error(f"Market data retrieval error: {e}")
            return {
                'symbol': symbol,
                'price': 100.0,
                'volume': 1000000,
                'volatility': 0.2,
                'liquidity': 0.8,
                'timestamp': utc_now().isoformat().replace('+00:00','Z')
            }
    
    async def optimize_portfolio_quantum(self, account_id: int, assets: List[str], 
                                       returns_data: List[List[float]], 
                                       risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Optimize portfolio using quantum algorithms"""
        try:
            # Convert returns data to numpy array
            import numpy as np
            returns_array = np.array(returns_data)
            
            result = await self.quantum_engine.optimize_portfolio_quantum(
                assets, returns_array, risk_free_rate
            )
            
            if result['success']:
                # Store optimization result in portfolio
                optimization_data = {
                    'optimization_id': result['optimization_id'],
                    'optimal_weights': result['optimal_weights'],
                    'expected_return': result['expected_return'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'quantum_advantage': result['quantum_advantage'],
                    'execution_time_ms': result['execution_time_ms'],
                    'confidence': result['confidence'],
                    'timestamp': utc_now().isoformat().replace('+00:00','Z')
                }
                
                # This would store the optimization result in the database
                logger.info(f"Portfolio optimization completed for account {account_id}")
                
                return {
                    'success': True,
                    'optimization': optimization_data,
                    'recommendations': self._generate_portfolio_recommendations(optimization_data)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Optimization failed')
                }
                
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_portfolio_recommendations(self, optimization_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading recommendations based on quantum optimization"""
        recommendations = []
        
        # Analyze optimal weights and generate recommendations
        optimal_weights = optimization_data['optimal_weights']
        expected_return = optimization_data['expected_return']
        sharpe_ratio = optimization_data['sharpe_ratio']
        
        # Generate buy/sell recommendations based on optimal weights
        for i, weight in enumerate(optimal_weights):
            if weight > 0.1:  # Significant position
                recommendations.append({
                    'action': 'buy',
                    'symbol': f'ASSET_{i}',
                    'weight': weight,
                    'reason': f'Optimal allocation: {weight:.2%}',
                    'confidence': optimization_data['confidence']
                })
            elif weight < 0.05:  # Small position
                recommendations.append({
                    'action': 'sell',
                    'symbol': f'ASSET_{i}',
                    'weight': weight,
                    'reason': f'Reduce allocation: {weight:.2%}',
                    'confidence': optimization_data['confidence']
                })
        
        return recommendations
    
    async def get_quantum_statistics(self) -> Dict[str, Any]:
        """Get quantum trading statistics"""
        try:
            stats = await self.quantum_engine.get_quantum_statistics()
            
            # Add trading-specific quantum statistics
            quantum_orders = [order for order in self.order_history 
                            if order.metadata.get('quantum_optimization')]
            
            stats['quantum_orders'] = len(quantum_orders)
            stats['quantum_order_success_rate'] = (
                len([order for order in quantum_orders if order.status == OrderStatus.FILLED]) / 
                len(quantum_orders) if quantum_orders else 0
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Quantum statistics error: {e}")
            return {
                'total_optimizations': 0,
                'quantum_advantages': 0,
                'advantage_rate': 0,
                'quantum_orders': 0,
                'quantum_order_success_rate': 0
            }
    
    # Helper methods (these would integrate with your data layer)
    async def _get_market_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for a symbol"""
        # This would integrate with your market data API
        # For now, return a mock price
        mock_prices = {
            'AAPL': Decimal('150.00'),
            'GOOGL': Decimal('2800.00'),
            'MSFT': Decimal('380.00'),
            'TSLA': Decimal('250.00'),
            'BTC': Decimal('45000.00'),
            'ETH': Decimal('3000.00')
        }
        return mock_prices.get(symbol, Decimal('100.00'))
    
    async def _get_account_balance(self, account_id: int) -> Decimal:
        """Get account balance"""
        # This would integrate with your database
        # For now, return a mock balance
        return Decimal('10000.00')
    
    async def _get_positions(self, account_id: int) -> Dict[str, Position]:
        """Get current positions for an account"""
        # This would integrate with your database
        # For now, return empty positions
        return {}
    
    def _calculate_commission(self, order: Order) -> Decimal:
        """Calculate commission for an order"""
        # Simple commission calculation
        commission_rate = Decimal('0.0025')  # 0.25%
        return order.filled_quantity * order.filled_price * commission_rate
    
    def _calculate_fees(self, order: Order) -> Decimal:
        """Calculate additional fees for an order"""
        # Simple fee calculation
        fee_rate = Decimal('0.0001')  # 0.01%
        return order.filled_quantity * order.filled_price * fee_rate 