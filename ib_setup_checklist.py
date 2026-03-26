#!/usr/bin/env python3
"""
INTERACTIVE BROKERS SETUP CHECKLIST
Critical settings needed for Prometheus real-time trading
"""

def print_checklist():
    """Print comprehensive IB setup checklist"""
    print("INTERACTIVE BROKERS SETUP CHECKLIST")
    print("=" * 60)
    print("Critical settings for Prometheus real-time trading")
    print()
    
    print("1. IB GATEWAY/TWS SETUP")
    print("-" * 30)
    print("[ ] Download and install IB Gateway or TWS")
    print("[ ] Login with your account: U2122116")
    print("[ ] Enable API connections in settings")
    print("[ ] Set port to 7496 (live trading) or 7497 (paper trading)")
    print("[ ] Enable 'Read-Only API' if you want to test first")
    print()
    
    print("2. API CONFIGURATION")
    print("-" * 30)
    print("[ ] Go to File -> Global Configuration -> API -> Settings")
    print("[ ] Check 'Enable ActiveX and Socket Clients'")
    print("[ ] Check 'Download open orders on connection'")
    print("[ ] Check 'Include FX positions in portfolio'")
    print("[ ] Set 'Read-Only API' to FALSE (for live trading)")
    print("[ ] Set 'Create API message log file' to TRUE")
    print("[ ] Add trusted IP: 127.0.0.1 (localhost)")
    print()
    
    print("3. TRADING PERMISSIONS")
    print("-" * 30)
    print("[ ] Enable 'Stock Trading' permissions")
    print("[ ] Enable 'Options Trading' permissions (if using options)")
    print("[ ] Enable 'Forex Trading' permissions (if using forex)")
    print("[ ] Enable 'Futures Trading' permissions (if using futures)")
    print("[ ] Verify account has sufficient buying power")
    print()
    
    print("4. MARKET DATA SUBSCRIPTIONS")
    print("-" * 30)
    print("[ ] Subscribe to US Equity and Options Add-On")
    print("[ ] Subscribe to US Securities Snapshot and Futures Value Bundle")
    print("[ ] Enable real-time market data for trading symbols")
    print("[ ] Verify market data permissions are active")
    print()
    
    print("5. RISK MANAGEMENT SETTINGS")
    print("-" * 30)
    print("[ ] Set maximum order size limits")
    print("[ ] Configure daily loss limits")
    print("[ ] Enable position size controls")
    print("[ ] Set up alerts for large orders")
    print("[ ] Configure emergency stop settings")
    print()
    
    print("6. CONNECTION SETTINGS")
    print("-" * 30)
    print("[ ] Host: 127.0.0.1 (localhost)")
    print("[ ] Port: 7496 (live) or 7497 (paper)")
    print("[ ] Client ID: 10 (or any unique number)")
    print("[ ] Connection timeout: 60 seconds")
    print("[ ] Enable auto-reconnect")
    print()
    
    print("7. ACCOUNT VERIFICATION")
    print("-" * 30)
    print("[ ] Account U2122116 is active and funded")
    print("[ ] Account has trading permissions")
    print("[ ] Account is not restricted or suspended")
    print("[ ] Buying power is sufficient for intended trades")
    print("[ ] Account type supports API trading")
    print()
    
    print("8. SECURITY SETTINGS")
    print("-" * 30)
    print("[ ] Two-factor authentication enabled")
    print("[ ] API access is secure")
    print("[ ] Regular password updates")
    print("[ ] Monitor API usage logs")
    print("[ ] Set up account alerts")
    print()
    
    print("9. TESTING VERIFICATION")
    print("-" * 30)
    print("[ ] Test connection with paper trading first")
    print("[ ] Verify order placement works")
    print("[ ] Check market data is flowing")
    print("[ ] Test position monitoring")
    print("[ ] Verify account data retrieval")
    print()
    
    print("10. PROMETHEUS INTEGRATION")
    print("-" * 30)
    print("[ ] Run: python connect_live_ib.py")
    print("[ ] Verify connection to IB Gateway")
    print("[ ] Test order placement through Prometheus")
    print("[ ] Monitor trade execution")
    print("[ ] Check position updates")
    print()

def print_connection_test():
    """Print connection test instructions"""
    print("CONNECTION TEST STEPS")
    print("=" * 40)
    print()
    print("1. Start IB Gateway/TWS")
    print("2. Login with account U2122116")
    print("3. Enable API connections")
    print("4. Run connection test:")
    print("   python connect_live_ib.py")
    print()
    print("5. Check connection status:")
    print("   python check_trading_status.py")
    print()
    print("6. Start live trading:")
    print("   python start_active_trading.py")
    print()

def print_troubleshooting():
    """Print troubleshooting guide"""
    print("TROUBLESHOOTING COMMON ISSUES")
    print("=" * 40)
    print()
    print("ISSUE: Connection refused")
    print("SOLUTION: Check IB Gateway is running and API enabled")
    print()
    print("ISSUE: Authentication failed")
    print("SOLUTION: Verify account credentials and permissions")
    print()
    print("ISSUE: No market data")
    print("SOLUTION: Subscribe to market data packages")
    print()
    print("ISSUE: Orders not executing")
    print("SOLUTION: Check account permissions and buying power")
    print()
    print("ISSUE: API timeout")
    print("SOLUTION: Increase timeout settings and check network")
    print()

def print_critical_settings():
    """Print the most critical settings"""
    print("MOST CRITICAL SETTINGS FOR PROMETHEUS")
    print("=" * 50)
    print()
    print("1. API ENABLEMENT (MOST IMPORTANT)")
    print("   - File -> Global Configuration -> API -> Settings")
    print("   - Check 'Enable ActiveX and Socket Clients'")
    print("   - Set 'Read-Only API' to FALSE")
    print("   - Add trusted IP: 127.0.0.1")
    print()
    print("2. CONNECTION SETTINGS")
    print("   - Port: 7496 (live trading)")
    print("   - Host: 127.0.0.1")
    print("   - Client ID: 10")
    print()
    print("3. TRADING PERMISSIONS")
    print("   - Enable Stock Trading")
    print("   - Verify account is funded")
    print("   - Check buying power")
    print()
    print("4. MARKET DATA")
    print("   - Subscribe to US Equity data")
    print("   - Enable real-time quotes")
    print()

def main():
    """Main function"""
    print_critical_settings()
    print()
    print_checklist()
    print_connection_test()
    print_troubleshooting()
    
    print("NEXT STEPS:")
    print("=" * 20)
    print("1. Configure IB Gateway with above settings")
    print("2. Test connection with Prometheus")
    print("3. Start with small position sizes")
    print("4. Monitor trading activity closely")
    print("5. Scale up as confidence grows")
    print()
    print("IMPORTANT: Start with paper trading to test everything!")

if __name__ == "__main__":
    main()










