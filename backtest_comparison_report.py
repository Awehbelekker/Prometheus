#!/usr/bin/env python3
"""
PROMETHEUS Backtest vs Actual Trading Comparison Report Generator
"""
import sqlite3
import yfinance as yf
import json
from datetime import datetime, timedelta
from pathlib import Path

def get_benchmark_performance(days: int = 60):
    """Get SPY benchmark performance"""
    end = datetime.now()
    start = end - timedelta(days=days)
    spy = yf.download('SPY', start=start, end=end, progress=False)
    if len(spy) > 0:
        first_price = float(spy['Close'].iloc[0])
        last_price = float(spy['Close'].iloc[-1])
        return (last_price - first_price) / first_price * 100
    return 0.0

def get_actual_trading_performance():
    """Get actual trading performance from database"""
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
                SUM(profit_loss) as total_pnl,
                AVG(profit_loss) as avg_pnl,
                MAX(profit_loss) as best_trade,
                MIN(profit_loss) as worst_trade
            FROM trade_history 
            WHERE profit_loss IS NOT NULL AND profit_loss != 0
        ''')
        row = c.fetchone()
        conn.close()
        
        if row and row[0] and row[0] > 0:
            return {
                'total_trades': row[0],
                'winning_trades': row[1] or 0,
                'losing_trades': row[2] or 0,
                'win_rate': (row[1] or 0) / row[0] * 100,
                'total_pnl': row[3] or 0,
                'avg_pnl': row[4] or 0,
                'best_trade': row[5] or 0,
                'worst_trade': row[6] or 0,
                'has_data': True
            }
    except Exception as e:
        print(f"Could not get trading history: {e}")
    
    return {'has_data': False}

def get_latest_backtest_results():
    """Get the latest backtest results from JSON files"""
    results = {'hourly': None, 'daily': None}
    
    # Find latest hourly result
    hourly_files = list(Path('.').glob('backtest_results_hourly_*.json'))
    if hourly_files:
        latest = max(hourly_files, key=lambda p: p.stat().st_mtime)
        with open(latest, 'r') as f:
            results['hourly'] = json.load(f)
    
    # Find latest daily result
    daily_files = list(Path('.').glob('backtest_results_daily_*.json'))
    if daily_files:
        latest = max(daily_files, key=lambda p: p.stat().st_mtime)
        with open(latest, 'r') as f:
            results['daily'] = json.load(f)
    
    return results

def generate_report():
    """Generate comprehensive comparison report"""
    print("=" * 80)
    print("PROMETHEUS BACKTEST VS ACTUAL TRADING COMPARISON REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Benchmark
    benchmark = get_benchmark_performance(60)
    print(f"\n📈 BENCHMARK (SPY - Last 60 Days): {benchmark:.2f}%")
    
    # Backtest Results
    backtest = get_latest_backtest_results()
    
    if backtest['daily']:
        bt = backtest['daily']
        print(f"\n--- DAILY BACKTEST RESULTS ({bt.get('period_days', 'N/A')} days) ---")
        print(f"Total Return:        {bt.get('total_return', 0):>10.2f}%")
        print(f"vs Benchmark:        {bt.get('total_return', 0) - benchmark:>10.2f}% (alpha)")
        print(f"Win Rate:            {bt.get('win_rate', 0):>10.1f}%")
        print(f"Sharpe Ratio:        {bt.get('sharpe_ratio', 0):>10.2f}")
        print(f"Max Drawdown:        {bt.get('max_drawdown', 0):>10.1f}%")
        print(f"Profit Factor:       {bt.get('profit_factor', 0):>10.2f}")
        print(f"Total Trades:        {bt.get('total_trades', 0):>10}")
    
    if backtest['hourly']:
        bt = backtest['hourly']
        print(f"\n--- HOURLY BACKTEST RESULTS ({bt.get('period_days', 'N/A')} days) ---")
        print(f"Total Return:        {bt.get('total_return', 0):>10.2f}%")
        print(f"vs Benchmark:        {bt.get('total_return', 0) - benchmark:>10.2f}% (alpha)")
        print(f"Win Rate:            {bt.get('win_rate', 0):>10.1f}%")
        print(f"Sharpe Ratio:        {bt.get('sharpe_ratio', 0):>10.2f}")
        print(f"Max Drawdown:        {bt.get('max_drawdown', 0):>10.1f}%")
        print(f"Profit Factor:       {bt.get('profit_factor', 0):>10.2f}")
        print(f"Total Trades:        {bt.get('total_trades', 0):>10}")
    
    # Actual Trading
    actual = get_actual_trading_performance()
    print(f"\n--- ACTUAL TRADING PERFORMANCE ---")
    if actual.get('has_data'):
        print(f"Total Trades:        {actual['total_trades']:>10}")
        print(f"Win Rate:            {actual['win_rate']:>10.1f}%")
        print(f"Total P/L:           ${actual['total_pnl']:>9.2f}")
        print(f"Avg P/L per Trade:   ${actual['avg_pnl']:>9.2f}")
        print(f"Best Trade:          ${actual['best_trade']:>9.2f}")
        print(f"Worst Trade:         ${actual['worst_trade']:>9.2f}")
    else:
        print("No completed trades with P/L data yet.")
        print("P/L will be recorded when positions are closed.")
    
    # Targets Assessment
    print(f"\n--- PERFORMANCE TARGETS ---")
    targets = [
        ('Win Rate', 55, backtest['daily'].get('win_rate', 0) if backtest['daily'] else 0, '%'),
        ('Sharpe Ratio', 2.0, backtest['daily'].get('sharpe_ratio', 0) if backtest['daily'] else 0, ''),
        ('Max Drawdown', 15, backtest['daily'].get('max_drawdown', 100) if backtest['daily'] else 100, '% (lower is better)'),
        ('Profit Factor', 1.5, backtest['daily'].get('profit_factor', 0) if backtest['daily'] else 0, '')
    ]
    
    for name, target, actual_val, unit in targets:
        if name == 'Max Drawdown':
            status = '✅ PASS' if actual_val <= target else '❌ FAIL'
        else:
            status = '✅ PASS' if actual_val >= target else '❌ FAIL'
        print(f"{name:20} Target: {target:>6}{unit}  Actual: {actual_val:>8.2f}  {status}")
    
    print("=" * 80)

if __name__ == "__main__":
    generate_report()

