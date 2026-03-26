#!/usr/bin/env python
"""
🏦 PROMETHEUS - Interactive Brokers Connection Test
"""
import asyncio
import sys
import socket

def test_port(port):
    """Test if a port is accessible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

async def test_ib_connection():
    print("="*70)
    print("🏦 INTERACTIVE BROKERS CONNECTION TEST")
    print("="*70)
    
    # Test port connectivity
    print("\n📡 Port Check:")
    if test_port(4002):
        print("   ✅ Port 4002 (Gateway Live) is OPEN and accepting connections")
    elif test_port(7497):
        print("   ✅ Port 7497 (TWS) is OPEN and accepting connections")
    else:
        print("   ❌ No IB ports accessible")
        return
    
    # Try to connect using our broker
    print("\n🔗 Testing API Connection...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("   ❌ ibapi module not installed")
            print("   Run: pip install ibapi")
            return
        
        # Configure IB connection - Port 4002 (Gateway Live)
        ib_config = {
            'host': '127.0.0.1',
            'port': 4002,
            'client_id': 99,  # Use unique client ID to avoid conflicts
            'paper_trading': False,  # Live trading (account U21922116)
            'account_id': 'U21922116'
        }
        
        print(f"   Connecting to {ib_config['host']}:{ib_config['port']}...")
        ib_broker = InteractiveBrokersBroker(ib_config)
        
        connected = await ib_broker.connect()
        
        if connected:
            print("   ✅ Connected to Interactive Brokers!")
            
            # Get account info
            print("\n💰 Account Information:")
            try:
                account = await ib_broker.get_account()
                print(f"   Account ID: {account.account_id}")
                print(f"   Cash: ${account.cash:.2f}")
                print(f"   Buying Power: ${account.buying_power:.2f}")
                print(f"   Portfolio Value: ${account.portfolio_value:.2f}")
            except Exception as e:
                print(f"   ⚠️ Could not get account info: {e}")
            
            # Get positions
            print("\n📈 Positions:")
            try:
                positions = await ib_broker.get_positions()
                if positions:
                    for p in positions:
                        print(f"   • {p.symbol}: {p.quantity} @ ${p.avg_price:.4f}")
                else:
                    print("   No positions")
            except Exception as e:
                print(f"   ⚠️ Could not get positions: {e}")
            
            # Get open orders
            print("\n📋 Open Orders:")
            try:
                orders = await ib_broker.get_orders()
                if orders:
                    for o in orders:
                        print(f"   • {o.symbol}: {o.side} {o.quantity} @ {o.order_type}")
                else:
                    print("   No open orders")
            except Exception as e:
                print(f"   ⚠️ Could not get orders: {e}")
            
            # Disconnect
            await ib_broker.disconnect()
            print("\n✅ Test complete - IB is ready for trading!")
        else:
            print("   ❌ Connection failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ib_connection())

