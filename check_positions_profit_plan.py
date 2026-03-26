"""
PROMETHEUS Position Analysis & Profit Plan
"""
from dotenv import load_dotenv
import os
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from datetime import datetime, timedelta

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
client = TradingClient(key, secret, paper=False)

print('='*70)
print(' PROMETHEUS CURRENT POSITIONS & PROFIT PLAN')
print('='*70)

# Get account
account = client.get_account()
print(f'\nAccount Value: ${float(account.equity):.2f}')
print(f'Cash Available: ${float(account.cash):.2f}')
print(f'Buying Power: ${float(account.buying_power):.2f}')

# Get positions
positions = client.get_all_positions()
print(f'\n[CURRENT POSITIONS: {len(positions)}]')
print('-'*70)

total_unrealized = 0
position_data = []

for pos in positions:
    symbol = pos.symbol
    qty = float(pos.qty)
    entry = float(pos.avg_entry_price)
    current = float(pos.current_price)
    market_val = float(pos.market_value)
    unrealized = float(pos.unrealized_pl)
    unrealized_pct = float(pos.unrealized_plpc) * 100
    
    total_unrealized += unrealized
    
    # Profit targets
    stop_loss = entry * 0.98  # 2% stop loss
    take_profit = entry * 1.05  # 5% take profit
    
    status = '🟢 PROFIT' if unrealized > 0 else '🔴 LOSS'
    
    position_data.append({
        'symbol': symbol,
        'qty': qty,
        'entry': entry,
        'current': current,
        'unrealized': unrealized,
        'unrealized_pct': unrealized_pct,
        'stop_loss': stop_loss,
        'take_profit': take_profit
    })
    
    print(f'{symbol}:')
    print(f'  Quantity: {qty:.6f}')
    print(f'  Entry Price: ${entry:.4f}')
    print(f'  Current Price: ${current:.4f}')
    print(f'  Market Value: ${market_val:.2f}')
    print(f'  Unrealized P/L: ${unrealized:.2f} ({unrealized_pct:+.2f}%) {status}')
    print(f'  🛑 Stop Loss: ${stop_loss:.4f} (-2%)')
    print(f'  🎯 Take Profit: ${take_profit:.4f} (+5%)')
    
    # Distance to targets
    dist_to_stop = ((current - stop_loss) / current) * 100
    dist_to_profit = ((take_profit - current) / current) * 100
    print(f'  Distance to Stop: {dist_to_stop:.1f}%')
    print(f'  Distance to Take Profit: {dist_to_profit:.1f}%')
    print()

print('-'*70)
print(f'TOTAL UNREALIZED P/L: ${total_unrealized:.2f}')

# Get recent orders to understand WHY trades were made
print('\n' + '='*70)
print(' WHY DID PROMETHEUS BUY THESE? (Recent Order History)')
print('='*70)

orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.ALL, limit=50))
filled_orders = [o for o in orders if o.status.value == 'filled']

# Group by symbol
from collections import defaultdict
by_symbol = defaultdict(list)
for o in filled_orders:
    by_symbol[o.symbol].append(o)

for symbol in [p['symbol'] for p in position_data]:
    symbol_orders = by_symbol.get(symbol, [])
    if symbol_orders:
        print(f'\n{symbol} Trade History:')
        recent = sorted(symbol_orders, key=lambda x: x.filled_at if x.filled_at else datetime.now(), reverse=True)[:5]
        for o in recent:
            side = o.side.value.upper()
            qty = float(o.filled_qty)
            price = float(o.filled_avg_price) if o.filled_avg_price else 0
            time = o.filled_at.strftime('%m/%d %H:%M') if o.filled_at else 'N/A'
            print(f'  {time} - {side} {qty:.6f} @ ${price:.4f}')

# PROFIT PLAN
print('\n' + '='*70)
print(' 📊 PROFIT PLAN & STRATEGY')
print('='*70)

print('''
CURRENT STRATEGY (Improved System):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Stop Loss: 2% (automatic exit if price drops)
✓ Take Profit: 5% (automatic exit when target reached)
✓ Higher Signal Threshold: 70% confidence required
✓ Trend Following: Only buy in confirmed uptrends

PROFIT TARGETS:
''')

for p in position_data:
    profit_needed = p['take_profit'] - p['current']
    profit_pct_needed = ((p['take_profit'] - p['current']) / p['current']) * 100
    potential_profit = (p['take_profit'] - p['entry']) * p['qty']
    
    print(f"{p['symbol']}:")
    print(f"  Current: ${p['current']:.4f}")
    print(f"  Target: ${p['take_profit']:.4f} (+{profit_pct_needed:.1f}% to go)")
    print(f"  Potential Profit: ${potential_profit:.2f}")
    print()

total_potential = sum((p['take_profit'] - p['entry']) * p['qty'] for p in position_data)
print(f'TOTAL POTENTIAL PROFIT (if all hit 5%): ${total_potential:.2f}')

print('\n' + '='*70)
print(' 🎯 RECOMMENDED ACTIONS')
print('='*70)

for p in position_data:
    if p['unrealized_pct'] <= -2:
        print(f"❌ {p['symbol']}: STOP LOSS TRIGGERED - SELL NOW")
    elif p['unrealized_pct'] >= 5:
        print(f"✅ {p['symbol']}: TAKE PROFIT TRIGGERED - SELL NOW")
    elif p['unrealized_pct'] > 0:
        print(f"🟢 {p['symbol']}: IN PROFIT ({p['unrealized_pct']:+.1f}%) - HOLD for +5%")
    else:
        print(f"🟡 {p['symbol']}: IN LOSS ({p['unrealized_pct']:+.1f}%) - HOLD (stop at -2%)")
