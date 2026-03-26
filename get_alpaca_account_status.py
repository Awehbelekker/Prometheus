#!/usr/bin/env python3
"""
Get Alpaca Account Status - Direct API Call
"""

import requests
import os
from datetime import datetime

# Load API keys from .env
api_key = None
secret_key = None

with open('.env', 'r') as f:
    for line in f:
        if 'ALPACA_LIVE_KEY' in line and '=' in line and 'SECRET' not in line:
            api_key = line.split('=', 1)[1].strip()
        elif 'ALPACA_LIVE_SECRET' in line and '=' in line:
            secret_key = line.split('=', 1)[1].strip()

if not api_key or not secret_key:
    print("[ERROR] Could not load API keys")
    exit(1)

# Alpaca API endpoints
base_url = "https://api.alpaca.markets"
headers = {
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": secret_key
}

print("=" * 80)
print("💰 ALPACA LIVE ACCOUNT - ACTUAL P/L & RETURNS")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
print()

try:
    # Get account info
    response = requests.get(f"{base_url}/v2/account", headers=headers)
    response.raise_for_status()
    account = response.json()
    
    equity = float(account['equity'])
    last_equity = float(account['last_equity'])
    cash = float(account['cash'])
    buying_power = float(account['buying_power'])
    
    # Calculate returns
    daily_return = equity - last_equity
    daily_return_pct = (daily_return / last_equity * 100) if last_equity > 0 else 0
    
    print("📊 ACCOUNT SUMMARY")
    print("-" * 80)
    print(f"Account Number: {account['account_number']}")
    print(f"Account Status: {account['status']}")
    print()
    print(f"Current Equity: ${equity:.2f}")
    print(f"Previous Close Equity: ${last_equity:.2f}")
    print(f"Cash Available: ${cash:.2f}")
    print(f"Buying Power: ${buying_power:.2f}")
    print()
    
    print("📈 RETURNS")
    print("-" * 80)
    print(f"Daily P/L: ${daily_return:+.2f}")
    print(f"Daily Return: {daily_return_pct:+.2f}%")
    print()
    
    # Color code the return
    if daily_return > 0:
        print("[CHECK] PROFITABLE SESSION!")
        print(f"   You're UP ${daily_return:.2f} ({daily_return_pct:+.2f}%)")
    elif daily_return < 0:
        print("[WARNING]️ LOSING SESSION")
        print(f"   You're DOWN ${abs(daily_return):.2f} ({daily_return_pct:.2f}%)")
    else:
        print("➖ BREAK EVEN")
    print()
    
    # Get positions
    response = requests.get(f"{base_url}/v2/positions", headers=headers)
    response.raise_for_status()
    positions = response.json()
    
    print("💼 CURRENT POSITIONS")
    print("-" * 80)
    if positions:
        total_value = 0
        total_pl = 0
        long_count = 0
        short_count = 0
        
        print(f"{'Symbol':<12} {'Side':<6} {'Qty':<14} {'Entry':<12} {'Current':<12} {'P/L':<12} {'P/L %':<10}")
        print("-" * 80)
        
        for pos in positions:
            qty = float(pos['qty'])
            entry = float(pos['avg_entry_price'])
            current = float(pos['current_price'])
            pl = float(pos['unrealized_pl'])
            pl_pct = float(pos['unrealized_plpc']) * 100
            value = abs(qty) * current
            side = pos['side']
            
            if side == 'long':
                long_count += 1
            else:
                short_count += 1
            
            total_value += value
            total_pl += pl
            
            pl_symbol = "[CHECK]" if pl > 0 else "[ERROR]" if pl < 0 else "➖"
            print(f"{pos['symbol']:<12} {side:<6} {qty:<14.6f} ${entry:<11.2f} ${current:<11.2f} ${pl:<11.2f} {pl_pct:+.2f}% {pl_symbol}")
        
        print("-" * 80)
        print(f"Total Positions: {len(positions)} (LONG: {long_count}, SHORT: {short_count})")
        print(f"Total Position Value: ${total_value:.2f}")
        print(f"Total Unrealized P/L: ${total_pl:+.2f}")
        
        if total_value > 0:
            total_pl_pct = (total_pl / (total_value - total_pl)) * 100
            print(f"Total Unrealized P/L %: {total_pl_pct:+.2f}%")
        print()
        
        # Check for short positions
        if short_count == 0:
            print("🚨 WARNING: NO SHORT POSITIONS!")
            print("   All positions are LONG only")
            print("   System is NOT shorting the market")
        else:
            print(f"[CHECK] SHORT POSITIONS: {short_count}")
            print(f"[CHECK] LONG POSITIONS: {long_count}")
    else:
        print("No open positions (all cash)")
    print()
    
    # Get recent orders
    response = requests.get(f"{base_url}/v2/orders?status=all&limit=100", headers=headers)
    response.raise_for_status()
    orders = response.json()
    
    print("📋 ORDER STATISTICS (Last 100)")
    print("-" * 80)
    filled_count = sum(1 for o in orders if o['status'] == 'filled')
    pending_count = sum(1 for o in orders if o['status'] in ['new', 'pending_new', 'accepted'])
    rejected_count = sum(1 for o in orders if o['status'] in ['rejected', 'canceled'])
    
    # Count buy vs sell
    buy_count = sum(1 for o in orders if o['side'] == 'buy' and o['status'] == 'filled')
    sell_count = sum(1 for o in orders if o['side'] == 'sell' and o['status'] == 'filled')
    
    print(f"Total Orders: {len(orders)}")
    print(f"[CHECK] Filled: {filled_count} (BUY: {buy_count}, SELL: {sell_count})")
    print(f"⏳ Pending: {pending_count}")
    print(f"[ERROR] Rejected/Canceled: {rejected_count}")
    if orders:
        print(f"Success Rate: {(filled_count/len(orders)*100):.1f}%")
    print()
    
    print("=" * 80)
    print("🎯 SUMMARY")
    print("=" * 80)
    print(f"[CHECK] Account Equity: ${equity:.2f}")
    print(f"[CHECK] Daily Return: {daily_return_pct:+.2f}% (${daily_return:+.2f})")
    print(f"[CHECK] Open Positions: {len(positions)}")
    print(f"[CHECK] Orders Filled: {filled_count}")
    
    if daily_return > 0:
        print(f"[CHECK] Status: PROFITABLE! 🚀")
    elif daily_return < 0:
        print(f"[WARNING]️ Status: LOSING (Down {abs(daily_return_pct):.2f}%)")
    else:
        print(f"➖ Status: Break Even")
    
    if short_count == 0:
        print()
        print("🚨 CRITICAL: NO SHORT POSITIONS!")
        print("   → System is only going LONG")
        print("   → Cannot profit from bearish signals")
        print("   → This explains the losses!")
    
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

