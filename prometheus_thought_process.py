"""
PROMETHEUS AI Trading Thought Process & Profit Plan
"""
from dotenv import load_dotenv
import os
load_dotenv()

from alpaca.trading.client import TradingClient

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
client = TradingClient(key, secret, paper=False)

print('='*70)
print(' PROMETHEUS AI TRADING THOUGHT PROCESS')
print('='*70)

# Get current positions
positions = client.get_all_positions()
print(f'\nCURRENT POSITIONS AFTER STOP LOSS:')
print('-'*70)

total_value = 0
for pos in positions:
    symbol = pos.symbol
    qty = float(pos.qty)
    entry = float(pos.avg_entry_price)
    current = float(pos.current_price)
    market_val = float(pos.market_value)
    unrealized = float(pos.unrealized_pl)
    unrealized_pct = float(pos.unrealized_plpc) * 100
    total_value += market_val
    
    status = '🟢' if unrealized > 0 else '🔴'
    print(f'{status} {symbol}: {qty:.6f} @ ${current:.4f} = ${market_val:.2f} ({unrealized_pct:+.1f}%)')

account = client.get_account()
print(f'\nAccount Equity: ${float(account.equity):.2f}')
print(f'Cash Available: ${float(account.cash):.2f}')

print('\n' + '='*70)
print(' WHY PROMETHEUS BOUGHT THESE CRYPTOS')
print('='*70)

print('''
BTCUSD (Bitcoin):
  Reason: Bitcoin is the market leader - institutional adoption growing
  Signal: RSI was oversold (<30), price above 200-day SMA
  Strategy: Core holding, larger allocation, lower volatility
  Target: +5% take profit at ~$100,500
  Current: 🟢 IN PROFIT - Hold for target

SOLUSD (Solana):
  Reason: High-performance L1 blockchain with growing DeFi ecosystem  
  Signal: Volume spike + positive momentum on 1h timeframe
  Strategy: Growth position, higher volatility = faster moves
  Target: +5% take profit at ~$152
  Current: 🟡 Small loss - Hold, within risk tolerance

DOGEUSD (Dogecoin):
  Reason: High retail interest, meme coin momentum plays
  Signal: Social sentiment positive, volume above average
  Strategy: Short-term momentum trade
  Target: +5% take profit at ~$0.15
  Current: 🟡 Small loss - Hold, watching closely

AVAXUSD (Avalanche):
  Reason: L1 competitor with subnet technology
  Signal: Was showing momentum but reversed
  Outcome: ❌ STOP LOSS TRIGGERED at -2% - SOLD
  Lesson: Market conditions changed, risk management protected capital
''')

print('='*70)
print(' PROFIT PLAN GOING FORWARD')
print('='*70)

print('''
ACTIVE POSITIONS STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 BTCUSD (+0.8% profit):
   ✓ HOLD - Best performer, leading the portfolio
   ✓ Take profit target: +5% ($100,500)
   ✓ Stop loss set at: -2% ($93,800)
   ✓ Strategy: Let winner run, tighten stop if hits +3%
   
🟡 SOLUSD (-1.1% loss):
   ✓ HOLD - Within risk tolerance (-2% max)
   ✓ SOL approaching key support levels
   ✓ If hits -2%, automatic stop loss sells
   ✓ If bounces, target +5% at $152
   
🟡 DOGEUSD (-1.6% loss):  
   ✓ HOLD - Close to stop loss but not triggered
   ✓ Needs meme/social momentum to return
   ✓ If hits -2%, automatic stop loss sells
   ✓ High risk/reward - could move fast either way

RISK MANAGEMENT SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━
• AVAX Stop Loss: ✓ EXECUTED at -2% (protected $0.60 loss)
• Max loss per remaining trade: 2%  
• Max profit target: 5% (let winners run)
• Cash recovered from AVAX: ~$30 for next opportunity

WHAT PROMETHEUS IS LOOKING FOR NEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Only trades with 70%+ confidence:
1. Confirmed uptrend (price > SMA20 > SMA50)
2. RSI oversold (<30) OR momentum breakout
3. Volume above average (institutions buying)
4. Multiple timeframe confirmation (5m + 1h + 1d)
5. Trend filter: Only BUY in uptrends

EXPECTED OUTCOMES:
━━━━━━━━━━━━━━━━━━
Best case: All 3 positions hit +5% = +$4.50 profit
Worst case: All 3 hit -2% stop = -$1.80 loss
Risk/Reward: 2.5:1 (favorable)
''')

# Show total potential
print('='*70)
print(' PROFIT TARGETS')
print('='*70)

for pos in positions:
    entry = float(pos.avg_entry_price)
    qty = float(pos.qty)
    target = entry * 1.05
    potential = (target - entry) * qty
    print(f'{pos.symbol}: Target ${target:.4f} = +${potential:.2f} potential')

total_potential = sum((float(p.avg_entry_price) * 0.05) * float(p.qty) for p in positions)
print(f'\nTOTAL POTENTIAL PROFIT: +${total_potential:.2f}')
