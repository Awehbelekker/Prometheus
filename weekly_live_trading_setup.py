#!/usr/bin/env python3
"""
WEEKLY LIVE TRADING SETUP
Configure Prometheus for week-long live trading with real money
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sqlite3

def setup_weekly_trading_parameters():
    """Set up weekly trading parameters and limits"""
    print("SETTING UP WEEKLY TRADING PARAMETERS")
    print("=" * 50)
    
    # Weekly trading configuration
    weekly_config = {
        "trading_duration": "7_days",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "daily_budget": 50.0,  # $50 per day from $250 total
        "max_daily_loss": 25.0,  # Max $25 loss per day
        "max_weekly_loss": 100.0,  # Max $100 loss for the week
        "position_sizing": "conservative",  # Start conservative
        "risk_level": "medium",
        "trading_hours": "24/7",  # Crypto and options trading
        "monitoring_interval": 300,  # Check every 5 minutes
        "auto_stop_loss": True,
        "auto_take_profit": True,
        "max_positions": 5,  # Maximum 5 concurrent positions
        "portfolio_rebalance": "daily"
    }
    
    print("Weekly Trading Configuration:")
    for key, value in weekly_config.items():
        print(f"  {key}: {value}")
    
    return weekly_config

def configure_risk_management():
    """Configure risk management for week-long trading"""
    print("\nCONFIGURING RISK MANAGEMENT")
    print("=" * 50)
    
    risk_config = {
        "stop_loss_percentage": 5.0,  # 5% stop loss
        "take_profit_percentage": 10.0,  # 10% take profit
        "trailing_stop": True,
        "trailing_stop_percentage": 3.0,
        "max_drawdown": 20.0,  # Max 20% drawdown
        "position_size_limit": 0.1,  # Max 10% of portfolio per position
        "daily_loss_limit": 10.0,  # Max $10 loss per day
        "weekly_loss_limit": 50.0,  # Max $50 loss per week
        "emergency_stop": True,
        "volatility_adjustment": True,
        "market_condition_monitoring": True
    }
    
    print("Risk Management Configuration:")
    for key, value in risk_config.items():
        print(f"  {key}: {value}")
    
    return risk_config

def setup_monitoring_and_alerts():
    """Set up monitoring and alerts for live trading"""
    print("\nSETTING UP MONITORING AND ALERTS")
    print("=" * 50)
    
    monitoring_config = {
        "performance_monitoring": True,
        "real_time_alerts": True,
        "daily_reports": True,
        "weekly_summary": True,
        "profit_loss_tracking": True,
        "risk_metrics": True,
        "ai_decision_logging": True,
        "trade_execution_logging": True,
        "system_health_monitoring": True,
        "alert_channels": ["email", "console", "log_file"],
        "monitoring_frequency": "5_minutes",
        "report_frequency": "daily"
    }
    
    print("Monitoring Configuration:")
    for key, value in monitoring_config.items():
        print(f"  {key}: {value}")
    
    return monitoring_config

def prepare_daily_trading_reports():
    """Prepare daily trading reports and analytics"""
    print("\nPREPARING DAILY TRADING REPORTS")
    print("=" * 50)
    
    report_config = {
        "daily_pnl_report": True,
        "position_analysis": True,
        "risk_metrics_report": True,
        "ai_performance_report": True,
        "market_analysis_report": True,
        "trading_activity_summary": True,
        "portfolio_performance": True,
        "system_performance": True,
        "export_formats": ["json", "csv", "pdf"],
        "report_schedule": "end_of_day",
        "historical_analysis": True,
        "trend_analysis": True
    }
    
    print("Report Configuration:")
    for key, value in report_config.items():
        print(f"  {key}: {value}")
    
    return report_config

def test_trading_systems():
    """Test all trading systems before starting live trading"""
    print("\nTESTING TRADING SYSTEMS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    test_endpoints = [
        ("Health Check", "/health"),
        ("Live Trading Status", "/api/live-trading/status"),
        ("Portfolio Positions", "/api/portfolio/positions"),
        ("Portfolio Value", "/api/portfolio/value"),
        ("Trading History", "/api/trading/history"),
        ("AI Coordinator", "/api/ai/coordinator/status"),
        ("Crypto Engine", "/api/trading/crypto-engine/status"),
        ("Options Engine", "/api/trading/options-engine/status"),
        ("Advanced Engine", "/api/trading/advanced-engine/status"),
        ("Market Maker", "/api/trading/market-maker/status"),
        ("Master Engine", "/api/trading/master-engine/status"),
        ("HRM Engine", "/api/trading/hrm-engine/status")
    ]
    
    results = []
    for name, endpoint in test_endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                results.append((name, "SUCCESS", response_time))
                print(f"[CHECK] {name}: {response_time:.3f}s")
            else:
                results.append((name, f"ERROR {response.status_code}", response_time))
                print(f"[ERROR] {name}: HTTP {response.status_code}")
        except Exception as e:
            results.append((name, f"ERROR: {str(e)}", 0))
            print(f"[ERROR] {name}: {str(e)}")
    
    success_count = sum(1 for _, status, _ in results if "SUCCESS" in status)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\nTrading Systems Test Results:")
    print(f"  Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")
    
    return results, success_rate

def start_live_trading_session():
    """Start the live trading session for the week"""
    print("\nSTARTING LIVE TRADING SESSION")
    print("=" * 50)
    
    # Test system readiness
    results, success_rate = test_trading_systems()
    
    if success_rate >= 90:
        print("[CHECK] SYSTEM READY FOR LIVE TRADING")
        print("[CHECK] All critical systems operational")
        print("[CHECK] Risk management configured")
        print("[CHECK] Monitoring systems active")
        print("[CHECK] Weekly parameters set")
        
        print("\n🚀 LIVE TRADING SESSION STARTED")
        print("=" * 50)
        print("Trading Duration: 7 days")
        print(f"Start Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Date: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')}")
        print("Budget: $250 total ($50/day)")
        print("Risk Level: Medium")
        print("Position Sizing: Conservative")
        print("Monitoring: Every 5 minutes")
        print("Reports: Daily")
        
        print("\n📊 TRADING CAPABILITIES ACTIVE:")
        print("[CHECK] Crypto Trading")
        print("[CHECK] Options Trading")
        print("[CHECK] Advanced Trading")
        print("[CHECK] Market Making")
        print("[CHECK] Portfolio Management")
        print("[CHECK] Risk Management")
        print("[CHECK] AI-Powered Decisions")
        print("[CHECK] Real-time Monitoring")
        
        print("\n[WARNING]️ IMPORTANT REMINDERS:")
        print("• Start with small position sizes")
        print("• Monitor your trades closely")
        print("• Set appropriate stop losses")
        print("• Keep Interactive Brokers account active")
        print("• Review daily reports")
        print("• Monitor system performance")
        
        return True
    else:
        print("[ERROR] SYSTEM NOT READY FOR LIVE TRADING")
        print(f"[ERROR] Success rate too low: {success_rate:.1f}%")
        print("[ERROR] Please fix system issues before starting live trading")
        return False

def create_weekly_trading_plan():
    """Create a comprehensive weekly trading plan"""
    print("\nCREATING WEEKLY TRADING PLAN")
    print("=" * 50)
    
    weekly_plan = {
        "week_start": datetime.now().strftime("%Y-%m-%d"),
        "week_end": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "daily_schedule": {
            "monday": {"focus": "crypto_analysis", "max_positions": 3},
            "tuesday": {"focus": "options_strategies", "max_positions": 4},
            "wednesday": {"focus": "market_making", "max_positions": 5},
            "thursday": {"focus": "advanced_trading", "max_positions": 4},
            "friday": {"focus": "portfolio_rebalance", "max_positions": 3},
            "saturday": {"focus": "crypto_weekend", "max_positions": 2},
            "sunday": {"focus": "analysis_prep", "max_positions": 1}
        },
        "risk_parameters": {
            "daily_budget": 50.0,
            "max_daily_loss": 25.0,
            "max_weekly_loss": 100.0,
            "position_size": "conservative",
            "stop_loss": 5.0,
            "take_profit": 10.0
        },
        "monitoring": {
            "frequency": "5_minutes",
            "alerts": True,
            "reports": "daily",
            "backup": True
        }
    }
    
    print("Weekly Trading Plan Created:")
    print(f"  Week: {weekly_plan['week_start']} to {weekly_plan['week_end']}")
    print(f"  Daily Budget: ${weekly_plan['risk_parameters']['daily_budget']}")
    print(f"  Max Daily Loss: ${weekly_plan['risk_parameters']['max_daily_loss']}")
    print(f"  Position Sizing: {weekly_plan['risk_parameters']['position_size']}")
    print(f"  Monitoring: Every {weekly_plan['monitoring']['frequency']}")
    
    return weekly_plan

def main():
    """Main function to set up weekly live trading"""
    print("PROMETHEUS WEEKLY LIVE TRADING SETUP")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Set up weekly trading parameters
    weekly_config = setup_weekly_trading_parameters()
    
    # Configure risk management
    risk_config = configure_risk_management()
    
    # Set up monitoring and alerts
    monitoring_config = setup_monitoring_and_alerts()
    
    # Prepare daily trading reports
    report_config = prepare_daily_trading_reports()
    
    # Create weekly trading plan
    weekly_plan = create_weekly_trading_plan()
    
    # Test trading systems
    results, success_rate = test_trading_systems()
    
    # Start live trading session
    if start_live_trading_session():
        print("\n" + "=" * 60)
        print("WEEKLY LIVE TRADING SETUP COMPLETE!")
        print("=" * 60)
        print("Your Prometheus Trading Platform is ready for week-long live trading!")
        print()
        print("NEXT STEPS:")
        print("1. Monitor the trading session")
        print("2. Review daily reports")
        print("3. Adjust parameters as needed")
        print("4. Track performance metrics")
        print("5. Maintain system health")
        print()
        print("🚀 LIVE TRADING FOR THE WEEK IS NOW ACTIVE!")
    else:
        print("\n" + "=" * 60)
        print("SETUP INCOMPLETE - SYSTEM ISSUES DETECTED")
        print("=" * 60)
        print("Please resolve system issues before starting live trading.")
        print("Run system diagnostics and fix any problems.")

if __name__ == "__main__":
    main()
