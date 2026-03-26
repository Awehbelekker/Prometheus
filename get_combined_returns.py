#!/usr/bin/env python3
"""
Get Combined Returns Across All Active Sessions
Safe query without disrupting trading sessions
"""
import requests
import json
import sqlite3
import os
from datetime import datetime

def get_combined_returns():
    """Get combined returns from all active sessions"""
    print("📊 PROMETHEUS COMBINED RETURNS - ALL ACTIVE SESSIONS")
    print("=" * 60)
    print(f"Query Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_pnl = 0
    total_trades = 0
    total_starting_capital = 0
    total_current_value = 0
    active_sessions_count = 0
    
    # 1. Check Revolutionary Server Performance
    print("🚀 REVOLUTIONARY ENGINES:")
    try:
        response = requests.get('http://localhost:8002/api/revolutionary/performance', timeout=5)
        if response.status_code == 200:
            rev_data = response.json()
            summary = rev_data.get('summary', {})
            
            rev_pnl = summary.get('total_pnl_total', 0)
            rev_today_pnl = summary.get('total_pnl_today', 0)
            rev_trades = summary.get('total_trades', 0)
            
            print(f"   [CHECK] Status: ACTIVE")
            print(f"   💰 Total P&L: ${rev_pnl:,.2f}")
            print(f"   💰 Today P&L: ${rev_today_pnl:,.2f}")
            print(f"   📊 Total Trades: {rev_trades:,}")
            print(f"   📈 Win Rate: {summary.get('win_rate', 0):.1%}")
            
            total_pnl += rev_pnl
            total_trades += rev_trades
            active_sessions_count += 1
        else:
            print(f"   [ERROR] Status: OFFLINE (HTTP {response.status_code})")
    except Exception as e:
        print(f"   [ERROR] Status: ERROR - {e}")
    
    # 2. Check Paper Trading Sessions
    print("\n📈 PAPER TRADING SESSIONS:")
    try:
        # Enhanced paper trading database
        if os.path.exists('enhanced_paper_trading.db'):
            conn = sqlite3.connect('enhanced_paper_trading.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, starting_capital, current_value, profit_loss, 
                       return_percentage, trades_count, session_type
                FROM paper_sessions 
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            active_paper_sessions = cursor.fetchall()
            
            if active_paper_sessions:
                print(f"   [CHECK] Active Sessions: {len(active_paper_sessions)}")
                
                session_total_pnl = 0
                session_total_trades = 0
                session_total_starting = 0
                session_total_current = 0
                
                for session in active_paper_sessions:
                    session_id, starting_capital, current_value, profit_loss, return_pct, trades_count, session_type = session
                    
                    print(f"   📊 Session {session_id[:8]}... ({session_type}):")
                    print(f"      Starting: ${starting_capital:,.2f}")
                    print(f"      Current: ${current_value:,.2f}")
                    print(f"      P&L: ${profit_loss:,.2f} ({return_pct:+.2f}%)")
                    print(f"      Trades: {trades_count}")
                    
                    session_total_pnl += profit_loss
                    session_total_trades += trades_count
                    session_total_starting += starting_capital
                    session_total_current += current_value
                
                print(f"   💰 Paper Trading Total P&L: ${session_total_pnl:,.2f}")
                print(f"   📊 Paper Trading Total Trades: {session_total_trades:,}")
                
                total_pnl += session_total_pnl
                total_trades += session_total_trades
                total_starting_capital += session_total_starting
                total_current_value += session_total_current
                active_sessions_count += len(active_paper_sessions)
                
            else:
                print("   [WARNING]️ No active paper trading sessions found")
            
            conn.close()
        else:
            print("   [ERROR] Enhanced paper trading database not found")
            
    except Exception as e:
        print(f"   [ERROR] Paper trading error: {e}")
    
    # 3. Check Internal Paper Trading Sessions
    print("\n🔬 INTERNAL PAPER TRADING:")
    try:
        # Look for internal session databases
        internal_dbs = [f for f in os.listdir('.') if f.startswith('internal_paper_session_') and f.endswith('.db')]
        
        if internal_dbs:
            print(f"   [CHECK] Internal Session DBs Found: {len(internal_dbs)}")
            
            internal_total_pnl = 0
            internal_total_trades = 0
            
            for db_file in internal_dbs[-3:]:  # Check last 3 files
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Get session info
                    cursor.execute('SELECT session_id, starting_capital, current_capital, total_pnl, total_trades FROM session_info ORDER BY id DESC LIMIT 1')
                    session_info = cursor.fetchone()
                    
                    if session_info:
                        session_id, starting_capital, current_capital, total_pnl_db, total_trades_db = session_info
                        print(f"   📊 {db_file[:25]}...:")
                        print(f"      Starting: ${starting_capital:,.2f}")
                        print(f"      Current: ${current_capital:,.2f}")
                        print(f"      P&L: ${total_pnl_db:,.2f}")
                        print(f"      Trades: {total_trades_db}")
                        
                        internal_total_pnl += total_pnl_db
                        internal_total_trades += total_trades_db
                    
                    conn.close()
                except Exception as e:
                    print(f"   [WARNING]️ Error reading {db_file}: {e}")
            
            print(f"   💰 Internal Trading Total P&L: ${internal_total_pnl:,.2f}")
            print(f"   📊 Internal Trading Total Trades: {internal_total_trades:,}")
            
            total_pnl += internal_total_pnl
            total_trades += internal_total_trades
            
        else:
            print("   [WARNING]️ No internal paper trading databases found")
            
    except Exception as e:
        print(f"   [ERROR] Internal trading error: {e}")
    
    # 4. Check Live Trading Status
    print("\n💰 LIVE TRADING CONTROL:")
    try:
        response = requests.get('http://localhost:8000/api/live-trading/status', timeout=5)
        if response.status_code == 200:
            live_data = response.json()
            active_live_sessions = live_data.get('active_sessions', [])
            
            if active_live_sessions:
                print(f"   [CHECK] Active Live Sessions: {len(active_live_sessions)}")
                
                live_total_pnl = 0
                live_total_trades = 0
                
                for session in active_live_sessions:
                    session_id = session.get('session_id', 'Unknown')
                    capital = session.get('capital', 0)
                    current_pnl = session.get('current_pnl', 0)
                    trades = session.get('trades_executed', 0)
                    
                    print(f"   📊 Live Session {session_id[:8]}...:")
                    print(f"      Capital: ${capital:,.2f}")
                    print(f"      P&L: ${current_pnl:,.2f}")
                    print(f"      Trades: {trades}")
                    
                    live_total_pnl += current_pnl
                    live_total_trades += trades
                
                print(f"   💰 Live Trading Total P&L: ${live_total_pnl:,.2f}")
                print(f"   📊 Live Trading Total Trades: {live_total_trades:,}")
                
                total_pnl += live_total_pnl
                total_trades += live_total_trades
                active_sessions_count += len(active_live_sessions)
                
            else:
                print("   [WARNING]️ No active live trading sessions")
        else:
            print(f"   [ERROR] Live trading API unavailable (HTTP {response.status_code})")
    except Exception as e:
        print(f"   [ERROR] Live trading error: {e}")
    
    # 5. Final Summary
    print("\n" + "=" * 60)
    print("📈 COMBINED RETURNS SUMMARY - ALL ACTIVE SESSIONS")
    print("=" * 60)
    print(f"🎯 Total Active Sessions: {active_sessions_count}")
    print(f"💰 Combined Total P&L: ${total_pnl:,.2f}")
    print(f"📊 Combined Total Trades: {total_trades:,}")
    
    if total_starting_capital > 0:
        combined_return_pct = (total_pnl / total_starting_capital) * 100
        print(f"📈 Combined Return %: {combined_return_pct:+.2f}%")
        print(f"💵 Total Starting Capital: ${total_starting_capital:,.2f}")
        print(f"💵 Total Current Value: ${total_current_value:,.2f}")
    
    if total_trades > 0:
        avg_pnl_per_trade = total_pnl / total_trades
        print(f"📊 Average P&L per Trade: ${avg_pnl_per_trade:,.2f}")
    
    print("=" * 60)
    print("🔒 Session Safety: All queries performed without disruption")
    print("⏰ Data reflects real-time status at query time")
    print("=" * 60)

if __name__ == "__main__":
    get_combined_returns()
