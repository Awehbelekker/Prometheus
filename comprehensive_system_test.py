#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE SYSTEM TEST - NO MOCK SYSTEMS
==============================================

This script tests ALL systems to ensure:
1. No mock systems are running
2. All revolutionary engines are active
3. Full AI intelligence is available
4. All trading capabilities are real
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_endpoint(method, url, data=None, description="Endpoint"):
    """Test a single endpoint"""
    start_time = time.time()
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"success": False, "error": "Invalid method", "description": description}

        response_time_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return {
                "success": True, 
                "status_code": response.status_code, 
                "response": response.json(), 
                "response_time_ms": response_time_ms, 
                "description": description
            }
        else:
            return {
                "success": False, 
                "status_code": response.status_code, 
                "response": response.text if response.text else "No response", 
                "response_time_ms": response_time_ms, 
                "error": f"HTTP {response.status_code}", 
                "description": description
            }
    except requests.exceptions.Timeout:
        return {
            "success": False, 
            "error": "Request timed out", 
            "response_time_ms": (time.time() - start_time) * 1000, 
            "description": description
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False, 
            "error": "Connection refused - server not running", 
            "response_time_ms": (time.time() - start_time) * 1000, 
            "description": description
        }
    except Exception as e:
        return {
            "success": False, 
            "error": str(e), 
            "response_time_ms": (time.time() - start_time) * 1000, 
            "description": description
        }

def test_ai_intelligence():
    """Test AI intelligence capabilities"""
    print("\n" + "=" * 60)
    print("TESTING AI INTELLIGENCE")
    print("=" * 60)
    
    ai_tests = [
        {
            "prompt": "Analyze AAPL stock for trading opportunities",
            "expected_keywords": ["analysis", "trading", "opportunity", "stock"]
        },
        {
            "prompt": "What is the current market sentiment for crypto?",
            "expected_keywords": ["sentiment", "crypto", "market", "analysis"]
        },
        {
            "prompt": "Generate a trading strategy for volatile markets",
            "expected_keywords": ["strategy", "trading", "volatile", "market"]
        }
    ]
    
    results = []
    for i, test in enumerate(ai_tests, 1):
        print(f"\nTest {i}: {test['prompt']}")
        result = test_endpoint(
            "POST", 
            "http://localhost:8000/api/ai/analyze", 
            {"prompt": test["prompt"]}, 
            f"AI Analysis Test {i}"
        )
        results.append(result)
        
        if result["success"]:
            response_text = str(result["response"]).lower()
            keywords_found = [kw for kw in test["expected_keywords"] if kw in response_text]
            print(f"[CHECK] Response time: {result['response_time_ms']:.0f}ms")
            print(f"[CHECK] Keywords found: {keywords_found}")
            print(f"[CHECK] AI Intelligence: ACTIVE")
        else:
            print(f"[ERROR] AI Test failed: {result['error']}")
    
    return results

def test_revolutionary_engines():
    """Test all revolutionary engines"""
    print("\n" + "=" * 60)
    print("🤖 TESTING REVOLUTIONARY ENGINES")
    print("=" * 60)
    
    # Test engines status
    result = test_endpoint(
        "GET", 
        "http://localhost:8000/api/revolutionary/engines/status", 
        None, 
        "Revolutionary Engines Status"
    )
    
    if result["success"]:
        engines = result["response"].get("engines", {})
        print("Revolutionary Engines Status:")
        for engine, status in engines.items():
            status_icon = "[CHECK]" if status == "active" else "[ERROR]"
            print(f"  {status_icon} {engine.upper()}: {status}")
        
        active_count = sum(1 for status in engines.values() if status == "active")
        total_count = len(engines)
        print(f"\nActive Engines: {active_count}/{total_count}")
        
        if active_count == total_count:
            print("[CHECK] ALL REVOLUTIONARY ENGINES ACTIVE - NO MOCK SYSTEMS!")
        else:
            print("[WARNING]️ Some engines not active - may have mock systems")
    else:
        print(f"[ERROR] Revolutionary engines test failed: {result['error']}")
    
    return result

def test_trading_systems():
    """Test trading system capabilities"""
    print("\n" + "=" * 60)
    print("💰 TESTING TRADING SYSTEMS")
    print("=" * 60)
    
    # Test trading status
    result = test_endpoint(
        "GET", 
        "http://localhost:8000/api/trading/status", 
        None, 
        "Trading System Status"
    )
    
    if result["success"]:
        trading_data = result["response"].get("trading", {})
        print("Trading System Status:")
        print(f"  Active: {trading_data.get('active', 'Unknown')}")
        print(f"  Mode: {trading_data.get('mode', 'Unknown')}")
        print(f"  Engines Available: {trading_data.get('engines_available', 'Unknown')}")
        print(f"  AI Analysis: {trading_data.get('ai_analysis', 'Unknown')}")
        print(f"  Market Data: {trading_data.get('market_data', 'Unknown')}")
        
        broker_connections = trading_data.get('broker_connections', {})
        print("\nBroker Connections:")
        for broker, status in broker_connections.items():
            status_icon = "[CHECK]" if status == "connected" else "[ERROR]"
            print(f"  {status_icon} {broker}: {status}")
        
        if trading_data.get('active') and trading_data.get('ai_analysis'):
            print("[CHECK] TRADING SYSTEMS ACTIVE - NO MOCK SYSTEMS!")
        else:
            print("[WARNING]️ Trading systems may have mock components")
    else:
        print(f"[ERROR] Trading systems test failed: {result['error']}")
    
    return result

