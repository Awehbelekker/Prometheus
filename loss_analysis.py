"""
PROMETHEUS Loss Analysis - Why is live trading losing money?
"""
from dotenv import load_dotenv
import os
load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from collections import defaultdict
from datetime import datetime, timedelta

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
client = TradingClient(key, secret, paper=False)

print('='*70)
print(' WHY IS PROMETHEUS LOSING MONEY? - DEEP ANALYSIS')
print('='*70)

orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.ALL, limit=500))
filled = [o for o in orders if o.status.value == 'filled']

# Group trades by symbol
by_symbol = defaultdict(list)
for o in filled:
    by_symbol[o.symbol].append({
        'side': str(o.side),
        'qty': float(o.filled_qty),
        'price': float(o.filled_avg_price) if o.filled_avg_price else 0,
        'time': o.filled_at,
        'value': float(o.filled_qty) * float(o.filled_avg_price or 0)
    })

print('\n[ANALYSIS BY SYMBOL]')
print('-'*70)

total_pl = 0
winners = 0
losers = 0
trade_details = []

for symbol in sorted(by_symbol.keys()):
    trades = by_symbol[symbol]
    buys = [t for t in trades if 'BUY' in t['side'].upper()]
    sells = [t for t in trades if 'SELL' in t['side'].upper()]
    
    buy_qty = sum(t['qty'] for t in buys)
    buy_val = sum(t['value'] for t in buys)
    sell_qty = sum(t['qty'] for t in sells)
    sell_val = sum(t['value'] for t in sells)
    
    avg_buy = buy_val / buy_qty if buy_qty > 0 else 0
    avg_sell = sell_val / sell_qty if sell_qty > 0 else 0
    
    # Only count closed trades (where we have both buys and sells)
    if sells and buys:
        closed_qty = min(buy_qty, sell_qty)
        pl = (avg_sell - avg_buy) * closed_qty
        total_pl += pl
        
        if pl > 0:
            winners += 1
            status = 'WIN'
        else:
            losers += 1
            status = 'LOSS'
        
        trade_details.append((symbol, buy_qty, avg_buy, sell_qty, avg_sell, pl, status))
        print(f'{symbol:12s} | Avg Buy: ${avg_buy:>8.4f} | Avg Sell: ${avg_sell:>8.4f} | P/L: ${pl:>+8.2f} | {status}')

print('-'*70)
print(f'Winning Symbols: {winners}')
print(f'Losing Symbols: {losers}')
if winners + losers > 0:
    print(f'Win Rate: {winners/(winners+losers)*100:.1f}%')
print(f'Estimated Total P/L from closed trades: ${total_pl:+.2f}')

# Trade frequency analysis
print('\n[TRADE FREQUENCY ANALYSIS]')
print('-'*70)

for symbol in sorted(by_symbol.keys()):
    trades = by_symbol[symbol]
    print(f'{symbol}: {len([t for t in trades if "BUY" in t["side"].upper()])} buys, {len([t for t in trades if "SELL" in t["side"].upper()])} sells')

# Problem identification
print('\n[ROOT CAUSE ANALYSIS]')
print('-'*70)

# Check for pattern: buying high, selling low
problem_trades = []
for symbol, trades in by_symbol.items():
    buys = [t for t in trades if 'BUY' in t['side'].upper()]
    sells = [t for t in trades if 'SELL' in t['side'].upper()]
    
    if buys and sells:
        avg_buy = sum(t['value'] for t in buys) / sum(t['qty'] for t in buys)
        avg_sell = sum(t['value'] for t in sells) / sum(t['qty'] for t in sells)
        
        if avg_sell < avg_buy * 0.99:  # Lost more than 1%
            loss_pct = (avg_sell/avg_buy - 1) * 100
            problem_trades.append((symbol, loss_pct, avg_buy, avg_sell))

print('\nPROBLEM 1: Buying High, Selling Low')
if problem_trades:
    for sym, loss, buy_p, sell_p in sorted(problem_trades, key=lambda x: x[1]):
        print(f'  {sym}: Bought @ ${buy_p:.4f}, Sold @ ${sell_p:.4f} = {loss:+.1f}%')
else:
    print('  None detected')

# Trading cost impact
print('\nPROBLEM 2: Trading Costs Eating Profits')
# Crypto spread + fees typically 0.3-0.6%
total_volume = sum(sum(t['value'] for t in trades) for trades in by_symbol.values())
estimated_fees = total_volume * 0.003  # 0.3% per trade
print(f'  Total Trading Volume: ${total_volume:.2f}')
print(f'  Estimated Trading Costs (0.3%): ${estimated_fees:.2f}')
print(f'  Net P/L after costs: ${total_pl - estimated_fees:.2f}')

# Overtrading check
print('\nPROBLEM 3: Overtrading Check')
total_trades = len(filled)
if total_trades > 0:
    first_trade = min(o.filled_at for o in filled if o.filled_at)
    last_trade = max(o.filled_at for o in filled if o.filled_at)
    days = (last_trade - first_trade).days + 1
    trades_per_day = total_trades / days
    print(f'  Total Trades: {total_trades}')
    print(f'  Trading Days: {days}')
    print(f'  Trades/Day: {trades_per_day:.1f}')
    if trades_per_day > 20:
        print(f'  WARNING: Overtrading detected! >20 trades/day increases costs')

# Signal quality check
print('\nPROBLEM 4: Signal Quality')
print(f'  Win Rate: {winners/(winners+losers)*100:.1f}%' if winners+losers > 0 else '  Win Rate: N/A')
if winners + losers > 0 and winners/(winners+losers) < 0.5:
    print('  WARNING: Win rate below 50% - signals need improvement')
    print('  SOLUTION: Increase signal confidence threshold')

# Recommendations
print('\n' + '='*70)
print(' RECOMMENDATIONS TO FIX LOSSES')
print('='*70)
print('''
1. INCREASE SIGNAL THRESHOLD: Current threshold may be too low
   - Raise from 0.6 to 0.75 for higher confidence trades

2. ADD TREND FILTER: Only trade in direction of overall trend
   - Use 200-day SMA as trend filter

3. REDUCE TRADE FREQUENCY: Less trades = less fees
   - Current: {:.0f} trades/day
   - Target: 5-10 high-quality trades/day

4. ADD STOP LOSSES: Limit downside on bad trades
   - Implement 2% stop loss on all positions

5. INCREASE HOLD TIME: Allow trades more time to profit
   - Current: Very short hold times
   - Target: Hold winners longer with trailing stops
'''.format(trades_per_day if 'trades_per_day' in dir() else 0))
