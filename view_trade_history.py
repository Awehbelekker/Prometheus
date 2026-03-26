#!/usr/bin/env python3
"""
📊 PROMETHEUS TRADE HISTORY VIEWER
View and analyze all trades from the learning database
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import sys

def connect_db():
    """Connect to the learning database"""
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[ERROR] Error connecting to database: {e}")
        sys.exit(1)

def get_all_trades(conn, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all trades from database"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM trade_history 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    trades = []
    for row in cursor.fetchall():
        trades.append(dict(row))
    
    return trades

def get_performance_summary(conn) -> Dict[str, Any]:
    """Calculate performance summary"""
    cursor = conn.cursor()
    
    # Total trades
    cursor.execute("SELECT COUNT(*) as total FROM trade_history")
    total_trades = cursor.fetchone()['total']
    
    if total_trades == 0:
        return {
            'total_trades': 0,
            'message': 'No trades yet'
        }
    
    # Get all trades for analysis
    cursor.execute("""
        SELECT action, confidence, price, quantity, total_value, profit_loss
        FROM trade_history
        ORDER BY timestamp DESC
    """)
    
    trades = cursor.fetchall()
    
    # Calculate metrics
    total_value = sum(t['total_value'] or 0 for t in trades)
    avg_confidence = sum(t['confidence'] for t in trades) / len(trades)
    
    # Count by action
    buys = sum(1 for t in trades if t['action'] == 'BUY')
    sells = sum(1 for t in trades if t['action'] == 'SELL')
    holds = sum(1 for t in trades if t['action'] == 'HOLD')
    
    # Profit/Loss (if available)
    total_pnl = sum(t['profit_loss'] or 0 for t in trades)
    winning_trades = sum(1 for t in trades if (t['profit_loss'] or 0) > 0)
    losing_trades = sum(1 for t in trades if (t['profit_loss'] or 0) < 0)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        'total_trades': total_trades,
        'total_value': total_value,
        'avg_confidence': avg_confidence,
        'buys': buys,
        'sells': sells,
        'holds': holds,
        'total_pnl': total_pnl,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate
    }

def get_symbol_breakdown(conn) -> Dict[str, int]:
    """Get trade count by symbol"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, COUNT(*) as count
        FROM trade_history
        GROUP BY symbol
        ORDER BY count DESC
    """)
    
    breakdown = {}
    for row in cursor.fetchall():
        breakdown[row['symbol']] = row['count']
    
    return breakdown

def format_trade(trade: Dict[str, Any]) -> str:
    """Format a single trade for display"""
    timestamp = trade['timestamp'][:19] if trade['timestamp'] else 'Unknown'
    symbol = trade['symbol']
    action = trade['action']
    quantity = trade['quantity']
    price = trade['price']
    total_value = trade['total_value'] or (quantity * price)
    confidence = trade['confidence'] * 100
    broker = trade['broker']
    order_id = trade['order_id'] or 'N/A'
    
    # Color code by action
    action_emoji = {
        'BUY': '🟢',
        'SELL': '🔴',
        'HOLD': '⏸️'
    }
    
    emoji = action_emoji.get(action, '⚪')
    
    return f"""
{emoji} {action} {symbol}
   Time: {timestamp}
   Quantity: {quantity:.8f}
   Price: ${price:.2f}
   Total Value: ${total_value:.2f}
   Confidence: {confidence:.1f}%
   Broker: {broker}
   Order ID: {order_id}
"""

def print_summary(summary: Dict[str, Any]):
    """Print performance summary"""
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 80)
    
    if summary.get('message'):
        print(f"\n{summary['message']}")
        return
    
    print(f"\n📈 Total Trades: {summary['total_trades']}")
    print(f"💰 Total Value Traded: ${summary['total_value']:.2f}")
    print(f"🎯 Average Confidence: {summary['avg_confidence']*100:.1f}%")
    print(f"\n📊 Trade Breakdown:")
    print(f"   🟢 Buys: {summary['buys']}")
    print(f"   🔴 Sells: {summary['sells']}")
    print(f"   ⏸️ Holds: {summary['holds']}")
    
    if summary['total_pnl'] != 0:
        print(f"\n💵 Profit/Loss: ${summary['total_pnl']:.2f}")
        print(f"[CHECK] Winning Trades: {summary['winning_trades']}")
        print(f"[ERROR] Losing Trades: {summary['losing_trades']}")
        print(f"📊 Win Rate: {summary['win_rate']:.1f}%")

def print_symbol_breakdown(breakdown: Dict[str, int]):
    """Print trade count by symbol"""
    print("\n" + "=" * 80)
    print("📊 TRADES BY SYMBOL")
    print("=" * 80)
    
    for symbol, count in breakdown.items():
        print(f"   {symbol}: {count} trades")

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("📊 PROMETHEUS TRADE HISTORY VIEWER")
    print("=" * 80)
    
    # Connect to database
    conn = connect_db()
    
    # Get performance summary
    summary = get_performance_summary(conn)
    print_summary(summary)
    
    # Get symbol breakdown
    if summary.get('total_trades', 0) > 0:
        breakdown = get_symbol_breakdown(conn)
        print_symbol_breakdown(breakdown)
    
    # Get recent trades
    print("\n" + "=" * 80)
    print("📜 RECENT TRADES (Last 20)")
    print("=" * 80)
    
    trades = get_all_trades(conn, limit=20)
    
    if not trades:
        print("\n[WARNING]️ No trades found in database")
    else:
        for trade in trades:
            print(format_trade(trade))
            print("-" * 80)
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[CHECK] Trade history review complete!")
    print("=" * 80)
    print("\nTIP: Run this script anytime to see your trading performance:")
    print("     python view_trade_history.py")
    print("\n")

if __name__ == "__main__":
    main()

