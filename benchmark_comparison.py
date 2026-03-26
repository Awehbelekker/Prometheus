"""
PROMETHEUS vs Market Benchmarks Comparison
Compares PROMETHEUS backtest performance against major market indices,
top ETFs, mega-cap stocks, crypto, and famous funds over the same period.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# === PROMETHEUS RESULTS (from 120-day backtest) ===
PROMETHEUS_RETURN = -25.87  # %
PROMETHEUS_SHARPE = -1.96
PROMETHEUS_WIN_RATE = 43.7
PROMETHEUS_MAX_DD = -26.04  # %
PROMETHEUS_TRADES = 167

# === Period matching the backtest ===
end_date = datetime(2026, 2, 8)
start_date = end_date - timedelta(days=120)

print("=" * 80)
print("  PROMETHEUS vs TOP MARKET PLAYERS — 120-Day Comparison")
print(f"  Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print("=" * 80)

# === Download benchmark data ===
benchmarks = {
    # Major Indices
    'SPY': 'S&P 500 (Index)',
    'QQQ': 'NASDAQ 100 (Index)',
    'DIA': 'Dow Jones (Index)',
    'IWM': 'Russell 2000 (Small Cap)',
    # Mega-Cap Stocks
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google (Alphabet)',
    'NVDA': 'NVIDIA',
    'AMZN': 'Amazon',
    'META': 'Meta (Facebook)',
    'TSLA': 'Tesla',
    # Crypto
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    # Famous Funds & ETFs
    'ARKK': 'ARK Innovation (Cathie Wood)',
    'BRK-B': 'Berkshire Hathaway (Buffett)',
    'GLD': 'Gold ETF',
    'VOO': 'Vanguard S&P 500',
    'TQQQ': 'ProShares 3x NASDAQ (Leveraged)',
    'SOXL': 'Direxion 3x Semis (Leveraged)',
}

tickers = list(benchmarks.keys())
print("\nDownloading market data for", len(tickers), "benchmarks...")
data = yf.download(tickers, start=start_date, end=end_date, progress=False)

# Calculate returns, max drawdown, and Sharpe for each
results = []
closes = data['Close'] if 'Close' in data.columns.get_level_values(0) else data

for ticker in tickers:
    try:
        if ticker in closes.columns:
            series = closes[ticker].dropna()
            if len(series) < 10:
                continue
            ret = (series.iloc[-1] / series.iloc[0] - 1) * 100
            # Max drawdown
            cummax = series.cummax()
            drawdown = ((series - cummax) / cummax * 100).min()
            # Sharpe (annualized from daily returns)
            daily_ret = series.pct_change().dropna()
            sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252) if daily_ret.std() > 0 else 0
            results.append({
                'ticker': ticker,
                'name': benchmarks[ticker],
                'return': ret,
                'max_dd': drawdown,
                'sharpe': sharpe,
                'start_price': series.iloc[0],
                'end_price': series.iloc[-1],
            })
    except Exception as e:
        print(f"  Warning: Could not process {ticker}: {e}")

# Add PROMETHEUS
results.append({
    'ticker': 'PROMETHEUS',
    'name': '🤖 PROMETHEUS AI Trading',
    'return': PROMETHEUS_RETURN,
    'max_dd': PROMETHEUS_MAX_DD,
    'sharpe': PROMETHEUS_SHARPE,
    'start_price': 10000,
    'end_price': 7413,
})

# Sort by return
results.sort(key=lambda x: x['return'], reverse=True)

# Print results
print("\n" + "=" * 80)
print(f"  {'Rank':<5} {'Ticker':<10} {'Name':<30} {'Return':>8} {'MaxDD':>8} {'Sharpe':>7}")
print("-" * 80)

prometheus_rank = None
for i, r in enumerate(results):
    rank = i + 1
    marker = " ◄◄◄" if r['ticker'] == 'PROMETHEUS' else ""
    if r['ticker'] == 'PROMETHEUS':
        prometheus_rank = rank
        print(f"  {rank:<5} {r['ticker']:<10} {r['name']:<30} {r['return']:>+7.2f}% {r['max_dd']:>+7.2f}% {r['sharpe']:>+6.2f}{marker}")
    else:
        print(f"  {rank:<5} {r['ticker']:<10} {r['name']:<30} {r['return']:>+7.2f}% {r['max_dd']:>+7.2f}% {r['sharpe']:>+6.2f}{marker}")

total = len(results)
print("-" * 80)
print(f"\n  PROMETHEUS Rank: #{prometheus_rank} out of {total} benchmarks")

# Beat/lost comparison
beat = [r for r in results if r['return'] < PROMETHEUS_RETURN and r['ticker'] != 'PROMETHEUS']
lost_to = [r for r in results if r['return'] > PROMETHEUS_RETURN and r['ticker'] != 'PROMETHEUS']
tied = [r for r in results if abs(r['return'] - PROMETHEUS_RETURN) < 0.5 and r['ticker'] != 'PROMETHEUS']

print(f"  Beat: {len(beat)} benchmarks")
print(f"  Lost to: {len(lost_to)} benchmarks")

if beat:
    print(f"\n  ✅ PROMETHEUS beat:")
    for b in beat:
        print(f"     {b['ticker']:>10} ({b['name']}) by {PROMETHEUS_RETURN - b['return']:+.2f}pp")

# Compare against buy-and-hold SPY
spy_result = next((r for r in results if r['ticker'] == 'SPY'), None)
if spy_result:
    print(f"\n  📊 vs Buy-and-Hold SPY: PROMETHEUS {PROMETHEUS_RETURN - spy_result['return']:+.2f}pp")
    print(f"     SPY return: {spy_result['return']:+.2f}%  |  PROMETHEUS: {PROMETHEUS_RETURN:+.2f}%")

btc_result = next((r for r in results if r['ticker'] == 'BTC-USD'), None)
if btc_result:
    print(f"  📊 vs Buy-and-Hold BTC: PROMETHEUS {PROMETHEUS_RETURN - btc_result['return']:+.2f}pp")
    print(f"     BTC return: {btc_result['return']:+.2f}%  |  PROMETHEUS: {PROMETHEUS_RETURN:+.2f}%")

print("\n" + "=" * 80)
print("  NOTE: PROMETHEUS trades actively (167 trades) vs passive buy-and-hold.")
print("  The 120-day period (Oct 2025 - Feb 2026) is a single snapshot.")
print("  Longer backtests show different relative performance.")
print("=" * 80)

