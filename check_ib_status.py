"""
Quick IB Status Check (Non-Interactive)
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_ib():
    print("\n" + "="*70)
    print("IB GATEWAY STATUS CHECK")
    print("="*70)
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("\n[ERROR] IB library not installed")
            print("        Run: pip install ibapi")
            return False
        
        print("\n[OK] IB library installed")
        
        # Get port from environment (defaults to 7496 for TWS Live)
        ib_port = int(os.getenv('IB_PORT', '7496'))
        
        config = {
            'host': '127.0.0.1',
            'port': ib_port,
            'client_id': 1
        }
        
        print(f"\n[TEST] Connecting to {config['host']}:{config['port']}...")
        print("       Account: U21922116")
        print("       Timeout: 10 seconds")
        
        broker = InteractiveBrokersBroker(config)
        
        try:
            connected = await asyncio.wait_for(broker.connect(), timeout=10.0)
            
            if connected:
                print("\n" + "="*70)
                print("SUCCESS - IB GATEWAY CONNECTED!")
                print("="*70)
                
                account = await broker.get_account()
                
                print(f"\nAccount: U21922116")
                print(f"Equity: ${float(account.equity):,.2f}")
                print(f"Cash: ${float(account.cash):,.2f}")
                
                print("\n[OK] IB is ready for trading!")
                print("="*70)
                
                await broker.disconnect()
                return True
                
            else:
                print("\n[FAILED] Could not connect")
                return False
                
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] IB Gateway not responding")
            print("\n[STATUS] Gateway appears to be:")
            print("  - Not running, OR")
            print("  - Not logged in, OR")
            print("  - API not enabled")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_ib())
    
    if result:
        print("\n[READY] IB U21922116 can be added to trading system!")
    else:
        print("\n[INFO] IB not available - system continues with Alpaca only")
        print("\nTo enable IB:")
        print("  1. Open IB Gateway")
        print("  2. Login to account U21922116")
        print("  3. Configure > API > Enable")
        print("  4. Restart this test")
