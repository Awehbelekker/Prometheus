"""
PROMETHEUS Dual Broker Status Checker
Checks current positions and account status on both IB and Alpaca
"""

import os
import sys
from datetime import datetime

os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'false'

print('\n' + '='*70)
print('  🔍 PROMETHEUS - DUAL BROKER STATUS CHECK')
print(f'  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*70)

# ============================================================================
# INTERACTIVE BROKERS CHECK
# ============================================================================
print('\n📊 INTERACTIVE BROKERS (IB Gateway Port 4002 - LIVE)')
print('-'*70)

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    import threading
    import time
    
    class IBChecker(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.positions = []
            self.account_value = {}
            self.connected = False
            self.done = False
            self.target_account = os.getenv('IB_ACCOUNT', 'U21922116')
            
        def nextValidId(self, orderId: int):
            self.connected = True
            self.reqPositions()
            # Request account summary for specific account
            self.reqAccountSummary(9001, 'All', 'NetLiquidation,TotalCashValue,UnrealizedPnL,RealizedPnL,BuyingPower')
            
        def position(self, account, contract, position, avgCost):
            # Only track positions for target account
            if account == self.target_account or account.endswith('2116'):
                self.positions.append({
                    'account': account,
                    'symbol': contract.symbol,
                    'quantity': position,
                    'avg_cost': avgCost,
                    'value': position * avgCost
                })
            
        def accountSummary(self, reqId, account, tag, value, currency):
            # Only track data for target account
            if account == self.target_account or account.endswith('2116'):
                self.account_value[tag] = value
            
        def positionEnd(self):
            pass
            
        def accountSummaryEnd(self, reqId):
            self.cancelPositions()
            self.cancelAccountSummary(reqId)
            self.done = True
    
    ib = IBChecker()
    ib.connect('127.0.0.1', 4002, clientId=998)
    
    api_thread = threading.Thread(target=ib.run, daemon=True)
    api_thread.start()
    
    # Wait for connection and data (give more time)
    for _ in range(60):  # 6 seconds
        if ib.done:
            break
        time.sleep(0.1)
    
    if ib.connected:
        print(f'✅ Connection: ACTIVE (Account: {ib.target_account})')
        net_liq = ib.account_value.get('NetLiquidation', 'N/A')
        cash = ib.account_value.get('TotalCashValue', 'N/A')
        unrealized = ib.account_value.get('UnrealizedPnL', 'N/A')
        realized = ib.account_value.get('RealizedPnL', 'N/A')
        buying_power = ib.account_value.get('BuyingPower', 'N/A')
        
        print(f'📈 Account Value: ${net_liq}')
        print(f'💵 Cash: ${cash}')
        print(f'💰 Buying Power: ${buying_power}')
        print(f'📊 Unrealized P&L: ${unrealized}')
        print(f'💰 Realized P&L: ${realized}')
        
        print(f'\n📍 Positions: {len(ib.positions)}')
        if ib.positions:
            for pos in ib.positions:
                symbol = pos['symbol']
                qty = pos['quantity']
                avg = pos['avg_cost']
                val = pos['value']
                print(f'   {symbol}: {qty} shares @ ${avg:.2f} = ${val:.2f}')
        else:
            print('   No open positions')
    else:
        print('❌ Connection: FAILED - IB Gateway may not be running')
        print('   Please check:')
        print('   1. IB Gateway is running')
        print('   2. Port 4002 is configured')
        print('   3. API connections are enabled')
    
    ib.disconnect()
    
except Exception as e:
    print(f'❌ IB Error: {str(e)}')
    print(f'   Type: {type(e).__name__}')

# ============================================================================
# ALPACA MARKETS CHECK
# ============================================================================
print('\n📊 ALPACA MARKETS (Live API)')
print('-'*70)

try:
    from alpaca.trading.client import TradingClient
    
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key:
        print('❌ ALPACA_API_KEY not found in environment')
    elif not api_secret:
        print('❌ ALPACA_SECRET_KEY not found in environment')
    else:
        client = TradingClient(api_key, api_secret, paper=False)
        
        account = client.get_account()
        positions = client.get_all_positions()
        
        print('✅ Connection: ACTIVE')
        print(f'📈 Account Value: ${float(account.equity):,.2f}')
        print(f'💵 Cash: ${float(account.cash):,.2f}')
        print(f'💰 Buying Power: ${float(account.buying_power):,.2f}')
        
        # Calculate P&L from positions if available
        if hasattr(account, 'unrealized_pl') and account.unrealized_pl:
            pl = float(account.unrealized_pl)
            plpc = (float(account.unrealized_plpc) * 100) if hasattr(account, 'unrealized_plpc') else 0
            print(f'📊 Unrealized P&L: ${pl:.2f} ({plpc:+.2f}%)')
        else:
            print(f'📊 Unrealized P&L: $0.00')
        
        print(f'\n📍 Positions: {len(positions)}')
        if positions:
            total_value = 0
            for pos in positions:
                qty = float(pos.qty)
                avg_price = float(pos.avg_entry_price)
                current_price = float(pos.current_price)
                current_value = qty * current_price
                pnl = float(pos.unrealized_pl)
                pnl_pct = float(pos.unrealized_plpc) * 100
                
                total_value += current_value
                
                print(f'\n   {pos.symbol}:')
                print(f'      Quantity: {qty}')
                print(f'      Avg Entry: ${avg_price:.4f}')
                print(f'      Current: ${current_price:.4f}')
                print(f'      Value: ${current_value:.2f}')
                print(f'      P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)')
            
            print(f'\n   Total Position Value: ${total_value:.2f}')
        else:
            print('   No open positions')
            
except Exception as e:
    print(f'❌ Alpaca Error: {str(e)}')
    print(f'   Type: {type(e).__name__}')

# ============================================================================
# SUMMARY
# ============================================================================
print('\n' + '='*70)
print('  ✅ STATUS CHECK COMPLETE')
print('='*70 + '\n')
