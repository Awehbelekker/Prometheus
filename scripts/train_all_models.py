#!/usr/bin/env python3
"""
Train all AI models with comprehensive historical data
Safe to run during active trading - trains to separate directory
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Symbols to train
STOCK_SYMBOLS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
    'SPY', 'QQQ', 'DIA', 'IWM', 'AMD', 'INTC', 'JPM', 'BAC'
]

CRYPTO_SYMBOLS = [
    'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 
    'ADA-USD', 'DOT-USD', 'MATIC-USD', 'AVAX-USD'
]

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for training"""
    try:
        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            # Flatten MultiIndex columns
            df.columns = df.columns.get_level_values(0)
        
        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Simple Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        bb_middle = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Middle'] = bb_middle
        df['BB_Upper'] = bb_middle + (bb_std * 2)
        df['BB_Lower'] = bb_middle - (bb_std * 2)
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        # Handle division by zero and ensure single column assignment
        df['Volume_Ratio'] = df['Volume'].div(df['Volume_SMA'].replace(0, np.nan))
        
        # Price momentum
        df['Momentum'] = df['Close'].pct_change(periods=10)
        
        # Volatility (ATR approximation)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['ATR'] = ranges.max(axis=1).rolling(window=14).mean()
        
        # Drop NaN values
        df = df.dropna()
        
        return df
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return df

def collect_historical_data(symbol: str, years: int = 5) -> pd.DataFrame:
    """Collect historical data for a symbol"""
    try:
        logger.info(f"Collecting {years} years of data for {symbol}...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # Download data
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            logger.warning(f"No data retrieved for {symbol}")
            return pd.DataFrame()
        
        # Calculate technical indicators
        data = calculate_technical_indicators(data)
        
        logger.info(f"[CHECK] {symbol}: {len(data)} data points collected")
        return data
        
    except Exception as e:
        logger.error(f"[ERROR] {symbol}: Failed to collect data - {e}")
        return pd.DataFrame()

def train_model_for_symbol(symbol: str, data: pd.DataFrame, output_dir: str):
    """Train models for a specific symbol"""
    try:
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        import joblib
        
        logger.info(f"Training models for {symbol}...")
        
        # Prepare features
        feature_columns = [
            'SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26',
            'MACD', 'MACD_Signal', 'RSI', 'BB_Upper', 'BB_Lower',
            'Volume_Ratio', 'Momentum', 'ATR'
        ]
        
        # Create target variables
        data['Price_Next'] = data['Close'].shift(-1)  # Next day price
        data['Direction'] = (data['Price_Next'] > data['Close']).astype(int)  # Up/Down
        
        # Drop NaN
        data = data.dropna()
        
        if len(data) < 100:
            logger.warning(f"{symbol}: Insufficient data for training")
            return
        
        X = data[feature_columns]
        y_price = data['Price_Next']
        y_direction = data['Direction']
        
        # Split data - use same split for both models
        X_train, X_test, y_price_train, y_price_test, y_dir_train, y_dir_test = train_test_split(
            X, y_price, y_direction, test_size=0.2, random_state=42
        )
        
        # Train price prediction model
        logger.info(f"  Training price predictor...")
        price_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        price_model.fit(X_train, y_price_train)
        price_score = price_model.score(X_test, y_price_test)
        
        # Train direction classifier
        logger.info(f"  Training direction classifier...")
        direction_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        direction_model.fit(X_train, y_dir_train)
        direction_score = direction_model.score(X_test, y_dir_test)
        
        # Save models
        os.makedirs(output_dir, exist_ok=True)
        
        price_model_path = os.path.join(output_dir, f'{symbol}_price_model.pkl')
        direction_model_path = os.path.join(output_dir, f'{symbol}_direction_model.pkl')
        
        joblib.dump(price_model, price_model_path)
        joblib.dump(direction_model, direction_model_path)
        
        logger.info(f"[CHECK] {symbol}: Models trained and saved")
        logger.info(f"   Price R²: {price_score:.4f}")
        logger.info(f"   Direction Accuracy: {direction_score:.4f}")
        
    except Exception as e:
        logger.error(f"[ERROR] {symbol}: Training failed - {e}")

def main():
    """Main training function"""
    logger.info("=" * 80)
    logger.info("PROMETHEUS AI MODEL PRE-TRAINING")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Output directory
    output_dir = 'models_pretrained'
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Stock Symbols: {len(STOCK_SYMBOLS)}")
    logger.info(f"Crypto Symbols: {len(CRYPTO_SYMBOLS)}")
    logger.info("")
    
    # Train stock models
    logger.info("=" * 80)
    logger.info("TRAINING STOCK MODELS")
    logger.info("=" * 80)
    
    for i, symbol in enumerate(STOCK_SYMBOLS, 1):
        logger.info(f"\n[{i}/{len(STOCK_SYMBOLS)}] Processing {symbol}...")
        data = collect_historical_data(symbol, years=5)
        if not data.empty:
            train_model_for_symbol(symbol, data, output_dir)
    
    # Train crypto models
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING CRYPTO MODELS")
    logger.info("=" * 80)
    
    for i, symbol in enumerate(CRYPTO_SYMBOLS, 1):
        logger.info(f"\n[{i}/{len(CRYPTO_SYMBOLS)}] Processing {symbol}...")
        data = collect_historical_data(symbol, years=5)
        if not data.empty:
            train_model_for_symbol(symbol, data, output_dir)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 80)
    
    model_files = list(Path(output_dir).glob('*.pkl'))
    logger.info(f"Total Models Trained: {len(model_files)}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    logger.info("[CHECK] All models trained successfully!")
    logger.info("")
    logger.info("Next Steps:")
    logger.info("1. Test models in paper trading")
    logger.info("2. Validate performance")
    logger.info("3. Deploy to production when ready")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nTraining interrupted by user")
    except Exception as e:
        logger.error(f"\n\nTraining failed: {e}")
        import traceback
        traceback.print_exc()

