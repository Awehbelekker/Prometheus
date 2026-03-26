#!/usr/bin/env python3
"""
Liquidate existing positions to increase buying power
"""

import requests
import json
from datetime import datetime

def liquidate_positions():
    print("=" * 80)
    print("LIQUIDATING POSITIONS TO INCREASE BUYING POWER")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Alpaca API credentials
    api_key = 'AKNGMUQPQGCFKRMTM5QG'
    secret_key = '7dNZf4igDG89MBp9dAzd7IabiAxsCIMEvgaCH0Pb'
    
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    try:
        # Check current positions
        print("CHECKING CURRENT POSITIONS:")
        print("-" * 40)
        
        positions_response = requests.get('https://api.alpaca.markets/v2/positions', headers=headers)
        print(f"Status: {positions_response.status_code}")
        
        if positions_response.status_code == 200:
            positions = positions_response.json()
            print(f"Number of positions: {len(positions)}")
            
            if positions:
                print("\nCURRENT POSITIONS:")
                for pos in positions:
                    symbol = pos.get('symbol', 'Unknown')
                    side = pos.get('side', 'Unknown')
                    qty = pos.get('qty', 0)
                    market_value = pos.get('market_value', 0)
                    unrealized_pl = pos.get('unrealized_pl', 0)
                    
                    print(f"Symbol: {symbol}")
                    print(f"Side: {side}")
                    print(f"Quantity: {qty}")
                    print(f"Market Value: ${market_value}")
                    print(f"Unrealized P&L: ${unrealized_pl}")
                    print()
                
                # Liquidate all positions
                print("LIQUIDATING ALL POSITIONS:")
                print("-" * 40)
                
                for pos in positions:
                    symbol = pos.get('symbol', '')
                    side = pos.get('side', '')
                    qty = pos.get('qty', 0)
                    
                    if float(qty) > 0:
                        # Determine order side (opposite of position)
                        if side == 'long':
                            order_side = 'sell'
                        else:  # short
                            order_side = 'buy'
                        
                        print(f"Liquidating {symbol} {side} position...")
                        
                        # Create market order to close position
                        # For crypto, use 'gtc' instead of 'day'
                        order_data = {
                            'symbol': symbol,
                            'qty': str(abs(float(qty))),  # Use absolute value
                            'side': order_side,
                            'type': 'market',
                            'time_in_force': 'gtc'  # Good Till Cancelled for crypto
                        }
                        
                        # Submit order
                        order_response = requests.post('https://api.alpaca.markets/v2/orders', headers=headers, json=order_data)
                        
                        if order_response.status_code == 200:
                            order_result = order_response.json()
                            print(f"  Order placed: {order_result.get('id')}")
                            print(f"  Status: {order_result.get('status')}")
                        else:
                            print(f"  Order failed: {order_response.status_code}")
                            print(f"  Error: {order_response.text}")
                        print()
            else:
                print("No positions found to liquidate")
        else:
            print(f"Error getting positions: {positions_response.status_code}")
            print(f"Response: {positions_response.text}")
        
        # Check account after liquidation
        print("CHECKING ACCOUNT AFTER LIQUIDATION:")
        print("-" * 40)
        
        account_response = requests.get('https://api.alpaca.markets/v2/account', headers=headers)
        if account_response.status_code == 200:
            account_data = account_response.json()
            print(f"Buying Power: ${account_data.get('buying_power', 0)}")
            print(f"Cash: ${account_data.get('cash', 0)}")
            print(f"Portfolio Value: ${account_data.get('portfolio_value', 0)}")
            print(f"Equity: ${account_data.get('equity', 0)}")
        else:
            print(f"Error checking account: {account_response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    liquidate_positions()
