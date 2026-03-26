#!/usr/bin/env python
"""
PROMETHEUS Position Monitor - Standalone Script
Monitors positions and auto-sells based on profit/loss thresholds
"""
import time
import os
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROFIT_THRESHOLD = 0.5  # Take profit at 0.5%+
STOP_LOSS_THRESHOLD = -3.0  # Stop loss at -3%
CHECK_INTERVAL = 60  # Check every 60 seconds

# Initialize client
client = TradingClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), paper=False)

def check_and_sell_positions():
    """Check positions and sell those meeting criteria"""
    positions = client.get_all_positions()
    sold_count = 0
    
    for p in positions:
        pnl_pct = float(p.unrealized_plpc) * 100
        qty_available = float(p.qty_available)
        
        # Skip if no quantity available (pending order)
        if qty_available <= 0:
            continue
            
        # Skip stablecoins
        if p.symbol in ['USDCUSD', 'USDTUSD']:
            continue
        
        should_sell = False
        reason = ""
        
        if pnl_pct >= PROFIT_THRESHOLD:
            should_sell = True
            reason = f"PROFIT ({pnl_pct:.2f}%)"
        elif pnl_pct <= STOP_LOSS_THRESHOLD:
            should_sell = True
            reason = f"STOP-LOSS ({pnl_pct:.2f}%)"
        
        if should_sell:
            try:
                order = client.submit_order(MarketOrderRequest(
                    symbol=p.symbol,
                    qty=qty_available,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC
                ))
                print(f"  [SOLD] {p.symbol}: {reason} - Order ID: {order.id}")
                sold_count += 1
            except Exception as e:
                print(f"  [ERROR] Failed to sell {p.symbol}: {e}")
    
    return sold_count

def display_status():
    """Display current account and position status"""
    account = client.get_account()
    positions = client.get_all_positions()
    
    print(f"\n{'='*60}")
    print(f"PROMETHEUS POSITION MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Cash: ${float(account.cash):.2f} | Buying Power: ${float(account.buying_power):.2f}")
    print(f"Portfolio: ${float(account.portfolio_value):.2f} | Positions: {len(positions)}")
    print(f"{'-'*60}")
    
    for p in positions:
        pnl_pct = float(p.unrealized_plpc) * 100
        pnl_usd = float(p.unrealized_pl)
        marker = "+" if pnl_pct >= 0 else "-"
        status = ""
        if pnl_pct >= PROFIT_THRESHOLD:
            status = " [SELL-PROFIT]"
        elif pnl_pct <= STOP_LOSS_THRESHOLD:
            status = " [SELL-STOPLOSS]"
        print(f"  {marker} {p.symbol}: {pnl_pct:+.2f}% (${pnl_usd:+.2f}){status}")
    
    print(f"{'='*60}")

def main():
    print("\n" + "="*60)
    print("PROMETHEUS POSITION MONITOR STARTED")
    print(f"Profit Threshold: {PROFIT_THRESHOLD}%")
    print(f"Stop-Loss Threshold: {STOP_LOSS_THRESHOLD}%")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print("="*60)
    
    while True:
        try:
            display_status()
            sold = check_and_sell_positions()
            if sold > 0:
                print(f"\n>>> Sold {sold} position(s)")
            print(f"\nNext check in {CHECK_INTERVAL} seconds... (Ctrl+C to stop)")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\nPosition monitor stopped by user.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print(f"Retrying in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

