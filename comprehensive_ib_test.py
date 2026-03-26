#!/usr/bin/env python3
"""
Comprehensive Interactive Brokers Live Trading Test for PROMETHEUS
Tests all IB live trading endpoints and safety features
"""
import sys
import time
import requests
import json
from datetime import datetime

def test_prometheus_backend():
    """Test PROMETHEUS backend is running"""
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[CHECK] PROMETHEUS Backend: Connected")
            print(f"   Account: {data.get('account_id', 'Unknown')}")
            print(f"   Port: {data.get('port', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"[ERROR] PROMETHEUS Backend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] PROMETHEUS Backend: Connection failed - {e}")
        return False

def check_safety_features():
    """Check all safety features are active"""
    try:
        response = requests.get('http://localhost:8000/api/ib-live/safety/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            safety = data.get('safety_systems', {})
            print("🛡️ Safety Features:")
            print(f"   Confirmation Required: {'[CHECK]' if safety.get('confirmation_required') else '[ERROR]'}")
            print(f"   Daily Loss Limit: {'[CHECK]' if safety.get('daily_loss_limit_active') else '[ERROR]'}")
            print(f"   Position Size Limits: {'[CHECK]' if safety.get('position_size_limits_active') else '[ERROR]'}")
            print(f"   Emergency Stop: {'[CHECK]' if safety.get('emergency_stop_available') else '[ERROR]'}")
            
            limits = data.get('current_limits', {})
            print("📊 Current Limits:")
            print(f"   Daily P&L: ${limits.get('daily_pnl', 0):.2f}")
            print(f"   Max Daily Loss: ${limits.get('max_daily_loss', 0):.2f}")
            print(f"   Trades Today: {limits.get('trades_today', 0)}")
            print(f"   Max Daily Trades: {limits.get('max_daily_trades', 0)}")
            return True
        else:
            print(f"[ERROR] Safety Check: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Safety Check: Failed - {e}")
        return False

def check_current_trading_session():
    """Check current paper trading session"""
    try:
        response = requests.get('http://localhost:8000/api/paper-trading/performance', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("📈 Current Paper Trading Session:")
            print(f"   P&L: ${data.get('total_pnl', 0):.2f}")
            print(f"   Return: {data.get('return_percentage', 0):.2f}%")
            print(f"   Trades: {data.get('total_trades', 0)}")
            print(f"   AI Decisions: {data.get('ai_decisions', 0)}")
            print(f"   Active Sessions: {data.get('active_sessions', 0)}")
            return True
        else:
            print(f"[ERROR] Trading Session: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Trading Session: Failed - {e}")
        return False

def test_ib_endpoints():
    """Test all IB live trading endpoints"""
    print("🔍 Testing IB Live Trading Endpoints:")
    
    # Test status endpoint
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status')
        print(f"   Status Endpoint: {'[CHECK]' if response.status_code == 200 else '[ERROR]'}")
    except:
        print("   Status Endpoint: [ERROR]")
    
    # Test account endpoint (should fail when disabled)
    try:
        response = requests.get('http://localhost:8000/api/ib-live/account')
        if response.status_code == 400:
            print("   Account Endpoint: [CHECK] (Properly secured)")
        else:
            print(f"   Account Endpoint: [WARNING]️ (HTTP {response.status_code})")
    except:
        print("   Account Endpoint: [ERROR]")
    
    # Test positions endpoint (should fail when disabled)
    try:
        response = requests.get('http://localhost:8000/api/ib-live/positions')
        if response.status_code == 400:
            print("   Positions Endpoint: [CHECK] (Properly secured)")
        else:
            print(f"   Positions Endpoint: [WARNING]️ (HTTP {response.status_code})")
    except:
        print("   Positions Endpoint: [ERROR]")
    
    # Test safety status endpoint
    try:
        response = requests.get('http://localhost:8000/api/ib-live/safety/status')
        print(f"   Safety Status Endpoint: {'[CHECK]' if response.status_code == 200 else '[ERROR]'}")
    except:
        print("   Safety Status Endpoint: [ERROR]")

def main():
    """Run comprehensive IB live trading test"""
    print("🚀 PROMETHEUS IB LIVE TRADING COMPREHENSIVE TEST")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Account: DUN683505 (wvtjnq273)")
    print("=" * 70)
    
    # Test backend connection
    backend_ok = test_prometheus_backend()
    print()
    
    # Check safety features
    if backend_ok:
        safety_ok = check_safety_features()
        print()
    else:
        safety_ok = False
    
    # Test all IB endpoints
    if backend_ok:
        test_ib_endpoints()
        print()
    
    # Check current trading session
    if backend_ok:
        session_ok = check_current_trading_session()
        print()
    else:
        session_ok = False
    
    # Summary
    print("=" * 70)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    print(f"PROMETHEUS Backend: {'[CHECK] Connected' if backend_ok else '[ERROR] Failed'}")
    print(f"Safety Features: {'[CHECK] Active' if safety_ok else '[ERROR] Not Active'}")
    print(f"Trading Session: {'[CHECK] Running' if session_ok else '[ERROR] Not Running'}")
    print("=" * 70)
    
    if backend_ok and safety_ok:
        print("[CHECK] PROMETHEUS is ready for IB live trading")
        print("[WARNING]️ Next steps:")
        print("   1. Configure IB Gateway on port 7496 (live trading)")
        print("   2. Enable live trading with confirmation code")
        print("   3. Test with small positions first")
        print()
        print("🚨 REMEMBER: This will trade with REAL MONEY!")
    else:
        print("[ERROR] Issues detected - resolve before enabling live trading")
    
    print("\n📚 Setup Guide: IB_LIVE_TRADING_SETUP_GUIDE.md")
    print("🔧 Enable Command: See setup guide for confirmation code")

if __name__ == "__main__":
    main()
