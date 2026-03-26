#!/usr/bin/env python
"""Full IB Connection Test with Account and Positions"""
import threading
import time
import sys

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
except ImportError:
    print("ERROR: ibapi not installed. Run: pip install ibapi")
    sys.exit(1)

class IBTestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.account_data = {}
        self.positions = []
        self.done_account = False
        self.done_positions = False
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        # Skip info messages
        if errorCode in [2104, 2106, 2158, 2119, 2108]:
            return
        if errorCode == 502:
            print(f"  ⚠️ Disconnected")
        elif errorCode < 1000:
            print(f"  ❌ Error {errorCode}: {errorString}")
        
    def nextValidId(self, orderId):
        self.connected = True
        print(f"  ✅ Connected! Next order ID: {orderId}")
        
    def managedAccounts(self, accountsList):
        print(f"  📋 Managed accounts: {accountsList}")
        
    def accountSummary(self, reqId, account, tag, value, currency):
        self.account_data[tag] = {'value': value, 'currency': currency}
        
    def accountSummaryEnd(self, reqId):
        self.done_account = True
        
    def position(self, account, contract, pos, avgCost):
        if pos != 0:
            self.positions.append({
                'symbol': contract.symbol,
                'secType': contract.secType,
                'qty': pos,
                'avgCost': avgCost
            })
            
    def positionEnd(self):
        self.done_positions = True

def main():
    print("="*65)
    print("🏦 INTERACTIVE BROKERS FULL CONNECTION TEST")
    print("="*65)
    
    app = IBTestApp()
    
    print("\n📡 Connecting to IB Gateway (port 4002)...")
    app.connect("127.0.0.1", 4002, clientId=101)
    
    # Start message thread
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    
    # Wait for connection
    for i in range(10):
        if app.connected:
            break
        time.sleep(1)
        print(f"  Waiting... {i+1}s")
    
    if not app.connected:
        print("\n❌ Failed to connect after 10 seconds")
        print("\nCheck IB Gateway settings:")
        print("  1. Configure → Settings → API → Settings")
        print("  2. Enable ActiveX and Socket Clients: ✓")
        print("  3. Allow connections from localhost: ✓")
        print("  4. Read-Only API: ✗ (uncheck for trading)")
        app.disconnect()
        return
    
    # Request account summary
    print("\n💰 Requesting account data...")
    app.reqAccountSummary(1, "All", "NetLiquidation,TotalCashValue,BuyingPower,AvailableFunds")
    
    for i in range(5):
        if app.done_account:
            break
        time.sleep(1)
    
    # Request positions
    print("📈 Requesting positions...")
    app.reqPositions()
    
    for i in range(5):
        if app.done_positions:
            break
        time.sleep(1)
    
    # Print results
    print("\n" + "="*65)
    print("📊 IB ACCOUNT SUMMARY")
    print("="*65)
    
    for tag, data in app.account_data.items():
        try:
            val = float(data['value'])
            print(f"  {tag}: ${val:,.2f} {data['currency']}")
        except:
            print(f"  {tag}: {data['value']} {data['currency']}")
    
    print(f"\n📈 POSITIONS ({len(app.positions)} total):")
    if app.positions:
        for p in app.positions:
            print(f"  • {p['symbol']} ({p['secType']}): {p['qty']} @ ${p['avgCost']:.2f}")
    else:
        print("  No positions")
    
    print("\n" + "="*65)
    print("✅ IB CONNECTION TEST COMPLETE")
    print("="*65)
    
    app.disconnect()

if __name__ == "__main__":
    main()

