"""
Verify All Brokers Are Live (Not Paper Trading)
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_brokers():
    print("\n" + "="*70)
    print("VERIFYING ALL BROKERS - LIVE MODE")
    print("="*70)
    
    brokers_status = {}
    
    # Check Alpaca
    print("\n[1/2] Checking Alpaca...")
    try:
        from brokers.alpaca_broker import AlpacaBroker
        
        api_key = os.getenv('ALPACA_API_KEY', 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not secret_key:
            print("[WARNING] Alpaca: Secret key not in .env")
            print("   Will be requested when launching")
            brokers_status['alpaca'] = 'pending_key'
        else:
            config = {
                'api_key': api_key,
                'secret_key': secret_key,
                'paper_trading': False  # LIVE!
            }
            
            broker = AlpacaBroker(config)
            connected = await broker.connect()
            
            if connected:
                account = await broker.get_account()
                equity = float(account.equity)
                
                print(f"✅ Alpaca: LIVE ACCOUNT")
                print(f"   Endpoint: https://api.alpaca.markets (LIVE)")
                print(f"   Status: {account.status}")
                print(f"   Equity: ${equity:,.2f}")
                print(f"   Buying Power: ${float(account.buying_power):,.2f}")
                
                brokers_status['alpaca'] = {
                    'status': 'live',
                    'connected': True,
                    'equity': equity
                }
            else:
                print("❌ Alpaca: Connection failed")
                brokers_status['alpaca'] = 'failed'
                
    except Exception as e:
        print(f"❌ Alpaca Error: {e}")
        brokers_status['alpaca'] = f'error: {e}'
    
    # Check IB
    print("\n[2/2] Checking Interactive Brokers...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print("[WARNING] IB: Library not installed")
            brokers_status['ib'] = 'not_installed'
        else:
            config = {
                'host': os.getenv('IB_HOST', '127.0.0.1'),
                'port': int(os.getenv('IB_PORT', 4002)),
                'client_id': 1
            }
            
            print(f"   Connecting to {config['host']}:{config['port']}...")
            print("   (IB Gateway/TWS must be running)")
            
            broker = InteractiveBrokersBroker(config)
            
            try:
                connected = await asyncio.wait_for(broker.connect(), timeout=10.0)
                
                if connected:
                    account = await broker.get_account()
                    equity = float(account.equity)
                    
                    # Check if paper or live based on port
                    if config['port'] == 7497 or config['port'] == 4002:
                        mode = "PAPER" if config['port'] == 7497 else "LIVE/PAPER (check TWS)"
                    else:
                        mode = "LIVE"
                    
                    print(f"✅ IB: CONNECTED")
                    print(f"   Port: {config['port']} ({mode})")
                    print(f"   Equity: ${equity:,.2f}")
                    print(f"   [WARNING] Check TWS/Gateway login to confirm LIVE vs PAPER")
                    
                    brokers_status['ib'] = {
                        'status': 'connected',
                        'port': config['port'],
                        'equity': equity
                    }
                else:
                    print("❌ IB: Could not connect")
                    print("   Make sure TWS/IB Gateway is running")
                    brokers_status['ib'] = 'not_connected'
                    
            except asyncio.TimeoutError:
                print("❌ IB: Connection timeout")
                print("   Make sure TWS/IB Gateway is running")
                brokers_status['ib'] = 'timeout'
                
    except Exception as e:
        print(f"❌ IB Error: {e}")
        brokers_status['ib'] = f'error: {e}'
    
    # Summary
    print("\n" + "="*70)
    print("BROKER STATUS SUMMARY")
    print("="*70)
    
    alpaca_ready = isinstance(brokers_status.get('alpaca'), dict)
    ib_ready = isinstance(brokers_status.get('ib'), dict)
    
    if alpaca_ready:
        print("✅ Alpaca: LIVE & READY")
        print(f"   ${brokers_status['alpaca']['equity']:,.2f} available")
    else:
        print(f"[WARNING] Alpaca: {brokers_status.get('alpaca', 'Unknown')}")
    
    if ib_ready:
        print("✅ IB: CONNECTED")
        print(f"   ${brokers_status['ib']['equity']:,.2f} available")
        print("   ⚠️  Verify in TWS if LIVE or PAPER account")
    else:
        print(f"[WARNING] IB: {brokers_status.get('ib', 'Unknown')}")
    
    print("="*70)
    
    if alpaca_ready or ib_ready:
        print("\n✅ At least one broker is ready for live trading!")
        
        if alpaca_ready and not ib_ready:
            print("[INFO] Autonomous system will use: Alpaca only")
        elif ib_ready and not alpaca_ready:
            print("[INFO] Autonomous system will use: IB only")
        else:
            print("[INFO] Autonomous system will use: Both brokers")
        
        print("\n[SUCCESS] You can now start live trading!")
        print("   Run: python launch_autonomous_live_trading.py")
        
        return True
    else:
        print("\n❌ No brokers ready for trading")
        print("   Fix broker connections before starting")
        return False

if __name__ == "__main__":
    asyncio.run(verify_brokers())
