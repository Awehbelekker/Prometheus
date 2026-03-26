"""
Aggregate statistics from the 50-repeat benchmark run.
Run this once all 50 iterations of benchmark_repeat50_FIXED_20260326_222921.log complete.

Usage:
    python _aggregate_50_runs.py

Filters JSON files created on/after the loop start: 20260326_222921
Prints mean, std, min, max, median, and 95% CI for all key metrics.
"""

import json
import os
import glob
import statistics
import math
import argparse
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
LOOP_START_STAMP = "20260326_222921"   # only count JSONs from this run onwards
BASELINE_FILE = "benchmark_50_year_20260309_225939.json"
LOG_FILE = "benchmark_repeat50_FIXED_20260326_222921.log"
# ──────────────────────────────────────────────────────────────────────────────


def ci95(data):
    """Return (mean, half-width) of 95% CI assuming t-distribution."""
    n = len(data)
    if n < 2:
        return statistics.mean(data), float("nan")
    m = statistics.mean(data)
    s = statistics.stdev(data)
    # Use 1.96 for n>=30, else a rough t-table approximation
    t = 1.96 if n >= 30 else {1: 12.7, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57,
                               6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23,
                               15: 2.13, 20: 2.09, 25: 2.06}.get(n - 1, 2.00)
    return m, t * s / math.sqrt(n)


def pct(v):
    return f"{v * 100:+.2f}%"


def fmt(v, decimals=3):
    return f"{v:.{decimals}f}"


def load_runs(min_stamp: str, scenario_filter: str = "any", require_seed: bool = False):
    pattern = "benchmark_50_year_*.json"
    files = sorted(glob.glob(pattern))

    # Filter: only files with stamp >= LOOP_START_STAMP (exclude pre-loop JSONs)
    run_files = []
    for f in files:
        # filename: benchmark_50_year_YYYYMMDD_HHMMSS.json
        basename = os.path.basename(f)
        try:
            stamp = basename.replace("benchmark_50_year_", "").replace(".json", "")
            if stamp >= min_stamp and basename != os.path.basename(BASELINE_FILE):
                run_files.append(f)
        except Exception:
            pass

    filtered = []
    for f in run_files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            sc = (d.get("scenario") or "base").lower()
            has_seed = "seed" in d
            if scenario_filter != "any" and sc != scenario_filter:
                continue
            if require_seed and not has_seed:
                continue
            filtered.append(f)
        except Exception:
            continue
    return filtered


def extract_metrics(path):
    with open(path, "r", encoding="utf-8") as fh:
        d = json.load(fh)

    pr = d.get("prometheus_results", {})
    kr = d.get("kelly_results", {})
    br = d.get("blend_results", {})

    return {
        "file": os.path.basename(path),
        "date": d.get("benchmark_date", "?"),
        "seed": d.get("seed"),
        "scenario": d.get("scenario", "base"),
        "rank": d.get("prometheus_rank", 99),
        "total_competitors": d.get("total_competitors", 15),
        # Legacy (prometheus_results)
        "leg_cagr":    pr.get("cagr", float("nan")),
        "leg_sharpe":  pr.get("sharpe_ratio", float("nan")),
        "leg_maxdd":   pr.get("max_drawdown", float("nan")),
        "leg_winrate": pr.get("win_rate", float("nan")),
        "leg_return":  pr.get("total_return", float("nan")),
        "leg_capital": pr.get("final_capital", float("nan")),
        # Kelly
        "kel_cagr":    kr.get("cagr", float("nan")),
        "kel_sharpe":  kr.get("sharpe_ratio", float("nan")),
        "kel_maxdd":   kr.get("max_drawdown", float("nan")),
        "kel_winrate": kr.get("win_rate", float("nan")),
        "kel_sortino": kr.get("sortino_ratio", float("nan")),
        "kel_calmar":  kr.get("calmar_ratio", float("nan")),
        # Blend
        "bld_cagr":    br.get("cagr", float("nan")),
        "bld_sharpe":  br.get("sharpe_ratio", float("nan")),
        "bld_maxdd":   br.get("max_drawdown", float("nan")),
        "bld_winrate": br.get("win_rate", float("nan")),
    }


def stats_block(label, values):
    clean = [v for v in values if not math.isnan(v)]
    if not clean:
        return f"  {label}: NO DATA"
    n = len(clean)
    mean, hw = ci95(clean)
    med = statistics.median(clean)
    lo, hi = min(clean), max(clean)
    std = statistics.stdev(clean) if n > 1 else 0.0
    cv = abs(std / mean * 100) if mean != 0 else float("nan")
    return (
        f"  {label:<28} mean={fmt(mean)}  ±{fmt(hw)} (95%CI)  "
        f"std={fmt(std)}  CV={cv:.1f}%  "
        f"median={fmt(med)}  min={fmt(lo)}  max={fmt(hi)}  n={n}"
    )


