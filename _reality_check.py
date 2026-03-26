#!/usr/bin/env python3
"""PROMETHEUS Reality Check - What's ACTUALLY working?"""
import os, sys, sqlite3
from pathlib import Path
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("PROMETHEUS REALITY CHECK - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
print("=" * 60)

# 1. Environment
print("\n--- ENVIRONMENT ---")
env_file = Path('.env')
if env_file.exists():
    content = env_file.read_text()
    lines = content.split('\n')
    def env_val(key):
        for l in lines:
            if l.startswith(key + '='):
                v = l.split('=', 1)[1].strip().strip('"').strip("'")
                return v if len(v) > 3 else None
        return None
    
    print(f"Alpaca API Key:  {'SET (' + env_val('ALPACA_API_KEY')[:8] + '...)' if env_val('ALPACA_API_KEY') else 'MISSING'}")
    print(f"Alpaca Secret:   {'SET' if env_val('ALPACA_SECRET_KEY') else 'MISSING'}")
    print(f"IB Host:         {env_val('IB_HOST') or 'NOT SET'}")
    print(f"IB Port:         {env_val('IB_PORT') or 'NOT SET'}")
    print(f"OpenAI Key:      {'SET' if env_val('OPENAI_API_KEY') else 'NOT SET'}")
    print(f"Live Execution:  {'ON' if 'ENABLE_LIVE_ORDER_EXECUTION=1' in content else 'OFF'}")
    print(f"Always Live:     {'ON' if 'ALWAYS_LIVE=1' in content else 'OFF'}")
else:
    print(".env FILE MISSING!")

# 2. Alpaca LIVE
print("\n--- ALPACA LIVE ACCOUNT ---")
try:
    from dotenv import load_dotenv
    load_dotenv()
    import alpaca_trade_api as tradeapi
    api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        'https://api.alpaca.markets'
    )
    acct = api.get_account()
    print(f"Status:       {acct.status}")
    print(f"Equity:       ${float(acct.equity):,.2f}")
    print(f"Cash:         ${float(acct.cash):,.2f}")
    print(f"Buying Power: ${float(acct.buying_power):,.2f}")
    print(f"Day Trades:   {acct.daytrade_count}")
    
    positions = api.list_positions()
    print(f"Positions:    {len(positions)}")
    total_mv = 0
    total_pl = 0
    for p in positions:
        mv = float(p.market_value)
        pl = float(p.unrealized_pl)
        total_mv += mv
        total_pl += pl
        pct = float(p.unrealized_plpc) * 100
        print(f"  {p.symbol:6s} {float(p.qty):>8.2f} sh  MV=${mv:>10,.2f}  P/L=${pl:>8,.2f} ({pct:+.1f}%)")
    if positions:
        print(f"  {'TOTAL':6s} {'':>8s}     MV=${total_mv:>10,.2f}  P/L=${total_pl:>8,.2f}")
    
    orders = api.list_orders(status='all', limit=10)
    recent_filled = [o for o in orders if o.status == 'filled']
    recent_other = [o for o in orders if o.status != 'filled']
    print(f"\nRecent Orders: {len(orders)} (filled: {len(recent_filled)})")
    for o in orders[:7]:
        t = str(o.created_at)[:16] if o.created_at else '?'
        print(f"  {t} {o.side:4s} {o.qty or '?':>5s} {o.symbol:6s} {o.type:6s} {o.status}")

except Exception as e:
    print(f"ERROR: {e}")

