#!/usr/bin/env python
"""Simplest possible IB test"""
import socket
import time

print("="*60)
print("SIMPLE IB SOCKET TEST")
print("="*60)

# Test raw socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    print("Connecting to 127.0.0.1:4002...")
    result = sock.connect_ex(('127.0.0.1', 4002))
    
    if result == 0:
        print("✅ Socket connected!")
        
        # Try to receive any data
        print("Waiting for data...")
        sock.settimeout(5)
        try:
            data = sock.recv(1024)
            print(f"Received: {data}")
        except socket.timeout:
            print("No data received (timeout)")
        except Exception as e:
            print(f"Recv error: {e}")
    else:
        print(f"❌ Connection failed: error {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sock.close()

print()
print("="*60)
print("IB Gateway API Settings Required:")
print("="*60)
print("""
In IB Gateway, check these settings:
1. Configure → Settings → API → Settings
2. ✅ Enable ActiveX and Socket Clients
3. ✅ Allow connections from localhost only  
4. ❌ Read-Only API (must be UNCHECKED for trading)
5. Socket port: 4002
6. Master API client ID: Can be empty or set specific ID
7. Trusted IPs: Add 127.0.0.1 if required

Also check:
- API → Precautions → Bypass Order Precautions for API Orders
""")

