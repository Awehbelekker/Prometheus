#!/usr/bin/env python3
"""
PROMETHEUS LIVE TRADING MONITOR
Monitors for successful trade executions after database fixes
"""
import sqlite3
import os
import time
from datetime import datetime, timedelta

def get_recent_trading_activity():
    """Get recent trading activity from the database"""
    db_path = "databases/prometheus_trading.db"
    if not os.path.exists(db_path):
        return {"error": "Database not found"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get open positions
        cursor.execute("SELECT COUNT(*) FROM open_positions WHERE status = 'OPEN'")
        open_positions = cursor.fetchone()[0]
        
        # Get recent positions (last hour)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM open_positions WHERE opened_at > ?", (one_hour_ago,))
        recent_positions = cursor.fetchone()[0]
        
        # Get all positions for details
        cursor.execute("""
            SELECT symbol, side, quantity, entry_price, current_price, 
                   unrealized_pnl, broker, opened_at, status
            FROM open_positions 
            ORDER BY opened_at DESC 
            LIMIT 10
        """)
        recent_details = cursor.fetchall()
        
        conn.close()
        
        return {
            "open_positions": open_positions,
            "recent_positions": recent_positions,
            "recent_details": recent_details
        }
        
    except Exception as e:
        return {"error": str(e)}

def monitor_trading():
    """Monitor trading activity"""
    print("================================================================================")
    print("PROMETHEUS LIVE TRADING MONITOR")
    print("================================================================================")
    print(f"Monitor Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Watching for successful trade executions...\n")
    
    last_position_count = 0
    
    while True:
        try:
            activity = get_recent_trading_activity()
            
            if "error" in activity:
                print(f"[ERROR] {activity['error']}")
                time.sleep(10)
                continue
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"[{current_time}] Trading Status:")
            print(f"  Open Positions: {activity['open_positions']}")
            print(f"  Recent Positions (1h): {activity['recent_positions']}")
            
            # Check for new positions
            if activity['open_positions'] > last_position_count:
                print(f"  🎉 NEW POSITION DETECTED! Total positions increased from {last_position_count} to {activity['open_positions']}")
            
            last_position_count = activity['open_positions']
            
            # Show recent position details
            if activity['recent_details']:
                print("  Recent Positions:")
                for pos in activity['recent_details'][:3]:  # Show top 3
                    symbol, side, qty, entry, current, pnl, broker, opened, status = pos
                    pnl_str = f"${pnl:.2f}" if pnl else "N/A"
                    print(f"    - {symbol} {side} {qty} @ ${entry:.2f} | PnL: {pnl_str} | {broker}")
            
            print()
            
            # Check every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\nMonitor stopped by user.")
            break
        except Exception as e:
            print(f"[ERROR] Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_trading()