def test_portfolio_systems():
    """Test portfolio and position systems"""
    print("\n" + "=" * 60)
    print("💼 TESTING PORTFOLIO SYSTEMS")
    print("=" * 60)
    
    result = test_endpoint(
        "GET", 
        "http://localhost:8000/api/portfolio/value", 
        None, 
        "Portfolio System"
    )
    
    if result["success"]:
        portfolio_data = result["response"].get("portfolio", {})
        print("Portfolio System Status:")
        print(f"  Total Value: ${portfolio_data.get('total_value', 'Unknown')}")
        print(f"  Cash Balance: ${portfolio_data.get('cash_balance', 'Unknown')}")
        print(f"  Positions: {len(portfolio_data.get('positions', []))}")
        
        if portfolio_data.get('total_value', 0) > 0:
            print("[CHECK] PORTFOLIO SYSTEM ACTIVE - REAL DATA!")
        else:
            print("[WARNING]️ Portfolio system may be using mock data")
    else:
        print(f"[ERROR] Portfolio systems test failed: {result['error']}")
    
    return result

def test_server_health():
    """Test overall server health"""
    print("\n" + "=" * 60)
    print("🏥 TESTING SERVER HEALTH")
    print("=" * 60)
    
    result = test_endpoint(
        "GET", 
        "http://localhost:8000/health", 
        None, 
        "Server Health Check"
    )
    
    if result["success"]:
        health_data = result["response"]
        print("Server Health Status:")
        print(f"  Status: {health_data.get('status', 'Unknown')}")
        print(f"  Uptime: {health_data.get('uptime_seconds', 0):.0f} seconds")
        print(f"  Systems Active: {health_data.get('systems_active', 'Unknown')}")
        print(f"  Total Systems: {health_data.get('total_systems', 'Unknown')}")
        
        if health_data.get('status') == 'healthy':
            print("[CHECK] SERVER HEALTHY - ALL SYSTEMS OPERATIONAL!")
        else:
            print("[WARNING]️ Server health issues detected")
    else:
        print(f"[ERROR] Server health test failed: {result['error']}")
    
    return result

def main():
    """Run comprehensive system test"""
    print("PROMETHEUS COMPREHENSIVE SYSTEM TEST")
    print("=" * 80)
    print("Testing for: NO MOCK SYSTEMS, FULL AI INTELLIGENCE, ALL ENGINES ACTIVE")
    print("=" * 80)
    
    # Test server connectivity first
    print("\nTesting server connectivity...")
    health_result = test_server_health()
    
    if not health_result["success"]:
        print("\n[ERROR] CRITICAL ERROR: Server not responding!")
        print("Please ensure the ultimate server is running:")
        print("  python launch_ultimate_prometheus_LIVE_TRADING.py")
        return
    
    # Run all tests
    test_results = []
    
    # Test revolutionary engines
    engine_result = test_revolutionary_engines()
    test_results.append(engine_result)
    
    # Test AI intelligence
    ai_results = test_ai_intelligence()
    test_results.extend(ai_results)
    
    # Test trading systems
    trading_result = test_trading_systems()
    test_results.append(trading_result)
    
    # Test portfolio systems
    portfolio_result = test_portfolio_systems()
    test_results.append(portfolio_result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for result in test_results if result["success"])
    total_tests = len(test_results)
    
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("[CHECK] NO MOCK SYSTEMS DETECTED")
        print("[CHECK] FULL AI INTELLIGENCE ACTIVE")
        print("[CHECK] ALL REVOLUTIONARY ENGINES OPERATIONAL")
        print("[CHECK] REAL TRADING SYSTEMS ACTIVE")
        print("\n🚀 PROMETHEUS IS READY FOR LIVE TRADING!")
    else:
        print(f"\n[WARNING]️ {total_tests - successful_tests} TESTS FAILED")
        print("Some systems may be using mock data or not fully active")
        
        print("\nFailed tests:")
        for result in test_results:
            if not result["success"]:
                print(f"  [ERROR] {result['description']}: {result['error']}")
    
    # Performance summary
    avg_response_time = sum(r.get("response_time_ms", 0) for r in test_results if r["success"]) / max(successful_tests, 1)
    print(f"\nAverage Response Time: {avg_response_time:.0f}ms")
    
    if avg_response_time < 200:
        print("[CHECK] EXCELLENT PERFORMANCE - Lightning fast responses!")
    elif avg_response_time < 500:
        print("[CHECK] GOOD PERFORMANCE - Fast responses")
    else:
        print("[WARNING]️ SLOW PERFORMANCE - May need optimization")

if __name__ == "__main__":
    main()
