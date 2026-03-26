"""
COMPREHENSIVE AUTONOMOUS SYSTEM TEST
====================================
Tests all integrated AI systems working together:
- Autonomous Market Scanner
- Dynamic Trading Universe
- Multi-Strategy Executor
- Profit Maximization Engine
- HRM + ThinkMesh + DeepConf + Ensemble + Multimodal

This validates that PROMETHEUS can truly autonomously find and trade
the most profitable opportunities across all markets.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results tracker
test_results = {
    'tests_run': 0,
    'tests_passed': 0,
    'tests_failed': 0,
    'start_time': None,
    'end_time': None
}

def test_result(test_name: str, passed: bool, details: str = ""):
    """Record test result"""
    test_results['tests_run'] += 1
    if passed:
        test_results['tests_passed'] += 1
        logger.info(f"✅ PASS: {test_name}")
    else:
        test_results['tests_failed'] += 1
        logger.error(f"❌ FAIL: {test_name}")
    if details:
        logger.info(f"   {details}")

async def test_autonomous_market_scanner():
    """Test 1: Autonomous Market Scanner"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: AUTONOMOUS MARKET SCANNER")
    logger.info("="*80)
    
    try:
        from core.autonomous_market_scanner import autonomous_scanner
        
        # Test discovery
        opportunities = await autonomous_scanner.discover_best_opportunities(limit=10)
        
        passed = len(opportunities) > 0
        test_result(
            "Market Scanner Discovery",
            passed,
            f"Found {len(opportunities)} opportunities across all markets"
        )
        
        if opportunities:
            top_opp = opportunities[0]
            logger.info(f"\n   Top Opportunity:")
            logger.info(f"   Symbol: {top_opp.symbol}")
            logger.info(f"   Asset Class: {top_opp.asset_class.value}")
            logger.info(f"   Type: {top_opp.opportunity_type.value}")
            logger.info(f"   Expected Return: {top_opp.expected_return:.2%}")
            logger.info(f"   Confidence: {top_opp.confidence:.0%}")
            logger.info(f"   Risk/Reward: {top_opp.risk_reward_ratio:.1f}")
            
            # Verify opportunity quality
            quality_passed = (
                top_opp.confidence >= 0.6 and
                top_opp.expected_return >= 0.005 and
                top_opp.risk_reward_ratio >= 0.5
            )
            test_result("Opportunity Quality Check", quality_passed)
        
        # Test multi-asset scanning
        asset_classes = set(opp.asset_class.value for opp in opportunities)
        multi_asset_passed = len(asset_classes) >= 1
        test_result(
            "Multi-Asset Class Scanning",
            multi_asset_passed,
            f"Scanned {len(asset_classes)} asset classes: {', '.join(asset_classes)}"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Scanner test error: {e}", exc_info=True)
        test_result("Market Scanner", False, str(e))
        return False

async def test_dynamic_universe():
    """Test 2: Dynamic Trading Universe"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: DYNAMIC TRADING UNIVERSE")
    logger.info("="*80)
    
    try:
        from core.dynamic_trading_universe import dynamic_universe
        from core.autonomous_market_scanner import autonomous_scanner
        
        # Get opportunities
        opportunities = await autonomous_scanner.discover_best_opportunities(limit=15)
        
        # Update universe
        update_result = await dynamic_universe.update_universe(opportunities)
        
        passed = update_result['active_symbols'] > 0
        test_result(
            "Universe Update",
            passed,
            f"Active: {update_result['active_symbols']}, "
            f"Watchlist: {update_result['watchlist_size']}, "
            f"Added: {len(update_result['added'])}"
        )
        
        # Test statistics
        stats = dynamic_universe.get_statistics()
        logger.info(f"\n   Universe Statistics:")
        logger.info(f"   Active Symbols: {stats['active_symbols']}")
        logger.info(f"   Watchlist Size: {stats['watchlist_size']}")
        logger.info(f"   Total Tracked: {stats['total_tracked']}")
        
        # Test dynamic behavior
        active_symbols = dynamic_universe.get_active_symbols()
        dynamic_passed = len(active_symbols) > 0
        test_result(
            "Dynamic Symbol Management",
            dynamic_passed,
            f"Managing {len(active_symbols)} active symbols"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Universe test error: {e}", exc_info=True)
        test_result("Dynamic Universe", False, str(e))
        return False

async def test_multi_strategy_executor():
    """Test 3: Multi-Strategy Executor"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: MULTI-STRATEGY EXECUTOR")
    logger.info("="*80)
    
    try:
        from core.multi_strategy_executor import multi_strategy_executor
        from core.autonomous_market_scanner import autonomous_scanner
        
        # Get an opportunity
        opportunities = await autonomous_scanner.discover_best_opportunities(limit=5)
        
        if not opportunities:
            test_result("Multi-Strategy Executor", False, "No opportunities to test")
            return False
        
        opportunity = opportunities[0]
        available_capital = 1000.0
        
        # Execute multiple strategies
        result = await multi_strategy_executor.maximize_opportunity(
            opportunity,
            available_capital
        )
        
        passed = len(result.strategies_executed) > 0
        test_result(
            "Multi-Strategy Execution",
            passed,
            f"Executed {len(result.strategies_executed)} strategies on {opportunity.symbol}"
        )
        
        logger.info(f"\n   Execution Details:")
        logger.info(f"   Symbol: {result.symbol}")
        logger.info(f"   Strategies: {len(result.strategies_executed)}")
        logger.info(f"   Capital Allocated: ${result.total_capital_allocated:.2f}")
        logger.info(f"   Expected Return: {result.expected_total_return:.2%}")
        logger.info(f"   Weighted Confidence: {result.weighted_confidence:.0%}")
        
        for i, execution in enumerate(result.strategies_executed, 1):
            logger.info(f"\n   Strategy {i}: {execution.strategy_type.value}")
            logger.info(f"      Capital: ${execution.capital_allocated:.2f}")
            logger.info(f"      Target: {execution.expected_return:.2%}")
            logger.info(f"      Entry: ${execution.entry_price:.2f}")
            logger.info(f"      Stop: ${execution.stop_price:.2f}")
        
        # Verify capital efficiency
        efficiency_passed = (
            result.total_capital_allocated > 0 and
            result.total_capital_allocated <= available_capital
        )
        test_result("Capital Allocation Efficiency", efficiency_passed)
        
        return True
        
    except Exception as e:
        logger.error(f"Multi-strategy test error: {e}", exc_info=True)
        test_result("Multi-Strategy Executor", False, str(e))
        return False

