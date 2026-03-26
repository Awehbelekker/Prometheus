#!/usr/bin/env python3
"""
Real Prometheus Status Check - Checks what's ACTUALLY running
"""

import psutil
import socket
import os
from pathlib import Path
from dotenv import load_dotenv

def check_running_prometheus():
    """Check if Prometheus is actually running"""
    print("=" * 80)
    print("CHECKING RUNNING PROCESSES")
    print("=" * 80)
    print()
    
    prometheus_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline_parts = proc.info.get('cmdline') or []
            cmdline = ' '.join(str(c) for c in cmdline_parts) if cmdline_parts else ''
            if 'launch_ultimate_prometheus' in cmdline.lower() or 'prometheus' in cmdline.lower():
                print(f"[OK] FOUND Prometheus Process:")
                print(f"   PID: {proc.info['pid']}")
                print(f"   Command: {cmdline[:100]}")
                prometheus_found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not prometheus_found:
        print("[WARNING] No Prometheus process found")
    return prometheus_found

def check_alpaca_config():
    """Check Alpaca configuration properly"""
    print()
    print("=" * 80)
    print("CHECKING ALPACA CONFIGURATION")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    # Check multiple possible variable names
    api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
    secret = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL') or os.getenv('APCA_API_BASE_URL', 'https://api.alpaca.markets')
    
    print(f"ALPACA_API_KEY: {'SET (' + str(len(api_key)) + ' chars)' if api_key else 'NOT SET'}")
    print(f"ALPACA_SECRET_KEY: {'SET (' + str(len(secret)) + ' chars)' if secret else 'NOT SET'}")
    print(f"ALPACA_BASE_URL: {base_url}")
    print()
    
    if api_key and secret:
        print("[OK] Alpaca API keys ARE configured!")
        return True
    else:
        print("[WARNING] Alpaca API keys NOT found in environment")
        print("   Checking .env file...")
        
        env_file = Path('.env')
        if env_file.exists():
            content = env_file.read_text()
            if 'ALPACA' in content or 'APCA' in content:
                print("   [INFO] .env file contains Alpaca variables")
                print("   [WARNING] Variables may not be loaded properly")
                print("   [SOLUTION] Restart Prometheus to reload .env")
            else:
                print("   [WARNING] .env file does not contain Alpaca variables")
        return False

def check_ib_connection():
    """Check IB connection status"""
    print()
    print("=" * 80)
    print("CHECKING IB CONNECTION")
    print("=" * 80)
    print()
    
    # Check port
    port = int(os.getenv('IB_PORT', '7497'))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"[OK] IB Gateway port {port} is OPEN")
            print(f"   Port {port} = {'LIVE' if port == 7497 else 'PAPER'} trading")
        else:
            print(f"[ERROR] IB Gateway port {port} is CLOSED")
            return False
    except Exception as e:
        print(f"[ERROR] Could not check port: {e}")
        return False
    
    # Try to check if API client is connected
    print()
    print("Checking IB API client connection...")
    try:
        # Try to import and check IB broker
        import sys
        sys.path.insert(0, '.')
        
        # Check if we can connect
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TestWrapper(EWrapper):
            def __init__(self):
                self.connected = False
            def nextValidId(self, orderId):
                self.connected = True
        
        wrapper = TestWrapper()
        client = EClient(wrapper)
        
        print(f"   Attempting connection test to {os.getenv('IB_HOST', '127.0.0.1')}:{port}...")
        client.connect(os.getenv('IB_HOST', '127.0.0.1'), port, int(os.getenv('IB_CLIENT_ID', '7777')))
        
        import time
        time.sleep(2)
        
        if client.isConnected():
            print("[OK] IB API client CAN connect!")
            client.disconnect()
            return True
        else:
            print("[WARNING] IB API client connection test failed")
            print("   This may mean:")
            print("   - IB Gateway is running but not accepting connections")
            print("   - Client ID conflict")
            print("   - API settings not enabled in IB Gateway")
            client.disconnect()
            return False
            
    except ImportError as e:
        print(f"[WARNING] Could not test IB API: {e}")
        return None
    except Exception as e:
        print(f"[WARNING] IB API test failed: {e}")
        return None

def main():
    print("=" * 80)
    print("REAL PROMETHEUS STATUS CHECK")
    print("=" * 80)
    print()
    
    # Check processes
    prometheus_running = check_running_prometheus()
    
    # Check Alpaca
    alpaca_configured = check_alpaca_config()
    
    # Check IB
    ib_status = check_ib_connection()
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Prometheus Running: {'[OK] YES' if prometheus_running else '[ERROR] NO'}")
    print(f"Alpaca Configured: {'[OK] YES' if alpaca_configured else '[WARNING] NO'}")
    print(f"IB Gateway: {'[OK] Port open' if ib_status else '[WARNING] Check needed'}")
    print()
    
    if prometheus_running:
        print("[INFO] Prometheus IS running - check terminal window for detailed status")
        print("   Look for connection messages in the terminal")
    else:
        print("[WARNING] Prometheus is NOT running")
        print("   Start with: python launch_ultimate_prometheus_LIVE_TRADING.py")
    
    print()

if __name__ == "__main__":
    main()

