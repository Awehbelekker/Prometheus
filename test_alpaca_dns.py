"""Test DNS resolution and connectivity for Alpaca API endpoints"""

import socket
import requests
from datetime import datetime
import sys

def test_alpaca_dns():
    """Test DNS resolution for Alpaca API"""
    
    print("=" * 60)
    print(f"Alpaca DNS Diagnostic Test")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test DNS Resolution
    endpoints = {
        'Paper Trading': 'paper-api.alpaca.markets',
        'Live Trading': 'api.alpaca.markets',
        'Data API': 'data.alpaca.markets'
    }
    
    results = {}
    
    for name, hostname in endpoints.items():
        print(f"\nTesting: {name}")
        print(f"   Hostname: {hostname}")
        print("-" * 60)
        
        # Test 1: DNS Resolution
        dns_ok = False
        ip_address = None
        try:
            ip_address = socket.gethostbyname(hostname)
            print(f"[OK] DNS Resolution: {ip_address}")
            dns_ok = True
        except socket.gaierror as e:
            print(f"[FAILED] DNS Resolution Failed")
            print(f"   Error: {e}")
            results[name] = {'dns': False, 'http': False, 'error': str(e)}
            continue
        
        # Test 2: HTTP Connection (with timeout)
        http_ok = False
        try:
            # Try a simple HEAD request to check connectivity
            response = requests.head(
                f"https://{hostname}/",
                timeout=10,
                allow_redirects=True
            )
            print(f"[OK] HTTP Connection: OK")
            print(f"   Status Code: {response.status_code}")
            http_ok = True
        except requests.exceptions.ConnectionError as e:
            print(f"[FAILED] HTTP Connection Failed")
            print(f"   Error: Cannot connect to server")
        except requests.exceptions.Timeout as e:
            print(f"[WARNING] Connection Timeout")
            print(f"   Error: Request took too long (>10s)")
        except requests.exceptions.SSLError as e:
            print(f"[FAILED] SSL Error")
            print(f"   Error: Certificate verification failed")
        except Exception as e:
            print(f"[FAILED] HTTP Error: {type(e).__name__}")
            print(f"   Error: {str(e)}")
        
        results[name] = {
            'dns': dns_ok,
            'http': http_ok,
            'ip': ip_address
        }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_dns_ok = all(r.get('dns', False) for r in results.values())
    all_http_ok = all(r.get('http', False) for r in results.values())
    
    if all_dns_ok and all_http_ok:
        print("[OK] All endpoints OK - No DNS issues detected")
        return_code = 0
    elif all_dns_ok and not all_http_ok:
        print("[WARNING] DNS OK but HTTP connection issues detected")
        print("   This may indicate: firewall, network, or Alpaca server issues")
        return_code = 1
    else:
        print("[FAILED] DNS resolution failures detected")
        print("   Recommended actions:")
        print("   1. Flush DNS cache: ipconfig /flushdns")
        print("   2. Restart network adapter")
        print("   3. Check internet connection")
        print("   4. Try different DNS servers (8.8.8.8 or 1.1.1.1)")
        return_code = 2
    
    print("\nEndpoint Status:")
    for name, result in results.items():
        status = "[OK]" if (result.get('dns') and result.get('http')) else "[FAILED]"
        print(f"   {status} {name}")
    
    print("\n" + "=" * 60)
    
    return return_code

def test_current_dns():
    """Test current DNS server performance"""
    print("\nTesting DNS Server Performance")
    print("-" * 60)
    
    import time
    
    test_domain = 'www.google.com'  # Well-known domain
    
    start = time.time()
    try:
        ip = socket.gethostbyname(test_domain)
        duration = (time.time() - start) * 1000
        
        if duration < 50:
            print(f"[OK] DNS Response Time: {duration:.0f}ms (Fast)")
        elif duration < 200:
            print(f"[WARNING] DNS Response Time: {duration:.0f}ms (Slow)")
        else:
            print(f"[FAILED] DNS Response Time: {duration:.0f}ms (Very Slow)")
        
        print(f"   Resolved: {test_domain} -> {ip}")
    except Exception as e:
        print(f"[FAILED] DNS Test Failed: {e}")

if __name__ == "__main__":
    try:
        test_current_dns()
        exit_code = test_alpaca_dns()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)

