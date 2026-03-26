import sqlite3
db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# Trades from Feb 16, 2026 onward (stated performance period)
c.execute("""SELECT id, symbol, action, price, profit_loss, timestamp, exit_timestamp 
             FROM trade_history 
             WHERE profit_loss != 0 AND timestamp >= '2026-02-16'
             ORDER BY timestamp""")
rows = c.fetchall()
wins = [r for r in rows if r[4] > 0]
losses = [r for r in rows if r[4] < 0]

print(f"=== Trades from Feb 16, 2026 onward ===")
print(f"Total with P/L: {len(rows)}  |  Wins: {len(wins)}  |  Losses: {len(losses)}")
if rows:
    print(f"Win Rate: {len(wins)/len(rows)*100:.1f}%")
print()
for r in rows:
    pl = r[4]
    result = "WIN" if pl > 0 else "LOSS"
    print(f"  #{r[0]:>3} {r[1]:>8} {r[2]:>5} PL=${pl:>10.4f} {result:>4} | {str(r[5])[:19]} -> {str(r[6])[:19]}")

print()
total_pl = sum(r[4] for r in rows)
print(f"Total P/L: ${total_pl:.4f}")

# Also check ALL trades
print("\n=== ALL trades with P/L ===")
c.execute("SELECT COUNT(*), SUM(CASE WHEN profit_loss>0 THEN 1 ELSE 0 END), SUM(CASE WHEN profit_loss<0 THEN 1 ELSE 0 END) FROM trade_history WHERE profit_loss!=0")
row = c.fetchone()
print(f"All time: {row[0]} trades | Wins: {row[1]} | Losses: {row[2]}")

db.close()
