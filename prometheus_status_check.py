"""PROMETHEUS System Status Check"""
import requests
import json
from datetime import datetime
import socket

print("=" * 70)
print("PROMETHEUS TRADING PLATFORM - SYSTEM STATUS")
print("Time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("=" * 70)

# Check backend
print("\n[1] BACKEND API (port 8000)")
try:
    r = requests.get("http://localhost:8000/", timeout=5)
    data = r.json()
    print("    Status: RUNNING")
    print("    Name: " + str(data.get('name')))
    print("    Version: " + str(data.get('version')))
except Exception as e:
    print("    Status: ERROR - " + str(e))

# Check health
print("\n[2] SYSTEM HEALTH")
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    data = r.json()
    print("    Status: " + str(data.get('status', 'unknown')))
except Exception as e:
    print("    Status: ERROR - " + str(e))

# Check trading status
print("\n[3] TRADING STATUS")
try:
    r = requests.get("http://localhost:8000/api/trading/status", timeout=5)
    if r.status_code == 200:
        data = r.json()
        trading = data.get('trading', {})
        print("    Active: " + str(trading.get('active')))
        print("    Mode: " + str(trading.get('mode')))
        brokers = trading.get('broker_connections', {})
        if brokers:
            print("    IB: " + str(brokers.get('interactive_brokers', 'unknown')))
            print("    Alpaca: " + str(brokers.get('alpaca', 'unknown')))
    else:
        print("    Error: HTTP " + str(r.status_code))
except Exception as e:
    print("    Error: " + str(e))

# Check live trading status
print("\n[4] LIVE TRADING STATUS")
try:
    r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print("    Active: " + str(data.get('active')))
        print("    User: " + str(data.get('user')))
        print("    Globally Enabled: " + str(data.get('enabled_globally')))
    else:
        print("    Error: HTTP " + str(r.status_code))
except Exception as e:
    print("    Error: " + str(e))

# Direct IB Gateway check
print("\n[5] DIRECT IB GATEWAY CHECK (port 4002)")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(("127.0.0.1", 4002))
    sock.close()
    if result == 0:
        print("    Port 4002: LISTENING (IB Gateway running)")
    else:
        print("    Port 4002: NOT AVAILABLE")
except Exception as e:
    print("    Error: " + str(e))

# Direct IB connection test
print("\n[6] DIRECT IB API TEST")
try:
    from ib_insync import IB
    import asyncio

    async def test_ib():
        ib = IB()
        try:
            await ib.connectAsync('127.0.0.1', 4002, clientId=99, timeout=5)
            if ib.isConnected():
                accounts = ib.managedAccounts()
                print("    Connected: YES")
                print("    Accounts: " + str(accounts))
                positions = ib.positions()
                print("    Positions: " + str(len(positions)))
                for pos in positions:
                    print("      - " + pos.contract.symbol + ": " + str(pos.position) + " shares")
                ib.disconnect()
            else:
                print("    Connected: NO")
        except Exception as e:
            print("    Error: " + str(e))

    asyncio.run(test_ib())
except Exception as e:
    print("    Error: " + str(e))

print("\n" + "=" * 70)
print("STATUS CHECK COMPLETE")
print("=" * 70)

