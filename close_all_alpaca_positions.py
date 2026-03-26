#!/usr/bin/env python3
"""
Close all Alpaca positions to free up capital for recovery mode
"""
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
from datetime import datetime

def close_all_positions():
    """Close all open positions"""
    try:
        load_dotenv()
        
        # Connect to Alpaca LIVE
        api_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET')
        
        api = tradeapi.REST(api_key, secret_key, base_url='https://api.alpaca.markets')
        
        # Get current positions
        positions = api.list_positions()
        
        if not positions:
            print("\n[CHECK] No positions to close")
            return
        
        print("\n" + "=" * 80)
        print("🔄 CLOSING ALL ALPACA POSITIONS")
        print("=" * 80)
        print(f"\nFound {len(positions)} positions to close\n")
        
        total_value = 0
        closed_count = 0
        failed_count = 0
        
        for position in positions:
            symbol = position.symbol
            qty = float(position.qty)
            current_price = float(position.current_price)
            market_value = float(position.market_value)
            unrealized_pl = float(position.unrealized_pl)
            
            total_value += abs(market_value)
            
            print(f"Closing {symbol}: {qty:.6f} @ ${current_price:.4f} | P&L: ${unrealized_pl:.2f}")
            
            try:
                # Close position (market order)
                api.close_position(symbol)
                closed_count += 1
                print(f"  [CHECK] Closed successfully")
            except Exception as e:
                failed_count += 1
                print(f"  [ERROR] Failed: {e}")
        
        print("\n" + "=" * 80)
        print(f"[CHECK] Closed: {closed_count}")
        print(f"[ERROR] Failed: {failed_count}")
        print(f"💰 Total value freed: ${total_value:.2f}")
        print("=" * 80)
        
        # Wait a moment for orders to settle
        import time
        print("\n⏳ Waiting 5 seconds for orders to settle...")
        time.sleep(5)
        
        # Check final account status
        account = api.get_account()
        print(f"\n💰 FINAL ACCOUNT STATUS:")
        print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        remaining_positions = api.list_positions()
        if remaining_positions:
            print(f"\n[WARNING]️  Warning: {len(remaining_positions)} positions still open")
        else:
            print(f"\n[CHECK] All positions closed successfully!")
            print(f"[CHECK] Ready for recovery mode with ${float(account.cash):,.2f}")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")

if __name__ == "__main__":
    close_all_positions()

