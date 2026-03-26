#!/usr/bin/env python3
"""
COMPREHENSIVE TRADING SYSTEM CHECK
Physical verification of all trading components
"""

import requests
import sqlite3
from datetime import datetime
import os

print("\n" + "=" * 80)
print("COMPREHENSIVE TRADING SYSTEM VERIFICATION")
print("=" * 80)

# 1. Check Backend Status
print("\n1. BACKEND SERVER STATUS...")
try:
    r = requests.get("http://localhost:8000/health", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Backend running: {data['uptime_seconds']/3600:.1f} hours")
        print(f"   Services: {data['services']}")
    else:
        print(f"   [FAIL] Status code: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Backend not responding: {e}")
    exit(1)

# 2. Check Trading System Initialization
print("\n2. TRADING SYSTEM INITIALIZATION...")
endpoints_to_check = [
    ("/api/trading/system/status", "Trading System Status"),
    ("/api/live-trading/status", "Live Trading Status"),
    ("/api/trading/alpaca/status", "Alpaca Status"),
    ("/api/trading/ib/status", "IB Status"),
]

for endpoint, name in endpoints_to_check:
    try:
        r = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
        print(f"   {name}: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"      Response: {str(data)[:150]}")
    except Exception as e:
        print(f"   {name}: Error - {e}")

# 3. Check Environment Configuration
print("\n3. ENVIRONMENT CONFIGURATION...")
env_vars = [
    'LIVE_TRADING_ENABLED',
    'ENABLE_LIVE_ORDER_EXECUTION',
    'ALWAYS_LIVE',
    'ALPACA_LIVE_API_KEY',
    'ALPACA_PAPER_API_KEY',
    'IB_ACCOUNT',
    'IB_PORT'
]

for var in env_vars:
    value = os.getenv(var, 'NOT SET')
    if 'KEY' in var and value != 'NOT SET':
        value = f"{value[:8]}..." if len(value) > 8 else value
    print(f"   {var}: {value}")

# 4. Check Configuration Files
print("\n4. CONFIGURATION FILES...")
configs = [
    ('live_trading_config.json', 'Live Trading Config'),
    ('paper_trading_config.json', 'Paper Trading Config'),
    ('.env', 'Environment Variables')
]

for filename, name in configs:
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"   [OK] {name}: {filename} ({size} bytes)")
    else:
        print(f"   [MISSING] {name}: {filename}")

# 5. Check Database for Trades
print("\n5. TRADE DATABASE...")
try:
    conn = sqlite3.connect('prometheus_learning.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trade_history")
    count = cursor.fetchone()[0]
    print(f"   Total trades in database: {count}")
    
    cursor.execute("SELECT MAX(timestamp) FROM trade_history")
    last_trade = cursor.fetchone()[0]
    if last_trade:
        print(f"   Last trade: {last_trade}")
    else:
        print(f"   No trades yet")
    conn.close()
except Exception as e:
    print(f"   Error checking database: {e}")

# 6. Final Assessment
print("\n" + "=" * 80)
print("ASSESSMENT")
print("=" * 80)
print("To enable autonomous trading:")
print("  1. Ensure LIVE_TRADING_ENABLED=true in .env")
print("  2. Ensure ENABLE_LIVE_ORDER_EXECUTION=true in .env")
print("  3. Backend must initialize trading system in lifespan")
print("  4. Trading system should auto-start background loop")
print("  5. Check logs for 'PROMETHEUS Trading System STARTED SUCCESSFULLY'")
print("=" * 80)
