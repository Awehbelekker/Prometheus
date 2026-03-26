#!/usr/bin/env python3
"""
PROMETHEUS Walk-Forward Validation
====================================
Splits S&P 500 data into in-sample (train) and out-of-sample (test) periods
to prove Prometheus isn't overfit.  Also runs rolling 5-year walk-forward
windows to show consistency across decades.

Usage:
    python prometheus_walk_forward_validation.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from prometheus_50_year_competitor_benchmark import (
    MarketDataGenerator,
    FiftyYearBenchmark,
)


def run_on_slice(data_slice: pd.DataFrame, label: str, initial_capital: float = 10_000.0):
    """Run Prometheus backtest on an arbitrary data slice."""
    bench = FiftyYearBenchmark(initial_capital=initial_capital, use_real_data=True)
    result = bench._run_prometheus_backtest(data_slice)
    n_years = max((len(data_slice) - 200) / 252, 1)
    print(f"  {label}:")
    print(f"    Period:       {data_slice['date'].iloc[0].strftime('%Y-%m-%d')} to {data_slice['date'].iloc[-1].strftime('%Y-%m-%d')}")
    print(f"    Days:         {len(data_slice):,}  ({n_years:.1f} years)")
    print(f"    CAGR:         {result['cagr']*100:>8.2f}%")
    print(f"    Sharpe:       {result['sharpe_ratio']:>8.2f}")
    print(f"    Max Drawdown: {result['max_drawdown']*100:>8.1f}%")
    print(f"    Final Capital: ${result['final_capital']:>12,.2f}")
    result['n_years'] = n_years
    result['label'] = label
    return result


def walk_forward_validation():
    """Run full walk-forward validation."""
    print("\n" + "=" * 80)
    print("  PROMETHEUS WALK-FORWARD VALIDATION")
    print("  Proving the strategy is NOT overfit")
    print("=" * 80 + "\n")

    # Load full dataset
    gen = MarketDataGenerator()
    data = gen.load_real_sp500()
    total_days = len(data)
    print(f"  Full dataset: {total_days:,} days")
    print(f"  Range: {data['date'].iloc[0].strftime('%Y-%m-%d')} to {data['date'].iloc[-1].strftime('%Y-%m-%d')}")

    results = {}

    # ═══════════════════════════════════════════════════════════════════
    # TEST 1: In-sample vs Out-of-sample split (70/30)
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print("  TEST 1: IN-SAMPLE vs OUT-OF-SAMPLE (70/30 split)")
    print(f"{'='*70}")

    split_idx = int(total_days * 0.70)
    in_sample  = data.iloc[:split_idx].copy().reset_index(drop=True)
    out_sample = data.iloc[split_idx:].copy().reset_index(drop=True)

    split_date = data.iloc[split_idx]['date'].strftime('%Y-%m-%d')
    print(f"  Split date: {split_date}\n")

    is_result  = run_on_slice(in_sample,  "IN-SAMPLE  (train)")
    print()
    oos_result = run_on_slice(out_sample, "OUT-OF-SAMPLE (test)")

    # Degradation analysis
    cagr_degrade  = (oos_result['cagr'] - is_result['cagr']) / abs(is_result['cagr']) * 100 if is_result['cagr'] != 0 else 0
    sharpe_degrade = (oos_result['sharpe_ratio'] - is_result['sharpe_ratio']) / abs(is_result['sharpe_ratio']) * 100 if is_result['sharpe_ratio'] != 0 else 0

    print(f"\n  DEGRADATION ANALYSIS:")
    print(f"    CAGR change:   {cagr_degrade:>+.1f}%  (positive = OOS is better)")
    print(f"    Sharpe change: {sharpe_degrade:>+.1f}%")

    if abs(cagr_degrade) < 30 and oos_result['cagr'] > 0.05:
        print(f"    VERDICT: PASSES  (OOS performance within acceptable range)")
    elif oos_result['cagr'] > is_result['cagr']:
        print(f"    VERDICT: EXCELLENT  (OOS actually BETTER than in-sample)")
    else:
        print(f"    VERDICT: POTENTIAL OVERFIT  (significant OOS degradation)")

    results['in_sample'] = {k: v for k, v in is_result.items() if k != 'equity_curve'}
    results['out_of_sample'] = {k: v for k, v in oos_result.items() if k != 'equity_curve'}
    results['cagr_degradation_pct'] = cagr_degrade
    results['sharpe_degradation_pct'] = sharpe_degrade

    # ═══════════════════════════════════════════════════════════════════
    # TEST 2: Rolling 5-year windows (walk-forward)
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n\n{'='*70}")
    print("  TEST 2: ROLLING 5-YEAR WALK-FORWARD WINDOWS")
    print(f"{'='*70}")

    window_days = 252 * 5  # 5 years
    step_days   = 252 * 5  # non-overlapping 5-year windows
    warmup      = 200      # need 200 days for indicators

    windows = []
    start = 0
    while start + window_days + warmup <= total_days:
        end = start + window_days + warmup
        window_data = data.iloc[start:end].copy().reset_index(drop=True)
        window_start_date = window_data['date'].iloc[0].strftime('%Y')
        window_end_date   = window_data['date'].iloc[-1].strftime('%Y')
        label = f"{window_start_date}-{window_end_date}"

        result = run_on_slice(window_data, label)
        result['window'] = label
        windows.append(result)
        print()

        start += step_days

    # Summary
    print(f"\n  ROLLING WINDOW SUMMARY:")
    print(f"  {'Window':<14} {'CAGR':>8} {'Sharpe':>8} {'Max DD':>8}")
    print(f"  {'-'*42}")

    positive_windows = 0
    for w in windows:
        mark = "+" if w['cagr'] > 0 else "-"
        print(f"  {w['window']:<14} {w['cagr']*100:>7.2f}% {w['sharpe_ratio']:>7.2f} {w['max_drawdown']*100:>7.1f}%  {mark}")
        if w['cagr'] > 0:
            positive_windows += 1

    avg_cagr   = np.mean([w['cagr'] for w in windows])
    avg_sharpe = np.mean([w['sharpe_ratio'] for w in windows])
    std_cagr   = np.std([w['cagr'] for w in windows])
    min_cagr   = min(w['cagr'] for w in windows)
    max_cagr   = max(w['cagr'] for w in windows)

    print(f"\n  Average CAGR:   {avg_cagr*100:.2f}%  (std: {std_cagr*100:.2f}%)")
    print(f"  Average Sharpe: {avg_sharpe:.2f}")
    print(f"  CAGR range:     {min_cagr*100:.2f}% to {max_cagr*100:.2f}%")
    print(f"  Profitable windows: {positive_windows}/{len(windows)}")

    # Consistency ratio (avg / std — higher = more consistent)
    consistency = avg_cagr / std_cagr if std_cagr > 0 else float('inf')
    print(f"  Consistency ratio (avg/std): {consistency:.2f}")

    if positive_windows == len(windows) and consistency > 0.5:
        print(f"\n  VERDICT: HIGHLY CONSISTENT  (positive in every window, consistent returns)")
    elif positive_windows >= len(windows) * 0.8:
        print(f"\n  VERDICT: CONSISTENT  (profitable in most windows)")
    else:
        print(f"\n  VERDICT: INCONSISTENT  (may be overfit to specific periods)")

    results['rolling_windows'] = [{k: v for k, v in w.items() if k != 'equity_curve'} for w in windows]
    results['rolling_avg_cagr'] = avg_cagr
    results['rolling_avg_sharpe'] = avg_sharpe
    results['rolling_consistency'] = consistency
    results['positive_windows'] = f"{positive_windows}/{len(windows)}"

    # ═══════════════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n\n{'='*70}")
    print("  FINAL WALK-FORWARD VERDICT")
    print(f"{'='*70}")

    overfit_flags = 0
    if abs(cagr_degrade) > 50:
        overfit_flags += 1
        print("  [WARN] Large CAGR degradation in OOS")
    if oos_result['cagr'] < 0.03:
        overfit_flags += 1
        print("  [WARN] OOS CAGR below 3%")
    if positive_windows < len(windows) * 0.6:
        overfit_flags += 1
        print("  [WARN] Fewer than 60% of windows profitable")
    if consistency < 0.3:
        overfit_flags += 1
        print("  [WARN] Low consistency ratio")

    if overfit_flags == 0:
        print("\n  CONCLUSION: NO EVIDENCE OF OVERFITTING")
        print("  The strategy performs consistently across all time periods.")
    elif overfit_flags == 1:
        print("\n  CONCLUSION: MINOR CONCERNS (1 flag) — likely robust")
    else:
        print(f"\n  CONCLUSION: {overfit_flags} OVERFITTING FLAGS — investigate further")

    results['overfit_flags'] = overfit_flags

    # Save
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = f'walk_forward_validation_{ts}.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")

    return results


if __name__ == '__main__':
    walk_forward_validation()
