#!/usr/bin/env python3
"""Check if the trading loop is alive and what's blocking execution."""
import requests, json

print("=" * 60)
print("  TRADING LOOP + GATE DIAGNOSTICS")
print("=" * 60)

# 1. Check if trading system task is alive
print("\n--- TRADING SYSTEM TASK STATUS ---")
try:
    # Try various endpoints that would indicate trading loop is running
    endpoints = [
        "/api/system-metrics",
        "/api/trading-session/status",
        "/api/live-trading/status",
        "/api/trading/session",
        "/api/trading/cycle-status",
        "/api/health/detailed",
    ]
    for ep in endpoints:
        try:
            r = requests.get(f"http://localhost:8000{ep}", timeout=3)
            data = r.json()
            if 'detail' not in data or data.get('detail') != 'not_found':
                print(f"\n  {ep}:")
                # Print flat keys
                for k, v in data.items():
                    if not isinstance(v, (dict, list)):
                        print(f"    {k}: {v}")
                    elif isinstance(v, dict) and len(str(v)) < 200:
                        print(f"    {k}: {v}")
        except:
            pass
except Exception as e:
    print(f"  Error: {e}")

# 2. Check what shadow trading sees for crypto
print("\n--- SHADOW TRADING DETAILS ---")
try:
    r = requests.get("http://localhost:8000/api/shadow-trading/status", timeout=5)
    st = r.json()
    # Check open trades
    print(f"  Total trades: {st.get('total_shadow_trades')}")
    print(f"  Open trades: {st.get('open_trades')}")
    print(f"  Closed trades: {st.get('closed_trades')}")
    print(f"  Total P/L: ${st.get('total_shadow_pnl', 0):.2f}")
    last = st.get('last_trade_time', 'unknown')
    print(f"  Last trade time: {last}")
    
    # Check strategies
    for s in st.get('strategies', []):
        print(f"  Strategy {s.get('name')}: {s.get('trades')} trades, WR={s.get('win_rate')}%, P/L=${s.get('pnl', 0):.2f}")
except Exception as e:
    print(f"  Shadow: {e}")

# 3. Check if the main loop is generating signals and what's happening
print("\n--- LOOKING FOR TRADE EXECUTION EVIDENCE ---")
import sqlite3
db = sqlite3.connect("prometheus_learning.db", timeout=5)
db.row_factory = sqlite3.Row

# Signal predictions from today
today_signals = db.execute("""
    SELECT timestamp, symbol, action, confidence 
    FROM signal_predictions 
    WHERE timestamp >= date('now', '-1 day')
    ORDER BY timestamp DESC
""").fetchall()
print(f"\n  Signals in last 24h: {len(today_signals)}")
for s in today_signals[:10]:
    print(f"    {s['timestamp'][:19]}  {s['symbol']:10} {s['action']:5} conf={s['confidence']:.3f}")

# Check if any signals have confidence >= 0.70 and action != HOLD
above_thresh = [s for s in today_signals if s['confidence'] >= 0.70 and s['action'] in ('BUY', 'SELL')]
print(f"\n  Actionable signals (conf>=0.70, BUY/SELL) in 24h: {len(above_thresh)}")
for s in above_thresh[:10]:
    print(f"    {s['timestamp'][:19]}  {s['symbol']:10} {s['action']:5} conf={s['confidence']:.3f}")

# Check trade_history for today
today_trades = db.execute("""
    SELECT timestamp, symbol, action, confidence, price, broker
    FROM trade_history 
    WHERE timestamp >= date('now', '-2 days')
    ORDER BY timestamp DESC
""").fetchall()
print(f"\n  Trades executed in last 48h: {len(today_trades)}")
for t in today_trades[:10]:
    print(f"    {t['timestamp'][:19]}  {t['symbol']:10} {t['action']:5} conf={t['confidence']:.2f} ${t['price']:.2f} via {t['broker']}")

db.close()

# 4. Check dead-end memory and shadow gate in DB
print("\n--- SHADOW GATE (DB) ---")
db2 = sqlite3.connect("prometheus_learning.db", timeout=5)
try:
    tables = [r[0] for r in db2.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    shadow_tables = [t for t in tables if 'shadow' in t.lower()]
    dead_tables = [t for t in tables if 'dead' in t.lower()]
    print(f"  Shadow-related tables: {shadow_tables}")
    print(f"  Dead-end tables: {dead_tables}")
    
    # Check shadow performance per symbol
    for t in shadow_tables:
        try:
            cols = [c[1] for c in db2.execute(f"PRAGMA table_info({t})").fetchall()]
            count = db2.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t}: {count} rows, cols: {cols[:8]}")
        except:
            pass
except Exception as e:
    print(f"  DB check: {e}")
db2.close()
