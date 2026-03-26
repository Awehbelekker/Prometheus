"""
Enhanced Error Handling Framework for PROMETHEUS Trading Platform
Comprehensive error classification, recovery, and monitoring system
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    MARKET_DATA = "market_data"
    ORDER_EXECUTION = "order_execution"
    ACCOUNT_ACCESS = "account_access"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    SYSTEM = "system"

@dataclass
class ErrorContext:
    """Context information for errors"""
    broker: str
    operation: str
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.additional_data is None:
            self.additional_data = {}

class TradingError(Exception):
    """Base trading error with enhanced context"""
    
    def __init__(self, message: str, category: ErrorCategory, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[ErrorContext] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext(broker="unknown", operation="unknown")
        self.original_error = original_error
        self.timestamp = datetime.now()
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"ERR_{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging"""
        return {
            'error_id': self.error_id,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'context': asdict(self.context),
            'timestamp': self.timestamp.isoformat(),
            'original_error': str(self.original_error) if self.original_error else None,
            'traceback': traceback.format_exc() if self.original_error else None
        }

# Specific error types
class ConnectionError(TradingError):
    """Connection-related errors"""
    def __init__(self, message: str, broker: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.CONNECTION,
            severity=ErrorSeverity.HIGH,
            context=ErrorContext(broker=broker, operation="connect"),
            original_error=original_error
        )

class AuthenticationError(TradingError):
    """Authentication failures"""
    def __init__(self, message: str, broker: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.CRITICAL,
            context=ErrorContext(broker=broker, operation="authenticate"),
            original_error=original_error
        )

class MarketDataError(TradingError):
    """Market data issues"""
    def __init__(self, message: str, broker: str, symbol: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.MARKET_DATA,
            severity=ErrorSeverity.MEDIUM,
            context=ErrorContext(broker=broker, operation="get_market_data", symbol=symbol),
            original_error=original_error
        )

class OrderExecutionError(TradingError):
    """Order execution problems"""
    def __init__(self, message: str, broker: str, order_id: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.ORDER_EXECUTION,
            severity=ErrorSeverity.HIGH,
            context=ErrorContext(broker=broker, operation="submit_order", order_id=order_id),
            original_error=original_error
        )

class AccountAccessError(TradingError):
    """Account access issues"""
    def __init__(self, message: str, broker: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.ACCOUNT_ACCESS,
            severity=ErrorSeverity.HIGH,
            context=ErrorContext(broker=broker, operation="get_account"),
            original_error=original_error
        )

class RateLimitError(TradingError):
    """Rate limiting errors"""
    def __init__(self, message: str, broker: str, retry_after: Optional[int] = None, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            context=ErrorContext(broker=broker, operation="api_call", additional_data={'retry_after': retry_after}),
            original_error=original_error
        )

class ValidationError(TradingError):
    """Data validation errors"""
    def __init__(self, message: str, broker: str, operation: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context=ErrorContext(broker=broker, operation=operation),
            original_error=original_error
        )

class SystemError(TradingError):
    """System-level errors"""
    def __init__(self, message: str, operation: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            context=ErrorContext(broker="system", operation=operation),
            original_error=original_error
        )

class RetryStrategy:
    """Base retry strategy"""
    
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts - 1:
                    await self._wait_before_retry(attempt)
                else:
                    break
        
        raise last_error
    
    async def _wait_before_retry(self, attempt: int):
        """Wait before retry - to be implemented by subclasses"""
        pass

class ExponentialBackoffRetry(RetryStrategy):
    """Exponential backoff retry strategy"""
    
    def __init__(self, max_attempts: int = 5, base_delay: float = 1.0, max_delay: float = 60.0):
        super().__init__(max_attempts)
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def _wait_before_retry(self, attempt: int):
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        logger.info(f"Retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_attempts})")
        await asyncio.sleep(delay)

