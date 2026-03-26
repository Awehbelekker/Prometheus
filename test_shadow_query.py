#!/usr/bin/env python3
import sqlite3
from pathlib import Path

db = Path('prometheus_learning.db')
if db.exists():
    conn = sqlite3.connect(str(db), timeout=3)
    cur = conn.cursor()
    
    # Test the exact query from the API
    print("=== Main Query ===")
    try:
        cur.execute('''
        SELECT
            COUNT(*),
            SUM(CASE WHEN exit_price IS NOT NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN exit_price IS NULL THEN 1 ELSE 0 END),
            COALESCE(SUM(CASE WHEN exit_price IS NOT NULL THEN profit_loss ELSE 0 END), 0)
        FROM shadow_trade_history
        ''')
        row = cur.fetchone()
        print(f'Query Result: {row}')
        if row:
            print(f'Total: {row[0]}, Closed: {row[1]}, Open: {row[2]}, PnL: {row[3]}')
    except Exception as e:
        print(f'Query Error: {e}')
    
    # Raw count as fallback
    print("\n=== Raw COUNT Fallback ===")
    try:
        cur.execute('SELECT COUNT(*) FROM shadow_trade_history')
        count = cur.fetchone()[0]
        print(f'Raw COUNT fallback: {count}')
    except Exception as e:
        print(f'Fallback Error: {e}')
    
    # Check schema
    print("\n=== Table Schema ===")
    try:
        cur.execute("PRAGMA table_info(shadow_trade_history)")
        for col in cur.fetchall():
            print(f"  {col[1]}: {col[2]}")
    except Exception as e:
        print(f'Schema Error: {e}')
    
    # Sample rows
    print("\n=== First 3 Shadow Trades ===")
    try:
        cur.execute("SELECT symbol, entry_price, exit_price, profit_loss, strategy_name FROM shadow_trade_history LIMIT 3")
        for row in cur.fetchall():
            print(f"  {row}")
    except Exception as e:
        print(f'Sample Error: {e}')
    
    conn.close()
else:
    print('Database not found')
