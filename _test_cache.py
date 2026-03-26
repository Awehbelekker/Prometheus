from core.redis_cache import get_cache
c = get_cache()
c.cache_price("AAPL", {"p": 150})
print("backend:", c.get_stats()["backend"])
print("price:", c.get_price("AAPL"))
print("stats:", c.get_stats())
