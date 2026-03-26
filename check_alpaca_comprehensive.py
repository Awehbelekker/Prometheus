#!/usr/bin/env python3
"""
Comprehensive Alpaca Status Check and Connection Test
Tests credentials, connection, account info, and trading capabilities
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any

sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class AlpacaStatusChecker:
    def __init__(self):
        self.api_key = None
        self.secret_key = None
        self.paper_trading = True
        self.connected = False
        self.account_info = None
        self.errors = []
        
    def check_credentials(self):
        """Check if Alpaca credentials are configured"""
        print("="*80)
        print("ALPACA CREDENTIALS CHECK")
        print("="*80)
        
        # Try multiple environment variable names
        self.api_key = (
            os.getenv('ALPACA_API_KEY') or 
            os.getenv('APCA_API_KEY_ID') or 
            os.getenv('ALPACA_LIVE_KEY') or
            os.getenv('ALPACA_PAPER_KEY')
        )
        
        self.secret_key = (
            os.getenv('ALPACA_SECRET_KEY') or 
            os.getenv('APCA_API_SECRET_KEY') or 
            os.getenv('ALPACA_LIVE_SECRET') or
            os.getenv('ALPACA_PAPER_SECRET')
        )
        
        # Check paper trading mode
        paper_env = os.getenv('ALPACA_PAPER_TRADING', 'true').lower()
        self.paper_trading = paper_env in ('true', '1', 'yes', 'on')
        
        if self.api_key and self.secret_key:
            print(f"✅ API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
            print(f"✅ Secret Key: {'*' * 20}...{self.secret_key[-4:]}")
            print(f"✅ Mode: {'PAPER TRADING' if self.paper_trading else 'LIVE TRADING'}")
            return True
        else:
            print("❌ Credentials not found")
            if not self.api_key:
                print("   Missing: ALPACA_API_KEY or ALPACA_LIVE_KEY")
            if not self.secret_key:
                print("   Missing: ALPACA_SECRET_KEY or ALPACA_LIVE_SECRET")
            return False
    
    async def test_connection(self):
        """Test Alpaca API connection"""
        print("\n" + "="*80)
        print("ALPACA CONNECTION TEST")
        print("="*80)
        
        if not self.api_key or not self.secret_key:
            print("❌ Cannot test connection - credentials missing")
            return False
        
        try:
            # Try using alpaca_trade_api library
            try:
                import alpaca_trade_api as tradeapi
                
                base_url = 'https://paper-api.alpaca.markets' if self.paper_trading else 'https://api.alpaca.markets'
                
                print(f"Connecting to: {base_url}")
                api = tradeapi.REST(
                    self.api_key,
                    self.secret_key,
                    base_url=base_url,
                    api_version='v2'
                )
                
                # Test account access
                print("Testing account access...")
                account = api.get_account()
                
                if account:
                    self.connected = True
                    self.account_info = {
                        'account_number': account.account_number,
                        'status': account.status,
                        'equity': float(account.equity),
                        'buying_power': float(account.buying_power),
                        'cash': float(account.cash),
                        'portfolio_value': float(account.portfolio_value),
                        'pattern_day_trader': account.pattern_day_trader,
                        'trading_blocked': account.trading_blocked,
                        'account_blocked': account.account_blocked,
                        'daytrading_buying_power': float(account.daytrading_buying_power) if hasattr(account, 'daytrading_buying_power') else 0,
                    }
                    
                    print("✅ Connection successful!")
                    return True
                else:
                    print("❌ Connection failed - no account data")
                    return False
                    
            except ImportError:
                print("⚠️ alpaca_trade_api not installed")
                print("   Install with: pip install alpaca-trade-api")
                # Try alternative method with requests
                return await self._test_connection_requests()
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            self.errors.append(f"Connection error: {e}")
            return False
    
    async def _test_connection_requests(self):
        """Test connection using requests library"""
        try:
            import requests
            
            base_url = 'https://paper-api.alpaca.markets' if self.paper_trading else 'https://api.alpaca.markets'
            headers = {
                'APCA-API-KEY-ID': self.api_key,
                'APCA-API-SECRET-KEY': self.secret_key
            }
            
            print("Testing connection with requests...")
            response = requests.get(f'{base_url}/v2/account', headers=headers, timeout=10)
            
            if response.status_code == 200:
                account_data = response.json()
                self.connected = True
                self.account_info = {
                    'account_number': account_data.get('account_number', 'N/A'),
                    'status': account_data.get('status', 'N/A'),
                    'equity': float(account_data.get('equity', 0)),
                    'buying_power': float(account_data.get('buying_power', 0)),
                    'cash': float(account_data.get('cash', 0)),
                    'portfolio_value': float(account_data.get('portfolio_value', 0)),
                    'pattern_day_trader': account_data.get('pattern_day_trader', False),
                    'trading_blocked': account_data.get('trading_blocked', False),
                    'account_blocked': account_data.get('account_blocked', False),
                }
                print("✅ Connection successful!")
                return True
            else:
                print(f"❌ Connection failed - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.errors.append(f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            self.errors.append(f"Connection test error: {e}")
            return False
    
    def display_account_info(self):
        """Display account information"""
        if not self.account_info:
            print("\n⚠️ No account information available")
            return
        
        print("\n" + "="*80)
        print("ALPACA ACCOUNT INFORMATION")
        print("="*80)
        
        info = self.account_info
        print(f"Account Number: {info.get('account_number', 'N/A')}")
        print(f"Status: {info.get('status', 'N/A')}")
        print(f"Equity: ${info.get('equity', 0):,.2f}")
        print(f"Cash: ${info.get('cash', 0):,.2f}")
        print(f"Portfolio Value: ${info.get('portfolio_value', 0):,.2f}")
        print(f"Buying Power: ${info.get('buying_power', 0):,.2f}")
        
        if info.get('daytrading_buying_power', 0) > 0:
            print(f"Day Trading Buying Power: ${info.get('daytrading_buying_power', 0):,.2f}")
        
        print(f"\nTrading Status:")
        print(f"  Pattern Day Trader: {'Yes' if info.get('pattern_day_trader') else 'No'}")
        print(f"  Trading Blocked: {'Yes' if info.get('trading_blocked') else 'No'}")
        print(f"  Account Blocked: {'Yes' if info.get('account_blocked') else 'No'}")
        
        if info.get('trading_blocked') or info.get('account_blocked'):
            print("\n⚠️ WARNING: Trading is blocked!")
    
    async def test_market_data(self):
        """Test market data access"""
        print("\n" + "="*80)
        print("MARKET DATA TEST")
        print("="*80)
        
        if not self.connected:
            print("⚠️ Cannot test market data - not connected")
            return False
        
        try:
            import alpaca_trade_api as tradeapi
            
            base_url = 'https://paper-api.alpaca.markets' if self.paper_trading else 'https://api.alpaca.markets'
            api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                base_url=base_url,
                api_version='v2'
            )
            
            # Test with AAPL
            print("Testing market data for AAPL...")
            try:
                quote = api.get_latest_quote('AAPL')
                if quote:
                    print(f"✅ Market data working!")
                    print(f"   AAPL Quote: Bid ${quote.bid_price}, Ask ${quote.ask_price}")
                    return True
            except Exception as e:
                print(f"⚠️ Quote data error: {e}")
            
            # Try bar data
            try:
                bars = api.get_bars('AAPL', '1Min', limit=1)
                if bars:
                    print(f"✅ Bar data working!")
                    print(f"   AAPL Latest: ${bars[0].c}")
                    return True
            except Exception as e:
                print(f"⚠️ Bar data error: {e}")
            
            return False
            
        except ImportError:
            print("⚠️ alpaca_trade_api not installed - skipping market data test")
            return False
        except Exception as e:
            print(f"❌ Market data test error: {e}")
            return False
    
    async def test_broker_interface(self):
        """Test using Prometheus broker interface"""
        print("\n" + "="*80)
        print("PROMETHEUS BROKER INTERFACE TEST")
        print("="*80)
        
        try:
            from brokers.alpaca_broker import AlpacaBroker
            
            config = {
                'api_key': self.api_key,
                'secret_key': self.secret_key,
                'paper_trading': self.paper_trading
            }
            
            broker = AlpacaBroker(config)
            print("Connecting via Prometheus broker interface...")
            connected = await broker.connect()
            
            if connected:
                print("✅ Prometheus broker interface connected!")
                
                # Get account info
                try:
                    account_info = await broker.get_account_info()
                    print(f"   Account: {account_info.get('account_number', 'N/A')}")
                    print(f"   Equity: ${float(account_info.get('equity', 0)):,.2f}")
                    return True
                except Exception as e:
                    print(f"⚠️ Error getting account info: {e}")
                    return True  # Connected but info fetch failed
            else:
                print("❌ Prometheus broker interface connection failed")
                return False
                
        except ImportError as e:
            print(f"⚠️ Cannot import AlpacaBroker: {e}")
            return False
        except Exception as e:
            print(f"❌ Broker interface test error: {e}")
            self.errors.append(f"Broker interface error: {e}")
            return False
    
    def generate_report(self):
        """Generate final status report"""
        print("\n" + "="*80)
        print("ALPACA STATUS SUMMARY")
        print("="*80)
        
        print(f"Credentials: {'✅ CONFIGURED' if (self.api_key and self.secret_key) else '❌ MISSING'}")
        print(f"Connection: {'✅ CONNECTED' if self.connected else '❌ NOT CONNECTED'}")
        print(f"Mode: {'PAPER TRADING' if self.paper_trading else 'LIVE TRADING'}")
        
        if self.account_info:
            print(f"Account Status: {self.account_info.get('status', 'N/A')}")
            print(f"Equity: ${self.account_info.get('equity', 0):,.2f}")
            print(f"Buying Power: ${self.account_info.get('buying_power', 0):,.2f}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ⚠️ {error}")
        
        print("\n" + "="*80)
        
        # Recommendations
        if not self.api_key or not self.secret_key:
            print("\n📝 RECOMMENDATIONS:")
            print("   1. Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
            print("   2. Or set ALPACA_LIVE_KEY and ALPACA_LIVE_SECRET for live trading")
            print("   3. Or set ALPACA_PAPER_KEY and ALPACA_PAPER_SECRET for paper trading")
        
        if self.connected and (self.account_info.get('trading_blocked') or self.account_info.get('account_blocked')):
            print("\n⚠️ WARNING:")
            print("   Trading is blocked. Check your Alpaca account status.")
        
        if not self.connected and self.api_key and self.secret_key:
            print("\n📝 TROUBLESHOOTING:")
            print("   1. Verify API keys are correct in Alpaca dashboard")
            print("   2. Check if account is active")
            print("   3. Verify network connection")
            print("   4. Check if using correct mode (paper vs live)")

async def main():
    print("="*80)
    print("PROMETHEUS ALPACA COMPREHENSIVE STATUS CHECK")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    checker = AlpacaStatusChecker()
    
    # Step 1: Check credentials
    if not checker.check_credentials():
        print("\n❌ Credentials not configured. Please set them in .env file.")
        return
    
    # Step 2: Test connection
    await checker.test_connection()
    
    # Step 3: Display account info
    if checker.connected:
        checker.display_account_info()
        
        # Step 4: Test market data
        await checker.test_market_data()
        
        # Step 5: Test Prometheus broker interface
        await checker.test_broker_interface()
    
    # Step 6: Generate report
    checker.generate_report()

if __name__ == "__main__":
    asyncio.run(main())

