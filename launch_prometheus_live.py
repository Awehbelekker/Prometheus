#!/usr/bin/env python3
"""
Quick launcher for PROMETHEUS Live Dual Broker Trading
With timezone-aware market hours detection
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Check for --force flag to bypass market hours check
FORCE_RUN = '--force' in sys.argv or '--force-run' in sys.argv
CRYPTO_ONLY = '--crypto-only' in sys.argv or '--crypto' in sys.argv

def show_timezone_status():
    """Display timezone-aware market status before trading"""
    try:
        from timezone_trading_scheduler import TradingScheduler
        scheduler = TradingScheduler()
        status = scheduler.get_market_status()
        
        print("\n" + "=" * 60)
        print("🕐 TIMEZONE-AWARE MARKET STATUS")
        print("=" * 60)
        print(f"   Your Local Time:  {status['times']['local']}")
        print(f"   US Eastern Time:  {status['times']['eastern']}")
        
        session_status = {
            "regular": "🟢 MARKET OPEN - Regular Hours",
            "pre_market": "🟡 PRE-MARKET - Limited Liquidity",
            "after_hours": "🟠 AFTER-HOURS - Extended Trading",
            "closed": "🔴 MARKET CLOSED",
            "weekend": "⚫ WEEKEND - Markets Closed",
            "holiday": "🔵 HOLIDAY - Markets Closed"
        }
        print(f"\n   Status: {session_status.get(status['session'], status['session'])}")
        
        if status['time_to_open']:
            print(f"   ⏳ Opens in: {status['time_to_open']}")
            print(f"   📅 Next open: {status['next_open']}")
        if status['time_to_close']:
            print(f"   ⏳ Closes in: {status['time_to_close']}")
        
        if status['is_holiday']:
            print("\n   ⚠️ TODAY IS A MARKET HOLIDAY!")
        if status['is_early_close']:
            print(f"\n   ⚠️ EARLY CLOSE TODAY: {status['close_time']}")
        
        print("=" * 60 + "\n")
        
        return status['is_open'] or status['session'] in ['pre_market', 'after_hours']
        
    except Exception as e:
        print(f"[Timezone check skipped: {e}]")
        return True  # Proceed anyway


from final_dual_broker_fixed import FinalDualBrokerTradingSystem, main

if __name__ == "__main__":
    print("🚀 Launching PROMETHEUS Live Dual Broker Trading System...")
    print("   - IB Account U21922116: $251.58")
    print("   - Alpaca Account: $122.48")
    print("   - Total Capital: $374.06")
    print("   - AI Brain: Universal Reasoning Engine (IQ 145)")
    print("   - Timezone: Auto-detected (US Eastern for market hours)")
    print("")
    
    # Show timezone-aware market status
    can_trade = show_timezone_status()
    
    if can_trade:
        print("✅ Market is tradeable - launching PROMETHEUS...")
        asyncio.run(main())
    elif FORCE_RUN or CRYPTO_ONLY:
        print("⚠️ Market closed but --force or --crypto-only flag set")
        print("   Launching PROMETHEUS for crypto trading (24/7)...")
        asyncio.run(main())
    else:
        print("❌ Market is currently closed.")
        print("   Options:")
        print("   1. Wait for market open")
        print("   2. Trade crypto (24/7 available)")
        print("   3. Run paper trading for practice")
        print("\n   Run: python timezone_trading_scheduler.py for full schedule")
        print("\n   Or use: python launch_prometheus_live.py --force")
