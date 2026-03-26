"""Quick IB integration verification"""
import asyncio, os, sys
sys.path.insert(0, '.')

# Load .env file
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('IB_ACCOUNT', 'U21922116')
os.environ.setdefault('IB_HOST', '127.0.0.1')
os.environ.setdefault('IB_PORT', '4002')
os.environ.setdefault('IB_CLIENT_ID', '99')

async def check():
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    from brokers.alpaca_broker import AlpacaBroker
    
    # Alpaca
    alpaca_config = {
        'api_key': os.environ.get('ALPACA_API_KEY', os.environ.get('ALPACA_LIVE_KEY', '')),
        'secret_key': os.environ.get('ALPACA_SECRET_KEY', os.environ.get('ALPACA_LIVE_SECRET', '')),
        'paper_trading': False,
        'enable_24_5_trading': True
    }
    alp = AlpacaBroker(alpaca_config)
    await alp.connect()
    alp_acc = await alp.get_account()
    alp_pos = await alp.get_positions()
    print(f'ALPACA: equity=${float(alp_acc.equity):.2f}, cash=${float(alp_acc.cash):.2f}, positions={len(alp_pos)}')
    for p in alp_pos:
        print(f'  {p.symbol}: qty={p.quantity}, val=${float(p.market_value):.2f}')
    
    # IB
    ib_config = {
        'host': os.environ.get('IB_HOST', '127.0.0.1'),
        'port': int(os.environ.get('IB_PORT', 4002)),
        'client_id': 99,
        'paper_trading': False
    }
    ib = InteractiveBrokersBroker(ib_config)
    await ib.connect()
    await asyncio.sleep(3)  # Wait for IB data
    ib_acc = await ib.get_account()
    ib_pos = await ib.get_positions()
    print(f'IB: equity=${float(ib_acc.equity):.2f}, cash=${float(ib_acc.cash):.2f}, positions={len(ib_pos)}')
    for p in ib_pos:
        print(f'  {p.symbol}: qty={p.quantity}, val=${float(p.market_value):.2f}')
    
    combined_equity = float(alp_acc.equity) + float(ib_acc.equity)
    combined_cash = float(alp_acc.cash) + float(ib_acc.cash)
    print(f'\nCOMBINED: equity=${combined_equity:.2f}, cash=${combined_cash:.2f}')
    print(f'IB idle: {float(ib_acc.cash)/max(float(ib_acc.equity),0.01)*100:.1f}%')
    print(f'INTEGRATION STATUS: BOTH BROKERS ACCESSIBLE')
    
    await ib.disconnect()

asyncio.run(check())
