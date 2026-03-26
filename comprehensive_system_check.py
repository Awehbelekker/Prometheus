#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM CHECK
Double-check all Prometheus trading components
"""

import requests
import json
import time
from datetime import datetime
import sqlite3

def check_server_health():
    """Check all server health"""
    print("1. CHECKING SERVER HEALTH")
    print("=" * 50)
    
    servers = {
        "Main Server (Port 8000)": "http://localhost:8000/health",
        "GPT-OSS 20B (Port 5000)": "http://localhost:5000/health", 
        "GPT-OSS 120B (Port 5001)": "http://localhost:5001/health"
    }
    
    all_healthy = True
    
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {name}: HEALTHY")
            else:
                print(f"   [ERROR] {name}: {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")
            all_healthy = False
    
    return all_healthy

def check_trading_status():
    """Check trading system status"""
    print("\n2. CHECKING TRADING STATUS")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/live-trading/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Live Trading: {data.get('active', False)}")
            print(f"   [OK] User: {data.get('user', 'Unknown')}")
            print(f"   [OK] Enabled Globally: {data.get('enabled_globally', False)}")
            return data.get('active', False)
        else:
            print(f"   [ERROR] Trading status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Trading status error: {str(e)}")
        return False

def check_database_integrity():
    """Check database integrity"""
    print("\n3. CHECKING DATABASE INTEGRITY")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("prometheus_trading.db")
        cursor = conn.cursor()
        
        # Check positions table
        cursor.execute("SELECT COUNT(*) FROM positions")
        position_count = cursor.fetchone()[0]
        print(f"   [OK] Positions table: {position_count} records")
        
        # Check trades table
        cursor.execute("SELECT COUNT(*) FROM trades")
        trade_count = cursor.fetchone()[0]
        print(f"   [OK] Trades table: {trade_count} records")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(positions)")
        position_columns = [row[1] for row in cursor.fetchall()]
        print(f"   [OK] Positions columns: {position_columns}")
        
        cursor.execute("PRAGMA table_info(trades)")
        trade_columns = [row[1] for row in cursor.fetchall()]
        print(f"   [OK] Trades columns: {trade_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   [ERROR] Database error: {str(e)}")
        return False

def check_api_endpoints():
    """Check all API endpoints"""
    print("\n4. CHECKING API ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        ("/api/portfolio/positions", "GET", "Portfolio positions"),
        ("/api/portfolio/value", "GET", "Portfolio value"),
        ("/api/portfolio/balance", "GET", "Account balance"),
        ("/api/trading/positions", "GET", "Trading positions"),
        ("/api/trading/history", "GET", "Trading history"),
        ("/api/trading/active", "GET", "Active trades"),
        ("/api/system/performance-metrics", "GET", "Performance metrics")
    ]
    
    working_endpoints = 0
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://localhost:8000{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"   [OK] {description}: {endpoint}")
                working_endpoints += 1
            else:
                print(f"   [ERROR] {description}: {endpoint} ({response.status_code})")
        except Exception as e:
            print(f"   [ERROR] {description}: {endpoint} - {str(e)}")
    
    return working_endpoints >= 5

def check_ai_functionality():
    """Check AI functionality"""
    print("\n5. CHECKING AI FUNCTIONALITY")
    print("=" * 50)
    
    test_prompts = [
        "Analyze AAPL for trading decision",
        "What is the market sentiment for TSLA?",
        "Should I buy or sell NVDA?"
    ]
    
    ai_working = 0
    
    for prompt in test_prompts:
        try:
            # Test GPT-OSS 20B
            response = requests.post(
                "http://localhost:5000/generate",
                json={"prompt": prompt, "max_tokens": 100},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('generated_text', '')
                print(f"   [OK] GPT-OSS 20B: {response_text[:50]}...")
                ai_working += 1
            else:
                print(f"   [ERROR] GPT-OSS 20B failed: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] GPT-OSS 20B error: {str(e)}")
    
    return ai_working >= 2

def check_trading_execution():
    """Check trading execution capability"""
    print("\n6. CHECKING TRADING EXECUTION")
    print("=" * 50)
    
    try:
        # Test trade execution
        response = requests.post(
            "http://localhost:8000/api/trading/execute",
            json={
                "symbol": "TEST",
                "side": "buy",
                "quantity": 1,
                "price": 100.0
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Trade execution: {data['message']}")
            
            # Check if trade was recorded
            time.sleep(1)
            history_response = requests.get("http://localhost:8000/api/trading/history", timeout=5)
            if history_response.status_code == 200:
                history_data = history_response.json()
                trades = history_data.get('trades', [])
                test_trades = [t for t in trades if t['symbol'] == 'TEST']
                if test_trades:
                    print(f"   [OK] Trade recorded: {len(test_trades)} TEST trades found")
                    return True
                else:
                    print(f"   [WARNING] Trade not found in history")
                    return False
            else:
                print(f"   [ERROR] Could not verify trade history")
                return False
        else:
            print(f"   [ERROR] Trade execution failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Trading execution error: {str(e)}")
        return False

def check_portfolio_management():
    """Check portfolio management"""
    print("\n7. CHECKING PORTFOLIO MANAGEMENT")
    print("=" * 50)
    
    try:
        # Check positions
        response = requests.get("http://localhost:8000/api/portfolio/positions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            positions = data.get('positions', [])
            print(f"   [OK] Portfolio positions: {len(positions)} active")
            
            # Check portfolio value
            value_response = requests.get("http://localhost:8000/api/portfolio/value", timeout=5)
            if value_response.status_code == 200:
                value_data = value_response.json()
                print(f"   [OK] Portfolio value: ${value_data.get('total_value', 0):,.2f}")
                print(f"   [OK] Cash balance: ${value_data.get('cash_balance', 0):,.2f}")
                return True
            else:
                print(f"   [ERROR] Portfolio value failed: {value_response.status_code}")
                return False
        else:
            print(f"   [ERROR] Portfolio positions failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Portfolio management error: {str(e)}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n8. CHECKING SYSTEM RESOURCES")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/system/performance-metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] CPU Usage: {data.get('cpu_percent', 0):.1f}%")
            print(f"   [OK] Memory Usage: {data.get('memory_percent', 0):.1f}%")
            print(f"   [OK] Requests/min: {data.get('requests_per_minute', 0)}")
            print(f"   [OK] Errors/min: {data.get('errors_per_minute', 0)}")
            return True
        else:
            print(f"   [ERROR] Performance metrics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] System resources error: {str(e)}")
        return False

def main():
    """Main comprehensive check"""
    print("PROMETHEUS COMPREHENSIVE SYSTEM CHECK")
    print("=" * 60)
    print(f"Check started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all checks
    checks = [
        ("Server Health", check_server_health),
        ("Trading Status", check_trading_status),
        ("Database Integrity", check_database_integrity),
        ("API Endpoints", check_api_endpoints),
        ("AI Functionality", check_ai_functionality),
        ("Trading Execution", check_trading_execution),
        ("Portfolio Management", check_portfolio_management),
        ("System Resources", check_system_resources)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
        except Exception as e:
            print(f"   [ERROR] {check_name} check failed: {str(e)}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE CHECK SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"Checks Passed: {passed}/{total}")
    print()
    
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"   {status}: {check_name}")
    
    print()
    
    if passed == total:
        print("🎯 ALL SYSTEMS OPERATIONAL!")
        print("Prometheus is fully functional and ready for live trading.")
    elif passed >= total * 0.8:
        print("[WARNING]️ MOSTLY OPERATIONAL")
        print("Most systems working, minor issues detected.")
    else:
        print("[ERROR] MULTIPLE ISSUES DETECTED")
        print("Several systems need attention before live trading.")
    
    print(f"\nCheck completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed == total

if __name__ == "__main__":
    success = main()
    print(f"\nFINAL RESULT: {'SYSTEM READY' if success else 'NEEDS ATTENTION'}")










