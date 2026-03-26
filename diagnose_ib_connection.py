#!/usr/bin/env python3
"""
Interactive Brokers Connection Diagnostic Tool
Checks IB Gateway status, port connectivity, and connection issues
"""

import os
import sys
import socket
import psutil
import asyncio
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_ib_gateway_running():
    """Check if IB Gateway/TWS is running"""
    print_header("CHECKING IB GATEWAY/TWS PROCESS")
    
    try:
        ib_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                name = proc.info.get('name', '').lower()
                exe = proc.info.get('exe', '')
                if exe:
                    exe_lower = exe.lower()
                else:
                    exe_lower = ''
                
                # Check for IB Gateway or TWS
                if any(keyword in name or keyword in exe_lower for keyword in ['tws', 'ibgateway', 'ib gateway', 'trader workstation']):
                    ib_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': exe
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if ib_processes:
            print(f"[OK] Found {len(ib_processes)} IB process(es):")
            for proc in ib_processes:
                print(f"   PID {proc['pid']}: {proc['name']}")
                if proc['exe']:
                    print(f"   Path: {proc['exe']}")
            return True
        else:
            print("[ERROR] IB Gateway/TWS NOT RUNNING")
            print()
            print("SOLUTION:")
            print("  1. Start IB Gateway (for API connections)")
            print("  2. Or start TWS (Trader Workstation)")
            print("  3. Ensure it's configured for API connections")
            print("  4. Check 'Enable ActiveX and Socket Clients' in TWS settings")
            return False
    except Exception as e:
        print(f"[ERROR] Could not check processes: {e}")
        return False

def check_port_connectivity(host, port):
    """Check if port is accessible"""
    print_header(f"CHECKING PORT {port} CONNECTIVITY")
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print()
    
    try:
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"[OK] Port {port} is OPEN and accepting connections")
            return True
        else:
            print(f"[ERROR] Port {port} is CLOSED or not accessible")
            print()
            print("POSSIBLE CAUSES:")
            print("  1. IB Gateway/TWS not running")
            print("  2. IB Gateway not listening on this port")
            print("  3. Firewall blocking the connection")
            print("  4. Wrong port number")
            print()
            print("SOLUTION:")
            print(f"  1. Ensure IB Gateway is running")
            print(f"  2. Check IB Gateway settings:")
            print(f"     - Configuration → API → Settings")
            print(f"     - Enable 'Enable ActiveX and Socket Clients'")
            print(f"     - Socket port should be {port}")
            print(f"  3. Check firewall: Run RUN_FIREWALL_CONFIG.bat as admin")
            return False
    except Exception as e:
        print(f"[ERROR] Could not check port: {e}")
        return False

def check_ib_api_available():
    """Check if IB API is installed"""
    print_header("CHECKING IB API INSTALLATION")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        print("[OK] IB API (ib_insync/ibapi) is installed")
        return True
    except ImportError as e:
        print("[ERROR] IB API not installed")
        print()
        print("SOLUTION:")
        print("  Install IB API:")
        print("    pip install ibapi")
        print("  OR")
        print("    pip install ib_insync")
        return False

def check_environment_variables():
    """Check IB environment variables"""
    print_header("CHECKING ENVIRONMENT VARIABLES")
    
    ib_host = os.getenv('IB_HOST', os.getenv('IB_GATEWAY_HOST', '127.0.0.1'))
    ib_port = int(os.getenv('IB_PORT', os.getenv('IB_GATEWAY_PORT', '7497')))
    ib_account = os.getenv('IB_ACCOUNT', os.getenv('IB_ACCOUNT_ID', 'U21922116'))
    ib_client_id = int(os.getenv('IB_CLIENT_ID', '7777'))
    
    print(f"IB_HOST: {ib_host}")
    print(f"IB_PORT: {ib_port}")
    print(f"IB_ACCOUNT: {ib_account}")
    print(f"IB_CLIENT_ID: {ib_client_id}")
    print()
    
    # Check port configuration
    if ib_port == 7496:
        print("[INFO] Port 7496 = PAPER TRADING")
    elif ib_port == 7497:
        print("[INFO] Port 7497 = LIVE TRADING")
    else:
        print(f"[WARNING] Port {ib_port} is non-standard")
        print("         Standard ports: 7496 (paper), 7497 (live)")
    
    return ib_host, ib_port, ib_account, ib_client_id

