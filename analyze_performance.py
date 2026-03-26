#!/usr/bin/env python3
"""
Trading Session Performance Analysis
"""

import json
from datetime import datetime

def analyze_trading_performance():
    print('🚀 PROMETHEUS TRADING SESSION PERFORMANCE ANALYSIS')
    print('=' * 60)
    print()

    # Load the most recent revolutionary session report
    try:
        with open('revolutionary_session_report_revolutionary_20250905_010808.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[ERROR] No recent trading session data found")
        return

    # Session Summary
    summary = data['session_summary']
    print('📊 SESSION OVERVIEW:')
    print(f'   Session ID: {summary["session_id"]}')
    print(f'   Duration: {summary["duration_hours"]:.2f} hours ({summary["duration_hours"]/24:.1f} days)')
    print(f'   Start Time: {summary["start_time"]}')
    print(f'   End Time: {summary["end_time"]}')
    print()

    # Financial Performance
    print('💰 FINANCIAL PERFORMANCE:')
    print(f'   Starting Capital: ${summary["starting_capital"]:,.2f}')
    print(f'   Final Value: ${summary["final_value"]:,.2f}')
    print(f'   Total P&L: ${summary["total_pnl"]:,.2f}')
    print(f'   Total Return: {summary["total_return"]*100:.2f}%')
    print(f'   Daily Return Rate: {summary["daily_return_rate"]*100:.2f}%')
    print(f'   Max Drawdown: {summary["max_drawdown"]*100:.4f}%')
    print()

    # Trading Activity
    print('📈 TRADING ACTIVITY:')
    print(f'   Total Trades: {summary["total_trades"]}')
    print(f'   Average P&L per Trade: ${summary["total_pnl"]/summary["total_trades"]:.2f}')
    print()

    # Feature Performance
    features = data['feature_performance']
    print('🤖 AI ENGINE PERFORMANCE:')
    for engine, perf in features.items():
        if engine == 'ai_consciousness':
            print(f'   AI Consciousness: {perf["decisions"]} decisions, {perf["accuracy"]*100:.1f}% accuracy')
        elif engine == 'quantum_optimization':
            print(f'   Quantum Optimization: {perf["optimizations"]} optimizations, +${perf["improvement"]:.2f} improvement')
        else:
            print(f'   {engine.replace("_", " ").title()}: {perf["trades"]} trades, ${perf["pnl"]:.2f} P&L')
    print()

    # Performance Rating
    if summary['total_return'] > 0.05:
        rating = '🌟 EXCELLENT'
    elif summary['total_return'] > 0.02:
        rating = '[CHECK] GOOD'
    elif summary['total_return'] > 0:
        rating = '📈 POSITIVE'
    else:
        rating = '📉 NEEDS IMPROVEMENT'

    print(f'🎯 OVERALL PERFORMANCE RATING: {rating}')
    print(f'   Return: {summary["total_return"]*100:.2f}% over {summary["duration_hours"]/24:.1f} days')
    print()

    # Overnight Session Comparison
    try:
        with open('overnight_report_overnight_20250903_185812.json', 'r') as f:
            overnight_data = json.load(f)
        
        print('🌙 OVERNIGHT SESSION COMPARISON:')
        print(f'   Overnight P&L: ${overnight_data["pnl"]:.2f} (${overnight_data["starting_capital"]:.0f} → ${overnight_data["final_value"]:.2f})')
        print(f'   Overnight Trades: {overnight_data["trade_count"]}')
        print(f'   Overnight Duration: {overnight_data["duration_hours"]:.1f} hours')
        print()
    except FileNotFoundError:
        pass

    # Key Insights
    print('🔍 KEY INSIGHTS:')
    if summary['total_return'] > 0:
        print(f'   [CHECK] Profitable session with {summary["total_return"]*100:.2f}% return')
    else:
        print(f'   [WARNING]️  Loss-making session with {summary["total_return"]*100:.2f}% return')
    
    if summary['max_drawdown'] < 0.01:
        print(f'   [CHECK] Low risk profile with {summary["max_drawdown"]*100:.4f}% max drawdown')
    else:
        print(f'   [WARNING]️  Higher risk with {summary["max_drawdown"]*100:.4f}% max drawdown')
    
    print(f'   📊 Trading frequency: {summary["total_trades"]/(summary["duration_hours"]/24):.1f} trades per day')
    print()

if __name__ == "__main__":
    analyze_trading_performance()