def main():
    parser = argparse.ArgumentParser(description="Aggregate benchmark runs with optional filters")
    parser.add_argument("--min-stamp", default=LOOP_START_STAMP, help="Include files >= this YYYYMMDD_HHMMSS stamp")
    parser.add_argument("--scenario", default="any", help="Scenario filter: any/base/flash_crash/prolonged_bear/vol_spike/sideways_chop/regime_whipsaw")
    parser.add_argument("--require-seed", action="store_true", help="Only include reports that contain seed metadata")
    args = parser.parse_args()

    run_files = load_runs(args.min_stamp, args.scenario.lower(), args.require_seed)
    n_found = len(run_files)

    print("=" * 80)
    print("  PROMETHEUS 50-REPEAT BENCHMARK AGGREGATION")
    print(f"  Min stamp        : {args.min_stamp}")
    print(f"  Scenario filter  : {args.scenario.lower()}")
    print(f"  Require seed     : {args.require_seed}")
    print(f"  JSON files found : {n_found}")
    print(f"  Generated        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if n_found == 0:
        print("\n  NO benchmark JSON files found for this loop yet. Try again after runs complete.")
        return

    # --- Check log progress ---
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        runs_done = content.count(" END ")
        reports_saved = content.count("Full report saved: benchmark_50_year_")
        completed = "Completed FIXED 50" in content
        print(f"\n  Log status  : {runs_done}/50 runs ended, {reports_saved} reports saved, loop_complete={completed}")
    else:
        print(f"\n  Log file not found: {LOG_FILE}")

    # --- Load all metrics ---
    runs = []
    errors = []
    for f in run_files:
        try:
            runs.append(extract_metrics(f))
        except Exception as e:
            errors.append(f"{f}: {e}")

    if errors:
        print(f"\n  LOAD ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    {e}")

    n = len(runs)
    if n == 0:
        print("\n  No valid runs loaded.")
        return

    # --- Helper: extract list ---
    def col(key):
        return [r[key] for r in runs]

    # ── RANK DISTRIBUTION ─────────────────────────────────────────────────────
    ranks = col("rank")
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    print(f"\n{'─'*80}")
    print("  RANK DISTRIBUTION (across all runs)")
    print(f"{'─'*80}")
    for rank in sorted(rank_counts):
        bar = "█" * rank_counts[rank]
        pct_r = rank_counts[rank] / n * 100
        label = f"  Rank #{rank:<3}"
        print(f"  {label}  {bar:<52}  {rank_counts[rank]:>3} runs ({pct_r:.1f}%)")
    mean_rank, hw_rank = ci95(ranks)
    print(f"\n  Mean rank: {mean_rank:.2f} ± {hw_rank:.2f} (95%CI)   "
          f"best={min(ranks)}  worst={max(ranks)}  rank_#1_rate={rank_counts.get(1,0)/n*100:.1f}%")

    # ── LEGACY METRICS ────────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  LEGACY (PROMETHEUS) METRICS")
    print(f"{'─'*80}")
    print(stats_block("CAGR",        col("leg_cagr")))
    print(stats_block("Sharpe",      col("leg_sharpe")))
    print(stats_block("Max Drawdown",col("leg_maxdd")))
    print(stats_block("Win Rate",    col("leg_winrate")))
    print(stats_block("Total Return",col("leg_return")))

    # ── KELLY METRICS ─────────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  KELLY METRICS")
    print(f"{'─'*80}")
    print(stats_block("CAGR",        col("kel_cagr")))
    print(stats_block("Sharpe",      col("kel_sharpe")))
    print(stats_block("Max Drawdown",col("kel_maxdd")))
    print(stats_block("Win Rate",    col("kel_winrate")))
    print(stats_block("Sortino",     col("kel_sortino")))
    print(stats_block("Calmar",      col("kel_calmar")))

    # ── BLEND METRICS ─────────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  BLEND (60/40) METRICS")
    print(f"{'─'*80}")
    print(stats_block("CAGR",        col("bld_cagr")))
    print(stats_block("Sharpe",      col("bld_sharpe")))
    print(stats_block("Max Drawdown",col("bld_maxdd")))
    print(stats_block("Win Rate",    col("bld_winrate")))

    # ── STABILITY VERDICT ─────────────────────────────────────────────────────
    leg_cagrs = [v for v in col("leg_cagr") if not math.isnan(v)]
    kel_cagrs = [v for v in col("kel_cagr") if not math.isnan(v)]
    leg_cv = abs(statistics.stdev(leg_cagrs) / statistics.mean(leg_cagrs) * 100) if len(leg_cagrs) > 1 else float("nan")
    kel_cv = abs(statistics.stdev(kel_cagrs) / statistics.mean(kel_cagrs) * 100) if len(kel_cagrs) > 1 else float("nan")

    print(f"\n{'─'*80}")
    print("  STABILITY VERDICT")
    print(f"{'─'*80}")
    print(f"  Coefficient of Variation (CV) — lower = more stable")
    print(f"  Legacy CAGR CV : {leg_cv:.2f}%   {'✓ STABLE' if leg_cv < 10 else '⚠ VARIABLE' if leg_cv < 25 else '✗ HIGH VARIANCE'}")
    print(f"  Kelly  CAGR CV : {kel_cv:.2f}%   {'✓ STABLE' if kel_cv < 10 else '⚠ VARIABLE' if kel_cv < 25 else '✗ HIGH VARIANCE'}")

    rank_1_rate = rank_counts.get(1, 0) / n * 100
    top3_rate = sum(rank_counts.get(r, 0) for r in [1, 2, 3]) / n * 100
    print(f"  Rank #1 rate   : {rank_1_rate:.1f}%   {'✓ DOMINANT' if rank_1_rate >= 70 else '⚠ INCONSISTENT' if rank_1_rate >= 40 else '✗ WEAK'}")
    print(f"  Top-3 rate     : {top3_rate:.1f}%")

    unique_seed_count = len({r['seed'] for r in runs if r.get('seed') is not None})
    unique_scenarios = sorted({str(r.get('scenario', 'base')) for r in runs})
    print(f"  Unique seeds    : {unique_seed_count}")
    print(f"  Scenarios       : {', '.join(unique_scenarios)}")
    if unique_seed_count <= 1 and n > 1:
        print("  WARNING         : Deterministic sample detected (<=1 unique seed).")

    # ── BEST / WORST RUNS ─────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  BEST / WORST RUNS (by Legacy CAGR)")
    print(f"{'─'*80}")
    valid_runs = [r for r in runs if not math.isnan(r["leg_cagr"])]
    if valid_runs:
        best = max(valid_runs, key=lambda r: r["leg_cagr"])
        worst = min(valid_runs, key=lambda r: r["leg_cagr"])
        print(f"  BEST  [{best['file']}]")
        print(f"    Rank #{best['rank']}  Legacy CAGR={pct(best['leg_cagr'])}  Sharpe={fmt(best['leg_sharpe'])}  "
              f"MaxDD={pct(best['leg_maxdd'])}  WinRate={pct(best['leg_winrate'])}")
        print(f"    Kelly  CAGR={pct(best['kel_cagr'])}  Sharpe={fmt(best['kel_sharpe'])}")
        print(f"\n  WORST [{worst['file']}]")
        print(f"    Rank #{worst['rank']}  Legacy CAGR={pct(worst['leg_cagr'])}  Sharpe={fmt(worst['leg_sharpe'])}  "
              f"MaxDD={pct(worst['leg_maxdd'])}  WinRate={pct(worst['leg_winrate'])}")
        print(f"    Kelly  CAGR={pct(worst['kel_cagr'])}  Sharpe={fmt(worst['kel_sharpe'])}")

    # ── COMPARE TO BASELINE ───────────────────────────────────────────────────
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE, "r", encoding="utf-8") as fh:
            base = json.load(fh)
        bpr = base.get("prometheus_results", {})
        bkr = base.get("kelly_results", {})

        print(f"\n{'─'*80}")
        print(f"  COMPARISON vs BASELINE ({os.path.basename(BASELINE_FILE)})")
        print(f"{'─'*80}")
        mean_leg_cagr, _ = ci95(leg_cagrs)
        mean_kel_cagr, _ = ci95(kel_cagrs)
        base_leg_cagr = bpr.get("cagr", 0)
        base_kel_cagr = bkr.get("cagr", 0)
        print(f"  Legacy CAGR   baseline={pct(base_leg_cagr)}  mean_50runs={pct(mean_leg_cagr)}  "
              f"delta={pct(mean_leg_cagr - base_leg_cagr)}")
        print(f"  Kelly  CAGR   baseline={pct(base_kel_cagr)}  mean_50runs={pct(mean_kel_cagr)}  "
              f"delta={pct(mean_kel_cagr - base_kel_cagr)}")
        base_rank = base.get("prometheus_rank", "?")
        print(f"  Rank          baseline=#{base_rank}  mean_50runs=#{mean_rank:.1f}  rank_#1_rate={rank_1_rate:.1f}%")

    # ── RISK-FIRST GATES ──────────────────────────────────────────────────────
    legacy_cagrs_sorted = sorted(leg_cagrs)
    p10_idx = int(max(0, math.floor(0.10 * (len(legacy_cagrs_sorted) - 1)))) if legacy_cagrs_sorted else 0
    cagr_p10 = legacy_cagrs_sorted[p10_idx] if legacy_cagrs_sorted else float("nan")
    mean_leg_sharpe = statistics.mean([v for v in col("leg_sharpe") if not math.isnan(v)])
    mean_leg_maxdd = statistics.mean([v for v in col("leg_maxdd") if not math.isnan(v)])

    checks = {
        "legacy_maxdd_mean_ge_-20pct": mean_leg_maxdd >= -0.20,
        "legacy_sharpe_mean_ge_1.5": mean_leg_sharpe >= 1.5,
        "legacy_cagr_p10_ge_0pct": cagr_p10 >= 0.0,
        "rank1_rate_ge_50pct": rank_1_rate >= 50.0,
        "multi_seed_required": unique_seed_count >= 10,
    }

    print(f"\n{'─'*80}")
    print("  RISK-FIRST GATES")
    print(f"{'─'*80}")
    print(f"  Legacy MaxDD mean : {pct(mean_leg_maxdd)}")
    print(f"  Legacy Sharpe mean: {mean_leg_sharpe:.3f}")
    print(f"  Legacy CAGR p10   : {pct(cagr_p10)}")
    print(f"  Rank #1 rate      : {rank_1_rate:.1f}%")
    print(f"  Unique seeds      : {unique_seed_count}")
    for name, ok in checks.items():
        print(f"  - {name:<32} {'PASS' if ok else 'FAIL'}")
    print(f"  OVERALL DECISION  : {'PASS' if all(checks.values()) else 'FAIL'}")

    # ── PER-RUN TABLE ─────────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  PER-RUN TABLE")
    print(f"{'─'*80}")
    hdr = f"  {'#':<4} {'File':<38} {'Rank':<6} {'LegCAGR':>9} {'LegSharpe':>10} {'LegDD':>8} {'KelCAGR':>9} {'KelSharpe':>10}"
    print(hdr)
    print(f"  {'─'*4} {'─'*38} {'─'*6} {'─'*9} {'─'*10} {'─'*8} {'─'*9} {'─'*10}")
    for i, r in enumerate(runs, 1):
        print(f"  {i:<4} {r['file']:<38} {r['rank']:<6} "
              f"{r['leg_cagr']*100:>8.2f}% {r['leg_sharpe']:>10.3f} "
              f"{r['leg_maxdd']*100:>7.2f}% {r['kel_cagr']*100:>8.2f}% {r['kel_sharpe']:>10.3f}")

    # ── SAVE JSON SUMMARY ─────────────────────────────────────────────────────
    summary = {
        "generated_at": datetime.now().isoformat(),
        "n_runs": n,
        "loop_start_stamp": LOOP_START_STAMP,
        "min_stamp_used": args.min_stamp,
        "scenario_filter": args.scenario.lower(),
        "unique_seed_count": unique_seed_count,
        "rank_distribution": rank_counts,
        "rank_1_rate_pct": rank_1_rate,
        "top3_rate_pct": top3_rate,
        "risk_gates": checks,
        "risk_gates_all_pass": all(checks.values()),
        "legacy": {
            "cagr_mean":    statistics.mean(leg_cagrs),
            "cagr_std":     statistics.stdev(leg_cagrs) if len(leg_cagrs) > 1 else 0,
            "cagr_min":     min(leg_cagrs),
            "cagr_max":     max(leg_cagrs),
            "cagr_cv_pct":  leg_cv,
            "sharpe_mean":  statistics.mean([v for v in col("leg_sharpe") if not math.isnan(v)]),
            "maxdd_mean":   statistics.mean([v for v in col("leg_maxdd") if not math.isnan(v)]),
            "winrate_mean": statistics.mean([v for v in col("leg_winrate") if not math.isnan(v)]),
        },
        "kelly": {
            "cagr_mean":    statistics.mean(kel_cagrs),
            "cagr_std":     statistics.stdev(kel_cagrs) if len(kel_cagrs) > 1 else 0,
            "cagr_min":     min(kel_cagrs),
            "cagr_max":     max(kel_cagrs),
            "cagr_cv_pct":  kel_cv,
        },
        "per_run": runs,
    }
    out_file = f"benchmark_50_repeat_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)
    print(f"\n  Summary JSON saved → {out_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
