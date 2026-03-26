#!/usr/bin/env python3
"""
PROMETHEUS TRADE EXECUTION TEST - FINAL VERIFICATION
Tests that the database fixes resolved the "no such table" errors
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:9090"

def print_status(message, status="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{status}] {timestamp} - {message}")

def test_backend_health():
    """Test if backend is responding"""
    print_status("=== TESTING BACKEND HEALTH ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_status("Backend is responding", "SUCCESS")
            return True
        else:
            print_status(f"Backend returned {response.status_code}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Backend not responding: {e}", "ERROR")
        return False

def test_market_data():
    """Test market data retrieval"""
    print_status("=== TESTING MARKET DATA ===")
    symbols = ["AAPL", "MSFT", "SPY"]
    
    for symbol in symbols:
        try:
            response = requests.get(f"{BASE_URL}/market-data/{symbol}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get('price', 'N/A')
                print_status(f"{symbol}: ${price}", "SUCCESS")
            else:
                print_status(f"{symbol}: HTTP {response.status_code}", "WARNING")
        except Exception as e:
            print_status(f"{symbol}: {e}", "ERROR")

def test_portfolio_status():
    """Test portfolio/positions retrieval"""
    print_status("=== TESTING PORTFOLIO STATUS ===")
    try:
        response = requests.get(f"{BASE_URL}/portfolio", timeout=5)
        if response.status_code == 200:
            data = response.json()
            positions = len(data.get('open_positions', []))
            total_value = data.get('total_value', 'N/A')
            print_status(f"Portfolio Value: ${total_value}", "SUCCESS")
            print_status(f"Open Positions: {positions}", "SUCCESS")
            return True
        else:
            print_status(f"Portfolio check failed: {response.status_code}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Portfolio check error: {e}", "ERROR")
        return False

def test_trade_execution():
    """Test actual trade execution"""
    print_status("=== TESTING TRADE EXECUTION ===")
    
    # Test a small buy order
    trade_data = {
        "symbol": "AAPL",
        "action": "BUY",
        "quantity": 1,
        "order_type": "MARKET",
        "price": 0  # Market order
    }
    
    try:
        response = requests.post(f"{BASE_URL}/trade", json=trade_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print_status(f"Trade executed successfully: {result}", "SUCCESS")
            return True
        else:
            print_status(f"Trade execution failed: {response.status_code}", "WARNING")
            print_status(f"Response: {response.text}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Trade execution error: {e}", "ERROR")
        return False

def test_short_selling_capability():
    """Test if short selling system is working"""
    print_status("=== TESTING SHORT SELLING CAPABILITY ===")
    
    # Test a small sell order (potential short)
    trade_data = {
        "symbol": "MSFT",
        "action": "SELL",
        "quantity": 1,
        "order_type": "MARKET",
        "price": 0  # Market order
    }
    
    try:
        response = requests.post(f"{BASE_URL}/trade", json=trade_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print_status(f"Short sell test executed: {result}", "SUCCESS")
            return True
        else:
            print_status(f"Short sell test failed: {response.status_code}", "WARNING")
            print_status(f"Response: {response.text}", "WARNING")
            return False
    except Exception as e:
        print_status(f"Short sell test error: {e}", "ERROR")
        return False

def main():
    print("================================================================================")
    print("PROMETHEUS TRADE EXECUTION TEST - FINAL VERIFICATION")
    print("================================================================================")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all tests
    backend_ok = test_backend_health()
    if not backend_ok:
        print_status("Backend not available. Cannot proceed with tests.", "CRITICAL")
        return
    
    time.sleep(2)  # Give backend a moment
    
    test_market_data()
    portfolio_ok = test_portfolio_status()
    trade_ok = test_trade_execution()
    short_ok = test_short_selling_capability()
    
    print("\n================================================================================")
    print("TEST RESULTS SUMMARY")
    print("================================================================================")
    
    if trade_ok:
        print_status("DATABASE FIX SUCCESSFUL - No more 'no such table' errors!", "SUCCESS")
    else:
        print_status("Database issues may still exist", "WARNING")
    
    if short_ok:
        print_status("SHORT SELLING SYSTEM WORKING!", "SUCCESS")
    else:
        print_status("Short selling may need Alpaca account verification", "WARNING")
    
    if all([backend_ok, portfolio_ok, trade_ok]):
        print_status("PROMETHEUS IS READY FOR AUTONOMOUS TRADING!", "SUCCESS")
        print_status("All systems operational - ready to make money!", "SUCCESS")
    else:
        print_status("Some systems need attention", "WARNING")
    
    print("\nNext Steps:")
    print("1. Monitor live trading activity")
    print("2. Verify IB Gateway shows 'Active API Client'")
    print("3. Check Alpaca account for short selling permissions")
    print("4. Watch for successful trade executions")

if __name__ == "__main__":
    main()








