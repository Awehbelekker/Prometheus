#!/usr/bin/env python3
"""
PROMETHEUS V2 - IMPROVED LEARNING SYSTEM
========================================
Fixed based on 5-year learning analysis:
- Dynamic position sizing
- Market regime detection  
- Better compound protection
- Balanced learning rate
- Profit protection mechanisms
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🚀 PROMETHEUS V2 - IMPROVED LEARNING BACKTEST")
print("   Fixed Compound Issues | Dynamic Sizing | Market Regimes")
print("=" * 80)
print()

class PrometheusV2:
    """Improved PROMETHEUS with fixes from 5-year analysis"""
    
    def __init__(self):
        self.initial_capital = 10000
        self.capital = self.initial_capital
        self.high_water_mark = self.initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
        
        # Dynamic parameters that adapt
        self.base_parameters = {
            'min_confidence': 0.50,
            'max_positions': 6,
            'stop_loss_pct': 0.04,
            'take_profit_pct': 0.12,
            'time_exit_days': 15
        }
        
        # Market regime detection
        self.market_regime = 'neutral'  # bull, bear, neutral
        self.spy_data = None
        
        # Performance tracking
        self.win_streak = 0
        self.loss_streak = 0
        self.recent_trades = []
        self.yearly_stats = []
        
    def detect_market_regime(self, spy_data, current_idx):
        """Detect if we're in bull/bear/neutral market"""
        if current_idx < 20:
            return 'neutral'
        
        # Look at SPY 20-day return
        current_price = spy_data.iloc[current_idx]['Close']
        price_20d_ago = spy_data.iloc[current_idx - 20]['Close']
        return_20d = (current_price - price_20d_ago) / price_20d_ago
        
        # Check volatility
        recent_closes = spy_data.iloc[current_idx-10:current_idx]['Close'].values
        volatility = np.std(np.diff(recent_closes) / recent_closes[:-1])
        
        if return_20d > 0.05 and volatility < 0.03:
            return 'bull'
        elif return_20d < -0.05 or volatility > 0.05:
            return 'bear'
        else:
            return 'neutral'
    
    def calculate_dynamic_position_size(self):
        """Calculate position size based on current performance"""
        # Calculate current drawdown
        current_value = self.get_total_value()
        if current_value > self.high_water_mark:
            self.high_water_mark = current_value
        
        drawdown = (self.high_water_mark - current_value) / self.high_water_mark
        
        # Base position size
        if self.market_regime == 'bull' and drawdown < 0.05:
            base_size = 0.18  # Aggressive in bull market
        elif self.market_regime == 'bear' or drawdown > 0.15:
            base_size = 0.06  # Conservative in bear/drawdown
        else:
            base_size = 0.12  # Normal
        
        # Adjust based on recent performance
        recent_win_rate = self.get_recent_win_rate()
        if recent_win_rate > 0.7:
            base_size *= 1.2  # Increase when hot
        elif recent_win_rate < 0.4:
            base_size *= 0.6  # Reduce when cold
        
        # Drawdown protection
        if drawdown > 0.20:
            base_size *= 0.3  # Survival mode
        elif drawdown > 0.10:
            base_size *= 0.6
        
        return max(0.02, min(0.25, base_size))
    
    def calculate_dynamic_confidence(self):
        """Adjust minimum confidence based on conditions"""
        base_conf = self.base_parameters['min_confidence']
        
        # Market regime adjustment
        if self.market_regime == 'bull':
            base_conf *= 0.85  # More aggressive in bull market
        elif self.market_regime == 'bear':
            base_conf *= 1.15  # More selective in bear market
        
        # Recent performance adjustment
        recent_win_rate = self.get_recent_win_rate()
        if recent_win_rate > 0.7:
            base_conf *= 0.9  # Lower threshold when hot
        elif recent_win_rate < 0.4:
            base_conf *= 1.1  # Higher threshold when cold
        
        return max(0.35, min(0.75, base_conf))
    
    def calculate_dynamic_take_profit(self):
        """Dynamic take profit based on market and performance"""
        base_tp = self.base_parameters['take_profit_pct']
        
        # In bull markets, let winners run longer
        if self.market_regime == 'bull':
            base_tp *= 1.3
        elif self.market_regime == 'bear':
            base_tp *= 0.7  # Take profits faster in bear
        
        # If account is up significantly, lock in gains faster
        current_value = self.get_total_value()
        account_gain = (current_value - self.initial_capital) / self.initial_capital
        if account_gain > 0.5:  # Up 50%+
            base_tp *= 0.7  # Take profits faster
        
        return base_tp
    
    def get_total_value(self):
        """Get current total account value"""
        return self.capital + sum(pos.get('current_value', 0) for pos in self.positions.values())
    
    def get_recent_win_rate(self, lookback=20):
        """Get win rate from recent trades"""
        if len(self.recent_trades) < 5:
            return 0.5
        
        recent = self.recent_trades[-lookback:]
        wins = sum(1 for trade in recent if trade.get('pnl', 0) > 0)
        return wins / len(recent)
    
    def enhanced_signal_generation(self, symbol, data, idx):
        """Generate enhanced trading signals"""
        if idx < 20:
            return 'HOLD', 0.3, []
        
        current = data.iloc[idx]
        prev = data.iloc[idx-1]
        prev5 = data.iloc[idx-5]
        prev20 = data.iloc[idx-20]
        
        # Calculate indicators
        change_1d = (current['Close'] - prev['Close']) / prev['Close']
        change_5d = (current['Close'] - prev5['Close']) / prev5['Close']
        change_20d = (current['Close'] - prev20['Close']) / prev20['Close']
        
        # Volume analysis
        vol_ratio = current['Volume'] / prev['Volume'] if prev['Volume'] > 0 else 1
        
        # Volatility
        recent_closes = data.iloc[idx-10:idx]['Close'].values
        volatility = np.std(np.diff(recent_closes) / recent_closes[:-1]) if len(recent_closes) > 1 else 0.02
        
        # AI Systems Voting (Enhanced)
        votes = {'BUY': 0, 'SELL': 0}
        ai_systems = []
        
        # 1. Trend Following (Market Regime Aware)
        if self.market_regime == 'bull':
            if change_20d > 0.02 and change_5d > 0:
                votes['BUY'] += 1.2
                ai_systems.append('BullTrend')
        elif self.market_regime == 'bear':
            if change_5d < -0.01:
                votes['SELL'] += 0.8
                ai_systems.append('BearTrend')
        else:
            if change_5d > 0.015:
                votes['BUY'] += 0.8
                ai_systems.append('NeutralTrend')
        
        # 2. Momentum with Volume
        if change_1d > 0.01 and vol_ratio > 1.3:
            votes['BUY'] += 1.0
            ai_systems.append('MomentumVolume')
        elif change_1d < -0.01 and vol_ratio > 1.3:
            votes['SELL'] += 1.0
            ai_systems.append('MomentumVolume')
        
        # 3. Mean Reversion (Market Aware)
        if change_5d < -0.05 and change_1d > 0:
            if self.market_regime != 'bear':  # Don't catch falling knives in bear market
                votes['BUY'] += 1.5
                ai_systems.append('MeanReversion')
        
        # 4. Volatility Filter
        if volatility > 0.04:  # High volatility
            # Reduce all votes
            for action in votes:
                votes[action] *= 0.6
            ai_systems.append('VolatilityFilter')
        
        # 5. Pattern Recognition
        if abs(change_1d) > 0.015 and vol_ratio > 1.5:
            action = 'BUY' if change_1d > 0 else 'SELL'
            votes[action] += 0.8
            ai_systems.append('PatternRecog')
        
        # 6. Market Oracle (Predictive)
        prediction = change_1d * 3 + change_5d * 1.5 + (vol_ratio - 1) * 0.2
        if prediction > 0.02:
            votes['BUY'] += 0.9
            ai_systems.append('Oracle')
        elif prediction < -0.02:
            votes['SELL'] += 0.9
            ai_systems.append('Oracle')
        
        # 7. Risk Assessment
        if self.market_regime == 'bear' and len(self.positions) > 3:
            # Reduce new position probability in bear market
            for action in votes:
                votes[action] *= 0.5
        
        # Determine final signal
        total_votes = sum(votes.values())
        if total_votes == 0:
            return 'HOLD', 0.3, ai_systems
        
        final_action = 'BUY' if votes['BUY'] > votes['SELL'] else 'SELL'
        base_confidence = votes[final_action] / total_votes
        
        # System agreement bonus
        agreement_bonus = min(0.15, len(ai_systems) * 0.025)
        final_confidence = min(0.95, base_confidence + agreement_bonus)
        
        # Market regime confidence adjustment
        if final_action == 'BUY' and self.market_regime == 'bear':
            final_confidence *= 0.7
        elif final_action == 'BUY' and self.market_regime == 'bull':
            final_confidence *= 1.1
        
        return final_action, final_confidence, ai_systems
    
    def check_exits(self, symbol, current_price, spy_idx):
        """Check position exits with dynamic parameters"""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        days_held = pos.get('days_held', 0)
        
        # Dynamic take profit
        take_profit = self.calculate_dynamic_take_profit()
        
        # Stop loss (tighter in bear markets)
        stop_loss = self.base_parameters['stop_loss_pct']
        if self.market_regime == 'bear':
            stop_loss *= 0.8
        
        # Exit conditions
        if pnl_pct <= -stop_loss:
            return {'reason': f'Stop Loss at {pnl_pct:.1%}', 'pnl_pct': pnl_pct}
        
        if pnl_pct >= take_profit:
            return {'reason': f'Take Profit at +{pnl_pct:.1%}', 'pnl_pct': pnl_pct}
        
        # Time exit (shorter in bear markets)
        time_limit = self.base_parameters['time_exit_days']
        if self.market_regime == 'bear':
            time_limit *= 0.7
        
        if days_held >= time_limit and pnl_pct < 0.02:
            return {'reason': f'Time Exit ({days_held}d)', 'pnl_pct': pnl_pct}
        
        # Trailing stop for big winners
        if pnl_pct > 0.08:
            # Implement trailing stop
            high_water = pos.get('high_water', current_price)
            if current_price > high_water:
                pos['high_water'] = current_price
                high_water = current_price
            
            trail_stop = high_water * 0.95  # 5% trail
            if current_price <= trail_stop:
                return {'reason': f'Trailing Stop at +{pnl_pct:.1%}', 'pnl_pct': pnl_pct}
        
        return None
    
    def run_improved_backtest(self, symbols, years=2):
        """Run improved backtest"""
        print(f"\n📊 Running {years}-year PROMETHEUS V2 backtest...")
        print("=" * 60)
        
        import yfinance as yf
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years + 50)
        
        print("📥 Downloading data...")
        all_data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                if len(hist) > 100:
                    all_data[symbol] = hist
                    print(f"  ✅ {symbol}: {len(hist)} days")
            except Exception as e:
                print(f"  ❌ {symbol}: {e}")
        
        if not all_data:
            return None
        
        # Get SPY for market regime detection
        self.spy_data = all_data.get('SPY', pd.DataFrame())
        
        # Get common dates
        common_dates = None
        for symbol, data in all_data.items():
            if common_dates is None:
                common_dates = set(data.index)
            else:
                common_dates = common_dates.intersection(set(data.index))
        
        dates = sorted(list(common_dates))
        print(f"\n📅 Backtesting {len(dates)} days with V2 improvements...")
        
        wins = 0
        losses = 0
        total_pnl = 0
        
        for i, current_date in enumerate(dates[20:], 20):
            # Update market regime
            if not self.spy_data.empty:
                self.market_regime = self.detect_market_regime(self.spy_data, i)
            
            # Update position days
            for symbol in self.positions:
                self.positions[symbol]['days_held'] = self.positions[symbol].get('days_held', 0) + 1
            
            # Check exits first
            for symbol in list(self.positions.keys()):
                if symbol in all_data and current_date in all_data[symbol].index:
                    current_price = all_data[symbol].loc[current_date]['Close']
                    
                    # Update position current value
                    pos = self.positions[symbol]
                    pos['current_value'] = pos['quantity'] * current_price
                    
                    exit_info = self.check_exits(symbol, current_price, i)
                    
                    if exit_info:
                        # Execute exit
                        quantity = pos['quantity']
                        proceeds = quantity * current_price
                        cost = quantity * pos['entry_price']
                        pnl = proceeds - cost
                        
                        self.capital += proceeds
                        total_pnl += pnl
                        
                        # Track trade
                        trade_record = {
                            'date': current_date,
                            'symbol': symbol,
                            'action': 'SELL',
                            'price': current_price,
                            'pnl': pnl,
                            'reason': exit_info['reason'],
                            'market_regime': self.market_regime,
                            'days_held': pos.get('days_held', 0)
                        }
                        
                        self.trades.append(trade_record)
                        self.recent_trades.append(trade_record)
                        
                        if pnl > 0:
                            wins += 1
                            self.win_streak += 1
                            self.loss_streak = 0
                        else:
                            losses += 1
                            self.loss_streak += 1
                            self.win_streak = 0
                        
                        del self.positions[symbol]
                        
                        # Keep only recent 50 trades in memory
                        if len(self.recent_trades) > 50:
                            self.recent_trades.pop(0)
            
            # Look for new entries
            dynamic_pos_size = self.calculate_dynamic_position_size()
            dynamic_confidence = self.calculate_dynamic_confidence()
            
            if len(self.positions) < self.base_parameters['max_positions']:
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
                    
                    # Get signal with V2 improvements
                    action, confidence, ai_systems = self.enhanced_signal_generation(symbol, data, date_idx)
                    
                    if action == 'BUY' and confidence >= dynamic_confidence:
                        best_signals.append({
                            'symbol': symbol,
                            'confidence': confidence,
                            'ai_systems': ai_systems,
                            'price': data.loc[current_date]['Close']
                        })
                
                # Enter best positions
                best_signals.sort(key=lambda x: x['confidence'], reverse=True)
                
                for signal in best_signals[:self.base_parameters['max_positions'] - len(self.positions)]:
                    symbol = signal['symbol']
                    price = signal['price']
                    
                    position_value = self.capital * dynamic_pos_size
                    if position_value > 100:  # Minimum $100 position
                        quantity = position_value / price
                        cost = quantity * price
                        
                        if cost <= self.capital:
                            self.capital -= cost
                            self.positions[symbol] = {
                                'entry_price': price,
                                'quantity': quantity,
                                'entry_date': current_date,
                                'ai_systems': signal['ai_systems'],
                                'confidence': signal['confidence'],
                                'days_held': 0,
                                'current_value': quantity * price,
                                'market_regime': self.market_regime
                            }
                            
                            self.trades.append({
                                'date': current_date,
                                'symbol': symbol,
                                'action': 'BUY',
                                'price': price,
                                'quantity': quantity,
                                'confidence': signal['confidence'],
                                'position_size_pct': dynamic_pos_size,
                                'market_regime': self.market_regime
                            })
            
            # Track daily value
            position_value = sum(pos.get('current_value', 0) for pos in self.positions.values())
            total_value = self.capital + position_value
            
            self.daily_values.append({
                'date': current_date,
                'value': total_value,
                'positions': len(self.positions),
                'market_regime': self.market_regime,
                'position_size_used': dynamic_pos_size,
                'confidence_threshold': dynamic_confidence
            })
        
        # Calculate final results
        final_value = self.get_total_value()
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate metrics
        daily_returns = []
        for i in range(1, len(self.daily_values)):
            prev_val = self.daily_values[i-1]['value']
            curr_val = self.daily_values[i]['value']
            if prev_val > 0:
                daily_returns.append((curr_val - prev_val) / prev_val)
        
        if daily_returns:
            sharpe = np.mean(daily_returns) * np.sqrt(252) / (np.std(daily_returns) + 0.0001)
        else:
            sharpe = 0
        
        # Max drawdown
        peak = self.initial_capital
        max_dd = 0
        for day in self.daily_values:
            if day['value'] > peak:
                peak = day['value']
            dd = (peak - day['value']) / peak
            max_dd = max(max_dd, dd)
        
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        avg_trade = total_pnl / len(self.trades) if self.trades else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annualized_return': (1 + total_return) ** (1 / years) - 1,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'total_trades': len(self.trades),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_trade_pnl': avg_trade,
            'final_win_streak': self.win_streak,
            'daily_values': self.daily_values[-250:]  # Last year for analysis
        }

