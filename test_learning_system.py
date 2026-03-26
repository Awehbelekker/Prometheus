"""
🧪 PROMETHEUS LEARNING SYSTEM TEST
Tests the learning system once we have closed trades
"""

import sqlite3
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

from prometheus_learning_engine import PrometheusLearningEngine

def check_database_status():
    """Check current state of database"""
    print("="*80)
    print("DATABASE STATUS CHECK")
    print("="*80)
    
    db = sqlite3.connect('prometheus_learning.db')
    cursor = db.cursor()
    
    # Check total trades
    cursor.execute("SELECT COUNT(*) FROM trade_history")
    total_trades = cursor.fetchone()[0]
    print(f"\n📊 Total Trades: {total_trades}")
    
    # Check pending vs closed
    cursor.execute("SELECT status, COUNT(*) FROM trade_history GROUP BY status")
    status_counts = cursor.fetchall()
    print(f"\n📈 Trade Status:")
    for status, count in status_counts:
        print(f"   {status}: {count}")
    
    # Check closed trades
    cursor.execute("""
        SELECT COUNT(*) FROM trade_history 
        WHERE status = 'closed' AND exit_price IS NOT NULL
    """)
    closed_with_exit = cursor.fetchone()[0]
    print(f"\n✅ Closed trades with exit price: {closed_with_exit}")
    
    # Check if we have any patterns
    cursor.execute("SELECT COUNT(*) FROM pattern_insights")
    pattern_count = cursor.fetchone()[0]
    print(f"🧠 Patterns identified: {pattern_count}")
    
    # Check optimizations
    cursor.execute("SELECT COUNT(*) FROM trade_optimization")
    optimization_count = cursor.fetchone()[0]
    print(f"📊 Trade optimizations: {optimization_count}")
    
    db.close()
    
    return closed_with_exit


def simulate_closed_trade_for_testing():
    """Simulate closing one trade for testing purposes"""
    print("\n" + "="*80)
    print("SIMULATING CLOSED TRADE FOR TESTING")
    print("="*80)
    
    db = sqlite3.connect('prometheus_learning.db')
    cursor = db.cursor()
    
    # Get one pending trade
    cursor.execute("""
        SELECT id, symbol, price, quantity, timestamp
        FROM trade_history
        WHERE status = 'pending'
        LIMIT 1
    """)
    
    trade = cursor.fetchone()
    
    if not trade:
        print("❌ No pending trades found")
        db.close()
        return False
    
    trade_id, symbol, entry_price, quantity, entry_time = trade
    
    # Simulate a profitable exit (5% profit)
    exit_price = entry_price * 1.05
    profit_loss = (exit_price - entry_price) * quantity
    exit_time = datetime.now().isoformat()
    
    # Update the trade to closed
    cursor.execute("""
        UPDATE trade_history
        SET status = 'closed',
            exit_price = ?,
            profit_loss = ?,
            exit_timestamp = ?,
            hold_duration_seconds = 3600
        WHERE id = ?
    """, (exit_price, profit_loss, exit_time, trade_id))
    
    db.commit()
    db.close()
    
    print(f"\n✅ Simulated closed trade:")
    print(f"   Trade ID: {trade_id}")
    print(f"   Symbol: {symbol}")
    print(f"   Entry: ${entry_price:.2f}")
    print(f"   Exit: ${exit_price:.2f}")
    print(f"   Profit: ${profit_loss:.2f} (+5.00%)")
    
    return True


def test_learning_engine():
    """Test the learning engine functionality"""
    print("\n" + "="*80)
    print("TESTING LEARNING ENGINE")
    print("="*80)
    
    engine = PrometheusLearningEngine()
    
    # Test 1: Pattern identification
    print("\n🧠 Test 1: Pattern Identification")
    print("-" * 80)
    patterns = engine.identify_successful_patterns(min_profit_pct=1.0)
    print(f"✅ Identified {len(patterns)} patterns")
    
    for pattern in patterns:
        print(f"\n   {pattern.pattern_type}:")
        print(f"      Success Rate: {pattern.success_rate:.1f}%")
        print(f"      Avg Profit: {pattern.avg_profit_pct:.2f}%")
        print(f"      Trades: {pattern.trade_count}")
    
    # Test 2: Trade optimization
    print("\n\n📊 Test 2: Trade Optimization Analysis")
    print("-" * 80)
    
    db = sqlite3.connect('prometheus_learning.db')
    cursor = db.cursor()
    cursor.execute("""
        SELECT id FROM trade_history 
        WHERE status = 'closed' AND exit_price IS NOT NULL
        LIMIT 1
    """)
    result = cursor.fetchone()
    db.close()
    
    if result:
        trade_id = result[0]
        print(f"Analyzing trade {trade_id}...")
        optimization = engine.analyze_trade_optimization(trade_id)
        
        if optimization:
            print(f"\n✅ Optimization Analysis:")
            print(f"   Symbol: {optimization.symbol}")
            print(f"   Actual Profit: {optimization.actual_profit_pct:+.2f}%")
            print(f"   Optimal Profit: {optimization.optimal_profit_pct:+.2f}%")
            print(f"   Missed Opportunity: {optimization.missed_opportunity_pct:.2f}%")
            print(f"   Exit Timing: {optimization.exit_timing}")
        else:
            print("⚠️ Could not analyze trade (no historical price data)")
    else:
        print("⚠️ No closed trades available for optimization analysis")
    
    # Test 3: Recommendations
    print("\n\n💡 Test 3: Learning Recommendations")
    print("-" * 80)
    recommendations = engine.get_learning_recommendations()
    
    if recommendations.get('action_items'):
        print("\n🎯 Action Items:")
        for i, item in enumerate(recommendations['action_items'], 1):
            print(f"   {i}. {item}")
    else:
        print("⚠️ No recommendations yet (need more closed trades)")


def main():
    """Main test function"""
    print("\n" + "="*80)
    print("🧪 PROMETHEUS LEARNING SYSTEM TEST")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database status
    closed_trades = check_database_status()
    
    if closed_trades == 0:
        print("\n" + "="*80)
        print("⚠️  NO CLOSED TRADES YET")
        print("="*80)
        print("\nThe learning system requires closed trades to analyze.")
        print("Currently all 400+ trades are in 'pending' status.")
        print("\nOptions:")
        print("  1. Wait for the advanced_trading_monitor.py to close positions")
        print("  2. Simulate a closed trade for testing (DEMO ONLY)")
        print("\nWould you like to simulate a closed trade for testing? (y/n)")
        
        choice = input("> ").strip().lower()
        if choice == 'y':
            if simulate_closed_trade_for_testing():
                print("\n✅ Proceeding with tests using simulated data...\n")
                test_learning_engine()
        else:
            print("\n✅ Check back after some positions close naturally!")
            print("   Run: python prometheus_learning_dashboard.py")
    else:
        print(f"\n✅ Found {closed_trades} closed trades - running tests!")
        test_learning_engine()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    print(f"\nNext steps:")
    print("  • Monitor is running and will close positions automatically")
    print("  • Once you have 10+ closed trades, run:")
    print("    python prometheus_learning_dashboard.py")
    print("  • Use option 7 to run full learning analysis")
    print("  • Review patterns and recommendations to improve trading")


if __name__ == '__main__':
    main()
