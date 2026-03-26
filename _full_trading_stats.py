#!/usr/bin/env python3
"""
PROMETHEUS Full Trading Stats - Both Brokers + Shadow Trading + DB
"""
import os, sys, sqlite3, json, traceback
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import requests

print()
print("=" * 80)
print("  PROMETHEUS FULL TRADING STATISTICS")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Local)")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: ALPACA LIVE ACCOUNT
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  ALPACA LIVE ACCOUNT")
print("=" * 80)

key = os.getenv('ALPACA_LIVE_API_KEY') or os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_LIVE_SECRET_KEY') or os.getenv('ALPACA_SECRET_KEY')
alpaca_equity = 0
alpaca_cash = 0
alpaca_positions = []

if key and secret:
    base = 'https://api.alpaca.markets'
    headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}

    try:
        acct = requests.get(f'{base}/v2/account', headers=headers, timeout=10).json()
        if 'code' not in acct and 'message' not in acct:
            alpaca_equity = float(acct.get('equity', 0))
            alpaca_cash = float(acct.get('cash', 0))
            buying_power = float(acct.get('buying_power', 0))
            last_equity = float(acct.get('last_equity', 0))
            day_pl = alpaca_equity - last_equity
            day_pl_pct = (day_pl / last_equity * 100) if last_equity > 0 else 0

            print(f"  Status:         {acct.get('status')}")
            print(f"  Account #:      {acct.get('account_number')}")
            print(f"  Equity:         ${alpaca_equity:.2f}")
            print(f"  Cash:           ${alpaca_cash:.2f}")
            print(f"  Buying Power:   ${buying_power:.2f}")
            print(f"  Day P/L:        ${day_pl:+.2f} ({day_pl_pct:+.2f}%)")
            print(f"  Invested:       ${alpaca_equity - alpaca_cash:.2f}")
            print()

            # Positions
            try:
                alpaca_positions = requests.get(f'{base}/v2/positions', headers=headers, timeout=10).json()
            except:
                alpaca_positions = []

            print(f"  POSITIONS ({len(alpaca_positions)}):")
            print(f"  {'Symbol':<8} {'Qty':>8} {'AvgEntry':>10} {'Current':>10} {'MktVal':>10} {'P/L':>10} {'P/L%':>8}")
            print(f"  {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")
            total_unrealized = 0
            total_mkt_val = 0
            for p in alpaca_positions:
                sym = p['symbol']
                qty = float(p['qty'])
                avg = float(p['avg_entry_price'])
                cur = float(p['current_price'])
                mkt = float(p['market_value'])
                upl = float(p['unrealized_pl'])
                upl_pct = float(p['unrealized_plpc']) * 100
                total_unrealized += upl
                total_mkt_val += mkt
                print(f"  {sym:<8} {qty:>8.4f} ${avg:>9.2f} ${cur:>9.2f} ${mkt:>9.2f} ${upl:>+9.2f} {upl_pct:>+7.2f}%")

            print(f"\n  Total Market Value:   ${total_mkt_val:.2f}")
            print(f"  Total Unrealized P/L: ${total_unrealized:+.2f}")

            # Recent orders
            try:
                orders = requests.get(f'{base}/v2/orders', headers=headers,
                                     params={'status': 'all', 'limit': 20, 'direction': 'desc'},
                                     timeout=10).json()
                filled = [o for o in orders if o.get('status') == 'filled']
                print(f"\n  RECENT FILLED ORDERS ({len(filled)}):")
                print(f"  {'Time':<20} {'Side':<5} {'Symbol':<7} {'Qty':>6} {'Price':>10} {'Status':<10}")
                print(f"  {'-'*20} {'-'*5} {'-'*7} {'-'*6} {'-'*10} {'-'*10}")
                for o in filled[:15]:
                    t = str(o.get('filled_at', o.get('created_at', '?')))[:19]
                    print(f"  {t:<20} {o.get('side','?'):<5} {o.get('symbol','?'):<7} {o.get('filled_qty','?'):>6} ${o.get('filled_avg_price','?'):>9} {o.get('status','?'):<10}")
            except Exception as e:
                print(f"  Error getting orders: {e}")
        else:
            print(f"  ERROR: {acct}")
    except Exception as e:
        print(f"  ERROR connecting: {e}")
