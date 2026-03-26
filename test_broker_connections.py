"""
Quick Broker Connection Test
Tests Alpaca and IB connectivity before trading
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def test_alpaca():
    """Test Alpaca connection"""
    print("\n" + "="*60)
    print("TESTING ALPACA BROKER")
    print("="*60)
    
    try:
        from brokers.alpaca_broker import AlpacaBroker
        
        config = {
            'api_key': os.getenv('ALPACA_API_KEY'),
            'secret_key': os.getenv('ALPACA_SECRET_KEY'),
            'paper_trading': True  # Always test with paper first!
        }
        
        if not config['api_key'] or not config['secret_key']:
            print("[ERROR] Alpaca API keys not found in .env")
            return False
        
        print("[INFO] Initializing Alpaca...")
        broker = AlpacaBroker(config)
        
        print("[INFO] Connecting...")
        connected = await broker.connect()
        
        if not connected:
            print("[FAILED] Could not connect to Alpaca")
            return False
        
        print("[OK] Connected successfully!")
        
        # Get account info
        print("\n[INFO] Fetching account information...")
        account = await broker.get_account()
        
        print(f"\n[ACCOUNT INFO]")
        print(f"  Equity: ${float(account.equity):,.2f}")
        print(f"  Cash: ${float(account.cash):,.2f}")
        print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        
        # Test market data
        print("\n[INFO] Testing market data (AAPL)...")
        try:
            quote = await broker.get_quote('AAPL')
            if quote:
                print(f"  AAPL: ${quote.price:.2f}")
        except Exception as e:
            print(f"  [WARNING] Market data test: {e}")
        
        print("\n[SUCCESS] Alpaca is READY FOR TRADING!")
        return True
        
    except Exception as e:
        print(f"\n[FAILED] Alpaca test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ib():
    """Test IB connection"""
    print("\n" + "="*60)
    print("TESTING INTERACTIVE BROKERS")
    print("="*60)
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("[INFO] IB library not installed")
            print("[INFO] Install with: pip install ibapi")
            return False
        
        config = {
            'host': os.getenv('IB_HOST', '127.0.0.1'),
            'port': int(os.getenv('IB_PORT', 7497)),  # 7497 = paper trading
            'client_id': 1
        }
        
        print(f"[INFO] Connecting to IB Gateway/TWS at {config['host']}:{config['port']}...")
        print("[INFO] Note: TWS or IB Gateway must be running!")
        
        broker = InteractiveBrokersBroker(config)
        
        # Try to connect with timeout
        try:
            connected = await asyncio.wait_for(broker.connect(), timeout=10.0)
            
            if not connected:
                print("[FAILED] Could not connect to IB")
                print("[INFO] Make sure TWS or IB Gateway is running")
                return False
            
            print("[OK] Connected successfully!")
            
            # Get account info
            print("\n[INFO] Fetching account information...")
            account = await broker.get_account()
            
            print(f"\n[ACCOUNT INFO]")
            print(f"  Equity: ${float(account.equity):,.2f}")
            print(f"  Cash: ${float(account.cash):,.2f}")
            
            print("\n[SUCCESS] IB is READY FOR TRADING!")
            return True
            
        except asyncio.TimeoutError:
            print("[FAILED] Connection timeout (10s)")
            print("[INFO] Is TWS or IB Gateway running?")
            print("[INFO] Check the port: 7497 (paper) or 7496 (live)")
            return False
        
    except Exception as e:
        print(f"\n[FAILED] IB test failed: {e}")
        return False

async def main():
    print("\n" + "="*60)
    print("PROMETHEUS BROKER CONNECTION TEST")
    print("="*60)
    print("\nThis will test your broker connections.")
    print("No trades will be placed.\n")
    
    # Test Alpaca
    alpaca_ok = await test_alpaca()
    
    # Test IB
    ib_ok = await test_ib()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\nAlpaca: {'[OK] READY' if alpaca_ok else '[FAILED] NOT READY'}")
    print(f"IB:     {'[OK] READY' if ib_ok else '[FAILED] NOT READY'}")
    
    if alpaca_ok or ib_ok:
        print("\n[SUCCESS] At least one broker is ready!")
        print("\nYou can now run the autonomous system.")
        return 0
    else:
        print("\n[ERROR] NO BROKERS READY!")
        print("\nFix broker connections before trading.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
