#!/usr/bin/env python3
"""
Start PROMETHEUS Trading System - Standalone Mode
Just the trading system without the heavy backend
"""

import asyncio
from launch_ultimate_prometheus_LIVE_TRADING import main

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Starting PROMETHEUS Trading System (Standalone Mode)")
    print("=" * 80)
    print("This will:")
    print("  1. Initialize Alpaca broker connection")
    print("  2. Initialize IB broker connection")
    print("  3. Start autonomous trading loop")
    print("  4. Generate AI signals every 30 seconds")
    print("  5. Execute trades automatically")
    print("=" * 80)
    print()
    
    # Run in standalone mode (creates its own API on port 8001)
    asyncio.run(main(standalone_mode=True))


