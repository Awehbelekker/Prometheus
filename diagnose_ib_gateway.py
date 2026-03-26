"""
Comprehensive IB Gateway Diagnostic Tool
Checks everything needed for IB connection
"""
import socket
import os
import sys
from pathlib import Path
import subprocess

def check_port(host, port):
    """Test if a port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def check_ib_process():
    """Check if IB Gateway process is running"""
    try:
        # Windows process check
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq ibgateway.exe'],
            capture_output=True,
            text=True
        )
        return 'ibgateway.exe' in result.stdout.lower()
    except:
        return False

def check_ib_files():
    """Check if IB Gateway is installed"""
    common_paths = [
        Path(r"C:\Jts\ibgateway"),
        Path(r"C:\Program Files\IBController"),
        Path(r"C:\Program Files (x86)\IBController"),
    ]
    
    for path in common_paths:
        if path.exists():
            return True, str(path)
    return False, None

def main():
    print("\n" + "="*70)
    print("IB GATEWAY COMPREHENSIVE DIAGNOSTIC")
    print("="*70)
    
    # 1. Check if IB is installed
    print("\n[1/6] Checking IB Gateway Installation...")
    installed, install_path = check_ib_files()
    if installed:
        print(f"  [OK] Found IB Gateway at: {install_path}")
    else:
        print(f"  [ERROR] IB Gateway installation not found")
        print(f"         Expected locations: C:\\Jts\\ibgateway")
    
    # 2. Check if IB Gateway process is running
    print("\n[2/6] Checking IB Gateway Process...")
    if check_ib_process():
        print(f"  [OK] IB Gateway process is running")
    else:
        print(f"  [ERROR] IB Gateway process NOT running")
        print(f"         Action: Start IB Gateway and login")
    
    # 3. Check standard IB ports
    print("\n[3/6] Checking IB API Ports...")
    ports_to_check = {
        4001: "Gateway Paper",
        4002: "Gateway Live",
        7496: "TWS Live",
        7497: "TWS Paper"
    }
    
    open_ports = []
    for port, description in ports_to_check.items():
        if check_port('127.0.0.1', port):
            print(f"  [OK] Port {port} ({description}) is OPEN")
            open_ports.append(port)
        else:
            print(f"  [CLOSED] Port {port} ({description})")
    
    if not open_ports:
        print(f"\n  [ERROR] NO IB API PORTS ARE OPEN")
        print(f"         This means:")
        print(f"         - IB Gateway/TWS is not running, OR")
        print(f"         - API is not enabled in settings, OR")
        print(f"         - Firewall is blocking connections")
    
    # 4. Check environment configuration
    print("\n[4/6] Checking Environment Configuration...")
    ib_host = os.getenv('IB_HOST', '127.0.0.1')
    ib_port = os.getenv('IB_PORT', '4002')
    ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
    
    print(f"  IB_HOST: {ib_host}")
    print(f"  IB_PORT: {ib_port}")
    print(f"  IB_ACCOUNT: {ib_account}")
    
    # 5. Check if PROMETHEUS broker module can be imported
    print("\n[5/6] Checking PROMETHEUS IB Integration...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        print(f"  [OK] IB broker module imported successfully")
    except ImportError as e:
        print(f"  [ERROR] Cannot import IB broker: {e}")
    
    # 6. Provide recommendations
    print("\n[6/6] Recommendations...")
    
    if not check_ib_process():
        print(f"\n  STEP 1: START IB GATEWAY")
        print(f"  - Open IB Gateway application")
        print(f"  - Login with account: U21922116")
        print(f"  - Wait for full login (don't close)")
    
    if not open_ports:
        print(f"\n  STEP 2: ENABLE API IN GATEWAY")
        print(f"  - Click Configure (gear icon)")
        print(f"  - Go to Settings > API > Settings")
        print(f"  - Check 'Enable ActiveX and Socket Clients'")
        print(f"  - Socket port should be: 4002 (for live)")
        print(f"  - Check 'Allow connections from localhost only'")
        print(f"  - Click OK")
        print(f"  - API should start automatically")
    
    if open_ports:
        print(f"\n  STEP 3: TEST CONNECTION")
        print(f"  - IB Gateway is responding on port(s): {open_ports}")
        print(f"  - Run: python check_ib_status.py")
        print(f"  - If still failing, check PROMETHEUS IB integration")
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"  IB Installed: {'Yes' if installed else 'No'}")
    print(f"  IB Running: {'Yes' if check_ib_process() else 'No'}")
    print(f"  API Ports Open: {len(open_ports)} of 4")
    print(f"  PROMETHEUS Ready: {'Yes' if open_ports else 'No - Fix IB Gateway first'}")
    print()

if __name__ == "__main__":
    main()
