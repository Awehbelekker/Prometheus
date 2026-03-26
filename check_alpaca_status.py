#!/usr/bin/env python3
"""
Check Alpaca trading status and recent activity
"""

import sqlite3
import os
from datetime import datetime, timedelta

def check_alpaca_status():
    """Check if Alpaca is actively trading"""
    print("=== ALPACA TRADING STATUS CHECK ===")
    
    # Check trading database
    trading_db = "databases/prometheus_trading.db"
    if os.path.exists(trading_db):
        try:
            conn = sqlite3.connect(trading_db)
            cursor = conn.cursor()
            
            # Check recent trades (last hour)
            cursor.execute("""
                SELECT COUNT(*) as total_trades, MAX(timestamp) as last_trade 
                FROM trades 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            result = cursor.fetchone()
            print(f"Recent trades (last hour): {result[0]}")
            print(f"Last trade timestamp: {result[1]}")
            
            # Check all trades today
            cursor.execute("""
                SELECT COUNT(*) as total_trades 
                FROM trades 
                WHERE date(timestamp) = date('now')
            """)
            today_trades = cursor.fetchone()[0]
            print(f"Trades today: {today_trades}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error checking trading database: {e}")
    else:
        print("Trading database not found")
    
    # Check portfolio database
    portfolio_db = "databases/prometheus_portfolio.db"
    if os.path.exists(portfolio_db):
        try:
            conn = sqlite3.connect(portfolio_db)
            cursor = conn.cursor()
            
            # Check open positions
            cursor.execute("SELECT COUNT(*) FROM open_positions")
            open_positions = cursor.fetchone()[0]
            print(f"Open positions: {open_positions}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error checking portfolio database: {e}")
    else:
        print("Portfolio database not found")
    
    # Check if Alpaca broker is connected
    print("\n=== NETWORK CONNECTIONS ===")
    print("Checking for Alpaca API connections...")
    
    # Look for Alpaca-related processes or connections
    import subprocess
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        alpaca_connections = [line for line in result.stdout.split('\n') if 'alpaca' in line.lower() or '34.86.145.125' in line or '35.221.23.121' in line]
        if alpaca_connections:
            print("Active Alpaca connections found:")
            for conn in alpaca_connections[:5]:  # Show first 5
                print(f"  {conn}")
        else:
            print("No direct Alpaca API connections detected")
    except Exception as e:
        print(f"Error checking network connections: {e}")

if __name__ == "__main__":
    check_alpaca_status()








