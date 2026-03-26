#!/usr/bin/env python3
"""
Comprehensive Backtesting and Benchmarking System
Compares Old Prometheus vs Enhanced Prometheus (Ultimate System)
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import systems
try:
    from core.hrm_integration import HRMTradingEngine as OldHRMEngine
    OLD_SYSTEM_AVAILABLE = True
except ImportError:
    OLD_SYSTEM_AVAILABLE = False
    logger.warning("Old HRM system not available")

try:
    from core.ultimate_trading_system import UltimateTradingSystem
    NEW_SYSTEM_AVAILABLE = True
except ImportError:
    NEW_SYSTEM_AVAILABLE = False
    logger.error("Ultimate Trading System not available")

from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel


class BacktestEngine:
    """
    Backtesting engine for comparing old vs new systems
    """
    
    def __init__(self, historical_data: List[Dict], initial_capital: float = 10000.0):
        self.historical_data = historical_data
        self.initial_capital = initial_capital
        self.results = {}
        
    def run_backtest(self, system_name: str, system, market_data_generator) -> Dict[str, Any]:
        """
        Run backtest for a system
        
        Args:
            system_name: Name of the system
            system: System instance
            market_data_generator: Function to generate market data from historical
            
        Returns:
            Backtest results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"BACKTESTING: {system_name}")
        logger.info(f"{'='*80}")
        
        capital = self.initial_capital
        positions = {}
        trades = []
        portfolio_value_history = [capital]
        
        start_time = time.time()
        decisions_made = 0
        
        for i, historical_point in enumerate(self.historical_data):
            # Generate market data
            market_data = market_data_generator(historical_point, i)
            
            # Get current portfolio state
            portfolio = {
                'total_value': capital,
                'positions': positions,
                'cash': capital - sum(p.get('value', 0) for p in positions.values())
            }
            
            # Make decision
            try:
                if system_name == "Old Prometheus":
                    # Old system
                    context = HRMReasoningContext(
                        market_data=market_data,
                        user_profile={},
                        trading_history=[],
                        current_portfolio=portfolio,
                        risk_preferences={},
                        reasoning_level=HRMReasoningLevel.HIGH_LEVEL
                    )
                    decision = system.make_hierarchical_decision(context)
                else:
                    # New system
                    decision = system.make_ultimate_decision(
                        market_data=market_data,
                        portfolio=portfolio,
                        context={}
                    )
                
                decisions_made += 1
                
                # Execute trade (simplified)
                trade_result = self._execute_trade(
                    decision, market_data, capital, positions
                )
                
                if trade_result:
                    trades.append(trade_result)
                    capital = trade_result['new_capital']
                    portfolio_value_history.append(capital)
                
            except Exception as e:
                logger.warning(f"Decision failed at point {i}: {e}")
                continue
        
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
        
        # Calculate Sharpe ratio (simplified)
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
        
        results = {
            'system_name': system_name,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
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
            'avg_decision_time_ms': (elapsed_time / decisions_made * 1000) if decisions_made > 0 else 0,
            'portfolio_value_history': portfolio_value_history
        }
        
        logger.info(f"\nResults for {system_name}:")
        logger.info(f"  Final Value: ${final_value:,.2f}")
        logger.info(f"  Total Return: {total_return*100:.2f}%")
        logger.info(f"  Trades: {num_trades} (Win: {winning_trades}, Loss: {losing_trades})")
        logger.info(f"  Win Rate: {win_rate*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {sharpe_ratio:.3f}")
        logger.info(f"  Max Drawdown: {max_drawdown*100:.2f}%")
        logger.info(f"  Avg Decision Time: {results['avg_decision_time_ms']:.2f}ms")
        
        return results
    
    def _execute_trade(self, decision: Dict, market_data: Dict, capital: float, positions: Dict) -> Optional[Dict]:
        """Execute trade based on decision (simplified simulation)"""
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
                
                # Simulate exit (simplified - exit after 1 period with random outcome)
                exit_price = price * (1 + np.random.normal(0, 0.02))  # 2% volatility
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


