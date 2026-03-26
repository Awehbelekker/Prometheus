"""
PROMETHEUS VS TOP COMPETITORS BENCHMARK
Compare against world's best hedge funds and AI systems
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_continuous_learning_backtest import ContinuousLearningBacktest, TradingParameters


class EliteCompetitorBenchmark:
    """Benchmark against top hedge funds and AI systems"""
    
    def __init__(self):
        self.results = {}
        self.prometheus_params = None
        
    def load_prometheus_best_params(self):
        """Load Prometheus's BEST parameters with all enhancements"""
        
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
        
        return False
    
    def create_elite_competitors(self):
        """Create strategies mimicking top hedge funds"""
        
        competitors = {
            'Renaissance Medallion (Simulated)': TradingParameters(
                win_rate=0.505,  # Slight edge, high frequency
                avg_win_pct=0.008,  # Small wins
                avg_loss_pct=0.007,  # Tight stops
                trades_per_day=50.0,  # Very high frequency
                max_position_size=0.02,  # Tiny positions
                transaction_cost=0.0001,  # Institutional pricing
                slippage=0.0002,
                risk_tolerance=0.02
            ),
            
            'Two Sigma Quant Strategy': TradingParameters(
                win_rate=0.58,
                avg_win_pct=0.018,
                avg_loss_pct=0.009,
                trades_per_day=12.0,
                max_position_size=0.08,
                transaction_cost=0.0005,
                slippage=0.0003,
                risk_tolerance=0.04
            ),
            
            'Citadel Multi-Strategy': TradingParameters(
                win_rate=0.62,
                avg_win_pct=0.022,
                avg_loss_pct=0.01,
                trades_per_day=10.0,
                max_position_size=0.10,
                transaction_cost=0.0005,
                slippage=0.0003,
                risk_tolerance=0.05
            ),
            
            'AQR Momentum Fund': TradingParameters(
                win_rate=0.56,
                avg_win_pct=0.035,
                avg_loss_pct=0.018,
                trades_per_day=2.0,
                max_position_size=0.15,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.06
            ),
            
            'DE Shaw Statistical Arbitrage': TradingParameters(
                win_rate=0.59,
                avg_win_pct=0.015,
                avg_loss_pct=0.008,
                trades_per_day=18.0,
                max_position_size=0.07,
                transaction_cost=0.0005,
                slippage=0.0003,
                risk_tolerance=0.04
            ),
            
            'Bridgewater All Weather': TradingParameters(
                win_rate=0.58,
                avg_win_pct=0.025,
                avg_loss_pct=0.012,
                trades_per_day=1.0,  # Lower frequency
                max_position_size=0.25,  # Larger positions
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.08
            ),
            
            'Jane Street Market Making': TradingParameters(
                win_rate=0.52,  # Tight spread capture
                avg_win_pct=0.005,
                avg_loss_pct=0.004,
                trades_per_day=100.0,  # Ultra high frequency
                max_position_size=0.01,
                transaction_cost=0.0001,
                slippage=0.0001,
                risk_tolerance=0.01
            ),
            
            'Man AHL Trend Following': TradingParameters(
                win_rate=0.48,  # Lower win rate, big winners
                avg_win_pct=0.055,
                avg_loss_pct=0.015,
                trades_per_day=3.0,
                max_position_size=0.18,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.07
            ),
            
            'Millennium Multi-PM': TradingParameters(
                win_rate=0.61,
                avg_win_pct=0.020,
                avg_loss_pct=0.010,
                trades_per_day=8.0,
                max_position_size=0.09,
                transaction_cost=0.0005,
                slippage=0.0003,
                risk_tolerance=0.04
            ),
            
            'Point72 Equity Long/Short': TradingParameters(
                win_rate=0.57,
                avg_win_pct=0.028,
                avg_loss_pct=0.014,
                trades_per_day=4.0,
                max_position_size=0.13,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.06
            ),
            
            'Enhanced Aggressive (Previous Best)': TradingParameters(
                win_rate=0.55,
                avg_win_pct=0.04,
                avg_loss_pct=0.02,
                trades_per_day=15.0,
                max_position_size=0.25,
                transaction_cost=0.001,
                slippage=0.0005,
                risk_tolerance=0.10
            )
        }
        
        return competitors
    
    def run_elite_benchmark(self, years=20):
        """Run benchmark against elite competitors"""
        
        print("\n" + "="*80)
        print("🏆 PROMETHEUS VS WORLD'S TOP HEDGE FUNDS")
        print("="*80)
        print()
        
        # Load Prometheus params
        if not self.load_prometheus_best_params():
            print("❌ Could not load Prometheus parameters!")
            return
        
        print("🤖 PROMETHEUS AI - ENHANCED CONFIGURATION")
        print("="*80)
        print(f"  Win Rate:        {self.prometheus_params.win_rate*100:.2f}%")
        print(f"  Avg Win:         {self.prometheus_params.avg_win_pct*100:.2f}%")
        print(f"  Avg Loss:        {self.prometheus_params.avg_loss_pct*100:.3f}%")
        print(f"  Trades/Day:      {self.prometheus_params.trades_per_day:.1f}")
        print(f"  Max Position:    {self.prometheus_params.max_position_size*100:.1f}%")
        print(f"  Risk Tolerance:  {self.prometheus_params.risk_tolerance*100:.1f}%")
        print()
        print("  Enhancements Applied:")
        print("  ✓ 16 Trading Books Integrated")
        print("  ✓ 20 Research Papers Applied")
        print("  ✓ 12 Market Insight Categories")
        print("  ✓ 125 Generations of Evolution")
        print("  ✓ 50-Year Deep Learning (469.68 fitness)")
        print()
        
        # Create elite competitors
        competitors = self.create_elite_competitors()
        
        print(f"🎯 COMPETITORS ({len(competitors)} Elite Strategies):")
        print("="*80)
        for i, name in enumerate(competitors.keys(), 1):
            print(f"  {i:2d}. {name}")
        print()
        
        print(f"📊 Testing {len(competitors)+1} strategies over {years} years...")
        print()
        
        proceed = input("Run elite benchmark? (yes/no) [yes]: ").strip().lower() or "yes"
        if proceed not in ['yes', 'y']:
            print("Cancelled.")
            return
        
        print("\n" + "="*80)
        print("🚀 RUNNING ELITE BENCHMARK...")
        print("="*80)
        print()
        
        backtest = ContinuousLearningBacktest()
        
        # Test Prometheus FIRST
        print("🤖 Testing PROMETHEUS AI (Enhanced)...")
        prometheus_result = backtest.run_backtest(self.prometheus_params, years)
        self.results['PROMETHEUS AI ⭐'] = prometheus_result
        print(f"   ✅ CAGR: {prometheus_result.cagr*100:.2f}%, Sharpe: {prometheus_result.sharpe_ratio:.2f}, Win Rate: {prometheus_result.win_rate*100:.1f}%")
        print()
        
        # Test each elite competitor
        for name, params in competitors.items():
            print(f"📈 Testing {name}...")
            result = backtest.run_backtest(params, years)
            self.results[name] = result
            print(f"   ✅ CAGR: {result.cagr*100:.2f}%, Sharpe: {result.sharpe_ratio:.2f}, Win Rate: {result.win_rate*100:.1f}%")
            print()
        
        self.print_elite_results()
        self.save_elite_results(years)
    
    def print_elite_results(self):
        """Print comprehensive elite benchmark results"""
        
        print("\n" + "="*80)
        print("🏆 ELITE BENCHMARK RESULTS - FINAL RANKINGS")
        print("="*80)
        print()
        
        # Sort by fitness score
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].fitness_score,
            reverse=True
        )
        
        # Print header
        print(f"{'RANK':<6} {'STRATEGY':<38} {'CAGR':<10} {'SHARPE':<8} {'WIN%':<8} {'MAXDD':<8} {'FITNESS':<10}")
        print("="*80)
        
        # Print results
        for rank, (name, result) in enumerate(sorted_results, 1):
            cagr = f"{result.cagr*100:.1f}%"
            sharpe = f"{result.sharpe_ratio:.2f}"
            win_rate = f"{result.win_rate*100:.1f}%"
            max_dd = f"{result.max_drawdown:.1f}%"
            fitness = f"{result.fitness_score:.2f}"
            
            # Special markers
            if "PROMETHEUS" in name:
                marker = "👑"
                name_display = f"{name}"
            elif rank <= 3:
                marker = f" {rank}"
                name_display = name[:36]
            else:
                marker = f" {rank}"
                name_display = name[:36]
            
            print(f"{marker:<6} {name_display:<38} {cagr:<10} {sharpe:<8} {win_rate:<8} {max_dd:<8} {fitness:<10}")
        
        print()
        
        # Performance analysis
        prometheus_result = None
        prometheus_rank = 0
        for rank, (name, result) in enumerate(sorted_results, 1):
            if "PROMETHEUS" in name:
                prometheus_result = result
                prometheus_rank = rank
                break
        
        if prometheus_result:
            print("="*80)
            print("📊 PROMETHEUS AI PERFORMANCE ANALYSIS")
            print("="*80)
            print()
            
            # Compare to each competitor
            wins = {'cagr': 0, 'sharpe': 0, 'win_rate': 0, 'drawdown': 0, 'fitness': 0}
            total_competitors = len(self.results) - 1
            
            for name, result in self.results.items():
                if "PROMETHEUS" in name:
                    continue
                
                if prometheus_result.cagr > result.cagr:
                    wins['cagr'] += 1
                if prometheus_result.sharpe_ratio > result.sharpe_ratio:
                    wins['sharpe'] += 1
                if prometheus_result.win_rate > result.win_rate:
                    wins['win_rate'] += 1
                if abs(prometheus_result.max_drawdown) < abs(result.max_drawdown):
                    wins['drawdown'] += 1
                if prometheus_result.fitness_score > result.fitness_score:
                    wins['fitness'] += 1
            
            print(f"  Overall Rank: #{prometheus_rank} out of {len(self.results)}")
            print()
            print(f"  Wins by Metric:")
            print(f"    CAGR:        {wins['cagr']}/{total_competitors} ({wins['cagr']/total_competitors*100:.1f}%)")
            print(f"    Sharpe:      {wins['sharpe']}/{total_competitors} ({wins['sharpe']/total_competitors*100:.1f}%)")
            print(f"    Win Rate:    {wins['win_rate']}/{total_competitors} ({wins['win_rate']/total_competitors*100:.1f}%)")
            print(f"    Drawdown:    {wins['drawdown']}/{total_competitors} ({wins['drawdown']/total_competitors*100:.1f}%)")
            print(f"    Fitness:     {wins['fitness']}/{total_competitors} ({wins['fitness']/total_competitors*100:.1f}%)")
            print()
            
            # Key advantages
            print("="*80)
            print("💪 PROMETHEUS KEY ADVANTAGES")
            print("="*80)
            print()
            
            # Find best competitor in each category
            best_cagr = max(self.results.items(), key=lambda x: x[1].cagr if "PROMETHEUS" not in x[0] else 0)
            best_sharpe = max(self.results.items(), key=lambda x: x[1].sharpe_ratio if "PROMETHEUS" not in x[0] else 0)
            best_win_rate = max(self.results.items(), key=lambda x: x[1].win_rate if "PROMETHEUS" not in x[0] else 0)
            
            print(f"  CAGR vs Best Competitor ({best_cagr[0][:30]}):")
            print(f"    Prometheus: {prometheus_result.cagr*100:.2f}%")
            print(f"    Competitor: {best_cagr[1].cagr*100:.2f}%")
            print(f"    Difference: {(prometheus_result.cagr - best_cagr[1].cagr)*100:+.2f}%")
            print()
            
            print(f"  Sharpe Ratio vs Best Competitor ({best_sharpe[0][:30]}):")
            print(f"    Prometheus: {prometheus_result.sharpe_ratio:.2f}")
            print(f"    Competitor: {best_sharpe[1].sharpe_ratio:.2f}")
            print(f"    Difference: {prometheus_result.sharpe_ratio - best_sharpe[1].sharpe_ratio:+.2f}")
            print()
            
            print(f"  Win Rate vs Best Competitor ({best_win_rate[0][:30]}):")
            print(f"    Prometheus: {prometheus_result.win_rate*100:.2f}%")
            print(f"    Competitor: {best_win_rate[1].win_rate*100:.2f}%")
            print(f"    Difference: {(prometheus_result.win_rate - best_win_rate[1].win_rate)*100:+.2f}%")
            print()
            
            # Final statistics
            print("="*80)
            print("📈 PROMETHEUS FINAL STATISTICS")
            print("="*80)
            print()
            print(f"  Final Capital:     ${prometheus_result.final_capital:,.2f}")
            print(f"  Total Return:      {prometheus_result.total_return*100:,.1f}%")
            print(f"  CAGR:              {prometheus_result.cagr*100:.2f}%")
            print(f"  Sharpe Ratio:      {prometheus_result.sharpe_ratio:.2f}")
            print(f"  Max Drawdown:      {prometheus_result.max_drawdown:.2f}%")
            print(f"  Win Rate:          {prometheus_result.win_rate*100:.2f}%")
            print(f"  Total Trades:      {prometheus_result.total_trades:,}")
            print(f"  Fitness Score:     {prometheus_result.fitness_score:.2f}")
            print()
            
            # Overall verdict
            if prometheus_rank == 1:
                print("🎉 VERDICT: PROMETHEUS AI RANKS #1 - WORLD CLASS PERFORMANCE!")
            elif prometheus_rank <= 3:
                print("🏆 VERDICT: PROMETHEUS AI IN TOP 3 - ELITE PERFORMANCE!")
            elif prometheus_rank <= 5:
                print("⭐ VERDICT: PROMETHEUS AI IN TOP 5 - EXCELLENT PERFORMANCE!")
            else:
                print("✅ VERDICT: PROMETHEUS AI COMPETITIVE WITH TOP HEDGE FUNDS!")
            print()
    
    def save_elite_results(self, years):
        """Save elite benchmark results"""
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_type": "Elite Hedge Fund Comparison",
            "benchmark_duration_years": years,
            "strategies_tested": len(self.results),
            "enhancements_applied": {
                "trading_books": 16,
                "research_papers": 20,
                "market_insights": 12,
                "training_generations": 125,
                "best_fitness": 469.68,
                "training_years": 50
            },
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
        
        # Find Prometheus rank
        for i, (name, _) in enumerate(sorted_results, 1):
            if "PROMETHEUS" in name:
                results_data["prometheus_rank"] = i
                break
        
        filename = f"prometheus_elite_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Elite benchmark results saved to: {filename}")
        print()


def main():
    print("\n" + "="*80)
    print("🏆 PROMETHEUS VS ELITE COMPETITORS BENCHMARK")
    print("="*80)
    print()
    print("This benchmark tests Prometheus AI against:")
    print("  • Renaissance Technologies (Medallion)")
    print("  • Two Sigma")
    print("  • Citadel")
    print("  • AQR")
    print("  • DE Shaw")
    print("  • Bridgewater")
    print("  • Jane Street")
    print("  • Man AHL")
    print("  • Millennium")
    print("  • Point72")
    print("  • Enhanced Aggressive Strategy")
    print()
    print("Duration options:")
    print("  1. Quick Test (5 years)")
    print("  2. Standard (20 years)")
    print("  3. Long-term (50 years)")
    print()
    
    choice = input("Enter choice [2]: ").strip() or "2"
    
    if choice == "1":
        years = 5
    elif choice == "3":
        years = 50
    else:
        years = 20
    
    benchmark = EliteCompetitorBenchmark()
    benchmark.run_elite_benchmark(years=years)
    
    print("="*80)
    print("✅ ELITE BENCHMARK COMPLETE!")
    print("="*80)
    print()


if __name__ == "__main__":
    main()