else:
    print("  Alpaca API keys not found in .env")

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: INTERACTIVE BROKERS ACCOUNT
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  INTERACTIVE BROKERS ACCOUNT")
print("=" * 80)

ib_equity = 0
ib_cash = 0
ib_positions = []
ib_connected = False

ib_host = os.getenv('IB_HOST', '127.0.0.1')
ib_port = int(os.getenv('IB_PORT', '4002'))
ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
print(f"  Config: {ib_host}:{ib_port}  Account={ib_account}")

try:
    from ib_insync import IB
    ib = IB()
    ib.connect(ib_host, ib_port, clientId=99, timeout=15)
    ib_connected = True
    print("  STATUS: CONNECTED")
    print()

    # Account summary
    account_values = ib.accountSummary(ib_account)
    summary = {}
    for av in account_values:
        if av.tag in ('NetLiquidation', 'TotalCashValue', 'BuyingPower',
                     'GrossPositionValue', 'UnrealizedPnL', 'RealizedPnL',
                     'AvailableFunds', 'SettledCash', 'ExcessLiquidity'):
            summary[av.tag] = float(av.value) if av.value else 0.0

    ib_equity = summary.get('NetLiquidation', 0)
    ib_cash = summary.get('TotalCashValue', 0)

    print(f"  Net Liquidation:    ${ib_equity:.2f}")
    print(f"  Total Cash:         ${ib_cash:.2f}")
    print(f"  Buying Power:       ${summary.get('BuyingPower', 0):.2f}")
    print(f"  Gross Position Val: ${summary.get('GrossPositionValue', 0):.2f}")
    print(f"  Unrealized P/L:     ${summary.get('UnrealizedPnL', 0):+.2f}")
    print(f"  Realized P/L:       ${summary.get('RealizedPnL', 0):+.2f}")
    print(f"  Available Funds:    ${summary.get('AvailableFunds', 0):.2f}")
    print(f"  Invested:           ${ib_equity - ib_cash:.2f}")
    print()

    # Positions
    positions = ib.positions(account=ib_account)
    ib_positions = positions
    print(f"  POSITIONS ({len(positions)}):")
    if not positions:
        print("    (no open positions)")
    else:
        for pos in positions:
            sym = pos.contract.symbol
            qty = pos.position
            avg = pos.avgCost
            print(f"    {sym:<8} qty={qty:>8.2f}  avgCost=${avg:>8.2f}")

    # Open orders
    open_orders = ib.openOrders()
    if open_orders:
        print(f"\n  OPEN ORDERS ({len(open_orders)}):")
        for order in open_orders:
            print(f"    {order.action} {order.totalQuantity}")

    ib.disconnect()

except ImportError:
    print("  ERROR: ib_insync not installed")
except Exception as e:
    print(f"  STATUS: DISCONNECTED - {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: COMBINED PORTFOLIO SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  COMBINED PORTFOLIO SUMMARY")
print("=" * 80)

total_equity = alpaca_equity + ib_equity
total_cash = alpaca_cash + ib_cash
total_invested = total_equity - total_cash
total_positions = len(alpaca_positions) + len(ib_positions)

