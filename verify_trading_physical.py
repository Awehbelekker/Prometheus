#!/usr/bin/env python3
"""
PHYSICALLY VERIFY IF TRADING SYSTEM IS RUNNING AND GENERATING SIGNALS
"""

import requests
import sqlite3
from datetime import datetime

print("\n" + "=" * 80)
print("PHYSICAL VERIFICATION: Trading System Signal Generation")
print("=" * 80)

# Check backend
print("\n1. CHECKING BACKEND SERVER...")
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Backend running for {data['uptime_seconds']/3600:.1f} hours")
        print(f"   Services: {data['services']}")
    else:
        print(f"   [FAIL] Backend returned {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Backend not responding: {e}")
    exit(1)

# Check if trading system was initialized
print("\n2. CHECKING TRADING SYSTEM INITIALIZATION...")
try:
    r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Live Trading Status API responded")
        print(f"   Response: {data}")
    else:
        print(f"   [WARNING] Status code: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   [INFO] Could not check status: {e}")

# Check for recent broker activity
print("\n3. CHECKING BROKER CONNECTIONS...")
try:
    r = requests.get("http://localhost:8000/api/trading/alpaca/status", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Alpaca: {data}")
    else:
        print(f"   Alpaca status returned {r.status_code}")
except Exception as e:
    print(f"   Could not check Alpaca: {e}")

try:
    r = requests.get("http://localhost:8000/api/trading/ib/status", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Interactive Brokers: {data}")
    else:
        print(f"   IB status returned {r.status_code}")
except Exception as e:
    print(f"   Could not check IB: {e}")

# Check database for trades
print("\n4. CHECKING TRADE DATABASE...")
try:
    conn = sqlite3.connect('prometheus_learning.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), MAX(timestamp) FROM trade_history")
    result = cursor.fetchone()
    print(f"   Total trades: {result[0]}")
    if result[1]:
        print(f"   Last trade: {result[1]}")
    
    conn.close()
except Exception as e:
    print(f"   Could not check database: {e}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Backend server: RUNNING")
print("Trading activity: CHECK LOGS ABOVE")
print("\nTo verify signal generation is working:")
print("  1. Backend must be running with trading system initialized")
print("  2. Check logs for 'TRADING CYCLE' or 'run_trading_cycle' messages")
print("  3. Check for recent API calls to brokers")
print("  4. Database should show increasing trade counts")
print("=" * 80)


