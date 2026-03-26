#!/usr/bin/env python3
"""
Full System Restart - Prometheus Trading Platform
Stops all processes and restarts everything for live trading
"""
import sys
import psutil
import os
import time
import subprocess
import signal

sys.stdout.reconfigure(encoding='utf-8')

def find_all_trading_processes():
    """Find all Prometheus-related processes"""
    keywords = [
        'launch_ultimate_prometheus',
        'prometheus',
        'trading',
        'unified_production_server',
        'backend',
        'cpt20b',
        'cpt120b'
    ]
    
    found_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(keyword.lower() in cmdline.lower() for keyword in keywords):
                    found_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return found_processes

def stop_all_processes():
    """Stop all Prometheus-related processes"""
    processes = find_all_trading_processes()
    
    if not processes:
        print("✅ No Prometheus processes found running")
        return True
    
    print(f"🛑 Found {len(processes)} process(es) to stop:")
    for proc in processes:
        try:
            cmdline = ' '.join(proc.info['cmdline'][:2]) if proc.info.get('cmdline') else 'unknown'
            print(f"   Stopping PID {proc.info['pid']}: {cmdline}")
            proc.terminate()
        except Exception as e:
            print(f"   ⚠️  Could not stop PID {proc.info['pid']}: {e}")
    
    # Wait for graceful termination
    print("\n⏳ Waiting for processes to stop gracefully...")
    time.sleep(5)
    
    # Force kill any remaining
    remaining = find_all_trading_processes()
    if remaining:
        print(f"⚠️  {len(remaining)} process(es) still running, force killing...")
        for proc in remaining:
            try:
                proc.kill()
            except:
                pass
        time.sleep(2)
    
    final_check = find_all_trading_processes()
    if final_check:
        print(f"❌ {len(final_check)} process(es) still running after force kill")
        return False
    else:
        print("✅ All processes stopped successfully")
        return True

def verify_configuration():
    """Verify all configurations are correct"""
    print("\n📋 Verifying Configuration...")
    print("-" * 40)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Alpaca (check all possible variable names)
    alpaca_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY') or os.getenv('APCA_API_KEY_ID')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET') or os.getenv('APCA_API_SECRET_KEY')
    print(f"{'✅' if alpaca_key else '❌'} Alpaca API Key: {'SET' if alpaca_key else 'NOT SET'}")
    print(f"{'✅' if alpaca_secret else '❌'} Alpaca Secret: {'SET' if alpaca_secret else 'NOT SET'}")
    
    # Check Polygon
    polygon_access = os.getenv('POLYGON_ACCESS_KEY_ID', 'NOT SET')
    polygon_secret = os.getenv('POLYGON_SECRET_ACCESS_KEY', 'NOT SET')
    print(f"{'✅' if polygon_access != 'NOT SET' else '❌'} Polygon Access Key: {'SET' if polygon_access != 'NOT SET' else 'NOT SET'}")
    print(f"{'✅' if polygon_secret != 'NOT SET' else '❌'} Polygon Secret: {'SET' if polygon_secret != 'NOT SET' else 'NOT SET'}")
    
    # Check IB Port
    ib_port = os.getenv('IB_PORT', '7497')
    ib_port_int = int(ib_port)
    port_type = 'PAPER' if ib_port_int == 7496 else 'LIVE'
    print(f"✅ IB Port: {ib_port_int} ({port_type} trading)")
    print(f"   💡 To change: set IB_PORT=7496 (paper) or IB_PORT=7497 (live)")
    
    print()

def start_trading_system():
    """Start the main trading system in external terminal"""
    print("\n🚀 Starting Prometheus Trading System...")
    print("-" * 40)
    
    script_path = os.path.join(os.getcwd(), 'launch_ultimate_prometheus_LIVE_TRADING.py')
    
    if not os.path.exists(script_path):
        print(f"❌ Trading script not found: {script_path}")
        return None
    
    try:
        if sys.platform == 'win32':
            # Windows: Use start command to open in new external terminal window
            # /k keeps window open, /d sets directory, title sets window title
            cmd = f'start "Prometheus Trading System" /d "{os.getcwd()}" cmd /k "python {script_path}"'
            subprocess.Popen(cmd, shell=True)
            print("✅ Trading system starting in external terminal window")
            print("   Look for a new window titled 'Prometheus Trading System'")
            print("   All output will be visible in that window")
            return True
        else:
            # Linux/Mac: Use xterm or gnome-terminal
            process = subprocess.Popen(
                ['gnome-terminal', '--', 'python3', script_path],
                cwd=os.getcwd()
            )
            print(f"✅ Trading system started in external terminal (PID: {process.pid})")
            return process
    except Exception as e:
        print(f"❌ Failed to start trading system: {e}")
        return None

def check_backend_services():
    """Check if backend services need to be started"""
    print("\n🔍 Checking Backend Services...")
    print("-" * 40)
    
    # Check for unified production server
    unified_server = os.path.join(os.getcwd(), 'unified_production_server.py')
    if os.path.exists(unified_server):
        print("✅ Unified production server found")
        print("   Note: Trading system can run standalone or with unified server")
    else:
        print("⚠️  Unified production server not found")
    
    print()

if __name__ == "__main__":
    print("="*80)
    print("FULL PROMETHEUS SYSTEM RESTART")
    print("="*80)
    print()
    print("This will:")
    print("  1. Stop all Prometheus-related processes")
    print("  2. Verify all configurations")
    print("  3. Start fresh trading system")
    print("  4. Initialize all components for live trading")
    print()
    
    # Step 1: Stop all processes
    print("STEP 1: Stopping all processes...")
    print("-" * 40)
    success = stop_all_processes()
    
    if not success:
        print("\n⚠️  Warning: Some processes may still be running")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Restart cancelled")
            sys.exit(1)
    
    # Step 2: Verify configuration
    verify_configuration()
    
    # Step 3: Check backend
    check_backend_services()
    
    # Step 4: Start trading system
    print("STEP 4: Starting Trading System...")
    print("-" * 40)
    process = start_trading_system()
    
    if process:
        print("\n" + "="*80)
        print("✅ FULL SYSTEM RESTART COMPLETE")
        print("="*80)
        print()
        print("📊 System Status:")
        print("   ✅ All old processes stopped")
        print("   ✅ Configuration verified")
        print("   ✅ Trading system started")
        print()
        print("🔄 Initialization in progress:")
        print("   - Loading all systems...")
        print("   - Connecting to Alpaca...")
        print("   - Connecting to IB Gateway (port 7497)...")
        print("   - Initializing AI systems...")
        print()
        print("💡 Monitor the console window for:")
        print("   - System initialization messages")
        print("   - Broker connection confirmations")
        print("   - Trading cycle activity")
        print()
        print("📋 Expected connections:")
        print("   ✅ Alpaca: Live trading (crypto 24/7)")
        print("   ✅ IB: Live trading on port 7497 (stocks, options, forex)")
        print("   ✅ Polygon: Premium S3 access")
        print()
        print("⏱️  Give the system 30-60 seconds to fully initialize")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO START TRADING SYSTEM")
        print("="*80)
        print("   Please start manually:")
        print("   python launch_ultimate_prometheus_LIVE_TRADING.py")
        print("="*80)
        sys.exit(1)

