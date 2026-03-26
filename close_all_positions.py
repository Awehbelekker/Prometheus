#!/usr/bin/env python3
"""
Close All Positions on Both Brokers
Frees up capital for fresh AI trading
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from ib_insync import IB, MarketOrder
import os
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

def close_alpaca_positions():
    """Close all Alpaca positions"""
    print("\n" + "="*70)
    print("💼 CLOSING ALPACA POSITIONS")
    print("="*70)
    
    client = TradingClient(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        paper=False
    )
    
    # Get all positions
    positions = client.get_all_positions()
    
    if not positions:
        print("\n✅ No Alpaca positions to close")
        return 0
    
    print(f"\n📊 Found {len(positions)} positions to close:")
    
    closed_count = 0
    total_pl = 0
    
    for pos in positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        entry = float(pos.avg_entry_price)
        current = float(pos.current_price)
        pl = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc) * 100
        
        print(f"\n  {symbol}:")
        print(f"    Quantity: {qty:.4f}")
        print(f"    Entry: ${entry:.2f}")
        print(f"    Current: ${current:.2f}")
        print(f"    P&L: ${pl:.2f} ({pl_pct:.2f}%)")
        
        try:
            # Close position using Alpaca's close endpoint
            print(f"    🔄 Closing position...")
            
            response = client.close_position(symbol)
            
            print(f"    ✅ Order submitted: {response.id}")
            print(f"    Status: {response.status}")
            
            closed_count += 1
            total_pl += pl
            
            time.sleep(0.5)  # Avoid rate limits
            
        except Exception as e:
            print(f"    ❌ Error closing {symbol}: {e}")
    
    print(f"\n" + "─"*70)
    print(f"📊 ALPACA SUMMARY:")
    print(f"  Positions Closed: {closed_count}/{len(positions)}")
    print(f"  Total P&L: ${total_pl:.2f}")
    print(f"─"*70)
    
    # Check final account status
    time.sleep(2)
    account = client.get_account()
    print(f"\n💰 ALPACA FINAL STATUS:")
    print(f"  Equity: ${float(account.equity):,.2f}")
    print(f"  Cash: ${float(account.cash):,.2f}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
    
    return closed_count

def close_ib_positions():
    """Close all IB positions"""
    print("\n" + "="*70)
    print("💼 CLOSING IB POSITIONS")
    print("="*70)
    
    ib = IB()
    
    try:
        host = os.getenv('IB_HOST', '127.0.0.1')
        port = int(os.getenv('IB_PORT', '4002'))
        client_id = int(os.getenv('IB_CLIENT_ID', '9998'))
        
        print(f"\n🔌 Connecting to IB at {host}:{port}...")
        ib.connect(host, port, clientId=client_id, timeout=10)
        
        if not ib.isConnected():
            print("❌ Failed to connect to IB")
            return 0
        
        print("✅ Connected to IB")
        
        # Get all positions
        positions = ib.positions()
        
        if not positions:
            print("\n✅ No IB positions to close")
            ib.disconnect()
            return 0
        
        print(f"\n📊 Found {len(positions)} positions to close:")
        
        closed_count = 0
        
        for pos in positions:
            symbol = pos.contract.symbol
            qty = pos.position
            entry = pos.avgCost
            
            print(f"\n  {symbol}:")
            print(f"    Quantity: {qty:.1f}")
            print(f"    Entry: ${entry:.2f}")
            
            try:
                # Create market order to close
                action = "SELL" if qty > 0 else "BUY"
                quantity = abs(qty)
                
                order = MarketOrder(action, quantity)
                
                print(f"    🔄 Placing {action} order for {quantity} shares...")
                
                trade = ib.placeOrder(pos.contract, order)
                
                # Wait for fill
                print(f"    ⏳ Waiting for fill...")
                for i in range(30):  # Wait up to 30 seconds
                    ib.sleep(1)
                    if trade.isDone():
                        break
                
                if trade.isDone():
                    fill_price = trade.orderStatus.avgFillPrice
                    print(f"    ✅ Filled at ${fill_price:.2f}")
                    closed_count += 1
                else:
                    print(f"    ⚠️ Order status: {trade.orderStatus.status}")
                
            except Exception as e:
                print(f"    ❌ Error closing {symbol}: {e}")
        
        print(f"\n" + "─"*70)
        print(f"📊 IB SUMMARY:")
        print(f"  Positions Closed: {closed_count}/{len(positions)}")
        print(f"─"*70)
        
        # Check final account status
        time.sleep(2)
        accounts = ib.managedAccounts()
        if accounts:
            account = accounts[0]
            account_values = ib.accountValues(account)
            
            equity = float(next((v.value for v in account_values if v.tag == 'NetLiquidation'), 0))
            cash = float(next((v.value for v in account_values if v.tag == 'TotalCashValue'), 0))
            buying_power = float(next((v.value for v in account_values if v.tag == 'BuyingPower'), 0))
            
            print(f"\n💰 IB FINAL STATUS:")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Buying Power: ${buying_power:,.2f}")
        
        ib.disconnect()
        return closed_count
        
    except Exception as e:
        print(f"❌ IB Error: {e}")
        if ib.isConnected():
            ib.disconnect()
        return 0

def main():
    print("\n" + "="*70)
    print("  🔄 CLOSE ALL POSITIONS - BOTH BROKERS")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*70)
    
    print("\n⚠️  This will close ALL positions on both Alpaca and IB")
    print("⚠️  Freeing up capital for fresh AI trading")
    
    # Close Alpaca positions
    alpaca_closed = close_alpaca_positions()
    
    # Close IB positions
    ib_closed = close_ib_positions()
    
    # Final summary
    print("\n" + "="*70)
    print("✅ OPERATION COMPLETE")
    print("="*70)
    print(f"\n📊 RESULTS:")
    print(f"  Alpaca Positions Closed: {alpaca_closed}")
    print(f"  IB Positions Closed: {ib_closed}")
    print(f"  Total Positions Closed: {alpaca_closed + ib_closed}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. All capital now available as buying power")
    print(f"  2. AI can enter fresh trades with full flexibility")
    print(f"  3. Both brokers ready for optimal trade execution")
    print(f"  4. Prometheus will analyze markets and find best opportunities")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
