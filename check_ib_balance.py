#!/usr/bin/env python3
"""Quick IB account balance check"""
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time

class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.account = None
        self.balance = None
        self.cash = None
        
    def nextValidId(self, orderId):
        print('✅ Connected to IB Gateway')
        self.reqAccountSummary(1, 'All', 'TotalCashBalance,NetLiquidation')
        
    def accountSummary(self, reqId, account, tag, value, currency):
        print(f'Account: {account} | {tag}: {value} {currency}')
        if tag == 'NetLiquidation':
            self.balance = value
        if tag == 'TotalCashBalance':
            self.cash = value
        self.account = account
        
    def accountSummaryEnd(self, reqId):
        print('\n✅ Account summary complete')
        self.disconnect()

app = IBApp()
app.connect('127.0.0.1', 4002, 0)
thread = threading.Thread(target=app.run)
thread.start()
time.sleep(4)
print(f'\n💰 ACCOUNT BALANCE:')
print(f'   Account: {app.account}')
print(f'   Cash: ${app.cash}')
print(f'   Net Liquidation: ${app.balance}\n')
