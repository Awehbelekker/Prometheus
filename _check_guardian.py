#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# Check schema
cursor.execute('PRAGMA table_info(guardian_state)')
columns = cursor.fetchall()
print('Guardian State Columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# Get latest state
cursor.execute('SELECT * FROM guardian_state ORDER BY id DESC LIMIT 1')
row = cursor.fetchone()

print('\nLatest Guardian State:')
if row:
    for i in range(len(row)):
        print(f'  {columns[i][1]}: {row[i]}')
else:
    print('  No data found')

conn.close()
