#!/usr/bin/env python
"""Quick system status check for PROMETHEUS"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("PROMETHEUS COMPREHENSIVE STATUS CHECK")
print("=" * 70)

# 1. Check Alpaca
print("\n[1] ALPACA BROKER:")
try:
    key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('APCA_API_KEY_ID')
    secret = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('APCA_API_SECRET_KEY')
    if key and secret:
        headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}
        r = requests.get('https://api.alpaca.markets/v2/account', headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"    Status: CONNECTED")
            print(f"    Account: {data.get('account_number')}")
            print(f"    Equity: ${float(data.get('equity', 0)):,.2f}")
            print(f"    Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
            # Check positions
            r2 = requests.get('https://api.alpaca.markets/v2/positions', headers=headers, timeout=10)
            if r2.status_code == 200:
                positions = r2.json()
                print(f"    Positions: {len(positions)}")
                for p in positions:
                    pnl = float(p.get('unrealized_pl', 0))
                    print(f"      {p['symbol']}: {p['qty']} shares @ ${float(p['current_price']):.2f} (P/L: ${pnl:+,.2f})")
        else:
            print(f"    Status: ERROR ({r.status_code})")
    else:
        print("    Status: NO API KEYS")
except Exception as e:
    print(f"    Status: ERROR - {e}")

# 2. Check Backend
print("\n[2] BACKEND SERVER (Port 8000):")
try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    if r.status_code == 200:
        print(f"    Status: RUNNING")
    else:
        print(f"    Status: ERROR ({r.status_code})")
except:
    print("    Status: NOT RUNNING")

# 3. Check Trading System
print("\n[3] TRADING SYSTEM (Port 8001):")
try:
    r = requests.get('http://localhost:8001/health', timeout=5)
    print(f"    Status: RUNNING")
except:
    print("    Status: NOT RUNNING")

# 4. Check IB Gateway Port
print("\n[4] IB GATEWAY (Port 4002):")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
result = sock.connect_ex(('127.0.0.1', 4002))
sock.close()
if result == 0:
    print("    Status: LISTENING")
else:
    print("    Status: NOT AVAILABLE")

# 5. Check IB Connection (quick test)
print("\n[5] IB API CONNECTION TEST:")
try:
    from ib_insync import IB
    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=99, timeout=10)
    accounts = ib.managedAccounts()
    positions = ib.positions()
    print(f"    Status: CONNECTED")
    print(f"    Accounts: {', '.join(accounts)}")
    print(f"    Positions: {len(positions)}")
    for p in positions:
        print(f"      {p.contract.symbol}: {p.position} @ ${p.avgCost:.2f}")
    ib.disconnect()
except Exception as e:
    print(f"    Status: CONNECTION FAILED")
    print(f"    Error: {e}")

# 6. Check running Python processes
print("\n[6] PROMETHEUS PROCESSES:")
import subprocess
try:
    result = subprocess.run(['wmic', 'process', 'where', "Name='python.exe'", 'get', 'ProcessId,CommandLine', '/format:list'],
                          capture_output=True, text=True, timeout=10)
    lines = result.stdout.strip().split('\n')
    prometheus_procs = []
    current_cmd = ""
    current_pid = ""
    for line in lines:
        if line.startswith('CommandLine='):
            current_cmd = line[12:]
        elif line.startswith('ProcessId='):
            current_pid = line[10:]
            if current_cmd and ('prometheus' in current_cmd.lower() or 'launch' in current_cmd.lower() or 'trading' in current_cmd.lower() or 'auto_exit' in current_cmd.lower()):
                prometheus_procs.append((current_pid, current_cmd[:80]))
            current_cmd = ""
    
    if prometheus_procs:
        for pid, cmd in prometheus_procs:
            print(f"    PID {pid}: {cmd}")
    else:
        print("    No PROMETHEUS processes detected")
except Exception as e:
    print(f"    Error checking: {e}")

print("\n" + "=" * 70)
print("STATUS CHECK COMPLETE")
print("=" * 70)

