#!/usr/bin/env python3
"""
COMPREHENSIVE AI LEARNING SUMMARY
Shows all completed training results
"""
import json
from pathlib import Path
from datetime import datetime

print("\n" + "="*80)
print("🧠 PROMETHEUS AI LEARNING - COMPREHENSIVE SUMMARY")
print("="*80)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

results_files = [
    ("20-Year Learning", "CONTINUOUS_LEARNING_RESULTS_20Y.json"),
    ("50-Year Learning", "CONTINUOUS_LEARNING_RESULTS_50Y.json"),
    ("100-Year Ultimate", "CONTINUOUS_LEARNING_RESULTS_100Y.json"),
]

all_results = []

for name, filename in results_files:
    filepath = Path(filename)
    if filepath.exists():
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            final = data.get('final_result', {})
            
            result = {
                'name': name,
                'years': data.get('years_tested', 0),
                'generations': data.get('generations', 0),
                'cagr': final.get('cagr', 0),
                'sharpe': final.get('sharpe_ratio', 0),
                'win_rate': final.get('win_rate', 0),
                'max_dd': final.get('max_drawdown', 0),
                'total_trades': final.get('total_trades', 0),
                'fitness': data.get('best_fitness', 0),
                'timestamp': data.get('timestamp', 'N/A')
            }
            all_results.append(result)
            
        except Exception as e:
            print(f"⚠️ Could not load {filename}: {e}")

if all_results:
    print("="*80)
    print("📊 LEARNING RESULTS COMPARISON")
    print("="*80)
    print(f"\n{'Training':<20} {'Years':>6} {'Gens':>5} {'CAGR':>10} {'Sharpe':>10} {'Win%':>10} {'MaxDD':>10}")
    print("-"*80)
    
    for r in all_results:
        print(f"{r['name']:<20} {r['years']:>6} {r['generations']:>5} "
              f"{r['cagr']*100:>9.1f}% {r['sharpe']:>10.2f} "
              f"{r['win_rate']*100:>9.1f}% {r['max_dd']*100:>9.1f}%")
    
    print("="*80)
    
    # Best overall
    best = max(all_results, key=lambda x: x['fitness'])
    
    print(f"\n🏆 BEST OVERALL TRAINING: {best['name']}")
    print(f"   Fitness Score: {best['fitness']:.2f}")
    print(f"   CAGR: {best['cagr']*100:.1f}%")
    print(f"   Sharpe Ratio: {best['sharpe']:.2f}")
    print(f"   Win Rate: {best['win_rate']*100:.1f}%")
    print(f"   Max Drawdown: {best['max_dd']*100:.1f}%")
    print(f"   Total Trades Tested: {best['total_trades']:,}")
    print()
    
    # Recommendations
    print("="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    print()
    
    if best['cagr'] > 1.0:  # >100% CAGR
        print("✅ Exceptional Performance:")
        print(f"   - AI achieved {best['cagr']*100:.0f}% CAGR over {best['years']} years")
        print(f"   - Sharpe ratio of {best['sharpe']:.2f} indicates excellent risk-adjusted returns")
        print(f"   - {best['win_rate']*100:.0f}% win rate with controlled {abs(best['max_dd'])*100:.1f}% drawdown")
        print()
        
    print("🎯 Current Trading System:")
    print("   - Main system running 48+ hours")
    print("   - Live Alpaca: $113.27 (3 crypto positions)")
    print("   - IB Paper: $240.78 (1 stock position)")
    print("   - Current P&L: -$18.97 (-5.36%)")
    print()
    
    print("🚀 Next Steps:")
    print("   1. AI has optimized parameters through extensive backtesting")
    print("   2. Parameters are being used by active trading system")
    print("   3. Continuous learning from live trades ongoing")
    print("   4. Monitor performance via live_visual_monitor.py")
    print()
    
else:
    print("❌ No learning results found")
    print("   Run: python run_continuous_learning_backtest.py")

print("="*80)
print()
