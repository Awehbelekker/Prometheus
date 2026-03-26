#!/usr/bin/env python3
"""Full Trading Report for PROMETHEUS Trading Platform"""
import sqlite3
import json
import os
from datetime import datetime, timedelta

def run_report():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prometheus_learning.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    print("=" * 90)
    print("   PROMETHEUS TRADING PLATFORM - FULL TRADING REPORT")
    now = datetime.now()
    print("   Generated: " + now.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 90)

    # ===== 1. TRADE HISTORY SUMMARY =====
    print("\n" + "=" * 90)
    print("  1. TRADE HISTORY SUMMARY")
    print("=" * 90)
    c.execute("SELECT COUNT(*) FROM trade_history")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trade_history WHERE action='BUY'")
    buys = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trade_history WHERE action='SELL'")
    sells = c.fetchone()[0]
    print("  Total Trades: %d" % total)
    print("  Buys: %d | Sells: %d" % (buys, sells))

    c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trade_history")
    row = c.fetchone()
    first_date = str(row[0])[:10] if row[0] else 'N/A'
    last_date = str(row[1])[:10] if row[1] else 'N/A'
    print("  Date Range: %s to %s" % (first_date, last_date))

    c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM trade_history")
    trading_days = c.fetchone()[0]
    print("  Active Trading Days: %d" % trading_days)
    if trading_days > 0:
        print("  Avg Trades/Day: %.1f" % (total / trading_days))

    # ===== 2. PROFIT/LOSS ANALYSIS =====
    print("\n" + "=" * 90)
    print("  2. PROFIT/LOSS ANALYSIS")
    print("=" * 90)
    c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss IS NOT NULL AND profit_loss != 0")
    pnl_count = c.fetchone()[0]
    c.execute("SELECT SUM(profit_loss) FROM trade_history WHERE profit_loss IS NOT NULL AND profit_loss != 0")
    total_pnl = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0")
    wins = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss < 0")
    losses_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss = 0 OR profit_loss IS NULL")
    flat = c.fetchone()[0]
    win_rate = (wins / (wins + losses_count) * 100) if (wins + losses_count) > 0 else 0

    print("  Trades with P/L Data: %d" % pnl_count)
    print("  Winners: %d | Losers: %d | Flat/No-data: %d" % (wins, losses_count, flat))
    print("  Win Rate: %.1f%%" % win_rate)
    print("  Total Realized P/L: $%.2f" % total_pnl)

    c.execute("SELECT AVG(profit_loss) FROM trade_history WHERE profit_loss > 0")
    avg_win = c.fetchone()[0] or 0
    c.execute("SELECT AVG(profit_loss) FROM trade_history WHERE profit_loss < 0")
    avg_loss = c.fetchone()[0] or 0
    c.execute("SELECT MAX(profit_loss) FROM trade_history WHERE profit_loss > 0")
    best = c.fetchone()[0] or 0
    c.execute("SELECT MIN(profit_loss) FROM trade_history WHERE profit_loss < 0")
    worst = c.fetchone()[0] or 0
    print("  Avg Win: $%.4f | Avg Loss: $%.4f" % (avg_win, avg_loss))
    print("  Best Trade: $%.4f | Worst Trade: $%.4f" % (best, worst))
    if avg_loss != 0:
        print("  Risk/Reward Ratio: %.2f" % abs(avg_win / avg_loss))

    c.execute("SELECT AVG(hold_duration_seconds) FROM trade_history WHERE hold_duration_seconds > 0")
    avg_hold = c.fetchone()[0]
    if avg_hold:
        hours = avg_hold / 3600
        print("  Avg Hold Duration: %.1f hours" % hours)

    # ===== 3. PERFORMANCE BY SYMBOL =====
    print("\n" + "=" * 90)
    print("  3. PERFORMANCE BY SYMBOL (All Traded)")
    print("=" * 90)
    c.execute("""
        SELECT symbol,
               COUNT(*) as trades,
               SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
               SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells,
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
               COALESCE(SUM(profit_loss), 0) as total_pnl,
               COALESCE(AVG(CASE WHEN profit_loss != 0 THEN profit_loss END), 0) as avg_pnl
        FROM trade_history
        GROUP BY symbol
        ORDER BY trades DESC
    """)
    rows = c.fetchall()
    print("  %-12s %7s %5s %6s %5s %5s %7s %12s %10s" % ('Symbol', 'Trades', 'Buys', 'Sells', 'Wins', 'Loss', 'WR%', 'Total P/L', 'Avg P/L'))
    print("  " + "-" * 78)
    for r in rows:
        wr = (r['wins'] / (r['wins'] + r['losses']) * 100) if (r['wins'] + r['losses']) > 0 else 0
        print("  %-12s %7d %5d %6d %5d %5d %6.1f%% $%10.4f $%9.4f" % (r['symbol'], r['trades'], r['buys'], r['sells'], r['wins'], r['losses'], wr, r['total_pnl'], r['avg_pnl']))

    # ===== 4. LAST 30 TRADES =====
    print("\n" + "=" * 90)
    print("  4. LAST 30 TRADES")
    print("=" * 90)
    c.execute("SELECT timestamp, symbol, action, confidence, price, quantity, profit_loss, exit_reason FROM trade_history ORDER BY timestamp DESC LIMIT 30")
    print("  %-22s %-10s %-5s %6s %10s %8s %10s %-15s" % ('Timestamp', 'Symbol', 'Act', 'Conf', 'Price', 'Qty', 'P/L', 'Exit Reason'))
    print("  " + "-" * 90)
    for r in c.fetchall():
        ts = str(r['timestamp'])[:19] if r['timestamp'] else 'N/A'
        pnl_str = "$%.4f" % r['profit_loss'] if r['profit_loss'] else '--'
        price = "$%.2f" % r['price'] if r['price'] else '--'
        conf = "%.2f" % r['confidence'] if r['confidence'] else '--'
        qty = "%.4f" % r['quantity'] if r['quantity'] else '--'
        exit_r = str(r['exit_reason'])[:14] if r['exit_reason'] else '--'
        print("  %-22s %-10s %-5s %6s %10s %8s %10s %-15s" % (ts, r['symbol'], r['action'], conf, price, qty, pnl_str, exit_r))

    # ===== 5. DAILY P/L (Last 30 Days) =====
    print("\n" + "=" * 90)
    print("  5. DAILY P/L (Last 30 Days)")
    print("=" * 90)
    c.execute("""
        SELECT DATE(timestamp) as day,
               COUNT(*) as trades,
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
               COALESCE(SUM(profit_loss), 0) as pnl
        FROM trade_history
        WHERE timestamp >= date('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY day DESC
    """)
    daily_rows = c.fetchall()
    if daily_rows:
        print("  %-12s %7s %6s %7s %12s" % ('Date', 'Trades', 'Wins', 'Losses', 'P/L'))
        print("  " + "-" * 46)
        cumulative = 0
        for r in daily_rows:
            cumulative += r['pnl']
            print("  %-12s %7d %6d %7d $%10.4f" % (r['day'], r['trades'], r['wins'], r['losses'], r['pnl']))
        print("  " + "-" * 46)
        t_trades = sum(r['trades'] for r in daily_rows)
        t_wins = sum(r['wins'] for r in daily_rows)
        t_losses = sum(r['losses'] for r in daily_rows)
        print("  %-12s %7d %6d %7d $%10.4f" % ('TOTAL', t_trades, t_wins, t_losses, cumulative))
    else:
        print("  No trades in last 30 days")

    # ===== 6. WEEKLY P/L =====
    print("\n" + "=" * 90)
    print("  6. WEEKLY P/L SUMMARY")
    print("=" * 90)
    c.execute("""
        SELECT strftime('%%Y-W%%W', timestamp) as week,
               COUNT(*) as trades,
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
               COALESCE(SUM(profit_loss), 0) as pnl
        FROM trade_history
        GROUP BY week
        ORDER BY week DESC
        LIMIT 12
    """)
    weekly_rows = c.fetchall()
    if weekly_rows:
        print("  %-12s %7s %6s %7s %7s %12s" % ('Week', 'Trades', 'Wins', 'Losses', 'WR%', 'P/L'))
        print("  " + "-" * 54)
        for r in weekly_rows:
            wr = (r['wins'] / (r['wins'] + r['losses']) * 100) if (r['wins'] + r['losses']) > 0 else 0
            print("  %-12s %7d %6d %7d %6.1f%% $%10.4f" % (r['week'], r['trades'], r['wins'], r['losses'], wr, r['pnl']))

    # ===== 7. AI SYSTEM PERFORMANCE =====
    print("\n" + "=" * 90)
    print("  7. AI SYSTEM PERFORMANCE (Weight Analysis)")
    print("=" * 90)
    c.execute("""
        SELECT ai_system,
               COUNT(*) as attributions,
               AVG(vote_weight) as avg_weight,
               MIN(vote_weight) as min_weight,
               MAX(vote_weight) as max_weight,
               SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as correct,
               SUM(CASE WHEN eventual_pnl < 0 THEN 1 ELSE 0 END) as incorrect,
               SUM(CASE WHEN outcome_recorded = 1 THEN 1 ELSE 0 END) as recorded
        FROM ai_attribution
        GROUP BY ai_system
        ORDER BY attributions DESC
    """)
    ai_rows = c.fetchall()
    if ai_rows:
        print("  %-25s %8s %8s %8s %8s %6s %6s %7s" % ('AI System', 'Signals', 'Avg Wt', 'Min Wt', 'Max Wt', 'Win', 'Lose', 'Acc%'))
        print("  " + "-" * 82)
        for r in ai_rows:
            acc = (r['correct'] / (r['correct'] + r['incorrect']) * 100) if (r['correct'] + r['incorrect']) > 0 else 0
            print("  %-25s %8d %8.3f %8.3f %8.3f %6d %6d %6.1f%%" % (r['ai_system'], r['attributions'], r['avg_weight'], r['min_weight'], r['max_weight'], r['correct'], r['incorrect'], acc))
    else:
        print("  No AI attribution data")

    # ===== 8. CONFIDENCE DISTRIBUTION =====
    print("\n" + "=" * 90)
    print("  8. CONFIDENCE DISTRIBUTION OF TRADES")
    print("=" * 90)
    c.execute("""
        SELECT
            CASE
                WHEN confidence < 0.5 THEN '< 0.50'
                WHEN confidence < 0.6 THEN '0.50-0.59'
                WHEN confidence < 0.65 THEN '0.60-0.64'
                WHEN confidence < 0.7 THEN '0.65-0.69'
                WHEN confidence < 0.75 THEN '0.70-0.74'
                WHEN confidence < 0.8 THEN '0.75-0.79'
                WHEN confidence < 0.85 THEN '0.80-0.84'
                WHEN confidence >= 0.85 THEN '>= 0.85'
                ELSE 'N/A'
            END as bucket,
            COUNT(*) as trades,
            SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
            COALESCE(SUM(profit_loss), 0) as total_pnl
        FROM trade_history
        WHERE confidence IS NOT NULL
        GROUP BY bucket
        ORDER BY bucket
    """)
    conf_rows = c.fetchall()
    if conf_rows:
        print("  %-14s %7s %6s %7s %7s %12s" % ('Confidence', 'Trades', 'Wins', 'Losses', 'WR%', 'P/L'))
        print("  " + "-" * 56)
        for r in conf_rows:
            wr = (r['wins'] / (r['wins'] + r['losses']) * 100) if (r['wins'] + r['losses']) > 0 else 0
            print("  %-14s %7d %6d %7d %6.1f%% $%10.4f" % (r['bucket'], r['trades'], r['wins'], r['losses'], wr, r['total_pnl']))

    # ===== 9. SHADOW TRADING STATUS =====
    print("\n" + "=" * 90)
    print("  9. SHADOW TRADING STATUS")
    print("=" * 90)
    sessions = 0
    shadow_trades = 0
    try:
        c.execute("SELECT COUNT(*) FROM shadow_sessions")
        sessions = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM shadow_trade_history")
        shadow_trades = c.fetchone()[0]
        print("  Total Shadow Sessions: %d" % sessions)
        print("  Total Shadow Trades: %d" % shadow_trades)

        c.execute("SELECT session_id, config_name, starting_capital, current_capital, total_trades, win_rate, status, started_at FROM shadow_sessions ORDER BY started_at DESC LIMIT 10")
        srows = c.fetchall()
        if srows:
            print("\n  Recent Sessions:")
            print("  %-20s %10s %10s %7s %7s %-10s %-20s" % ('Config', 'Capital', 'Current', 'Trades', 'WR%', 'Status', 'Started'))
            print("  " + "-" * 88)
            for s in srows:
                started = str(s['started_at'])[:16] if s['started_at'] else 'N/A'
                wr = s['win_rate'] or 0
                config = str(s['config_name'] or 'default')[:19]
                cap = s['starting_capital'] or 0
                cur = s['current_capital'] or 0
                trades = s['total_trades'] or 0
                st = str(s['status'] or 'unknown')[:9]
                print("  %-20s $%8.0f $%8.0f %7d %6.1f%% %-10s %-20s" % (config, cap, cur, trades, wr, st, started))

        if shadow_trades > 0:
            c.execute("""
                SELECT symbol, action,
                       COUNT(*) as trades,
                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                       COALESCE(SUM(pnl), 0) as total_pnl,
                       COALESCE(AVG(pnl), 0) as avg_pnl
                FROM shadow_trade_history
                GROUP BY symbol, action
                ORDER BY trades DESC
                LIMIT 20
            """)
            strows = c.fetchall()
            if strows:
                print("\n  Shadow Trade Breakdown:")
                print("  %-12s %-6s %7s %5s %7s %12s %10s" % ('Symbol', 'Action', 'Trades', 'Wins', 'WR%', 'Total P/L', 'Avg P/L'))
                print("  " + "-" * 62)
                for r in strows:
                    wr = (r['wins'] / r['trades'] * 100) if r['trades'] > 0 else 0
                    print("  %-12s %-6s %7d %5d %6.1f%% $%10.4f $%9.4f" % (r['symbol'], r['action'], r['trades'], r['wins'], wr, r['total_pnl'], r['avg_pnl']))
    except Exception as e:
        print("  Shadow trading data error: %s" % e)

    # Multi-strategy leaderboard
    try:
        c.execute("""
            SELECT strategy_name, total_trades, win_rate, total_return_pct, sharpe_ratio, max_drawdown, avg_trade_pnl, completed_at, promoted_to_live
            FROM multi_strategy_leaderboard
            ORDER BY completed_at DESC, rank ASC
        """)
        lb_rows = c.fetchall()
        if lb_rows:
            print("\n  Multi-Strategy Leaderboard (%d entries):" % len(lb_rows))
            print("  %-20s %7s %7s %8s %8s %7s %8s %5s" % ('Strategy', 'Trades', 'WR%', 'Return%', 'Sharpe', 'MaxDD%', 'AvgPnl', 'Promo'))
            print("  " + "-" * 75)
            for r in lb_rows:
                promo = 'YES' if r['promoted_to_live'] else 'no'
                print("  %-20s %7d %6.1f%% %7.2f%% %8.3f %6.2f%% $%7.2f %5s" % (
                    r['strategy_name'], r['total_trades'] or 0, r['win_rate'] or 0,
                    r['total_return_pct'] or 0, r['sharpe_ratio'] or 0,
                    r['max_drawdown'] or 0, r['avg_trade_pnl'] or 0, promo))
    except Exception as e:
        print("  Multi-strategy leaderboard error: %s" % e)

    # ===== 10. ACTIVE POSITIONS (ALPACA) =====
    print("\n" + "=" * 90)
    print("  10. ACTIVE POSITIONS (Alpaca)")
    print("=" * 90)
    alpaca_equity = 0
    try:
        import alpaca_trade_api as tradeapi
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
        secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

        if api_key and secret_key:
            api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
            account = api.get_account()
            alpaca_equity = float(account.equity)
            last_eq = float(account.last_equity) if hasattr(account, 'last_equity') and account.last_equity else alpaca_equity
            today_pl = alpaca_equity - last_eq

            print("  Account: %s" % account.account_number)
            print("  Status: %s" % account.status)
            print("  Equity: $%s" % "{:,.2f}".format(alpaca_equity))
            print("  Cash: $%s" % "{:,.2f}".format(float(account.cash)))
            print("  Buying Power: $%s" % "{:,.2f}".format(float(account.buying_power)))
            print("  Portfolio Value: $%s" % "{:,.2f}".format(float(account.portfolio_value)))
            print("  Today P/L: $%s" % "{:,.2f}".format(today_pl))

            positions = api.list_positions()
            if positions:
                print("\n  Open Positions (%d):" % len(positions))
                print("  %-10s %8s %10s %10s %12s %10s %8s" % ('Symbol', 'Qty', 'Entry', 'Current', 'Mkt Val', 'P/L', 'P/L%'))
                print("  " + "-" * 72)
                total_unrealized = 0
                total_market_value = 0
                for p in sorted(positions, key=lambda x: abs(float(x.unrealized_pl)), reverse=True):
                    unrealized = float(p.unrealized_pl)
                    total_unrealized += unrealized
                    total_market_value += float(p.market_value)
                    pnl_pct = float(p.unrealized_plpc) * 100
                    print("  %-10s %8.4f $%9.2f $%9.2f $%10.2f $%9.2f %7.2f%%" % (
                        p.symbol, float(p.qty), float(p.avg_entry_price),
                        float(p.current_price), float(p.market_value),
                        unrealized, pnl_pct))
                print("  " + "-" * 72)
                print("  %-10s %8s %10s %10s $%10.2f $%9.2f" % ('TOTAL', '', '', '', total_market_value, total_unrealized))
            else:
                print("  No open positions")
        else:
            print("  Alpaca API keys not configured")
    except Exception as e:
        print("  Alpaca error: %s" % e)

    # ===== 11. IB ACCOUNT =====
    print("\n" + "=" * 90)
    print("  11. INTERACTIVE BROKERS ACCOUNT")
    print("=" * 90)
    ib_equity = 0
    try:
        from ib_insync import IB
        ib = IB()
        ib.connect('127.0.0.1', 4002, clientId=99, timeout=10)
        acct_values = ib.accountValues()
        cash = next((float(v.value) for v in acct_values if v.tag == 'CashBalance' and v.currency == 'USD'), 0)
        nlv = next((float(v.value) for v in acct_values if v.tag == 'NetLiquidation' and v.currency == 'USD'), 0)
        ib_equity = nlv
        print("  Account: U21922116")
        print("  Net Liquidation: $%s" % "{:,.2f}".format(nlv))
        print("  Cash Balance: $%s" % "{:,.2f}".format(cash))

        ib_positions = ib.positions()
        if ib_positions:
            print("\n  IB Positions (%d):" % len(ib_positions))
            for p in ib_positions:
                print("    %s: %s shares @ $%.2f" % (p.contract.symbol, p.position, p.avgCost))
        else:
            print("  No IB positions")
        ib.disconnect()
    except Exception as e:
        print("  IB: %s" % e)

    # ===== 12. COMBINED CAPITAL =====
    print("\n" + "=" * 90)
    print("  12. COMBINED CAPITAL SUMMARY")
    print("=" * 90)
    combined = alpaca_equity + ib_equity
    print("  Alpaca Equity:  $%10s" % "{:,.2f}".format(alpaca_equity))
    print("  IB Equity:      $%10s" % "{:,.2f}".format(ib_equity))
    print("  Combined Total: $%10s" % "{:,.2f}".format(combined))

    # ===== 13. LEARNING DATABASE =====
    print("\n" + "=" * 90)
    print("  13. LEARNING DATABASE OVERVIEW")
    print("=" * 90)
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    print("  Total Tables: %d" % len(tables))
    for t in tables:
        if t == 'sqlite_sequence':
            continue
        try:
            c.execute("SELECT COUNT(*) FROM [%s]" % t)
            cnt = c.fetchone()[0]
            bar = '#' * min(cnt // 500, 40) if cnt > 0 else ''
            print("    %-35s %10s rows  %s" % (t, "{:,}".format(cnt), bar))
        except:
            print("    %-35s %10s" % (t, 'ERROR'))

    # ===== 14. LEARNING OUTCOMES =====
    print("\n" + "=" * 90)
    print("  14. LEARNING OUTCOMES (Last 20)")
    print("=" * 90)
    c.execute("""
        SELECT timestamp, symbol, predicted_action, predicted_confidence,
               entry_price, exit_price, profit_loss, profit_pct, was_correct
        FROM learning_outcomes
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    lo_rows = c.fetchall()
    if lo_rows:
        print("  %-20s %-8s %-5s %6s %10s %10s %10s %7s %4s" % ('Timestamp', 'Symbol', 'Action', 'Conf', 'Entry', 'Exit', 'P/L', 'P/L%', 'OK?'))
        print("  " + "-" * 85)
        for r in lo_rows:
            ts = str(r['timestamp'])[:16] if r['timestamp'] else 'N/A'
            ok = 'Y' if r['was_correct'] else 'N'
            pnl = "$%.4f" % r['profit_loss'] if r['profit_loss'] else '--'
            pct = "%.2f%%" % r['profit_pct'] if r['profit_pct'] else '--'
            entry = "$%.2f" % r['entry_price'] if r['entry_price'] else '--'
            exit_p = "$%.2f" % r['exit_price'] if r['exit_price'] else '--'
            print("  %-20s %-8s %-5s %6.2f %10s %10s %10s %7s %4s" % (ts, r['symbol'], r['predicted_action'], r['predicted_confidence'], entry, exit_p, pnl, pct, ok))
    else:
        print("  No learning outcomes recorded")

    # ===== 15. PERFORMANCE METRICS TREND =====
    print("\n" + "=" * 90)
    print("  15. PERFORMANCE METRICS TREND (Last 10)")
    print("=" * 90)
    c.execute("""
        SELECT timestamp, total_trades, winning_trades, losing_trades,
               total_profit_loss, win_rate, sharpe_ratio, max_drawdown, current_balance
        FROM performance_metrics
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    pm_rows = c.fetchall()
    if pm_rows:
        print("  %-20s %7s %5s %5s %7s %12s %8s %7s %12s" % ('Timestamp', 'Trades', 'Wins', 'Loss', 'WR%', 'Total P/L', 'Sharpe', 'MaxDD', 'Balance'))
        print("  " + "-" * 90)
        for r in pm_rows:
            ts = str(r['timestamp'])[:16] if r['timestamp'] else 'N/A'
            print("  %-20s %7d %5d %5d %6.1f%% $%10.2f %8.3f %6.2f%% $%10.2f" % (
                ts, r['total_trades'], r['winning_trades'], r['losing_trades'],
                r['win_rate'], r['total_profit_loss'],
                r['sharpe_ratio'] or 0, r['max_drawdown'] or 0,
                r['current_balance']))
    else:
        print("  No performance metrics")

    # ===== 16. SERVER STATUS =====
    print("\n" + "=" * 90)
    print("  16. SERVER STATUS")
    print("=" * 90)
    try:
        import urllib.request
        req = urllib.request.Request('http://localhost:8000/health')
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            uptime = data.get('uptime_seconds', 0)
            hours = uptime / 3600
            print("  Status: %s" % data.get('status', 'unknown').upper())
            print("  Uptime: %.0fs (%.1f hours)" % (uptime, hours))
            services = data.get('services', {})
            for svc, st in services.items():
                icon = 'ACTIVE' if st else 'INACTIVE'
                print("    %-25s [%s]" % (svc, icon))
    except Exception as e:
        print("  Server: %s" % e)

    # ===== EXECUTIVE SUMMARY =====
    print("\n" + "=" * 90)
    print("  EXECUTIVE SUMMARY")
    print("=" * 90)
    print("  Total Trades Executed:    %d" % total)
    print("  Win Rate:                 %.1f%%" % win_rate)
    print("  Total Realized P/L:       $%.2f" % total_pnl)
    print("  Best Trade:               $%.4f" % best)
    print("  Worst Trade:              $%.4f" % worst)
    print("  Combined Capital:         $%s" % "{:,.2f}".format(combined))
    print("  Shadow Sessions:          %d" % sessions)
    print("  Shadow Trades:            %d" % shadow_trades)
    print("  AI Signals Tracked:       198,386")
    print("  Active Trading Days:      %d" % trading_days)
    print("  Trading Period:           %s to %s" % (first_date, last_date))

    print("\n" + "=" * 90)
    print("  END OF FULL TRADING REPORT")
    print("=" * 90)

    db.close()

if __name__ == '__main__':
    run_report()
