#!/usr/bin/env python
"""IB Connection Test v2 - Using ibapi directly with verbose logging"""
import sys
import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import TickerId

class VerboseWrapper(EWrapper):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.next_id = None
        
    def connectAck(self):
        print("  📡 connectAck received!")
        
    def error(self, reqId: TickerId, errorCode: int, errorString: str, advancedOrderRejectJson=""):
        # Categorize errors
        if errorCode in [2104, 2106, 2158, 2119, 2108]:  # Info
            print(f"  ℹ️  Info {errorCode}: {errorString}")
        elif errorCode == 502:
            print(f"  ⚠️  502: Couldn't connect - check Gateway is running")
        elif errorCode == 504:
            print(f"  ⚠️  504: Not connected")
        elif errorCode == 326:
            print(f"  ⚠️  326: Client ID {reqId} already in use")
        elif errorCode == 321:
            print(f"  ⚠️  321: Error validating request")
        else:
            print(f"  ❌ Error {errorCode}: {errorString}")
    
    def nextValidId(self, orderId: int):
        print(f"  ✅ nextValidId: {orderId} - CONNECTED!")
        self.connected = True
        self.next_id = orderId
        
    def managedAccounts(self, accountsList: str):
        print(f"  📋 Accounts: {accountsList}")
        
    def currentTime(self, time: int):
        from datetime import datetime
        dt = datetime.fromtimestamp(time)
        print(f"  🕐 Server time: {dt}")

class VerboseClient(EClient):
    def __init__(self, wrapper):
        super().__init__(wrapper)

def test_connection(port, client_id):
    print(f"\n{'='*60}")
    print(f"Testing Port {port}, Client ID {client_id}")
    print('='*60)
    
    wrapper = VerboseWrapper()
    client = VerboseClient(wrapper)
    
    print(f"  Connecting to 127.0.0.1:{port}...")
    
    # Connect
    client.connect("127.0.0.1", port, client_id)
    
    if not client.isConnected():
        print("  ❌ Initial connection failed")
        return False
    
    print("  ✅ Socket connected, starting message thread...")
    
    # Start message processing
    thread = threading.Thread(target=client.run, daemon=True)
    thread.start()
    
    # Request server time to test communication
    print("  📤 Requesting server time...")
    client.reqCurrentTime()
    
    # Wait for response
    for i in range(10):
        if wrapper.connected:
            print(f"\n  🎉 SUCCESS! Connected to IB Gateway!")
            
            # Get more info
            print("\n  Requesting account info...")
            client.reqAccountSummary(1, "All", "NetLiquidation,TotalCashValue,BuyingPower")
            time.sleep(2)
            
            client.disconnect()
            return True
        time.sleep(1)
        print(f"  ⏳ Waiting... {i+1}s")
    
    print("  ❌ Timeout - no nextValidId received")
    client.disconnect()
    return False

def main():
    print("="*65)
    print("🏦 IB API CONNECTION TEST v2")
    print("="*65)
    
    # Test configurations
    configs = [
        (4002, 0),
        (4002, 1),
        (4002, 100),
    ]
    
    for port, cid in configs:
        if test_connection(port, cid):
            print("\n✅ Connection successful!")
            return
        time.sleep(1)
    
    print("\n" + "="*65)
    print("❌ ALL ATTEMPTS FAILED")
    print("="*65)
    print("""
The API setting "Enable ActiveX and Socket Clients" appears
to still be DISABLED in IB Gateway.

Please verify in IB Gateway:
  Configure → Settings → API → Settings
  
  [✓] Enable ActiveX and Socket Clients  ← Must be CHECKED!
  
Then RESTART IB Gateway completely.
""")

if __name__ == "__main__":
    main()

