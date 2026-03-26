#!/usr/bin/env python3
"""
PROMETHEUS MISSING TABLE FIXER
Adds the missing open_positions table to all relevant databases
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

def add_open_positions_table(db_path: str) -> bool:
    """Add open_positions table to a specific database"""
    try:
        if not os.path.exists(db_path):
            print(f"  [SKIP] {db_path} does not exist")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='open_positions'")
        if cursor.fetchone():
            print(f"  [SKIP] {db_path} - open_positions table already exists")
            conn.close()
            return True
        
        # Create the open_positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS open_positions (
                position_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL DEFAULT 0.0,
                unrealized_pnl REAL DEFAULT 0.0,
                broker TEXT NOT NULL,
                account_id TEXT,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'open'
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"  [CHECK] {db_path} - open_positions table created")
        return True
        
    except Exception as e:
        print(f"  [ERROR] {db_path} - Failed to create table: {e}")
        return False

def add_enhanced_tables_to_databases():
    """Add enhanced tables from Enterprise package to Trading Platform databases"""
    print("\nAdding Enhanced Tables from Enterprise Package...")
    
    # Target databases that need the open_positions table
    target_databases = [
        "databases/prometheus_trading.db",
        "databases/persistent_trading.db", 
        "databases/live_trading.db",
        "databases/enhanced_paper_trading.db",
        "databases/paper_trading.db",
        "databases/portfolio_persistence.db"
    ]
    
    success_count = 0
    total_count = 0
    
    for db_path in target_databases:
        if os.path.exists(db_path):
            total_count += 1
            if add_open_positions_table(db_path):
                success_count += 1
    
    print(f"\n[RESULT] Successfully added open_positions table to {success_count}/{total_count} databases")
    return success_count == total_count

def verify_all_databases():
    """Verify all databases have the open_positions table"""
    print("\nVerifying open_positions table in all databases...")
    
    databases_to_check = [
        "databases/prometheus_trading.db",
        "databases/persistent_trading.db", 
        "databases/live_trading.db",
        "databases/enhanced_paper_trading.db",
        "databases/paper_trading.db",
        "databases/portfolio_persistence.db"
    ]
    
    all_good = True
    for db_path in databases_to_check:
        if not os.path.exists(db_path):
            continue
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='open_positions'")
        exists = cursor.fetchone() is not None
        conn.close()
        
        if exists:
            print(f"  [CHECK] {db_path} - open_positions table exists")
        else:
            print(f"  [ERROR] {db_path} - open_positions table missing")
            all_good = False
    
    return all_good

def main():
    """Main function to fix missing tables"""
    print("=" * 80)
    print("PROMETHEUS MISSING TABLE FIXER")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nAdding missing open_positions table to all relevant databases...")
    
    try:
        # Add the missing table
        success = add_enhanced_tables_to_databases()
        
        # Verify everything
        print("\n" + "=" * 80)
        if verify_all_databases():
            print("\n[CHECK] ALL DATABASES NOW HAVE open_positions TABLE!")
            print("\nTrading execution should now work properly")
            print("\nNext Steps:")
            print("  1. Stop the current trading platform")
            print("  2. Restart the trading platform")
            print("  3. Verify trades execute without 'no such table' errors")
        else:
            print("\n[WARNING] Some databases still have issues - please review above")
            
    except Exception as e:
        print(f"\n[ERROR] Error during table creation: {e}")
        raise

if __name__ == "__main__":
    main()
