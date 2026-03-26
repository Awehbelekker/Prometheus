#!/usr/bin/env python3
"""
ENABLE LIVE TRADING CONFIGURATION
Update server configuration to enable live trading
"""

import os
import json
from datetime import datetime

def update_live_trading_config():
    """Update the live trading configuration to enable live trading"""
    print("UPDATING LIVE TRADING CONFIGURATION")
    print("=" * 50)
    
    # Update environment variables
    os.environ['LIVE_TRADING_ENABLED'] = 'true'
    os.environ['PAPER_TRADING_ONLY'] = 'false'
    os.environ['ENABLE_LIVE_ORDER_EXECUTION'] = 'true'
    os.environ['TRADING_MODE'] = 'live'
    
    print("   [SUCCESS] Environment variables updated")
    print(f"   LIVE_TRADING_ENABLED: {os.environ.get('LIVE_TRADING_ENABLED', 'false')}")
    print(f"   PAPER_TRADING_ONLY: {os.environ.get('PAPER_TRADING_ONLY', 'true')}")
    print(f"   ENABLE_LIVE_ORDER_EXECUTION: {os.environ.get('ENABLE_LIVE_ORDER_EXECUTION', 'false')}")
    print(f"   TRADING_MODE: {os.environ.get('TRADING_MODE', 'paper')}")

def create_live_trading_env():
    """Create a .env file with live trading enabled"""
    print("\nCREATING LIVE TRADING ENVIRONMENT FILE")
    print("=" * 50)
    
    env_content = f"""# PROMETHEUS LIVE TRADING CONFIGURATION
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# LIVE TRADING ACTIVATION
LIVE_TRADING_ENABLED=true
PAPER_TRADING_ONLY=false
ENABLE_LIVE_ORDER_EXECUTION=true
TRADING_MODE=live

# CONSERVATIVE RISK MANAGEMENT
MAX_POSITION_SIZE_PERCENT=1.0
MAX_DAILY_TRADES=5
MAX_PORTFOLIO_RISK_PERCENT=0.5
DEFAULT_STOP_LOSS_PERCENT=2.0
EMERGENCY_STOP_LOSS_PERCENT=5.0
MAX_DRAWDOWN_PERCENT=10.0

# DAILY LIMITS
MAX_DAILY_LOSS_DOLLARS=200.00
MAX_DAILY_TRADES_PER_SYMBOL=2
MAX_TOTAL_EXPOSURE_PERCENT=25.0

# SAFETY CONTROLS
ENABLE_CIRCUIT_BREAKERS=true
CIRCUIT_BREAKER_LOSS_PERCENT=2.0
TRADE_ONLY_MARKET_HOURS=true
AVOID_FIRST_15_MINUTES=true
AVOID_LAST_15_MINUTES=true

# INITIAL TESTING SETTINGS
TESTING_MODE=true
DRY_RUN_MODE=false
REQUIRE_MANUAL_APPROVAL=false
TEST_CAPITAL_DOLLARS=250.00

# MONITORING & ALERTS
ENABLE_REAL_TIME_MONITORING=true
MONITORING_INTERVAL_SECONDS=30
ENABLE_METRICS=true
LOG_LEVEL=INFO

# TRADING STRATEGIES
ENABLE_ADVANCED_ENGINE=true
ENABLE_CRYPTO_ENGINE=false
ENABLE_OPTIONS_ENGINE=false
ENABLE_MARKET_MAKER=false

# ALLOWED SYMBOLS (Conservative list)
ALLOWED_SYMBOLS=SPY,QQQ,AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA

# COMPLIANCE & LOGGING
ENABLE_TRADE_SURVEILLANCE=true
ENABLE_AUDIT_LOGGING=true
LOG_ALL_DECISIONS=true
TRADE_DATA_RETENTION_DAYS=2555

# AUTHENTICATION & SECURITY
JWT_SECRET_KEY=prometheus-live-trading-secret-key-2025
ENTERPRISE_MODE=true
MFA_ENABLED=false
AUDIT_LOGGING_ENABLED=true

# DATABASE
DATABASE_URL=sqlite:///prometheus_trading.db
AUTO_MIGRATE=true

# FRONTEND
ENABLE_FRONTEND=true
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=production
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   [SUCCESS] .env file created with live trading enabled")
        return True
    except Exception as e:
        print(f"   [ERROR] Failed to create .env file: {str(e)}")
        return False

def update_config_file():
    """Update the live trading config file"""
    print("\nUPDATING CONFIG FILE")
    print("=" * 50)
    
    config_file = "config/live_trading_config.py"
    
    try:
        # Read the current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace the key settings
        replacements = [
            ('live_trading_enabled: bool = False', 'live_trading_enabled: bool = True'),
            ('paper_trading_only: bool = True', 'paper_trading_only: bool = False'),
            ('enable_live_order_execution: bool = False', 'enable_live_order_execution: bool = True'),
            ('trading_mode: TradingMode = TradingMode.PAPER', 'trading_mode: TradingMode = TradingMode.LIVE')
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Write back the updated config
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("   [SUCCESS] Config file updated")
        return True
        
    except Exception as e:
        print(f"   [ERROR] Failed to update config file: {str(e)}")
        return False

def main():
    """Main function to enable live trading"""
    print("PROMETHEUS LIVE TRADING CONFIGURATION ENABLER")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Update environment variables
    update_live_trading_config()
    
    # Create .env file
    env_created = create_live_trading_env()
    
    # Update config file
    config_updated = update_config_file()
    
    if env_created and config_updated:
        print("\n[SUCCESS] LIVE TRADING CONFIGURATION ENABLED!")
        print("=" * 50)
        print("Configuration changes made:")
        print("  - LIVE_TRADING_ENABLED: true")
        print("  - PAPER_TRADING_ONLY: false")
        print("  - ENABLE_LIVE_ORDER_EXECUTION: true")
        print("  - TRADING_MODE: live")
        print()
        print("NEXT STEPS:")
        print("1. Restart the Prometheus server")
        print("2. Run: python start_active_trading.py")
        print("3. Monitor trading activity")
        print()
        print("IMPORTANT: This enables REAL MONEY trading!")
        print("Start with small position sizes and monitor closely.")
        
        return True
    else:
        print("\n[ERROR] Failed to enable live trading configuration")
        print("Check file permissions and try again")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nFINAL RESULT: {'CONFIGURATION UPDATED' if success else 'UPDATE FAILED'}")












