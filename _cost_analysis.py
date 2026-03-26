#!/usr/bin/env python3
"""Analyze trading costs, slippage, and breakeven requirements"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  TRADING COST & BREAKEVEN ANALYSIS")
print("=" * 70)

# Get recent filled orders
yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
orders = api.list_orders(status='filled', limit=100, after=f'{yesterday}T00:00:00Z')

print(f"\nAnalyzing {len(orders)} filled orders...")

# Analyze order types and potential slippage
market_orders = []
limit_orders = []
total_buy_value = 0
total_sell_value = 0

for o in orders:
    qty = float(o.filled_qty or 0)
    price = float(o.filled_avg_price or 0)
    value = qty * price
    
    if o.type == 'market':
        market_orders.append(o)
    else:
        limit_orders.append(o)
    
    if o.side == 'buy':
        total_buy_value += value
    else:
        total_sell_value += value

print(f"\n📊 ORDER TYPE BREAKDOWN:")
print(f"   Market Orders: {len(market_orders)}")
print(f"   Limit Orders: {len(limit_orders)}")
print(f"   Total Buy Volume: ${total_buy_value:.2f}")
print(f"   Total Sell Volume: ${total_sell_value:.2f}")

# Alpaca Fee Structure
print("\n" + "=" * 70)
print("  ALPACA FEE STRUCTURE")
print("=" * 70)

print("\n💰 COMMISSIONS:")
print("   Stock Trading: $0.00 (commission-free)")
print("   Crypto Trading: $0.00 (commission-free)")

print("\n📋 REGULATORY FEES (on SELLS only):")
print("   SEC Fee: $0.0000278 per $1 of sale proceeds")
print("   FINRA TAF: $0.000166 per share (max $8.30)")

# Calculate actual fees on sells
sec_fee = total_sell_value * 0.0000278
finra_fee = sum(float(o.filled_qty or 0) * 0.000166 for o in orders if o.side == 'sell')
total_fees = sec_fee + finra_fee

print(f"\n📊 YOUR ACTUAL FEES (Last 2 Days):")
print(f"   SEC Fee: ${sec_fee:.4f}")
print(f"   FINRA TAF: ${finra_fee:.4f}")
print(f"   TOTAL FEES: ${total_fees:.4f}")

# Slippage Analysis
print("\n" + "=" * 70)
print("  SLIPPAGE ANALYSIS")
print("=" * 70)

# Typical slippage for different order types
print("\n📈 TYPICAL SLIPPAGE:")
print("   Market Orders: 0.05% - 0.20% (depends on liquidity)")
print("   Limit Orders: 0.00% (but may not fill)")
print("   Extended Hours: 0.10% - 0.50% (wider spreads)")

# Estimate slippage based on order types
market_slippage_est = len(market_orders) * 5.40 * 0.001  # ~0.1% on avg $5.40 order
extended_hours_orders = [o for o in orders if o.submitted_at and (o.submitted_at.hour < 9 or o.submitted_at.hour >= 16)]
extended_slippage_est = len(extended_hours_orders) * 5.40 * 0.003  # ~0.3% extended hours

print(f"\n📊 ESTIMATED SLIPPAGE (Your Orders):")
print(f"   Market Order Slippage: ~${market_slippage_est:.4f}")
print(f"   Extended Hours Slippage: ~${extended_slippage_est:.4f}")
print(f"   TOTAL ESTIMATED SLIPPAGE: ~${market_slippage_est + extended_slippage_est:.4f}")

# Breakeven Calculation
print("\n" + "=" * 70)
print("  BREAKEVEN REQUIREMENTS")
print("=" * 70)

avg_position_size = 5.40  # Your typical position size
round_trip_fees = avg_position_size * 0.0000278  # SEC fee on sell
round_trip_slippage = avg_position_size * 0.002  # ~0.2% round trip slippage estimate
total_round_trip_cost = round_trip_fees + round_trip_slippage

breakeven_pct = (total_round_trip_cost / avg_position_size) * 100

print(f"\n💵 PER TRADE COSTS (${avg_position_size:.2f} position):")
print(f"   Commissions: $0.00")
print(f"   SEC Fee (sell): ${round_trip_fees:.6f}")
print(f"   Est. Slippage: ${round_trip_slippage:.4f}")
print(f"   TOTAL COST: ${total_round_trip_cost:.4f}")

print(f"\n🎯 BREAKEVEN REQUIREMENT:")
print(f"   Minimum Profit Needed: {breakeven_pct:.3f}%")
print(f"   On $5.40 position: ${total_round_trip_cost:.4f}")

print("\n" + "=" * 70)
print("  RECOMMENDATION")
print("=" * 70)

print(f"""
   Your costs are VERY LOW because:
   ✅ Alpaca is commission-free
   ✅ Small position sizes ($5-6 each)
   ✅ Regulatory fees are tiny (~$0.0001 per trade)
   
   MINIMUM PROFIT TO BREAKEVEN: ~0.20% - 0.25%
   
   Your current take profit (5%) is 20-25x the breakeven!
   Your stop loss (3%) is reasonable.
   
   The main cost is SLIPPAGE, not fees.
   To minimize slippage:
   - Use limit orders (PROMETHEUS already does this)
   - Avoid trading during extended hours when possible
   - Trade liquid stocks (SPY, AAPL, etc.) - you're doing this
""")

print("=" * 70)

