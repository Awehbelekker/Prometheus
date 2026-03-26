#!/usr/bin/env python3
"""Check Backend Server Status"""

import sys
import requests
import socket
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("BACKEND SERVER STATUS CHECK")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check if port is open
def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

# Check backend on port 8000
port = 8000
host = '127.0.0.1'

print(f"Checking Backend Server on {host}:{port}...\n")

# Check if port is listening
port_open = check_port(host, port)
print(f"Port {port} Status: {'OPEN' if port_open else 'CLOSED'}")

if port_open:
    # Try to connect to health endpoint
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ BACKEND SERVER: UP AND RUNNING")
            print(f"   Status Code: {response.status_code}")
            if isinstance(data, dict):
                print(f"   Status: {data.get('status', 'Unknown')}")
                print(f"   Uptime: {data.get('uptime_seconds', 0):.2f} seconds")
                print(f"   Version: {data.get('version', 'Unknown')}")
        else:
            print(f"\n⚠️ BACKEND SERVER: RESPONDING BUT ERROR")
            print(f"   Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ BACKEND SERVER: PORT OPEN BUT NOT RESPONDING")
        print("   Port is open but /health endpoint not accessible")
    except Exception as e:
        print(f"\n⚠️ BACKEND SERVER: ERROR")
        print(f"   Error: {e}")
else:
    print(f"\n❌ BACKEND SERVER: DOWN")
    print("   Port 8000 is not open")
    print("\n💡 To start the backend:")
    print("   python -m uvicorn unified_production_server:app --host 127.0.0.1 --port 8000")
    print("   OR")
    print("   python start_backend_server.py")

print("\n" + "="*80)



