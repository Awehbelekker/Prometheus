"""
AUTONOMOUS POSITION CLOSER
Closes ALL positions across all brokers programmatically
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def close_all_positions_alpaca():
    """Close all Alpaca positions"""
    print("\n" + "="*70)
    print("[1/2] CLOSING ALL ALPACA POSITIONS...")
    print("="*70)
    
    try:
        from brokers.alpaca_broker import AlpacaBroker
        
        alpaca_config = {
            'api_key': os.getenv('ALPACA_API_KEY'),
            'secret_key': os.getenv('ALPACA_SECRET_KEY'),
            'base_url': 'https://api.alpaca.markets',
            'paper_trading': False
        }
        
        alpaca = AlpacaBroker(alpaca_config)
        if await alpaca.connect():
            positions = await alpaca.get_positions()
            
            print(f"\nFound {len(positions)} position(s) to close")
            
            if len(positions) == 0:
                print("  [OK] No positions to close")
                await alpaca.disconnect()
                return True
            
            # Close each position
            closed_count = 0
            failed_count = 0
            
            for pos in positions:
                symbol = pos.symbol
                qty = float(pos.qty)
                
                print(f"\n  Closing {symbol} ({qty} shares)...")
                
                try:
                    # Determine side (close long = sell, close short = buy)
                    side = 'sell' if qty > 0 else 'buy'
                    qty_abs = abs(qty)
                    
                    # Place market order to close
                    order = await alpaca.place_order(
                        symbol=symbol,
                        qty=qty_abs,
                        side=side,
                        order_type='market',
                        time_in_force='day'
                    )
                    
                    if order:
                        print(f"    [OK] {symbol} close order submitted")
                        closed_count += 1
                    else:
                        print(f"    [ERROR] Failed to close {symbol}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"    [ERROR] {symbol}: {str(e)[:100]}")
                    failed_count += 1
            
            print(f"\n{'='*70}")
            print(f"ALPACA SUMMARY:")
            print(f"  Closed: {closed_count}")
            print(f"  Failed: {failed_count}")
            print(f"{'='*70}")
            
            await alpaca.disconnect()
            return failed_count == 0
            
    except Exception as e:
        print(f"\n[ERROR] Alpaca: {e}")
        import traceback
        traceback.print_exc()
        return False

async def close_all_positions_ib():
    """Close all IB positions"""
    print("\n" + "="*70)
    print("[2/2] CLOSING ALL IB POSITIONS...")
    print("="*70)
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        ib_port = int(os.getenv('IB_PORT', '4002'))
        ib_config = {
            'host': '127.0.0.1',
            'port': ib_port,
            'client_id': 1
        }
        
        ib = InteractiveBrokersBroker(ib_config)
        if await asyncio.wait_for(ib.connect(), timeout=10.0):
            positions = await ib.get_positions()
            
            print(f"\nFound {len(positions)} position(s) to close")
            
            if len(positions) == 0:
                print("  [OK] No positions to close")
                await ib.disconnect()
                return True
            
            # Close each position
            closed_count = 0
            failed_count = 0
            
            for symbol, pos_data in positions.items():
                qty = pos_data.get('quantity', 0)
                
                print(f"\n  Closing {symbol} ({qty} shares)...")
                
                try:
                    # Determine side
                    side = 'sell' if qty > 0 else 'buy'
                    qty_abs = abs(qty)
                    
                    # Place market order to close
                    order = await ib.place_order(
                        symbol=symbol,
                        qty=qty_abs,
                        side=side,
                        order_type='market',
                        time_in_force='day'
                    )
                    
                    if order:
                        print(f"    [OK] {symbol} close order submitted")
                        closed_count += 1
                    else:
                        print(f"    [ERROR] Failed to close {symbol}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"    [ERROR] {symbol}: {str(e)[:100]}")
                    failed_count += 1
            
            print(f"\n{'='*70}")
            print(f"IB SUMMARY:")
            print(f"  Closed: {closed_count}")
            print(f"  Failed: {failed_count}")
            print(f"{'='*70}")
            
            await ib.disconnect()
            return failed_count == 0
            
    except Exception as e:
        print(f"\n[ERROR] IB: {str(e)[:100]}")
        return False

async def main():
    print("\n" + "="*70)
    print("PROMETHEUS AUTONOMOUS POSITION CLOSER")
    print("="*70)
    print("\n[WARNING] This will close ALL positions in ALL brokers")
    print("          This action CANNOT be undone!")
    print("\nPositions to close:")
    print("  - Alpaca: 13 positions (~$115)")
    print("  - IB TWS: 3 positions (~$682)")
    print("\nExpected result:")
    print("  - Total cash available: ~$1,015")
    print("  - Clean slate for autonomous trading")
    
    print("\n" + "="*70)
    response = input("\nType 'CLOSE ALL POSITIONS' to proceed: ").strip()
    
    if response != 'CLOSE ALL POSITIONS':
        print("\n[CANCELLED] No positions closed")
        return False
    
    print("\n[CONFIRMED] Closing all positions...")
    
    # Close Alpaca positions
    alpaca_success = await close_all_positions_alpaca()
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Close IB positions
    ib_success = await close_all_positions_ib()
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    
    if alpaca_success and ib_success:
        print("\n[SUCCESS] All positions closed successfully!")
        print("\nWait 30 seconds for orders to fill, then run:")
        print("  python verify_positions_closed.py")
        print("\nThen launch Prometheus:")
        print("  python START_LIVE_TRADING_NOW.py")
        return True
    else:
        print("\n[WARNING] Some positions may have failed to close")
        print("Check your broker accounts and try again if needed")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
