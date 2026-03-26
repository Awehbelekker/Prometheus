#!/usr/bin/env python3
"""
Benchmark suite runner implementing three lanes:
1) Regression lane: fixed-seed deterministic check
2) Robustness lane: multi-seed distribution testing
3) Stress lane: scenario-based risk testing

Usage examples:
  python _run_benchmark_suite.py --mode regression
  python _run_benchmark_suite.py --mode robustness --runs 50 --start-seed 1000
  python _run_benchmark_suite.py --mode stress --seed 42
  python _run_benchmark_suite.py --mode all --runs 50 --start-seed 1000 --seed 42
"""

import argparse
import json
import math
import statistics
from datetime import datetime

from prometheus_50_year_competitor_benchmark import FiftyYearBenchmark


DEFAULT_STRESS_SCENARIOS = [
    "flash_crash",
    "prolonged_bear",
    "vol_spike",
    "sideways_chop",
    "regime_whipsaw",
]


def extract_core(report):
    pr = report.get("prometheus_results", {})
    kr = report.get("kelly_results", {}) or {}
    return {
        "rank": report.get("prometheus_rank"),
        "seed": report.get("seed"),
        "scenario": report.get("scenario"),
        "legacy_cagr": pr.get("cagr"),
        "legacy_sharpe": pr.get("sharpe_ratio"),
        "legacy_maxdd": pr.get("max_drawdown"),
        "legacy_winrate": pr.get("win_rate"),
        "kelly_cagr": kr.get("cagr"),
        "kelly_sharpe": kr.get("sharpe_ratio"),
        "kelly_maxdd": kr.get("max_drawdown"),
    }


def make_json_safe(obj):
    """Recursively convert numpy/pandas scalar types to native Python."""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            return obj
    return obj


def run_single(seed, scenario, use_real_data=False):
    bench = FiftyYearBenchmark(
        initial_capital=10000.0,
        use_real_data=use_real_data,
        seed=seed,
        scenario=scenario,
    )
    report = bench.run_full_benchmark()
    return extract_core(report)


def pct(v):
    return f"{v * 100:+.2f}%"


def safe_mean(vals):
    vals = [v for v in vals if v is not None and not math.isnan(v)]
    return statistics.mean(vals) if vals else float("nan")


def safe_std(vals):
    vals = [v for v in vals if v is not None and not math.isnan(v)]
    return statistics.stdev(vals) if len(vals) > 1 else 0.0


def cv_pct(vals):
    m = safe_mean(vals)
    s = safe_std(vals)
    if m == 0 or math.isnan(m):
        return float("nan")
    return abs(s / m) * 100.0


