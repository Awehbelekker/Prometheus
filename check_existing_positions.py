"""
Check Existing Positions Across All Brokers
Shows what positions exist BEFORE starting autonomous trading
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_all_positions():
    print("\n" + "="*70)
    print("CHECKING EXISTING POSITIONS - PRE-LAUNCH")
    print("="*70)
    
    total_positions = []
    
    # 1. Check Alpaca Positions
    print("\n[1/2] ALPACA POSITIONS...")
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
            
            print(f"  Account: 910544927")
            print(f"  Equity: ${float(account.equity):,.2f}")
            print(f"  Cash: ${float(account.cash):,.2f}")
            print(f"  Positions: {len(positions)}")
            
            if positions:
                print(f"\n  Current Holdings:")
                for pos in positions:
                    symbol = pos.symbol
                    qty = float(pos.qty)
                    current_price = float(pos.current_price)
                    market_value = float(pos.market_value)
                    unrealized_pl = float(pos.unrealized_pl)
                    unrealized_plpc = float(pos.unrealized_plpc)
                    
                    print(f"\n    {symbol}:")
                    print(f"      Quantity: {qty}")
                    print(f"      Current Price: ${current_price:,.2f}")
                    print(f"      Market Value: ${market_value:,.2f}")
                    print(f"      Unrealized P/L: ${unrealized_pl:,.2f} ({unrealized_plpc:.2%})")
                    
                    total_positions.append({
                        'broker': 'Alpaca',
                        'symbol': symbol,
                        'qty': qty,
                        'value': market_value,
                        'pl': unrealized_pl
                    })
            else:
                print(f"  [OK] No existing positions in Alpaca")
            
            await alpaca.disconnect()
    except Exception as e:
        print(f"  [ERROR] Alpaca: {e}")
    
    # 2. Check IB Positions
    print("\n[2/2] IB TWS POSITIONS...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        ib_port = int(os.getenv('IB_PORT', '7496'))
        ib_config = {
            'host': '127.0.0.1',
            'port': ib_port,
            'client_id': 1
        }
        
        ib = InteractiveBrokersBroker(ib_config)
        if await asyncio.wait_for(ib.connect(), timeout=10.0):
            account = await ib.get_account()
            positions = await ib.get_positions()
            
            print(f"  Account: U21922116")
            print(f"  Equity: ${float(account.equity):,.2f}")
            print(f"  Cash: ${float(account.cash):,.2f}")
            print(f"  Positions: {len(positions)}")
            
            if positions:
                print(f"\n  Current Holdings:")
                for symbol, pos_data in positions.items():
                    qty = pos_data.get('quantity', 0)
                    market_value = pos_data.get('market_value', 0)
                    avg_cost = pos_data.get('avg_cost', 0)
                    
                    print(f"\n    {symbol}:")
                    print(f"      Quantity: {qty}")
                    print(f"      Market Value: ${market_value:,.2f}")
                    print(f"      Avg Cost: ${avg_cost:,.2f}")
                    
                    total_positions.append({
                        'broker': 'IB',
                        'symbol': symbol,
                        'qty': qty,
                        'value': market_value,
                        'pl': market_value - (avg_cost * abs(qty))
                    })
            else:
                print(f"  [OK] No existing positions in IB")
            
            await ib.disconnect()
        else:
            print(f"  [INFO] IB not connected - cannot check positions")
    except Exception as e:
        print(f"  [INFO] IB not available: {str(e)[:50]}")
    
    # Summary
    print("\n" + "="*70)
    print("POSITION SUMMARY")
    print("="*70)
    
    if total_positions:
        print(f"\n[IMPORTANT] You have {len(total_positions)} existing position(s):")
        total_value = sum(p['value'] for p in total_positions)
        total_pl = sum(p['pl'] for p in total_positions)
        
        for p in total_positions:
            print(f"  - {p['symbol']} ({p['broker']}): {p['qty']} shares, ${p['value']:,.2f}")
        
        print(f"\n  Total Market Value: ${total_value:,.2f}")
        print(f"  Total Unrealized P/L: ${total_pl:,.2f}")
        
        print("\n" + "="*70)
        print("AUTONOMOUS TRADING BEHAVIOR WITH EXISTING POSITIONS")
        print("="*70)
        
        print("\n[CRITICAL] PROMETHEUS WILL:")
        print("  ✓ Monitor your existing positions")
        print("  ✓ Include them in portfolio calculations")
        print("  ✓ Consider them when sizing new positions")
        
        print("\n[CRITICAL] PROMETHEUS WILL NOT:")
        print("  ✗ Automatically sell your existing positions")
        print("  ✗ Close positions it didn't open")
        print("  ✗ Override your manual holdings")
        
        print("\n[OPTIONS] You can:")
        print("  A) Keep existing positions (Prometheus works around them)")
        print("  B) Manually close positions before starting")
        print("  C) Let Prometheus manage only NEW positions")
        
        print("\n[RECOMMENDATION]:")
        print("  If you want full autonomous control, manually close existing")
        print("  positions first. Otherwise, Prometheus will trade alongside them.")
        
    else:
        print("\n[OK] No existing positions found")
        print("     Prometheus will start fresh with $123.52 capital")
    
    print("\n" + "="*70)
    return total_positions

if __name__ == "__main__":
    positions = asyncio.run(check_all_positions())
