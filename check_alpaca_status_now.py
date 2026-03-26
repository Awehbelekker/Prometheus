#!/usr/bin/env python3
"""
Check Current Alpaca Status
Shows connection, account, positions, and recent trades
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_alpaca_connection():
    """Check Alpaca connection and account status"""
    print_header("ALPACA CONNECTION STATUS")
    
    try:
        import alpaca_trade_api as tradeapi
        
        # Get credentials
        api_key = (os.getenv('ALPACA_API_KEY') or 
                  os.getenv('ALPACA_LIVE_KEY') or
                  os.getenv('APCA_API_KEY_ID'))
        secret_key = (os.getenv('ALPACA_SECRET_KEY') or 
                     os.getenv('ALPACA_LIVE_SECRET') or
                     os.getenv('APCA_API_SECRET_KEY'))
        base_url = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
        
        if not api_key or not secret_key:
            print("[ERROR] Alpaca API credentials not found")
            print("   Checked: ALPACA_API_KEY, ALPACA_LIVE_KEY, APCA_API_KEY_ID")
            return None
        
        print(f"[OK] API Key: Found ({len(api_key)} chars)")
        print(f"[OK] Secret Key: Found ({len(secret_key)} chars)")
        print(f"[OK] Base URL: {base_url}")
        print()
        
        # Connect to Alpaca
        print("Connecting to Alpaca...")
        api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
        
        # Get account
        account = api.get_account()
        
        print("[OK] Connected to Alpaca!")
        print()
        
        return api, account
        
    except ImportError:
        print("[ERROR] alpaca_trade_api not installed")
        print("   Install with: pip install alpaca-trade-api")
        return None
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

def show_account_status(api, account):
    """Show account status"""
    print_header("ACCOUNT STATUS")
    
    try:
        print(f"Account Number: {account.account_number}")
        print(f"Status: {account.status}")
        print(f"Trading Blocked: {account.trading_blocked}")
        print(f"Account Blocked: {account.account_blocked}")
        print()
        
        print("BALANCE INFORMATION:")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Equity: ${float(account.equity):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        print(f"  Pattern Day Trader: {account.pattern_day_trader}")
        print()
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to get account status: {e}")
        return False

def show_positions(api):
    """Show current positions"""
    print_header("CURRENT POSITIONS")
    
    try:
        positions = api.list_positions()
        
        if not positions:
            print("[INFO] No open positions")
            return
        
        print(f"Open Positions: {len(positions)}")
        print()
        
        total_value = 0
        for pos in positions:
            value = float(pos.qty) * float(pos.current_price)
            total_value += value
            
            print(f"Symbol: {pos.symbol}")
            print(f"  Quantity: {pos.qty}")
            print(f"  Current Price: ${float(pos.current_price):,.2f}")
            print(f"  Market Value: ${value:,.2f}")
            print(f"  Avg Entry Price: ${float(pos.avg_entry_price):,.2f}")
            print(f"  Unrealized P&L: ${float(pos.unrealized_pl):,.2f}")
            print(f"  Unrealized P&L %: {float(pos.unrealized_plpc):.2%}")
            print()
        
        print(f"Total Positions Value: ${total_value:,.2f}")
        print()
        
    except Exception as e:
        print(f"[ERROR] Failed to get positions: {e}")

def show_recent_orders(api):
    """Show recent orders"""
    print_header("RECENT ORDERS")
    
    try:
        orders = api.list_orders(status='all', limit=10)
        
        if not orders:
            print("[INFO] No recent orders")
            return
        
        print(f"Recent Orders: {len(orders)}")
        print()
        
        for order in orders:
            print(f"Order ID: {order.id}")
            print(f"  Symbol: {order.symbol}")
            print(f"  Side: {order.side}")
            print(f"  Quantity: {order.qty}")
            print(f"  Type: {order.order_type}")
            print(f"  Status: {order.status}")
            if order.filled_at:
                print(f"  Filled At: {order.filled_at}")
            if order.filled_avg_price:
                print(f"  Filled Price: ${float(order.filled_avg_price):,.2f}")
            print()
        
    except Exception as e:
        print(f"[ERROR] Failed to get orders: {e}")

def show_recent_activity(api):
    """Show recent account activity"""
    print_header("RECENT ACTIVITY")
    
    try:
        activities = api.get_activities(activity_types='FILL', limit=10)
        
        if not activities:
            print("[INFO] No recent activity")
            return
        
        print(f"Recent Activity: {len(activities)}")
        print()
        
        for activity in activities:
            print(f"Activity: {activity.activity_type}")
            print(f"  Symbol: {activity.symbol}")
            print(f"  Side: {activity.side}")
            print(f"  Quantity: {activity.qty}")
            print(f"  Price: ${float(activity.price):,.2f}")
            print(f"  Transaction Time: {activity.transaction_time}")
            print()
        
    except Exception as e:
        print(f"[ERROR] Failed to get activity: {e}")

def main():
    print("=" * 80)
    print("ALPACA STATUS CHECK")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check connection
    result = check_alpaca_connection()
    if not result:
        print()
        print("=" * 80)
        print("ALPACA NOT CONNECTED")
        print("=" * 80)
        return
    
    api, account = result
    
    # Show account status
    show_account_status(api, account)
    
    # Show positions
    show_positions(api)
    
    # Show recent orders
    show_recent_orders(api)
    
    # Show recent activity
    show_recent_activity(api)
    
    # Summary
    print()
    print("=" * 80)
    print("STATUS SUMMARY")
    print("=" * 80)
    print()
    print("[OK] Alpaca: CONNECTED")
    print(f"[OK] Account: {account.account_number}")
    print(f"[OK] Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"[OK] Buying Power: ${float(account.buying_power):,.2f}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStatus check cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Status check failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

