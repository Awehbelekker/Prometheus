"""
FINAL Position Closer - Handles Stocks & Crypto properly
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
        
        positions = client.get_all_positions()
        
        print(f"\nFound {len(positions)} position(s)")
        
        if not positions:
            print("  [OK] No positions to close")
            return True, 0
        
        closed = 0
        failed = 0
        
        for pos in positions:
            symbol = pos.symbol
            qty = abs(float(pos.qty))
            side = pos.side
            
            # Detect if crypto (ends with USD and not a stock)
            is_crypto = symbol.endswith('USD') and symbol not in ['GOOGL', 'AAPL', 'MSFT', 'TSLA', 'META', 'AMZN', 'NVDA']
            
            print(f"\n  Closing {symbol}: {qty} ({'crypto' if is_crypto else 'stock'})...")
            
            try:
                order_side = OrderSide.SELL if side == 'long' else OrderSide.BUY
                
                # Crypto uses GTC, stocks use DAY
                tif = TimeInForce.GTC if is_crypto else TimeInForce.DAY
                
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=tif
                )
                
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
        from ibapi.contract import Contract
        from ibapi.order import Order
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
        
        # Get positions list
        positions_data = await ib.get_positions()
        
        print(f"\nFound {len(positions_data) if positions_data else 0} position(s)")
        
        if not positions_data:
            print("  [OK] No positions to close")
            await ib.disconnect()
            return True, 0
        
        closed = 0
        failed = 0
        
        # Positions is a list of Position objects or dicts
        for pos_item in positions_data:
            # Extract symbol and qty
            if isinstance(pos_item, dict):
                symbol = pos_item.get('symbol', 'UNKNOWN')
                qty = pos_item.get('quantity', pos_item.get('qty', 0))
            else:
                # Position object
                symbol = getattr(pos_item, 'symbol', getattr(pos_item, 'contract', {}).symbol if hasattr(getattr(pos_item, 'contract', None), 'symbol') else 'UNKNOWN')
                qty = getattr(pos_item, 'quantity', getattr(pos_item, 'position', 0))
            
            if not symbol or symbol == 'UNKNOWN' or qty == 0:
                continue
            
            print(f"\n  Closing {symbol}: {qty} shares...")
            
            try:
                # Create contract
                contract = Contract()
                contract.symbol = symbol
                contract.secType = "STK"
                contract.exchange = "SMART"
                contract.currency = "USD"
                
                # Create order
                order = Order()
                order.action = "SELL" if qty > 0 else "BUY"
                order.orderType = "MKT"
                order.totalQuantity = abs(qty)
                
                # Place order
                order_id = ib.next_order_id
                if order_id:
                    ib.client.placeOrder(order_id, contract, order)
                    ib.next_order_id += 1
                    print(f"    [OK] Order placed (ID: {order_id})")
                    closed += 1
                else:
                    print(f"    [ERROR] No order ID available")
                    failed += 1
                    
            except Exception as e:
                print(f"    [ERROR] {str(e)[:100]}")
                failed += 1
        
        print(f"\n{'='*70}")
        print(f"IB: Closed {closed}/{len(positions_data)}, Failed {failed}")
        print(f"{'='*70}")
        
        await ib.disconnect()
        return failed == 0, closed
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)[:100]}")
        return False, 0

async def main():
    print("\n" + "="*70)
    print("PROMETHEUS - CLOSE ALL POSITIONS (FINAL)")
    print("="*70)
    
    alpaca_ok, alpaca_closed = await close_alpaca_positions()
    await asyncio.sleep(2)
    ib_ok, ib_closed = await close_ib_positions()
    
    total = alpaca_closed + ib_closed
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"\nTotal closed: {total} positions")
    print(f"  Alpaca: {alpaca_closed}")
    print(f"  IB: {ib_closed}")
    
    if alpaca_ok and ib_ok and total > 10:
        print("\n[SUCCESS] All positions closed!")
        print("\nWait 30 seconds for orders to fill...")
        print("Then verify: python verify_positions_closed.py")
        print("Then launch: python START_LIVE_TRADING_NOW.py")
    else:
        print(f"\n[RESULT] Closed {total} positions")
        if total < 10:
            print("Some positions may need manual closing")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())
