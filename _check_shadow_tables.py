import sqlite3
conn = sqlite3.connect('prometheus_learning.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shadow%'")
tables = [r[0] for r in cur.fetchall()]
print("Shadow tables:", tables)
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM [{t}]")
    print(f"  {t}: {cur.fetchone()[0]} rows")
    cur.execute(f"PRAGMA table_info([{t}])")
    cols = [r[1] for r in cur.fetchall()]
    print(f"    columns: {cols}")
conn.close()