# 3. Alpaca PAPER
print("\n--- ALPACA PAPER ACCOUNT ---")
try:
    paper_api = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        'https://paper-api.alpaca.markets'
    )
    pacct = paper_api.get_account()
    print(f"Paper Equity:    ${float(pacct.equity):,.2f}")
    print(f"Paper Cash:      ${float(pacct.cash):,.2f}")
    paper_pos = paper_api.list_positions()
    print(f"Paper Positions: {len(paper_pos)}")
    for p in paper_pos[:5]:
        print(f"  {p.symbol:6s} {float(p.qty):>8.2f} sh  MV=${float(p.market_value):>10,.2f}")
    paper_orders = paper_api.list_orders(status='all', limit=5)
    print(f"Paper Orders:    {len(paper_orders)} recent")
    for o in paper_orders[:3]:
        t = str(o.created_at)[:16] if o.created_at else '?'
        print(f"  {t} {o.side:4s} {o.qty or '?':>5s} {o.symbol:6s} {o.status}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. IB Gateway
print("\n--- IB GATEWAY ---")
try:
    import socket
    ib_host = os.getenv("IB_HOST", "127.0.0.1")
    ib_port = int(os.getenv("IB_PORT", "4002"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((ib_host, ib_port))
    sock.close()
    if result == 0:
        print(f"Port {ib_port}: REACHABLE (IB Gateway/TWS may be running)")
    else:
        print(f"Port {ib_port}: NOT REACHABLE (IB Gateway/TWS not running)")
except Exception as e:
    print(f"ERROR: {e}")

# 5. Databases
print("\n--- DATABASES ---")
for db_name in ['prometheus_learning.db', 'prometheus_trading.db', 'multi_strategy_shadow.db', 
                'shadow_trading_results.db', 'trading_data.db']:
    db_path = Path(db_name)
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024*1024)
        try:
            conn = sqlite3.connect(str(db_path), timeout=3)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            info_parts = []
            for t in tables[:4]:
                try:
                    cur.execute(f'SELECT COUNT(*) FROM [{t}]')
                    info_parts.append(f"{t}:{cur.fetchone()[0]}")
                except:
                    pass
            conn.close()
            print(f"  {db_name}: {size_mb:.1f}MB, {len(tables)} tables")
            if info_parts:
                print(f"    rows: {', '.join(info_parts)}")
        except Exception as e:
            print(f"  {db_name}: {size_mb:.1f}MB (err: {e})")
    else:
        print(f"  {db_name}: NOT FOUND")

# 6. Trading history
print("\n--- ACTUAL TRADING HISTORY ---")
for db_name in ['prometheus_learning.db', 'prometheus_trading.db', 'trading_data.db']:
    db_path = Path(db_name)
    if not db_path.exists():
        continue
    try:
        conn = sqlite3.connect(str(db_path), timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            if 'trade' in t.lower() or 'order' in t.lower() or 'history' in t.lower():
                try:
                    cur.execute(f"SELECT COUNT(*) FROM [{t}]")
                    cnt = cur.fetchone()[0]
                    if cnt > 0:
                        # Get most recent
                        cur.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 3")
                        cols = [d[0] for d in cur.description]
                        rows = cur.fetchall()
                        print(f"\n  {db_name} -> {t}: {cnt} rows")
                        print(f"    Columns: {', '.join(cols[:8])}")
                        for r in rows:
                            vals = [str(v)[:20] for v in r[:6]]
                            print(f"    Latest: {' | '.join(vals)}")
                except:
                    pass
        conn.close()
    except:
        pass

# 7. Key files
print("\n--- KEY FILES ---")
files = [
    'unified_production_server.py',
    'admin_command_center.html',
    'live_dashboard.html',
    'alert_monitor.py',
    'rebalance_portfolio.py',
    'core/alpaca_trading_service.py',
    'core/options_strategies.py',
]
for f in files:
    p = Path(f)
    if p.exists():
        kb = p.stat().st_size / 1024
        print(f"  OK     {f} ({kb:.0f}KB)")
    else:
        print(f"  MISSING {f}")

# 8. Server check
print("\n--- UNIFIED SERVER STATUS ---")
server = Path('unified_production_server.py')
if server.exists():
    size_kb = server.stat().st_size / 1024
    content = server.read_text(encoding='utf-8', errors='ignore')
    route_count = content.count('@app.get(') + content.count('@app.post(') + content.count('@app.put(') + content.count('@app.delete(')
    has_admin_full = '/api/admin/full-status' in content
    has_dashboard_route = '@app.get("/dashboard")' in content
    line_count = content.count('\n')
    print(f"  Size: {size_kb:.0f}KB, {line_count} lines, {route_count} routes")
    print(f"  Has /api/admin/full-status: {has_admin_full}")
    print(f"  Has /dashboard route: {has_dashboard_route}")

print("\n" + "=" * 60)
print("END OF REALITY CHECK")
print("=" * 60)
