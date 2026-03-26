#!/usr/bin/env python3
"""
Full Prometheus Trading System Status Report
Comprehensive status of all systems, brokers, AI, and trading activity
"""

import os
import sys
import psutil
import socket
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_prometheus_processes():
    """Check if Prometheus is running"""
    print_header("PROMETHEUS PROCESSES")
    
    prometheus_procs = []
    backend_procs = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
            try:
                cmdline_parts = proc.info.get('cmdline') or []
                cmdline = ' '.join(str(c) for c in cmdline_parts) if cmdline_parts else ''
                cmdline_lower = cmdline.lower()
                
                if 'launch_ultimate_prometheus' in cmdline_lower:
                    runtime = (datetime.now().timestamp() - proc.info['create_time']) / 60
                    prometheus_procs.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline[:100],
                        'runtime_min': int(runtime),
                        'memory_mb': proc.info['memory_info'].rss / (1024 * 1024)
                    })
                elif 'unified_production_server' in cmdline_lower:
                    runtime = (datetime.now().timestamp() - proc.info['create_time']) / 60
                    backend_procs.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline[:100],
                        'runtime_min': int(runtime),
                        'memory_mb': proc.info['memory_info'].rss / (1024 * 1024)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"[ERROR] Could not check processes: {e}")
        return False, False
    
    if prometheus_procs:
        print(f"[OK] Prometheus Trading System: RUNNING")
        for proc in prometheus_procs:
            print(f"   PID: {proc['pid']}")
            print(f"   Runtime: {proc['runtime_min']} minutes")
            print(f"   Memory: {proc['memory_mb']:.1f} MB")
            print(f"   Command: {proc['cmdline']}")
    else:
        print("[WARNING] Prometheus Trading System: NOT RUNNING")
    
    if backend_procs:
        print()
        print(f"[OK] Backend Server: RUNNING")
        for proc in backend_procs:
            print(f"   PID: {proc['pid']}")
            print(f"   Runtime: {proc['runtime_min']} minutes")
    
    return len(prometheus_procs) > 0, len(backend_procs) > 0

def check_alpaca_status():
    """Check Alpaca broker status"""
    print_header("ALPACA BROKER STATUS")
    
    try:
        import alpaca_trade_api as tradeapi
        
        api_key = (os.getenv('ALPACA_API_KEY') or 
                  os.getenv('ALPACA_LIVE_KEY') or
                  os.getenv('APCA_API_KEY_ID'))
        secret_key = (os.getenv('ALPACA_SECRET_KEY') or 
                     os.getenv('ALPACA_LIVE_SECRET') or
                     os.getenv('APCA_API_SECRET_KEY'))
        base_url = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
        
        if not api_key or not secret_key:
            print("[ERROR] Alpaca credentials not found")
            return False
        
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        account = api.get_account()
        positions = api.list_positions()
        orders = api.list_orders(status='all', limit=5)
        
        print(f"[OK] Connection: CONNECTED")
        print(f"[OK] Account: {account.account_number}")
        print(f"[OK] Status: {account.status}")
        print()
        print("ACCOUNT BALANCE:")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   Equity: ${float(account.equity):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        print()
        print(f"OPEN POSITIONS: {len(positions)}")
        for pos in positions:
            pnl = float(pos.unrealized_pl)
            pnl_pct = float(pos.unrealized_plpc)
            print(f"   {pos.symbol}: {pos.qty} @ ${float(pos.current_price):,.2f} (P&L: ${pnl:,.2f} / {pnl_pct:.2%})")
        print()
        print(f"RECENT ORDERS: {len(orders)}")
        for order in orders[:3]:
            status_icon = "[OK]" if order.status == 'filled' else "[PENDING]"
            print(f"   {status_icon} {order.symbol} {order.side.upper()} {order.qty} - {order.status}")
        
        return True
        
    except ImportError:
        print("[ERROR] alpaca_trade_api not installed")
        return False
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

def check_ib_status():
    """Check Interactive Brokers status"""
    print_header("INTERACTIVE BROKERS STATUS")
    
    ib_port = int(os.getenv('IB_PORT', '7497'))
    ib_host = os.getenv('IB_HOST', '127.0.0.1')
    
    # Check port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ib_host, ib_port))
        sock.close()
        
        if result == 0:
            print(f"[OK] IB Gateway Port {ib_port}: OPEN")
            print(f"   Mode: {'LIVE' if ib_port == 7497 else 'PAPER'} trading")
            print(f"   Host: {ib_host}")
            print()
            print("[INFO] Port is open - IB Gateway appears to be running")
            print("[INFO] Check Prometheus logs for API client connection status")
            return True
        else:
            print(f"[ERROR] IB Gateway Port {ib_port}: CLOSED")
            print("   IB Gateway is not running or not accepting connections")
            return False
    except Exception as e:
        print(f"[ERROR] Could not check port: {e}")
        return False

def check_ai_systems():
    """Check AI systems status"""
    print_header("AI SYSTEMS STATUS")
    
    # Check GPT-OSS / CPT-OSS
    try:
        from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
        gpt_oss = GPTOSSTradingAdapter()
        if gpt_oss:
            model_size = getattr(gpt_oss, 'model_size', '20b')
            print(f"[OK] CPT-OSS: AVAILABLE (Model: {model_size})")
        else:
            print("[WARNING] CPT-OSS: Not initialized")
    except Exception as e:
        print(f"[WARNING] CPT-OSS: Not available ({str(e)[:50]})")
    
    # Check HRM
    try:
        from core.hrm_official_integration import get_official_hrm_adapter, OFFICIAL_HRM_AVAILABLE
        if OFFICIAL_HRM_AVAILABLE:
            print("[OK] Official HRM: AVAILABLE")
        else:
            print("[INFO] Official HRM: Not available (using fallback)")
    except:
        print("[INFO] HRM: Check needed")
    
    # Check Universal Reasoning Engine
    try:
        from core.universal_reasoning_engine import UniversalReasoningEngine
        print("[OK] Universal Reasoning Engine: Available")
    except:
        print("[INFO] Universal Reasoning Engine: Check needed")
    
    # Check Market Oracle
    try:
        from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
        print("[OK] Market Oracle Engine: Available")
    except:
        print("[INFO] Market Oracle Engine: Check needed")

def check_api_servers():
    """Check API server status"""
    print_header("API SERVERS STATUS")
    
    ports = {
        8000: "Main API Server",
        8001: "Alternative API Server", 
        9090: "Metrics Server"
    }
    
    active_ports = []
    for port, name in ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"[OK] {name}: RUNNING (port {port})")
                active_ports.append(port)
            else:
                print(f"[INFO] {name}: Not active (port {port})")
        except:
            print(f"[INFO] {name}: Could not check (port {port})")
    
    return len(active_ports) > 0

