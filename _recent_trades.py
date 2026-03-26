import sqlite3
from datetime import datetime

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# Get column names
c.execute('PRAGMA table_info(trade_history)')
cols = [r[1] for r in c.fetchall()]
print(f'Columns: {cols}')

# Get recent closed trades
c.execute('''
    SELECT symbol, action, price, exit_price, profit_loss, 
           timestamp, exit_timestamp
    FROM trade_history 
    WHERE exit_price IS NOT NULL 
    ORDER BY exit_timestamp DESC
    LIMIT 20
''')

rows = c.fetchall()
print('=' * 90)
print('RECENT CLOSED TRADES')
print('=' * 90)

if rows:
    for row in rows:
        symbol, action, entry, exit_p, pnl, ts, exit_ts = row
        pnl_pct = ((exit_p - entry) / entry * 100) if entry and exit_p else 0
        print(f'{symbol:10} {action:4} Entry:{entry:>8.2f} Exit:{exit_p:>8.2f} PnL:{pnl_pct:>+6.2f}% Exit:{str(exit_ts)[:16] if exit_ts else "N/A"}')
else:
    print('No recent closed trades found')

db.close()

