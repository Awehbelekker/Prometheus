#!/usr/bin/env python3
"""
PROMETHEUS LIVE TRADING PERFORMANCE ANALYSIS
Analyzes all trades from Alpaca and calculates real performance metrics
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from collections import defaultdict

load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus, OrderSide

def analyze_live_trading():
    key = os.getenv('ALPACA_API_KEY')
    secret = os.getenv('ALPACA_SECRET_KEY')
    
    client = TradingClient(key, secret, paper=False)
    
    print("="*70)
    print(" PROMETHEUS LIVE TRADING PERFORMANCE ANALYSIS")
    print("="*70)
    
    # Get account
    account = client.get_account()
    print(f"\n[ACCOUNT STATUS]")
    print(f"   Account:      {account.account_number}")
    print(f"   Equity:       ${float(account.equity):,.2f}")
    print(f"   Cash:         ${float(account.cash):,.2f}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    
    # Current positions
    positions = client.get_all_positions()
    print(f"\n[CURRENT POSITIONS] ({len(positions)})")
    total_position_value = 0
    total_unrealized_pl = 0
    for p in positions:
        value = float(p.market_value)
        pl = float(p.unrealized_pl)
        pl_pct = float(p.unrealized_plpc) * 100
        total_position_value += value
        total_unrealized_pl += pl
        print(f"   {p.symbol:12s} {float(p.qty):>12.6f} @ ${float(p.avg_entry_price):>10.4f} = ${value:>8.2f} ({pl:+.2f} / {pl_pct:+.1f}%)")
    
    print(f"   {'TOTAL':12s} {'':>12s} {'':>10s}   ${total_position_value:>8.2f} ({total_unrealized_pl:+.2f})")
    
    # Get all orders
    orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.ALL, limit=500))
    
    print(f"\n[ORDER HISTORY] ({len(orders)} orders)")
    
    # Analyze orders
    filled_orders = [o for o in orders if o.status.value == 'filled']
    buy_orders = [o for o in filled_orders if o.side == OrderSide.BUY]
    sell_orders = [o for o in filled_orders if o.side == OrderSide.SELL]
    
    print(f"   Filled:   {len(filled_orders)}")
    print(f"   Buys:     {len(buy_orders)}")
    print(f"   Sells:    {len(sell_orders)}")
    
    # Group by date
    orders_by_date = defaultdict(list)
    for o in filled_orders:
        date_str = o.filled_at.strftime("%Y-%m-%d") if o.filled_at else "Unknown"
        orders_by_date[date_str].append(o)
    
    print(f"\n[TRADING ACTIVITY BY DAY]")
    for date in sorted(orders_by_date.keys(), reverse=True)[:10]:
        day_orders = orders_by_date[date]
        buys = sum(1 for o in day_orders if o.side == OrderSide.BUY)
        sells = sum(1 for o in day_orders if o.side == OrderSide.SELL)
        symbols = set(o.symbol for o in day_orders)
        print(f"   {date}: {len(day_orders)} orders ({buys} buys, {sells} sells) - {', '.join(symbols)}")
    
    # Calculate realized P&L from closed trades
    print(f"\n[TRADE ANALYSIS]")
    
    # Match buys with sells to calculate P&L
    trades_by_symbol = defaultdict(list)
    for o in filled_orders:
        trades_by_symbol[o.symbol].append({
            'side': o.side,
            'qty': float(o.filled_qty),
            'price': float(o.filled_avg_price) if o.filled_avg_price else 0,
            'time': o.filled_at,
            'value': float(o.filled_qty) * float(o.filled_avg_price or 0)
        })
    
    total_realized_pl = 0
    total_buys = 0
    total_sells = 0
    
    for symbol, trades in trades_by_symbol.items():
        buys = [t for t in trades if t['side'] == OrderSide.BUY]
        sells = [t for t in trades if t['side'] == OrderSide.SELL]
        
        buy_value = sum(t['value'] for t in buys)
        sell_value = sum(t['value'] for t in sells)
        total_buys += buy_value
        total_sells += sell_value
        
        if sells:  # Only show if there were sells (closed trades)
            realized_pl = sell_value - buy_value
            total_realized_pl += realized_pl
            # print(f"   {symbol:12s} Bought: ${buy_value:>8.2f} | Sold: ${sell_value:>8.2f} | P/L: ${realized_pl:+.2f}")
    
    print(f"   Total Bought:    ${total_buys:,.2f}")
    print(f"   Total Sold:      ${total_sells:,.2f}")
    print(f"   Realized P/L:    ${total_realized_pl:+,.2f}")
    print(f"   Unrealized P/L:  ${total_unrealized_pl:+,.2f}")
    print(f"   TOTAL P/L:       ${total_realized_pl + total_unrealized_pl:+,.2f}")
    
    # Performance metrics
    print(f"\n[PERFORMANCE SUMMARY]")
    
    # Estimate starting capital from trades
    if filled_orders:
        first_order = min(filled_orders, key=lambda x: x.filled_at if x.filled_at else datetime.now())
        days_trading = (datetime.now(first_order.filled_at.tzinfo) - first_order.filled_at).days if first_order.filled_at else 1
        
        print(f"   First Trade:    {first_order.filled_at.strftime('%Y-%m-%d') if first_order.filled_at else 'Unknown'}")
        print(f"   Days Trading:   {days_trading}")
        print(f"   Trades/Day:     {len(filled_orders) / max(days_trading, 1):.1f}")
        
        # Win rate approximation (if we have position data)
        winning_positions = sum(1 for p in positions if float(p.unrealized_pl) > 0)
        if positions:
            print(f"   Current Win %:  {winning_positions/len(positions)*100:.1f}% ({winning_positions}/{len(positions)})")
    
    # Recent orders detail
    print(f"\n[RECENT ORDERS (Last 15)]")
    for o in orders[:15]:
        status = o.status.value
        side = "BUY " if o.side == OrderSide.BUY else "SELL"
        qty = float(o.qty)
        price = float(o.filled_avg_price) if o.filled_avg_price else 0
        value = qty * price
        time_str = o.filled_at.strftime("%Y-%m-%d %H:%M") if o.filled_at else o.created_at.strftime("%Y-%m-%d %H:%M")
        print(f"   {time_str} | {o.symbol:12s} | {side} {qty:>12.6f} | ${price:>10.4f} | ${value:>8.2f} | {status}")

if __name__ == "__main__":
    analyze_live_trading()
