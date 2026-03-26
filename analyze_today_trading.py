#!/usr/bin/env python3
"""
Analyze today's trading activity and returns
"""

import sqlite3
from datetime import datetime, timedelta
import os

def analyze_trading():
    print("=" * 80)
    print("📊 PROMETHEUS TRADING PLATFORM - TODAY'S TRADING REPORT")
    print("=" * 80)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check prometheus_learning.db
    if os.path.exists('prometheus_learning.db'):
        print("\n📁 Database: prometheus_learning.db")
        print("-" * 80)
        
        conn = sqlite3.connect('prometheus_learning.db')
        cursor = conn.cursor()
        
        # Total trades in database
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]
        print(f"Total trades in database: {total_trades}")
        
        # Date range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trades")
        dates = cursor.fetchone()
        print(f"Date range: {dates[0]} to {dates[1]}")
        
        # Today's trades
        cursor.execute("SELECT COUNT(*) FROM trades WHERE date(timestamp) = date('now')")
        today_trades = cursor.fetchone()[0]
        print(f"\n🔹 Trades today: {today_trades}")
        
        if today_trades > 0:
            # Today's P&L
            cursor.execute("SELECT SUM(pnl) FROM trades WHERE date(timestamp) = date('now')")
            today_pnl = cursor.fetchone()[0]
            print(f"🔹 Total P&L today: ${today_pnl if today_pnl else 0:.2f}")
            
            # Today's trades by symbol
            cursor.execute("""
                SELECT symbol, COUNT(*) as count, SUM(pnl) as total_pnl
                FROM trades 
                WHERE date(timestamp) = date('now')
                GROUP BY symbol
                ORDER BY count DESC
                LIMIT 10
            """)
            symbol_stats = cursor.fetchall()
            
            if symbol_stats:
                print(f"\n🔹 Top symbols traded today:")
                for symbol, count, pnl in symbol_stats:
                    print(f"   {symbol}: {count} trades | P&L: ${pnl if pnl else 0:.2f}")
            
            # Recent trades
            cursor.execute("""
                SELECT symbol, side, quantity, price, timestamp, pnl
                FROM trades 
                WHERE date(timestamp) = date('now')
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            recent_trades = cursor.fetchall()
            
            if recent_trades:
                print(f"\n🔹 Recent trades today:")
                for trade in recent_trades:
                    symbol, side, qty, price, ts, pnl = trade
                    print(f"   {ts}: {side} {qty} {symbol} @ ${price} | P&L: ${pnl if pnl else 0:.2f}")
        else:
            print("[WARNING]️ No trades executed today")
        
        # All-time P&L
        cursor.execute("SELECT SUM(pnl) FROM trades")
        total_pnl = cursor.fetchone()[0]
        print(f"\n💰 Total P&L all time: ${total_pnl if total_pnl else 0:.2f}")
        
        conn.close()
    else:
        print("\n[ERROR] prometheus_learning.db not found")
    
    # Check enhanced_paper_trading.db
    if os.path.exists('enhanced_paper_trading.db'):
        print("\n\n📁 Database: enhanced_paper_trading.db")
        print("-" * 80)
        
        conn = sqlite3.connect('enhanced_paper_trading.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Today's trades
        try:
            cursor.execute("SELECT COUNT(*) FROM trades WHERE date(timestamp) = date('now')")
            today_trades = cursor.fetchone()[0]
            print(f"\n🔹 Trades today: {today_trades}")
            
            if today_trades > 0:
                # Today's P&L
                cursor.execute("SELECT SUM(pnl) FROM trades WHERE date(timestamp) = date('now')")
                today_pnl = cursor.fetchone()[0]
                print(f"🔹 Total P&L today: ${today_pnl if today_pnl else 0:.2f}")
                
                # Recent trades
                cursor.execute("""
                    SELECT symbol, side, quantity, price, timestamp
                    FROM trades 
                    WHERE date(timestamp) = date('now')
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)
                recent_trades = cursor.fetchall()
                
                if recent_trades:
                    print(f"\n🔹 Recent trades today:")
                    for trade in recent_trades:
                        symbol, side, qty, price, ts = trade
                        print(f"   {ts}: {side} {qty} {symbol} @ ${price}")
        except Exception as e:
            print(f"[WARNING]️ Error querying trades: {e}")
        
        # Check sessions
        try:
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE date(start_time) = date('now')")
            today_sessions = cursor.fetchone()[0]
            print(f"\n🔹 Trading sessions today: {today_sessions}")
            
            if today_sessions > 0:
                cursor.execute("""
                    SELECT session_id, start_time, end_time, total_pnl, total_trades
                    FROM sessions 
                    WHERE date(start_time) = date('now')
                    ORDER BY start_time DESC
                """)
                sessions = cursor.fetchall()
                
                print(f"\n🔹 Today's sessions:")
                for session in sessions:
                    sid, start, end, pnl, trades = session
                    status = "Active" if not end else "Completed"
                    print(f"   Session {sid}: {status} | Trades: {trades} | P&L: ${pnl if pnl else 0:.2f}")
        except Exception as e:
            print(f"[WARNING]️ Error querying sessions: {e}")
        
        conn.close()
    else:
        print("\n[ERROR] enhanced_paper_trading.db not found")
    
    # Check prometheus_trading.db
    if os.path.exists('prometheus_trading.db'):
        print("\n\n📁 Database: prometheus_trading.db")
        print("-" * 80)
        
        conn = sqlite3.connect('prometheus_trading.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Try to get today's data
        try:
            cursor.execute("SELECT COUNT(*) FROM trades WHERE date(timestamp) = date('now')")
            today_trades = cursor.fetchone()[0]
            print(f"\n🔹 Trades today: {today_trades}")
        except Exception as e:
            print(f"[WARNING]️ Error querying trades: {e}")
        
        conn.close()
    else:
        print("\n[ERROR] prometheus_trading.db not found")
    
    print("\n" + "=" * 80)
    print("📊 END OF REPORT")
    print("=" * 80)

if __name__ == "__main__":
    analyze_trading()

