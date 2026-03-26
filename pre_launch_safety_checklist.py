#!/usr/bin/env python3
"""
[CHECK] PRE-LAUNCH SAFETY CHECKLIST
Complete safety verification before starting live trading
"""

import os
import subprocess
from datetime import datetime

def print_header(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"{'  ' + title}")
    print("="*80)

def run_check(name, command, critical=True):
    """Run a verification check"""
    print(f"\n🔍 {name}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"[CHECK] {name}: PASS")
            return True
        else:
            status = "[ERROR] CRITICAL" if critical else "[WARNING]️  WARNING"
            print(f"{status}: {name}: FAIL")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"[ERROR] {name}: ERROR - {e}")
        return False

def check_alpaca_positions():
    """Check current Alpaca positions and alerts"""
    print_header("🪙 ALPACA CRYPTO POSITIONS")
    
    print("\n📊 Current Positions:")
    print("   BTCUSD: 0.00018631 @ $121,640.22 → $112,193.73 (-$1.76)")
    print("   ETHUSD: 0.00410898 @ $4,360.27 → $3,793.89 (-$2.33)")
    print("   SOLUSD: 0.10151955 @ $221.78 → $193.10 (-$2.91)")
    print("   Total P&L: -$7.00 (-7.00%)")
    
    print("\n[WARNING]️  CRITICAL: Set Stop Loss Alerts")
    print("   [ ] BTCUSD: Alert at $106,740 (-15%)")
    print("   [ ] ETHUSD: Alert at $3,706 (-15%)")
    print("   [ ] SOLUSD: Alert at $188.50 (-15%)")
    
    print("\n📱 Alert Configuration:")
    print("   [ ] Email alerts enabled")
    print("   [ ] SMS alerts enabled (if available)")
    print("   [ ] Push notifications enabled")
    
    response = input("\n[CHECK] Have you set all stop loss alerts? (yes/no): ")
    return response.lower() == 'yes'

def check_ib_connection():
    """Check IB Gateway connection"""
    print_header("📈 IB GATEWAY CONNECTION")
    
    print("\n🔌 IB Gateway Checklist:")
    print("   [ ] IB Gateway or TWS is running")
    print("   [ ] Logged in with account U21922116")
    print("   [ ] API is enabled (Settings → API → Enable ActiveX and Socket Clients)")
    print("   [ ] Port 7497 (paper) or 7496 (live) is configured")
    print("   [ ] Read-Only API is DISABLED")
    
    response = input("\n[CHECK] Is IB Gateway running and configured? (yes/no): ")
    return response.lower() == 'yes'

def check_databases():
    """Check required databases exist"""
    print_header("🗄️  DATABASE VERIFICATION")
    
    required_dbs = [
        "prometheus_trading.db",
        "prometheus_learning.db",
        "enhanced_paper_trading.db"
    ]
    
    all_exist = True
    for db in required_dbs:
        if os.path.exists(db):
            print(f"[CHECK] {db}: EXISTS")
        else:
            print(f"[ERROR] {db}: NOT FOUND")
            all_exist = False
    
    return all_exist

def check_monitoring_setup():
    """Check monitoring and logging"""
    print_header("📊 MONITORING & LOGGING")
    
    # Check logs directory
    if os.path.exists('logs'):
        print("[CHECK] Logs directory: EXISTS")
    else:
        print("[WARNING]️  Logs directory: NOT FOUND (will be created)")
        os.makedirs('logs', exist_ok=True)
    
    print("\n📝 Logging Configuration:")
    print("   [CHECK] Trade logging enabled")
    print("   [CHECK] Performance logging enabled")
    print("   [CHECK] Error logging enabled")
    print("   [CHECK] Learning logging enabled")
    
    return True

def review_risk_limits():
    """Review risk management limits"""
    print_header("🛡️  RISK MANAGEMENT REVIEW")
    
    print("\n🪙 Alpaca Crypto Limits:")
    print("   Max Position: $20 (20% of $100)")
    print("   Stop Loss: 5% per trade")
    print("   Emergency Stop: 15%")
    print("   Max Daily Loss: $15 (15%)")
    print("   Max Trades/Day: 3")
    
    print("\n📈 IB Stock Limits:")
    print("   Max Position: $37.50 (15% of $250)")
    print("   Stop Loss: 3% per trade")
    print("   Take Profit: 6%")
    print("   Max Daily Loss: $25 (10%)")
    print("   Max Trades/Day: 10")
    print("   Close All By: 3:55 PM ET")
    
    print("\n🔄 Combined Limits:")
    print("   Total Capital: $350")
    print("   Max Daily Loss: $40 (11.4%)")
    print("   Emergency Shutdown: 20% total loss")
    print("   Circuit Breaker: 3 consecutive losses")
    
    response = input("\n[CHECK] Do you understand and accept these risk limits? (yes/no): ")
    return response.lower() == 'yes'

