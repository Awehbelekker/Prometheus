#!/usr/bin/env python3
"""Check why crypto isn't trading 24/7."""
import requests, json, sqlite3
from datetime import datetime

print("=" * 60)
print("  CRYPTO 24/7 TRADING CHECK")
print("=" * 60)

# 1. Server & live trading status
r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
lt = r.json()
print(f"\nLive Trading Active: {lt.get('active')}")
print(f"User: {lt.get('user')}")
print(f"Enabled Globally: {lt.get('enabled_globally')}")

r2 = requests.get("http://localhost:8000/health", timeout=5)
h = r2.json()
print(f"Server: {h.get('status')} (uptime {h.get('uptime_seconds',0)/3600:.1f}h)")

# 2. Check shadow trading
try:
    r3 = requests.get("http://localhost:8000/api/shadow-trading/status", timeout=5)
    st = r3.json()
    print(f"\nShadow Trading:")
    print(f"  Active threads: {st.get('active_threads', '?')}")
    print(f"  Total trades: {st.get('total_trades', '?')}")
except Exception as e:
    print(f"\nShadow Trading: {e}")

# 3. Check recent signals for crypto
db = sqlite3.connect("prometheus_learning.db", timeout=5)
db.row_factory = sqlite3.Row

# Last signal of any kind
r = db.execute("SELECT MAX(timestamp) as last FROM signal_predictions").fetchone()
print(f"\nLast signal prediction: {r['last']}")

# Last crypto signal
r = db.execute("""
    SELECT timestamp, symbol, action, confidence 
    FROM signal_predictions 
    WHERE symbol LIKE '%USD%' OR symbol LIKE '%BTC%' OR symbol LIKE '%ETH%' OR symbol LIKE '%SOL%'
    ORDER BY timestamp DESC LIMIT 5
""").fetchall()
print(f"\nLast 5 crypto signals:")
for row in r:
    print(f"  {row['timestamp']}  {row['symbol']:10} {row['action']:5} conf={row['confidence']:.3f}")

# Last trade of any kind
r = db.execute("SELECT MAX(timestamp) as last FROM trade_history").fetchone()
print(f"\nLast trade in DB: {r['last']}")

# Last crypto trade
r = db.execute("""
    SELECT timestamp, symbol, action, confidence, price
    FROM trade_history
    WHERE symbol LIKE '%USD%' OR symbol LIKE '%BTC%' OR symbol LIKE '%ETH%' OR symbol LIKE '%SOL%'
    ORDER BY timestamp DESC LIMIT 5
""").fetchall()
print(f"\nLast 5 crypto trades:")
for row in r:
    ts = str(row['timestamp'])[:19]
    print(f"  {ts}  {row['symbol']:10} {row['action']:5} conf={row['confidence']:.2f} ${row['price']:.2f}")

db.close()

# 4. Check if there's a market-hours gate
print("\n--- CHECKING FOR MARKET HOURS GATE ---")
try:
    # Try to get trading system health
    r4 = requests.get("http://localhost:8000/api/health/trading-system", timeout=5)
    ts = r4.json()
    trading = ts.get("trading_system", {})
    print(f"Trading system status: {trading.get('status', '?')}")
    if "market_open" in str(ts).lower():
        print(f"  Market open flag found: {ts}")
    brokers = trading.get("active_brokers", [])
    for b in brokers:
        if isinstance(b, dict):
            print(f"  Broker: {b.get('name')} connected={b.get('connected', '?')}")
except Exception as e:
    print(f"  Trading system check: {e}")

# 5. Check what the trading loop is doing
try:
    r5 = requests.get("http://localhost:8000/api/system/status", timeout=5)
    sys_status = r5.json()
    for k, v in sys_status.items():
        if not isinstance(v, (dict, list)):
            print(f"  {k}: {v}")
except Exception as e:
    print(f"  System status: {e}")

print(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Sunday)")
print("Crypto SHOULD be trading 24/7!")
