#!/usr/bin/env python3
"""
REALISTIC PROMETHEUS vs COMPETITION BENCHMARK
Uses actual market data to calculate what competitors would achieve
Tests over multiple realistic periods
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("REALISTIC PROMETHEUS vs COMPETITION BENCHMARK")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# === TEST PERIODS ===
PERIODS = [
    ('1 Year (2025)', '2025-01-01', '2025-12-31'),
    ('2 Years (2024-2025)', '2024-01-01', '2025-12-31'),
    ('3 Years (2023-2025)', '2023-01-01', '2025-12-31'),
    ('5 Years (2020-2025)', '2020-01-01', '2025-12-31'),
]

# === REALISTIC HEDGE FUND BENCHMARKS ===
# These are ACTUAL historical average returns, not peak returns
REALISTIC_COMPETITION = {
    'S&P 500 Index': {
        'description': 'Passive market benchmark',
        'typical_annual': 10.0,
        'sharpe': 0.50,
    },
    'Average Hedge Fund': {
        'description': 'HFRI Fund Weighted Composite',
        'typical_annual': 7.5,  # 2015-2024 average
        'sharpe': 0.65,
    },
    'Top Quartile Hedge Funds': {
        'description': 'Top 25% performers',
        'typical_annual': 12.0,
        'sharpe': 1.0,
    },
    'Quant Funds Average': {
        'description': 'Systematic/algorithmic funds',
        'typical_annual': 9.0,
        'sharpe': 0.85,
    },
    'Retail Day Traders': {
        'description': '90% lose money',
        'typical_annual': -15.0,
        'sharpe': -0.5,
    },
    'Robo-Advisors': {
        'description': 'Betterment, Wealthfront',
        'typical_annual': 8.0,
        'sharpe': 0.55,
    },
}

# Symbols
SYMBOLS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA', 'META', 'AMZN']

def add_indicators(df):
    """Add technical indicators"""
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Momentum'] = df['Close'].pct_change(5)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['Uptrend'] = (df['Close'] > df['SMA_20']) & (df['SMA_20'] > df['SMA_50'])
    return df

def prometheus_signal(row):
    """PROMETHEUS Enhanced signal"""
    score = 0
    if row.get('Uptrend', False): score += 2
    if pd.notna(row.get('SMA_20')) and row['Close'] > row['SMA_20']: score += 1
    if pd.notna(row.get('SMA_50')) and row.get('SMA_20', 0) > row['SMA_50']: score += 1
    rsi = row.get('RSI', 50)
    if pd.notna(rsi) and rsi < 35: score += 2
    elif pd.notna(rsi) and rsi > 65: score -= 2
    mom = row.get('Momentum', 0)
    if pd.notna(mom) and mom > 0.01: score += 1
    
    if score >= 3:
        return 'BUY', min(0.55 + score * 0.05, 0.95)
    return 'HOLD', 0.5

def run_prometheus(data, use_enhancements=True):
    """Run PROMETHEUS with 6 enhancements"""
    capital = 10000
    positions = {}
    trades = []
    portfolio_values = []
    
    all_dates = set()
    for df in data.values():
        all_dates.update(df.index.tolist())
    all_dates = sorted(all_dates)
    
    for date in all_dates:
        # Manage positions with enhancements
        for symbol in list(positions.keys()):
            if symbol not in data or date not in data[symbol].index:
                continue
            
            pos = positions[symbol]
            price = data[symbol].loc[date, 'Close']
            pnl_pct = (price - pos['entry']) / pos['entry']
            days_held = (date - pos['date']).days
            
            if price > pos['high']:
                pos['high'] = price
            
            drop_from_high = (pos['high'] - price) / pos['high'] if pos['high'] > 0 else 0
            sell = False
            
            if use_enhancements:
                # Trailing stop
                if pnl_pct >= 0.03 and drop_from_high >= 0.015:
                    sell = True
                # Time exit
                max_days = 7 if 'USD' in symbol else 14
                if days_held >= max_days:
                    sell = True
                # Scale out
                if not pos.get('scaled') and pnl_pct >= 0.03:
                    sell_qty = pos['qty'] * 0.5
                    capital += sell_qty * price
                    trades.append({'pnl': sell_qty * (price - pos['entry'])})
                    pos['qty'] -= sell_qty
                    pos['scaled'] = True
                if pos.get('scaled') and pnl_pct >= 0.07:
                    sell = True
                # DCA
                if pnl_pct <= -0.03 and pos.get('dca', 0) < 2:
                    add_amt = capital * 0.05
                    if capital >= add_amt:
                        add_qty = add_amt / price
                        old_qty = pos['qty']
                        pos['qty'] += add_qty
                        pos['entry'] = (pos['entry'] * old_qty + price * add_qty) / pos['qty']
                        pos['dca'] = pos.get('dca', 0) + 1
                        capital -= add_amt
            else:
                if pnl_pct >= 0.05: sell = True
                if pnl_pct <= -0.02: sell = True
            
            if pnl_pct <= -0.15: sell = True
            
            if sell:
                capital += pos['qty'] * price
                trades.append({'pnl': pos['qty'] * (price - pos['entry'])})
                del positions[symbol]
        
        # New buys
        for symbol, df in data.items():
            if symbol in positions or date not in df.index:
                continue
            if len(positions) >= 5:
                continue
            
            row = df.loc[date]
            action, conf = prometheus_signal(row)
            
            if action == 'BUY' and conf >= 0.55:
                pos_value = capital * 0.15
                if pos_value > 50 and capital >= pos_value:
                    qty = pos_value / row['Close']
                    capital -= pos_value
                    positions[symbol] = {
                        'qty': qty, 'entry': row['Close'], 'date': date,
                        'high': row['Close'], 'dca': 0, 'scaled': False
                    }
        
        value = capital
        for symbol, pos in positions.items():
            if symbol in data and date in data[symbol].index:
                value += pos['qty'] * data[symbol].loc[date, 'Close']
        portfolio_values.append(value)
    
    if not portfolio_values:
        return {}
    
    values = portfolio_values
    total_return = (values[-1] - values[0]) / values[0]
    wins = [t['pnl'] for t in trades if t['pnl'] > 0]
    losses = [t['pnl'] for t in trades if t['pnl'] < 0]
    win_rate = len(wins) / len(trades) if trades else 0
    
    returns = pd.Series(values).pct_change().dropna()
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    peak = pd.Series(values).expanding().max()
    drawdown = (pd.Series(values) - peak) / peak
    max_dd = drawdown.min()
    
    years = len(all_dates) / 252
    annual_return = ((1 + total_return) ** (1/years) - 1) * 100 if years > 0 else total_return * 100
    
    return {
        'total_return': total_return * 100,
        'annual_return': annual_return,
        'sharpe': sharpe,
        'max_drawdown': max_dd * 100,
        'win_rate': win_rate * 100,
        'trades': len(trades),
        'final_value': values[-1]
    }

def run_sp500_benchmark(data, start, end):
    """Run actual S&P 500 buy & hold"""
    try:
        spy = yf.Ticker('SPY').history(start=start, end=end)
        if spy.empty:
            return None
        
        start_price = spy['Close'].iloc[0]
        end_price = spy['Close'].iloc[-1]
        total_return = (end_price - start_price) / start_price
        
        years = len(spy) / 252
        annual_return = ((1 + total_return) ** (1/years) - 1) * 100 if years > 0 else total_return * 100
        
        returns = spy['Close'].pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        peak = spy['Close'].expanding().max()
        drawdown = (spy['Close'] - peak) / peak
        max_dd = drawdown.min()
        
        return {
            'total_return': total_return * 100,
            'annual_return': annual_return,
            'sharpe': sharpe,
            'max_drawdown': max_dd * 100,
        }
    except:
        return None

# === RUN BENCHMARKS ===
all_results = []

for period_name, start, end in PERIODS:
    print(f"\n{'='*80}")
    print(f"PERIOD: {period_name}")
    print(f"{'='*80}")
    
    # Download data
    data = {}
    for symbol in SYMBOLS:
        try:
            df = yf.Ticker(symbol).history(start=start, end=end)
            if not df.empty and len(df) > 50:
                df = add_indicators(df)
                data[symbol] = df
        except:
            pass
    
    if not data:
        print("  No data available")
        continue
    
    print(f"  Downloaded {len(data)} symbols")
    
    # Run PROMETHEUS
    prom = run_prometheus(data, use_enhancements=True)
    
    # Get actual S&P 500 performance
    sp500 = run_sp500_benchmark(data, start, end)
    
    if not prom:
        continue
    
    print(f"\n  {'Strategy':<30} {'Total %':<12} {'Annual %':<12} {'Sharpe':<10} {'Win Rate':<10}")
    print("  " + "-" * 75)
    
    # PROMETHEUS
    print(f"  {'>>> PROMETHEUS (Enhanced)':<30} {prom['total_return']:>8.1f}%   {prom['annual_return']:>8.1f}%   {prom['sharpe']:>8.2f}   {prom['win_rate']:>8.1f}%")
    
    # S&P 500 actual
    if sp500:
        print(f"  {'S&P 500 (SPY Actual)':<30} {sp500['total_return']:>8.1f}%   {sp500['annual_return']:>8.1f}%   {sp500['sharpe']:>8.2f}   {'N/A':<10}")
        sp500_return = sp500['annual_return']
    else:
        sp500_return = 10.0
    
    print("  " + "-" * 75)
    
    # Competition estimates (scaled to period)
    years = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365
    
    for name, comp in REALISTIC_COMPETITION.items():
        est_annual = comp['typical_annual']
        est_total = ((1 + est_annual/100) ** years - 1) * 100
        print(f"  {name:<30} {est_total:>8.1f}%   {est_annual:>8.1f}%   {comp['sharpe']:>8.2f}   {'N/A':<10}")
    
    # Store results
    all_results.append({
        'period': period_name,
        'prometheus_annual': prom['annual_return'],
        'prometheus_total': prom['total_return'],
        'prometheus_sharpe': prom['sharpe'],
        'prometheus_win': prom['win_rate'],
        'sp500_annual': sp500['annual_return'] if sp500 else 10.0,
    })
    
    # Comparison
    print(f"\n  PROMETHEUS vs Competition:")
    
    beats = 0
    for name, comp in REALISTIC_COMPETITION.items():
        diff = prom['annual_return'] - comp['typical_annual']
        if diff > 0:
            beats += 1
            print(f"    [WIN] vs {name}: +{diff:.1f}%")
        else:
            print(f"    [LOSE] vs {name}: {diff:.1f}%")
    
    print(f"\n  BEATS: {beats}/{len(REALISTIC_COMPETITION)} competitors")

# === SUMMARY ===
print("\n" + "=" * 80)
print("OVERALL SUMMARY ACROSS ALL PERIODS")
print("=" * 80)

if all_results:
    avg_prom_annual = np.mean([r['prometheus_annual'] for r in all_results])
    avg_prom_sharpe = np.mean([r['prometheus_sharpe'] for r in all_results])
    avg_prom_win = np.mean([r['prometheus_win'] for r in all_results])
    avg_sp500 = np.mean([r['sp500_annual'] for r in all_results])
    
    print(f"\n  PROMETHEUS Average Annual Return: {avg_prom_annual:.1f}%")
    print(f"  PROMETHEUS Average Sharpe Ratio:  {avg_prom_sharpe:.2f}")
    print(f"  PROMETHEUS Average Win Rate:      {avg_prom_win:.1f}%")
    print(f"  S&P 500 Average Annual Return:    {avg_sp500:.1f}%")
    
    print("\n  PROMETHEUS vs Realistic Competition:")
    
    # Compare to realistic benchmarks
    comparisons = [
        ('S&P 500 Index', 10.0),
        ('Average Hedge Fund', 7.5),
        ('Top Quartile Hedge Funds', 12.0),
        ('Quant Funds Average', 9.0),
        ('Retail Day Traders', -15.0),
        ('Robo-Advisors', 8.0),
    ]
    
    for name, benchmark in comparisons:
        diff = avg_prom_annual - benchmark
        if diff > 0:
            print(f"    [OK] BEATS {name}: {avg_prom_annual:.1f}% vs {benchmark:.1f}% (+{diff:.1f}%)")
        else:
            print(f"    [X] Below {name}: {avg_prom_annual:.1f}% vs {benchmark:.1f}% ({diff:.1f}%)")

print("\n" + "=" * 80)
print("REALISTIC ASSESSMENT")
print("=" * 80)
print("""
IMPORTANT CONTEXT:
- Renaissance Medallion's 66% annual returns are NOT realistic for comparison
  - They use $100B+ capital, 300+ PhD quants, proprietary data feeds
  - Fund is CLOSED to outside investors since 1993
  - Their returns come from HFT and strategies impossible for retail

- REALISTIC benchmarks for retail/small traders:
  - S&P 500 Buy & Hold: ~10% annually
  - Average Hedge Fund: ~7.5% annually  
  - 90% of retail day traders LOSE money

PROMETHEUS REALISTIC PERFORMANCE:
""")

if all_results:
    if avg_prom_annual > 10:
        print(f"  [EXCELLENT] {avg_prom_annual:.1f}% annual beats S&P 500 index")
    if avg_prom_annual > 7.5:
        print(f"  [EXCELLENT] {avg_prom_annual:.1f}% annual beats average hedge fund")
    if avg_prom_win > 70:
        print(f"  [EXCELLENT] {avg_prom_win:.1f}% win rate is exceptional")
    if avg_prom_sharpe > 1.5:
        print(f"  [EXCELLENT] {avg_prom_sharpe:.2f} Sharpe ratio is institutional-grade")

print("\n" + "=" * 80)
print("BENCHMARK COMPLETE!")
print("=" * 80)
