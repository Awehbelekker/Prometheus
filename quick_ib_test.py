"""
Quick IB Gateway Connection Test
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ib():
    print("\n" + "="*70)
    print("IB GATEWAY CONNECTION TEST")
    print("="*70)
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("\n[ERROR] IB library not installed")
            print("        Run: pip install ibapi")
            return
        
        print("\n[OK] IB library installed")
        
        config = {
            'host': '127.0.0.1',
            'port': 4002,
            'client_id': 1
        }
        
        print(f"\n[INFO] Attempting to connect to {config['host']}:{config['port']}...")
        print("       This will timeout in 15 seconds if Gateway not responding")
        
        broker = InteractiveBrokersBroker(config)
        
        try:
            connected = await asyncio.wait_for(broker.connect(), timeout=15.0)
            
            if connected:
                print("\n[SUCCESS] IB Gateway Connected!")
                
                # Get account info
                account = await broker.get_account()
                print(f"\nAccount Details:")
                print(f"  Equity: ${float(account.equity):,.2f}")
                print(f"  Cash: ${float(account.cash):,.2f}")
                print(f"\n[OK] IB is ready for trading!")
                
                await broker.disconnect()
                return True
            else:
                print("\n[FAILED] Could not connect to IB Gateway")
                print("\nPossible issues:")
                print("  1. Gateway/TWS not running")
                print("  2. Not logged in")
                print("  3. Wrong port (should be 4002 for live, 7497 for paper)")
                print("  4. API not enabled in settings")
                return False
                
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] IB Gateway did not respond")
            print("\nTroubleshooting:")
            print("  1. Is IB Gateway or TWS running?")
            print("  2. Are you logged in?")
            print("  3. Check File > Global Configuration > API > Settings")
            print("     - Enable ActiveX and Socket Clients: CHECKED")
            print("     - Socket port: 4002")
            print("     - Read-Only API: UNCHECKED (for trading)")
            print("  4. Try restarting IB Gateway")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_ib())
    
    if result:
        print("\n" + "="*70)
        print("IB IS READY - You can run the full launcher now!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("FIX IB BEFORE RUNNING FULL SYSTEM")
        print("="*70)
        print("\nOR: Run with Alpaca only (system will work with just Alpaca)")
