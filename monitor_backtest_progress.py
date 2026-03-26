#!/usr/bin/env python3
"""
Monitor Comprehensive Backtest Progress
Shows real-time progress of ongoing backtests
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def monitor_progress():
    """Monitor backtest progress"""
    print("=" * 80)
    print("COMPREHENSIVE BACKTEST PROGRESS MONITOR")
    print("=" * 80)
    print()
    
    # Check for log files
    log_files = sorted(Path('.').glob('backtest_*.log'), key=lambda f: f.stat().st_mtime, reverse=True)
    comprehensive_logs = sorted(Path('.').glob('comprehensive_backtest_*.log'), key=lambda f: f.stat().st_mtime, reverse=True)
    
    all_logs = log_files + comprehensive_logs
    
    if all_logs:
        latest_log = all_logs[0]
        print(f"Latest Log File: {latest_log.name}")
        print(f"  Size: {latest_log.stat().st_size / 1024:.1f} KB")
        print(f"  Modified: {datetime.fromtimestamp(latest_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Read last 20 lines
        try:
            with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print("Last 20 lines:")
                print("-" * 80)
                for line in lines[-20:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"Error reading log: {e}")
    else:
        print("No log files found yet.")
    
    print()
    print("-" * 80)
    
    # Check for result files
    result_files = list(Path('.').glob('*_backtest_report_*.md'))
    pattern_files = list(Path('.').glob('learned_patterns_*.json'))
    
    print("Generated Files:")
    print(f"  Result Reports: {len(result_files)}")
    print(f"  Pattern Files: {len(pattern_files)}")
    
    if result_files:
        print("\nLatest Reports:")
        for f in sorted(result_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    
    if pattern_files:
        print("\nLatest Patterns:")
        for f in sorted(pattern_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    monitor_progress()

