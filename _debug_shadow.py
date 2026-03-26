#!/usr/bin/env python3
"""Debug shadow trading to find why it dies silently after init."""
import asyncio
import sys
import traceback
import logging

# Force ALL logging to stderr so we see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stderr
)

async def test_shadow():
    print("=" * 60)
    print("SHADOW TRADING DEBUG TEST")
    print("=" * 60)
    
    # Step 1: Import
    print("\n[1] Importing multi_strategy_shadow_runner...")
    try:
        from multi_strategy_shadow_runner import MultiStrategyShadowRunner
        print("    OK")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 2: Create runner
    print("\n[2] Creating runner (conservative only, 3 symbols)...")
    try:
        runner = MultiStrategyShadowRunner(
            strategies=['conservative'],
            starting_capital=100000.0,
            watchlist=['AAPL', 'MSFT', 'SPY']
        )
        print("    OK")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 3: Create instance manually
    print("\n[3] Creating strategy instance...")
    try:
        instance = runner._create_strategy_instance('conservative')
        print(f"    OK - instance type: {type(instance).__name__}")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 4: Initialize AI
    print("\n[4] Initializing AI systems...")
    try:
        await instance.initialize_all_ai_systems()
        print("    OK - AI systems initialized")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 5: Get market data
    print("\n[5] Getting market data (yfinance)...")
    try:
        market_data = await instance.get_market_data(['AAPL', 'MSFT', 'SPY'])
        print(f"    OK - got data for {len(market_data)} symbols: {list(market_data.keys())}")
        if market_data:
            sym = list(market_data.keys())[0]
            print(f"    Sample ({sym}): price=${market_data[sym]['price']:.2f}")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 6: Make AI decision
    print("\n[6] Making AI decision...")
    try:
        if market_data:
            sym = list(market_data.keys())[0]
            decision = await instance.make_ai_decision(sym, market_data[sym])
            print(f"    OK - {sym}: {decision['action']} (confidence={decision.get('confidence', 'N/A')})")
            print(f"    Reason: {decision.get('reason', 'N/A')[:100]}")
        else:
            print("    SKIP - no market data")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    # Step 7: Test _run_single_strategy for 1 iteration
    print("\n[7] Running single strategy (max_iterations=1)...")
    try:
        await runner._run_single_strategy(
            strategy_name='conservative',
            interval_seconds=5,
            max_iterations=1,
            report_interval=1
        )
        print("    OK - 1 iteration completed")
    except Exception as e:
        print(f"    FAIL: {e}")
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - Shadow trading works!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(test_shadow())
    except Exception as e:
        print(f"\nFATAL: {e}")
        traceback.print_exc()
