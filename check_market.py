import yfinance as yf
from datetime import datetime, timedelta

# Get SPY performance for last 60 days
end = datetime.now()
start = end - timedelta(days=60)

spy = yf.download('SPY', start=start, end=end, progress=False)
if len(spy) > 0:
    first_price = float(spy['Close'].iloc[0])
    last_price = float(spy['Close'].iloc[-1])
    spy_return = (last_price - first_price) / first_price * 100
    print(f'SPY Performance (last 60 days):')
    print(f'  Start: ${first_price:.2f}')
    print(f'  End: ${last_price:.2f}')
    print(f'  Return: {spy_return:.2f}%')
    print(f'  Days: {len(spy)}')

