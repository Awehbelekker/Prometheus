#!/usr/bin/env python3
"""
PROMETHEUS Historical Data Pipeline
====================================
Enhanced historical data pipeline for AI pre-training.
Extends existing real_time_market_data.py with long-term historical data storage.

Features:
- Download 5+ years of historical data
- SQLite database storage
- Multiple timeframes (1d, 1h, 5m)
- Feature engineering for ML training
- Data quality validation
- Integration with existing market data systems
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
from dataclasses import dataclass

# Import existing market data providers
from core.real_time_market_data import (
    RealTimeMarketDataOrchestrator,
    MarketDataPoint
)

# --- Symbol normalization helpers (support crypto pairs like BTC/USD -> BTC-USD) ---
def _normalize_symbol(symbol: str) -> str:
    s = (symbol or "").strip().upper()
    # unify common separators to hyphen for storage and yfinance
    return s.replace(" ", "").replace("/", "-").replace("\\", "-").replace("_", "-")

def _to_yf_symbol(symbol: str) -> str:
    # For Yahoo Finance, hyphenated crypto pairs are expected (e.g., BTC-USD)
    return _normalize_symbol(symbol)

logger = logging.getLogger(__name__)

@dataclass
class HistoricalDataConfig:
    """Configuration for historical data pipeline"""
    data_dir: str = "historical_data"
    db_name: str = "historical_data.db"
    default_period_years: int = 5
    supported_timeframes: List[str] = None

    def __post_init__(self):
        if self.supported_timeframes is None:
            self.supported_timeframes = ['1d', '1h', '5m']


class HistoricalDataPipeline:
    """
    Enhanced historical data pipeline for AI pre-training
    Extends existing market data infrastructure
    """

    def __init__(self, config: HistoricalDataConfig = None):
        self.config = config or HistoricalDataConfig()
        self.data_dir = Path(self.config.data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database path
        self.db_path = self.data_dir / self.config.db_name

        # Initialize database
        self._init_database()

        # Use existing market data orchestrator for real-time data
        self.market_data = RealTimeMarketDataOrchestrator()

        logger.info(f"📊 Historical Data Pipeline initialized: {self.data_dir}")

    def _init_database(self):
        """Initialize SQLite database for historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Historical OHLCV data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')

        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_timeframe
            ON historical_data(symbol, timeframe, timestamp)
        ''')

        # Features table for pre-calculated technical indicators
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                features TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        ''')

        # Metadata table for tracking downloads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                record_count INTEGER,
                data_quality_score REAL,
                downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timeframe)
            )
        ''')

        conn.commit()
        conn.close()

        logger.info("[CHECK] Database initialized")

    async def download_historical_data(
        self,
        symbols: List[str],
        start_date: datetime = None,
        end_date: datetime = None,
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Download historical data for multiple symbols

        Args:
            symbols: List of ticker symbols
            start_date: Start date (default: 5 years ago)
            end_date: End date (default: today)
            interval: Data interval (1d, 1h, 5m, etc.)

        Returns:
            Dictionary of symbol -> DataFrame
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365 * self.config.default_period_years)
        if end_date is None:
            end_date = datetime.now()

        logger.info(f"📥 Downloading historical data for {len(symbols)} symbols...")
        logger.info(f"   Period: {start_date.date()} to {end_date.date()}")
        logger.info(f"   Interval: {interval}")

        data = {}
        successful = 0

        for i, symbol in enumerate(symbols, 1):
            try:
                storage_symbol = _normalize_symbol(symbol)
                yf_sym = _to_yf_symbol(symbol)
                logger.info(f"  [{i}/{len(symbols)}] Downloading {storage_symbol} (yf: {yf_sym})...")

                # Download data using yfinance
                ticker = yf.Ticker(yf_sym)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )

                if not df.empty:
                    # Clean column names
                    df.columns = [col.lower() for col in df.columns]

                    # Calculate data quality score
                    quality_score = self._calculate_data_quality(df)

                    # Store in database under normalized symbol
                    await self._store_data(storage_symbol, interval, df, quality_score)

                    data[storage_symbol] = df
                    successful += 1
                    logger.info(f"    [CHECK] {storage_symbol}: {len(df)} bars (quality: {quality_score:.2%})")
                else:
                    logger.warning(f"    [WARNING]️ {storage_symbol}: No data available")

            except Exception as e:
                logger.error(f"    [ERROR] {storage_symbol if 'storage_symbol' in locals() else symbol}: Error downloading data: {e}")

        logger.info(f"[CHECK] Downloaded data for {successful}/{len(symbols)} symbols")
        return data

    def _calculate_data_quality(self, df: pd.DataFrame) -> float:
        """Calculate data quality score (0-1)"""
        if df.empty:
            return 0.0

        # Check for missing values
        completeness = 1.0 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))

        # Check for zero volumes (suspicious)
        if 'volume' in df.columns:
            non_zero_volume = (df['volume'] > 0).sum() / len(df)
        else:
            non_zero_volume = 1.0

        # Check for price consistency (no extreme jumps)
        if 'close' in df.columns:
            price_changes = df['close'].pct_change().abs()
            reasonable_changes = (price_changes < 0.5).sum() / len(price_changes)
        else:
            reasonable_changes = 1.0

        # Combined quality score
        quality_score = (completeness * 0.4 + non_zero_volume * 0.3 + reasonable_changes * 0.3)

        return quality_score

    async def _store_data(
        self,
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
        quality_score: float
    ):
        """Store historical data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stored_count = 0

        for timestamp, row in df.iterrows():
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO historical_data
                    (symbol, timeframe, timestamp, open, high, low, close, volume, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    timeframe,
                    timestamp.isoformat(),
                    float(row.get('open', 0)),
                    float(row.get('high', 0)),
                    float(row.get('low', 0)),
                    float(row.get('close', 0)),
                    int(row.get('volume', 0)),
                    'yfinance'
                ))
                stored_count += 1
            except Exception as e:
                logger.debug(f"Error storing data point for {symbol}: {e}")

        # Update metadata
        cursor.execute('''
            INSERT OR REPLACE INTO download_metadata
            (symbol, timeframe, start_date, end_date, record_count, data_quality_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            timeframe,
            df.index[0].isoformat() if len(df) > 0 else None,
            df.index[-1].isoformat() if len(df) > 0 else None,
            stored_count,
            quality_score
        ))

        conn.commit()
        conn.close()

    async def load_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        """Load historical data from database"""
        conn = sqlite3.connect(self.db_path)

        storage_symbol = _normalize_symbol(symbol)
        query = '''
            SELECT timestamp, open, high, low, close, volume
            FROM historical_data
            WHERE symbol = ? AND timeframe = ?
        '''
        params = [storage_symbol, timeframe]

        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date.isoformat())

        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date.isoformat())

        query += ' ORDER BY timestamp'

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            return df

        # On-demand download if missing locally and no explicit date bounds
        if start_date is None and end_date is None:
            try:
                await self.download_historical_data([symbol], interval=timeframe)
                # Retry with normalized symbol
                return await self.load_data(symbol, timeframe=timeframe)
            except Exception as e:
                logger.debug(f"On-demand download failed for {symbol}: {e}")

        return df

    def get_download_status(self) -> pd.DataFrame:
        """Get status of all downloaded data"""
        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT symbol, timeframe, start_date, end_date,
                   record_count, data_quality_score, downloaded_at
            FROM download_metadata
            ORDER BY symbol, timeframe
        '''

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    async def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators and features for ML training

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added features
        """
        logger.info("🔧 Calculating technical features...")

        # Make a copy to avoid modifying original
        data = df.copy()

        # Price-based features
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['sma_200'] = data['close'].rolling(200).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()

        # Momentum indicators
        data['rsi'] = self._calculate_rsi(data['close'])
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_hist'] = data['macd'] - data['macd_signal']

        # Volatility indicators
        data['atr'] = self._calculate_atr(data)
        bb_std = data['close'].rolling(20).std()
        data['bb_upper'] = data['sma_20'] + 2 * bb_std
        data['bb_lower'] = data['sma_20'] - 2 * bb_std
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['sma_20']
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])

        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']

        # Price changes
        data['return_1d'] = data['close'].pct_change()
        data['return_5d'] = data['close'].pct_change(periods=5)
        data['return_20d'] = data['close'].pct_change(periods=20)

        # Volatility
        data['volatility_20d'] = data['return_1d'].rolling(20).std()
        data['volatility_50d'] = data['return_1d'].rolling(50).std()

        # Price patterns
        data['higher_high'] = (data['high'] > data['high'].shift(1)).astype(int)
        data['lower_low'] = (data['low'] < data['low'].shift(1)).astype(int)

        # Trend strength
        data['trend_strength'] = abs(data['sma_20'] - data['sma_50']) / data['close']

        # Distance from moving averages
        data['dist_from_sma20'] = (data['close'] - data['sma_20']) / data['sma_20']
        data['dist_from_sma50'] = (data['close'] - data['sma_50']) / data['sma_50']

        logger.info(f"[CHECK] Calculated {len(data.columns) - len(df.columns)} features")

        return data

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()

        return atr

    async def prepare_training_data(
        self,
        data: pd.DataFrame,
        target_periods: int = 5,
        target_type: str = 'return'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for model training

        Args:
            data: DataFrame with features
            target_periods: Number of periods ahead to predict
            target_type: 'return' for regression, 'direction' for classification

        Returns:
            X (features), y (targets)
        """
        logger.info("🎯 Preparing training data...")

        # Calculate target
        if target_type == 'return':
            data['target'] = data['close'].pct_change(periods=target_periods).shift(-target_periods)
        elif target_type == 'direction':
            data['target'] = (data['close'].pct_change(periods=target_periods).shift(-target_periods) > 0).astype(int)
        else:
            raise ValueError(f"Unknown target_type: {target_type}")

        # Select feature columns (exclude OHLCV and target)
        feature_columns = [col for col in data.columns if col not in [
            'open', 'high', 'low', 'close', 'volume', 'target'
        ]]

        # Remove rows with NaN
        data_clean = data[feature_columns + ['target']].dropna()

        if len(data_clean) == 0:
            logger.warning("[WARNING]️ No valid data after removing NaN values")
            return np.array([]), np.array([])

        X = data_clean[feature_columns].values
        y = data_clean['target'].values

        logger.info(f"[CHECK] Prepared {len(X)} training samples with {len(feature_columns)} features")

        return X, y


# Global instance
_historical_pipeline = None

def get_historical_pipeline() -> HistoricalDataPipeline:
    """Get global historical data pipeline instance"""
    global _historical_pipeline
    if _historical_pipeline is None:
        _historical_pipeline = HistoricalDataPipeline()
    return _historical_pipeline


# Example usage
async def main():
    """Example usage of Historical Data Pipeline"""

    # Initialize pipeline
    pipeline = get_historical_pipeline()

    # Define symbols and date range
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY', 'QQQ', 'NVDA', 'AMZN']
    start_date = datetime.now() - timedelta(days=365*5)  # 5 years
    end_date = datetime.now()

    # Download historical data
    data = await pipeline.download_historical_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )

    # Show download status
    status = pipeline.get_download_status()
    print("\n" + "="*80)
    print("DOWNLOAD STATUS")
    print("="*80)
    print(status.to_string())
    print("="*80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

