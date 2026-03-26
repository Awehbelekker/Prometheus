"""
PROMETHEUS COMPREHENSIVE BENCHMARK SYSTEM
Test Prometheus AI against multiple strategies and market conditions
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_continuous_learning_backtest import ContinuousLearningBacktest, TradingParameters


class PrometheusBenchmark:
    """Comprehensive benchmark system for Prometheus AI"""
    
    def __init__(self):
        self.results = {}
        self.prometheus_params = None
        
    def load_prometheus_best_params(self):
        """Load Prometheus's best learned parameters"""
        
        # Try live config first
        if os.path.exists('live_ai_config.json'):
            with open('live_ai_config.json', 'r') as f:
                config = json.load(f)
                params_dict = config.get('parameters', {})
                
                self.prometheus_params = TradingParameters(
                    win_rate=params_dict.get('win_rate', 0.711),
                    avg_win_pct=params_dict.get('avg_win_pct', 0.03),
                    avg_loss_pct=params_dict.get('avg_loss_pct', 0.0045),
                    trades_per_day=params_dict.get('trades_per_day', 8),
                    max_position_size=params_dict.get('max_position_size', 0.12),
                    transaction_cost=params_dict.get('transaction_cost', 0.001),
                    slippage=params_dict.get('slippage', 0.0005),
                    risk_tolerance=params_dict.get('risk_tolerance', 0.05)
                )
                return True
        
        # Fallback to learning state
        if os.path.exists('learning_state.json'):
            with open('learning_state.json', 'r') as f:
                state = json.load(f)
                params_dict = state.get('best_params', {})
                
                self.prometheus_params = TradingParameters(
                    win_rate=params_dict.get('win_rate', 0.711),
                    avg_win_pct=params_dict.get('avg_win_pct', 0.03),
                    avg_loss_pct=params_dict.get('avg_loss_pct', 0.0045),
                    trades_per_day=params_dict.get('trades_per_day', 8),
                    max_position_size=params_dict.get('max_position_size', 0.12),
                    transaction_cost=params_dict.get('transaction_cost', 0.001),
                    slippage=params_dict.get('slippage', 0.0005),
                    risk_tolerance=params_dict.get('risk_tolerance', 0.05)
                )
                return True
        
        return False
    
    def create_baseline_strategies(self):
        """Create baseline strategies to compare against"""
        
        strategies = {
            'Buy and Hold': TradingParameters(
                win_rate=0.55,
                avg_win_pct=0.10,  # Large wins
                avg_loss_pct=0.05,  # Large losses
                trades_per_day=0.01,  # Almost never trade
                max_position_size=1.0,  # Full position
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.20  # High tolerance
            ),
            
            'Conservative': TradingParameters(
                win_rate=0.60,
                avg_win_pct=0.01,
                avg_loss_pct=0.005,
                trades_per_day=1.0,
                max_position_size=0.05,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.02
            ),
            
            'Aggressive': TradingParameters(
                win_rate=0.55,
                avg_win_pct=0.04,
                avg_loss_pct=0.02,
                trades_per_day=15.0,
                max_position_size=0.25,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.10
            ),
            
            'Momentum': TradingParameters(
                win_rate=0.58,
                avg_win_pct=0.025,
                avg_loss_pct=0.01,
                trades_per_day=5.0,
                max_position_size=0.15,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.06
            ),
            
            'Mean Reversion': TradingParameters(
                win_rate=0.65,
                avg_win_pct=0.015,
                avg_loss_pct=0.01,
                trades_per_day=10.0,
                max_position_size=0.10,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.04
            ),
            
            'Random Walk': TradingParameters(
                win_rate=0.50,
                avg_win_pct=0.02,
                avg_loss_pct=0.02,
                trades_per_day=3.0,
                max_position_size=0.10,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.05
            )
        }
        
        return strategies
    
    def run_benchmark(self, years=20):
        """Run comprehensive benchmark"""
        
        print("\n" + "="*80)
        print("🏁 PROMETHEUS COMPREHENSIVE BENCHMARK")
        print("="*80)
        print()
        
        # Load Prometheus params
        if not self.load_prometheus_best_params():
            print("❌ Could not load Prometheus parameters!")
            return
        
        print("✅ Loaded Prometheus AI parameters")
        print(f"   Win Rate: {self.prometheus_params.win_rate*100:.2f}%")
        print(f"   Avg Win: {self.prometheus_params.avg_win_pct*100:.2f}%")
        print(f"   Trades/Day: {self.prometheus_params.trades_per_day:.1f}")
        print()
        
        # Create baseline strategies
        strategies = self.create_baseline_strategies()
        
        print(f"📊 Testing {len(strategies)+1} strategies over {years} years:")
        print("   1. Prometheus AI (learned)")
        for i, name in enumerate(strategies.keys(), 2):
            print(f"   {i}. {name}")
        print()
        
        proceed = input("Run benchmark? (yes/no) [yes]: ").strip().lower() or "yes"
        if proceed not in ['yes', 'y']:
            print("Cancelled.")
            return
        
        print("\n" + "="*80)
        print("🚀 RUNNING BENCHMARKS...")
        print("="*80)
        print()
        
        backtest = ContinuousLearningBacktest()
        
        # Test Prometheus
        print("🤖 Testing Prometheus AI...")
        prometheus_result = backtest.run_backtest(self.prometheus_params, years)
        self.results['Prometheus AI'] = prometheus_result
        print(f"   ✅ CAGR: {prometheus_result.cagr*100:.1f}%, Sharpe: {prometheus_result.sharpe_ratio:.2f}")
        print()
        
        # Test each baseline strategy
        for name, params in strategies.items():
            print(f"📈 Testing {name}...")
            result = backtest.run_backtest(params, years)
            self.results[name] = result
            print(f"   ✅ CAGR: {result.cagr*100:.1f}%, Sharpe: {result.sharpe_ratio:.2f}")
            print()
        
        self.print_results()
        self.save_results(years)
    
    def print_results(self):
        """Print comprehensive results"""
        
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80)
        print()
        
        # Sort by fitness score
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].fitness_score,
            reverse=True
        )
        
        print(f"{'Rank':<6} {'Strategy':<20} {'CAGR':<10} {'Sharpe':<10} {'Win Rate':<12} {'Max DD':<10} {'Fitness':<10}")
        print("-" * 80)
        
        for rank, (name, result) in enumerate(sorted_results, 1):
            cagr = f"{result.cagr*100:.1f}%"
            sharpe = f"{result.sharpe_ratio:.2f}"
            win_rate = f"{result.win_rate*100:.1f}%"
            max_dd = f"{result.max_drawdown:.1f}%"
            fitness = f"{result.fitness_score:.2f}"
            
            marker = "👑" if name == "Prometheus AI" else "  "
            print(f"{marker}{rank:<5} {name:<20} {cagr:<10} {sharpe:<10} {win_rate:<12} {max_dd:<10} {fitness:<10}")
        
        print()
        
        # Performance comparison
        prometheus_result = self.results.get('Prometheus AI')
        if prometheus_result:
            print("="*80)
            print("🏆 PROMETHEUS AI PERFORMANCE VS COMPETITORS")
            print("="*80)
            print()
            
            for name, result in self.results.items():
                if name == 'Prometheus AI':
                    continue
                
                cagr_diff = (prometheus_result.cagr - result.cagr) * 100
                sharpe_diff = prometheus_result.sharpe_ratio - result.sharpe_ratio
                
                print(f"vs {name}:")
                print(f"   CAGR: {cagr_diff:+.1f}% better")
                print(f"   Sharpe: {sharpe_diff:+.2f} better")
                print()
            
            # Overall statistics
            print("="*80)
            print("📈 PROMETHEUS AI HIGHLIGHTS")
            print("="*80)
            print()
            print(f"   Final Capital: ${prometheus_result.final_capital:,.2f}")
            print(f"   Total Return: {prometheus_result.total_return*100:,.1f}%")
            print(f"   CAGR: {prometheus_result.cagr*100:.2f}%")
            print(f"   Sharpe Ratio: {prometheus_result.sharpe_ratio:.2f}")
            print(f"   Max Drawdown: {prometheus_result.max_drawdown:.2f}%")
            print(f"   Win Rate: {prometheus_result.win_rate*100:.2f}%")
            print(f"   Total Trades: {prometheus_result.total_trades:,}")
            print(f"   Fitness Score: {prometheus_result.fitness_score:.2f}")
            print()
    
    def save_results(self, years):
        """Save benchmark results"""
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_duration_years": years,
            "strategies_tested": len(self.results),
            "results": {}
        }
        
        for name, result in self.results.items():
            results_data["results"][name] = {
                "final_capital": result.final_capital,
                "total_return": result.total_return * 100,
                "cagr": result.cagr * 100,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate * 100,
                "total_trades": result.total_trades,
                "fitness_score": result.fitness_score
            }
        
        # Add rankings
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].fitness_score,
            reverse=True
        )
        
        results_data["rankings"] = [name for name, _ in sorted_results]
        results_data["prometheus_rank"] = results_data["rankings"].index("Prometheus AI") + 1
        
        filename = f"prometheus_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Benchmark results saved to: {filename}")
        print()


