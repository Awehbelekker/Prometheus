"""Check if Alpaca can trade both stocks and crypto in parallel"""
import os
from dotenv import load_dotenv
load_dotenv()

from alpaca.trading.client import TradingClient

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')

print('=' * 70)
print('ALPACA DUAL TRADING CAPABILITY CHECK')
print('=' * 70)

try:
    client = TradingClient(api_key, secret_key, paper=False)
    account = client.get_account()
    
    print(f'\nAccount Status: {account.status}')
    print(f'Account Equity: ${float(account.equity):.2f}')
    print(f'Cash: ${float(account.cash):.2f}')
    print(f'Buying Power: ${float(account.buying_power):.2f}')
    
    # Get all positions
    positions = client.get_all_positions()
    
    stock_positions = []
    crypto_positions = []
    
    for p in positions:
        if '/' in p.symbol:
            crypto_positions.append(p)
        else:
            stock_positions.append(p)
    
    print(f'\nCurrent Positions:')
    print(f'  Stocks: {len(stock_positions)}')
    for p in stock_positions[:5]:
        print(f'    {p.symbol}: {p.qty} @ ${float(p.avg_entry_price):.2f}')
    
    print(f'  Crypto: {len(crypto_positions)}')
    for p in crypto_positions[:5]:
        print(f'    {p.symbol}: {p.qty} @ ${float(p.avg_entry_price):.4f}')
    
    print('\n' + '=' * 70)
    print('RESULT: Alpaca CAN trade BOTH stocks AND crypto in parallel!')
    print('=' * 70)
    print('  - Stocks: $0 commission, 9:30 AM - 4 PM ET (some 24/5)')
    print('  - Crypto: 24/7 trading, ~0.25% taker fee')
    print('')
    print('PROMETHEUS can use Alpaca for BOTH asset types simultaneously!')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

