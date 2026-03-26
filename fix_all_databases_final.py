#!/usr/bin/env python3
"""
Fix All Databases - FINAL COMPREHENSIVE FIX
Adds missing open_positions table to ALL databases in both directories
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

def fix_database_schema(db_path: str) -> bool:
    """Fix a single database by adding the open_positions table"""
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
        
        # Create the open_positions table with comprehensive schema
        cursor.execute("""
            CREATE TABLE open_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL DEFAULT 0.0,
                realized_pnl REAL DEFAULT 0.0,
                stop_loss REAL,
                take_profit REAL,
                broker TEXT NOT NULL,
                account_id TEXT,
                position_id TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed', 'partial')),
                strategy TEXT,
                confidence REAL,
                notes TEXT,
                order_id TEXT,
                client_id INTEGER,
                leverage REAL DEFAULT 1.0,
                commission REAL DEFAULT 0.0,
                asset_type TEXT DEFAULT 'stock',
                market_value REAL,
                day_change REAL DEFAULT 0.0,
                day_change_pct REAL DEFAULT 0.0
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_positions_symbol ON open_positions(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_positions_status ON open_positions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_positions_broker ON open_positions(broker)")
        
        conn.commit()
        conn.close()
        print(f"  [FIXED] {db_path} - added open_positions table with full schema")
        return True
        
    except sqlite3.Error as e:
        print(f"  [ERROR] Failed to fix {db_path}: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Unexpected error with {db_path}: {e}")
        return False

def main():
    print("================================================================================")
    print("PROMETHEUS COMPREHENSIVE DATABASE FIX")
    print("================================================================================")
    print(f"Fix Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define all possible database locations
    trading_platform_dir = Path("C:/Users/Judy/Desktop/PROMETHEUS-Trading-Platform/databases")
    enterprise_dir = Path("C:/Users/Judy/Desktop/PROMETHEUS-Enterprise-Package-COMPLETE/databases")
    
    all_db_paths = []
    
    # Add Trading Platform databases
    if trading_platform_dir.exists():
        for db_file in trading_platform_dir.glob("*.db"):
            all_db_paths.append(str(db_file))
    
    # Add Enterprise Package databases
    if enterprise_dir.exists():
        for db_file in enterprise_dir.glob("*.db"):
            all_db_paths.append(str(db_file))
    
    if not all_db_paths:
        print("[ERROR] No database files found in either directory!")
        return
    
    print(f"Found {len(all_db_paths)} database files to check:\n")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for db_path in all_db_paths:
        result = fix_database_schema(db_path)
        if result:
            fixed_count += 1
        else:
            if "already exists" in str(result):
                skipped_count += 1
            else:
                error_count += 1
    
    print(f"\n================================================================================")
    print("FIX SUMMARY")
    print("================================================================================")
    print(f"Total databases processed: {len(all_db_paths)}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Skipped (already fixed): {skipped_count}")
    print(f"Errors: {error_count}")
    
    if error_count == 0:
        print("\n[SUCCESS] All databases now have the open_positions table!")
        print("Trading execution should work without 'no such table' errors.")
    else:
        print(f"\n[WARNING] {error_count} databases had errors. Check the output above.")
    
    print("\nNext Steps:")
    print("1. Verify IB Gateway API settings")
    print("2. Restart the trading platform")
    print("3. Test trade execution")

if __name__ == "__main__":
    main()








