#!/usr/bin/env python3
"""Quick script to check database schema"""
import sqlite3
import os

def check_db(db_path):
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist")
        return
    
    print(f"\n=== {db_path} ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Get schema for each table
    for table in tables:
        table_name = table[0]
        print(f"\n--- {table_name} ---")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
    
    conn.close()

# Check relevant databases
check_db("live_trading.db")
check_db("prometheus_trading.db")

