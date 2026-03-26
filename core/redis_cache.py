"""
Redis Cache Layer for PROMETHEUS
Provides a unified caching interface with Redis (if available) or falls back
to in-memory TTLCache.

Features:
  - Transparent fallback: Redis down? → in-memory cache, zero code changes
  - JSON serialization for complex objects
  - TTL-based expiration
  - Pub/sub for real-time price broadcasting
  - Market data, AI response, and signal caching

Usage:
    from core.redis_cache import get_cache
    cache = get_cache()
    cache.set("price:AAPL", {"price": 150.25, "ts": "..."}, ttl=60)
    data = cache.get("price:AAPL")
"""

import os
import json
import logging
import time
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

# In-memory fallback
from cachetools import TTLCache

REDIS_AVAILABLE = False
_redis_client = None


def _init_redis():
    """Try to connect to Redis server."""
    global REDIS_AVAILABLE, _redis_client
    try:
        import redis
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        password = os.getenv("REDIS_PASSWORD", None)

        client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=2,
            socket_connect_timeout=2,
            decode_responses=True,
        )
        client.ping()
        _redis_client = client
        REDIS_AVAILABLE = True
        logger.info(f"Redis connected: {host}:{port}/db{db}")
    except Exception as e:
        REDIS_AVAILABLE = False
        _redis_client = None
        logger.info(f"Redis not available ({e}) — using in-memory TTLCache fallback")


# Try to connect at module load
_init_redis()


class PrometheusCache:
    """
    Unified cache with Redis backend + in-memory fallback.

    Namespaces:
      - price:{symbol}     — real-time price data (TTL 30s)
      - ai:{symbol}        — AI analysis results (TTL 300s)
      - signal:{symbol}    — trading signals (TTL 120s)
      - market:{key}       — general market data (TTL 60s)
      - meta:{key}         — metadata (TTL 3600s)
    """

    DEFAULT_TTLS = {
        "price": 30,
        "ai": 300,
        "signal": 120,
        "market": 60,
        "meta": 3600,
    }

    def __init__(self):
        self.redis = _redis_client
        self.use_redis = REDIS_AVAILABLE

        # In-memory fallback caches (one per namespace)
        self._memory_caches: Dict[str, TTLCache] = {
            "price": TTLCache(maxsize=2000, ttl=30),
            "ai": TTLCache(maxsize=500, ttl=300),
            "signal": TTLCache(maxsize=1000, ttl=120),
            "market": TTLCache(maxsize=1000, ttl=60),
            "meta": TTLCache(maxsize=200, ttl=3600),
            "default": TTLCache(maxsize=1000, ttl=300),
        }

        # Stats
        self.hits = 0
        self.misses = 0
        self.sets = 0

    def _namespace(self, key: str) -> str:
        """Extract namespace from key like 'price:AAPL' → 'price'."""
        if ":" in key:
            return key.split(":")[0]
        return "default"

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value. Automatically serializes dicts/lists to JSON.
        TTL defaults based on namespace if not specified.
        """
        ns = self._namespace(key)
        if ttl is None:
            ttl = self.DEFAULT_TTLS.get(ns, 300)

        self.sets += 1

        if self.use_redis and self.redis:
            try:
                serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                self.redis.setex(key, ttl, serialized)
                return True
            except Exception as e:
                logger.debug(f"Redis set failed for {key}: {e}")
                # Fall through to memory

        # In-memory fallback
        cache = self._memory_caches.get(ns, self._memory_caches["default"])
        cache[key] = value
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value. Automatically deserializes JSON strings.
        """
        if self.use_redis and self.redis:
            try:
                raw = self.redis.get(key)
                if raw is not None:
                    self.hits += 1
                    try:
                        return json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        return raw
                self.misses += 1
                return default
            except Exception as e:
                logger.debug(f"Redis get failed for {key}: {e}")

        # In-memory fallback
        ns = self._namespace(key)
        cache = self._memory_caches.get(ns, self._memory_caches["default"])
        val = cache.get(key)
        if val is not None:
            self.hits += 1
            return val
        self.misses += 1
        return default

    def delete(self, key: str) -> bool:
        """Delete a key."""
        if self.use_redis and self.redis:
            try:
                self.redis.delete(key)
                return True
            except Exception:
                pass

        ns = self._namespace(key)
        cache = self._memory_caches.get(ns, self._memory_caches["default"])
        cache.pop(key, None)
        return True

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self.use_redis and self.redis:
            try:
                return bool(self.redis.exists(key))
            except Exception:
                pass

        ns = self._namespace(key)
        cache = self._memory_caches.get(ns, self._memory_caches["default"])
        return key in cache

    # ------------------------------------------------------------------
    # Convenience methods for trading data
    # ------------------------------------------------------------------

    def cache_price(self, symbol: str, price_data: Dict[str, Any], ttl: int = 30) -> bool:
        """Cache real-time price data."""
        return self.set(f"price:{symbol}", price_data, ttl=ttl)

    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached price data."""
        return self.get(f"price:{symbol}")

    def cache_ai_analysis(self, symbol: str, analysis: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache AI analysis result (5 min default)."""
        return self.set(f"ai:{symbol}", analysis, ttl=ttl)

    def get_ai_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached AI analysis."""
        return self.get(f"ai:{symbol}")

    def cache_signal(self, symbol: str, signal: Dict[str, Any], ttl: int = 120) -> bool:
        """Cache a trading signal."""
        return self.set(f"signal:{symbol}", signal, ttl=ttl)

    def get_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached signal."""
        return self.get(f"signal:{symbol}")

    # ------------------------------------------------------------------
    # Pub/Sub (Redis only — no-op without Redis)
    # ------------------------------------------------------------------

    def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a Redis channel (for real-time broadcasting)."""
        if self.use_redis and self.redis:
            try:
                self.redis.publish(channel, json.dumps(message))
                return True
            except Exception as e:
                logger.debug(f"Redis publish failed on {channel}: {e}")
        return False

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        hit_rate = round(self.hits / max(self.hits + self.misses, 1) * 100, 1)
        memory_items = sum(len(c) for c in self._memory_caches.values())

        stats = {
            "backend": "redis" if self.use_redis else "in-memory (TTLCache)",
            "redis_available": self.use_redis,
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "hit_rate_pct": hit_rate,
            "memory_items": memory_items,
        }

        if self.use_redis and self.redis:
            try:
                info = self.redis.info("keyspace")
                stats["redis_keys"] = sum(
                    db.get("keys", 0) for db in info.values() if isinstance(db, dict)
                )
            except Exception:
                pass

        return stats

    def flush_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        count = 0
        if self.use_redis and self.redis:
            try:
                keys = self.redis.keys(f"{namespace}:*")
                if keys:
                    count = self.redis.delete(*keys)
            except Exception:
                pass

        cache = self._memory_caches.get(namespace)
        if cache:
            mem_count = len(cache)
            cache.clear()
            count += mem_count

        return count


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------

_cache: Optional[PrometheusCache] = None


def get_cache() -> PrometheusCache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        _cache = PrometheusCache()
    return _cache
