"""
IB Gateway Version Compatibility Test
Tests different API version strings to find one that works
"""
import socket
import struct
import time

HOST = '127.0.0.1'
PORT = 4002

# Different API version strings to try
VERSION_STRINGS = [
    "v100..176",   # Latest
    "v100..175",
    "v100..170",
    "v100..163",
    "v100..157",
    "v100..151",
    "v100..148",
    "v100..142",   # Older
    "v100..100",   # Very old
]

def test_version(version_str):
    """Test a specific API version string"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        
        # Send API marker
        sock.send(b"API\0")
        
        # Send version with length prefix
        msg_bytes = version_str.encode('ascii')
        length = len(msg_bytes)
        full_msg = struct.pack('>I', length) + msg_bytes
        sock.send(full_msg)
        
        # Wait for response
        sock.settimeout(3)
        try:
            response = sock.recv(4096)
            if response:
                return True, f"Got response: {len(response)} bytes"
            else:
                return False, "Empty response"
        except socket.timeout:
            return False, "Timeout"
        finally:
            sock.close()
    except Exception as e:
        return False, str(e)

def test_without_version():
    """Test connecting without sending version (some old APIs)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        
        # Just send API marker
        sock.send(b"API\0")
        
        # Wait for response
        sock.settimeout(3)
        try:
            response = sock.recv(4096)
            if response:
                return True, f"Got response: {len(response)} bytes"
            else:
                return False, "Empty response"
        except socket.timeout:
            return False, "Timeout"
        finally:
            sock.close()
    except Exception as e:
        return False, str(e)

def test_raw_connect():
    """Test if we get any data just by connecting"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        
        # Don't send anything, just wait
        sock.settimeout(3)
        try:
            response = sock.recv(4096)
            if response:
                return True, f"Got unsolicited data: {response[:50]}"
            else:
                return False, "No data"
        except socket.timeout:
            return False, "No unsolicited data (expected)"
        finally:
            sock.close()
    except Exception as e:
        return False, str(e)

print("=" * 60)
print("IB GATEWAY API VERSION COMPATIBILITY TEST")
print("=" * 60)

print("\n[1] Testing raw connection (no data sent)...")
success, msg = test_raw_connect()
print(f"    {'✅' if success else '⚪'} {msg}")

print("\n[2] Testing API marker only (no version)...")
success, msg = test_without_version()
print(f"    {'✅' if success else '❌'} {msg}")

print("\n[3] Testing different API versions...")
for version in VERSION_STRINGS:
    success, msg = test_version(version)
    status = '✅' if success else '❌'
    print(f"    {status} {version}: {msg}")
    if success:
        print(f"\n    🎉 FOUND WORKING VERSION: {version}")
        break
    time.sleep(0.5)  # Small delay between tests

print("\n" + "=" * 60)
print("If all versions failed, the API is not accepting connections.")
print("Check IB Gateway for any popups that need to be dismissed.")
print("=" * 60)

