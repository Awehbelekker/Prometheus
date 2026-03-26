#!/usr/bin/env python3
"""
ENABLE LIVE TRADING
Enable live trading globally and start active trading session
"""

import requests
import json
import time
from datetime import datetime

def check_current_status():
    """Check current trading status"""
    print("CHECKING CURRENT TRADING STATUS")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/live-trading/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Active: {data.get('active', False)}")
            print(f"   User: {data.get('user', 'None')}")
            print(f"   Enabled Globally: {data.get('enabled_globally', False)}")
            return data
        else:
            print(f"   [ERROR] Status check failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   [ERROR] Status check failed: {str(e)}")
        return None

def enable_live_trading():
    """Enable live trading globally"""
    print("\nENABLING LIVE TRADING")
    print("=" * 50)
    
    # Try to enable live trading
    try:
        # First, try to start the live trading engine
        response = requests.post(
            "http://localhost:8000/api/live-trading/start-engine",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   [SUCCESS] Live Trading Engine Started")
            print(f"   Response: {result}")
            return True
        else:
            print(f"   [ERROR] Failed to start engine: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Engine start failed: {str(e)}")
        return False

def start_trading_session():
    """Start an active trading session"""
    print("\nSTARTING ACTIVE TRADING SESSION")
    print("=" * 50)
    
    # Try different approaches to start trading
    approaches = [
        {
            "name": "Direct Live Trading Start",
            "url": "http://localhost:8000/api/live-trading/start",
            "method": "POST",
            "data": {"auto_trading": True, "capital": 250.0}
        },
        {
            "name": "Trading Start with Mode",
            "url": "http://localhost:8000/api/trading/start",
            "method": "POST", 
            "data": {"mode": "live", "auto_trading": True}
        }
    ]
    
    for approach in approaches:
        print(f"   Trying: {approach['name']}")
        
        try:
            if approach['method'] == 'POST':
                response = requests.post(
                    approach['url'],
                    json=approach['data'],
                    timeout=10
                )
            else:
                response = requests.get(approach['url'], timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   [SUCCESS] {approach['name']} worked!")
                print(f"   Response: {result}")
                return True, result
            else:
                print(f"   [ERROR] {approach['name']} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   [ERROR] {approach['name']} failed: {str(e)}")
    
    return False, None

def monitor_trading_activity():
    """Monitor trading activity"""
    print("\nMONITORING TRADING ACTIVITY")
    print("=" * 50)
    
    for i in range(5):
        print(f"   Check {i+1}/5...")
        
        # Check live trading status
        try:
            response = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Active: {data.get('active', False)}")
                print(f"      User: {data.get('user', 'None')}")
                print(f"      Enabled: {data.get('enabled_globally', False)}")
                
                if data.get('active', False):
                    print("      [SUCCESS] Trading is now active!")
                    return True
            else:
                print(f"      [ERROR] Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"      [ERROR] Status check failed: {str(e)}")
        
        if i < 4:  # Don't sleep on last iteration
            time.sleep(3)
    
    return False

def main():
    """Main function to enable and start live trading"""
    print("PROMETHEUS LIVE TRADING ENABLER")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check current status
    current_status = check_current_status()
    
    if not current_status:
        print("\n[ERROR] Could not check current status")
        return False
    
    # Enable live trading if needed
    if not current_status.get('enabled_globally', False):
        print("\nLive trading is globally disabled. Enabling...")
        engine_started = enable_live_trading()
        
        if not engine_started:
            print("\n[ERROR] Could not enable live trading")
            print("Check server configuration and permissions")
            return False
    else:
        print("\nLive trading is already enabled globally")
    
    # Start trading session
    session_started, session_result = start_trading_session()
    
    if not session_started:
        print("\n[ERROR] Could not start trading session")
        print("Check available endpoints and server configuration")
        return False
    
    print("\n[SUCCESS] Trading session started!")
    
    # Monitor activity
    trading_active = monitor_trading_activity()
    
    if trading_active:
        print("\n[SUCCESS] TRADING IS NOW ACTIVE!")
        print("Prometheus is actively trading with real money")
        print("\nIMPORTANT:")
        print("- Monitor performance closely")
        print("- Check trade execution logs")
        print("- Review AI decision quality")
        print("- Start with small position sizes")
    else:
        print("\n[WARNING] Trading session started but not yet active")
        print("AI may need time to analyze markets")
        print("Check again in a few minutes")
    
    return trading_active

if __name__ == "__main__":
    success = main()
    print(f"\nFINAL RESULT: {'LIVE TRADING ACTIVE' if success else 'NEEDS ATTENTION'}")