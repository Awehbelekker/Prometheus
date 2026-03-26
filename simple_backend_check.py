#!/usr/bin/env python3
"""Simple Backend Check - writes to file"""

import requests
import socket
from datetime import datetime

output = []
output.append("="*80)
output.append("BACKEND SERVER STATUS")
output.append("="*80)
output.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check port
port = 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
result = sock.connect_ex(('127.0.0.1', port))
sock.close()

if result == 0:
    output.append(f"✅ Port {port}: OPEN")
    output.append("✅ Backend: UP")
    
    # Check health endpoint
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=3)
        if response.status_code == 200:
            output.append(f"✅ Health Endpoint: OK (Status: {response.status_code})")
            try:
                data = response.json()
                output.append(f"   Status: {data.get('status', 'Unknown')}")
                if 'uptime_seconds' in data:
                    output.append(f"   Uptime: {data['uptime_seconds']:.2f} seconds")
            except:
                output.append(f"   Response: {response.text[:100]}")
        else:
            output.append(f"⚠️ Health Endpoint: ERROR (Status: {response.status_code})")
    except Exception as e:
        output.append(f"⚠️ Health Endpoint: NOT RESPONDING - {e}")
else:
    output.append(f"❌ Port {port}: CLOSED")
    output.append("❌ Backend: DOWN")
    output.append("\n💡 To start backend:")
    output.append("   python -m uvicorn unified_production_server:app --host 127.0.0.1 --port 8000")

output.append("\n" + "="*80)

# Write to file and print
result_text = "\n".join(output)
with open('backend_status_result.txt', 'w', encoding='utf-8') as f:
    f.write(result_text)
print(result_text)



