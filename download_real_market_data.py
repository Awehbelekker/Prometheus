#!/usr/bin/env python3
"""
PROMETHEUS Real Market Data Downloader
=======================================
Downloads historical data for multiple asset classes from Yahoo Finance.
Creates regime-labeled datasets for multi-asset backtesting.

Assets covered:
  - S&P 500 (^GSPC) — already have 1976-2026
  - NASDAQ 100 (^NDX)
  - Sector ETFs: XLK, XLF, XLE, XLV, XLI, XLC
  - Gold (GLD), Bonds (TLT), VIX (^VIX)
  - Individual stocks: AAPL, MSFT, NVDA, AMZN, GOOGL, TSLA, META, JPM
  - Crypto: BTC-USD, ETH-USD (shorter history)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pathlib import Path

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

# ── Symbol groups ─────────────────────────────────────────────────────────────
DOWNLOAD_CONFIG = {
    # Indices (long history)
    'indices': {
        'symbols': ['^GSPC', '^NDX', '^DJI', '^RUT'],
        'start': '1990-01-01',
        'names': ['SP500', 'NASDAQ100', 'DowJones', 'Russell2000'],
    },
    # Sector ETFs (since ~1998-2000)
    'sectors': {
        'symbols': ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLC', 'XLY', 'XLP'],
        'start': '1999-01-01',
        'names': ['Tech', 'Financials', 'Energy', 'Healthcare', 'Industrials',
                  'Communications', 'ConsumerDisc', 'ConsumerStaples'],
    },
    # Safe havens & macro
    'macro': {
        'symbols': ['GLD', 'TLT', '^VIX', 'UUP'],
        'start': '2004-01-01',
        'names': ['Gold', 'LongBonds', 'VIX', 'USDollar'],
    },
    # Individual mega-caps (various start dates)
    'stocks': {
        'symbols': ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'TSLA', 'META', 'JPM'],
        'start': '2005-01-01',
        'names': None,  # use ticker names
    },
    # Crypto
    'crypto': {
        'symbols': ['BTC-USD', 'ETH-USD', 'SOL-USD'],
        'start': '2015-01-01',
        'names': ['Bitcoin', 'Ethereum', 'Solana'],
    },
}


def classify_regime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify market regime for any asset using returns + volatility.
    Same methodology as build_real_sp500_data.py for consistency.
    """
    df = df.copy()
    df['daily_ret'] = df['Close'].pct_change()
    df['ret_20'] = df['Close'].pct_change(20)
    df['ret_60'] = df['Close'].pct_change(60)
    df['vol_20'] = df['daily_ret'].rolling(20).std() * np.sqrt(252)

    # Rolling peak and drawdown
    df['peak_252'] = df['Close'].rolling(252, min_periods=1).max()
    df['dd_252'] = (df['Close'] - df['peak_252']) / df['peak_252']

    df['regime'] = 'sideways'  # default

    for i in range(len(df)):
        dd = df.iloc[i]['dd_252'] if pd.notna(df.iloc[i]['dd_252']) else 0
        ret20 = df.iloc[i]['ret_20'] if pd.notna(df.iloc[i]['ret_20']) else 0
        ret60 = df.iloc[i]['ret_60'] if pd.notna(df.iloc[i]['ret_60']) else 0
        vol = df.iloc[i]['vol_20'] if pd.notna(df.iloc[i]['vol_20']) else 0.15

        if dd < -0.20 or ret20 < -0.15:
            df.iloc[i, df.columns.get_loc('regime')] = 'crash'
        elif dd < -0.10 or ret60 < -0.10:
            df.iloc[i, df.columns.get_loc('regime')] = 'bear'
        elif vol > 0.30 and abs(ret20) < 0.05:
            df.iloc[i, df.columns.get_loc('regime')] = 'volatile'
        elif ret20 > 0.08 and dd > -0.05:
            df.iloc[i, df.columns.get_loc('regime')] = 'recovery'
        elif ret60 > 0.05 and dd > -0.05:
            df.iloc[i, df.columns.get_loc('regime')] = 'bull'
        else:
            df.iloc[i, df.columns.get_loc('regime')] = 'sideways'

    return df


def download_group(group_name: str, config: dict):
    """Download a group of symbols and save regime-labeled CSVs."""
    symbols = config['symbols']
    start = config['start']
    names = config.get('names') or symbols
    end = datetime.now().strftime('%Y-%m-%d')

    print(f"\n{'='*60}")
    print(f"  Downloading: {group_name.upper()} ({len(symbols)} symbols)")
    print(f"  Period: {start} → {end}")
    print(f"{'='*60}")

    for sym, name in zip(symbols, names):
        try:
            print(f"\n  [{name}] Downloading {sym}...", end=' ')
            ticker = yf.Ticker(sym)
            df = ticker.history(start=start, end=end, auto_adjust=True)

            if df.empty or len(df) < 100:
                print(f"SKIP (only {len(df)} rows)")
                continue

            # Keep standard columns
            df = df.reset_index()
            df = df.rename(columns={'Date': 'date'})

            # Remove timezone info if present
            if hasattr(df['date'].dtype, 'tz') and df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)

            # Classify regime
            df = classify_regime(df)

            # Select output columns
            out_cols = ['date', 'Close', 'High', 'Low', 'Volume',
                        'daily_ret', 'ret_20', 'ret_60', 'vol_20',
                        'peak_252', 'dd_252', 'regime']
            df = df[[c for c in out_cols if c in df.columns]]

            # Rename Close → close for benchmark compatibility
            df = df.rename(columns={'Close': 'close', 'High': 'high',
                                    'Low': 'low', 'Volume': 'volume'})

            # Save
            safe_name = name.replace('/', '-').replace('^', '')
            filename = DATA_DIR / f"{safe_name.lower()}_regime_labeled.csv"
            df.to_csv(filename, index=False)

            # Report
            date_range = f"{df['date'].iloc[0].strftime('%Y-%m-%d')} → {df['date'].iloc[-1].strftime('%Y-%m-%d')}"
            regimes = df['regime'].value_counts()
            print(f"OK ({len(df):,} days, {date_range})")
            for r in ['bull', 'sideways', 'volatile', 'bear', 'crash', 'recovery']:
                cnt = regimes.get(r, 0)
                if cnt > 0:
                    print(f"    {r:12s}: {cnt:6,} ({cnt/len(df)*100:.1f}%)")

        except Exception as e:
            print(f"ERROR: {e}")


def main():
    print("\n" + "🔥" * 30)
    print("  PROMETHEUS Multi-Asset Data Downloader")
    print("  Downloading real historical data for backtesting")
    print("🔥" * 30)

    total_files = 0
    for group_name, config in DOWNLOAD_CONFIG.items():
        download_group(group_name, config)
        total_files += len(config['symbols'])

    # Summary
    print(f"\n{'='*60}")
    print(f"  DOWNLOAD COMPLETE")
    print(f"{'='*60}")

    csv_files = list(DATA_DIR.glob('*_regime_labeled.csv'))
    print(f"\n  Total regime-labeled datasets: {len(csv_files)}")
    for f in sorted(csv_files):
        size_kb = f.stat().st_size / 1024
        print(f"    {f.name:45s} {size_kb:8.1f} KB")

    print(f"\n  These files can be used with the benchmark:")
    print(f"    benchmark.data_generator.load_real_sp500('data/<file>.csv')")
    print(f"\n  The benchmark's load_real_sp500() accepts any regime-labeled CSV")
    print(f"  with columns: date, close, volume, regime")


if __name__ == '__main__':
    main()
