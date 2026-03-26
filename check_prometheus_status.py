#!/usr/bin/env python3
"""
Comprehensive Prometheus Trading System Status Check
Shows current system status, broker connections, and trading sessions
"""

import os
import sys
import psutil
import socket
from datetime import datetime
from pathlib import Path

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_prometheus_processes():
    """Check if Prometheus processes are running"""
    print_header("PROMETHEUS PROCESSES")
    
    prometheus_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', [])).lower()
                if any(keyword in cmdline for keyword in ['prometheus', 'launch_ultimate', 'trading']):
                    if 'python' in proc.info['name'].lower():
                        prometheus_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(proc.info.get('cmdline', [])[:3]),
                            'runtime': datetime.now().timestamp() - proc.info['create_time']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"[ERROR] Could not check processes: {e}")
        return []
    
    if prometheus_processes:
        print(f"[OK] Found {len(prometheus_processes)} Prometheus process(es):")
        for proc in prometheus_processes:
            runtime_min = int(proc['runtime'] / 60)
            print(f"   PID {proc['pid']}: {proc['cmdline'][:80]}")
            print(f"   Runtime: {runtime_min} minutes")
        return prometheus_processes
    else:
        print("[WARNING] No Prometheus processes found running")
        print("   Prometheus may not be running")
        return []

def check_broker_connections():
    """Check broker connection status"""
    print_header("BROKER CONNECTIONS")
    
    # Check Alpaca
    alpaca_status = "UNKNOWN"
    try:
        import alpaca_trade_api as tradeapi
        api_key = os.getenv('ALPACA_API_KEY', '')
        api_secret = os.getenv('ALPACA_SECRET_KEY', '')
        base_url = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
        
        if api_key and api_secret:
            try:
                api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
                account = api.get_account()
                alpaca_status = f"[OK] CONNECTED - Account: {account.account_number}"
            except Exception as e:
                alpaca_status = f"[ERROR] Connection failed: {str(e)[:50]}"
        else:
            alpaca_status = "[WARNING] API keys not configured"
    except ImportError:
        alpaca_status = "[WARNING] Alpaca API not installed"
    except Exception as e:
        alpaca_status = f"[ERROR] {str(e)[:50]}"
    
    print(f"Alpaca: {alpaca_status}")
    
    # Check IB Gateway
    ib_status = "UNKNOWN"
    ib_port = int(os.getenv('IB_PORT', '7497'))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', ib_port))
        sock.close()
        
        if result == 0:
            ib_status = f"[OK] Port {ib_port} is OPEN (IB Gateway may be running)"
        else:
            ib_status = f"[ERROR] Port {ib_port} is CLOSED (IB Gateway not running)"
    except Exception as e:
        ib_status = f"[ERROR] Could not check port: {str(e)[:50]}"
    
    print(f"Interactive Brokers: {ib_status}")
    print(f"   Port: {ib_port} ({'LIVE' if ib_port == 7497 else 'PAPER'})")
    
    return alpaca_status, ib_status

def check_api_server():
    """Check if API server is running"""
    print_header("API SERVER STATUS")
    
    ports = [8000, 8001, 9090]
    active_ports = []
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                active_ports.append(port)
                print(f"[OK] Port {port}: ACTIVE")
            else:
                print(f"[INFO] Port {port}: Not active")
        except:
            print(f"[INFO] Port {port}: Could not check")
    
    if active_ports:
        print(f"\n[OK] API server running on port(s): {', '.join(map(str, active_ports))}")
        return True
    else:
        print("\n[WARNING] API server not detected")
        return False

def check_databases():
    """Check trading databases"""
    print_header("TRADING DATABASES")
    
    db_files = [
        'prometheus_trading.db',
        'enhanced_paper_trading.db',
        'learning_database.db',
        'portfolio_persistence.db'
    ]
    
    found_dbs = []
    for db_file in db_files:
        db_path = Path(db_file)
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            found_dbs.append(db_file)
            print(f"[OK] {db_file}: {size_mb:.2f} MB")
        else:
            print(f"[INFO] {db_file}: Not found")
    
    if found_dbs:
        print(f"\n[OK] Found {len(found_dbs)} database(s)")
    else:
        print("\n[INFO] No databases found (may be first run)")

def check_system_resources():
    """Check system resources"""
    print_header("SYSTEM RESOURCES")
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU Usage: {cpu_percent:.1f}%")
        print(f"Memory: {memory.percent:.1f}% used ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)")
        print(f"Disk: {disk.percent:.1f}% used ({disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB)")
        
        if cpu_percent > 90:
            print("[WARNING] High CPU usage")
        if memory.percent > 90:
            print("[WARNING] High memory usage")
        if disk.percent > 90:
            print("[WARNING] Low disk space")
            
    except Exception as e:
        print(f"[ERROR] Could not check resources: {e}")

def main():
    print("=" * 80)
    print("PROMETHEUS TRADING SYSTEM STATUS")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check processes
    processes = check_prometheus_processes()
    
    # Check brokers
    alpaca_status, ib_status = check_broker_connections()
    
    # Check API server
    api_running = check_api_server()
    
    # Check databases
    check_databases()
    
    # Check resources
    check_system_resources()
    
    # Summary
    print()
    print("=" * 80)
    print("STATUS SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Prometheus Running: {'[OK] YES' if processes else '[WARNING] NO'}")
    print(f"Alpaca Broker: {alpaca_status.split(' - ')[0] if ' - ' in alpaca_status else alpaca_status}")
    print(f"IB Gateway: {ib_status.split(' - ')[0] if ' - ' in ib_status else ib_status}")
    print(f"API Server: {'[OK] RUNNING' if api_running else '[WARNING] NOT RUNNING'}")
    print()
    
    if processes:
        print("[OK] Prometheus appears to be running")
        print("   Check terminal windows for detailed logs")
    else:
        print("[WARNING] Prometheus does not appear to be running")
        print("   To start: python launch_ultimate_prometheus_LIVE_TRADING.py")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStatus check cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Status check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

