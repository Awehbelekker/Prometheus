#!/usr/bin/env python3
"""Full Alpaca + IB Trading Report"""
import requests
import json
from collections import defaultdict, Counter
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# ALPACA LIVE ACCOUNT
# ═══════════════════════════════════════════════════════════════
headers = {
    'APCA-API-KEY-ID': 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z',
    'APCA-API-SECRET-KEY': 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX'
}
base = 'https://api.alpaca.markets'

print("=" * 70)
print("  PROMETHEUS FULL TRADING REPORT — March 4, 2026")
print("=" * 70)

# ── Account ──
acct = requests.get(f'{base}/v2/account', headers=headers, timeout=10).json()
equity = float(acct.get('equity', 0))
cash = float(acct.get('cash', 0))
portfolio_val = float(acct.get('portfolio_value', 0))
long_val = float(acct.get('long_market_value', 0))
buying_power = float(acct.get('buying_power', 0))

print(f"\n{'─'*70}")
print(f"  ALPACA LIVE ACCOUNT (#{acct.get('account_number', '?')})")
print(f"{'─'*70}")
print(f"  Status:          {acct.get('status')}")
print(f"  Equity:          ${equity:.2f}")
print(f"  Cash:            ${cash:.2f}")
print(f"  Long Value:      ${long_val:.2f}")
print(f"  Buying Power:    ${buying_power:.2f}")
print(f"  Pattern Day:     {acct.get('pattern_day_trader', 'N/A')}")
print(f"  Daytrade Count:  {acct.get('daytrade_count', 0)}")

# ── Open Positions ──
pos = requests.get(f'{base}/v2/positions', headers=headers, timeout=10).json()
print(f"\n  OPEN POSITIONS ({len(pos)})")
print(f"  {'Symbol':<10} {'Qty':>10} {'Entry':>10} {'Now':>10} {'P/L':>10} {'%':>8} {'Value':>10}")
print(f"  {'─'*68}")
total_unrealized = 0
for p in pos:
    sym = p['symbol']
    qty = float(p['qty'])
    entry = float(p['avg_entry_price'])
    curr = float(p['current_price'])
    pl = float(p['unrealized_pl'])
    plpct = float(p['unrealized_plpc']) * 100
    mkt_val = float(p['market_value'])
    total_unrealized += pl
    print(f"  {sym:<10} {qty:>10.6f} ${entry:>8.2f} ${curr:>8.2f} ${pl:>8.2f} {plpct:>+7.1f}% ${mkt_val:>8.2f}")
print(f"  {'─'*68}")
print(f"  {'TOTAL UNREALIZED':>42} ${total_unrealized:>8.2f}")

# ── ALL Orders (paginate by date) ──
all_orders = []
after_date = '2025-01-01T00:00:00Z'
max_pages = 20
for page in range(max_pages):
    url = f'{base}/v2/orders?status=all&limit=500&direction=asc&after={after_date}'
    resp = requests.get(url, headers=headers, timeout=15)
    data = resp.json()
    if isinstance(data, dict):
        if 'message' in data:
            print(f"  API pagination note: {data.get('message', 'unknown')}")
        break
    if not data:
        break
    all_orders.extend(data)
    # Next page starts after the last order's timestamp
    last_ts = data[-1].get('submitted_at') or data[-1].get('created_at')
    if last_ts and len(data) >= 500:
        after_date = last_ts
    else:
        break

filled = [o for o in all_orders if o['status'] == 'filled']
cancelled = [o for o in all_orders if o['status'] == 'canceled']
rejected = [o for o in all_orders if o['status'] in ('rejected', 'expired')]

print(f"\n  ORDER HISTORY")
print(f"  Total orders:    {len(all_orders)}")
print(f"  Filled:          {len(filled)}")
print(f"  Cancelled:       {len(cancelled)}")
print(f"  Rejected/Exp:    {len(rejected)}")

# ── Trade Analysis by Symbol ──
symbol_trades = defaultdict(list)
for o in filled:
    sym = o['symbol']
    side = o['side']
    qty = float(o.get('filled_qty') or o.get('qty') or 0)
    price = float(o['filled_avg_price']) if o.get('filled_avg_price') else 0
    date = o['filled_at'][:10] if o.get('filled_at') else o['submitted_at'][:10]
    notional = qty * price
    symbol_trades[sym].append({
        'date': date, 'side': side, 'qty': qty,
        'price': price, 'notional': notional
    })

