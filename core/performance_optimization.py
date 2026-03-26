"""
Advanced Performance Optimizations for MASS Framework
Implements caching, connection pooling, and async optimizations
"""

import asyncio
import time
import redis
import pickle
import hashlib
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from functools import wraps
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuration for different cache types"""
    ttl: int  # Time to live in seconds
    max_size: int  # Maximum cache size
    prefix: str  # Cache key prefix

class AdvancedCacheManager:
    """
    Multi-layer caching system with Redis and in-memory fallback
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = None
        self.local_cache: Dict[str, tuple] = {}
        self.cache_configs = {
            'agent_responses': CacheConfig(ttl=600, max_size=1000, prefix='agent'),
            'market_data': CacheConfig(ttl=300, max_size=500, prefix='market'),
            'api_responses': CacheConfig(ttl=180, max_size=2000, prefix='api'),
            'user_sessions': CacheConfig(ttl=3600, max_size=10000, prefix='session'),
            'generated_code': CacheConfig(ttl=1800, max_size=100, prefix='code')
        }
        
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using local cache only: {e}")
    
    def _generate_key(self, cache_type: str, key: str) -> str:
        """Generate cache key with proper prefix"""
        config = self.cache_configs.get(cache_type, self.cache_configs['api_responses'])
        return f"{config.prefix}:{key}"
    
    async def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Get item from cache with fallback hierarchy"""
        cache_key = self._generate_key(cache_type, key)
        
        # Try Redis first
        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    return pickle.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Fallback to local cache
        if cache_key in self.local_cache:
            data, timestamp = self.local_cache[cache_key]
            config = self.cache_configs.get(cache_type, self.cache_configs['api_responses'])
            if time.time() - timestamp < config.ttl:
                return data
            else:
                del self.local_cache[cache_key]
        
        return None
    
    async def set(self, cache_type: str, key: str, value: Any) -> bool:
        """Set item in cache with proper TTL"""
        cache_key = self._generate_key(cache_type, key)
        config = self.cache_configs.get(cache_type, self.cache_configs['api_responses'])
        
        # Set in Redis
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    config.ttl, 
                    pickle.dumps(value)
                )
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Set in local cache (with size limit)
        if len(self.local_cache) >= config.max_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.local_cache.keys(), 
                key=lambda k: self.local_cache[k][1]
            )[:len(self.local_cache) - config.max_size + 1]
            for old_key in oldest_keys:
                del self.local_cache[old_key]
        
        self.local_cache[cache_key] = (value, time.time())
        return True
    
    async def invalidate(self, cache_type: str, pattern: str = "*") -> int:
        """Invalidate cache entries matching pattern"""
        count = 0
        cache_prefix = self.cache_configs.get(cache_type, self.cache_configs['api_responses']).prefix
        
        # Invalidate Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"{cache_prefix}:{pattern}")
                if keys:
                    count += self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis invalidate error: {e}")
        
        # Invalidate local cache
        to_delete = [
            key for key in self.local_cache.keys() 
            if key.startswith(f"{cache_prefix}:")
        ]
        for key in to_delete:
            del self.local_cache[key]
            count += 1
        
        return count

def cache_result(cache_type: str = 'api_responses', ttl: Optional[int] = None):
    """
    Decorator for caching function results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager:
                cached_result = await cache_manager.get(cache_type, cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            if cache_manager and result is not None:
                await cache_manager.set(cache_type, cache_key, result)
                logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator

class ConnectionPoolManager:
    """
    Manages database and API connection pools for optimal performance
    """
    
    def __init__(self):
        self.pools: Dict[str, Any] = {}
        self.pool_configs = {
            'database': {
                'min_size': 5,
                'max_size': 20,
                'max_queries': 50000,
                'max_inactive_connection_lifetime': 300
            },
            'api': {
                'connector_limit': 100,
                'limit_per_host': 30,
                'timeout': 30
            }
        }
    
    async def get_db_pool(self, database_url: str):
        """Get or create database connection pool"""
        if 'database' not in self.pools:
            try:
                import asyncpg
                self.pools['database'] = await asyncpg.create_pool(
                    database_url,
                    **self.pool_configs['database']
                )
                logger.info("Database connection pool created")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                return None
        
        return self.pools['database']
    
    async def get_http_session(self):
        """Get or create HTTP session with optimized settings"""
        if 'http' not in self.pools:
            try:
                import aiohttp
                connector = aiohttp.TCPConnector(
                    limit=self.pool_configs['api']['connector_limit'],
                    limit_per_host=self.pool_configs['api']['limit_per_host'],
                    enable_cleanup_closed=True
                )
                
                timeout = aiohttp.ClientTimeout(
                    total=self.pool_configs['api']['timeout']
                )
                
                self.pools['http'] = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                )
                logger.info("HTTP session pool created")
            except Exception as e:
                logger.error(f"Failed to create HTTP session: {e}")
                return None
        
        return self.pools['http']
    
    async def cleanup(self):
        """Clean up all connection pools"""
        for pool_name, pool in self.pools.items():
            try:
                if hasattr(pool, 'close'):
                    await pool.close()
                logger.info(f"Closed {pool_name} pool")
            except Exception as e:
                logger.error(f"Error closing {pool_name} pool: {e}")

