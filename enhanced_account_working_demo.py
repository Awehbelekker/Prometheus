#!/usr/bin/env python3
"""
Enhanced Account Management Working Demo
Demonstrates comprehensive account features while preserving 48-hour demo
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_account_management import EnhancedAccountManager


class EnhancedAccountDemo:
    """Enhanced account management demonstration"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.manager = None
        
    def setup_account_manager(self):
        """Setup enhanced account manager"""
        try:
            self.manager = EnhancedAccountManager()
            print("[CHECK] Enhanced account manager initialized")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to setup account manager: {e}")
            return False
    
    def demo_comprehensive_account_analysis(self):
        """Demonstrate comprehensive account analysis"""
        print("\n🏦 COMPREHENSIVE ACCOUNT ANALYSIS")
        print("=" * 60)
        
        try:
            # Get comprehensive account info
            account_info = self.manager.get_comprehensive_account_info()
            
            print(f"\n📋 ACCOUNT OVERVIEW:")
            print(f"  Account Number: {account_info.account_number}")
            print(f"  Status: {account_info.status}")
            print(f"  Classification: {account_info.get_account_classification()}")
            print(f"  Currency: {account_info.currency}")
            print(f"  Created: {account_info.created_at}")
            
            print(f"\n💰 FINANCIAL POSITION:")
            print(f"  Equity: ${float(account_info.equity):,.2f}")
            print(f"  Cash: ${float(account_info.cash):,.2f}")
            print(f"  Buying Power: ${float(account_info.buying_power):,.2f}")
            
            print(f"\n⚖️ MARGIN DETAILS:")
            print(f"  Multiplier: {account_info.multiplier}x")
            print(f"  Explanation: {account_info.get_buying_power_explanation()}")
            
            print(f"\n🚦 TRADING STATUS:")
            trading_allowed = account_info.is_trading_allowed()
            print(f"  Trading Allowed: {'[CHECK]' if trading_allowed else '[ERROR]'}")
            print(f"  Pattern Day Trader: {'[CHECK]' if account_info.pattern_day_trader else '[ERROR]'}")
            print(f"  Day Trade Count: {account_info.daytrade_count}/3")
            print(f"  Shorting Enabled: {'[CHECK]' if account_info.shorting_enabled else '[ERROR]'}")
            
            # Show restrictions if any
            restrictions = account_info.get_restrictions()
            if restrictions:
                print(f"\n[WARNING]️ CURRENT RESTRICTIONS:")
                for i, restriction in enumerate(restrictions, 1):
                    print(f"  {i}. {restriction}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Account analysis failed: {e}")
            return False
    
    def demo_account_validation(self):
        """Demonstrate account validation for trading"""
        print("\n[CHECK] ACCOUNT VALIDATION FOR TRADING")
        print("=" * 60)
        
        try:
            validation = self.manager.validate_account_for_trading()
            
            print(f"\n🔍 VALIDATION RESULTS:")
            print(f"  Account Valid for Trading: {'[CHECK]' if validation['valid'] else '[ERROR]'}")
            print(f"  Account Status: {validation['account_status']}")
            print(f"  Cash Available: ${validation['cash_available']:,.2f}")
            print(f"  Buying Power: ${validation['buying_power']:,.2f}")
            print(f"  Can Day Trade: {'[CHECK]' if validation['can_day_trade'] else '[ERROR]'}")
            print(f"  Can Short Sell: {'[CHECK]' if validation['can_short'] else '[ERROR]'}")
            
            if validation['restrictions']:
                print(f"\n[WARNING]️ RESTRICTIONS:")
                for i, restriction in enumerate(validation['restrictions'], 1):
                    print(f"  {i}. {restriction}")
            
            if validation['recommendations']:
                print(f"\n💡 RECOMMENDATIONS:")
                for i, recommendation in enumerate(validation['recommendations'], 1):
                    print(f"  {i}. {recommendation}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Account validation failed: {e}")
            return False
    
    def demo_detailed_analysis(self):
        """Demonstrate detailed account analysis"""
        print("\n📊 DETAILED ACCOUNT ANALYSIS")
        print("=" * 60)
        
        try:
            analysis = self.manager.get_account_analysis()
            
            print(f"\n🏷️ BASIC INFORMATION:")
            basic = analysis['basic_info']
            print(f"  Account ID: {basic['account_id']}")
            print(f"  Classification: {basic['classification']}")
            print(f"  Crypto Status: {basic['crypto_status']}")
            
            print(f"\n💹 FINANCIAL SUMMARY:")
            financial = analysis['financial_summary']
            print(f"  Equity: ${financial['equity']:,.2f}")
            print(f"  Portfolio Value: ${financial['portfolio_value']:,.2f}")
            print(f"  Long Positions: ${financial['long_market_value']:,.2f}")
            print(f"  Short Positions: ${financial['short_market_value']:,.2f}")
            
            print(f"\n📈 MARGIN INFORMATION:")
            margin = analysis['margin_details']
            print(f"  Multiplier: {margin['multiplier']}x")
            print(f"  Initial Margin: ${margin['initial_margin']:,.2f}")
            print(f"  Maintenance Margin: ${margin['maintenance_margin']:,.2f}")
            print(f"  Day Trading BP: ${margin['daytrading_buying_power']:,.2f}")
            print(f"  Reg T BP: ${margin['regt_buying_power']:,.2f}")
            
            print(f"\n🏦 TRANSFERS & FEES:")
            transfers = analysis['transfers_and_fees']
            print(f"  Pending Transfer In: ${transfers['pending_transfer_in']:,.2f}")
            print(f"  Pending Transfer Out: ${transfers['pending_transfer_out']:,.2f}")
            print(f"  Accrued Fees: ${transfers['accrued_fees']:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Detailed analysis failed: {e}")
            return False
    
    def demo_buying_power_calculation(self):
        """Demonstrate buying power calculation explanation"""
        print("\n🧮 BUYING POWER CALCULATION BREAKDOWN")
        print("=" * 60)
        
        try:
            account_info = self.manager.get_comprehensive_account_info()
            
            multiplier = int(account_info.multiplier)
            equity = float(account_info.equity)
            cash = float(account_info.cash)
            initial_margin = float(account_info.initial_margin)
            
            print(f"\n📋 ACCOUNT TYPE: {account_info.get_account_classification()}")
            print(f"  Multiplier: {multiplier}x")
            
            print(f"\n💰 CURRENT VALUES:")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Initial Margin: ${initial_margin:,.2f}")
            
            print(f"\n🔢 CALCULATION:")
            if multiplier == 4:
                last_equity = float(account_info.last_equity)
                last_maintenance = float(account_info.last_maintenance_margin)
                daytrading_bp = (last_equity - last_maintenance) * 4
                print(f"  Formula: (last_equity - last_maintenance_margin) * 4")
                print(f"  Calculation: (${last_equity:,.2f} - ${last_maintenance:,.2f}) * 4")
                print(f"  Day Trading BP: ${daytrading_bp:,.2f}")
            elif multiplier == 2:
                reg_t_bp = max(equity - initial_margin, 0) * 2
                print(f"  Formula: max(equity - initial_margin, 0) * 2")
                print(f"  Calculation: max(${equity:,.2f} - ${initial_margin:,.2f}, 0) * 2")
                print(f"  Reg T BP: ${reg_t_bp:,.2f}")
            else:
                print(f"  Formula: buying_power = cash")
                print(f"  Limited Margin BP: ${cash:,.2f}")
            
            print(f"\n📝 EXPLANATION:")
            print(f"  {account_info.get_buying_power_explanation()}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Buying power calculation failed: {e}")
            return False
    
    def demo_account_status_definitions(self):
        """Demonstrate account status definitions"""
        print("\n📚 ACCOUNT STATUS DEFINITIONS")
        print("=" * 60)
        
        print(f"\n🏷️ ACCOUNT STATUSES:")
        statuses = {
            "ONBOARDING": "The account is onboarding",
            "SUBMISSION_FAILED": "Application submission failed",
            "SUBMITTED": "Application submitted for review",
            "ACCOUNT_UPDATED": "Account information being updated",
            "APPROVAL_PENDING": "Final approval pending",
            "ACTIVE": "Account active for trading",
            "REJECTED": "Application rejected"
        }
        
        for status, description in statuses.items():
            print(f"  {status}: {description}")
        
        print(f"\n🪙 CRYPTO STATUSES:")
        crypto_statuses = {
            "ACTIVE": "Crypto trading enabled",
            "INACTIVE": "Crypto trading not enabled",
            "PENDING": "Crypto enablement pending",
            "DISABLED": "Crypto trading disabled"
        }
        
        for status, description in crypto_statuses.items():
            print(f"  {status}: {description}")
        
        print(f"\n[LIGHTNING] MULTIPLIER TYPES:")
        multipliers = {
            "1x": "Limited margin account (buying_power = cash)",
            "2x": "Reg T margin account (default for $2,000+ equity)",
            "4x": "PDT account (4x intraday, 2x overnight)"
        }
        
        for mult, description in multipliers.items():
            print(f"  {mult}: {description}")
        
        return True
    
    def check_demo_status(self):
        """Check 48-hour demo status"""
        print("\n⏱️ DEMO STATUS CHECK")
        print("=" * 60)
        
        try:
            # Check if demo is still running
            import sqlite3
            conn = sqlite3.connect('prometheus_trading.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as total_calls,
                       MIN(created_at) as first_call,
                       MAX(created_at) as last_call
                FROM alpaca_requests
            ''')
            
            row = cursor.fetchone()
            if row and row[0] > 0:
                total_calls, first_call, last_call = row
                
                # Calculate runtime
                from datetime import datetime
                if first_call:
                    start_time = datetime.fromisoformat(first_call.replace('Z', '+00:00'))
                    now = datetime.now(start_time.tzinfo)
                    runtime_hours = (now - start_time).total_seconds() / 3600
                    
                    print(f"📊 DEMO STATISTICS:")
                    print(f"  Total API Calls: {total_calls}")
                    print(f"  Demo Started: {first_call}")
                    print(f"  Last Activity: {last_call}")
                    print(f"  Runtime: {runtime_hours:.1f} hours")
                    print(f"  Status: {'🟢 Active' if runtime_hours < 48 else '🔴 Expired'}")
                    
                    if runtime_hours < 48:
                        remaining = 48 - runtime_hours
                        print(f"  Time Remaining: {remaining:.1f} hours")
                else:
                    print("📊 No demo activity recorded yet")
            else:
                print("📊 Demo not started or no activity recorded")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] Demo status check failed: {e}")
            return False
    
    def run_enhanced_demo(self):
        """Run the complete enhanced account demo"""
        print("🚀 ENHANCED ALPACA ACCOUNT MANAGEMENT DEMO")
        print("=" * 80)
        print("Comprehensive account analysis while preserving 48-hour demo")
        print("=" * 80)
        
        # Setup
        if not self.setup_account_manager():
            print("[ERROR] Demo setup failed")
            return
        
        # Demo sections
        demos = [
            ("Demo Status Check", self.check_demo_status),
            ("Comprehensive Analysis", self.demo_comprehensive_account_analysis),
            ("Account Validation", self.demo_account_validation),
            ("Detailed Analysis", self.demo_detailed_analysis),
            ("Buying Power Calculation", self.demo_buying_power_calculation),
            ("Status Definitions", self.demo_account_status_definitions)
        ]
        
        success_count = 0
        for demo_name, demo_func in demos:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            try:
                if demo_func():
                    success_count += 1
                    print(f"[CHECK] {demo_name} completed successfully")
                else:
                    print(f"[ERROR] {demo_name} failed")
            except Exception as e:
                print(f"[ERROR] {demo_name} error: {e}")
        
        # Summary
        print(f"\n🎯 DEMO SUMMARY")
        print("=" * 60)
        print(f"Completed: {success_count}/{len(demos)} sections")
        print(f"Success Rate: {(success_count/len(demos)*100):.1f}%")
        
        if success_count == len(demos):
            print("[CHECK] All enhanced account features working perfectly!")
            print("🎉 Enhanced account management ready for integration!")
        else:
            print("[WARNING]️ Some features need attention")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. Enhanced account endpoints ready for server integration")
        print("2. Full Alpaca documentation compliance implemented")
        print("3. Comprehensive account analysis available")
        print("4. Demo continues running uninterrupted")
        print("5. Ready for live trading account support")


if __name__ == "__main__":
    demo = EnhancedAccountDemo()
    demo.run_enhanced_demo()
