#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🔄 PROMETHEUS CONTINUOUS IMPROVEMENT CYCLE
═══════════════════════════════════════════════════════════════════════════════
Automated training-benchmarking-optimization loop that continuously improves
PROMETHEUS until it outperforms industry benchmarks and competitors.

Author: PROMETHEUS AI Trading System
Version: 1.0.0
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PROMETHEUS-ContinuousImprovement')

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 PERFORMANCE BENCHMARKS & SUCCESS CRITERIA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PerformanceBenchmarks:
    """Industry benchmarks and target performance metrics"""
    
    # PROMETHEUS Target Metrics (Must achieve for deployment)
    target_daily_return_min: float = 0.05      # 5% minimum daily return
    target_daily_return_max: float = 0.09      # 9% optimal daily return
    target_win_rate: float = 0.55              # 55% minimum win rate
    target_sharpe_ratio: float = 2.0           # Sharpe ratio > 2.0 is excellent
    target_max_drawdown: float = 0.15          # Maximum 15% drawdown
    target_profit_factor: float = 1.5          # Profit factor > 1.5
    target_sortino_ratio: float = 2.5          # Sortino ratio > 2.5
    
    # Stretch Goals (Outperform competitors)
    stretch_win_rate: float = 0.65             # 65% win rate
    stretch_sharpe_ratio: float = 3.0          # Sharpe > 3.0 is exceptional
    stretch_daily_return: float = 0.08         # 8% consistent daily return
    stretch_max_drawdown: float = 0.10         # <10% drawdown
    
    # Industry Benchmarks (Annual returns, converted to daily for comparison)
    sp500_annual_return: float = 0.10          # S&P 500 ~10% annual
    qqq_annual_return: float = 0.15            # QQQ ~15% annual
    hedge_fund_annual_return: float = 0.20     # Top hedge funds ~20% annual
    quant_fund_annual_return: float = 0.30     # Top quant funds ~30% annual
    
    # Competitor Benchmarks (estimated)
    competitor_win_rate: float = 0.52          # Average algo trader ~52%
    competitor_sharpe: float = 1.5             # Good algo trader Sharpe ~1.5
    competitor_max_drawdown: float = 0.25      # Average max drawdown ~25%
    
    def get_daily_benchmark(self, annual_return: float) -> float:
        """Convert annual return to daily compound return"""
        return (1 + annual_return) ** (1/252) - 1
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class OptimizationState:
    """Track optimization progress across iterations"""
    iteration: int = 0
    best_win_rate: float = 0.0
    best_sharpe_ratio: float = 0.0
    best_daily_return: float = 0.0
    best_max_drawdown: float = 1.0
    best_profit_factor: float = 0.0
    current_parameters: Dict[str, float] = None
    improvement_history: List[Dict] = None
    targets_met: Dict[str, bool] = None
    deployment_ready: bool = False
    
    def __post_init__(self):
        if self.current_parameters is None:
            self.current_parameters = {}
        if self.improvement_history is None:
            self.improvement_history = []
        if self.targets_met is None:
            self.targets_met = {
                'win_rate': False,
                'sharpe_ratio': False,
                'daily_return': False,
                'max_drawdown': False,
                'profit_factor': False
            }

