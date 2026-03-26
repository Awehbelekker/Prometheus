import sqlite3
from pathlib import Path

p = Path('prometheus_trading.db')
print('trading db exists:', p.exists(), '| size:', p.stat().st_size if p.exists() else 0)
if p.exists():
    db = sqlite3.connect(str(p))
    tbls = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print('tables:', [t[0] for t in tbls])
    for t in [r[0] for r in tbls]:
        cnt = db.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0]
        if cnt > 0:
            print(f'  {t}: {cnt} rows')
    db.close()
else:
    print('File not found - checking learning db trade_history instead...')
    db2 = sqlite3.connect('prometheus_learning.db')
    try:
        cnt = db2.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
        print(f'learning db trade_history: {cnt} rows')
        cols = [x[1] for x in db2.execute('PRAGMA table_info(trade_history)').fetchall()]
        print('columns:', cols)
        if cnt > 0:
            rows = db2.execute("SELECT * FROM trade_history ORDER BY rowid DESC LIMIT 3").fetchall()
            for r in rows:
                print(dict(zip(cols, r)))
    except Exception as e:
        print('trade_history error:', e)
    db2.close()
