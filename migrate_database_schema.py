#!/usr/bin/env python3
"""
🔧 DATABASE SCHEMA MIGRATION SCRIPT
Migrates the old trade_history table to the new schema with all required columns
"""

import sqlite3
import sys
from datetime import datetime

def migrate_database():
    """Migrate the database schema"""
    print("\n" + "=" * 80)
    print("🔧 PROMETHEUS DATABASE SCHEMA MIGRATION")
    print("=" * 80)
    
    try:
        # Connect to database
        print("\n📊 Connecting to prometheus_learning.db...")
        conn = sqlite3.connect('prometheus_learning.db')
        cursor = conn.cursor()
        
        # Check if old table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='trade_history'
        """)
        
        if not cursor.fetchone():
            print("[CHECK] No existing trade_history table found - will create new one")
            create_new_schema(cursor)
            conn.commit()
            conn.close()
            print("\n[CHECK] Migration complete!")
            return
        
        print("📋 Found existing trade_history table")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(trade_history)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"   Existing columns: {', '.join(existing_columns)}")
        
        # Required columns
        required_columns = {
            'id', 'symbol', 'action', 'quantity', 'price', 'total_value',
            'broker', 'confidence', 'reasoning', 'timestamp', 'order_id',
            'status', 'profit_loss', 'exit_price', 'exit_timestamp',
            'hold_duration_seconds'
        }
        
        missing_columns = required_columns - existing_columns
        
        if not missing_columns:
            print("[CHECK] Schema is already up to date!")
            conn.close()
            return
        
        print(f"\n🔧 Missing columns: {', '.join(missing_columns)}")
        print("   Migrating schema...")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_history_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_value REAL,
                broker TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                timestamp TEXT NOT NULL,
                order_id TEXT,
                status TEXT DEFAULT 'executed',
                profit_loss REAL DEFAULT 0,
                exit_price REAL,
                exit_timestamp TEXT,
                hold_duration_seconds INTEGER
            )
        """)
        
        # Copy data from old table to new table
        print("   Copying existing data...")
        
        # Get column names that exist in both tables
        common_columns = existing_columns & required_columns
        columns_str = ', '.join(common_columns)
        
        cursor.execute(f"""
            INSERT INTO trade_history_new ({columns_str})
            SELECT {columns_str} FROM trade_history
        """)
        
        rows_copied = cursor.rowcount
        print(f"   [CHECK] Copied {rows_copied} existing trades")
        
        # Drop old table
        cursor.execute("DROP TABLE trade_history")
        
        # Rename new table
        cursor.execute("ALTER TABLE trade_history_new RENAME TO trade_history")
        
        # Create other tables if they don't exist
        print("\n📊 Creating additional tables...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit_loss REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                average_profit REAL DEFAULT 0,
                average_loss REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                current_balance REAL DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                symbol TEXT,
                description TEXT NOT NULL,
                confidence_impact REAL DEFAULT 0,
                applied BOOLEAN DEFAULT 0
            )
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 80)
        print("[CHECK] MIGRATION COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   - Migrated {rows_copied} existing trades")
        print(f"   - Added {len(missing_columns)} new columns")
        print(f"   - Created performance_metrics table")
        print(f"   - Created learning_insights table")
        print("\n[CHECK] Database is now ready for full trade history tracking!")
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during migration: {e}")
        print("\nTIP: Stop PROMETHEUS before running migration:")
        print("     1. Press Ctrl+C to stop PROMETHEUS")
        print("     2. Run: python migrate_database_schema.py")
        print("     3. Restart: python launch_ultimate_prometheus_LIVE_TRADING.py")
        sys.exit(1)

def create_new_schema(cursor):
    """Create new schema from scratch"""
    print("   Creating new schema...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            total_value REAL,
            broker TEXT NOT NULL,
            confidence REAL NOT NULL,
            reasoning TEXT,
            timestamp TEXT NOT NULL,
            order_id TEXT,
            status TEXT DEFAULT 'executed',
            profit_loss REAL DEFAULT 0,
            exit_price REAL,
            exit_timestamp TEXT,
            hold_duration_seconds INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            total_profit_loss REAL DEFAULT 0,
            win_rate REAL DEFAULT 0,
            average_profit REAL DEFAULT 0,
            average_loss REAL DEFAULT 0,
            sharpe_ratio REAL DEFAULT 0,
            max_drawdown REAL DEFAULT 0,
            current_balance REAL DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            symbol TEXT,
            description TEXT NOT NULL,
            confidence_impact REAL DEFAULT 0,
            applied BOOLEAN DEFAULT 0
        )
    """)
    
    print("   [CHECK] New schema created")

if __name__ == "__main__":
    migrate_database_schema()

