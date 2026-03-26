#!/usr/bin/env python3
"""
Comprehensive Returns Report - All Active Sessions Combined
"""
import sqlite3
import json
import os
from datetime import datetime

def generate_comprehensive_returns_report():
    """Generate comprehensive returns report for all active sessions"""
    print("📊 PROMETHEUS COMPREHENSIVE RETURNS REPORT")
    print("=" * 70)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔒 Safe Query Mode: No disruption to active trading sessions")
    print("=" * 70)
    
    # Initialize totals
    total_starting_capital = 0
    total_current_value = 0
    total_pnl = 0
    total_trades = 0
    session_details = []
    
    print("\n🎯 ACTIVE SESSION ANALYSIS:")
    print("-" * 50)
    
    # 1. Enhanced Paper Trading Sessions
    print("\n📈 ENHANCED PAPER TRADING SESSIONS:")
    try:
        if os.path.exists('enhanced_paper_trading.db'):
            conn = sqlite3.connect('enhanced_paper_trading.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, starting_capital, current_value, profit_loss, 
                       return_percentage, trades_count, session_type, created_at
                FROM paper_sessions 
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            paper_sessions = cursor.fetchall()
            
            if paper_sessions:
                for session in paper_sessions:
                    session_id, starting_capital, current_value, profit_loss, return_pct, trades_count, session_type, created_at = session
                    
                    session_details.append({
                        'type': 'Enhanced Paper Trading',
                        'session_id': session_id,
                        'starting_capital': starting_capital,
                        'current_value': current_value,
                        'pnl': profit_loss,
                        'return_pct': return_pct,
                        'trades': trades_count,
                        'session_type': session_type,
                        'created_at': created_at
                    })
                    
                    print(f"   [CHECK] Session: {session_id[:12]}... ({session_type})")
                    print(f"      Starting Capital: ${starting_capital:,.2f}")
                    print(f"      Current Value: ${current_value:,.2f}")
                    print(f"      P&L: ${profit_loss:,.2f} ({return_pct:+.2f}%)")
                    print(f"      Trades: {trades_count}")
                    print(f"      Created: {created_at}")
                    
                    total_starting_capital += starting_capital
                    total_current_value += current_value
                    total_pnl += profit_loss
                    total_trades += trades_count
                    
                print(f"\n   📊 Enhanced Paper Trading Totals:")
                print(f"      Sessions: {len(paper_sessions)}")
                print(f"      Combined P&L: ${sum(s[3] for s in paper_sessions):,.2f}")
                print(f"      Combined Trades: {sum(s[5] for s in paper_sessions):,}")
            else:
                print("   [WARNING]️ No active enhanced paper trading sessions")
            
            conn.close()
        else:
            print("   [ERROR] Enhanced paper trading database not found")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # 2. Internal Paper Trading Session
    print("\n🔬 INTERNAL PAPER TRADING SESSION:")
    try:
        internal_db = 'internal_paper_session_internal_paper_20250930_064848.db'
        if os.path.exists(internal_db):
            conn = sqlite3.connect(internal_db)
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute('SELECT * FROM session_info ORDER BY id DESC LIMIT 1')
            session_info = cursor.fetchone()
            
            if session_info:
                _, session_id, start_time, end_time, starting_capital, current_capital, total_trades_db, total_pnl_db, status, created_at = session_info
                
                # Calculate actual P&L
                actual_pnl = current_capital - starting_capital
                actual_return_pct = (actual_pnl / starting_capital) * 100 if starting_capital > 0 else 0
                
                session_details.append({
                    'type': 'Internal Paper Trading',
                    'session_id': session_id,
                    'starting_capital': starting_capital,
                    'current_value': current_capital,
                    'pnl': actual_pnl,
                    'return_pct': actual_return_pct,
                    'trades': total_trades_db,
                    'session_type': 'internal_paper',
                    'created_at': created_at,
                    'status': status
                })
                
                print(f"   [CHECK] Session: {session_id}")
                print(f"      Starting Capital: ${starting_capital:,.2f}")
                print(f"      Current Value: ${current_capital:,.2f}")
                print(f"      P&L: ${actual_pnl:,.2f} ({actual_return_pct:+.2f}%)")
                print(f"      Trades: {total_trades_db}")
                print(f"      Status: {status}")
                print(f"      Duration: {start_time} to {end_time or 'ACTIVE'}")
                
                # Get recent trades for analysis
                cursor.execute('SELECT COUNT(*), AVG(price) FROM trades')
                trade_stats = cursor.fetchone()
                print(f"      Trade Analysis: {trade_stats[0]} trades, avg price ${trade_stats[1]:.2f}")
                
                total_starting_capital += starting_capital
                total_current_value += current_capital
                total_pnl += actual_pnl
                total_trades += total_trades_db
                
                # [WARNING]️ CRITICAL FINDING
                if actual_pnl < -5000:  # More than 50% loss
                    print(f"      [WARNING]️ CRITICAL: Significant loss detected!")
                    print(f"      📉 Loss Amount: ${abs(actual_pnl):,.2f}")
                    print(f"      📉 Loss Percentage: {abs(actual_return_pct):.2f}%")
            
            conn.close()
        else:
            print("   [ERROR] Internal paper trading database not found")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # 3. Revolutionary Session Reports
    print("\n🚀 REVOLUTIONARY SESSION REPORTS:")
    try:
        rev_files = [f for f in os.listdir('.') if f.startswith('revolutionary_session_report_') and f.endswith('.json')]
        
        if rev_files:
            print(f"   [CHECK] Revolutionary Reports Found: {len(rev_files)}")
            
            for rev_file in rev_files[-2:]:  # Last 2 reports
                try:
                    with open(rev_file, 'r') as f:
                        rev_data = json.load(f)
                    
                    summary = rev_data.get('session_summary', {})
                    session_id = summary.get('session_id', 'Unknown')
                    starting_capital = summary.get('starting_capital', 0)
                    final_value = summary.get('final_value', 0)
                    total_pnl_rev = summary.get('total_pnl', 0)
                    total_return = summary.get('total_return', 0)
                    total_trades_rev = summary.get('total_trades', 0)
                    duration_hours = summary.get('duration_hours', 0)
                    
                    print(f"   📊 Report: {rev_file}")
                    print(f"      Session ID: {session_id}")
                    print(f"      Starting Capital: ${starting_capital:,.2f}")
                    print(f"      Final Value: ${final_value:,.2f}")
                    print(f"      P&L: ${total_pnl_rev:,.2f} ({total_return*100:+.2f}%)")
                    print(f"      Trades: {total_trades_rev}")
                    print(f"      Duration: {duration_hours:.2f} hours")
                    
                    # Note: These are historical reports, not active sessions
                    print(f"      Status: COMPLETED (Historical)")
                    
                except Exception as e:
                    print(f"   [WARNING]️ Error reading {rev_file}: {e}")
        else:
            print("   [WARNING]️ No revolutionary session reports found")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # 4. Current Live Session Configuration
    print("\n🎯 CURRENT LIVE SESSION:")
    try:
        live_session_file = 'trading_session_live_internal_20251001_023631.json'
        if os.path.exists(live_session_file):
            with open(live_session_file, 'r') as f:
                live_data = json.load(f)
            
            print(f"   [CHECK] Live Session Configuration Found")
            print(f"      Session ID: {live_data.get('session_id', 'Unknown')}")
            print(f"      Session Type: {live_data.get('session_type', 'Unknown')}")
            print(f"      Starting Capital: ${live_data.get('starting_capital', 0):,.2f}")
            print(f"      Duration: {live_data.get('duration_hours', 0)} hours")
            print(f"      Start Time: {live_data.get('start_time', 'Unknown')}")
            print(f"      End Time: {live_data.get('end_time', 'Unknown')}")
            print(f"      Status: {live_data.get('status', 'Unknown')}")
            print(f"      Features: {len(live_data.get('features_enabled', {}))} enabled")
            print(f"      Engines: {len(live_data.get('engines_active', []))} active")
        else:
            print("   [WARNING]️ No current live session configuration found")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
    
    # 5. FINAL SUMMARY
    print("\n" + "=" * 70)
    print("📈 COMPREHENSIVE RETURNS SUMMARY - ALL ACTIVE SESSIONS")
    print("=" * 70)
    
    print(f"🎯 Total Active Sessions Analyzed: {len(session_details)}")
    print(f"💰 Combined Starting Capital: ${total_starting_capital:,.2f}")
    print(f"💰 Combined Current Value: ${total_current_value:,.2f}")
    print(f"📊 Combined Total P&L: ${total_pnl:,.2f}")
    print(f"📊 Combined Total Trades: {total_trades:,}")
    
    if total_starting_capital > 0:
        combined_return_pct = (total_pnl / total_starting_capital) * 100
        print(f"📈 Combined Return Percentage: {combined_return_pct:+.2f}%")
        
        # Performance Analysis
        if combined_return_pct > 0:
            print(f"[CHECK] Overall Performance: POSITIVE")
        elif combined_return_pct > -5:
            print(f"[WARNING]️ Overall Performance: MINOR LOSS")
        elif combined_return_pct > -50:
            print(f"[ERROR] Overall Performance: SIGNIFICANT LOSS")
        else:
            print(f"🚨 Overall Performance: CRITICAL LOSS")
    
    if total_trades > 0:
        avg_pnl_per_trade = total_pnl / total_trades
        print(f"📊 Average P&L per Trade: ${avg_pnl_per_trade:,.2f}")
    
    # Session Breakdown
    print(f"\n📋 SESSION BREAKDOWN:")
    for i, session in enumerate(session_details, 1):
        print(f"   {i}. {session['type']}")
        print(f"      P&L: ${session['pnl']:,.2f} ({session['return_pct']:+.2f}%)")
        print(f"      Trades: {session['trades']}")
    
    print("\n" + "=" * 70)
    print("🔒 Report completed without disrupting active trading sessions")
    print("⏰ Data reflects real-time status at report generation time")
    print("🎯 For live updates, re-run this report")
    print("=" * 70)

if __name__ == "__main__":
    generate_comprehensive_returns_report()