class QuickBenchmark:
    """Quick 5-year benchmark for rapid testing"""
    
    def run(self):
        """Run quick benchmark"""
        
        print("\n" + "="*80)
        print("⚡ QUICK BENCHMARK (5 years)")
        print("="*80)
        print()
        
        benchmark = PrometheusBenchmark()
        benchmark.run_benchmark(years=5)


def main():
    print("\n" + "="*80)
    print("🏁 PROMETHEUS BENCHMARK SYSTEM")
    print("="*80)
    print()
    print("Choose benchmark type:")
    print("  1. Quick Benchmark (5 years)")
    print("  2. Standard Benchmark (20 years)")
    print("  3. Comprehensive Benchmark (50 years)")
    print()
    
    choice = input("Enter choice [2]: ").strip() or "2"
    
    benchmark = PrometheusBenchmark()
    
    if choice == "1":
        benchmark.run_benchmark(years=5)
    elif choice == "2":
        benchmark.run_benchmark(years=20)
    elif choice == "3":
        benchmark.run_benchmark(years=50)
    else:
        print("Invalid choice. Running standard benchmark...")
        benchmark.run_benchmark(years=20)
    
    print("="*80)
    print("✅ BENCHMARK COMPLETE!")
    print("="*80)
    print()


if __name__ == "__main__":
    main()
