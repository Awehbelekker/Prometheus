import yfinance as yf
t = yf.Ticker("AAPL")
h = t.history(period="5d", interval="5m")
print(f"Rows: {len(h)}")
if len(h) > 0:
    print(f"Last close: {h['Close'].iloc[-1]:.2f}")
    print(f"Time range: {h.index[0]} to {h.index[-1]}")
else:
    print("EMPTY - yfinance returned no data")
