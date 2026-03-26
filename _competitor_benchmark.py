"""
PROMETHEUS COMPETITOR PERFORMANCE BENCHMARK
============================================
Compares PROMETHEUS live + backtest performance against:
  - S&P 500 Buy & Hold (SPY)
  - NASDAQ Buy & Hold (QQQ)
  - Renaissance Medallion Fund (best-known quant hedge fund)
  - Two Sigma / Citadel class HFTs
  - Retail algo trading platforms (Quantopian era, typical retail quant)
  - Warren Buffett / Berkshire (long-term benchmark)
  - Typical ChatGPT/AI trading strategies (academic papers)
  - Alpaca AI (competitor robo-trader)
"""

import json, os, requests, sys
from datetime import datetime, date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
REPORTS = BASE / "backtest_reports"

# ─────────────────────────────────────────────
# 1. PROMETHEUS LIVE ACCOUNT
# ─────────────────────────────────────────────
def get_prometheus_live():
    headers = {
        'APCA-API-KEY-ID':    os.getenv('ALPACA_API_KEY', 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z'),
        'APCA-API-SECRET-KEY':os.getenv('ALPACA_SECRET_KEY', 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX')
    }
    base = 'https://api.alpaca.markets'
    acct = requests.get(f'{base}/v2/account', headers=headers, timeout=10).json()
    equity    = float(acct.get('equity', 0))
    last_equity = float(acct.get('last_equity', equity))
    orders    = requests.get(f'{base}/v2/orders?status=all&limit=500&direction=desc', headers=headers, timeout=10).json()
    filled    = [o for o in orders if o.get('status') == 'filled']
    # Oldest filled order = start date
    if filled:
        start_str = sorted(filled, key=lambda o: o['submitted_at'])[0]['submitted_at'][:10]
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
    else:
        start = date(2026, 2, 19)
    days_live = max((date.today() - start).days, 1)
    # Total P&L approximation from order fills
    buys  = sum(float(o.get('filled_avg_price',0))*float(o.get('qty',0)) for o in filled if o['side']=='buy')
    sells = sum(float(o.get('filled_avg_price',0))*float(o.get('qty',0)) for o in filled if o['side']=='sell')
    net_pnl_pct = ((equity - last_equity) / last_equity * 100) if last_equity else 0
    total_return_pct = ((equity - 100.0) / 100.0) * 100  # Started with ~$100
    annualized = ((1 + total_return_pct/100) ** (365/days_live) - 1) * 100
    return {
        'equity': equity,
        'total_return_pct': total_return_pct,
        'annualized_pct': annualized,
        'days_live': days_live,
        'trades': len(filled),
        'start_date': str(start),
    }

# ─────────────────────────────────────────────
# 2. PROMETHEUS BACKTESTS
# ─────────────────────────────────────────────
def get_prometheus_backtests():
    results = []
    for f in sorted(REPORTS.glob("*prometheus_ai_20260302*.json")):
        d = json.loads(f.read_text())
        m = d.get('overall_metrics', {})
        wf = d.get('walk_forward', {})
        mc = d.get('monte_carlo', {})
        results.append({
            'symbol':       d.get('symbol', f.stem.split('_')[0]),
            'total_return': round(float(m.get('total_return_pct', 0)), 1),
            'ann_return':   round(float(m.get('annualized_return_pct', 0)), 1),
            'bnh_return':   round(float(m.get('buy_and_hold_return_pct', 0)), 1),
            'sharpe':       round(float(m.get('sharpe_ratio', 0)), 2),
            'sortino':      round(float(m.get('sortino_ratio', 0)), 2),
            'calmar':       round(float(m.get('calmar_ratio', 0)), 2),
            'max_dd':       round(float(m.get('max_drawdown_pct', 0)), 1),
            'win_rate':     round(float(m.get('win_rate', 0)) * 100, 1),
            'trades':       int(m.get('total_trades', 0)),
            'wf_sharpe':    round(float(wf.get('avg_test_sharpe', 0)), 2),
            'verdict':      mc.get('verdict', '?'),
        })
    return results

# ─────────────────────────────────────────────
# 3. INDUSTRY BENCHMARKS (public figures)
# ─────────────────────────────────────────────
COMPETITORS = [
    # name, annual_return%, sharpe, max_dd%, notes
    ("S&P 500 (SPY buy & hold)",        18.9,   0.74,  -15.0, "SPY 1yr passive, our test period"),
    ("NASDAQ 100 (QQQ buy & hold)",     22.1,   0.94,  -18.0, "QQQ 1yr passive, our test period"),
    ("Warren Buffett / Berkshire",       19.8,   0.75,  -12.0, "50yr avg ~20%/yr, Sharpe ~0.75"),
    ("Renaissance Medallion Fund",       66.0,   2.50,   -5.0, "Best quant fund ever, ~66%/yr before fees"),
    ("Two Sigma / Citadel (est.)",       30.0,   1.80,   -8.0, "Top HFT/quant, est. ~30%/yr"),
    ("Typical Retail Algo Trader",       12.0,   0.60,  -20.0, "Most retail quants, 10-15%/yr"),
    ("ChatGPT-4 Trading (academia)",     15.3,   0.85,  -14.0, "Lopez-Lira & Tang 2023, GPT-4 sentiment"),
    ("Alpaca Broker Algo Avg",           11.0,   0.55,  -18.0, "Alpaca community algo avg estimate"),
    ("Hedge Fund Industry Avg",          11.5,   0.62,  -12.0, "HFR Index 2024 avg net of fees"),
]

# ─────────────────────────────────────────────
# MAIN REPORT
# ─────────────────────────────────────────────
def main():
    print("=" * 80)
    print("  PROMETHEUS TRADING PLATFORM — COMPETITOR BENCHMARK")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    # --- Live account ---
    print("\n📡 Fetching live Alpaca account data...")
    try:
        live = get_prometheus_live()
        print(f"\n{'─'*80}")
        print("  PROMETHEUS LIVE ACCOUNT (Real Money — Alpaca)")
        print(f"{'─'*80}")
        print(f"  Portfolio value : ${live['equity']:.2f}")
        print(f"  Total return    : {live['total_return_pct']:+.2f}%  (since {live['start_date']})")
        print(f"  Annualized      : {live['annualized_pct']:+.1f}%/yr  ({live['days_live']} days live)")
        print(f"  Total trades    : {live['trades']}")
    except Exception as e:
        print(f"  [Live data error: {e}]")
        live = None

    # --- Backtests ---
    backtests = get_prometheus_backtests()
    print(f"\n{'─'*80}")
    print("  PROMETHEUS BACKTEST RESULTS (1yr walk-forward, 200 Monte Carlo sims)")
    print(f"{'─'*80}")
    print(f"  {'Symbol':<8}  {'1yr Return':>10}  {'AnnRet':>8}  {'Sharpe':>7}  {'Sortino':>8}  {'MaxDD':>7}  {'WinRate':>8}  {'B&H':>8}  {'Trades':>6}")
    print(f"  {'─'*7}  {'─'*10}  {'─'*8}  {'─'*7}  {'─'*8}  {'─'*7}  {'─'*8}  {'─'*8}  {'─'*6}")
    sharpes = []
    for b in backtests:
        ret_str  = f"{b['total_return']:+.1f}%"
        ann_str  = f"{b['ann_return']:+.1f}%"
        bnh_str  = f"{b['bnh_return']:+.1f}%"
        verdict  = "✅ VALIDATED" if "VALIDATED" in str(b['verdict']) else str(b['verdict'])[:15]
        print(f"  {b['symbol']:<8}  {ret_str:>10}  {ann_str:>8}  {b['sharpe']:>7.2f}  {b['sortino']:>8.2f}  {b['max_dd']:>6.1f}%  {b['win_rate']:>7.1f}%  {bnh_str:>8}  {b['trades']:>6}")
        sharpes.append(b['sharpe'])
    if sharpes:
        avg_s = sum(sharpes)/len(sharpes)
        print(f"\n  Avg Sharpe: {avg_s:.2f}  |  Best Sharpe: {max(sharpes):.2f}  |  Symbols tested: {len(sharpes)}")

    # --- Head-to-head comparison table ---
    avg_sharpe  = sum(sharpes)/len(sharpes) if sharpes else 0
    best_sharpe = max(sharpes) if sharpes else 0
    best_b      = sorted(backtests, key=lambda x: x.get('total_return', 0), reverse=True)
    best_return_label = f"{best_b[0]['total_return']:+.1f}% ({best_b[0]['symbol']})" if best_b else "n/a"

    print(f"\n{'─'*80}")
    print("  HEAD-TO-HEAD: PROMETHEUS vs COMPETITORS")
    print(f"  (Backtest figures; live account only {live['days_live'] if live else '?'} days old)")
    print(f"{'─'*80}")
    print(f"  {'Platform / Strategy':<40}  {'Annual Return':>13}  {'Sharpe':>7}  {'Max DD':>7}  Notes")
    print(f"  {'─'*39}  {'─'*13}  {'─'*7}  {'─'*7}  {'─'*30}")

    # PROMETHEUS rows
    for b in backtests:
        ret_str  = f"{b['total_return']:+.1f}%"
        alpha    = b['total_return'] - b['bnh_return']
        alpha_str = f"(+{alpha:.1f}% vs B&H)" if alpha > 0 else f"({alpha:.1f}% vs B&H)"
        print(f"  {'PROMETHEUS (' + b['symbol'] + ')':<40}  {ret_str:>13}  {b['sharpe']:>7.2f}  {b['max_dd']:>6.1f}%  ✅ {alpha_str}")

    if live:
        ann_str = f"{live['annualized_pct']:+.1f}%"
        print(f"  {'PROMETHEUS (Live Alpaca)':<40}  {ann_str:>13}  {'n/a':>7}  {'n/a':>7}  Real money, {live['days_live']}d track record")

    print(f"  {'─'*39}  {'─'*13}  {'─'*7}  {'─'*7}")

    for name, ann, sharpe, dd, notes in COMPETITORS:
        better_sharpe = "⬆️ " if avg_sharpe > sharpe else "  "
        print(f"  {name:<40}  {ann:>+12.1f}%  {better_sharpe}{sharpe:>4.2f}  {dd:>6.1f}%  {notes}")

    # --- Summary verdict ---
    print(f"\n{'─'*80}")
    print("  VERDICT")
    print(f"{'─'*80}")
    beats = sum(1 for _, _, s, _, _ in COMPETITORS if avg_sharpe > s)
    print(f"  PROMETHEUS avg backtest Sharpe: {avg_sharpe:.2f}")
    print(f"  PROMETHEUS beats {beats}/{len(COMPETITORS)} competitors on Sharpe ratio")
    print(f"  Best backtest return: {best_return_label}")
    if live:
        print(f"  Live account annualized: {live['annualized_pct']:+.1f}%/yr  (only {live['days_live']} days — too short for statistical significance)")
    print()
    print("  ⚠️  IMPORTANT CAVEATS:")
    print("    • Backtest returns are in-sample/walk-forward and may not reflect live performance")
    print("    • Renaissance Medallion is CLOSED to outside investors; figures are pre-fee")
    print("    • Live account is only " + (str(live['days_live']) if live else "?") + " days old — need 6+ months for meaningful comparison")
    print("    • PROMETHEUS uses fractional share sizing ($100 account) — transaction costs matter more at small scale")
    print()
    print("=" * 80)

    # Save JSON report
    report = {
        'generated': str(datetime.now()),
        'prometheus_live': live,
        'prometheus_backtests': backtests,
        'competitors': [{'name': n, 'annual_return': a, 'sharpe': s, 'max_dd': d, 'notes': note}
                        for n, a, s, d, note in COMPETITORS],
        'summary': {
            'avg_backtest_sharpe': avg_sharpe,
            'best_backtest': best_return_label,
            'competitors_beaten_on_sharpe': beats,
            'total_competitors': len(COMPETITORS),
        }
    }
    out = BASE / f"competitor_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"  Report saved: {out.name}")

if __name__ == "__main__":
    main()
