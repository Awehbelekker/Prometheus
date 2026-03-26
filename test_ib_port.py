#!/usr/bin/env python
"""Test IB port connectivity"""
import socket

ports_to_test = [
    (7497, "TWS Live API"),
    (7496, "TWS Paper API"),
    (4001, "Gateway Paper"),
    (4002, "Gateway Live"),
]

print("="*60)
print("IB PORT CONNECTIVITY TEST")
print("="*60)

for port, desc in ports_to_test:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"  [OK] Port {port} ({desc}) - CONNECTED")
        else:
            error_msgs = {
                10061: "Connection refused - API not enabled",
                10060: "Connection timed out",
                10049: "Address not available",
            }
            msg = error_msgs.get(result, f"Error code {result}")
            print(f"  [FAIL] Port {port} ({desc}) - {msg}")
    except Exception as e:
        print(f"  [ERROR] Port {port} ({desc}) - {e}")

print()
print("="*60)
print("ACTION REQUIRED:")
print("="*60)
print("""
To enable IB API connections in TWS:
1. In TWS, go to: Edit → Global Configuration → API → Settings
2. Check: "Enable ActiveX and Socket Clients"
3. Check: "Allow connections from localhost only"
4. Set Socket Port to: 7497
5. Click Apply and OK
6. Restart TWS

To enable IB API in IB Gateway:
1. In Gateway, go to: Configure → Settings → API → Settings
2. Check: "Enable ActiveX and Socket Clients"
3. Set Socket Port to: 4001 (paper) or 4002 (live)
4. Click Apply and OK
""")

