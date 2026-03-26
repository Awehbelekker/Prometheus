"""
🧠 PROMETHEUS AI INTELLIGENCE & TRADING BENCHMARK
Comprehensive test of AI decision-making, signal quality, and trading performance
"""
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🧠 PROMETHEUS AI INTELLIGENCE & TRADING BENCHMARK")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# =============================================================================
# BENCHMARK 1: SIGNAL ACCURACY TEST
# =============================================================================
print("=" * 80)
print("📊 BENCHMARK 1: SIGNAL ACCURACY (Backtested)")
print("=" * 80)
print()

def test_signal_accuracy(symbol, period='1y'):
    """Test if our signals would have been profitable"""
    try:
        df = yf.download(symbol, period=period, progress=False)
        if len(df) < 50:
            return None
        
        # Calculate indicators (same as PROMETHEUS uses)
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['RSI'] = calculate_rsi(df['Close'], 14)
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['BB_Upper'] = df['SMA20'] + (df['Close'].rolling(20).std() * 2)
        df['BB_Lower'] = df['SMA20'] - (df['Close'].rolling(20).std() * 2)
        
        df = df.dropna()
        
        # Generate signals like PROMETHEUS
        signals = []
        for i in range(len(df) - 5):  # Leave 5 days for outcome
            row = df.iloc[i]
            score = 0
            
            # Uptrend (+1)
            if row['SMA20'] > row['SMA50']:
                score += 1
            
            # RSI oversold (+1)
            if row['RSI'] < 35:
                score += 1
            
            # MACD bullish (+1)
            if row['MACD'] > row['MACD_Signal']:
                score += 1
            
            # Near BB lower (+1)
            if row['Close'] < row['BB_Lower'] * 1.02:
                score += 1
            
            # Generate BUY signal if score >= 3
            if score >= 3:
                entry_price = float(row['Close'])
                future_price = float(df.iloc[i+5]['Close'])
                profit = (future_price / entry_price - 1) * 100
                signals.append({
                    'date': df.index[i],
                    'score': score,
                    'entry': entry_price,
                    'exit': future_price,
                    'profit': profit,
                    'win': profit > 0
                })
        
        if not signals:
            return None
        
        wins = sum(1 for s in signals if s['win'])
        total = len(signals)
        avg_profit = np.mean([s['profit'] for s in signals])
        
        return {
            'symbol': symbol,
            'signals': total,
            'wins': wins,
            'win_rate': wins / total * 100,
            'avg_profit': avg_profit
        }
    except:
        return None

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Test on key assets
test_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GLD', 'SPY', 'QQQ']
print(f"Testing signal accuracy on {len(test_symbols)} assets...")
print()

accuracy_results = []
for symbol in test_symbols:
    result = test_signal_accuracy(symbol)
    if result:
        accuracy_results.append(result)
        icon = "✅" if result['win_rate'] > 50 else "❌"
        print(f"{icon} {result['symbol']:<6} | Signals: {result['signals']:>3} | Win Rate: {result['win_rate']:>5.1f}% | Avg Profit: {result['avg_profit']:>+5.2f}%")

if accuracy_results:
    avg_win_rate = np.mean([r['win_rate'] for r in accuracy_results])
    avg_profit = np.mean([r['avg_profit'] for r in accuracy_results])
    print("-" * 60)
    print(f"📊 OVERALL | Win Rate: {avg_win_rate:.1f}% | Avg Profit: {avg_profit:+.2f}%")

# =============================================================================
# BENCHMARK 2: AI vs RANDOM TRADING
# =============================================================================
print()
print("=" * 80)
print("🎲 BENCHMARK 2: AI SIGNALS vs RANDOM TRADING")
print("=" * 80)
print()

def compare_ai_vs_random(symbol, num_trials=100):
    """Compare AI signal returns vs random entry returns"""
    try:
        df = yf.download(symbol, period='1y', progress=False)
        if len(df) < 100:
            return None
        
        returns = df['Close'].pct_change().dropna()
        
        # AI Strategy: Enter on RSI < 35, Exit after 5 days
        df['RSI'] = calculate_rsi(df['Close'], 14)
        ai_returns = []
        
        for i in range(50, len(df) - 5):
            if df['RSI'].iloc[i] < 35:
                ret = (df['Close'].iloc[i+5] / df['Close'].iloc[i] - 1) * 100
                ai_returns.append(float(ret))
        
        # Random Strategy: Random entries, 5 day hold
        np.random.seed(42)
        random_returns = []
        valid_indices = list(range(50, len(df) - 5))
        
        for _ in range(min(len(ai_returns) * 2, num_trials)):
            i = np.random.choice(valid_indices)
            ret = (df['Close'].iloc[i+5] / df['Close'].iloc[i] - 1) * 100
            random_returns.append(float(ret))
        
        if not ai_returns or not random_returns:
            return None
        
        return {
            'symbol': symbol,
            'ai_avg': np.mean(ai_returns),
            'ai_win_rate': sum(1 for r in ai_returns if r > 0) / len(ai_returns) * 100,
            'random_avg': np.mean(random_returns),
            'random_win_rate': sum(1 for r in random_returns if r > 0) / len(random_returns) * 100,
            'ai_trades': len(ai_returns),
            'random_trades': len(random_returns)
        }
    except:
        return None

