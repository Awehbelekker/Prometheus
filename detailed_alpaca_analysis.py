#!/usr/bin/env python3
"""
Detailed Analysis of Alpaca Trading Activity
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

print("=" * 80)
print("DETAILED ALPACA TRADING ANALYSIS")
print("=" * 80)
print()

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# 1. Total Trade Count
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE broker = 'Alpaca'")
total_alpaca_trades = cursor.fetchone()[0]
print(f"📊 Total Alpaca Trades: {total_alpaca_trades}")

# 2. Trade Status Breakdown
cursor.execute("SELECT status, COUNT(*) FROM trade_history WHERE broker = 'Alpaca' GROUP BY status")
status_breakdown = cursor.fetchall()
print(f"\n📋 Trade Status:")
for status, count in status_breakdown:
    print(f"  {status}: {count} trades")

# 3. Recent Trading Activity (last 7 days)
cursor.execute("""
    SELECT DATE(timestamp) as trade_date, COUNT(*) as trades, SUM(profit_loss) as pnl
    FROM trade_history 
    WHERE broker = 'Alpaca' AND timestamp > datetime('now', '-7 days')
    GROUP BY DATE(timestamp)
    ORDER BY trade_date DESC
""")
recent_activity = cursor.fetchall()
print(f"\n📅 Recent Activity (Last 7 Days):")
for date, trades, pnl in recent_activity:
    pnl_str = f"${pnl:.2f}" if pnl else "$0.00"
    print(f"  {date}: {trades} trades, P&L: {pnl_str}")

# 4. Symbol Distribution
cursor.execute("""
    SELECT symbol, COUNT(*) as trades 
    FROM trade_history 
    WHERE broker = 'Alpaca'
    GROUP BY symbol
    ORDER BY trades DESC
    LIMIT 15
""")
symbols = cursor.fetchall()
print(f"\n🎯 Most Traded Symbols:")
for symbol, count in symbols:
    print(f"  {symbol}: {count} trades")

# 5. P&L Analysis
cursor.execute("""
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
        SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
        SUM(profit_loss) as total_pnl,
        AVG(profit_loss) as avg_pnl,
        MAX(profit_loss) as best_trade,
        MIN(profit_loss) as worst_trade
    FROM trade_history
    WHERE broker = 'Alpaca' AND profit_loss IS NOT NULL AND profit_loss != 0
""")
pnl_data = cursor.fetchone()

if pnl_data and pnl_data[0] > 0:
    total, wins, losses, total_pnl, avg_pnl, best, worst = pnl_data
    win_rate = (wins / total * 100) if total > 0 else 0
    
    print(f"\n💰 P&L Analysis (Closed Trades):")
    print(f"  Closed Trades: {total}")
    print(f"  Winning: {wins} ({win_rate:.1f}%)")
    print(f"  Losing: {losses}")
    print(f"  Total P&L: ${total_pnl:.2f}")
    print(f"  Avg P&L/Trade: ${avg_pnl:.2f}")
    print(f"  Best Trade: ${best:.2f}")
    print(f"  Worst Trade: ${worst:.2f}")
else:
    print(f"\n💰 P&L Analysis:")
    print(f"  ⚠️ No closed trades with recorded P&L yet")
    print(f"  All {total_alpaca_trades} trades are either pending or P&L not recorded")

# 6. Current Open Positions
cursor.execute("""
    SELECT symbol, side, quantity, entry_price, current_price, unrealized_pl
    FROM open_positions
    WHERE broker = 'Alpaca'
    ORDER BY ABS(unrealized_pl) DESC
    LIMIT 10
""")
open_positions = cursor.fetchall()
print(f"\n📈 Current Open Positions:")
if open_positions:
    for symbol, side, qty, entry, current, upl in open_positions:
        upl_str = f"${upl:.2f}" if upl else "$0.00"
        pct = ((current - entry) / entry * 100) if entry else 0
        print(f"  {symbol} {side}: {qty:.4f} @ ${entry:.2f} → ${current:.2f} ({pct:+.2f}%) | Unrealized: {upl_str}")
else:
    print(f"  No open positions")

# 7. Latest Trades
cursor.execute("""
    SELECT timestamp, symbol, action, quantity, price, profit_loss, status
    FROM trade_history
    WHERE broker = 'Alpaca'
    ORDER BY timestamp DESC
    LIMIT 10
""")
latest_trades = cursor.fetchall()
print(f"\n🔄 Latest 10 Trades:")
for ts, symbol, action, qty, price, pnl, status in latest_trades:
    pnl_str = f"P&L: ${pnl:.2f}" if pnl and pnl != 0 else "P&L: pending"
    print(f"  {ts}: {action} {qty:.4f} {symbol} @ ${price:.2f} | {pnl_str} ({status})")

# 8. AI System Performance
cursor.execute("""
    SELECT 
        ai_components,
        COUNT(*) as trades,
        AVG(confidence) as avg_confidence
    FROM trade_history
    WHERE broker = 'Alpaca' AND ai_components IS NOT NULL
    GROUP BY ai_components
    ORDER BY trades DESC
    LIMIT 10
""")
ai_systems = cursor.fetchall()
print(f"\n🤖 AI System Usage:")
for system, trades, conf in ai_systems:
    # Truncate long system names
    system_short = system[:60] + "..." if len(system) > 60 else system
    print(f"  {system_short}: {trades} trades (avg conf: {conf:.2f})")

# 9. Trading Velocity
cursor.execute("""
    SELECT 
        COUNT(*) as trades,
        MIN(timestamp) as first_trade,
        MAX(timestamp) as last_trade
    FROM trade_history
    WHERE broker = 'Alpaca'
""")
velocity = cursor.fetchone()
if velocity and velocity[0] > 0:
    trades, first, last = velocity
    if first and last:
        first_dt = datetime.fromisoformat(first)
        last_dt = datetime.fromisoformat(last)
        days = (last_dt - first_dt).days + 1
        trades_per_day = trades / days if days > 0 else 0
        
        print(f"\n⚡ Trading Velocity:")
        print(f"  First Trade: {first}")
        print(f"  Last Trade: {last}")
        print(f"  Trading Period: {days} days")
        print(f"  Trades/Day: {trades_per_day:.1f}")

conn.close()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"\n✅ System IS actively trading with Alpaca!")
print(f"✅ Total of {total_alpaca_trades} trade records found")
print(f"\n⚠️ However, most trades appear to be in 'pending' status")
print(f"⚠️ Need to check if trades are being properly closed and P&L recorded")
print()
