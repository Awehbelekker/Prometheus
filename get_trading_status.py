#!/usr/bin/env python3
"""Get trading status for Alpaca and IB"""

import os
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("TRADING STATUS - YESTERDAY (Nov 26, 2025)")
print("="*80)

# Check Alpaca
print("\nALPACA:")
api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')

if api_key and secret_key:
    try:
        from alpaca_trade_api import REST
        api = REST(api_key, secret_key, 'https://paper-api.alpaca.markets', api_version='v2')
        
        # Account
        account = api.get_account()
        print(f"  Account Status: {account.status}")
        print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        
        # Orders yesterday
        yesterday = datetime.now() - timedelta(days=1)
        orders = api.list_orders(status='all', after=yesterday.isoformat(), limit=50)
        print(f"\n  Orders Yesterday: {len(orders)}")
        
        filled = [o for o in orders if o.status == 'filled']
        if filled:
            print(f"  Filled Orders: {len(filled)}")
            for o in filled[:5]:
                print(f"    - {o.symbol} {o.side.upper()} {o.filled_qty} @ ${float(o.filled_avg_price):.2f} ({o.created_at})")
        
        # Positions
        positions = api.list_positions()
        print(f"\n  Current Positions: {len(positions)}")
        for p in positions[:5]:
            print(f"    - {p.symbol}: {p.qty} shares, P&L: ${float(p.unrealized_pl):.2f}")
            
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("  Credentials not found")

# Check IB
print("\nINTERACTIVE BROKERS:")
try:
    import ibapi
    print("  IB API: Available")
    print("  Note: Requires TWS/Gateway connection to check status")
except:
    print("  IB API: Not installed")

print("\n" + "="*80)



