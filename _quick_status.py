"""Quick status check for PROMETHEUS Trading Platform"""
import sqlite3
import os
import json
import socket
from datetime import datetime

def check_status():
    print("=" * 60)
    print("  PROMETHEUS - CURRENT STATUS")
    print("=" * 60)

    # Check trading DB
    for db_name in ['prometheus_trading.db', 'prometheus_learning.db']:
        if not os.path.exists(db_name):
            print(f"\n{db_name}: NOT FOUND")
            continue
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n{db_name}: {len(tables)} tables")
        
        # Check for trade-related tables
        for t in tables:
            if any(k in t.lower() for k in ['trade', 'order', 'position', 'signal']):
                try:
                    cur.execute(f"SELECT COUNT(*) FROM [{t}]")
                    cnt = cur.fetchone()[0]
                    if cnt > 0:
                        print(f"  {t}: {cnt} rows")
                except:
                    pass
        conn.close()

    # Check ports
    for name, port in [("Server", 8000), ("IB Gateway", 4002)]:
        s = socket.socket()
        s.settimeout(2)
        r = s.connect_ex(('127.0.0.1', port))
        print(f"\n{name} (port {port}): {'OPEN' if r == 0 else 'CLOSED'}")
        s.close()

    print("\n" + "=" * 60)

    # Also run original shadow check
    DB_PATH = os.path.join(os.path.dirname(__file__), 'prometheus_learning.db')
    if not os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    
    multi_tables = [t for t in tables if 'multi' in t or 'shadow' in t or 'strategy' in t]
    print(f"\n=== Multi-Strategy Tables: {multi_tables}")
    
    for t in multi_tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  {t}: {count} rows")
        if count > 0:
            cur.execute(f"SELECT * FROM {t} LIMIT 3")
            cols = [d[0] for d in cur.description]
            print(f"    Columns: {cols}")
            for row in cur.fetchall():
                print(f"    {dict(zip(cols, row))}")
    
    # Check shadow sessions
    if 'shadow_sessions' in tables:
        cur.execute("SELECT COUNT(*) FROM shadow_sessions")
        print(f"\n=== Shadow Sessions: {cur.fetchone()[0]} total")
        cur.execute("SELECT * FROM shadow_sessions ORDER BY id DESC LIMIT 5")
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            d = dict(zip(cols, row))
            print(f"  Session {d.get('id')}: strategy={d.get('strategy_name','?')}, "
                  f"trades={d.get('total_trades',0)}, started={d.get('start_time','?')}")
    
    # Check shadow trades
    if 'shadow_trades' in tables:
        cur.execute("SELECT COUNT(*) FROM shadow_trades")
        total = cur.fetchone()[0]
        print(f"\n=== Shadow Trades: {total} total")
        if total > 0:
            cur.execute("SELECT * FROM shadow_trades ORDER BY id DESC LIMIT 5")
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                d = dict(zip(cols, row))
                print(f"  Trade: {d.get('symbol','?')} {d.get('action','?')} @ {d.get('price','?')}")
    
    # Check recent shadow results
    results_dir = os.path.join(os.path.dirname(__file__), 'shadow_results')
    if os.path.exists(results_dir):
        files = sorted(os.listdir(results_dir), reverse=True)[:5]
        print(f"\n=== Recent Shadow Result Files: {len(os.listdir(results_dir))} total")
        for f in files:
            fpath = os.path.join(results_dir, f)
            try:
                with open(fpath) as fp:
                    data = json.load(fp)
                trades = data.get('total_trades', data.get('summary', {}).get('total_trades', 0))
                strategy = data.get('strategy_name', 'default')
                print(f"  {f}: strategy={strategy}, trades={trades}")
            except:
                print(f"  {f}: (could not parse)")
    
    # Check trade_history for recent P/L fix verification
    print(f"\n=== P/L Recording Verification ===")
    cur.execute("""SELECT COUNT(*) FROM trade_history 
                   WHERE profit_loss != 0 AND profit_loss IS NOT NULL""")
    nonzero_pl = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM trade_history")
    total_trades = cur.fetchone()[0]
    cur.execute("""SELECT COUNT(*) FROM trade_history 
                   WHERE action='BUY' AND exit_price IS NULL""")
    open_buys = cur.fetchone()[0]
    
    print(f"  Total trade records: {total_trades}")
    print(f"  Records with non-zero P/L: {nonzero_pl}")
    print(f"  Open BUY positions (no exit): {open_buys}")
    
    # Check if any trades happened today
    today = datetime.now().strftime('%Y-%m-%d')
    cur.execute(f"SELECT COUNT(*) FROM trade_history WHERE timestamp LIKE '{today}%'")
    today_trades = cur.fetchone()[0]
    print(f"  Trades today ({today}): {today_trades}")
    
    conn.close()

if __name__ == '__main__':
    check_status()
