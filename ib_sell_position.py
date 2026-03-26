"""
IB Gateway - Sell Position Script
Sells a specified position on Interactive Brokers
"""
from ib_insync import IB, Stock, MarketOrder
import sys

def sell_position(symbol: str, quantity: int = 1):
    """Sell a position on IB"""
    ib = IB()
    
    try:
        print(f"\n{'='*60}")
        print(f"🔴 SELLING {quantity} share(s) of {symbol}")
        print(f"{'='*60}\n")
        
        # Connect to IB Gateway
        print("1. Connecting to IB Gateway...")
        ib.connect('127.0.0.1', 4002, clientId=2)
        print("   ✅ Connected!")
        
        # Get current positions
        print("\n2. Checking current positions...")
        positions = ib.positions()
        
        position_found = None
        for pos in positions:
            if pos.contract.symbol == symbol:
                position_found = pos
                print(f"   Found: {pos.contract.symbol} - {pos.position} shares @ ${pos.avgCost:.2f}")
                break
        
        if not position_found:
            print(f"   ❌ No position found for {symbol}")
            return False
        
        if position_found.position < quantity:
            print(f"   ❌ Not enough shares. You have {position_found.position}, trying to sell {quantity}")
            return False
        
        # Create the contract
        print(f"\n3. Creating sell order for {symbol}...")
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        
        # Create market sell order
        order = MarketOrder('SELL', quantity)
        
        # Place the order
        print(f"\n4. Placing SELL order...")
        trade = ib.placeOrder(contract, order)
        
        # Wait for order to fill
        print("   Waiting for order to fill...")
        
        # Give it some time to fill
        for i in range(30):  # Wait up to 30 seconds
            ib.sleep(1)
            if trade.orderStatus.status in ['Filled', 'Cancelled', 'ApiCancelled']:
                break
            print(f"   Status: {trade.orderStatus.status}...")
        
        # Check final status
        print(f"\n{'='*60}")
        if trade.orderStatus.status == 'Filled':
            avg_price = trade.orderStatus.avgFillPrice
            print(f"✅ ORDER FILLED!")
            print(f"   Symbol: {symbol}")
            print(f"   Quantity: {quantity}")
            print(f"   Fill Price: ${avg_price:.2f}")
            print(f"   Total: ${avg_price * quantity:.2f}")
        else:
            print(f"⚠️ Order Status: {trade.orderStatus.status}")
            print(f"   Order ID: {trade.order.orderId}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        ib.disconnect()
        print("Disconnected from IB Gateway.")


if __name__ == "__main__":
    # Default: sell 1 share of NOK
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NOK"
    quantity = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    print("\n" + "="*60)
    print("IB GATEWAY - SELL POSITION")
    print("="*60)
    print(f"\nSymbol to sell: {symbol}")
    print(f"Quantity: {quantity}")
    print("\n⚠️  THIS IS A LIVE TRADE ON YOUR IB ACCOUNT!")
    
    confirm = input("\nProceed with SELL order? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        sell_position(symbol, quantity)
    else:
        print("\nOrder cancelled.")

