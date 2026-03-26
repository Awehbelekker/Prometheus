"""Deep inspection of trade data across all databases."""
import sqlite3
import os

def inspect_db(db_path, keywords=None):
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    
    relevant = []
    for t in tables:
        if keywords:
            if not any(kw in t.lower() for kw in keywords):
                continue
        c.execute(f"SELECT COUNT(*) FROM [{t}]")
        cnt = c.fetchone()[0]
        if cnt > 0:
            relevant.append((t, cnt))
    
    if relevant:
        print(f"\n{'='*60}")
        print(f"{db_path} — trade-related tables with data:")
        print(f"{'='*60}")
        for t, cnt in relevant:
            print(f"\n  >> {t}: {cnt} rows")
            c.execute(f"PRAGMA table_info([{t}])")
            cols = [r[1] for r in c.fetchall()]
            print(f"     Columns: {cols}")
            c.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 3")
            for row in c.fetchall():
                # Truncate long values
                row_str = []
                for i, v in enumerate(row):
                    s = str(v)
                    if len(s) > 60:
                        s = s[:57] + "..."
                    row_str.append(f"{cols[i]}={s}")
                print(f"     {', '.join(row_str)}")
    conn.close()

trade_kw = ["trade", "order", "position", "signal", "shadow", "outcome", "ledger", "execution"]

dbs = sorted([f for f in os.listdir('.') if f.endswith('.db') and os.path.getsize(f) > 0])
for db in dbs:
    inspect_db(db, trade_kw)

# Specific deep dive: prometheus_trading.db trade tables
print("\n" + "="*60)
print("DEEP DIVE: prometheus_trading.db trade tracking")
print("="*60)

db = "prometheus_trading.db"
if os.path.exists(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    # live_trade_outcomes
    c.execute("SELECT COUNT(*) FROM live_trade_outcomes")
    total = c.fetchone()[0]
    print(f"\nlive_trade_outcomes: {total} total")
    if total > 0:
        c.execute("PRAGMA table_info(live_trade_outcomes)")
        cols = [r[1] for r in c.fetchall()]
        print(f"  Columns: {cols}")
        
        # Check exit tracking
        exit_cols = [col for col in cols if any(kw in col.lower() for kw in ["exit", "close", "sell", "pnl", "profit", "loss", "outcome"])]
        print(f"  Exit-related columns: {exit_cols}")
        
        for col in exit_cols:
            c.execute(f"SELECT COUNT(*) FROM live_trade_outcomes WHERE [{col}] IS NOT NULL AND [{col}] != '' AND [{col}] != 0")
            filled = c.fetchone()[0]
            print(f"    {col}: {filled}/{total} filled ({100*filled/total:.0f}%)")
        
        # Status distribution
        for col in cols:
            if "status" in col.lower() or "outcome" in col.lower() or "side" in col.lower():
                c.execute(f"SELECT [{col}], COUNT(*) FROM live_trade_outcomes GROUP BY [{col}] ORDER BY COUNT(*) DESC LIMIT 10")
                dist = c.fetchall()
                print(f"  {col} distribution: {dist}")

    # trade_ledger
    if "trade_ledger" in [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        c.execute("SELECT COUNT(*) FROM trade_ledger")
        total = c.fetchone()[0]
        print(f"\ntrade_ledger: {total} total")
        if total > 0:
            c.execute("PRAGMA table_info(trade_ledger)")
            cols = [r[1] for r in c.fetchall()]
            print(f"  Columns: {cols}")
            c.execute("SELECT * FROM trade_ledger ORDER BY rowid DESC LIMIT 3")
            for row in c.fetchall():
                print(f"  {dict(zip(cols, row))}")
    
    # positions
    if "positions" in [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        c.execute("SELECT COUNT(*) FROM positions")
        total = c.fetchone()[0]
        print(f"\npositions: {total} total")
        if total > 0:
            c.execute("PRAGMA table_info(positions)")
            cols = [r[1] for r in c.fetchall()]
            print(f"  Columns: {cols}")
            c.execute("SELECT * FROM positions ORDER BY rowid DESC LIMIT 5")
            for row in c.fetchall():
                print(f"  {dict(zip(cols, row))}")
    
    conn.close()

# Check persistent_trading.db
db = "persistent_trading.db"
if os.path.exists(db) and os.path.getsize(db) > 0:
    print(f"\n{'='*60}")
    print(f"DEEP DIVE: {db}")
    print(f"{'='*60}")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    print(f"Tables: {tables}")
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM [{t}]")
        cnt = c.fetchone()[0]
        if cnt > 0:
            print(f"\n  {t}: {cnt} rows")
            c.execute(f"PRAGMA table_info([{t}])")
            cols = [r[1] for r in c.fetchall()]
            print(f"  Columns: {cols}")
            c.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 3")
            for row in c.fetchall():
                d = dict(zip(cols, row))
                # show compact
                compact = {k: v for k, v in d.items() if v is not None and v != '' and v != 0}
                print(f"  {compact}")
    conn.close()
