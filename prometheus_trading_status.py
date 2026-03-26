#!/usr/bin/env python3
"""
PROMETHEUS TRADING STATUS MONITOR
Real-time monitoring of trading activity and system status
"""

import requests
import time
import json
from datetime import datetime

def get_api_data(endpoint):
    """Get data from PROMETHEUS API"""
    try:
        response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def check_trading_status():
    """Check comprehensive trading status"""
    print("\n" + "="*80)
    print("PROMETHEUS TRADING STATUS MONITOR".center(80))
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # System Health
    health = get_api_data("/health")
    print(f"System Health: {health.get('status', 'UNKNOWN')}")
    print(f"Server Version: {health.get('version', 'N/A')}")
    
    # Live Trading Status
    live_trading = get_api_data("/api/live-trading/status")
    live_enabled = live_trading.get('live_trading', {}).get('enabled', False)
    live_active = live_trading.get('live_trading', {}).get('active', False)
    print(f"Live Trading Enabled: {live_enabled}")
    print(f"Live Trading Active: {live_active}")
    
    # Portfolio Status
    portfolio = get_api_data("/api/portfolio/value")
    total_value = portfolio.get('total_value', 0.0)
    cash_balance = portfolio.get('cash_balance', 0.0)
    unrealized_pnl = portfolio.get('unrealized_pnl', 0.0)
    print(f"Portfolio Value: ${total_value:,.2f}")
    print(f"Cash Balance: ${cash_balance:,.2f}")
    print(f"Unrealized P&L: ${unrealized_pnl:,.2f}")
    
    # Trading Activity
    active_trades = get_api_data("/api/trading/active")
    trade_history = get_api_data("/api/trading/history")
    num_active = active_trades.get('count', 0)
    num_total = trade_history.get('count', 0)
    print(f"Active Trades: {num_active}")
    print(f"Total Trades: {num_total}")
    
    # AI Status
    ai_status = get_api_data("/api/ai/coordinator/status")
    print(f"AI Coordinator: {ai_status.get('status', 'N/A')}")
    
    # Revolutionary Engines
    engines = get_api_data("/api/revolutionary/engines")
    engines_status = engines.get('engines', {})
    print(f"Revolutionary Engines: {len(engines_status)} active")
    
    # Broker Status
    print("\nBROKER CONNECTIONS:")
    try:
        # Check if we can get broker-specific data
        ib_status = get_api_data("/api/brokers/ib/status")
        alpaca_status = get_api_data("/api/brokers/alpaca/status")
        print(f"IB Status: {ib_status.get('status', 'Unknown')}")
        print(f"Alpaca Status: {alpaca_status.get('status', 'Unknown')}")
    except:
        print("Broker status endpoints not available")
    
    # Market Analysis
    print("\nMARKET ANALYSIS:")
    if num_total == 0:
        print("NO TRADES EXECUTED - System may not be actively trading")
        print("Possible reasons:")
        print("1. Market conditions don't meet confidence threshold")
        print("2. Main trading launcher not running properly")
        print("3. Broker connections issues")
        print("4. Market hours restrictions")
        print("5. AI models not generating signals")
    else:
        print(f"TRADING ACTIVE - {num_total} trades executed")
        print(f"Active positions: {num_active}")
    
    # Performance Projection
    if num_total > 0:
        # Calculate basic performance metrics
        print(f"\nPERFORMANCE ANALYSIS:")
        print(f"Trading Activity: {'ACTIVE' if num_total > 0 else 'IDLE'}")
        if num_total > 0:
            print(f"Average trades per hour: {num_total / max(1, 1)}")  # Placeholder calculation
    else:
        print(f"\nPERFORMANCE ANALYSIS:")
        print("No trading data available yet")
        print("System needs to execute first trades to show performance metrics")
    
    print("="*80)
    return {
        'health': health.get('status'),
        'live_enabled': live_enabled,
        'live_active': live_active,
        'total_value': total_value,
        'active_trades': num_active,
        'total_trades': num_total
    }

def monitor_continuously():
    """Monitor trading status continuously"""
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            status = check_trading_status()
            
            # Check if we should alert
            if status['total_trades'] == 0 and status['live_enabled']:
                print(f"\n⚠️  ALERT: Live trading enabled but no trades executed")
                print("System may need manual intervention")
            
            print(f"\nNext check in 30 seconds...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError in monitoring: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor_continuously()
    else:
        check_trading_status()