class ImmediateRetry(RetryStrategy):
    """Immediate retry strategy"""
    
    async def _wait_before_retry(self, attempt: int):
        await asyncio.sleep(0.1)  # Minimal delay

class NoRetry(RetryStrategy):
    """No retry strategy - fail immediately"""
    
    def __init__(self):
        super().__init__(1)

class ErrorRecoveryManager:
    """Manages error recovery strategies"""
    
    def __init__(self):
        self.retry_strategies = {
            ConnectionError: ExponentialBackoffRetry(max_attempts=5),
            AuthenticationError: NoRetry(),  # Don't retry auth errors
            MarketDataError: ImmediateRetry(max_attempts=3),
            OrderExecutionError: NoRetry(),  # Don't retry order errors
            AccountAccessError: ExponentialBackoffRetry(max_attempts=3),
            RateLimitError: ExponentialBackoffRetry(max_attempts=3, base_delay=2.0),
            ValidationError: NoRetry(),  # Don't retry validation errors
            SystemError: ExponentialBackoffRetry(max_attempts=3)
        }
    
    async def handle_error(self, error: TradingError, func: Callable, *args, **kwargs) -> Any:
        """Handle error with appropriate recovery strategy"""
        strategy = self.retry_strategies.get(type(error))
        
        if strategy and strategy.max_attempts > 1:
            logger.info(f"Attempting recovery for {type(error).__name__}: {error.message}")
            try:
                return await strategy.execute(func, *args, **kwargs)
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                raise error  # Re-raise original error if recovery fails
        else:
            logger.error(f"No recovery strategy for {type(error).__name__}: {error.message}")
            raise error

class ErrorLogger:
    """Enhanced error logging system"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "logs/trading_errors.jsonl"
        self.error_database = ErrorDatabase()
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def log_error(self, error: TradingError):
        """Log error with full context"""
        error_data = error.to_dict()
        
        # Log to file
        await self._log_to_file(error_data)
        
        # Store in database
        await self.error_database.store_error(error_data)
        
        # Log to standard logger
        logger.error(f"Trading Error [{error.error_id}]: {error.message}")
        
        # Send alerts for critical errors
        if error.severity == ErrorSeverity.CRITICAL:
            await self._send_critical_alert(error)
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Recursively convert objects to JSON-serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._make_json_serializable(item) for item in obj)
        elif hasattr(obj, 'isoformat'):  # Other datetime-like objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Custom objects
            return self._make_json_serializable(obj.__dict__)
        else:
            try:
                json.dumps(obj)  # Test if already serializable
                return obj
            except (TypeError, ValueError):
                return str(obj)  # Fallback to string representation
    
    async def _log_to_file(self, error_data: Dict[str, Any]):
        """Log error to JSONL file"""
        try:
            # Recursively convert all datetime objects to strings for JSON serialization
            serializable_data = self._make_json_serializable(error_data)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(serializable_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to log error to file: {e}")
    
    async def _send_critical_alert(self, error: TradingError):
        """Send critical error alert"""
        alert_message = f"""
