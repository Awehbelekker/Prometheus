#!/usr/bin/env python3
"""
Multi-parameter sweep for PROMETHEUS 50-year benchmark.
Phase 1: Coarse grid over 7 env-var knobs.
Phase 2: Fine-tune around best combo from Phase 1.

Targets: Sharpe >= 3.20, MaxDD >= -7.0%, CAGR ~41%
(matching March 9 golden baseline)
"""
import subprocess, sys, os, re, json, time, itertools
from datetime import datetime
from pathlib import Path

PYTHON = str(Path(sys.executable))
BENCH  = "prometheus_50_year_competitor_benchmark.py"
BASE   = Path(__file__).parent

# ── Baseline targets ─────────────────────────────────────────
TARGET_SHARPE = 3.275
TARGET_MAXDD  = -0.0636
TARGET_CAGR   = 0.4105

def run_bench(params: dict) -> dict:
    """Run benchmark with given env vars, parse Legacy results."""
    env = os.environ.copy()
    for k, v in params.items():
        env[k] = str(v)
    
    t0 = time.time()
    proc = subprocess.run(
        [PYTHON, BENCH],
        capture_output=True, text=True, timeout=300,
        cwd=str(BASE), env=env
    )
    elapsed = time.time() - t0
    
    output = proc.stdout + proc.stderr
    
    # Parse Legacy metrics from log output
    result = {'elapsed': elapsed, 'exit_code': proc.returncode}
    
    # Look for PROMETHEUS completed line
    m = re.search(r'Final Capital: \$([0-9,.]+)', output)
    if m:
        result['final_capital'] = float(m.group(1).replace(',', ''))
    
    m = re.search(r'CAGR: ([0-9.]+)%', output)
    if m:
        result['cagr'] = float(m.group(1)) / 100
    
    m = re.search(r'Sharpe Ratio: ([0-9.]+)', output)
    if m:
        result['sharpe'] = float(m.group(1))
    
    m = re.search(r'Max Drawdown: (-[0-9.]+)%', output)
    if m:
        result['maxdd'] = float(m.group(1)) / 100
    
    m = re.search(r'Win Rate: ([0-9.]+)%', output)
    if m:
        result['winrate'] = float(m.group(1)) / 100
    
    m = re.search(r'Total Trades: (\d+)', output)
    if m:
        result['trades'] = int(m.group(1))
    
    return result


def score(r: dict) -> float:
    """
    Score a result.  Higher = better.
    Weights: 40% Sharpe gap, 40% MaxDD gap, 20% CAGR proximity.
    """
    sharpe = r.get('sharpe', 0)
    maxdd  = r.get('maxdd', -1.0)
    cagr   = r.get('cagr', 0)
    
    if sharpe == 0:
        return -999
    
    # Sharpe: penalize being below target, reward being above
    sharpe_gap = sharpe - TARGET_SHARPE  # positive = better
    
    # MaxDD: penalize being worse (more negative) than target
    maxdd_gap = maxdd - TARGET_MAXDD  # positive = MaxDD less severe → better
    # Normalize: MaxDD ranges ~0.05 to 0.20
    
    # CAGR: reward being close to target (don't want too low)
    cagr_gap = cagr - TARGET_CAGR  # positive = higher CAGR → OK but not main objective
    cagr_penalty = -abs(cagr_gap) * 0.5 if cagr < 0.30 else 0  # heavy penalty if CAGR < 30%
    
    return (
        sharpe_gap * 4.0     # 1 point of Sharpe = 4 score units
        + maxdd_gap * 20.0   # 0.01 (1pp) MaxDD improvement = 0.2 score units
        + min(cagr_gap, 0.10) * 1.0  # cap CAGR bonus
        + cagr_penalty
    )


