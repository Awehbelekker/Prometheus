#!/usr/bin/env python3
"""
100-Year Backtest for Full Prometheus System
Tests the complete optimized system with Universal Reasoning + RL + Predictive Forecasting
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import optimized system
try:
    from core.performance_optimizer import OptimizedTradingSystem
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    logger.error("Optimized Trading System not available")


class HundredYearBacktest:
    """
    100-Year Backtest Engine
    Generates 100 years of market data and tests full Prometheus system
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.results = {}
        
    def generate_100_years_data(self) -> List[Dict]:
        """
        Generate 100 years of realistic market data
        Simulates various market regimes: bull, bear, volatile, sideways
        """
        logger.info("Generating 100 years of market data...")
        
        # 100 years = 36,500 days (approx)
        # For backtesting, we'll use daily data
        num_days = 365 * 100  # 36,500 days
        
        data = []
        base_price = 100.0
        current_year = 1925  # Start from 1925
        
        # Market regime parameters
        regimes = ['bull', 'bear', 'volatile', 'sideways']
        current_regime = 'bull'
        regime_duration = 0
        regime_change_prob = 0.001  # 0.1% chance of regime change per day
        
        for day in range(num_days):
            # Determine current year
            year = 1925 + (day // 365)
            
            # Regime change logic
            if np.random.random() < regime_change_prob or regime_duration > 365 * 5:
                current_regime = np.random.choice(regimes)
                regime_duration = 0
            else:
                regime_duration += 1
            
            # Generate price movement based on regime
            if current_regime == 'bull':
                # Bull market: upward trend with small volatility
                trend = 0.0003  # 0.03% daily return
                volatility = 0.015  # 1.5% volatility
            elif current_regime == 'bear':
                # Bear market: downward trend with higher volatility
                trend = -0.0002  # -0.02% daily return
                volatility = 0.025  # 2.5% volatility
            elif current_regime == 'volatile':
                # Volatile market: high volatility, no clear trend
                trend = 0.0
                volatility = 0.04  # 4% volatility
            else:  # sideways
                # Sideways market: low volatility, no trend
                trend = 0.0
                volatility = 0.01  # 1% volatility
            
            # Add some long-term growth (market grows over 100 years)
            long_term_growth = 0.0001 * (year - 1925) / 100  # Gradual increase
            
            # Generate price change
            daily_change = np.random.normal(trend + long_term_growth, volatility)
            base_price *= (1 + daily_change)
            
            # Ensure price doesn't go negative
            base_price = max(base_price, 1.0)
            
            # Generate volume (higher in volatile markets)
            if current_regime == 'volatile':
                volume = np.random.randint(2000000, 5000000)
            else:
                volume = np.random.randint(1000000, 3000000)
            
            # Generate indicators
            # RSI: oscillates around 50, with regime bias
            if current_regime == 'bull':
                rsi = 50 + np.random.normal(15, 10)  # Bias toward overbought
            elif current_regime == 'bear':
                rsi = 50 + np.random.normal(-15, 10)  # Bias toward oversold
            else:
                rsi = 50 + np.random.normal(0, 15)
            rsi = max(0, min(100, rsi))
            
            # MACD
            if current_regime == 'bull':
                macd = np.random.normal(1.0, 0.5)
            elif current_regime == 'bear':
                macd = np.random.normal(-1.0, 0.5)
            else:
                macd = np.random.normal(0, 0.8)
            
            # Volatility
            volatility_indicator = volatility
            
            # Momentum
            momentum = np.random.normal(trend * 100, volatility * 50)
            
            # Trend strength
            if current_regime in ['bull', 'bear']:
                trend_strength = np.random.uniform(0.6, 1.0)
            else:
                trend_strength = np.random.uniform(0.0, 0.4)
            
            # Trend direction
            if current_regime == 'bull':
                trend_direction = 1.0
            elif current_regime == 'bear':
                trend_direction = -1.0
            else:
                trend_direction = np.random.choice([-0.5, 0, 0.5])
            
            data.append({
                'timestamp': datetime(1925, 1, 1) + timedelta(days=day),
                'year': year,
                'price': base_price,
                'volume': volume,
                'regime': current_regime,
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'volatility': volatility_indicator,
                    'momentum': momentum,
                    'trend_strength': trend_strength,
                    'trend_direction': trend_direction,
                    'volume_trend': np.random.normal(0, 0.3),
                    'volume_ratio': np.random.uniform(0.8, 1.5),
                    'support_level': base_price * 0.95,
                    'resistance_level': base_price * 1.05
                }
            })
            
            if (day + 1) % 10000 == 0:
                logger.info(f"  Generated {day + 1:,} days ({year} year)")
        
        logger.info(f"✅ Generated {len(data):,} days of market data (100 years)")
        return data
    
    def run_backtest(self, system, data: List[Dict]) -> Dict[str, Any]:
        """
        Run backtest on 100 years of data
        """
        logger.info("="*80)
        logger.info("RUNNING 100-YEAR BACKTEST")
        logger.info("="*80)
        
        capital = self.initial_capital
        positions = {}
        trades = []
        portfolio_value_history = [capital]
        decision_times = []
        
        start_time = time.time()
        decisions_made = 0
        last_log_time = time.time()
        
        for i, data_point in enumerate(data):
            # Generate market data format
            market_data = {
                'symbol': 'TEST',
                'price': data_point['price'],
                'volume': data_point['volume'],
                'indicators': data_point['indicators'],
                'timestamp': data_point['timestamp']
            }
            
            # Get current portfolio state
            portfolio = {
                'total_value': capital,
                'positions': positions,
                'cash': capital - sum(p.get('value', 0) for p in positions.values())
            }
            
            # Make decision
            try:
                decision_start = time.time()
                decision = system.make_optimized_decision(
                    market_data=market_data,
                    portfolio=portfolio,
                    context={}
                )
                decision_time = (time.time() - decision_start) * 1000
                decision_times.append(decision_time)
                decisions_made += 1
                
                # Execute trade
                trade_result = self._execute_trade(
                    decision, market_data, capital, positions
                )
                
                if trade_result:
                    trades.append(trade_result)
                    capital = trade_result['new_capital']
                    portfolio_value_history.append(capital)
                    
                    # Learn from outcome
                    system.learn_from_outcome(decision, {
                        'profit': trade_result.get('profit', 0),
                        'loss': trade_result.get('loss', 0),
                        'success': trade_result.get('profit', 0) > 0
                    })
                
            except Exception as e:
                logger.warning(f"Decision failed at day {i}: {e}")
                continue
            
            # Progress logging
            if time.time() - last_log_time > 30:  # Log every 30 seconds
                progress = (i + 1) / len(data) * 100
                year = data_point['year']
                logger.info(f"Progress: {progress:.1f}% ({i+1:,}/{len(data):,} days, Year {year}, "
                          f"Capital: ${capital:,.2f}, Trades: {len(trades)})")
                last_log_time = time.time()
        
        elapsed_time = time.time() - start_time
        
        # Calculate metrics
        final_value = capital
        total_return = (final_value - self.initial_capital) / self.initial_capital
        num_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        losing_trades = num_trades - winning_trades
        win_rate = winning_trades / num_trades if num_trades > 0 else 0
        
        total_profit = sum(t.get('profit', 0) for t in trades)
        total_loss = sum(abs(t.get('loss', 0)) for t in trades if t.get('loss', 0) < 0)
        avg_profit = total_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = total_loss / losing_trades if losing_trades > 0 else 0
        
        # Calculate annualized return
        years = 100
        annualized_return = ((final_value / self.initial_capital) ** (1 / years) - 1) * 100
        
        # Calculate Sharpe ratio
        returns = np.diff(portfolio_value_history) / portfolio_value_history[:-1]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        # Max drawdown
        peak = self.initial_capital
        max_drawdown = 0
        for value in portfolio_value_history:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate CAGR (Compound Annual Growth Rate)
        cagr = ((final_value / self.initial_capital) ** (1 / years) - 1) * 100
        
        results = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annualized_return': annualized_return,
            'cagr': cagr,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'elapsed_time': elapsed_time,
            'decisions_made': decisions_made,
            'avg_decision_time_ms': np.mean(decision_times) if decision_times else 0,
            'years': years,
            'days': len(data)
        }
        
        return results
    
    def _execute_trade(self, decision: Dict, market_data: Dict, capital: float, positions: Dict) -> Optional[Dict]:
        """Execute trade based on decision"""
        action = decision.get('action', 'HOLD')
        confidence = decision.get('confidence', 0.5)
        symbol = market_data.get('symbol', 'TEST')
        price = market_data.get('price', 100.0)
        
        if action == 'HOLD':
            return None
        
        # Position sizing
        position_size_pct = decision.get('position_size', confidence * 0.1)
        position_value = capital * min(position_size_pct, 0.1)  # Max 10%
        quantity = position_value / price
        
        if action == 'BUY':
            if capital >= position_value:
                # Buy
                cost = position_value
                positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'value': cost
                }
                
                # Simulate exit (simplified - exit after 1-5 periods with outcome based on regime)
                hold_periods = np.random.randint(1, 6)
                # Price movement based on market conditions
                volatility = market_data.get('indicators', {}).get('volatility', 0.02)
                price_change = np.random.normal(0, volatility)
                exit_price = price * (1 + price_change * hold_periods)
                exit_value = quantity * exit_price
                profit = exit_value - cost
                
                capital = capital - cost + exit_value
                del positions[symbol]
                
                return {
                    'action': 'BUY',
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': price,
                    'exit_price': exit_price,
                    'profit': profit,
                    'loss': 0 if profit > 0 else profit,
                    'new_capital': capital,
                    'confidence': confidence
                }
        
        elif action == 'SELL':
            if symbol in positions:
                # Sell existing position
                position = positions[symbol]
                entry_value = position['value']
                exit_value = position['quantity'] * price
                profit = exit_value - entry_value
                
                capital = capital + exit_value
                del positions[symbol]
                
                return {
                    'action': 'SELL',
                    'symbol': symbol,
                    'quantity': position['quantity'],
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'profit': profit,
                    'loss': 0 if profit > 0 else profit,
                    'new_capital': capital,
                    'confidence': confidence
                }
        
        return None


