#!/usr/bin/env python3
"""
Database Migration Script
Migrates existing prometheus_learning.db to new schema
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate database to new schema"""
    
    db_path = 'prometheus_learning.db'
    backup_path = f'prometheus_learning_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print("🔄 PROMETHEUS DATABASE MIGRATION")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("[CHECK] No existing database found - will create new one")
        create_new_database()
        return
    
    # Backup existing database
    print(f"📦 Creating backup: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    print("[CHECK] Backup created")
    
    # Connect to database
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(trade_history)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f"\n📊 Current columns: {', '.join(columns)}")
    
    # Check if migration needed
    if 'broker' in columns:
        print("[CHECK] Database already migrated")
        db.close()
        return
    
    print("\n🔧 Migrating database schema...")
    
    try:
        # Create new table with correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                broker TEXT,
                symbol TEXT,
                action TEXT,
                quantity REAL,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                pnl_percent REAL,
                ai_confidence REAL,
                agents_agreed INTEGER,
                success INTEGER,
                reason TEXT
            )
        ''')
        
        # Copy data from old table to new table
        cursor.execute('''
            INSERT INTO trade_history_new 
            (id, timestamp, symbol, action, quantity, entry_price, exit_price, 
             pnl, pnl_percent, ai_confidence, agents_agreed, success, reason, broker)
            SELECT 
                id, timestamp, symbol, action, quantity, entry_price, exit_price,
                pnl, pnl_percent, ai_confidence, agents_agreed, success, reason, 'alpaca'
            FROM trade_history
        ''')
        
        # Drop old table
        cursor.execute('DROP TABLE trade_history')
        
        # Rename new table
        cursor.execute('ALTER TABLE trade_history_new RENAME TO trade_history')
        
        db.commit()
        print("[CHECK] Migration successful")
        
        # Verify
        cursor.execute("PRAGMA table_info(trade_history)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"[CHECK] New columns: {', '.join(new_columns)}")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        db.rollback()
        print(f"💡 Restoring from backup: {backup_path}")
        db.close()
        os.remove(db_path)
        shutil.copy2(backup_path, db_path)
        print("[CHECK] Restored from backup")
        return
    
    db.close()
    print("\n[CHECK] Database migration complete!")
    print(f"📦 Backup saved as: {backup_path}")


def create_new_database():
    """Create new database with correct schema"""
    
    db = sqlite3.connect('prometheus_learning.db')
    cursor = db.cursor()
    
    # Trade history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            broker TEXT,
            symbol TEXT,
            action TEXT,
            quantity REAL,
            entry_price REAL,
            exit_price REAL,
            pnl REAL,
            pnl_percent REAL,
            ai_confidence REAL,
            agents_agreed INTEGER,
            success INTEGER,
            reason TEXT
        )
    ''')
    
    # Learning patterns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pattern_type TEXT,
            symbol TEXT,
            success_rate REAL,
            avg_return REAL,
            occurrences INTEGER
        )
    ''')
    
    db.commit()
    db.close()
    
    print("[CHECK] New database created with correct schema")


if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"[ERROR] Error: {e}")

