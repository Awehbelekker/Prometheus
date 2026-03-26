#!/usr/bin/env python3
"""
Monitor 100-Year Backtest Progress
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import glob
from pathlib import Path
from datetime import datetime

def check_backtest_status():
    """Check if backtest is running or completed"""
    print("="*80)
    print("100-YEAR BACKTEST STATUS")
    print("="*80)
    
    # Check for results files
    result_files = glob.glob("backtest_100_years_*.json")
    
    if result_files:
        # Get latest result file
        latest_file = max(result_files, key=lambda f: Path(f).stat().st_mtime)
        
        print(f"\n✅ Found results file: {latest_file}")
        
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        print("\n" + "="*80)
        print("BACKTEST RESULTS")
        print("="*80)
        print(f"\nInitial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Value: ${results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return_pct']:.2f}%")
        print(f"Annualized Return: {results['annualized_return']:.2f}%")
        print(f"CAGR: {results['cagr']:.2f}%")
        print(f"\nTrades: {results['num_trades']:,}")
        print(f"  Winning: {results['winning_trades']:,}")
        print(f"  Losing: {results['losing_trades']:,}")
        print(f"Win Rate: {results['win_rate']*100:.2f}%")
        print(f"\nSharpe Ratio: {results['sharpe_ratio']:.3f}")
        print(f"Max Drawdown: {results['max_drawdown']*100:.2f}%")
        print(f"\nAvg Decision Time: {results['avg_decision_time_ms']:.2f}ms")
        print(f"Days Tested: {results['days']:,}")
        
        # Calculate multiplier
        multiplier = results['final_value'] / results['initial_capital']
        print(f"\n{'='*80}")
        print(f"FINAL RESULT: ${results['initial_capital']:,.2f} → ${results['final_value']:,.2f}")
        print(f"Multiplier: {multiplier:.2f}x over 100 years")
        print(f"CAGR: {results['cagr']:.2f}% per year")
        print(f"{'='*80}")
        
    else:
        print("\n⏳ Backtest is still running or hasn't started yet...")
        print("   Check the terminal output for progress updates.")
        print("   Results will be saved to backtest_100_years_*.json when complete.")

if __name__ == "__main__":
    check_backtest_status()

