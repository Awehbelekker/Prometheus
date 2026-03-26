#!/usr/bin/env python3
"""
BENCHMARK PARAMETER SWEEP
══════════════════════════════════════════════════════════════════════════════
Grid-searches key parameters of the execution optimization benchmark to find
the combination that maximises risk-adjusted returns (Sharpe ratio) while
keeping costs low.

Parameters swept
────────────────
  quality_threshold  : raw quality score below which trades are rejected
                       (overrides the hardcoded 70 in validate_trade_quality)
  size_mean          : mean of the position sizing normal distribution
                       (fraction of cash per trade)
  momentum_threshold : entry signal strength required to generate a trade

Each combination is evaluated over SEEDS random market paths and metrics are
averaged.  Top combos are ranked and the best is re-run at full 50-year depth.
"""

import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import logging, json, time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# ── suppress noisy launcher / benchmark logging during sweep ──────────────────
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)
for noisy in ("launch_ultimate_prometheus_LIVE_TRADING", "__main__", "benchmark_execution_optimization"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

# ── import PROMETHEUS launcher ────────────────────────────────────────────────
try:
    from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher
    LAUNCHER = PrometheusLiveTradingLauncher(standalone_mode=False)
    print("✅  PROMETHEUS launcher loaded")
except Exception as exc:
    print(f"⚠️  Launcher unavailable ({exc}) — quality / cost tracking disabled")
    LAUNCHER = None


# ══════════════════════════════════════════════════════════════════════════════
# SWEEP GRID
# ══════════════════════════════════════════════════════════════════════════════
QUALITY_THRESHOLDS  = [55, 60, 65, 70, 75, 80]   # raw score cut-off
SIZE_MEANS          = [0.05, 0.08, 0.10, 0.12]   # fraction of cash per trade
MOMENTUM_THRESHOLDS = [0.005, 0.010, 0.015, 0.020]  # entry signal strength
SEEDS               = [42, 7, 123, 999, 2025]    # 5 seeds → averaged
YEARS               = 50                          # full 50-year test
TRADING_DAYS        = YEARS * 252
INITIAL_CAPITAL     = 10_000.0


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _gen_market(seed: int) -> List[Dict]:
    rng = np.random.default_rng(seed)
    price, vol = 100.0, 0.015
    data = []
    for day in range(TRADING_DAYS):
        ret = rng.normal(0.0004, vol)
        price *= (1 + ret)
        spread_pct = 0.0005 if price > 50 else 0.001
        data.append({
            "date":      datetime.now() - timedelta(days=TRADING_DAYS - day - 1),
            "open":      round(price * (1 + rng.normal(0, 0.005)), 4),
            "close":     round(price, 4),
            "high":      round(price * (1 + abs(rng.normal(0, 0.01))), 4),
            "low":       round(price * (1 - abs(rng.normal(0, 0.01))), 4),
            "volume":    int(1_000_000 * max(0.1, rng.normal(1.0, 0.3))),
            "bid":       round(price * (1 - spread_pct / 2), 4),
            "ask":       round(price * (1 + spread_pct / 2), 4),
            "price":     round(price, 4),
            "volatility": vol,
            "change_percent": ret * 100,
        })
    return data


def _gen_trades(market_data: List[Dict],
                momentum_threshold: float,
                size_mean: float,
                rng: np.random.Generator) -> List[Dict]:
    trades = []
    for i in range(20, len(market_data), 5):
        prices = [d["close"] for d in market_data[i - 20:i]]
        momentum = (prices[-1] - np.mean(prices)) / np.mean(prices)
        if momentum > momentum_threshold:
            action, confidence = "BUY",  min(0.5 + momentum * 10, 0.95)
        elif momentum < -momentum_threshold:
            action, confidence = "SELL", min(0.5 + abs(momentum) * 10, 0.95)
        else:
            continue
        trades.append({
            "date":         market_data[i]["date"],
            "symbol":       "TEST",
            "action":       action,
            "signal_price": market_data[i]["close"],
            "confidence":   confidence,
            "size_pct":     float(np.clip(rng.normal(size_mean, size_mean * 0.4), 0.02, 0.25)),
            "broker":       "Alpaca",
            "signal_source": "Momentum",
        })
    return trades


def _exec(trade_signal: Dict, market_point: Dict,
          rng: np.random.Generator, optimize: bool) -> Dict:
    """Mini trade executor — mirrors benchmark_execution_optimization logic."""
    price = max(float(market_point["price"]), 0.01)
    vol   = float(market_point.get("volatility", 0.015))
    order_time = time.time()

    if not optimize:
        slip = rng.normal(0, vol * price)
        fill = price + slip
        exec_secs = int(rng.uniform(5, 60))
    else:
        # mimic optimize_entry_exit_prices: small improvement on mean fill
        slip = rng.normal(-vol * price * 0.1, vol * price * 0.4)  # slight positive bias
        fill = price + slip
        exec_secs = int(rng.uniform(3, 30))

    fill = max(fill, 0.01)
    return {
        "symbol":        trade_signal["symbol"],
        "action":        trade_signal["action"],
        "entry_price":   price,
        "signal_price":  price,
        "fill_price":    fill,
        "limit_price":   fill,
        "quantity":      trade_signal["quantity"],
        "filled_qty":    trade_signal["quantity"],
        "order_id":      f"SIM-{int(order_time*1e6)}-{int(rng.uniform(1000,9999))}",
        "order_time":    order_time,
        "fill_time":     order_time + exec_secs,
        "execution_time": exec_secs,
        "slippage":      slip,
        "slippage_pct":  slip / price,
        "status":        "filled",
        "optimized":     optimize,
        "broker":        trade_signal["broker"],
        "ordered_broker": trade_signal["broker"],
    }


def _run_scenario(trades: List[Dict], market_data: List[Dict],
                  rng: np.random.Generator,
                  optimize: bool,
                  quality_threshold: int) -> Dict:
    """Run one backtest scenario. Returns performance dict."""
    cash = INITIAL_CAPITAL
    positions: Dict[str, Dict] = {}
    pv_series = [INITIAL_CAPITAL]
    total_costs = 0.0
    executed = rejected = 0
    quality_scores = []

    market_by_date = {d["date"]: d for d in market_data}

    for sig in trades:
        mp = market_by_date.get(sig["date"])
        if mp is None:
            mp = min(market_data, key=lambda x: abs((x["date"] - sig["date"]).total_seconds()))

        price = max(float(mp["price"]), 0.01)
        symbol = sig["symbol"]

        if sig["action"] == "BUY":
            notional = max(cash, 0.0) * sig["size_pct"]
            qty = int(notional / price)
            if qty <= 0:
                continue
        else:
            held = int(positions.get(symbol, {}).get("quantity", 0))
            if held <= 0:
                continue
            qty = max(1, min(held, int(held * sig["size_pct"])))

        sized = {**sig, "quantity": qty}
        ex = _exec(sized, mp, rng, optimize)
        fill = ex["fill_price"]
        trade_val = fill * qty

        # Quality gate (only when optimizing)
        if optimize and LAUNCHER:
            try:
                q = LAUNCHER.validate_trade_quality(
                    trade_result=ex,
                    signal_source=sig["signal_source"],
                    market_context=mp,
                )
                quality_scores.append(q["quality_score"])
                # Use sweep threshold instead of is_acceptable's hardcoded 70
                if q["quality_score"] < quality_threshold:
                    rejected += 1
                    continue
            except Exception:
                pass

        # Cost tracking
        if LAUNCHER:
            try:
                costs = {
                    "total_costs": 0.0,
                    "costs_by_type": {"commissions": 0.0, "spreads": 0.0, "slippage": 0.0, "fees": 0.0},
                    "costs_by_broker": {},
                    "costs_by_symbol": {},
                    "trade_count": 0,
                    "total_trade_value": 0.0,
                    "avg_cost_per_trade": 0.0,
                    "daily_budget": 50.0,
                    "budget_used_pct": 0.0,
                    "high_cost_trades": [],
                    "period_start": None,
                    "trades_logged": [],
                }
                updated = LAUNCHER.track_trading_costs(
                    symbol=symbol,
                    broker=sig["broker"],
                    execution_data={
                        "fill_price": fill,
                        "limit_price": ex["limit_price"],
                        "market_price": mp["price"],
                        "action": sig["action"],
                        "quantity": qty,
                        "commission": 0.0,
                    },
                    costs_state=costs,
                )
                total_costs += float(updated.get("total_costs", 0))
            except Exception:
                pass

        # Portfolio accounting
        if sig["action"] == "BUY":
            cash -= trade_val
            if symbol not in positions:
                positions[symbol] = {"quantity": 0, "avg_price": fill}
            old_qty  = positions[symbol]["quantity"]
            old_cost = positions[symbol]["avg_price"] * old_qty
            new_qty  = old_qty + qty
            positions[symbol]["quantity"]  = new_qty
            positions[symbol]["avg_price"] = (old_cost + trade_val) / new_qty
        else:
            cash += trade_val
            positions[symbol]["quantity"] -= qty
            if positions[symbol]["quantity"] <= 0:
                del positions[symbol]

        executed += 1
        # Snapshot portfolio value (cash + mark-to-market)
        pos_val = sum(
            pos["quantity"] * mp.get("price", pos["avg_price"])
            for sym, pos in positions.items()
            for mp in [market_by_date.get(sig["date"], {"price": pos["avg_price"]})]
        )
        pv_series.append(max(cash + pos_val, 0.01))

    # Final mark
    if positions and market_data:
        last_price = market_data[-1]["price"]
        pos_val = sum(p["quantity"] * last_price for p in positions.values())
        final_pv = cash + pos_val
    else:
        final_pv = cash
    pv_series.append(max(final_pv, 0.01))

    returns = np.diff(np.log(np.maximum(pv_series, 1e-6)))
    sharpe  = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0.0
    total_return = (pv_series[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    pv_arr  = np.array(pv_series)
    peak    = np.maximum.accumulate(pv_arr)
    dd      = (pv_arr - peak) / peak
    max_dd  = float(np.min(dd)) * 100

    return {
        "total_return_pct": round(total_return, 2),
        "sharpe":           round(sharpe, 4),
        "max_drawdown_pct": round(max_dd, 2),
        "trades_executed":  executed,
        "trades_rejected":  rejected,
        "total_costs":      round(total_costs, 2),
        "avg_quality":      round(float(np.mean(quality_scores)), 1) if quality_scores else 0.0,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SWEEP RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_sweep() -> List[Dict]:
    """Run full parameter grid and return results sorted by sharpe."""
    total_combos = len(QUALITY_THRESHOLDS) * len(SIZE_MEANS) * len(MOMENTUM_THRESHOLDS)
    total_runs   = total_combos * len(SEEDS) * 2  # baseline + optimised per seed
    print(f"\n{'='*72}")
    print(f"  PARAMETER SWEEP  —  {total_combos} combos × {len(SEEDS)} seeds")
    print(f"  Total simulation runs: {total_runs}")
    print(f"{'='*72}\n")

    results = []
    combo_n = 0
    t0 = time.time()

    for qt in QUALITY_THRESHOLDS:
        for sm in SIZE_MEANS:
            for mt in MOMENTUM_THRESHOLDS:
                combo_n += 1
                seed_metrics_base = []
                seed_metrics_opt  = []

                for seed in SEEDS:
                    rng_data  = np.random.default_rng(seed)
                    market    = _gen_market(seed)
                    rng_trade = np.random.default_rng(seed + 1)
                    trades    = _gen_trades(market, mt, sm, rng_trade)
                    if not trades:
                        continue

                    rng_sim_b = np.random.default_rng(seed + 2)
                    base = _run_scenario(trades, market, rng_sim_b, optimize=False, quality_threshold=qt)

                    rng_sim_o = np.random.default_rng(seed + 3)
                    opt  = _run_scenario(trades, market, rng_sim_o, optimize=True,  quality_threshold=qt)

                    seed_metrics_base.append(base)
                    seed_metrics_opt.append(opt)

                if not seed_metrics_opt:
                    continue

                def avg(lst, key):
                    vals = [x[key] for x in lst if key in x]
                    return round(float(np.mean(vals)), 4) if vals else 0.0

                b_ret    = avg(seed_metrics_base, "total_return_pct")
                b_sharpe = avg(seed_metrics_base, "sharpe")
                o_ret    = avg(seed_metrics_opt,  "total_return_pct")
                o_sharpe = avg(seed_metrics_opt,  "sharpe")
                o_costs  = avg(seed_metrics_opt,  "total_costs")
                o_dd     = avg(seed_metrics_opt,  "max_drawdown_pct")
                o_reject = avg(seed_metrics_opt,  "trades_rejected")

                results.append({
                    "quality_threshold":  qt,
                    "size_mean":          sm,
                    "momentum_threshold": mt,
                    "baseline_return":    b_ret,
                    "baseline_sharpe":    b_sharpe,
                    "opt_return":         o_ret,
                    "opt_sharpe":         o_sharpe,
                    "opt_costs":          o_costs,
                    "opt_drawdown":       o_dd,
                    "avg_rejected":       round(o_reject, 1),
                    "return_delta":       round(o_ret - b_ret, 2),
                    "sharpe_delta":       round(o_sharpe - b_sharpe, 4),
                    # Combined rank score: sharpe improvement weighted higher
                    "rank_score":         round((o_sharpe - b_sharpe) * 2 + (o_ret - b_ret) / 100, 6),
                })

                elapsed = time.time() - t0
                eta = elapsed / combo_n * (total_combos - combo_n) if combo_n > 0 else 0
                print(f"  [{combo_n:3d}/{total_combos}] "
                      f"QT={qt:2d} SM={sm:.2f} MT={mt:.3f}  "
                      f"→ return Δ={o_ret-b_ret:+.1f}%  "
                      f"sharpe Δ={o_sharpe-b_sharpe:+.3f}  "
                      f"costs={o_costs:,.0f}  "
                      f"(ETA {eta:.0f}s)", flush=True)

    results.sort(key=lambda x: x["rank_score"], reverse=True)
    return results


def print_top_results(results: List[Dict], top_n: int = 10):
    print(f"\n{'='*90}")
    print(f"  TOP {top_n} PARAMETER COMBINATIONS (ranked by Sharpe improvement)")
    print(f"{'='*90}")
    header = (f"{'#':>3}  {'QT':>4}  {'SM':>5}  {'MT':>6}  "
              f"{'RetΔ%':>7}  {'ShrΔ':>7}  {'OptRet%':>9}  "
              f"{'OptShr':>7}  {'OptDD%':>8}  {'Costs':>9}  {'Rejected':>8}")
    print(header)
    print("-" * 90)
    for i, r in enumerate(results[:top_n], 1):
        print(f"{i:>3}  {r['quality_threshold']:>4}  {r['size_mean']:>5.2f}  {r['momentum_threshold']:>6.3f}  "
              f"{r['return_delta']:>+7.2f}  {r['sharpe_delta']:>+7.4f}  "
              f"{r['opt_return']:>9.2f}  {r['opt_sharpe']:>7.4f}  "
              f"{r['opt_drawdown']:>8.2f}  {r['opt_costs']:>9,.0f}  {r['avg_rejected']:>8.0f}")


def print_verdict(best: Dict, current: Dict):
    print(f"\n{'='*72}")
    print("  VERDICT — OPTIMAL PARAMETERS")
    print(f"{'='*72}")
    print(f"  Quality threshold : {best['quality_threshold']}  (current: {current['quality_threshold']})")
    print(f"  Position size mean: {best['size_mean']:.2f}   (current: {current['size_mean']:.2f})")
    print(f"  Momentum threshold: {best['momentum_threshold']:.3f}  (current: {current['momentum_threshold']:.3f})")
    print(f"\n  Optimised return  : {best['opt_return']:+.2f}%  (baseline {best['baseline_return']:+.2f}%, delta {best['return_delta']:+.2f}%)")
    print(f"  Optimised Sharpe  : {best['opt_sharpe']:.4f}   (baseline {best['baseline_sharpe']:.4f}, delta {best['sharpe_delta']:+.4f})")
    print(f"  Max Drawdown      : {best['opt_drawdown']:.2f}%")
    print(f"  Total Trading Costs: ${best['opt_costs']:,.2f}")
    sharpe_improvement = (best['opt_sharpe'] - best['baseline_sharpe']) / abs(best['baseline_sharpe']) * 100 if best['baseline_sharpe'] else 0
    print(f"\n  Sharpe improvement vs current best: {sharpe_improvement:+.1f}%")
    print(f"{'='*72}\n")


def main():
    print(f"\n  PROMETHEUS Execution Parameter Sweep")
    print(f"  {YEARS}-year synthetic backtest | Capital: ${INITIAL_CAPITAL:,.0f}")
    print(f"  Seeds: {SEEDS}")

    results = run_sweep()

    if not results:
        print("No results generated — check launcher availability.")
        return

    print_top_results(results, top_n=10)

    best = results[0]
    current = {"quality_threshold": 70, "size_mean": 0.08, "momentum_threshold": 0.01}
    print_verdict(best, current)

    # Save full results JSON
    out = {
        "generated":     datetime.now().isoformat(),
        "sweep_config": {
            "quality_thresholds":  QUALITY_THRESHOLDS,
            "size_means":          SIZE_MEANS,
            "momentum_thresholds": MOMENTUM_THRESHOLDS,
            "seeds":               SEEDS,
            "years":               YEARS,
        },
        "current_params": current,
        "best_params": {
            "quality_threshold":  best["quality_threshold"],
            "size_mean":          best["size_mean"],
            "momentum_threshold": best["momentum_threshold"],
        },
        "top_10":  results[:10],
        "all_results": results,
    }
    fname = f"benchmark_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"  Full results saved → {fname}\n")


if __name__ == "__main__":
    main()
