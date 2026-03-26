"""Check Alpaca and IB account status"""
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

print("=== ALPACA LIVE ACCOUNT STATUS ===")
try:
    client = TradingClient(os.getenv('ALPACA_LIVE_KEY'), os.getenv('ALPACA_LIVE_SECRET'))
    account = client.get_account()
    
    print(f"Account Status: {account.status}")
    print(f"Equity: ${float(account.equity):,.2f}")
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    
    # Get positions
    positions = client.get_all_positions()
    stock_positions = [p for p in positions if '/' not in p.symbol and not p.symbol.endswith('USD')]
    crypto_positions = [p for p in positions if '/' in p.symbol or p.symbol.endswith('USD')]
    
    print(f"\nTotal Positions: {len(positions)}")
    print(f"  Stocks: {len(stock_positions)}")
    print(f"  Crypto: {len(crypto_positions)}")
    
    if crypto_positions:
        print("\nCrypto Positions:")
        for p in crypto_positions:
            print(f"  {p.symbol}: {float(p.qty):.6f} @ ${float(p.current_price):.2f} = ${float(p.market_value):.2f}")
    else:
        print("\nNo Crypto positions currently")
        
except Exception as e:
    print(f"Error connecting to Alpaca Live: {e}")

print("\n" + "=" * 50)
print("=== IB GATEWAY STATUS ===")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 4002))
    if result == 0:
        print("IB Gateway Port 4002: OPEN")
    else:
        print("IB Gateway Port 4002: CLOSED/NOT RUNNING")
    sock.close()
except Exception as e:
    print(f"Error checking IB Gateway: {e}")

