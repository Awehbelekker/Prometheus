#!/usr/bin/env python3
"""
Run All Comprehensive Backtests
Orchestrates all backtesting across multiple timeframes and learning angles
"""

import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'comprehensive_backtest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_comprehensive_real_market_backtest():
    """Run comprehensive real market backtest"""
    logger.info("=" * 80)
    logger.info("STARTING COMPREHENSIVE REAL MARKET BACKTEST")
    logger.info("=" * 80)
    
    try:
        from comprehensive_real_market_backtest import ComprehensiveRealMarketBacktest
        
        backtester = ComprehensiveRealMarketBacktest(initial_capital=10000.0)
        results = await backtester.run_comprehensive_backtest()
        
        logger.info("✅ Comprehensive Real Market Backtest Complete")
        return results
    except Exception as e:
        logger.error(f"❌ Comprehensive Real Market Backtest Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_advanced_learning_backtest():
    """Run advanced learning backtest"""
    logger.info("=" * 80)
    logger.info("STARTING ADVANCED LEARNING BACKTEST")
    logger.info("=" * 80)
    
    try:
        from advanced_learning_backtest import AdvancedLearningBacktest
        
        backtester = AdvancedLearningBacktest(initial_capital=10000.0)
        results = await backtester.run_advanced_learning_backtest()
        
        logger.info("✅ Advanced Learning Backtest Complete")
        return results
    except Exception as e:
        logger.error(f"❌ Advanced Learning Backtest Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_all_backtests():
    """Run all comprehensive backtests"""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE BACKTEST SUITE")
    logger.info("=" * 80)
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    logger.info("This will test Prometheus across:")
    logger.info("  - Timeframes: 1, 5, 10, 20, 50, 100 years")
    logger.info("  - Multiple symbols: SPY, QQQ, AAPL, MSFT, TSLA, NVDA, BTC-USD, ETH-USD")
    logger.info("  - Different market conditions: Bull, Bear, Volatile, Sideways")
    logger.info("  - Learning from multiple angles")
    logger.info("")
    logger.info("This may take significant time. Progress will be logged.")
    logger.info("")
    
    # Run both backtests
    # Note: These can run in parallel, but for now we'll run sequentially
    # to avoid overwhelming the system
    
    results = {}
    
    # Phase 1: Real Market Backtest
    logger.info("PHASE 1: Real Market Backtest")
    logger.info("-" * 80)
    real_market_results = await run_comprehensive_real_market_backtest()
    results['real_market'] = real_market_results
    
    # Phase 2: Advanced Learning Backtest
    logger.info("")
    logger.info("PHASE 2: Advanced Learning Backtest")
    logger.info("-" * 80)
    learning_results = await run_advanced_learning_backtest()
    results['learning'] = learning_results
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("BACKTEST SUITE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    logger.info("Results Summary:")
    logger.info(f"  Real Market Backtest: {'✅ Complete' if real_market_results else '❌ Failed'}")
    logger.info(f"  Learning Backtest: {'✅ Complete' if learning_results else '❌ Failed'}")
    logger.info("")
    logger.info("Check generated report files for detailed results:")
    logger.info("  - real_market_backtest_report_*.md")
    logger.info("  - advanced_learning_backtest_report_*.md")
    logger.info("  - learned_patterns_*.json")
    logger.info("")
    logger.info("Patterns will be automatically integrated into Prometheus!")
    
    return results

async def main():
    await run_all_backtests()

if __name__ == "__main__":
    asyncio.run(main())

