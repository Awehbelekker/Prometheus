"""
PROMETHEUS AUTONOMOUS SYSTEM - PRODUCTION DEPLOYMENT
===================================================
Deploys the fully autonomous trading system to production.

This script:
1. Validates all components
2. Initializes systems
3. Starts autonomous trading
4. Monitors performance
5. Provides real-time status updates
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'reports/autonomous_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def validate_systems():
    """Validate all required systems are available"""
    logger.info("="*80)
    logger.info("SYSTEM VALIDATION")
    logger.info("="*80)
    
    validation_results = []
    
    # Check core autonomous components
    try:
        from core.autonomous_market_scanner import autonomous_scanner
        logger.info("[OK] Autonomous Market Scanner: OK")
        validation_results.append(True)
    except Exception as e:
        logger.error(f"[FAILED] Autonomous Market Scanner: FAILED - {e}")
        validation_results.append(False)
    
    try:
        from core.dynamic_trading_universe import dynamic_universe
        logger.info("[OK] Dynamic Trading Universe: OK")
        validation_results.append(True)
    except Exception as e:
        logger.error(f"[FAILED] Dynamic Trading Universe: FAILED - {e}")
        validation_results.append(False)
    
    try:
        from core.multi_strategy_executor import multi_strategy_executor
        logger.info("[OK] Multi-Strategy Executor: OK")
        validation_results.append(True)
    except Exception as e:
        logger.error(f"[FAILED] Multi-Strategy Executor: FAILED - {e}")
        validation_results.append(False)
    
    try:
        from core.profit_maximization_engine import ProfitMaximizationEngine
        logger.info("[OK] Profit Maximization Engine: OK")
        validation_results.append(True)
    except Exception as e:
        logger.error(f"[FAILED] Profit Maximization Engine: FAILED - {e}")
        validation_results.append(False)
    
    # Check AI systems
    try:
        from core.universal_reasoning_engine import UniversalReasoningEngine
        logger.info("[OK] Universal Reasoning Engine: OK")
        validation_results.append(True)
    except Exception as e:
        logger.warning(f"[WARNING] Universal Reasoning Engine: {e}")
        validation_results.append(True)  # Not critical
    
    try:
        from core.unified_ai_provider import UnifiedAIProvider
        logger.info("[OK] Unified AI Provider: OK")
        validation_results.append(True)
    except Exception as e:
        logger.warning(f"[WARNING] Unified AI Provider: {e}")
        validation_results.append(True)  # Not critical
    
    # Check data providers
    try:
        from core.real_time_market_data import market_data_orchestrator
        logger.info("[OK] Real-Time Market Data: OK")
        validation_results.append(True)
    except Exception as e:
        logger.error(f"[FAILED] Real-Time Market Data: FAILED - {e}")
        validation_results.append(False)
    
    success_rate = sum(validation_results) / len(validation_results)
    logger.info(f"\nValidation Success Rate: {success_rate*100:.1f}%")
    
    return all(validation_results[:4])  # Core components must all pass

async def initialize_systems(config: dict):
    """Initialize all systems with configuration"""
    logger.info("\n" + "="*80)
    logger.info("SYSTEM INITIALIZATION")
    logger.info("="*80)
    
    from core.profit_maximization_engine import ProfitMaximizationEngine
    
    # Create engine with configuration
    engine = ProfitMaximizationEngine(
        total_capital=config.get('capital', 10000),
        scan_interval_seconds=config.get('scan_interval', 60),
        max_capital_per_opportunity=config.get('max_per_opportunity', 1000)
    )
    
    # Configure thresholds
    engine.min_opportunity_confidence = config.get('min_confidence', 0.70)
    engine.min_opportunity_return = config.get('min_return', 0.008)
    engine.max_opportunities_per_cycle = config.get('max_per_cycle', 5)
    
    logger.info(f"[OK] Engine Configuration:")
    logger.info(f"   Capital: ${config.get('capital', 10000):,.2f}")
    logger.info(f"   Scan Interval: {config.get('scan_interval', 60)}s")
    logger.info(f"   Min Confidence: {config.get('min_confidence', 0.70)*100:.0f}%")
    logger.info(f"   Min Return: {config.get('min_return', 0.008)*100:.1f}%")
    logger.info(f"   Max Opportunities/Cycle: {config.get('max_per_cycle', 5)}")
    
    return engine

async def run_production_trading(config: dict):
    """Run autonomous trading in production mode"""
    logger.info("\n" + "="*80)
    logger.info("STARTING AUTONOMOUS TRADING - PRODUCTION MODE")
    logger.info("="*80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {'LIVE TRADING' if config.get('live', False) else 'PAPER TRADING'}")
    logger.info(f"Duration: {config.get('duration_hours', 'CONTINUOUS')}")
    logger.info("="*80)
    
    # Validate systems
    if not await validate_systems():
        logger.error("\n[ERROR] System validation failed. Cannot start trading.")
        return False
    
    # Initialize
    engine = await initialize_systems(config)
    
    # Start trading
    try:
        await engine.start_autonomous_trading(
            duration_hours=config.get('duration_hours', None)
        )
        
        # Print final metrics
        metrics = engine.get_metrics()
        logger.info("\n" + "="*80)
        logger.info("📊 FINAL PERFORMANCE SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Runtime: {metrics.runtime_minutes:.1f} minutes")
        logger.info(f"Total Cycles: {metrics.scan_cycles}")
        logger.info(f"Opportunities Discovered: {metrics.opportunities_discovered}")
        logger.info(f"Opportunities Executed: {metrics.opportunities_executed}")
        logger.info(f"Capital Deployed: ${metrics.total_capital_deployed:,.2f}")
        logger.info(f"Expected Return: {metrics.expected_total_return:.2%}")
        logger.info(f"Active Positions: {len(engine.active_executions)}")
        logger.info("="*80)
        
        return True
        
    except KeyboardInterrupt:
        logger.info("\n[STOPPED] Trading stopped by user")
        return True
    except Exception as e:
        logger.error(f"\n[ERROR] Trading error: {e}", exc_info=True)
        return False

def get_user_configuration():
    """Get configuration from user input"""
    print("\n" + "="*80)
    print("PROMETHEUS AUTONOMOUS TRADING - DEPLOYMENT CONFIGURATION")
    print("="*80)
    
    config = {}
    
    # Capital
    capital_input = input("\nStarting Capital (default $10,000): $")
    config['capital'] = float(capital_input) if capital_input else 10000
    
    # Duration
    duration_input = input("Duration in hours (blank for continuous): ")
    config['duration_hours'] = float(duration_input) if duration_input else None
    
    # Scan interval
    interval_input = input("Scan interval in seconds (default 60): ")
    config['scan_interval'] = int(interval_input) if interval_input else 60
    
    # Risk level
    print("\nRisk Level:")
    print("1. Conservative (70% confidence, 1% return)")
    print("2. Moderate (65% confidence, 0.8% return)")
    print("3. Aggressive (60% confidence, 0.5% return)")
    risk_input = input("Select (1-3, default 2): ")
    
    if risk_input == "1":
        config['min_confidence'] = 0.70
        config['min_return'] = 0.01
        config['max_per_cycle'] = 3
    elif risk_input == "3":
        config['min_confidence'] = 0.60
        config['min_return'] = 0.005
        config['max_per_cycle'] = 7
    else:  # Default moderate
        config['min_confidence'] = 0.65
        config['min_return'] = 0.008
        config['max_per_cycle'] = 5
    
    # Trading mode
    mode_input = input("\nTrading Mode (paper/live, default paper): ").lower()
    config['live'] = mode_input == 'live'
    
    # Confirmation
    print("\n" + "="*80)
    print("DEPLOYMENT CONFIGURATION SUMMARY")
    print("="*80)
    print(f"Capital: ${config['capital']:,.2f}")
    print(f"Duration: {config['duration_hours'] or 'Continuous'}")
    print(f"Scan Interval: {config['scan_interval']}s")
    print(f"Min Confidence: {config['min_confidence']*100:.0f}%")
    print(f"Min Return: {config['min_return']*100:.1f}%")
    print(f"Max Opportunities/Cycle: {config['max_per_cycle']}")
    print(f"Mode: {'LIVE TRADING' if config['live'] else 'PAPER TRADING'}")
    print("="*80)
    
    confirm = input("\nProceed with this configuration? (yes/no): ").lower()
    if confirm != 'yes':
        print("Deployment cancelled.")
        sys.exit(0)
    
    return config

async def main():
    """Main deployment function"""
    print("\n" + "="*80)
    print("PROMETHEUS AUTONOMOUS TRADING SYSTEM")
    print("   Production Deployment v2.0")
    print("="*80)
    
    # Check if automated configuration is provided
    if len(sys.argv) > 1:
        # Automated deployment with CLI args
        config = {
            'capital': float(sys.argv[1]) if len(sys.argv) > 1 else 10000,
            'duration_hours': float(sys.argv[2]) if len(sys.argv) > 2 else None,
            'scan_interval': int(sys.argv[3]) if len(sys.argv) > 3 else 60,
            'min_confidence': 0.65,
            'min_return': 0.008,
            'max_per_cycle': 5,
            'live': False
        }
        logger.info("Using automated configuration from command line")
    else:
        # Interactive configuration
        config = get_user_configuration()
    
    # Run production trading
    success = await run_production_trading(config)
    
    if success:
        print("\n[SUCCESS] Deployment completed successfully!")
        print(f"Logs saved to: reports/autonomous_trading_*.log")
    else:
        print("\n[ERROR] Deployment failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    # Run deployment
    asyncio.run(main())

