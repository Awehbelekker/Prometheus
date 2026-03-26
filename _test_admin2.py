"""Test admin endpoints after fix."""
import urllib.request
import json

print("=" * 60)
print("TESTING ADMIN ENDPOINTS (after catch-all fix)")
print("=" * 60)

# Test 1: /api/admin/full-status
print("\n[1] GET /api/admin/full-status")
try:
    req = urllib.request.urlopen("http://localhost:8000/api/admin/full-status", timeout=15)
    data = json.loads(req.read())
    print(f"  STATUS: {req.status}")
    print(f"  success: {data.get('success')}")
    print(f"  uptime: {data.get('uptime_seconds')}s")
    print(f"  live_exec: {data.get('live_execution_enabled')}")
    
    al = data.get("alpaca_live", {})
    print(f"  ALPACA LIVE: connected={al.get('connected')}, value=${al.get('account_value', 0):.2f}, positions={al.get('position_count', 0)}")
    
    ib = data.get("ib_broker", {})
    print(f"  IB BROKER: reachable={ib.get('port_reachable')}, status={ib.get('status')}")
    
    st = data.get("shadow_trading", {})
    print(f"  SHADOW: total_trades={st.get('total_shadow_trades', 0)}")
    
    ta = data.get("trading_activity", {})
    print(f"  TRADES: total={ta.get('trades_total', 0)}, 24h={ta.get('trades_24h', 0)}, win_rate={ta.get('win_rate', 0)}%, pnl=${ta.get('total_pnl', 0)}")
    
    at = data.get("autonomous_trading", {})
    print(f"  AUTONOMOUS: threads={at.get('threads', 0)}, live={at.get('live_execution')}")
    print(f"    thread_names: {at.get('thread_names', [])}")
    
    ot = data.get("options_trading", {})
    print(f"  OPTIONS: available={ot.get('module_available', False)}, status={ot.get('status', '?')}")
    
    r = data.get("resources", {})
    print(f"  RESOURCES: CPU={r.get('cpu_percent')}%, MEM={r.get('memory_percent')}%")
    
    ai = data.get("ai_learning", {})
    print(f"  AI: systems={ai.get('systems', [])}, threads={ai.get('total_threads', 0)}")
    
    print(f"\n  ALL KEYS: {list(data.keys())}")
    print("\n  >>> ADMIN STATUS ENDPOINT: WORKING! <<<")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 2: /admin-dashboard
print("\n[2] GET /admin-dashboard")
try:
    req2 = urllib.request.urlopen("http://localhost:8000/admin-dashboard", timeout=10)
    body = req2.read()
    print(f"  STATUS: {req2.status}, size={len(body)} bytes")
    if b"PROMETHEUS" in body:
        print("  >>> ADMIN DASHBOARD HTML: WORKING! (Contains PROMETHEUS branding) <<<")
    else:
        print("  WARNING: Response does not contain PROMETHEUS branding")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 3: /health (should still work)
print("\n[3] GET /health")
try:
    req3 = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
    print(f"  STATUS: {req3.status} - OK")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
