"""Check actual trading history performance"""
import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
c = conn.cursor()

# Get recent trade performance
c.execute('''
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning,
        SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing,
        SUM(profit_loss) as total_pnl,
        AVG(profit_loss) as avg_pnl
    FROM trade_history 
    WHERE profit_loss IS NOT NULL AND profit_loss != 0
''')
row = c.fetchone()
if row and row[0] > 0:
    print('=== ACTUAL TRADING PERFORMANCE ===')
    print(f'Total Trades with P/L: {row[0]}')
    print(f'Winning: {row[1] or 0}')
    print(f'Losing: {row[2] or 0}')
    if row[0] > 0:
        win_rate = (row[1] or 0) / row[0] * 100
        print(f'Win Rate: {win_rate:.1f}%')
    print(f'Total P/L: ${row[3] or 0:.2f}')
    print(f'Avg P/L per trade: ${row[4] or 0:.2f}')
else:
    print('No trades with P/L recorded yet')

# Get recent trades
print('\n=== RECENT TRADES ===')
c.execute('''
    SELECT symbol, action, price, quantity, profit_loss, timestamp
    FROM trade_history 
    ORDER BY timestamp DESC
    LIMIT 10
''')
for row in c.fetchall():
    pnl = f'${row[4]:.2f}' if row[4] else 'N/A'
    ts = row[5][:16] if row[5] else 'N/A'
    print(f'{ts} | {row[0]:6} | {row[1]:4} | ${row[2]:.2f} | P/L: {pnl}')

conn.close()

