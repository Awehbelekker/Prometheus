import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

print("\n=== PERFORMANCE METRICS SUMMARY ===\n")

# Get all non-null P&L data
cursor.execute("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(total_profit_loss) as records_with_pnl,
        SUM(total_profit_loss) as total_pnl,
        AVG(win_rate) as avg_win_rate,
        MAX(current_balance) as peak_balance,
        MIN(current_balance) as min_balance
    FROM performance_metrics
""")

result = cursor.fetchone()
print(f"Total Records: {result[0]}")
print(f"Records with P&L: {result[1]}")
print(f"Total P&L: ${result[2] if result[2] else 0:.2f}")
print(f"Avg Win Rate: {result[3] if result[3] else 0:.2f}%")
print(f"Peak Balance: ${result[4] if result[4] else 0:.2f}")
print(f"Min Balance: ${result[5] if result[5] else 0:.2f}")

# Get sample of recent records
print("\n=== RECENT PERFORMANCE SNAPSHOTS ===\n")
cursor.execute("""
    SELECT timestamp, total_trades, winning_trades, losing_trades, 
           total_profit_loss, win_rate, current_balance
    FROM performance_metrics
    ORDER BY timestamp DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"Time: {row[0]}")
    print(f"  Trades: {row[1]} (W:{row[2]}, L:{row[3]})")
    print(f"  P&L: ${row[4] if row[4] else 0:.2f}")
    print(f"  Win Rate: {row[5] if row[5] else 0:.2f}%")
    print(f"  Balance: ${row[6] if row[6] else 0:.2f}")
    print()

conn.close()

