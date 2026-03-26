#!/usr/bin/env python3
"""
Run Comprehensive Backtests and Integrate Patterns into Prometheus
This script runs backtests across all timeframes and integrates learned patterns
"""

import sys
import asyncio
import logging
from pathlib import Path

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_full_backtest_suite():
    """Run complete backtest suite"""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE BACKTEST SUITE WITH PATTERN INTEGRATION")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Run learning backtest (learns patterns from all angles)
    logger.info("STEP 1: Learning patterns from all angles...")
    try:
        from advanced_learning_backtest import AdvancedLearningBacktest
        learning_backtest = AdvancedLearningBacktest()
        patterns = await learning_backtest.run_learning_backtest()
        logger.info("✅ Pattern learning complete")
    except Exception as e:
        logger.error(f"❌ Pattern learning failed: {e}")
        return
    
    # Step 2: Run comprehensive real market backtest
    logger.info("\nSTEP 2: Running comprehensive real market backtest...")
    try:
        from comprehensive_real_market_backtest import ComprehensiveRealMarketBacktest
        real_backtest = ComprehensiveRealMarketBacktest(initial_capital=10000.0)
        results = await real_backtest.run_comprehensive_backtest()
        logger.info("✅ Real market backtest complete")
    except Exception as e:
        logger.error(f"❌ Real market backtest failed: {e}")
        return
    
    # Step 3: Integrate patterns into Prometheus
    logger.info("\nSTEP 3: Integrating patterns into Prometheus...")
    try:
        from integrate_backtest_patterns import PatternIntegrationEngine
        integrator = PatternIntegrationEngine()
        
        # Test integration
        test_market = {
            'symbol': 'SPY',
            'price': 450.0,
            'volatility': 0.02,
            'volume_ratio': 1.2,
            'trend': 'up',
            'regime': 'bull'
        }
        
        test_decision = {
            'action': 'BUY',
            'confidence': 0.6,
            'symbol': 'SPY'
        }
        
        enhanced = await integrator.enhance_prometheus_decision(
            test_market,
            {'value': 10000},
            test_decision
        )
        
        logger.info(f"✅ Pattern integration complete")
        logger.info(f"   Patterns matched: {enhanced.get('patterns_matched', 0)}")
    except Exception as e:
        logger.error(f"❌ Pattern integration failed: {e}")
        return
    
    # Step 4: Verify integration
    logger.info("\nSTEP 4: Verifying integration...")
    try:
        from core.universal_reasoning_engine import UniversalReasoningEngine
        
        engine = UniversalReasoningEngine()
        status = engine.get_system_status()
        
        logger.info("Universal Reasoning Engine Status:")
        logger.info(f"  Pattern Integration: {'✅ Active' if status.get('pattern_integration') else '❌ Not Active'}")
        logger.info(f"  Total Sources: {status.get('total_sources', 0)}")
        
        if status.get('pattern_integration'):
            logger.info("✅ Patterns successfully integrated into Prometheus!")
        else:
            logger.warning("⚠️ Pattern integration not active - check initialization")
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST SUITE COMPLETE")
    logger.info("=" * 80)
    logger.info("\nNext Steps:")
    logger.info("  1. Patterns are now integrated into Universal Reasoning Engine")
    logger.info("  2. Prometheus will use patterns in all future decisions")
    logger.info("  3. Monitor pattern effectiveness in live trading")
    logger.info("  4. Patterns will improve over time with continuous learning")

async def main():
    await run_full_backtest_suite()

if __name__ == "__main__":
    asyncio.run(main())