🚨 CRITICAL TRADING ERROR 🚨
Error ID: {error.error_id}
Broker: {error.context.broker}
Operation: {error.context.operation}
Message: {error.message}
Time: {error.timestamp}
        """
        logger.critical(alert_message)
        # TODO: Integrate with notification system

class ErrorDatabase:
    """In-memory error database for analysis"""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.max_errors = 10000  # Keep last 10k errors
    
    async def store_error(self, error_data: Dict[str, Any]):
        """Store error in database"""
        self.errors.append(error_data)
        
        # Keep only recent errors
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
    
    def get_errors_by_broker(self, broker: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get errors by broker within time window"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            error for error in self.errors
            if error['context']['broker'] == broker and 
            datetime.fromisoformat(error['timestamp']) > cutoff
        ]
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in self.errors
            if datetime.fromisoformat(error['timestamp']) > cutoff
        ]
        
        if not recent_errors:
            return {
                'total_errors': 0,
                'error_by_type': {},
                'error_by_broker': {},
                'critical_errors': 0,
                'recovery_success_rate': 0.0
            }
        
        # Count by type
        error_by_type = {}
        error_by_broker = {}
        critical_count = 0
        
        for error in recent_errors:
            error_type = error['category']
            broker = error['context']['broker']
            severity = error['severity']
            
            error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
            error_by_broker[broker] = error_by_broker.get(broker, 0) + 1
            
            if severity == 'critical':
                critical_count += 1
        
        return {
            'total_errors': len(recent_errors),
            'error_by_type': error_by_type,
            'error_by_broker': error_by_broker,
            'critical_errors': critical_count,
            'recovery_success_rate': 0.0  # TODO: Calculate from recovery attempts
        }

class ErrorMonitoringDashboard:
    """Error monitoring and analytics dashboard"""
    
    def __init__(self, error_database: ErrorDatabase):
        self.error_database = error_database
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        summary = self.error_database.get_error_summary(hours)
        
        # Get recent critical errors
        recent_errors = self.error_database.errors[-50:]  # Last 50 errors
        
        return {
            'summary': summary,
            'recent_errors': recent_errors,
            'broker_health': self._get_broker_health(hours),
            'error_trends': self._get_error_trends(hours)
        }
    
    def _get_broker_health(self, hours: int) -> Dict[str, str]:
        """Get broker health status"""
        health = {}
        for broker in ['IB', 'Alpaca']:
            errors = self.error_database.get_errors_by_broker(broker, hours)
            critical_errors = [e for e in errors if e['severity'] == 'critical']
            
            if critical_errors:
                health[broker] = 'CRITICAL'
            elif len(errors) > 10:
                health[broker] = 'WARNING'
            elif len(errors) > 0:
                health[broker] = 'DEGRADED'
            else:
                health[broker] = 'HEALTHY'
        
        return health
    
    def _get_error_trends(self, hours: int) -> Dict[str, List[int]]:
        """Get error trends over time"""
        # TODO: Implement time-series error tracking
        return {'IB': [], 'Alpaca': []}

# Global error handling instances
error_logger = ErrorLogger()
error_recovery_manager = ErrorRecoveryManager()
error_database = ErrorDatabase()
error_monitoring = ErrorMonitoringDashboard(error_database)

def handle_trading_error(error: TradingError, func: Callable = None, *args, **kwargs):
    """Decorator for handling trading errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, TradingError):
                trading_error = e
            else:
                # Convert generic exception to TradingError
                trading_error = SystemError(
                    message=str(e),
                    operation=func.__name__ if func else "unknown",
                    original_error=e
                )
            
            # Log the error
            await error_logger.log_error(trading_error)
            
            # Attempt recovery if function provided
            if func and trading_error.severity != ErrorSeverity.CRITICAL:
                try:
                    return await error_recovery_manager.handle_error(trading_error, func, *args, **kwargs)
                except Exception:
                    pass  # Recovery failed, re-raise original error
            
            raise trading_error
    
    return wrapper

# Utility functions for common error scenarios
def create_connection_error(broker: str, original_error: Exception) -> ConnectionError:
    """Create connection error with context"""
    return ConnectionError(
        message=f"Failed to connect to {broker}: {str(original_error)}",
        broker=broker,
        original_error=original_error
    )

def create_market_data_error(broker: str, symbol: str, original_error: Exception) -> MarketDataError:
    """Create market data error with context"""
    return MarketDataError(
        message=f"Failed to get market data for {symbol} from {broker}: {str(original_error)}",
        broker=broker,
        symbol=symbol,
        original_error=original_error
    )

def create_order_execution_error(broker: str, order_id: str, original_error: Exception) -> OrderExecutionError:
    """Create order execution error with context"""
    return OrderExecutionError(
        message=f"Failed to execute order {order_id} on {broker}: {str(original_error)}",
        broker=broker,
        order_id=order_id,
        original_error=original_error
    )