def pass_fail_gates(robust_rows, stress_rows, mode):
    # Risk-first gates
    # - Legacy MaxDD mean >= -20%
    # - Legacy Sharpe mean >= 1.5
    # - Legacy CAGR 10th percentile >= 0%
    # - Rank #1 frequency >= 50%
    # - Stress worst MaxDD >= -35%
    legacy_cagr = sorted([r["legacy_cagr"] for r in robust_rows if r["legacy_cagr"] is not None])
    legacy_sharpe = [r["legacy_sharpe"] for r in robust_rows if r["legacy_sharpe"] is not None]
    legacy_maxdd = [r["legacy_maxdd"] for r in robust_rows if r["legacy_maxdd"] is not None]
    ranks = [r["rank"] for r in robust_rows if r["rank"] is not None]

    p10_idx = int(max(0, math.floor(0.10 * (len(legacy_cagr) - 1)))) if legacy_cagr else 0
    cagr_p10 = legacy_cagr[p10_idx] if legacy_cagr else float("nan")
    rank1_rate = (sum(1 for r in ranks if r == 1) / len(ranks) * 100.0) if ranks else 0.0

    stress_maxdd = [r["legacy_maxdd"] for r in stress_rows if r.get("legacy_maxdd") is not None]
    stress_worst_dd = min(stress_maxdd) if stress_maxdd else float("nan")

    has_robust = len(robust_rows) > 0
    has_stress = len(stress_rows) > 0
    enforce_robust = mode in ("robustness", "all", "regression")
    enforce_stress = mode in ("stress", "all")

    checks = {
        "legacy_maxdd_mean_ge_-20pct": (not enforce_robust) or (has_robust and bool(safe_mean(legacy_maxdd) >= -0.20)),
        "legacy_sharpe_mean_ge_1.5": (not enforce_robust) or (has_robust and bool(safe_mean(legacy_sharpe) >= 1.5)),
        "legacy_cagr_p10_ge_0pct": (not enforce_robust) or (has_robust and bool(cagr_p10 >= 0.0)),
        "rank1_rate_ge_50pct": (not enforce_robust) or (has_robust and bool(rank1_rate >= 50.0)),
        "stress_worst_dd_ge_-35pct": (not enforce_stress) or (has_stress and bool(stress_worst_dd >= -0.35)),
    }

    return {
        "checks": checks,
        "all_pass": all(checks.values()),
        "metrics": {
            "legacy_cagr_p10": cagr_p10,
            "legacy_sharpe_mean": safe_mean(legacy_sharpe),
            "legacy_maxdd_mean": safe_mean(legacy_maxdd),
            "rank1_rate_pct": rank1_rate,
            "stress_worst_maxdd": stress_worst_dd,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run benchmark policy suite")
    parser.add_argument("--mode", choices=["regression", "robustness", "stress", "all"], default="all")
    parser.add_argument("--runs", type=int, default=50, help="Number of seeds for robustness lane")
    parser.add_argument("--start-seed", type=int, default=1000, help="Starting seed for robustness lane")
    parser.add_argument("--seed", type=int, default=42, help="Seed for regression/stress lane")
    parser.add_argument("--real-data", action="store_true", help="Use real S&P 500 data where supported")
    args = parser.parse_args()

    started = datetime.now().isoformat()
    regression_rows = []
    robustness_rows = []
    stress_rows = []

    if args.mode in ("regression", "all"):
        print("[regression] running fixed-seed baseline...")
        regression_rows.append(run_single(seed=42, scenario="base", use_real_data=args.real_data))

    if args.mode in ("robustness", "all"):
        print(f"[robustness] running {args.runs} seeds from {args.start_seed}...")
        for i in range(args.runs):
            seed = args.start_seed + i
            print(f"  - seed {seed}")
            robustness_rows.append(run_single(seed=seed, scenario="base", use_real_data=args.real_data))

    if args.mode in ("stress", "all"):
        print("[stress] running stress scenarios...")
        for sc in DEFAULT_STRESS_SCENARIOS:
            print(f"  - scenario {sc} (seed {args.seed})")
            stress_rows.append(run_single(seed=args.seed, scenario=sc, use_real_data=args.real_data))

    if args.mode == "regression":
        robust_for_gates = regression_rows
    elif args.mode == "stress":
        robust_for_gates = []
    else:
        robust_for_gates = robustness_rows

    gates = pass_fail_gates(robust_for_gates, stress_rows, args.mode)

    # Summary
    legacy_cagrs = [r["legacy_cagr"] for r in robust_for_gates if r.get("legacy_cagr") is not None]
    legacy_sharpes = [r["legacy_sharpe"] for r in robust_for_gates if r.get("legacy_sharpe") is not None]
    legacy_dds = [r["legacy_maxdd"] for r in robust_for_gates if r.get("legacy_maxdd") is not None]

    summary = {
        "started_at": started,
        "completed_at": datetime.now().isoformat(),
        "mode": args.mode,
        "config": {
            "runs": args.runs,
            "start_seed": args.start_seed,
            "stress_seed": args.seed,
            "real_data": args.real_data,
        },
        "regression": regression_rows,
        "robustness": robustness_rows,
        "stress": stress_rows,
        "robustness_stats": {
            "legacy_cagr_mean": safe_mean(legacy_cagrs),
            "legacy_cagr_std": safe_std(legacy_cagrs),
            "legacy_cagr_cv_pct": cv_pct(legacy_cagrs),
            "legacy_sharpe_mean": safe_mean(legacy_sharpes),
            "legacy_maxdd_mean": safe_mean(legacy_dds),
        },
        "gates": gates,
    }

    out_file = f"benchmark_suite_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(make_json_safe(summary), f, indent=2)

    print("\n=== BENCHMARK SUITE SUMMARY ===")
    if legacy_cagrs:
        print(f"Legacy CAGR mean: {pct(safe_mean(legacy_cagrs))} | std: {safe_std(legacy_cagrs):.4f} | CV: {cv_pct(legacy_cagrs):.2f}%")
    if legacy_sharpes:
        print(f"Legacy Sharpe mean: {safe_mean(legacy_sharpes):.3f}")
    if legacy_dds:
        print(f"Legacy MaxDD mean: {pct(safe_mean(legacy_dds))}")
    print(f"Gate decision: {'PASS' if gates['all_pass'] else 'FAIL'}")
    for k, v in gates["checks"].items():
        print(f"  - {k}: {'PASS' if v else 'FAIL'}")
    print(f"Summary file: {out_file}")


if __name__ == "__main__":
    main()