class ContinuousImprovementEngine:
    """
    Automated optimization loop that continuously improves PROMETHEUS
    """
    
    def __init__(self, db_path: str = 'prometheus_learning.db'):
        self.db_path = db_path
        self.benchmarks = PerformanceBenchmarks()
        self.state = OptimizationState()
        self.results_dir = Path('optimization_results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Parameter search space
        self.parameter_space = {
            'take_profit_pct': [0.05, 0.08, 0.10, 0.12, 0.15],
            'stop_loss_pct': [0.02, 0.03, 0.04, 0.05],
            'position_size_pct': [0.03, 0.05, 0.08, 0.10],
            'min_confidence': [0.45, 0.50, 0.55, 0.60, 0.65],
            'trailing_stop_pct': [0.02, 0.025, 0.03, 0.035]
        }
        
        logger.info("🔄 PROMETHEUS Continuous Improvement Engine initialized")
        logger.info(f"📊 Target Win Rate: {self.benchmarks.target_win_rate:.0%}")
        logger.info(f"📊 Target Sharpe Ratio: {self.benchmarks.target_sharpe_ratio:.1f}")
        logger.info(f"📊 Target Daily Return: {self.benchmarks.target_daily_return_min:.0%}-{self.benchmarks.target_daily_return_max:.0%}")
        logger.info(f"📊 Target Max Drawdown: <{self.benchmarks.target_max_drawdown:.0%}")

    def load_state(self) -> bool:
        """Load previous optimization state if exists"""
        state_file = self.results_dir / 'optimization_state.json'
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                    self.state = OptimizationState(**data)
                    logger.info(f"📂 Loaded optimization state: iteration {self.state.iteration}")
                    return True
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
        return False

    def save_state(self):
        """Save current optimization state"""
        state_file = self.results_dir / 'optimization_state.json'
        try:
            with open(state_file, 'w') as f:
                json.dump({
                    'iteration': self.state.iteration,
                    'best_win_rate': self.state.best_win_rate,
                    'best_sharpe_ratio': self.state.best_sharpe_ratio,
                    'best_daily_return': self.state.best_daily_return,
                    'best_max_drawdown': self.state.best_max_drawdown,
                    'best_profit_factor': self.state.best_profit_factor,
                    'current_parameters': self.state.current_parameters,
                    'improvement_history': self.state.improvement_history,
                    'targets_met': self.state.targets_met,
                    'deployment_ready': self.state.deployment_ready
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save state: {e}")

    def run_training(self, min_trades: int = 10) -> Optional[Dict]:
        """Run supervised learning training pipeline"""
        logger.info("🧠 Running supervised learning training...")
        try:
            from train_prometheus_supervised import SupervisedLearningPipeline
            pipeline = SupervisedLearningPipeline()
            metrics = pipeline.run_training(min_trades=min_trades)
            return metrics
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return None

    def run_backtest(self, params: Dict[str, float], days: int = 90) -> Optional[Dict]:
        """Run backtesting with specific parameters"""
        logger.info(f"📈 Running backtest with params: {params}")
        try:
            import asyncio
            from prometheus_real_ai_backtest import PrometheusRealAIBacktester, BacktestMetrics

            backtest = PrometheusRealAIBacktester(
                initial_capital=100000.0,
                take_profit_pct=params.get('take_profit_pct', 0.10),
                stop_loss_pct=params.get('stop_loss_pct', 0.03),
                max_position_pct=params.get('position_size_pct', 0.05),
                min_confidence=params.get('min_confidence', 0.50)
            )

            symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']

            # Run async backtest
            async def run_async_backtest():
                return await backtest.run_backtest(symbols=symbols, period_days=days)

            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If already in async context, create new loop
                    import nest_asyncio
                    nest_asyncio.apply()
                    results = loop.run_until_complete(run_async_backtest())
                else:
                    results = loop.run_until_complete(run_async_backtest())
            except RuntimeError:
                results = asyncio.run(run_async_backtest())

            # Convert BacktestMetrics dataclass to dict
            if isinstance(results, BacktestMetrics):
                return {
                    'metrics': {
                        'total_return_pct': results.total_return * 100,
                        'sharpe_ratio': results.sharpe_ratio,
                        'sortino_ratio': results.sortino_ratio,
                        'max_drawdown': results.max_drawdown,
                        'win_rate': results.win_rate,
                        'profit_factor': results.profit_factor,
                        'total_trades': results.total_trades
                    },
                    'trading_days': days
                }

            return results
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def evaluate_performance(self, backtest_results: Dict) -> Dict[str, Any]:
        """Evaluate performance against benchmarks"""
        metrics = backtest_results.get('metrics', {})

        win_rate = metrics.get('win_rate', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 1))
        profit_factor = metrics.get('profit_factor', 0)
        total_return = metrics.get('total_return_pct', 0) / 100

        # Calculate daily return from total return over period
        days = backtest_results.get('trading_days', 90)
        daily_return = (1 + total_return) ** (1/days) - 1 if days > 0 else 0

        # Compare against targets
        evaluation = {
            'metrics': {
                'win_rate': win_rate,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'profit_factor': profit_factor,
                'daily_return': daily_return,
                'total_return': total_return
            },
            'targets_met': {
                'win_rate': bool(win_rate >= self.benchmarks.target_win_rate),
                'sharpe_ratio': bool(sharpe >= self.benchmarks.target_sharpe_ratio),
                'daily_return': bool(daily_return >= self.benchmarks.target_daily_return_min),
                'max_drawdown': bool(max_drawdown <= self.benchmarks.target_max_drawdown),
                'profit_factor': bool(profit_factor >= self.benchmarks.target_profit_factor)
            },
            'vs_benchmarks': {
                'vs_sp500': daily_return / self.benchmarks.get_daily_benchmark(0.10) if daily_return else 0,
                'vs_qqq': daily_return / self.benchmarks.get_daily_benchmark(0.15) if daily_return else 0,
                'vs_competitors': sharpe / self.benchmarks.competitor_sharpe if sharpe else 0
            },
            'stretch_goals': {
                'win_rate_stretch': win_rate >= self.benchmarks.stretch_win_rate,
                'sharpe_stretch': sharpe >= self.benchmarks.stretch_sharpe_ratio,
                'drawdown_stretch': max_drawdown <= self.benchmarks.stretch_max_drawdown
            }
        }

        # Check if deployment ready (all core targets met)
        all_targets_met = all(evaluation['targets_met'].values())
        evaluation['deployment_ready'] = all_targets_met

        return evaluation

    def optimize_parameters(self, current_results: Dict, current_params: Dict) -> Dict[str, float]:
        """Generate improved parameters based on current results"""
        evaluation = self.evaluate_performance(current_results)
        metrics = evaluation['metrics']

        new_params = current_params.copy()

        # Adaptive parameter adjustment based on performance gaps
        if metrics['win_rate'] < self.benchmarks.target_win_rate:
            # Low win rate: increase confidence threshold, tighten stops
            if 'min_confidence' in new_params:
                idx = self.parameter_space['min_confidence'].index(new_params['min_confidence'])
                if idx < len(self.parameter_space['min_confidence']) - 1:
                    new_params['min_confidence'] = self.parameter_space['min_confidence'][idx + 1]

        if metrics['max_drawdown'] > self.benchmarks.target_max_drawdown:
            # High drawdown: reduce position size, tighten stop loss
            if 'position_size_pct' in new_params:
                idx = self.parameter_space['position_size_pct'].index(new_params['position_size_pct'])
                if idx > 0:
                    new_params['position_size_pct'] = self.parameter_space['position_size_pct'][idx - 1]
            if 'stop_loss_pct' in new_params:
                idx = self.parameter_space['stop_loss_pct'].index(new_params['stop_loss_pct'])
                if idx > 0:
                    new_params['stop_loss_pct'] = self.parameter_space['stop_loss_pct'][idx - 1]

        if metrics['profit_factor'] < self.benchmarks.target_profit_factor:
            # Low profit factor: increase take profit target
            if 'take_profit_pct' in new_params:
                idx = self.parameter_space['take_profit_pct'].index(new_params['take_profit_pct'])
                if idx < len(self.parameter_space['take_profit_pct']) - 1:
                    new_params['take_profit_pct'] = self.parameter_space['take_profit_pct'][idx + 1]

        return new_params

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🔍 GRID SEARCH OPTIMIZATION
    # ═══════════════════════════════════════════════════════════════════════════════

    def run_grid_search(self, param_subset: Dict[str, List] = None, days: int = 60) -> Dict:
        """
        Run exhaustive grid search over parameter combinations.
        Returns best parameters and their performance.
        """
        import itertools

        search_space = param_subset or self.parameter_space
        param_names = list(search_space.keys())
        param_values = list(search_space.values())

        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)

        logger.info(f"🔍 GRID SEARCH: Testing {total_combinations} parameter combinations...")

        best_score = -float('inf')
        best_params = None
        best_metrics = None
        all_results = []

        for i, combination in enumerate(itertools.product(*param_values)):
            params = dict(zip(param_names, combination))
            logger.info(f"  [{i+1}/{total_combinations}] Testing: {params}")

            results = self.run_backtest(params, days=days)

            if results and 'metrics' in results:
                metrics = results['metrics']
                # Score: weighted combination of metrics
                score = (
                    metrics.get('win_rate', 0) * 100 +
                    metrics.get('sharpe_ratio', 0) * 10 +
                    metrics.get('profit_factor', 0) * 20 -
                    metrics.get('max_drawdown', 1) * 50
                )

                all_results.append({
                    'params': params,
                    'metrics': metrics,
                    'score': score
                })

                if score > best_score:
                    best_score = score
                    best_params = params
                    best_metrics = metrics
                    logger.info(f"  ⭐ NEW BEST: score={score:.2f}, win_rate={metrics.get('win_rate', 0)*100:.1f}%")

        # Sort by score
        all_results.sort(key=lambda x: x['score'], reverse=True)

        grid_result = {
            'best_params': best_params,
            'best_metrics': best_metrics,
            'best_score': best_score,
            'total_tested': total_combinations,
            'top_5': all_results[:5]
        }

        # Save grid search results
        grid_file = self.results_dir / f'grid_search_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(grid_file, 'w') as f:
            json.dump(grid_result, f, indent=2, default=str)

        logger.info(f"✅ Grid Search Complete! Best score: {best_score:.2f}")
        logger.info(f"   Best params: {best_params}")

        return grid_result

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🧠 BAYESIAN OPTIMIZATION
    # ═══════════════════════════════════════════════════════════════════════════════

    def run_bayesian_optimization(self, n_iterations: int = 20, days: int = 60) -> Dict:
        """
        Bayesian optimization using Gaussian Process surrogate model.
        More efficient than grid search for finding optimal parameters.
        """
        logger.info(f"🧠 BAYESIAN OPTIMIZATION: Running {n_iterations} iterations...")

        # Convert parameter space to continuous bounds
        bounds = {
            'take_profit_pct': (0.05, 0.15),
            'stop_loss_pct': (0.02, 0.05),
            'position_size_pct': (0.03, 0.10),
            'min_confidence': (0.45, 0.65),
            'trailing_stop_pct': (0.02, 0.04)
        }

        # History for Bayesian updates
        X_history = []  # Parameter combinations tried
        y_history = []  # Scores achieved

        best_score = -float('inf')
        best_params = None
        best_metrics = None

        for iteration in range(n_iterations):
            # Acquisition function: Expected Improvement with exploration
            if iteration < 5:
                # Initial random exploration
                params = {k: np.random.uniform(v[0], v[1]) for k, v in bounds.items()}
            else:
                # Bayesian-guided selection (simplified)
                params = self._bayesian_next_point(X_history, y_history, bounds)

            logger.info(f"  [{iteration+1}/{n_iterations}] Testing: {params}")

            results = self.run_backtest(params, days=days)

            if results and 'metrics' in results:
                metrics = results['metrics']
                # Multi-objective score
                score = self._calculate_optimization_score(metrics)

                X_history.append(list(params.values()))
                y_history.append(score)

                if score > best_score:
                    best_score = score
                    best_params = params
                    best_metrics = metrics
                    logger.info(f"  ⭐ NEW BEST: score={score:.2f}")

        bayesian_result = {
            'best_params': best_params,
            'best_metrics': best_metrics,
            'best_score': best_score,
            'iterations': n_iterations,
            'exploration_history': [
                {'params': dict(zip(bounds.keys(), x)), 'score': y}
                for x, y in zip(X_history, y_history)
            ]
        }

        # Save results
        bayes_file = self.results_dir / f'bayesian_opt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(bayes_file, 'w') as f:
            json.dump(bayesian_result, f, indent=2, default=str)

        logger.info(f"✅ Bayesian Optimization Complete!")
        logger.info(f"   Best score: {best_score:.2f}")
        logger.info(f"   Best params: {best_params}")

        return bayesian_result

    def _calculate_optimization_score(self, metrics: Dict) -> float:
        """Calculate weighted optimization score from metrics"""
        win_rate = metrics.get('win_rate', 0)
        sharpe = max(metrics.get('sharpe_ratio', -5), -5)  # Clip extreme negative
        profit_factor = metrics.get('profit_factor', 0)
        max_dd = metrics.get('max_drawdown', 1)
        total_return = metrics.get('total_return_pct', 0) / 100

        # Weighted score (higher is better)
        score = (
            win_rate * 40 +                    # Win rate contribution
            sharpe * 15 +                      # Risk-adjusted return
            profit_factor * 20 +               # Profit quality
            (1 - max_dd) * 15 +               # Drawdown penalty
            max(total_return, -1) * 10        # Total return
        )
        return score

    def _bayesian_next_point(self, X_history: List, y_history: List, bounds: Dict) -> Dict:
        """
        Select next point to evaluate using simplified Bayesian approach.
        Uses Upper Confidence Bound (UCB) acquisition.
        """
        if len(X_history) < 3:
            # Not enough data, return random point
            return {k: np.random.uniform(v[0], v[1]) for k, v in bounds.items()}

        X = np.array(X_history)
        y = np.array(y_history)

        # Normalize y for stability
        y_mean = np.mean(y)
        y_std = max(np.std(y), 1e-6)
        y_norm = (y - y_mean) / y_std

        # Generate candidate points
        n_candidates = 100
        candidates = []
        for _ in range(n_candidates):
            point = {k: np.random.uniform(v[0], v[1]) for k, v in bounds.items()}
            candidates.append(list(point.values()))

        candidates = np.array(candidates)

        # Simple UCB: predict mean + exploration bonus
        # Use weighted average of nearest neighbors as surrogate
        best_ucb = -float('inf')
        best_idx = 0

        for i, cand in enumerate(candidates):
            # Distance to historical points
            distances = np.sqrt(np.sum((X - cand) ** 2, axis=1))
            weights = 1 / (distances + 1e-6)
            weights /= np.sum(weights)

            # Predicted value (weighted average)
            pred_mean = np.sum(weights * y_norm)

            # Exploration bonus (higher for points far from explored)
            exploration = 0.5 * np.log(len(X_history)) * np.min(distances)

            ucb = pred_mean + exploration

            if ucb > best_ucb:
                best_ucb = ucb
                best_idx = i

        return dict(zip(bounds.keys(), candidates[best_idx]))

    def update_live_trading_params(self, params: Dict[str, float]):
        """Update live trading parameters in launch script"""
        logger.info(f"🔧 Updating live trading parameters: {params}")

        # Save optimized parameters to file for reference
        params_file = self.results_dir / 'optimized_parameters.json'
        with open(params_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'parameters': params,
                'iteration': self.state.iteration
            }, f, indent=2)

        logger.info(f"💾 Optimized parameters saved to {params_file}")

    def run_optimization_cycle(self, max_iterations: int = 10, min_trades: int = 10) -> Dict:
        """Run complete optimization cycle"""
        logger.info("=" * 70)
        logger.info("🔄 STARTING PROMETHEUS CONTINUOUS IMPROVEMENT CYCLE")
        logger.info("=" * 70)

        self.load_state()

        # Initial parameters
        if not self.state.current_parameters:
            self.state.current_parameters = {
                'take_profit_pct': 0.10,
                'stop_loss_pct': 0.03,
                'position_size_pct': 0.05,
                'min_confidence': 0.50,
                'trailing_stop_pct': 0.025
            }

        results_summary = {
            'iterations_completed': 0,
            'improvement_achieved': False,
            'deployment_ready': False,
            'best_metrics': {},
            'history': []
        }

        for iteration in range(self.state.iteration, self.state.iteration + max_iterations):
            self.state.iteration = iteration + 1
            logger.info(f"\n{'='*60}")
            logger.info(f"📍 ITERATION {self.state.iteration}")
            logger.info(f"{'='*60}")

            # Step 1: Run training on accumulated data
            logger.info("\n🧠 Step 1: Running supervised learning training...")
            training_results = self.run_training(min_trades=min_trades)
            if training_results:
                # TrainingMetrics is a dataclass, not a dict
                success_rate = getattr(training_results, 'success_rate', 0) if hasattr(training_results, 'success_rate') else training_results.get('success_rate', 0) if isinstance(training_results, dict) else 0
                logger.info(f"   Training complete: {success_rate:.1%} success rate")

            # Step 2: Run backtest with current parameters
            logger.info("\n📈 Step 2: Running backtest with current parameters...")
            backtest_results = self.run_backtest(self.state.current_parameters)

            if not backtest_results:
                logger.warning("   Backtest failed, skipping iteration")
                continue

            # Step 3: Evaluate against benchmarks
            logger.info("\n📊 Step 3: Evaluating performance against benchmarks...")
            evaluation = self.evaluate_performance(backtest_results)

            metrics = evaluation['metrics']
            targets = evaluation['targets_met']

            logger.info(f"   Win Rate: {metrics['win_rate']:.1%} (target: {self.benchmarks.target_win_rate:.0%}) {'✅' if targets['win_rate'] else '❌'}")
            logger.info(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f} (target: {self.benchmarks.target_sharpe_ratio:.1f}) {'✅' if targets['sharpe_ratio'] else '❌'}")
            logger.info(f"   Max Drawdown: {metrics['max_drawdown']:.1%} (target: <{self.benchmarks.target_max_drawdown:.0%}) {'✅' if targets['max_drawdown'] else '❌'}")
            logger.info(f"   Profit Factor: {metrics['profit_factor']:.2f} (target: {self.benchmarks.target_profit_factor:.1f}) {'✅' if targets['profit_factor'] else '❌'}")

            # Update best metrics
            if metrics['win_rate'] > self.state.best_win_rate:
                self.state.best_win_rate = metrics['win_rate']
            if metrics['sharpe_ratio'] > self.state.best_sharpe_ratio:
                self.state.best_sharpe_ratio = metrics['sharpe_ratio']
            if metrics['max_drawdown'] < self.state.best_max_drawdown:
                self.state.best_max_drawdown = metrics['max_drawdown']
            if metrics['profit_factor'] > self.state.best_profit_factor:
                self.state.best_profit_factor = metrics['profit_factor']

            # Record iteration
            iteration_record = {
                'iteration': self.state.iteration,
                'timestamp': datetime.now().isoformat(),
                'parameters': self.state.current_parameters.copy(),
                'metrics': metrics,
                'targets_met': targets,
                'deployment_ready': evaluation['deployment_ready']
            }
            self.state.improvement_history.append(iteration_record)
            results_summary['history'].append(iteration_record)

            # Check if deployment ready
            if evaluation['deployment_ready']:
                logger.info("\n🎉 ALL TARGETS MET - PROMETHEUS IS DEPLOYMENT READY!")
                self.state.deployment_ready = True
                self.state.targets_met = targets
                self.update_live_trading_params(self.state.current_parameters)
                results_summary['deployment_ready'] = True
                break

            # Step 4: Optimize parameters for next iteration
            logger.info("\n🔧 Step 4: Optimizing parameters for next iteration...")
            self.state.current_parameters = self.optimize_parameters(
                backtest_results,
                self.state.current_parameters
            )
            logger.info(f"   New parameters: {self.state.current_parameters}")

            # Save state after each iteration
            self.save_state()
            results_summary['iterations_completed'] = self.state.iteration

        # Final summary
        results_summary['best_metrics'] = {
            'best_win_rate': self.state.best_win_rate,
            'best_sharpe_ratio': self.state.best_sharpe_ratio,
            'best_max_drawdown': self.state.best_max_drawdown,
            'best_profit_factor': self.state.best_profit_factor
        }

        # Save final results
        results_file = self.results_dir / f'optimization_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump(results_summary, f, indent=2, default=str)

        logger.info(f"\n{'='*60}")
        logger.info("🏁 OPTIMIZATION CYCLE COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"   Iterations: {results_summary['iterations_completed']}")
        logger.info(f"   Best Win Rate: {self.state.best_win_rate:.1%}")
        logger.info(f"   Best Sharpe: {self.state.best_sharpe_ratio:.2f}")
        logger.info(f"   Deployment Ready: {'YES ✅' if results_summary['deployment_ready'] else 'NOT YET ❌'}")

        return results_summary

    def get_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report for dashboard"""
        self.load_state()

        report = {
            'current_iteration': self.state.iteration,
            'deployment_ready': self.state.deployment_ready,
            'best_metrics': {
                'win_rate': self.state.best_win_rate,
                'sharpe_ratio': self.state.best_sharpe_ratio,
                'max_drawdown': self.state.best_max_drawdown,
                'profit_factor': self.state.best_profit_factor
            },
            'current_parameters': self.state.current_parameters,
            'targets': {
                'win_rate': self.benchmarks.target_win_rate,
                'sharpe_ratio': self.benchmarks.target_sharpe_ratio,
                'max_drawdown': self.benchmarks.target_max_drawdown,
                'profit_factor': self.benchmarks.target_profit_factor,
                'daily_return_range': [
                    self.benchmarks.target_daily_return_min,
                    self.benchmarks.target_daily_return_max
                ]
            },
            'targets_met': self.state.targets_met,
            'improvement_history': self.state.improvement_history[-20:],  # Last 20 iterations
            'progress_pct': self._calculate_progress_pct(),
            'benchmarks': self.benchmarks.to_dict(),
            'timestamp': datetime.now().isoformat()
        }

        return report

    def _calculate_progress_pct(self) -> float:
        """Calculate overall progress toward deployment readiness"""
        if not self.state.targets_met:
            return 0.0

        progress_items = [
            min(self.state.best_win_rate / self.benchmarks.target_win_rate, 1.0),
            min(self.state.best_sharpe_ratio / self.benchmarks.target_sharpe_ratio, 1.0),
            min(self.benchmarks.target_max_drawdown / max(self.state.best_max_drawdown, 0.01), 1.0),
            min(self.state.best_profit_factor / self.benchmarks.target_profit_factor, 1.0)
        ]

        return sum(progress_items) / len(progress_items)


# ═══════════════════════════════════════════════════════════════════════════════
# 🏃 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_continuous_improvement(
    max_iterations: int = 10,
    min_trades: int = 10,
    report_only: bool = False
) -> Dict:
    """
    Run the PROMETHEUS continuous improvement cycle

    Args:
        max_iterations: Maximum optimization iterations to run
        min_trades: Minimum trades required for training
        report_only: If True, only generate report without running optimization

    Returns:
        Optimization results or progress report
    """
    engine = ContinuousImprovementEngine()

    if report_only:
        return engine.get_progress_report()

    return engine.run_optimization_cycle(
        max_iterations=max_iterations,
        min_trades=min_trades
    )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='PROMETHEUS Continuous Improvement Cycle')
    parser.add_argument('--iterations', type=int, default=5, help='Max iterations to run')
    parser.add_argument('--min-trades', type=int, default=10, help='Min trades for training')
    parser.add_argument('--report', action='store_true', help='Generate report only')
    parser.add_argument('--grid-search', action='store_true', help='Run grid search optimization')
    parser.add_argument('--bayesian', action='store_true', help='Run Bayesian optimization')
    parser.add_argument('--days', type=int, default=60, help='Backtest period in days')

    args = parser.parse_args()

    engine = ContinuousImprovementEngine()

    if args.report:
        results = engine.get_progress_report()
    elif args.grid_search:
        # Run grid search with focused parameter subset
        param_subset = {
            'take_profit_pct': [0.08, 0.10, 0.12],
            'stop_loss_pct': [0.02, 0.03, 0.04],
            'position_size_pct': [0.05, 0.08],
            'min_confidence': [0.45, 0.50, 0.55]
        }
        results = engine.run_grid_search(param_subset=param_subset, days=args.days)
    elif args.bayesian:
        results = engine.run_bayesian_optimization(n_iterations=args.iterations, days=args.days)
    else:
        results = engine.run_optimization_cycle(
            max_iterations=args.iterations,
            min_trades=args.min_trades
        )

    print("\n" + "=" * 60)
    print(json.dumps(results, indent=2, default=str))

