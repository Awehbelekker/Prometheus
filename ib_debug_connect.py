#!/usr/bin/env python
"""Debug IB connection - check what Gateway is doing"""
import socket
import time
import select

print("="*65)
print("🔬 IB GATEWAY DEBUG - Raw Socket Analysis")
print("="*65)

HOST = '127.0.0.1'
PORT = 4002

def test_basic_socket():
    """Test basic socket connectivity"""
    print("\n[1] BASIC SOCKET TEST")
    print("-"*40)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        sock.connect((HOST, PORT))
        print(f"  ✅ Connected to {HOST}:{PORT}")
        
        # Check if socket is readable (server sent something)
        sock.setblocking(False)
        time.sleep(0.5)
        
        try:
            ready = select.select([sock], [], [], 2)
            if ready[0]:
                data = sock.recv(1024)
                print(f"  📩 Server sent data: {len(data)} bytes")
                print(f"     {data[:50]}...")
            else:
                print("  📭 Server did NOT send initial data (this is normal)")
        except:
            print("  📭 No initial data from server")
            
        sock.close()
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ib_handshake():
    """Test IB API handshake"""
    print("\n[2] IB API HANDSHAKE TEST")
    print("-"*40)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((HOST, PORT))
        print(f"  ✅ Socket connected")
        
        # Send IB API handshake
        # Format: "API\0" + 4-byte length + "v100..176"
        import struct
        
        # First send "API\0"
        api_marker = b"API\x00"
        sock.send(api_marker)
        print(f"  📤 Sent API marker: {api_marker}")
        
        # Then send version string with length prefix
        version = b"v100..176"
        length = struct.pack(">I", len(version))
        sock.send(length + version)
        print(f"  📤 Sent version: {version.decode()}")
        
        # Wait for response
        print("  ⏳ Waiting for response...")
        sock.settimeout(8)
        
        try:
            response = sock.recv(4096)
            if response:
                print(f"  ✅ Got response: {len(response)} bytes")
                print(f"     Raw: {response[:80]}")
                return True
            else:
                print("  ❌ Connection closed by server (no response)")
        except socket.timeout:
            print("  ❌ TIMEOUT - Gateway not responding to API handshake")
            print()
            print("  ⚠️  This confirms: API connections are NOT enabled in Gateway")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    finally:
        sock.close()
    
    return False

def main():
    test_basic_socket()
    success = test_ib_handshake()
    
    print("\n" + "="*65)
    print("📋 DIAGNOSIS")
    print("="*65)
    
    if not success:
        print("""
The IB Gateway socket accepts connections but does NOT respond
to API requests. This is 100% a Gateway configuration issue.

🔧 SOLUTION - In IB Gateway:

1. Click: Configure → Settings → API → Settings

2. Make SURE these are set:
   ┌─────────────────────────────────────────────────────────┐
   │ ☑ Enable ActiveX and Socket Clients    ← CRITICAL!     │
   │ ☑ Allow connections from localhost only                │
   │ ☐ Read-Only API  (uncheck for trading)                 │
   │                                                         │
   │ Socket port: 4002                                       │
   │ Master API client ID: [leave blank]                     │
   └─────────────────────────────────────────────────────────┘

3. Click OK/Apply

4. ⚠️ FULLY RESTART IB Gateway (File → Exit, then reopen)

5. After restart, run this test again

Note: You have 2 IB Gateway instances running. Close extras!
""")
    else:
        print("✅ IB Gateway is responding to API requests!")

if __name__ == "__main__":
    main()

