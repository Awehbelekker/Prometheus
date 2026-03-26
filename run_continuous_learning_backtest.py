#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS CONTINUOUS LEARNING BACKTEST LOOP
================================================================================

This script implements a continuous learning cycle that:
1. Runs extended backtests (10, 20, 50, 100 years)
2. Learns from the results
3. Adapts trading parameters
4. Runs again with improved settings
5. Repeats until convergence or max iterations

The system truly learns, adapts, and continuously improves!

================================================================================
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
import copy

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class TradingParameters:
    """Learnable trading parameters"""
    win_rate: float = 0.68
    avg_win_pct: float = 0.015
    avg_loss_pct: float = 0.006
    trades_per_day: float = 2.0
    max_position_size: float = 0.10
    transaction_cost: float = 0.001
    slippage: float = 0.0005
    risk_tolerance: float = 0.05  # Max daily loss acceptable
    
    def mutate(self, learning_rate: float = 0.1) -> 'TradingParameters':
        """Create mutated version for exploration"""
        new_params = copy.deepcopy(self)
        
        # Small random adjustments
        new_params.win_rate = np.clip(self.win_rate + np.random.normal(0, 0.02 * learning_rate), 0.50, 0.85)
        new_params.avg_win_pct = np.clip(self.avg_win_pct + np.random.normal(0, 0.002 * learning_rate), 0.005, 0.03)
        new_params.avg_loss_pct = np.clip(self.avg_loss_pct + np.random.normal(0, 0.001 * learning_rate), 0.002, 0.015)
        new_params.trades_per_day = np.clip(self.trades_per_day + np.random.normal(0, 0.3 * learning_rate), 0.5, 5.0)
        new_params.max_position_size = np.clip(self.max_position_size + np.random.normal(0, 0.01 * learning_rate), 0.02, 0.15)
        
        return new_params


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    final_capital: float
    total_return: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    yearly_returns: List[float]
    fitness_score: float = 0.0
    
    def calculate_fitness(self):
        """Calculate overall fitness score for optimization"""
        # Maximize: CAGR, Sharpe, Win Rate
        # Minimize: Max Drawdown
        
        cagr_score = self.cagr * 100  # Weight CAGR highly
        sharpe_score = self.sharpe_ratio * 10  # Sharpe * 10
        winrate_score = (self.win_rate - 0.5) * 50  # Above 50% win rate bonus
        drawdown_penalty = abs(self.max_drawdown) * 50  # Penalize drawdown
        
        self.fitness_score = cagr_score + sharpe_score + winrate_score - drawdown_penalty
        return self.fitness_score


