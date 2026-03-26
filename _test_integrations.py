"""Test all Phase 21 integrations."""
import sys, os, warnings
warnings.filterwarnings("ignore")
os.chdir(r'c:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform')
sys.path.insert(0, '.')

results = {}

# 1. LangGraph
try:
    from core.langgraph_trading_orchestrator import LangGraphTradingOrchestrator
    lg = LangGraphTradingOrchestrator()
    has_graph = lg.graph is not None if hasattr(lg, 'graph') else 'no attr'
    results['LangGraph'] = f'OK (graph={has_graph})'
except Exception as e:
    results['LangGraph'] = f'FAIL: {e}'

# 2. OpenBB
try:
    from core.openbb_data_provider import OpenBBDataProvider
    obb = OpenBBDataProvider()
    results['OpenBB'] = f'OK (available={getattr(obb, "available", True)})'
except Exception as e:
    results['OpenBB'] = f'FAIL: {e}'

# 3. CCXT
try:
    from core.ccxt_exchange_bridge import CCXTExchangeBridge
    ccxt_b = CCXTExchangeBridge()
    exch = list(ccxt_b.exchanges.keys()) if hasattr(ccxt_b, 'exchanges') else '?'
    results['CCXT'] = f'OK (exchanges={exch})'
except Exception as e:
    results['CCXT'] = f'FAIL: {e}'

# 4. Gymnasium/SB3
try:
    from core.gymnasium_trading_env import TradingGymEnv, SB3TradingAgent
    results['Gymnasium_SB3'] = 'OK'
except Exception as e:
    results['Gymnasium_SB3'] = f'FAIL: {e}'

# 5. Mercury2
try:
    from core.mercury2_adapter import Mercury2Adapter
    m2 = Mercury2Adapter()
    results['Mercury2'] = f'OK (available={m2.is_available()})'
except Exception as e:
    results['Mercury2'] = f'FAIL: {e}'

# 6. Redis Cache
try:
    from core.redis_cache import get_cache
    cache = get_cache()
    backend = "Redis" if cache.use_redis else "TTLCache"
    results['Cache'] = f'OK (backend={backend})'
except Exception as e:
    results['Cache'] = f'FAIL: {e}'

print("=" * 60)
print("PHASE 21 INTEGRATION TEST")
print("=" * 60)
for k, v in results.items():
    status = "PASS" if v.startswith("OK") else "FAIL"
    print(f"  [{status}] {k}: {v}")
ok = sum(1 for v in results.values() if v.startswith("OK"))
print(f"\nResult: {ok}/6 integrations working")
