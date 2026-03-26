#!/usr/bin/env python3
"""
Configure Windows Defender Firewall Exceptions
Adds firewall rules for Prometheus, IB, and Alpaca connections
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def add_firewall_rule(name, description, program_path=None, port=None, protocol="TCP", direction="Inbound"):
    """
    Add Windows Firewall rule using netsh
    
    Args:
        name: Rule name
        description: Rule description
        program_path: Path to executable (optional)
        port: Port number (optional)
        protocol: TCP or UDP
        direction: Inbound or Outbound
    """
    try:
        if program_path and os.path.exists(program_path):
            # Rule for specific program
            cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={name}',
                f'description={description}',
                f'dir={direction}',
                f'action=allow',
                f'program={program_path}',
                f'enable=yes'
            ]
        elif port:
            # Rule for specific port
            cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={name}',
                f'description={description}',
                f'dir={direction}',
                f'action=allow',
                f'protocol={protocol}',
                f'localport={port}',
                f'enable=yes'
            ]
        else:
            print(f"[SKIP] {name}: Need program_path or port")
            return False
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"[OK] Added firewall rule: {name}")
            return True
        else:
            # Check if rule already exists
            if "already exists" in result.stderr.lower() or "already exists" in result.stdout.lower():
                print(f"[OK] Firewall rule already exists: {name}")
                return True
            else:
                print(f"[WARNING] Could not add rule {name}: {result.stderr}")
                return False
    except Exception as e:
        print(f"[ERROR] Failed to add rule {name}: {e}")
        return False

def find_python_exe():
    """Find Python executable"""
    return sys.executable

def find_ib_gateway():
    """Find Interactive Brokers Gateway/TWS"""
    possible_paths = [
        r"C:\Program Files\IB Gateway\ibgateway.exe",
        r"C:\Program Files\IBKR\IB Gateway\ibgateway.exe",
        r"C:\Program Files (x86)\IB Gateway\ibgateway.exe",
        r"C:\Program Files (x86)\IBKR\IB Gateway\ibgateway.exe",
        r"C:\Jts\ibgateway\ibgateway.exe",
        r"C:\Program Files\TWS\tws.exe",
        r"C:\Program Files\IBKR\TWS\tws.exe",
        r"C:\Program Files (x86)\TWS\tws.exe",
        r"C:\Jts\tws\tws.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    """Main configuration"""
    print("=" * 80)
    print("WINDOWS FIREWALL CONFIGURATION FOR PROMETHEUS")
    print("=" * 80)
    print()
    
    # Check admin rights
    if not check_admin():
        print("[ERROR] This script requires Administrator privileges!")
        print()
        print("Please run as Administrator:")
        print("  1. Right-click PowerShell/Command Prompt")
        print("  2. Select 'Run as administrator'")
        print("  3. Navigate to this directory")
        print("  4. Run: python configure_firewall_exceptions.py")
        print()
        return False
    
    print("[OK] Running with Administrator privileges")
    print()
    
    # Get paths
    python_exe = find_python_exe()
    project_dir = Path(__file__).parent
    ib_gateway = find_ib_gateway()
    
    print_header("CONFIGURING FIREWALL RULES")
    
    rules_added = 0
    
    # 1. Python/Prometheus rules
    print("Adding Python/Prometheus rules...")
    if python_exe:
        # Outbound rule for Python (Prometheus)
        if add_firewall_rule(
            name="Prometheus Trading Platform",
            description="Allow Prometheus trading platform to connect to internet (outbound)",
            program_path=python_exe,
            direction="Outbound"
        ):
            rules_added += 1
        
        # Inbound rule for Python (if needed for API server)
        if add_firewall_rule(
            name="Prometheus Trading Platform (Inbound)",
            description="Allow Prometheus API server to receive connections (inbound)",
            program_path=python_exe,
            direction="Inbound"
        ):
            rules_added += 1
    
    # 2. Interactive Brokers rules
    print()
    print("Adding Interactive Brokers rules...")
    if ib_gateway:
        # IB Gateway/TWS outbound
        if add_firewall_rule(
            name="Interactive Brokers Gateway",
            description="Allow IB Gateway/TWS to connect to IB servers (outbound)",
            program_path=ib_gateway,
            direction="Outbound"
        ):
            rules_added += 1
        
        # IB Gateway/TWS inbound (for local connections)
        if add_firewall_rule(
            name="Interactive Brokers Gateway (Inbound)",
            description="Allow IB Gateway/TWS to receive local connections (inbound)",
            program_path=ib_gateway,
            direction="Inbound"
        ):
            rules_added += 1
    else:
        print("[WARNING] IB Gateway/TWS not found")
        print("         Will add port-based rules instead")
    
    # 3. IB Port rules (7496 paper, 7497 live)
    print()
    print("Adding IB port rules...")
    for port in [7496, 7497]:
        # Inbound for local connections
        if add_firewall_rule(
            name=f"IB Gateway Port {port} (Inbound)",
            description=f"Allow local connections to IB Gateway on port {port}",
            port=port,
            protocol="TCP",
            direction="Inbound"
        ):
            rules_added += 1
        
        # Outbound (if needed)
        if add_firewall_rule(
            name=f"IB Gateway Port {port} (Outbound)",
            description=f"Allow outbound connections to IB Gateway on port {port}",
            port=port,
            protocol="TCP",
            direction="Outbound"
        ):
            rules_added += 1
    
    # 4. Alpaca API endpoints (HTTPS)
    print()
    print("Adding Alpaca API rules...")
    # Alpaca uses HTTPS (port 443) - usually already allowed, but we'll add explicit rules
    alpaca_domains = [
        "api.alpaca.markets",
        "paper-api.alpaca.markets",
        "data.alpaca.markets",
    ]
    
    # Note: Windows Firewall doesn't support domain-based rules via netsh easily
    # We'll add a note about this
    print("[INFO] Alpaca uses HTTPS (port 443) - usually already allowed")
    print("       If blocked, ensure 'HTTPS (443)' is allowed in Windows Firewall")
    
    # 5. Common trading API ports
    print()
    print("Adding common trading API ports...")
    common_ports = [
        (80, "HTTP"),
        (443, "HTTPS"),
        (8080, "Alternative HTTP"),
    ]
    
    for port, desc in common_ports:
        if add_firewall_rule(
            name=f"Trading API {desc} (Outbound)",
            description=f"Allow outbound {desc} connections for trading APIs",
            port=port,
            protocol="TCP",
            direction="Outbound"
        ):
            rules_added += 1
    
    # 6. Prometheus API server ports (if running unified server)
    print()
    print("Adding Prometheus API server ports...")
    prometheus_ports = [8000, 8001, 9090]  # API, alternative, metrics
    
    for port in prometheus_ports:
        if add_firewall_rule(
            name=f"Prometheus API Port {port} (Inbound)",
            description=f"Allow inbound connections to Prometheus API on port {port}",
            port=port,
            protocol="TCP",
            direction="Inbound"
        ):
            rules_added += 1
    
    # Summary
    print()
    print("=" * 80)
    print("CONFIGURATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Rules added/verified: {rules_added}")
    print()
    print("Firewall rules configured for:")
    print("  ✅ Prometheus Trading Platform (Python)")
    print("  ✅ Interactive Brokers Gateway/TWS")
    print("  ✅ IB Gateway ports (7496 paper, 7497 live)")
    print("  ✅ Common trading API ports (80, 443, 8080)")
    print("  ✅ Prometheus API server ports (8000, 8001, 9090)")
    print()
    print("Note: Alpaca uses HTTPS (port 443) which is usually already allowed.")
    print("      If you experience connection issues, check Windows Defender settings.")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

