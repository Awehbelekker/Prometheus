#!/usr/bin/env python3
"""
Parameter sweep for execution optimization benchmark.

Runs multiple 50-year benchmark configurations across random seeds and ranks
configs by averaged Hard-Gate improvements (Sharpe/Return/Cost/Drawdown).
"""

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

from benchmark_execution_optimization import ExecutionOptimizationBenchmark


@dataclass
class SweepResult:
    momentum_threshold: float
    size_mean: float
    quality_threshold: float
    seeds: List[int]
    avg_return_improvement_pct: float
    avg_sharpe_improvement: float
    avg_drawdown_improvement_pct: float
    avg_cost_reduction_pct: float
    avg_rejected_trades: float
    avg_hard_return_pct: float
    avg_hard_sharpe: float
    positive_return_ratio: float
    positive_sharpe_ratio: float
    passed_guardrails: bool
    traffic_light: str
    guardrail_failures: List[str]
    score: float


async def run_one(
    years: int,
    initial_capital: float,
    momentum_threshold: float,
    size_mean: float,
    quality_threshold: float,
    seed: int,
) -> Dict:
    bench = ExecutionOptimizationBenchmark(
        years=years,
        initial_capital=initial_capital,
        momentum_threshold=momentum_threshold,
        size_mean=size_mean,
        size_std=0.03,
        size_min=0.02,
        size_max=0.20,
        quality_threshold=quality_threshold,
        seed=seed,
    )
    await bench.run()

    base = bench.baseline_results
    hard = bench.optimized_results

    return {
        "seed": seed,
        "return_improvement_pct": hard["total_return_pct"] - base["total_return_pct"],
        "sharpe_improvement": hard["sharpe_ratio"] - base["sharpe_ratio"],
        "drawdown_improvement_pct": abs(base["max_drawdown_pct"]) - abs(hard["max_drawdown_pct"]),
        "cost_reduction_pct": ((base["total_costs"] - hard["total_costs"]) / max(base["total_costs"], 1.0)) * 100.0,
        "rejected_trades": hard.get("trades_rejected", 0),
        "hard_return_pct": hard["total_return_pct"],
        "hard_sharpe": hard["sharpe_ratio"],
    }


def aggregate(
    momentum_threshold: float,
    size_mean: float,
    quality_threshold: float,
    run_metrics: List[Dict],
    guardrails: Dict[str, float],
) -> SweepResult:
    def avg(key: str) -> float:
        return float(np.mean([m[key] for m in run_metrics]))

    positive_return_ratio = float(np.mean([m["return_improvement_pct"] >= 0 for m in run_metrics]))
    positive_sharpe_ratio = float(np.mean([m["sharpe_improvement"] > 0 for m in run_metrics]))

    guardrail_failures: List[str] = []
    if avg("return_improvement_pct") < guardrails["min_avg_return_improvement_pct"]:
        guardrail_failures.append(
            f"avg_return_improvement_pct<{guardrails['min_avg_return_improvement_pct']:.2f}"
        )
    if avg("sharpe_improvement") < guardrails["min_avg_sharpe_improvement"]:
        guardrail_failures.append(
            f"avg_sharpe_improvement<{guardrails['min_avg_sharpe_improvement']:.3f}"
        )
    if avg("drawdown_improvement_pct") < guardrails["min_avg_drawdown_improvement_pct"]:
        guardrail_failures.append(
            f"avg_drawdown_improvement_pct<{guardrails['min_avg_drawdown_improvement_pct']:.2f}"
        )
    if avg("cost_reduction_pct") < guardrails["min_avg_cost_reduction_pct"]:
        guardrail_failures.append(
            f"avg_cost_reduction_pct<{guardrails['min_avg_cost_reduction_pct']:.2f}"
        )
    if positive_return_ratio < guardrails["min_positive_return_ratio"]:
        guardrail_failures.append(
            f"positive_return_ratio<{guardrails['min_positive_return_ratio']:.2f}"
        )
    if positive_sharpe_ratio < guardrails["min_positive_sharpe_ratio"]:
        guardrail_failures.append(
            f"positive_sharpe_ratio<{guardrails['min_positive_sharpe_ratio']:.2f}"
        )
    passed_guardrails = len(guardrail_failures) == 0

    if not passed_guardrails:
        traffic_light = "RED"
    elif positive_return_ratio >= 0.7 and avg("drawdown_improvement_pct") >= 0:
        traffic_light = "GREEN"
    else:
        traffic_light = "YELLOW"

    # Weighted score favoring robust risk-adjusted returns and lower costs.
    score = (
        avg("avg_sharpe_component")
        if "avg_sharpe_component" in run_metrics[0]
        else (avg("sharpe_improvement") * 120.0
              + avg("return_improvement_pct") * 1.5
              + avg("cost_reduction_pct") * 0.20
              + avg("drawdown_improvement_pct") * 2.0)
    )

    return SweepResult(
        momentum_threshold=momentum_threshold,
        size_mean=size_mean,
        quality_threshold=quality_threshold,
        seeds=[int(m["seed"]) for m in run_metrics],
        avg_return_improvement_pct=avg("return_improvement_pct"),
        avg_sharpe_improvement=avg("sharpe_improvement"),
        avg_drawdown_improvement_pct=avg("drawdown_improvement_pct"),
        avg_cost_reduction_pct=avg("cost_reduction_pct"),
        avg_rejected_trades=avg("rejected_trades"),
        avg_hard_return_pct=avg("hard_return_pct"),
        avg_hard_sharpe=avg("hard_sharpe"),
        positive_return_ratio=positive_return_ratio,
        positive_sharpe_ratio=positive_sharpe_ratio,
        passed_guardrails=passed_guardrails,
        traffic_light=traffic_light,
        guardrail_failures=guardrail_failures,
        score=score,
    )


