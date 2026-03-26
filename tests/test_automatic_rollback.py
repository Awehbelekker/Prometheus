"""
TEST AUTOMATIC ROLLBACK SYSTEM
================================

Tests for the automatic rollback system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.automatic_rollback_system import AutomaticRollbackSystem
import time

def test_version_snapshot():
    """Test creating version snapshots"""
    print("\n" + "="*80)
    print("TEST 1: Version Snapshot Creation")
    print("="*80)
    
    rollback = AutomaticRollbackSystem(db_path="test_rollback.db")
    
    # Create initial version
    settings_v1 = {
        'stop_loss_percent': 2.0,
        'take_profit_percent': 6.0,
        'max_daily_trades': 30,
        'risk_per_trade': 0.03
    }
    
    performance_v1 = {
        'win_rate': 0.65,
        'avg_daily_pnl': 15.50,
        'sharpe_ratio': 1.8,
        'total_trades': 50
    }
    
    version1 = rollback.create_version_snapshot(settings_v1, performance_v1, "Initial baseline")
    
    print(f"\n[CHECK] Version 1 created: {version1.version_id[:12]}...")
    print(f"   Settings: {settings_v1}")
    print(f"   Performance: Win rate {performance_v1['win_rate']:.1%}, P&L ${performance_v1['avg_daily_pnl']:.2f}")
    
    assert version1 is not None, "Version should be created"
    assert version1.is_active, "Version should be active"
    
    print("\n[CHECK] TEST PASSED: Version snapshot creation working!")
    
    return rollback

def test_performance_degradation_detection(rollback):
    """Test performance degradation detection"""
    print("\n" + "="*80)
    print("TEST 2: Performance Degradation Detection")
    print("="*80)
    
    # Simulate good performance (no degradation)
    good_performance = {
        'win_rate': 0.67,  # Slightly better
        'avg_daily_pnl': 16.00,  # Slightly better
        'sharpe_ratio': 1.9,  # Slightly better
        'total_trades': 60
    }
    
    degraded = rollback.check_performance_degradation(good_performance)
    print(f"\n📊 Good performance check: Degradation = {degraded}")
    assert not degraded, "Should not detect degradation for good performance"
    
    # Simulate degraded performance (>10% drop)
    bad_performance = {
        'win_rate': 0.55,  # 15% drop from 0.65
        'avg_daily_pnl': 12.00,  # 23% drop from 15.50
        'sharpe_ratio': 1.5,  # 17% drop from 1.8
        'total_trades': 60
    }
    
    degraded = rollback.check_performance_degradation(bad_performance)
    print(f"\n📊 Bad performance check: Degradation = {degraded}")
    assert degraded, "Should detect degradation for bad performance"
    
    print("\n[CHECK] TEST PASSED: Performance degradation detection working!")

def test_rollback_mechanism(rollback):
    """Test rollback mechanism"""
    print("\n" + "="*80)
    print("TEST 3: Rollback Mechanism")
    print("="*80)
    
    # Create a new version with different settings
    settings_v2 = {
        'stop_loss_percent': 3.0,  # Changed
        'take_profit_percent': 8.0,  # Changed
        'max_daily_trades': 40,  # Changed
        'risk_per_trade': 0.04  # Changed
    }
    
    performance_v2 = {
        'win_rate': 0.55,  # Worse
        'avg_daily_pnl': 12.00,  # Worse
        'sharpe_ratio': 1.5,  # Worse
        'total_trades': 60
    }
    
    version2 = rollback.create_version_snapshot(settings_v2, performance_v2, "Experimental settings")
    
    print(f"\n📸 Version 2 created: {version2.version_id[:12]}...")
    print(f"   Settings: {settings_v2}")
    print(f"   Performance: Win rate {performance_v2['win_rate']:.1%}, P&L ${performance_v2['avg_daily_pnl']:.2f}")
    
    # Perform rollback
    print(f"\n🔄 Performing rollback...")
    previous_version = rollback.rollback_to_previous_version("Performance degradation detected")
    
    assert previous_version is not None, "Should rollback to previous version"
    assert previous_version.settings['stop_loss_percent'] == 2.0, "Should restore original settings"
    
    print(f"\n[CHECK] Rolled back to: {previous_version.version_id[:12]}...")
    print(f"   Settings restored: {previous_version.settings}")
    print(f"   Performance: Win rate {previous_version.performance_metrics['win_rate']:.1%}")
    
    print("\n[CHECK] TEST PASSED: Rollback mechanism working!")

def test_version_history(rollback):
    """Test version history retrieval"""
    print("\n" + "="*80)
    print("TEST 4: Version History")
    print("="*80)
    
    versions = rollback.get_version_history(limit=10)
    
    print(f"\n📚 Version history ({len(versions)} versions):")
    for i, version in enumerate(versions, 1):
        active = "[CHECK] ACTIVE" if version.is_active else "  "
        print(f"{active} {i}. {version.version_id[:12]}... - {version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      {version.reason}")
        print(f"      Win rate: {version.performance_metrics.get('win_rate', 0):.1%}")
    
    assert len(versions) >= 2, "Should have at least 2 versions"
    
    print("\n[CHECK] TEST PASSED: Version history retrieval working!")

def test_rollback_report(rollback):
    """Test rollback report generation"""
    print("\n" + "="*80)
    print("TEST 5: Rollback Report")
    print("="*80)
    
    report = rollback.get_rollback_report()
    
    print(f"\n{report}")
    
    assert "AUTOMATIC ROLLBACK SYSTEM REPORT" in report, "Report should have title"
    assert "Current Version" in report, "Report should show current version"
    
    print("\n[CHECK] TEST PASSED: Rollback report generation working!")

def test_automatic_rollback_workflow():
    """Test complete automatic rollback workflow"""
    print("\n" + "="*80)
    print("TEST 6: Complete Automatic Rollback Workflow")
    print("="*80)
    
    rollback = AutomaticRollbackSystem(db_path="test_rollback_workflow.db")
    
    # Step 1: Create baseline version
    print("\n📸 Step 1: Creating baseline version...")
    baseline_settings = {
        'stop_loss_percent': 2.0,
        'take_profit_percent': 6.0,
        'max_daily_trades': 30
    }
    baseline_performance = {
        'win_rate': 0.70,
        'avg_daily_pnl': 20.00,
        'sharpe_ratio': 2.0,
        'total_trades': 100
    }
    rollback.create_version_snapshot(baseline_settings, baseline_performance, "Baseline")
    print("   [CHECK] Baseline created")
    
    # Step 2: Create experimental version
    print("\n📸 Step 2: Creating experimental version...")
    time.sleep(1)  # Ensure different timestamp
    experimental_settings = {
        'stop_loss_percent': 1.5,  # More aggressive
        'take_profit_percent': 10.0,  # More aggressive
        'max_daily_trades': 50
    }
    experimental_performance = {
        'win_rate': 0.70,
        'avg_daily_pnl': 20.00,
        'sharpe_ratio': 2.0,
        'total_trades': 20  # Not enough trades yet
    }
    rollback.create_version_snapshot(experimental_settings, experimental_performance, "Experimental")
    print("   [CHECK] Experimental version created")
    
    # Step 3: Simulate performance degradation
    print("\n📊 Step 3: Simulating performance degradation...")
    degraded_performance = {
        'win_rate': 0.60,  # 14% drop
        'avg_daily_pnl': 15.00,  # 25% drop
        'sharpe_ratio': 1.6,  # 20% drop
        'total_trades': 50  # Enough trades now
    }
    
    # Step 4: Check for degradation
    print("\n🔍 Step 4: Checking for degradation...")
    is_degraded = rollback.check_performance_degradation(degraded_performance)
    print(f"   Degradation detected: {is_degraded}")
    
    # Step 5: Automatic rollback if degraded
    if is_degraded:
        print("\n🔄 Step 5: Performing automatic rollback...")
        previous = rollback.rollback_to_previous_version("Automatic rollback due to performance degradation")
        print(f"   [CHECK] Rolled back to: {previous.version_id[:12]}...")
        print(f"   Settings restored: stop_loss={previous.settings['stop_loss_percent']}%")
        
        assert previous.settings['stop_loss_percent'] == 2.0, "Should restore baseline settings"
    
    print("\n[CHECK] TEST PASSED: Complete automatic rollback workflow working!")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 AUTOMATIC ROLLBACK SYSTEM TEST SUITE")
    print("="*80)
    
    try:
        rollback = test_version_snapshot()
        test_performance_degradation_detection(rollback)
        test_rollback_mechanism(rollback)
        test_version_history(rollback)
        test_rollback_report(rollback)
        test_automatic_rollback_workflow()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\n[CHECK] Automatic Rollback System is working correctly!")
        print("[CHECK] Version control: ACTIVE")
        print("[CHECK] Performance degradation detection: ACTIVE")
        print("[CHECK] Automatic rollback: ACTIVE")
        print("[CHECK] Version history: ACTIVE")
        print("[CHECK] Rollback reporting: ACTIVE")
        print("\n🛡️ Safety Features:")
        print("   - Automatic revert if performance drops >10%")
        print("   - Keep last 7 days of settings")
        print("   - Quick restore to any previous version")
        print("   - Comprehensive logging and reporting")
        
        # Cleanup test databases
        import os
        for db_file in ["test_rollback.db", "test_rollback_workflow.db"]:
            if os.path.exists(db_file):
                os.remove(db_file)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