print(f"\n  REALIZED P/L BY SYMBOL")
print(f"  {'Symbol':<10} {'Buys':>5} {'Sells':>5} {'AvgBuy':>10} {'AvgSell':>10} {'Realized':>10} {'Status':<15}")
print(f"  {'─'*68}")

total_realized = 0
winners = 0
losers = 0
for sym in sorted(symbol_trades.keys()):
    trades = symbol_trades[sym]
    buys = [t for t in trades if t['side'] == 'buy']
    sells = [t for t in trades if t['side'] == 'sell']
    
    buy_cost = sum(t['notional'] for t in buys)
    buy_qty = sum(t['qty'] for t in buys)
    sell_rev = sum(t['notional'] for t in sells)
    sell_qty = sum(t['qty'] for t in sells)
    
    avg_buy = buy_cost / buy_qty if buy_qty > 0 else 0
    avg_sell = sell_rev / sell_qty if sell_qty > 0 else 0
    
    matched_qty = min(buy_qty, sell_qty)
    if matched_qty > 0 and avg_buy > 0:
        realized = matched_qty * (avg_sell - avg_buy)
    else:
        realized = 0
    
    remaining_qty = buy_qty - sell_qty
    total_realized += realized
    
    if realized > 0.001:
        winners += 1
    elif realized < -0.001:
        losers += 1
    
    status = 'CLOSED' if abs(remaining_qty) < 0.0001 else 'OPEN'
    print(f"  {sym:<10} {len(buys):>5} {len(sells):>5} ${avg_buy:>8.2f} ${avg_sell:>8.2f} ${realized:>+8.2f}   {status}")

print(f"  {'─'*68}")
print(f"  TOTAL REALIZED P/L: ${total_realized:+.2f}")
print(f"  Winners: {winners}  |  Losers: {losers}  |  Win Rate: {winners/(winners+losers)*100:.0f}%" if (winners+losers) > 0 else "")

# ── Activity Timeline ──
dates = sorted(set(o['filled_at'][:10] for o in filled if o.get('filled_at')))
if dates:
    print(f"\n  ACTIVITY TIMELINE")
    print(f"  First trade:     {dates[0]}")
    print(f"  Last trade:      {dates[-1]}")
    print(f"  Active days:     {len(dates)}")
    
    # Monthly breakdown
    months = Counter(d[:7] for d in dates)
    print(f"\n  Monthly Trade Counts:")
    for month in sorted(months.keys()):
        bar = '#' * months[month]
        print(f"    {month}: {months[month]:>3} trades  {bar}")

# ── Last 10 trades ──
print(f"\n  LAST 10 TRADES")
print(f"  {'Date':<12} {'Side':<5} {'Symbol':<10} {'Qty':>12} {'Price':>10}")
print(f"  {'─'*52}")
for o in sorted(filled, key=lambda x: x.get('filled_at', ''))[-10:]:
    date = o['filled_at'][:10] if o.get('filled_at') else '?'
    side = o['side'].upper()
    sym = o['symbol']
    qty = float(o.get('filled_qty') or o.get('qty') or 0)
    price = float(o['filled_avg_price']) if o.get('filled_avg_price') else 0
    print(f"  {date:<12} {side:<5} {sym:<10} {qty:>12.6f} ${price:>8.2f}")

# ── Account Performance ──
# Try to get portfolio history
try:
    hist = requests.get(f'{base}/v2/account/portfolio/history?period=3M&timeframe=1D',
                       headers=headers, timeout=10).json()
    if hist.get('equity'):
        equities = hist['equity']
        timestamps = hist['timestamp']
        if equities and len(equities) > 1:
            first_eq = None
            for e in equities:
                if e and e > 0:
                    first_eq = e
                    break
            last_eq = equities[-1]
            
            if first_eq and last_eq:
                growth = (last_eq - first_eq) / first_eq * 100
                peak = max(e for e in equities if e)
                trough = min(e for e in equities if e and e > 0)
                max_dd = (trough - peak) / peak * 100 if peak > 0 else 0
                
                print(f"\n  PORTFOLIO PERFORMANCE (3 months)")
                print(f"  Starting equity:  ${first_eq:.2f}")
                print(f"  Current equity:   ${last_eq:.2f}")
                print(f"  Growth:           {growth:+.2f}%")
                print(f"  Peak:             ${peak:.2f}")
                print(f"  Trough:           ${trough:.2f}")
                print(f"  Max Drawdown:     {max_dd:.1f}%")
