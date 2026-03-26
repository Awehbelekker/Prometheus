#!/usr/bin/env python3
"""
Trading Status Report for Alpaca and Interactive Brokers
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_alpaca_status():
    """Check Alpaca broker status and recent activity"""
    print("\n" + "="*80)
    print("ALPACA TRADING STATUS")
    print("="*80)
    
    # Check credentials
    api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
    secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
    
    print(f"\nCredentials:")
    print(f"  API Key: {'✅ Found' if api_key else '❌ Not found'}")
    print(f"  Secret Key: {'✅ Found' if secret_key else '❌ Not found'}")
    
    if not api_key or not secret_key:
        print("\n⚠️  Cannot check Alpaca - credentials missing")
        return
    
    try:
        from alpaca_trade_api import REST
        
        # Connect to paper trading
        api = REST(api_key, secret_key, 'https://paper-api.alpaca.markets', api_version='v2')
        
        # Get account info
        try:
            account = api.get_account()
            print(f"\nAccount Status:")
            print(f"  Status: {account.status}")
            print(f"  Buying Power: ${float(account.buying_power):,.2f}")
            print(f"  Cash: ${float(account.cash):,.2f}")
            print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"  Equity: ${float(account.equity):,.2f}")
        except Exception as e:
            print(f"\n⚠️  Could not get account info: {e}")
        
        # Get recent orders (yesterday)
        yesterday = datetime.now() - timedelta(days=1)
        print(f"\nRecent Orders (since {yesterday.strftime('%Y-%m-%d')}):")
        
        try:
            orders = api.list_orders(
                status='all',
                after=yesterday.isoformat(),
                limit=50
            )
            
            if orders:
                print(f"  Found {len(orders)} orders:")
                print("-" * 80)
                
                filled_orders = [o for o in orders if o.status == 'filled']
                pending_orders = [o for o in orders if o.status in ['new', 'accepted', 'pending_new']]
                
                print(f"\n  Filled Orders: {len(filled_orders)}")
                for order in filled_orders[:10]:
                    print(f"    ✅ {order.symbol} {order.side.upper()} {order.filled_qty} @ ${float(order.filled_avg_price):.2f}")
                    print(f"       Time: {order.created_at}")
                
                if pending_orders:
                    print(f"\n  Pending Orders: {len(pending_orders)}")
                    for order in pending_orders[:5]:
                        print(f"    ⏳ {order.symbol} {order.side.upper()} {order.qty} @ ${float(order.limit_price) if order.limit_price else 'Market'}")
                
            else:
                print("  No orders found")
                
        except Exception as e:
            print(f"  ⚠️  Could not get orders: {e}")
        
        # Get current positions
        try:
            positions = api.list_positions()
            if positions:
                print(f"\nCurrent Positions: {len(positions)}")
                print("-" * 80)
                for pos in positions:
                    pnl = float(pos.unrealized_pl)
                    pnl_pct = float(pos.unrealized_plpc) * 100
                    print(f"  {pos.symbol}: {pos.qty} shares")
                    print(f"    Avg Entry: ${float(pos.avg_entry_price):.2f}")
                    print(f"    Current: ${float(pos.current_price):.2f}")
                    print(f"    P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
            else:
                print("\nCurrent Positions: None")
        except Exception as e:
            print(f"\n⚠️  Could not get positions: {e}")
            
    except ImportError:
        print("\n⚠️  Alpaca library not installed: pip install alpaca-trade-api")
    except Exception as e:
        print(f"\n⚠️  Error checking Alpaca: {e}")

def check_ib_status():
    """Check Interactive Brokers status"""
    print("\n" + "="*80)
    print("INTERACTIVE BROKERS TRADING STATUS")
    print("="*80)
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        print("\nIB API Status:")
        print("  ✅ IB API library available")
        print("\nNote: IB requires TWS/Gateway to be running")
        print("      Connection status cannot be checked without active connection")
        
    except ImportError:
        print("\n⚠️  IB API library not installed: pip install ibapi")
    except Exception as e:
        print(f"\n⚠️  Error checking IB: {e}")

def main():
    print("\n" + "="*80)
    print("TRADING STATUS REPORT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    check_alpaca_status()
    check_ib_status()
    
    print("\n" + "="*80)
    print("REPORT COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()



