#!/usr/bin/env python3
"""
PROMETHEUS Crypto Chart Generator
Generates candlestick charts for crypto symbols to train visual AI
"""

import os
import yfinance as yf
import mplfinance as mpf
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Crypto symbols to generate charts for (Yahoo Finance format)
CRYPTO_SYMBOLS = [
    'BTC-USD',   # Bitcoin
    'ETH-USD',   # Ethereum
    'SOL-USD',   # Solana
    'DOGE-USD',  # Dogecoin
    'AVAX-USD',  # Avalanche
    'LINK-USD',  # Chainlink
    'ADA-USD',   # Cardano
    'XRP-USD',   # Ripple
    'DOT-USD',   # Polkadot
    'LTC-USD',   # Litecoin
    'ATOM-USD',  # Cosmos
    'MATIC-USD', # Polygon
]

# Time periods to generate (in days)
TIME_PERIODS = [35, 65, 95, 125, 185, 245, 365]

CHARTS_DIR = 'charts'

def generate_candlestick_chart(symbol: str, days: int) -> str:
    """Generate a candlestick chart for a symbol"""

    # Clean symbol for filename (BTC-USD -> BTC)
    clean_symbol = symbol.replace('-USD', '')

    # Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 10)

    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if data.empty:
            print(f"  ⚠️ No data for {symbol}")
            return None

        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Take last N days
        data = data.tail(days)

        if len(data) < 20:  # Need at least 20 data points
            print(f"  ⚠️ Insufficient data for {symbol}: {len(data)} days")
            return None

    except Exception as e:
        print(f"  ❌ Error fetching {symbol}: {e}")
        return None

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{clean_symbol}_historical_{days}d_1D_{timestamp}.png"
    filepath = os.path.join(CHARTS_DIR, filename)

    try:
        # Use mplfinance for clean candlestick charts
        mpf.plot(data, type='candle', style='charles',
                 title=f'{symbol} - {days} Day Chart',
                 volume=True,
                 savefig=filepath,
                 figsize=(12, 8))
        return filename
    except Exception as e:
        print(f"  ❌ Chart error: {e}")
        return None

def main():
    print("=" * 60)
    print("🚀 PROMETHEUS Crypto Chart Generator")
    print("=" * 60)
    
    # Ensure charts directory exists
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    total_charts = 0
    failed_charts = 0
    
    for symbol in CRYPTO_SYMBOLS:
        print(f"\n📊 Processing {symbol}...")
        
        for days in TIME_PERIODS:
            result = generate_candlestick_chart(symbol, days)
            if result:
                print(f"  ✅ {result}")
                total_charts += 1
            else:
                failed_charts += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Generated: {total_charts} charts")
    print(f"❌ Failed: {failed_charts} charts")
    print("=" * 60)
    print(f"\n📁 Charts saved to: {os.path.abspath(CHARTS_DIR)}")
    print("\n🎯 Next step: Run 'python CLOUD_VISION_TRAINING.py' to analyze charts")

if __name__ == "__main__":
    main()