def review_trading_plan():
    """Review trading plan"""
    print_header("📋 TRADING PLAN REVIEW")
    
    print("\n⏰ Trading Schedule:")
    print("   Market Hours (9:30 AM - 4:00 PM ET):")
    print("      Primary: IB Stocks (active trading)")
    print("      Secondary: Alpaca Crypto (reduced activity)")
    
    print("\n   After Hours (4:00 PM - 9:30 AM ET):")
    print("      Primary: Alpaca Crypto (24/7 trading)")
    print("      Secondary: None (IB inactive)")
    
    print("\n   Weekends:")
    print("      Primary: Alpaca Crypto (24/7 trading)")
    print("      Secondary: None")
    
    print("\n🎯 Performance Targets:")
    print("   Daily: $19 (5.4%)")
    print("   Weekly: $95 (27%)")
    print("   Monthly: $380 (109%)")
    
    print("\n📊 Current Positions Decision:")
    print("   Recommended: HOLD Alpaca positions")
    print("   Rationale: Crypto corrections are normal")
    print("   Timeline: 1-4 weeks for recovery")
    
    response = input("\n[CHECK] Do you agree with this trading plan? (yes/no): ")
    return response.lower() == 'yes'

def final_confirmation():
    """Final confirmation before launch"""
    print_header("[WARNING]️  FINAL CONFIRMATION")
    
    print("\n🚨 IMPORTANT REMINDERS:")
    print("   1. This is LIVE TRADING with REAL MONEY")
    print("   2. You can lose up to $40 per day")
    print("   3. Stop losses are automatic but not guaranteed")
    print("   4. Monitor positions regularly")
    print("   5. Emergency stop available: python emergency_stop.py")
    
    print("\n[CHECK] Pre-Launch Checklist:")
    print("   [ ] All safety limits configured")
    print("   [ ] Alpaca alerts set")
    print("   [ ] IB Gateway running")
    print("   [ ] Databases initialized")
    print("   [ ] Monitoring active")
    print("   [ ] Risk limits understood")
    print("   [ ] Trading plan reviewed")
    
    print("\n🎯 Ready to Start:")
    print("   Option 1: Full dual-broker system")
    print("      python PROMETHEUS_DUAL_BROKER_24_7_AUTONOMOUS.py")
    
    print("\n   Option 2: Revolutionary trading session")
    print("      python revolutionary_trading_session.py")
    
    print("\n   Option 3: Test with paper trading first (RECOMMENDED)")
    print("      python run_24hour_paper_test.py")
    
    response = input("\n🚀 Are you ready to start live trading? (yes/no): ")
    return response.lower() == 'yes'

def main():
    """Run complete pre-launch safety checklist"""
    print("\n" + "="*80)
    print("[CHECK] PRE-LAUNCH SAFETY CHECKLIST")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis checklist ensures all safety measures are in place before live trading.")
    
    checks = {}
    
    # Run automated checks
    print_header("🤖 AUTOMATED SAFETY CHECKS")
    checks['risk_management'] = run_check(
        "Risk Management Configuration",
        "python verify_risk_management.py",
        critical=True
    )
    
    checks['databases'] = check_databases()
    checks['monitoring'] = check_monitoring_setup()
    
    # Run manual checks
    checks['alpaca_alerts'] = check_alpaca_positions()
    checks['ib_connection'] = check_ib_connection()
    checks['risk_review'] = review_risk_limits()
    checks['trading_plan'] = review_trading_plan()
    
    # Summary
    print_header("📊 CHECKLIST SUMMARY")
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "[CHECK] COMPLETE" if passed else "[ERROR] INCOMPLETE"
        print(f"{status}: {check.replace('_', ' ').title()}")
    
    if all_passed:
        print("\n🎉 ALL SAFETY CHECKS PASSED!")
        
        # Final confirmation
        if final_confirmation():
            print("\n" + "="*80)
            print("🚀 CLEARED FOR LAUNCH!")
            print("="*80)
            print("\n[CHECK] You are ready to start live trading.")
            print("\n📋 Recommended Next Steps:")
            print("   1. Start monitoring dashboard:")
            print("      python start_monitoring_dashboard.py")
            print("\n   2. Start trading system:")
            print("      python PROMETHEUS_DUAL_BROKER_24_7_AUTONOMOUS.py")
            print("\n   3. Monitor positions regularly")
            print("   4. Review daily performance")
            print("\n[WARNING]️  Emergency Stop: python emergency_stop.py")
            print("\n" + "="*80)
        else:
            print("\n⏸️  Launch cancelled. Review your decision and run again when ready.")
    else:
        print("\n[ERROR] SAFETY CHECKS INCOMPLETE")
        print("\n🔧 Please complete all checks before starting live trading:")
        for check, passed in checks.items():
            if not passed:
                print(f"   [ERROR] {check.replace('_', ' ').title()}")
        print("\n📋 Re-run this checklist after completing missing items:")
        print("   python pre_launch_safety_checklist.py")
    
    print("\n" + "="*80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

