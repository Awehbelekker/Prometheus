#!/usr/bin/env python3
"""Display Adaptive Market Learning Results"""
import json
from pathlib import Path

results_file = Path("ADAPTIVE_MARKET_LEARNING_RESULTS.json")

if not results_file.exists():
    print("❌ No adaptive learning results found")
    exit(1)

try:
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*70)
    print("🏆 ADAPTIVE MARKET LEARNING RESULTS")
    print("="*70)
    print(f"\nTimestamp: {data['timestamp']}")
    print(f"Regimes Tested: {data['regimes_tested']}")
    
    if 'summary' in data and data['summary']:
        print("\n" + "="*70)
        print("📊 PERFORMANCE BY MARKET REGIME")
        print("="*70)
        print(f"\n{'Regime':<30} {'CAGR':>10} {'Sharpe':>10} {'Win%':>10} {'MaxDD':>10}")
        print("-"*70)
        
        for s in data['summary']:
            regime = s['regime']
            cagr = s['cagr'] * 100
            sharpe = s['sharpe']
            win_rate = s['win_rate'] * 100
            max_dd = s['max_dd'] * 100
            
            print(f"{regime:<30} {cagr:>9.1f}% {sharpe:>10.2f} {win_rate:>9.1f}% {max_dd:>9.1f}%")
        
        print("="*70)
        
        # Find best performers
        best_cagr = max(data['summary'], key=lambda x: x['cagr'])
        best_sharpe = max(data['summary'], key=lambda x: x['sharpe'])
        best_wr = max(data['summary'], key=lambda x: x['win_rate'])
        best_dd = max(data['summary'], key=lambda x: -x['max_dd'])
        
        print("\n🏆 BEST PERFORMERS:")
        print(f"   Highest CAGR:   {best_cagr['regime']} ({best_cagr['cagr']*100:.1f}%)")
        print(f"   Best Sharpe:    {best_sharpe['regime']} ({best_sharpe['sharpe']:.2f})")
        print(f"   Highest Win%:   {best_wr['regime']} ({best_wr['win_rate']*100:.1f}%)")
        print(f"   Best Drawdown:  {best_dd['regime']} ({best_dd['max_dd']*100:.1f}%)")
        print()
    else:
        print("\n⚠️ Summary data not available")
        print(f"Regime results keys: {list(data['regime_results'].keys())}")

except json.JSONDecodeError as e:
    print(f"❌ JSON parse error: {e}")
    print("File may be incomplete or corrupted")
except Exception as e:
    print(f"❌ Error: {e}")