print(f"{'Symbol':<8} {'AI Avg':<10} {'AI Win%':<10} {'Random Avg':<12} {'Random Win%':<12} {'Winner'}")
print("-" * 70)

ai_vs_random = []
for symbol in test_symbols:
    result = compare_ai_vs_random(symbol)
    if result:
        ai_vs_random.append(result)
        winner = "🤖 AI" if result['ai_avg'] > result['random_avg'] else "🎲 Random"
        print(f"{result['symbol']:<8} {result['ai_avg']:>+6.2f}%   {result['ai_win_rate']:>5.1f}%     {result['random_avg']:>+6.2f}%      {result['random_win_rate']:>5.1f}%       {winner}")

if ai_vs_random:
    ai_wins = sum(1 for r in ai_vs_random if r['ai_avg'] > r['random_avg'])
    print("-" * 70)
    print(f"🏆 AI beats Random in {ai_wins}/{len(ai_vs_random)} assets ({ai_wins/len(ai_vs_random)*100:.0f}%)")

# =============================================================================
# BENCHMARK 3: STRATEGY COMPARISON
# =============================================================================
print()
print("=" * 80)
print("📈 BENCHMARK 3: PROMETHEUS vs COMMON STRATEGIES (1 Year)")
print("=" * 80)
print()

def backtest_strategy(df, strategy):
    """Backtest different strategies"""
    df = df.copy()
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['RSI'] = calculate_rsi(df['Close'], 14)
    df = df.dropna()
    
    trades = []
    position = None
    
    for i in range(len(df) - 1):
        sma20_val = float(df['SMA20'].iloc[i])
        sma50_val = float(df['SMA50'].iloc[i])
        rsi_val = float(df['RSI'].iloc[i])
        close_val = float(df['Close'].iloc[i])
        
        if strategy == 'buy_hold':
            # Just track buy and hold
            if i == 0:
                return (float(df['Close'].iloc[-1]) / float(df['Close'].iloc[0]) - 1) * 100
        
        elif strategy == 'sma_cross':
            # SMA 20/50 crossover
            if position is None and sma20_val > sma50_val:
                position = close_val
            elif position is not None and sma20_val < sma50_val:
                trades.append((close_val / position - 1) * 100)
                position = None
        
        elif strategy == 'rsi_mean_revert':
            # Buy RSI < 30, Sell RSI > 70
            if position is None and rsi_val < 30:
                position = close_val
            elif position is not None and rsi_val > 70:
                trades.append((close_val / position - 1) * 100)
                position = None
        
        elif strategy == 'prometheus':
            # PROMETHEUS: Multi-indicator with trailing stop simulation
            score = 0
            if sma20_val > sma50_val:
                score += 1
            if rsi_val < 35:
                score += 1
            
            if position is None and score >= 2:
                position = close_val
                high_since_entry = position
            elif position is not None:
                high_since_entry = max(high_since_entry, close_val)
                current = close_val
                
                # Trailing stop at 1.5% below high
                if current < high_since_entry * 0.985:
                    trades.append((current / position - 1) * 100)
                    position = None
                # Take profit at 5%
                elif current > position * 1.05:
                    trades.append((current / position - 1) * 100)
                    position = None
    
    if trades:
        return sum(trades)
    return 0

# Test on SPY (market benchmark)
spy_df = yf.download('SPY', period='1y', progress=False)

strategies = {
    'Buy & Hold': 'buy_hold',
    'SMA Crossover': 'sma_cross',
    'RSI Mean Revert': 'rsi_mean_revert',
    'PROMETHEUS AI': 'prometheus'
}

print(f"{'Strategy':<20} {'Return':<12} {'vs Buy&Hold'}")
print("-" * 50)

strategy_results = {}
for name, strat in strategies.items():
    ret = backtest_strategy(spy_df, strat)
    strategy_results[name] = ret
    
buy_hold_ret = strategy_results['Buy & Hold']
for name, ret in sorted(strategy_results.items(), key=lambda x: x[1], reverse=True):
    diff = ret - buy_hold_ret
    icon = "🥇" if ret == max(strategy_results.values()) else "  "
    print(f"{icon} {name:<18} {ret:>+7.1f}%    {diff:>+7.1f}%")

