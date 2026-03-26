#!/usr/bin/env python3
"""Check if trading loop is running after restart."""
import requests, sqlite3
from datetime import datetime, timedelta
import time

print("=" * 70)
print("  CHECKING TRADING ACTIVITY POST-RESTART")
print("=" * 70)

# Wait a bit for trading loop to start generating signals
print("\nWaiting for signals...")
time.sleep(5)

db = sqlite3.connect('prometheus_learning.db', timeout=5)
db.row_factory = sqlite3.Row

# Check activity in last minute
one_min_ago = (datetime.now() - timedelta(minutes=1)).isoformat()

sigs = db.execute("SELECT COUNT(*) FROM signal_predictions WHERE timestamp > ?", (one_min_ago,)).fetchone()[0]
trades = db.execute("SELECT COUNT(*) FROM trade_history WHERE timestamp > ?", (one_min_ago,)).fetchone()[0]

print(f"\nLast 1 minute:")
print(f"  New signals: {sigs}")
print(f"  New trades: {trades}")

# Show latest signals
if sigs > 0:
    latest = db.execute("""
        SELECT timestamp, symbol, action, confidence 
        FROM signal_predictions 
        WHERE timestamp > ? 
        ORDER BY timestamp DESC LIMIT 10
    """, (one_min_ago,)).fetchall()
    print(f"\nLatest {min(10, len(latest))} signals:")
    for s in latest:
        print(f"  {s['timestamp'][:19]}  {s['symbol']:10} {s['action']:5} {s['confidence']:.1%}")

# Show latest trades
if trades > 0:
    latest_trades = db.execute("""
        SELECT timestamp, symbol, action, broker 
        FROM trade_history 
        WHERE timestamp > ? 
        ORDER BY timestamp DESC LIMIT 10
    """, (one_min_ago,)).fetchall()
    print(f"\nLatest {min(10, len(latest_trades))} trades:")
    for t in latest_trades:
        print(f"  {t['timestamp'][:19]}  {t['symbol']:10} {t['action']:5} via {t['broker']}")

# Check if IB has been used at all
print("\n--- IB TRADING HISTORY ---")
ib_trades = db.execute("""
    SELECT COUNT(*) as cnt, 
           COUNT(DISTINCT symbol) as symbols
    FROM trade_history 
    WHERE broker LIKE '%IB%' OR broker = 'Interactive Brokers'
""").fetchone()
print(f"  Total IB trades ever: {ib_trades['cnt']}")
print(f"  Symbols traded on IB: {ib_trades['symbols']}")

# Check Alpaca trades
alpaca_trades = db.execute("""
    SELECT COUNT(*) as cnt, 
           COUNT(DISTINCT symbol) as symbols
    FROM trade_history 
    WHERE broker LIKE '%Alpaca%'
""").fetchone()
print(f"  Total Alpaca trades ever: {alpaca_trades['cnt']}")
print(f"  Symbols traded on Alpaca: {alpaca_trades['symbols']}")

# Check live trading flag
print("\n--- LIVE TRADING STATUS ---")
try:
    r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
    status = r.json()
    print(f"  Active: {status.get('active')}")
    print(f"  Enabled Globally: {status.get('enabled_globally')}")
except Exception as e:
    print(f"  Error: {e}")

db.close()

print("\n" + "=" * 70)
print(f"Check time: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)
