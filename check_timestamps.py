import sqlite3
from datetime import datetime

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT symbol, timestamp, exit_timestamp 
    FROM trade_history 
    WHERE status='closed' 
    ORDER BY timestamp
""")

print("Trade Timestamps:")
print("=" * 80)
for row in cursor.fetchall():
    symbol, opened, closed = row
    print(f"{symbol:12} Opened: {opened[:19]} | Closed: {closed[:19]}")

print("\n" + "=" * 80)
cursor.execute("SELECT MIN(timestamp), MAX(exit_timestamp) FROM trade_history WHERE status='closed'")
min_time, max_time = cursor.fetchone()
print(f"Date range: {min_time[:19]} to {max_time[:19]}")

# Parse dates
from datetime import datetime
start = datetime.fromisoformat(min_time)
end = datetime.fromisoformat(max_time)
days = (end - start).days
hours = (end - start).total_seconds() / 3600

print(f"Duration: {days} days ({hours:.1f} hours)")

conn.close()