def print_row(i, params, r, sc):
    sharpe = r.get('sharpe', 0)
    maxdd  = r.get('maxdd', 0) * 100
    cagr   = r.get('cagr', 0) * 100
    winr   = r.get('winrate', 0) * 100
    tr     = r.get('trades', 0)
    lev    = params.get('PROMETHEUS_MAX_LEVERAGE', 1.25)
    mom    = params.get('PROMETHEUS_MOMENTUM_SCALE', 1.0)
    shock  = params.get('PROMETHEUS_SHOCK_SCALE', 1.0)
    gt     = params.get('PROMETHEUS_GUARDIAN_TRAILING', -0.08)
    gc     = params.get('PROMETHEUS_GUARDIAN_CRITICAL', -0.18)
    be     = params.get('PROMETHEUS_BEAR_EXPOSURE', 0.24)
    ve     = params.get('PROMETHEUS_VOLATILE_EXPOSURE', 0.55)
    print(f"  {i:>3}  Lev={lev:<5} Mom={mom:<4} Shk={shock:<4} GT={gt:<6} GC={gc:<6} "
          f"BE={be:<5} VE={ve:<5} │ "
          f"CAGR={cagr:>6.2f}% Sharpe={sharpe:>5.3f} MaxDD={maxdd:>7.2f}% "
          f"Win={winr:>5.1f}% Trades={tr:>5} Score={sc:>+6.3f}")