print(f"  Combined Equity:    ${total_equity:.2f}")
print(f"  Combined Cash:      ${total_cash:.2f} ({total_cash/total_equity*100:.1f}% idle)" if total_equity > 0 else "  Combined Cash:      $0.00")
print(f"  Combined Invested:  ${total_invested:.2f}")
print(f"  Total Positions:    {total_positions} (Alpaca: {len(alpaca_positions)}, IB: {len(ib_positions)})")
print(f"  Alpaca:             ${alpaca_equity:.2f} ({'CONNECTED' if key else 'N/A'})")
print(f"  IB:                 ${ib_equity:.2f} ({'CONNECTED' if ib_connected else 'DISCONNECTED'})")

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: DATABASE STATS (prometheus_learning.db)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  DATABASE STATS (prometheus_learning.db)")
print("=" * 80)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prometheus_learning.db')
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()

        # List tables
        tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        print(f"\n  Tables ({len(tables)}):")
        for t in tables:
            count = cursor.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
            print(f"    {t:<40} {count:>6} rows")

        # Open positions from DB
        if 'open_positions' in tables:
            print(f"\n  LIVE OPEN POSITIONS (from DB):")
            rows = cursor.execute("SELECT symbol, broker, entry_price, quantity, entry_time FROM open_positions ORDER BY entry_time DESC").fetchall()
            if rows:
                print(f"  {'Symbol':<10} {'Broker':<10} {'Entry$':>10} {'Qty':>8} {'EntryTime':<20}")
                for r in rows:
                    print(f"  {r[0]:<10} {r[1] or 'Alpaca':<10} ${r[2] or 0:>9.2f} {r[3] or 0:>8.4f} {str(r[4] or '?')[:19]:<20}")
            else:
                print("    (none)")

        # Trade history from learning_trades if exists
        if 'learning_trades' in tables:
            print(f"\n  TRADE HISTORY (learning_trades):")
            total = cursor.execute("SELECT COUNT(*) FROM learning_trades").fetchone()[0]
            wins = cursor.execute("SELECT COUNT(*) FROM learning_trades WHERE pnl > 0").fetchone()[0]
            losses = cursor.execute("SELECT COUNT(*) FROM learning_trades WHERE pnl <= 0").fetchone()[0]
            total_pnl = cursor.execute("SELECT COALESCE(SUM(pnl), 0) FROM learning_trades").fetchone()[0]
            avg_pnl = cursor.execute("SELECT COALESCE(AVG(pnl), 0) FROM learning_trades").fetchone()[0]
            win_rate = (wins / total * 100) if total > 0 else 0

            print(f"    Total Trades:    {total}")
            print(f"    Wins:            {wins}")
            print(f"    Losses:          {losses}")
            print(f"    Win Rate:        {win_rate:.1f}%")
            print(f"    Total P/L:       ${total_pnl:+.2f}")
            print(f"    Avg P/L:         ${avg_pnl:+.2f}")

            # Recent trades
            recent = cursor.execute("""
                SELECT symbol, action, pnl, exit_time, entry_price, exit_price
                FROM learning_trades ORDER BY exit_time DESC LIMIT 10
            """).fetchall()
            if recent:
                print(f"\n    RECENT CLOSED TRADES:")
                print(f"    {'Symbol':<8} {'Action':<6} {'Entry':>8} {'Exit':>8} {'P/L':>10} {'Time':<20}")
                for r in recent:
                    print(f"    {r[0] or '?':<8} {r[1] or '?':<6} ${r[4] or 0:>7.2f} ${r[5] or 0:>7.2f} ${r[2] or 0:>+9.2f} {str(r[3] or '?')[:19]:<20}")

        # Shadow trading stats
        if 'shadow_trade_history' in tables:
            print(f"\n  SHADOW TRADING STATS:")
            total = cursor.execute("SELECT COUNT(*) FROM shadow_trade_history").fetchone()[0]
            open_t = cursor.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='OPEN'").fetchone()[0]
            closed_t = cursor.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='CLOSED'").fetchone()[0]
            wins = cursor.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='CLOSED' AND pnl > 0").fetchone()[0]
            losses = cursor.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='CLOSED' AND pnl <= 0").fetchone()[0]
            total_pnl = cursor.execute("SELECT COALESCE(SUM(pnl), 0) FROM shadow_trade_history WHERE status='CLOSED'").fetchone()[0]
            win_rate = (wins / closed_t * 100) if closed_t > 0 else 0

            print(f"    Total Shadow Trades:  {total}")
            print(f"    Open:                 {open_t}")
            print(f"    Closed:               {closed_t}")
            print(f"    Wins:                 {wins}")
            print(f"    Losses:               {losses}")
            print(f"    Win Rate:             {win_rate:.1f}%")
            print(f"    Total P/L:            ${total_pnl:+.2f}")

            # By asset class
            try:
                by_class = cursor.execute("""
                    SELECT asset_class, COUNT(*), COALESCE(SUM(pnl), 0),
                           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)
                    FROM shadow_trade_history WHERE status='CLOSED'
                    GROUP BY asset_class
                """).fetchall()
                if by_class:
                    print(f"\n    BY ASSET CLASS:")
                    print(f"    {'Class':<12} {'Trades':>8} {'P/L':>12} {'WinRate':>8}")
                    for r in by_class:
                        wr = (r[3] / r[1] * 100) if r[1] > 0 else 0
                        print(f"    {r[0] or 'unknown':<12} {r[1]:>8} ${r[2]:>+11.2f} {wr:>7.1f}%")
            except:
                pass

            # Recent shadow trades
            try:
                recent = cursor.execute("""
                    SELECT symbol, action, confidence, entry_price, pnl, timestamp, status, asset_class
                    FROM shadow_trade_history ORDER BY timestamp DESC LIMIT 10
                """).fetchall()
                if recent:
                    print(f"\n    RECENT SHADOW TRADES:")
                    print(f"    {'Symbol':<10} {'Action':<6} {'Conf':>6} {'Entry$':>10} {'P/L':>10} {'Status':<8}")
                    for r in recent:
                        pnl_str = f"${r[4]:>+9.2f}" if r[4] else "     open"
                        print(f"    {r[0] or '?':<10} {r[1] or '?':<6} {r[2] or 0:>5.1f}% ${r[3] or 0:>9.2f} {pnl_str} {r[6] or '?':<8}")
            except:
                pass

        # Shadow sessions
        if 'shadow_sessions' in tables:
            print(f"\n  SHADOW SESSIONS:")
            sessions = cursor.execute("""
                SELECT session_id, config_name, starting_capital, current_capital, total_trades, win_rate, total_pnl, status
                FROM shadow_sessions ORDER BY started_at DESC LIMIT 5
            """).fetchall()
            if sessions:
                for s in sessions:
                    print(f"    Session: {s[0]}")
                    print(f"      Config: {s[1]}, Capital: ${s[2] or 0:,.0f} -> ${s[3] or 0:,.2f}")
                    print(f"      Trades: {s[4] or 0}, Win Rate: {s[5] or 0:.1f}%, P/L: ${s[6] or 0:+.2f}, Status: {s[7]}")
            else:
                print("    (no sessions)")

        # Shadow position tracking
        if 'shadow_position_tracking' in tables:
            spt_count = cursor.execute("SELECT COUNT(*) FROM shadow_position_tracking").fetchone()[0]
            print(f"\n  Shadow Position Tracking: {spt_count} entries")

        # AI learning data
        if 'ai_performance' in tables:
            print(f"\n  AI PERFORMANCE TRACKING:")
            ai_rows = cursor.execute("SELECT COUNT(*) FROM ai_performance").fetchone()[0]
            print(f"    Total AI performance records: {ai_rows}")

        conn.close()
    except Exception as e:
        print(f"  ERROR reading database: {e}")
        traceback.print_exc()