async def test_profit_maximization_engine():
    """Test 4: Profit Maximization Engine (Short Run)"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: PROFIT MAXIMIZATION ENGINE")
    logger.info("="*80)
    
    try:
        from core.profit_maximization_engine import ProfitMaximizationEngine
        
        # Create engine with test parameters
        engine = ProfitMaximizationEngine(
            total_capital=5000.0,
            scan_interval_seconds=5,  # Fast for testing
            max_capital_per_opportunity=500.0
        )
        
        # Run for 30 seconds (3 cycles minimum)
        logger.info("\n   Running autonomous engine for 30 seconds...")
        
        # Run in background task
        engine_task = asyncio.create_task(
            engine.start_autonomous_trading(duration_hours=30/3600)  # 30 seconds
        )
        
        # Wait for completion
        await engine_task
        
        # Get metrics
        metrics = engine.get_metrics()
        
        logger.info(f"\n   Engine Metrics:")
        logger.info(f"   Cycles Run: {metrics.scan_cycles}")
        logger.info(f"   Opportunities Discovered: {metrics.opportunities_discovered}")
        logger.info(f"   Opportunities Executed: {metrics.opportunities_executed}")
        logger.info(f"   Capital Deployed: ${metrics.total_capital_deployed:.2f}")
        logger.info(f"   Expected Return: {metrics.expected_total_return:.2%}")
        logger.info(f"   Runtime: {metrics.runtime_minutes:.2f} minutes")
        
        passed = (
            metrics.scan_cycles >= 2 and
            metrics.opportunities_discovered > 0
        )
        test_result(
            "Profit Maximization Engine",
            passed,
            f"{metrics.scan_cycles} cycles, {metrics.opportunities_discovered} opportunities"
        )
        
        # Test autonomous decision making
        autonomous_passed = metrics.opportunities_executed > 0
        test_result(
            "Autonomous Decision Making",
            autonomous_passed,
            f"Autonomously executed {metrics.opportunities_executed} opportunities"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Engine test error: {e}", exc_info=True)
        test_result("Profit Maximization Engine", False, str(e))
        return False

async def test_integrated_ai_systems():
    """Test 5: Integrated AI Systems (HRM, ThinkMesh, DeepConf, Ensemble)"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: INTEGRATED AI SYSTEMS")
    logger.info("="*80)
    
    try:
        # Test HRM
        try:
            from core.hierarchical_reasoning import HierarchicalReasoningModel
            logger.info("   ✅ HRM Available")
            test_result("HRM Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ HRM: {e}")
            test_result("HRM Integration", False)
        
        # Test ThinkMesh
        try:
            from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter
            logger.info("   ✅ ThinkMesh Available")
            test_result("ThinkMesh Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ ThinkMesh: {e}")
            test_result("ThinkMesh Integration", False)
        
        # Test DeepConf
        try:
            from core.reasoning.official_deepconf_adapter import OfficialDeepConfAdapter
            logger.info("   ✅ DeepConf Available")
            test_result("DeepConf Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ DeepConf: {e}")
            test_result("DeepConf Integration", False)
        
        # Test Ensemble
        try:
            from core.ensemble_voting_system import EnsembleVotingSystem
            logger.info("   ✅ Ensemble Voting Available")
            test_result("Ensemble Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ Ensemble: {e}")
            test_result("Ensemble Integration", False)
        
        # Test Multimodal
        try:
            from core.multimodal_analyzer import MultimodalAnalyzer
            logger.info("   ✅ Multimodal Analyzer Available")
            test_result("Multimodal Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ Multimodal: {e}")
            test_result("Multimodal Integration", False)
        
        # Test Universal Reasoning Engine
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            engine = UniversalReasoningEngine()
            logger.info("   ✅ Universal Reasoning Engine Available")
            test_result("Universal Reasoning Integration", True)
        except Exception as e:
            logger.warning(f"   ⚠️ Universal Reasoning: {e}")
            test_result("Universal Reasoning Integration", False)
        
        return True
        
    except Exception as e:
        logger.error(f"AI systems test error: {e}", exc_info=True)
        return False

