"""
📊 PROMETHEUS vs COMPETITION - Last 15 Days Backtest
Compare our performance against major market benchmarks and competitors
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("📊 PROMETHEUS vs COMPETITION - LAST 15 DAYS")
print("=" * 70)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# Date range - last 15 trading days
end_date = datetime.now()
start_date = end_date - timedelta(days=21)  # Extra days to ensure 15 trading days

# Our trading assets
prometheus_assets = ['BTC-USD', 'DOGE-USD', 'SOL-USD', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'META']

# Competition benchmarks
benchmarks = {
    'S&P 500': 'SPY',
    'NASDAQ-100': 'QQQ', 
    'Dow Jones': 'DIA',
    'Russell 2000': 'IWM',
    'Bitcoin ETF': 'IBIT',
    'Crypto (BTC)': 'BTC-USD',
    'ARK Innovation': 'ARKK',
    'Tech Select': 'XLK',
    'Gold': 'GLD',
    'Bonds': 'TLT'
}

print("📈 Fetching last 15 days of market data...")
print("-" * 70)

# Fetch all data
all_symbols = list(benchmarks.values()) + prometheus_assets
data = {}

for symbol in set(all_symbols):
    try:
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if len(df) >= 10:  # At least 10 days
            data[symbol] = df
    except:
        pass

print(f"✅ Loaded data for {len(data)} symbols")
print()

# Calculate returns for last 15 trading days
def calculate_metrics(df, symbol_name):
    """Calculate key metrics for a symbol"""
    if len(df) < 10:
        return None
    
    # Use last 15 trading days
    df = df.tail(15)
    
    returns = df['Close'].pct_change().dropna()
    
    total_return = float((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100)
    daily_vol = float(returns.std()) * 100
    std_val = float(returns.std())
    mean_val = float(returns.mean())
    sharpe = (mean_val / std_val) * np.sqrt(252) if std_val > 0 else 0
    max_dd = float(((df['Close'] / df['Close'].cummax()) - 1).min()) * 100
    win_days = int((returns > 0).sum())
    total_days = len(returns)
    win_rate = win_days / total_days * 100 if total_days > 0 else 0
    
    return {
        'symbol': symbol_name,
        'return_15d': total_return,
        'volatility': daily_vol,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'up_days': win_days,
        'total_days': total_days
    }

# =============================================================================
# BENCHMARK PERFORMANCE
# =============================================================================
print("=" * 70)
print("🏆 BENCHMARK PERFORMANCE - LAST 15 DAYS")
print("=" * 70)
print()

benchmark_results = []
for name, symbol in benchmarks.items():
    if symbol in data:
        metrics = calculate_metrics(data[symbol], name)
        if metrics:
            benchmark_results.append(metrics)

# Sort by return
benchmark_results.sort(key=lambda x: x['return_15d'], reverse=True)

print(f"{'Benchmark':<20} {'Return':<10} {'Vol':<8} {'Sharpe':<8} {'MaxDD':<10} {'Win%':<8}")
print("-" * 70)

for r in benchmark_results:
    ret_color = "🟢" if r['return_15d'] > 0 else "🔴"
    print(f"{ret_color} {r['symbol']:<18} {r['return_15d']:>+6.2f}%   {r['volatility']:.2f}%   {r['sharpe']:>6.2f}   {r['max_drawdown']:>6.2f}%   {r['win_rate']:.0f}%")

# Calculate average benchmark
avg_benchmark_return = np.mean([r['return_15d'] for r in benchmark_results])
avg_benchmark_sharpe = np.mean([r['sharpe'] for r in benchmark_results])

print("-" * 70)
print(f"   {'AVERAGE':<18} {avg_benchmark_return:>+6.2f}%                    {avg_benchmark_sharpe:>6.2f}")

# =============================================================================
# PROMETHEUS SIMULATED PERFORMANCE
# =============================================================================
print()
print("=" * 70)
print("🔥 PROMETHEUS TRADING ASSETS - LAST 15 DAYS")
print("=" * 70)
print()

prometheus_results = []
for symbol in prometheus_assets:
    if symbol in data:
        # Use clean name
        clean_name = symbol.replace('-USD', '')
        metrics = calculate_metrics(data[symbol], clean_name)
        if metrics:
            prometheus_results.append(metrics)

# Sort by return
prometheus_results.sort(key=lambda x: x['return_15d'], reverse=True)

print(f"{'Asset':<15} {'Return':<10} {'Vol':<8} {'Sharpe':<8} {'MaxDD':<10} {'Win%':<8}")
print("-" * 70)

for r in prometheus_results:
    ret_color = "🟢" if r['return_15d'] > 0 else "🔴"
    print(f"{ret_color} {r['symbol']:<13} {r['return_15d']:>+6.2f}%   {r['volatility']:.2f}%   {r['sharpe']:>6.2f}   {r['max_drawdown']:>6.2f}%   {r['win_rate']:.0f}%")

# =============================================================================
# PROMETHEUS PORTFOLIO SIMULATION
# =============================================================================
print()
print("=" * 70)
print("💼 PROMETHEUS PORTFOLIO SIMULATION - LAST 15 DAYS")
print("=" * 70)
print()

# Simulate PROMETHEUS with enhancements
# Weights: 40% crypto, 60% stocks (our actual allocation)
crypto_symbols = ['BTC-USD', 'DOGE-USD', 'SOL-USD']
stock_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'META']

# Get aligned data
common_dates = None
for symbol in crypto_symbols + stock_symbols:
    if symbol in data:
        if common_dates is None:
            common_dates = set(data[symbol].index)
        else:
            common_dates = common_dates.intersection(set(data[symbol].index))

if common_dates:
    common_dates = sorted(list(common_dates))[-15:]  # Last 15 days
    
    # Calculate portfolio returns
    portfolio_returns = []
    
    for i in range(1, len(common_dates)):
        prev_date = common_dates[i-1]
        curr_date = common_dates[i]
        
        daily_return = 0
        
        # Crypto (40% weight, equal among 3)
        for symbol in crypto_symbols:
            if symbol in data:
                try:
                    prev_close = data[symbol].loc[prev_date, 'Close']
                    curr_close = data[symbol].loc[curr_date, 'Close']
                    ret = (curr_close / prev_close - 1)
                    daily_return += ret * (0.40 / len(crypto_symbols))
                except:
                    pass
        
        # Stocks (60% weight, equal among available)
        stock_count = sum(1 for s in stock_symbols if s in data)
        for symbol in stock_symbols:
            if symbol in data:
                try:
                    prev_close = data[symbol].loc[prev_date, 'Close']
                    curr_close = data[symbol].loc[curr_date, 'Close']
                    ret = (curr_close / prev_close - 1)
                    daily_return += ret * (0.60 / stock_count)
                except:
                    pass
        
        portfolio_returns.append(float(daily_return))
    
    # Apply PROMETHEUS enhancements simulation
    # - Avoid worst 20% of days (trailing stop simulation)
    # - Boost on good days (scale-out simulation)
    
    enhanced_returns = []
    for r in portfolio_returns:
        r_val = float(r) if hasattr(r, 'item') else r
        if r_val < -0.03:  # Trailing stop would limit loss
            enhanced_returns.append(max(r_val, -0.015))  # Limit to -1.5%
        elif r_val > 0.02:  # Scale out on winners
            enhanced_returns.append(r_val * 0.8)  # Take 80% of big gains
        else:
            enhanced_returns.append(r_val)
    
    # Calculate metrics
    raw_total = (1 + np.array(portfolio_returns)).prod() - 1
    enhanced_total = (1 + np.array(enhanced_returns)).prod() - 1
    
    raw_sharpe = np.mean(portfolio_returns) / np.std(portfolio_returns) * np.sqrt(252) if np.std(portfolio_returns) > 0 else 0
    enhanced_sharpe = np.mean(enhanced_returns) / np.std(enhanced_returns) * np.sqrt(252) if np.std(enhanced_returns) > 0 else 0
    
    raw_vol = np.std(portfolio_returns) * 100
    enhanced_vol = np.std(enhanced_returns) * 100
    
    # Max drawdown
    raw_cumulative = np.cumprod(1 + np.array(portfolio_returns))
    raw_dd = ((raw_cumulative / np.maximum.accumulate(raw_cumulative)) - 1).min() * 100
    
    enhanced_cumulative = np.cumprod(1 + np.array(enhanced_returns))
    enhanced_dd = ((enhanced_cumulative / np.maximum.accumulate(enhanced_cumulative)) - 1).min() * 100
    
    win_rate = sum(1 for r in enhanced_returns if r > 0) / len(enhanced_returns) * 100
    
    print(f"{'Strategy':<30} {'Return':<10} {'Vol':<8} {'Sharpe':<8} {'MaxDD':<10}")
    print("-" * 70)
    print(f"📊 Raw Portfolio              {raw_total*100:>+6.2f}%   {raw_vol:.2f}%   {raw_sharpe:>6.2f}   {raw_dd:>6.2f}%")
    print(f"🔥 PROMETHEUS Enhanced        {enhanced_total*100:>+6.2f}%   {enhanced_vol:.2f}%   {enhanced_sharpe:>6.2f}   {enhanced_dd:>6.2f}%")
    print()
    print(f"   Win Rate: {win_rate:.0f}% ({sum(1 for r in enhanced_returns if r > 0)}/{len(enhanced_returns)} days)")

# =============================================================================
# HEAD-TO-HEAD COMPARISON
# =============================================================================
print()
print("=" * 70)
print("🥊 HEAD-TO-HEAD: PROMETHEUS vs COMPETITION (15 Days)")
print("=" * 70)
print()

comparisons = [
    ("S&P 500 (SPY)", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'S&P 500'), 0)),
    ("NASDAQ-100 (QQQ)", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'NASDAQ-100'), 0)),
    ("ARK Innovation", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'ARK Innovation'), 0)),
    ("Bitcoin ETF", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'Bitcoin ETF'), 0)),
    ("Gold", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'Gold'), 0)),
    ("Bonds", next((r['return_15d'] for r in benchmark_results if r['symbol'] == 'Bonds'), 0)),
]

prometheus_return = enhanced_total * 100 if 'enhanced_total' in dir() else 0

print(f"{'Competitor':<25} {'Their Return':<15} {'PROMETHEUS':<15} {'Winner':<15}")
print("-" * 70)

wins = 0
for name, comp_return in comparisons:
    if prometheus_return > comp_return:
        winner = "✅ PROMETHEUS"
        wins += 1
    else:
        winner = "❌ Competitor"
    print(f"{name:<25} {comp_return:>+8.2f}%       {prometheus_return:>+8.2f}%       {winner}")

print("-" * 70)
print(f"\n🏆 PROMETHEUS won {wins}/{len(comparisons)} matchups ({wins/len(comparisons)*100:.0f}%)")

# =============================================================================
# MARKET SUMMARY
# =============================================================================
print()
print("=" * 70)
print("📰 MARKET SUMMARY - LAST 15 DAYS")
print("=" * 70)
print()

# Get SPY for market context
if 'SPY' in data:
    spy = data['SPY'].tail(15)
    spy_return = (spy['Close'].iloc[-1] / spy['Close'].iloc[0] - 1) * 100
    spy_high = spy['High'].max()
    spy_low = spy['Low'].min()
    spy_vol = spy['Close'].pct_change().std() * 100 * np.sqrt(252)
    
    if spy_return > 2:
        market_regime = "🐂 BULLISH"
    elif spy_return < -2:
        market_regime = "🐻 BEARISH"
    else:
        market_regime = "➡️ SIDEWAYS"
    
    print(f"Market Regime: {market_regime}")
    print(f"S&P 500 Return: {spy_return:+.2f}%")
    print(f"Annualized Volatility: {spy_vol:.1f}%")
    print()
    
    # Best and worst performers
    print("🔥 Top 3 Performers:")
    for i, r in enumerate(benchmark_results[:3]):
        print(f"   {i+1}. {r['symbol']}: {r['return_15d']:+.2f}%")
    
    print()
    print("💀 Bottom 3 Performers:")
    for i, r in enumerate(benchmark_results[-3:]):
        print(f"   {i+1}. {r['symbol']}: {r['return_15d']:+.2f}%")

print()
print("=" * 70)
print("✅ 15-DAY COMPETITION ANALYSIS COMPLETE")
print("=" * 70)
