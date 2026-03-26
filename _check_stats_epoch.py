import sqlite3
db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# All-time stats (what dashboard is showing now)
c.execute('SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL')
all_closed = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL')
all_wins = c.fetchone()[0]
if all_closed:
    print(f'ALL-TIME: {all_wins}/{all_closed} wins = {all_wins/all_closed*100:.1f}%')

# Feb 2026+ stats
EPOCH = '2026-02-01'
c.execute('SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL AND timestamp >= ?', (EPOCH,))
feb_closed = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL AND timestamp >= ?', (EPOCH,))
feb_wins = c.fetchone()[0]
c.execute('SELECT COALESCE(SUM(profit_loss),0) FROM trade_history WHERE exit_price IS NOT NULL AND timestamp >= ?', (EPOCH,))
feb_pnl = c.fetchone()[0]
if feb_closed:
    print(f'FEB 2026+: {feb_wins}/{feb_closed} wins = {feb_wins/feb_closed*100:.1f}%  PnL=${feb_pnl:.2f}')

# Breakdown by month
c.execute("""SELECT strftime('%Y-%m', timestamp) as month,
    COUNT(*) as total,
    SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(profit_loss),2) as pnl
    FROM trade_history WHERE exit_price IS NOT NULL
    GROUP BY month ORDER BY month""")
print('\nMONTH      CLOSED  WINS  WIN%     PNL')
for r in c.fetchall():
    wr = r[2]/r[1]*100 if r[1]>0 else 0
    print(f'{r[0]}    {r[1]:>5}  {r[2]:>4}  {wr:>5.1f}%  ${r[3]:>8.2f}')

# Check how many total trades (including unclosed)
c.execute('SELECT COUNT(*) FROM trade_history')
total = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM trade_history WHERE timestamp >= ?', (EPOCH,))
feb_total = c.fetchone()[0]
print(f'\nTotal rows: {total} (all-time), {feb_total} (Feb+)')

db.close()
