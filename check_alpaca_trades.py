#!/usr/bin/env python3
"""
Check Alpaca trading activity across all databases
"""

import sqlite3
import os
from datetime import datetime

print("=" * 80)
print("ALPACA TRADING ACTIVITY CHECK")
print("=" * 80)
print()

# Check all database files
db_files = [
    'alpaca_requests.db',
    'paper_trading.db',
    'prometheus_trading.db',
    'prometheus_learning.db',
    'persistent_trading.db',
    'prometheus_trades.db'
]

total_trades = 0
all_trades = []

for db_file in db_files:
    if not os.path.exists(db_file):
        continue
        
    print(f"\n📁 Checking: {db_file}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Check each table for trade-like data
        for table in tables:
            try:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Check if it looks like a trades table
                if any(keyword in str(columns).lower() for keyword in ['trade', 'symbol', 'order', 'buy', 'sell', 'pnl']):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        print(f"\n  ✅ Table '{table}': {count} rows")
                        print(f"     Columns: {columns}")
                        
                        # Get recent entries
                        cursor.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 5")
                        rows = cursor.fetchall()
                        
                        if rows:
                            print(f"     Recent entries:")
                            for row in rows[:3]:
                                print(f"       {row}")
                            
                            total_trades += count
                            all_trades.extend([(db_file, table, row) for row in rows])
                            
            except Exception as e:
                # Skip tables that cause errors
                pass
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total trade records found: {total_trades}")
print(f"Databases checked: {len([f for f in db_files if os.path.exists(f)])}")

if all_trades:
    print(f"\n📊 Sample of recent trades:")
    for db, table, row in all_trades[:10]:
        print(f"  {db} -> {table}: {row}")
else:
    print("\n⚠️ No trade records found in any database!")

print()
