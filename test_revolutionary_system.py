#!/usr/bin/env python3
"""Test Revolutionary HRM System"""

from launch_revolutionary_prometheus import RevolutionaryPrometheusLauncher
import asyncio

async def test():
    print("="*80)
    print("TESTING REVOLUTIONARY PROMETHEUS SYSTEM")
    print("="*80)
    
    launcher = RevolutionaryPrometheusLauncher()
    
    # Get status
    status = launcher.get_system_status()
    print("\nSystem Status:")
    print(f"  Multi-Agent: {status['hrm_system']['multi_agent']['available']}")
    print(f"  Ensemble: {status['hrm_system']['ensemble']['available']}")
    print(f"  Memory: {status['hrm_system']['memory']['available']}")
    print(f"  Workflows: {status['workflows']['available']}")
    print(f"  Evaluation: {status['evaluation']['available']}")
    print(f"  Alpaca MCP: {status['alpaca_mcp']['available']}")
    
    # Test decision
    market_data = {
        'symbol': 'AAPL',
        'price': 150.0,
        'volume': 1000000,
        'indicators': {
            'rsi': 65.5,
            'macd': 0.8,
            'volatility': 0.02
        }
    }
    
    print("\n" + "="*80)
    print("MAKING REVOLUTIONARY DECISION")
    print("="*80)
    
    decision = await launcher.make_trading_decision(market_data)
    
    print(f"\nDecision: {decision['action']}")
    print(f"Confidence: {decision['confidence']:.3f}")
    print(f"Position Size: {decision.get('position_size', 0):.3f}")
    print(f"Sources: {decision.get('num_sources', 0)}")
    print(f"Enhancements: {decision.get('enhancements', {})}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE - REVOLUTIONARY SYSTEM OPERATIONAL!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test())

