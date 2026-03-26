#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - System Status Checker
Comprehensive health check for all system components.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class PrometheusStatusChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.domain_urls = [
            "https://prometheus-trade.com",
            "https://app.prometheus-trade.com", 
            "https://api.prometheus-trade.com",
            "https://admin.prometheus-trade.com",
            "https://trade.prometheus-trade.com",
            "https://docs.prometheus-trade.com"
        ]
        
    def check_local_backend(self) -> Tuple[bool, str]:
        """Check if local backend server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return True, f"[CHECK] Backend running (Status: {response.status_code})"
            else:
                return False, f"[ERROR] Backend unhealthy (Status: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return False, "[ERROR] Backend not accessible (Connection refused)"
        except requests.exceptions.Timeout:
            return False, "[ERROR] Backend timeout (>5s)"
        except Exception as e:
            return False, f"[ERROR] Backend error: {str(e)}"
    
    def check_local_frontend(self) -> Tuple[bool, str]:
        """Check if local frontend server is running"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                return True, f"[CHECK] Frontend running (Status: {response.status_code})"
            else:
                return False, f"[ERROR] Frontend unhealthy (Status: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return False, "[ERROR] Frontend not accessible (Connection refused)"
        except requests.exceptions.Timeout:
            return False, "[ERROR] Frontend timeout (>5s)"
        except Exception as e:
            return False, f"[ERROR] Frontend error: {str(e)}"
    
    def check_domain_access(self, url: str) -> Tuple[bool, str]:
        """Check if domain is accessible through Cloudflare tunnel"""
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                return True, f"[CHECK] Accessible (Status: {response.status_code})"
            elif response.status_code in [301, 302, 307, 308]:
                return True, f"[CHECK] Redirecting (Status: {response.status_code})"
            else:
                return False, f"[ERROR] Unhealthy (Status: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return False, "[ERROR] Connection failed"
        except requests.exceptions.Timeout:
            return False, "[ERROR] Timeout (>10s)"
        except requests.exceptions.SSLError:
            return False, "[ERROR] SSL/TLS error"
        except Exception as e:
            return False, f"[ERROR] Error: {str(e)[:50]}"
    
    def check_api_endpoints(self) -> Dict[str, Tuple[bool, str]]:
        """Check critical API endpoints"""
        endpoints = {
            "/health": "Health check",
            "/docs": "API documentation", 
            "/api/v1/market/status": "Market status",
            "/api/v1/trading/portfolio": "Portfolio data",
            "/api/v1/auth/status": "Authentication status"
        }
        
        results = {}
        for endpoint, description in endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    results[endpoint] = (True, f"[CHECK] {description} OK")
                elif response.status_code == 401:
                    results[endpoint] = (True, f"[CHECK] {description} (Auth required)")
                elif response.status_code == 404:
                    results[endpoint] = (False, f"[ERROR] {description} (Not found)")
                else:
                    results[endpoint] = (False, f"[ERROR] {description} (Status: {response.status_code})")
            except Exception as e:
                results[endpoint] = (False, f"[ERROR] {description} (Error: {str(e)[:30]})")
        
        return results
    
    def check_database_connection(self) -> Tuple[bool, str]:
        """Check database connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/system/db-status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "connected":
                    return True, f"[CHECK] Database connected ({data.get('type', 'Unknown')})"
                else:
                    return False, f"[ERROR] Database disconnected"
            else:
                return False, f"[ERROR] Database status check failed (Status: {response.status_code})"
        except Exception:
            # Fallback: check if database file exists
            db_path = "Desktop/PROMETHEUS-Trading-Platform/prometheus_trading.db"
            if os.path.exists(db_path):
                return True, "[CHECK] SQLite database file exists"
            else:
                return False, "[ERROR] Database file not found"
    
    def check_market_data_feed(self) -> Tuple[bool, str]:
        """Check market data feed status"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/market/data/AAPL", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "price" in data and data["price"] > 0:
                    return True, f"[CHECK] Market data active (AAPL: ${data['price']})"
                else:
                    return False, "[ERROR] Market data invalid"
            else:
                return False, f"[ERROR] Market data unavailable (Status: {response.status_code})"
        except Exception as e:
            return False, f"[ERROR] Market data error: {str(e)[:30]}"
    
    def check_cloudflare_tunnel(self) -> Tuple[bool, str]:
        """Check if Cloudflare tunnel is running"""
        try:
            # Check tunnel metrics endpoint
            response = requests.get("http://127.0.0.1:20241/metrics", timeout=3)
            if response.status_code == 200:
                return True, "[CHECK] Cloudflare tunnel active (metrics accessible)"
            else:
                return False, "[ERROR] Cloudflare tunnel metrics unavailable"
        except Exception:
            return False, "[ERROR] Cloudflare tunnel not detected"
    
    def run_comprehensive_check(self) -> Dict[str, any]:
        """Run all system checks and return results"""
        print("🔍 PROMETHEUS Trading Platform - System Status Check")
        print("=" * 60)
        print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        
        # Local services check
        print("🖥️  LOCAL SERVICES:")
        backend_ok, backend_msg = self.check_local_backend()
        frontend_ok, frontend_msg = self.check_local_frontend()
        
        print(f"   Backend:  {backend_msg}")
        print(f"   Frontend: {frontend_msg}")
        
        results["checks"]["local_backend"] = {"status": backend_ok, "message": backend_msg}
        results["checks"]["local_frontend"] = {"status": frontend_ok, "message": frontend_msg}
        
        # Database check
        print("\n💾 DATABASE:")
        db_ok, db_msg = self.check_database_connection()
        print(f"   Database: {db_msg}")
        results["checks"]["database"] = {"status": db_ok, "message": db_msg}
        
        # Market data check
        print("\n📊 MARKET DATA:")
        market_ok, market_msg = self.check_market_data_feed()
        print(f"   Data Feed: {market_msg}")
        results["checks"]["market_data"] = {"status": market_ok, "message": market_msg}
        
        # Cloudflare tunnel check
        print("\n☁️  CLOUDFLARE TUNNEL:")
        tunnel_ok, tunnel_msg = self.check_cloudflare_tunnel()
        print(f"   Tunnel: {tunnel_msg}")
        results["checks"]["cloudflare_tunnel"] = {"status": tunnel_ok, "message": tunnel_msg}
        
        # Domain accessibility check
        print("\n🌐 DOMAIN ACCESS:")
        domain_results = {}
        for url in self.domain_urls:
            domain_ok, domain_msg = self.check_domain_access(url)
            domain_name = url.replace("https://", "").replace("http://", "")
            print(f"   {domain_name:<25} {domain_msg}")
            domain_results[url] = {"status": domain_ok, "message": domain_msg}
        
        results["checks"]["domains"] = domain_results
        
        # API endpoints check
        if backend_ok:
            print("\n🔌 API ENDPOINTS:")
            api_results = self.check_api_endpoints()
            for endpoint, (status, message) in api_results.items():
                print(f"   {endpoint:<25} {message}")
            results["checks"]["api_endpoints"] = {ep: {"status": status, "message": msg} for ep, (status, msg) in api_results.items()}
        
        # Calculate summary
        all_checks = []
        all_checks.extend([backend_ok, frontend_ok, db_ok, market_ok, tunnel_ok])
        all_checks.extend([result["status"] for result in domain_results.values()])
        if backend_ok:
            all_checks.extend([status for status, _ in self.check_api_endpoints().values()])
        
        results["summary"]["total"] = len(all_checks)
        results["summary"]["passed"] = sum(all_checks)
        results["summary"]["failed"] = len(all_checks) - sum(all_checks)
        
        # Print summary
        print(f"\n📋 SUMMARY:")
        print(f"   Total Checks: {results['summary']['total']}")
        print(f"   [CHECK] Passed: {results['summary']['passed']}")
        print(f"   [ERROR] Failed: {results['summary']['failed']}")
        
        if results["summary"]["failed"] == 0:
            print(f"\n🎉 All systems operational! PROMETHEUS is ready for trading.")
        else:
            print(f"\n[WARNING]️  Some issues detected. Please review failed checks above.")
        
        return results

def main():
    """Main function"""
    checker = PrometheusStatusChecker()
    results = checker.run_comprehensive_check()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"Desktop/PROMETHEUS-Trading-Platform/logs/system_status_{timestamp}.json"
    
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n[WARNING]️  Could not save results: {e}")
    
    # Return exit code based on results
    return 0 if results["summary"]["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
