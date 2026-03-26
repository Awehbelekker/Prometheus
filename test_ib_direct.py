#!/usr/bin/env python
"""Direct IB API Test - Minimal"""
import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class TestWrapper(EWrapper):
    def __init__(self):
        self.connected = False
        self.account_data = {}
        self.positions = []
        self.next_order_id = None
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode in [2104, 2106, 2158, 2119]:  # Info messages
            print(f"  [INFO] {errorCode}: {errorString}")
        elif errorCode == 502:
            print(f"  [WARN] Not connected to IB")
        else:
            print(f"  [ERROR] {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        print(f"  ✅ Connected! Next Order ID: {orderId}")
        self.next_order_id = orderId
        self.connected = True
        
    def managedAccounts(self, accountsList):
        print(f"  📋 Accounts: {accountsList}")
        
    def accountSummary(self, reqId, account, tag, value, currency):
        self.account_data[tag] = value
        if tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower']:
            print(f"  💰 {tag}: ${float(value):,.2f} {currency}")
            
    def accountSummaryEnd(self, reqId):
        print("  ✅ Account summary received")
        
    def position(self, account, contract, pos, avgCost):
        if pos != 0:
            self.positions.append({
                'symbol': contract.symbol,
                'qty': pos,
                'avg_cost': avgCost
            })
            print(f"  📈 Position: {contract.symbol} | Qty: {pos} | Avg: ${avgCost:.2f}")
            
    def positionEnd(self):
        print(f"  ✅ Positions received: {len(self.positions)} total")

class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

def main():
    print("="*60)
    print("🏦 DIRECT IB API CONNECTION TEST")
    print("="*60)
    
    wrapper = TestWrapper()
    client = TestClient(wrapper)
    
    print("\n📡 Connecting to IB Gateway on port 4002...")
    client.connect("127.0.0.1", 4002, clientId=100)
    
    # Start message thread
    api_thread = threading.Thread(target=client.run, daemon=True)
    api_thread.start()
    
    # Wait for connection
    print("  Waiting for connection...")
    for i in range(15):
        time.sleep(1)
        if wrapper.connected:
            break
        print(f"  ... {i+1}s")
    
    if not wrapper.connected:
        print("\n❌ Connection failed after 15 seconds")
        client.disconnect()
        return
    
    print("\n💰 Requesting Account Summary...")
    client.reqAccountSummary(1, "All", "NetLiquidation,TotalCashValue,BuyingPower,AvailableFunds")
    time.sleep(3)
    
    print("\n📈 Requesting Positions...")
    client.reqPositions()
    time.sleep(3)
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"  Connected: {'✅ YES' if wrapper.connected else '❌ NO'}")
    print(f"  Account Data: {len(wrapper.account_data)} fields")
    print(f"  Positions: {len(wrapper.positions)}")
    
    # Disconnect
    client.disconnect()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()

