#!/usr/bin/env python3
"""
Restart Prometheus Trading System
Stops old processes and starts fresh with new API keys
"""
import sys
import psutil
import os
import time
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def find_trading_processes():
    """Find all trading-related Python processes"""
    trading_keywords = ['launch_ultimate_prometheus_LIVE_TRADING', 'trading']
    found_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(keyword in cmdline.lower() for keyword in trading_keywords):
                    found_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return found_processes

def stop_trading_processes():
    """Stop all trading processes"""
    processes = find_trading_processes()
    
    if not processes:
        print("✅ No trading processes found running")
        return True
    
    print(f"🛑 Found {len(processes)} trading process(es) to stop:")
    for proc in processes:
        try:
            print(f"   Stopping PID {proc.info['pid']}...")
            proc.terminate()
        except Exception as e:
            print(f"   ⚠️  Could not stop PID {proc.info['pid']}: {e}")
            try:
                proc.kill()
                print(f"   ✅ Force killed PID {proc.info['pid']}")
            except:
                pass
    
    # Wait for processes to terminate
    print("\n⏳ Waiting for processes to stop...")
    time.sleep(3)
    
    # Check if any are still running
    remaining = find_trading_processes()
    if remaining:
        print(f"⚠️  {len(remaining)} process(es) still running, force killing...")
        for proc in remaining:
            try:
                proc.kill()
            except:
                pass
        time.sleep(1)
    
    final_check = find_trading_processes()
    if final_check:
        print(f"❌ {len(final_check)} process(es) still running")
        return False
    else:
        print("✅ All trading processes stopped")
        return True

def start_trading_system():
    """Start the trading system"""
    print("\n🚀 Starting Prometheus Trading System...")
    print("   Loading new API keys from .env...")
    print()
    
    script_path = os.path.join(os.getcwd(), 'launch_ultimate_prometheus_LIVE_TRADING.py')
    
    if not os.path.exists(script_path):
        print(f"❌ Trading script not found: {script_path}")
        return None
    
    try:
        # Start in new process (detached)
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        print(f"✅ Trading system started (PID: {process.pid})")
        print("   Check the console window for trading activity")
        return process
    except Exception as e:
        print(f"❌ Failed to start trading system: {e}")
        return None

if __name__ == "__main__":
    print("="*80)
    print("RESTARTING PROMETHEUS TRADING SYSTEM")
    print("="*80)
    print()
    
    # Step 1: Stop old processes
    print("STEP 1: Stopping old trading processes...")
    print("-" * 40)
    success = stop_trading_processes()
    
    if not success:
        print("\n⚠️  Warning: Some processes may still be running")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Restart cancelled")
            sys.exit(1)
    
    # Step 2: Start new process
    print("\nSTEP 2: Starting fresh trading system...")
    print("-" * 40)
    process = start_trading_system()
    
    if process:
        print("\n" + "="*80)
        print("✅ TRADING SYSTEM RESTARTED SUCCESSFULLY")
        print("="*80)
        print()
        print("📊 The system will now:")
        print("   - Load new API keys from .env")
        print("   - Connect to Alpaca with new credentials")
        print("   - Start analyzing markets every 30 seconds")
        print("   - Execute trades when opportunities are found")
        print()
        print("💡 Monitor activity:")
        print("   - Watch the console window for trading cycles")
        print("   - Check logs: prometheus_live_trading_*.log")
        print("   - View dashboard: python view_alpaca_live_trading.py")
        print()
        print("🛑 To stop: Close the console window or press Ctrl+C")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO START TRADING SYSTEM")
        print("="*80)
        print("   Please start manually:")
        print("   python launch_ultimate_prometheus_LIVE_TRADING.py")
        print("="*80)
        sys.exit(1)