class PerformanceOptimizer:
    """
    Main performance optimization coordinator
    """
    
    def __init__(self):
        self.cache_manager = AdvancedCacheManager()
        self.connection_manager = ConnectionPoolManager()
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'db_queries': 0,
            'avg_response_time': 0.0
        }
    
    async def initialize(self, database_url: str = None):
        """Initialize performance optimizations"""
        if database_url:
            await self.connection_manager.get_db_pool(database_url)
        
        await self.connection_manager.get_http_session()
        
        # Attach cache manager to cached functions
        for func in _cached_functions:
            func._cache_manager = self.cache_manager
        
        logger.info("Performance optimizer initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (
            self.metrics['cache_hits'] / total_requests * 100 
            if total_requests > 0 else 0
        )
        
        return {
            **self.metrics,
            'cache_hit_rate': cache_hit_rate,
            'total_requests': total_requests
        }
    
    async def optimize_agent_coordination(self, agents: List[Any], task: Dict[str, Any]) -> List[Any]:
        """
        Optimize agent coordination with parallel execution and caching
        """
        start_time = time.time()
        
        # Check if we have cached results for this exact task
        task_hash = hashlib.md5(str(task).encode()).hexdigest()
        cache_key = f"coordination:{task_hash}"
        
        cached_result = await self.cache_manager.get('agent_responses', cache_key)
        if cached_result:
            self.metrics['cache_hits'] += 1
            logger.info(f"Using cached coordination result for task {task_hash[:8]}")
            return cached_result
        
        self.metrics['cache_misses'] += 1
        
        # Execute agents in parallel with proper error handling
        async def execute_agent_safely(agent, task):
            try:
                return await agent.process_task(task)
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} failed: {e}")
                return {"error": str(e), "agent_id": agent.agent_id}
        
        # Run agents in parallel
        agent_tasks = [execute_agent_safely(agent, task) for agent in agents]
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Filter out exceptions and failed results
        valid_results = [
            result for result in results 
            if not isinstance(result, Exception) and "error" not in result
        ]
        
        # Cache successful results
        if valid_results:
            await self.cache_manager.set('agent_responses', cache_key, valid_results)
        
        # Update metrics
        execution_time = time.time() - start_time
        self.metrics['avg_response_time'] = (
            (self.metrics['avg_response_time'] * (total_requests - 1) + execution_time) 
            / total_requests if total_requests > 0 else execution_time
        )
        
        logger.info(f"Agent coordination completed in {execution_time:.2f}s")
        return valid_results
    
    async def preload_critical_data(self):
        """Preload frequently accessed data into cache"""
        logger.info("Preloading critical data...")
        
        # Preload common market data
        try:
            from data_sources.live_data_orchestrator import LiveDataOrchestrator
            orchestrator = LiveDataOrchestrator()
            
            # Common technology categories
            common_techs = ["python", "javascript", "react", "fastapi", "docker"]
            await orchestrator.get_technology_trends(common_techs)
            
            # Common app categories
            common_categories = ["productivity", "social", "ecommerce", "education"]
            for category in common_categories:
                await orchestrator.get_competitive_analysis(category)
            
            logger.info("Critical data preloaded successfully")
        except Exception as e:
            logger.warning(f"Failed to preload data: {e}")

# Global list to track cached functions
_cached_functions = []

def register_cached_function(func):
    """Register function for cache manager attachment"""
    _cached_functions.append(func)
    return func

# Global optimizer instance
performance_optimizer = PerformanceOptimizer()
