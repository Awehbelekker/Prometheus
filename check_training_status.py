#!/usr/bin/env python3
"""
Quick Status Checker for Extended Training
Shows progress and estimated completion time
"""

import json
import time
from datetime import datetime
from pathlib import Path

def check_status():
    """Check status of all running systems"""
    print("="*80)
    print("📊 PROMETHEUS SYSTEMS STATUS")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Learning Engine Status
    try:
        with open('ultimate_strategies.json', 'r') as f:
            strategies = json.load(f)
        
        total_strategies = len(strategies)
        tested_strategies = sum(1 for s in strategies.values() if s.get('total_trades', 0) >= 100)
        total_backtests = sum(s.get('total_trades', 0) for s in strategies.values())
        
        print("🧬 LEARNING ENGINE:")
        print(f"   Strategies Evolved: {total_strategies}")
        print(f"   Well-Tested (100+ trades): {tested_strategies}")
        print(f"   Total Backtests: {total_backtests:,}")
        
        # Top strategy
        best = max(strategies.values(), key=lambda x: x.get('sharpe_ratio', 0))
        print(f"   Top Strategy: {best.get('name')} (Sharpe: {best.get('sharpe_ratio', 0):.2f}, Win: {best.get('win_rate', 0)*100:.1f}%)")
        print()
        
    except:
        print("🧬 LEARNING ENGINE: Not yet started\n")
    
    # 2. Claude Vision Training Status
    try:
        with open('visual_ai_patterns_cloud.json', 'r') as f:
            patterns = json.load(f)
        
        analyzed = patterns.get('total_analyzed', 0)
        found = patterns.get('total_patterns', 0)
        
        print("☁️ CLAUDE VISION TRAINING:")
        print(f"   Charts Analyzed: {analyzed}/1320 ({analyzed/1320*100:.1f}%)")
        print(f"   Patterns Found: {found}")
        
        if analyzed < 1320:
            remaining = 1320 - analyzed
            rate = 12  # charts/minute
            minutes_left = remaining / rate
            print(f"   ETA: {minutes_left:.0f} minutes")
        else:
            print(f"   Status: ✅ COMPLETE")
        print()
        
    except:
        print("☁️ CLAUDE VISION TRAINING: Not yet started\n")
    
    # 3. Extended Training Status
    extended_files = list(Path('.').glob('extended_training_*yr*.json'))
    
    if extended_files:
        latest = max(extended_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest, 'r') as f:
            results = json.load(f)
        
        print("📈 EXTENDED HISTORICAL TRAINING:")
        print(f"   Latest: {latest.name}")
        
        if results:
            best = results[0]
            years = best.get('years_tested', 5)
            cagr = best.get('avg_cagr_pct', 0)
            sharpe = best.get('avg_sharpe_ratio', 0)
            
            print(f"   Period: {years:.0f} years")
            print(f"   Best Strategy: {best.get('strategy_name')}")
            print(f"   CAGR: {cagr:.2f}%")
            print(f"   Sharpe: {sharpe:.2f}")
            print(f"   Status: ✅ COMPLETE")
        print()
    else:
        print("📈 EXTENDED HISTORICAL TRAINING: Running or not started\n")
    
    # 4. Benchmark Status
    benchmark_files = list(Path('.').glob('prometheus_realworld_benchmark_*.txt'))
    
    if benchmark_files:
        latest = max(benchmark_files, key=lambda p: p.stat().st_mtime)
        
        print("🏆 LATEST BENCHMARK:")
        print(f"   File: {latest.name}")
        print(f"   Status: ✅ COMPLETE")
        print()
    
    print("="*80)
    print("\n💡 TIP: Run benchmarks again after extended training completes")
    print("   Command: python run_realworld_benchmarks.py\n")


if __name__ == "__main__":
    check_status()
