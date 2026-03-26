#!/usr/bin/env python3
"""
🚀 PROMETHEUS COMPREHENSIVE BENCHMARK SUITE
Tests backtesting across multiple time periods for both STOCKS and CRYPTO

Time Periods: 1, 5, 10, 25, 50, 100 years (where data available)
Asset Classes: Stocks (SPY, QQQ, AAPL, etc.) and Crypto (BTC, ETH, etc.)
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Import our backtester
from prometheus_real_ai_backtest import PrometheusRealAIBacktester

# Asset definitions
STOCK_SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'AMD', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'V']
CRYPTO_SYMBOLS = ['BTCUSD', 'ETHUSD', 'SOLUSD', 'BNBUSD', 'XRPUSD', 'ADAUSD', 'DOGEUSD', 'AVAXUSD']

# Time periods in days (approximate)
TIME_PERIODS = {
    '1_year': 365,
    '5_years': 365 * 5,
    '10_years': 365 * 10,
    '25_years': 365 * 25,
    '50_years': 365 * 50,
    '100_years': 365 * 100,
}

# Note: yfinance has data limits - crypto typically has 5-10 years max
CRYPTO_MAX_YEARS = 10
STOCK_MAX_YEARS = 50  # Some stocks have very long history

async def run_benchmark(symbols: List[str], period_days: int, period_name: str, 
                       asset_type: str) -> Dict[str, Any]:
    """Run a single benchmark test"""
    print(f"\n{'='*60}")
    print(f"📊 Running {asset_type.upper()} benchmark: {period_name}")
    print(f"   Symbols: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    print(f"   Period: {period_days} days ({period_days/365:.1f} years)")
    print(f"{'='*60}")
    
    try:
        backtester = PrometheusRealAIBacktester(
            initial_capital=100000,
            max_position_pct=0.10,
            stop_loss_pct=0.03,
            take_profit_pct=0.08
        )
        
        metrics = await backtester.run_backtest(symbols, period_days, '1d')
        
        return {
            'period_name': period_name,
            'period_days': period_days,
            'asset_type': asset_type,
            'symbols': symbols,
            'total_return': metrics.total_return,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'avg_win': metrics.avg_win,
            'avg_loss': metrics.avg_loss,
            'best_trade': metrics.best_trade,
            'worst_trade': metrics.worst_trade,
            'status': 'success'
        }
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return {
            'period_name': period_name,
            'period_days': period_days,
            'asset_type': asset_type,
            'symbols': symbols,
            'status': 'failed',
            'error': str(e)
        }

async def run_all_benchmarks():
    """Run comprehensive benchmarks across all periods and asset types"""
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "🚀"*30)
    print("PROMETHEUS COMPREHENSIVE BENCHMARK SUITE")
    print("🚀"*30 + "\n")
    
    # Stock benchmarks
    print("\n📈 STOCK BENCHMARKS")
    print("-" * 40)
    for period_name, period_days in TIME_PERIODS.items():
        years = period_days / 365
        if years <= STOCK_MAX_YEARS:
            result = await run_benchmark(STOCK_SYMBOLS, period_days, period_name, 'stocks')
            results.append(result)
        else:
            print(f"⏭️ Skipping {period_name} for stocks (exceeds {STOCK_MAX_YEARS} year limit)")
    
    # Crypto benchmarks  
    print("\n₿ CRYPTO BENCHMARKS")
    print("-" * 40)
    for period_name, period_days in TIME_PERIODS.items():
        years = period_days / 365
        if years <= CRYPTO_MAX_YEARS:
            result = await run_benchmark(CRYPTO_SYMBOLS, period_days, period_name, 'crypto')
            results.append(result)
        else:
            print(f"⏭️ Skipping {period_name} for crypto (exceeds {CRYPTO_MAX_YEARS} year limit)")
    
    # Combined benchmarks (stocks + crypto)
    print("\n🌐 COMBINED BENCHMARKS (Stocks + Crypto)")
    print("-" * 40)
    combined_symbols = STOCK_SYMBOLS[:6] + CRYPTO_SYMBOLS[:4]
    for period_name, period_days in [('1_year', 365), ('5_years', 365*5)]:
        result = await run_benchmark(combined_symbols, period_days, period_name, 'combined')
        results.append(result)
    
    # Save results
    results_file = f'benchmark_results_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print_benchmark_summary(results)
    print(f"\n📁 Full results saved to: {results_file}")
    
    return results

def print_benchmark_summary(results: List[Dict]):
    """Print a summary table of all benchmark results"""
    print("\n" + "="*100)
    print("📊 BENCHMARK SUMMARY")
    print("="*100)
    print(f"{'Period':<12} {'Type':<10} {'Return':<12} {'Sharpe':<10} {'MaxDD':<10} {'WinRate':<10} {'PF':<8} {'Trades':<8}")
    print("-"*100)
    
    for r in results:
        if r['status'] == 'success':
            print(f"{r['period_name']:<12} {r['asset_type']:<10} "
                  f"{r['total_return']:>8.2f}% {r['sharpe_ratio']:>10.2f} "
                  f"{r['max_drawdown']:>8.2f}% {r['win_rate']*100:>8.1f}% "
                  f"{r['profit_factor']:>8.2f} {r['total_trades']:>8}")
        else:
            print(f"{r['period_name']:<12} {r['asset_type']:<10} {'FAILED':<12} {r.get('error', 'Unknown')[:50]}")

if __name__ == '__main__':
    asyncio.run(run_all_benchmarks())

