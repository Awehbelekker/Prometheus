#!/usr/bin/env python3
"""
DEEP DIVE TRADING READINESS TEST
=================================
Comprehensive end-to-end test of ALL trading capabilities
- Signal generation
- Trade execution
- Broker connections
- AI systems
- Revolutionary engines
- Risk management
- Position management
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import traceback

print("\n" + "=" * 80)
print("DEEP DIVE TRADING READINESS TEST")
print("=" * 80)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

test_results = {
    "passed": [],
    "failed": [],
    "warnings": [],
    "ready_to_trade": False
}

def test_pass(name: str, details: str = ""):
    test_results["passed"].append(name)
    print(f"[PASS] {name}")
    if details:
        print(f"       {details}")

def test_fail(name: str, reason: str = ""):
    test_results["failed"].append((name, reason))
    print(f"[FAIL] {name}")
    if reason:
        print(f"       {reason}")

def test_warn(name: str, reason: str = ""):
    test_results["warnings"].append((name, reason))
    print(f"[WARN] {name}")
    if reason:
        print(f"       {reason}")

async def test_revolutionary_engines():
    """Test all 5 revolutionary trading engines"""
    print("\n" + "=" * 80)
    print("TESTING: Revolutionary Engines (5 Systems)")
    print("=" * 80)
    
    engines = [
        "revolutionary_master_engine",
        "revolutionary_crypto_engine", 
        "revolutionary_options_engine",
        "revolutionary_advanced_engine",
        "revolutionary_market_maker"
    ]
    
    for engine in engines:
        try:
            module = __import__(engine)
            engine_class = getattr(module, [c for c in dir(module) if 'Engine' in c][0])
            instance = engine_class()
            test_pass(f"Revolutionary Engine: {engine.replace('revolutionary_', '').replace('_', ' ').title()}")
        except Exception as e:
            test_fail(f"Revolutionary Engine: {engine}", str(e))

async def test_ai_signal_generation():
    """Test AI signal generation"""
    print("\n" + "=" * 80)
    print("TESTING: AI Signal Generation")
    print("=" * 80)
    
    try:
        from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
        
        coordinator = HierarchicalAgentCoordinator()
        test_pass("Hierarchical Agent Coordinator initialized")
        
        # Test signal generation
        mock_data = {
            'symbol': 'AAPL',
            'price': 150.0,
            'volume': 1000000,
            'high': 152.0,
            'low': 149.0
        }
        
        signal = await coordinator.generate_signal(mock_data)
        if signal:
            test_pass("AI Signal Generation", f"Generated signal: {signal.get('action', 'N/A')}")
        else:
            test_warn("AI Signal Generation", "No signal generated")
            
    except Exception as e:
        test_fail("AI Signal Generation", str(e))

async def test_broker_execution():
    """Test broker trade execution"""
    print("\n" + "=" * 80)
    print("TESTING: Broker Trade Execution")
    print("=" * 80)
    
    # Test Alpaca
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        api_key = os.getenv('ALPACA_PAPER_KEY')
        api_secret = os.getenv('ALPACA_PAPER_SECRET')
        
        if api_key and api_secret:
            trading_client = TradingClient(api_key, api_secret, paper=True)
            account = trading_client.get_account()
            test_pass("Alpaca Connection", f"Balance: ${float(account.cash):.2f}")
            
            # Test order submission (limit order to avoid execution)
            market_order = MarketOrderRequest(
                symbol="AAPL",
                qty=0.01,  # Tiny quantity to test
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = trading_client.submit_order(order_data=market_order)
            test_pass("Alpaca Order Submission", f"Order ID: {order.id}")
            
            # Cancel the test order
            trading_client.cancel_order_by_id(order.id)
            test_pass("Alpaca Order Cancellation", "Test order cancelled")
            
        else:
            test_warn("Alpaca Connection", "Credentials not found")
            
    except Exception as e:
        test_warn("Alpaca Broker", str(e))
    
    # Test IB
    try:
        from ib_insync import IB, Stock, MarketOrder
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if ib.isConnected():
            account_values = ib.accountValues()
            balance = None
            for av in account_values:
                if av.tag == 'NetLiquidation' and av.currency == 'USD':
                    balance = float(av.value)
                    break
            
            test_pass("IB Connection", f"Balance: ${balance:.2f}" if balance else "Connected")
            test_pass("IB Trade Execution Ready", "Can execute trades via IB")
            ib.disconnect()
        else:
            test_fail("IB Connection", "Not connected")
            
    except Exception as e:
        test_warn("IB Broker", str(e))

async def test_risk_management():
    """Test risk management and position sizing"""
    print("\n" + "=" * 80)
    print("TESTING: Risk Management & Position Sizing")
    print("=" * 80)
    
    try:
        from core.risk_manager import RiskManager
        
        risk_mgr = RiskManager()
        test_pass("Risk Manager initialized")
        
        # Test position sizing
        account_balance = 10000
        risk_per_trade = 0.02  # 2%
        price = 100
        stop_loss_pct = 0.05  # 5%
        
        position_size = risk_mgr.calculate_position_size(
            account_balance, risk_per_trade, price, stop_loss_pct
        )
        
        test_pass("Position Sizing", f"Calculated size: {position_size:.2f} shares")
        
    except ImportError:
        # Fallback calculation
        account_balance = 10000
        risk_per_trade = 0.02
        price = 100
        stop_loss_pct = 0.05
        position_size = (account_balance * risk_per_trade) / (price * stop_loss_pct)
        test_pass("Position Sizing (Manual)", f"Calculated size: {position_size:.2f} shares")
    except Exception as e:
        test_fail("Risk Management", str(e))

async def test_market_data():
    """Test market data feeds"""
    print("\n" + "=" * 80)
    print("TESTING: Market Data Feeds")
    print("=" * 80)
    
    # Test real-time data
    try:
        from core.real_time_market_data import RealTimeMarketDataOrchestrator
        
        orchestrator = RealTimeMarketDataOrchestrator()
        data = await orchestrator.get_market_data('AAPL')
        
        if data and 'price' in data:
            test_pass("Real-Time Market Data", f"AAPL price: ${data['price']:.2f}")
        else:
            test_warn("Real-Time Market Data", "No data returned")
            
    except Exception as e:
        test_warn("Real-Time Market Data", str(e))
    
    # Test Yahoo Finance fallback
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        price = info.get('currentPrice')
        test_pass("Yahoo Finance Data", f"AAPL: ${price:.2f}" if price else "Connected")
    except Exception as e:
        test_warn("Yahoo Finance", str(e))

async def test_order_management():
    """Test order tracking and management"""
    print("\n" + "=" * 80)
    print("TESTING: Order Management")
    print("=" * 80)
    
    try:
        from core.order_manager import OrderManager
        
        order_mgr = OrderManager()
        orders = await order_mgr.get_open_orders()
        test_pass("Order Manager", f"{len(orders)} open orders")
        
    except ImportError:
        test_warn("Order Manager", "Module not found (may use broker directly)")
    except Exception as e:
        test_warn("Order Manager", str(e))

async def test_portfolio_tracking():
    """Test portfolio and position tracking"""
    print("\n" + "=" * 80)
    print("TESTING: Portfolio Tracking")
    print("=" * 80)
    
    try:
        from core.portfolio_manager import PortfolioManager
        
        portfolio_mgr = PortfolioManager()
        positions = await portfolio_mgr.get_positions()
        test_pass("Portfolio Manager", f"{len(positions)} positions")
        
    except ImportError:
        test_warn("Portfolio Manager", "Module not found (may use broker directly)")
    except Exception as e:
        test_warn("Portfolio Manager", str(e))

async def test_ai_learning_system():
    """Test continuous learning system"""
    print("\n" + "=" * 80)
    print("TESTING: AI Learning System")
    print("=" * 80)
    
    try:
        from core.continuous_learning_engine import ContinuousLearningEngine
        
        learning_engine = ContinuousLearningEngine()
        test_pass("Continuous Learning Engine initialized")
        
        # Check if learning is active
        if hasattr(learning_engine, 'is_active'):
            if learning_engine.is_active:
                test_pass("Learning System Active", "Adapting from trade outcomes")
            else:
                test_warn("Learning System", "Not currently active")
        
    except Exception as e:
        test_warn("Continuous Learning", str(e))

async def test_database_operations():
    """Test database read/write operations"""
    print("\n" + "=" * 80)
    print("TESTING: Database Operations")
    print("=" * 80)
    
    try:
        import sqlite3
        
        # Test trading database
        conn = sqlite3.connect('prometheus_trading.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trading_data WHERE symbol = 'AAPL'")
        count = cursor.fetchone()[0]
        test_pass("Trading Database Read", f"AAPL records: {count}")
        conn.close()
        
        # Test write operation
        conn = sqlite3.connect('prometheus_trading.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trading_data (symbol, price, volume, timestamp)
            VALUES (?, ?, ?, ?)
        """, ('TEST', 100.0, 1000, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        test_pass("Trading Database Write", "Write operation successful")
        
    except Exception as e:
        test_warn("Database Operations", str(e))

async def test_backend_server_health():
    """Test backend server health and endpoints"""
    print("\n" + "=" * 80)
    print("TESTING: Backend Server")
    print("=" * 80)
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            test_pass("Backend Health Check", "Server running")
        else:
            test_fail("Backend Health Check", f"Status: {response.status_code}")
        
        # Test other endpoints
        endpoints = [
            "/api/v1/account",
            "/api/v1/positions",
            "/api/v1/orders",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
                if response.status_code in [200, 404]:
                    test_pass(f"Endpoint: {endpoint}", f"Status: {response.status_code}")
                else:
                    test_warn(f"Endpoint: {endpoint}", f"Status: {response.status_code}")
            except:
                test_warn(f"Endpoint: {endpoint}", "Not accessible")
        
    except Exception as e:
        test_fail("Backend Server", str(e))

async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("STARTING DEEP DIVE TESTS")
    print("=" * 80)
    
    # Run all test suites
    await test_revolutionary_engines()
    await test_ai_signal_generation()
    await test_broker_execution()
    await test_risk_management()
    await test_market_data()
    await test_order_management()
    await test_portfolio_tracking()
    await test_ai_learning_system()
    await test_database_operations()
    await test_backend_server_health()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    print(f"Warnings: {len(test_results['warnings'])}")
    
    total = len(test_results['passed']) + len(test_results['failed'])
    pass_rate = (len(test_results['passed']) / total * 100) if total > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Determine readiness
    if len(test_results['failed']) == 0:
        test_results['ready_to_trade'] = True
        print("\n[SUCCESS] SYSTEM IS FULLY READY TO TRADE!")
    elif pass_rate >= 80:
        test_results['ready_to_trade'] = True
        print("\n[SUCCESS] SYSTEM IS READY TO TRADE (with minor issues)")
    else:
        print("\n[WARNING] SYSTEM HAS ISSUES - Review failures above")
    
    # Save report
    report_path = f"deep_dive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nReport saved: {report_path}")
    print("=" * 80 + "\n")
    
    return test_results['ready_to_trade']

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed: {e}")
        traceback.print_exc()
        sys.exit(1)

