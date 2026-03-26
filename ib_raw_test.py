#!/usr/bin/env python
"""Raw IB API handshake test - bypassing ibapi wrapper"""
import socket
import struct
import sys

print("="*65)
print("🔬 RAW IB API HANDSHAKE TEST")
print("="*65)
print()

HOST = '127.0.0.1'
PORT = 4002
CLIENT_ID = 0

print(f"Connecting to {HOST}:{PORT}...")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((HOST, PORT))
    print("✅ Socket connected!")
    
    # IB API handshake: send "API\0" followed by version
    # The ibapi uses: "API\0" + "v" + min_version + ".." + max_version
    # For version 176 (current)
    
    print("\nSending API handshake...")
    
    # Method 1: Simple handshake
    handshake = b"API\0"
    sock.send(handshake)
    print(f"  Sent: {handshake}")
    
    # Send version range (v100..176)
    version_msg = "v100..176"
    # IB expects length-prefixed messages
    msg_bytes = version_msg.encode('ascii')
    length = len(msg_bytes)
    full_msg = struct.pack('>I', length) + msg_bytes
    sock.send(full_msg)
    print(f"  Sent version: {version_msg}")
    
    print("\nWaiting for response (10s timeout)...")
    sock.settimeout(10)
    
    try:
        response = sock.recv(4096)
        if response:
            print(f"✅ Received {len(response)} bytes!")
            print(f"  Raw: {response[:100]}...")
            
            # Try to decode
            try:
                decoded = response.decode('ascii', errors='replace')
                print(f"  Decoded: {decoded[:100]}...")
            except:
                pass
        else:
            print("❌ Empty response - connection closed by server")
            
    except socket.timeout:
        print("❌ TIMEOUT - No response from IB Gateway")
        print()
        print("This means IB Gateway is accepting the socket but NOT")
        print("responding to the API handshake. Check these settings:")
        print()
        print("  In IB Gateway → Configure → Settings → API → Settings:")
        print("  ┌─────────────────────────────────────────────────┐")
        print("  │ [✓] Enable ActiveX and Socket Clients          │")
        print("  │ [✓] Allow connections from localhost only      │")
        print("  │ [ ] Read-Only API  ← MUST BE UNCHECKED         │")
        print("  │ Socket port: 4002                              │")
        print("  │ Master API client ID: (leave blank)            │")
        print("  │ Trusted IPs: 127.0.0.1 (add if present)        │")
        print("  └─────────────────────────────────────────────────┘")
        print()
        print("  IMPORTANT: After changing settings, RESTART IB Gateway!")
        
except socket.error as e:
    print(f"❌ Socket error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sock.close()
    
print()
print("="*65)

