#!/usr/bin/env python3
"""
Retrain ML direction models for all backtest symbols on fresh 2025-2026 data.

Trains: SPY, AAPL, MSFT, TSLA, QQQ, NVDA, AMD, AMZN, GOOGL, META
Uses AutoModelRetrainer with force=True to bypass staleness checks.

Usage:  python _retrain_backtest_models.py
"""
import sys, asyncio, time, json
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Priority symbols — ones we benchmark + high-volume trading symbols
RETRAIN_SYMBOLS = [
    "SPY", "QQQ",                          # Indices (most important for benchmarks)
    "AAPL", "MSFT", "TSLA", "NVDA", "AMD", # High-beta individual names
    "AMZN", "GOOGL", "META",               # Mega-cap tech
]

print("=" * 68)
print("  PROMETHEUS MODEL RETRAINER")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Symbols: {', '.join(RETRAIN_SYMBOLS)}")
print("=" * 68)


async def main():
    from core.auto_model_retrainer import AutoModelRetrainer

    retrainer = AutoModelRetrainer(symbols=RETRAIN_SYMBOLS)
    print(f"\n  Retrainer ready. Min accuracy threshold: "
          f"{retrainer.min_direction_accuracy:.0%}  "
          f"(stale if >{retrainer.stale_days}d old)\n")

    all_results = []
    t_start = time.time()

    for sym in RETRAIN_SYMBOLS:
        print(f"  ── {sym} ──────────────────────────────────")
        t0 = time.time()
        try:
            results = await retrainer.retrain_symbol(sym, force=True)
            dt = time.time() - t0

            for r in results:
                icon = "+" if r.success else "x"
                metric_str = ""
                if r.new_metric is not None:
                    label = "acc" if r.model_type == "direction" else "R²"
                    if r.old_metric is not None:
                        delta = r.new_metric - r.old_metric
                        metric_str = (f"{label}={r.new_metric:.3f} "
                                      f"(was {r.old_metric:.3f}, "
                                      f"{'▲' if delta >= 0 else '▼'}{abs(delta):.3f})")
                    else:
                        label = "acc" if r.model_type == "direction" else "R²"
                        metric_str = f"{label}={r.new_metric:.3f} (new model)"
                reason = f"  [{r.reason}]" if r.reason and not r.success else ""
                print(f"    [{icon}] {r.model_type:<12} {metric_str}  samples={r.samples}  {dt:.1f}s{reason}")
                all_results.append({
                    "symbol": sym,
                    "model_type": r.model_type,
                    "success": r.success,
                    "old_metric": r.old_metric,
                    "new_metric": r.new_metric,
                    "samples": r.samples,
                    "reason": r.reason,
                })
        except Exception as e:
            dt = time.time() - t0
            print(f"    [x] FAILED: {e}  ({dt:.1f}s)")
            all_results.append({"symbol": sym, "success": False, "reason": str(e)})

    total_time = time.time() - t_start

    # ── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print("  RETRAINING SUMMARY")
    print("=" * 68)

    direction_results = [r for r in all_results if r.get("model_type") == "direction"]
    successes = [r for r in direction_results if r.get("success")]
    improved  = [r for r in successes
                 if r.get("new_metric") and r.get("old_metric")
                 and r["new_metric"] > r["old_metric"]]
    new_models = [r for r in successes if r.get("old_metric") is None]

    print(f"\n  Direction models: {len(successes)}/{len(direction_results)} retrained")
    print(f"  Improved vs old:  {len(improved)}")
    print(f"  Brand new:        {len(new_models)}")
    print(f"  Total time:       {total_time:.1f}s")

    if successes:
        accs = [r["new_metric"] for r in successes if r.get("new_metric")]
        if accs:
            print(f"\n  Accuracy stats  min={min(accs):.3f}  avg={sum(accs)/len(accs):.3f}  max={max(accs):.3f}")

    if improved:
        print(f"\n  Top improvements:")
        improved.sort(key=lambda r: r["new_metric"] - r["old_metric"], reverse=True)
        for r in improved[:5]:
            delta = r["new_metric"] - r["old_metric"]
            print(f"    {r['symbol']:<6} {r['old_metric']:.3f} → {r['new_metric']:.3f}  (+{delta:.3f})")

    # Save results
    out = {
        "timestamp": datetime.now().isoformat(),
        "symbols": RETRAIN_SYMBOLS,
        "total_time_s": round(total_time, 1),
        "direction_retrained": len(successes),
        "results": all_results,
    }
    out_path = f"retrain_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved: {out_path}")

    # ── Advice on benchmarks ─────────────────────────────────────
    if successes:
        print(f"\n  Next: run  python _run_full_test_suite.py  to see updated benchmark results.")

    return len(successes)


if __name__ == "__main__":
    n = asyncio.run(main())
    print("\n  Done.\n")
    sys.exit(0 if n > 0 else 1)
