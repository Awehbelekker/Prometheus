#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Trade Status Report for IB and Alpaca
====================================================
Generates a complete status report for both Interactive Brokers and Alpaca
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Load environment variables
load_dotenv()

class TradeStatusReport:
    def __init__(self):
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'ib': {},
            'alpaca': {},
            'summary': {}
        }
    
    async def check_alpaca(self) -> Dict[str, Any]:
        """Check Alpaca trading status"""
        print("\n" + "="*80)
        print("🦙 ALPACA TRADING STATUS")
        print("="*80)
        
        try:
            import alpaca_trade_api as tradeapi
            
            # Load credentials
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
            
            if not api_key or not secret_key:
                print("[ERROR] Alpaca credentials not found in .env")
                return {
                    'connected': False,
                    'error': 'Missing API credentials'
                }
            
            # Check if paper or live
            paper_trading = os.getenv('ALPACA_PAPER_TRADING', 'true').lower() == 'true'
            base_url = 'https://paper-api.alpaca.markets' if paper_trading else 'https://api.alpaca.markets'
            
            print(f"Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
            print(f"API URL: {base_url}")
            
            # Initialize API
            api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
            
            # Test connection
            account = api.get_account()
            print(f"\n✅ Connected to Alpaca")
            print(f"Account Number: {account.account_number}")
            print(f"Status: {account.status}")
            
            # Account information
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            cash = float(account.cash)
            buying_power = float(account.buying_power)
            portfolio_value = float(account.portfolio_value)
            
            daily_return = equity - last_equity
            daily_return_pct = (daily_return / last_equity * 100) if last_equity > 0 else 0
            
            print("\n📊 ACCOUNT SUMMARY")
            print("-" * 80)
            print(f"Current Equity: ${equity:,.2f}")
            print(f"Previous Equity: ${last_equity:,.2f}")
            print(f"Daily P/L: ${daily_return:+,.2f} ({daily_return_pct:+.2f}%)")
            print(f"Cash: ${cash:,.2f}")
            print(f"Buying Power: ${buying_power:,.2f}")
            print(f"Portfolio Value: ${portfolio_value:,.2f}")
            
            # Get positions
            positions = api.list_positions()
            
            print(f"\n💼 POSITIONS: {len(positions)}")
            print("-" * 80)
            
            if positions:
                print(f"{'Symbol':<12} {'Side':<6} {'Qty':<12} {'Entry':<12} {'Current':<12} {'P/L':<12} {'P/L %':<10}")
                print("-" * 80)
                
                total_value = 0
                total_pl = 0
                
                for pos in positions:
                    qty = float(pos.qty)
                    entry = float(pos.avg_entry_price)
                    current = float(pos.current_price)
                    pl = float(pos.unrealized_pl)
                    pl_pct = float(pos.unrealized_plpc) * 100
                    value = abs(qty) * current
                    
                    total_value += value
                    total_pl += pl
                    
                    pl_symbol = "💰" if pl > 0 else "🔴" if pl < 0 else "➖"
                    print(f"{pos.symbol:<12} {pos.side:<6} {qty:<12.2f} ${entry:<11.2f} ${current:<11.2f} ${pl:<11.2f} {pl_pct:+.2f}% {pl_symbol}")
                
                print("-" * 80)
                print(f"Total Position Value: ${total_value:,.2f}")
                print(f"Total Unrealized P/L: ${total_pl:+,.2f}")
                
                if total_value > 0:
                    total_pl_pct = (total_pl / (total_value - total_pl)) * 100
                    print(f"Total P/L %: {total_pl_pct:+.2f}%")
            else:
                print("No open positions")
            
            # Get recent orders
            orders = api.list_orders(status='all', limit=50)
            
            print(f"\n📋 RECENT ORDERS: {len(orders)}")
            print("-" * 80)
            
            filled = [o for o in orders if o.status == 'filled']
            pending = [o for o in orders if o.status in ['new', 'pending_new', 'accepted']]
            rejected = [o for o in orders if o.status in ['rejected', 'canceled']]
            
            print(f"Total Orders: {len(orders)}")
            print(f"✅ Filled: {len(filled)}")
            print(f"⏳ Pending: {len(pending)}")
            print(f"❌ Rejected/Canceled: {len(rejected)}")
            
            if filled:
                win_rate = len([o for o in filled if float(o.filled_avg_price) > 0]) / len(filled) * 100
                print(f"Success Rate: {win_rate:.1f}%")
            
            # Return data
            return {
                'connected': True,
                'paper_trading': paper_trading,
                'account': {
                    'number': account.account_number,
                    'status': account.status,
                    'equity': equity,
                    'last_equity': last_equity,
                    'cash': cash,
                    'buying_power': buying_power,
                    'portfolio_value': portfolio_value,
                    'daily_return': daily_return,
                    'daily_return_pct': daily_return_pct
                },
                'positions': {
                    'count': len(positions),
                    'total_value': sum(abs(float(p.qty)) * float(p.current_price) for p in positions),
                    'total_pnl': sum(float(p.unrealized_pl) for p in positions),
                    'details': [
                        {
                            'symbol': p.symbol,
                            'side': p.side,
                            'quantity': float(p.qty),
                            'entry_price': float(p.avg_entry_price),
                            'current_price': float(p.current_price),
                            'pnl': float(p.unrealized_pl),
                            'pnl_pct': float(p.unrealized_plpc) * 100
                        }
                        for p in positions
                    ]
                },
                'orders': {
                    'total': len(orders),
                    'filled': len(filled),
                    'pending': len(pending),
                    'rejected': len(rejected)
                }
            }
            
        except ImportError:
            print("[ERROR] Alpaca API not installed")
            return {'connected': False, 'error': 'Alpaca API not installed'}
        except Exception as e:
            print(f"[ERROR] Alpaca check failed: {e}")
            import traceback
            traceback.print_exc()
            return {'connected': False, 'error': str(e)}
    
    async def check_ib(self) -> Dict[str, Any]:
        """Check Interactive Brokers trading status"""
        print("\n" + "="*80)
        print("🏦 INTERACTIVE BROKERS TRADING STATUS")
        print("="*80)
        
        try:
            from brokers.interactive_brokers_broker import InteractiveBrokersBroker
            
            # Configuration
            ib_config = {
                'host': os.getenv('IB_GATEWAY_HOST', '127.0.0.1'),
                'port': int(os.getenv('IB_GATEWAY_PORT', '7497')),
                'client_id': int(os.getenv('IB_CLIENT_ID', '1')),
                'account_id': os.getenv('IB_ACCOUNT_ID', ''),
                'paper_trading': os.getenv('IB_PAPER_TRADING', 'true').lower() == 'true'
            }
            
            paper_trading = ib_config['paper_trading']
            port = ib_config['port']
            
            print(f"Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
            print(f"Host: {ib_config['host']}")
            print(f"Port: {port}")
            print(f"Client ID: {ib_config['client_id']}")
            
            # Initialize broker
            broker = InteractiveBrokersBroker(ib_config)
            
            print("\n🔄 Attempting connection...")
            connected = await broker.connect()
            
            if not connected:
                print("[ERROR] Failed to connect to IB Gateway/TWS")
                print("\n⚠️  TROUBLESHOOTING:")
                print("   1. Make sure IB Gateway or TWS is running")
                print("   2. Check if API is enabled (Configure → Settings → API)")
                print(f"   3. Verify port {port} is correct")
                print("   4. Ensure no firewall is blocking the connection")
                return {
                    'connected': False,
                    'error': 'Connection failed'
                }
            
            print("✅ Connected to IB")
            
            # Wait for data sync
            await asyncio.sleep(3)
            
            # Get account information
            print("\n📊 ACCOUNT INFORMATION")
            print("-" * 80)
            
            try:
                account = await broker.get_account()
                print(f"Account ID: {account.account_id}")
                print(f"Portfolio Value: ${account.portfolio_value:,.2f}")
                print(f"Cash: ${account.cash:,.2f}")
                print(f"Buying Power: ${account.buying_power:,.2f}")
                print(f"Equity: ${account.equity:,.2f}")
            except Exception as e:
                print(f"[WARNING] Could not get account info: {e}")
                account = None
            
            # Get positions
            print("\n💼 POSITIONS")
            print("-" * 80)
            
            try:
                positions = await broker.get_positions()
                print(f"Open Positions: {len(positions)}")
                
                if positions:
                    print(f"{'Symbol':<12} {'Side':<6} {'Qty':<12} {'Avg Price':<12} {'Value':<12}")
                    print("-" * 80)
                    
                    for pos in positions:
                        value = pos.quantity * pos.avg_price
                        print(f"{pos.symbol:<12} {pos.side:<6} {pos.quantity:<12.2f} ${pos.avg_price:<11.2f} ${value:,.2f}")
                else:
                    print("No open positions")
                
            except Exception as e:
                print(f"[WARNING] Could not get positions: {e}")
                positions = []
            
            # Test market data
            print("\n📈 MARKET DATA TEST")
            print("-" * 80)
            
            test_symbols = ['AAPL', 'MSFT', 'GOOGL']
            market_data_ok = 0
            
            for symbol in test_symbols:
                try:
                    data = await broker.get_market_data(symbol)
                    if data and data.get('price', 0) > 0:
                        print(f"✅ {symbol}: ${data['price']:,.2f}")
                        market_data_ok += 1
                    else:
                        print(f"⚠️  {symbol}: No data")
                except Exception as e:
                    print(f"❌ {symbol}: Error - {str(e)[:50]}")
                
                await asyncio.sleep(0.5)
            
            # Get session information
            session = broker._get_current_trading_session()
            print(f"\n⏰ CURRENT SESSION: {session.upper()}")
            
            # Disconnect
            await broker.disconnect()
            
            # Return data
            return {
                'connected': True,
                'paper_trading': paper_trading,
                'config': ib_config,
                'account': {
                    'id': account.account_id if account else None,
                    'portfolio_value': account.portfolio_value if account else 0,
                    'cash': account.cash if account else 0,
                    'buying_power': account.buying_power if account else 0,
                    'equity': account.equity if account else 0
                },
                'positions': {
                    'count': len(positions),
                    'details': [
                        {
                            'symbol': p.symbol,
                            'side': p.side,
                            'quantity': p.quantity,
                            'avg_price': p.avg_price,
                            'market_value': p.market_value
                        }
                        for p in positions
                    ]
                },
                'market_data': {
                    'working': market_data_ok > 0,
                    'success_rate': market_data_ok / len(test_symbols) if test_symbols else 0
                },
                'session': session
            }
            
        except ImportError:
            print("[ERROR] IB API not installed or not available")
            return {'connected': False, 'error': 'IB API not available'}
        except Exception as e:
            print(f"[ERROR] IB check failed: {e}")
            import traceback
            traceback.print_exc()
            return {'connected': False, 'error': str(e)}
    
    async def generate_summary(self):
        """Generate summary comparison"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE SUMMARY")
        print("="*80)
        
        ib_data = self.report_data['ib']
        alpaca_data = self.report_data['alpaca']
        
        # Connection Status
        print("\n🔌 CONNECTION STATUS")
        print("-" * 80)
        print(f"Interactive Brokers: {'✅ CONNECTED' if ib_data.get('connected') else '❌ NOT CONNECTED'}")
        print(f"Alpaca: {'✅ CONNECTED' if alpaca_data.get('connected') else '❌ NOT CONNECTED'}")
        
        if not ib_data.get('connected'):
            print(f"   IB Error: {ib_data.get('error', 'Unknown error')}")
        if not alpaca_data.get('connected'):
            print(f"   Alpaca Error: {alpaca_data.get('error', 'Unknown error')}")
        
        # Account Comparison
        print("\n💰 ACCOUNT COMPARISON")
        print("-" * 80)
        
        if alpaca_data.get('connected') and alpaca_data.get('account'):
            acc = alpaca_data['account']
            print(f"\nAlpaca ({'PAPER' if alpaca_data.get('paper_trading') else 'LIVE'}):")
            print(f"   Portfolio Value: ${acc.get('portfolio_value', 0):,.2f}")
            print(f"   Cash: ${acc.get('cash', 0):,.2f}")
            print(f"   Buying Power: ${acc.get('buying_power', 0):,.2f}")
            print(f"   Daily P/L: ${acc.get('daily_return', 0):+,.2f} ({acc.get('daily_return_pct', 0):+.2f}%)")
        
        if ib_data.get('connected') and ib_data.get('account'):
            acc = ib_data['account']
            print(f"\nInteractive Brokers ({'PAPER' if ib_data.get('paper_trading') else 'LIVE'}):")
            print(f"   Portfolio Value: ${acc.get('portfolio_value', 0):,.2f}")
            print(f"   Cash: ${acc.get('cash', 0):,.2f}")
            print(f"   Buying Power: ${acc.get('buying_power', 0):,.2f}")
        
        # Positions
        print("\n💼 POSITIONS SUMMARY")
        print("-" * 80)
        
        alpaca_pos = alpaca_data.get('positions', {})
        ib_pos = ib_data.get('positions', {})
        
        print(f"Alpaca Positions: {alpaca_pos.get('count', 0)}")
        if alpaca_pos.get('count', 0) > 0:
            print(f"   Total Value: ${alpaca_pos.get('total_value', 0):,.2f}")
            print(f"   Total P/L: ${alpaca_pos.get('total_pnl', 0):+,.2f}")
        
        print(f"IB Positions: {ib_pos.get('count', 0)}")
        
        # Trading Capabilities
        print("\n🎯 TRADING CAPABILITIES")
        print("-" * 80)
        print("Alpaca:")
        print("   • Stocks: ✅")
        print("   • Crypto: ✅ (24/7)")
        print("   • Options: ❌")
        print("   • Forex: ❌")
        
        print("\nInteractive Brokers:")
        print("   • Stocks: ✅")
        print("   • Crypto: ❌")
        print("   • Options: ✅")
        print("   • Forex: ✅")
        print("   • Futures: ✅")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 80)
        
        if not alpaca_data.get('connected') and not ib_data.get('connected'):
            print("⚠️  NO BROKERS CONNECTED!")
            print("   • Start Alpaca: Set up API credentials in .env")
            print("   • Start IB: Open IB Gateway/TWS and enable API")
        elif not alpaca_data.get('connected'):
            print("⚠️  Alpaca not connected - crypto trading unavailable")
        elif not ib_data.get('connected'):
            print("⚠️  IB not connected - options/forex trading unavailable")
        else:
            print("✅ Both brokers operational!")
            print("   • Use Alpaca for crypto trading")
            print("   • Use IB for stocks, options, and forex")
        
        # Save report data
        self.report_data['summary'] = {
            'both_connected': alpaca_data.get('connected') and ib_data.get('connected'),
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n" + "="*80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

async def main():
    """Main function"""
    print("\n" + "="*80)
    print("🚀 COMPREHENSIVE TRADE STATUS REPORT")
    print("Interactive Brokers + Alpaca")
    print("="*80)
    
    report = TradeStatusReport()
    
    # Check both brokers
    report.report_data['alpaca'] = await report.check_alpaca()
    report.report_data['ib'] = await report.check_ib()
    
    # Generate summary
    await report.generate_summary()
    
    # Save report to file
    try:
        import json
        report_file = f"trade_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report.report_data, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {report_file}")
    except Exception as e:
        print(f"[WARNING] Could not save report file: {e}")

if __name__ == "__main__":
    asyncio.run(main())

