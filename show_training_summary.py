"""Quick summary of training results"""
import json
import glob

print("="*70)
print("PROMETHEUS TRAINING SUMMARY")
print("="*70)

# 1. Continuous Learning Results
try:
    with open('CONTINUOUS_LEARNING_RESULTS_20Y.json', 'r') as f:
        lr = json.load(f)
    print()
    print("1. CONTINUOUS LEARNING (20-Year Backtest)")
    print("-"*50)
    print(f"   Generations: {lr['generations']}")
    print(f"   Best CAGR: {lr['final_result']['cagr']*100:.1f}%")
    print(f"   Best Sharpe: {lr['final_result']['sharpe_ratio']:.2f}")
    print(f"   Best Win Rate: {lr['final_result']['win_rate']*100:.1f}%")
    print(f"   Max Drawdown: {lr['final_result']['max_drawdown']*100:.1f}%")
except Exception as e:
    print(f"   Error loading learning results: {e}")

# 2. Visual Pattern Training
try:
    with open('visual_ai_patterns.json', 'r') as f:
        vp = json.load(f)
    print()
    print("2. VISUAL CHART PATTERN TRAINING")
    print("-"*50)
    print(f"   Charts Analyzed: {vp['total_analyzed']}")
    print(f"   Successful: {vp['successful_analyses']}")
    print(f"   Patterns Found: {vp['total_patterns']}")
    top = sorted(vp.get('pattern_summary', {}).items(), key=lambda x: -x[1])[:5]
    if top:
        print(f"   Top Patterns: {', '.join([p for p,c in top])}")
except Exception as e:
    print(f"   Error loading visual patterns: {e}")

# 3. Learned Trading Patterns
try:
    files = sorted(glob.glob('learned_patterns*.json'))
    if files:
        with open(files[-1], 'r') as f:
            lp = json.load(f)
        total = sum(len(v) if isinstance(v, list) else 1 for v in lp.values())
        print()
        print("3. TRADING PATTERN LEARNING")
        print("-"*50)
        print(f"   Pattern File: {files[-1]}")
        print(f"   Symbols Trained: {len(lp)}")
        print(f"   Total Patterns: {total}")
except Exception as e:
    print(f"   Error loading patterns: {e}")

# 4. Learning State
try:
    with open('learning_state.json', 'r') as f:
        ls = json.load(f)
    print()
    print("4. LEARNING STATE (Saved for Continuation)")
    print("-"*50)
    print(f"   Generations Completed: {ls['generation']}")
    print(f"   Best Fitness: {ls['best_fitness']:.2f}")
    print(f"   Can Resume: YES")
except Exception as e:
    print(f"   No learning state saved")

print()
print("="*70)
print("TRAINING COMPLETE - SYSTEM READY!")
print("="*70)
