#!/usr/bin/env python3
"""
Database Performance Benchmark for PROMETHEUS Trading Platform
"""

import sqlite3
import time
from datetime import datetime, timedelta
import statistics

def benchmark_database_performance():
    """Benchmark database query performance"""
    
    print("📊 DATABASE PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    db_path = "enhanced_paper_trading.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Session retrieval performance
        print("\n🔍 Test 1: Session Retrieval Performance")
        session_times = []
        
        for i in range(10):
            start_time = time.time()
            cursor.execute("SELECT * FROM paper_sessions WHERE status = 'active'")
            results = cursor.fetchall()
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            session_times.append(query_time)
        
        avg_session_time = statistics.mean(session_times)
        print(f"   Average query time: {avg_session_time:.2f}ms")
        print(f"   Active sessions found: {len(results)}")
        print(f"   Target: <100ms - {'[CHECK] PASS' if avg_session_time < 100 else '[ERROR] FAIL'}")
        
        # Test 2: Market data freshness
        print("\n🔍 Test 2: Market Data Freshness")
        cursor.execute("SELECT symbol, price, updated_at FROM market_data ORDER BY updated_at DESC LIMIT 10")
        market_data = cursor.fetchall()
        
        if market_data:
            latest_update = market_data[0][2]
            print(f"   Latest market data update: {latest_update}")
            
            # Parse timestamp and check freshness
            try:
                update_time = datetime.fromisoformat(latest_update.replace('Z', '+00:00'))
                now = datetime.now()
                age_seconds = (now - update_time).total_seconds()
                
                print(f"   Data age: {age_seconds:.1f} seconds")
                print(f"   Target: <300 seconds - {'[CHECK] PASS' if age_seconds < 300 else '[ERROR] FAIL'}")
                
                print(f"   Market data symbols: {len(market_data)} symbols")
                for symbol, price, updated_at in market_data[:5]:
                    print(f"     {symbol}: ${price:.2f} (updated: {updated_at})")
                    
            except Exception as e:
                print(f"   [WARNING]️ Could not parse timestamp: {e}")
        else:
            print("   [ERROR] No market data found")
        
        # Test 3: Trade execution analysis
        print("\n🔍 Test 3: Trade Execution Analysis")
        cursor.execute("SELECT COUNT(*) FROM paper_trades")
        total_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE created_at > datetime('now', '-1 hour')")
        recent_trades = cursor.fetchone()[0]
        
        print(f"   Total trades in database: {total_trades}")
        print(f"   Trades in last hour: {recent_trades}")
        
        if total_trades > 0:
            cursor.execute("""
                SELECT symbol, side, quantity, price, profit_loss, created_at 
                FROM paper_trades 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_trade_details = cursor.fetchall()
            
            print(f"   Recent trades:")
            for trade in recent_trade_details:
                symbol, side, quantity, price, pnl, created_at = trade
                pnl_str = f"${pnl:.2f}" if pnl is not None else "N/A"
                print(f"     {symbol} {side} {quantity} @ ${price:.2f} - P&L: {pnl_str} ({created_at})")
        
        # Test 4: Active session details
        print("\n🔍 Test 4: Active Session Performance Analysis")
        cursor.execute("""
            SELECT session_id, user_id, session_type, starting_capital, 
                   current_value, profit_loss, return_percentage, trades_count, 
                   created_at, started_at
            FROM paper_sessions 
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        
        active_sessions = cursor.fetchall()
        
        if active_sessions:
            print(f"   Active sessions: {len(active_sessions)}")
            
            for session in active_sessions:
                (session_id, user_id, session_type, starting_capital, 
                 current_value, profit_loss, return_pct, trades_count, 
                 created_at, started_at) = session
                
                duration_type = "24h" if session_type == "24_hour" else "48h" if session_type == "48_hour" else session_type
                
                print(f"\n   📈 {duration_type} Session ({session_id[:8]}...):")
                print(f"      User: {user_id}")
                print(f"      Starting Capital: ${starting_capital:,.2f}")
                print(f"      Current Value: ${current_value:,.2f}")
                print(f"      P&L: ${profit_loss:,.2f} ({return_pct:+.2f}%)")
                print(f"      Trades: {trades_count}")
                print(f"      Created: {created_at}")
                print(f"      Started: {started_at}")
                
                # Calculate session runtime
                if started_at:
                    try:
                        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                        runtime = datetime.now() - start_time
                        runtime_hours = runtime.total_seconds() / 3600
                        print(f"      Runtime: {runtime_hours:.1f} hours")
                        
                        # Project performance
                        if runtime_hours > 0:
                            hourly_return = return_pct / runtime_hours
                            target_hours = 24 if session_type == "24_hour" else 48
                            projected_return = hourly_return * target_hours
                            print(f"      Projected Final Return: {projected_return:+.2f}%")
                            
                            target_return = 6.0  # Minimum target
                            on_track = projected_return >= target_return
                            print(f"      Target Achievement: {'[CHECK] ON TRACK' if on_track else '[WARNING]️ BELOW TARGET'}")
                            
                    except Exception as e:
                        print(f"      [WARNING]️ Could not calculate runtime: {e}")
        else:
            print("   [ERROR] No active sessions found")
        
        # Test 5: Database size and optimization
        print("\n🔍 Test 5: Database Optimization")
        cursor.execute("SELECT COUNT(*) FROM paper_sessions")
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paper_trades")
        trade_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM market_data")
        market_data_count = cursor.fetchone()[0]
        
        print(f"   Total sessions: {session_count}")
        print(f"   Total trades: {trade_count}")
        print(f"   Market data records: {market_data_count}")
        
        # Check database file size
        import os
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            print(f"   Database size: {db_size:.2f} KB")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[CHECK] DATABASE BENCHMARK COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Database benchmark error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    benchmark_database_performance()
