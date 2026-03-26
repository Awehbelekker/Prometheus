"""Quick IB account check."""
import asyncio
import logging
logging.disable(logging.CRITICAL)

from brokers.interactive_brokers_broker import InteractiveBrokersBroker

async def main():
    config = {
        'host': '127.0.0.1',
        'port': 4002,
        'account_id': 'U21922116',
        'paper_trading': False,
        'client_id': 55
    }
    broker = InteractiveBrokersBroker(config)
    result = await broker.connect()
    
    if not broker.connected:
        print("FAILED to connect to IB Gateway")
        return
    
    print("Connected to IB Gateway")
    await asyncio.sleep(4)
    
    vals = broker.account_values
    
    # Print ALL account values for debugging
    want_keys = ['NetLiquidation', 'TotalCashValue', 'AvailableFunds', 'BuyingPower', 'GrossPositionValue', 'CashBalance', 'Cushion']
    printed = set()
    for vk, vv in sorted(vals.items()):
        for wk in want_keys:
            if wk.lower() in vk.lower() and vk not in printed:
                print(f"  {vk} = {vv}")
                printed.add(vk)
    
    if not printed:
        print("  No matching account values found. All keys:")
        for vk, vv in sorted(vals.items()):
            print(f"    {vk} = {vv}")
    
    # Positions
    print(f"\nPositions: {len(broker.positions_data)}")
    for sym, pos in broker.positions_data.items():
        print(f"  {sym}: {pos}")
    
    if not broker.positions_data:
        print("  (no open positions)")
    
    await broker.disconnect()
    print("\nDisconnected.")

asyncio.run(main())
