#!/usr/bin/env python3
"""Debug why stop loss isn't triggering for AMD"""
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  STOP LOSS DEBUG - AMD")
print("=" * 70)

# Current settings
take_profit_pct = 0.025  # 2.5%
stop_loss_pct = 0.03     # 3%
min_profit_pct = 0.005   # 0.5%

print(f"\nSettings:")
print(f"  Take Profit: {take_profit_pct*100}%")
print(f"  Stop Loss: {stop_loss_pct*100}%")
print(f"  Min Profit: {min_profit_pct*100}%")

# Get all positions
positions = api.list_positions()
print(f"\nFound {len(positions)} positions\n")

positions_to_sell = []

for pos in positions:
    symbol = pos.symbol
    qty = float(pos.qty)
    avg_price = float(pos.avg_entry_price)
    market_value = float(pos.market_value)
    unrealized_pnl = float(pos.unrealized_pl)
    pnl_pct = float(pos.unrealized_plpc)  # Alpaca returns as decimal (e.g., -0.0674)
    
    print(f"{symbol}:")
    print(f"  Qty: {qty}")
    print(f"  Avg Price: ${avg_price:.2f}")
    print(f"  Current Value: ${market_value:.2f}")
    print(f"  P/L: ${unrealized_pnl:.2f} ({pnl_pct*100:.2f}%)")
    
    # Check exit conditions (same logic as in the trading engine)
    should_sell = False
    sell_reason = None
    
    # 1. TAKE PROFIT
    if pnl_pct >= take_profit_pct:
        should_sell = True
        sell_reason = f"TAKE_PROFIT ({pnl_pct*100:.2f}% >= {take_profit_pct*100:.1f}%)"
    
    # 2. STOP LOSS  
    elif pnl_pct <= -stop_loss_pct:
        should_sell = True
        sell_reason = f"STOP_LOSS ({pnl_pct*100:.2f}% <= -{stop_loss_pct*100:.1f}%)"
    
    # 3. SMALL PROFIT
    elif pnl_pct >= min_profit_pct:
        should_sell = True
        sell_reason = f"PROFIT_TAKING ({pnl_pct*100:.2f}% gain)"
    
    if should_sell:
        positions_to_sell.append({'symbol': symbol, 'reason': sell_reason, 'pnl_pct': pnl_pct})
        print(f"  >>> SHOULD SELL: {sell_reason}")
    else:
        print(f"  >>> NO ACTION")
    
    print()

print("=" * 70)
print(f"\nSUMMARY: {len(positions_to_sell)} positions should be sold:\n")
for p in positions_to_sell:
    emoji = "🛑" if "STOP_LOSS" in p['reason'] else "💰"
    print(f"  {emoji} {p['symbol']}: {p['reason']}")

if not positions_to_sell:
    print("  (None)")
    
print("\n" + "=" * 70)
print("\nISSUE ANALYSIS:")
print("-" * 70)

# Check AMD specifically
amd = [p for p in positions if p.symbol == 'AMD']
if amd:
    p = amd[0]
    pnl = float(p.unrealized_plpc)
    print(f"\nAMD P/L %: {pnl*100:.2f}%")
    print(f"Stop Loss Threshold: -{stop_loss_pct*100}%")
    print(f"Condition Check: pnl_pct ({pnl:.4f}) <= -stop_loss_pct ({-stop_loss_pct:.4f})")
    print(f"Result: {pnl} <= {-stop_loss_pct} = {pnl <= -stop_loss_pct}")
    
    if pnl <= -stop_loss_pct:
        print("\n*** AMD SHOULD BE SOLD but ISN'T - BUG CONFIRMED! ***")
        print("\nPossible causes:")
        print("1. Position monitor function not running")
        print("2. sell() method failing silently")
        print("3. Exception being caught and swallowed")
        print("4. Alpaca broker not connected properly")

