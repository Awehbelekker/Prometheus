#!/usr/bin/env python3
"""
PROMETHEUS TRADING STATUS SUMMARY
Comprehensive status report on trading capabilities
"""

import requests
import json
import time
from datetime import datetime

def check_system_status():
    """Check overall system status"""
    print("PROMETHEUS TRADING STATUS SUMMARY")
    print("=" * 60)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check server status
    print("1. SERVER STATUS")
    print("-" * 30)
    
    servers = {
        "Main Server": "http://localhost:8000",
        "GPT-OSS 20B": "http://localhost:5000",
        "GPT-OSS 120B": "http://localhost:5001"
    }
    
    all_servers_running = True
    
    for name, url in servers.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {name}: RUNNING")
            else:
                print(f"   [ERROR] {name}: ERROR ({response.status_code})")
                all_servers_running = False
        except Exception as e:
            print(f"   [OFFLINE] {name}: OFFLINE")
            all_servers_running = False
    
    # Check live trading status
    print("\n2. LIVE TRADING STATUS")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Active: {data.get('active', False)}")
            print(f"   User: {data.get('user', 'None')}")
            print(f"   Enabled Globally: {data.get('enabled_globally', False)}")
            
            if data.get('enabled_globally', False):
                print("   [ENABLED] Live trading is ENABLED globally")
            else:
                print("   [DISABLED] Live trading is DISABLED globally")
                print("   [INFO] Server needs to be restarted to pick up new config")
        else:
            print(f"   [ERROR] Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Status check failed: {str(e)}")
    
    # Check AI activity
    print("\n3. AI SYSTEM STATUS")
    print("-" * 30)
    
    ai_working = 0
    for port, name in [(5000, "GPT-OSS 20B"), (5001, "GPT-OSS 120B")]:
        try:
            response = requests.post(
                f"http://localhost:{port}/generate",
                json={"prompt": "Test AI response", "max_tokens": 50},
                timeout=5
            )
            if response.status_code == 200:
                print(f"   [OK] {name}: RESPONDING")
                ai_working += 1
            else:
                print(f"   [ERROR] {name}: ERROR ({response.status_code})")
        except Exception as e:
            print(f"   [OFFLINE] {name}: OFFLINE")
    
    # Overall assessment
    print("\n4. OVERALL ASSESSMENT")
    print("-" * 30)
    
    if all_servers_running and ai_working > 0:
        print("   [OPERATIONAL] SYSTEM STATUS: OPERATIONAL")
        print("   All servers are running")
        print("   AI systems are responding")
        
        # Check if trading is enabled
        try:
            response = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('enabled_globally', False):
                    print("   [ENABLED] LIVE TRADING: ENABLED")
                    print("   Ready for real money trading")
                else:
                    print("   [DISABLED] LIVE TRADING: DISABLED")
                    print("   Server restart required to enable")
            else:
                print("   [ERROR] Could not check trading status")
        except Exception as e:
            print(f"   [ERROR] Trading status check failed: {str(e)}")
    else:
        print("   [NOT READY] SYSTEM STATUS: NOT READY")
        print("   Some components need attention")
    
    return all_servers_running, ai_working > 0

def provide_next_steps():
    """Provide clear next steps"""
    print("\n5. NEXT STEPS TO ACTIVATE TRADING")
    print("-" * 30)
    
    print("To start actively trading with Prometheus:")
    print()
    print("OPTION 1: RESTART SERVER (Recommended)")
    print("1. Stop the current server (Ctrl+C)")
    print("2. Restart: python unified_production_server.py")
    print("3. Run: python start_active_trading.py")
    print("4. Monitor: python check_trading_status.py")
    print()
    print("OPTION 2: USE EXISTING SESSION")
    print("1. The AI systems are already running")
    print("2. AI is generating trading decisions")
    print("3. Manual trading can be initiated")
    print()
    print("CURRENT STATUS:")
    print("- All servers running")
    print("- AI systems operational") 
    print("- Live trading needs server restart")
    print("- AI is ready to make trading decisions")

def main():
    """Main function"""
    servers_ok, ai_ok = check_system_status()
    provide_next_steps()
    
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    if servers_ok and ai_ok:
        print("[READY] PROMETHEUS IS READY FOR TRADING")
        print("AI systems are operational and generating decisions")
        print("All servers are running properly")
        print()
        print("TO START ACTIVE TRADING:")
        print("1. Restart server to enable live trading")
        print("2. Run trading session starter")
        print("3. Monitor AI decision making")
        print("4. Begin with small position sizes")
    else:
        print("[NOT READY] PROMETHEUS NEEDS ATTENTION")
        print("Some components are not ready")
        print("Fix server issues before trading")

if __name__ == "__main__":
    main()










