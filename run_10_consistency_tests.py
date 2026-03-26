#!/usr/bin/env python3
"""
PROMETHEUS V2 - 10 RUN CONSISTENCY TEST (3-WAY)
================================================
Run PROMETHEUS V2 ten times per strategy to demonstrate:
- Consistency of performance across Legacy, Kelly, and 60/40 Blend
- Risk management effectiveness
- Overall system reliability
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import time

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🚀 PROMETHEUS V2 - 10 RUN CONSISTENCY TEST (Legacy / Kelly / Blend)")
print("   Testing Performance Consistency & Improvements")
print("=" * 80)
print()

# Kelly Criterion integration
try:
    from advanced_risk_management import KellyPositionSizer, VolatilityScaler, DrawdownProtection
    KELLY_AVAILABLE = True
except ImportError:
    KELLY_AVAILABLE = False
    print("\u26a0\ufe0f Kelly module not found — running legacy-only")

class PrometheusV2Runner:
    """Optimized PROMETHEUS V2 for multiple runs"""
    
    def __init__(self, run_id, slight_variation=0, sizing_strategy='legacy'):
        self.run_id = run_id
        self.sizing_strategy = sizing_strategy  # 'legacy', 'kelly', or 'blend'
        self.initial_capital = 10000
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
        
        # Base parameters with slight variations per run
        self.parameters = {
            'min_confidence': 0.48 + (slight_variation * 0.02),  # 0.46-0.52
            'position_size_base': 0.12 + (slight_variation * 0.01),  # 0.11-0.14
            'max_positions': 6,
            'stop_loss_pct': 0.04 - (slight_variation * 0.005),  # 0.035-0.045
            'take_profit_pct': 0.12 + (slight_variation * 0.01),  # 0.11-0.14
            'time_exit_days': 15 + int(slight_variation * 3)  # 12-18
        }
        
        self.market_regime = 'neutral'
        self.win_streak = 0
        self.recent_trades = []
        self.high_water_mark = self.initial_capital
        
    def detect_market_regime(self, spy_data, current_idx):
        """Quick market regime detection"""
        if current_idx < 20:
            return 'neutral'
        
        current_price = spy_data.iloc[current_idx]['Close']
        price_20d_ago = spy_data.iloc[current_idx - 20]['Close']
        return_20d = (current_price - price_20d_ago) / price_20d_ago
        
        if return_20d > 0.05:
            return 'bull'
        elif return_20d < -0.05:
            return 'bear'
        else:
            return 'neutral'
    
    def calculate_dynamic_position_size(self, confidence=0.6, indicators=None):
        """Dynamic position sizing — supports legacy, kelly, or blend."""
        current_value = self.capital + sum(pos.get('current_value', 0) for pos in self.positions.values())
        if current_value > self.high_water_mark:
            self.high_water_mark = current_value
        
        drawdown = (self.high_water_mark - current_value) / self.high_water_mark

        # Legacy heuristic size
        base_size = self.parameters['position_size_base']
        
        # Market regime adjustment
        if self.market_regime == 'bull' and drawdown < 0.05:
            base_size *= 1.2
        elif self.market_regime == 'bear' or drawdown > 0.10:
            base_size *= 0.6
        
        # Recent performance adjustment
        if len(self.recent_trades) >= 5:
            recent_wins = sum(1 for t in self.recent_trades[-10:] if t.get('pnl', 0) > 0)
            win_rate = recent_wins / min(10, len(self.recent_trades))
            
            if win_rate > 0.7:
                base_size *= 1.1
            elif win_rate < 0.4:
                base_size *= 0.8
        
        legacy_size = max(0.03, min(0.20, base_size))

        if self.sizing_strategy == 'legacy' or not KELLY_AVAILABLE:
            return legacy_size

        # Kelly sizing
        kelly = KellyPositionSizer(fractional_kelly=0.25)
        vol_scaler = VolatilityScaler()
        dd_protect = DrawdownProtection(warning_level=0.10, emergency_level=0.13, max_drawdown=0.15)

        # Estimate win parameters from recent trades
        if len(self.recent_trades) >= 5:
            wins_list = [t['pnl'] for t in self.recent_trades if t.get('pnl', 0) > 0]
            loss_list = [abs(t['pnl']) for t in self.recent_trades if t.get('pnl', 0) < 0]
            total = len(self.recent_trades)
            wr = len(wins_list) / total if total else 0.55
            avg_w = np.mean(wins_list) if wins_list else 100
            avg_l = np.mean(loss_list) if loss_list else 100
        else:
            wr, avg_w, avg_l = 0.55, 100, 100

        kelly_dollars, _ = kelly.calculate_position_size(
            win_rate=max(wr, 0.40), avg_win=max(avg_w, 1), avg_loss=max(avg_l, 1),
            confidence=confidence, capital=current_value,
        )

        # VIX proxy (use indicator if available)
        sim_vix = indicators.get('sim_vix', 20) if indicators else 20
        vol_mult, _ = vol_scaler.get_volatility_multiplier(sim_vix)
        kelly_dollars *= vol_mult

        dd_mult, _ = dd_protect.get_drawdown_multiplier(abs(drawdown))
        kelly_dollars *= dd_mult

        kelly_size = kelly_dollars / current_value if current_value > 0 else 0.05
        kelly_size = max(0.01, min(0.15, kelly_size))

        if self.sizing_strategy == 'kelly':
            return kelly_size
        else:  # blend
            return 0.6 * legacy_size + 0.4 * kelly_size
    
    def generate_signal(self, symbol, data, idx):
        """Enhanced signal generation"""
        if idx < 15:
            return 'HOLD', 0.3
        
        current = data.iloc[idx]
        prev = data.iloc[idx-1]
        prev5 = data.iloc[idx-5]
        prev15 = data.iloc[idx-15]
        
        # Price changes
        change_1d = (current['Close'] - prev['Close']) / prev['Close']
        change_5d = (current['Close'] - prev5['Close']) / prev5['Close']
        change_15d = (current['Close'] - prev15['Close']) / prev15['Close']
        
        # Volume
        vol_ratio = current['Volume'] / prev['Volume'] if prev['Volume'] > 0 else 1
        
        # AI Systems simulation (streamlined)
        score = 0.5  # Base neutral
        
        # Trend following
        if change_15d > 0.03:
            score += 0.15
        elif change_15d < -0.03:
            score -= 0.15
        
        # Momentum
        if change_5d > 0.02 and change_1d > 0:
            score += 0.12
        elif change_5d < -0.02 and change_1d < 0:
            score -= 0.12
        
        # Volume confirmation
        if vol_ratio > 1.3:
            score += 0.08 * (1 if change_1d > 0 else -1)
        
        # Mean reversion
        if change_5d < -0.04 and change_1d > 0.005:
            if self.market_regime != 'bear':
                score += 0.20
        
        # Market regime adjustment
        if self.market_regime == 'bull':
            score += 0.05
        elif self.market_regime == 'bear':
            score -= 0.05
        
        # Convert to action
        if score > 0.60:
            return 'BUY', score
        elif score < 0.40:
            return 'SELL', 1 - score
        else:
            return 'HOLD', abs(score - 0.5) + 0.3
    
    def check_exits(self, symbol, current_price, days_held):
        """Check exit conditions"""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Dynamic take profit
        take_profit = self.parameters['take_profit_pct']
        if self.market_regime == 'bull':
            take_profit *= 1.2
        elif self.market_regime == 'bear':
            take_profit *= 0.8
        
        # Exit conditions
        if pnl_pct <= -self.parameters['stop_loss_pct']:
            return {'reason': 'Stop Loss', 'pnl_pct': pnl_pct}
        
        if pnl_pct >= take_profit:
            return {'reason': 'Take Profit', 'pnl_pct': pnl_pct}
        
        if days_held >= self.parameters['time_exit_days'] and pnl_pct < 0.02:
            return {'reason': 'Time Exit', 'pnl_pct': pnl_pct}
        
        # Trailing stop for big winners
        if pnl_pct > 0.08:
            high_water = pos.get('high_water', current_price)
            if current_price > high_water:
                pos['high_water'] = current_price
                high_water = current_price
            
            trail_stop = high_water * 0.94
            if current_price <= trail_stop:
                return {'reason': 'Trailing Stop', 'pnl_pct': pnl_pct}
        
        return None
    
    def run_single_test(self, all_data, test_days=300):
        """Run a single backtest"""
        # Reset
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
        self.recent_trades = []
        self.high_water_mark = self.initial_capital
        
        # Get SPY for market regime
        spy_data = all_data.get('SPY', pd.DataFrame())
        
        # Get common dates
        common_dates = None
        for symbol, data in all_data.items():
            if common_dates is None:
                common_dates = set(data.index)
            else:
                common_dates = common_dates.intersection(set(data.index))
        
        dates = sorted(list(common_dates))[-test_days:]  # Last N days
        
        wins = 0
        losses = 0
        
        position_days = {}  # Track days held
        
        for i, current_date in enumerate(dates[20:], 20):
            # Update market regime
            if not spy_data.empty and current_date in spy_data.index:
                spy_idx = list(spy_data.index).index(current_date)
                self.market_regime = self.detect_market_regime(spy_data, spy_idx)
            
            # Update position days
            for symbol in position_days:
                position_days[symbol] += 1
            
            # Check exits
            for symbol in list(self.positions.keys()):
                if symbol in all_data and current_date in all_data[symbol].index:
                    current_price = all_data[symbol].loc[current_date]['Close']
                    pos = self.positions[symbol]
                    pos['current_value'] = pos['quantity'] * current_price
                    
                    days_held = position_days.get(symbol, 0)
                    exit_info = self.check_exits(symbol, current_price, days_held)
                    
                    if exit_info:
                        # Execute exit
                        quantity = pos['quantity']
                        proceeds = quantity * current_price
                        cost = quantity * pos['entry_price']
                        pnl = proceeds - cost
                        
                        self.capital += proceeds
                        
                        # Track trade
                        trade_record = {
                            'symbol': symbol,
                            'pnl': pnl,
                            'reason': exit_info['reason'],
                            'days_held': days_held
                        }
                        
                        self.trades.append(trade_record)
                        self.recent_trades.append(trade_record)
                        
                        if pnl > 0:
                            wins += 1
                        else:
                            losses += 1
                        
                        del self.positions[symbol]
                        del position_days[symbol]
                        
                        # Keep recent trades manageable
                        if len(self.recent_trades) > 30:
                            self.recent_trades.pop(0)
            
            # Look for entries
            dynamic_pos_size = self.calculate_dynamic_position_size(confidence=0.6)
            
            if len(self.positions) < self.parameters['max_positions']:
                best_signals = []
                
                for symbol in all_data.keys():
                    if symbol in self.positions:
                        continue
                    
                    data = all_data[symbol]
                    if current_date not in data.index:
                        continue
                    
                    date_idx = list(data.index).index(current_date)
                    if date_idx < 20:
                        continue
                    
                    action, confidence = self.generate_signal(symbol, data, date_idx)
                    
                    if action == 'BUY' and confidence >= self.parameters['min_confidence']:
                        best_signals.append({
                            'symbol': symbol,
                            'confidence': confidence,
                            'price': data.loc[current_date]['Close']
                        })
                
                # Enter best positions
                best_signals.sort(key=lambda x: x['confidence'], reverse=True)
                
                for signal in best_signals[:self.parameters['max_positions'] - len(self.positions)]:
                    symbol = signal['symbol']
                    price = signal['price']
                    
                    position_value = self.capital * dynamic_pos_size
                    if position_value > 100:
                        quantity = position_value / price
                        cost = quantity * price
                        
                        if cost <= self.capital:
                            self.capital -= cost
                            self.positions[symbol] = {
                                'entry_price': price,
                                'quantity': quantity,
                                'current_value': quantity * price
                            }
                            
                            position_days[symbol] = 0
                            
                            self.trades.append({
                                'symbol': symbol,
                                'action': 'BUY',
                                'price': price
                            })
            
            # Track daily value
            position_value = sum(pos.get('current_value', 0) for pos in self.positions.values())
            total_value = self.capital + position_value
            self.daily_values.append({'date': current_date, 'value': total_value})
        
        # Calculate results
        final_value = self.capital + sum(pos.get('current_value', 0) for pos in self.positions.values())
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate Sharpe
        daily_returns = []
        for i in range(1, len(self.daily_values)):
            prev_val = self.daily_values[i-1]['value']
            curr_val = self.daily_values[i]['value']
            if prev_val > 0:
                daily_returns.append((curr_val - prev_val) / prev_val)
        
        sharpe = 0
        max_dd = 0
        if daily_returns:
            sharpe = np.mean(daily_returns) * np.sqrt(252) / (np.std(daily_returns) + 0.0001)
            
            # Max drawdown
            peak = self.initial_capital
            for day in self.daily_values:
                if day['value'] > peak:
                    peak = day['value']
                dd = (peak - day['value']) / peak
                max_dd = max(max_dd, dd)
        
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        return {
            'run_id': self.run_id,
            'final_value': final_value,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd * 100,
            'total_trades': len([t for t in self.trades if 'pnl' in t]),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate * 100,
            'parameters_used': dict(self.parameters)
        }

# ═══════════════════════════════════════════════════════════════════════════════
# RUN 10 TESTS PER STRATEGY (LEGACY / KELLY / BLEND)
# ═══════════════════════════════════════════════════════════════════════════════

print("📥 Loading market data for consistency tests...")

import yfinance as yf

# Get comprehensive data
end_date = datetime.now()
start_date = end_date - timedelta(days=500)  # 500 days of data

symbols = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN',
    'JPM', 'GS', 'BAC', 'WFC',
    'SPY', 'QQQ', 'XLF', 'XLE',
    'TSLA', 'GLD'
]

all_market_data = {}
for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        if len(hist) > 200:
            all_market_data[symbol] = hist
            print(f"  ✅ {symbol}: {len(hist)} days")
    except:
        print(f"  ⚠️ {symbol}: Failed to load")

if len(all_market_data) < 10:
    print("❌ Insufficient data for testing")
    exit(1)

strategies = ['legacy']
if KELLY_AVAILABLE:
    strategies += ['kelly', 'blend']

num_strategies = len(strategies)
total_runs = 10 * num_strategies

print(f"\n🚀 Running {total_runs} PROMETHEUS V2 tests ({num_strategies} strategies × 10 runs)...")
print("=" * 80)

all_results = {}  # strategy -> list of results

for strat in strategies:
    strat_label = strat.upper() if strat != 'blend' else 'BLEND (60/40)'
    print(f"\n── {strat_label} ──")
    all_results[strat] = []
    
    for run_num in range(1, 11):
        print(f"  🔄 {strat_label} Run {run_num}/10", end=" ")
        
        variation = (run_num - 5.5) / 10  # -0.45 to +0.45
        runner = PrometheusV2Runner(run_num, variation, sizing_strategy=strat)
        
        start_time = time.time()
        result = runner.run_single_test(all_market_data, test_days=250)
        elapsed = time.time() - start_time
        
        result['strategy'] = strat
        all_results[strat].append(result)
        
        print(f"✅ Return: {result['total_return_pct']:+5.1f}% | "
              f"Sharpe: {result['sharpe_ratio']:4.2f} | "
              f"DD: {result['max_drawdown']:4.1f}% | "
              f"WR: {result['win_rate']:4.1f}% | "
              f"({elapsed:.1f}s)")


# ═══════════════════════════════════════════════════════════════════════════════
# 3-WAY COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

def compute_stats(result_list):
    returns = [r['total_return_pct'] for r in result_list]
    sharpes = [r['sharpe_ratio'] for r in result_list]
    drawdowns = [r['max_drawdown'] for r in result_list]
    win_rates = [r['win_rate'] for r in result_list]
    trades = [r['total_trades'] for r in result_list]
    positive = sum(1 for r in returns if r > 0)
    cv = abs(np.std(returns) / np.mean(returns)) if np.mean(returns) != 0 else 999
    risk_adj = [r['total_return_pct'] / max(r['max_drawdown'], 1) for r in result_list]
    return {
        'avg_return': np.mean(returns), 'med_return': np.median(returns),
        'best_return': max(returns), 'worst_return': min(returns),
        'std_return': np.std(returns), 'cv': cv,
        'avg_sharpe': np.mean(sharpes), 'best_sharpe': max(sharpes), 'worst_sharpe': min(sharpes),
        'avg_dd': np.mean(drawdowns),
        'avg_wr': np.mean(win_rates), 'wr_min': min(win_rates), 'wr_max': max(win_rates),
        'avg_trades': np.mean(trades),
        'positive_runs': positive,
        'avg_risk_adj': np.mean(risk_adj),
    }


stat_map = {s: compute_stats(all_results[s]) for s in strategies}

print("\n" + "=" * 80)
print("📊 3-WAY CONSISTENCY COMPARISON  (10 runs each)")
print("=" * 80)

# Header
hdr = f"{'Metric':<28}"
for s in strategies:
    label = s.upper() if s != 'blend' else 'BLEND(60/40)'
    hdr += f"  {label:>14}"
print(hdr)
print("-" * (28 + 16 * len(strategies)))

rows = [
    ('Avg Return %',        'avg_return',  '+.2f', '%'),
    ('Median Return %',     'med_return',  '+.2f', '%'),
    ('Best Return %',       'best_return', '+.2f', '%'),
    ('Worst Return %',      'worst_return','+.2f', '%'),
    ('Std Deviation %',     'std_return',  '.2f',  '%'),
    ('Consistency (CV)',     'cv',          '.2f',  ''),
    ('Avg Sharpe',          'avg_sharpe',  '.2f',  ''),
    ('Best Sharpe',         'best_sharpe', '.2f',  ''),
    ('Worst Sharpe',        'worst_sharpe','.2f',  ''),
    ('Avg Max Drawdown %',  'avg_dd',      '.2f',  '%'),
    ('Avg Win Rate %',      'avg_wr',      '.1f',  '%'),
    ('Win Rate Range',      None,          None,   None),
    ('Avg Trades',          'avg_trades',  '.0f',  ''),
    ('Positive Runs',       'positive_runs','d',   '/10'),
    ('Return/DD Ratio',     'avg_risk_adj','.2f',  ''),
]

for label, key, fmt, suffix in rows:
    line = f"  {label:<26}"
    if key is None:
        # win rate range special
        for s in strategies:
            st = stat_map[s]
            val = f"{st['wr_min']:.1f}-{st['wr_max']:.1f}%"
            line += f"  {val:>14}"
    else:
        for s in strategies:
            v = stat_map[s][key]
            val = f"{v:{fmt}}{suffix}"
            line += f"  {val:>14}"
    print(line)

# Winner determination
print("\n" + "-" * 80)
metrics_better_higher = ['avg_return', 'avg_sharpe', 'positive_runs', 'avg_wr', 'avg_risk_adj']
metrics_better_lower  = ['avg_dd', 'cv']

wins = {s: 0 for s in strategies}
for m in metrics_better_higher:
    best_s = max(strategies, key=lambda s: stat_map[s][m])
    wins[best_s] += 1
for m in metrics_better_lower:
    best_s = min(strategies, key=lambda s: stat_map[s][m])
    wins[best_s] += 1

print("  SCORECARD (7 metrics):")
for s in strategies:
    label = s.upper() if s != 'blend' else 'BLEND(60/40)'
    bar = '█' * wins[s]
    print(f"    {label:<14} {wins[s]}/7 {bar}")

best_strategy = max(strategies, key=lambda s: wins[s])
best_label = best_strategy.upper() if best_strategy != 'blend' else 'BLEND(60/40)'
print(f"\n  🏆 WINNER: {best_label}")

# SPY benchmark
spy_data = all_market_data.get('SPY')
spy_return = None
if spy_data is not None and len(spy_data) >= 250:
    spy_start = spy_data.iloc[-250]['Close']
    spy_end = spy_data.iloc[-1]['Close']
    spy_return = (spy_end - spy_start) / spy_start * 100
    
    print(f"\n📈 vs S&P 500 ({spy_return:+.2f}% over 250 days):")
    for s in strategies:
        label = s.upper() if s != 'blend' else 'BLEND(60/40)'
        avg = stat_map[s]['avg_return']
        diff = avg - spy_return
        icon = '🏆' if diff > 0 else '  '
        print(f"  {icon} {label:<14} {avg:+.2f}% (outperformance: {diff:+.2f}%)")

# Overall assessment per strategy
print("\n📋 ASSESSMENT:")
for s in strategies:
    label = s.upper() if s != 'blend' else 'BLEND(60/40)'
    st = stat_map[s]
    pos = st['positive_runs']
    avg = st['avg_return']
    if pos >= 8 and avg > 5:
        grade = '🏆 EXCELLENT'
    elif pos >= 6 and avg > 0:
        grade = '✅ GOOD'
    else:
        grade = '⚠️ NEEDS IMPROVEMENT'
    print(f"  {label:<14} → {grade}  ({pos}/10 positive, avg {avg:+.1f}%)")

# Save comprehensive results
comprehensive_data = {
    'timestamp': datetime.now().isoformat(),
    'test_type': '10_run_consistency_test_3way',
    'system': 'PROMETHEUS_V2',
    'strategies': strategies,
    'winner': best_strategy,
    'scorecard': {s: wins[s] for s in strategies},
    'spy_return_250d': spy_return,
}

for s in strategies:
    comprehensive_data[f'{s}_summary'] = {
        'average_return_pct': float(stat_map[s]['avg_return']),
        'median_return_pct': float(stat_map[s]['med_return']),
        'return_std_dev': float(stat_map[s]['std_return']),
        'consistency_cv': float(stat_map[s]['cv']),
        'average_sharpe': float(stat_map[s]['avg_sharpe']),
        'average_max_drawdown': float(stat_map[s]['avg_dd']),
        'average_win_rate': float(stat_map[s]['avg_wr']),
        'positive_runs': int(stat_map[s]['positive_runs']),
        'avg_risk_adjusted': float(stat_map[s]['avg_risk_adj']),
    }
    comprehensive_data[f'{s}_individual'] = all_results[s]

filename = f'10_run_consistency_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(filename, 'w') as f:
    json.dump(comprehensive_data, f, indent=2, default=str)

print(f"\n💾 Complete results saved to: {filename}")

print("\n" + "=" * 80)
print("🚀 PROMETHEUS V2 - 3-WAY CONSISTENCY TEST COMPLETE!")
for s in strategies:
    label = s.upper() if s != 'blend' else 'BLEND(60/40)'
    st = stat_map[s]
    print(f"   {label}: {st['avg_return']:+.1f}% avg | {st['positive_runs']}/10 positive | Sharpe {st['avg_sharpe']:.2f}")
print(f"   🏆 Winner: {best_label}")
print("=" * 80)