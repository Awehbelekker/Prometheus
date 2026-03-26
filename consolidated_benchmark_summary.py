#!/usr/bin/env python3
"""
Consolidated benchmark summary for PROMETHEUS.

Combines:
- benchmark_execution_optimization_report.json
- latest competitor_benchmark_*.json

Outputs:
- Human-readable terminal dashboard
- Optional JSON summary via --out
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _latest_competitor_report(root: Path) -> Optional[Path]:
    files = sorted(root.glob("competitor_benchmark_*.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _format_num(v: Any, digits: int = 2) -> str:
    try:
        return f"{float(v):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def _print_section(title: str) -> None:
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def _safe_best_backtest(backtests: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not backtests:
        return {}
    return max(backtests, key=lambda x: _to_float(x.get("ann_return"), -1e9))


def build_summary(execution_report: Dict[str, Any], competitor_report: Dict[str, Any]) -> Dict[str, Any]:
    baseline = execution_report.get("baseline", {})
    opt_log = execution_report.get("optimized_log_only", {})
    opt_hard = execution_report.get("optimized", {})

    live = competitor_report.get("prometheus_live", {})
    backtests = competitor_report.get("prometheus_backtests", [])
    competitor_summary = competitor_report.get("summary", {})

    ann_returns = [_to_float(b.get("ann_return")) for b in backtests if b.get("ann_return") is not None]
    sharpes = [_to_float(b.get("sharpe")) for b in backtests if b.get("sharpe") is not None]
    best_bt = _safe_best_backtest(backtests)

    consolidated = {
        "generated_at": datetime.now().isoformat(),
        "inputs": {
            "execution_report_timestamp": execution_report.get("timestamp"),
            "competitor_report_generated": competitor_report.get("generated"),
            "years": execution_report.get("benchmark_config", {}).get("years"),
        },
        "execution_ab": {
            "baseline": {
                "return_pct": _to_float(baseline.get("total_return_pct")),
                "sharpe": _to_float(baseline.get("sharpe_ratio")),
                "max_drawdown_pct": _to_float(baseline.get("max_drawdown_pct")),
                "win_rate_pct": _to_float(baseline.get("win_rate")),
                "trades": int(_to_float(baseline.get("trades_executed"), 0)),
                "total_costs": _to_float(baseline.get("total_costs")),
            },
            "optimized_log_only": {
                "return_pct": _to_float(opt_log.get("total_return_pct")),
                "sharpe": _to_float(opt_log.get("sharpe_ratio")),
                "max_drawdown_pct": _to_float(opt_log.get("max_drawdown_pct")),
                "win_rate_pct": _to_float(opt_log.get("win_rate")),
                "trades": int(_to_float(opt_log.get("trades_executed"), 0)),
                "total_costs": _to_float(opt_log.get("total_costs")),
            },
            "optimized_hard_gate": {
                "return_pct": _to_float(opt_hard.get("total_return_pct")),
                "sharpe": _to_float(opt_hard.get("sharpe_ratio")),
                "max_drawdown_pct": _to_float(opt_hard.get("max_drawdown_pct")),
                "win_rate_pct": _to_float(opt_hard.get("win_rate")),
                "trades": int(_to_float(opt_hard.get("trades_executed"), 0)),
                "rejected_trades": int(_to_float(opt_hard.get("trades_rejected"), 0)),
                "avg_quality_score": _to_float(opt_hard.get("avg_trade_quality")),
                "total_costs": _to_float(opt_hard.get("total_costs")),
            },
            "deltas_vs_baseline": {
                "hard_return_delta_pct": _to_float(opt_hard.get("total_return_pct")) - _to_float(baseline.get("total_return_pct")),
                "hard_sharpe_delta": _to_float(opt_hard.get("sharpe_ratio")) - _to_float(baseline.get("sharpe_ratio")),
                "hard_drawdown_delta_pct": abs(_to_float(baseline.get("max_drawdown_pct"))) - abs(_to_float(opt_hard.get("max_drawdown_pct"))),
                "hard_cost_delta": _to_float(baseline.get("total_costs")) - _to_float(opt_hard.get("total_costs")),
            },
        },
        "competitor_context": {
            "live": {
                "equity": _to_float(live.get("equity")),
                "total_return_pct": _to_float(live.get("total_return_pct")),
                "annualized_pct": _to_float(live.get("annualized_pct")),
                "days_live": int(_to_float(live.get("days_live"), 0)),
                "trades": int(_to_float(live.get("trades"), 0)),
            },
            "backtests": {
                "symbols": len(backtests),
                "avg_annual_return_pct": mean(ann_returns) if ann_returns else 0.0,
                "avg_sharpe": mean(sharpes) if sharpes else 0.0,
                "best_symbol": best_bt.get("symbol"),
                "best_annual_return_pct": _to_float(best_bt.get("ann_return")),
                "best_sharpe": _to_float(best_bt.get("sharpe")),
            },
            "industry": {
                "competitors_beaten_on_sharpe": int(_to_float(competitor_summary.get("competitors_beaten_on_sharpe"), 0)),
                "total_competitors": int(_to_float(competitor_summary.get("total_competitors"), 0)),
            },
        },
        "status": {
            "execution_change_positive": (
                (_to_float(opt_hard.get("total_return_pct")) > _to_float(baseline.get("total_return_pct")))
                and (_to_float(opt_hard.get("sharpe_ratio")) > _to_float(baseline.get("sharpe_ratio")))
            ),
            "risk_tradeoff_present": _to_float(opt_hard.get("max_drawdown_pct")) < _to_float(baseline.get("max_drawdown_pct")),
        },
    }

    return consolidated


def print_dashboard(summary: Dict[str, Any], execution_path: Path, competitor_path: Path) -> None:
    ex = summary["execution_ab"]
    cc = summary["competitor_context"]

    _print_section("PROMETHEUS CONSOLIDATED BENCHMARK DASHBOARD")
    print(f"Execution report : {execution_path.name}")
    print(f"Competitor report: {competitor_path.name}")
    print(f"Generated        : {summary.get('generated_at')}")

    _print_section("Execution A/B (50-Year Synthetic)")
    print(f"{'Metric':<24} {'Baseline':>12} {'Opt(Log)':>12} {'Opt(Hard)':>12}")
    print("-" * 64)
    print(f"{'Return %':<24} {_format_num(ex['baseline']['return_pct']):>12} {_format_num(ex['optimized_log_only']['return_pct']):>12} {_format_num(ex['optimized_hard_gate']['return_pct']):>12}")
    print(f"{'Sharpe':<24} {_format_num(ex['baseline']['sharpe']):>12} {_format_num(ex['optimized_log_only']['sharpe']):>12} {_format_num(ex['optimized_hard_gate']['sharpe']):>12}")
    print(f"{'Max Drawdown %':<24} {_format_num(ex['baseline']['max_drawdown_pct']):>12} {_format_num(ex['optimized_log_only']['max_drawdown_pct']):>12} {_format_num(ex['optimized_hard_gate']['max_drawdown_pct']):>12}")
    print(f"{'Win Rate %':<24} {_format_num(ex['baseline']['win_rate_pct']):>12} {_format_num(ex['optimized_log_only']['win_rate_pct']):>12} {_format_num(ex['optimized_hard_gate']['win_rate_pct']):>12}")
    print(f"{'Trades':<24} {_format_num(ex['baseline']['trades'], 0):>12} {_format_num(ex['optimized_log_only']['trades'], 0):>12} {_format_num(ex['optimized_hard_gate']['trades'], 0):>12}")
    print(f"{'Total Costs':<24} {_format_num(ex['baseline']['total_costs']):>12} {_format_num(ex['optimized_log_only']['total_costs']):>12} {_format_num(ex['optimized_hard_gate']['total_costs']):>12}")

    _print_section("Deltas vs Baseline (Hard Gate)")
    print(f"Return delta %   : {_format_num(ex['deltas_vs_baseline']['hard_return_delta_pct'])}")
    print(f"Sharpe delta     : {_format_num(ex['deltas_vs_baseline']['hard_sharpe_delta'])}")
    print(f"Drawdown delta % (positive=better): {_format_num(ex['deltas_vs_baseline']['hard_drawdown_delta_pct'])}")
    print(f"Cost delta       : {_format_num(ex['deltas_vs_baseline']['hard_cost_delta'])}")
    print(f"Rejected trades  : {_format_num(ex['optimized_hard_gate']['rejected_trades'], 0)}")

    _print_section("Competitor Context")
    print(f"Live annualized %              : {_format_num(cc['live']['annualized_pct'])}")
    print(f"Live total return %            : {_format_num(cc['live']['total_return_pct'])}")
    print(f"Avg backtest annual return %   : {_format_num(cc['backtests']['avg_annual_return_pct'])}")
    print(f"Avg backtest Sharpe            : {_format_num(cc['backtests']['avg_sharpe'])}")
    print(f"Best symbol (annualized)       : {cc['backtests']['best_symbol']} ({_format_num(cc['backtests']['best_annual_return_pct'])}%)")
    print(f"Competitors beaten on Sharpe   : {cc['industry']['competitors_beaten_on_sharpe']}/{cc['industry']['total_competitors']}")

    _print_section("Verdict")
    print(f"Execution change positive (return+sharpe): {summary['status']['execution_change_positive']}")
    print(f"Risk tradeoff present (hard-gate drawdown): {summary['status']['risk_tradeoff_present']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolidate execution and competitor benchmark reports")
    parser.add_argument(
        "--execution",
        type=Path,
        default=Path("benchmark_execution_optimization_report.json"),
        help="Path to execution optimization report JSON",
    )
    parser.add_argument(
        "--competitor",
        type=Path,
        default=None,
        help="Path to competitor benchmark JSON. If omitted, latest competitor_benchmark_*.json is used.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("consolidated_benchmark_summary.json"),
        help="Output JSON summary path",
    )
    args = parser.parse_args()

    root = Path.cwd()
    execution_path = args.execution
    competitor_path = args.competitor or _latest_competitor_report(root)

    if not execution_path.exists():
        raise SystemExit(f"Execution report not found: {execution_path}")
    if competitor_path is None or not competitor_path.exists():
        raise SystemExit("No competitor report found. Run _competitor_benchmark.py first.")

    execution_report = _read_json(execution_path)
    competitor_report = _read_json(competitor_path)

    summary = build_summary(execution_report, competitor_report)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print_dashboard(summary, execution_path, competitor_path)
    print("\nSaved consolidated JSON:", args.out)


if __name__ == "__main__":
    main()
