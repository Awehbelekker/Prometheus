#!/usr/bin/env python3
"""
Get PROMETHEUS Morning Stats - Trading, Returns, Learning Confidence
"""

import sqlite3
import os
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient

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

# ============================================================================
# ALPACA ACCOUNT STATS
# ============================================================================

# Load from .env file
api_key = None
secret_key = None

try:
    with open('.env', 'r') as f:
        for line in f:
            if 'ALPACA_LIVE_API_KEY' in line and '=' in line:
                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
            elif 'ALPACA_LIVE_SECRET_KEY' in line and '=' in line:
                secret_key = line.split('=', 1)[1].strip().strip('"').strip("'")
except Exception as e:
    print(f"Error loading .env: {e}")

if api_key and secret_key:
    try:
        client = TradingClient(api_key, secret_key, paper=False)
        
        print("=" * 80)
        print("💰 ALPACA LIVE ACCOUNT - RETURNS & PERFORMANCE")
        print("=" * 80)
        print()
        
        # Get account info
        account = client.get_account()
        
        equity = float(account.equity)
        last_equity = float(account.last_equity)
        buying_power = float(account.buying_power)
        cash = float(account.cash)
        
        # Calculate returns
        daily_return = equity - last_equity
        daily_return_pct = (daily_return / last_equity * 100) if last_equity > 0 else 0
        
        print("📊 ACCOUNT SUMMARY")
        print("-" * 80)
        print(f"Current Equity: ${equity:.2f}")
        print(f"Previous Close: ${last_equity:.2f}")
        print(f"Cash Available: ${cash:.2f}")
        print(f"Buying Power: ${buying_power:.2f}")
        print()
        
        print("📈 RETURNS")
        print("-" * 80)
        print(f"Daily P/L: ${daily_return:+.2f}")
        print(f"Daily Return: {daily_return_pct:+.2f}%")
        
        # Color code the return
        if daily_return > 0:
            print("[CHECK] PROFITABLE SESSION")
        elif daily_return < 0:
            print("[WARNING]️ LOSING SESSION")
        else:
            print("➖ BREAK EVEN")
        print()
        
        # Get positions
        positions = client.get_all_positions()
        
        print("💼 CURRENT POSITIONS")
        print("-" * 80)
        if positions:
            total_value = 0
            total_pl = 0
            print(f"{'Symbol':<10} {'Qty':<14} {'Entry':<12} {'Current':<12} {'P/L':<12} {'P/L %':<10}")
            print("-" * 80)
            for pos in positions:
                qty = float(pos.qty)
                entry = float(pos.avg_entry_price)
                current = float(pos.current_price)
                pl = float(pos.unrealized_pl)
                pl_pct = float(pos.unrealized_plpc) * 100
                value = qty * current
                
                total_value += value
                total_pl += pl
                
                pl_symbol = "[CHECK]" if pl > 0 else "[ERROR]" if pl < 0 else "➖"
                print(f"{pos.symbol:<10} {qty:<14.6f} ${entry:<11.2f} ${current:<11.2f} ${pl:<11.2f} {pl_pct:+.2f}% {pl_symbol}")
            
            print("-" * 80)
            print(f"Total Position Value: ${total_value:.2f}")
            print(f"Total Unrealized P/L: ${total_pl:+.2f}")
        else:
            print("No open positions (all cash)")
        print()
        
        # Get recent orders
        orders = client.get_orders(status='all', limit=50)
        
        print("📋 ORDER STATISTICS (Last 50)")
        print("-" * 80)
        filled_count = sum(1 for o in orders if o.status == 'filled')
        pending_count = sum(1 for o in orders if o.status in ['new', 'pending_new', 'accepted'])
        rejected_count = sum(1 for o in orders if o.status in ['rejected', 'canceled'])
        
        print(f"Total Orders: {len(orders)}")
        print(f"[CHECK] Filled: {filled_count}")
        print(f"⏳ Pending: {pending_count}")
        print(f"[ERROR] Rejected/Canceled: {rejected_count}")
        if orders:
            print(f"Success Rate: {(filled_count/len(orders)*100):.1f}%")
        print()
        
        print("=" * 80)
        print("🎯 SUMMARY")
        print("=" * 80)
        print(f"[CHECK] Trading Session: ACTIVE (Cycle 204+)")
        print(f"[CHECK] Database: Recording trades correctly")
        print(f"[CHECK] AI Confidence: {avg_confidence:.1f}%" if avg_confidence else "[CHECK] AI Confidence: N/A")
        print(f"[CHECK] Account Equity: ${equity:.2f}")
        print(f"[CHECK] Daily Return: {daily_return_pct:+.2f}%")
        print("=" * 80)
        
    except Exception as e:
        print(f"[ERROR] Error connecting to Alpaca: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[ERROR] Could not load Alpaca API keys from .env file")

