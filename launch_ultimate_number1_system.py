#!/usr/bin/env python3
"""
Launch Ultimate Trading System - #1 in the World
Combines Universal Reasoning Engine + RL + Predictive Forecasting
"""

import asyncio
import logging
from core.ultimate_trading_system import UltimateTradingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main launcher"""
    logger.info("="*80)
    logger.info("🚀 LAUNCHING ULTIMATE TRADING SYSTEM - #1 IN THE WORLD")
    logger.info("="*80)
    
    # Initialize ultimate system
    system = UltimateTradingSystem()
    
    # Get system status
    status = system.get_system_status()
    logger.info("\nSystem Status:")
    logger.info(f"  Universal Reasoning: {status['universal_reasoning']['total_sources']} sources")
    logger.info(f"  Reinforcement Learning: {status['reinforcement_learning'].get('status', 'ready')}")
    logger.info(f"  Regime Forecasting: {status['regime_forecasting']['history_size']} history points")
    
    # Example usage
    market_data = {
        'symbol': 'AAPL',
        'price': 150.0,
        'volume': 1000000,
        'indicators': {
            'rsi': 65.5,
            'macd': 0.8,
            'volatility': 0.02,
            'momentum': 0.5,
            'trend_strength': 0.7,
            'trend_direction': 1.0,
            'volume_trend': 0.3,
            'volume_ratio': 1.2,
            'support_level': 145.0,
            'resistance_level': 155.0
        }
    }
    
    portfolio = {
        'total_value': 10000.0,
        'positions': []
    }
    
    context = {
        'user_profile': {},
        'trading_history': [],
        'risk_preferences': {}
    }
    
    # Make ultimate decision
    logger.info("\n" + "="*80)
    logger.info("MAKING ULTIMATE DECISION")
    logger.info("="*80)
    
    decision = system.make_ultimate_decision(market_data, portfolio, context)
    
    logger.info(f"\n🎯 ULTIMATE DECISION:")
    logger.info(f"   Action: {decision['action']}")
    logger.info(f"   Confidence: {decision['confidence']:.3f}")
    logger.info(f"   Position Size: {decision.get('position_size', 0):.3f}")
    logger.info(f"   Sources: {decision['num_sources']}/3 systems")
    
    # Show system breakdown
    if 'system_decisions' in decision:
        logger.info(f"\n   System Breakdown:")
        for system_name, system_data in decision['system_decisions'].items():
            logger.info(f"     {system_name}: {system_data['action']} "
                      f"(confidence: {system_data['confidence']:.3f}, "
                      f"weight: {system_data['weight']:.2f})")
    
    logger.info("\n" + "="*80)
    logger.info("✅ ULTIMATE TRADING SYSTEM OPERATIONAL - #1 IN THE WORLD!")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(main())

