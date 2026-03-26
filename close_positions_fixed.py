"""
FIXED Position Closer - Handles actual API response format
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def close_alpaca_positions():
    print("\n" + "="*70)
    print("[1/2] CLOSING ALPACA POSITIONS")
    print("="*70)
    
    try:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_SECRET_KEY')
        
        client = TradingClient(api_key, api_secret, paper=False)
        
        # Get all positions
        positions = client.get_all_positions()
        
        print(f"\nFound {len(positions)} position(s)")
        
        if not positions:
            print("  [OK] No positions to close")
            return True, 0
        
        closed = 0
        failed = 0
        
        for pos in positions:
            symbol = pos.symbol
            qty = abs(float(pos.qty))  # Get absolute value
            side = pos.side  # 'long' or 'short'
            
            print(f"\n  Closing {symbol}: {qty} shares ({side})...")
            
            try:
                # Determine order side (opposite of position side)
                order_side = OrderSide.SELL if side == 'long' else OrderSide.BUY
                
                # Create market order
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=TimeInForce.DAY
                )
                
                # Submit order
                order = client.submit_order(order_data)
                
                print(f"    [OK] Order submitted: {order.id}")
                closed += 1
                
            except Exception as e:
                print(f"    [ERROR] {str(e)[:100]}")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"ALPACA: Closed {closed}/{len(positions)}, Failed {failed}")
        print(f"{'='*70}")
        
        return failed == 0, closed
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, 0

async def close_ib_positions():
    print("\n" + "="*70)
    print("[2/2] CLOSING IB POSITIONS")
    print("="*70)
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        ib_config = {
            'host': '127.0.0.1',
            'port': int(os.getenv('IB_PORT', '4002')),
            'client_id': 1
        }
        
        ib = InteractiveBrokersBroker(ib_config)
        
        if not await asyncio.wait_for(ib.connect(), timeout=10.0):
            print("  [ERROR] Could not connect to IB")
            return False, 0
        
        # Get positions - returns a list
        positions_data = await ib.get_positions()
        
        # positions_data might be a list or dict, handle both
        if isinstance(positions_data, dict):
            positions = list(positions_data.items())
        else:
            # It's a list, convert to (symbol, data) tuples
            positions = [(p.get('symbol', 'UNKNOWN'), p) for p in positions_data] if positions_data else []
        
        print(f"\nFound {len(positions)} position(s)")
        
        if not positions:
            print("  [OK] No positions to close")
            await ib.disconnect()
            return True, 0
        
        closed = 0
        failed = 0
        
        for symbol_or_tuple in positions:
            if isinstance(symbol_or_tuple, tuple):
                symbol, pos_data = symbol_or_tuple
            else:
                # Direct object
                symbol = symbol_or_tuple
                pos_data = symbol_or_tuple
            
            # Get quantity - try different attribute names
            qty = None
            if hasattr(pos_data, 'quantity'):
                qty = pos_data.quantity
            elif isinstance(pos_data, dict):
                qty = pos_data.get('quantity', pos_data.get('qty', 0))
            else:
                qty = getattr(pos_data, 'qty', 0)
            
            if qty == 0:
                continue
            
            print(f"\n  Closing {symbol}: {qty} shares...")
            
            try:
                # Determine side
                side = 'sell' if qty > 0 else 'buy'
                qty_abs = abs(qty)
                
                # Place order
                order = await ib.place_order(
                    symbol=symbol,
                    qty=qty_abs,
                    side=side,
                    order_type='market',
                    time_in_force='day'
                )
                
                if order:
                    print(f"    [OK] Order submitted")
                    closed += 1
                else:
                    print(f"    [ERROR] Order failed")
                    failed += 1
                    
            except Exception as e:
                print(f"    [ERROR] {str(e)[:100]}")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"IB: Closed {closed}/{len(positions)}, Failed {failed}")
        print(f"{'='*70}")
        
        await ib.disconnect()
        return failed == 0, closed
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return False, 0

async def main():
    print("\n" + "="*70)
    print("PROMETHEUS - CLOSE ALL POSITIONS")
    print("="*70)
    
    alpaca_ok, alpaca_closed = await close_alpaca_positions()
    await asyncio.sleep(2)
    ib_ok, ib_closed = await close_ib_positions()
    
    total = alpaca_closed + ib_closed
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal positions closed: {total}")
    print(f"  Alpaca: {alpaca_closed}")
    print(f"  IB: {ib_closed}")
    
    if alpaca_ok and ib_ok:
        print("\n[SUCCESS] All positions closed!")
        print("\nWait 30 seconds, then verify:")
        print("  python verify_positions_closed.py")
    else:
        print("\n[PARTIAL] Some may have failed - check manually")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
