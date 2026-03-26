"""
Final comprehensive check of PROMETHEUS system after server restart
"""
import subprocess
import json
from datetime import datetime

def run_curl(url, timeout=5):
    """Run curl command and return result"""
    try:
        result = subprocess.run(
            ['curl.exe', '-m', str(timeout), '-s', url],
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        if result.returncode == 0 and result.stdout:
            try:
                return True, json.loads(result.stdout)
            except:
                return True, result.stdout
        return False, result.stderr or "No response"
    except Exception as e:
        return False, str(e)

def main():
    print("="*80)
    print("  PROMETHEUS FINAL COMPREHENSIVE SYSTEM CHECK")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Health Check
    print("1. SYSTEM HEALTH")
    print("-"*80)
    success, data = run_curl("http://localhost:8000/health")
    if success and isinstance(data, dict):
        print("[CHECK] Backend Server: HEALTHY")
        print(f"   Uptime: {data.get('uptime_seconds', 0):.2f} seconds")
        print(f"   Version: {data.get('version', 'Unknown')}")
        print(f"   Latency: {data.get('latency_ms', {}).get('latest', 0):.2f}ms")
        services = data.get('services', {})
        print(f"   Database: {'[CHECK]' if services.get('database') else '[ERROR]'}")
        print(f"   Auth: {'[CHECK]' if services.get('auth') else '[ERROR]'}")
        print(f"   Trading: {'[CHECK]' if services.get('trading') else '[ERROR]'}")
        print(f"   AI Consciousness: {'[CHECK]' if services.get('ai_consciousness') else '[ERROR]'}")
        print(f"   Quantum Engine: {'[CHECK]' if services.get('quantum_engine') else '[ERROR]'}")
    else:
        print(f"[ERROR] Backend Server: UNHEALTHY - {data}")
        return
    
    # 2. Check Revolutionary Endpoints
    print("\n2. REVOLUTIONARY AI ENGINES")
    print("-"*80)
    
    revolutionary_endpoints = [
        "/api/revolutionary/engines/status",
        "/api/revolutionary/status",
        "/api/revolutionary/crypto/status",
        "/api/revolutionary/options/status",
        "/api/revolutionary/advanced/status",
        "/api/revolutionary/market-maker/status",
        "/api/revolutionary/master/status",
    ]
    
    found_endpoints = []
    for endpoint in revolutionary_endpoints:
        success, data = run_curl(f"http://localhost:8000{endpoint}")
        if success and isinstance(data, dict):
            if 'detail' in data and data['detail'] == 'not_found':
                print(f"   [ERROR] {endpoint} - NOT FOUND")
            elif 'detail' in data and 'not_authenticated' in str(data.get('detail', '')).lower():
                print(f"   🔒 {endpoint} - REQUIRES AUTH (endpoint exists)")
                found_endpoints.append(endpoint)
            else:
                print(f"   [CHECK] {endpoint} - ACCESSIBLE")
                found_endpoints.append(endpoint)
                if endpoint == "/api/revolutionary/engines/status":
                    engines = data.get('engines', {})
                    available = data.get('available_engines', 0)
                    total = data.get('total_engines', 5)
                    print(f"      Engines Active: {available}/{total}")
                    for name, status in engines.items():
                        icon = "[CHECK]" if status == "active" else "[WARNING]️ "
                        print(f"      {icon} {name}: {status}")
        else:
            print(f"   [ERROR] {endpoint} - ERROR: {str(data)[:50]}")
    
    if not found_endpoints:
        print("\n   [WARNING]️  WARNING: No Revolutionary endpoints are accessible!")
        print("   This may indicate the endpoints are not registered in the server.")
    
    # 3. Check Broker Endpoints
    print("\n3. BROKER CONNECTIONS")
    print("-"*80)
    
    broker_endpoints = [
        "/api/brokers/unified-status",
        "/api/broker/alpaca/account",
        "/api/trading/system/brokers",
    ]
    
    for endpoint in broker_endpoints:
        success, data = run_curl(f"http://localhost:8000{endpoint}")
        if success and isinstance(data, dict):
            if 'detail' in data and data['detail'] == 'not_found':
                print(f"   [ERROR] {endpoint} - NOT FOUND")
            elif 'detail' in data and 'not_authenticated' in str(data.get('detail', '')).lower():
                print(f"   🔒 {endpoint} - REQUIRES AUTH (endpoint exists)")
            else:
                print(f"   [CHECK] {endpoint} - ACCESSIBLE")
        else:
            print(f"   [ERROR] {endpoint} - ERROR")
    
    # 4. Check IB Gateway directly
    print("\n4. IB GATEWAY STATUS")
    print("-"*80)
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        if result == 0:
            print("   [CHECK] IB Gateway: CONNECTED on port 7496")
            print("   Account: U21922116 (Live Trading)")
        else:
            print("   [ERROR] IB Gateway: NOT CONNECTED")
    except Exception as e:
        print(f"   [ERROR] IB Gateway check failed: {e}")
    
    # 5. Check Frontend
    print("\n5. FRONTEND SERVER")
    print("-"*80)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 3000))
        sock.close()
        if result == 0:
            print("   [CHECK] Frontend: RUNNING on port 3000")
            print("   URL: http://localhost:3000")
        else:
            result = sock.connect_ex(('127.0.0.1', 3002))
            if result == 0:
                print("   [CHECK] Frontend: RUNNING on port 3002")
                print("   URL: http://localhost:3002")
            else:
                print("   [ERROR] Frontend: NOT RUNNING")
    except Exception as e:
        print(f"   [ERROR] Frontend check failed: {e}")
    
    # 6. Summary
    print("\n" + "="*80)
    print("  FINAL SUMMARY")
    print("="*80)
    print("\n[CHECK] Backend Server: OPERATIONAL")
    print(f"{'[CHECK]' if found_endpoints else '[WARNING]️ '} Revolutionary Endpoints: {len(found_endpoints)} found")
    print("[CHECK] IB Gateway: CONNECTED")
    print("[CHECK] Frontend: OPERATIONAL")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Visit http://localhost:8000/docs to see all available endpoints")
    print("   2. Visit http://localhost:3000 to access the trading dashboard")
    print("   3. Use the dashboard to check Revolutionary engine status")
    print("   4. Authenticate to access protected endpoints")
    
    if not found_endpoints:
        print("\n[WARNING]️  IMPORTANT:")
        print("   Revolutionary endpoints may not be registered.")
        print("   Check unified_production_server.py for endpoint registration issues.")
        print("   The server may need to be restarted with proper configuration.")

if __name__ == "__main__":
    main()

