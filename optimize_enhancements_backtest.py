#!/usr/bin/env python3
"""
PROMETHEUS ENHANCEMENT OPTIMIZER - Find the best configuration to beat all benchmarks
Tests multiple configurations over 10 years and learns from each one
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Any
import json
import warnings
warnings.filterwarnings('ignore')

class EnhancementOptimizer:
    """Optimizer to find best enhancement configuration"""
    
    def __init__(self):
        self.results = []
        self.best_config = None
        self.best_sharpe = -999
        
        # Symbols for testing
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'TSLA', 'META', 'AMZN',
                       'BTC-USD', 'ETH-USD', 'SPY', 'QQQ']
        
        # Benchmark targets to beat
        self.benchmarks = {
            'sp500': 0.10,  # 10% annual
            'top_hedge_fund': 0.12,  # 12% annual
            'quant_fund': 0.09,  # 9% annual
        }
    
    def download_data(self, start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Download historical data"""
        print(f"\n[DOWNLOAD] Fetching data from {start_date} to {end_date}...")
        data = {}
        for symbol in self.symbols:
            try:
                df = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if len(df) > 100:
                    df['SMA_20'] = df['Close'].rolling(20).mean()
                    df['SMA_50'] = df['Close'].rolling(50).mean()
                    df['RSI'] = self.calc_rsi(df['Close'])
                    df['Momentum'] = df['Close'].pct_change(5)
                    data[symbol] = df
                    print(f"  ✓ {symbol}: {len(df)} days")
            except:
                pass
        return data
    
    def calc_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def get_scalar(self, val, default=0):
        """Safely extract scalar from pandas Series or return value"""
        try:
            if hasattr(val, 'iloc'):
                return float(val.iloc[0])
            elif hasattr(val, 'item'):
                return float(val.item())
            else:
                result = float(val)
                return result if not np.isnan(result) else default
        except:
            return default

    def run_backtest(self, data: Dict[str, pd.DataFrame], config: Dict) -> Dict:
        """Run backtest with specific configuration"""
        capital = 10000
        positions = {}
        trades = []
        portfolio_values = []

        all_dates = set()
        for df in data.values():
            all_dates.update(df.index.tolist())
        all_dates = sorted(all_dates)

        for date in all_dates:
            # Calculate portfolio value
            port_value = capital
            for sym, pos in positions.items():
                if sym in data and date in data[sym].index:
                    p = self.get_scalar(data[sym].loc[date, 'Close'])
                    port_value += pos['qty'] * p
            portfolio_values.append({'date': date, 'value': port_value})

            # Manage existing positions
            for symbol in list(positions.keys()):
                if symbol not in data or date not in data[symbol].index:
                    continue

                pos = positions[symbol]
                price = self.get_scalar(data[symbol].loc[date, 'Close'])
                pnl_pct = (price - pos['entry']) / pos['entry'] if pos['entry'] > 0 else 0
                days_held = (date - pos['date']).days

                # Track high for trailing stop
                if price > pos.get('high', pos['entry']):
                    pos['high'] = price

                drop_from_high = (pos['high'] - price) / pos['high'] if pos.get('high', 0) > 0 else 0
                sell_reason = None
                
                # TRAILING STOP
                if config.get('trailing_stop_enabled', True):
                    if pnl_pct >= config['trailing_trigger'] and drop_from_high >= config['trailing_distance']:
                        sell_reason = "TRAILING_STOP"
                
                # SCALE OUT (first level)
                if config.get('scale_out_enabled', True) and not pos.get('scaled'):
                    if pnl_pct >= config['scale_out_first']:
                        # Sell half
                        sell_qty = pos['qty'] * 0.5
                        capital += sell_qty * price
                        pos['qty'] -= sell_qty
                        pos['scaled'] = True
                        trades.append({'pnl_pct': pnl_pct, 'reason': 'SCALE_OUT_1', 'win': pnl_pct > 0})
                
                # SCALE OUT (second level)
                if config.get('scale_out_enabled', True) and pos.get('scaled'):
                    if pnl_pct >= config['scale_out_second']:
                        sell_reason = "SCALE_OUT_2"
                
                # TIME EXIT
                if config.get('time_exit_enabled', True):
                    max_days = config['time_exit_crypto'] if 'USD' in symbol else config['time_exit_stock']
                    if days_held >= max_days and pnl_pct < config.get('min_profit_to_hold', 0.02):
                        sell_reason = "TIME_EXIT"
                
                # TAKE PROFIT
                if pnl_pct >= config['take_profit']:
                    sell_reason = "TAKE_PROFIT"
                
                # STOP LOSS
                if pnl_pct <= -config['stop_loss']:
                    sell_reason = "STOP_LOSS"
                
                # Execute sell
                if sell_reason:
                    capital += pos['qty'] * price
                    trades.append({'pnl_pct': pnl_pct, 'reason': sell_reason, 'win': pnl_pct > 0})
                    del positions[symbol]
            
            # Look for new entries
            for symbol, df in data.items():
                if date not in df.index or symbol in positions:
                    continue
                if len(positions) >= config.get('max_positions', 6):
                    continue

                row = df.loc[date]
                price = self.get_scalar(row['Close'])

                # Generate signal
                score = 0
                close_val = self.get_scalar(row['Close'])
                sma20_val = self.get_scalar(row['SMA_20'])
                sma50_val = self.get_scalar(row['SMA_50'])

                if close_val > sma20_val > sma50_val and sma20_val > 0:
                    score += 2

                rsi = self.get_scalar(row['RSI'], 50)
                if rsi < 40:
                    score += 2
                elif rsi < 50:
                    score += 1

                if score >= config.get('min_score', 3):
                    # CORRELATION FILTER
                    if config.get('correlation_filter_enabled', True):
                        correlated = config.get('correlated_assets', {}).get(symbol, [])
                        if any(c in positions for c in correlated):
                            continue
                    
                    # Buy
                    position_size = capital * config.get('position_size', 0.15)
                    if position_size > 100 and capital >= position_size:
                        qty = position_size / price
                        capital -= position_size
                        positions[symbol] = {
                            'qty': qty, 'entry': price, 'date': date,
                            'high': price, 'scaled': False
                        }
        
        # Calculate metrics
        if not portfolio_values:
            return {'sharpe': -999, 'annual_return': 0, 'win_rate': 0}
        
        final_value = portfolio_values[-1]['value']
        total_return = (final_value - 10000) / 10000
        years = len(all_dates) / 252
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # Calculate Sharpe
        returns = pd.Series([p['value'] for p in portfolio_values]).pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        win_rate = sum(1 for t in trades if t['win']) / len(trades) * 100 if trades else 0
        
        return {
            'sharpe': sharpe,
            'annual_return': annual_return,
            'total_return': total_return,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'final_value': final_value
        }

    def get_configurations(self) -> List[Dict]:
        """Generate different configurations to test"""
        configs = []

        # Config 1: BASELINE (no enhancements)
        configs.append({
            'name': 'BASELINE (No Enhancements)',
            'trailing_stop_enabled': False, 'scale_out_enabled': False,
            'time_exit_enabled': False, 'correlation_filter_enabled': False,
            'take_profit': 0.05, 'stop_loss': 0.03, 'position_size': 0.15,
            'max_positions': 6, 'min_score': 3
        })

        # Config 2: CURRENT (your current settings)
        configs.append({
            'name': 'CURRENT (6 Enhancements)',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.03, 'trailing_distance': 0.015,
            'scale_out_enabled': True, 'scale_out_first': 0.03, 'scale_out_second': 0.07,
            'time_exit_enabled': True, 'time_exit_crypto': 7, 'time_exit_stock': 14,
            'correlation_filter_enabled': True,
            'take_profit': 0.10, 'stop_loss': 0.05, 'position_size': 0.15,
            'max_positions': 6, 'min_score': 3, 'min_profit_to_hold': 0.02,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        # Config 3: AGGRESSIVE (tighter stops, faster exits)
        configs.append({
            'name': 'AGGRESSIVE (Fast Exits)',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.02, 'trailing_distance': 0.01,
            'scale_out_enabled': True, 'scale_out_first': 0.02, 'scale_out_second': 0.04,
            'time_exit_enabled': True, 'time_exit_crypto': 3, 'time_exit_stock': 7,
            'correlation_filter_enabled': True,
            'take_profit': 0.05, 'stop_loss': 0.02, 'position_size': 0.12,
            'max_positions': 8, 'min_score': 2, 'min_profit_to_hold': 0.01,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        # Config 4: CONSERVATIVE (wider stops, longer holds)
        configs.append({
            'name': 'CONSERVATIVE (Patient)',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.05, 'trailing_distance': 0.025,
            'scale_out_enabled': True, 'scale_out_first': 0.05, 'scale_out_second': 0.10,
            'time_exit_enabled': True, 'time_exit_crypto': 14, 'time_exit_stock': 30,
            'correlation_filter_enabled': True,
            'take_profit': 0.15, 'stop_loss': 0.08, 'position_size': 0.20,
            'max_positions': 5, 'min_score': 4, 'min_profit_to_hold': 0.03,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        # Config 5: HIGH WIN RATE (optimized for wins)
        configs.append({
            'name': 'HIGH WIN RATE',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.015, 'trailing_distance': 0.008,
            'scale_out_enabled': True, 'scale_out_first': 0.015, 'scale_out_second': 0.03,
            'time_exit_enabled': True, 'time_exit_crypto': 5, 'time_exit_stock': 10,
            'correlation_filter_enabled': True,
            'take_profit': 0.03, 'stop_loss': 0.015, 'position_size': 0.10,
            'max_positions': 10, 'min_score': 2, 'min_profit_to_hold': 0.005,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        # Config 6: MAX RETURN (optimized for returns)
        configs.append({
            'name': 'MAX RETURN',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.08, 'trailing_distance': 0.04,
            'scale_out_enabled': False,  # Let winners run
            'time_exit_enabled': True, 'time_exit_crypto': 21, 'time_exit_stock': 45,
            'correlation_filter_enabled': False,  # Allow concentration
            'take_profit': 0.25, 'stop_loss': 0.10, 'position_size': 0.25,
            'max_positions': 4, 'min_score': 4, 'min_profit_to_hold': 0.05,
            'correlated_assets': {}
        })

        # Config 7: BALANCED OPTIMAL
        configs.append({
            'name': 'BALANCED OPTIMAL',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.04, 'trailing_distance': 0.02,
            'scale_out_enabled': True, 'scale_out_first': 0.04, 'scale_out_second': 0.08,
            'time_exit_enabled': True, 'time_exit_crypto': 10, 'time_exit_stock': 21,
            'correlation_filter_enabled': True,
            'take_profit': 0.12, 'stop_loss': 0.06, 'position_size': 0.18,
            'max_positions': 6, 'min_score': 3, 'min_profit_to_hold': 0.025,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        # Config 8: TREND FOLLOWER
        configs.append({
            'name': 'TREND FOLLOWER',
            'trailing_stop_enabled': True, 'trailing_trigger': 0.06, 'trailing_distance': 0.03,
            'scale_out_enabled': True, 'scale_out_first': 0.06, 'scale_out_second': 0.12,
            'time_exit_enabled': False,  # Let trends run
            'correlation_filter_enabled': True,
            'take_profit': 0.20, 'stop_loss': 0.07, 'position_size': 0.20,
            'max_positions': 5, 'min_score': 4, 'min_profit_to_hold': 0.04,
            'correlated_assets': {'BTC-USD': ['ETH-USD'], 'NVDA': ['AMD'], 'AAPL': ['MSFT']}
        })

        return configs

    def run_optimization(self, years: int = 10):
        """Run optimization across all configurations"""
        end_date = "2025-12-31"
        start_date = f"{2025 - years}-01-01"

        print("=" * 80)
        print(f"PROMETHEUS ENHANCEMENT OPTIMIZER - {years} YEAR BACKTEST")
        print("=" * 80)
        print(f"Period: {start_date} to {end_date}")
        print(f"Testing {len(self.get_configurations())} configurations")

        # Download data once
        data = self.download_data(start_date, end_date)

        if not data:
            print("ERROR: No data downloaded")
            return

        configs = self.get_configurations()
        results = []

        print("\n" + "=" * 80)
        print("RUNNING BACKTESTS...")
        print("=" * 80)

        for i, config in enumerate(configs):
            print(f"\n[{i+1}/{len(configs)}] Testing: {config['name']}")
            result = self.run_backtest(data, config)
            result['config_name'] = config['name']
            result['config'] = config
            results.append(result)

            print(f"  Annual Return: {result['annual_return']*100:.1f}%")
            print(f"  Sharpe Ratio:  {result['sharpe']:.2f}")
            print(f"  Win Rate:      {result['win_rate']:.1f}%")
            print(f"  Total Trades:  {result['total_trades']}")

        # Sort by combined score (return + sharpe + win_rate)
        for r in results:
            r['score'] = r['annual_return'] * 100 + r['sharpe'] * 5 + r['win_rate'] * 0.5

        results.sort(key=lambda x: x['score'], reverse=True)

        # Print results table
        print("\n" + "=" * 80)
        print("RESULTS RANKED BY COMBINED SCORE")
        print("=" * 80)
        print(f"{'Rank':<5} {'Configuration':<25} {'Annual %':<10} {'Sharpe':<8} {'Win Rate':<10} {'Score':<8}")
        print("-" * 80)

        for i, r in enumerate(results):
            print(f"{i+1:<5} {r['config_name']:<25} {r['annual_return']*100:>7.1f}%  {r['sharpe']:>6.2f}  {r['win_rate']:>7.1f}%  {r['score']:>6.1f}")

        # Benchmark comparison
        print("\n" + "=" * 80)
        print("BENCHMARK COMPARISON (Best Config)")
        print("=" * 80)

        best = results[0]
        print(f"\nBest Configuration: {best['config_name']}")
        print(f"Annual Return: {best['annual_return']*100:.1f}%")

        benchmarks = [
            ('S&P 500 Index', 0.10),
            ('Top Quartile Hedge Funds', 0.12),
            ('Quant Funds Average', 0.09),
            ('Average Hedge Fund', 0.075),
            ('Robo-Advisors', 0.08),
        ]

        beats = 0
        for name, target in benchmarks:
            status = "✅ BEATS" if best['annual_return'] >= target else "❌ BELOW"
            diff = (best['annual_return'] - target) * 100
            print(f"  {status} {name}: {best['annual_return']*100:.1f}% vs {target*100:.1f}% ({diff:+.1f}%)")
            if best['annual_return'] >= target:
                beats += 1

        print(f"\nBEATS {beats}/{len(benchmarks)} benchmarks")

        # Save results
        output = {
            'test_date': datetime.now().isoformat(),
            'period': f"{start_date} to {end_date}",
            'years': years,
            'results': [{k: v for k, v in r.items() if k != 'config'} for r in results],
            'best_config': best['config'],
            'benchmarks_beaten': beats
        }

        filename = f"optimization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\n[SAVED] Results saved to {filename}")

        return results


if __name__ == "__main__":
    optimizer = EnhancementOptimizer()
    results = optimizer.run_optimization(years=10)

