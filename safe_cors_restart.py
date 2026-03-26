#!/usr/bin/env python3
"""
🔧 SAFE CORS RESTART - Apply CORS fix without disrupting trading
This script safely restarts the backend server to apply CORS OPTIONS handlers
"""

import requests
import time
import subprocess
import os
from datetime import datetime

def check_trading_status():
    """Check if there are active trading sessions"""
    try:
        response = requests.get('http://localhost:8000/api/paper-trading/sessions/active', timeout=5)
        if response.status_code == 200:
            data = response.json()
            active_sessions = data.get('active_sessions', [])
            return len(active_sessions), active_sessions
        return 0, []
    except Exception as e:
        print(f"[ERROR] Could not check trading status: {e}")
        return -1, []

def check_live_trading_status():
    """Check live trading status"""
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('trading_mode', 'unknown'), data
        return 'unknown', {}
    except Exception as e:
        print(f"[ERROR] Could not check live trading status: {e}")
        return 'error', {}

def test_cors_fix():
    """Test if CORS fix is working"""
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options('http://localhost:8000/api/auth/login', headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] CORS test failed: {e}")
        return False

def main():
    print("🔧 SAFE CORS RESTART FOR PROMETHEUS TRADING PLATFORM")
    print("=" * 70)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check current CORS status
    print("🔍 CHECKING CURRENT CORS STATUS...")
    cors_working = test_cors_fix()
    if cors_working:
        print("[CHECK] CORS is already working! No restart needed.")
        return
    else:
        print("[ERROR] CORS preflight failing (OPTIONS returns 405)")
    
    print()
    
    # Check trading sessions
    print("🔍 CHECKING TRADING SESSIONS...")
    session_count, sessions = check_trading_status()
    live_mode, live_data = check_live_trading_status()
    
    if session_count > 0:
        print(f"[WARNING]️ WARNING: {session_count} active trading sessions detected!")
        for i, session in enumerate(sessions[:3], 1):
            session_id = session.get('session_id', 'Unknown')[:8]
            status = session.get('status', 'Unknown')
            print(f"   Session {i}: {session_id}... ({status})")
        print()
        
    if live_mode != 'unknown' and live_mode != 'error':
        print(f"🚨 LIVE TRADING MODE: {live_mode}")
        account = live_data.get('account_id', 'Unknown')
        print(f"   Account: {account}")
        print()
    
    # Safety check
    print("🛡️ SAFETY ASSESSMENT:")
    if session_count > 0 or live_mode in ['live', 'live_conservative']:
        print("[ERROR] ACTIVE TRADING DETECTED - RESTART NOT RECOMMENDED")
        print()
        print("💡 ALTERNATIVE SOLUTIONS:")
        print("1. Wait for trading sessions to complete")
        print("2. Use browser CORS bypass for development")
        print("3. Use a CORS proxy server")
        print("4. Disable CORS in browser for testing")
        print()
        
        user_input = input("[WARNING]️ Do you want to proceed anyway? (type 'FORCE' to continue): ")
        if user_input != 'FORCE':
            print("[CHECK] Restart cancelled - trading sessions preserved")
            return
    else:
        print("[CHECK] No active trading sessions detected")
        print("[CHECK] Safe to restart server")
    
    print()
    print("🔧 APPLYING CORS FIX...")
    print("The CORS fix has already been added to the server code.")
    print("The server needs to be restarted to apply the changes.")
    print()
    
    print("📋 MANUAL RESTART INSTRUCTIONS:")
    print("1. Go to Terminal 88 (running the backend server)")
    print("2. Press Ctrl+C to stop the server")
    print("3. Run: python start_backend_with_live_env.py")
    print("4. Wait for server to start")
    print("5. Test login functionality")
    print()
    
    print("🎯 EXPECTED RESULT:")
    print("[CHECK] OPTIONS requests will return 200 OK")
    print("[CHECK] CORS preflight will work")
    print("[CHECK] Frontend login will function")
    print("[CHECK] All trading functionality preserved")
    print()
    
    print("[WARNING]️ IMPORTANT: The CORS fix is already in the code!")
    print("File: PROMETHEUS-Enterprise-Package/backend/unified_production_server.py")
    print("Lines: 1659-1675 (OPTIONS handlers added)")

if __name__ == "__main__":
    main()
