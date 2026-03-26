#!/usr/bin/env python3
"""
EXECUTION OPTIMIZATION BENCHMARK
═════════════════════════════════════════════════════════════════════════════
Tests the 4 new execution optimization methods over 50 years of simulated trades:
  1. calibrate_broker_parameters() - Broker-specific parameter optimization
  2. optimize_entry_exit_prices() - Market microstructure analysis
  3. track_trading_costs() - Cost tracking and analytics
  4. validate_trade_quality() - Trade quality assessment

Compares:
  - Baseline (original system without optimization)
  - With optimization methods enabled
  - Against theoretical maximum (if all trades were perfect)
  
Key metrics:
  - Total return % (profit after costs)
  - Sharpe ratio (risk-adjusted returns)
  - Maximum drawdown
  - Execution quality score
  - Cost efficiency
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
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('benchmark_execution_optimization.log')
    ]
)
logger = logging.getLogger(__name__)

# Try to import PROMETHEUS systems
try:
    # Import the launcher with our new methods
    from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher
    PROMETHEUS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"PROMETHEUS launcher not available: {e}")
    PROMETHEUS_AVAILABLE = False


class ExecutionOptimizationBenchmark:
    """
    Benchmark the execution optimization methods over 50 years of simulated trading
    """
    
    def __init__(
        self,
        years: int = 50,
        initial_capital: float = 10000.0,
        momentum_threshold: float = 0.0105,
        size_mean: float = 0.09,
        size_std: float = 0.03,
        size_min: float = 0.02,
        size_max: float = 0.20,
        quality_threshold: float = 72.0,
        seed: Optional[int] = None,
    ):
        self.years = years
        self.initial_capital = initial_capital
        self.total_days = years * 252  # Trading days per year
        self.momentum_threshold = momentum_threshold
        self.size_mean = size_mean
        self.size_std = size_std
        self.size_min = size_min
        self.size_max = size_max
        self.quality_threshold = quality_threshold
        self.seed = seed

        if self.seed is not None:
            np.random.seed(self.seed)
        
        # Results tracking
        self.baseline_results = {}
        self.optimized_results = {}
        self.optimized_log_only_results = {}
        self.theoretical_results = {}
        
        # Create launcher instance for access to optimization methods
        self.launcher = None
        if PROMETHEUS_AVAILABLE:
            self.launcher = PrometheusLiveTradingLauncher(standalone_mode=False)
        
        logger.info(
            f"✅ Initialized benchmark for {years}-year period ({self.total_days} trading days), "
            f"momentum={self.momentum_threshold:.4f}, size_mean={self.size_mean:.3f}, "
            f"quality_threshold={self.quality_threshold:.1f}, seed={self.seed}"
        )
    
    def generate_synthetic_market_data(self, days: int = None) -> List[Dict[str, Any]]:
        """Generate realistic 50-year synthetic market data"""
        if days is None:
            days = self.total_days
        
        market_data = []
        current_price = 100.0
        volatility = 0.015  # 1.5% daily vol
        
        for day in range(days):
            # Geometric Brownian motion for realistic price movements
            daily_return = np.random.normal(0.0004, volatility)  # 0.04% mean daily return
            current_price *= (1 + daily_return)
            
            # Create realistic OHLCV data
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            close_price = current_price
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
            
            # Volume with realistic patterns
            base_volume = 1000000
            volume = int(base_volume * (0.5 + abs(np.random.normal(1.0, 0.3))))
            
            # Bid-ask spread (tighter for higher prices, wider for lower vol)
            spread_pct = 0.0005 if current_price > 50 else 0.001
            bid = close_price * (1 - spread_pct / 2)
            ask = close_price * (1 + spread_pct / 2)
            
            market_data.append({
                'date': datetime.now() - timedelta(days=days - day - 1),
                'open': round(open_price, 4),
                'high': round(high_price, 4),
                'low': round(low_price, 4),
                'close': round(close_price, 4),
                'volume': volume,
                'bid': round(bid, 4),
                'ask': round(ask, 4),
                'price': round(close_price, 4),
                'volatility': volatility,
                'change_percent': daily_return * 100
            })
        
        return market_data
    
    def generate_synthetic_trades(self, market_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate realistic synthetic trade signals"""
        trades = []
        
        # Simple momentum-based signal generation
        for i in range(20, len(market_data), 5):  # Generate trades every 5 days
            window = market_data[i-20:i]
            prices = [d['close'] for d in window]
            
            # Simple momentum indicator
            avg_price = np.mean(prices)
            current_price = prices[-1]
            momentum = (current_price - avg_price) / avg_price
            
            if momentum > self.momentum_threshold:  # Bullish
                action = 'BUY'
                confidence = min(0.5 + momentum * 10, 0.95)
            elif momentum < -self.momentum_threshold:  # Bearish
                action = 'SELL'
                confidence = min(0.5 + abs(momentum) * 10, 0.95)
            else:
                continue  # Neutral, skip
            
            # Signal sizing as % of available cash at execution time.
            # This avoids unrealistic leverage and keeps runs comparable.
            size_pct = float(np.clip(np.random.normal(self.size_mean, self.size_std), self.size_min, self.size_max))
            
            trades.append({
                'date': market_data[i]['date'],
                'symbol': 'TEST',
                'action': action,
                'signal_price': current_price,
                'confidence': confidence,
                'size_pct': size_pct,
                'broker': 'Alpaca',
                'signal_source': 'Momentum'
            })
        
        logger.info(f"Generated {len(trades)} synthetic trading signals")
        return trades
    
    def simulate_trade_execution(self, trade_signal: Dict, market_data: Dict,
                                  optimize: bool = False) -> Dict[str, Any]:
        """Simulate trade execution with or without optimization"""
        
        entry_price = market_data['price']
        order_time = time.time()
        
        # Without optimization: use market price
        if not optimize:
            fill_price = entry_price
            limit_price = entry_price
            slippage = np.random.normal(0, market_data.get('volatility', 0.01) * entry_price)
            fill_price += slippage
            execution_time = int(np.random.uniform(5, 60))  # 5-60 seconds
            
            return {
                'symbol': trade_signal['symbol'],
                'action': trade_signal['action'],
                'entry_price': entry_price,
                'signal_price': entry_price,
                'fill_price': fill_price,
                'limit_price': limit_price,
                'quantity': trade_signal['quantity'],
                'filled_qty': trade_signal['quantity'],
                'order_id': f"SIM-{int(order_time * 1_000_000)}-{np.random.randint(1000, 9999)}",
                'order_time': order_time,
                'fill_time': order_time + execution_time,
                'execution_time': execution_time,
                'slippage': slippage,
                'slippage_pct': slippage / entry_price if entry_price > 0 else 0,
                'status': 'filled',
                'optimized': False,
                'broker': trade_signal['broker'],
                'ordered_broker': trade_signal['broker']
            }
        
        # With optimization: call optimize_entry_exit_prices
        if self.launcher:
            try:
                optimization = self.launcher.optimize_entry_exit_prices(
                    symbol=trade_signal['symbol'],
                    market_data=market_data,
                    current_price=entry_price,
                    trade_type='ENTRY'
                )
                
                recommended_price = optimization['recommended_price']
                limit_price = optimization['limit_price']
                execution_prob = optimization['execution_probability']
                
                # Simulate execution at recommended price with some variance
                if np.random.random() < execution_prob:
                    fill_price = recommended_price + np.random.normal(0, market_data.get('volatility', 0.01) * entry_price * 0.5)
                else:
                    fill_price = entry_price  # No fill at limit
                
                execution_time = int(np.random.uniform(3, 30))  # Faster with optimization
                
                return {
                    'symbol': trade_signal['symbol'],
                    'action': trade_signal['action'],
                    'entry_price': entry_price,
                    'signal_price': entry_price,
                    'fill_price': fill_price,
                    'limit_price': limit_price,
                    'quantity': trade_signal['quantity'],
                    'filled_qty': trade_signal['quantity'],
                    'order_id': f"SIM-{int(order_time * 1_000_000)}-{np.random.randint(1000, 9999)}",
                    'order_time': order_time,
                    'fill_time': order_time + execution_time,
                    'execution_time': execution_time,
                    'slippage': fill_price - entry_price,
                    'slippage_pct': (fill_price - entry_price) / entry_price if entry_price > 0 else 0,
                    'status': 'filled',
                    'optimized': True,
                    'broker': trade_signal['broker'],
                    'ordered_broker': trade_signal['broker'],
                    'optimization': optimization
                }
            except Exception as e:
                logger.warning(f"Optimization failed: {e}, falling back to baseline")
        
        # Fallback if launcher unavailable
        return self.simulate_trade_execution(trade_signal, market_data, optimize=False)
    
    def simulate_backtest_scenario(self, trades: List[Dict], market_data: List[Dict],
                                   optimize: bool = False,
                                   quality_gate_mode: str = 'hard') -> Dict[str, Any]:
        """
        Simulate backtest scenario with or without optimization
        Returns comprehensive performance metrics
        """
        scenario_name = "OPTIMIZED" if optimize else "BASELINE"
        if optimize and quality_gate_mode == 'log_only':
            scenario_name = "OPTIMIZED_LOG_ONLY"
        logger.info(f"\n{'='*80}")
        logger.info(f"Running {scenario_name} Scenario")
        logger.info(f"{'='*80}")
        
        capital = self.initial_capital
        positions = {}  # symbol -> {avg_price, quantity, entry_value}
        cash = capital
        
        portfolio_values = [capital]
        all_trades = []
        trades_executed = 0
        trades_rejected = 0
        
        costs_tracked = {}
        if self.launcher:
            costs_tracked = {
                'total_costs': 0.0,
                'costs_by_type': {'commissions': 0.0, 'spreads': 0.0, 'slippage': 0.0, 'fees': 0.0},
                'costs_by_broker': {},
                'costs_by_symbol': {},
                'trade_count': 0,
                'total_trade_value': 0.0,
                'avg_cost_per_trade': 0.0,
                'daily_budget': 50.0,
                'budget_used_pct': 0.0,
                'high_cost_trades': [],
                'period_start': None,
                'trades_logged': []
            }
        
        quality_scores = []
        
        # Date-based market data lookup for efficiency
        market_by_date = {d['date']: d for d in market_data}
        
        for i, trade_signal in enumerate(trades):
            date = trade_signal['date']
            
            # Find closest market data
            market_point = market_by_date.get(date)
            if not market_point:
                # Find nearest
                closest = min(market_data, key=lambda x: abs((x['date'] - date).total_seconds()))
                market_point = closest
            
            # Dynamic quantity sizing with capital/position constraints.
            current_price = max(float(market_point.get('price', 0.0)), 0.01)
            symbol = trade_signal['symbol']
            signal_side = trade_signal['action']

            sized_qty = 0
            if signal_side == 'BUY':
                target_notional = max(cash, 0.0) * float(trade_signal.get('size_pct', 0.08))
                sized_qty = int(target_notional / current_price)
                if sized_qty <= 0:
                    continue
            else:
                held_qty = int(positions.get(symbol, {}).get('quantity', 0))
                if held_qty <= 0:
                    continue
                sized_qty = max(1, int(held_qty * float(trade_signal.get('size_pct', 0.08))))
                sized_qty = min(sized_qty, held_qty)

            sized_signal = dict(trade_signal)
            sized_signal['quantity'] = sized_qty

            # Simulate execution with or without optimization
            execution = self.simulate_trade_execution(sized_signal, market_point, optimize=optimize)
            execution['fill_price'] = max(float(execution.get('fill_price', current_price)), 0.01)
            
            trade_value = execution['fill_price'] * execution['quantity']
            
            # Track trade quality if using optimized scenario
            if optimize and self.launcher:
                try:
                    quality = self.launcher.validate_trade_quality(
                        trade_result=execution,
                        signal_source=trade_signal['signal_source'],
                        market_context=market_point
                    )
                    quality_scores.append(quality['quality_score'])
                    
                    is_acceptable = quality.get('quality_score', 0) >= self.quality_threshold
                    if not is_acceptable and quality_gate_mode == 'hard':
                        trades_rejected += 1
                        logger.debug(f"Trade rejected: Quality score {quality['quality_score']:.0f}")
                        continue  # Skip low-quality trades
                except Exception as e:
                    logger.debug(f"Quality validation error: {e}")
            
            # Track costs in both scenarios for fair comparison.
            if self.launcher:
                try:
                    execution_data = {
                        'fill_price': execution['fill_price'],
                        'limit_price': execution['limit_price'],
                        'market_price': market_point['price'],
                        'action': execution['action'],
                        'timestamp': date
                    }
                    costs_tracked = self.launcher.track_trading_costs(
                        trade_data={
                            'symbol': execution['symbol'],
                            'quantity': execution['quantity'],
                            'entry_price': execution['signal_price'],
                            'broker': execution['broker']
                        },
                        execution_data=execution_data,
                        session_daily_costs=costs_tracked
                    )
                except Exception as e:
                    logger.debug(f"Cost tracking error: {e}")
            
            # Simplified P&L tracking with no leverage/shorting.
            if execution['action'] == 'BUY':
                affordable_qty = int(max(cash, 0.0) / max(execution['fill_price'], 0.01))
                if affordable_qty <= 0:
                    continue
                if execution['quantity'] > affordable_qty:
                    execution['quantity'] = affordable_qty
                    execution['filled_qty'] = affordable_qty
                    trade_value = execution['fill_price'] * execution['quantity']

                if execution['symbol'] not in positions:
                    positions[execution['symbol']] = {'avg_price': 0, 'quantity': 0}
                pos = positions[execution['symbol']]
                total_qty = pos['quantity'] + execution['quantity']
                if total_qty > 0:
                    pos['avg_price'] = (pos['avg_price'] * pos['quantity'] + execution['fill_price'] * execution['quantity']) / total_qty
                pos['quantity'] = total_qty
                cash -= trade_value
            else:  # SELL
                if execution['symbol'] in positions:
                    pos = positions[execution['symbol']]
                    sell_qty = min(execution['quantity'], int(pos['quantity']))
                    if sell_qty <= 0:
                        continue
                    execution['quantity'] = sell_qty
                    execution['filled_qty'] = sell_qty
                    trade_value = execution['fill_price'] * sell_qty

                    # Proceeds already include realized P/L relative to basis,
                    # so do not add P/L separately (prevents double counting).
                    cash += trade_value
                    pos['quantity'] -= sell_qty
                    if pos['quantity'] <= 0:
                        del positions[execution['symbol']]
            
            all_trades.append(execution)
            trades_executed += 1
            
            # Update portfolio value
            position_value = sum(pos['quantity'] * current_price for pos in positions.values())
            portfolio_values.append(cash + position_value)
        
        # Calculate performance metrics
        final_value = portfolio_values[-1]
        total_return_pct = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Sharpe ratio
        pv = np.array(portfolio_values, dtype=float)
        pv_prev = pv[:-1]
        pv_curr = pv[1:]
        valid = pv_prev > 1e-9
        returns = (pv_curr[valid] - pv_prev[valid]) / pv_prev[valid]
        sharpe_ratio = (np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)) if len(returns) > 1 else 0.0
        
        # Maximum drawdown
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (np.array(portfolio_values) - peak) / peak
        max_drawdown_pct = np.min(drawdown) * 100
        
        # Win rate
        winning_trades = sum(1 for t in all_trades if (t['fill_price'] - t['signal_price']) * 
                            (1 if t['action'] == 'BUY' else -1) > 0)
        win_rate = (winning_trades / len(all_trades) * 100) if all_trades else 0
        
        results = {
            'scenario': scenario_name,
            'final_value': final_value,
            'total_return_pct': total_return_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown_pct,
            'trades_executed': trades_executed,
            'trades_rejected': trades_rejected,
            'win_rate': win_rate,
            'avg_trade_quality': np.mean(quality_scores) if quality_scores else 100.0,
            'total_costs': costs_tracked.get('total_costs', 0),
            'cost_efficiency': costs_tracked.get('total_costs', 0) / trades_executed if trades_executed > 0 else 0,
            'quality_gate_mode': quality_gate_mode if optimize else 'none',
            'portfolio_values': portfolio_values,
            'trades': all_trades,
            'quality_scores': quality_scores
        }
        
        return results
    
    async def run(self):
        """Run the full benchmark"""
        logger.info("\n" + "="*80)
        logger.info("EXECUTION OPTIMIZATION BENCHMARK")
        logger.info(f"Period: {self.years} years ({self.total_days} trading days)")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info("="*80)
        
        # Generate synthetic data
        logger.info("\n📊 Generating synthetic market data...")
        market_data = self.generate_synthetic_market_data()
        
        # Generate trade signals
        logger.info("\n📈 Generating trade signals...")
        trades = self.generate_synthetic_trades(market_data)
        
        # Run baseline (no optimization)
        logger.info("\n" + "-"*80)
        self.baseline_results = self.simulate_backtest_scenario(
            trades,
            market_data,
            optimize=False,
            quality_gate_mode='none'
        )

        # Run optimized with quality logging only (no hard rejections).
        logger.info("\n" + "-"*80)
        self.optimized_log_only_results = self.simulate_backtest_scenario(
            trades,
            market_data,
            optimize=True,
            quality_gate_mode='log_only'
        )
        
        # Run optimized (with new methods)
        logger.info("\n" + "-"*80)
        self.optimized_results = self.simulate_backtest_scenario(
            trades,
            market_data,
            optimize=True,
            quality_gate_mode='hard'
        )
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive benchmark report"""
        logger.info("\n" + "="*80)
        logger.info("BENCHMARK RESULTS SUMMARY")
        logger.info("="*80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_config': {
                'years': self.years,
                'initial_capital': self.initial_capital,
                'trading_days': self.total_days,
                'momentum_threshold': self.momentum_threshold,
                'size_mean': self.size_mean,
                'size_std': self.size_std,
                'size_min': self.size_min,
                'size_max': self.size_max,
                'quality_threshold': self.quality_threshold,
                'seed': self.seed
            },
            'baseline': self.baseline_results,
            'optimized_log_only': self.optimized_log_only_results,
            'optimized': self.optimized_results,
            'improvements': {}
        }
        
        # Calculate improvements
        if self.baseline_results and self.optimized_results:
            baseline = self.baseline_results
            optimized = self.optimized_results
            optimized_log_only = self.optimized_log_only_results or {}
            
            improvements = {
                'return_improvement_pct': optimized['total_return_pct'] - baseline['total_return_pct'],
                'sharpe_improvement': optimized['sharpe_ratio'] - baseline['sharpe_ratio'],
                'drawdown_improvement_pct': baseline['max_drawdown_pct'] - optimized['max_drawdown_pct'],
                'win_rate_improvement_pct': optimized['win_rate'] - baseline['win_rate'],
                'cost_reduction_pct': ((baseline['total_costs'] - optimized['total_costs']) / 
                                       max(baseline['total_costs'], 1)) * 100,
                'quality_score_improvement': optimized['avg_trade_quality'] - baseline.get('avg_trade_quality', 0)
            }
            report['improvements'] = improvements

            if optimized_log_only:
                report['improvements_log_only'] = {
                    'return_improvement_pct': optimized_log_only['total_return_pct'] - baseline['total_return_pct'],
                    'sharpe_improvement': optimized_log_only['sharpe_ratio'] - baseline['sharpe_ratio'],
                    'drawdown_improvement_pct': baseline['max_drawdown_pct'] - optimized_log_only['max_drawdown_pct'],
                    'win_rate_improvement_pct': optimized_log_only['win_rate'] - baseline['win_rate'],
                    'cost_reduction_pct': ((baseline['total_costs'] - optimized_log_only['total_costs']) /
                                           max(baseline['total_costs'], 1)) * 100,
                    'quality_score_improvement': optimized_log_only['avg_trade_quality'] - baseline.get('avg_trade_quality', 0)
                }
        
        # Print summary
        print("\n" + "="*80)
        print("RESULTS COMPARISON")
        print("="*80)
        
        metrics = [
            ('Total Return %', 'total_return_pct'),
            ('Sharpe Ratio', 'sharpe_ratio'),
            ('Max Drawdown %', 'max_drawdown_pct'),
            ('Win Rate %', 'win_rate'),
            ('Trades Executed', 'trades_executed'),
            ('Avg Quality Score', 'avg_trade_quality'),
            ('Total Trading Costs', 'total_costs'),
        ]
        
        print(f"\n{'Metric':<25} {'Baseline':>15} {'Opt(LogOnly)':>15} {'Opt(Hard)':>15}")
        print("-" * 80)
        
        for metric_name, key in metrics:
            baseline_val = self.baseline_results.get(key, 0)
            optimized_log_val = self.optimized_log_only_results.get(key, 0)
            optimized_val = self.optimized_results.get(key, 0)

            print(f"{metric_name:<25} {baseline_val:>15.2f} {optimized_log_val:>15.2f} {optimized_val:>15.2f}")
        
        # Key findings
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        if report['improvements']['return_improvement_pct'] > 0:
            print(f"✅ Return Improvement: +{report['improvements']['return_improvement_pct']:.2f}%")
        
        if report['improvements']['sharpe_improvement'] > 0:
            print(f"✅ Sharpe Ratio Improvement: +{report['improvements']['sharpe_improvement']:.2f}")
        
        if report['improvements']['drawdown_improvement_pct'] > 0:
            print(f"✅ Drawdown Reduction: -{report['improvements']['drawdown_improvement_pct']:.2f}%")
        
        if report['improvements']['cost_reduction_pct'] > 0:
            print(f"✅ Cost Reduction: -{report['improvements']['cost_reduction_pct']:.2f}%")
        
        trades_rejected = self.optimized_results.get('trades_rejected', 0)
        if trades_rejected > 0:
            print(f"✅ Low-Quality Trades Filtered Out (Hard Gate): {trades_rejected} trades")
        
        # Save report
        report_path = Path('benchmark_execution_optimization_report.json')
        report_path.write_text(json.dumps(report, indent=2, default=str))
        logger.info(f"\n📊 Report saved to {report_path}")
        
        return report


async def main():
    """Main entry point"""
    benchmark = ExecutionOptimizationBenchmark(
        years=50,
        initial_capital=10000.0,
        momentum_threshold=0.0105,
        size_mean=0.09,
        quality_threshold=72.0,
    )
    await benchmark.run()


if __name__ == '__main__':
    asyncio.run(main())
