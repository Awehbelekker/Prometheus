"""Inspect live_trading.db for trade exit tracking issues and shadow trading state."""
import sqlite3
import os

# Find all .db files
dbs = sorted([f for f in os.listdir('.') if f.endswith('.db')])
print(f"Database files ({len(dbs)}):")
for d in dbs:
    size_kb = os.path.getsize(d) / 1024
    print(f"  {d} ({size_kb:.0f} KB)")
print()

# ── live_trading.db ──
db = "live_trading.db"
if os.path.exists(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    print(f"=== {db} ===")
    print(f"Tables: {tables}\n")

    if "live_trades" in tables:
        c.execute("SELECT COUNT(*) FROM live_trades")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM live_trades WHERE exit_price IS NOT NULL AND exit_price > 0")
        with_exit = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM live_trades WHERE profit_loss IS NOT NULL AND profit_loss != 0")
        with_pnl = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM live_trades WHERE status = 'closed'")
        closed = c.fetchone()[0]
        no_exit = total - with_exit
        print(f"live_trades: {total} total")
        print(f"  With exit_price: {with_exit}")
        print(f"  Without exit (BROKEN): {no_exit}")
        print(f"  With non-zero P/L: {with_pnl}")
        print(f"  Status=closed: {closed}")
        print()

        # Column schema
        c.execute("PRAGMA table_info(live_trades)")
        cols = [(r[1], r[2]) for r in c.fetchall()]
        print(f"Schema: {cols}\n")

        # Show last 10 trades
        print("Last 10 trades:")
        c.execute("""
            SELECT id, symbol, side, status, entry_price, exit_price, 
                   profit_loss, quantity, created_at
            FROM live_trades ORDER BY id DESC LIMIT 10
        """)
        for r in c.fetchall():
            exit_str = f"${r[5]:.2f}" if r[5] else "NONE"
            pnl_str = f"${r[6]:.2f}" if r[6] else "$0"
            print(f"  #{r[0]} {r[1]:6s} {r[2]:4s} st={r[3]:8s} "
                  f"entry=${r[4] or 0:.2f} exit={exit_str} pnl={pnl_str} "
                  f"qty={r[7]} at={r[8]}")

        # Status distribution
        print("\nStatus distribution:")
        c.execute("SELECT status, COUNT(*) FROM live_trades GROUP BY status ORDER BY COUNT(*) DESC")
        for r in c.fetchall():
            print(f"  {r[0]}: {r[1]}")

        # Date range
        c.execute("SELECT MIN(created_at), MAX(created_at) FROM live_trades")
        dr = c.fetchone()
        print(f"\nDate range: {dr[0]} to {dr[1]}")

    conn.close()
else:
    print(f"{db} NOT FOUND")

print()

# ── Check shadow trading tables ──
for db in ["prometheus_trading.db", "shadow_trading.db", "live_trading.db"]:
    if not os.path.exists(db):
        continue
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shadow%' ORDER BY name")
    shadow_tables = [r[0] for r in c.fetchall()]
    if shadow_tables:
        print(f"=== Shadow tables in {db} ===")
        for t in shadow_tables:
            c.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = c.fetchone()[0]
            print(f"  {t}: {cnt} rows")
            if cnt > 0:
                c.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 3")
                cols = [desc[0] for desc in c.description]
                print(f"    Columns: {cols}")
                for row in c.fetchall():
                    print(f"    {row}")
    conn.close()

# ── Check prometheus_trading.db ──
db = "prometheus_trading.db"
if os.path.exists(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    print(f"\n=== {db} ===")
    print(f"Tables ({len(tables)}): {tables[:20]}...")
    
    # Check for trade-related tables
    for t in tables:
        if any(kw in t.lower() for kw in ["trade", "order", "position", "signal"]):
            c.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = c.fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt} rows")
    conn.close()
