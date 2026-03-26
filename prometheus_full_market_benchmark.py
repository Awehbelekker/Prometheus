#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS FULL MARKET BENCHMARK - STOCKS + CRYPTO
================================================================================

Like Renaissance Medallion, this benchmark tests ALL available assets:
- 15 Stocks/ETFs: AAPL, AMZN, AMD, BAC, GOOGL, INTC, JPM, META, MSFT, NFLX, NVDA, SPY, QQQ, IWM, DIA
- 8 Crypto: BTC, ETH, SOL, BNB, ADA, DOT, AVAX, MATIC

Uses REAL trained ML models on REAL historical data.
================================================================================
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


@dataclass
class Asset:
    """Asset configuration"""
    symbol: str
    name: str
    asset_type: str  # 'stock', 'etf', 'crypto'
    start_date: str


class FullMarketModelLoader:
    """Loads trained ML models for all assets"""
    
    def __init__(self, models_dir: str = "models_pretrained"):
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Any] = {}
        self.models_loaded = 0
        
    def load_models(self, symbols: List[str]) -> Dict[str, bool]:
        """Load trained models for all symbols"""
        status = {}
        
        for symbol in symbols:
            model_key = symbol.replace('/', '-')
            direction_model_path = self.models_dir / f"{model_key}_direction_model.pkl"
            
            loaded = False
            if JOBLIB_AVAILABLE and direction_model_path.exists():
                try:
                    self.models[f"{symbol}_direction"] = joblib.load(direction_model_path)
                    loaded = True
                    self.models_loaded += 1
                except Exception as e:
                    pass
                    
            status[symbol] = loaded
            
        return status
    
    def predict(self, symbol: str, features: np.ndarray) -> Tuple[str, float, float]:
        """Make prediction using trained model"""
        direction = 'hold'
        confidence = 0.5
        predicted_return = 0.0
        
        if features is None:
            return direction, confidence, predicted_return
        
        direction_key = f"{symbol}_direction"
        if direction_key in self.models:
            try:
                model = self.models[direction_key]
                
                if len(features.shape) == 1:
                    features = features.reshape(1, -1)
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features)[0]
                    up_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
                    down_prob = float(proba[0]) if len(proba) > 1 else 1 - up_prob
                    
                    if up_prob > down_prob:
                        direction = 'long'
                        confidence = up_prob
                    else:
                        direction = 'short'
                        confidence = down_prob
                        
                    predicted_return = (confidence - 0.5) * 0.1
                else:
                    pred = model.predict(features)[0]
                    direction = 'long' if pred > 0 else 'short'
                    confidence = 0.6
                    predicted_return = 0.01 if pred > 0 else -0.01
                    
            except Exception:
                pass
                
        return direction, confidence, predicted_return


class FeatureEngineer:
    """Calculate the exact 13 features the models expect"""
    
    @staticmethod
    def calculate_features(df: pd.DataFrame) -> Optional[np.ndarray]:
        """Calculate the EXACT 13 technical features"""
        
        if len(df) < 200:
            return None
            
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values if 'Volume' in df.columns else np.ones(len(close))
        
        # 1. SMA_20
        sma_20 = np.mean(close[-20:])
        # 2. SMA_50
        sma_50 = np.mean(close[-50:])
        # 3. SMA_200
        sma_200 = np.mean(close[-200:])
        # 4. EMA_12
        ema_12 = FeatureEngineer._ema(close, 12)
        # 5. EMA_26
        ema_26 = FeatureEngineer._ema(close, 26)
        # 6. MACD
        macd = ema_12 - ema_26
        # 7. MACD_Signal
        macd_signal = macd * 0.9  # Approximation
        # 8. RSI
        returns = np.diff(close[-15:])
        gains = np.maximum(returns, 0)
        losses = np.maximum(-returns, 0)
        avg_gain = np.mean(gains) if len(gains) > 0 else 0.01
        avg_loss = np.mean(losses) if len(losses) > 0 else 0.01
        rs = avg_gain / max(avg_loss, 0.0001)
        rsi = 100 - (100 / (1 + rs))
        # 9. BB_Upper
        bb_std = np.std(close[-20:])
        bb_upper = sma_20 + 2 * bb_std
        # 10. BB_Lower
        bb_lower = sma_20 - 2 * bb_std
        # 11. Volume_Ratio
        vol_sma = np.mean(volume[-20:]) if len(volume) >= 20 else volume[-1]
        volume_ratio = volume[-1] / max(vol_sma, 1)
        # 12. Momentum
        momentum = (close[-1] / close[-10] - 1) * 100 if len(close) >= 10 else 0
        # 13. ATR
        tr_values = []
        for i in range(-14, 0):
            if abs(i) < len(close):
                h = high[i]
                l = low[i]
                c_prev = close[i-1] if i > -len(close) else close[i]
                tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
                tr_values.append(tr)
        atr = np.mean(tr_values) if tr_values else 0
        
        return np.array([sma_20, sma_50, sma_200, ema_12, ema_26, macd, macd_signal,
                        rsi, bb_upper, bb_lower, volume_ratio, momentum, atr])
    
    @staticmethod
    def _ema(data: np.ndarray, period: int) -> float:
        if len(data) < period:
            return np.mean(data)
        multiplier = 2 / (period + 1)
        ema = np.mean(data[:period])
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
        return ema


