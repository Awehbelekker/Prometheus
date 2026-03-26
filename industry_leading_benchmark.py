#!/usr/bin/env python3
"""
Industry Leading Benchmark Comparison
Compares Prometheus against:
- S&P 500 (market benchmark)
- Top Hedge Funds (Renaissance, Bridgewater, etc.)
- Industry Averages
- Elite Trading Systems
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndustryBenchmark:
    """
    Industry Leading Benchmarks
    Based on real-world performance data
    """
    
    def __init__(self):
        # Industry benchmarks (annual returns, CAGR)
        self.benchmarks = {
            'S&P 500': {
                'cagr': 10.0,  # Historical average ~10% per year
                'sharpe_ratio': 0.5,
                'max_drawdown': 0.50,  # 2008 crash
                'win_rate': 0.55,  # Market goes up ~55% of years
                'description': 'Market benchmark - passive index fund'
            },
            'Renaissance Technologies (Medallion Fund)': {
                'cagr': 66.0,  # Legendary performance
                'sharpe_ratio': 2.0,
                'max_drawdown': 0.20,
                'win_rate': 0.75,
                'description': 'Top quant fund - closed to public'
            },
            'Bridgewater Pure Alpha': {
                'cagr': 12.0,
                'sharpe_ratio': 1.2,
                'max_drawdown': 0.15,
                'win_rate': 0.65,
                'description': 'Top macro hedge fund'
            },
            'Citadel': {
                'cagr': 20.0,
                'sharpe_ratio': 1.5,
                'max_drawdown': 0.25,
                'win_rate': 0.70,
                'description': 'Top multi-strategy fund'
            },
            'Two Sigma': {
                'cagr': 15.0,
                'sharpe_ratio': 1.3,
                'max_drawdown': 0.18,
                'win_rate': 0.68,
                'description': 'Top quant fund'
            },
            'Industry Average (Hedge Funds)': {
                'cagr': 8.0,
                'sharpe_ratio': 0.8,
                'max_drawdown': 0.30,
                'win_rate': 0.60,
                'description': 'Average hedge fund performance'
            },
            'Top 10% Hedge Funds': {
                'cagr': 15.0,
                'sharpe_ratio': 1.2,
                'max_drawdown': 0.22,
                'win_rate': 0.65,
                'description': 'Top decile performance'
            },
            'Elite Trading Systems': {
                'cagr': 25.0,
                'sharpe_ratio': 1.8,
                'max_drawdown': 0.15,
                'win_rate': 0.72,
                'description': 'Best proprietary trading systems'
            }
        }
    
    def compare_prometheus(self, prometheus_results: Dict) -> Dict[str, Any]:
        """
        Compare Prometheus results against industry benchmarks
        """
        logger.info("="*80)
        logger.info("INDUSTRY LEADING BENCHMARK COMPARISON")
        logger.info("="*80)
        
        prometheus_cagr = prometheus_results.get('cagr', 0)
        prometheus_sharpe = prometheus_results.get('sharpe_ratio', 0)
        prometheus_drawdown = prometheus_results.get('max_drawdown', 0)
        prometheus_win_rate = prometheus_results.get('win_rate', 0)
        
        comparisons = {}
        
        for benchmark_name, benchmark_data in self.benchmarks.items():
            comparison = {
                'benchmark': benchmark_name,
                'benchmark_cagr': benchmark_data['cagr'],
                'prometheus_cagr': prometheus_cagr,
                'cagr_difference': prometheus_cagr - benchmark_data['cagr'],
                'cagr_percent_diff': ((prometheus_cagr - benchmark_data['cagr']) / benchmark_data['cagr'] * 100) if benchmark_data['cagr'] > 0 else 0,
                'benchmark_sharpe': benchmark_data['sharpe_ratio'],
                'prometheus_sharpe': prometheus_sharpe,
                'sharpe_difference': prometheus_sharpe - benchmark_data['sharpe_ratio'],
                'benchmark_drawdown': benchmark_data['max_drawdown'],
                'prometheus_drawdown': prometheus_drawdown,
                'drawdown_difference': benchmark_data['max_drawdown'] - prometheus_drawdown,  # Lower is better
                'benchmark_win_rate': benchmark_data['win_rate'],
                'prometheus_win_rate': prometheus_win_rate,
                'win_rate_difference': prometheus_win_rate - benchmark_data['win_rate'],
                'description': benchmark_data['description']
            }
            
            # Overall ranking
            score = 0
            if prometheus_cagr > benchmark_data['cagr']:
                score += 2
            if prometheus_sharpe > benchmark_data['sharpe_ratio']:
                score += 1
            if prometheus_drawdown < benchmark_data['max_drawdown']:
                score += 1
            if prometheus_win_rate > benchmark_data['win_rate']:
                score += 1
            
            comparison['score'] = score
            comparison['beats_benchmark'] = score >= 3
            
            comparisons[benchmark_name] = comparison
        
        return comparisons
    
    def generate_report(self, prometheus_results: Dict, comparisons: Dict) -> str:
        """
        Generate comprehensive benchmark report
        """
        report = []
        report.append("="*80)
        report.append("INDUSTRY LEADING BENCHMARK COMPARISON REPORT")
        report.append("="*80)
        report.append("")
        
        # Prometheus Results Summary
        report.append("PROMETHEUS RESULTS:")
        report.append(f"  CAGR: {prometheus_results.get('cagr', 0):.2f}%")
        report.append(f"  Sharpe Ratio: {prometheus_results.get('sharpe_ratio', 0):.3f}")
        report.append(f"  Max Drawdown: {prometheus_results.get('max_drawdown', 0)*100:.2f}%")
        report.append(f"  Win Rate: {prometheus_results.get('win_rate', 0)*100:.2f}%")
        report.append("")
        
        # Comparison Table
        report.append("="*80)
        report.append("COMPARISON TABLE")
        report.append("="*80)
        report.append(f"{'Benchmark':<40} {'CAGR':>10} {'Sharpe':>10} {'Drawdown':>12} {'Win Rate':>12} {'Status':>10}")
        report.append("-"*80)
        
        for benchmark_name, comparison in comparisons.items():
            status = "✅ BEATS" if comparison['beats_benchmark'] else "⚠️ BELOW"
            report.append(f"{benchmark_name:<40} "
                         f"{comparison['prometheus_cagr']:>9.1f}% "
                         f"{comparison['prometheus_sharpe']:>9.2f} "
                         f"{comparison['prometheus_drawdown']*100:>11.1f}% "
                         f"{comparison['prometheus_win_rate']*100:>11.1f}% "
                         f"{status:>10}")
        
        report.append("")
        report.append("="*80)
        report.append("DETAILED COMPARISONS")
        report.append("="*80)
        
        # Detailed comparisons
        for benchmark_name, comparison in comparisons.items():
            report.append("")
            report.append(f"vs {benchmark_name}:")
            report.append(f"  Description: {comparison['description']}")
            report.append(f"  CAGR: {comparison['prometheus_cagr']:.2f}% vs {comparison['benchmark_cagr']:.2f}% "
                        f"({comparison['cagr_difference']:+.2f}%, {comparison['cagr_percent_diff']:+.1f}%)")
            report.append(f"  Sharpe: {comparison['prometheus_sharpe']:.3f} vs {comparison['benchmark_sharpe']:.3f} "
                        f"({comparison['sharpe_difference']:+.3f})")
            report.append(f"  Drawdown: {comparison['prometheus_drawdown']*100:.2f}% vs {comparison['benchmark_drawdown']*100:.2f}% "
                        f"({comparison['drawdown_difference']*100:+.2f}% better)")
            report.append(f"  Win Rate: {comparison['prometheus_win_rate']*100:.2f}% vs {comparison['benchmark_win_rate']*100:.2f}% "
                        f"({comparison['win_rate_difference']*100:+.2f}%)")
            report.append(f"  Status: {'✅ BEATS BENCHMARK' if comparison['beats_benchmark'] else '⚠️ BELOW BENCHMARK'}")
        
        # Overall Assessment
        report.append("")
        report.append("="*80)
        report.append("OVERALL ASSESSMENT")
        report.append("="*80)
        
        beats_count = sum(1 for c in comparisons.values() if c['beats_benchmark'])
        total_count = len(comparisons)
        
        report.append(f"Prometheus beats {beats_count}/{total_count} benchmarks")
        
        # Ranking
        sorted_benchmarks = sorted(comparisons.items(), 
                                  key=lambda x: (x[1]['prometheus_cagr'], x[1]['prometheus_sharpe']),
                                  reverse=True)
        
        report.append("")
        report.append("PROMETHEUS RANKING:")
        for i, (name, comp) in enumerate(sorted_benchmarks[:5], 1):
            report.append(f"  {i}. vs {name}: {comp['prometheus_cagr']:.2f}% CAGR")
        
        # Final Verdict
        report.append("")
        report.append("="*80)
        report.append("FINAL VERDICT")
        report.append("="*80)
        
        if prometheus_results.get('cagr', 0) > 20:
            report.append("✅ PROMETHEUS: ELITE PERFORMANCE")
            report.append("   Performance exceeds most industry benchmarks!")
        elif prometheus_results.get('cagr', 0) > 15:
            report.append("✅ PROMETHEUS: TOP TIER PERFORMANCE")
            report.append("   Performance matches top hedge funds!")
        elif prometheus_results.get('cagr', 0) > 10:
            report.append("✅ PROMETHEUS: ABOVE AVERAGE")
            report.append("   Performance beats market and industry average!")
        else:
            report.append("⚠️ PROMETHEUS: NEEDS IMPROVEMENT")
            report.append("   Performance below industry leaders.")
        
        return "\n".join(report)


def load_prometheus_results(results_file: str = None) -> Dict:
    """Load Prometheus backtest results"""
    if results_file:
        with open(results_file, 'r') as f:
            return json.load(f)
    
    # Try to find latest results file
    result_files = list(Path('.').glob('backtest_100_years_*.json'))
    if result_files:
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Loading results from {latest_file}")
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    # Return sample results if no file found
    logger.warning("No results file found, using sample data")
    return {
        'cagr': 15.0,
        'sharpe_ratio': 1.2,
        'max_drawdown': 0.18,
        'win_rate': 0.50
    }


def main():
    """Main benchmark comparison"""
    # Load Prometheus results
    prometheus_results = load_prometheus_results()
    
    # Create benchmark comparison
    benchmark = IndustryBenchmark()
    comparisons = benchmark.compare_prometheus(prometheus_results)
    
    # Generate report
    report = benchmark.generate_report(prometheus_results, comparisons)
    
    # Print report
    print(report)
    
    # Save report
    output_file = f"industry_benchmark_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"\n✅ Report saved to {output_file}")
    
    return comparisons


if __name__ == "__main__":
    main()

