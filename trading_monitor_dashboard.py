#!/usr/bin/env python3
"""
🎮 TRADING MONITOR DASHBOARD
Real-time dashboard for monitoring trading activity with live updates
"""

import sqlite3
import time
import os
from datetime import datetime, timedelta
from collections import defaultdict

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_db_stats():
    """Get comprehensive statistics from database"""
    conn = sqlite3.connect('prometheus_learning.db')
    cursor = conn.cursor()
    
    stats = {}
    
    # Open positions
    cursor.execute("SELECT COUNT(*), SUM(unrealized_pl) FROM open_positions")
    open_count, total_unrealized = cursor.fetchone()
    stats['open_positions'] = open_count or 0
    stats['total_unrealized_pl'] = total_unrealized or 0.0
    
    # Closed positions (last 24h)
    cursor.execute("""
        SELECT COUNT(*), SUM(profit_loss), 
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END)
        FROM trade_history
        WHERE status = 'closed' 
        AND exit_timestamp > datetime('now', '-24 hours')
    """)
    closed_24h, pnl_24h, wins_24h, losses_24h = cursor.fetchone()
    stats['closed_24h'] = closed_24h or 0
    stats['pnl_24h'] = pnl_24h or 0.0
    stats['wins_24h'] = wins_24h or 0
    stats['losses_24h'] = losses_24h or 0
    
    # All-time closed positions
    cursor.execute("""
        SELECT COUNT(*), SUM(profit_loss),
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END),
               AVG(profit_loss),
               MAX(profit_loss),
               MIN(profit_loss)
        FROM trade_history
        WHERE status = 'closed'
    """)
    result = cursor.fetchone()
    if result and result[0]:
        stats['total_closed'] = result[0]
        stats['total_pnl'] = result[1] or 0.0
        stats['total_wins'] = result[2] or 0
        stats['total_losses'] = result[3] or 0
        stats['avg_pnl'] = result[4] or 0.0
        stats['best_trade'] = result[5] or 0.0
        stats['worst_trade'] = result[6] or 0.0
    else:
        stats['total_closed'] = 0
        stats['total_pnl'] = 0.0
        stats['total_wins'] = 0
        stats['total_losses'] = 0
        stats['avg_pnl'] = 0.0
        stats['best_trade'] = 0.0
        stats['worst_trade'] = 0.0
    
    # Pending trades
    cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status = 'pending'")
    stats['pending_trades'] = cursor.fetchone()[0] or 0
    
    # Top symbols
    cursor.execute("""
        SELECT symbol, COUNT(*), AVG(unrealized_pl)
        FROM open_positions
        GROUP BY symbol
        ORDER BY COUNT(*) DESC
        LIMIT 5
    """)
    stats['top_symbols'] = cursor.fetchall()
    
    # Recent exits (last 10)
    cursor.execute("""
        SELECT symbol, exit_timestamp, profit_loss, 
               (profit_loss / (entry_price * quantity)) * 100 as pnl_pct
        FROM trade_history
        WHERE status = 'closed'
        ORDER BY exit_timestamp DESC
        LIMIT 10
    """)
    stats['recent_exits'] = cursor.fetchall()
    
    conn.close()
    return stats

def display_dashboard():
    """Display the dashboard"""
    while True:
        try:
            clear_screen()
            stats = get_db_stats()
            
            # Header
            print("="*100)
            print(f"🎮 PROMETHEUS TRADING MONITOR DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*100)
            print()
            
            # Position Summary
            print("📊 POSITION SUMMARY:")
            print(f"   Open Positions: {stats['open_positions']}")
            print(f"   Unrealized P&L: ${stats['total_unrealized_pl']:.2f}")
            print(f"   Pending Trades: {stats['pending_trades']}")
            print()
            
            # 24-Hour Performance
            win_rate_24h = (stats['wins_24h'] / stats['closed_24h'] * 100) if stats['closed_24h'] > 0 else 0
            emoji_24h = "💚" if stats['pnl_24h'] > 0 else "❤️" if stats['pnl_24h'] < 0 else "💛"
            
            print("📅 LAST 24 HOURS:")
            print(f"   Closed Trades: {stats['closed_24h']}")
            print(f"   P&L: {emoji_24h} ${stats['pnl_24h']:.2f}")
            print(f"   Winners: {stats['wins_24h']} | Losers: {stats['losses_24h']}")
            print(f"   Win Rate: {win_rate_24h:.1f}%")
            print()
            
            # All-Time Performance
            if stats['total_closed'] > 0:
                win_rate_total = (stats['total_wins'] / stats['total_closed'] * 100)
                emoji_total = "💚" if stats['total_pnl'] > 0 else "❤️"
                
                print("🏆 ALL-TIME PERFORMANCE:")
                print(f"   Total Closed: {stats['total_closed']}")
                print(f"   Total P&L: {emoji_total} ${stats['total_pnl']:.2f}")
                print(f"   Winners: {stats['total_wins']} | Losers: {stats['total_losses']}")
                print(f"   Win Rate: {win_rate_total:.1f}%")
                print(f"   Avg Trade: ${stats['avg_pnl']:.2f}")
                print(f"   Best Trade: ${stats['best_trade']:.2f}")
                print(f"   Worst Trade: ${stats['worst_trade']:.2f}")
            else:
                print("🏆 ALL-TIME PERFORMANCE:")
                print("   No closed trades yet")
            print()
            
            # Top Symbols
            if stats['top_symbols']:
                print("🎯 TOP SYMBOLS (Open Positions):")
                for symbol, count, avg_pl in stats['top_symbols']:
                    emoji = "📈" if avg_pl > 0 else "📉"
                    print(f"   {emoji} {symbol}: {count} positions | Avg P&L: ${avg_pl:.2f}")
                print()
            
            # Recent Exits
            if stats['recent_exits']:
                print("🔄 RECENT EXITS:")
                for symbol, exit_time, pnl, pnl_pct in stats['recent_exits'][:5]:
                    emoji = "💰" if pnl > 0 else "📉"
                    time_str = exit_time.split('T')[1][:8] if 'T' in exit_time else exit_time[-8:]
                    print(f"   {emoji} {time_str} | {symbol:10s} | ${pnl:7.2f} ({pnl_pct:+6.2f}%)")
                print()
            
            # Instructions
            print("-"*100)
            print("📝 Monitor is running... Updates every 10 seconds | Press Ctrl+C to stop")
            print("="*100)
            
            time.sleep(10)  # Update every 10 seconds
            
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    display_dashboard()
