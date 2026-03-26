"""
QUICK START - Use Existing Broker Setup
========================================
Starts autonomous system using your EXISTING working broker infrastructure.
No new broker connections needed!
"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_with_existing_brokers():
    """Start autonomous system with existing broker setup"""
    
    print("\n" + "="*70)
    print("PROMETHEUS AUTONOMOUS SYSTEM - QUICK START")
    print("Using Your Existing Broker Infrastructure")
    print("="*70)
    
    try:
        # Import autonomous system
        from core.profit_maximization_engine import ProfitMaximizationEngine
        
        # Create engine (paper trading mode for safety)
        print("\n[1/3] Initializing Autonomous Engine...")
        engine = ProfitMaximizationEngine(
            total_capital=5000,  # Start with $5000
            scan_interval_seconds=30,  # Scan every 30 seconds
            max_capital_per_opportunity=500,  # Max $500 per trade
            paper_trading=True,  # SAFE - Paper trading
            enable_broker_execution=False  # Simulation mode first
        )
        
        print("[OK] Engine initialized")
        print(f"   Capital: ${engine.total_capital:,.2f}")
        print(f"   Mode: {'PAPER' if engine.paper_trading else 'LIVE'}")
        print(f"   Broker Execution: {'ENABLED' if engine.enable_broker_execution else 'SIMULATION'}")
        
        # Start autonomous trading
        print("\n[2/3] Starting Autonomous Trading...")
        print("   Duration: 5 minutes (test run)")
        print("   Press Ctrl+C to stop anytime")
        
        # Run for 5 minutes as test
        await engine.start_autonomous_trading(duration_hours=5/60)  # 5 minutes
        
        print("\n[3/3] Test Complete!")
        
        # Show results
        metrics = engine.get_metrics()
        print("\n" + "="*70)
        print("TEST RESULTS")
        print("="*70)
        print(f"Runtime: {metrics.runtime_minutes:.1f} minutes")
        print(f"Scan Cycles: {metrics.scan_cycles}")
        print(f"Opportunities Discovered: {metrics.opportunities_discovered}")
        print(f"Opportunities Executed: {metrics.opportunities_executed}")
        print(f"Capital Deployed: ${metrics.total_capital_deployed:,.2f}")
        print(f"Expected Return: {metrics.expected_total_return:.2%}")
        print("="*70)
        
        if metrics.opportunities_discovered > 0:
            print("\n[SUCCESS] System is finding opportunities!")
            print("\nNext steps:")
            print("1. Review the opportunities found")
            print("2. Enable broker execution when ready:")
            print("   enable_broker_execution=True")
        else:
            print("\n[INFO] No opportunities found in test period")
            print("This is normal - market conditions vary")
            print("Try running for longer or during market hours")
        
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Test stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

async def demo_discovery_only():
    """Demo: Just show market discovery (no execution)"""
    
    print("\n" + "="*70)
    print("DEMO: AUTONOMOUS MARKET DISCOVERY")
    print("="*70)
    
    try:
        from core.autonomous_market_scanner import autonomous_scanner
        from core.dynamic_trading_universe import dynamic_universe
        
        print("\n[INFO] Scanning ALL markets for opportunities...")
        opportunities = await autonomous_scanner.discover_best_opportunities(limit=10)
        
        if opportunities:
            print(f"\n[SUCCESS] Found {len(opportunities)} opportunities!")
            print("\nTop 5 Opportunities:")
            print("-" * 70)
            
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"\n{i}. {opp.symbol} ({opp.asset_class.value})")
                print(f"   Type: {opp.opportunity_type.value}")
                print(f"   Expected Return: {opp.expected_return:.2%}")
                print(f"   Confidence: {opp.confidence:.0%}")
                print(f"   Entry: ${opp.entry_price:.2f}")
                print(f"   Target: ${opp.target_price:.2f}")
                print(f"   Risk/Reward: {opp.risk_reward_ratio:.1f}")
                print(f"   Reasoning: {opp.reasoning}")
            
            # Update universe
            print("\n[INFO] Updating trading universe...")
            update = await dynamic_universe.update_universe(opportunities)
            print(f"[OK] Active symbols: {update['active_symbols']}")
            print(f"     Added: {len(update['added'])}")
            print(f"     Removed: {len(update['removed'])}")
            
        else:
            print("\n[INFO] No opportunities found right now")
            print("Try again during market hours or with different settings")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main menu"""
    print("\n" + "="*70)
    print("PROMETHEUS AUTONOMOUS SYSTEM")
    print("Quick Start Options")
    print("="*70)
    print("\n1. Full Test (5 minutes) - Recommended")
    print("2. Discovery Demo Only (30 seconds)")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(start_with_existing_brokers())
    elif choice == "2":
        asyncio.run(demo_discovery_only())
    else:
        print("\nExiting...")

if __name__ == "__main__":
    main()