async def test_ib_connection(host, port, client_id):
    """Test actual IB connection"""
    print_header("TESTING IB CONNECTION")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TestWrapper(EWrapper):
            def __init__(self):
                self.connected = False
                self.next_order_id = None
                
            def nextValidId(self, orderId):
                self.next_order_id = orderId
                self.connected = True
                print(f"[OK] Received nextValidId: {orderId}")
                print("[OK] Connection established successfully!")
        
        wrapper = TestWrapper()
        client = EClient(wrapper)
        
        print(f"Connecting to {host}:{port} (client_id: {client_id})...")
        client.connect(host, port, client_id)
        
        # Wait for connection (max 5 seconds)
        for i in range(50):  # 50 * 0.1 = 5 seconds
            await asyncio.sleep(0.1)
            if wrapper.connected:
                client.disconnect()
                return True
        
        client.disconnect()
        print("[ERROR] Connection timeout - no response from IB Gateway")
        print()
        print("POSSIBLE CAUSES:")
        print("  1. IB Gateway not running")
        print("  2. Wrong port number")
        print("  3. Client ID conflict (another client using same ID)")
        print("  4. IB Gateway not accepting API connections")
        return False
        
    except ImportError:
        print("[ERROR] IB API not available - cannot test connection")
        return False
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main diagnostic"""
    print("=" * 80)
    print("INTERACTIVE BROKERS CONNECTION DIAGNOSTIC")
    print("=" * 80)
    print()
    
    results = {}
    
    # Check 1: IB Gateway running
    results['ib_gateway'] = check_ib_gateway_running()
    
    # Check 2: Environment variables
    host, port, account, client_id = check_environment_variables()
    
    # Check 3: Port connectivity
    results['port'] = check_port_connectivity(host, port)
    
    # Check 4: IB API installed
    results['ib_api'] = check_ib_api_available()
    
    # Check 5: Test connection
    if results['ib_api'] and results['port']:
        results['connection'] = asyncio.run(test_ib_connection(host, port, client_id))
    else:
        print()
        print("[SKIP] Skipping connection test (prerequisites not met)")
        results['connection'] = False
    
    # Summary
    print()
    print("=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print()
    
    print(f"IB Gateway Running: {'✅ YES' if results['ib_gateway'] else '❌ NO'}")
    print(f"Port {port} Accessible: {'✅ YES' if results['port'] else '❌ NO'}")
    print(f"IB API Installed: {'✅ YES' if results['ib_api'] else '❌ NO'}")
    print(f"Connection Test: {'✅ SUCCESS' if results.get('connection') else '❌ FAILED'}")
    print()
    
    if all([results['ib_gateway'], results['port'], results['ib_api'], results.get('connection')]):
        print("=" * 80)
        print("✅ ALL CHECKS PASSED - IB SHOULD BE CONNECTED")
        print("=" * 80)
        print()
        print("If Prometheus still shows 'not connected', check:")
        print("  1. System logs for connection errors")
        print("  2. IB Gateway logs for API connection attempts")
        print("  3. Client ID conflicts (ensure unique client_id)")
    else:
        print("=" * 80)
        print("❌ ISSUES DETECTED - SEE ABOVE FOR SOLUTIONS")
        print("=" * 80)
        print()
        print("QUICK FIXES:")
        if not results['ib_gateway']:
            print("  → Start IB Gateway/TWS")
        if not results['port']:
            print(f"  → Check IB Gateway is listening on port {port}")
            print("  → Run firewall configuration: RUN_FIREWALL_CONFIG.bat")
        if not results['ib_api']:
            print("  → Install IB API: pip install ibapi")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

