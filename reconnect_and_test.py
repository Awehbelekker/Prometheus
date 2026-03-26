"""Reconnect PROMETHEUS to IB Gateway and test connection"""
import time
import subprocess
import socket

print("\n" + "="*80)
print("🔄 RECONNECTING PROMETHEUS TO IB GATEWAY")
print("="*80)

# Step 1: Check if IB Gateway is listening on port 7497
print("\n1️⃣ Checking IB Gateway API port...")
def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

ib_listening = check_port('127.0.0.1', 7497)
if ib_listening:
    print("   [CHECK] IB Gateway is listening on port 7497")
else:
    print("   [ERROR] IB Gateway is NOT listening on port 7497")
    print("   [WARNING]️  You need to enable API in IB Gateway settings:")
    print("      1. Open IB Gateway")
    print("      2. Configure → Settings → API → Settings")
    print("      3. Check 'Enable ActiveX and Socket Clients'")
    print("      4. Port: 7497")
    print("      5. Click OK")
    print("\n   Waiting 30 seconds for you to enable API...")
    time.sleep(30)
    
    # Check again
    ib_listening = check_port('127.0.0.1', 7497)
    if ib_listening:
        print("   [CHECK] IB Gateway is now listening on port 7497!")
    else:
        print("   [ERROR] Still not listening. Please enable API and run this script again.")
        exit(1)

# Step 2: Restart PROMETHEUS service to reconnect
print("\n2️⃣ Restarting PROMETHEUS service...")
try:
    # Stop service
    print("   Stopping service...")
    result = subprocess.run(['sc', 'stop', 'PrometheusTrading'], 
                          capture_output=True, text=True, timeout=30)
    time.sleep(5)
    
    # Start service
    print("   Starting service...")
    result = subprocess.run(['sc', 'start', 'PrometheusTrading'], 
                          capture_output=True, text=True, timeout=30)
    time.sleep(10)
    
    # Check status
    result = subprocess.run(['sc', 'query', 'PrometheusTrading'], 
                          capture_output=True, text=True)
    if 'RUNNING' in result.stdout:
        print("   [CHECK] Service restarted successfully")
    else:
        print("   [WARNING]️  Service may not have started properly")
        print(result.stdout)
except Exception as e:
    print(f"   [ERROR] Error restarting service: {e}")
    print("   Try manually: Restart-Service PrometheusTrading")

# Step 3: Wait for connection to establish
print("\n3️⃣ Waiting for PROMETHEUS to connect to IB Gateway...")
print("   (This may take 30-60 seconds)")
time.sleep(30)

# Step 4: Test IB connection
print("\n4️⃣ Testing IB connection...")
try:
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    
    config = {
        'host': '127.0.0.1',
        'port': 7497,
        'client_id': 1,
        'paper_trading': True
    }
    
    print("   Attempting to connect...")
    broker = InteractiveBrokersBroker(config)
    
    # Try to connect
    try:
        broker.connect()
        time.sleep(5)
        
        if broker.is_connected():
            print("   [CHECK] Successfully connected to IB Gateway!")
            
            # Try to get account info
            try:
                account = broker.get_account_info()
                print(f"   [CHECK] Account connected: {account.get('account_id', 'Unknown')}")
                print(f"   💰 Buying Power: ${account.get('buying_power', 0):,.2f}")
            except Exception as e:
                print(f"   [WARNING]️  Connected but couldn't get account info: {e}")
            
            broker.disconnect()
        else:
            print("   [ERROR] Connection attempt failed")
            print("   Check IB Gateway API settings")
    except Exception as e:
        print(f"   [ERROR] Connection error: {e}")
        
except Exception as e:
    print(f"   [ERROR] Error testing connection: {e}")

# Step 5: Final status check
print("\n5️⃣ Final Status Check...")
time.sleep(5)

result = subprocess.run(['python', 'quick_status_check.py'], 
                       capture_output=True, text=True, timeout=30)
print(result.stdout)

print("\n" + "="*80)
print("🏁 RECONNECTION COMPLETE")
print("="*80)
print("\nNext Steps:")
print("1. If port 7497 is now active: [CHECK] System should start trading")
print("2. If port 7497 still not active: [ERROR] Enable API in IB Gateway")
print("3. Monitor for 30 minutes to see if trades execute")
print("4. Check logs: Get-Content 'logs\\prometheus_stderr.log' -Tail 50")
print("="*80)

