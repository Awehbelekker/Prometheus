#!/usr/bin/env python3
"""
Quick Multi-Year Benchmark for PROMETHEUS
Tests 1, 5, 10 years for both Stocks and Crypto
"""

import asyncio
import json
from datetime import datetime
from prometheus_real_ai_backtest import PrometheusRealAIBacktester

async def quick_benchmark():
    results = {}
    
    # Test periods (in days)
    periods = {
        '1_year': 365,
        '5_years': 365 * 5,
        '10_years': 365 * 10,
    }
    
    # Stock symbols
    stock_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']
    
    # Crypto symbols  
    crypto_symbols = ['BTCUSD', 'ETHUSD']
    
    print('='*60)
    print('PROMETHEUS MULTI-YEAR BENCHMARK')
    print('='*60)
    
    # Run stock benchmarks
    print('\n📈 STOCK BENCHMARKS')
    for name, days in periods.items():
        print(f'\nRunning {name} stock backtest ({days} days)...')
        try:
            bt = PrometheusRealAIBacktester(
                initial_capital=100000,
                max_position_pct=0.10,
                stop_loss_pct=0.03,
                take_profit_pct=0.08
            )
            metrics = await bt.run_backtest(stock_symbols, days, '1d')
            results[f'stocks_{name}'] = {
                'total_return': round(metrics.total_return * 100, 2),
                'sharpe': round(metrics.sharpe_ratio, 2),
                'max_dd': round(metrics.max_drawdown * 100, 2),
                'win_rate': round(metrics.win_rate * 100, 1),
                'profit_factor': round(metrics.profit_factor, 2),
                'trades': metrics.total_trades
            }
            print(f'  ✅ Return: {metrics.total_return*100:.2f}%, Trades: {metrics.total_trades}')
        except Exception as e:
            print(f'  ❌ Failed: {e}')
            results[f'stocks_{name}'] = {'error': str(e)}
    
    # Run crypto benchmarks
    print('\n💰 CRYPTO BENCHMARKS')
    for name, days in periods.items():
        print(f'\nRunning {name} crypto backtest ({days} days)...')
        try:
            bt = PrometheusRealAIBacktester(
                initial_capital=100000,
                max_position_pct=0.10,
                stop_loss_pct=0.03,
                take_profit_pct=0.08
            )
            metrics = await bt.run_backtest(crypto_symbols, days, '1d')
            results[f'crypto_{name}'] = {
                'total_return': round(metrics.total_return * 100, 2),
                'sharpe': round(metrics.sharpe_ratio, 2),
                'max_dd': round(metrics.max_drawdown * 100, 2),
                'win_rate': round(metrics.win_rate * 100, 1),
                'profit_factor': round(metrics.profit_factor, 2),
                'trades': metrics.total_trades
            }
            print(f'  ✅ Return: {metrics.total_return*100:.2f}%, Trades: {metrics.total_trades}')
        except Exception as e:
            print(f'  ❌ Failed: {e}')
            results[f'crypto_{name}'] = {'error': str(e)}
    
    # Print summary
    print('\n' + '='*60)
    print('BENCHMARK SUMMARY')
    print('='*60)
    
    # Format as table
    print(f"\n{'Asset':<15} {'Period':<10} {'Return':<10} {'Sharpe':<8} {'MaxDD':<8} {'WinRate':<8} {'PF':<6} {'Trades':<8}")
    print('-'*75)
    for key, val in results.items():
        if 'error' not in val:
            parts = key.split('_')
            asset = parts[0].upper()
            period = '_'.join(parts[1:])
            print(f"{asset:<15} {period:<10} {val['total_return']:>7.2f}% {val['sharpe']:>7.2f} {val['max_dd']:>6.2f}% {val['win_rate']:>6.1f}% {val['profit_factor']:>5.2f} {val['trades']:>7}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'benchmark_multi_year_{timestamp}.json'
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n✅ Results saved to {filename}')
    
    return results

if __name__ == '__main__':
    asyncio.run(quick_benchmark())

