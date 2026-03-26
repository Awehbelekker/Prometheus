#!/usr/bin/env python3
"""
Working Micro Trading Strategy with $64 Capital
"""

import requests
import json
from datetime import datetime

def working_micro_trading():
    print("=" * 80)
    print("WORKING MICRO TRADING STRATEGY WITH $64 CAPITAL")
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
        # Check account status
        print("CURRENT ACCOUNT STATUS:")
        print("-" * 40)
        
        account_response = requests.get('https://api.alpaca.markets/v2/account', headers=headers)
        if account_response.status_code == 200:
            account_data = account_response.json()
            
            buying_power = float(account_data.get('buying_power', 0))
            cash = float(account_data.get('cash', 0))
            portfolio_value = float(account_data.get('portfolio_value', 0))
            
            print(f"Buying Power: ${buying_power:.2f}")
            print(f"Cash: ${cash:.2f}")
            print(f"Portfolio Value: ${portfolio_value:.2f}")
            print()
            
            if buying_power < 5.0:
                print("CAPITAL TOO LOW FOR MEANINGFUL TRADING")
                print("Recommendation: Use paper trading instead")
                return
            
            print("MICRO TRADING STRATEGY:")
            print("-" * 40)
            print()
            
            # Strategy parameters
            position_size = buying_power * 0.15  # 15% per trade (about $10)
            max_positions = 2  # Only 2 positions with $64
            target_symbols = ['BTC/USD', 'ETH/USD']
            
            print(f"Position Size: ${position_size:.2f} per trade")
            print(f"Max Positions: {max_positions}")
            print(f"Target Symbols: {', '.join(target_symbols)}")
            print()
            
            # Place micro trades using estimated prices
            print("PLACING MICRO TRADES:")
            print("-" * 40)
            
            # Use estimated prices for crypto
            estimated_prices = {
                'BTC/USD': 108000.0,  # Estimated BTC price
                'ETH/USD': 3800.0,    # Estimated ETH price
            }
            
            trades_placed = 0
            for symbol in target_symbols:
                if trades_placed >= max_positions:
                    break
                
                estimated_price = estimated_prices.get(symbol, 0)
                if estimated_price <= 0:
                    continue
                
                # Calculate quantity for position size
                quantity = position_size / estimated_price
                
                print(f"Placing trade for {symbol}:")
                print(f"  Estimated Price: ${estimated_price:.2f}")
                print(f"  Quantity: {quantity:.8f}")
                print(f"  Value: ${position_size:.2f}")
                
                # Place buy order
                order_data = {
                    'symbol': symbol,
                    'qty': str(quantity),
                    'side': 'buy',
                    'type': 'market',
                    'time_in_force': 'gtc'
                }
                
                order_response = requests.post('https://api.alpaca.markets/v2/orders', headers=headers, json=order_data)
                
                if order_response.status_code == 200:
                    order_result = order_response.json()
                    print(f"  Order placed: {order_result.get('id')}")
                    print(f"  Status: {order_result.get('status')}")
                    trades_placed += 1
                else:
                    print(f"  Order failed: {order_response.status_code}")
                    print(f"  Error: {order_response.text}")
                
                print()
            
            print(f"Trades placed: {trades_placed}/{max_positions}")
            print()
            
            # Check final account status
            print("FINAL ACCOUNT STATUS:")
            print("-" * 40)
            
            final_account_response = requests.get('https://api.alpaca.markets/v2/account', headers=headers)
            if final_account_response.status_code == 200:
                final_account_data = final_account_response.json()
                print(f"Buying Power: ${final_account_data.get('buying_power', 0)}")
                print(f"Cash: ${final_account_data.get('cash', 0)}")
                print(f"Portfolio Value: ${final_account_data.get('portfolio_value', 0)}")
            
            print()
            print("=" * 80)
            print("MICRO TRADING COMPLETE!")
            print("=" * 80)
            print()
            print("NEXT STEPS:")
            print("1. Monitor positions in Alpaca dashboard")
            print("2. Let PROMETHEUS system manage the trades")
            print("3. Watch for profit/loss")
            print("4. Learn from the experience")
            print("5. Consider paper trading for more learning")
            print("=" * 80)
            
        else:
            print(f"Error getting account: {account_response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    working_micro_trading()
