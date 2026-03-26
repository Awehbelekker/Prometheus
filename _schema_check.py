import sqlite3
c = sqlite3.connect('prometheus_learning.db').cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
for t in tables:
    c.execute(f"PRAGMA table_info([{t}])")
    cols = c.fetchall()
    col_names = [col[1] for col in cols]
    c.execute(f"SELECT COUNT(*) FROM [{t}]")
    cnt = c.fetchone()[0]
    print(f"{t} ({cnt} rows): {', '.join(col_names)}")
