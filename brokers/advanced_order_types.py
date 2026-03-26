"""
Advanced Order Types System
Implements TWAP, VWAP, Iceberg, and other institutional-grade order types
Reduces market impact and improves execution quality
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Advanced order types"""
    MARKET = "market"
    LIMIT = "limit"
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    ICEBERG = "iceberg"  # Hidden orders
    POV = "pov"  # Percentage of Volume
    ARRIVAL_PRICE = "arrival_price"  # Implementation shortfall
    DARK_POOL = "dark_pool"  # Dark pool execution

@dataclass
class AdvancedOrder:
    """Advanced order specification"""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    total_quantity: float
    order_type: OrderType
    start_time: datetime
    end_time: datetime
    
    # TWAP parameters
    twap_intervals: Optional[int] = None
    twap_interval_seconds: Optional[int] = None
    
    # VWAP parameters
    vwap_profile: Optional[List[float]] = None  # Volume distribution
    
    # Iceberg parameters
    iceberg_visible_quantity: Optional[float] = None
    
    # POV parameters
    pov_target_percentage: Optional[float] = None
    
    # Execution tracking
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    slices: List[Dict[str, Any]] = None
    status: str = 'pending'

class AdvancedOrderExecutor:
    """
    Executes advanced order types with minimal market impact
    Implements institutional-grade algorithms
    """
    
    def __init__(self):
        # Active orders
        self.active_orders = {}
        
        # Execution statistics
        self.execution_stats = {
            'total_orders': 0,
            'completed_orders': 0,
            'cancelled_orders': 0,
            'average_slippage': 0.0,
            'average_fill_rate': 0.0
        }
        
        # Market impact models
        self.market_impact_models = {
            'default': lambda qty, vol: 0.001 * (qty / vol) ** 0.5
        }
        
        logger.info("✅ Advanced Order Executor initialized")
    
    async def execute_twap_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        intervals: int = None
    ) -> AdvancedOrder:
        """
        Execute Time-Weighted Average Price order
        Splits order into equal intervals over time
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            total_quantity: Total quantity to trade
            duration_minutes: Order duration in minutes
            intervals: Number of intervals (default: duration_minutes)
            
        Returns:
            Advanced order object
        """
        try:
            if intervals is None:
                intervals = duration_minutes
            
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(minutes=duration_minutes)
            interval_seconds = (duration_minutes * 60) / intervals
            
            order = AdvancedOrder(
                order_id=self._generate_order_id(),
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                order_type=OrderType.TWAP,
                start_time=start_time,
                end_time=end_time,
                twap_intervals=intervals,
                twap_interval_seconds=int(interval_seconds),
                slices=[]
            )
            
            self.active_orders[order.order_id] = order
            
            logger.info(f"📊 Executing TWAP order: {total_quantity} {symbol} over {duration_minutes}min")
            logger.info(f"   Intervals: {intervals}, Slice size: {total_quantity/intervals:.4f}")
            
            # Execute slices
            slice_quantity = total_quantity / intervals
            
            for i in range(intervals):
                if order.status == 'cancelled':
                    break
                
                # Wait for next interval
                if i > 0:
                    await asyncio.sleep(interval_seconds)
                
                # Execute slice
                slice_result = await self._execute_slice(
                    order,
                    slice_quantity,
                    f"TWAP slice {i+1}/{intervals}"
                )
                
                order.slices.append(slice_result)
                order.filled_quantity += slice_result['filled_quantity']
                
                # Update average fill price
                if order.filled_quantity > 0:
                    order.average_fill_price = (
                        (order.average_fill_price * (order.filled_quantity - slice_result['filled_quantity']) +
                         slice_result['fill_price'] * slice_result['filled_quantity']) /
                        order.filled_quantity
                    )
                
                logger.info(f"   ✅ Slice {i+1} complete: {slice_result['filled_quantity']:.4f} @ {slice_result['fill_price']:.2f}")
            
            order.status = 'completed'
            self.execution_stats['completed_orders'] += 1
            
            logger.info(f"✅ TWAP order complete: {order.filled_quantity:.4f} @ avg {order.average_fill_price:.2f}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error executing TWAP order: {e}")
            if 'order' in locals():
                order.status = 'error'
            raise
    
    async def execute_vwap_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        volume_profile: Optional[List[float]] = None
    ) -> AdvancedOrder:
        """
        Execute Volume-Weighted Average Price order
        Distributes order based on expected volume profile
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            total_quantity: Total quantity to trade
            duration_minutes: Order duration
            volume_profile: Expected volume distribution (default: U-shaped)
            
        Returns:
            Advanced order object
        """
        try:
            # Default U-shaped volume profile (higher at open/close)
            if volume_profile is None:
                intervals = min(duration_minutes, 60)
                volume_profile = self._generate_u_shaped_profile(intervals)
            else:
                intervals = len(volume_profile)
            
            # Normalize profile
            volume_profile = np.array(volume_profile) / np.sum(volume_profile)
            
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(minutes=duration_minutes)
            interval_seconds = (duration_minutes * 60) / intervals
            
            order = AdvancedOrder(
                order_id=self._generate_order_id(),
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                order_type=OrderType.VWAP,
                start_time=start_time,
                end_time=end_time,
                vwap_profile=volume_profile.tolist(),
                slices=[]
            )
            
            self.active_orders[order.order_id] = order
            
            logger.info(f"📊 Executing VWAP order: {total_quantity} {symbol} over {duration_minutes}min")
            logger.info(f"   Using {'custom' if volume_profile is not None else 'U-shaped'} volume profile")
            
            # Execute slices according to volume profile
            for i, volume_weight in enumerate(volume_profile):
                if order.status == 'cancelled':
                    break
                
                if i > 0:
                    await asyncio.sleep(interval_seconds)
                
                slice_quantity = total_quantity * volume_weight
                
                slice_result = await self._execute_slice(
                    order,
                    slice_quantity,
                    f"VWAP slice {i+1}/{intervals} ({volume_weight:.1%})"
                )
                
                order.slices.append(slice_result)
                order.filled_quantity += slice_result['filled_quantity']
                
                if order.filled_quantity > 0:
                    order.average_fill_price = (
                        (order.average_fill_price * (order.filled_quantity - slice_result['filled_quantity']) +
                         slice_result['fill_price'] * slice_result['filled_quantity']) /
                        order.filled_quantity
                    )
                
                logger.info(f"   ✅ Slice {i+1}: {slice_result['filled_quantity']:.4f} @ {slice_result['fill_price']:.2f}")
            
            order.status = 'completed'
            self.execution_stats['completed_orders'] += 1
            
            logger.info(f"✅ VWAP order complete: {order.filled_quantity:.4f} @ avg {order.average_fill_price:.2f}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error executing VWAP order: {e}")
            if 'order' in locals():
                order.status = 'error'
            raise
    
    async def execute_iceberg_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        visible_quantity: float,
        limit_price: Optional[float] = None
    ) -> AdvancedOrder:
        """
        Execute Iceberg order
        Only shows small portion of order to market
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            total_quantity: Total quantity (hidden)
            visible_quantity: Quantity visible to market
            limit_price: Limit price (None for market)
            
        Returns:
            Advanced order object
        """
        try:
            start_time = datetime.utcnow()
            
            order = AdvancedOrder(
                order_id=self._generate_order_id(),
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                order_type=OrderType.ICEBERG,
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),  # Max 1 hour
                iceberg_visible_quantity=visible_quantity,
                slices=[]
            )
            
            self.active_orders[order.order_id] = order
            
            logger.info(f"🧊 Executing Iceberg order: {total_quantity} {symbol}")
            logger.info(f"   Visible: {visible_quantity}, Hidden: {total_quantity - visible_quantity}")
            
            # Execute in visible slices
            remaining = total_quantity
            slice_num = 0
            
            while remaining > 0 and order.status != 'cancelled':
                slice_num += 1
                current_slice = min(visible_quantity, remaining)
                
                slice_result = await self._execute_slice(
                    order,
                    current_slice,
                    f"Iceberg slice {slice_num} (visible: {current_slice:.4f})",
                    limit_price=limit_price
                )
                
                order.slices.append(slice_result)
                order.filled_quantity += slice_result['filled_quantity']
                remaining -= slice_result['filled_quantity']
                
                if order.filled_quantity > 0:
                    order.average_fill_price = (
                        (order.average_fill_price * (order.filled_quantity - slice_result['filled_quantity']) +
                         slice_result['fill_price'] * slice_result['filled_quantity']) /
                        order.filled_quantity
                    )
                
                logger.info(f"   ✅ Slice {slice_num}: {slice_result['filled_quantity']:.4f} @ {slice_result['fill_price']:.2f}, Remaining: {remaining:.4f}")
                
                # Small delay between slices to avoid detection
                if remaining > 0:
                    await asyncio.sleep(np.random.uniform(1, 3))
            
            order.status = 'completed'
            self.execution_stats['completed_orders'] += 1
            
            logger.info(f"✅ Iceberg order complete: {order.filled_quantity:.4f} @ avg {order.average_fill_price:.2f}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error executing Iceberg order: {e}")
            if 'order' in locals():
                order.status = 'error'
            raise
    
    async def execute_pov_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        target_pov: float,  # 0.0 to 1.0 (e.g., 0.1 = 10% of volume)
        duration_minutes: int = 60
    ) -> AdvancedOrder:
        """
        Execute Percentage of Volume order
        Trades at specified percentage of market volume
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            total_quantity: Total quantity
            target_pov: Target percentage of volume (0.0-1.0)
            duration_minutes: Maximum duration
            
        Returns:
            Advanced order object
        """
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            order = AdvancedOrder(
                order_id=self._generate_order_id(),
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                order_type=OrderType.POV,
                start_time=start_time,
                end_time=end_time,
                pov_target_percentage=target_pov,
                slices=[]
            )
            
            self.active_orders[order.order_id] = order
            
            logger.info(f"📊 Executing POV order: {total_quantity} {symbol} @ {target_pov:.1%} of volume")
            
            # Execute based on market volume
            check_interval = 60  # Check every minute
            remaining = total_quantity
            
            while remaining > 0 and datetime.utcnow() < end_time and order.status != 'cancelled':
                # Get current market volume (simulated)
                market_volume = await self._get_market_volume(symbol, check_interval)
                
                # Calculate slice size
                slice_quantity = min(market_volume * target_pov, remaining)
                
                if slice_quantity > 0:
                    slice_result = await self._execute_slice(
                        order,
                        slice_quantity,
                        f"POV slice (market vol: {market_volume:.0f})"
                    )
                    
                    order.slices.append(slice_result)
                    order.filled_quantity += slice_result['filled_quantity']
                    remaining -= slice_result['filled_quantity']
                    
                    if order.filled_quantity > 0:
                        order.average_fill_price = (
                            (order.average_fill_price * (order.filled_quantity - slice_result['filled_quantity']) +
                             slice_result['fill_price'] * slice_result['filled_quantity']) /
                            order.filled_quantity
                        )
                    
                    logger.info(f"   ✅ Executed {slice_result['filled_quantity']:.4f}, Remaining: {remaining:.4f}")
                
                # Wait for next interval
                await asyncio.sleep(check_interval)
            
            order.status = 'completed'
            self.execution_stats['completed_orders'] += 1
            
            logger.info(f"✅ POV order complete: {order.filled_quantity:.4f} @ avg {order.average_fill_price:.2f}")
            
            return order
            
        except Exception as e:
            logger.error(f"Error executing POV order: {e}")
            if 'order' in locals():
                order.status = 'error'
            raise
    
    async def _execute_slice(
        self,
        order: AdvancedOrder,
        quantity: float,
        description: str,
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Execute a single order slice"""
        try:
            # Simulate market order execution
            await asyncio.sleep(0.1)  # Network delay
            
            # Simulate fill price with slippage
            base_price = 100.0  # Simulated market price
            slippage = np.random.uniform(-0.001, 0.001)  # ±0.1% slippage
            fill_price = base_price * (1 + slippage)
            
            if limit_price is not None:
                if order.side == 'buy' and fill_price > limit_price:
                    fill_price = limit_price
                elif order.side == 'sell' and fill_price < limit_price:
                    fill_price = limit_price
            
            return {
                'slice_id': self._generate_order_id(),
                'description': description,
                'quantity': quantity,
                'filled_quantity': quantity,
                'fill_price': fill_price,
                'timestamp': datetime.utcnow().isoformat(),
                'slippage': slippage
            }
            
        except Exception as e:
            logger.error(f"Error executing slice: {e}")
            return {
                'slice_id': 'error',
                'quantity': quantity,
                'filled_quantity': 0.0,
                'fill_price': 0.0,
                'error': str(e)
            }
    
    async def _get_market_volume(self, symbol: str, window_seconds: int) -> float:
        """Get market volume over time window"""
        # Simulated - in production, get actual market volume
        base_volume = 10000.0
        variation = np.random.uniform(0.8, 1.2)
        return base_volume * variation
    
    def _generate_u_shaped_profile(self, intervals: int) -> List[float]:
        """Generate U-shaped volume profile (high at open/close)"""
        profile = []
        for i in range(intervals):
            # U-shape: higher at start and end
            x = i / (intervals - 1) if intervals > 1 else 0.5
            y = (x - 0.5) ** 2 * 4 + 0.5  # Parabola
            profile.append(y)
        
        return profile
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import hashlib
        import time
        return f"ADV_{int(time.time() * 1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an active order"""
        if order_id in self.active_orders:
            self.active_orders[order_id].status = 'cancelled'
            self.execution_stats['cancelled_orders'] += 1
            logger.info(f"🛑 Cancelled order: {order_id}")
            return True
        return False
    
    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order status"""
        if order_id not in self.active_orders:
            return None
        
        order = self.active_orders[order_id]
        
        return {
            'order_id': order.order_id,
            'symbol': order.symbol,
            'side': order.side,
            'order_type': order.order_type.value,
            'total_quantity': order.total_quantity,
            'filled_quantity': order.filled_quantity,
            'average_fill_price': order.average_fill_price,
            'status': order.status,
            'slices_executed': len(order.slices) if order.slices else 0,
            'start_time': order.start_time.isoformat(),
            'end_time': order.end_time.isoformat()
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            **self.execution_stats,
            'active_orders': len([o for o in self.active_orders.values() if o.status == 'pending']),
            'completed_orders': len([o for o in self.active_orders.values() if o.status == 'completed'])
        }


# Global instance
_advanced_order_executor = None

def get_advanced_order_executor() -> AdvancedOrderExecutor:
    """Get or create global advanced order executor"""
    global _advanced_order_executor
    if _advanced_order_executor is None:
        _advanced_order_executor = AdvancedOrderExecutor()
    return _advanced_order_executor
