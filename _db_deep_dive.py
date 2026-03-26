#!/usr/bin/env python3
"""Quick DB deep dive"""
import sqlite3, os
db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prometheus_learning.db')
conn = sqlite3.connect(db, timeout=10)
c = conn.cursor()

print("=== open_positions columns ===")
for r in c.execute("PRAGMA table_info(open_positions)").fetchall():
    print(f"  {r[1]} ({r[2]})")

print("\n=== open_positions data ===")
for r in c.execute("SELECT * FROM open_positions").fetchall():
    print(r)

print("\n=== trade_history columns ===")
for r in c.execute("PRAGMA table_info(trade_history)").fetchall():
    print(f"  {r[1]} ({r[2]})")

print("\n=== trade_history stats ===")
total = c.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
print(f"Total rows: {total}")
sells = c.execute("SELECT COUNT(*) FROM trade_history WHERE action IN ('SELL','sell')").fetchone()[0]
buys = c.execute("SELECT COUNT(*) FROM trade_history WHERE action IN ('BUY','buy')").fetchone()[0]
print(f"Buys: {buys}, Sells: {sells}")

# Check for pnl
cols = [r[1] for r in c.execute("PRAGMA table_info(trade_history)").fetchall()]
print(f"Columns: {cols}")
if 'pnl' in cols:
    pnl = c.execute("SELECT COALESCE(SUM(pnl),0) FROM trade_history WHERE pnl IS NOT NULL").fetchone()[0]
    wins = c.execute("SELECT COUNT(*) FROM trade_history WHERE pnl > 0").fetchone()[0]
    losses = c.execute("SELECT COUNT(*) FROM trade_history WHERE pnl < 0 AND pnl IS NOT NULL").fetchone()[0]
    print(f"PnL sum: ${pnl:+.2f}, Wins: {wins}, Losses: {losses}")

print("\n=== trade_history recent 10 ===")
for r in c.execute("SELECT * FROM trade_history ORDER BY id DESC LIMIT 10").fetchall():
    print(r)

print("\n=== shadow_sessions columns ===")
for r in c.execute("PRAGMA table_info(shadow_sessions)").fetchall():
    print(f"  {r[1]} ({r[2]})")

print("\n=== shadow_sessions data (last 5) ===")
for r in c.execute("SELECT * FROM shadow_sessions ORDER BY rowid DESC LIMIT 5").fetchall():
    print(r)

print("\n=== performance_metrics columns ===")
for r in c.execute("PRAGMA table_info(performance_metrics)").fetchall():
    print(f"  {r[1]} ({r[2]})")

print("\n=== performance_metrics last 3 ===")
for r in c.execute("SELECT * FROM performance_metrics ORDER BY rowid DESC LIMIT 3").fetchall():
    print(r)

print("\n=== learning_outcomes columns ===")
for r in c.execute("PRAGMA table_info(learning_outcomes)").fetchall():
    print(f"  {r[1]} ({r[2]})")

print("\n=== learning_outcomes last 5 ===")
for r in c.execute("SELECT * FROM learning_outcomes ORDER BY rowid DESC LIMIT 5").fetchall():
    print(r)

print("\n=== ai_attribution stats ===")
total_attr = c.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
print(f"Total records: {total_attr}")
acols = [r[1] for r in c.execute("PRAGMA table_info(ai_attribution)").fetchall()]
print(f"Columns: {acols}")
# Sample
for r in c.execute("SELECT * FROM ai_attribution ORDER BY rowid DESC LIMIT 3").fetchall():
    print(r)

conn.close()
