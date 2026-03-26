#!/usr/bin/env python3
"""Run status check and display results"""

import sys
import os
import psutil
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

output_lines = []

def log(msg):
    print(msg)
    output_lines.append(msg)

log("="*80)
log("PROMETHEUS SYSTEM STATUS")
log("="*80)
log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check Python processes
log("PYTHON PROCESSES:")
python_procs = []
try:
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'][:3]) if proc.info['cmdline'] else 'N/A'
                python_procs.append((proc.info['pid'], cmdline))
        except:
            pass
except Exception as e:
    log(f"  Error checking processes: {e}")

if python_procs:
    log(f"  Found {len(python_procs)} Python process(es):")
    for pid, cmd in python_procs[:10]:
        log(f"    PID {pid}: {cmd[:80]}")
else:
    log("  No Python processes found")

# Check servers
log("\nSERVERS:")
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
            log(f"  {name} (Port {port}): UP")
        else:
            log(f"  {name} (Port {port}): DOWN (Status: {response.status_code})")
    except Exception as e:
        log(f"  {name} (Port {port}): DOWN")

# Check brokers
log("\nBROKERS:")
alpaca_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
log(f"  Alpaca: {'CONFIGURED' if alpaca_key else 'NOT CONFIGURED'}")
log("  Interactive Brokers: DOWN (as noted)")

# Check ports in use
log("\nPORTS IN USE:")
try:
    for conn in psutil.net_connections(kind='inet'):
        try:
            if conn.status == 'LISTEN' and conn.laddr.port in [8000, 5000, 5001, 8002]:
                log(f"  Port {conn.laddr.port}: IN USE (PID: {conn.pid})")
        except:
            pass
except Exception as e:
    log(f"  Error checking ports: {e}")

log("\n" + "="*80)

# Save to file
with open('status_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("\nStatus report saved to: status_report.txt")



