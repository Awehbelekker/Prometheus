"""
PROMETHEUS REALISTIC BACKTEST
Test with real-world constraints and conservative assumptions
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_continuous_learning_backtest import ContinuousLearningBacktest, TradingParameters


class RealisticBacktest:
    """Backtest with realistic market conditions"""
    
    def __init__(self):
        self.results = {}
        
    def create_realistic_parameters(self):
        """Create parameters with real-world constraints"""
        
        scenarios = {
            'Prometheus Optimistic': {
                'description': 'Best case - everything works as trained',
                'params': TradingParameters(
                    win_rate=0.711,  # From training
                    avg_win_pct=0.03,
                    avg_loss_pct=0.0045,
                    trades_per_day=8.0,
                    max_position_size=0.12,
                    transaction_cost=0.001,  # 10 bps
                    slippage=0.0005,  # 5 bps
                    risk_tolerance=0.05
                )
            },
            
            'Prometheus Realistic': {
                'description': 'Expected real-world performance with friction',
                'params': TradingParameters(
                    win_rate=0.65,  # Lower than training (market adaptation)
                    avg_win_pct=0.025,  # Slightly lower wins
                    avg_loss_pct=0.006,  # Slightly larger losses
                    trades_per_day=8.0,
                    max_position_size=0.12,
                    transaction_cost=0.002,  # 20 bps (retail + market impact)
                    slippage=0.001,  # 10 bps (realistic slippage)
                    risk_tolerance=0.05
                )
            },
            
            'Prometheus Conservative': {
                'description': 'Worst case - high friction, lower performance',
                'params': TradingParameters(
                    win_rate=0.60,  # Significantly degraded
                    avg_win_pct=0.020,  # Smaller wins
                    avg_loss_pct=0.008,  # Larger losses
                    trades_per_day=8.0,
                    max_position_size=0.10,  # Smaller positions
                    transaction_cost=0.003,  # 30 bps (high friction)
                    slippage=0.0015,  # 15 bps (adverse selection)
                    risk_tolerance=0.04  # Lower risk
                )
            },
            
            'Retail Trader Benchmark': {
                'description': 'Typical retail trader with basic strategy',
                'params': TradingParameters(
                    win_rate=0.45,  # Below breakeven before costs
                    avg_win_pct=0.03,
                    avg_loss_pct=0.03,  # Equal win/loss size
                    trades_per_day=5.0,
                    max_position_size=0.15,
                    transaction_cost=0.002,  # 20 bps
                    slippage=0.001,  # 10 bps
                    risk_tolerance=0.08
                )
            },
            
            'Professional Trader': {
                'description': 'Experienced professional with institutional costs',
                'params': TradingParameters(
                    win_rate=0.55,  # Professional edge
                    avg_win_pct=0.025,
                    avg_loss_pct=0.015,  # Tight stops
                    trades_per_day=6.0,
                    max_position_size=0.12,
                    transaction_cost=0.0005,  # 5 bps (institutional)
                    slippage=0.0003,  # 3 bps
                    risk_tolerance=0.05
                )
            }
        }
        
        return scenarios
    
    def run_realistic_backtest(self, years=10):
        """Run backtest with realistic scenarios"""
        
        print("\n" + "="*80)
        print("📊 PROMETHEUS REALISTIC BACKTEST")
        print("="*80)
        print()
        print("Testing Prometheus AI under real-world conditions:")
        print()
        
        scenarios = self.create_realistic_parameters()
        
        for i, (name, config) in enumerate(scenarios.items(), 1):
            print(f"{i}. {name}")
            print(f"   {config['description']}")
            params = config['params']
            print(f"   Win Rate: {params.win_rate*100:.1f}%, "
                  f"Avg Win: {params.avg_win_pct*100:.2f}%, "
                  f"Avg Loss: {params.avg_loss_pct*100:.2f}%")
            print(f"   Transaction Cost: {params.transaction_cost*10000:.1f} bps, "
                  f"Slippage: {params.slippage*10000:.1f} bps")
            print()
        
        print(f"📅 Backtest Duration: {years} years")
        print()
        
        proceed = input("Run realistic backtest? (yes/no) [yes]: ").strip().lower() or "yes"
        if proceed not in ['yes', 'y']:
            print("Cancelled.")
            return
        
        print("\n" + "="*80)
        print("🚀 RUNNING REALISTIC BACKTEST...")
        print("="*80)
        print()
        
        backtest = ContinuousLearningBacktest()
        
        for name, config in scenarios.items():
            print(f"📈 Testing: {name}")
            print(f"   {config['description']}")
            
            result = backtest.run_backtest(config['params'], years)
            self.results[name] = {
                'result': result,
                'description': config['description'],
                'params': config['params']
            }
            
            print(f"   ✅ CAGR: {result.cagr*100:.2f}%, "
                  f"Sharpe: {result.sharpe_ratio:.2f}, "
                  f"Win Rate: {result.win_rate*100:.1f}%, "
                  f"Max DD: {result.max_drawdown:.2f}%")
            print()
        
        self.print_results()
        self.save_results(years)
    
    def print_results(self):
        """Print comprehensive realistic backtest results"""
        
        print("\n" + "="*80)
        print("📊 REALISTIC BACKTEST RESULTS")
        print("="*80)
        print()
        
        # Sort by fitness
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['result'].fitness_score,
            reverse=True
        )
        
        print(f"{'RANK':<6} {'SCENARIO':<32} {'CAGR':<10} {'SHARPE':<8} {'WIN%':<8} {'MAXDD':<8} {'FITNESS':<10}")
        print("="*80)
        
        for rank, (name, data) in enumerate(sorted_results, 1):
            result = data['result']
            cagr = f"{result.cagr*100:.1f}%"
            sharpe = f"{result.sharpe_ratio:.2f}"
            win_rate = f"{result.win_rate*100:.1f}%"
            max_dd = f"{result.max_drawdown:.2f}%"
            fitness = f"{result.fitness_score:.2f}"
            
            marker = f" {rank}" if rank > 3 else f"{'🥇🥈🥉'[rank-1]} {rank}"
            name_display = name[:30]
            
            print(f"{marker:<6} {name_display:<32} {cagr:<10} {sharpe:<8} {win_rate:<8} {max_dd:<8} {fitness:<10}")
        
        print()
        print("="*80)
        print("🎯 PROMETHEUS PERFORMANCE ANALYSIS")
        print("="*80)
        print()
        
        # Find Prometheus scenarios
        prometheus_scenarios = {k: v for k, v in self.results.items() if 'Prometheus' in k}
        
        if prometheus_scenarios:
            print("📈 PROMETHEUS SCENARIOS COMPARISON:")
            print()
            
            for name in ['Prometheus Optimistic', 'Prometheus Realistic', 'Prometheus Conservative']:
                if name in prometheus_scenarios:
                    result = prometheus_scenarios[name]['result']
                    desc = prometheus_scenarios[name]['description']
                    params = prometheus_scenarios[name]['params']
                    
                    print(f"  {name}:")
                    print(f"    {desc}")
                    print(f"    CAGR:              {result.cagr*100:.2f}%")
                    print(f"    Sharpe Ratio:      {result.sharpe_ratio:.2f}")
                    print(f"    Win Rate:          {result.win_rate*100:.2f}%")
                    print(f"    Max Drawdown:      {result.max_drawdown:.2f}%")
                    print(f"    Total Trades:      {result.total_trades:,}")
                    print(f"    Final Capital:     ${result.final_capital:,.2f}")
                    print(f"    Fitness Score:     {result.fitness_score:.2f}")
                    print(f"    Transaction Cost:  {params.transaction_cost*10000:.1f} bps")
                    print(f"    Slippage:          {params.slippage*10000:.1f} bps")
                    print()
            
            # Performance degradation analysis
            if 'Prometheus Optimistic' in prometheus_scenarios and 'Prometheus Realistic' in prometheus_scenarios:
                opt_result = prometheus_scenarios['Prometheus Optimistic']['result']
                real_result = prometheus_scenarios['Prometheus Realistic']['result']
                
                print("="*80)
                print("📉 PERFORMANCE DEGRADATION (Optimistic → Realistic):")
                print("="*80)
                print()
                
                cagr_drop = (opt_result.cagr - real_result.cagr) * 100
                sharpe_drop = opt_result.sharpe_ratio - real_result.sharpe_ratio
                fitness_drop = opt_result.fitness_score - real_result.fitness_score
                
                print(f"  CAGR Drop:         {cagr_drop:.2f}% ({cagr_drop/opt_result.cagr/100*100:.1f}% relative)")
                print(f"  Sharpe Drop:       {sharpe_drop:.2f} ({sharpe_drop/opt_result.sharpe_ratio*100:.1f}% relative)")
                print(f"  Fitness Drop:      {fitness_drop:.2f} ({fitness_drop/opt_result.fitness_score*100:.1f}% relative)")
                print()
                
                # Still profitable?
                if real_result.cagr > 0.10:  # 10% CAGR threshold
                    print(f"  ✅ VERDICT: Realistic scenario still highly profitable!")
                    print(f"     {real_result.cagr*100:.2f}% CAGR remains excellent for real-world trading")
                elif real_result.cagr > 0.05:
                    print(f"  ⚠️  VERDICT: Realistic scenario moderately profitable")
                    print(f"     {real_result.cagr*100:.2f}% CAGR is acceptable but monitor closely")
                else:
                    print(f"  ⚠️  VERDICT: Realistic scenario shows concerning performance")
                    print(f"     {real_result.cagr*100:.2f}% CAGR requires strategy adjustment")
                print()
        
        # Compare to benchmarks
        if 'Retail Trader Benchmark' in self.results or 'Professional Trader' in self.results:
            print("="*80)
            print("📊 PROMETHEUS VS BENCHMARKS:")
            print("="*80)
            print()
            
            if 'Prometheus Realistic' in self.results:
                prom_result = self.results['Prometheus Realistic']['result']
                
                if 'Retail Trader Benchmark' in self.results:
                    retail_result = self.results['Retail Trader Benchmark']['result']
                    cagr_adv = (prom_result.cagr - retail_result.cagr) * 100
                    sharpe_adv = prom_result.sharpe_ratio - retail_result.sharpe_ratio
                    
                    print(f"  Prometheus Realistic vs Retail Trader:")
                    print(f"    CAGR Advantage:    {cagr_adv:+.2f}%")
                    print(f"    Sharpe Advantage:  {sharpe_adv:+.2f}")
                    
                    if prom_result.cagr > retail_result.cagr:
                        improvement = (prom_result.cagr / retail_result.cagr - 1) * 100 if retail_result.cagr > 0 else float('inf')
                        print(f"    📈 Prometheus is {improvement:.1f}% better!")
                    print()
                
                if 'Professional Trader' in self.results:
                    pro_result = self.results['Professional Trader']['result']
                    cagr_adv = (prom_result.cagr - pro_result.cagr) * 100
                    sharpe_adv = prom_result.sharpe_ratio - pro_result.sharpe_ratio
                    
                    print(f"  Prometheus Realistic vs Professional Trader:")
                    print(f"    CAGR Advantage:    {cagr_adv:+.2f}%")
                    print(f"    Sharpe Advantage:  {sharpe_adv:+.2f}")
                    
                    if prom_result.cagr > pro_result.cagr:
                        improvement = (prom_result.cagr / pro_result.cagr - 1) * 100 if pro_result.cagr > 0 else float('inf')
                        print(f"    📈 Prometheus is {improvement:.1f}% better!")
                    print()
        
        # Final recommendation
        print("="*80)
        print("💡 REALISTIC TRADING RECOMMENDATIONS:")
        print("="*80)
        print()
        
        if 'Prometheus Realistic' in self.results:
            result = self.results['Prometheus Realistic']['result']
            
            print(f"  Expected Real-World Performance:")
            print(f"    Annual Return:     {result.cagr*100:.2f}%")
            print(f"    Risk-Adjusted:     {result.sharpe_ratio:.2f} Sharpe")
            print(f"    Win Consistency:   {result.win_rate*100:.2f}%")
            print(f"    Worst Drawdown:    {result.max_drawdown:.2f}%")
            print()
            
            # Calculate realistic expectations
            initial_capital = 10000
            year1 = initial_capital * (1 + result.cagr)
            year3 = initial_capital * ((1 + result.cagr) ** 3)
            year5 = initial_capital * ((1 + result.cagr) ** 5)
            
            print(f"  Capital Growth Projection (Starting ${initial_capital:,}):")
            print(f"    After 1 year:      ${year1:,.2f} ({(year1-initial_capital):+,.2f})")
            print(f"    After 3 years:     ${year3:,.2f} ({(year3-initial_capital):+,.2f})")
            print(f"    After 5 years:     ${year5:,.2f} ({(year5-initial_capital):+,.2f})")
            print()
            
            if result.sharpe_ratio > 2.0:
                print("  ✅ EXCELLENT: Sharpe > 2.0 indicates professional-grade performance")
            elif result.sharpe_ratio > 1.0:
                print("  ✅ GOOD: Sharpe > 1.0 indicates solid risk-adjusted returns")
            else:
                print("  ⚠️  CAUTION: Sharpe < 1.0 suggests high volatility relative to returns")
            print()
            
            if result.cagr > 0.30:
                print("  🚀 EXCEPTIONAL: >30% CAGR is rare in real-world trading")
            elif result.cagr > 0.15:
                print("  💪 STRONG: >15% CAGR beats most professional traders")
            elif result.cagr > 0.08:
                print("  ✅ SOLID: >8% CAGR beats market averages")
            else:
                print("  ⚠️  REVIEW: <8% CAGR may not justify active trading")
            print()
    
    def save_results(self, years):
        """Save realistic backtest results"""
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "backtest_type": "Realistic Performance Test",
            "backtest_duration_years": years,
            "scenarios_tested": len(self.results),
            "results": {}
        }
        
        for name, data in self.results.items():
            result = data['result']
            params = data['params']
            
            results_data["results"][name] = {
                "description": data['description'],
                "parameters": {
                    "win_rate": params.win_rate * 100,
                    "avg_win_pct": params.avg_win_pct * 100,
                    "avg_loss_pct": params.avg_loss_pct * 100,
                    "trades_per_day": params.trades_per_day,
                    "max_position_size": params.max_position_size * 100,
                    "transaction_cost_bps": params.transaction_cost * 10000,
                    "slippage_bps": params.slippage * 10000,
                    "risk_tolerance": params.risk_tolerance * 100
                },
                "performance": {
                    "final_capital": result.final_capital,
                    "total_return": result.total_return * 100,
                    "cagr": result.cagr * 100,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate * 100,
                    "total_trades": result.total_trades,
                    "fitness_score": result.fitness_score
                }
            }
        
        filename = f"prometheus_realistic_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Realistic backtest results saved to: {filename}")
        print()


def main():
    print("\n" + "="*80)
    print("📊 PROMETHEUS REALISTIC BACKTEST")
    print("="*80)
    print()
    print("This backtest tests Prometheus under realistic conditions:")
    print("  • Real transaction costs (retail vs institutional)")
    print("  • Market slippage and impact")
    print("  • Performance degradation from training")
    print("  • Conservative parameter estimates")
    print("  • Comparison to typical traders")
    print()
    print("Duration options:")
    print("  1. Short-term (5 years)")
    print("  2. Medium-term (10 years) [recommended]")
    print("  3. Long-term (20 years)")
    print()
    
    choice = input("Enter choice [2]: ").strip() or "2"
    
    if choice == "1":
        years = 5
    elif choice == "3":
        years = 20
    else:
        years = 10
    
    backtest = RealisticBacktest()
    backtest.run_realistic_backtest(years=years)
    
    print("="*80)
    print("✅ REALISTIC BACKTEST COMPLETE!")
    print("="*80)
    print()


if __name__ == "__main__":
    main()
