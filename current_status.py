#!/usr/bin/env python3
"""Current System Status"""

import sys
import os
import psutil
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("PROMETHEUS SYSTEM STATUS")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check Python processes
print("PYTHON PROCESSES:")
python_procs = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.info['name'].lower():
            cmdline = ' '.join(proc.info['cmdline'][:3]) if proc.info['cmdline'] else 'N/A'
            python_procs.append((proc.info['pid'], cmdline))
    except:
        pass

if python_procs:
    print(f"  Found {len(python_procs)} Python process(es):")
    for pid, cmd in python_procs[:10]:
        print(f"    PID {pid}: {cmd[:80]}")
else:
    print("  No Python processes found")

# Check servers
print("\nSERVERS:")
servers = {
    "Main Server": ("http://localhost:8000/health", 8000),
    "GPT-OSS 20B": ("http://localhost:5000/health", 5000),
    "GPT-OSS 120B": ("http://localhost:5001/health", 5001),
    "Revolutionary": ("http://localhost:8002/health", 8002)
}

for name, (url, port) in servers.items():
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"  {name} (Port {port}): UP")
        else:
            print(f"  {name} (Port {port}): DOWN (Status: {response.status_code})")
    except:
        print(f"  {name} (Port {port}): DOWN")

# Check brokers
print("\nBROKERS:")
alpaca_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
print(f"  Alpaca: {'CONFIGURED' if alpaca_key else 'NOT CONFIGURED'}")
print(f"  Interactive Brokers: DOWN (as noted)")

# Check ports in use
print("\nPORTS IN USE:")
for conn in psutil.net_connections(kind='inet'):
    try:
        if conn.status == 'LISTEN' and conn.laddr.port in [8000, 5000, 5001, 8002]:
            print(f"  Port {conn.laddr.port}: IN USE (PID: {conn.pid})")
    except:
        pass

# Write to file as well
with open('status_report.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("PROMETHEUS SYSTEM STATUS\n")
    f.write("="*80 + "\n")
    f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("PYTHON PROCESSES:\n")
    if python_procs:
        f.write(f"  Found {len(python_procs)} Python process(es):\n")
        for pid, cmd in python_procs[:10]:
            f.write(f"    PID {pid}: {cmd[:80]}\n")
    else:
        f.write("  No Python processes found\n")
    
    f.write("\nSERVERS:\n")
    for name, (url, port) in servers.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                f.write(f"  {name} (Port {port}): UP\n")
            else:
                f.write(f"  {name} (Port {port}): DOWN (Status: {response.status_code})\n")
        except:
            f.write(f"  {name} (Port {port}): DOWN\n")
    
    f.write("\nBROKERS:\n")
    f.write(f"  Alpaca: {'CONFIGURED' if alpaca_key else 'NOT CONFIGURED'}\n")
    f.write("  Interactive Brokers: DOWN (as noted)\n")
    
    f.write("\nPORTS IN USE:\n")
    for conn in psutil.net_connections(kind='inet'):
        try:
            if conn.status == 'LISTEN' and conn.laddr.port in [8000, 5000, 5001, 8002]:
                f.write(f"  Port {conn.laddr.port}: IN USE (PID: {conn.pid})\n")
        except:
            pass
    
    f.write("\n" + "="*80 + "\n")

print("\n" + "="*80)
print("Status report also saved to: status_report.txt")
print("="*80)
