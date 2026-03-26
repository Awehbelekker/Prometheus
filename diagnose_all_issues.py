#!/usr/bin/env python3
"""
COMPREHENSIVE DIAGNOSTIC TOOL FOR PROMETHEUS TRADING PLATFORM
Diagnoses: Alpaca issues, IB random positions, Terminal display problems
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Setup logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Clean output
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ComprehensiveDiagnostics:
    """Complete diagnostic system for all three issues"""
    
    def __init__(self):
        self.issues_found = []
        self.alpaca_status = {}
        self.ib_status = {}
        self.terminal_issues = []
        
    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    
    def print_subheader(self, title: str):
        """Print formatted subsection header"""
        print(f"\n{'-' * 80}")
        print(f"  {title}")
        print(f"{'-' * 80}")
    
    async def diagnose_all(self):
        """Run all diagnostic checks"""
        self.print_header("🔍 PROMETHEUS PLATFORM COMPREHENSIVE DIAGNOSTICS")
        print(f"Diagnostic Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Issue 1: Alpaca Broker
        await self.diagnose_alpaca()
        
        # Issue 2: IB Random Position
        await self.diagnose_ib_positions()
        
        # Issue 3: Terminal Display
        await self.diagnose_terminal_display()
        
        # Summary
        self.print_summary()
    
    async def diagnose_alpaca(self):
        """ISSUE 1: Diagnose Alpaca broker problems"""
        self.print_header("📊 ISSUE 1: ALPACA BROKER DIAGNOSTICS")
        
        # Check API keys
        self.print_subheader("API Key Configuration")
        alpaca_key = os.getenv('ALPACA_API_KEY')
        alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        
        if not alpaca_key:
            print("❌ ALPACA_API_KEY: MISSING")
            self.issues_found.append("Alpaca API Key not set in environment")
            self.alpaca_status['api_key'] = 'MISSING'
        else:
            print(f"✅ ALPACA_API_KEY: Set (ends with ...{alpaca_key[-4:]})")
            self.alpaca_status['api_key'] = 'SET'
        
        if not alpaca_secret:
            print("❌ ALPACA_SECRET_KEY: MISSING")
            self.issues_found.append("Alpaca Secret Key not set in environment")
            self.alpaca_status['secret_key'] = 'MISSING'
        else:
            print(f"✅ ALPACA_SECRET_KEY: Set (ends with ...{alpaca_secret[-4:]})")
            self.alpaca_status['secret_key'] = 'SET'
        
        # Check configuration file
        self.print_subheader("Configuration Files")
        try:
            with open('alpaca_crypto_optimal_config.json', 'r') as f:
                alpaca_config = json.load(f)
            print("✅ alpaca_crypto_optimal_config.json: Found")
            print(f"   Starting Capital: ${alpaca_config.get('starting_capital', 0):.2f}")
            positions = alpaca_config.get('current_positions', {})
            print(f"   Tracked Positions: {len(positions)}")
            for symbol, pos_data in positions.items():
                qty = pos_data.get('qty', 0)
                entry = pos_data.get('entry', 0)
                current = pos_data.get('current', 0)
                pnl_pct = ((current - entry) / entry * 100) if entry > 0 else 0
                print(f"     • {symbol}: {qty:.6f} @ ${entry:.2f} → ${current:.2f} ({pnl_pct:+.2f}%)")
            self.alpaca_status['config_file'] = 'OK'
        except FileNotFoundError:
            print("❌ alpaca_crypto_optimal_config.json: NOT FOUND")
            self.issues_found.append("Alpaca config file missing")
            self.alpaca_status['config_file'] = 'MISSING'
        except Exception as e:
            print(f"❌ Error reading Alpaca config: {e}")
            self.issues_found.append(f"Alpaca config error: {e}")
            self.alpaca_status['config_file'] = 'ERROR'
        
        # Check broker implementation
        self.print_subheader("Broker Implementation")
        try:
            from brokers.alpaca_broker import AlpacaBroker
            print("✅ AlpacaBroker class: Imported successfully")
            
            # Check for place_order method
            if hasattr(AlpacaBroker, 'submit_order'):
                print("✅ submit_order method: Available")
                self.alpaca_status['submit_order'] = 'OK'
            else:
                print("❌ submit_order method: NOT FOUND")
                self.issues_found.append("AlpacaBroker missing 'submit_order' method")
                self.alpaca_status['submit_order'] = 'MISSING'
            
            # Check for place_order alias
            if hasattr(AlpacaBroker, 'place_order'):
                print("✅ place_order method: Available (alias)")
                self.alpaca_status['place_order'] = 'OK'
            else:
                print("⚠️  place_order method: NOT FOUND (should be alias for submit_order)")
                self.issues_found.append("AlpacaBroker missing 'place_order' alias method")
                self.alpaca_status['place_order'] = 'MISSING'
                
        except ImportError as e:
            print(f"❌ Cannot import AlpacaBroker: {e}")
            self.issues_found.append(f"AlpacaBroker import failed: {e}")
            self.alpaca_status['broker_class'] = 'IMPORT_ERROR'
        
        # Test connection (if keys available)
        if alpaca_key and alpaca_secret:
            self.print_subheader("Connection Test")
            try:
                from brokers.alpaca_broker import AlpacaBroker
                config = {
                    'api_key': alpaca_key,
                    'secret_key': alpaca_secret,
                    'paper_trading': True  # Use paper for testing
                }
                broker = AlpacaBroker(config)
                connected = await broker.connect()
                
                if connected:
                    print("✅ Connection: SUCCESS")
                    account = await broker.get_account()
                    print(f"   Account ID: {account.account_id}")
                    print(f"   Buying Power: ${account.buying_power:.2f}")
                    print(f"   Portfolio Value: ${account.portfolio_value:.2f}")
                    self.alpaca_status['connection'] = 'OK'
                    
                    # Check positions
                    positions = await broker.get_positions()
                    print(f"   Live Positions: {len(positions)}")
                    for pos in positions:
                        print(f"     • {pos.symbol}: {pos.quantity} @ ${pos.avg_price:.2f} = ${pos.market_value:.2f}")
                    
                    await broker.disconnect()
                else:
                    print("❌ Connection: FAILED")
                    self.issues_found.append("Alpaca connection test failed")
                    self.alpaca_status['connection'] = 'FAILED'
            except Exception as e:
                print(f"❌ Connection test error: {e}")
                self.issues_found.append(f"Alpaca connection error: {e}")
                self.alpaca_status['connection'] = 'ERROR'
        else:
            print("⚠️  Skipping connection test (API keys not set)")
            self.alpaca_status['connection'] = 'SKIPPED'
    
    async def diagnose_ib_positions(self):
        """ISSUE 2: Diagnose IB random position"""
        self.print_header("📈 ISSUE 2: INTERACTIVE BROKERS POSITION ANALYSIS")
        
        # Check IB configuration
        self.print_subheader("IB Configuration")
        ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
        print(f"IB Account: {ib_account}")
        
        try:
            with open('dual_broker_config.json', 'r') as f:
                broker_config = json.load(f)
            ib_config = broker_config.get('brokers', {}).get('interactive_brokers', {})
            print(f"✅ IB Configuration loaded")
            print(f"   Enabled: {ib_config.get('enabled', False)}")
            print(f"   Mode: {ib_config.get('mode', 'unknown')}")
            print(f"   Host: {ib_config.get('host', 'unknown')}:{ib_config.get('port', 'unknown')}")
            print(f"   Account: {ib_config.get('account', 'unknown')}")
            self.ib_status['config'] = 'OK'
        except Exception as e:
            print(f"❌ Error loading IB config: {e}")
            self.issues_found.append(f"IB config error: {e}")
            self.ib_status['config'] = 'ERROR'
        
        # Check for IB broker implementation
        self.print_subheader("IB Broker Implementation")
        try:
            from brokers.interactive_brokers_broker import InteractiveBrokersBroker
            print("✅ InteractiveBrokersBroker class: Imported successfully")
            self.ib_status['broker_class'] = 'OK'
        except ImportError as e:
            print(f"❌ Cannot import InteractiveBrokersBroker: {e}")
            self.issues_found.append(f"IB broker import failed: {e}")
            self.ib_status['broker_class'] = 'IMPORT_ERROR'
            return
        
        # Try to connect and get positions
        self.print_subheader("Position Analysis")
        try:
            from brokers.interactive_brokers_broker import InteractiveBrokersBroker
            config = {
                'account_id': ib_account,
                'host': '127.0.0.1',
                'port': 7496,
                'client_id': 7777
            }
            broker = InteractiveBrokersBroker(config)
            
            print("🔄 Attempting to connect to IB Gateway/TWS...")
            connected = await broker.connect()
            
            if connected:
                print("✅ Connection: SUCCESS")
                self.ib_status['connection'] = 'OK'
                
                # Wait for account data
                await asyncio.sleep(3)
                
                # Get account info
                print("\n📊 Account Summary:")
                if hasattr(broker, 'account_data') and broker.account_data:
                    for tag, value in broker.account_data.items():
                        print(f"   {tag}: {value}")
                elif hasattr(broker, 'account_values') and broker.account_values:
                    for key, value in broker.account_values.items():
                        print(f"   {key}: {value}")
                else:
                    print("   ⚠️  No account data received yet")
                
                # Get positions
                print("\n📈 Current Positions:")
                if hasattr(broker, 'positions_data') and broker.positions_data:
                    for symbol, pos_data in broker.positions_data.items():
                        qty = pos_data.get('quantity', 0)
                        avg_price = pos_data.get('avg_price', 0)
                        
                        print(f"\n   🎯 POSITION FOUND: {symbol}")
                        print(f"      Quantity: {qty}")
                        print(f"      Avg Cost: ${avg_price:.2f}")
                        print(f"      Market Value: ${qty * avg_price:.2f}")
                        
                        # Try to get current price
                        try:
                            import yfinance as yf
                            ticker = yf.Ticker(symbol)
                            current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
                            if current_price > 0:
                                pnl = (current_price - avg_price) * qty
                                pnl_pct = ((current_price - avg_price) / avg_price) * 100
                                print(f"      Current Price: ${current_price:.2f}")
                                print(f"      P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
                                
                                if pnl > 0:
                                    print(f"      ✅ PROFITABLE POSITION")
                                else:
                                    print(f"      ⚠️  LOSING POSITION")
                        except Exception as e:
                            print(f"      ⚠️  Could not get current price: {e}")
                        
                        # Analyze if this was random/unintended
                        print(f"\n      🔍 Position Analysis:")
                        print(f"         - Check if {symbol} is in your watchlist")
                        print(f"         - Review recent trades to see when/why it was bought")
                        print(f"         - This could be from automated trading logic")
                else:
                    print("   ℹ️  No positions detected")
                
                # Check open orders
                print("\n📋 Open Orders:")
                if hasattr(broker, 'open_orders') and broker.open_orders:
                    for order_id, order_data in broker.open_orders.items():
                        contract = order_data.get('contract')
                        order = order_data.get('order')
                        print(f"   Order {order_id}: {contract.symbol} {order.action} {order.totalQuantity}")
                else:
                    print("   ℹ️  No open orders")
                
                await broker.disconnect()
            else:
                print("❌ Connection: FAILED")
                print("   Make sure IB Gateway or TWS is running on port 7496")
                self.issues_found.append("Cannot connect to IB - check if TWS/Gateway is running")
                self.ib_status['connection'] = 'FAILED'
        except Exception as e:
            print(f"❌ IB connection error: {e}")
            print(f"   Error details: {type(e).__name__}: {str(e)}")
            self.issues_found.append(f"IB connection error: {e}")
            self.ib_status['connection'] = 'ERROR'
    
    async def diagnose_terminal_display(self):
        """ISSUE 3: Diagnose terminal display and logging issues"""
        self.print_header("🖥️  ISSUE 3: TERMINAL DISPLAY & LOGGING DIAGNOSTICS")
        
        self.print_subheader("Current Logging Configuration")
        
        # Check the main trading script logging
        try:
            with open('improved_dual_broker_trading.py', 'r') as f:
                content = f.read()
            
            # Check logging format
            if 'format=' in content:
                print("✅ Custom logging format detected")
            else:
                print("⚠️  Using default logging format")
                self.terminal_issues.append("No custom logging format configured")
            
            # Check for rich console output
            if 'from rich' in content or 'rich.console' in content:
                print("✅ Rich console library: Available")
            else:
                print("⚠️  Rich console library: Not used (could improve display)")
                self.terminal_issues.append("Rich console not utilized for better formatting")
            
            # Check for emoji/unicode issues
            if '\\uf' in content or 'encode(' in content:
                print("⚠️  Potential Unicode/Emoji encoding issues detected")
                self.terminal_issues.append("Unicode encoding issues may cause display problems")
            
        except FileNotFoundError:
            print("❌ improved_dual_broker_trading.py not found")
            self.terminal_issues.append("Main trading script not found")
        
        self.print_subheader("Terminal Display Recommendations")
        print("""
        IDENTIFIED ISSUES:
        
        1. LOGGING FORMAT:
           - Current format may be too verbose or unclear
           - Missing key information (positions, P&L, real-time status)
           - No color coding for different log levels
        
        2. INFORMATION DENSITY:
           - Not showing enough actionable information
           - Missing summary dashboards
           - No real-time position tracking display
        
        3. RENDERING PROBLEMS:
           - Possible unicode/emoji encoding issues
           - Terminal may not support certain characters
           - Text wrapping and formatting issues
        
        SOLUTIONS:
        
        ✅ Implement Rich Console for better formatting
        ✅ Add color-coded log levels (INFO=blue, WARNING=yellow, ERROR=red)
        ✅ Create status dashboard showing:
           - Current positions with P&L
           - Daily trade count and limits
           - Account balances (IB + Alpaca)
           - Recent signals and confidence levels
        ✅ Add progress bars for long operations
        ✅ Use tables for position summaries
        ✅ Fix unicode encoding for Windows terminal
        """)
    
    def print_summary(self):
        """Print diagnostic summary"""
        self.print_header("📋 DIAGNOSTIC SUMMARY")
        
        print(f"Total Issues Found: {len(self.issues_found)}\n")
        
        if self.issues_found:
            print("🔴 ISSUES REQUIRING ATTENTION:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ No critical issues detected!")
        
        print("\n" + "=" * 80)
        print("\n📊 DETAILED STATUS:")
        print(f"\nALPACA STATUS: {json.dumps(self.alpaca_status, indent=2)}")
        print(f"\nIB STATUS: {json.dumps(self.ib_status, indent=2)}")
        print(f"\nTERMINAL ISSUES: {len(self.terminal_issues)} identified")
        
        print("\n" + "=" * 80)
        print("\n✨ RECOMMENDED NEXT STEPS:")
        print("""
        1. For Alpaca Issues:
           - Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
           - Add 'place_order' alias method to AlpacaBroker class
           - Test connection after fixes
        
        2. For IB Position Issues:
           - Review position list in diagnostic output above
           - Check trading logs for entry signals
           - Decide: HOLD (if profitable) or CLOSE (if unwanted)
           - Verify automatic trading logic is working as intended
        
        3. For Terminal Display Issues:
           - Implement Rich console library for better formatting
           - Add comprehensive status dashboard
           - Fix unicode encoding for Windows
           - Add color-coded logging
        """)
        
        print("\n" + "=" * 80)
        print(f"\nDiagnostic completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")


async def main():
    """Run comprehensive diagnostics"""
    diagnostics = ComprehensiveDiagnostics()
    await diagnostics.diagnose_all()


if __name__ == "__main__":
    asyncio.run(main())
