"""Quick check: today's trading activity on Alpaca + IB"""
import sqlite3, json
from datetime import datetime

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# Today's trades
c.execute("SELECT id, symbol, action, quantity, price, broker, confidence, timestamp, status, profit_loss, exit_price, exit_reason FROM trade_history WHERE timestamp >= '2026-03-12' ORDER BY timestamp DESC")
rows = c.fetchall()
print(f"=== TRADES TODAY (Mar 12): {len(rows)} ===")
for r in rows:
    print(f"  #{r[0]} {r[1]} {r[2]} qty={r[3]} @${r[4]} via {r[5]} conf={r[6]:.0%} status={r[8]} P/L=${r[9] or 0:.4f} | {r[7]}")

# Open positions (still active)
c.execute("SELECT symbol, position_high, entry_time, scaled_level, dca_count, trade_id FROM position_tracking ORDER BY entry_time DESC")
positions = c.fetchall()
print(f"\n=== OPEN POSITIONS TRACKED: {len(positions)} ===")
for p in positions:
    print(f"  {p[0]}: high=${p[1]}, entered={p[2]}, scale_level={p[3]}, dca={p[4]}, trade_id={p[5]}")

# Recent trades (last 5 closed)
c.execute("SELECT id, symbol, action, price, broker, profit_loss, exit_reason, timestamp, exit_timestamp FROM trade_history WHERE exit_price IS NOT NULL ORDER BY exit_timestamp DESC LIMIT 5")
closed = c.fetchall()
print(f"\n=== LAST 5 CLOSED TRADES ===")
for r in closed:
    pl = r[5] or 0
    result = "WIN" if pl > 0 else "LOSS" if pl < 0 else "FLAT"
    print(f"  #{r[0]} {r[1]} {r[2]} @${r[3]} via {r[4]} P/L=${pl:.4f} ({result}) reason={r[6]} | {r[7]} -> {r[8]}")

# All-time stats
c.execute("SELECT COUNT(*) FROM trade_history")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL")
closed_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL")
wins = c.fetchone()[0]
c.execute("SELECT SUM(profit_loss) FROM trade_history WHERE exit_price IS NOT NULL")
total_pl = c.fetchone()[0] or 0
print(f"\n=== ALL-TIME STATS ===")
print(f"  Total trades: {total} | Closed: {closed_count} | Wins: {wins} | Win rate: {wins/closed_count*100:.1f}%" if closed_count > 0 else f"  Total: {total} | No closed trades")
print(f"  Total P&L: ${total_pl:.4f}")

# By broker
c.execute("SELECT broker, COUNT(*), SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END), SUM(profit_loss) FROM trade_history WHERE exit_price IS NOT NULL GROUP BY broker")
brokers = c.fetchall()
print(f"\n=== BY BROKER ===")
for b in brokers:
    wr = b[2]/b[1]*100 if b[1] > 0 else 0
    print(f"  {b[0]}: {b[1]} closed | {b[2]} wins ({wr:.1f}%) | P/L: ${b[3] or 0:.4f}")

db.close()
