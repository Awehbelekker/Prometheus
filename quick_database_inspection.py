"""Quick database inspection to check for recent trading data"""
import sqlite3
import os
from datetime import datetime, timedelta

def inspect_database(db_name):
    """Inspect a database for tables and recent data"""
    if not os.path.exists(db_name):
        print(f"[ERROR] {db_name} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 {db_name}")
    print(f"{'='*60}")
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("  [INFO]️  No tables found")
            conn.close()
            return
        
        print(f"  📋 Tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"\n  [CHECK] {table_name}: {count} rows")
                    
                    # Try to get recent data
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    col_names = [col[1] for col in columns]
                    
                    # Check for timestamp columns
                    timestamp_cols = [c for c in col_names if 'time' in c.lower() or 'date' in c.lower()]
                    
                    if timestamp_cols:
                        # Get most recent entry
                        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {timestamp_cols[0]} DESC LIMIT 1")
                        recent = cursor.fetchone()
                        if recent:
                            print(f"     Latest: {timestamp_cols[0]} = {recent[col_names.index(timestamp_cols[0])]}")
                    
                    # Show sample columns
                    print(f"     Columns: {', '.join(col_names[:5])}{'...' if len(col_names) > 5 else ''}")
                else:
                    print(f"  ⚪ {table_name}: empty")
                    
            except Exception as e:
                print(f"  [WARNING]️  {table_name}: Error - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

# Inspect key databases
print("\n" + "="*60)
print("🔍 PROMETHEUS DATABASE INSPECTION")
print("="*60)

databases = [
    "prometheus_trading.db",
    "prometheus_learning.db",
    "live_trading.db",
    "paper_trading.db",
    "enhanced_paper_trading.db",
    "prometheus_advanced_trading.db"
]

for db in databases:
    inspect_database(db)

print("\n" + "="*60)
print("[CHECK] Inspection Complete")
print("="*60 + "\n")

