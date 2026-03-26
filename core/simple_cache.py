"""
PROMETHEUS Trading Platform - Simple Cache Configuration
In-memory caching for improved performance
"""

import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

class SimpleCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with TTL."""
        expiry = time.time() + (ttl or self.default_ttl)
        self.cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value."""
        if key not in self.cache:
            return default
        
        item = self.cache[key]
        if time.time() > item['expiry']:
            del self.cache[key]
            return default
        
        return item['value']
    
    def delete(self, key: str) -> None:
        """Delete cache key."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time > item['expiry']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)

# Global cache instance
cache = SimpleCache()

# Cache decorator
def cached(ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
