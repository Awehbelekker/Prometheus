"""
PROMETHEUS Full Performance Benchmark
======================================
Compares real PROMETHEUS live trading results against:
  - SPY   (S&P 500)
  - QQQ   (Nasdaq 100)
  - IWM   (Russell 2000 small-cap)
  - BTC   (Bitcoin)
  - BLEND (weighted by actual PROMETHEUS trade mix)

Metrics: Total return, Sharpe ratio, Sortino ratio, Max drawdown,
         Win rate, Alpha, Beta, monthly breakdown, best/worst trades.

Usage:
  python benchmark_full.py
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import math

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    HAS_YF = True
except ImportError:
    HAS_YF = False
    print("[WARN] yfinance/pandas/numpy not available - benchmark comparisons limited")

DB = Path("prometheus_learning.db")

# Period covered by real PROMETHEUS trades
PERIOD_START = "2025-12-01"
PERIOD_END   = "2026-04-29"
STARTING_CAPITAL = 211.0   # funded capital per .env


# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt(v, prefix="$", pct=False):
    if pct:
        return f"{v:+.2f}%"
    return f"{prefix}{v:+.2f}" if prefix else f"{v:.2f}"


def sharpe(returns, rf=0.0):
    """Annualised Sharpe from daily-like return series."""
    r = [x for x in returns if x is not None]
    if len(r) < 2:
        return 0.0
    mean = sum(r) / len(r)
    std  = math.sqrt(sum((x - mean) ** 2 for x in r) / (len(r) - 1))
    if std == 0:
        return 0.0
    return (mean - rf) / std * math.sqrt(252)


def sortino(returns, rf=0.0):
    r = [x for x in returns if x is not None]
    if len(r) < 2:
        return 0.0
    mean = sum(r) / len(r)
    neg  = [x for x in r if x < rf]
    if not neg:
        return float("inf")
    downside = math.sqrt(sum((x - rf) ** 2 for x in neg) / len(neg))
    if downside == 0:
        return 0.0
    return (mean - rf) / downside * math.sqrt(252)


def max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0.0
    for v in equity_curve:
        if v > peak:
            peak = v
        dd = (peak - v) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
    return max_dd


# ── Load PROMETHEUS real trades ────────────────────────────────────────────

def load_prometheus_trades():
    conn = sqlite3.connect(str(DB))
    rows = conn.execute("""
        SELECT symbol, timestamp, exit_timestamp, profit_loss, total_value,
               price, exit_price, action, confidence
        FROM trade_history
        WHERE exit_price > 0
          AND profit_loss IS NOT NULL
          AND profit_loss != 0
          AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp
    """, (PERIOD_START, PERIOD_END)).fetchall()
    conn.close()
    return rows


def build_equity_curve(trades):
    """Reconstruct equity curve from trades."""
    capital = STARTING_CAPITAL
    curve = []
    daily_returns = []
    last_date = None

    for sym, ts, exit_ts, pnl, val, entry_px, exit_px, action, conf in trades:
        capital += pnl
        date = ts[:10]
        curve.append((date, capital))
        if last_date and last_date != date:
            # approximate daily return
            prev = curve[-2][1] if len(curve) >= 2 else STARTING_CAPITAL
            if prev > 0:
                daily_returns.append((capital - prev) / prev)
        last_date = date

    return curve, capital, daily_returns


def trade_symbol_mix(trades):
    """Return dict of symbol -> % of trades."""
    crypto_keywords = {"/USD", "-USD"}
    crypto_count = sum(1 for t in trades if any(k in t[0] for k in crypto_keywords))
    equity_count  = len(trades) - crypto_count
    total = len(trades)
    return {
        "crypto_pct": crypto_count / total * 100 if total else 0,
        "equity_pct": equity_count / total * 100 if total else 0,
        "crypto_count": crypto_count,
        "equity_count": equity_count,
    }


# ── Market benchmark data ─────────────────────────────────────────────────

def fetch_benchmark(ticker, start, end, label):
    if not HAS_YF:
        return None
    try:
        hist = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=True)
        if len(hist) < 5:
            return None
        start_price = hist["Close"].iloc[0]
        end_price   = hist["Close"].iloc[-1]
        total_ret   = (end_price - start_price) / start_price * 100

        daily_ret = hist["Close"].pct_change().dropna().tolist()
        sh = sharpe(daily_ret)
        so = sortino(daily_ret)
        eq_curve = [float(p) for p in hist["Close"].tolist()]
        mdd = max_drawdown(eq_curve)

        # Volatility (annualised)
        std_daily = math.sqrt(sum(r**2 for r in daily_ret) / max(len(daily_ret)-1,1))
        vol = std_daily * math.sqrt(252) * 100

        return {
            "label":      label,
            "ticker":     ticker,
            "return_pct": round(total_ret, 2),
            "sharpe":     round(sh, 2),
            "sortino":    round(so, 2),
            "max_dd":     round(mdd, 2),
            "volatility": round(vol, 2),
            "daily_ret":  daily_ret,
        }
    except Exception as e:
        print(f"  [WARN] {label} fetch failed: {e}")
        return None


def build_blended_benchmark(spy, btc, crypto_pct):
    """Weighted blend of SPY + BTC based on actual trade mix."""
    if spy is None or btc is None:
        return None
    w_btc = crypto_pct / 100
    w_spy = 1 - w_btc
    blend_ret = w_spy * spy["return_pct"] + w_btc * btc["return_pct"]

    # Blend daily returns (zip to same length)
    spy_r = spy["daily_ret"]
    btc_r = btc["daily_ret"]
    min_len = min(len(spy_r), len(btc_r))
    blend_daily = [w_spy * s + w_btc * b for s, b in zip(spy_r[:min_len], btc_r[:min_len])]

    sh = sharpe(blend_daily)
    so = sortino(blend_daily)

    return {
        "label":      f"BLEND ({100-int(crypto_pct)}% SPY / {int(crypto_pct)}% BTC)",
        "ticker":     "BLEND",
        "return_pct": round(blend_ret, 2),
        "sharpe":     round(sh, 2),
        "sortino":    round(so, 2),
        "max_dd":     0.0,
        "volatility": 0.0,
        "daily_ret":  blend_daily,
    }


# ── Alpha / Beta calculation ──────────────────────────────────────────────

def calc_alpha_beta(prom_daily, benchmark_daily):
    if not prom_daily or not benchmark_daily:
        return 0.0, 0.0
    n = min(len(prom_daily), len(benchmark_daily))
    if n < 5:
        return 0.0, 0.0
    p = prom_daily[:n]
    b = benchmark_daily[:n]
    # Beta = Cov(p,b) / Var(b)
    mean_p = sum(p) / n
    mean_b = sum(b) / n
    cov    = sum((pi - mean_p) * (bi - mean_b) for pi, bi in zip(p, b)) / (n - 1)
    var_b  = sum((bi - mean_b) ** 2 for bi in b) / (n - 1)
    beta   = cov / var_b if var_b != 0 else 0.0
    # Alpha (annualised)
    alpha  = (mean_p - beta * mean_b) * 252 * 100
    return round(alpha, 2), round(beta, 2)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  PROMETHEUS Full Performance Benchmark")
    print(f"  Period: {PERIOD_START}  to  {PERIOD_END}")
    print(f"  Starting capital: ${STARTING_CAPITAL:.0f}")
    print("=" * 70)

    # ── PROMETHEUS stats ──────────────────────────────────────────────────
    print("\n  Loading PROMETHEUS live trades...")
    trades = load_prometheus_trades()
    if not trades:
        print("  No closed trades found in database.")
        return

    equity_curve, final_capital, daily_rets = build_equity_curve(trades)
    total_pnl    = final_capital - STARTING_CAPITAL
    total_return = total_pnl / STARTING_CAPITAL * 100
    wins         = sum(1 for t in trades if t[3] > 0)
    losses       = sum(1 for t in trades if t[3] < 0)
    win_rate     = wins / len(trades) * 100
    best_trade   = max(t[3] for t in trades)
    worst_trade  = min(t[3] for t in trades)
    avg_pnl      = total_pnl / len(trades) if trades else 0
    mdd          = max_drawdown([v for _, v in equity_curve])
    sh           = sharpe(daily_rets)
    so           = sortino(daily_rets)
    mix          = trade_symbol_mix(trades)

    # ── Market benchmarks ─────────────────────────────────────────────────
    print("  Fetching market benchmarks...")
    spy  = fetch_benchmark("SPY",     PERIOD_START, PERIOD_END, "S&P 500 (SPY)")
    qqq  = fetch_benchmark("QQQ",     PERIOD_START, PERIOD_END, "Nasdaq 100 (QQQ)")
    iwm  = fetch_benchmark("IWM",     PERIOD_START, PERIOD_END, "Russell 2000 (IWM)")
    btc  = fetch_benchmark("BTC-USD", PERIOD_START, PERIOD_END, "Bitcoin (BTC)")
    blend = build_blended_benchmark(spy, btc, mix["crypto_pct"])

    benchmarks = [b for b in [spy, qqq, iwm, btc, blend] if b is not None]

    # Alpha/Beta vs SPY
    alpha, beta = calc_alpha_beta(daily_rets, spy["daily_ret"] if spy else [])

    # ── Monthly breakdown ─────────────────────────────────────────────────
    monthly = defaultdict(lambda: {"trades": 0, "wins": 0, "pnl": 0.0})
    for sym, ts, exit_ts, pnl, val, ep, xp, action, conf in trades:
        m = ts[:7]
        monthly[m]["trades"] += 1
        monthly[m]["wins"]   += 1 if pnl > 0 else 0
        monthly[m]["pnl"]    += pnl

    # ── PRINT RESULTS ─────────────────────────────────────────────────────

    print()
    print("=" * 70)
    print("  PROMETHEUS LIVE PERFORMANCE")
    print("=" * 70)
    print(f"  Trades:       {len(trades)} closed  ({wins}W / {losses}L)")
    print(f"  Win Rate:     {win_rate:.1f}%")
    print(f"  Total PnL:    ${total_pnl:+.2f}")
    print(f"  Total Return: {total_return:+.2f}%  (${STARTING_CAPITAL:.0f} to ${final_capital:.2f})")
    print(f"  Best Trade:   ${best_trade:+.2f}")
    print(f"  Worst Trade:  ${worst_trade:+.2f}")
    print(f"  Avg/Trade:    ${avg_pnl:+.3f}")
    print(f"  Max Drawdown: {mdd:.1f}%")
    print(f"  Sharpe Ratio: {sh:.2f}")
    print(f"  Sortino Ratio:{so:.2f}")
    print(f"  Alpha vs SPY: {alpha:+.2f}%/yr")
    print(f"  Beta vs SPY:  {beta:.2f}")
    print(f"  Trade Mix:    {mix['equity_pct']:.0f}% equities / {mix['crypto_pct']:.0f}% crypto")
    print(f"               ({mix['equity_count']} equity trades / {mix['crypto_count']} crypto trades)")

    # ── Monthly table ─────────────────────────────────────────────────────
    print()
    print(f"  {'Month':<8}  {'Trades':>6}  {'Win%':>5}  {'PnL':>10}  {'Running Capital':>16}")
    print(f"  {'------':<8}  {'------':>6}  {'----':>5}  {'---':>10}  {'---------------':>16}")
    cap = STARTING_CAPITAL
    for m in sorted(monthly):
        d = monthly[m]
        wr = d["wins"] / d["trades"] * 100 if d["trades"] else 0
        cap += d["pnl"]
        print(f"  {m:<8}  {d['trades']:>6}  {wr:>4.0f}%  ${d['pnl']:>+8.2f}  ${cap:>14.2f}")

    # ── Benchmark comparison table ─────────────────────────────────────────
    print()
    print("=" * 70)
    print("  HEAD-TO-HEAD vs MARKET BENCHMARKS")
    print("=" * 70)
    print(f"  {'Asset':<28}  {'Return':>8}  {'Sharpe':>7}  {'Sortino':>8}  {'MaxDD':>7}  {'Vol':>6}")
    print(f"  {'-'*28}  {'-'*8}  {'-'*7}  {'-'*8}  {'-'*7}  {'-'*6}")

    prom_row = f"  {'*** PROMETHEUS (live) ***':<28}  {total_return:>+7.2f}%  {sh:>7.2f}  {so:>8.2f}  {mdd:>6.1f}%  {'N/A':>6}"
    print(prom_row)

    for bm in benchmarks:
        vol_str = f"{bm['volatility']:.1f}%" if bm['volatility'] > 0 else "N/A"
        print(f"  {bm['label']:<28}  {bm['return_pct']:>+7.2f}%  {bm['sharpe']:>7.2f}  {bm['sortino']:>8.2f}  {bm['max_dd']:>6.1f}%  {vol_str:>6}")

    # ── Beat/lose summary ──────────────────────────────────────────────────
    print()
    print("  PROMETHEUS vs each benchmark:")
    for bm in benchmarks:
        diff = total_return - bm["return_pct"]
        verdict = "BEATS" if diff > 0 else "LAGS "
        bar_len = min(abs(int(diff)), 30)
        bar = ("+" if diff > 0 else "-") * bar_len
        print(f"  {verdict}  {bm['label']:<28}  {diff:>+6.2f}%  [{bar}]")

    # ── Top symbols ───────────────────────────────────────────────────────
    sym_stats = defaultdict(lambda: {"trades": 0, "wins": 0, "pnl": 0.0})
    for sym, ts, exit_ts, pnl, val, ep, xp, action, conf in trades:
        sym_stats[sym]["trades"] += 1
        sym_stats[sym]["wins"]   += 1 if pnl > 0 else 0
        sym_stats[sym]["pnl"]    += pnl

    print()
    print("  TOP SYMBOLS BY PnL:")
    print(f"  {'Symbol':<12}  {'Trades':>6}  {'Win%':>5}  {'PnL':>9}  {'Avg/Trade':>10}")
    print(f"  {'-'*12}  {'-'*6}  {'-'*5}  {'-'*9}  {'-'*10}")
    for sym, d in sorted(sym_stats.items(), key=lambda x: x[1]["pnl"], reverse=True)[:12]:
        wr  = d["wins"] / d["trades"] * 100 if d["trades"] else 0
        avg = d["pnl"] / d["trades"]
        print(f"  {sym:<12}  {d['trades']:>6}  {wr:>4.0f}%  ${d['pnl']:>+7.2f}  ${avg:>+8.3f}")

    # ── Final verdict ──────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  VERDICT")
    print("=" * 70)

    beats_count = sum(1 for bm in benchmarks if total_return > bm["return_pct"])
    total_bm    = len(benchmarks)

    print(f"  PROMETHEUS beats {beats_count}/{total_bm} benchmarks on raw return")

    if sh > 1.0:
        print(f"  Sharpe {sh:.2f} = GOOD risk-adjusted returns (>1.0 is strong)")
    elif sh > 0.5:
        print(f"  Sharpe {sh:.2f} = MODERATE risk-adjusted returns")
    else:
        print(f"  Sharpe {sh:.2f} = WEAK risk-adjusted returns (target >1.0)")

    if beta < 0.5:
        print(f"  Beta {beta:.2f} = LOW market correlation (good for diversification)")
    elif beta < 1.0:
        print(f"  Beta {beta:.2f} = MODERATE market correlation")
    else:
        print(f"  Beta {beta:.2f} = HIGH market correlation (moves with market)")

    if alpha > 0:
        print(f"  Alpha {alpha:+.2f}%/yr = generating EXCESS returns above market")
    else:
        print(f"  Alpha {alpha:+.2f}%/yr = underperforming vs market on risk-adjusted basis")

    if mdd < 10:
        print(f"  Max drawdown {mdd:.1f}% = TIGHT capital protection")
    elif mdd < 20:
        print(f"  Max drawdown {mdd:.1f}% = ACCEPTABLE drawdown control")
    else:
        print(f"  Max drawdown {mdd:.1f}% = ELEVATED drawdown — review risk limits")

    print()
    print(f"  Period: {PERIOD_START} to {PERIOD_END}  ({len(trades)} real closed trades)")
    print("=" * 70)


if __name__ == "__main__":
    main()
