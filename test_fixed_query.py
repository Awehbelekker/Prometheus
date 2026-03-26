#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db = Path('prometheus_learning.db')
if db.exists():
    conn = sqlite3.connect(str(db), timeout=3)
    cur = conn.cursor()
    
    # Test the FIXED query with pnl instead of profit_loss
    print("=== Fixed Query (Using pnl column) ===")
    try:
        cur.execute('''
        SELECT
            COUNT(*),
            SUM(CASE WHEN exit_price IS NOT NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN exit_price IS NULL THEN 1 ELSE 0 END),
            COALESCE(SUM(CASE WHEN exit_price IS NOT NULL THEN pnl ELSE 0 END), 0)
        FROM shadow_trade_history
        ''')
        row = cur.fetchone()
        print(f'Query Result: {row}')
        if row:
            print(f'Total Trades: {int(row[0])}, Closed: {int(row[1])}, Open: {int(row[2])}, PnL: ${float(row[3]):.2f}')
    except Exception as e:
        print(f'Query Error: {e}')
    
    # Test strategy breakdown
    print("\n=== Strategy Breakdown ===")
    try:
        cur.execute('''
        SELECT
            COALESCE(strategy_name, 'Unknown') as strategy,
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
        GROUP BY COALESCE(strategy_name, 'Unknown')
        ORDER BY total_trades DESC
        ''')
        strategies = cur.fetchall()
        for row in strategies:
            print(f"  {row[0]:20} | Trades: {int(row[1]):2} | Closed: {int(row[2]):2} | Open: {int(row[3]):2} | Wins: {int(row[4]):2} | WinRate: {float(row[5]):.1f}% | PnL: ${float(row[6]):.2f}")
    except Exception as e:
        print(f'Strategy Error: {e}')
    
    conn.close()
else:
    print('Database not found')
