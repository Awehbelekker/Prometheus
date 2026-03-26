#!/usr/bin/env python3
"""Check progress of running backtests"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_backtest_progress():
    """Check backtest progress"""
    print("=" * 80)
    print("BACKTEST PROGRESS CHECK")
    print("=" * 80)
    print()
    
    # Check for result files
    result_files = list(Path('.').glob('comprehensive_backtest_results_*.json'))
    pattern_files = list(Path('.').glob('learned_patterns_*.json'))
    log_files = list(Path('.').glob('backtest_*.log'))
    
    print("FILES FOUND:")
    print(f"  Result files: {len(result_files)}")
    print(f"  Pattern files: {len(pattern_files)}")
    print(f"  Log files: {len(log_files)}")
    print()
    
    if result_files:
        latest_result = max(result_files, key=lambda f: f.stat().st_mtime)
        print(f"LATEST RESULTS: {latest_result.name}")
        
        try:
            with open(latest_result, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            print(f"  Timeframes tested: {len(results)}")
            for timeframe, data in results.items():
                if data:
                    print(f"    {timeframe}: {len(data)} symbols")
        except Exception as e:
            print(f"  Error reading file: {e}")
    
    if pattern_files:
        latest_patterns = max(pattern_files, key=lambda f: f.stat().st_mtime)
        print(f"\nLATEST PATTERNS: {latest_patterns.name}")
        
        try:
            with open(latest_patterns, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
            
            total_patterns = sum(len(v) for v in patterns.values() if isinstance(v, dict))
            print(f"  Total pattern sets: {total_patterns}")
        except Exception as e:
            print(f"  Error reading file: {e}")
    
    if log_files:
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        print(f"\nLATEST LOG: {latest_log.name}")
        print(f"  Size: {latest_log.stat().st_size / 1024:.1f} KB")
        print(f"  Modified: {datetime.fromtimestamp(latest_log.stat().st_mtime)}")

if __name__ == "__main__":
    check_backtest_progress()
