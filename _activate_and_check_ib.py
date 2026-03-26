#!/usr/bin/env python3
"""Activate live trading and check IB routing logic."""
import requests, json, os

print("=" * 70)
print("  REACTIVATING LIVE TRADING + CHECKING IB ROUTING")
print("=" * 70)

# 1. Activate live trading
print("\n--- ACTIVATING LIVE TRADING ---")
r = requests.post("http://localhost:8000/api/live-trading/start", timeout=5)
result = r.json()
print(f"  Start endpoint: {result.get('active', result)}")

# 2. Verify it's active
time = 0
for attempt in range(5):
    r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
    status = r.json()
    if status.get('active'):
        print(f"  ✅ Live Trading is NOW ACTIVE")
        break
    else:
        print(f"  Attempt {attempt+1}: Still initializing...")
        if attempt < 4:
            import time
            time.sleep(1)

# 3. Check .env for IB configuration
print("\n--- .ENV IB CONFIGURATION ---")
try:
    with open('.env', 'r') as f:
        env_lines = f.readlines()
    for line in env_lines:
        if 'IB' in line.upper() or 'BROKER' in line:
            print(f"  {line.strip()}")
except Exception as e:
    print(f"  Error reading .env: {e}")

# 4. Check autonomous_broker_executor logic
print("\n--- CHECKING BROKER ROUTING LOGIC ---")
# Read the router file to understand IB routing
try:
    with open('core/autonomous_broker_executor.py', 'r') as f:
        content = f.read()
    
    # Look for IB routing logic
    if 'ib_broker' in content.lower():
        print("  ✅ IB broker routing found in code")
        
        # Check for conditions that might skip IB
        if 'ib_connected' in content.lower() or 'not.*ib' in content.lower():
            print("  ⚠️ Found conditional IB connection checks")
        
        # Check if there's a fallback to Alpaca
        if 'alpaca' in content.lower() and 'fallback' in content.lower():
            print("  ⚠️ Alpaca is set as fallback (stocks prefer IB but fallback to Alpaca)")
    else:
        print("  ❌ IB routing not found in autonomous_broker_executor.py!")
        
except Exception as e:
    print(f"  Error: {e}")

# 5. Check if there's a market hours gate blocking IB
print("\n--- CHECKING FOR IB MARKET HOURS GATE ---")
try:
    with open('launch_ultimate_prometheus_LIVE_TRADING.py', 'r') as f:
        content = f.read()
    
    # Look for conditions that block IB when market is closed
    if 'market_open' in content.lower() and 'ib' in content.lower():
        print("  ⚠️ Found market_open condition affecting IB routing")
        print("     → This might block IB during market hours != 9:30-16:00 ET")
        print("     → Problem: IB trades 24/5 but gate checks is_market_open()")
    
    if 'is_alpaca_24hr_stock' in content.lower():
        print("  ⚠️ System prefers Alpaca 24hr stocks even for regular symbols")
        
except Exception as e:
    print(f"  Error: {e}")

# 6. Get account status for both brokers
print("\n--- BROKER ACCOUNT STATUS ---")
try:
    r = requests.get("http://localhost:8000/api/account/summary", timeout=5)
    if r.status_code == 200:
        acc = r.json()
        print(f"  Account data retrieved")
        for k, v in acc.items():
            if isinstance(v, (str, int, float)):
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Cannot get account summary: {e}")

# 7. Check what signals are being generated NOW
print("\n--- CURRENT TRADING ACTIVITY (next 10 seconds) ---")
import time
import sqlite3
db = sqlite3.connect("prometheus_learning.db", timeout=5)
start_count = db.execute("SELECT COUNT(*) FROM signal_predictions").fetchone()[0]
print(f"  Signals before wait: {start_count}")

time.sleep(10)

end_count = db.execute("SELECT COUNT(*) FROM signal_predictions").fetchone()[0]
print(f"  Signals after 10s: {end_count}")
new_signals = end_count - start_count
print(f"  New signals generated: {new_signals}")

if new_signals > 0:
    recent = db.execute("""
        SELECT symbol, action, confidence FROM signal_predictions 
        ORDER BY timestamp DESC LIMIT 5
    """).fetchall()
    print(f"  Latest signals:")
    for sig in recent:
        print(f"    {sig[0]:10} {sig[1]:5} conf={sig[2]:.3f}")

db.close()

print("\n" + "=" * 70)
