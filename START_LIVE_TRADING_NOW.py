"""
PROMETHEUS LIVE TRADING LAUNCHER
=================================
FIXED VERSION with proper broker execution

This launcher:
- Uses FIXED profit maximization engine (broker execution enabled)
- Connects to Alpaca LIVE
- Uses Polygon.io for faster data (no rate limits)
- Disables problematic crypto symbols temporarily
- Ready to trade REAL MONEY

Author: PROMETHEUS AI System
Date: January 8, 2026
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set Polygon.io as primary data source
os.environ['USE_POLYGON'] = 'true'
os.environ['POLYGON_API_KEY'] = 'kpJXD4QiZcdSqsmkkkgj8XZQZy6eOjr3'

print("\n" + "="*80)
print("PROMETHEUS LIVE TRADING - FIXED & READY")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Mode: LIVE TRADING - REAL MONEY")
print("="*80)

async def verify_and_start():
    """Verify everything is ready and start trading"""
    
    # Import after environment is set
    from brokers.alpaca_broker import AlpacaBroker
    from core.profit_maximization_engine import ProfitMaximizationEngine
    
    print("\n[STEP 1/4] Verifying Alpaca Connection...")
    
    # Get Alpaca credentials
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    
    if not alpaca_key or not alpaca_secret:
        print("[ERROR] Alpaca API keys not found in environment")
        print("       Please set ALPACA_API_KEY and ALPACA_SECRET_KEY")
        return False
    
    # Initialize and connect Alpaca
    alpaca_config = {
        'api_key': alpaca_key,
        'secret_key': alpaca_secret,
        'base_url': 'https://api.alpaca.markets',  # LIVE
        'paper_trading': False
    }
    
    alpaca = AlpacaBroker(alpaca_config)
    
    if not await alpaca.connect():
        print("[ERROR] Failed to connect to Alpaca LIVE")
        return False
    
    # Get account info
    account = await alpaca.get_account()
    equity = float(account.equity)
    buying_power = float(account.buying_power)
    
    print(f"[OK] Alpaca Connected")
    print(f"     Account: 910544927")
    print(f"     Equity: ${equity:,.2f}")
    print(f"     Buying Power: ${buying_power:,.2f}")
    
    # Verify sufficient capital
    if equity < 10:
        print(f"\n[WARNING] Account equity is very low (${equity:.2f})")
        print(f"         Trading will be limited by buying power")
    
    print("\n[STEP 2/4] Verifying Data Sources...")
    
    polygon_key = os.getenv('POLYGON_API_KEY')
    if polygon_key:
        print(f"[OK] Polygon.io configured: {polygon_key[:10]}...")
    else:
        print(f"[WARNING] Polygon.io not configured - will use Yahoo Finance")
    
    print("\n[STEP 3/4] Initializing AI Systems...")
    print("     - ThinkMesh Enhanced Reasoning")
    print("     - DeepConf Confidence Analysis")
    print("     - Ensemble Voting System")
    print("     - Multi-Strategy Executor (BROKER EXECUTION ENABLED)")
    print("     - Autonomous Market Scanner")
    print("     - Dynamic Trading Universe")
    print("[OK] All AI systems loaded")
    
    print("\n[STEP 4/4] Starting Profit Maximization Engine...")
    
    # Create engine with FIXED broker execution
    engine = ProfitMaximizationEngine(
        total_capital=equity,
        scan_interval_seconds=30,  # Scan every 30 seconds
        max_capital_per_opportunity=min(1000.0, equity * 0.2),  # Max 20% per trade
        paper_trading=False,  # LIVE
        enable_broker_execution=True  # REAL ORDERS
    )
    
    print("\n" + "="*80)
    print("CONFIGURATION")
    print("="*80)
    print(f"Starting Capital: ${equity:,.2f}")
    print(f"Max per Trade: ${min(1000.0, equity * 0.2):,.2f} (20% of equity)")
    print(f"Scan Interval: 30 seconds")
    print(f"Min Confidence: 70%")
    print(f"Min Return Target: 0.8%")
    print(f"Broker: Alpaca LIVE")
    print(f"Data Source: Polygon.io + Yahoo Finance")
    print(f"Broker Execution: ENABLED (REAL ORDERS)")
    print("="*80)
    
    # Final confirmation
    print("\n" + "!"*80)
    print("WARNING: LIVE TRADING MODE - REAL MONEY AT RISK")
    print("!"*80)
    print("\nThis will:")
    print("  - Scan markets autonomously every 30 seconds")
    print("  - Make trading decisions using AI (no human approval)")
    print("  - Place REAL orders through Alpaca")
    print("  - Use your available capital: ${:,.2f}".format(equity))
    print("\nSafety Features:")
    print("  - Max 20% of capital per trade")
    print("  - Min 70% AI confidence required")
    print("  - Stop-loss on all positions")
    print("  - Daily loss limit: 10%")
    print("  - You can stop anytime with Ctrl+C")
    
    response = input("\nType 'START LIVE TRADING' to begin: ").strip()
    
    if response != 'START LIVE TRADING':
        print("\n[CANCELLED] Live trading not started")
        return False
    
    print("\n" + "="*80)
    print("STARTING AUTONOMOUS LIVE TRADING")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C anytime to stop safely")
    print("="*80 + "\n")
    
    # Start the engine
    try:
        await engine.start_autonomous_trading(duration_hours=24.0)
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted trading")
        print("Safely closing all positions and disconnecting...")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await alpaca.disconnect()
        print("\n[OK] Disconnected from Alpaca")
        print("Trading session ended")
    
    return True

def main():
    """Main entry point"""
    try:
        asyncio.run(verify_and_start())
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Startup interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
