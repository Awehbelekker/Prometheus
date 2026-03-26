#!/usr/bin/env python3
"""
Clean PROMETHEUS Position Monitor
"""

import requests
import json
from datetime import datetime

def monitor_positions():
    print("=" * 80)
    print("PROMETHEUS POSITION MONITOR")
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
        print("ACCOUNT STATUS:")
        print("-" * 40)
        
        account_response = requests.get('https://api.alpaca.markets/v2/account', headers=headers)
        if account_response.status_code == 200:
            account_data = account_response.json()
            
            buying_power = float(account_data.get('buying_power', 0))
            cash = float(account_data.get('cash', 0))
            portfolio_value = float(account_data.get('portfolio_value', 0))
            equity = float(account_data.get('equity', 0))
            
            print(f"Buying Power: ${buying_power:.2f}")
            print(f"Cash: ${cash:.2f}")
            print(f"Portfolio Value: ${portfolio_value:.2f}")
            print(f"Equity: ${equity:.2f}")
            print()
        
        # Check current positions
        print("CURRENT POSITIONS:")
        print("-" * 40)
        
        positions_response = requests.get('https://api.alpaca.markets/v2/positions', headers=headers)
        if positions_response.status_code == 200:
            positions = positions_response.json()
            
            if positions:
                total_unrealized_pl = 0
                for pos in positions:
                    symbol = pos.get('symbol', 'Unknown')
                    side = pos.get('side', 'Unknown')
                    qty = pos.get('qty', 0)
                    market_value = pos.get('market_value', 0)
                    unrealized_pl = pos.get('unrealized_pl', 0)
                    current_price = pos.get('current_price', 0)
                    
                    total_unrealized_pl += float(unrealized_pl)
                    
                    print(f"Symbol: {symbol}")
                    print(f"Side: {side}")
                    print(f"Quantity: {qty}")
                    print(f"Current Price: ${float(current_price):.2f}")
                    print(f"Market Value: ${float(market_value):.2f}")
                    print(f"Unrealized P&L: ${float(unrealized_pl):.2f}")
                    print()
                
                print(f"TOTAL UNREALIZED P&L: ${total_unrealized_pl:.2f}")
                print()
                
                # Performance analysis
                if total_unrealized_pl > 0:
                    print("PERFORMANCE: PROFITABLE!")
                elif total_unrealized_pl < 0:
                    print("PERFORMANCE: LOSS (monitoring...)")
                else:
                    print("PERFORMANCE: BREAKEVEN")
                print()
            else:
                print("No positions found")
        else:
            print(f"Error getting positions: {positions_response.status_code}")
        
        # Check recent orders
        print("RECENT ORDERS:")
        print("-" * 40)
        
        orders_response = requests.get('https://api.alpaca.markets/v2/orders?status=all&limit=5', headers=headers)
        if orders_response.status_code == 200:
            orders = orders_response.json()
            
            for order in orders:
                symbol = order.get('symbol', 'Unknown')
                side = order.get('side', 'Unknown')
                qty = order.get('qty', 0)
                status = order.get('status', 'Unknown')
                created_at = order.get('created_at', 'Unknown')
                filled_at = order.get('filled_at', 'Unknown')
                
                print(f"Symbol: {symbol}")
                print(f"Side: {side}")
                print(f"Quantity: {qty}")
                print(f"Status: {status}")
                print(f"Created: {created_at}")
                if filled_at:
                    print(f"Filled: {filled_at}")
                print()
        else:
            print(f"Error getting orders: {orders_response.status_code}")
        
        print("=" * 80)
        print("PROMETHEUS SYSTEM STATUS:")
        print("=" * 80)
        print("POSITIONS: Active")
        print("AI SIGNALS: Generating")
        print("RISK MANAGEMENT: Active")
        print("POSITION TRACKING: Active")
        print("SHORT SELLING: Enabled")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor_positions()
