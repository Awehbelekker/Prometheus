"""
Build regime-labeled real S&P 500 data for the 50-year benchmark.
Classifies each day into: bull, bear, crash, recovery, volatile, sideways
using rolling returns + rolling volatility (no lookahead bias).
"""

import pandas as pd
import numpy as np
import os

def classify_regimes(csv_path: str = 'data/sp500_historical_1976_2026.csv') -> pd.DataFrame:
    """
    Load real S&P 500 data and classify market regimes.
    
    Classification rules (using 60-day lookback, no lookahead):
      - crash:    60d return < -20% OR 20d vol > 40%
      - bear:     60d return < -12% AND 20d vol > 20%
      - volatile: 20d vol > 28% (but not crash/bear)
      - recovery: 60d return > +12% AND was recently in bear/crash
      - bull:     20d vol < 22% AND 60d return > -5% (normal upward drift)
      - sideways: everything else
    """
    print(f"Loading {csv_path}...")
    raw = pd.read_csv(csv_path, header=[0, 1], index_col=0, parse_dates=True)
    
    # Flatten multi-level columns from yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [col[0] for col in raw.columns]
    
    # Drop any rows where Close is NaN (header artifacts)
    raw = raw.dropna(subset=['Close'])
    
    # Ensure we have the columns we need
    close_col = 'Close' if 'Close' in raw.columns else 'close'
    high_col = 'High' if 'High' in raw.columns else 'high'
    low_col = 'Low' if 'Low' in raw.columns else 'low'
    vol_col = 'Volume' if 'Volume' in raw.columns else 'volume'
    
    df = pd.DataFrame()
    df['date'] = raw.index
    df['close'] = raw[close_col].values
    df['high'] = raw[high_col].values if high_col in raw.columns else df['close'] * 1.005
    df['low'] = raw[low_col].values if low_col in raw.columns else df['close'] * 0.995
    df['volume'] = raw[vol_col].values if vol_col in raw.columns else 1e9
    df = df.reset_index(drop=True)
    
    # Rolling features
    df['ret_20'] = df['close'].pct_change(20)
    df['ret_60'] = df['close'].pct_change(60)
    df['daily_ret'] = df['close'].pct_change()
    df['vol_20'] = df['daily_ret'].rolling(20).std() * np.sqrt(252)  # annualized
    
    # Drawdown from 252-day peak
    df['peak_252'] = df['close'].rolling(252, min_periods=1).max()
    df['dd_252'] = (df['close'] - df['peak_252']) / df['peak_252']
    
    # Classify regimes
    regimes = []
    recent_bear_crash = False
    bear_crash_counter = 0
    
    for i in range(len(df)):
        ret60 = df.loc[i, 'ret_60'] if not pd.isna(df.loc[i, 'ret_60']) else 0
        ret20 = df.loc[i, 'ret_20'] if not pd.isna(df.loc[i, 'ret_20']) else 0
        vol20 = df.loc[i, 'vol_20'] if not pd.isna(df.loc[i, 'vol_20']) else 0.15
        dd = df.loc[i, 'dd_252'] if not pd.isna(df.loc[i, 'dd_252']) else 0
        
        if vol20 > 0.45 or ret60 < -0.25 or dd < -0.30:
            regime = 'crash'
            recent_bear_crash = True
            bear_crash_counter = 60
        elif ret60 < -0.12 and vol20 > 0.20:
            regime = 'bear'
            recent_bear_crash = True
            bear_crash_counter = 60
        elif vol20 > 0.28:
            regime = 'volatile'
        elif recent_bear_crash and ret60 > 0.12:
            regime = 'recovery'
            bear_crash_counter -= 1
            if bear_crash_counter <= 0:
                recent_bear_crash = False
        elif vol20 < 0.22 and ret60 > -0.05:
            regime = 'bull'
        else:
            regime = 'sideways'
            
        if bear_crash_counter > 0:
            bear_crash_counter -= 1
            if bear_crash_counter <= 0:
                recent_bear_crash = False
                
        regimes.append(regime)
    
    df['regime'] = regimes
    
    # Add volatility column (daily, not annualized)
    df['volatility'] = df['vol_20'] / np.sqrt(252)
    df['volatility'] = df['volatility'].fillna(0.01)
    
    # Print regime distribution
    print(f"\nTotal trading days: {len(df):,}")
    print(f"Date range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
    print(f"\nRegime distribution:")
    for regime, count in df['regime'].value_counts().sort_index().items():
        pct = count / len(df) * 100
        print(f"  {regime:12s}: {count:6,} days ({pct:5.1f}%)")
    
    # Buy-and-hold CAGR
    years = (df['date'].iloc[-1] - df['date'].iloc[0]).days / 365.25
    bh_cagr = (df['close'].iloc[-1] / df['close'].iloc[0]) ** (1/years) - 1
    print(f"\nBuy-and-hold CAGR: {bh_cagr*100:.2f}% over {years:.1f} years")
    
    # Save
    out_path = 'data/sp500_regime_labeled.csv'
    df.to_csv(out_path, index=False)
    print(f"\nSaved regime-labeled data to {out_path}")
    
    return df


if __name__ == '__main__':
    classify_regimes()
