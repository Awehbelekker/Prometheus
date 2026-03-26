#!/usr/bin/env python3
"""Quick status check for all PROMETHEUS systems."""
import urllib.request, json

def get(path):
    try:
        r = urllib.request.urlopen(f'http://localhost:8000{path}', timeout=15)
        return json.loads(r.read().decode())
    except Exception as e:
        return {'error': str(e)}

print("=" * 60)
print("PROMETHEUS SYSTEM STATUS CHECK")
print("=" * 60)

# 1. All systems status
d = get('/api/ai/all-systems/status')
active = d.get('active_systems', '?')
total = d.get('total_systems', '?')
print(f'\n1. AI SYSTEMS: {active}/{total} active')
cb = d.get('circuit_breaker', {})
print(f'   Circuit breaker: paused={cb.get("paused")}, cooldown={cb.get("cooldown_until")}')

# 2. Shadow trading
d2 = get('/api/shadow-trading/status')
print(f'\n2. SHADOW TRADING')
print(f'   Threads: {d2.get("active_threads")}, Trades: {d2.get("total_trades")}')

# 3. System health
d3 = get('/api/system/health')
svcs = d3.get('services', {})
print(f'\n3. SERVICES')
for k, v in svcs.items():
    print(f'   {k}: {v}')

# 4. Trading system health
d4 = get('/api/health/trading-system')
ts = d4.get('trading_system', {})
print(f'\n4. TRADING SYSTEM')
print(f'   Status: {ts.get("status")}')
brokers = ts.get('active_brokers', [])
for b in brokers:
    if isinstance(b, dict):
        print(f'   Broker: {b.get("name")} - equity=${b.get("equity", "?")}')
    else:
        print(f'   Broker: {b}')

# 5. Memory check
import os
mem_info = d3.get('system', {})
print(f'\n5. RESOURCES')
print(f'   Memory: {mem_info}')

# 6. Real metrics
d5 = get('/api/ai/all-systems/status')
metrics = d5.get('real_metrics', d5.get('metrics', {}))
print(f'\n6. REAL TRADE METRICS')
print(f'   {metrics}')

print("\n" + "=" * 60)
print("STATUS CHECK COMPLETE")
print("=" * 60)
