"""Sell IB CRM Position Now"""
import asyncio
from ib_insync import IB, Stock, MarketOrder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sell_crm_position():
    """Sell CRM position on IB"""
    print("=" * 60)
    print("  SELLING CRM POSITION ON INTERACTIVE BROKERS")
    print("=" * 60)
    
    ib = IB()
    
    try:
        # Connect to IB Gateway
        print("\n🔌 Connecting to IB Gateway...")
        await ib.connectAsync('127.0.0.1', 4002, clientId=99)
        print("✅ Connected to IB")
        
        # Get current positions
        positions = ib.positions()
        print(f"\n📊 Current Positions: {len(positions)}")
        
        crm_position = None
        for pos in positions:
            symbol = pos.contract.symbol
            qty = pos.position
            avg_cost = pos.avgCost
            print(f"   {symbol}: {qty} shares @ ${avg_cost:.2f}")
            
            if symbol == 'CRM':
                crm_position = pos
        
        if not crm_position:
            print("\n❌ No CRM position found!")
            return False
        
        # Get current price
        crm_contract = Stock('CRM', 'SMART', 'USD')
        ib.qualifyContracts(crm_contract)
        
        ticker = ib.reqMktData(crm_contract)
        await asyncio.sleep(2)  # Wait for market data
        
        current_price = ticker.last if ticker.last else ticker.close
        print(f"\n💰 CRM Current Price: ${current_price:.2f}")
        
        qty = abs(crm_position.position)
        entry = crm_position.avgCost
        pnl = (current_price - entry) * qty
        pnl_pct = ((current_price - entry) / entry) * 100
        
        print(f"   Entry: ${entry:.2f}")
        print(f"   Quantity: {qty}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
        
        # Create sell order
        print(f"\n🚀 Placing SELL order for {qty} CRM shares...")
        
        sell_order = MarketOrder('SELL', qty)
        trade = ib.placeOrder(crm_contract, sell_order)
        
        # Wait for fill
        print("⏳ Waiting for fill...")
        for i in range(30):  # Wait up to 30 seconds
            await asyncio.sleep(1)
            if trade.orderStatus.status == 'Filled':
                break
            print(f"   Status: {trade.orderStatus.status}")
        
        if trade.orderStatus.status == 'Filled':
            fill_price = trade.orderStatus.avgFillPrice
            actual_pnl = (fill_price - entry) * qty
            print(f"\n✅ ORDER FILLED!")
            print(f"   Fill Price: ${fill_price:.2f}")
            print(f"   Realized P&L: ${actual_pnl:+.2f}")
            print(f"\n🎉 CRM POSITION CLOSED SUCCESSFULLY!")
            return True
        else:
            print(f"\n⚠️ Order status: {trade.orderStatus.status}")
            print("   Order may still be pending...")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        ib.disconnect()
        print("\n🔌 Disconnected from IB")

if __name__ == "__main__":
    print("\n⚠️ This will SELL your CRM position on IB!")
    print("   Press Ctrl+C within 5 seconds to cancel...")
    
    import time
    try:
        for i in range(5, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n❌ Cancelled!")
        exit(0)
    
    asyncio.run(sell_crm_position())
