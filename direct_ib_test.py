#!/usr/bin/env python3
"""
Direct IB Gateway Test - No PROMETHEUS imports
Test your $250 live account connection
"""

import time
import threading
from datetime import datetime

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    print("[CHECK] IB API available")
except ImportError:
    print("[ERROR] IB API not available. Install with: pip install ibapi")
    exit(1)

class LiveTestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)
        self.connected = False
        self.account_data = {}
        self.next_order_id = None
        
    def connectAck(self):
        print("   [CHECK] Connection acknowledged")
        self.connected = True
        
    def nextValidId(self, orderId: int):
        self.next_order_id = orderId
        print(f"   📋 Next Order ID: {orderId}")
        
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key in ['NetLiquidation', 'AvailableFunds', 'BuyingPower']:
            try:
                value = float(val) if val else 0.0
                self.account_data[key] = value
                print(f"   💰 {key}: ${value:,.2f}")
            except:
                pass
            
    def accountDownloadEnd(self, accountName: str):
        print(f"   [CHECK] Account download complete: {accountName}")
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        if errorCode in [2104, 2106, 2158, 2119]:  # Info messages
            print(f"   [INFO]️  {errorCode}: {errorString}")
        else:
            print(f"   [WARNING]️  Error {errorCode}: {errorString}")

def test_connection():
    print("🚨 DIRECT IB GATEWAY TEST")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💰 Account: U21922116")
    print("🚪 Port: 7496 (Live)")
    print()
    
    wrapper = LiveTestWrapper()
    client = EClient(wrapper)
    
    print("1️⃣ Connecting...")
    
    try:
        client.connect("127.0.0.1", 7496, 25)
        
        api_thread = threading.Thread(target=client.run, daemon=True)
        api_thread.start()
        
        # Wait for connection
        timeout = 10
        start_time = time.time()
        
        while not client.isConnected() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if client.isConnected():
            print("   🎉 Connected to IB Gateway!")
            
            # Wait for wrapper ready
            start_time = time.time()
            while not wrapper.connected and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            print("\n2️⃣ Getting Account Data...")
            client.reqAccountUpdates(True, "U21922116")
            
            # Wait for account data
            time.sleep(8)
            
            print("\n3️⃣ Results:")
            if wrapper.account_data:
                net_liq = wrapper.account_data.get('NetLiquidation', 0)
                available = wrapper.account_data.get('AvailableFunds', 0)
                
                print(f"   💰 Net Liquidation: ${net_liq:,.2f}")
                print(f"   💵 Available Funds: ${available:,.2f}")
                
                if net_liq >= 250:
                    print("   🎉 SUCCESS: $250+ Account Found!")
                    result = True
                elif net_liq > 0:
                    print(f"   [WARNING]️  Found ${net_liq:,.2f} (less than $250)")
                    result = True
                else:
                    print("   [ERROR] No balance found")
                    result = False
            else:
                print("   [ERROR] No account data received")
                result = False
            
            # Cleanup
            client.reqAccountUpdates(False, "DUN683505")
            client.disconnect()
            
            return result
            
        else:
            print("   [ERROR] Connection failed")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        if client.isConnected():
            client.disconnect()
        return False

if __name__ == "__main__":
    success = test_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: Live account accessible!")
        print("💡 Ready for PROMETHEUS integration")
    else:
        print("[ERROR] FAILED: Check IB Gateway settings")
        print("💡 Ensure:")
        print("   - IB Gateway running")
        print("   - Logged into DUN683505")
        print("   - API enabled")
        print("   - Port 7496 configured")
