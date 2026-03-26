"""
Circuit Breaker Pattern Implementation for Resilient External API Calls
Provides automatic retry, exponential backoff, and fallback mechanisms
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random
import statistics
from contextlib import asynccontextmanager
import aiohttp
import json

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Request timeout in seconds
    max_retries: int = 3                # Maximum retry attempts
    base_delay: float = 1.0             # Base delay for exponential backoff
    max_delay: float = 60.0             # Maximum delay between retries
    jitter: bool = True                 # Add random jitter to delays

@dataclass
class RetryConfig:
    """Configuration for retry mechanism"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_status_codes: List[int] = field(default_factory=lambda: [408, 429, 500, 502, 503, 504])
    retryable_exceptions: List[type] = field(default_factory=lambda: [
        aiohttp.ClientTimeout,
        aiohttp.ClientConnectionError,
        aiohttp.ServerConnectionError
    ])

class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        
        # Metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.circuit_opens = 0
        self.response_times = []
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function call through the circuit breaker"""
        self.total_calls += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' moving to HALF_OPEN")
            else:
                self.failed_calls += 1
                raise CircuitBreakerError(f"Circuit breaker '{self.name}' is OPEN")
        
        # Execute the call
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record success
            self._record_success(duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_failure(e, duration)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _record_success(self, duration: float):
        """Record a successful call"""
        self.successful_calls += 1
        self.response_times.append(duration)
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _record_failure(self, error: Exception, duration: float):
        """Record a failed call"""
        self.failed_calls += 1
        self.response_times.append(duration)
        self.last_failure_time = time.time()
        
        if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
            self.failure_count += 1
            self.success_count = 0  # Reset success count
            
            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit breaker"""
        self.state = CircuitState.OPEN
        self.circuit_opens += 1
        logger.warning(f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures")
    
    def _close_circuit(self):
        """Close the circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' CLOSED")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            'name': self.name,
            'state': self.state.value,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0,
            'failure_count': self.failure_count,
            'circuit_opens': self.circuit_opens,
            'avg_response_time': statistics.mean(self.response_times[-100:]) if self.response_times else 0,
            'last_failure_time': self.last_failure_time
        }


class RetryMechanism:
    """
    Advanced retry mechanism with exponential backoff and jitter
    """
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    async def retry_call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    logger.debug(f"Non-retryable exception: {type(e).__name__}")
                    raise
                
                # Don't retry on last attempt
                if attempt == self.config.max_attempts - 1:
                    break
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s")
                
                await asyncio.sleep(delay)
        
        # All attempts failed
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if an exception should trigger a retry"""
        # Check by exception type
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Check HTTP status codes for aiohttp errors
        if hasattr(exception, 'status'):
            return exception.status in self.config.retryable_status_codes
        
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff"""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


class FallbackMechanism:
    """
    Fallback mechanism for when primary services fail
    """
    
    def __init__(self):
        self.fallback_handlers: Dict[str, Callable] = {}
        self.fallback_data: Dict[str, Any] = {}
    
    def register_fallback(self, service_name: str, handler: Callable):
        """Register a fallback handler for a service"""
        self.fallback_handlers[service_name] = handler
        logger.info(f"Registered fallback handler for service: {service_name}")
    
    def set_fallback_data(self, service_name: str, data: Any):
        """Set static fallback data for a service"""
        self.fallback_data[service_name] = data
        logger.info(f"Set fallback data for service: {service_name}")
    
    async def execute_fallback(self, service_name: str, *args, **kwargs) -> Any:
        """Execute fallback for a service"""
        # Try handler first
        if service_name in self.fallback_handlers:
            try:
                handler = self.fallback_handlers[service_name]
                return await handler(*args, **kwargs) if asyncio.iscoroutinefunction(handler) else handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback handler failed for {service_name}: {str(e)}")
        
        # Try static data
        if service_name in self.fallback_data:
            logger.info(f"Using fallback data for service: {service_name}")
            return self.fallback_data[service_name]
        
        # No fallback available
        raise Exception(f"No fallback available for service: {service_name}")


class ResilientApiClient:
    """
    Resilient API client with circuit breaker, retry, and fallback mechanisms
    """
    
    def __init__(self, 
                 base_url: str,
                 circuit_config: CircuitBreakerConfig = None,
                 retry_config: RetryConfig = None,
                 timeout: float = 30.0):
        
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # Initialize mechanisms
        self.circuit_breaker = CircuitBreaker(f"api_client_{base_url}", circuit_config)
        self.retry_mechanism = RetryMechanism(retry_config)
        self.fallback_mechanism = FallbackMechanism()
        
        # Session management
        self._session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request with resilience patterns"""
        return await self._make_request('GET', endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request with resilience patterns"""
        return await self._make_request('POST', endpoint, json=data, **kwargs)
    
    async def put(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request with resilience patterns"""
        return await self._make_request('PUT', endpoint, json=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request with resilience patterns"""
        return await self._make_request('DELETE', endpoint, **kwargs)
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with all resilience patterns"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        service_name = f"{method}:{endpoint}"
        
        try:
            # Execute through circuit breaker and retry mechanism
            return await self.circuit_breaker.call(
                self.retry_mechanism.retry_call,
                self._execute_request,
                method, url, **kwargs
            )
            
        except Exception as e:
            logger.error(f"All attempts failed for {method} {url}: {str(e)}")
            
            # Try fallback
            try:
                return await self.fallback_mechanism.execute_fallback(service_name, method, url, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                raise e  # Raise original exception
    
    async def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute the actual HTTP request"""
        if not self._session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        async with self._session.request(method, url, **kwargs) as response:
            # Check for HTTP errors
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_text
                )
            
            # Parse response
            try:
                return await response.json()
            except json.JSONDecodeError:
                return {'text': await response.text()}
    
    def register_fallback(self, endpoint: str, method: str, handler: Callable):
        """Register fallback for specific endpoint"""
        service_name = f"{method}:{endpoint}"
        self.fallback_mechanism.register_fallback(service_name, handler)
    
    def set_fallback_data(self, endpoint: str, method: str, data: Any):
        """Set fallback data for specific endpoint"""
        service_name = f"{method}:{endpoint}"
        self.fallback_mechanism.set_fallback_data(service_name, data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'base_url': self.base_url,
            'circuit_breaker': self.circuit_breaker.get_stats()
        }


class ServiceRegistry:
    """
    Registry for managing multiple resilient API clients
    """
    
    def __init__(self):
        self.clients: Dict[str, ResilientApiClient] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_service(self, 
                        name: str, 
                        base_url: str,
                        circuit_config: CircuitBreakerConfig = None,
                        retry_config: RetryConfig = None) -> ResilientApiClient:
        """Register a new service"""
        
        client = ResilientApiClient(base_url, circuit_config, retry_config)
        self.clients[name] = client
        self.circuit_breakers[name] = client.circuit_breaker
        
        logger.info(f"Registered service '{name}' at {base_url}")
        return client
    
    def get_client(self, name: str) -> Optional[ResilientApiClient]:
        """Get client for a service"""
        return self.clients.get(name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all services"""
        return {
            name: client.get_stats()
            for name, client in self.clients.items()
        }
    
    def get_health_status(self) -> Dict[str, str]:
        """Get health status of all services"""
        return {
            name: breaker.state.value
            for name, breaker in self.circuit_breakers.items()
        }


# Global service registry
service_registry = ServiceRegistry()

# Convenience functions
def register_service(name: str, base_url: str, **config):
    """Register a new resilient service"""
    return service_registry.register_service(name, base_url, **config)

def get_service_client(name: str) -> Optional[ResilientApiClient]:
    """Get client for a registered service"""
    return service_registry.get_client(name)

@asynccontextmanager
async def resilient_api_call(service_name: str, base_url: str = None):
    """Context manager for resilient API calls"""
    if base_url:
        # Temporary client
        async with ResilientApiClient(base_url) as client:
            yield client
    else:
        # Use registered service
        client = service_registry.get_client(service_name)
        if not client:
            raise ValueError(f"Service '{service_name}' not registered")
        yield client

# Example usage and setup
async def setup_default_services():
    """Setup default external services with resilience patterns"""
    
    # OpenAI API
    openai_config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
        timeout=60.0
    )
    openai_client = register_service("openai", "https://api.openai.com", circuit_config=openai_config)
    
    # Set fallback for OpenAI
    openai_client.set_fallback_data("chat/completions", "POST", {
        "choices": [{"message": {"content": "Service temporarily unavailable. Please try again later."}}]
    })
    
    # GitHub API
    github_config = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60
    )
    register_service("github", "https://api.github.com", circuit_config=github_config)
    
    logger.info("Default services registered with resilience patterns")

# Auto-setup on import
asyncio.create_task(setup_default_services()) if asyncio.get_event_loop().is_running() else None
