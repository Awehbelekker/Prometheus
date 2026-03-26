#!/usr/bin/env python3
"""Check the PROMETHEUS learning database status."""

import sqlite3
import os

db_path = 'prometheus_learning.db'

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

print(f"Database: {db_path}")
print(f"Size: {os.path.getsize(db_path)} bytes")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")
print()

# Check each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} records")
    
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"  Columns: {columns}")
        for row in rows:
            print(f"  Sample: {row[:5]}...")  # First 5 columns

conn.close()
print("\nDone!")

