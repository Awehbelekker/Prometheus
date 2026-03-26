import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT symbol, price, exit_price, profit_loss, quantity, action
    FROM trade_history 
    WHERE status='closed' 
    ORDER BY profit_loss DESC
""")

print("Raw P&L Data:")
print("=" * 90)
print(f"{'Symbol':<12} {'Entry':>10} {'Exit':>10} {'P&L $':>10} {'Qty':>8} {'Action':<6} {'Calc Check'}")
print("=" * 90)

for row in cursor.fetchall():
    symbol, entry, exit_price, pnl, qty, action = row
    calc_pnl = (exit_price - entry) * qty if qty else 0
    pct = ((exit_price - entry) / entry * 100) if entry else 0
    print(f"{symbol:<12} ${entry:>9.2f} ${exit_price:>9.2f} ${pnl:>9.4f} {qty:>8.4f} {action:<6} ${calc_pnl:>9.4f} ({pct:>+6.2f}%)")

print("=" * 90)

# Check if any have profit_loss > 0
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed' AND profit_loss > 0")
positive_count = cursor.fetchone()[0]
print(f"\nTrades with profit_loss > 0: {positive_count}")

cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed' AND profit_loss < 0")
negative_count = cursor.fetchone()[0]
print(f"Trades with profit_loss < 0: {negative_count}")

cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed' AND profit_loss = 0")
zero_count = cursor.fetchone()[0]
print(f"Trades with profit_loss = 0: {zero_count}")

conn.close()
