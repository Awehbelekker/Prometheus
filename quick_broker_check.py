"""Quick Alpaca and Broker Status Check"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  BROKER STATUS CHECK - January 26, 2026")
print("=" * 60)

# Alpaca
key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')

print("\n📊 ALPACA LIVE ACCOUNT")
print("-" * 60)

try:
    headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}
    r = requests.get('https://api.alpaca.markets/v2/account', headers=headers)
    
    if r.status_code == 200:
        d = r.json()
        print(f"✅ Status: {d.get('status')}")
        print(f"💵 Cash: ${float(d.get('cash', 0)):.2f}")
        print(f"📈 Portfolio Value: ${float(d.get('portfolio_value', 0)):.2f}")
        print(f"💰 Buying Power: ${float(d.get('buying_power', 0)):.2f}")
        print(f"📊 Equity: ${float(d.get('equity', 0)):.2f}")
        
        # Get positions
        r2 = requests.get('https://api.alpaca.markets/v2/positions', headers=headers)
        positions = r2.json()
        print(f"\n📍 Positions: {len(positions)}")
        if positions:
            for p in positions:
                symbol = p['symbol']
                qty = p['qty']
                entry = float(p['avg_entry_price'])
                current = float(p['current_price'])
                pnl = float(p['unrealized_pl'])
                print(f"   {symbol}: {qty} shares @ ${entry:.2f} | Now: ${current:.2f} | P/L: ${pnl:+.2f}")
        else:
            print("   (No open positions - all cash)")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# IB Check
print("\n📊 INTERACTIVE BROKERS")
print("-" * 60)
try:
    from ib_insync import IB
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=99)
    
    account = ib.accountSummary()
    nav = next((a.value for a in account if a.tag == 'NetLiquidation'), 'N/A')
    cash = next((a.value for a in account if a.tag == 'TotalCashValue'), 'N/A')
    
    print(f"✅ Connected: Account U21922116")
    print(f"💵 Net Liquidation: ${float(nav):.2f}")
    print(f"💰 Cash: ${float(cash):.2f}")
    
    positions = ib.positions()
    print(f"\n📍 Positions: {len(positions)}")
    for pos in positions:
        print(f"   {pos.contract.symbol}: {pos.position} shares @ ${pos.avgCost:.2f}")
    
    ib.disconnect()
except Exception as e:
    print(f"⚠️ IB Status: {e}")

print("\n" + "=" * 60)
print("  STATUS CHECK COMPLETE")
print("=" * 60)
