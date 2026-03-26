#!/usr/bin/env python3
"""
PROMETHEUS Multi-Strategy Shadow Comparison Tool

Quick script to view and compare multi-strategy shadow trading results.
Run after multi_strategy_shadow_runner.py to see which strategy is winning.

Usage:
    python _strategy_comparison.py              # Show leaderboard
    python _strategy_comparison.py --detail     # Show detailed breakdown
    python _strategy_comparison.py --history    # Show performance over time
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB = 'prometheus_learning.db'


def show_leaderboard():
    """Show the most recent multi-strategy leaderboard"""
    db = sqlite3.connect(DB)
    cursor = db.cursor()

    # Get most recent run
    cursor.execute("""
        SELECT DISTINCT run_id, completed_at
        FROM multi_strategy_leaderboard
        ORDER BY completed_at DESC LIMIT 1
    """)
    run = cursor.fetchone()

    if not run:
        # Fall back to snapshots
        cursor.execute("""
            SELECT DISTINCT run_id FROM multi_strategy_snapshots
            ORDER BY timestamp DESC LIMIT 1
        """)
        run_row = cursor.fetchone()
        if run_row:
            show_live_snapshots(run_row[0])
        else:
            print("No multi-strategy results found.")
            print("Run: python multi_strategy_shadow_runner.py --iterations 50")
        db.close()
        return

    run_id, completed = run
    print(f"\n{'='*90}")
    print(f"🏆 MULTI-STRATEGY LEADERBOARD — Run: {run_id}")
    print(f"   Completed: {completed}")
    print(f"{'='*90}")

    cursor.execute("""
        SELECT strategy_name, rank, final_capital, total_return_pct,
               total_trades, win_rate, sharpe_ratio, max_drawdown, avg_trade_pnl
        FROM multi_strategy_leaderboard
        WHERE run_id = ?
        ORDER BY rank
    """, (run_id,))

    rows = cursor.fetchall()
    print(f"{'Rank':<5} {'Strategy':<18} {'Capital':>12} {'Return':>9} {'Trades':>7} {'WR':>7} {'Sharpe':>8} {'MaxDD':>8} {'AvgPnL':>10}")
    print("-" * 90)

    for name, rank, capital, ret, trades, wr, sharpe, dd, avg_pnl in rows:
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        sign = "+" if ret >= 0 else ""
        print(f"{medal}{rank:<3} {name:<18} ${capital:>10,.2f} {sign}{ret:>7.2f}% {trades:>6} "
              f"{wr*100:>5.1f}% {sharpe:>7.2f} {dd*100:>6.2f}% ${avg_pnl:>8,.2f}")

    print("=" * 90)
    db.close()


def show_live_snapshots(run_id: str = None):
    """Show live snapshots for an active or recent run"""
    db = sqlite3.connect(DB)
    cursor = db.cursor()

    if not run_id:
        cursor.execute("SELECT DISTINCT run_id FROM multi_strategy_snapshots ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("No snapshots found.")
            db.close()
            return
        run_id = row[0]

    # Get latest snapshot per strategy
    cursor.execute("""
        SELECT strategy_name, MAX(iteration) as last_iter, capital, total_trades,
               win_rate, total_pnl, sharpe_ratio, max_drawdown, open_positions
        FROM multi_strategy_snapshots
        WHERE run_id = ?
        GROUP BY strategy_name
        ORDER BY capital DESC
    """, (run_id,))

    rows = cursor.fetchall()
    if not rows:
        print("No snapshots for this run.")
        db.close()
        return

    starting_capital = 100000.0  # Default

    print(f"\n{'='*90}")
    print(f"📊 LIVE STRATEGY SNAPSHOTS — Run: {run_id}")
    print(f"{'='*90}")
    print(f"{'#':<4} {'Strategy':<18} {'Capital':>12} {'Return':>9} {'Trades':>7} {'WR':>7} {'PnL':>10} {'Open':>5} {'Iter':>6}")
    print("-" * 90)

    for i, (name, itr, capital, trades, wr, pnl, sharpe, dd, open_pos) in enumerate(rows, 1):
        ret_pct = ((capital - starting_capital) / starting_capital) * 100
        sign = "+" if ret_pct >= 0 else ""
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{medal}{i:<2} {name:<18} ${capital:>10,.2f} {sign}{ret_pct:>7.2f}% {trades:>6} "
              f"{wr*100:>5.1f}% ${pnl:>8,.2f} {open_pos:>4} {itr:>5}")

    print("=" * 90)
    db.close()


def show_detail():
    """Show detailed breakdown per strategy including trades"""
    db = sqlite3.connect(DB)
    cursor = db.cursor()

    # Get shadow trades grouped by session/config
    cursor.execute("""
        SELECT session_id, symbol, action, quantity, entry_price, exit_price,
               pnl, pnl_pct, status, exit_reason, confidence, ai_components
        FROM shadow_trade_history
        WHERE session_id LIKE 'multi_%'
        ORDER BY session_id, timestamp DESC
        LIMIT 200
    """)

    rows = cursor.fetchall()
    if not rows:
        print("No multi-strategy trades found yet.")
        db.close()
        return

    current_session = None
    for row in rows:
        session, sym, action, qty, entry, exit_p, pnl, pnl_pct, status, reason, conf, ai = row
        strategy = session.split('_')[-1] if session else 'unknown'

        if session != current_session:
            current_session = session
            print(f"\n{'='*80}")
            print(f"Strategy: {strategy.upper()} (session: {session})")
            print(f"{'Symbol':<10} {'Action':<6} {'Qty':>8} {'Entry':>10} {'Exit':>10} {'PnL':>10} {'PnL%':>8} {'Status':<8} {'Reason'}")
            print("-" * 80)

        exit_str = f"${exit_p:>8.2f}" if exit_p else "     open"
        pnl_str = f"${pnl:>8.2f}" if pnl else "       -"
        pnl_pct_str = f"{pnl_pct:>6.2f}%" if pnl_pct else "     -"
        print(f"{sym:<10} {action:<6} {qty:>8.2f} ${entry:>8.2f} {exit_str} {pnl_str} {pnl_pct_str} {status:<8} {reason or ''}")

    print("=" * 80)
    db.close()


def show_all_shadow_sessions():
    """Show ALL shadow trading sessions (not just multi-strategy)"""
    db = sqlite3.connect(DB)
    cursor = db.cursor()

    cursor.execute("""
        SELECT session_id, config_name, start_time, 
               starting_capital, current_capital,
               total_trades, winning_trades, losing_trades
        FROM shadow_sessions
        ORDER BY start_time DESC
        LIMIT 30
    """)

    rows = cursor.fetchall()
    if not rows:
        print("No shadow sessions found.")
        db.close()
        return

    print(f"\n{'='*90}")
    print(f"📋 ALL SHADOW TRADING SESSIONS (last 30)")
    print(f"{'='*90}")
    print(f"{'Session ID':<40} {'Config':<16} {'Capital':>12} {'Trades':>7} {'W/L':>8}")
    print("-" * 90)

    for sess_id, config, start, start_cap, cur_cap, trades, wins, losses in rows:
        cap_str = f"${cur_cap:,.0f}" if cur_cap else f"${start_cap:,.0f}"
        wl = f"{wins or 0}/{losses or 0}"
        print(f"{sess_id:<40} {config or 'default':<16} {cap_str:>12} {trades or 0:>6} {wl:>8}")

    print("=" * 90)
    db.close()


if __name__ == '__main__':
    import sys

    if '--detail' in sys.argv:
        show_detail()
    elif '--history' in sys.argv or '--sessions' in sys.argv:
        show_all_shadow_sessions()
    elif '--live' in sys.argv:
        show_live_snapshots()
    else:
        show_leaderboard()
        print()
        show_live_snapshots()
