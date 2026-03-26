#!/usr/bin/env python3
"""
PROMETHEUS Multi-Asset Benchmark
=================================
Tests Prometheus on NASDAQ-100, AAPL, MSFT, and NVDA to prove the
strategy generalizes beyond S&P 500. Reuses the exact same backtest
engine from the 50-year competitive benchmark.

Usage:
    python prometheus_multi_asset_benchmark.py
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

# Reuse existing benchmark infrastructure
from prometheus_50_year_competitor_benchmark import (
    MarketDataGenerator,
    PrometheusSimulator,
    FiftyYearBenchmark,
)


# Assets to test  (label, csv path, buy-and-hold description)
ASSETS = [
    ('S&P 500',     'data/sp500_regime_labeled.csv',     'SPY buy-and-hold'),
    ('NASDAQ-100',  'data/nasdaq100_regime_labeled.csv',  'QQQ buy-and-hold'),
    ('AAPL',        'data/aapl_regime_labeled.csv',       'AAPL buy-and-hold'),
    ('MSFT',        'data/msft_regime_labeled.csv',       'MSFT buy-and-hold'),
    ('NVDA',        'data/nvda_regime_labeled.csv',       'NVDA buy-and-hold'),
]


def load_asset(path: str) -> pd.DataFrame:
    """Load any regime-labeled CSV and enrich it to match the benchmark schema."""
    gen = MarketDataGenerator()
    return gen.load_real_sp500(path)      # works for any CSV with date/close/volume/regime


def buy_and_hold_stats(data: pd.DataFrame, initial_capital: float = 10_000.0):
    """Compute buy-and-hold baseline for comparison."""
    start_price = data.iloc[200]['close']   # skip same 200-day warm-up
    end_price   = data.iloc[-1]['close']
    n_days  = len(data) - 200
    n_years = max(n_days / 252, 1)

    total_return = end_price / start_price
    cagr = total_return ** (1 / n_years) - 1

    # Drawdown
    prices = data['close'].iloc[200:].values
    peak = np.maximum.accumulate(prices)
    dd   = (prices - peak) / peak
    max_dd = dd.min()

    # Sharpe
    returns = pd.Series(prices).pct_change().dropna()
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

    final_capital = initial_capital * total_return

    return {
        'cagr':         cagr,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'final_capital': final_capital,
        'total_return':  total_return - 1,
        'n_years':       n_years,
    }


def run_multi_asset_benchmark():
    """Run Prometheus on every asset and compare vs buy-and-hold."""
    initial_capital = 10_000.0

    print("\n" + "=" * 80)
    print("  PROMETHEUS MULTI-ASSET BENCHMARK")
    print("  Proving the strategy generalizes beyond S&P 500")
    print("=" * 80 + "\n")

    all_results = {}

    for label, csv_path, bh_label in ASSETS:
        if not Path(csv_path).exists():
            logger.warning(f"  Skipping {label}: {csv_path} not found")
            continue

        print(f"\n{'='*70}")
        print(f"  ASSET: {label}  ({csv_path})")
        print(f"{'='*70}")

        # Load data
        data = load_asset(csv_path)
        n_years = max((len(data) - 200) / 252, 1)
        print(f"  Data: {len(data):,} days  ({n_years:.1f} years)")

        # Buy-and-hold baseline
        bh = buy_and_hold_stats(data, initial_capital)
        print(f"\n  {bh_label}:")
        print(f"    CAGR:         {bh['cagr']*100:>8.2f}%")
        print(f"    Sharpe:       {bh['sharpe_ratio']:>8.2f}")
        print(f"    Max Drawdown: {bh['max_drawdown']*100:>8.1f}%")
        print(f"    Final Capital: ${bh['final_capital']:>12,.2f}")

        # Prometheus backtest (fresh simulator per asset to avoid state leakage)
        bench = FiftyYearBenchmark(initial_capital=initial_capital, use_real_data=True)
        prom = bench._run_prometheus_backtest(data)

        print(f"\n  PROMETHEUS:")
        print(f"    CAGR:         {prom['cagr']*100:>8.2f}%")
        print(f"    Sharpe:       {prom['sharpe_ratio']:>8.2f}")
        print(f"    Max Drawdown: {prom['max_drawdown']*100:>8.1f}%")
        print(f"    Final Capital: ${prom['final_capital']:>12,.2f}")

        # Alpha over buy-and-hold
        alpha = prom['cagr'] - bh['cagr']
        sharpe_edge = prom['sharpe_ratio'] - bh['sharpe_ratio']
        dd_improvement = abs(prom['max_drawdown']) - abs(bh['max_drawdown'])

        verdict = "OUTPERFORMS" if alpha > 0 else "UNDERPERFORMS"
        print(f"\n  VERDICT: {verdict}")
        print(f"    Alpha (CAGR):        {alpha*100:>+.2f}%")
        print(f"    Sharpe edge:         {sharpe_edge:>+.2f}")
        print(f"    Drawdown improvement:{dd_improvement*100:>+.1f}%  (negative = better)")

        all_results[label] = {
            'buy_and_hold': bh,
            'prometheus':   prom,
            'alpha':        alpha,
            'sharpe_edge':  sharpe_edge,
            'n_years':      n_years,
        }

    # ── Summary table ────────────────────────────────────────────────
    print("\n\n" + "=" * 80)
    print("  MULTI-ASSET SUMMARY")
    print("=" * 80)
    header = f"  {'Asset':<12} {'Years':>6} {'BH CAGR':>9} {'PROM CAGR':>10} {'Alpha':>8} {'BH Sharpe':>10} {'PROM Sharpe':>12} {'BH DD':>8} {'PROM DD':>9}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    wins = 0
    total = 0
    for label in [a[0] for a in ASSETS]:
        if label not in all_results:
            continue
        r = all_results[label]
        bh = r['buy_and_hold']
        p  = r['prometheus']
        a  = r['alpha']
        total += 1
        if a > 0:
            wins += 1
        mark = " +" if a > 0 else " -"
        print(f"  {label:<12} {r['n_years']:>5.1f}y "
              f"{bh['cagr']*100:>8.2f}% "
              f"{p['cagr']*100:>9.2f}% "
              f"{a*100:>+7.2f}%"
              f"{bh['sharpe_ratio']:>10.2f} "
              f"{p['sharpe_ratio']:>11.2f} "
              f"{bh['max_drawdown']*100:>8.1f}% "
              f"{p['max_drawdown']*100:>8.1f}%"
              f"{mark}")

    print(f"\n  Prometheus beats buy-and-hold on {wins}/{total} assets")

    # Check generalization
    if total > 0:
        avg_alpha = np.mean([r['alpha'] for r in all_results.values()])
        avg_sharpe_edge = np.mean([r['sharpe_edge'] for r in all_results.values()])
        print(f"  Average alpha:       {avg_alpha*100:>+.2f}%")
        print(f"  Average Sharpe edge: {avg_sharpe_edge:>+.2f}")

        if wins >= total * 0.6:
            print("\n  CONCLUSION: Strategy GENERALIZES across asset classes")
        else:
            print("\n  CONCLUSION: Strategy may be overfit to S&P 500 dynamics")

    # Save results
    save_results = {}
    for label, r in all_results.items():
        bh = r['buy_and_hold']
        p  = r['prometheus']
        # Remove non-serializable equity_curve
        p_clean = {k: v for k, v in p.items() if k != 'equity_curve'}
        save_results[label] = {
            'buy_and_hold': bh,
            'prometheus': p_clean,
            'alpha_cagr': r['alpha'],
            'sharpe_edge': r['sharpe_edge'],
            'n_years': r['n_years'],
        }

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = f'multi_asset_benchmark_{ts}.json'
    with open(out_path, 'w') as f:
        json.dump(save_results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")

    return all_results


if __name__ == '__main__':
    run_multi_asset_benchmark()