def check_databases():
    """Check trading databases"""
    print_header("DATABASES STATUS")
    
    db_files = {
        'prometheus_trading.db': 'Main Trading Database',
        'portfolio_persistence.db': 'Portfolio Persistence',
        'enhanced_paper_trading.db': 'Paper Trading Database',
        'learning_database.db': 'Learning Database'
    }
    
    found = 0
    for db_file, description in db_files.items():
        db_path = Path(db_file)
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"[OK] {description}: {size_mb:.2f} MB")
            found += 1
        else:
            print(f"[INFO] {description}: Not found")
    
    print()
    print(f"Active Databases: {found}/{len(db_files)}")

def check_system_resources():
    """Check system resources"""
    print_header("SYSTEM RESOURCES")
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU Usage: {cpu_percent:.1f}%")
        if cpu_percent > 90:
            print("   [WARNING] High CPU usage")
        
        print(f"Memory: {memory.percent:.1f}% used")
        print(f"   Used: {memory.used / (1024**3):.1f} GB")
        print(f"   Total: {memory.total / (1024**3):.1f} GB")
        if memory.percent > 90:
            print("   [WARNING] High memory usage")
        
        print(f"Disk: {disk.percent:.1f}% used")
        print(f"   Used: {disk.used / (1024**3):.1f} GB")
        print(f"   Total: {disk.total / (1024**3):.1f} GB")
        if disk.percent > 90:
            print("   [WARNING] Low disk space")
            
    except Exception as e:
        print(f"[ERROR] Could not check resources: {e}")

def check_configuration():
    """Check key configuration"""
    print_header("CONFIGURATION STATUS")
    
    # Alpaca
    alpaca_key = (os.getenv('ALPACA_API_KEY') or 
                 os.getenv('ALPACA_LIVE_KEY') or
                 os.getenv('APCA_API_KEY_ID'))
    print(f"Alpaca API Key: {'[OK] SET' if alpaca_key else '[ERROR] NOT SET'}")
    
    # IB
    ib_port = os.getenv('IB_PORT', '7497')
    ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
    print(f"IB Port: {ib_port} ({'LIVE' if ib_port == '7497' else 'PAPER'})")
    print(f"IB Account: {ib_account}")
    
    # CUDA
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"CUDA: {'[OK] AVAILABLE' if cuda_available else '[INFO] Not available (CPU mode)'}")
    except:
        print("CUDA: [INFO] PyTorch not available")

def main():
    print("=" * 80)
    print("PROMETHEUS FULL SYSTEM STATUS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check processes
    prometheus_running, backend_running = check_prometheus_processes()
    
    # Check brokers
    alpaca_connected = check_alpaca_status()
    ib_gateway_running = check_ib_status()
    
    # Check AI systems
    check_ai_systems()
    
    # Check API servers
    api_running = check_api_servers()
    
    # Check databases
    check_databases()
    
    # Check resources
    check_system_resources()
    
    # Check configuration
    check_configuration()
    
    # Final summary
    print()
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print()
    print(f"Prometheus System: {'[OK] RUNNING' if prometheus_running else '[ERROR] NOT RUNNING'}")
    print(f"Backend Server: {'[OK] RUNNING' if backend_running else '[INFO] Not running (optional)'}")
    print(f"Alpaca Broker: {'[OK] CONNECTED' if alpaca_connected else '[ERROR] NOT CONNECTED'}")
    print(f"IB Gateway: {'[OK] RUNNING' if ib_gateway_running else '[ERROR] NOT RUNNING'}")
    print(f"API Servers: {'[OK] ACTIVE' if api_running else '[INFO] Not active'}")
    print()
    
    if prometheus_running and alpaca_connected:
        print("[OK] SYSTEM OPERATIONAL - Trading active")
    elif prometheus_running:
        print("[WARNING] System running but Alpaca not connected")
    else:
        print("[ERROR] Prometheus not running - start with: python full_system_restart.py")
    
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

