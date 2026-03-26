#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Comprehensive System Status
"""
import os
import sys
import requests
import subprocess
import time
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def check_service(name, url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"[CHECK] {name}: OPERATIONAL (Status: {response.status_code})")
            return True
        else:
            print(f"[WARNING]️ {name}: RESPONDING BUT ERROR (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] {name}: CONNECTION REFUSED")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {name}: ERROR - {e}")
        return False

def check_alpaca_credentials():
    print_header("ALPACA API CREDENTIALS STATUS")
    
    paper_key = os.getenv('ALPACA_PAPER_KEY')
    paper_secret = os.getenv('ALPACA_PAPER_SECRET')
    live_key = os.getenv('ALPACA_LIVE_KEY')
    live_secret = os.getenv('ALPACA_LIVE_SECRET')
    
    print(f"📊 Paper Trading Key: {'[CHECK] SET' if paper_key else '[ERROR] MISSING'}")
    print(f"🔐 Paper Trading Secret: {'[CHECK] SET' if paper_secret else '[ERROR] MISSING'}")
    print(f"💰 Live Trading Key: {'[CHECK] SET' if live_key else '[ERROR] MISSING'}")
    print(f"🔒 Live Trading Secret: {'[CHECK] SET' if live_secret else '[ERROR] MISSING'}")
    
    return all([paper_key, paper_secret])

def check_core_services():
    print_header("CORE SERVICES STATUS")
    
    services = [
        ("Backend API", "http://127.0.0.1:8000/health"),
        ("Alpaca Status", "http://127.0.0.1:8000/api/alpaca/debug-status"),
        ("AI Trading", "http://127.0.0.1:8000/api/ai-trading/health"),
        ("Frontend App", "http://127.0.0.1:3000"),
        ("API Docs", "http://127.0.0.1:8000/docs")
    ]
    
    results = {}
    for name, url in services:
        results[name] = check_service(name, url)
    
    return results

def check_ports():
    print_header("PORT STATUS")
    
    try:
        result = subprocess.run(
            ["netstat", "-an"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        ports_to_check = [3000, 3001, 3002, 8000, 8001]
        for port in ports_to_check:
            if f":{port}" in result.stdout and "LISTENING" in result.stdout:
                print(f"[CHECK] Port {port}: LISTENING")
            else:
                print(f"[ERROR] Port {port}: NOT LISTENING")
                
    except Exception as e:
        print(f"💥 Port check failed: {e}")

def test_alpaca_integration():
    print_header("ALPACA INTEGRATION TEST")
    
    try:
        # Test direct Alpaca service
        result = subprocess.run(
            [sys.executable, "core/alpaca_trading_service.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[CHECK] Direct Alpaca service test: PASSED")
            if "$200,000" in result.stdout:
                print("💰 Paper trading buying power: $200,000 confirmed")
            return True
        else:
            print(f"[ERROR] Direct Alpaca service test: FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"💥 Alpaca test error: {e}")
        return False

def main():
    print("🚀 PROMETHEUS Trading Platform - System Status Check")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    # Check credentials
    creds_ok = check_alpaca_credentials()
    
    # Check Alpaca integration
    alpaca_ok = test_alpaca_integration()
    
    # Check ports
    check_ports()
    
    # Check core services
    services_status = check_core_services()
    
    # Summary
    print_header("SYSTEM SUMMARY")
    
    print(f"🔑 Alpaca Credentials: {'[CHECK] CONFIGURED' if creds_ok else '[ERROR] MISSING'}")
    print(f"📈 Alpaca Integration: {'[CHECK] WORKING' if alpaca_ok else '[ERROR] FAILED'}")
    
    working_services = sum(1 for status in services_status.values() if status)
    total_services = len(services_status)
    print(f"🌐 Services Operational: {working_services}/{total_services}")
    
    if creds_ok and alpaca_ok:
        print("\n🎉 TRADING PLATFORM READY!")
        print("📋 Next Steps:")
        print("   1. Start backend: python unified_production_server.py")
        print("   2. Start frontend: cd frontend && npm start")
        print("   3. Access app: http://localhost:3002")
    else:
        print("\n[WARNING]️ CONFIGURATION INCOMPLETE")
        if not creds_ok:
            print("   - Configure Alpaca API credentials")
        if not alpaca_ok:
            print("   - Fix Alpaca integration")

if __name__ == "__main__":
    main()
