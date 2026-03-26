"""
Check Existing Positions - FIXED VERSION
Shows actual position attributes from Alpaca API
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_positions():
    print("\n" + "="*70)
    print("EXISTING POSITIONS CHECK - PRE-LAUNCH")
    print("="*70)
    
    # Check Alpaca
    print("\n[ALPACA LIVE - Account 910544927]")
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
            
            print(f"\nAccount Summary:")
            print(f"  Total Equity: ${equity:,.2f}")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Positions: {len(positions)}")
            
            if positions:
                print(f"\n{'='*70}")
                print("CURRENT HOLDINGS:")
                print(f"{'='*70}")
                
                total_market_value = 0
                total_pl = 0
                
                for i, pos in enumerate(positions, 1):
                    # Access position attributes correctly
                    symbol = pos.symbol
                    quantity = float(pos.qty)
                    current_price = float(pos.current_price)
                    market_value = float(pos.market_value)
                    avg_entry_price = float(pos.avg_entry_price)
                    unrealized_pl = float(pos.unrealized_pl)
                    unrealized_plpc = float(pos.unrealized_plpc)
                    
                    total_market_value += market_value
                    total_pl += unrealized_pl
                    
                    pl_sign = "+" if unrealized_pl >= 0 else ""
                    
                    print(f"\n{i}. {symbol}")
                    print(f"   Quantity: {quantity:,.2f} shares")
                    print(f"   Avg Entry: ${avg_entry_price:,.2f}")
                    print(f"   Current: ${current_price:,.2f}")
                    print(f"   Market Value: ${market_value:,.2f}")
                    print(f"   P/L: {pl_sign}${unrealized_pl:,.2f} ({pl_sign}{unrealized_plpc:.2%})")
                
                print(f"\n{'='*70}")
                print(f"TOTAL POSITIONS VALUE: ${total_market_value:,.2f}")
                print(f"TOTAL UNREALIZED P/L: ${total_pl:+,.2f}")
                print(f"{'='*70}")
                
            await alpaca.disconnect()
            return positions
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []

async def explain_autonomous_behavior(has_positions):
    print("\n" + "="*70)
    print("AUTONOMOUS TRADING BEHAVIOR")
    print("="*70)
    
    if has_positions:
        print("\n[CRITICAL INFORMATION]")
        print("\nYou have EXISTING positions in your Alpaca account.")
        print("\nPROMETHEUS AUTONOMOUS BEHAVIOR:")
        
        print("\n✓ PROMETHEUS WILL:")
        print("  - See your existing positions")
        print("  - Include them in total portfolio value calculations")
        print("  - Consider them when calculating available capital")
        print("  - Monitor them for informational purposes")
        
        print("\n✗ PROMETHEUS WILL NOT:")
        print("  - Automatically sell your existing positions")
        print("  - Close positions it didn't open itself")
        print("  - Modify or manage your manual holdings")
        print("  - Make decisions about positions opened before it started")
        
        print("\n[WHAT PROMETHEUS DOES AUTONOMOUSLY]:")
        print("  1. Scans markets for NEW opportunities")
        print("  2. Opens NEW positions when AI confidence >= 70%")
        print("  3. Manages positions IT opens (stop-loss, profit targets)")
        print("  4. Closes positions IT opened based on AI decisions")
        
        print("\n[YOUR EXISTING POSITIONS]:")
        print("  - Will remain untouched by Prometheus")
        print("  - You must manage them manually")
        print("  - Or manually close them before starting")
        
        print("\n[OPTIONS]:")
        print("  A) Start Prometheus now - it trades alongside your positions")
        print("  B) Manually close all positions first - full autonomous control")
        print("  C) Selectively close some - hybrid approach")
        
        print("\n[RECOMMENDATION]:")
        print("  For FULL autonomous trading, manually close existing positions")
        print("  before starting. Otherwise, Prometheus only manages NEW trades.")
        
    else:
        print("\n[EXCELLENT] No existing positions found!")
        print("\nPROMETHEUS WILL:")
        print("  ✓ Start with clean slate")
        print("  ✓ Full autonomous control")
        print("  ✓ Manage ALL positions it opens")
        print("  ✓ Complete freedom to trade")

async def main():
    positions = await check_positions()
    await explain_autonomous_behavior(len(positions) > 0)
    
    print("\n" + "="*70)
    if positions:
        print(f"[READY] {len(positions)} existing positions detected")
        print("        Prometheus will trade alongside them")
    else:
        print("[READY] Clean slate - full autonomous control")
    print("="*70)
    print("\nNext step: python START_LIVE_TRADING_NOW.py")
    print()

if __name__ == "__main__":
    asyncio.run(main())