# =============================================================================
# BENCHMARK 4: RISK-ADJUSTED PERFORMANCE
# =============================================================================
print()
print("=" * 80)
print("⚖️ BENCHMARK 4: RISK-ADJUSTED METRICS")
print("=" * 80)
print()

def calculate_risk_metrics(symbol):
    """Calculate comprehensive risk metrics"""
    try:
        df = yf.download(symbol, period='1y', progress=False)
        if len(df) < 50:
            return None
        
        returns = df['Close'].pct_change().dropna()
        
        total_return = float((df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100)
        volatility = float(returns.std()) * np.sqrt(252) * 100
        
        # Sharpe Ratio (assuming 5% risk-free rate)
        excess_return = float(returns.mean()) * 252 - 0.05
        sharpe = excess_return / (float(returns.std()) * np.sqrt(252)) if returns.std().item() > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside = returns[returns < 0]
        downside_std = float(downside.std()) * np.sqrt(252) if len(downside) > 0 else 0.01
        sortino = excess_return / downside_std if downside_std > 0 else 0
        
        # Max Drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative / rolling_max - 1)
        max_dd = float(drawdown.min()) * 100
        
        # Calmar Ratio
        calmar = total_return / abs(max_dd) if max_dd != 0 else 0
        
        return {
            'symbol': symbol,
            'return': total_return,
            'volatility': volatility,
            'sharpe': sharpe,
            'sortino': sortino,
            'max_dd': max_dd,
            'calmar': calmar
        }
    except:
        return None

risk_symbols = ['SPY', 'QQQ', 'GLD', 'NVDA', 'BTC-USD', 'TSLA']
print(f"{'Asset':<10} {'Return':<10} {'Vol':<10} {'Sharpe':<8} {'Sortino':<8} {'MaxDD':<10} {'Calmar'}")
print("-" * 75)

for symbol in risk_symbols:
    r = calculate_risk_metrics(symbol)
    if r:
        print(f"{r['symbol']:<10} {r['return']:>+6.1f}%   {r['volatility']:>6.1f}%   {r['sharpe']:>6.2f}   {r['sortino']:>6.2f}   {r['max_dd']:>7.1f}%   {r['calmar']:>5.2f}")

# =============================================================================
# BENCHMARK 5: AI LEARNING EFFECTIVENESS
# =============================================================================
print()
print("=" * 80)
print("🧠 BENCHMARK 5: AI LEARNING & PATTERN RECOGNITION")
print("=" * 80)
print()

import os
import json

# Check learned patterns
pattern_files = [f for f in os.listdir('.') if f.startswith('learned_patterns') and f.endswith('.json')]
pattern_files.sort(reverse=True)

if pattern_files:
    latest_patterns = pattern_files[0]
    with open(latest_patterns, 'r') as f:
        patterns = json.load(f)
    
    print(f"📚 Latest Pattern File: {latest_patterns}")
    print()
    
    total_patterns = 0
    for category, data in patterns.items():
        if isinstance(data, dict):
            count = len(data)
            total_patterns += count
            print(f"  {category}: {count} patterns")
    
    print("-" * 40)
    print(f"  TOTAL: {total_patterns} learned patterns")
else:
    print("❌ No learned patterns found")

# =============================================================================
# FINAL SCORECARD
# =============================================================================
print()
print("=" * 80)
print("🏆 PROMETHEUS AI FINAL SCORECARD")
print("=" * 80)
print()

# Calculate final scores
signal_score = avg_win_rate if accuracy_results else 50
ai_vs_random_score = (ai_wins / len(ai_vs_random) * 100) if ai_vs_random else 50
strategy_score = 75 if strategy_results.get('PROMETHEUS AI', 0) > 0 else 50
learning_score = min(100, total_patterns / 2) if pattern_files else 0

overall_score = (signal_score + ai_vs_random_score + strategy_score + learning_score) / 4

print(f"📊 Signal Accuracy Score:     {signal_score:.0f}/100")
print(f"🎲 AI vs Random Score:        {ai_vs_random_score:.0f}/100")
print(f"📈 Strategy Performance:      {strategy_score:.0f}/100")
print(f"🧠 Learning Patterns:         {learning_score:.0f}/100")
print()
print(f"{'=' * 40}")
print(f"🎯 OVERALL AI INTELLIGENCE:   {overall_score:.0f}/100")
print(f"{'=' * 40}")

if overall_score >= 70:
    print("\n✅ PROMETHEUS AI is performing WELL")
elif overall_score >= 50:
    print("\n⚠️ PROMETHEUS AI is AVERAGE - needs more learning")
else:
    print("\n❌ PROMETHEUS AI needs improvement")

print()
print("=" * 80)
print("✅ AI INTELLIGENCE BENCHMARK COMPLETE")
print("=" * 80)
