#!/usr/bin/env python3
"""
PROMETHEUS Broker Connection Test - Simple Version
Tests both Alpaca and Interactive Brokers connections
"""

import asyncio
import os
import sys
from datetime import datetime
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brokers.alpaca_broker import AlpacaBroker
from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_alpaca_connection():
    """Test Alpaca broker connection"""
    print("\n" + "="*60)
    print("TESTING ALPACA BROKER CONNECTION")
    print("="*60)
    
    try:
        # Get credentials from environment
        api_key = os.getenv('ALPACA_API_KEY', 'DEMO_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY', 'DEMO_SECRET')
        
        if api_key == 'DEMO_KEY' or secret_key == 'DEMO_SECRET':
            print("WARNING: Using demo credentials - limited functionality")
        
        # Create broker instance
        config = {
            'api_key': api_key,
            'secret_key': secret_key,
            'paper_trading': True  # Always start with paper trading
        }
        
        broker = AlpacaBroker(config)
        
        # Test connection
        print("Connecting to Alpaca...")
        connected = await broker.connect()
        
        if connected:
            print("SUCCESS: Alpaca connection successful!")
            
            # Get account info
            try:
                account = await broker.get_account()
                print(f"   Account ID: {account.account_id}")
                print(f"   Buying Power: ${account.buying_power:,.2f}")
                print(f"   Cash: ${account.cash:,.2f}")
                print(f"   Portfolio Value: ${account.portfolio_value:,.2f}")
                print(f"   Equity: ${account.equity:,.2f}")
                print(f"   Day Trade Count: {account.day_trade_count}")
                print(f"   Pattern Day Trader: {account.pattern_day_trader}")
                
                # Test market data
                print("\nTesting market data...")
                market_data = await broker.get_market_data('AAPL')
                if market_data:
                    print(f"   AAPL Price: ${market_data.get('price', 'N/A')}")
                    print(f"   Volume: {market_data.get('volume', 'N/A')}")
                    print(f"   Timestamp: {market_data.get('timestamp', 'N/A')}")
                
                return True
                
            except Exception as e:
                print(f"ERROR: Error getting account info: {e}")
                return False
        else:
            print("FAILED: Alpaca connection failed!")
            return False
            
    except Exception as e:
        print(f"ERROR: Alpaca test failed: {e}")
        return False
    finally:
        if 'broker' in locals():
            await broker.disconnect()

async def test_ib_connection():
    """Test Interactive Brokers connection"""
    print("\n" + "="*60)
    print("TESTING INTERACTIVE BROKERS CONNECTION")
    print("="*60)
    
    if not IB_AVAILABLE:
        print("ERROR: Interactive Brokers API not available")
        print("   Install with: pip install ibapi")
        return False
    
    try:
        # Get credentials from environment
        host = os.getenv('IB_HOST', '127.0.0.1')
        port = int(os.getenv('IB_PORT', '7496'))
        client_id = int(os.getenv('IB_CLIENT_ID', '1'))
        
        print(f"Connecting to IB Gateway at {host}:{port} (Client ID: {client_id})")
        
        # Create broker instance
        config = {
            'host': host,
            'port': port,
            'client_id': client_id,
            'account': os.getenv('IB_ACCOUNT', 'U21922116')
        }
        
        broker = InteractiveBrokersBroker(config)
        
        # Test connection
        connected = await broker.connect()
        
        if connected:
            print("SUCCESS: Interactive Brokers connection successful!")
            
            # Get account info
            try:
                account = await broker.get_account()
                print(f"   Account ID: {account.account_id}")
                print(f"   Buying Power: ${account.buying_power:,.2f}")
                print(f"   Cash: ${account.cash:,.2f}")
                print(f"   Portfolio Value: ${account.portfolio_value:,.2f}")
                print(f"   Equity: ${account.equity:,.2f}")
                print(f"   Day Trade Count: {account.day_trade_count}")
                print(f"   Pattern Day Trader: {account.pattern_day_trader}")
                
                # Test market data
                print("\nTesting market data...")
                market_data = await broker.get_market_data('AAPL')
                if market_data:
                    print(f"   AAPL Price: ${market_data.get('price', 'N/A')}")
                    print(f"   Volume: {market_data.get('volume', 'N/A')}")
                    print(f"   Timestamp: {market_data.get('timestamp', 'N/A')}")
                
                return True
                
            except Exception as e:
                print(f"ERROR: Error getting account info: {e}")
                return False
        else:
            print("FAILED: Interactive Brokers connection failed!")
            print("   Make sure IB Gateway/TWS is running on port 7496")
            return False
            
    except Exception as e:
        print(f"ERROR: IB test failed: {e}")
        return False
    finally:
        if 'broker' in locals():
            await broker.disconnect()

async def test_order_creation():
    """Test order creation (without execution)"""
    print("\n" + "="*60)
    print("TESTING ORDER CREATION")
    print("="*60)
    
    try:
        from brokers.universal_broker_interface import Order, OrderSide, OrderType
        
        # Create a test order
        test_order = Order(
            symbol='AAPL',
            quantity=1.0,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force='day'
        )
        
        print("SUCCESS: Order object created successfully:")
        print(f"   Symbol: {test_order.symbol}")
        print(f"   Quantity: {test_order.quantity}")
        print(f"   Side: {test_order.side.value}")
        print(f"   Type: {test_order.order_type.value}")
        print(f"   Time in Force: {test_order.time_in_force}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Order creation test failed: {e}")
        return False

async def main():
    """Run all broker connection tests"""
    print("PROMETHEUS BROKER CONNECTION TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {
        'alpaca': False,
        'interactive_brokers': False,
        'order_creation': False
    }
    
    # Test order creation first
    results['order_creation'] = await test_order_creation()
    
    # Test Alpaca connection
    results['alpaca'] = await test_alpaca_connection()
    
    # Test Interactive Brokers connection
    results['interactive_brokers'] = await test_ib_connection()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for broker, status in results.items():
        status_text = "PASS" if status else "FAIL"
        print(f"{status_text}: {broker.replace('_', ' ').title()}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("SUCCESS: ALL BROKER CONNECTIONS SUCCESSFUL!")
        print("   The PROMETHEUS trading system is ready for operation.")
    elif passed_tests > 0:
        print("WARNING: PARTIAL SUCCESS - Some brokers are working")
        print("   Check failed connections and retry.")
    else:
        print("ERROR: ALL BROKER CONNECTIONS FAILED")
        print("   Check broker configurations and network connectivity.")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())

