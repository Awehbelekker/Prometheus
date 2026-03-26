#!/usr/bin/env python3
"""Check both Alpaca and IB broker status, positions, equity, and idle cash."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import requests

def check_alpaca():
    """Check Alpaca live account."""
    print("=" * 60)
    print(" ALPACA LIVE ACCOUNT")
    print("=" * 60)
    
    key = os.getenv('ALPACA_LIVE_API_KEY') or os.getenv('ALPACA_API_KEY')
    secret = os.getenv('ALPACA_LIVE_SECRET_KEY') or os.getenv('ALPACA_SECRET_KEY')
    
    if not key or not secret:
        print("ERROR: Alpaca API keys not found in .env")
        return
    
    base = 'https://api.alpaca.markets'
    headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}
    
    # Account
    try:
        acct = requests.get(f'{base}/v2/account', headers=headers, timeout=10).json()
    except Exception as e:
        print(f"ERROR connecting to Alpaca: {e}")
        return
    
    if 'code' in acct or 'message' in acct:
        print(f"ERROR: {acct}")
        return
    
    equity = float(acct.get('equity', 0))
    cash = float(acct.get('cash', 0))
    buying_power = float(acct.get('buying_power', 0))
    portfolio_val = float(acct.get('portfolio_value', 0))
    last_equity = float(acct.get('last_equity', 0))
    day_pl = equity - last_equity
    
    print(f"  Equity:         ${equity:.2f}")
    print(f"  Cash:           ${cash:.2f}")
    print(f"  Buying Power:   ${buying_power:.2f}")
    print(f"  Portfolio Val:  ${portfolio_val:.2f}")
    print(f"  Day P/L:        ${day_pl:+.2f}")
    print(f"  Status:         {acct.get('status')}")
    print()
    
    # Positions
    try:
        positions = requests.get(f'{base}/v2/positions', headers=headers, timeout=10).json()
    except Exception as e:
        print(f"ERROR getting positions: {e}")
        positions = []
    
    print(f"  POSITIONS ({len(positions)}):")
    total_unrealized = 0.0
    total_market_val = 0.0
    for p in positions:
        sym = p['symbol']
        qty = float(p['qty'])
        avg = float(p['avg_entry_price'])
        cur = float(p['current_price'])
        mkt_val = float(p['market_value'])
        unrealized = float(p['unrealized_pl'])
        unrealized_pct = float(p['unrealized_plpc']) * 100
        total_unrealized += unrealized
        total_market_val += mkt_val
        print(f"    {sym:6s}  qty={qty:>6.2f}  avg=${avg:>8.2f}  cur=${cur:>8.2f}  mkt=${mkt_val:>8.2f}  P/L=${unrealized:>+7.2f} ({unrealized_pct:>+6.2f}%)")
    
    print()
    print(f"  Total Market Value:   ${total_market_val:.2f}")
    print(f"  Total Unrealized P/L: ${total_unrealized:+.2f}")
    print(f"  Idle Cash:            ${cash:.2f}")
    print(f"  Invested:             ${equity - cash:.2f}")
    
    # Recent orders
    try:
        orders = requests.get(f'{base}/v2/orders', headers=headers, 
                             params={'status': 'closed', 'limit': 15, 'direction': 'desc'},
                             timeout=10).json()
    except:
        orders = []
    
    if orders:
        print(f"\n  RECENT CLOSED ORDERS ({len(orders)}):")
        for o in orders:
            sym = o.get('symbol', '?')
            side = o.get('side', '?')
            qty = o.get('filled_qty', '?')
            filled_avg = o.get('filled_avg_price', '?')
            created = str(o.get('created_at', '?'))[:19]
            status = o.get('status', '?')
            print(f"    {created}  {side:4s} {sym:6s}  qty={qty}  price=${filled_avg}  [{status}]")
    
    print()

def check_ib():
    """Check Interactive Brokers account."""
    print("=" * 60)
    print(" INTERACTIVE BROKERS ACCOUNT")
    print("=" * 60)
    
    ib_host = os.getenv('IB_HOST', '127.0.0.1')
    ib_port = int(os.getenv('IB_PORT', '4002'))
    ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
    ib_client_id = 99  # Use unique client ID to avoid conflicts with running server
    
    print(f"  Config: {ib_host}:{ib_port}  Account={ib_account}  ClientID={ib_client_id}")
    print()
    
    try:
        from ib_insync import IB, util
    except ImportError:
        print("  ERROR: ib_insync not installed. Run: pip install ib_insync")
        return
    
    ib = IB()
    try:
        ib.connect(ib_host, ib_port, clientId=ib_client_id, timeout=15)
        print("  Connected to IB Gateway!")
    except Exception as e:
        print(f"  ERROR connecting to IB: {e}")
        print("  Make sure IB Gateway/TWS is running and accepting connections.")
        return
    
    try:
        # Account summary
        account_values = ib.accountSummary(ib_account)
        
        summary = {}
        for av in account_values:
            if av.tag in ('NetLiquidation', 'TotalCashValue', 'BuyingPower', 
                         'GrossPositionValue', 'UnrealizedPnL', 'RealizedPnL',
                         'AvailableFunds', 'SettledCash', 'ExcessLiquidity'):
                summary[av.tag] = float(av.value) if av.value else 0.0
        
        print(f"  Net Liquidation:    ${summary.get('NetLiquidation', 0):.2f}")
        print(f"  Total Cash:         ${summary.get('TotalCashValue', 0):.2f}")
        print(f"  Buying Power:       ${summary.get('BuyingPower', 0):.2f}")
        print(f"  Gross Position Val: ${summary.get('GrossPositionValue', 0):.2f}")
        print(f"  Unrealized P/L:     ${summary.get('UnrealizedPnL', 0):+.2f}")
        print(f"  Realized P/L:       ${summary.get('RealizedPnL', 0):+.2f}")
        print(f"  Available Funds:    ${summary.get('AvailableFunds', 0):.2f}")
        print(f"  Settled Cash:       ${summary.get('SettledCash', 0):.2f}")
        print(f"  Excess Liquidity:   ${summary.get('ExcessLiquidity', 0):.2f}")
        print()
        
        # Idle Cash
        idle_cash = summary.get('TotalCashValue', 0)
        invested = summary.get('NetLiquidation', 0) - idle_cash
        print(f"  Idle Cash:          ${idle_cash:.2f}")
        print(f"  Invested:           ${invested:.2f}")
        print()
        
        # Positions
        positions = ib.positions(account=ib_account)
        print(f"  POSITIONS ({len(positions)}):")
        if not positions:
            print("    (no open positions)")
        for pos in positions:
            contract = pos.contract
            sym = contract.symbol
            qty = pos.position
            avg_cost = pos.avgCost
            # Try to get current market price
            print(f"    {sym:6s}  qty={qty:>8.2f}  avgCost=${avg_cost:>8.2f}")
        
        # Open orders
        open_orders = ib.openOrders()
        if open_orders:
            print(f"\n  OPEN ORDERS ({len(open_orders)}):")
            for order in open_orders:
                print(f"    {order.action} {order.totalQuantity} @ {order.lmtPrice if hasattr(order, 'lmtPrice') else 'MKT'}")
        
    except Exception as e:
        print(f"  ERROR querying IB: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            ib.disconnect()
            print("\n  Disconnected from IB.")
        except:
            pass
    
    print()

def main():
    print()
    print("PROMETHEUS DUAL-BROKER STATUS CHECK")
    print(f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_alpaca()
    check_ib()
    
    print("=" * 60)
    print(" CHECK COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
