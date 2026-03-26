#!/usr/bin/env python3
"""Check all PROMETHEUS databases for trading and learning data"""
import sqlite3
import os

print('='*70)
print('PROMETHEUS DATABASE STATUS')
print('='*70)

# Check key databases
databases = [
    'prometheus_learning.db',
    'prometheus_trading.db',
    'performance_metrics.db'
]

for db_name in databases:
    if not os.path.exists(db_name):
        print(f'\n{db_name}: NOT FOUND')
        continue
        
    print(f'\n{db_name}:')
    print('-'*40)
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'  Tables: {tables}')
        
        # Check specific tables
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            if count > 0:
                print(f'  {table}: {count} records')
        
        # Check for trade history
        if 'trade_history' in tables:
            cursor.execute('SELECT COUNT(*), SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END), SUM(profit_loss) FROM trade_history')
            row = cursor.fetchone()
            print(f'\n  Trade Summary: {row[0]} trades, {row[1] or 0} wins, P/L: ${row[2] or 0:.2f}')
        
        # Check for learned patterns
        if 'learned_patterns' in tables:
            cursor.execute('SELECT COUNT(*) FROM learned_patterns')
            count = cursor.fetchone()[0]
            print(f'\n  Learned Patterns: {count}')
            
        conn.close()
    except Exception as e:
        print(f'  Error: {e}')

print('\n' + '='*70)

