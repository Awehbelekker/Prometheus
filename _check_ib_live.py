"""Check IB Gateway - all accounts, balances, positions, recent trades."""
try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.execution import ExecutionFilter
    import threading

    WANT_ACCOUNT = "U21922116"

    class IBChecker(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.managed_accounts = []
            self.summary = {}        # tag -> {acct: (val, cur)}
            self.updates  = {}       # acct -> {tag: (val, cur)}
            self.positions = []
            self.executions = []
            self.acct_done  = threading.Event()
            self.upd_done   = threading.Event()
            self.pos_done   = threading.Event()
            self.exec_done  = threading.Event()

        def managedAccounts(self, accountsList):
            self.managed_accounts = [a.strip() for a in accountsList.split(",") if a.strip()]
            print(f"[OK] IB Gateway connected")
            print(f"     Managed accounts: {self.managed_accounts}")
            # Request full detail for the target account
            self.reqAccountUpdates(True, WANT_ACCOUNT)
            self.reqAccountSummary(1, "All",
                "AccountType,NetLiquidation,TotalCashValue,BuyingPower,AvailableFunds")
            self.reqPositions()
            filt = ExecutionFilter()
            filt.acctCode = WANT_ACCOUNT
            self.reqExecutions(2, filt)

        def updateAccountValue(self, key, val, currency, accountName):
            if accountName not in self.updates:
                self.updates[accountName] = {}
            self.updates[accountName][key] = (val, currency)

        def updatePortfolio(self, contract, pos, mktPrice, mktVal, avgCost, unrealPnl, realPnl, acct):
            if pos != 0:
                self.positions.append((contract.symbol, pos, avgCost, unrealPnl, acct))

        def updateAccountTime(self, timeStamp):
            self.upd_done.set()

        def accountSummary(self, reqId, account, tag, value, currency):
            if account not in self.summary:
                self.summary[account] = {}
            self.summary[account][tag] = (value, currency)

        def accountSummaryEnd(self, reqId):
            self.acct_done.set()

        def position(self, account, contract, pos, avgCost):
            pass  # using updatePortfolio instead

        def positionEnd(self):
            self.pos_done.set()

        def execDetails(self, reqId, contract, execution):
            self.executions.append((
                execution.time[:10] if execution.time else "?",
                execution.side,
                execution.shares,
                contract.symbol,
                execution.price,
                execution.acctNumber,
                execution.orderId,
            ))

        def execDetailsEnd(self, reqId):
            self.exec_done.set()

        def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
            if errorCode not in (2104, 2106, 2158, 2119, 2108):
                print(f"  IB [{errorCode}]: {errorString}")

    app = IBChecker()
    app.connect("127.0.0.1", 4002, clientId=97)
    t = threading.Thread(target=app.run, daemon=True)
    t.start()

    app.acct_done.wait(timeout=10)
    app.upd_done.wait(timeout=10)
    app.pos_done.wait(timeout=10)
    app.exec_done.wait(timeout=10)

    # --- Account Summary (all managed accounts) ---
    print()
    print("=== IB ACCOUNT SUMMARY (all managed) ===")
    for acct, tags in sorted(app.summary.items()):
        print(f"  Account: {acct}")
        for tag, (val, cur) in sorted(tags.items()):
            print(f"    {tag:<22}: {val} {cur}")

    # --- Full account update for target ---
    print()
    print(f"=== ACCOUNT UPDATES for {WANT_ACCOUNT} ===")
    data = app.updates.get(WANT_ACCOUNT, {})
    key_fields = ["AccountType", "NetLiquidation", "TotalCashValue",
                  "BuyingPower", "AvailableFunds", "GrossPositionValue",
                  "RealizedPnL", "UnrealizedPnL", "Currency"]
    for k in key_fields:
        if k in data:
            print(f"  {k:<22}: {data[k][0]} {data[k][1]}")

    # --- Positions ---
    print()
    print("=== OPEN POSITIONS ===")
    if app.positions:
        for sym, qty, avg, upnl, acct in app.positions:
            print(f"  {acct}  {sym:<8}  qty={qty}  avg=${avg:.2f}  unrealPnL=${upnl:.2f}")
    else:
        print("  (none)")

    # --- Executions (recent trades) ---
    print()
    print("=== RECENT EXECUTIONS ===")
    if app.executions:
        for date, side, qty, sym, price, acct, oid in sorted(app.executions, reverse=True)[:20]:
            print(f"  {date}  {side:<4}  {qty}x {sym:<8}  @${price:.2f}  acct={acct}")
    else:
        print("  (none returned)")

    app.reqAccountUpdates(False, WANT_ACCOUNT)
    app.disconnect()

except ImportError:
    print("ibapi not installed")
except Exception as e:
    import traceback; traceback.print_exc()
