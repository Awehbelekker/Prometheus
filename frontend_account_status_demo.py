#!/usr/bin/env python3
"""
Frontend Account Status Demo
Shows how the frontend can display IB account status
"""

import requests
import json
from datetime import datetime
import time

def get_account_status():
    """Get current account status for frontend display"""
    try:
        response = requests.get('http://localhost:8000/api/ib-live/account', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_trading_status():
    """Get current trading status"""
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def format_currency(amount):
    """Format currency for display"""
    return f"${amount:,.2f}"

def get_account_status_display():
    """Get formatted account status for frontend display"""
    account = get_account_status()
    trading = get_trading_status()
    
    if "error" in account:
        return {
            "status": "error",
            "message": f"Account connection failed: {account['error']}"
        }
    
    # Determine account funding status
    buying_power = account.get('buying_power', 0)
    net_liquidation = account.get('net_liquidation', 0)
    
    if buying_power > 0 or net_liquidation > 0:
        funding_status = "funded"
        funding_message = "Account is funded and ready for trading"
        funding_color = "success"
    else:
        funding_status = "pending"
        funding_message = "Awaiting funds - system ready to trade when funds arrive"
        funding_color = "warning"
    
    # Trading mode status
    trading_status = trading.get('status', 'unknown')
    if trading_status == 'configured':
        trading_ready = True
        trading_message = "Live trading configured and ready"
        trading_color = "success"
    else:
        trading_ready = False
        trading_message = "Live trading not configured"
        trading_color = "error"
    
    return {
        "status": "success",
        "account": {
            "account_id": account.get('account_id', 'Unknown'),
            "account_type": account.get('account_type', 'Unknown'),
            "currency": account.get('currency', 'USD'),
            "buying_power": buying_power,
            "buying_power_formatted": format_currency(buying_power),
            "net_liquidation": net_liquidation,
            "net_liquidation_formatted": format_currency(net_liquidation),
            "available_funds": account.get('available_funds', 0),
            "available_funds_formatted": format_currency(account.get('available_funds', 0)),
            "day_trades_remaining": account.get('day_trades_remaining', 0)
        },
        "funding": {
            "status": funding_status,
            "message": funding_message,
            "color": funding_color,
            "is_funded": buying_power > 0 or net_liquidation > 0
        },
        "trading": {
            "status": trading_status,
            "ready": trading_ready,
            "message": trading_message,
            "color": trading_color,
            "port": trading.get('port', 7496),
            "mode": trading.get('trading_mode', 'unknown')
        },
        "safety": {
            "daily_loss_limit": trading.get('risk_management', {}).get('max_daily_loss_dollars', 50),
            "max_daily_trades": trading.get('risk_management', {}).get('max_daily_trades', 5),
            "position_size_limit": trading.get('risk_management', {}).get('max_position_size_percent', 1.0),
            "emergency_stop_available": trading.get('safety_features', {}).get('emergency_stop_available', True)
        },
        "timestamp": datetime.now().isoformat(),
        "last_updated": datetime.now().strftime('%H:%M:%S')
    }

def demo_frontend_display():
    """Demo how frontend would display account status"""
    
    print("🖥️  FRONTEND ACCOUNT STATUS DISPLAY DEMO")
    print("=" * 60)
    
    # Get account status
    status_data = get_account_status_display()
    
    if status_data["status"] == "error":
        print(f"[ERROR] {status_data['message']}")
        return
    
    account = status_data["account"]
    funding = status_data["funding"]
    trading = status_data["trading"]
    safety = status_data["safety"]
    
    # Account Header
    print(f"\n🏦 ACCOUNT: {account['account_id']}")
    print("-" * 40)
    print(f"Type: {account['account_type'].upper()}")
    print(f"Currency: {account['currency']}")
    print(f"Last Updated: {status_data['last_updated']}")
    
    # Funding Status
    funding_icon = "[CHECK]" if funding["is_funded"] else "⏳"
    print(f"\n💰 FUNDING STATUS: {funding_icon}")
    print("-" * 40)
    print(f"Status: {funding['status'].upper()}")
    print(f"Message: {funding['message']}")
    print(f"Buying Power: {account['buying_power_formatted']}")
    print(f"Net Liquidation: {account['net_liquidation_formatted']}")
    print(f"Available Funds: {account['available_funds_formatted']}")
    
    # Trading Status
    trading_icon = "[CHECK]" if trading["ready"] else "[ERROR]"
    print(f"\n🚀 TRADING STATUS: {trading_icon}")
    print("-" * 40)
    print(f"Status: {trading['status'].upper()}")
    print(f"Mode: {trading['mode'].upper()}")
    print(f"Port: {trading['port']}")
    print(f"Message: {trading['message']}")
    
    # Safety Features
    print(f"\n🛡️  SAFETY FEATURES:")
    print("-" * 40)
    print(f"Daily Loss Limit: ${safety['daily_loss_limit']:.2f}")
    print(f"Max Daily Trades: {safety['max_daily_trades']}")
    print(f"Position Size Limit: {safety['position_size_limit']:.1f}%")
    print(f"Emergency Stop: {'Available' if safety['emergency_stop_available'] else 'Not Available'}")
    
    # Overall Status
    print(f"\n🎯 OVERALL STATUS:")
    print("=" * 60)
    
    if funding["is_funded"] and trading["ready"]:
        print("[CHECK] READY FOR LIVE TRADING")
        print("💰 Account funded and trading configured")
        print("🤖 Autonomous trading will execute automatically")
    elif not funding["is_funded"] and trading["ready"]:
        print("⏳ READY - AWAITING FUNDS")
        print("🔧 Trading configured, waiting for account funding")
        print("🤖 Will start autonomous trading when funds arrive")
    else:
        print("[WARNING]️  CONFIGURATION NEEDED")
        print("🔧 Complete setup required before trading")
    
    print("\n" + "=" * 60)
    
    return status_data

def continuous_monitoring_demo():
    """Demo continuous account monitoring"""
    print("\n🔄 CONTINUOUS MONITORING DEMO")
    print("(Press Ctrl+C to stop)")
    print("-" * 40)
    
    try:
        while True:
            status_data = get_account_status_display()
            
            if status_data["status"] == "success":
                account = status_data["account"]
                funding = status_data["funding"]
                
                # Simple status line
                funding_icon = "💰" if funding["is_funded"] else "⏳"
                print(f"{status_data['last_updated']} | {funding_icon} {account['account_id']} | "
                      f"Buying Power: {account['buying_power_formatted']} | "
                      f"Status: {funding['status'].upper()}")
            else:
                print(f"{datetime.now().strftime('%H:%M:%S')} | [ERROR] Connection Error")
            
            time.sleep(10)  # Update every 10 seconds
            
    except KeyboardInterrupt:
        print("\n\n[CHECK] Monitoring stopped")

if __name__ == "__main__":
    # Run the demo
    demo_frontend_display()
    
    # Ask if user wants continuous monitoring
    print("\nWould you like to see continuous monitoring? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            continuous_monitoring_demo()
    except KeyboardInterrupt:
        print("\n[CHECK] Demo completed")