else:
    print("  Database not found!")

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: SHADOW TRADING RESULTS FILES
# ═══════════════════════════════════════════════════════════════════
results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shadow_trading_results')
if os.path.exists(results_dir):
    print("\n" + "=" * 80)
    print("  SHADOW TRADING RESULTS FILES")
    print("=" * 80)
    files = os.listdir(results_dir)
    print(f"  Files in shadow_trading_results/: {len(files)}")
    for f in sorted(files)[:20]:
        fpath = os.path.join(results_dir, f)
        size = os.path.getsize(fpath)
        print(f"    {f:<50} {size:>8} bytes")

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: SERVER STATUS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  SERVER STATUS")
print("=" * 80)

try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    health = r.json()
    print(f"  Backend Server:  RUNNING (port 8000)")
    print(f"  Status:          {health.get('status', 'unknown')}")
except:
    print(f"  Backend Server:  NOT RESPONDING (port 8000)")

# Check if trading system is responding in logs
print(f"\n  IB Gateway:      {'CONNECTED' if ib_connected else 'DISCONNECTED'}")
print(f"  Alpaca API:      {'CONNECTED' if alpaca_equity > 0 else 'ERROR'}")

print("\n" + "=" * 80)
print("  STATS COMPLETE")
print("=" * 80)
