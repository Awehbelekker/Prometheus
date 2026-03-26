import sqlite3

db = sqlite3.connect('prometheus_learning.db')
cursor = db.cursor()

print("=" * 60)
print("TRADE_HISTORY TABLE SCHEMA")
print("=" * 60)
cursor.execute('PRAGMA table_info(trade_history)')
for row in cursor.fetchall():
    print(f"  {row[1]:<30} {row[2]}")

print("\n" + "=" * 60)
print("SAMPLE TRADE RECORD")
print("=" * 60)
cursor.execute('SELECT * FROM trade_history LIMIT 1')
columns = [description[0] for description in cursor.description]
row = cursor.fetchone()
if row:
    for i, col in enumerate(columns):
        print(f"  {col:<30} {row[i]}")

print("\n" + "=" * 60)
print("ALL TABLES IN DATABASE")
print("=" * 60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print(f"  {table[0]}")

db.close()
