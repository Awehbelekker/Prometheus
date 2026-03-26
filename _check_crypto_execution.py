#!/usr/bin/env python3
"""Deep dive: why are crypto signals generated but not executed?"""
import requests, json

print("=" * 60)
print("  WHY AREN'T CRYPTO SIGNALS BEING EXECUTED?")
print("=" * 60)

# 1. Check if the main trading loop is running
print("\n--- 1. LIVE TRADING STATUS ---")
r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
status = r.json()
for k, v in status.items():
    print(f"  {k}: {v}")

# 2. Check recent logs for trade execution attempts
print("\n--- 2. RECENT TRADING LOGS ---")
try:
    r = requests.get("http://localhost:8000/api/logs/recent", timeout=5)
    logs = r.json()
    if isinstance(logs, list):
        for log in logs[-20:]:
            print(f"  {log}")
    elif isinstance(logs, dict):
        for k, v in logs.items():
            print(f"  {k}: {v}")
except Exception as e:
    print(f"  Logs endpoint: {e}")

# 3. Check trading engine state
print("\n--- 3. TRADING ENGINE STATUS ---")
try:
    r = requests.get("http://localhost:8000/api/trading/status", timeout=5)
    ts = r.json()
    for k, v in ts.items():
        if not isinstance(v, (dict, list)):
            print(f"  {k}: {v}")
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if not isinstance(v2, (dict, list)):
                    print(f"  {k}.{k2}: {v2}")
except Exception as e:
    print(f"  Trading engine: {e}")

# 4. Check broker connections
print("\n--- 4. BROKER CONNECTIONS ---")
try:
    r = requests.get("http://localhost:8000/api/brokers/status", timeout=5)
    bs = r.json()
    for k, v in bs.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")
except Exception as e:
    print(f"  Broker status: {e}")

# 5. Check positions (max positions might be blocking)
print("\n--- 5. CURRENT POSITIONS (checking max_positions gate) ---")
try:
    r = requests.get("http://localhost:8000/api/positions", timeout=5)
    pos = r.json()
    if isinstance(pos, list):
        print(f"  Open positions: {len(pos)}")
        for p in pos:
            if isinstance(p, dict):
                print(f"    {p.get('symbol', '?')}: qty={p.get('qty', '?')} mkt_val={p.get('market_value', '?')}")
    elif isinstance(pos, dict):
        positions = pos.get('positions', pos.get('data', []))
        print(f"  Open positions: {len(positions)}")
        for p in positions:
            if isinstance(p, dict):
                print(f"    {p.get('symbol', '?')}: qty={p.get('qty', '?')} mkt_val={p.get('market_value', '?')}")
except Exception as e:
    print(f"  Positions: {e}")

# 6. Check the shadow/learning gate
print("\n--- 6. SHADOW TRADING GATE ---")
try:
    r = requests.get("http://localhost:8000/api/shadow-trading/status", timeout=5)
    st = r.json()
    print(f"  Shadow status: {json.dumps(st, indent=4)[:500]}")
except Exception as e:
    print(f"  Shadow: {e}")

# 7. Check guardian status
print("\n--- 7. DRAWDOWN GUARDIAN ---")
try:
    r = requests.get("http://localhost:8000/api/guardian/status", timeout=5)
    gs = r.json()
    print(f"  Guardian: {json.dumps(gs, indent=4)[:500]}")
except Exception as e:
    print(f"  Guardian: {e}")

# 8. Check dead-end memory
print("\n--- 8. DEAD-END MEMORY ---")
try:
    r = requests.get("http://localhost:8000/api/dead-end-memory/status", timeout=5)
    de = r.json()
    print(f"  Dead-end: {json.dumps(de, indent=4)[:500]}")
except Exception as e:
    print(f"  Dead-end: {e}")

# 9. Check regime exposure
print("\n--- 9. REGIME EXPOSURE ---")
try:
    r = requests.get("http://localhost:8000/api/regime/status", timeout=5)
    re_status = r.json()
    print(f"  Regime: {json.dumps(re_status, indent=4)[:500]}")
except Exception as e:
    print(f"  Regime: {e}")
