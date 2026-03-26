#!/usr/bin/env python3
"""
COMPREHENSIVE READINESS TEST FOR PROMETHEUS TRADING SYSTEM
Tests all critical components before live trading
"""

import asyncio
import sys
from datetime import datetime
from ib_insync import IB, Stock, MarketOrder

print("\n" + "=" * 80)
print("  🔍 COMPREHENSIVE READINESS TEST")
print("=" * 80)
print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test results
tests_passed = 0
tests_failed = 0
critical_failures = []

def test_result(test_name, passed, critical=False):
    global tests_passed, tests_failed, critical_failures
    if passed:
        tests_passed += 1
        print(f"[CHECK] {test_name}")
    else:
        tests_failed += 1
        print(f"[ERROR] {test_name}")
        if critical:
            critical_failures.append(test_name)

async def main():
    print("=" * 80)
    print("TEST 1: IB GATEWAY API CONNECTION")
    print("=" * 80)
    
    ib = None
    ib_connected = False
    
    try:
        ib = IB()
        print("🔌 Attempting to connect to IB Gateway on port 7496...")
        await ib.connectAsync('127.0.0.1', 7496, clientId=999, timeout=10)
        
        if ib.isConnected():
            ib_connected = True
            test_result("IB Gateway API connection successful", True, critical=True)
            
            # Get account info
            await asyncio.sleep(2)
            account_values = ib.accountValues()
            
            balance = None
            for av in account_values:
                if av.tag == 'NetLiquidation' and av.currency == 'USD':
                    balance = float(av.value)
                    print(f"   💰 Account Balance: ${balance:.2f}")
                    break
            
            if balance and balance >= 250:
                test_result(f"Account has sufficient funds (${balance:.2f})", True, critical=True)
            elif balance:
                test_result(f"Account balance too low (${balance:.2f} < $250)", False, critical=True)
            else:
                test_result("Could not verify account balance", False, critical=False)
                
        else:
            test_result("IB Gateway API connection failed", False, critical=True)
            
    except Exception as e:
        test_result(f"IB Gateway connection error: {e}", False, critical=True)
        print("\n[WARNING]️  CRITICAL: IB Gateway API is not enabled!")
        print("   Please enable API in IB Gateway:")
        print("   1. File → Global Configuration → API → Settings")
        print("   2. Check 'Enable ActiveX and Socket Clients'")
        print("   3. Set Socket port: 7496")
        print("   4. Add 127.0.0.1 to Trusted IP Addresses")
        print("   5. Restart IB Gateway\n")
    
    print("\n" + "=" * 80)
    print("TEST 2: CODE LOGIC VERIFICATION")
    print("=" * 80)
    
    # Test broker priority logic
    try:
        from PROMETHEUS_AI_POWERED_24_7_AUTONOMOUS import PrometheusAIPowered24x7TradingSystem
        
        test_result("Trading system module imports successfully", True, critical=True)
        
        # Check if IB execution code exists
        import inspect
        source = inspect.getsource(PrometheusAIPowered24x7TradingSystem.execute_trade)
        
        if 'broker == "ib"' in source:
            test_result("IB trade execution code path exists", True, critical=True)
        else:
            test_result("IB trade execution code path MISSING", False, critical=True)
        
        if 'broker == "alpaca"' in source:
            test_result("Alpaca trade execution code path exists", True, critical=False)
        else:
            test_result("Alpaca trade execution code path missing", False, critical=False)
            
    except Exception as e:
        test_result(f"Code verification error: {e}", False, critical=True)
    
    print("\n" + "=" * 80)
    print("TEST 3: CONFIGURATION VERIFICATION")
    print("=" * 80)
    
    # Check .env configuration
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        ib_account = os.getenv('IB_ACCOUNT')
        ib_port = os.getenv('IB_PORT')
        primary_broker = os.getenv('PRIMARY_BROKER')
        
        if ib_account == 'U21922116':
            test_result(f"IB Account configured correctly ({ib_account})", True, critical=True)
        else:
            test_result(f"IB Account incorrect ({ib_account})", False, critical=True)
        
        if ib_port == '7496':
            test_result(f"IB Port configured correctly ({ib_port})", True, critical=True)
        else:
            test_result(f"IB Port incorrect ({ib_port})", False, critical=True)
        
        if primary_broker == 'interactive_brokers':
            test_result(f"Primary broker set to IB", True, critical=True)
        else:
            test_result(f"Primary broker not set to IB ({primary_broker})", False, critical=False)
            
    except Exception as e:
        test_result(f"Configuration verification error: {e}", False, critical=False)
    
    print("\n" + "=" * 80)
    print("TEST 4: RISK MANAGEMENT SETTINGS")
    print("=" * 80)
    
    try:
        from core.hierarchical_agent_coordinator import PortfolioSupervisorAgent
        
        # Check risk appetite settings
        agent = PortfolioSupervisorAgent()
        
        # Simulate moderate market conditions
        global_intelligence = {
            'overall_sentiment': 0.2,
            'risk_level': 0.5,
            'opportunity_score': 0.6
        }
        
        result = await agent.analyze_global_strategy(global_intelligence)
        risk_appetite = result.get('risk_appetite', 0)
        
        if risk_appetite >= 0.55:
            test_result(f"Risk appetite reasonable ({risk_appetite:.2f} >= 0.55)", True, critical=False)
        else:
            test_result(f"Risk appetite too conservative ({risk_appetite:.2f} < 0.55)", False, critical=False)
            print("   [WARNING]️  System may filter all trades as 'too risky'")
            
    except Exception as e:
        test_result(f"Risk management verification error: {e}", False, critical=False)
    
    print("\n" + "=" * 80)
    print("TEST 5: AI SYSTEMS AVAILABILITY")
    print("=" * 80)
    
    try:
        # Test AI system imports
        from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
        test_result("Hierarchical Agent Coordinator available", True, critical=False)
        
        from core.real_world_data_orchestrator import RealWorldDataOrchestrator
        test_result("Real-World Data Orchestrator available", True, critical=False)
        
        from core.continuous_learning_engine import ContinuousLearningEngine
        test_result("Continuous Learning Engine available", True, critical=False)
        
    except Exception as e:
        test_result(f"AI systems verification error: {e}", False, critical=False)
    
    # Disconnect IB
    if ib and ib.isConnected():
        ib.disconnect()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n[CHECK] Tests Passed: {tests_passed}/{total_tests} ({pass_rate:.1f}%)")
    print(f"[ERROR] Tests Failed: {tests_failed}/{total_tests}")
    
    if critical_failures:
        print(f"\n🔴 CRITICAL FAILURES ({len(critical_failures)}):")
        for failure in critical_failures:
            print(f"   [ERROR] {failure}")
        print("\n[WARNING]️  SYSTEM NOT READY FOR TRADING")
        print("   Fix critical failures before proceeding!")
    else:
        print("\n🟢 ALL CRITICAL TESTS PASSED")
        if tests_failed > 0:
            print("   [WARNING]️  Some non-critical tests failed")
            print("   System can trade but may have reduced functionality")
        else:
            print("   [CHECK] SYSTEM FULLY READY FOR TRADING")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if not ib_connected:
        print("\n🔴 CRITICAL: Enable IB Gateway API")
        print("   1. Open IB Gateway")
        print("   2. Go to: File → Global Configuration → API → Settings")
        print("   3. Check 'Enable ActiveX and Socket Clients'")
        print("   4. Set Socket port: 7496")
        print("   5. Add 127.0.0.1 to Trusted IP Addresses")
        print("   6. Click OK and restart IB Gateway")
        print("   7. Run this test again")
    elif critical_failures:
        print("\n🔴 Fix critical failures listed above")
    else:
        print("\n[CHECK] System is ready!")
        print("   Next steps:")
        print("   1. Run paper trading test: python START_IB_ONLY_TRADING.py")
        print("   2. Verify at least 1 trade executes")
        print("   3. Switch to live trading")
    
    print("\n" + "=" * 80)
    
    return len(critical_failures) == 0

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