async def main():
    """Main backtest execution"""
    logger.info("="*80)
    logger.info("100-YEAR BACKTEST FOR FULL PROMETHEUS SYSTEM")
    logger.info("="*80)
    
    if not SYSTEM_AVAILABLE:
        logger.error("Optimized Trading System not available!")
        return
    
    # Initialize system
    logger.info("Initializing Optimized Trading System...")
    system = OptimizedTradingSystem()
    
    # Initialize backtest
    backtest = HundredYearBacktest(initial_capital=10000.0)
    
    # Generate data
    logger.info("Generating 100 years of market data...")
    data = backtest.generate_100_years_data()
    
    # Run backtest
    logger.info("Starting 100-year backtest...")
    results = backtest.run_backtest(system, data)
    
    # Display results
    logger.info("\n" + "="*80)
    logger.info("100-YEAR BACKTEST RESULTS")
    logger.info("="*80)
    logger.info(f"\nInitial Capital: ${results['initial_capital']:,.2f}")
    logger.info(f"Final Value: ${results['final_value']:,.2f}")
    logger.info(f"Total Return: {results['total_return_pct']:.2f}%")
    logger.info(f"Annualized Return: {results['annualized_return']:.2f}%")
    logger.info(f"CAGR: {results['cagr']:.2f}%")
    logger.info(f"\nTrades: {results['num_trades']:,}")
    logger.info(f"  Winning: {results['winning_trades']:,}")
    logger.info(f"  Losing: {results['losing_trades']:,}")
    logger.info(f"Win Rate: {results['win_rate']*100:.2f}%")
    logger.info(f"\nTotal Profit: ${results['total_profit']:,.2f}")
    logger.info(f"Total Loss: ${results['total_loss']:,.2f}")
    logger.info(f"Avg Profit: ${results['avg_profit']:,.2f}")
    logger.info(f"Avg Loss: ${results['avg_loss']:,.2f}")
    logger.info(f"\nSharpe Ratio: {results['sharpe_ratio']:.3f}")
    logger.info(f"Max Drawdown: {results['max_drawdown']*100:.2f}%")
    logger.info(f"\nAvg Decision Time: {results['avg_decision_time_ms']:.2f}ms")
    logger.info(f"Total Time: {results['elapsed_time']:.2f} seconds")
    logger.info(f"Days Tested: {results['days']:,}")
    
    # Calculate final multiplier
    multiplier = results['final_value'] / results['initial_capital']
    logger.info(f"\n{'='*80}")
    logger.info(f"FINAL RESULT: ${results['initial_capital']:,.2f} → ${results['final_value']:,.2f}")
    logger.info(f"Multiplier: {multiplier:.2f}x over 100 years")
    logger.info(f"CAGR: {results['cagr']:.2f}% per year")
    logger.info(f"{'='*80}")
    
    # Save results
    output_file = f"backtest_100_years_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n✅ Results saved to {output_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

