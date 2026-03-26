#!/usr/bin/env python3
"""
Final System Integration Test
Tests both backend API and frontend connectivity
"""

import requests
import json
import time
from datetime import datetime

def test_backend_api():
    """Test backend API endpoints"""
    print("=" * 60)
    print("BACKEND API TESTING")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoints = [
        {"url": f"{base_url}/health", "name": "Health Check"},
        {"url": f"{base_url}/api/revolutionary/engines/status", "name": "Revolutionary Engines"},
        {"url": f"{base_url}/api/trading/status", "name": "Trading Status"},
        {"url": f"{base_url}/api/portfolio/value", "name": "Portfolio Value"},
        {"url": f"{base_url}/api/system/metrics", "name": "System Metrics"},
    ]
    
    backend_results = []
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint['url'], timeout=5)
            success = response.status_code == 200
            backend_results.append({
                "name": endpoint['name'],
                "success": success,
                "status_code": response.status_code
            })
            print(f"{'PASS' if success else 'FAIL'} - {endpoint['name']} ({response.status_code})")
        except Exception as e:
            backend_results.append({
                "name": endpoint['name'],
                "success": False,
                "error": str(e)
            })
            print(f"FAIL - {endpoint['name']} (Error: {e})")
    
    return backend_results

def test_frontend_connectivity():
    """Test frontend connectivity"""
    print("\n" + "=" * 60)
    print("FRONTEND CONNECTIVITY TESTING")
    print("=" * 60)
    
    frontend_url = "http://localhost:3000"
    
    try:
        response = requests.get(frontend_url, timeout=10)
        success = response.status_code == 200
        print(f"{'PASS' if success else 'FAIL'} - Frontend Main Page ({response.status_code})")
        
        # Check if it's serving HTML
        is_html = 'text/html' in response.headers.get('content-type', '')
        print(f"{'PASS' if is_html else 'FAIL'} - Serving HTML Content")
        
        return {
            "main_page": success,
            "html_content": is_html,
            "status_code": response.status_code
        }
    except Exception as e:
        print(f"FAIL - Frontend Connection (Error: {e})")
        return {
            "main_page": False,
            "html_content": False,
            "error": str(e)
        }

def test_api_integration():
    """Test API integration from frontend perspective"""
    print("\n" + "=" * 60)
    print("API INTEGRATION TESTING")
    print("=" * 60)
    
    # Test AI Analysis endpoint
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/analyze",
            json={"query": "Test AI analysis"},
            timeout=10
        )
        success = response.status_code == 200
        print(f"{'PASS' if success else 'FAIL'} - AI Analysis API ({response.status_code})")
        
        if success:
            data = response.json()
            print(f"    Response: {data.get('status', 'unknown')}")
        
        return success
    except Exception as e:
        print(f"FAIL - AI Analysis API (Error: {e})")
        return False

def main():
    """Run complete system test"""
    print("COMPLETE SYSTEM INTEGRATION TEST")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test backend
    backend_results = test_backend_api()
    
    # Test frontend
    frontend_results = test_frontend_connectivity()
    
    # Test API integration
    api_integration = test_api_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPLETE SYSTEM TEST SUMMARY")
    print("=" * 80)
    
    backend_passed = sum(1 for r in backend_results if r['success'])
    backend_total = len(backend_results)
    
    print(f"Backend API: {backend_passed}/{backend_total} endpoints working")
    print(f"Frontend: {'Working' if frontend_results['main_page'] else 'Not Working'}")
    print(f"API Integration: {'Working' if api_integration else 'Not Working'}")
    
    overall_success = (
        backend_passed == backend_total and 
        frontend_results['main_page'] and 
        api_integration
    )
    
    print(f"\nOverall System Status: {'FULLY OPERATIONAL' if overall_success else 'NEEDS ATTENTION'}")
    
    if overall_success:
        print("\nSYSTEM IS READY FOR TRADING!")
        print("Backend API: http://localhost:8000")
        print("Frontend: http://localhost:3000")
    else:
        print("\nIssues found that need to be addressed:")
        if backend_passed < backend_total:
            print(f"- {backend_total - backend_passed} backend endpoints not working")
        if not frontend_results['main_page']:
            print("- Frontend not accessible")
        if not api_integration:
            print("- API integration issues")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
