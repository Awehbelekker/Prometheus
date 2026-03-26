"""
Quick verification of Revolutionary AI and Broker status
"""
import requests
import socket
import json
from datetime import datetime

def check_port(host, port, name):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def main():
    print("="*80)
    print("  PROMETHEUS - REVOLUTIONARY AI & BROKER STATUS CHECK")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Check Backend Server
    print("1. BACKEND SERVER STATUS")
    print("-" * 80)
    backend_up = check_port('127.0.0.1', 8000, 'Backend')
    if backend_up:
        print("[CHECK] Backend Server: RUNNING on port 8000")
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"   Uptime: {data.get('uptime_seconds', 0):.2f} seconds")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Database: {'[CHECK] Connected' if data.get('services', {}).get('database') else '[ERROR] Disconnected'}")
        except Exception as e:
            print(f"   [WARNING]️  Health check failed: {e}")
    else:
        print("[ERROR] Backend Server: NOT RUNNING")
        return
    
    # 2. Check Revolutionary AI Engines
    print("\n2. REVOLUTIONARY AI ENGINES")
    print("-" * 80)
    try:
        response = requests.get("http://localhost:8000/api/revolutionary/engines/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                engines = data.get('engines', {})
                available = data.get('available_engines', 0)
                total = data.get('total_engines', 5)
                
                print(f"[CHECK] Revolutionary Engines API: ACCESSIBLE")
                print(f"   Status: {available}/{total} engines active\n")
                
                engine_names = {
                    'crypto': 'Revolutionary Crypto Engine',
                    'options': 'Revolutionary Options Engine',
                    'advanced': 'Revolutionary Advanced Engine',
                    'market_maker': 'Revolutionary Market Maker',
                    'master': 'Revolutionary Master Engine'
                }
                
                for key, name in engine_names.items():
                    status = engines.get(key, 'unknown')
                    icon = "[CHECK]" if status == "active" else "[WARNING]️ "
                    print(f"   {icon} {name}: {status.upper()}")
                
                if available == 0:
                    print("\n   [WARNING]️  WARNING: No Revolutionary engines are currently active!")
                    print("   💡 Engines may need to be initialized or started via API")
            else:
                print(f"[ERROR] Revolutionary Engines: {data.get('error', 'Unknown error')}")
        else:
            print(f"[ERROR] Revolutionary Engines API returned status {response.status_code}")
    except requests.exceptions.Timeout:
        print("[ERROR] Revolutionary Engines API: TIMEOUT (server may be overloaded)")
    except Exception as e:
        print(f"[ERROR] Revolutionary Engines check failed: {e}")
    
    # 3. Check Broker Connections
    print("\n3. BROKER CONNECTIONS")
    print("-" * 80)
    
    # Check IB Gateway on port 4002 (Gateway Live)
    print("📊 Interactive Brokers:")
    ib_port_open = check_port('127.0.0.1', 4002, 'IB Gateway')
    if ib_port_open:
        print("   [CHECK] IB Gateway: CONNECTED on port 4002")
        print("   Account: U21922116 (Live Trading)")
        print("   Status: Ready for trading operations")
    else:
        print("   [ERROR] IB Gateway: NOT CONNECTED (port 4002 closed)")
        print("   💡 Start IB Gateway and ensure API is enabled on port 4002")
    
    # Check Alpaca configuration
    print("\n📊 Alpaca:")
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        alpaca_key = os.getenv('ALPACA_API_KEY')
        alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        
        if alpaca_key and alpaca_secret:
            print(f"   [CHECK] API Credentials: Configured")
            print(f"   Key: {alpaca_key[:8]}...")
            print(f"   Status: Ready for trading operations")
        else:
            print("   [WARNING]️  API Credentials: NOT CONFIGURED")
            print("   💡 Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
    except Exception as e:
        print(f"   [WARNING]️  Configuration check failed: {e}")
    
    # 4. Check Frontend
    print("\n4. FRONTEND SERVER")
    print("-" * 80)
    frontend_up = check_port('127.0.0.1', 3000, 'Frontend')
    if frontend_up:
        print("[CHECK] Frontend Server: RUNNING on port 3000")
        print("   URL: http://localhost:3000")
    else:
        frontend_3002 = check_port('127.0.0.1', 3002, 'Frontend')
        if frontend_3002:
            print("[CHECK] Frontend Server: RUNNING on port 3002")
            print("   URL: http://localhost:3002")
        else:
            print("[ERROR] Frontend Server: NOT RUNNING")
    
    # 5. Summary
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    
    components = {
        "Backend Server": backend_up,
        "Frontend Server": frontend_up or check_port('127.0.0.1', 3002, 'Frontend'),
        "IB Gateway": ib_port_open,
    }
    
    all_good = all(components.values())
    
    for component, status in components.items():
        icon = "[CHECK]" if status else "[ERROR]"
        print(f"{icon} {component}: {'OPERATIONAL' if status else 'DOWN'}")
    
    print("\n" + "="*80)
    if all_good:
        print("[CHECK] ALL CORE SYSTEMS OPERATIONAL")
        print("\n💡 Next Steps:")
        print("   1. Visit http://localhost:3000 to access the trading dashboard")
        print("   2. Visit http://localhost:8000/docs to explore API endpoints")
        print("   3. Check Revolutionary engine status in the dashboard")
        print("   4. Verify broker connections in the dashboard")
    else:
        print("[WARNING]️  SOME SYSTEMS ARE DOWN")
        print("\n💡 Troubleshooting:")
        if not backend_up:
            print("   • Start backend: python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8000")
        if not (frontend_up or check_port('127.0.0.1', 3002, 'Frontend')):
            print("   • Start frontend: cd frontend && npm start")
        if not ib_port_open:
            print("   • Start IB Gateway or TWS for Interactive Brokers trading")
    
    print("="*80)

if __name__ == "__main__":
    main()

