#!/usr/bin/env python3
"""Check post-restart status and why IB isn't trading."""
import requests, sqlite3, json
from datetime import datetime, timedelta

print("=" * 70)
print("  POST-RESTART: TRADING LOOP + IB DIAGNOSTICS")
print("=" * 70)

# 1. Live trading status
print("\n--- LIVE TRADING STATUS ---")
r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
lt = r.json()
print(f"  Live Trading Active: {lt.get('active')}")
print(f"  Enabled Globally: {lt.get('enabled_globally')}")

# 2. Check recent signals
print("\n--- SIGNALS IN LAST 5 MINUTES ---")
db = sqlite3.connect("prometheus_learning.db", timeout=5)
db.row_factory = sqlite3.Row

five_min_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
sigs = db.execute("""
    SELECT timestamp, symbol, action, confidence 
    FROM signal_predictions 
    WHERE timestamp > ?
    ORDER BY timestamp DESC LIMIT 20
""", (five_min_ago,)).fetchall()
print(f"  Signals since restart: {len(sigs)}")
for s in sigs:
    print(f"    {s['timestamp'][:19]}  {s['symbol']:10} {s['action']:5} conf={s['confidence']:.3f}")

# 3. Check IB routing
print("\n--- IB TRADING AVAILABILITY ---")
try:
    # Check if any IB trades were attempted in last 2 hours
    two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()
    ib_trades = db.execute("""
        SELECT timestamp, symbol, action, broker FROM trade_history 
        WHERE broker = 'Interactive Brokers' OR broker LIKE '%IB%'
        AND timestamp > ?
        ORDER BY timestamp DESC LIMIT 5
    """, (two_hours_ago,)).fetchall()
    print(f"  IB trades (last 2h): {len(ib_trades)}")
    for t in ib_trades:
        print(f"    {t['timestamp'][:19]}  {t['symbol']:10} {t['action']:5}")
    
    # Check if any stocks have IB routing rules
    all_trades = db.execute("""
        SELECT DISTINCT symbol, broker FROM trade_history 
        WHERE broker LIKE '%IB%' OR symbol IN ('AAPL', 'MSFT', 'SPY', 'QQQ')
        LIMIT 10
    """).fetchall()
    print(f"\n  Symbols with IB connection: {len(all_trades)}")
    for t in all_trades:
        print(f"    {t[0]:10} via {t[1]}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Check if IB connection is up
print("\n--- IB CONNECTION CHECK ---")
try:
    r = requests.post("http://localhost:8000/api/brokers/status", timeout=5)
    bs = r.json()
    print(f"  Broker status endpoint: OK")
except:
    print(f"  Cannot check broker status - endpoint unavailable")

# 5. Check trading loop logs
print("\n--- CHECKING FOR TRADING LOOP ERRORS ---")
try:
    # Look for any indication that trades failed due to broker issues
    latest_log_check = db.execute("""
        SELECT COUNT(*) as cnt FROM trade_history 
        WHERE timestamp > ?
    """, (five_min_ago,)).fetchone()
    recent_trades = latest_log_check['cnt'] if latest_log_check else 0
    print(f"  Trades since restart: {recent_trades}")
    
    if recent_trades == 0:
        print(f"  ⚠️ No trades executed yet - trading loop may still be initializing")
    else:
        print(f"  ✅ Trading loop is executing trades")
except Exception as e:
    print(f"  Error: {e}")

# 6. IB-specific questions
print("\n--- IB ROUTING LOGIC CHECK ---")
print("  Questions about IB trading:")
print("  1. Is IB connected and authenticated?")
print("  2. Does the system detect when IB is NOT connected?")
print("  3. Are there position limits blocking IB trades?")
print("  4. Is 'market hours' blocking IB 24/5 forex/crypto trading?")
print("  5. Are stocks being routed to Alpaca instead of IB?")

db.close()

print("\n" + "=" * 70)
print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