except Exception as e:
    print(f"\n  (Portfolio history unavailable: {e})")

# ═══════════════════════════════════════════════════════════════
# IB ACCOUNT CHECK
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*70}")
print(f"  INTERACTIVE BROKERS ACCOUNT")
print(f"{'─'*70}")

# Check if IB Gateway is running
import socket
ib_ports = [4002, 7497, 4001, 7496]
ib_connected = False
ib_port = None
for port in ib_ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        if result == 0:
            ib_connected = True
            ib_port = port
            break
    except:
        pass

if ib_connected:
    print(f"  Status:          CONNECTED (port {ib_port})")
    # Try to get IB account info via ib_insync
    try:
        from ib_insync import IB
        ib = IB()
        ib.connect('127.0.0.1', ib_port, clientId=99, timeout=5)
        
        # Target the correct account (U21922116 has funds)
        TARGET_IB_ACCOUNT = 'U21922116'
        managed = ib.managedAccounts()
        print(f"  Managed accounts: {managed}")
        
        acct_values = {item.tag: item.value 
                      for item in ib.accountValues(account=TARGET_IB_ACCOUNT) 
                      if item.currency in ('USD', '', 'BASE')}
        
        ib_equity = float(acct_values.get('NetLiquidation', 0))
        ib_cash = float(acct_values.get('TotalCashValue', 0))
        ib_unrealized = float(acct_values.get('UnrealizedPnL', 0))
        ib_realized = float(acct_values.get('RealizedPnL', 0))
        ib_buying = float(acct_values.get('BuyingPower', 0))
        
        print(f"  Account:         {TARGET_IB_ACCOUNT}")
        print(f"  Net Liquidation: ${ib_equity:.2f}")
        print(f"  Cash:            ${ib_cash:.2f}")
        print(f"  Buying Power:    ${ib_buying:.2f}")
        print(f"  Unrealized P/L:  ${ib_unrealized:.2f}")
        print(f"  Realized P/L:    ${ib_realized:.2f}")
        
        # Positions
        positions = ib.positions()
        if positions:
            print(f"\n  IB POSITIONS ({len(positions)})")
            for p in positions:
                sym = p.contract.symbol
                qty = p.position
                avg_cost = p.avgCost
                mkt_val = qty * avg_cost
                print(f"    {sym:<10} qty={qty}  avgCost=${avg_cost:.2f}  value=${mkt_val:.2f}")
        else:
            print(f"  Positions:       (none)")
        
        # Recent trades
        trades = ib.trades()
        if trades:
            print(f"\n  IB RECENT TRADES ({len(trades)})")
            for t in trades[-10:]:
                c = t.contract
                o = t.order
                print(f"    {c.symbol} {o.action} {o.totalQuantity} @ {o.lmtPrice if o.lmtPrice else 'MKT'} — {t.orderStatus.status}")
        
        ib.disconnect()
    except ImportError:
        print(f"  (ib_insync not installed — cannot query IB details)")
    except Exception as e:
        print(f"  Connection error: {e}")
else:
    print(f"  Status:          NOT CONNECTED")
    print(f"  (IB Gateway/TWS not running on ports {ib_ports})")
    print(f"  Start IB Gateway or TWS to enable IB trading")

# ═══════════════════════════════════════════════════════════════
# COMBINED SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print(f"  COMBINED SUMMARY")
print(f"{'═'*70}")
print(f"  Alpaca Equity:     ${equity:.2f}")
if ib_connected:
    try:
        print(f"  IB Equity:         ${ib_equity:.2f}")
        print(f"  Combined Equity:   ${equity + ib_equity:.2f}")
    except:
        print(f"  IB Equity:         (unavailable)")
        print(f"  Combined Equity:   ${equity:.2f}")
else:
    print(f"  IB Equity:         (not connected)")
    print(f"  Combined Equity:   ${equity:.2f}")

print(f"\n  Alpaca Realized P/L:  ${total_realized:+.2f}")
print(f"  Alpaca Unrealized:    ${total_unrealized:+.2f}")
print(f"  Alpaca Total P/L:     ${total_realized + total_unrealized:+.2f}")

print(f"\n{'═'*70}")
