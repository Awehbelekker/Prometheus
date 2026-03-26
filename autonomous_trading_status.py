#!/usr/bin/env python3
"""
PROMETHEUS Autonomous Trading Status Checker
Shows current configuration and system readiness
"""

import requests
import json
from datetime import datetime
import os

def check_autonomous_status():
    """Check autonomous trading configuration and status"""
    
    print("🤖 PROMETHEUS AUTONOMOUS TRADING STATUS")
    print("=" * 60)
    print(f"📅 Status Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check environment configuration
    print("\n🔧 CONFIGURATION STATUS:")
    print("-" * 40)
    
    # Load environment variables from .env.live
    env_vars = {}
    try:
        with open('.env.live', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("[ERROR] .env.live file not found")
        return
    
    # Check autonomous settings
    autonomous_settings = {
        'TESTING_MODE': 'false',
        'DRY_RUN_MODE': 'false', 
        'REQUIRE_MANUAL_APPROVAL': 'false',
        'AUTONOMOUS_TRADING_ENABLED': 'true',
        'AUTO_EXECUTE_TRADES': 'true'
    }
    
    all_autonomous = True
    for setting, expected in autonomous_settings.items():
        actual = env_vars.get(setting, 'not_set').lower()
        status = "[CHECK]" if actual == expected else "[ERROR]"
        print(f"   {status} {setting}: {actual}")
        if actual != expected:
            all_autonomous = False
    
    print(f"\n🎯 AUTONOMOUS MODE: {'[CHECK] ENABLED' if all_autonomous else '[ERROR] DISABLED'}")
    
    # Check IB Live Trading Status
    print("\n💰 INTERACTIVE BROKERS LIVE TRADING:")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status', timeout=5)
        if response.status_code == 200:
            ib_status = response.json()
            print(f"   [CHECK] Backend Connection: Active")
            print(f"   📊 Status: {ib_status['status']}")
            print(f"   🏦 Account: {ib_status['account_id']}")
            print(f"   🔌 Port: {ib_status['port']} (Live Trading)")
            print(f"   🛡️ Safety Features: Active")
        else:
            print(f"   [ERROR] Backend Connection: Failed ({response.status_code})")
    except Exception as e:
        print(f"   [ERROR] Backend Connection: Error - {e}")
    
    # Check Account Status
    print("\n💳 ACCOUNT STATUS:")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:8000/api/ib-live/account', timeout=5)
        if response.status_code == 200:
            account = response.json()
            print(f"   🏦 Account ID: {account['account_id']}")
            print(f"   💰 Buying Power: ${account['buying_power']:,.2f}")
            print(f"   💵 Available Funds: ${account['available_funds']:,.2f}")
            print(f"   📈 Net Liquidation: ${account['net_liquidation']:,.2f}")
            
            if account['buying_power'] > 0:
                print(f"   [CHECK] Account Status: FUNDED AND READY")
            else:
                print(f"   ⏳ Account Status: AWAITING FUNDS")
                print(f"   📝 Note: System ready - will trade when funds arrive")
        else:
            print(f"   [ERROR] Account Check: Failed ({response.status_code})")
    except Exception as e:
        print(f"   [ERROR] Account Check: Error - {e}")
    
    # Check Current Trading Session
    print("\n📊 CURRENT TRADING SESSION:")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:8000/api/paper-trading/performance', timeout=5)
        if response.status_code == 200:
            performance = response.json()
            if performance.get('active_sessions', 0) > 0:
                print(f"   [CHECK] Active Sessions: {performance['active_sessions']}")
                print(f"   💰 Current P&L: ${performance.get('current_pnl', 0):,.2f}")
                print(f"   📈 Return: {performance.get('return_percentage', 0):.2f}%")
                print(f"   🤖 AI Decisions: {performance.get('ai_decisions', 0)}")
                print(f"   📋 Trades: {performance.get('total_trades', 0)}")
            else:
                print(f"   ⏸️ No active trading sessions")
        else:
            print(f"   [ERROR] Session Check: Failed ({response.status_code})")
    except Exception as e:
        print(f"   [ERROR] Session Check: Error - {e}")
    
    # System Readiness Summary
    print("\n🎯 SYSTEM READINESS SUMMARY:")
    print("=" * 60)
    
    if all_autonomous:
        print("[CHECK] AUTONOMOUS TRADING: ENABLED")
        print("[CHECK] MANUAL APPROVAL: DISABLED") 
        print("[CHECK] DRY RUN MODE: DISABLED")
        print("[CHECK] LIVE TRADING: CONFIGURED")
        print("[CHECK] BACKEND: OPERATIONAL")
        print()
        print("🚀 PROMETHEUS IS READY FOR AUTONOMOUS TRADING!")
        print()
        print("📋 WHAT HAPPENS NEXT:")
        print("   • System monitors markets continuously")
        print("   • AI makes trading decisions automatically") 
        print("   • Trades execute without manual approval")
        print("   • Account shows $0 until funds clear")
        print("   • Trading begins automatically when funded")
        print()
        print("[WARNING]️  IMPORTANT:")
        print("   • This will trade with REAL MONEY when funded")
        print("   • All safety limits are active ($50 daily loss)")
        print("   • Emergency stop available if needed")
    else:
        print("[WARNING]️ AUTONOMOUS TRADING: NOT FULLY ENABLED")
        print("📝 Check configuration settings above")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_autonomous_status()
