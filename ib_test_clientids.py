#!/usr/bin/env python
"""Test IB with various client IDs - Master API client ID is 0"""
import socket
import threading
import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class QuickApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.error_code = None
        
    def error(self, reqId, errorCode, errorString, advJson=""):
        if errorCode not in [2104, 2106, 2158, 2119, 2108]:
            print(f"    Error {errorCode}: {errorString[:50]}")
            self.error_code = errorCode
            
    def nextValidId(self, orderId):
        self.connected = True
        print(f"    ✅ CONNECTED! Order ID: {orderId}")
        
    def managedAccounts(self, accounts):
        print(f"    📋 Accounts: {accounts}")

print("="*60)
print("🔬 IB CLIENT ID TEST")
print("="*60)

# First check if port is open
sock = socket.socket()
sock.settimeout(3)
result = sock.connect_ex(('127.0.0.1', 4002))
sock.close()
print(f"\nPort 4002: {'OPEN' if result == 0 else 'CLOSED'}")

if result != 0:
    print("❌ Gateway not running!")
    exit(1)

# Try different client IDs (Master is 0, so avoid 0)
client_ids = [1, 2, 5, 10, 100, 123, 999]

for cid in client_ids:
    print(f"\n🔄 Testing Client ID {cid}...")
    
    app = QuickApp()
    try:
        app.connect("127.0.0.1", 4002, cid)
        
        if not app.isConnected():
            print(f"    ❌ Socket connect failed")
            continue
            
        print(f"    Socket connected, waiting for API response...")
        
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        
        # Wait up to 8 seconds
        for i in range(8):
            if app.connected:
                # Success! Get account info
                print(f"\n🎉 SUCCESS with Client ID {cid}!")
                app.reqAccountSummary(1, "All", "NetLiquidation,TotalCashValue")
                time.sleep(2)
                app.disconnect()
                print("\n✅ IB Gateway connection working!")
                exit(0)
            if app.error_code:
                break
            time.sleep(1)
        
        if not app.connected:
            print(f"    ⏰ Timeout")
            
        app.disconnect()
        time.sleep(0.3)
        
    except Exception as e:
        print(f"    ❌ Exception: {e}")

print("\n" + "="*60)
print("❌ All client IDs failed")
print("="*60)
print("""
Your API settings look correct in the screenshots.
The issue might be:

1. Settings not saved - Click OK/Apply and close the dialog
2. Need to restart Gateway after settings change
3. Windows Firewall blocking the connection

Try:
1. Close the Configuration dialog (click OK)
2. Close IB Gateway completely (File → Exit)
3. Restart IB Gateway
4. Run this test again
""")

