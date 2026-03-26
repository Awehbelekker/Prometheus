#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db = Path('prometheus_learning.db')
conn = sqlite3.connect(str(db), timeout=3)
cur = conn.cursor()

# Test strategy breakdown with status column
cur.execute('''
SELECT
    COALESCE(status, 'Unknown') as status_type,
    COUNT(*) as total_trades,
    SUM(CASE WHEN exit_price IS NOT NULL THEN 1 ELSE 0 END) as closed_trades,
    SUM(CASE WHEN exit_price IS NULL THEN 1 ELSE 0 END) as open_trades,
    SUM(CASE WHEN exit_price IS NOT NULL AND pnl > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(
        CASE
            WHEN SUM(CASE WHEN exit_price IS NOT NULL THEN 1 ELSE 0 END) > 0
            THEN CAST(SUM(CASE WHEN exit_price IS NOT NULL AND pnl > 0 THEN 1 ELSE 0 END) AS FLOAT)
                 / SUM(CASE WHEN exit_price IS NOT NULL THEN 1 ELSE 0 END) * 100
            ELSE 0
        END,
        1
    ) as win_rate,
    ROUND(COALESCE(SUM(CASE WHEN exit_price IS NOT NULL THEN pnl ELSE 0 END), 0), 2) as pnl
FROM shadow_trade_history
GROUP BY COALESCE(status, 'Unknown')
ORDER BY total_trades DESC
''')

print('=== Shadow Trading Status Breakdown ===')
for row in cur.fetchall():
    status = str(row[0])
    trades = int(row[1])
    closed = int(row[2])
    open_t = int(row[3])
    wins = int(row[4])
    win_rate = float(row[5])
    pnl_val = float(row[6])
    print(f'{status:15} | Trades: {trades:2} | Closed: {closed:2} | Open: {open_t:2} | Wins: {wins:2} | WinRate: {win_rate:5.1f}% | PnL: ${pnl_val:9.2f}')

conn.close()