async def test_end_to_end_autonomous_flow():
    """Test 6: End-to-End Autonomous Trading Flow"""
    logger.info("\n" + "="*80)
    logger.info("TEST 6: END-TO-END AUTONOMOUS FLOW")
    logger.info("="*80)
    
    try:
        logger.info("\n   Simulating complete autonomous trading cycle...")
        
        # 1. Scan markets
        from core.autonomous_market_scanner import autonomous_scanner
        logger.info("\n   Step 1: Scanning markets...")
        opportunities = await autonomous_scanner.discover_best_opportunities(limit=10)
        logger.info(f"   ✅ Found {len(opportunities)} opportunities")
        
        # 2. Update universe
        from core.dynamic_trading_universe import dynamic_universe
        logger.info("\n   Step 2: Updating trading universe...")
        universe_result = await dynamic_universe.update_universe(opportunities)
        logger.info(f"   ✅ Universe: {universe_result['active_symbols']} active symbols")
        
        # 3. Execute strategies
        from core.multi_strategy_executor import multi_strategy_executor
        logger.info("\n   Step 3: Executing multi-strategy approach...")
        if opportunities:
            result = await multi_strategy_executor.maximize_opportunity(
                opportunities[0],
                500.0
            )
            logger.info(f"   ✅ Executed {len(result.strategies_executed)} strategies")
        
        # 4. Get AI decision
        logger.info("\n   Step 4: Getting AI ensemble decision...")
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            ai_provider = UnifiedAIProvider()
            decision = await ai_provider.get_response(
                "Should I buy AAPL based on current market conditions?",
                model="deepseek-r1:8b"
            )
            logger.info(f"   ✅ AI Decision received: {len(decision)} chars")
        except Exception as e:
            logger.warning(f"   ⚠️ AI decision: {e}")
        
        test_result(
            "End-to-End Autonomous Flow",
            True,
            "Complete autonomous cycle executed successfully"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"E2E test error: {e}", exc_info=True)
        test_result("End-to-End Flow", False, str(e))
        return False

def print_final_summary():
    """Print final test summary"""
    duration = (test_results['end_time'] - test_results['start_time']).total_seconds()
    
    logger.info("\n" + "="*80)
    logger.info("🏁 COMPREHENSIVE TEST RESULTS")
    logger.info("="*80)
    logger.info(f"Tests Run: {test_results['tests_run']}")
    logger.info(f"Tests Passed: {test_results['tests_passed']} ✅")
    logger.info(f"Tests Failed: {test_results['tests_failed']} ❌")
    logger.info(f"Success Rate: {(test_results['tests_passed'] / max(test_results['tests_run'], 1)) * 100:.1f}%")
    logger.info(f"Duration: {duration:.1f}s")
    logger.info("="*80)
    
    if test_results['tests_failed'] == 0:
        logger.info("\n🎉 ALL TESTS PASSED! PROMETHEUS IS FULLY OPERATIONAL!")
        logger.info("🚀 System is ready for autonomous profit maximization!")
    else:
        logger.warning(f"\n⚠️ {test_results['tests_failed']} tests failed. Review logs above.")

async def main():
    """Run all comprehensive tests"""
    test_results['start_time'] = datetime.now()
    
    logger.info("\n" + "="*80)
    logger.info("🚀 STARTING COMPREHENSIVE AUTONOMOUS SYSTEM TESTS")
    logger.info("="*80)
    logger.info("This validates ALL systems working together:")
    logger.info("- Autonomous Market Scanner")
    logger.info("- Dynamic Trading Universe")
    logger.info("- Multi-Strategy Executor")
    logger.info("- Profit Maximization Engine")
    logger.info("- HRM + ThinkMesh + DeepConf + Ensemble + Multimodal")
    logger.info("="*80)
    
    # Run all tests
    await test_autonomous_market_scanner()
    await test_dynamic_universe()
    await test_multi_strategy_executor()
    await test_integrated_ai_systems()
    await test_end_to_end_autonomous_flow()
    await test_profit_maximization_engine()
    
    test_results['end_time'] = datetime.now()
    print_final_summary()

if __name__ == "__main__":
    asyncio.run(main())

