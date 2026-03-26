"""
Test IB Connection for Account U21922116
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ib_account():
    print("\n" + "="*70)
    print("IB ACCOUNT U21922116 - CONNECTION TEST")
    print("="*70)
    
    # Check if IB Gateway is configured
    print("\n[PRE-CHECK] Before we test...")
    print("1. Is IB Gateway or TWS running? (Y/N)")
    response = input("   Answer: ").strip().upper()
    
    if response != 'Y':
        print("\n[STOP] Please start IB Gateway first!")
        print("       Then run this test again.")
        return False
    
    print("\n2. Are you logged in? (Y/N)")
    response = input("   Answer: ").strip().upper()
    
    if response != 'Y':
        print("\n[STOP] Please login to IB Gateway first!")
        return False
    
    print("\n3. Is API enabled in Configure > API > Settings? (Y/N)")
    response = input("   Answer: ").strip().upper()
    
    if response != 'Y':
        print("\n[HELP] Enable API:")
        print("       1. Click Configure (gear icon)")
        print("       2. Go to: API > Settings")
        print("       3. Check: 'Enable ActiveX and Socket Clients'")
        print("       4. Socket port: 4002")
        print("       5. Click OK")
        print("       6. Restart Gateway")
        print("\n       Then run this test again.")
        return False
    
    # Now test connection
    print("\n[TESTING] Attempting to connect to IB...")
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("\n[ERROR] IB library not installed")
            print("        Run: pip install ibapi")
            return False
        
        config = {
            'host': '127.0.0.1',
            'port': 4002,  # LIVE port
            'client_id': 1
        }
        
        print(f"\n   Host: {config['host']}")
        print(f"   Port: {config['port']} (LIVE)")
        print(f"   Expected Account: U21922116")
        print("\n   Connecting... (15 second timeout)")
        
        broker = InteractiveBrokersBroker(config)
        
        try:
            connected = await asyncio.wait_for(broker.connect(), timeout=15.0)
            
            if connected:
                print("\n" + "="*70)
                print("SUCCESS - IB CONNECTED!")
                print("="*70)
                
                # Get account details
                account = await broker.get_account()
                
                print(f"\nAccount Number: {account.account_id if hasattr(account, 'account_id') else 'U21922116'}")
                print(f"Equity: ${float(account.equity):,.2f}")
                print(f"Cash: ${float(account.cash):,.2f}")
                print(f"Buying Power: ${float(account.buying_power if hasattr(account, 'buying_power') else account.cash):,.2f}")
                
                print("\n" + "="*70)
                print("IB ACCOUNT U21922116 IS READY FOR TRADING!")
                print("="*70)
                
                print("\n[NEXT STEP] Run the full system:")
                print("            python launch_full_system_maximum_performance.py")
                
                await broker.disconnect()
                return True
                
            else:
                print("\n[FAILED] Connection failed")
                print("\nTroubleshooting:")
                print("  1. Is Gateway still logged in?")
                print("  2. Check API is enabled (see setup_ib_account_U21922116.md)")
                print("  3. Try restarting Gateway")
                return False
                
        except asyncio.TimeoutError:
            print("\n[TIMEOUT] Gateway not responding")
            print("\nMost common causes:")
            print("  1. API not enabled in settings")
            print("  2. Wrong port (should be 4002 for LIVE)")
            print("  3. Gateway not fully logged in")
            print("\nSee: setup_ib_account_U21922116.md for full instructions")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nThis test will verify IB Gateway connection for account U21922116")
    print("Make sure IB Gateway is running and logged in!\n")
    
    result = asyncio.run(test_ib_account())
    
    if result:
        print("\n[SUCCESS] You can now use both Alpaca + IB for maximum power!")
    else:
        print("\n[INFO] System still works with Alpaca only")
        print("       Fix IB using: setup_ib_account_U21922116.md")
        print("       Then test again with: python test_ib_U21922116.py")
