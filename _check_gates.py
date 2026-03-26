#!/usr/bin/env python3
"""Test each gate for SOL-USD BUY and ETH-USD BUY to find what's blocking."""
import sqlite3

db = sqlite3.connect("prometheus_learning.db", timeout=5)

print("=" * 60)
print("  GATE-BY-GATE CHECK FOR CRYPTO SIGNALS")
print("=" * 60)

# 1. SHADOW GATE - per symbol+action
print("\n--- SHADOW GATE ---")
for sym, act in [("SOL-USD", "BUY"), ("ETH-USD", "BUY"), ("SOL/USD", "BUY"), ("ETH/USD", "BUY"),
                  ("SOLUSD", "BUY"), ("ETHUSD", "BUY")]:
    row = db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            AVG(pnl) as avg_pnl,
            SUM(pnl) as total_pnl
        FROM shadow_trade_history
        WHERE symbol = ? AND action = ? AND timestamp > datetime('now', '-7 days')
          AND exit_price IS NOT NULL
    """, (sym, act)).fetchone()
    if row and row[0] > 0:
        total, wins, avg_pnl, total_pnl = row
        wr = (wins or 0) / total if total else 0
        blocked = wr < 0.20 and (total_pnl or 0) < 0
        print(f"  {sym:10} {act}: {total} trades, WR={wr:.0%}, P/L=${total_pnl or 0:.2f} → {'BLOCKED' if blocked else 'ALLOWED'}")
    else:
        print(f"  {sym:10} {act}: No shadow data → ALLOWED (insufficient data < 3)")

# Check ALL shadow trades to see what symbols exist
print("\n--- ALL SHADOW TRADE SYMBOLS ---")
rows = db.execute("""
    SELECT symbol, action, COUNT(*) as cnt, 
           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(pnl) as total_pnl
    FROM shadow_trade_history
    WHERE exit_price IS NOT NULL
    GROUP BY symbol, action
    ORDER BY cnt DESC
""").fetchall()
for r in rows:
    sym, act, cnt, wins, pnl = r
    wr = (wins or 0) / cnt if cnt else 0
    blocked = cnt >= 3 and wr < 0.20 and (pnl or 0) < 0
    print(f"  {sym:10} {act:5}: {cnt} trades, WR={wr:.0%}, P/L=${pnl or 0:.2f} → {'WOULD BLOCK' if blocked else 'OK'}")

# 2. DEAD-END MEMORY
print("\n--- DEAD-END MEMORY ---")
try:
    cols = [c[1] for c in db.execute("PRAGMA table_info(dead_end_memory)").fetchall()]
    print(f"  Columns: {cols}")
    count = db.execute("SELECT COUNT(*) FROM dead_end_memory").fetchone()[0]
    print(f"  Total entries: {count}")
    
    # Check for crypto entries
    crypto_entries = db.execute("""
        SELECT * FROM dead_end_memory 
        WHERE symbol LIKE '%USD%' OR symbol LIKE '%BTC%' OR symbol LIKE '%ETH%' OR symbol LIKE '%SOL%'
        LIMIT 10
    """).fetchall()
    print(f"  Crypto dead-end entries: {len(crypto_entries)}")
    for e in crypto_entries:
        print(f"    {e}")
except Exception as e:
    print(f"  Dead-end check: {e}")

# 3. Check if the signal_predictions matches actual execution attempts
print("\n--- SIGNALS vs TRADES ANALYSIS ---")
# Get recent BUY signals that should have been executed
sigs = db.execute("""
    SELECT timestamp, symbol, action, confidence 
    FROM signal_predictions 
    WHERE confidence >= 0.70 AND action IN ('BUY', 'SELL')
    ORDER BY timestamp DESC LIMIT 20
""").fetchall()
print(f"  Last 20 actionable signals:")
for s in sigs:
    # Check if there's a matching trade
    trade = db.execute("""
        SELECT timestamp FROM trade_history 
        WHERE symbol = ? AND action = ? 
        AND timestamp >= datetime(?, '-5 minutes') AND timestamp <= datetime(?, '+5 minutes')
    """, (s[1], s[2], s[0], s[0])).fetchone()
    executed = "EXECUTED" if trade else "NOT EXECUTED"
    print(f"    {str(s[0])[:19]}  {s[1]:10} {s[2]:5} conf={s[3]:.3f}  → {executed}")

db.close()
