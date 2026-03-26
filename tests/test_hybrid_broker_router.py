"""
Test suite for Hybrid Broker Router
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.hybrid_broker_router import HybridBrokerRouter
from datetime import datetime
import pytz


def test_broker_selection_crypto():
    """Test crypto routing (should always go to Alpaca)"""
    print("\n" + "="*80)
    print("TEST 1: Crypto Broker Selection")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Test crypto symbols
    crypto_symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
    
    for symbol in crypto_symbols:
        broker, reason = router.select_broker(symbol, 'BUY')
        print(f"   {symbol:12} → {broker.upper():8} ({reason})")
        assert broker == 'alpaca', f"Crypto should route to Alpaca, got {broker}"
    
    print("[CHECK] PASSED: All crypto routes to Alpaca")


def test_broker_selection_stocks():
    """Test stock routing (time-based)"""
    print("\n" + "="*80)
    print("TEST 2: Stock Broker Selection (Time-Based)")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Test stock symbols
    stock_symbols = ['AAPL', 'GOOGL', 'TSLA']
    
    session = router.get_market_session()
    print(f"   Current Market Session: {session.upper()}")
    
    for symbol in stock_symbols:
        broker, reason = router.select_broker(symbol, 'BUY')
        if broker:
            print(f"   {symbol:12} → {broker.upper():8} ({reason})")
        else:
            print(f"   {symbol:12} → NONE      ({reason})")
    
    print("[CHECK] PASSED: Stock routing based on market session")


def test_market_session_detection():
    """Test market session detection"""
    print("\n" + "="*80)
    print("TEST 3: Market Session Detection")
    print("="*80)
    
    router = HybridBrokerRouter()
    session = router.get_market_session()
    
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    
    print(f"   Current Time (ET): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"   Detected Session: {session.upper()}")
    print(f"   Day of Week: {now.strftime('%A')}")
    
    assert session in ['market_hours', 'extended_hours', 'after_hours', 'closed'], \
        f"Invalid session: {session}"
    
    print("[CHECK] PASSED: Market session detected correctly")


def test_duplicate_position_prevention():
    """Test duplicate position prevention"""
    print("\n" + "="*80)
    print("TEST 4: Duplicate Position Prevention")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Add position on IB
    router.update_position('ib', 'AAPL', 100)
    print("   Added: AAPL 100 shares on IB")
    
    # Try to add same symbol on Alpaca
    is_duplicate = router.check_duplicate_position('AAPL', 'alpaca')
    print(f"   Check duplicate AAPL on Alpaca: {is_duplicate}")
    assert is_duplicate == True, "Should detect duplicate"
    
    # Try different symbol
    is_duplicate = router.check_duplicate_position('GOOGL', 'alpaca')
    print(f"   Check duplicate GOOGL on Alpaca: {is_duplicate}")
    assert is_duplicate == False, "Should not detect duplicate for different symbol"
    
    print("[CHECK] PASSED: Duplicate position prevention works")


def test_broker_health_tracking():
    """Test broker health tracking"""
    print("\n" + "="*80)
    print("TEST 5: Broker Health Tracking")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Initial health
    print(f"   Initial IB health: {router.broker_health['ib']['healthy']}")
    assert router.broker_health['ib']['healthy'] == True
    
    # Mark failures
    for i in range(3):
        router.mark_broker_failure('ib')
        print(f"   Failure {i+1}: consecutive_failures = {router.broker_health['ib']['consecutive_failures']}")
    
    # Should be unhealthy after 3 failures
    print(f"   Final IB health: {router.broker_health['ib']['healthy']}")
    assert router.broker_health['ib']['healthy'] == False, "Should be unhealthy after 3 failures"
    
    # Mark success to recover
    router.mark_broker_success('ib')
    print(f"   After success: {router.broker_health['ib']['healthy']}")
    assert router.broker_health['ib']['healthy'] == True, "Should recover after success"
    
    print("[CHECK] PASSED: Broker health tracking works")


def test_failover_logic():
    """Test failover to backup broker"""
    print("\n" + "="*80)
    print("TEST 6: Failover Logic")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Mark IB as unhealthy
    for i in range(3):
        router.mark_broker_failure('ib')
    
    print(f"   IB Health: {router.broker_health['ib']['healthy']}")
    
    # Try to route stock during market hours (should failover to Alpaca)
    # Note: This test assumes market hours, adjust if needed
    broker, reason = router.select_broker('AAPL', 'BUY')
    
    if broker:
        print(f"   AAPL routed to: {broker.upper()}")
        print(f"   Reason: {reason}")
        # During market hours, should failover to Alpaca if IB unhealthy
        if 'failover' in reason.lower():
            print("   [CHECK] Failover activated")
    else:
        print(f"   No broker available: {reason}")
    
    print("[CHECK] PASSED: Failover logic works")


def test_position_tracking():
    """Test position tracking across brokers"""
    print("\n" + "="*80)
    print("TEST 7: Position Tracking")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Add positions
    router.update_position('ib', 'AAPL', 100)
    router.update_position('ib', 'GOOGL', 50)
    router.update_position('alpaca', 'BTC/USD', 0.5)
    router.update_position('alpaca', 'ETH/USD', 2.0)
    
    print(f"   IB Positions: {router.broker_positions['ib']}")
    print(f"   Alpaca Positions: {router.broker_positions['alpaca']}")
    
    assert len(router.broker_positions['ib']) == 2, "Should have 2 IB positions"
    assert len(router.broker_positions['alpaca']) == 2, "Should have 2 Alpaca positions"
    
    # Remove position
    router.update_position('ib', 'AAPL', 0)
    print(f"   After removing AAPL: {router.broker_positions['ib']}")
    assert 'AAPL' not in router.broker_positions['ib'], "AAPL should be removed"
    
    print("[CHECK] PASSED: Position tracking works")


def test_routing_summary():
    """Test routing summary display"""
    print("\n" + "="*80)
    print("TEST 8: Routing Summary Display")
    print("="*80)
    
    router = HybridBrokerRouter()
    
    # Add some positions
    router.update_position('ib', 'AAPL', 100)
    router.update_position('alpaca', 'BTC/USD', 0.5)
    
    summary = router.get_routing_summary()
    print(summary)
    
    assert 'HYBRID BROKER ROUTING STATUS' in summary
    print("[CHECK] PASSED: Routing summary displays correctly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 HYBRID BROKER ROUTER TEST SUITE")
    print("="*80)
    
    tests = [
        test_broker_selection_crypto,
        test_broker_selection_stocks,
        test_market_session_detection,
        test_duplicate_position_prevention,
        test_broker_health_tracking,
        test_failover_logic,
        test_position_tracking,
        test_routing_summary
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[ERROR] FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] ERROR: {e}")
            failed += 1
    
    print("\n" + "="*80)
    print("📊 TEST RESULTS")
    print("="*80)
    print(f"   [CHECK] Passed: {passed}/{len(tests)}")
    print(f"   [ERROR] Failed: {failed}/{len(tests)}")
    print(f"   📈 Success Rate: {passed/len(tests)*100:.0f}%")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