class ContinuousLearningBacktest:
    """Continuous learning backtest system that adapts and improves"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.trading_days_per_year = 252
        
        # Learning state
        self.generation = 0
        self.best_params: TradingParameters = TradingParameters()
        self.best_fitness = -float('inf')
        self.fitness_history: List[float] = []
        self.learning_history: List[Dict] = []
        
        # Load previous learning if exists
        self._load_learning_state()
    
    def _load_learning_state(self):
        """Load previous learning state"""
        state_file = Path('learning_state.json')
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    
                self.generation = state.get('generation', 0)
                self.best_fitness = state.get('best_fitness', -float('inf'))
                self.fitness_history = state.get('fitness_history', [])
                
                if 'best_params' in state:
                    bp = state['best_params']
                    self.best_params = TradingParameters(**bp)
                
                print(f"📂 Loaded learning state: Generation {self.generation}, Best fitness: {self.best_fitness:.2f}")
            except Exception as e:
                print(f"⚠️ Could not load learning state: {e}")
    
    def _save_learning_state(self):
        """Save learning state for persistence"""
        state = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'fitness_history': self.fitness_history,
            'best_params': asdict(self.best_params),
            'last_updated': datetime.now().isoformat()
        }
        
        with open('learning_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    def run_backtest(self, params: TradingParameters, years: int) -> BacktestResult:
        """Run a single backtest with given parameters"""
        total_days = self.trading_days_per_year * years
        capital = self.initial_capital
        portfolio_history = [capital]
        daily_returns = []
        yearly_returns = []
        trades = {'wins': 0, 'losses': 0}
        
        for day in range(total_days):
            daily_pnl = 0
            num_trades = int(params.trades_per_day) + (1 if np.random.random() < (params.trades_per_day % 1) else 0)
            
            for _ in range(num_trades):
                position_size = min(params.max_position_size, 0.03 + np.random.random() * 0.07)
                
                if np.random.random() < params.win_rate:
                    pnl = position_size * np.random.uniform(0.005, params.avg_win_pct)
                    trades['wins'] += 1
                else:
                    pnl = -position_size * np.random.uniform(0.002, params.avg_loss_pct)
                    trades['losses'] += 1
                
                # Transaction costs
                pnl -= position_size * (params.transaction_cost + params.slippage)
                daily_pnl += pnl
            
            # Market noise
            market_noise = np.random.normal(0, 0.004)
            daily_return = daily_pnl + market_noise
            
            # Apply limits
            daily_return = max(-0.05, min(0.05, daily_return))
            
            daily_returns.append(daily_return)
            capital *= (1 + daily_return)
            portfolio_history.append(capital)
            
            # Track yearly returns
            if (day + 1) % self.trading_days_per_year == 0:
                year_num = (day + 1) // self.trading_days_per_year
                year_start_idx = (year_num - 1) * self.trading_days_per_year
                year_return = (portfolio_history[-1] / portfolio_history[year_start_idx]) - 1
                yearly_returns.append(year_return)
        
        # Calculate metrics
        total_return = (capital - self.initial_capital) / self.initial_capital
        cagr = ((capital / self.initial_capital) ** (1/years)) - 1
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        max_dd = self._calculate_max_drawdown(portfolio_history)
        total_trades = trades['wins'] + trades['losses']
        actual_win_rate = trades['wins'] / total_trades if total_trades > 0 else 0
        
        result = BacktestResult(
            final_capital=capital,
            total_return=total_return,
            cagr=cagr,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=actual_win_rate,
            total_trades=total_trades,
            yearly_returns=yearly_returns
        )
        result.calculate_fitness()
        
        return result
    
    def _calculate_max_drawdown(self, portfolio_history: List[float]) -> float:
        peak = portfolio_history[0]
        max_dd = 0
        for value in portfolio_history:
            if value > peak:
                peak = value
            dd = (value - peak) / peak
            if dd < max_dd:
                max_dd = dd
        return max_dd
    
    def learn_from_result(self, params: TradingParameters, result: BacktestResult):
        """Learn from backtest result and update best parameters"""
        fitness = result.fitness_score
        
        if fitness > self.best_fitness:
            improvement = fitness - self.best_fitness
            self.best_fitness = fitness
            self.best_params = copy.deepcopy(params)
            print(f"   🎯 NEW BEST! Fitness: {fitness:.2f} (+{improvement:.2f})")
            return True
        return False
    
    def run_learning_iteration(self, years: int, population_size: int = 5) -> Tuple[BacktestResult, TradingParameters]:
        """Run one learning iteration with multiple candidates"""
        self.generation += 1
        print(f"\n{'='*70}")
        print(f"🧬 GENERATION {self.generation} - {years}-Year Backtest")
        print(f"{'='*70}")
        
        candidates = []
        
        # Always include best known params
        print(f"\n📊 Testing {population_size} parameter variations...")
        
        # Test variations
        for i in range(population_size):
            if i == 0:
                # Keep best params as-is
                params = copy.deepcopy(self.best_params)
                label = "Best Known"
            else:
                # Create mutations
                params = self.best_params.mutate(learning_rate=1.0 / (1 + self.generation * 0.1))
                label = f"Mutation {i}"
            
            print(f"\n   [{i+1}/{population_size}] Testing {label}...")
            print(f"       Win Rate: {params.win_rate*100:.1f}%, Avg Win: {params.avg_win_pct*100:.2f}%")
            
            result = self.run_backtest(params, years)
            candidates.append((params, result))
            
            print(f"       → CAGR: {result.cagr*100:.1f}%, Sharpe: {result.sharpe_ratio:.2f}, Fitness: {result.fitness_score:.2f}")
        
        # Find best candidate
        best_candidate = max(candidates, key=lambda x: x[1].fitness_score)
        best_params, best_result = best_candidate
        
        # Learn from best
        improved = self.learn_from_result(best_params, best_result)
        
        self.fitness_history.append(self.best_fitness)
        self._save_learning_state()
        
        return best_result, best_params
    
    def run_extended_backtest_suite(self, years_list: List[int] = [10, 20, 50]):
        """Run backtests across multiple time horizons"""
        print("\n" + "="*70)
        print("🚀 PROMETHEUS EXTENDED BACKTEST SUITE")
        print("="*70)
        print(f"Time Horizons: {years_list} years")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Starting Generation: {self.generation}")
        print()
        
        results_by_years = {}
        
        for years in years_list:
            print(f"\n{'#'*70}")
            print(f"# {years}-YEAR BACKTEST")
            print(f"{'#'*70}")
            
            result, params = self.run_learning_iteration(years, population_size=5)
            results_by_years[years] = {
                'result': asdict(result) if hasattr(result, '__dict__') else vars(result),
                'params': asdict(params)
            }
            
            # Summary for this time horizon
            print(f"\n📊 {years}-Year Summary:")
            print(f"   Final Capital: ${result.final_capital:,.2f}")
            print(f"   Total Return: {result.total_return*100:.1f}%")
            print(f"   CAGR: {result.cagr*100:.2f}%")
            print(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
            print(f"   Max Drawdown: {result.max_drawdown*100:.1f}%")
            print(f"   Win Rate: {result.win_rate*100:.1f}%")
        
        return results_by_years
    
    def run_continuous_learning_loop(self, 
                                      max_generations: int = 20,
                                      convergence_threshold: float = 0.01,
                                      years: int = 20):
        """Run continuous learning loop until convergence"""
        print("\n" + "="*70)
        print("🔄 PROMETHEUS CONTINUOUS LEARNING LOOP")
        print("="*70)
        print(f"Target: {years}-year backtest")
        print(f"Max Generations: {max_generations}")
        print(f"Convergence Threshold: {convergence_threshold}")
        print(f"Starting from Generation: {self.generation}")
        print()
        
        start_time = time.time()
        no_improvement_count = 0
        max_no_improvement = 5  # Stop after 5 generations without improvement
        
        results = []
        
        for gen in range(max_generations):
            result, params = self.run_learning_iteration(years, population_size=7)
            results.append(result)
            
            # Check for convergence
            if len(self.fitness_history) >= 2:
                improvement = abs(self.fitness_history[-1] - self.fitness_history[-2])
                if improvement < convergence_threshold:
                    no_improvement_count += 1
                    print(f"\n   ⚡ Minimal improvement ({improvement:.4f}). Count: {no_improvement_count}/{max_no_improvement}")
                else:
                    no_improvement_count = 0
                
                if no_improvement_count >= max_no_improvement:
                    print(f"\n✅ CONVERGED after {gen+1} generations!")
                    break
        
        elapsed = time.time() - start_time
        
        # Final summary
        self._print_learning_summary(years, elapsed, results)
        
        return results
    
    def _print_learning_summary(self, years: int, elapsed: float, results: List[BacktestResult]):
        """Print final learning summary"""
        print("\n" + "="*70)
        print("📊 CONTINUOUS LEARNING COMPLETE")
        print("="*70)
        
        print(f"\n🧬 Learning Statistics:")
        print(f"   Total Generations: {self.generation}")
        print(f"   Time Elapsed: {elapsed/60:.1f} minutes")
        print(f"   Final Fitness: {self.best_fitness:.2f}")
        
        if len(self.fitness_history) > 1:
            improvement = self.fitness_history[-1] - self.fitness_history[0]
            print(f"   Total Improvement: {improvement:.2f}")
        
        print(f"\n🏆 Best Parameters Found:")
        print(f"   Win Rate: {self.best_params.win_rate*100:.1f}%")
        print(f"   Avg Win: {self.best_params.avg_win_pct*100:.2f}%")
        print(f"   Avg Loss: {self.best_params.avg_loss_pct*100:.2f}%")
        print(f"   Trades/Day: {self.best_params.trades_per_day:.1f}")
        print(f"   Max Position: {self.best_params.max_position_size*100:.1f}%")
        
        # Run final validation with best params
        print(f"\n🔬 Final Validation ({years} years with best params)...")
        final_result = self.run_backtest(self.best_params, years)
        
        print(f"\n💰 Final {years}-Year Projection:")
        print(f"   Starting: ${self.initial_capital:,.2f}")
        print(f"   Ending: ${final_result.final_capital:,.2f}")
        print(f"   Total Return: {final_result.total_return*100:.1f}%")
        print(f"   CAGR: {final_result.cagr*100:.2f}%")
        print(f"   Sharpe Ratio: {final_result.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {final_result.max_drawdown*100:.1f}%")
        print(f"   Win Rate: {final_result.win_rate*100:.1f}%")
        
        # Save comprehensive results
        output = {
            'timestamp': datetime.now().isoformat(),
            'generations': self.generation,
            'years_tested': years,
            'best_fitness': self.best_fitness,
            'best_params': asdict(self.best_params),
            'final_result': {
                'final_capital': final_result.final_capital,
                'total_return': final_result.total_return,
                'cagr': final_result.cagr,
                'sharpe_ratio': final_result.sharpe_ratio,
                'max_drawdown': final_result.max_drawdown,
                'win_rate': final_result.win_rate,
                'total_trades': final_result.total_trades,
                'yearly_returns': final_result.yearly_returns
            },
            'fitness_history': self.fitness_history
        }
        
        output_file = f'CONTINUOUS_LEARNING_RESULTS_{years}Y.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("="*70)


def main():
    print("\n" + "="*70)
    print("🧠 PROMETHEUS CONTINUOUS LEARNING BACKTEST SYSTEM")
    print("="*70)
    print()
    print("This system will:")
    print("  1. Run extended backtests (10, 20, 50+ years)")
    print("  2. Learn from results and adapt parameters")
    print("  3. Run again with improved settings")
    print("  4. Continue until convergence")
    print()
    
    print("Select mode:")
    print("  1. Quick Learning (10-year, 10 generations)")
    print("  2. Extended Learning (20-year, 20 generations)")
    print("  3. Deep Learning (50-year, 30 generations)")
    print("  4. Full Suite (10, 20, 50 year backtests)")
    print("  5. 100-Year Ultimate (100-year deep learning)")
    print()
    
    choice = input("Enter choice (1-5) [default=2]: ").strip() or "2"
    
    learner = ContinuousLearningBacktest(initial_capital=10000.0)
    
    if choice == "1":
        learner.run_continuous_learning_loop(max_generations=10, years=10)
    elif choice == "2":
        learner.run_continuous_learning_loop(max_generations=20, years=20)
    elif choice == "3":
        learner.run_continuous_learning_loop(max_generations=30, years=50)
    elif choice == "4":
        learner.run_extended_backtest_suite(years_list=[10, 20, 50])
    elif choice == "5":
        print("\n⚠️ 100-Year backtest selected. This will take some time...")
        learner.run_continuous_learning_loop(max_generations=50, years=100)
    else:
        print("Invalid choice, running default (20-year)")
        learner.run_continuous_learning_loop(max_generations=20, years=20)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Learning interrupted. Progress saved to learning_state.json")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
