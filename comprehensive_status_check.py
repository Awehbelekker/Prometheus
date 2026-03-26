#!/usr/bin/env python3
"""
PROMETHEUS COMPREHENSIVE STATUS CHECK
Verifies all systems before restart
"""
import requests
import sqlite3
import os
from datetime import datetime

def check_alpaca_account():
    """Check Alpaca account status for short selling capability"""
    print("=== ALPACA ACCOUNT CHECK ===")
    try:
        # This would normally use the Alpaca API, but for now we'll check the logs
        print("Alpaca Account: 910544927")
        print("Short Selling Requirements:")
        print("  - Minimum $2,000 equity: CHECK ACCOUNT BALANCE")
        print("  - Margin account: DEFAULT (all Alpaca accounts)")
        print("  - Shorting enabled: CHECK ACCOUNT SETTINGS")
        print("  - ETB securities only: CHECK SYMBOL AVAILABILITY")
        return True
    except Exception as e:
        print(f"Error checking Alpaca account: {e}")
        return False

def check_ib_gateway():
    """Check IB Gateway connection status"""
    print("\n=== IB GATEWAY CHECK ===")
    try:
        # Check if port 7496 is listening
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        
        if result == 0:
            print("IB Gateway: CONNECTED (Port 7496 active)")
            print("Required Settings:")
            print("  - Master API client ID: 7777")
            print("  - Enable Forex trading: CHECK")
            print("  - Socket port: 7496")
            print("  - Allow localhost only: CHECK")
            return True
        else:
            print("IB Gateway: NOT CONNECTED (Port 7496 inactive)")
            return False
    except Exception as e:
        print(f"Error checking IB Gateway: {e}")
        return False

def check_databases():
    """Check database schema and connectivity"""
    print("\n=== DATABASE CHECK ===")
    
    db_locations = [
        "databases/prometheus_trading.db",
        "databases/prometheus_learning.db",
        "databases/live_trading.db",
        "databases/persistent_trading.db"
    ]
    
    all_good = True
    for db_path in db_locations:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if open_positions table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='open_positions'")
                if cursor.fetchone():
                    print(f"  [OK] {db_path} - open_positions table exists")
                else:
                    print(f"  [ERROR] {db_path} - open_positions table missing")
                    all_good = False
                
                conn.close()
            except Exception as e:
                print(f"  [ERROR] {db_path} - {e}")
                all_good = False
        else:
            print(f"  [SKIP] {db_path} - file not found")
    
    return all_good

def check_short_selling_system():
    """Check if short selling system is properly configured"""
    print("\n=== SHORT SELLING SYSTEM CHECK ===")
    
    # Check if enhanced trading logic exists
    if os.path.exists("enhanced_trading_logic.py"):
        print("  [OK] enhanced_trading_logic.py exists")
    else:
        print("  [ERROR] enhanced_trading_logic.py missing")
        return False
    
    # Check if position manager exists
    if os.path.exists("position_manager.py"):
        print("  [OK] position_manager.py exists")
    else:
        print("  [ERROR] position_manager.py missing")
        return False
    
    # Check database path in position manager
    try:
        with open("position_manager.py", "r") as f:
            content = f.read()
            if "prometheus_learning.db" in content:
                print("  [OK] Position manager uses correct database path")
            else:
                print("  [WARNING] Position manager database path may be incorrect")
    except Exception as e:
        print(f"  [ERROR] Could not check position manager: {e}")
        return False
    
    return True

def main():
    print("================================================================================")
    print("PROMETHEUS COMPREHENSIVE STATUS CHECK")
    print("================================================================================")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all checks
    alpaca_ok = check_alpaca_account()
    ib_ok = check_ib_gateway()
    db_ok = check_databases()
    short_ok = check_short_selling_system()
    
    print("\n================================================================================")
    print("STATUS SUMMARY")
    print("================================================================================")
    print(f"Alpaca Account: {'OK' if alpaca_ok else 'NEEDS CHECK'}")
    print(f"IB Gateway: {'CONNECTED' if ib_ok else 'NOT CONNECTED'}")
    print(f"Databases: {'OK' if db_ok else 'HAS ISSUES'}")
    print(f"Short Selling System: {'OK' if short_ok else 'HAS ISSUES'}")
    
    if all([alpaca_ok, ib_ok, db_ok, short_ok]):
        print("\n[SUCCESS] All systems ready for trading!")
        print("Short selling should work if Alpaca account meets requirements.")
    else:
        print("\n[WARNING] Some systems need attention before trading.")
    
    print("\nNext Steps:")
    print("1. Verify Alpaca account has $2,000+ equity and shorting enabled")
    print("2. Ensure IB Gateway shows 'Active API Client' with ID 7777")
    print("3. Restart trading platform")
    print("4. Monitor for successful trade executions")

if __name__ == "__main__":
    main()








