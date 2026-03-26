"""
IB Gateway Connection Diagnostic Tool
Comprehensive testing to identify connection issues
"""

import socket
import time
import sys
from ib_insync import IB, util

print("=" * 70)
print("IB GATEWAY CONNECTION DIAGNOSTIC")
print("=" * 70)

# Test 1: Raw Socket Connection
print("\n[TEST 1] Raw Socket Connection to 127.0.0.1:4002")
print("-" * 70)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
start = time.time()
try:
    s.connect(('127.0.0.1', 4002))
    elapsed = time.time() - start
    print(f"✅ Socket connected in {elapsed:.2f}s")
    
    # Try to send IB API handshake
    print("   Attempting IB API handshake...")
    s.send(b'API\0')
    time.sleep(0.5)
    
    try:
        data = s.recv(1024)
        print(f"   Received response: {data[:50]}")
    except socket.timeout:
        print("   ⚠️  No response received (timeout)")
    
    s.close()
    socket_works = True
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Socket connection FAILED after {elapsed:.2f}s")
    print(f"   Error: {type(e).__name__}: {e}")
    socket_works = False
finally:
    try:
        s.close()
    except:
        pass

# Test 2: IB-Insync Connection with Different Client IDs
print("\n[TEST 2] IB-Insync Connection Tests")
print("-" * 70)

test_configs = [
    (0, "Master Client ID"),
    (1, "Standard Client ID"),
    (99, "High Client ID"),
    (888, "Custom Client ID"),
]

successful_client_id = None

for client_id, description in test_configs:
    print(f"\nTesting Client ID {client_id} ({description})...")
    ib = IB()
    try:
        ib.connect('127.0.0.1', 4002, clientId=client_id, timeout=10)
        print(f"✅ CONNECTED with Client ID {client_id}")
        print(f"   Accounts: {ib.managedAccounts()}")
        
        # Get account summary
        try:
            positions = ib.positions()
            print(f"   Positions: {len(positions)}")
            for p in positions[:3]:
                print(f"      • {p.contract.symbol}: {p.position} @ ${p.avgCost:.2f}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch positions: {e}")
        
        ib.disconnect()
        successful_client_id = client_id
        print(f"   Disconnected cleanly")
        break
        
    except Exception as e:
        print(f"❌ FAILED with Client ID {client_id}")
        print(f"   Error: {type(e).__name__}: {e}")
        try:
            ib.disconnect()
        except:
            pass

# Test 3: Check for Trusted IPs Configuration
print("\n[TEST 3] IB Gateway Configuration Check")
print("-" * 70)
print("IB Gateway API Settings should have:")
print("  ✅ Enable ActiveX and Socket Clients: CHECKED")
print("  ✅ Socket port: 4002")
print("  ⬜ Read-Only API: UNCHECKED (for trading)")
print("  ✅ Trusted IPs: Should include 127.0.0.1 or be empty")
print("\nIf 'Trusted IPs' is configured, make sure 127.0.0.1 is in the list!")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

if socket_works:
    print("✅ Raw socket connection: WORKING")
else:
    print("❌ Raw socket connection: FAILED")
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("   1. Restart IB Gateway completely (close and reopen)")
    print("   2. In IB Gateway: Configure → Settings → API → Settings")
    print("   3. Check 'Enable ActiveX and Socket Clients'")
    print("   4. Click Apply, then OK")
    print("   5. Wait 10 seconds for settings to take effect")

if successful_client_id is not None:
    print(f"✅ IB-Insync connection: WORKING (Client ID {successful_client_id})")
    print(f"\n🎯 RECOMMENDED CLIENT ID FOR PROMETHEUS: {successful_client_id}")
else:
    print("❌ IB-Insync connection: FAILED")
    print("\n🔧 POSSIBLE CAUSES:")
    print("   1. API not enabled in IB Gateway settings")
    print("   2. Trusted IPs blocking 127.0.0.1")
    print("   3. Too many active connections (max 32)")
    print("   4. IB Gateway needs restart")
    print("   5. Windows Firewall blocking localhost connections")

print("=" * 70)