class FullMarketBacktest:
    """
    Full market backtest across stocks AND crypto - like Renaissance Medallion
    """
    
    # ALL AVAILABLE ASSETS
    ASSETS = [
        # STOCKS
        Asset("AAPL", "Apple", "stock", "2010-01-01"),
        Asset("AMZN", "Amazon", "stock", "2010-01-01"),
        Asset("AMD", "AMD", "stock", "2010-01-01"),
        Asset("BAC", "Bank of America", "stock", "2010-01-01"),
        Asset("GOOGL", "Google", "stock", "2015-01-01"),
        Asset("INTC", "Intel", "stock", "2010-01-01"),
        Asset("JPM", "JPMorgan", "stock", "2010-01-01"),
        Asset("META", "Meta", "stock", "2012-05-18"),
        Asset("MSFT", "Microsoft", "stock", "2010-01-01"),
        Asset("NFLX", "Netflix", "stock", "2010-01-01"),
        Asset("NVDA", "Nvidia", "stock", "2010-01-01"),
        # ETFs
        Asset("SPY", "S&P 500 ETF", "etf", "2010-01-01"),
        Asset("QQQ", "Nasdaq ETF", "etf", "2010-01-01"),
        Asset("IWM", "Russell 2000 ETF", "etf", "2010-01-01"),
        Asset("DIA", "Dow Jones ETF", "etf", "2010-01-01"),
        # CRYPTO
        Asset("BTC-USD", "Bitcoin", "crypto", "2014-09-17"),
        Asset("ETH-USD", "Ethereum", "crypto", "2017-11-09"),
        Asset("SOL-USD", "Solana", "crypto", "2020-04-10"),
        Asset("ADA-USD", "Cardano", "crypto", "2017-10-01"),
        Asset("DOT-USD", "Polkadot", "crypto", "2020-08-19"),
        Asset("AVAX-USD", "Avalanche", "crypto", "2020-09-22"),
        Asset("MATIC-USD", "Polygon", "crypto", "2021-02-27"),
    ]
    
    COMPETITORS = {
        "Renaissance Medallion": {"cagr": 0.66, "sharpe": 2.0, "max_dd": -0.20, "assets": "All"},
        "Citadel": {"cagr": 0.20, "sharpe": 1.5, "max_dd": -0.25, "assets": "All"},
        "Two Sigma": {"cagr": 0.15, "sharpe": 1.3, "max_dd": -0.18, "assets": "All"},
        "Bridgewater": {"cagr": 0.12, "sharpe": 1.0, "max_dd": -0.20, "assets": "All"},
        "S&P 500 Buy&Hold": {"cagr": 0.104, "sharpe": 0.4, "max_dd": -0.55, "assets": "SPY only"},
    }
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.model_loader = FullMarketModelLoader()
        self.feature_engineer = FeatureEngineer()
        
        # Trading parameters
        self.position_size = 0.15  # 15% per position (diversified)
        self.confidence_threshold = 0.55
        self.stop_loss = 0.05
        self.take_profit = 0.10
        self.max_holding_days = 7
        self.max_positions = 5  # More diversified
        
        # Results
        self.trades = []
        self.portfolio_history = []
        self.daily_returns = []
        
    def load_historical_data(self, asset: Asset) -> pd.DataFrame:
        """Load historical data for an asset"""
        if not YFINANCE_AVAILABLE:
            return pd.DataFrame()
            
        try:
            ticker = yf.Ticker(asset.symbol)
            df = ticker.history(start=asset.start_date, end=datetime.now().strftime('%Y-%m-%d'))
            
            # Normalize timezone
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
                
            return df
        except Exception as e:
            print(f"  Warning: Could not load {asset.symbol}: {e}")
            return pd.DataFrame()
    
    def run_backtest(self) -> Dict[str, Any]:
        """Run full market backtest"""
        print()
        print("=" * 80)
        print("PROMETHEUS FULL MARKET BENCHMARK - STOCKS + CRYPTO")
        print("=" * 80)
        print()
        print("Like Renaissance Medallion, testing across ALL asset classes:")
        print(f"  • Stocks: {len([a for a in self.ASSETS if a.asset_type == 'stock'])}")
        print(f"  • ETFs: {len([a for a in self.ASSETS if a.asset_type == 'etf'])}")
        print(f"  • Crypto: {len([a for a in self.ASSETS if a.asset_type == 'crypto'])}")
        print()
        
        # Step 1: Load models
        print("Step 1: Loading trained ML models...")
        symbols = [a.symbol for a in self.ASSETS]
        model_status = self.model_loader.load_models(symbols)
        
        stocks_loaded = sum(1 for a in self.ASSETS if a.asset_type in ['stock', 'etf'] and model_status.get(a.symbol, False))
        crypto_loaded = sum(1 for a in self.ASSETS if a.asset_type == 'crypto' and model_status.get(a.symbol, False))
        
        print(f"  Stocks/ETFs: {stocks_loaded}/{len([a for a in self.ASSETS if a.asset_type in ['stock', 'etf']])} models loaded")
        print(f"  Crypto: {crypto_loaded}/{len([a for a in self.ASSETS if a.asset_type == 'crypto'])} models loaded")
        print()
        
        # Step 2: Load data
        print("Step 2: Loading historical data...")
        all_data: Dict[str, pd.DataFrame] = {}
        
        for asset in self.ASSETS:
            df = self.load_historical_data(asset)
            if len(df) > 200:
                all_data[asset.symbol] = df
                years = len(df) / 252
                print(f"  ✅ {asset.symbol}: {len(df)} days ({years:.1f} years)")
            else:
                print(f"  ❌ {asset.symbol}: Insufficient data")
        print()
        
        if not all_data:
            print("ERROR: No data loaded")
            return {}
            
        # Step 3: Find common backtest period
        print("Step 3: Running multi-asset backtest...")
        
        # Use stocks from 2015 onwards for consistent data
        start_date = pd.Timestamp('2015-01-01')
        end_date = min(df.index[-1] for df in all_data.values())
        
        print(f"  Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Get trading dates from SPY
        if 'SPY' in all_data:
            reference_data = all_data['SPY']
        else:
            reference_data = list(all_data.values())[0]
            
        trading_dates = reference_data.loc[start_date:end_date].index
        total_days = len(trading_dates)
        total_years = total_days / 252
        
        print(f"  Trading days: {total_days} ({total_years:.1f} years)")
        print()
        
        # Run backtest
        capital = self.initial_capital
        self.portfolio_history = [capital]
        positions: Dict[str, Dict] = {}
        
        stock_trades = 0
        crypto_trades = 0
        
        last_report = 0
        
        for i, current_date in enumerate(trading_dates):
            if i < 200:
                self.portfolio_history.append(capital)
                self.daily_returns.append(0)
                continue
                
            daily_pnl = 0
            
            # Check existing positions
            closed_positions = []
            for symbol, pos in positions.items():
                if symbol not in all_data or current_date not in all_data[symbol].index:
                    continue
                    
                current_price = all_data[symbol].loc[current_date, 'Close']
                entry_price = pos['entry_price']
                days_held = (current_date - pos['entry_time']).days
                
                if pos['direction'] == 'long':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                    
                should_exit = False
                if pnl_pct <= -self.stop_loss or pnl_pct >= self.take_profit or days_held >= self.max_holding_days:
                    should_exit = True
                    
                if should_exit:
                    self.trades.append({
                        'symbol': symbol,
                        'direction': pos['direction'],
                        'pnl_percent': pnl_pct,
                        'asset_type': pos['asset_type']
                    })
                    
                    trade_pnl = pos['size'] * pnl_pct
                    capital += trade_pnl
                    daily_pnl += trade_pnl / self.portfolio_history[-1] if self.portfolio_history[-1] > 0 else 0
                    
                    if pos['asset_type'] == 'crypto':
                        crypto_trades += 1
                    else:
                        stock_trades += 1
                        
                    closed_positions.append(symbol)
                    
            for symbol in closed_positions:
                del positions[symbol]
                
            # Generate new signals
            if len(positions) < self.max_positions:
                for asset in self.ASSETS:
                    symbol = asset.symbol
                    if symbol in positions or symbol not in all_data:
                        continue
                    if current_date not in all_data[symbol].index:
                        continue
                        
                    hist_data = all_data[symbol].loc[:current_date].tail(250)
                    if len(hist_data) < 200:
                        continue
                        
                    features = self.feature_engineer.calculate_features(hist_data)
                    if features is None:
                        continue
                        
                    direction, confidence, _ = self.model_loader.predict(symbol, features)
                    
                    if confidence >= self.confidence_threshold and direction != 'hold':
                        current_price = hist_data['Close'].iloc[-1]
                        position_value = capital * self.position_size
                        
                        positions[symbol] = {
                            'direction': direction,
                            'entry_price': current_price,
                            'entry_time': current_date,
                            'size': position_value,
                            'confidence': confidence,
                            'asset_type': asset.asset_type
                        }
                        
                        if len(positions) >= self.max_positions:
                            break
                            
            self.portfolio_history.append(capital)
            self.daily_returns.append(daily_pnl)
            
            progress = (i / len(trading_dates)) * 100
            if progress >= last_report + 10:
                print(f"  Progress: {progress:.0f}% - Capital: ${capital:,.2f} - Trades: {len(self.trades)} (S:{stock_trades} C:{crypto_trades})")
                last_report = int(progress // 10) * 10
                
        # Close remaining positions
        for symbol, pos in positions.items():
            if symbol in all_data and len(all_data[symbol]) > 0:
                final_price = all_data[symbol]['Close'].iloc[-1]
                entry_price = pos['entry_price']
                
                if pos['direction'] == 'long':
                    pnl_pct = (final_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - final_price) / entry_price
                    
                self.trades.append({
                    'symbol': symbol,
                    'direction': pos['direction'],
                    'pnl_percent': pnl_pct,
                    'asset_type': pos['asset_type']
                })
                
                capital += pos['size'] * pnl_pct
                
        print(f"  Progress: 100% - Final: ${capital:,.2f}")
        print()
        
        # Calculate metrics
        results = self._calculate_metrics(capital, total_years, stock_trades, crypto_trades)
        
        # Print results
        self._print_results(results)
        
        # Compare with competitors
        self._compare_with_competitors(results)
        
        # Save results
        self._save_results(results)
        
        return results
        
    def _calculate_metrics(self, final_capital: float, years: float, stock_trades: int, crypto_trades: int) -> Dict[str, Any]:
        """Calculate performance metrics"""
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        cagr = ((final_capital / self.initial_capital) ** (1/max(years, 1))) - 1
        
        daily_ret = np.array(self.daily_returns)
        sharpe = np.mean(daily_ret) / np.std(daily_ret) * np.sqrt(252) if np.std(daily_ret) > 0 else 0
        
        peak = self.portfolio_history[0]
        max_dd = 0
        for value in self.portfolio_history:
            if value > peak:
                peak = value
            dd = (value - peak) / peak if peak > 0 else 0
            if dd < max_dd:
                max_dd = dd
                
        if len(self.trades) > 0:
            wins = sum(1 for t in self.trades if t['pnl_percent'] > 0)
            win_rate = wins / len(self.trades)
        else:
            win_rate = 0
            
        return {
            'final_capital': final_capital,
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'win_rate': win_rate,
            'total_trades': len(self.trades),
            'stock_trades': stock_trades,
            'crypto_trades': crypto_trades,
            'years_tested': years,
            'models_loaded': self.model_loader.models_loaded,
        }
        
    def _print_results(self, results: Dict[str, Any]):
        """Print results"""
        print("=" * 80)
        print("FULL MARKET BENCHMARK RESULTS")
        print("=" * 80)
        
        print("\n📊 PERFORMANCE (Stocks + Crypto):")
        print("-" * 50)
        print(f"  Initial Capital:     ${self.initial_capital:>15,.2f}")
        print(f"  Final Capital:       ${results['final_capital']:>15,.2f}")
        print(f"  Total Return:        {results['total_return']*100:>15.1f}%")
        print(f"  CAGR:                {results['cagr']*100:>15.2f}%")
        print(f"  Sharpe Ratio:        {results['sharpe_ratio']:>15.2f}")
        print(f"  Max Drawdown:        {results['max_drawdown']*100:>15.1f}%")
        print(f"  Win Rate:            {results['win_rate']*100:>15.1f}%")
        print(f"  Years Tested:        {results['years_tested']:>15.1f}")
        
        print("\n📈 TRADE BREAKDOWN:")
        print("-" * 50)
        print(f"  Total Trades:        {results['total_trades']:>15,}")
        print(f"  Stock/ETF Trades:    {results['stock_trades']:>15,}")
        print(f"  Crypto Trades:       {results['crypto_trades']:>15,}")
        print(f"  ML Models Used:      {results['models_loaded']:>15}")
        
    def _compare_with_competitors(self, results: Dict[str, Any]):
        """Compare with hedge funds"""
        print()
        print("=" * 80)
        print("COMPETITIVE COMPARISON - FULL MARKET")
        print("=" * 80)
        
        print("\n🏆 FULL MARKET LEADERBOARD:")
        print("-" * 80)
        print(f"{'Rank':<6}{'System':<30}{'CAGR':<12}{'Sharpe':<10}{'Assets':<15}")
        print("-" * 80)
        
        all_systems = []
        for name, metrics in self.COMPETITORS.items():
            all_systems.append({
                'name': name,
                'cagr': metrics['cagr'],
                'sharpe': metrics['sharpe'],
                'assets': metrics['assets'],
                'ours': False
            })
            
        all_systems.append({
            'name': 'PROMETHEUS (Stocks+Crypto)',
            'cagr': results['cagr'],
            'sharpe': results['sharpe_ratio'],
            'assets': 'Stocks+Crypto',
            'ours': True
        })
        
        all_systems.sort(key=lambda x: x['cagr'], reverse=True)
        
        for i, sys in enumerate(all_systems, 1):
            marker = ">>> " if sys['ours'] else "    "
            print(f"{marker}{i:<3}{sys['name']:<28}{sys['cagr']*100:>8.1f}%   {sys['sharpe']:>6.2f}   {sys['assets']:<15}")
            
        print("-" * 80)
        
        our_rank = next(i for i, s in enumerate(all_systems, 1) if s['ours'])
        print(f"\n📍 PROMETHEUS RANK: #{our_rank} of {len(all_systems)}")
        
        if results['cagr'] > 0.20:
            print("🏆 Status: ELITE TIER - Competing with top hedge funds!")
        elif results['cagr'] > 0.10:
            print("⭐ Status: PROFESSIONAL TIER - Beating market benchmarks")
        elif results['cagr'] > 0.05:
            print("📈 Status: DEVELOPING - Shows promise")
        else:
            print("🔧 Status: NEEDS IMPROVEMENT")
            
    def _save_results(self, results: Dict[str, Any]):
        """Save results"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_type': 'FULL_MARKET_STOCKS_CRYPTO',
            'description': 'Like Renaissance - tests stocks, ETFs, and crypto',
            'results': results,
            'honest_assessment': f"CAGR: {results['cagr']*100:.1f}% across {results['total_trades']} trades in stocks and crypto"
        }
        
        filename = f"FULL_MARKET_BENCHMARK_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
            
        print(f"\n📁 Results saved to: {filename}")


def main():
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " PROMETHEUS FULL MARKET BENCHMARK ".center(78) + "║")
    print("║" + " Testing Stocks + ETFs + Crypto (Like Renaissance Medallion) ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    backtest = FullMarketBacktest(initial_capital=10000.0)
    results = backtest.run_backtest()
    
    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
