"""
IB Execution Performance Tracker
Integrates with existing PROMETHEUS performance monitoring infrastructure
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import statistics

logger = logging.getLogger(__name__)

@dataclass
class IBExecutionMetric:
    """IB-specific execution metric"""
    timestamp: datetime
    order_id: str
    symbol: str
    side: str
    quantity: int
    order_type: str
    submission_time: float
    fill_time: Optional[float] = None
    fill_price: Optional[float] = None
    expected_price: Optional[float] = None
    slippage: Optional[float] = None
    execution_latency: Optional[float] = None
    status: str = "submitted"

@dataclass
class IBConnectionMetric:
    """IB connection health metric"""
    timestamp: datetime
    connected: bool
    retry_count: int
    last_health_check: Optional[float]
    error_code: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class IBSessionPerformance:
    """IB session performance summary"""
    session_type: str  # overnight, pre_market, regular, after_hours
    start_time: datetime
    end_time: Optional[datetime]
    total_orders: int
    filled_orders: int
    cancelled_orders: int
    total_volume: float
    total_pnl: float
    avg_execution_latency: float
    avg_slippage: float
    connection_uptime: float

class IBExecutionTracker:
    """IB-specific execution performance tracker that integrates with existing monitoring"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        
        # Execution tracking
        self.executions: deque = deque(maxlen=max_samples)
        self.connection_metrics: deque = deque(maxlen=max_samples)
        self.session_performance: Dict[str, IBSessionPerformance] = {}
        
        # Performance calculations
        self.latency_buffer = deque(maxlen=100)
        self.slippage_buffer = deque(maxlen=100)
        self.fill_rate_buffer = deque(maxlen=50)
        
        # Integration with existing monitoring
        self._integrate_with_existing_monitoring()
        
        logger.info("IB Execution Tracker initialized")
    
    def _integrate_with_existing_monitoring(self):
        """Integrate with existing performance monitoring infrastructure"""
        try:
            # Import existing performance monitor
            from services.performance_monitor import performance_monitor
            self.existing_monitor = performance_monitor
            logger.info("✅ Integrated with existing performance monitoring")
        except ImportError:
            logger.warning("⚠️ Existing performance monitor not available - running standalone")
            self.existing_monitor = None
    
    def record_order_submission(self, order_id: str, symbol: str, side: str, 
                              quantity: int, order_type: str, expected_price: Optional[float] = None):
        """Record order submission for latency tracking"""
        metric = IBExecutionMetric(
            timestamp=datetime.now(),
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            submission_time=time.time(),
            expected_price=expected_price,
            status="submitted"
        )
        
        self.executions.append(metric)
        
        # Record in existing monitoring if available
        if self.existing_monitor:
            self.existing_monitor.record_metric("ib_order_submission", 1.0)
        
        logger.debug(f"📋 IB Order submitted: {order_id} - {symbol} {side} {quantity}")
    
    def record_order_fill(self, order_id: str, fill_price: float, fill_time: Optional[float] = None):
        """Record order fill and calculate execution metrics"""
        if fill_time is None:
            fill_time = time.time()
        
        # Find the corresponding submission
        for execution in self.executions:
            if execution.order_id == order_id and execution.status == "submitted":
                execution.fill_time = fill_time
                execution.fill_price = fill_price
                execution.status = "filled"
                
                # Calculate execution latency
                execution.execution_latency = fill_time - execution.submission_time
                self.latency_buffer.append(execution.execution_latency)
                
                # Calculate slippage if expected price available
                if execution.expected_price:
                    execution.slippage = abs(fill_price - execution.expected_price)
                    self.slippage_buffer.append(execution.slippage)
                
                # Record in existing monitoring
                if self.existing_monitor:
                    self.existing_monitor.record_metric("ib_execution_latency", execution.execution_latency)
                    if execution.slippage:
                        self.existing_monitor.record_metric("ib_slippage", execution.slippage)
                
                logger.info(f"✅ IB Order filled: {order_id} @ ${fill_price:.2f} (latency: {execution.execution_latency:.3f}s)")
                break
    
    def record_order_cancellation(self, order_id: str):
        """Record order cancellation"""
        for execution in self.executions:
            if execution.order_id == order_id and execution.status == "submitted":
                execution.status = "cancelled"
                logger.info(f"❌ IB Order cancelled: {order_id}")
                break
    
    def record_connection_event(self, connected: bool, retry_count: int = 0, 
                              error_code: Optional[int] = None, error_message: Optional[str] = None):
        """Record IB connection events"""
        metric = IBConnectionMetric(
            timestamp=datetime.now(),
            connected=connected,
            retry_count=retry_count,
            last_health_check=time.time(),
            error_code=error_code,
            error_message=error_message
        )
        
        self.connection_metrics.append(metric)
        
        # Record in existing monitoring
        if self.existing_monitor:
            self.existing_monitor.record_metric("ib_connection_status", 1.0 if connected else 0.0)
            if retry_count > 0:
                self.existing_monitor.record_metric("ib_connection_retries", retry_count)
    
    def get_execution_metrics(self, minutes: int = 60) -> Dict[str, Any]:
        """Get execution performance metrics for the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        
        # Filter recent executions
        recent_executions = [
            exec for exec in self.executions
            if exec.submission_time >= cutoff_time
        ]
        
        if not recent_executions:
            return {
                "total_orders": 0,
                "filled_orders": 0,
                "cancelled_orders": 0,
                "fill_rate": 0.0,
                "avg_execution_latency": 0.0,
                "avg_slippage": 0.0,
                "total_volume": 0.0
            }
        
        # Calculate metrics
        total_orders = len(recent_executions)
        filled_orders = len([e for e in recent_executions if e.status == "filled"])
        cancelled_orders = len([e for e in recent_executions if e.status == "cancelled"])
        fill_rate = (filled_orders / total_orders) * 100 if total_orders > 0 else 0.0
        
        # Calculate average latency
        latencies = [e.execution_latency for e in recent_executions if e.execution_latency]
        avg_latency = statistics.mean(latencies) if latencies else 0.0
        
        # Calculate average slippage
        slippages = [e.slippage for e in recent_executions if e.slippage]
        avg_slippage = statistics.mean(slippages) if slippages else 0.0
        
        # Calculate total volume
        total_volume = sum(e.quantity * (e.fill_price or 0) for e in recent_executions if e.fill_price)
        
        return {
            "total_orders": total_orders,
            "filled_orders": filled_orders,
            "cancelled_orders": cancelled_orders,
            "fill_rate": fill_rate,
            "avg_execution_latency": avg_latency,
            "avg_slippage": avg_slippage,
            "total_volume": total_volume,
            "timeframe_minutes": minutes
        }
    
    def get_connection_health(self, minutes: int = 60) -> Dict[str, Any]:
        """Get connection health metrics"""
        cutoff_time = time.time() - (minutes * 60)
        
        recent_connections = [
            conn for conn in self.connection_metrics
            if conn.timestamp.timestamp() >= cutoff_time
        ]
        
        if not recent_connections:
            return {
                "uptime_percentage": 0.0,
                "total_retries": 0,
                "last_connection_status": "unknown",
                "connection_events": 0
            }
        
        # Calculate uptime
        connected_events = len([c for c in recent_connections if c.connected])
        total_events = len(recent_connections)
        uptime_percentage = (connected_events / total_events) * 100 if total_events > 0 else 0.0
        
        # Get retry count
        total_retries = sum(c.retry_count for c in recent_connections)
        
        # Last connection status
        last_connection = recent_connections[-1] if recent_connections else None
        last_status = "connected" if last_connection and last_connection.connected else "disconnected"
        
        return {
            "uptime_percentage": uptime_percentage,
            "total_retries": total_retries,
            "last_connection_status": last_status,
            "connection_events": total_events,
            "timeframe_minutes": minutes
        }
    
    def get_session_performance(self, session_type: str) -> Optional[IBSessionPerformance]:
        """Get performance metrics for a specific trading session"""
        return self.session_performance.get(session_type)
    
    def start_session_tracking(self, session_type: str):
        """Start tracking a new trading session"""
        self.session_performance[session_type] = IBSessionPerformance(
            session_type=session_type,
            start_time=datetime.now(),
            end_time=None,
            total_orders=0,
            filled_orders=0,
            cancelled_orders=0,
            total_volume=0.0,
            total_pnl=0.0,
            avg_execution_latency=0.0,
            avg_slippage=0.0,
            connection_uptime=0.0
        )
        logger.info(f"🎯 Started tracking {session_type} session")
    
    def end_session_tracking(self, session_type: str):
        """End tracking for a trading session and calculate final metrics"""
        if session_type not in self.session_performance:
            return
        
        session = self.session_performance[session_type]
        session.end_time = datetime.now()
        
        # Calculate session metrics
        session_metrics = self.get_execution_metrics(minutes=1440)  # 24 hours
        connection_health = self.get_connection_health(minutes=1440)
        
        session.total_orders = session_metrics["total_orders"]
        session.filled_orders = session_metrics["filled_orders"]
        session.cancelled_orders = session_metrics["cancelled_orders"]
        session.total_volume = session_metrics["total_volume"]
        session.avg_execution_latency = session_metrics["avg_execution_latency"]
        session.avg_slippage = session_metrics["avg_slippage"]
        session.connection_uptime = connection_health["uptime_percentage"]
        
        logger.info(f"📊 {session_type} session completed:")
        logger.info(f"   Orders: {session.total_orders} (filled: {session.filled_orders})")
        logger.info(f"   Volume: ${session.total_volume:.2f}")
        logger.info(f"   Avg Latency: {session.avg_execution_latency:.3f}s")
        logger.info(f"   Uptime: {session.connection_uptime:.1f}%")
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive IB performance report"""
        execution_metrics = self.get_execution_metrics(minutes=60)
        connection_health = self.get_connection_health(minutes=60)
        
        # Get session summaries
        session_summaries = {}
        for session_type, session in self.session_performance.items():
            session_summaries[session_type] = asdict(session)
        
        return {
            "execution_performance": execution_metrics,
            "connection_health": connection_health,
            "session_performance": session_summaries,
            "total_tracked_executions": len(self.executions),
            "total_connection_events": len(self.connection_metrics),
            "timestamp": datetime.now().isoformat()
        }

# Global IB execution tracker instance
ib_execution_tracker = IBExecutionTracker()

# Convenience functions for integration
def track_ib_order_submission(order_id: str, symbol: str, side: str, quantity: int, order_type: str, expected_price: Optional[float] = None):
    """Track IB order submission"""
    ib_execution_tracker.record_order_submission(order_id, symbol, side, quantity, order_type, expected_price)

def track_ib_order_fill(order_id: str, fill_price: float, fill_time: Optional[float] = None):
    """Track IB order fill"""
    ib_execution_tracker.record_order_fill(order_id, fill_price, fill_time)

def track_ib_connection_event(connected: bool, retry_count: int = 0, error_code: Optional[int] = None, error_message: Optional[str] = None):
    """Track IB connection event"""
    ib_execution_tracker.record_connection_event(connected, retry_count, error_code, error_message)

def get_ib_performance_report() -> Dict[str, Any]:
    """Get comprehensive IB performance report"""
    return ib_execution_tracker.get_comprehensive_report()