class BenchmarkComparison:
    """
    Comprehensive benchmark comparison
    """
    
    def __init__(self):
        self.results = {}
    
    def generate_test_data(self, num_points: int = 100) -> List[Dict]:
        """Generate synthetic test data"""
        logger.info(f"Generating {num_points} test data points...")
        
        data = []
        base_price = 100.0
        
        for i in range(num_points):
            # Simulate price movement
            change = np.random.normal(0, 0.02)  # 2% volatility
            base_price *= (1 + change)
            
            # Generate indicators
            rsi = 50 + np.random.normal(0, 15)
            macd = np.random.normal(0, 0.5)
            volatility = abs(np.random.normal(0.02, 0.01))
            
            data.append({
                'timestamp': datetime.now() - timedelta(days=num_points-i),
                'price': base_price,
                'volume': np.random.randint(100000, 1000000),
                'indicators': {
                    'rsi': max(0, min(100, rsi)),
                    'macd': macd,
                    'volatility': volatility,
                    'momentum': np.random.normal(0, 0.5),
                    'trend_strength': np.random.uniform(0, 1),
                    'trend_direction': np.random.choice([-1, 0, 1]),
                    'volume_trend': np.random.normal(0, 0.3),
                    'volume_ratio': np.random.uniform(0.5, 2.0),
                    'support_level': base_price * 0.95,
                    'resistance_level': base_price * 1.05
                }
            })
        
        return data
    
    def market_data_generator(self, historical_point: Dict, index: int) -> Dict:
        """Convert historical point to market data format"""
        return {
            'symbol': 'TEST',
            'price': historical_point['price'],
            'volume': historical_point['volume'],
            'indicators': historical_point['indicators'],
            'timestamp': historical_point['timestamp']
        }
    
    async def run_comprehensive_benchmark(self):
        """Run comprehensive benchmark comparing old vs new"""
        logger.info("="*80)
        logger.info("COMPREHENSIVE BACKTESTING AND BENCHMARKING")
        logger.info("Comparing Old Prometheus vs Enhanced Prometheus (Ultimate System)")
        logger.info("="*80)
        
        # Generate test data
        test_data = self.generate_test_data(num_points=100)
        
        # Initialize backtest engine
        backtest = BacktestEngine(test_data, initial_capital=10000.0)
        
        results = {}
        
        # Test Old System
        if OLD_SYSTEM_AVAILABLE:
            try:
                old_system = OldHRMEngine(device='cpu')
                old_results = backtest.run_backtest(
                    "Old Prometheus",
                    old_system,
                    self.market_data_generator
                )
                results['old'] = old_results
            except Exception as e:
                logger.error(f"Old system backtest failed: {e}")
        
        # Test New System
        if NEW_SYSTEM_AVAILABLE:
            try:
                new_system = UltimateTradingSystem()
                new_results = backtest.run_backtest(
                    "Enhanced Prometheus (Ultimate System)",
                    new_system,
                    self.market_data_generator
                )
                results['new'] = new_results
            except Exception as e:
                logger.error(f"New system backtest failed: {e}")
        
        # Compare results
        if 'old' in results and 'new' in results:
            self._compare_results(results['old'], results['new'])
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _compare_results(self, old_results: Dict, new_results: Dict):
        """Compare old vs new results"""
        logger.info("\n" + "="*80)
        logger.info("PERFORMANCE COMPARISON: Old vs Enhanced")
        logger.info("="*80)
        
        comparisons = {
            'Total Return': {
                'old': old_results['total_return_pct'],
                'new': new_results['total_return_pct'],
                'improvement': ((new_results['total_return'] - old_results['total_return']) / abs(old_results['total_return']) * 100) if old_results['total_return'] != 0 else 0
            },
            'Win Rate': {
                'old': old_results['win_rate'] * 100,
                'new': new_results['win_rate'] * 100,
                'improvement': (new_results['win_rate'] - old_results['win_rate']) / old_results['win_rate'] * 100 if old_results['win_rate'] > 0 else 0
            },
            'Sharpe Ratio': {
                'old': old_results['sharpe_ratio'],
                'new': new_results['sharpe_ratio'],
                'improvement': ((new_results['sharpe_ratio'] - old_results['sharpe_ratio']) / abs(old_results['sharpe_ratio']) * 100) if old_results['sharpe_ratio'] != 0 else 0
            },
            'Max Drawdown': {
                'old': old_results['max_drawdown'] * 100,
                'new': new_results['max_drawdown'] * 100,
                'improvement': ((old_results['max_drawdown'] - new_results['max_drawdown']) / old_results['max_drawdown'] * 100) if old_results['max_drawdown'] > 0 else 0
            },
            'Avg Decision Time (ms)': {
                'old': old_results['avg_decision_time_ms'],
                'new': new_results['avg_decision_time_ms'],
                'improvement': ((old_results['avg_decision_time_ms'] - new_results['avg_decision_time_ms']) / old_results['avg_decision_time_ms'] * 100) if old_results['avg_decision_time_ms'] > 0 else 0
            },
            'Number of Trades': {
                'old': old_results['num_trades'],
                'new': new_results['num_trades'],
                'improvement': ((new_results['num_trades'] - old_results['num_trades']) / old_results['num_trades'] * 100) if old_results['num_trades'] > 0 else 0
            }
        }
        
        print("\n" + "="*80)
        print("PERFORMANCE METRICS COMPARISON")
        print("="*80)
        print(f"{'Metric':<30} {'Old':>15} {'Enhanced':>15} {'Improvement':>15}")
        print("-"*80)
        
        for metric, data in comparisons.items():
            old_val = data['old']
            new_val = data['new']
            improvement = data['improvement']
            
            if 'Time' in metric or 'Drawdown' in metric:
                # Lower is better
                sign = "↓" if improvement > 0 else "↑"
            else:
                # Higher is better
                sign = "↑" if improvement > 0 else "↓"
            
            print(f"{metric:<30} {old_val:>15.2f} {new_val:>15.2f} {sign}{abs(improvement):>14.2f}%")
        
        # Overall assessment
        print("\n" + "="*80)
        print("OVERALL ASSESSMENT")
        print("="*80)
        
        total_return_improvement = comparisons['Total Return']['improvement']
        win_rate_improvement = comparisons['Win Rate']['improvement']
        sharpe_improvement = comparisons['Sharpe Ratio']['improvement']
        
        if total_return_improvement > 0 and win_rate_improvement > 0 and sharpe_improvement > 0:
            print("✅ Enhanced Prometheus shows IMPROVEMENT across all key metrics!")
        elif total_return_improvement > 0 or win_rate_improvement > 0:
            print("⚠️ Enhanced Prometheus shows improvement in some metrics")
        else:
            print("⚠️ Results need further analysis")
        
        print(f"\nKey Improvements:")
        print(f"  Total Return: {total_return_improvement:+.2f}%")
        print(f"  Win Rate: {win_rate_improvement:+.2f}%")
        print(f"  Sharpe Ratio: {sharpe_improvement:+.2f}%")
        print(f"  Decision Speed: {comparisons['Avg Decision Time (ms)']['improvement']:+.2f}%")
    
    def _save_results(self, results: Dict):
        """Save results to file"""
        output_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to JSON-serializable format
        json_results = {}
        for key, value in results.items():
            json_results[key] = {
                k: v for k, v in value.items()
                if k != 'portfolio_value_history'  # Skip large arrays
            }
            json_results[key]['portfolio_value_history_length'] = len(value.get('portfolio_value_history', []))
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to {output_file}")


async def main():
    """Main benchmark execution"""
    benchmark = BenchmarkComparison()
    results = await benchmark.run_comprehensive_benchmark()
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETE")
    print("="*80)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())

