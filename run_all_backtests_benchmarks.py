"""
PROMETHEUS Master Backtest & Benchmark Runner
==============================================
Runs ALL backtests and benchmarks in priority order.
Captures output, timing, and pass/fail for each.
Results saved to MASTER_BENCHMARK_RESULTS_<timestamp>.json
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
TIMEOUT_QUICK = 120       # 2 min
TIMEOUT_MEDIUM = 600      # 10 min
TIMEOUT_LONG = 1800       # 30 min
TIMEOUT_VERY_LONG = 3600  # 60 min

BASE_DIR = Path(__file__).parent

# Scripts in execution order: (name, file, timeout, tier, description)
SCRIPTS = [
    # ── TIER 1: System Validation ──
    ("System Full Test",           "benchmark_full_system_test.py",              TIMEOUT_MEDIUM, "TIER-1", "Validates ALL systems, 6 enhancements, aggressive config"),
    ("AI Capabilities Benchmark",  "comprehensive_ai_capabilities_benchmark.py", TIMEOUT_LONG,   "TIER-1", "Tests all 80+ AI systems with learning feedback"),
    ("Real AI Backtest",           "prometheus_real_ai_backtest.py",             TIMEOUT_LONG,   "TIER-1", "Uses actual AI pipeline on historical market data"),

    # ── TIER 2: Critical Backtests ──
    ("5-Year Learning Backtest",   "backtest_5_year_learning.py",               TIMEOUT_LONG,   "TIER-2", "5-year backtest with learning engine and pattern discovery"),
    ("Real Market Backtest",       "comprehensive_real_market_backtest.py",      TIMEOUT_VERY_LONG, "TIER-2", "Multi-timeframe on 10 symbols with real market data"),
    ("Realistic Backtest",         "prometheus_realistic_backtest.py",           TIMEOUT_MEDIUM, "TIER-2", "3 scenarios: optimistic, realistic, conservative"),

    # ── TIER 3: Competitive Benchmarks ──
    ("Benchmark Comparison",       "benchmark_comparison.py",                   TIMEOUT_MEDIUM, "TIER-3", "PROMETHEUS vs 20 market benchmarks"),
    ("HRM Industry Validator",     "hrm_industry_benchmark_validator.py",       TIMEOUT_MEDIUM, "TIER-3", "HRM vs industry standards validation"),
    ("Competitor Benchmark",       "_competitor_benchmark.py",                  TIMEOUT_MEDIUM, "TIER-3", "Live Alpaca vs Renaissance, Two Sigma, Citadel"),
    ("HRM Performance",            "hrm_performance_benchmark.py",              TIMEOUT_MEDIUM, "TIER-3", "HRM latency, init, model loading benchmarks"),

    # ── TIER 4: Additional Tests ──
    ("1-Year Competition",         "backtest_1_year_competition.py",            TIMEOUT_MEDIUM, "TIER-4", "1-year competitive vs 18+ benchmarks"),
    ("Advanced Learning Backtest", "advanced_learning_backtest.py",             TIMEOUT_LONG,   "TIER-4", "8-perspective multi-timeframe learning"),
    ("Intelligence Benchmark",     "intelligence_benchmark.py",                 TIMEOUT_MEDIUM, "TIER-4", "AI reasoning quality and confidence calibration"),
    ("Full Power Backtest",        "backtest_full_power_optimized.py",          TIMEOUT_MEDIUM, "TIER-4", "Aggressive parameters with all knowledge bases"),
    ("Enhanced Backtest",          "prometheus_enhanced_backtest.py",            TIMEOUT_MEDIUM, "TIER-4", "Enhanced logic on 2022-2024 data"),
    ("Performance Suite",          "performance_benchmarking_suite.py",         TIMEOUT_MEDIUM, "TIER-4", "Revolutionary Session vs S&P 500"),
    ("Industry Leading Benchmark", "industry_leading_benchmark.py",             TIMEOUT_QUICK,  "TIER-4", "Hardcoded comparison vs top funds"),
    ("AI vs OpenAI Benchmark",     "benchmark_ai_vs_openai.py",                TIMEOUT_MEDIUM, "TIER-4", "Prometheus AI vs OpenAI capabilities"),
    ("ThinkMesh Benchmark",        "thinkmesh_enhanced_benchmark.py",           TIMEOUT_MEDIUM, "TIER-4", "ThinkMesh cognitive architecture benchmark"),
    ("Backtest Benchmark Combo",   "comprehensive_backtest_benchmark.py",       TIMEOUT_LONG,   "TIER-4", "Old HRM vs Enhanced/Ultimate comparison"),
]


def run_script(name, filename, timeout, tier, description):
    """Run a single script and capture results."""
    filepath = BASE_DIR / filename
    if not filepath.exists():
        return {
            "name": name,
            "file": filename,
            "tier": tier,
            "status": "SKIPPED",
            "reason": "File not found",
            "duration": 0,
        }

    print(f"\n{'='*70}")
    print(f"  [{tier}] {name}")
    print(f"  File: {filename}")
    print(f"  {description}")
    print(f"  Timeout: {timeout}s")
    print(f"{'='*70}")

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(filepath)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BASE_DIR),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"},
            encoding="utf-8",
            errors="replace",
        )
        duration = round(time.time() - start, 1)
        stdout = result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout
        stderr = result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr

        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"  Status: {status} (exit code {result.returncode}, {duration}s)")

        # Print last 20 lines of output
        lines = stdout.strip().split('\n')
        for line in lines[-20:]:
            print(f"    {line}")

        return {
            "name": name,
            "file": filename,
            "tier": tier,
            "status": status,
            "exit_code": result.returncode,
            "duration": duration,
            "output_tail": stdout[-2000:],
            "stderr_tail": stderr[-500:] if stderr else "",
        }

    except subprocess.TimeoutExpired:
        duration = round(time.time() - start, 1)
        print(f"  Status: TIMEOUT after {duration}s")
        return {
            "name": name,
            "file": filename,
            "tier": tier,
            "status": "TIMEOUT",
            "duration": duration,
            "reason": f"Exceeded {timeout}s timeout",
        }
    except Exception as e:
        duration = round(time.time() - start, 1)
        print(f"  Status: ERROR - {e}")
        return {
            "name": name,
            "file": filename,
            "tier": tier,
            "status": "ERROR",
            "duration": duration,
            "reason": str(e)[:200],
        }


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print("  PROMETHEUS MASTER BACKTEST & BENCHMARK RUNNER")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Scripts to run: {len(SCRIPTS)}")
    print("=" * 70)

    results = []
    total_start = time.time()

    for i, (name, filename, timeout, tier, desc) in enumerate(SCRIPTS, 1):
        print(f"\n>>> Running {i}/{len(SCRIPTS)}: {name} ...")
        result = run_script(name, filename, timeout, tier, desc)
        results.append(result)

        # Running tally
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        skipped = sum(1 for r in results if r["status"] == "SKIPPED")
        timed_out = sum(1 for r in results if r["status"] == "TIMEOUT")
        errors = sum(1 for r in results if r["status"] == "ERROR")
        print(f"\n  Tally: {passed} PASS | {failed} FAIL | {timed_out} TIMEOUT | {skipped} SKIP | {errors} ERROR  ({i}/{len(SCRIPTS)} done)")

    total_duration = round(time.time() - total_start, 1)

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  FINAL RESULTS SUMMARY")
    print("=" * 70)

    for tier_name in ["TIER-1", "TIER-2", "TIER-3", "TIER-4"]:
        tier_results = [r for r in results if r["tier"] == tier_name]
        if not tier_results:
            continue
        print(f"\n  {tier_name}:")
        for r in tier_results:
            icon = {"PASS": "OK", "FAIL": "XX", "TIMEOUT": "TO", "SKIPPED": "--", "ERROR": "!!"}.get(r["status"], "??")
            print(f"    [{icon}] {r['name']:<35} {r['status']:<10} {r['duration']}s")

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)
    print(f"\n  TOTAL: {passed}/{total} PASSED  |  {failed} FAILED  |  {total_duration}s total runtime")
    print(f"  Pass rate: {round(passed/total*100, 1) if total > 0 else 0}%")

    # ── Save results ─────────────────────────────────────────────────────
    output_file = BASE_DIR / f"MASTER_BENCHMARK_RESULTS_{timestamp}.json"
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_scripts": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        "total_runtime_seconds": total_duration,
        "results": results,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n  Results saved to: {output_file.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
