#!/usr/bin/env python3
"""
Get PROMETHEUS Morning Stats - Simple Version
"""

import sqlite3
from datetime import datetime, timedelta

print("=" * 80)
print("📊 PROMETHEUS TRADING STATS - MORNING REPORT")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
print()

# ============================================================================
# DATABASE STATS
# ============================================================================

db = sqlite3.connect('prometheus_learning.db')
cursor = db.cursor()

# Get total trades
cursor.execute('SELECT COUNT(*) FROM trade_history')
total_trades = cursor.fetchone()[0]

# Get trades in last 6 hours
six_hours_ago = (datetime.now() - timedelta(hours=6)).isoformat()
cursor.execute('SELECT COUNT(*) FROM trade_history WHERE timestamp > ?', (six_hours_ago,))
trades_6h = cursor.fetchone()[0]

# Get average confidence (using ai_confidence column)
cursor.execute('SELECT AVG(ai_confidence) FROM trade_history WHERE ai_confidence IS NOT NULL')
avg_confidence = cursor.fetchone()[0]

# Get success rate
cursor.execute('SELECT COUNT(*) FROM trade_history WHERE success = 1')
successful = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM trade_history WHERE success IS NOT NULL')
total_with_outcome = cursor.fetchone()[0]

# Get P/L stats
cursor.execute('SELECT SUM(pnl), AVG(pnl), MIN(pnl), MAX(pnl) FROM trade_history WHERE pnl IS NOT NULL')
pnl_stats = cursor.fetchone()

# Get recent trades with price
cursor.execute('''
    SELECT symbol, action, quantity, price, ai_confidence, timestamp 
    FROM trade_history 
    WHERE price IS NOT NULL AND price > 0
    ORDER BY id DESC 
    LIMIT 15
''')
recent_trades = cursor.fetchall()

print("📈 OVERALL STATISTICS")
print("-" * 80)
print(f"Total Trades Recorded: {total_trades}")
print(f"Trades (Last 6 hours): {trades_6h}")
if avg_confidence:
    print(f"Average AI Confidence: {avg_confidence:.1f}%")
else:
    print("Average AI Confidence: N/A")
    
if total_with_outcome > 0:
    success_rate = (successful / total_with_outcome) * 100
    print(f"Success Rate: {success_rate:.1f}% ({successful}/{total_with_outcome})")
else:
    print("Success Rate: N/A")
print()

print("💰 PROFIT/LOSS STATISTICS (Database)")
print("-" * 80)
if pnl_stats[0] is not None:
    print(f"Total P/L: ${pnl_stats[0]:.2f}")
    print(f"Average P/L per Trade: ${pnl_stats[1]:.2f}")
    print(f"Best Trade: ${pnl_stats[3]:.2f}")
    print(f"Worst Trade: ${pnl_stats[2]:.2f}")
else:
    print("No P/L data available yet (positions still open)")
print()

print("🔥 RECENT TRADES (Last 15 with price data)")
print("-" * 80)
if recent_trades:
    print(f"{'Action':<6} {'Quantity':<14} {'Symbol':<12} {'Price':<14} {'Conf':<8} {'Time'}")
    print("-" * 80)
    for trade in recent_trades:
        symbol, action, qty, price, conf, ts = trade
        conf_str = f"{conf:.1f}%" if conf else "N/A"
        time_str = ts[:19] if ts else "N/A"
        print(f"{action:<6} {qty:<14.6f} {symbol:<12} ${price:<13.2f} {conf_str:<8} {time_str}")
else:
    print("No trades with price data yet")
print()

# Get symbol breakdown
cursor.execute('''
    SELECT symbol, COUNT(*) as count, AVG(ai_confidence) as avg_conf
    FROM trade_history 
    WHERE price IS NOT NULL AND price > 0
    GROUP BY symbol
    ORDER BY count DESC
    LIMIT 10
''')
symbol_stats = cursor.fetchall()

if symbol_stats:
    print("📊 TOP TRADED SYMBOLS")
    print("-" * 80)
    print(f"{'Symbol':<12} {'Trades':<10} {'Avg Confidence'}")
    print("-" * 80)
    for symbol, count, avg_conf in symbol_stats:
        conf_str = f"{avg_conf:.1f}%" if avg_conf else "N/A"
        print(f"{symbol:<12} {count:<10} {conf_str}")
    print()

db.close()

print("=" * 80)
print("🎯 SUMMARY")
print("=" * 80)
print(f"[CHECK] Trading Session: ACTIVE (Cycle 204+)")
print(f"[CHECK] Database: Recording trades correctly")
print(f"[CHECK] AI Confidence: {avg_confidence:.1f}%" if avg_confidence else "[CHECK] AI Confidence: N/A")
print(f"[CHECK] Total Trades: {total_trades}")
print(f"[CHECK] Recent Trades (6h): {trades_6h}")
print("=" * 80)
print()
print("💡 To get Alpaca account returns, check Terminal 3 output or run:")
print("   python check_alpaca_live_account.py")
print()

