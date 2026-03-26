#!/usr/bin/env python3
"""
View Live Alpaca Trading Activity
Shows real-time account status, positions, orders, and recent trades
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    logger = logging.getLogger(__name__)
    logger.info("✅ Loaded .env file")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("python-dotenv not installed, .env file not loaded")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from core.alpaca_trading_service import get_alpaca_service
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.error("Alpaca service not available")


def format_currency(value: float) -> str:
    """Format currency value"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage"""
    return f"{value:.2f}%"


def view_live_trading():
    """View live Alpaca trading activity"""
    print("="*80)
    print("ALPACA LIVE TRADING DASHBOARD")
    print("="*80)
    
    if not ALPACA_AVAILABLE:
        print("\n❌ Alpaca service not available")
        print("   Install: pip install alpaca-trade-api")
        return
    
    # Check what credentials are available and fill in missing ones from daily_trading_report.py
    paper_key = os.getenv('ALPACA_PAPER_KEY') or os.getenv('ALPACA_API_KEY')
    paper_secret = os.getenv('ALPACA_PAPER_SECRET')
    live_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
    live_secret = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_SECRET_KEY')
    
    # Try to load missing credentials from daily_trading_report.py
    if not paper_key or not paper_secret or not live_key or not live_secret:
        try:
            # Read credentials from daily_trading_report.py
            daily_report_path = os.path.join(os.path.dirname(__file__), 'daily_trading_report.py')
            if os.path.exists(daily_report_path):
                with open(daily_report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract credentials using regex - handle both single and double quotes
                    import re
                    paper_key_match = re.search(r"os\.environ\['ALPACA_PAPER_KEY'\]\s*=\s*['\"]([^'\"]+)['\"]", content)
                    paper_secret_match = re.search(r"os\.environ\['ALPACA_PAPER_SECRET'\]\s*=\s*['\"]([^'\"]+)['\"]", content)
                    live_key_match = re.search(r"os\.environ\['ALPACA_LIVE_KEY'\]\s*=\s*['\"]([^'\"]+)['\"]", content)
                    live_secret_match = re.search(r"os\.environ\['ALPACA_LIVE_SECRET'\]\s*=\s*['\"]([^'\"]+)['\"]", content)
                    
                    if paper_key_match and not paper_key:
                        os.environ['ALPACA_PAPER_KEY'] = paper_key_match.group(1)
                        logger.info("✅ Loaded ALPACA_PAPER_KEY from daily_trading_report.py")
                    
                    if paper_secret_match and not paper_secret:
                        os.environ['ALPACA_PAPER_SECRET'] = paper_secret_match.group(1)
                        logger.info("✅ Loaded ALPACA_PAPER_SECRET from daily_trading_report.py")
                    
                    if live_key_match and not live_key:
                        os.environ['ALPACA_LIVE_KEY'] = live_key_match.group(1)
                        logger.info("✅ Loaded ALPACA_LIVE_KEY from daily_trading_report.py")
                    
                    if live_secret_match and not live_secret:
                        os.environ['ALPACA_LIVE_SECRET'] = live_secret_match.group(1)
                        logger.info("✅ Loaded ALPACA_LIVE_SECRET from daily_trading_report.py")
        except Exception as e:
            logger.debug(f"Could not load credentials from daily_trading_report: {e}")
    
    # Get Alpaca service (try paper first, then live)
    service = None
    use_paper = True
    connection_error = None
    
    # Try paper trading first
    try:
        service = get_alpaca_service(use_paper=True)
        if service.is_available():
            # Test connection by getting account
            try:
                test_account = service.get_account_info()
                if 'error' in test_account and 'unauthorized' in str(test_account.get('error', '')).lower():
                    connection_error = "Paper trading: unauthorized (keys may be invalid)"
                    logger.warning(connection_error)
                    # Try live trading as fallback
                    logger.info("Trying live trading as fallback...")
                    use_paper = False
                    service = get_alpaca_service(use_paper=False)
                    if service.is_available():
                        test_account = service.get_account_info()
                        if 'error' in test_account and 'unauthorized' in str(test_account.get('error', '')).lower():
                            connection_error = "Both paper and live trading: unauthorized"
                            logger.error(connection_error)
                else:
                    use_paper = True
            except Exception as e:
                connection_error = f"Paper trading connection error: {e}"
                logger.warning(connection_error)
                # Try live trading
                use_paper = False
                service = get_alpaca_service(use_paper=False)
        else:
            # Try live trading if paper not available
            logger.info("Paper trading not available, trying live trading...")
            use_paper = False
            service = get_alpaca_service(use_paper=False)
    except Exception as e:
        logger.warning(f"Error getting paper trading service: {e}")
        connection_error = f"Paper trading error: {e}"
        # Try live trading as fallback
        try:
            use_paper = False
            service = get_alpaca_service(use_paper=False)
        except Exception as e2:
            logger.error(f"Error getting live trading service: {e2}")
            connection_error = f"Both paper and live failed: {e2}"
            service = None
    except Exception as e:
        print(f"\n⚠️ Error getting Alpaca service: {e}")
        print("\nTo enable Alpaca trading:")
        print("  1. Set ALPACA_PAPER_KEY environment variable")
        print("  2. Set ALPACA_PAPER_SECRET environment variable")
        print("  3. Or set ALPACA_LIVE_KEY and ALPACA_LIVE_SECRET for live trading")
        return
    
    if not service or not service.is_available():
        print("\n⚠️ Alpaca service not available")
        if connection_error:
            print(f"   Error: {connection_error}")
        print("\n   Current credentials status:")
        print(f"   ALPACA_PAPER_KEY: {'SET (' + os.getenv('ALPACA_PAPER_KEY', '')[:10] + '...)' if os.getenv('ALPACA_PAPER_KEY') else 'NOT SET'}")
        print(f"   ALPACA_PAPER_SECRET: {'SET (' + os.getenv('ALPACA_PAPER_SECRET', '')[:4] + '...)' if os.getenv('ALPACA_PAPER_SECRET') else 'NOT SET'}")
        print(f"   ALPACA_LIVE_KEY: {'SET (' + os.getenv('ALPACA_LIVE_KEY', '')[:10] + '...)' if os.getenv('ALPACA_LIVE_KEY') else 'NOT SET'}")
        print(f"   ALPACA_LIVE_SECRET: {'SET (' + os.getenv('ALPACA_LIVE_SECRET', '')[:4] + '...)' if os.getenv('ALPACA_LIVE_SECRET') else 'NOT SET'}")
        print("\n💡 Troubleshooting:")
        print("   1. Check Alpaca dashboard: https://app.alpaca.markets/")
        print("   2. Verify API keys are active and not expired")
        print("   3. Check account status (not suspended/restricted)")
        print("   4. Paper trading keys start with 'PK', Live keys start with 'AK'")
        print("   5. Ensure keys have trading permissions enabled")
        return
    
    print(f"\n📊 Mode: {'PAPER TRADING' if service.use_paper_trading else 'LIVE TRADING'}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get account information
    print("\n" + "="*80)
    print("ACCOUNT INFORMATION")
    print("="*80)
    
    try:
        account = service.get_account_info()
        
        if 'error' in account:
            print(f"\n❌ Error: {account['error']}")
            return
        
        print(f"\nAccount ID: {account.get('account_id', 'N/A')}")
        print(f"Status: {account.get('status', 'N/A')}")
        print(f"Currency: {account.get('currency', 'USD')}")
        print(f"\n💰 Portfolio Value: {format_currency(account.get('portfolio_value', 0))}")
        print(f"💵 Cash: {format_currency(account.get('cash', 0))}")
        print(f"📈 Equity: {format_currency(account.get('equity', 0))}")
        print(f"💪 Buying Power: {format_currency(account.get('buying_power', 0))}")
        print(f"\nLong Market Value: {format_currency(account.get('long_market_value', 0))}")
        print(f"Short Market Value: {format_currency(account.get('short_market_value', 0))}")
        print(f"SMA: {format_currency(account.get('sma', 0))}")
        print(f"\nDay Trade Count: {account.get('day_trade_count', 0)}")
        print(f"Pattern Day Trader: {account.get('pattern_day_trader', False)}")
        print(f"Trading Blocked: {account.get('trading_blocked', False)}")
        print(f"Account Blocked: {account.get('account_blocked', False)}")
        
        # Calculate returns if we have last equity
        last_equity = account.get('last_equity', 0)
        current_equity = account.get('equity', 0)
        if last_equity > 0:
            daily_return = ((current_equity - last_equity) / last_equity) * 100
            print(f"\n📊 Daily Return: {format_percentage(daily_return)}")
            print(f"   Last Equity: {format_currency(last_equity)}")
            print(f"   Current Equity: {format_currency(current_equity)}")
        
    except Exception as e:
        print(f"\n❌ Error getting account info: {e}")
        return
    
    # Get positions
    print("\n" + "="*80)
    print("OPEN POSITIONS")
    print("="*80)
    
    try:
        positions = service.get_positions()
        
        if not positions:
            print("\n📭 No open positions")
        else:
            print(f"\n📊 Total Positions: {len(positions)}")
            print(f"\n{'Symbol':<10} {'Qty':>10} {'Entry Price':>15} {'Current Price':>15} {'Market Value':>15} {'P/L':>15} {'P/L %':>10}")
            print("-"*80)
            
            total_pnl = 0
            for pos in positions:
                symbol = pos.get('symbol', 'N/A')
                qty = pos.get('qty', 0)
                entry_price = pos.get('avg_entry_price', 0)
                current_price = pos.get('current_price', 0)
                market_value = pos.get('market_value', 0)
                unrealized_pl = pos.get('unrealized_pl', 0)
                unrealized_plpc = pos.get('unrealized_plpc', 0) * 100
                
                total_pnl += unrealized_pl
                
                print(f"{symbol:<10} {qty:>10.2f} {format_currency(entry_price):>15} "
                      f"{format_currency(current_price):>15} {format_currency(market_value):>15} "
                      f"{format_currency(unrealized_pl):>15} {format_percentage(unrealized_plpc):>10}")
            
            print("-"*80)
            print(f"{'TOTAL UNREALIZED P/L':<50} {format_currency(total_pnl):>15}")
            
    except Exception as e:
        print(f"\n❌ Error getting positions: {e}")
    
    # Get orders
    print("\n" + "="*80)
    print("RECENT ORDERS")
    print("="*80)
    
    try:
        orders = service.get_orders(limit=10, status='all')
        
        if not orders:
            print("\n📭 No recent orders")
        else:
            print(f"\n📋 Recent Orders: {len(orders)}")
            print(f"\n{'Symbol':<10} {'Side':<6} {'Qty':>10} {'Type':<10} {'Status':<12} {'Filled':>10} {'Price':>12} {'Time':>20}")
            print("-"*100)
            
            for order in orders:
                symbol = order.get('symbol', 'N/A')
                side = order.get('side', 'N/A')
                qty = order.get('qty', 0)
                order_type = order.get('order_type', 'N/A')
                status = order.get('status', 'N/A')
                filled_qty = order.get('filled_qty', 0)
                filled_avg_price = order.get('filled_avg_price', 0)
                submitted_at = order.get('submitted_at', 'N/A')
                
                if isinstance(submitted_at, str) and 'T' in submitted_at:
                    try:
                        dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                        submitted_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                print(f"{symbol:<10} {side:<6} {qty:>10.2f} {order_type:<10} {status:<12} "
                      f"{filled_qty:>10.2f} {format_currency(filled_avg_price):>12} {submitted_at:>20}")
            
    except Exception as e:
        print(f"\n❌ Error getting orders: {e}")
    
    # Get recent trades/activities
    print("\n" + "="*80)
    print("RECENT ACTIVITIES")
    print("="*80)
    
    try:
        activities = service.get_activities(activity_types=['FILL'], limit=20)
        
        if not activities:
            print("\n📭 No recent trade activities")
        else:
            print(f"\n📈 Recent Trades: {len(activities)}")
            print(f"\n{'Time':<20} {'Symbol':<10} {'Side':<6} {'Qty':>10} {'Price':>12} {'Value':>15}")
            print("-"*80)
            
            for activity in activities:
                activity_type = activity.get('activity_type', 'N/A')
                symbol = activity.get('symbol', 'N/A')
                side = activity.get('side', 'N/A')
                qty = activity.get('qty', 0)
                price = activity.get('price', 0)
                value = qty * price if qty and price else 0
                transaction_time = activity.get('transaction_time', 'N/A')
                
                if isinstance(transaction_time, str) and 'T' in transaction_time:
                    try:
                        dt = datetime.fromisoformat(transaction_time.replace('Z', '+00:00'))
                        transaction_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                print(f"{transaction_time:<20} {symbol:<10} {side:<6} {qty:>10.2f} "
                      f"{format_currency(price):>12} {format_currency(value):>15}")
            
    except Exception as e:
        print(f"\n⚠️ Could not get activities: {e}")
        print("   (This is optional - orders shown above)")
    
    # Portfolio performance
    print("\n" + "="*80)
    print("PORTFOLIO PERFORMANCE")
    print("="*80)
    
    try:
        # Get portfolio history
        portfolio_history = service.get_portfolio_history(days=30)
        
        if portfolio_history and 'equity' in portfolio_history:
            equity_history = portfolio_history['equity']
            if len(equity_history) > 1:
                initial_equity = equity_history[0]
                current_equity = equity_history[-1]
                total_return = ((current_equity - initial_equity) / initial_equity) * 100
                
                print(f"\n📊 30-Day Performance:")
                print(f"   Initial Equity: {format_currency(initial_equity)}")
                print(f"   Current Equity: {format_currency(current_equity)}")
                print(f"   Total Return: {format_percentage(total_return)}")
                
                # Calculate daily returns
                if len(equity_history) > 1:
                    returns = [(equity_history[i] - equity_history[i-1]) / equity_history[i-1] * 100 
                              for i in range(1, len(equity_history))]
                    avg_daily_return = sum(returns) / len(returns) if returns else 0
                    print(f"   Avg Daily Return: {format_percentage(avg_daily_return)}")
        else:
            print("\n📊 Portfolio history not available")
            
    except Exception as e:
        print(f"\n⚠️ Could not get portfolio history: {e}")
    
    print("\n" + "="*80)
    print("LIVE TRADING DASHBOARD COMPLETE")
    print("="*80)
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Tip: Run this script periodically to monitor live trading activity")


if __name__ == "__main__":
    view_live_trading()

