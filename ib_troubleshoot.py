#!/usr/bin/env python
"""IB Troubleshooting - Try multiple approaches"""
import socket
import threading
import time
import sys

print("="*65)
print("🔧 IB GATEWAY TROUBLESHOOTING")
print("="*65)

# Step 1: Raw socket test
print("\n[1] RAW SOCKET TEST")
print("-"*40)

for port in [4002, 4001, 7497, 7496]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('127.0.0.1', port))
    status = "✅ OPEN" if result == 0 else f"❌ CLOSED (err {result})"
    print(f"  Port {port}: {status}")
    sock.close()

# Step 2: Check if ibapi is installed correctly
print("\n[2] IBAPI MODULE CHECK")
print("-"*40)
try:
    import ibapi
    print(f"  ✅ ibapi version: {ibapi.__version__ if hasattr(ibapi, '__version__') else 'installed'}")
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    print(f"  ✅ EClient and EWrapper imported")
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    sys.exit(1)

# Step 3: Try connection with different client IDs
print("\n[3] CONNECTION TEST - Multiple Client IDs")
print("-"*40)

class QuickTest(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.error_msg = None
        
    def error(self, reqId, errorCode, errorString, advancedOrderReject=""):
        if errorCode == 502:
            self.error_msg = "Disconnected"
        elif errorCode == 326:
            self.error_msg = f"Client ID already in use"
        elif errorCode == 501:
            self.error_msg = "Already connected"
        elif errorCode == 504:
            self.error_msg = "Not connected"
        elif errorCode < 2000:  # Real errors
            self.error_msg = f"Error {errorCode}: {errorString}"
            print(f"    Error {errorCode}: {errorString}")
            
    def nextValidId(self, orderId):
        self.connected = True
        print(f"    ✅ CONNECTED! Order ID: {orderId}")
        
    def connectAck(self):
        print(f"    📡 Connection acknowledged")

# Try different client IDs and ports
test_configs = [
    (4002, 0, "Gateway Live, Client 0"),
    (4002, 1, "Gateway Live, Client 1"),
    (4002, 999, "Gateway Live, Client 999"),
    (7497, 0, "TWS, Client 0"),
]

for port, client_id, desc in test_configs:
    # Check if port is open first
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    if sock.connect_ex(('127.0.0.1', port)) != 0:
        sock.close()
        continue
    sock.close()
    
    print(f"\n  Testing: {desc}")
    app = QuickTest()
    
    try:
        app.connect("127.0.0.1", port, client_id)
        
        # Start API thread
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        
        # Wait up to 5 seconds
        for i in range(5):
            if app.connected:
                break
            if app.error_msg:
                print(f"    ❌ {app.error_msg}")
                break
            time.sleep(1)
        
        if app.connected:
            print(f"    🎉 SUCCESS with client ID {client_id}!")
            app.disconnect()
            time.sleep(1)
            break
        elif not app.error_msg:
            print(f"    ⏰ Timeout - no response")
            
        app.disconnect()
        time.sleep(0.5)
        
    except Exception as e:
        print(f"    ❌ Exception: {e}")

print("\n" + "="*65)
print("📋 TROUBLESHOOTING TIPS")
print("="*65)
print("""
If connection fails, check IB Gateway:

1. API Settings (Configure → Settings → API → Settings):
   □ Enable ActiveX and Socket Clients = CHECKED
   □ Allow connections from localhost only = CHECKED  
   □ Read-Only API = UNCHECKED (for trading)
   □ Socket port = 4002 (or your port)
   □ Master API client ID = BLANK (or specific number)

2. API Precautions (Configure → Settings → API → Precautions):
   □ Bypass Order Precautions for API Orders = CHECKED

3. After changes: RESTART IB Gateway

4. Check for existing connections using same client ID
""")

