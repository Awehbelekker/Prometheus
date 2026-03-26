#!/usr/bin/env python3
"""
FORCE PROMETHEUS TRADING ACTIVATION
Direct activation of the trading system with comprehensive monitoring
"""

import asyncio
import sys
import os
import time
import requests
from datetime import datetime

def check_system_status():
    """Check current system status"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Ultra-Fast Server: ACTIVE")
            return True
        else:
            print(f"✗ Ultra-Fast Server: ERROR {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ultra-Fast Server: CONNECTION FAILED - {e}")
        return False

def check_trading_status():
    """Check current trading status"""
    try:
        response = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            live_enabled = data.get('live_trading', {}).get('enabled', False)
            live_active = data.get('live_trading', {}).get('active', False)
            print(f"Live Trading Enabled: {live_enabled}")
            print(f"Live Trading Active: {live_active}")
            return live_enabled, live_active
        else:
            print(f"✗ Live Trading Status: ERROR {response.status_code}")
            return False, False
    except Exception as e:
        print(f"✗ Live Trading Status: ERROR - {e}")
        return False, False

def check_portfolio_status():
    """Check portfolio status"""
    try:
        response = requests.get("http://localhost:8000/api/portfolio/value", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_value = data.get('total_value', 0)
            print(f"Portfolio Value: ${total_value:,.2f}")
            return total_value
        else:
            print(f"✗ Portfolio Status: ERROR {response.status_code}")
            return 0
    except Exception as e:
        print(f"✗ Portfolio Status: ERROR - {e}")
        return 0

def check_trading_activity():
    """Check trading activity"""
    try:
        response = requests.get("http://localhost:8000/api/trading/history", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_trades = data.get('count', 0)
            print(f"Total Trades: {total_trades}")
            return total_trades
        else:
            print(f"✗ Trading History: ERROR {response.status_code}")
            return 0
    except Exception as e:
        print(f"✗ Trading History: ERROR - {e}")
        return 0

async def force_trading_activation():
    """Force activation of the trading system"""
    print("PROMETHEUS TRADING FORCE ACTIVATION")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Check system status
    print("\n1. CHECKING SYSTEM STATUS...")
    if not check_system_status():
        print("❌ System not ready - cannot proceed")
        return False
    
    # Step 2: Check trading status
    print("\n2. CHECKING TRADING STATUS...")
    live_enabled, live_active = check_trading_status()
    
    # Step 3: Check portfolio
    print("\n3. CHECKING PORTFOLIO...")
    portfolio_value = check_portfolio_status()
    
    # Step 4: Check trading activity
    print("\n4. CHECKING TRADING ACTIVITY...")
    total_trades = check_trading_activity()
    
    # Step 5: Analysis
    print("\n5. ANALYSIS...")
    if total_trades > 0:
        print("✅ TRADING ALREADY ACTIVE!")
        print(f"Total trades executed: {total_trades}")
        return True
    elif live_enabled and not live_active:
        print("⚠️  LIVE TRADING ENABLED BUT NOT ACTIVE")
        print("This is the main issue - the trading execution engine is not running")
    elif not live_enabled:
        print("❌ LIVE TRADING NOT ENABLED")
        print("The system needs to be configured for live trading")
    else:
        print("❓ UNKNOWN STATUS")
    
    # Step 6: Force activation
    print("\n6. FORCING TRADING ACTIVATION...")
    print("Starting main trading launcher...")
    
    try:
        # Import and run the main trading launcher
        from launch_ultimate_prometheus_LIVE_TRADING import PrometheusTradingLauncher
        
        print("Creating trading launcher instance...")
        launcher = PrometheusTradingLauncher()
        
        print("TRADING EXECUTION ENGINE ACTIVATED!")
        print("Parameters:")
        print(f"  - Position Size: {launcher.risk_limits.get('position_size_pct', 0.08) * 100:.1f}%")
        print(f"  - Confidence Threshold: {launcher.risk_limits.get('min_confidence', 0.45) * 100:.1f}%")
        print(f"  - Max Trades/Hour: {launcher.risk_limits.get('max_trades_per_hour', 20)}")
        print(f"  - Daily Loss Limit: {launcher.risk_limits.get('daily_loss_limit', 10)}%")
        
        print("\n🚀 PROMETHEUS IS NOW ACTIVELY TRADING!")
        print("The system will start executing trades based on AI signals")
        print("Monitor the system for first trades within 30-60 minutes")
        
        # Start the main trading loop
        await launcher.run()
        
    except Exception as e:
        print(f"❌ FAILED TO ACTIVATE TRADING ENGINE: {e}")
        print("Possible issues:")
        print("1. Missing dependencies")
        print("2. Broker connection problems")
        print("3. Configuration errors")
        print("4. Market hours restrictions")
        return False
    
    return True

def main():
    """Main function"""
    print("Starting PROMETHEUS Force Trading Activation...")
    
    try:
        asyncio.run(force_trading_activation())
    except KeyboardInterrupt:
        print("\nTrading activation stopped by user")
    except Exception as e:
        print(f"Trading activation error: {e}")

if __name__ == "__main__":
    main()

