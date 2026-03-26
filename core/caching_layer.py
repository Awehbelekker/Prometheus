"""
Advanced Caching Layer Implementation
Provides Redis-based distributed caching with intelligent invalidation
"""

import redis
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
from dataclasses import dataclass
import pickle

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuration for cache settings"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    default_ttl: int = 3600  # 1 hour
    key_prefix: str = "mass_framework:"

class DistributedCache:
    """
    High-performance distributed caching with Redis backend
    Supports intelligent invalidation and cache warming
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client = None
        self.connection_pool = None
        self._initialize_redis()
        
    def _initialize_redis(self):
        """Initialize Redis connection with pool"""
        try:
            self.connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis connection established at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to memory cache: {str(e)}")
            self.redis_client = None
            self._memory_cache = {}
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate standardized cache key"""
        return f"{self.config.key_prefix}{namespace}:{key}"
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for cache storage"""
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=str)
            else:
                return pickle.dumps(data).hex()
        except Exception as e:
            logger.error(f"Serialization error: {str(e)}")
            return json.dumps({"error": "serialization_failed"})
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from cache"""
        try:
            # Try JSON first
            return json.loads(data)
        except json.JSONDecodeError:
            try:
                # Try pickle for complex objects
                return pickle.loads(bytes.fromhex(data))
            except Exception as e:
                logger.error(f"Deserialization error: {str(e)}")
                return None
    
    async def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value with optional TTL"""
        cache_key = self._generate_key(namespace, key)
        serialized_value = self._serialize_data(value)
        ttl = ttl or self.config.default_ttl
        
        try:
            if self.redis_client:
                result = self.redis_client.setex(cache_key, ttl, serialized_value)
                logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
                return result
            else:
                # Fallback to memory cache
                self._memory_cache[cache_key] = {
                    'value': serialized_value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
                return True
                
        except Exception as e:
            logger.error(f"Cache SET error for {cache_key}: {str(e)}")
            return False
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get cache value"""
        cache_key = self._generate_key(namespace, key)
        
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return self._deserialize_data(cached_data)
                else:
                    logger.debug(f"Cache MISS: {cache_key}")
                    return None
            else:
                # Fallback to memory cache
                cached_item = self._memory_cache.get(cache_key)
                if cached_item and cached_item['expires'] > datetime.now():
                    return self._deserialize_data(cached_item['value'])
                elif cached_item:
                    # Expired, remove it
                    del self._memory_cache[cache_key]
                return None
                
        except Exception as e:
            logger.error(f"Cache GET error for {cache_key}: {str(e)}")
            return None
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete cache key"""
        cache_key = self._generate_key(namespace, key)
        
        try:
            if self.redis_client:
                result = self.redis_client.delete(cache_key)
                logger.debug(f"Cache DELETE: {cache_key}")
                return bool(result)
            else:
                # Fallback to memory cache
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache DELETE error for {cache_key}: {str(e)}")
            return False
    
    async def invalidate_pattern(self, namespace: str, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            if self.redis_client:
                search_pattern = self._generate_key(namespace, pattern)
                keys = self.redis_client.keys(search_pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"Cache INVALIDATE: {deleted} keys matching {search_pattern}")
                    return deleted
                return 0
            else:
                # Fallback to memory cache
                search_key = self._generate_key(namespace, "")
                deleted = 0
                keys_to_delete = []
                for key in self._memory_cache.keys():
                    if key.startswith(search_key) and pattern in key:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self._memory_cache[key]
                    deleted += 1
                
                return deleted
                
        except Exception as e:
            logger.error(f"Cache INVALIDATE error for {namespace}:{pattern}: {str(e)}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    "backend": "redis",
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B"),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "hit_rate": self._calculate_hit_rate(info)
                }
            else:
                return {
                    "backend": "memory",
                    "total_keys": len(self._memory_cache),
                    "estimated_size": sum(len(str(v)) for v in self._memory_cache.values())
                }
                
        except Exception as e:
            logger.error(f"Cache STATS error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


class AgentConfigCache(DistributedCache):
    """
    Specialized cache for agent configurations with intelligent invalidation
    """
    
    NAMESPACE = "agent_configs"
    
    async def cache_agent_config(self, agent_id: str, config: Dict[str, Any], ttl: int = 7200):
        """Cache agent configuration with 2-hour default TTL"""
        return await self.set(self.NAMESPACE, agent_id, config, ttl)
    
    async def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get cached agent configuration"""
        return await self.get(self.NAMESPACE, agent_id)
    
    async def invalidate_agent_config(self, agent_id: str) -> bool:
        """Invalidate specific agent configuration"""
        return await self.delete(self.NAMESPACE, agent_id)
    
    async def invalidate_all_agents(self) -> int:
        """Invalidate all agent configurations"""
        return await self.invalidate_pattern(self.NAMESPACE, "*")
    
    async def warm_cache(self, agent_configs: Dict[str, Dict[str, Any]]):
        """Pre-warm cache with agent configurations"""
        success_count = 0
        for agent_id, config in agent_configs.items():
            if await self.cache_agent_config(agent_id, config):
                success_count += 1
        
        logger.info(f"Cache warmed: {success_count}/{len(agent_configs)} agent configs")
        return success_count


class WorkflowCache(DistributedCache):
    """
    Specialized cache for workflow results and intermediate states
    """
    
    NAMESPACE = "workflows"
    
    async def cache_workflow_result(self, workflow_id: str, result: Dict[str, Any], ttl: int = 3600):
        """Cache workflow execution result"""
        return await self.set(self.NAMESPACE, f"result:{workflow_id}", result, ttl)
    
    async def get_workflow_result(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get cached workflow result"""
        return await self.get(self.NAMESPACE, f"result:{workflow_id}")
    
    async def cache_workflow_state(self, workflow_id: str, state: Dict[str, Any], ttl: int = 1800):
        """Cache intermediate workflow state"""
        return await self.set(self.NAMESPACE, f"state:{workflow_id}", state, ttl)
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get cached workflow state"""
        return await self.get(self.NAMESPACE, f"state:{workflow_id}")
    
    async def invalidate_workflow(self, workflow_id: str) -> int:
        """Invalidate all cached data for a workflow"""
        return await self.invalidate_pattern(self.NAMESPACE, f"*:{workflow_id}")


# Global cache instances
cache_config = CacheConfig()
distributed_cache = DistributedCache(cache_config)
agent_cache = AgentConfigCache(cache_config)
workflow_cache = WorkflowCache(cache_config)


@asynccontextmanager
async def cache_context():
    """Context manager for cache operations"""
    try:
        yield {
            'distributed': distributed_cache,
            'agents': agent_cache,
            'workflows': workflow_cache
        }
    finally:
        # Cleanup if needed
        pass


def cache_decorator(namespace: str, key_func: callable = None, ttl: int = 3600):
    """
    Decorator for automatic caching of function results
    
    Args:
        namespace: Cache namespace
        key_func: Function to generate cache key from args
        ttl: Time to live in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                args_str = "_".join(str(arg) for arg in args)
                kwargs_str = "_".join(f"{k}={v}" for k, v in kwargs.items())
                cache_key = f"{func.__name__}:{args_str}:{kwargs_str}"
            
            # Try to get from cache
            cached_result = await distributed_cache.get(namespace, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await distributed_cache.set(namespace, cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Example usage decorators
def cache_agent_operation(ttl: int = 3600):
    """Cache agent operation results"""
    return cache_decorator("agent_ops", ttl=ttl)


def cache_workflow_step(ttl: int = 1800):
    """Cache workflow step results"""
    return cache_decorator("workflow_steps", ttl=ttl)
