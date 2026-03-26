#!/usr/bin/env python3
"""
Train only the missing AI models to complete the set
This will train the 4 models needed to reach 96 files (24 symbols × 4 files)
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check which models are missing
def get_missing_symbols():
    """Determine which symbols need models trained"""
    ai_models_dir = Path('ai_models')
    
    # Expected symbols (24 total)
    expected_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
                       'SPY', 'QQQ', 'DIA', 'IWM', 'AMD', 'INTC', 'JPM', 'BAC']
    expected_crypto = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 
                       'ADA-USD', 'DOT-USD', 'MATIC-USD', 'AVAX-USD']
    
    all_expected = expected_stocks + expected_crypto
    
    # Check which ones are missing
    missing = []
    for symbol in all_expected:
        price_model = ai_models_dir / f'{symbol}_price_model.joblib'
        if not price_model.exists():
            missing.append(symbol)
    
    return missing

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for training"""
    try:
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
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
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
        logger.info(f"  Collecting {years} years of data for {symbol}...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)

        # Download data
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if data.empty:
            logger.warning(f"  No data retrieved for {symbol}")
            return pd.DataFrame()

        # Flatten multi-level columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Calculate technical indicators
        data = calculate_technical_indicators(data)

        logger.info(f"  [CHECK] {symbol}: {len(data)} data points collected")
        return data

    except Exception as e:
        logger.error(f"  [ERROR] {symbol}: Failed to collect data - {e}")
        return pd.DataFrame()

def train_model_for_symbol(symbol: str, data: pd.DataFrame, output_dir: str):
    """Train models for a specific symbol"""
    try:
        logger.info(f"  Training models for {symbol}...")
        
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
            logger.warning(f"  {symbol}: Insufficient data for training")
            return False
        
        X = data[feature_columns]
        y_price = data['Price_Next']
        y_direction = data['Direction']
        
        # Split data
        X_train, X_test, y_price_train, y_price_test = train_test_split(
            X, y_price, test_size=0.2, random_state=42
        )
        _, _, y_dir_train, y_dir_test = train_test_split(
            X, y_direction, test_size=0.2, random_state=42
        )
        
        # Create scalers
        price_scaler = StandardScaler()
        direction_scaler = StandardScaler()
        
        X_train_scaled = price_scaler.fit_transform(X_train)
        X_test_scaled = price_scaler.transform(X_test)
        
        # Train price prediction model
        logger.info(f"    Training price predictor...")
        price_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        price_model.fit(X_train_scaled, y_price_train)
        price_score = price_model.score(X_test_scaled, y_price_test)
        
        # Train direction classifier
        logger.info(f"    Training direction classifier...")
        direction_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        direction_model.fit(X_train_scaled, y_dir_train)
        direction_score = direction_model.score(X_test_scaled, y_dir_test)
        
        # Save models and scalers
        os.makedirs(output_dir, exist_ok=True)
        
        price_model_path = os.path.join(output_dir, f'{symbol}_price_model.joblib')
        price_scaler_path = os.path.join(output_dir, f'{symbol}_price_scaler.joblib')
        direction_model_path = os.path.join(output_dir, f'{symbol}_direction_model.joblib')
        direction_scaler_path = os.path.join(output_dir, f'{symbol}_direction_scaler.joblib')
        
        joblib.dump(price_model, price_model_path)
        joblib.dump(price_scaler, price_scaler_path)
        joblib.dump(direction_model, direction_model_path)
        joblib.dump(direction_scaler, direction_scaler_path)
        
        logger.info(f"  [CHECK] {symbol}: Models trained and saved (4 files)")
        logger.info(f"     Price R²: {price_score:.4f}")
        logger.info(f"     Direction Accuracy: {direction_score:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"  [ERROR] {symbol}: Training failed - {e}")
        return False

def main():
    """Main training function"""
    logger.info("=" * 80)
    logger.info("PROMETHEUS - TRAIN MISSING AI MODELS")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Output directory
    output_dir = 'ai_models'
    os.makedirs(output_dir, exist_ok=True)
    
    # Check current status
    current_files = list(Path(output_dir).glob('*.joblib'))
    logger.info(f"Current model files: {len(current_files)}")
    logger.info(f"Target: 96 files (24 symbols × 4 files)")
    logger.info("")
    
    # Get missing symbols
    missing_symbols = get_missing_symbols()
    
    if not missing_symbols:
        logger.info("[CHECK] All models already trained!")
        logger.info(f"Total files: {len(current_files)}")
        return
    
    logger.info(f"Missing symbols: {len(missing_symbols)}")
    logger.info(f"Symbols to train: {', '.join(missing_symbols)}")
    logger.info("")
    
    # Train missing models
    logger.info("=" * 80)
    logger.info("TRAINING MISSING MODELS")
    logger.info("=" * 80)
    logger.info("")
    
    trained_count = 0
    failed_count = 0
    
    for i, symbol in enumerate(missing_symbols, 1):
        logger.info(f"[{i}/{len(missing_symbols)}] Processing {symbol}...")
        data = collect_historical_data(symbol, years=5)
        
        if not data.empty:
            success = train_model_for_symbol(symbol, data, output_dir)
            if success:
                trained_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1
        
        logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 80)
    
    final_files = list(Path(output_dir).glob('*.joblib'))
    logger.info(f"Models trained: {trained_count} symbols")
    logger.info(f"Failed: {failed_count} symbols")
    logger.info(f"Total model files: {len(final_files)}")
    logger.info(f"Target: 96 files")
    logger.info(f"Progress: {len(final_files)}/96 ({len(final_files)/96*100:.1f}%)")
    logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    if len(final_files) >= 96:
        logger.info("🎉 SUCCESS! All 96 model files complete!")
    else:
        logger.info(f"[WARNING]️ Still need {96 - len(final_files)} more files")
    
    logger.info("")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nTraining interrupted by user")
    except Exception as e:
        logger.error(f"\n\nTraining failed: {e}")
        import traceback
        traceback.print_exc()

