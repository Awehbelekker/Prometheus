"""Analyze trade exit tracking in prometheus_learning.db."""
import sqlite3

conn = sqlite3.connect("prometheus_learning.db")
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM trade_history")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL AND exit_price > 0")
with_exit = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss != 0")
with_pnl = c.fetchone()[0]

c.execute("SELECT status, COUNT(*) FROM trade_history GROUP BY status ORDER BY COUNT(*) DESC")
status_dist = c.fetchall()

print(f"trade_history: {total} total")
print(f"  exit_price filled: {with_exit} ({100*with_exit/total:.0f}%)")
print(f"  non-zero P/L: {with_pnl} ({100*with_pnl/total:.0f}%)")
print(f"  Broken (no exit): {total - with_exit} ({100*(total-with_exit)/total:.0f}%)")
print(f"  Status distribution: {status_dist}")

# Date ranges
c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trade_history WHERE exit_price IS NOT NULL AND exit_price > 0")
r = c.fetchone()
print(f"\nClosed trades date range: {r[0]} to {r[1]}")

c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trade_history WHERE exit_price IS NULL OR exit_price = 0")
r = c.fetchone()
print(f"Pending trades date range: {r[0]} to {r[1]}")

# Recent pending
c.execute("""
    SELECT symbol, timestamp, price, status, exit_price, profit_loss 
    FROM trade_history WHERE exit_price IS NULL OR exit_price = 0
    ORDER BY timestamp DESC LIMIT 10
""")
print("\nMost recent unfilled trades:")
for r in c.fetchall():
    print(f"  {r[0]:10s} {str(r[1]):30s} price={r[2]:10.4f} status={r[3]} exit={r[4]} pnl={r[5]}")

# Oldest pending
c.execute("""
    SELECT symbol, timestamp, price, status
    FROM trade_history WHERE exit_price IS NULL OR exit_price = 0
    ORDER BY timestamp ASC LIMIT 5
""")
print("\nOldest unfilled trades:")
for r in c.fetchall():
    print(f"  {r[0]:10s} {str(r[1]):30s} price={r[2]:10.4f} status={r[3]}")

# How many are still real open positions vs abandoned?
c.execute("""
    SELECT th.symbol, th.timestamp, th.price, th.status
    FROM trade_history th
    WHERE (th.exit_price IS NULL OR th.exit_price = 0)
    AND th.symbol NOT IN (SELECT symbol FROM open_positions)
    ORDER BY th.timestamp DESC LIMIT 10
""")
print("\nUnfilled trades NOT in current open_positions (definitely abandoned):")
for r in c.fetchall():
    print(f"  {r[0]:10s} {str(r[1]):30s} price={r[2]:10.4f} status={r[3]}")

c.execute("""
    SELECT COUNT(*) FROM trade_history 
    WHERE (exit_price IS NULL OR exit_price = 0)
    AND symbol NOT IN (SELECT symbol FROM open_positions)
""")
abandoned = c.fetchone()[0]
print(f"\nTotal abandoned (no exit, not currently open): {abandoned}")

c.execute("""
    SELECT COUNT(*) FROM trade_history 
    WHERE (exit_price IS NULL OR exit_price = 0)
    AND symbol IN (SELECT symbol FROM open_positions)
""")
still_open = c.fetchone()[0]
print(f"Total still legitimately open: {still_open}")

conn.close()
