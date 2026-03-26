#!/usr/bin/env python3
"""
Comprehensive Real Market Backtesting System
Tests Prometheus across multiple timeframes (1, 5, 10, 20, 50, 100 years)
with real market data and different market conditions
"""

import sys
import asyncio
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import time
from collections import defaultdict

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backtest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveRealMarketBacktest:
    """
    Comprehensive backtesting with real market data
    Tests across multiple timeframes and market conditions
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.results = {}
        self.learning_patterns = defaultdict(list)
        
        # Timeframes to test (in years)
        self.timeframes = [1, 5, 10, 20, 50, 100]
        
        # Market symbols to test (diverse portfolio)
        self.symbols = [
            'SPY',   # S&P 500
            'QQQ',   # NASDAQ
            'DIA',   # Dow Jones
            'AAPL',  # Tech
            'MSFT',  # Tech
            'GOOGL', # Tech
            'TSLA',  # Volatile
            'NVDA',  # Tech/Volatile
            'BTC-USD', # Crypto
            'ETH-USD'  # Crypto
        ]
        
    def download_real_historical_data(self, symbol: str, years: int) -> Optional[pd.DataFrame]:
        """Download real historical market data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            logger.info(f"[DOWNLOAD] Fetching {years} years of data for {symbol}...")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if data.empty:
                logger.warning(f"[WARNING] No data for {symbol}")
                return None
            
            # Ensure we have required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                logger.warning(f"[WARNING] Missing columns for {symbol}")
                return None
            
            logger.info(f"[SUCCESS] Downloaded {len(data)} days of data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to download {symbol}: {e}")
            return None
    
    def identify_market_regime(self, data: pd.DataFrame, window: int = 30) -> List[str]:
        """Identify market regime for each period"""
        regimes = []
        
        for i in range(window, len(data)):
            window_data = data.iloc[i-window:i]
            returns = window_data['Close'].pct_change().dropna()
            
            if len(returns) < 10:
                regimes.append('unknown')
                continue
            
            avg_return = returns.mean()
            volatility = returns.std()
            trend = (window_data['Close'].iloc[-1] - window_data['Close'].iloc[0]) / window_data['Close'].iloc[0]
            
            # Classify regime
            if trend > 0.1 and volatility < 0.02:
                regime = 'bull'
            elif trend < -0.1:
                regime = 'bear'
            elif volatility > 0.03:
                regime = 'volatile'
            else:
                regime = 'sideways'
            
            regimes.append(regime)
        
        # Pad beginning
        regimes = ['unknown'] * window + regimes
        
        return regimes
    
    async def simulate_prometheus_decision(
        self,
        market_data: Dict,
        portfolio: Dict,
        market_regime: str,
        timeframe: int
    ) -> Dict[str, Any]:
        """Simulate Prometheus decision-making"""
        try:
            # Import Prometheus components
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            # Prepare market data for decision
            decision_data = {
                'price': market_data.get('Close', market_data.get('price', 100)),
                'volume': market_data.get('Volume', 1000000),
                'high': market_data.get('High', market_data.get('price', 100)),
                'low': market_data.get('Low', market_data.get('price', 100)),
                'open': market_data.get('Open', market_data.get('price', 100)),
                'regime': market_regime,
                'timeframe': timeframe
            }
            
            # Make decision (simplified - actual implementation would be more complex)
            # For now, we'll simulate based on market conditions
            decision = await self._simulate_decision_logic(decision_data, portfolio, market_regime)
            
            return decision
            
        except Exception as e:
            logger.error(f"[ERROR] Decision simulation failed: {e}")
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': str(e)}
    
    async def _simulate_decision_logic(
        self,
        market_data: Dict,
        portfolio: Dict,
        regime: str
    ) -> Dict[str, Any]:
        """Simulate Prometheus decision logic"""
        # This is a simplified simulation
        # In real implementation, this would call the actual Universal Reasoning Engine
        
        price = market_data['price']
        volume = market_data.get('volume', 1000000)
        
        # Simple logic based on regime
        if regime == 'bull':
            action = 'BUY'
            confidence = 0.7
        elif regime == 'bear':
            action = 'SELL'
            confidence = 0.6
        elif regime == 'volatile':
            action = 'HOLD'
            confidence = 0.4
        else:  # sideways
            action = 'HOLD'
            confidence = 0.5
        
        return {
            'action': action,
            'confidence': confidence,
            'price': price,
            'regime': regime,
            'timestamp': datetime.now().isoformat()
        }
    
    def learn_patterns_from_data(
        self,
        data: pd.DataFrame,
        regimes: List[str],
        timeframe: int,
        symbol: str
    ):
        """Learn patterns from historical data"""
        patterns = {
            'timeframe': timeframe,
            'symbol': symbol,
            'total_days': len(data),
            'regimes': {},
            'volatility_patterns': [],
            'trend_patterns': [],
            'volume_patterns': []
        }
        
        # Analyze regime patterns
        for regime in ['bull', 'bear', 'volatile', 'sideways']:
            regime_indices = [i for i, r in enumerate(regimes) if r == regime]
            if regime_indices:
                regime_data = data.iloc[regime_indices]
                patterns['regimes'][regime] = {
                    'count': len(regime_indices),
                    'avg_return': regime_data['Close'].pct_change().mean() if len(regime_data) > 1 else 0,
                    'avg_volatility': regime_data['Close'].pct_change().std() if len(regime_data) > 1 else 0
                }
        
        # Learn volatility patterns
        returns = data['Close'].pct_change().dropna()
        if len(returns) > 0:
            patterns['volatility_patterns'] = {
                'mean': returns.std(),
                'max': returns.max(),
                'min': returns.min(),
                'skewness': returns.skew()
            }
        
        # Learn trend patterns
        if len(data) > 0:
            total_return = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
            patterns['trend_patterns'] = {
                'total_return': total_return,
                'trend_direction': 'up' if total_return > 0 else 'down'
            }
        
        # Learn volume patterns
        if 'Volume' in data.columns:
            patterns['volume_patterns'] = {
                'mean': data['Volume'].mean(),
                'std': data['Volume'].std(),
                'max': data['Volume'].max()
            }
        
        self.learning_patterns[f"{symbol}_{timeframe}"] = patterns
        
        return patterns
    
    async def run_backtest_for_timeframe(
        self,
        symbol: str,
        years: int
    ) -> Dict[str, Any]:
        """Run backtest for a specific timeframe"""
        logger.info(f"[BACKTEST] Starting {years}-year backtest for {symbol}...")
        
        # Download real data
        data = self.download_real_historical_data(symbol, years)
        
        if data is None or len(data) < 30:
            logger.warning(f"[SKIP] Insufficient data for {symbol} ({years} years)")
            return None
        
        # Identify market regimes
        regimes = self.identify_market_regime(data)
        
        # Learn patterns
        patterns = self.learn_patterns_from_data(data, regimes, years, symbol)
        
        # Initialize portfolio
        portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'value': self.initial_capital,
            'trades': []
        }
        
        # Run backtest
        portfolio_values = [self.initial_capital]
        trades = []
        
        for i in range(30, len(data)):  # Start after regime identification window
            current_data = data.iloc[i]
            regime = regimes[i] if i < len(regimes) else 'unknown'
            
            # Prepare market data
            market_data = {
                'Close': current_data['Close'],
                'Open': current_data['Open'],
                'High': current_data['High'],
                'Low': current_data['Low'],
                'Volume': current_data['Volume'],
                'price': current_data['Close']
            }
            
            # Get Prometheus decision
            decision = await self.simulate_prometheus_decision(
                market_data,
                portfolio,
                regime,
                years
            )
            
            # Execute trade if confidence is high enough
            if decision['confidence'] >= 0.5:
                # Simplified trade execution
                trade_result = self._execute_trade(
                    decision,
                    market_data,
                    portfolio,
                    i
                )
                
                if trade_result:
                    trades.append(trade_result)
            
            # Update portfolio value
            portfolio_value = portfolio['cash']
            for pos_symbol, pos_data in portfolio['positions'].items():
                if pos_symbol == symbol:
                    portfolio_value += pos_data['quantity'] * market_data['Close']
            
            portfolio_values.append(portfolio_value)
            portfolio['value'] = portfolio_value
        
        # Calculate metrics
        final_value = portfolio_values[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate annualized return
        annualized_return = ((final_value / self.initial_capital) ** (1 / years)) - 1 if years > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        returns = pd.Series(portfolio_values).pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Calculate max drawdown
        cumulative = pd.Series(portfolio_values)
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        result = {
            'symbol': symbol,
            'timeframe_years': years,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t.get('profit', 0) > 0]),
            'losing_trades': len([t for t in trades if t.get('profit', 0) < 0]),
            'patterns_learned': patterns,
            'portfolio_values': portfolio_values,
            'trades': trades[:100]  # Store first 100 trades
        }
        
        logger.info(f"[RESULT] {symbol} ({years} years): {annualized_return:.2%} annualized return")
        
        return result
    
    def _execute_trade(
        self,
        decision: Dict,
        market_data: Dict,
        portfolio: Dict,
        index: int
    ) -> Optional[Dict]:
        """Execute a trade"""
        action = decision.get('action', 'HOLD')
        price = market_data['Close']
        
        if action == 'HOLD':
            return None
        
        # Simplified trade execution
        trade_size = portfolio['cash'] * 0.05  # 5% position size
        
        if action == 'BUY' and trade_size > 0:
            quantity = trade_size / price
            portfolio['cash'] -= trade_size
            portfolio['positions'][market_data.get('symbol', 'UNKNOWN')] = {
                'quantity': quantity,
                'entry_price': price,
                'entry_time': index
            }
            
            return {
                'action': 'BUY',
                'price': price,
                'quantity': quantity,
                'timestamp': index
            }
        
        elif action == 'SELL':
            # Sell existing positions
            total_value = 0
            for pos_symbol, pos_data in list(portfolio['positions'].items()):
                quantity = pos_data['quantity']
                value = quantity * price
                portfolio['cash'] += value
                total_value += value
                del portfolio['positions'][pos_symbol]
            
            if total_value > 0:
                return {
                    'action': 'SELL',
                    'price': price,
                    'value': total_value,
                    'timestamp': index
                }
        
        return None
    
    async def run_comprehensive_backtest(self):
        """Run comprehensive backtest across all timeframes and symbols"""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE REAL MARKET BACKTEST")
        logger.info("=" * 80)
        logger.info(f"Timeframes: {self.timeframes} years")
        logger.info(f"Symbols: {self.symbols}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info("")
        
        all_results = {}
        
        for years in self.timeframes:
            logger.info(f"\n{'='*80}")
            logger.info(f"TESTING {years}-YEAR TIMEFRAME")
            logger.info(f"{'='*80}")
            
            timeframe_results = {}
            
            for symbol in self.symbols:
                try:
                    result = await self.run_backtest_for_timeframe(symbol, years)
                    if result:
                        timeframe_results[symbol] = result
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"[ERROR] Backtest failed for {symbol} ({years} years): {e}")
                    continue
            
            all_results[f"{years}_years"] = timeframe_results
        
        # Generate comprehensive report
        self.generate_comprehensive_report(all_results)
        
        # Save results
        results_file = f"comprehensive_backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        logger.info(f"\n[SAVED] Results saved to {results_file}")
        
        return all_results
    
    def generate_comprehensive_report(self, results: Dict):
        """Generate comprehensive backtest report"""
        logger.info("\n" + "=" * 80)
        logger.info("COMPREHENSIVE BACKTEST REPORT")
        logger.info("=" * 80)
        
        # Summary by timeframe
        for timeframe_key, timeframe_results in results.items():
            years = timeframe_key.replace('_years', '')
            logger.info(f"\n{'-'*80}")
            logger.info(f"{years}-YEAR TIMEFRAME RESULTS")
            logger.info(f"{'-'*80}")
            
            if not timeframe_results:
                logger.info("  No results for this timeframe")
                continue
            
            # Calculate averages
            annualized_returns = [r['annualized_return'] for r in timeframe_results.values()]
            sharpe_ratios = [r['sharpe_ratio'] for r in timeframe_results.values()]
            max_drawdowns = [r['max_drawdown'] for r in timeframe_results.values()]
            
            logger.info(f"  Symbols tested: {len(timeframe_results)}")
            logger.info(f"  Avg Annualized Return: {np.mean(annualized_returns):.2%}")
            logger.info(f"  Avg Sharpe Ratio: {np.mean(sharpe_ratios):.2f}")
            logger.info(f"  Avg Max Drawdown: {np.mean(max_drawdowns):.2%}")
            
            # Best and worst performers
            if annualized_returns:
                best_idx = np.argmax(annualized_returns)
                worst_idx = np.argmin(annualized_returns)
                
                best_symbol = list(timeframe_results.keys())[best_idx]
                worst_symbol = list(timeframe_results.keys())[worst_idx]
                
                logger.info(f"  Best: {best_symbol} ({annualized_returns[best_idx]:.2%})")
                logger.info(f"  Worst: {worst_symbol} ({annualized_returns[worst_idx]:.2%})")
        
        # Pattern learning summary
        logger.info(f"\n{'-'*80}")
        logger.info("PATTERNS LEARNED")
        logger.info(f"{'-'*80}")
        logger.info(f"  Total pattern sets: {len(self.learning_patterns)}")
        
        # Regime analysis
        regime_counts = defaultdict(int)
        for patterns in self.learning_patterns.values():
            for regime, data in patterns.get('regimes', {}).items():
                regime_counts[regime] += data.get('count', 0)
        
        logger.info("  Market Regimes Detected:")
        for regime, count in regime_counts.items():
            logger.info(f"    {regime}: {count} periods")

async def main():
    backtester = ComprehensiveRealMarketBacktest(initial_capital=10000.0)
    results = await backtester.run_comprehensive_backtest()
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE BACKTEST COMPLETE")
    print("=" * 80)
    print("\nCheck the log file and JSON results for detailed analysis.")

if __name__ == "__main__":
    asyncio.run(main())