def parse_float_list(raw: str) -> List[float]:
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def parse_int_list(raw: str) -> List[int]:
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


async def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep execution benchmark parameters")
    parser.add_argument("--years", type=int, default=50)
    parser.add_argument("--capital", type=float, default=10000.0)
    parser.add_argument("--momentum-thresholds", type=str, default="0.008,0.010,0.012")
    parser.add_argument("--size-means", type=str, default="0.06,0.08,0.10")
    parser.add_argument("--quality-thresholds", type=str, default="68,70,72")
    parser.add_argument("--seeds", type=str, default="11,29")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--out", type=str, default="execution_param_sweep_report.json")
    parser.add_argument("--min-avg-return-improvement-pct", type=float, default=0.0)
    parser.add_argument("--min-avg-sharpe-improvement", type=float, default=0.0)
    parser.add_argument("--min-avg-drawdown-improvement-pct", type=float, default=0.0)
    parser.add_argument("--min-avg-cost-reduction-pct", type=float, default=0.0)
    parser.add_argument("--min-positive-return-ratio", type=float, default=0.5)
    parser.add_argument("--min-positive-sharpe-ratio", type=float, default=1.0)
    args = parser.parse_args()

    guardrails = {
        "min_avg_return_improvement_pct": args.min_avg_return_improvement_pct,
        "min_avg_sharpe_improvement": args.min_avg_sharpe_improvement,
        "min_avg_drawdown_improvement_pct": args.min_avg_drawdown_improvement_pct,
        "min_avg_cost_reduction_pct": args.min_avg_cost_reduction_pct,
        "min_positive_return_ratio": args.min_positive_return_ratio,
        "min_positive_sharpe_ratio": args.min_positive_sharpe_ratio,
    }

    momentum_thresholds = parse_float_list(args.momentum_thresholds)
    size_means = parse_float_list(args.size_means)
    quality_thresholds = parse_float_list(args.quality_thresholds)
    seeds = parse_int_list(args.seeds)

    logging.getLogger().setLevel(logging.ERROR)
    noisy_loggers = [
        "benchmark_execution_optimization",
        "launch_ultimate_prometheus_LIVE_TRADING",
        "core",
        "tensorflow",
        "httpx",
        "torch",
    ]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.ERROR)

    all_results: List[SweepResult] = []
    detailed_runs: Dict[str, List[Dict]] = {}

    total_configs = len(momentum_thresholds) * len(size_means) * len(quality_thresholds)
    print(f"Running sweep: {total_configs} configs x {len(seeds)} seeds each")

    config_idx = 0
    for mom in momentum_thresholds:
        for size_mean in size_means:
            for qthr in quality_thresholds:
                config_idx += 1
                key = f"mom={mom:.4f}|size={size_mean:.3f}|q={qthr:.1f}"
                print(f"[{config_idx}/{total_configs}] {key}")

                run_metrics = []
                for seed in seeds:
                    metrics = await run_one(
                        years=args.years,
                        initial_capital=args.capital,
                        momentum_threshold=mom,
                        size_mean=size_mean,
                        quality_threshold=qthr,
                        seed=seed,
                    )
                    run_metrics.append(metrics)

                agg = aggregate(mom, size_mean, qthr, run_metrics, guardrails)
                all_results.append(agg)
                detailed_runs[key] = run_metrics

    ranked_all = sorted(all_results, key=lambda x: x.score, reverse=True)
    ranked_passed = [x for x in ranked_all if x.passed_guardrails]
    top_n = ranked_passed[: max(1, args.top)]

    print("\nTop configs (guardrails passed):")
    print("-" * 110)
    print(
        f"{'Rank':<6}{'Momentum':<12}{'SizeMean':<10}{'QThreshold':<12}"
        f"{'RetImp%':<10}{'SharpeImp':<11}{'DDImp%':<9}{'CostRed%':<10}{'P(Ret+)':<9}{'Status':<8}{'Score':<10}"
    )
    print("-" * 110)

    if top_n:
        for i, row in enumerate(top_n, start=1):
            print(
                f"{i:<6}{row.momentum_threshold:<12.4f}{row.size_mean:<10.3f}{row.quality_threshold:<12.1f}"
                f"{row.avg_return_improvement_pct:<10.2f}{row.avg_sharpe_improvement:<11.3f}"
                f"{row.avg_drawdown_improvement_pct:<9.2f}{row.avg_cost_reduction_pct:<10.2f}"
                f"{row.positive_return_ratio:<9.2f}{row.traffic_light:<8}{row.score:<10.2f}"
            )
    else:
        print("No configs passed guardrails. Consider relaxing thresholds.")

    print("\nGuardrails:")
    print(json.dumps(guardrails, indent=2))

    report = {
        "generated_at": datetime.now().isoformat(),
        "config": {
            "years": args.years,
            "capital": args.capital,
            "momentum_thresholds": momentum_thresholds,
            "size_means": size_means,
            "quality_thresholds": quality_thresholds,
            "seeds": seeds,
            "top": args.top,
        },
        "guardrails": guardrails,
        "summary": {
            "green_count": sum(1 for x in ranked_all if x.traffic_light == "GREEN"),
            "yellow_count": sum(1 for x in ranked_all if x.traffic_light == "YELLOW"),
            "red_count": sum(1 for x in ranked_all if x.traffic_light == "RED"),
        },
        "best": asdict(ranked_passed[0]) if ranked_passed else None,
        "top": [asdict(x) for x in top_n],
        "all": [asdict(x) for x in ranked_all],
        "passed_count": len(ranked_passed),
        "failed_count": len(ranked_all) - len(ranked_passed),
        "detailed_runs": detailed_runs,
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved sweep report: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
