import sqlite3, os
dbs = ['prometheus_trading.db', 'prometheus_trades.db', 'persistent_trading.db']
for db in dbs:
    if os.path.exists(db):
        print(f"\n=== {db} ===")
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        print(f"Tables: {tables}")
        for t in tables[:5]:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cur.fetchone()[0]
            print(f"  {t}: {cnt} rows")
            if cnt > 0 and cnt < 20:
                cur.execute(f"SELECT * FROM [{t}] LIMIT 2")
                for r in cur.fetchall():
                    print(f"    {r}")
        conn.close()

