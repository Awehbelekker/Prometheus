"""
Verify All Positions Are Closed
Checks both Alpaca and IB for zero positions
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_all_closed():
    print("\n" + "="*70)
    print("VERIFYING ALL POSITIONS CLOSED")
    print("="*70)
    
    all_clear = True
    total_cash = 0
    
    # Check Alpaca
    print("\n[1/2] CHECKING ALPACA...")
    try:
        from brokers.alpaca_broker import AlpacaBroker
        
        alpaca_config = {
            'api_key': os.getenv('ALPACA_API_KEY'),
            'secret_key': os.getenv('ALPACA_SECRET_KEY'),
            'base_url': 'https://api.alpaca.markets',
            'paper_trading': False
        }
        
        alpaca = AlpacaBroker(alpaca_config)
        if await alpaca.connect():
            account = await alpaca.get_account()
            positions = await alpaca.get_positions()
            
            equity = float(account.equity)
            cash = float(account.cash)
            
            print(f"  Account: 910544927")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Positions: {len(positions)}")
            
            if len(positions) == 0:
                print(f"  [OK] All Alpaca positions closed!")
                total_cash += equity
            else:
                print(f"  [WARNING] Still have {len(positions)} position(s):")
                for pos in positions:
                    print(f"    - {pos.symbol}")
                all_clear = False
            
            await alpaca.disconnect()
    except Exception as e:
        print(f"  [ERROR] {e}")
        all_clear = False
    
    # Check IB
    print("\n[2/2] CHECKING IB TWS...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        ib_port = int(os.getenv('IB_PORT', '4002'))
        ib_config = {
            'host': '127.0.0.1',
            'port': ib_port,
            'client_id': 1
        }
        
        ib = InteractiveBrokersBroker(ib_config)
        if await asyncio.wait_for(ib.connect(), timeout=10.0):
            account = await ib.get_account()
            positions = await ib.get_positions()
            
            equity = float(account.equity)
            cash = float(account.cash)
            
            print(f"  Account: U21922116")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Positions: {len(positions)}")
            
            if len(positions) == 0:
                print(f"  [OK] All IB positions closed!")
                total_cash += equity
            else:
                print(f"  [WARNING] Still have {len(positions)} position(s):")
                for symbol in positions.keys():
                    print(f"    - {symbol}")
                all_clear = False
            
            await ib.disconnect()
    except Exception as e:
        print(f"  [ERROR] {str(e)[:100]}")
        all_clear = False
    
    # Results
    print("\n" + "="*70)
    if all_clear:
        print("STATUS: ALL CLEAR - CLEAN SLATE ACHIEVED!")
        print("="*70)
        print(f"\nTotal Available Capital: ${total_cash:,.2f}")
        print("\nPROMETHEUS IS READY FOR MAXIMUM POWER LAUNCH!")
        print("\nNext step:")
        print("  python START_LIVE_TRADING_NOW.py")
        print("\nExpected daily profit potential:")
        print(f"  Conservative (3-5%): ${total_cash * 0.03:,.2f} - ${total_cash * 0.05:,.2f}")
        print(f"  Aggressive (8-10%): ${total_cash * 0.08:,.2f} - ${total_cash * 0.10:,.2f}")
    else:
        print("STATUS: POSITIONS STILL OPEN")
        print("="*70)
        print("\nPlease close remaining positions and run this again.")
        print("Once all positions are closed, you'll see 'ALL CLEAR' message.")
    
    print()
    return all_clear

if __name__ == "__main__":
    result = asyncio.run(verify_all_closed())
    exit(0 if result else 1)
