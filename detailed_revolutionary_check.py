"""
Detailed check of Revolutionary AI engines with extended timeout
"""
import requests
import json
from datetime import datetime
import time

def check_revolutionary_engines():
    """Check Revolutionary engines with retry logic"""
    print("="*80)
    print("  REVOLUTIONARY AI ENGINES - DETAILED STATUS CHECK")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    url = "http://localhost:8000/api/revolutionary/engines/status"
    
    print(f"Checking endpoint: {url}")
    print("Please wait, this may take up to 30 seconds...\n")
    
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}/3...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("\n[CHECK] SUCCESS! Revolutionary Engines API responded\n")
                print("="*80)
                print("  REVOLUTIONARY ENGINES STATUS")
                print("="*80)
                print(json.dumps(data, indent=2))
                
                if data.get('success'):
                    engines = data.get('engines', {})
                    available = data.get('available_engines', 0)
                    total = data.get('total_engines', 5)
                    
                    print("\n" + "="*80)
                    print("  SUMMARY")
                    print("="*80)
                    print(f"Total Engines: {total}")
                    print(f"Active Engines: {available}")
                    print(f"Inactive Engines: {total - available}")
                    
                    if available == 0:
                        print("\n[WARNING]️  WARNING: No Revolutionary engines are currently active!")
                        print("\n💡 POSSIBLE REASONS:")
                        print("   1. Engines need to be initialized on server startup")
                        print("   2. Engines require explicit activation via API")
                        print("   3. Server may have started without Revolutionary components")
                        print("\n💡 SOLUTIONS:")
                        print("   1. Restart the backend server to reinitialize engines")
                        print("   2. Call POST /api/revolutionary/start (requires admin auth)")
                        print("   3. Check unified_production_server.py startup code")
                    elif available < total:
                        print(f"\n[WARNING]️  WARNING: Only {available}/{total} engines are active")
                        inactive = [name for name, status in engines.items() if status != "active"]
                        print(f"   Inactive engines: {', '.join(inactive)}")
                    else:
                        print("\n[CHECK] ALL REVOLUTIONARY ENGINES ARE ACTIVE!")
                        print("   The system is ready for advanced trading operations")
                
                return True
            else:
                print(f"   [ERROR] HTTP {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout after 30 seconds")
            if attempt < 2:
                print("   Retrying in 5 seconds...")
                time.sleep(5)
        except requests.exceptions.ConnectionError as e:
            print(f"   [ERROR] Connection Error: {e}")
            break
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
            if attempt < 2:
                print("   Retrying in 5 seconds...")
                time.sleep(5)
    
    print("\n" + "="*80)
    print("[ERROR] FAILED TO GET REVOLUTIONARY ENGINES STATUS")
    print("="*80)
    print("\n💡 TROUBLESHOOTING:")
    print("   1. Backend server may be overloaded or stuck")
    print("   2. Check if backend process is responsive:")
    print("      • Open http://localhost:8000/docs in browser")
    print("      • Try simpler endpoint: http://localhost:8000/health")
    print("   3. Consider restarting the backend server")
    print("   4. Check server logs for errors")
    
    return False

def check_broker_endpoints():
    """Check broker status endpoints"""
    print("\n" + "="*80)
    print("  BROKER STATUS CHECK")
    print("="*80)
    
    # Try the trading system brokers endpoint (may not require auth)
    url = "http://localhost:8000/api/trading/system/brokers"
    print(f"\nChecking: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("[CHECK] SUCCESS!\n")
            print(json.dumps(data, indent=2))
        elif response.status_code == 401:
            print("[WARNING]️  Requires authentication")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Check IB status endpoint
    url = "http://localhost:8000/api/ib/status"
    print(f"\nChecking: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("[CHECK] SUCCESS!\n")
            print(json.dumps(data, indent=2))
        elif response.status_code == 401:
            print("[WARNING]️  Requires authentication")
        elif response.status_code == 404:
            print("[WARNING]️  Endpoint not found")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    # Check Revolutionary engines
    success = check_revolutionary_engines()
    
    # Check broker endpoints
    check_broker_endpoints()
    
    print("\n" + "="*80)
    print("  CHECK COMPLETE")
    print("="*80)
    print(f"\nFor full API documentation, visit: http://localhost:8000/docs")
    print("For the trading dashboard, visit: http://localhost:3000")

