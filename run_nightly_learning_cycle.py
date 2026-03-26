#!/usr/bin/env python3
"""Nightly learning cycle for PROMETHEUS with promotion gating and failure memory."""

import argparse
import glob
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from prometheus_continuous_improvement import PerformanceBenchmarks


def run_command(cmd):
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def newest_matching_file(pattern):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None


def load_json_file(path):
    if not path or not Path(path).exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_learning_tables(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS learning_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            symbol TEXT,
            description TEXT NOT NULL,
            confidence_impact REAL DEFAULT 0,
            applied BOOLEAN DEFAULT 0
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS dead_end_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            symbol TEXT,
            failure_signature TEXT NOT NULL,
            details TEXT,
            severity REAL DEFAULT 0
        )
        """
    )


def build_promotion_decision(backtest_results, optimization_results):
    benchmarks = PerformanceBenchmarks()
    metrics = backtest_results or {}
    reasons = []

    if not optimization_results:
        reasons.append("missing_optimization_results")
    elif not optimization_results.get("deployment_ready", False):
        reasons.append("optimization_not_deployment_ready")

    win_rate = float(metrics.get("win_rate", 0.0) or 0.0)
    sharpe_ratio = float(metrics.get("sharpe_ratio", 0.0) or 0.0)
    max_drawdown = float(metrics.get("max_drawdown", 1.0) or 1.0)
    profit_factor = float(metrics.get("profit_factor", 0.0) or 0.0)
    total_return = float(metrics.get("total_return", 0.0) or 0.0)

    if win_rate < benchmarks.target_win_rate:
        reasons.append(f"win_rate<{benchmarks.target_win_rate:.2f}")
    if sharpe_ratio < benchmarks.target_sharpe_ratio:
        reasons.append(f"sharpe<{benchmarks.target_sharpe_ratio:.2f}")
    if max_drawdown > benchmarks.target_max_drawdown:
        reasons.append(f"max_drawdown>{benchmarks.target_max_drawdown:.2f}")
    if profit_factor < benchmarks.target_profit_factor:
        reasons.append(f"profit_factor<{benchmarks.target_profit_factor:.2f}")
    if total_return <= 0:
        reasons.append("non_positive_total_return")

    approved = len(reasons) == 0
    confidence_impact = round(max(min(win_rate, 1.0), 0.0), 4)

    return {
        "approved": approved,
        "reasons": reasons,
        "confidence_impact": confidence_impact,
        "benchmarks": {
            "win_rate": benchmarks.target_win_rate,
            "sharpe_ratio": benchmarks.target_sharpe_ratio,
            "max_drawdown": benchmarks.target_max_drawdown,
            "profit_factor": benchmarks.target_profit_factor,
        },
    }


def write_promoted_candidate(parameters, decision, results_file, optimization_file):
    candidate_path = Path("optimization_results") / "nightly_promoted_live_candidate.json"
    candidate_payload = {
        "timestamp": datetime.now().isoformat(),
        "parameters": parameters,
        "promotion_decision": decision,
        "backtest_results_file": results_file,
        "optimization_results_file": optimization_file,
    }
    candidate_path.parent.mkdir(exist_ok=True)
    with open(candidate_path, "w", encoding="utf-8") as handle:
        json.dump(candidate_payload, handle, indent=2)
    return str(candidate_path)


def persist_cycle_records(period_days, symbols, iterations, results_file, optimization_file,
                          decision, backtest_results, optimization_results, candidate_file=None):
    timestamp = datetime.now().isoformat()
    con = sqlite3.connect("prometheus_learning.db")
    cur = con.cursor()
    ensure_learning_tables(cur)

    summary = {
        "cycle": "nightly_learning",
        "iterations": iterations,
        "period_days": period_days,
        "symbols": symbols,
        "results_file": results_file,
        "optimization_file": optimization_file,
        "candidate_file": candidate_file,
        "promotion_approved": decision["approved"],
        "reasons": decision["reasons"],
        "backtest_summary": {
            "total_return": (backtest_results or {}).get("total_return"),
            "win_rate": (backtest_results or {}).get("win_rate"),
            "sharpe_ratio": (backtest_results or {}).get("sharpe_ratio"),
            "max_drawdown": (backtest_results or {}).get("max_drawdown"),
            "profit_factor": (backtest_results or {}).get("profit_factor"),
        },
        "optimization_summary": {
            "deployment_ready": (optimization_results or {}).get("deployment_ready"),
            "iterations_completed": (optimization_results or {}).get("iterations_completed"),
            "best_metrics": (optimization_results or {}).get("best_metrics"),
        },
    }

    cur.execute(
        """
        INSERT INTO learning_insights
        (timestamp, insight_type, symbol, description, confidence_impact, applied)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, "nightly_cycle", None, json.dumps(summary), decision["confidence_impact"], int(decision["approved"])),
    )

    promotion_description = json.dumps({
        "approved": decision["approved"],
        "reasons": decision["reasons"],
        "candidate_file": candidate_file,
    })
    cur.execute(
        """
        INSERT INTO learning_insights
        (timestamp, insight_type, symbol, description, confidence_impact, applied)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, "promotion_decision", None, promotion_description, decision["confidence_impact"], int(decision["approved"])),
    )

    if not decision["approved"]:
        cur.execute(
            """
            INSERT INTO dead_end_memory
            (timestamp, memory_type, symbol, failure_signature, details, severity)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                "nightly_cycle_rejection",
                None,
                "|".join(decision["reasons"]) or "rejected_without_reason",
                json.dumps(summary),
                round(min(1.0, 0.25 * max(len(decision["reasons"]), 1)), 4),
            ),
        )

    con.commit()
    con.close()