def main():
    print("=" * 120)
    print("  PROMETHEUS MULTI-PARAMETER SWEEP")
    print(f"  Target: Sharpe≥{TARGET_SHARPE:.3f}  MaxDD≥{TARGET_MAXDD*100:.2f}%  CAGR~{TARGET_CAGR*100:.1f}%")
    print("=" * 120)
    
    # ── Phase 1: Coarse grid ─────────────────────────────────
    # Key hypothesis: the golden baseline had (a) no leverage, (b) tighter guardian,
    # (c) more aggressive shock detector, (d) lower bear/vol exposure
    
    coarse_grid = {
        'PROMETHEUS_MAX_LEVERAGE':      [1.00, 1.10, 1.25],
        'PROMETHEUS_MOMENTUM_SCALE':    [0.0, 0.5, 1.0],
        'PROMETHEUS_SHOCK_SCALE':       [1.0, 1.5, 2.0],
        'PROMETHEUS_GUARDIAN_TRAILING':  [-0.04, -0.06, -0.08],
        'PROMETHEUS_GUARDIAN_CRITICAL':  [-0.10, -0.14, -0.18],
        'PROMETHEUS_BEAR_EXPOSURE':     [0.10, 0.24],
        'PROMETHEUS_VOLATILE_EXPOSURE': [0.35, 0.55],
    }
    
    # Full cartesian product is 3*3*3*3*3*2*2 = 972 — too many.
    # Use a stratified sample: vary 2-3 params at a time, fix others.
    
    # Strategy: test the most impactful params first (leverage, guardian, shock),
    # then combine winners with secondary params (momentum, exposure).
    
    all_results = []
    run_idx = 0
    
    print("\n─── Phase 1a: Leverage × Guardian × Shock (core risk params) ───")
    print(f"  {'#':>3}  {'Parameters':<65} │ {'Results'}")
    print(f"  {'─'*3}  {'─'*65} │ {'─'*60}")
    
    # Phase 1a: Core risk params (3×3×3×3×3 = 243, but we'll do a Latin hypercube-ish subset)
    # Fix: momentum=1.0, bear=0.24, volatile=0.55
    phase1a_combos = list(itertools.product(
        [1.00, 1.10, 1.25],               # leverage
        [1.0, 1.5, 2.0],                  # shock
        [-0.04, -0.06, -0.08],            # guardian trailing
        [-0.10, -0.14, -0.18],            # guardian critical
    ))
    
    for lev, shock, gt, gc in phase1a_combos:
        # Guardian critical must be worse than trailing
        if gc > gt:
            continue
        
        params = {
            'PROMETHEUS_MAX_LEVERAGE': lev,
            'PROMETHEUS_MOMENTUM_SCALE': 1.0,
            'PROMETHEUS_SHOCK_SCALE': shock,
            'PROMETHEUS_GUARDIAN_TRAILING': gt,
            'PROMETHEUS_GUARDIAN_CRITICAL': gc,
            'PROMETHEUS_BEAR_EXPOSURE': 0.24,
            'PROMETHEUS_VOLATILE_EXPOSURE': 0.55,
        }
        
        run_idx += 1
        r = run_bench(params)
        sc = score(r)
        all_results.append((params.copy(), r, sc))
        print_row(run_idx, params, r, sc)
    
    # Sort Phase 1a by score
    all_results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n  Phase 1a: {run_idx} runs completed")
    best_params, best_result, best_score = all_results[0]
    print(f"  Best so far: Score={best_score:+.3f}")
    print_row(0, best_params, best_result, best_score)
    
    # Phase 1b: Take top-3 combos and vary momentum + exposure
    print(f"\n─── Phase 1b: Refine top-3 with Momentum × Exposure ───")
    print(f"  {'#':>3}  {'Parameters':<65} │ {'Results'}")
    print(f"  {'─'*3}  {'─'*65} │ {'─'*60}")
    
    top3 = all_results[:3]
    for base_params, _, _ in top3:
        for mom in [0.0, 0.5, 1.0]:
            for be in [0.10, 0.24]:
                for ve in [0.35, 0.55]:
                    # Skip the default combo (already tested)
                    if mom == 1.0 and be == 0.24 and ve == 0.55:
                        continue
                    
                    params = base_params.copy()
                    params['PROMETHEUS_MOMENTUM_SCALE'] = mom
                    params['PROMETHEUS_BEAR_EXPOSURE'] = be
                    params['PROMETHEUS_VOLATILE_EXPOSURE'] = ve
                    
                    run_idx += 1
                    r = run_bench(params)
                    sc = score(r)
                    all_results.append((params.copy(), r, sc))
                    print_row(run_idx, params, r, sc)
    
    # Final ranking
    all_results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'=' * 120}")
    print(f"  FINAL RANKING (top 10 of {len(all_results)} runs)")
    print(f"{'=' * 120}")
    print(f"  {'Rank':>4}  {'Parameters':<65} │ {'Results'}")
    print(f"  {'─'*4}  {'─'*65} │ {'─'*60}")
    
    for rank, (params, r, sc) in enumerate(all_results[:10], 1):
        print(f"  #{rank:<3}", end="")
        print_row(0, params, r, sc)
    
    # Compare to baseline
    print(f"\n  BASELINE TARGET: CAGR={TARGET_CAGR*100:.2f}% Sharpe={TARGET_SHARPE:.3f} MaxDD={TARGET_MAXDD*100:.2f}%")
    
    winner_params, winner_result, winner_score = all_results[0]
    print(f"\n  WINNER:")
    for k, v in sorted(winner_params.items()):
        print(f"    {k} = {v}")
    print(f"    → CAGR={winner_result.get('cagr',0)*100:.2f}%  "
          f"Sharpe={winner_result.get('sharpe',0):.3f}  "
          f"MaxDD={winner_result.get('maxdd',0)*100:.2f}%  "
          f"Win={winner_result.get('winrate',0)*100:.1f}%")
    
    # Save results
    out = {
        'timestamp': datetime.now().isoformat(),
        'total_runs': len(all_results),
        'target': {'sharpe': TARGET_SHARPE, 'maxdd': TARGET_MAXDD, 'cagr': TARGET_CAGR},
        'winner': {'params': winner_params, 'result': winner_result, 'score': winner_score},
        'top10': [
            {'rank': i+1, 'params': p, 'result': r, 'score': s}
            for i, (p, r, s) in enumerate(all_results[:10])
        ],
    }
    outfile = BASE / f"param_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    outfile.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n  Results saved: {outfile.name}")


if __name__ == '__main__':
    main()
