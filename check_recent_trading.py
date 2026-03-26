#!/usr/bin/env python3
"""
Check Recent Trading Activity for Alpaca and Interactive Brokers
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_alpaca_trades():
    """Check Alpaca trading activity"""
    print("\n" + "="*80)
    print("ALPACA TRADING ACTIVITY")
    print("="*80)
    
    # Check multiple possible database locations
    db_paths = [
        "databases/prometheus_trading.db",
        "databases/live_trading.db",
        "databases/paper_trading.db",
        "prometheus_trading.db",
        "live_trading.db",
        "paper_trading.db",
        "databases/alpaca_requests.db",
        "alpaca_requests.db"
    ]
    
    found_trades = False
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check for trades in various table structures
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Try different table/column combinations
            queries = [
                ("SELECT * FROM trades WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM trading_history WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM live_trades WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM orders WHERE created_at >= ? ORDER BY created_at DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM alpaca_orders WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
            ]
            
            for query, params in queries:
                try:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    if rows:
                        found_trades = True
                        print(f"\nFound {len(rows)} trades in {db_path}:")
                        print("-" * 80)
                        
                        # Get column names
                        cursor.execute(query.replace('*', '1').replace('LIMIT 20', 'LIMIT 1'), params)
                        columns = [description[0] for description in cursor.description]
                        
                        for row in rows[:10]:  # Show first 10
                            trade_dict = dict(zip(columns, row))
                            print(f"  Trade: {json.dumps(trade_dict, indent=2, default=str)}")
                            print()
                        break
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
            
        except Exception as e:
            continue
    
    if not found_trades:
        print("  No recent Alpaca trades found in databases")
        print("  Checking Alpaca API directly...")
        
        # Try to check Alpaca API directly
        try:
            import os
            from alpaca_trade_api import REST
            
            api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
            secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
            
            if api_key and secret_key:
                api = REST(api_key, secret_key, 'https://paper-api.alpaca.markets', api_version='v2')
                
                # Get recent orders
                yesterday = datetime.now() - timedelta(days=1)
                orders = api.list_orders(
                    status='all',
                    after=yesterday.isoformat(),
                    limit=50
                )
                
                if orders:
                    print(f"\n  Found {len(orders)} orders from Alpaca API:")
                    print("-" * 80)
                    for order in orders[:10]:
                        print(f"  Order ID: {order.id}")
                        print(f"    Symbol: {order.symbol}")
                        print(f"    Side: {order.side}")
                        print(f"    Quantity: {order.qty}")
                        print(f"    Status: {order.status}")
                        print(f"    Filled: {order.filled_qty}")
                        print(f"    Price: ${order.filled_avg_price if order.filled_avg_price else 'N/A'}")
                        print(f"    Time: {order.created_at}")
                        print()
                else:
                    print("  No orders found from Alpaca API yesterday")
            else:
                print("  Alpaca API credentials not found")
        except Exception as e:
            print(f"  Could not check Alpaca API: {e}")

def check_ib_trades():
    """Check Interactive Brokers trading activity"""
    print("\n" + "="*80)
    print("INTERACTIVE BROKERS TRADING ACTIVITY")
    print("="*80)
    
    # Check multiple possible database locations
    db_paths = [
        "databases/prometheus_trading.db",
        "databases/live_trading.db",
        "databases/paper_trading.db",
        "prometheus_trading.db",
        "live_trading.db",
        "paper_trading.db"
    ]
    
    found_trades = False
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Try different table/column combinations for IB
            queries = [
                ("SELECT * FROM trades WHERE broker = 'IB' AND timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM trading_history WHERE broker = 'IB' AND timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM live_trades WHERE broker = 'IB' AND timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM ib_orders WHERE timestamp >= ? ORDER BY timestamp DESC LIMIT 20", [yesterday]),
                ("SELECT * FROM orders WHERE broker = 'InteractiveBrokers' AND created_at >= ? ORDER BY created_at DESC LIMIT 20", [yesterday]),
            ]
            
            for query, params in queries:
                try:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    if rows:
                        found_trades = True
                        print(f"\nFound {len(rows)} trades in {db_path}:")
                        print("-" * 80)
                        
                        # Get column names
                        cursor.execute(query.replace('*', '1').replace('LIMIT 20', 'LIMIT 1'), params)
                        columns = [description[0] for description in cursor.description]
                        
                        for row in rows[:10]:  # Show first 10
                            trade_dict = dict(zip(columns, row))
                            print(f"  Trade: {json.dumps(trade_dict, indent=2, default=str)}")
                            print()
                        break
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
            
        except Exception as e:
            continue
    
    if not found_trades:
        print("  No recent IB trades found in databases")
        print("  Note: IB trades require TWS/Gateway connection to query")

def check_portfolio_performance():
    """Check overall portfolio performance"""
    print("\n" + "="*80)
    print("PORTFOLIO PERFORMANCE SUMMARY")
    print("="*80)
    
    db_paths = [
        "databases/portfolio_persistence.db",
        "databases/user_portfolios.db",
        "databases/prometheus_trading.db",
        "portfolio_persistence.db",
        "user_portfolios.db"
    ]
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to get portfolio data
            queries = [
                "SELECT * FROM user_portfolios ORDER BY last_updated DESC LIMIT 5",
                "SELECT * FROM portfolios ORDER BY updated_at DESC LIMIT 5",
            ]
            
            for query in queries:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    if rows:
                        print(f"\nPortfolio data from {db_path}:")
                        print("-" * 80)
                        
                        columns = [description[0] for description in cursor.description]
                        for row in rows:
                            portfolio = dict(zip(columns, row))
                            print(f"  User: {portfolio.get('user_id', 'N/A')}")
                            print(f"    Value: ${portfolio.get('current_value', portfolio.get('portfolio_value', 0)):.2f}")
                            print(f"    Return: {portfolio.get('total_return_percent', portfolio.get('return_percent', 0)):.2f}%")
                            print(f"    Last Updated: {portfolio.get('last_updated', portfolio.get('updated_at', 'N/A'))}")
                            print()
                        break
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
            
        except Exception as e:
            continue

def main():
    print("\n" + "="*80)
    print("RECENT TRADING ACTIVITY REPORT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    check_alpaca_trades()
    check_ib_trades()
    check_portfolio_performance()
    
    print("\n" + "="*80)
    print("REPORT COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()



