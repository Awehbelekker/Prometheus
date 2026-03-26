#!/usr/bin/env python3
"""
Wait for IB API to be enabled, then automatically start trading
"""

import sys
import time
import threading

print("=" * 80)
print("  🔍 WAITING FOR IB API TO BE ENABLED")
print("=" * 80)
print()
print("This script will:")
print("  1. Check every 10 seconds if IB API is enabled")
print("  2. Automatically start trading when API is ready")
print("  3. You can leave this running while you enable the API")
print()
print("=" * 80)
print()

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
except ImportError:
    print("[ERROR] ibapi not installed")
    sys.exit(1)

class QuickTest(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        
    def error(self, reqId, errorCode, errorString):
        pass  # Ignore errors during testing
    
    def nextValidId(self, orderId):
        self.connected = True

def test_connection():
    """Quick connection test"""
    try:
        app = QuickTest()
        app.connect("127.0.0.1", 7496, 2)
        
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        
        # Wait 3 seconds
        for i in range(30):
            if app.connected:
                app.disconnect()
                return True
            time.sleep(0.1)
        
        app.disconnect()
        return False
    except:
        return False

def start_trading():
    """Start the trading bot"""
    print("\n" + "=" * 80)
    print("  [CHECK] API IS ENABLED! STARTING TRADING BOT...")
    print("=" * 80)
    print()
    
    # Import and run the trading bot
    import subprocess
    subprocess.run([sys.executable, "auto_start_ib_trading.py"])

# Main loop
attempt = 0
while True:
    attempt += 1
    print(f"[{time.strftime('%H:%M:%S')}] Attempt {attempt}: Testing IB API connection...", end=" ")
    
    if test_connection():
        print("[CHECK] CONNECTED!")
        start_trading()
        break
    else:
        print("[ERROR] Not ready yet")
        print("  💡 Enable API in IB Gateway: Configure → API → Settings")
        print("  💡 Check 'Enable ActiveX and Socket Clients'")
        print("  💡 Uncheck 'Read-Only API'")
        print("  💡 Set Socket Port to 7496")
        print("  💡 Click OK, Apply, and Restart IB Gateway")
        print()
        print(f"  ⏳ Waiting 10 seconds before next attempt...")
        print()
        time.sleep(10)