def persist_failed_cycle(period_days, symbols, iterations, error_message):
    timestamp = datetime.now().isoformat()
    con = sqlite3.connect("prometheus_learning.db")
    cur = con.cursor()
    ensure_learning_tables(cur)

    details = json.dumps({
        "cycle": "nightly_learning",
        "iterations": iterations,
        "period_days": period_days,
        "symbols": symbols,
        "error": error_message,
    })

    cur.execute(
        """
        INSERT INTO dead_end_memory
        (timestamp, memory_type, symbol, failure_signature, details, severity)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, "nightly_cycle_failure", None, error_message[:250], details, 1.0),
    )
    con.commit()
    con.close()


def main():
    parser = argparse.ArgumentParser(description="Run PROMETHEUS nightly learning cycle")
    parser.add_argument("--iterations", type=int, default=2, help="Improvement iterations")
    parser.add_argument("--days", type=int, default=60, help="Backtest period days")
    parser.add_argument("--symbols", type=str, default="SPY,QQQ,AAPL,MSFT,NVDA,BTCUSD,ETHUSD")
    parser.add_argument("--min-trades", type=int, default=10, help="Minimum trades required for training")
    parser.add_argument("--promote-if-ready", action="store_true", help="Write a live candidate config when all gates pass")
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    py = sys.executable

    try:
        run_command([
            py,
            "prometheus_continuous_improvement.py",
            "--iterations",
            str(args.iterations),
            "--min-trades",
            str(args.min_trades),
            "--days",
            str(args.days),
        ])

        run_command([
            py,
            "prometheus_real_ai_backtest.py",
            "--period",
            str(args.days),
            "--symbols",
            ",".join(symbols),
        ])

        latest_backtest = newest_matching_file("backtest_results_daily_*.json")
        latest_optimization = newest_matching_file("optimization_results/optimization_results_*.json")
        optimization_state = load_json_file("optimization_results/optimization_state.json") or {}
        backtest_results = load_json_file(latest_backtest) or {}
        optimization_results = load_json_file(latest_optimization) or {}

        decision = build_promotion_decision(backtest_results, optimization_results)
        candidate_file = None
        parameters = optimization_state.get("current_parameters") or {}
        if args.promote_if_ready and decision["approved"] and parameters:
            candidate_file = write_promoted_candidate(parameters, decision, latest_backtest, latest_optimization)

        persist_cycle_records(
            args.days,
            symbols,
            args.iterations,
            latest_backtest,
            latest_optimization,
            decision,
            backtest_results,
            optimization_results,
            candidate_file=candidate_file,
        )

        print("[OK] Nightly learning cycle complete")
        print("[INFO] Latest backtest:", latest_backtest)
        print("[INFO] Latest optimization:", latest_optimization)
        print("[INFO] Promotion approved:", decision["approved"])
        if decision["reasons"]:
            print("[INFO] Promotion gates blocked by:", ", ".join(decision["reasons"]))
        if candidate_file:
            print("[INFO] Live candidate written to:", candidate_file)
    except Exception as exc:
        persist_failed_cycle(args.days, symbols, args.iterations, str(exc))
        raise


if __name__ == "__main__":
    main()
