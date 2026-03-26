#!/usr/bin/env python3
"""
🏦 Account Analysis Demo
Based on Alpaca API Documentation for /account endpoint

This script demonstrates:
1. View Account Information
2. View Gain/Loss of Portfolio
3. Account restrictions and trading status
4. Buying power analysis
5. Daily profit/loss calculations
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

class AlpacaAccountAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = None
        
    def authenticate(self) -> bool:
        """Authenticate with the trading platform"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": "admin@prometheus-trader.com",
                    "password": "PrometheusAdmin2024!"
                }
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("[CHECK] Authentication successful")
                return True
            else:
                print(f"[ERROR] Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Authentication error: {e}")
            return False
    
    def get_account_info(self, use_paper: bool = True) -> Dict[str, Any]:
        """Get account information from Alpaca API"""
        try:
            response = requests.get(
                f"{self.base_url}/api/trading/alpaca/account",
                headers=self.headers,
                params={"use_paper": use_paper}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Account info request failed: {response.status_code}")
                return {}
        except Exception as e:
            print(f"[ERROR] Account info error: {e}")
            return {}
    
    def analyze_account_information(self, account_data: Dict[str, Any]):
        """Analyze and display account information (Alpaca Doc Example 1)"""
        account = account_data.get("account", {})
        
        print("\n" + "="*60)
        print("🏦 ACCOUNT INFORMATION ANALYSIS")
        print("="*60)
        
        # Basic account info
        print(f"Account ID: {account.get('account_id', 'N/A')}")
        print(f"Status: {account.get('status', 'N/A')}")
        print(f"Currency: {account.get('currency', 'USD')}")
        print(f"Created: {account.get('created_at', 'N/A')}")
        
        print("\n📊 FINANCIAL OVERVIEW:")
        print(f"💰 Buying Power: ${account.get('buying_power', 0):,.2f}")
        print(f"💵 Cash: ${account.get('cash', 0):,.2f}")
        print(f"📈 Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
        print(f"🎯 Equity: ${account.get('equity', 0):,.2f}")
        print(f"📊 Long Market Value: ${account.get('long_market_value', 0):,.2f}")
        print(f"📉 Short Market Value: ${account.get('short_market_value', 0):,.2f}")
        
        # Trading restrictions (from Alpaca documentation)
        print("\n🔒 TRADING RESTRICTIONS:")
        trading_blocked = account.get('trading_blocked', False)
        if trading_blocked:
            print("[WARNING]️  Account is currently restricted from trading.")
        else:
            print("[CHECK] Account is free to trade")
            
        print(f"🔄 Pattern Day Trader: {'Yes' if account.get('pattern_day_trader', False) else 'No'}")
        print(f"🚫 Transfers Blocked: {'Yes' if account.get('transfers_blocked', False) else 'No'}")
        print(f"⛔ Account Blocked: {'Yes' if account.get('account_blocked', False) else 'No'}")
        
        # Day trading info
        print(f"📅 Day Trade Count: {account.get('day_trade_count', 0)}")
        print(f"💡 SMA: ${account.get('sma', 0):,.2f}")
        
        # Check buying power availability (from Alpaca documentation)
        buying_power = float(account.get('buying_power', 0))
        print(f"\n💸 ${buying_power:,.2f} is available as buying power.")
        
        return account
    
    def analyze_portfolio_gains_losses(self, account_data: Dict[str, Any]):
        """Analyze portfolio gain/loss (Alpaca Doc Example 2)"""
        account = account_data.get("account", {})
        
        print("\n" + "="*60)
        print("📈 PORTFOLIO GAIN/LOSS ANALYSIS")
        print("="*60)
        
        # Get current and last equity (from Alpaca documentation)
        current_equity = float(account.get('equity', 0))
        last_equity = float(account.get('last_equity', 0))
        
        # Calculate daily balance change (from Alpaca documentation)
        balance_change = current_equity - last_equity
        
        print(f"Current Equity: ${current_equity:,.2f}")
        print(f"Last Equity: ${last_equity:,.2f}")
        print(f"Today's portfolio balance change: ${balance_change:,.2f}")
        
        # Calculate percentage change
        if last_equity > 0:
            percentage_change = (balance_change / last_equity) * 100
            print(f"Today's percentage change: {percentage_change:+.2f}%")
            
            # Color-coded display
            if balance_change > 0:
                print("🟢 Portfolio is UP today!")
            elif balance_change < 0:
                print("🔴 Portfolio is DOWN today!")
            else:
                print("🟡 Portfolio is FLAT today!")
        else:
            print("[INFO]️  No previous equity data available for comparison")
        
        # Additional analysis
        portfolio_value = float(account.get('portfolio_value', 0))
        cash = float(account.get('cash', 0))
        invested_amount = portfolio_value - cash
        
        print(f"\n💼 PORTFOLIO COMPOSITION:")
        print(f"Total Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Cash: ${cash:,.2f} ({(cash/portfolio_value*100) if portfolio_value > 0 else 0:.1f}%)")
        print(f"Invested: ${invested_amount:,.2f} ({(invested_amount/portfolio_value*100) if portfolio_value > 0 else 0:.1f}%)")
        
        return {
            "current_equity": current_equity,
            "last_equity": last_equity,
            "balance_change": balance_change,
            "percentage_change": percentage_change if last_equity > 0 else 0
        }
    
    def check_trading_eligibility(self, account_data: Dict[str, Any]):
        """Check if account is eligible for trading"""
        account = account_data.get("account", {})
        
        print("\n" + "="*60)
        print("🔍 TRADING ELIGIBILITY CHECK")
        print("="*60)
        
        checks = []
        
        # Trading blocked check
        if not account.get('trading_blocked', True):
            checks.append("[CHECK] Trading is enabled")
        else:
            checks.append("[ERROR] Trading is blocked")
        
        # Account status check
        if account.get('status') == 'ACTIVE':
            checks.append("[CHECK] Account is active")
        else:
            checks.append(f"[ERROR] Account status: {account.get('status', 'Unknown')}")
        
        # Buying power check
        buying_power = float(account.get('buying_power', 0))
        if buying_power > 0:
            checks.append(f"[CHECK] Buying power available: ${buying_power:,.2f}")
        else:
            checks.append("[ERROR] No buying power available")
        
        # Day trading check
        if account.get('pattern_day_trader', False):
            checks.append("[WARNING]️  Pattern Day Trader status - special rules apply")
        else:
            checks.append("[CHECK] No PDT restrictions")
        
        for check in checks:
            print(check)
        
        # Overall eligibility
        eligible = (not account.get('trading_blocked', True) and 
                   account.get('status') == 'ACTIVE' and 
                   buying_power > 0)
        
        print(f"\n🎯 OVERALL TRADING ELIGIBILITY: {'[CHECK] ELIGIBLE' if eligible else '[ERROR] NOT ELIGIBLE'}")
        
        return eligible
    
    def run_full_analysis(self, use_paper: bool = True):
        """Run complete account analysis"""
        print("🚀 Starting Alpaca Account Analysis")
        print(f"Trading Mode: {'Paper Trading' if use_paper else 'Live Trading'}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.authenticate():
            return
        
        account_data = self.get_account_info(use_paper=use_paper)
        if not account_data:
            print("[ERROR] Failed to retrieve account data")
            return
        
        # Run all analyses
        account_info = self.analyze_account_information(account_data)
        gains_losses = self.analyze_portfolio_gains_losses(account_data)
        eligible = self.check_trading_eligibility(account_data)
        
        print("\n" + "="*60)
        print("📋 ANALYSIS SUMMARY")
        print("="*60)
        print(f"Account Status: {account_info.get('status', 'Unknown')}")
        print(f"Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
        print(f"Daily P&L: ${gains_losses.get('balance_change', 0):+,.2f}")
        print(f"Trading Eligible: {'Yes' if eligible else 'No'}")
        print("="*60)

if __name__ == "__main__":
    analyzer = AlpacaAccountAnalyzer()
    
    print("🎯 Choose analysis mode:")
    print("1. Paper Trading Account")
    print("2. Live Trading Account")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        use_paper = choice == "1"
        
        analyzer.run_full_analysis(use_paper=use_paper)
        
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
