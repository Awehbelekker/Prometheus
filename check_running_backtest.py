#!/usr/bin/env python3
"""
Check if 100-Year Backtest is Running
Comprehensive check for running backtest processes
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import psutil
import time
from pathlib import Path

def check_running_backtest():
    """Check if backtest is running"""
    print("="*80)
    print("CHECKING FOR RUNNING 100-YEAR BACKTEST")
    print("="*80)
    
    backtest_found = False
    
    # Check all Python processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Check if it's the backtest
                if 'backtest_100_years' in cmdline or '100_years' in cmdline:
                    backtest_found = True
                    runtime = time.time() - proc.info['create_time']
                    hours = int(runtime // 3600)
                    minutes = int((runtime % 3600) // 60)
                    seconds = int(runtime % 60)
                    
                    print(f"\n✅ BACKTEST PROCESS FOUND!")
                    print(f"   PID: {proc.info['pid']}")
                    print(f"   Command: {cmdline[:100]}...")
                    print(f"   Runtime: {hours}h {minutes}m {seconds}s")
                    print(f"   CPU: {proc.info['cpu_percent']:.1f}%")
                    print(f"   Memory: {proc.info['memory_info'].rss / 1024 / 1024:.1f} MB")
                    print(f"   Status: RUNNING")
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not backtest_found:
        print("\n⏳ NO BACKTEST PROCESS FOUND")
        print("   The backtest may have:")
        print("   - Completed (check for results files)")
        print("   - Not started yet")
        print("   - Stopped/errored")
        print("\n   To start: python backtest_100_years_full_prometheus.py")
    
    # Check for results files
    print("\n" + "="*80)
    print("CHECKING FOR RESULTS FILES")
    print("="*80)
    
    result_files = list(Path('.').glob('backtest_100_years_*.json'))
    if result_files:
        latest = max(result_files, key=lambda f: f.stat().st_mtime)
        file_time = latest.stat().st_mtime
        file_size = latest.stat().st_size
        
        print(f"\n✅ RESULTS FILE FOUND!")
        print(f"   File: {latest.name}")
        print(f"   Modified: {time.ctime(file_time)}")
        print(f"   Size: {file_size:,} bytes")
        print(f"   Status: COMPLETED")
        
        # Try to load and show summary
        try:
            import json
            with open(latest, 'r') as f:
                results = json.load(f)
            
            print(f"\n   Quick Summary:")
            print(f"   - Final Value: ${results.get('final_value', 0):,.2f}")
            print(f"   - CAGR: {results.get('cagr', 0):.2f}%")
            print(f"   - Win Rate: {results.get('win_rate', 0)*100:.2f}%")
            print(f"   - Trades: {results.get('num_trades', 0):,}")
        except:
            pass
    else:
        print("\n⏳ NO RESULTS FILES FOUND")
        print("   Backtest may still be running or hasn't completed")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        check_running_backtest()
    except ImportError:
        print("⚠️ psutil not available, using basic check...")
        print("   Install with: pip install psutil")
        print("\nChecking for Python processes manually...")
        import subprocess
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                print("   ✅ Python processes detected")
                print("   (Cannot determine if backtest is running without psutil)")
            else:
                print("   ⏳ No Python processes found")
        except:
            print("   ⚠️ Could not check processes")

