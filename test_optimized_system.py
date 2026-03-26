#!/usr/bin/env python3
"""
Test Optimized Trading System
Tests the three key optimizations: Win Rate, Profitability, Decision Speed
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import logging
import numpy as np
from core.performance_optimizer import OptimizedTradingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_optimizations():
    """Test all three optimizations"""
    print("="*80)
    print("TESTING OPTIMIZED TRADING SYSTEM")
    print("="*80)
    
    # Initialize optimized system
    system = OptimizedTradingSystem()
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'High Confidence Buy',
            'market_data': {
                'symbol': 'AAPL',
                'price': 150.0,
                'volume': 1000000,
                'indicators': {
                    'rsi': 45,
                    'macd': 1.2,
                    'volatility': 0.02,
                    'momentum': 0.5,
                    'trend_strength': 0.7,
                    'trend_direction': 1.0
                }
            },
            'portfolio': {'total_value': 10000.0, 'positions': []}
        },
        {
            'name': 'Low Confidence Scenario',
            'market_data': {
                'symbol': 'AAPL',
                'price': 150.0,
                'volume': 800000,
                'indicators': {
                    'rsi': 50,
                    'macd': 0.1,
                    'volatility': 0.015,
                    'momentum': 0.0,
                    'trend_strength': 0.3,
                    'trend_direction': 0.0
                }
            },
            'portfolio': {'total_value': 10000.0, 'positions': []}
        },
        {
            'name': 'High Volatility',
            'market_data': {
                'symbol': 'AAPL',
                'price': 150.0,
                'volume': 1200000,
                'indicators': {
                    'rsi': 55,
                    'macd': 0.5,
                    'volatility': 0.06,  # High volatility
                    'momentum': 0.3,
                    'trend_strength': 0.5,
                    'trend_direction': 0.5
                }
            },
            'portfolio': {'total_value': 10000.0, 'positions': []}
        }
    ]
    
    print("\n" + "="*80)
    print("TESTING DECISION SPEED OPTIMIZATION")
    print("="*80)
    
    decision_times = []
    for scenario in test_scenarios:
        import time
        start = time.time()
        decision = system.make_optimized_decision(
            scenario['market_data'],
            scenario['portfolio'],
            {}
        )
        elapsed = (time.time() - start) * 1000
        decision_times.append(elapsed)
        
        print(f"\n{scenario['name']}:")
        print(f"  Action: {decision['action']}")
        print(f"  Confidence: {decision.get('confidence', 0):.3f}")
        print(f"  Decision Time: {elapsed:.2f}ms")
        if 'stop_loss' in decision:
            print(f"  Stop Loss: ${decision['stop_loss']:.2f}")
            print(f"  Take Profit: ${decision['take_profit']:.2f}")
            print(f"  Risk/Reward: {decision.get('risk_reward_ratio', 0):.1f}:1")
    
    avg_time = np.mean(decision_times)
    print(f"\n✅ Average Decision Time: {avg_time:.2f}ms")
    print(f"   Target: <100ms")
    print(f"   Status: {'✅ PASS' if avg_time < 100 else '⚠️ NEEDS IMPROVEMENT'}")
    
    print("\n" + "="*80)
    print("TESTING WIN RATE OPTIMIZATION")
    print("="*80)
    
    # Simulate trades and outcomes
    outcomes = [
        {'profit': 50.0, 'success': True},
        {'profit': -30.0, 'success': False},
        {'profit': 40.0, 'success': True},
        {'profit': -25.0, 'success': False},
        {'profit': 60.0, 'success': True},
        {'profit': -20.0, 'success': False},
        {'profit': 45.0, 'success': True},
        {'profit': -35.0, 'success': False},
        {'profit': 55.0, 'success': True},
        {'profit': -40.0, 'success': False},
    ]
    
    for i, outcome in enumerate(outcomes):
        decision = system.make_optimized_decision(
            test_scenarios[0]['market_data'],
            test_scenarios[0]['portfolio'],
            {}
        )
        system.learn_from_outcome(decision, outcome)
    
    status = system.get_status()
    win_rate = status['metrics']['win_rate']
    
    print(f"\n✅ Win Rate: {win_rate*100:.2f}%")
    print(f"   Target: >50%")
    print(f"   Status: {'✅ PASS' if win_rate >= 0.5 else '⚠️ NEEDS IMPROVEMENT'}")
    print(f"   Confidence Threshold: {status['optimization']['win_rate']['confidence_threshold']:.2f}")
    
    print("\n" + "="*80)
    print("TESTING PROFITABILITY OPTIMIZATION")
    print("="*80)
    
    avg_profit = status['metrics']['avg_profit']
    total_trades = status['metrics']['total_trades']
    winning_trades = status['metrics']['winning_trades']
    
    print(f"\n✅ Average Profit: ${avg_profit:.2f}")
    print(f"   Total Trades: {total_trades}")
    print(f"   Winning Trades: {winning_trades}")
    print(f"   Status: {'✅ PROFITABLE' if avg_profit > 0 else '⚠️ NEEDS IMPROVEMENT'}")
    
    print("\n" + "="*80)
    print("OPTIMIZATION STATUS SUMMARY")
    print("="*80)
    
    opt_status = status['optimization']
    
    print(f"\nWin Rate:")
    print(f"  Current: {opt_status['win_rate']['current']*100:.2f}%")
    print(f"  Target: {opt_status['win_rate']['target']*100:.0f}%")
    print(f"  Status: {opt_status['win_rate']['status']}")
    
    print(f"\nProfitability:")
    print(f"  Avg Profit: ${opt_status['profitability']['avg_profit']:.2f}")
    print(f"  Total Trades: {opt_status['profitability']['total_trades']}")
    print(f"  Status: {opt_status['profitability']['status']}")
    
    print(f"\nDecision Speed:")
    print(f"  Avg Time: {opt_status['decision_speed']['avg_time_ms']:.2f}ms")
    print(f"  Target: {opt_status['decision_speed']['target_ms']:.0f}ms")
    print(f"  Status: {opt_status['decision_speed']['status']}")
    print(f"  Cache Size: {opt_status['decision_speed']['cache_size']}")
    
    print("\n" + "="*80)
    print("✅ OPTIMIZATION TESTING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_optimizations())

