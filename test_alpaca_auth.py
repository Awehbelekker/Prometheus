#!/usr/bin/env python3
"""Test Alpaca Authentication"""
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# LIVE credentials
live_key = os.getenv('ALPACA_LIVE_KEY', '').strip("'")
live_secret = os.getenv('ALPACA_LIVE_SECRET', '').strip("'")

# PAPER credentials
paper_key = os.getenv('ALPACA_PAPER_KEY', '').strip("'")
paper_secret = os.getenv('ALPACA_PAPER_SECRET', '').strip("'")

print(f'LIVE Key: {live_key[:10]}... Secret: {live_secret[:10]}...')
print(f'PAPER Key: {paper_key[:10]}... Secret: {paper_secret[:10]}...')

# Test LIVE
print('\nTesting LIVE mode...')
try:
    client = TradingClient(live_key, live_secret, paper=False)
    account = client.get_account()
    print(f'LIVE SUCCESS! Account: {account.account_number}, Equity: ${float(account.equity):,.2f}')
except Exception as e:
    print(f'LIVE Error: {e}')

# Test PAPER with PAPER credentials
print('\nTesting PAPER mode...')
try:
    client = TradingClient(paper_key, paper_secret, paper=True)
    account = client.get_account()
    print(f'PAPER SUCCESS! Account: {account.account_number}, Equity: ${float(account.equity):,.2f}')
except Exception as e:
    print(f'PAPER Error: {e}')
