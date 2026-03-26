#!/usr/bin/env python3
"""Exit all positions that have breached 2% stop loss."""
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
base = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
h = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}

STOP_LOSS_PCT = 0.02  # 2% stop loss from config
STABLECOINS = {'USDCUSD', 'USDTUSD'}

pos = requests.get(f'{base}/v2/positions', headers=h, timeout=10).json()

print("EXECUTING STOP-LOSS EXITS")
print("=" * 60)

sold = []
kept = []

for p in pos:
    sym = p['symbol']
    plpct = float(p['unrealized_plpc'])
    pl = float(p['unrealized_pl'])
    qty = p['qty']
    
    if sym in STABLECOINS:
        kept.append(f"{sym}: stablecoin, holding")
        continue
    
    if plpct < -STOP_LOSS_PCT:
        # Sell the position
        print(f"  SELLING {sym}: {plpct*100:+.2f}% ({pl:+.4f}) — breached {STOP_LOSS_PCT*100}% stop")
        
        # Close position via Alpaca API
        r = requests.delete(f'{base}/v2/positions/{sym}', headers=h, timeout=10)
        if r.status_code in (200, 204):
            data = r.json() if r.text else {}
            print(f"    -> Order submitted: {r.status_code}")
            sold.append(sym)
        else:
            print(f"    -> ERROR: {r.status_code} {r.text[:100]}")
    else:
        kept.append(f"{sym}: {plpct*100:+.2f}%, within tolerance")

print(f"\nSOLD: {len(sold)} positions ({', '.join(sold)})")
print(f"KEPT: {len(kept)} positions")
for k in kept:
    print(f"  {k}")

# Wait and check final state
time.sleep(3)
print("\n--- ACCOUNT AFTER EXITS ---")
acct = requests.get(f'{base}/v2/account', headers=h, timeout=10).json()
print(f"Equity:       ${float(acct['equity']):.2f}")
print(f"Cash:         ${float(acct['cash']):.2f}")
print(f"Buying Power: ${float(acct['buying_power']):.2f}")

pos2 = requests.get(f'{base}/v2/positions', headers=h, timeout=10).json()
print(f"Remaining positions: {len(pos2)}")
for p in pos2:
    print(f"  {p['symbol']}: {p['qty']} @ ${float(p['current_price']):.4f}  P/L: ${float(p['unrealized_pl']):+.4f}")
