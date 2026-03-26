#!/usr/bin/env python3
"""
QUICK PERFORMANCE TEST
Test current performance after Windows optimizations
"""

import requests
import time
import psutil
from datetime import datetime

def test_performance():
    """Test current system performance"""
    print("QUICK PERFORMANCE TEST")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    print("SYSTEM RESOURCES:")
    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory.percent}%")
    print(f"Available Memory: {memory.available / (1024**3):.1f} GB")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        ("Health Check", "/health"),
        ("GPT-OSS Models", "/api/gpt-oss/models"),
        ("AI Coordinator", "/api/ai/coordinator/status"),
        ("Performance Metrics", "/api/performance/metrics")
    ]
    
    results = []
    
    print("TESTING ENDPOINTS:")
    print("-" * 30)
    
    for name, endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                results.append(response_time)
                print(f"[SUCCESS] {name}: {response_time:.3f}s")
            else:
                print(f"[ERROR] {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)}")
    
    if results:
        avg_response_time = sum(results) / len(results)
        min_response = min(results)
        max_response = max(results)
        
        print()
        print("PERFORMANCE SUMMARY:")
        print("-" * 30)
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"Fastest Response: {min_response:.3f}s")
        print(f"Slowest Response: {max_response:.3f}s")
        
        # Compare with baseline
        baseline = 2.0
        improvement = ((baseline - avg_response_time) / baseline) * 100
        
        print()
        print("IMPROVEMENT ANALYSIS:")
        print("-" * 30)
        print(f"Baseline: {baseline:.3f}s")
        print(f"Current: {avg_response_time:.3f}s")
        print(f"Improvement: {improvement:.1f}%")
        
        if improvement > 50:
            print("STATUS: EXCELLENT - Major performance improvement!")
        elif improvement > 25:
            print("STATUS: GOOD - Significant performance improvement!")
        elif improvement > 10:
            print("STATUS: MODERATE - Some performance improvement!")
        elif improvement > 0:
            print("STATUS: MINIMAL - Small performance improvement!")
        else:
            print("STATUS: NO IMPROVEMENT - System bottleneck persists")
        
        print()
        print("RECOMMENDATIONS:")
        print("-" * 30)
        if improvement < 25:
            print("1. Apply Windows Defender exclusions manually")
            print("2. Disable Windows Search indexing")
            print("3. Disable unnecessary Windows services")
            print("4. Consider hardware upgrade (CPU/Memory)")
            print("5. Use WSL2 or Docker for better performance")
        else:
            print("1. Performance is good - continue with live trading")
            print("2. Monitor system resources during trading")
            print("3. Consider additional optimizations if needed")
    
    print()
    print("=" * 50)
    print("TEST COMPLETE")

if __name__ == "__main__":
    test_performance()

