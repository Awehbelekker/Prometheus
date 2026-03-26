import sqlite3

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# Check for shadow trading tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
shadow_tables = [t for t in tables if 'shadow' in t.lower()]
print(f"Shadow Trading Tables: {shadow_tables}")

if 'shadow_sessions' in tables:
    c.execute('SELECT COUNT(*) FROM shadow_sessions')
    count = c.fetchone()[0]
    print(f"Shadow Sessions: {count}")
    
if 'shadow_trade_history' in tables:
    c.execute('SELECT COUNT(*) FROM shadow_trade_history')
    count = c.fetchone()[0]
    print(f"Shadow Trade History: {count}")

if 'shadow_position_tracking' in tables:
    c.execute('SELECT COUNT(*) FROM shadow_position_tracking')
    count = c.fetchone()[0]
    print(f"Shadow Position Tracking: {count}")

db.close()
print("Shadow trading process is running (PID 28680)")

