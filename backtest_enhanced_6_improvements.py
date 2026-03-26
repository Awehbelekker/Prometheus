#!/usr/bin/env python3
"""
PROMETHEUS ENHANCED BACKTEST - WITH ALL 6 IMPROVEMENTS
Tests: Trailing Stop, DCA, Time Exit, Sentiment, Scale Out, Correlation Filter
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPrometheusBacktester:
    """Backtester with all 6 trading enhancements"""
    
    def __init__(self, start_date: str = "2023-01-01", end_date: str = "2025-12-31"):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = 10000  # Match your actual capital
        
        # === ENHANCEMENT 1: TRAILING STOP ===
        self.trailing_stop_enabled = True
        self.trailing_stop_trigger = 0.03  # Activate at +3%
        self.trailing_stop_distance = 0.015  # Trail 1.5% behind high
        
        # === ENHANCEMENT 2: DCA ON DIPS ===
        self.dca_enabled = True
        self.dca_trigger_pct = -0.03  # Buy more at -3%
        self.dca_max_adds = 2  # Max 2 DCA buys per position
        
        # === ENHANCEMENT 3: TIME-BASED EXIT ===
        self.time_exit_enabled = True
        self.max_hold_days_crypto = 7
        self.max_hold_days_stock = 14
        
        # === ENHANCEMENT 4: SENTIMENT (Fed days) ===
        self.sentiment_enabled = True
        # 2024-2025 FOMC dates
        self.fed_days = [
            "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
            "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-11-05", "2025-12-17"
        ]
        
        # === ENHANCEMENT 5: SCALE OUT ===
        self.scale_out_enabled = True
        self.scale_out_first_pct = 0.03  # Sell 50% at +3%
        self.scale_out_second_pct = 0.07  # Sell rest at +7%
        
        # === ENHANCEMENT 6: CORRELATION FILTER ===
        self.correlation_filter_enabled = True
        self.correlated_assets = {
            'BTC-USD': ['ETH-USD', 'SOL-USD'],
            'ETH-USD': ['BTC-USD', 'SOL-USD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'NVDA': ['AMD'],
            'AMD': ['NVDA'],
        }
        
        # Trading parameters
        self.min_confidence = 0.55  # Lowered for more trades
        self.take_profit_pct = 0.05
        self.catastrophic_stop_pct = 0.15
        self.max_position_pct = 0.15  # 15% per position
        self.max_positions = 6
        
        # Symbols to test
        self.symbols = {
            'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD'],
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'TSLA', 'META', 'AMZN']
        }
        
        # Results tracking
        self.results = {
            'with_enhancements': None,
            'without_enhancements': None
        }
        
        logger.info("=" * 60)
        logger.info("PROMETHEUS ENHANCED BACKTEST - 6 IMPROVEMENTS")
        logger.info("=" * 60)
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Capital: ${self.initial_capital:,}")

    def download_data(self) -> Dict[str, pd.DataFrame]:
        """Download historical data"""
        logger.info("\n[DOWNLOAD] Fetching historical data...")
        data = {}
        
        all_symbols = self.symbols['crypto'] + self.symbols['stocks']
        for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=self.start_date, end=self.end_date)
                if not df.empty:
                    df = self._add_indicators(df)
                    data[symbol] = df
                    logger.info(f"  ✓ {symbol}: {len(df)} days")
            except Exception as e:
                logger.warning(f"  ✗ {symbol}: {e}")
        
        return data

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Momentum
        df['Momentum'] = df['Close'].pct_change(5)
        
        # Volatility
        df['Volatility'] = df['Close'].rolling(window=20).std() / df['Close'].rolling(window=20).mean()
        
        # Trend
        df['Uptrend'] = (df['Close'] > df['SMA_20']) & (df['SMA_20'] > df['SMA_50'])
        df['Downtrend'] = (df['Close'] < df['SMA_20']) & (df['SMA_20'] < df['SMA_50'])
        
        return df

    def generate_signal(self, row: pd.Series, symbol: str) -> dict:
        """Generate trading signal based on indicators"""
        signal = {'action': 'HOLD', 'confidence': 0.5, 'score': 0}
        
        score = 0
        
        # Trend (+2)
        if row.get('Uptrend', False):
            score += 2
        elif row.get('Downtrend', False):
            score -= 2
        
        # RSI (+2)
        rsi = row.get('RSI', 50)
        if pd.notna(rsi):
            if rsi < 35:
                score += 2
            elif rsi < 45:
                score += 1
            elif rsi > 65:
                score -= 2
            elif rsi > 55:
                score -= 1
        
        # Momentum (+1)
        momentum = row.get('Momentum', 0)
        if pd.notna(momentum):
            if momentum > 0.01:
                score += 1
            elif momentum < -0.01:
                score -= 1
        
        # Price vs SMA (+1)
        close = row.get('Close', 0)
        sma20 = row.get('SMA_20', close)
        sma50 = row.get('SMA_50', close)
        if pd.notna(sma20) and close > sma20:
            score += 1
        elif pd.notna(sma20) and close < sma20:
            score -= 1
        
        # SMA crossover (+1)
        if pd.notna(sma20) and pd.notna(sma50):
            if sma20 > sma50:
                score += 1
            else:
                score -= 1
        
        # Convert score to action (more sensitive thresholds)
        if score >= 2:
            signal['action'] = 'BUY'
            signal['confidence'] = min(0.55 + score * 0.05, 0.95)
            signal['score'] = score
        elif score <= -2:
            signal['action'] = 'SELL'
            signal['confidence'] = min(0.55 + abs(score) * 0.05, 0.95)
            signal['score'] = score
        
        return signal

    def run_backtest(self, data: Dict[str, pd.DataFrame], use_enhancements: bool = True) -> dict:
        """Run backtest with or without enhancements"""
        mode = "WITH" if use_enhancements else "WITHOUT"
        logger.info(f"\n{'='*60}")
        logger.info(f"RUNNING BACKTEST {mode} ENHANCEMENTS")
        logger.info(f"{'='*60}")
        
        capital = self.initial_capital
        positions = {}  # {symbol: {'qty': x, 'entry_price': y, 'entry_date': z, 'high_price': h, 'dca_count': n, 'scaled_out': bool}}
        trades = []
        portfolio_values = []
        
        # Build date list from actual data indexes (preserving timezone info)
        all_dates = set()
        for symbol, df in data.items():
            all_dates.update(df.index.tolist())
        all_dates = sorted(all_dates)
        
        trade_count = 0
        
        for date in all_dates:
            date_str = date.strftime('%Y-%m-%d')
            daily_value = capital
            
            # Check Fed day (Enhancement 4)
            is_fed_day = use_enhancements and self.sentiment_enabled and date_str in self.fed_days
            
            # First: Calculate current portfolio value and manage positions
            positions_to_close = []
            
            for symbol, pos in list(positions.items()):
                if symbol not in data or date not in data[symbol].index:
                    daily_value += pos['qty'] * pos['entry_price']  # Use last known price
                    continue
                
                row = data[symbol].loc[date]
                price = row['Close']
                daily_value += pos['qty'] * price
                
                pnl_pct = (price - pos['entry_price']) / pos['entry_price']
                days_held = (date - pos['entry_date']).days
                
                # Update high price for trailing stop
                if price > pos['high_price']:
                    pos['high_price'] = price
                
                drop_from_high = (pos['high_price'] - price) / pos['high_price'] if pos['high_price'] > 0 else 0
                
                sell_reason = None
                sell_qty = pos['qty']
                
                # === ENHANCEMENT 3: TIME EXIT ===
                if use_enhancements and self.time_exit_enabled:
                    max_days = self.max_hold_days_crypto if 'USD' in symbol else self.max_hold_days_stock
                    if days_held >= max_days:
                        sell_reason = f"TIME_EXIT ({days_held}d)"
                
                # === ENHANCEMENT 5: SCALE OUT ===
                if use_enhancements and self.scale_out_enabled and not pos.get('scaled_out', False):
                    if pnl_pct >= self.scale_out_first_pct:
                        sell_reason = f"SCALE_OUT_1 (+{pnl_pct:.1%})"
                        sell_qty = pos['qty'] * 0.5
                        pos['scaled_out'] = True
                
                if use_enhancements and self.scale_out_enabled and pos.get('scaled_out', False):
                    if pnl_pct >= self.scale_out_second_pct:
                        sell_reason = f"SCALE_OUT_2 (+{pnl_pct:.1%})"
                
                # === ENHANCEMENT 1: TRAILING STOP ===
                if use_enhancements and self.trailing_stop_enabled:
                    if pnl_pct >= self.trailing_stop_trigger and drop_from_high >= self.trailing_stop_distance:
                        sell_reason = f"TRAILING_STOP (was +{((pos['high_price']-pos['entry_price'])/pos['entry_price']):.1%})"
                
                # Take profit (without enhancements, simple 5%)
                if not use_enhancements and pnl_pct >= self.take_profit_pct:
                    sell_reason = f"TAKE_PROFIT (+{pnl_pct:.1%})"
                
                # Catastrophic stop
                if pnl_pct <= -self.catastrophic_stop_pct:
                    sell_reason = f"CATASTROPHIC ({pnl_pct:.1%})"
                
                # Simple stop loss without enhancements
                if not use_enhancements and pnl_pct <= -0.02:  # Old 2% stop
                    sell_reason = f"STOP_LOSS ({pnl_pct:.1%})"
                
                # === ENHANCEMENT 2: DCA ===
                if use_enhancements and self.dca_enabled and sell_reason is None:
                    if pnl_pct <= self.dca_trigger_pct and pos.get('dca_count', 0) < self.dca_max_adds:
                        dca_amount = capital * 0.05  # 5% of capital
                        if dca_amount > 10 and capital >= dca_amount:
                            dca_qty = dca_amount / price
                            old_qty = pos['qty']
                            pos['qty'] += dca_qty
                            # Recalculate avg price
                            total_cost = pos['entry_price'] * old_qty + price * dca_qty
                            pos['entry_price'] = total_cost / pos['qty']
                            pos['dca_count'] = pos.get('dca_count', 0) + 1
                            capital -= dca_amount
                            daily_value -= dca_amount  # Adjust for spent capital
                            trades.append({
                                'date': date_str, 'symbol': symbol, 'action': 'DCA_BUY',
                                'price': price, 'qty': dca_qty, 'pnl': 0,
                                'reason': f'DCA #{pos["dca_count"]}'
                            })
                            trade_count += 1
                
                # Queue sell if triggered
                if sell_reason:
                    positions_to_close.append((symbol, sell_qty, sell_reason, price, pos))
            
            # Execute sells
            for symbol, sell_qty, sell_reason, price, pos in positions_to_close:
                sell_value = sell_qty * price
                cost_basis = sell_qty * pos['entry_price']
                pnl = sell_value - cost_basis
                capital += sell_value
                
                trades.append({
                    'date': date_str, 'symbol': symbol, 'action': 'SELL',
                    'price': price, 'qty': sell_qty, 'pnl': pnl,
                    'reason': sell_reason
                })
                trade_count += 1
                
                # Remove or reduce position
                if sell_qty >= positions[symbol]['qty']:
                    del positions[symbol]
                else:
                    positions[symbol]['qty'] -= sell_qty
            
            # Check for new BUY signals
            for symbol, df in data.items():
                if date not in df.index:
                    continue
                
                if symbol in positions:
                    continue  # Already have position
                
                row = df.loc[date]
                price = row['Close']
                
                signal = self.generate_signal(row, symbol)
                
                if signal['action'] == 'BUY' and signal['confidence'] >= self.min_confidence:
                    # Skip if Fed day
                    if is_fed_day:
                        continue
                    
                    # === ENHANCEMENT 6: CORRELATION FILTER ===
                    if use_enhancements and self.correlation_filter_enabled:
                        correlated = self.correlated_assets.get(symbol, [])
                        if any(c in positions for c in correlated):
                            continue  # Skip - already have correlated asset
                    
                    # Check position limits
                    if len(positions) >= self.max_positions:
                        continue
                    
                    # Calculate position size
                    position_value = capital * self.max_position_pct
                    if position_value > 50 and capital >= position_value:
                        qty = position_value / price
                        capital -= position_value
                        
                        positions[symbol] = {
                            'qty': qty,
                            'entry_price': price,
                            'entry_date': date,
                            'high_price': price,
                            'dca_count': 0,
                            'scaled_out': False
                        }
                        
                        trades.append({
                            'date': date_str, 'symbol': symbol, 'action': 'BUY',
                            'price': price, 'qty': qty, 'pnl': 0,
                            'reason': f'SIGNAL (conf={signal["confidence"]:.0%})'
                        })
                        trade_count += 1
            
            # Recalculate portfolio value after all operations
            daily_value = capital
            for symbol, pos in positions.items():
                if symbol in data and date in data[symbol].index:
                    daily_value += pos['qty'] * data[symbol].loc[date, 'Close']
                else:
                    daily_value += pos['qty'] * pos['entry_price']
            
            portfolio_values.append({'date': date_str, 'value': daily_value})
        
        logger.info(f"  Total trades: {trade_count}")
        
        # Calculate metrics
        results = self._calculate_metrics(trades, portfolio_values)
        results['mode'] = mode
        
        return results

    def _calculate_metrics(self, trades: list, portfolio_values: list) -> dict:
        """Calculate performance metrics"""
        if not portfolio_values:
            return {}
        
        values = [p['value'] for p in portfolio_values]
        returns = pd.Series(values).pct_change().dropna()
        
        total_return = (values[-1] - values[0]) / values[0] if values[0] > 0 else 0
        
        # Win rate
        winning = [t for t in trades if t['action'] == 'SELL' and t['pnl'] > 0]
        losing = [t for t in trades if t['action'] == 'SELL' and t['pnl'] < 0]
        total_sells = len(winning) + len(losing)
        win_rate = len(winning) / total_sells if total_sells > 0 else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning)
        gross_loss = abs(sum(t['pnl'] for t in losing))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sharpe ratio (annualized)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Max drawdown
        peak = pd.Series(values).expanding().max()
        drawdown = (pd.Series(values) - peak) / peak
        max_drawdown = drawdown.min()
        
        # Average trade
        avg_win = np.mean([t['pnl'] for t in winning]) if winning else 0
        avg_loss = np.mean([t['pnl'] for t in losing]) if losing else 0
        
        return {
            'total_return': total_return,
            'total_return_pct': f"{total_return:.1%}",
            'final_value': values[-1],
            'total_trades': len(trades),
            'sell_trades': total_sells,
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': win_rate,
            'win_rate_pct': f"{win_rate:.1%}",
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': f"{max_drawdown:.1%}",
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'trades': trades
        }

    def run_comparison(self):
        """Run comparison: with vs without enhancements"""
        logger.info("\n" + "=" * 70)
        logger.info("PROMETHEUS ENHANCEMENT COMPARISON BACKTEST")
        logger.info("=" * 70)
        
        # Download data
        data = self.download_data()
        if not data:
            logger.error("No data downloaded!")
            return
        
        # Run WITHOUT enhancements (old strategy)
        results_without = self.run_backtest(data, use_enhancements=False)
        
        # Run WITH enhancements (new strategy)
        results_with = self.run_backtest(data, use_enhancements=True)
        
        # Print comparison
        logger.info("\n" + "=" * 70)
        logger.info("RESULTS COMPARISON")
        logger.info("=" * 70)
        
        logger.info(f"\n{'Metric':<25} {'WITHOUT':<20} {'WITH ENHANCEMENTS':<20} {'IMPROVEMENT':<15}")
        logger.info("-" * 80)
        
        metrics = [
            ('Total Return', 'total_return_pct', 'total_return'),
            ('Final Value', 'final_value', 'final_value'),
            ('Win Rate', 'win_rate_pct', 'win_rate'),
            ('Profit Factor', 'profit_factor', 'profit_factor'),
            ('Sharpe Ratio', 'sharpe_ratio', 'sharpe_ratio'),
            ('Max Drawdown', 'max_drawdown_pct', 'max_drawdown'),
            ('Total Trades', 'total_trades', 'total_trades'),
            ('Gross Profit', 'gross_profit', 'gross_profit'),
            ('Avg Win', 'avg_win', 'avg_win'),
        ]
        
        for name, display_key, calc_key in metrics:
            val_without = results_without.get(display_key, 'N/A')
            val_with = results_with.get(display_key, 'N/A')
            
            # Calculate improvement
            if calc_key in results_without and calc_key in results_with:
                v1 = results_without[calc_key]
                v2 = results_with[calc_key]
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)) and v1 != 0:
                    if calc_key == 'max_drawdown':  # Less negative is better
                        improvement = ((v1 - v2) / abs(v1)) * 100 if v1 != 0 else 0
                    else:
                        improvement = ((v2 - v1) / abs(v1)) * 100 if v1 != 0 else 0
                    imp_str = f"{improvement:+.1f}%"
                else:
                    imp_str = "N/A"
            else:
                imp_str = "N/A"
            
            # Format values
            if isinstance(val_without, float):
                val_without = f"${val_without:,.2f}" if val_without > 100 else f"{val_without:.2f}"
            if isinstance(val_with, float):
                val_with = f"${val_with:,.2f}" if val_with > 100 else f"{val_with:.2f}"
            
            logger.info(f"{name:<25} {str(val_without):<20} {str(val_with):<20} {imp_str:<15}")
        
        # Enhancement breakdown
        logger.info("\n" + "=" * 70)
        logger.info("ENHANCEMENT IMPACT SUMMARY")
        logger.info("=" * 70)
        
        with_trades = results_with.get('trades', [])
        enhancement_counts = {
            'TRAILING_STOP': len([t for t in with_trades if 'TRAILING' in t.get('reason', '')]),
            'SCALE_OUT': len([t for t in with_trades if 'SCALE_OUT' in t.get('reason', '')]),
            'TIME_EXIT': len([t for t in with_trades if 'TIME_EXIT' in t.get('reason', '')]),
            'DCA_BUY': len([t for t in with_trades if t.get('action') == 'DCA_BUY']),
        }
        
        for enhancement, count in enhancement_counts.items():
            logger.info(f"  {enhancement}: {count} times triggered")
        
        # Save results
        results_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'without_enhancements': {k: v for k, v in results_without.items() if k != 'trades'},
                'with_enhancements': {k: v for k, v in results_with.items() if k != 'trades'},
                'enhancement_triggers': enhancement_counts
            }, f, indent=2, default=str)
        
        logger.info(f"\n[SAVED] Results saved to {results_file}")
        
        return results_without, results_with


async def main():
    """Main entry point"""
    # Run 2-year backtest (2024-2025)
    backtester = EnhancedPrometheusBacktester(
        start_date="2024-01-01",
        end_date="2025-12-31"
    )
    
    results = backtester.run_comparison()
    
    print("\n" + "=" * 70)
    print("BACKTEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
