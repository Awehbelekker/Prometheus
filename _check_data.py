import pandas as pd, os
files = ['vix_regime_labeled.csv', 'gold_regime_labeled.csv', 'longbonds_regime_labeled.csv', 'sp500_regime_labeled.csv']
for f in files:
    path = os.path.join('data', f)
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=['date'])
        print(f"{f:40s} {len(df):>6} days  {df['date'].min().strftime('%Y-%m-%d')} -> {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"   Columns: {list(df.columns)}")
    else:
        print(f"{f:40s} NOT FOUND")