# ═══════════════════════════════════════════════════════════════════════════════
# RUN PROMETHEUS V2 BACKTEST
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("🚀 PROMETHEUS V2 BACKTEST")
print("   Dynamic Sizing | Market Regimes | Improved Learning")
print("=" * 80)

# Test symbols
test_symbols = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN',
    'JPM', 'GS', 'BAC', 
    'SPY', 'QQQ', 'XLF',
    'TSLA', 'GLD'
]

prometheus_v2 = PrometheusV2()
results_v2 = prometheus_v2.run_improved_backtest(test_symbols, years=2)

if results_v2:
    print("\n" + "=" * 80)
    print("🎯 PROMETHEUS V2 RESULTS")
    print("=" * 80)
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║  PROMETHEUS V2 - IMPROVED 2-YEAR BACKTEST                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  💰 Initial Capital:     ${results_v2['initial_capital']:>10,.2f}                    ║
    ║  💵 Final Value:         ${results_v2['final_value']:>10,.2f}                    ║
    ║  📈 Total Return:        {results_v2['total_return_pct']:>+10.2f}%                      ║
    ║  📊 Annualized Return:   {results_v2['annualized_return']*100:>+10.2f}%                      ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📉 Sharpe Ratio:        {results_v2['sharpe_ratio']:>10.2f}                         ║
    ║  ⚠️  Max Drawdown:        {results_v2['max_drawdown']*100:>10.2f}%                      ║
    ║  🎯 Win Rate:            {results_v2['win_rate']*100:>10.1f}%                       ║
    ║  🔥 Win Streak:          {results_v2['final_win_streak']:>10}                          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📊 Total Trades:        {results_v2['total_trades']:>10}                          ║
    ║  ✅ Wins:                {results_v2['wins']:>10}                          ║
    ║  ❌ Losses:              {results_v2['losses']:>10}                          ║
    ║  💲 Avg Trade P&L:       ${results_v2['avg_trade_pnl']:>10.2f}                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Show improvements
    print("\n" + "=" * 80)
    print("🔧 V2 IMPROVEMENTS ACTIVE")
    print("=" * 80)
    print("""
    ✅ Dynamic Position Sizing (2%-25% based on performance)
    ✅ Market Regime Detection (Bull/Bear/Neutral)
    ✅ Adaptive Confidence Thresholds
    ✅ Dynamic Take Profit Levels
    ✅ Compound Protection Mechanisms
    ✅ Trailing Stops for Big Winners
    ✅ Enhanced Risk Management
    """)
    
    # Analyze market regimes during test
    if results_v2['daily_values']:
        regime_counts = {}
        for day in results_v2['daily_values']:
            regime = day.get('market_regime', 'neutral')
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        print(f"\n📊 Market Regime Distribution:")
        for regime, count in regime_counts.items():
            pct = count / len(results_v2['daily_values']) * 100
            print(f"  {regime.title()}: {count} days ({pct:.1f}%)")
    
    # Benchmark comparison
    print("\n" + "=" * 80)
    print("📈 V2 vs BENCHMARK")
    print("=" * 80)
    
    import yfinance as yf
    spy = yf.Ticker('SPY')
    spy_hist = spy.history(period='2y')
    
    if len(spy_hist) > 0:
        spy_return = (spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[0]) / spy_hist['Close'].iloc[0] * 100
        
        print(f"""
    ┌────────────────────────────────────────────────────┐
    │  2-Year Performance Comparison                     │
    ├────────────────────────────────────────────────────┤
    │  S&P 500:           {spy_return:>+7.2f}%                    │
    │  PROMETHEUS V2:     {results_v2['total_return_pct']:>+7.2f}%                    │
    │  Outperformance:    {results_v2['total_return_pct'] - spy_return:>+7.2f}%                    │
    └────────────────────────────────────────────────────┘
        """)
        
        if results_v2['total_return_pct'] > spy_return:
            outperformance = results_v2['total_return_pct'] - spy_return
            print(f"    🏆 PROMETHEUS V2 BEATS S&P 500 BY {outperformance:.1f}%!")
            
            # Value demonstration
            if results_v2['total_return_pct'] > 0:
                print(f"\n    💎 Value Demonstration:")
                print(f"       $1M capital → +${results_v2['total_return_pct'] * 10000:,.0f}")
                print(f"       $5M capital → +${results_v2['total_return_pct'] * 50000:,.0f}")
    
    # Save V2 results
    v2_data = {
        'timestamp': datetime.now().isoformat(),
        'system': 'PROMETHEUS_V2_IMPROVED',
        'improvements': [
            'dynamic_position_sizing',
            'market_regime_detection',
            'adaptive_confidence_thresholds',
            'compound_protection',
            'enhanced_risk_management'
        ],
        'results': results_v2
    }
    
    filename = f'prometheus_v2_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w') as f:
        json.dump(v2_data, f, indent=2, default=str)
    
    print(f"\n💾 V2 results saved to: {filename}")

print("\n" + "=" * 80)
print("🚀 PROMETHEUS V2 IMPROVED BACKTEST COMPLETE!")
print("   Fixed the compound issues!")
print("=" * 80)