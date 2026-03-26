#!/usr/bin/env python3
"""
AI Learning Engine for Prometheus Trading Platform
Revolutionary self-improving trading intelligence system
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import sqlite3
from dataclasses import dataclass, asdict
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import threading
from collections import deque, defaultdict
import yfinance as yf
import ta  # Technical Analysis library

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeOutcome:
    trade_id: str
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    side: str  # 'buy' or 'sell'
    entry_time: str
    exit_time: str
    profit_loss: float
    profit_loss_percent: float
    strategy_used: str
    market_conditions: Dict[str, Any]
    user_id: str
    success: bool

@dataclass
class MarketFeatures:
    timestamp: str
    symbol: str
    price: float
    volume: int
    volatility: float
    rsi: float
    macd: float
    bollinger_position: float
    volume_sma_ratio: float
    price_change_1h: float
    price_change_24h: float
    sentiment_score: float
    news_impact: float

@dataclass
class StrategyPerformance:
    strategy_id: str
    total_trades: int
    successful_trades: int
    success_rate: float
    avg_profit: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    last_updated: str

class AILearningEngine:
    def __init__(self, db_path: str = "ai_learning.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.trade_history = deque(maxlen=10000)
        self.market_features_history = deque(maxlen=50000)
        self.strategy_performance = {}
        
        # Learning parameters - ADJUSTED for faster learning
        self.min_trades_for_learning = 20  # Reduced from 50 to learn faster
        self.model_update_frequency = 50   # Reduced from 100 for more frequent updates
        self.feature_importance_threshold = 0.005  # More sensitive to features
        
        # Initialize database
        self._init_database()
        
        # Load existing models
        self._load_models()
        
        # Start background learning
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._background_learning, daemon=True)
        self.learning_thread.start()
        
        logger.info("AI Learning Engine initialized")

    def _init_database(self):
        """Initialize database for storing learning data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Trade outcomes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trade_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE,
                    symbol TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    quantity REAL,
                    side TEXT,
                    entry_time TEXT,
                    exit_time TEXT,
                    profit_loss REAL,
                    profit_loss_percent REAL,
                    strategy_used TEXT,
                    market_conditions TEXT,
                    user_id TEXT,
                    success BOOLEAN,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market features table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    price REAL,
                    volume INTEGER,
                    volatility REAL,
                    rsi REAL,
                    macd REAL,
                    bollinger_position REAL,
                    volume_sma_ratio REAL,
                    price_change_1h REAL,
                    price_change_24h REAL,
                    sentiment_score REAL,
                    news_impact REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Strategy performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id TEXT UNIQUE,
                    total_trades INTEGER,
                    successful_trades INTEGER,
                    success_rate REAL,
                    avg_profit REAL,
                    avg_loss REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    last_updated TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing AI learning database: {e}")

    def _load_models(self):
        """Load existing ML models from disk"""
        try:
            models_dir = "models"
            if os.path.exists(models_dir):
                for filename in os.listdir(models_dir):
                    if filename.endswith('.joblib'):
                        model_name = filename.replace('.joblib', '')
                        model_path = os.path.join(models_dir, filename)
                        self.models[model_name] = joblib.load(model_path)
                        logger.info(f"Loaded model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def _save_model(self, model_name: str, model: Any):
        """Save ML model to disk"""
        try:
            models_dir = "models"
            os.makedirs(models_dir, exist_ok=True)
            model_path = os.path.join(models_dir, f"{model_name}.joblib")
            joblib.dump(model, model_path)
            logger.info(f"Saved model: {model_name}")
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")

    async def record_trade_outcome(self, trade_outcome: TradeOutcome):
        """Record a trade outcome for learning"""
        try:
            # Add to memory
            self.trade_history.append(trade_outcome)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trade_outcomes 
                (trade_id, symbol, entry_price, exit_price, quantity, side, 
                 entry_time, exit_time, profit_loss, profit_loss_percent, 
                 strategy_used, market_conditions, user_id, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_outcome.trade_id,
                trade_outcome.symbol,
                trade_outcome.entry_price,
                trade_outcome.exit_price,
                trade_outcome.quantity,
                trade_outcome.side,
                trade_outcome.entry_time,
                trade_outcome.exit_time,
                trade_outcome.profit_loss,
                trade_outcome.profit_loss_percent,
                trade_outcome.strategy_used,
                json.dumps(trade_outcome.market_conditions),
                trade_outcome.user_id,
                trade_outcome.success
            ))
            
            conn.commit()
            conn.close()
            
            # Trigger learning if we have enough data
            if len(self.trade_history) % self.model_update_frequency == 0:
                asyncio.create_task(self._update_models())
            
            logger.info(f"Recorded trade outcome: {trade_outcome.trade_id}")
            
        except Exception as e:
            logger.error(f"Error recording trade outcome: {e}")

    async def extract_market_features(self, symbol: str) -> MarketFeatures:
        """Extract comprehensive market features for a symbol"""
        try:
            # Get market data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d", interval="1h")
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate technical indicators
            hist['RSI'] = ta.momentum.RSIIndicator(hist['Close']).rsi()
            hist['MACD'] = ta.trend.MACD(hist['Close']).macd()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(hist['Close'])
            hist['BB_upper'] = bb.bollinger_hband()
            hist['BB_lower'] = bb.bollinger_lband()
            hist['BB_position'] = (hist['Close'] - hist['BB_lower']) / (hist['BB_upper'] - hist['BB_lower'])
            
            # Volume indicators
            hist['Volume_SMA'] = hist['Volume'].rolling(window=20).mean()
            hist['Volume_Ratio'] = hist['Volume'] / hist['Volume_SMA']
            
            # Price changes
            hist['Price_Change_1h'] = hist['Close'].pct_change()
            hist['Price_Change_24h'] = hist['Close'].pct_change(periods=24)
            
            # Volatility
            hist['Volatility'] = hist['Close'].rolling(window=20).std()
            
            # Get latest values
            latest = hist.iloc[-1]
            
            # Mock sentiment and news impact (in real implementation, integrate with news APIs)
            sentiment_score = np.random.uniform(-1, 1)  # -1 to 1 scale
            news_impact = np.random.uniform(0, 1)       # 0 to 1 scale
            
            features = MarketFeatures(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                price=float(latest['Close']),
                volume=int(latest['Volume']),
                volatility=float(latest['Volatility']) if not pd.isna(latest['Volatility']) else 0.0,
                rsi=float(latest['RSI']) if not pd.isna(latest['RSI']) else 50.0,
                macd=float(latest['MACD']) if not pd.isna(latest['MACD']) else 0.0,
                bollinger_position=float(latest['BB_position']) if not pd.isna(latest['BB_position']) else 0.5,
                volume_sma_ratio=float(latest['Volume_Ratio']) if not pd.isna(latest['Volume_Ratio']) else 1.0,
                price_change_1h=float(latest['Price_Change_1h']) if not pd.isna(latest['Price_Change_1h']) else 0.0,
                price_change_24h=float(latest['Price_Change_24h']) if not pd.isna(latest['Price_Change_24h']) else 0.0,
                sentiment_score=sentiment_score,
                news_impact=news_impact
            )
            
            # Store features
            self.market_features_history.append(features)
            await self._store_market_features(features)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting market features for {symbol}: {e}")
            # Return default features
            return MarketFeatures(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                price=100.0,
                volume=1000000,
                volatility=0.02,
                rsi=50.0,
                macd=0.0,
                bollinger_position=0.5,
                volume_sma_ratio=1.0,
                price_change_1h=0.0,
                price_change_24h=0.0,
                sentiment_score=0.0,
                news_impact=0.0
            )

    async def _store_market_features(self, features: MarketFeatures):
        """Store market features in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO market_features 
                (timestamp, symbol, price, volume, volatility, rsi, macd, 
                 bollinger_position, volume_sma_ratio, price_change_1h, 
                 price_change_24h, sentiment_score, news_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                features.timestamp,
                features.symbol,
                features.price,
                features.volume,
                features.volatility,
                features.rsi,
                features.macd,
                features.bollinger_position,
                features.volume_sma_ratio,
                features.price_change_1h,
                features.price_change_24h,
                features.sentiment_score,
                features.news_impact
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing market features: {e}")

    async def predict_trade_success(self, symbol: str, strategy: str, 
                                  market_features: MarketFeatures) -> Tuple[float, Dict[str, float]]:
        """Predict probability of trade success using ML models"""
        try:
            model_name = f"success_predictor_{strategy}"
            
            if model_name not in self.models:
                # If no specific model, use general model or return default
                if "success_predictor_general" in self.models:
                    model_name = "success_predictor_general"
                else:
                    return 0.5, {"confidence": 0.1}  # Default prediction
            
            model = self.models[model_name]
            scaler = self.scalers.get(f"{model_name}_scaler")
            
            # Prepare features
            feature_vector = np.array([[
                market_features.price,
                market_features.volume,
                market_features.volatility,
                market_features.rsi,
                market_features.macd,
                market_features.bollinger_position,
                market_features.volume_sma_ratio,
                market_features.price_change_1h,
                market_features.price_change_24h,
                market_features.sentiment_score,
                market_features.news_impact
            ]])
            
            if scaler:
                feature_vector = scaler.transform(feature_vector)
            
            # Make prediction
            if hasattr(model, 'predict_proba'):
                prediction_proba = model.predict_proba(feature_vector)[0]
                success_probability = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
            else:
                success_probability = model.predict(feature_vector)[0]
            
            # Get feature importance if available
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = [
                    'price', 'volume', 'volatility', 'rsi', 'macd',
                    'bollinger_position', 'volume_sma_ratio', 'price_change_1h',
                    'price_change_24h', 'sentiment_score', 'news_impact'
                ]
                feature_importance = dict(zip(feature_names, model.feature_importances_))
            
            return float(success_probability), feature_importance
            
        except Exception as e:
            logger.error(f"Error predicting trade success: {e}")
            return 0.5, {"confidence": 0.1}

    async def _update_models(self):
        """Update ML models with new trade data"""
        try:
            if len(self.trade_history) < self.min_trades_for_learning:
                return
            
            logger.info("Updating ML models with new trade data...")
            
            # Prepare training data
            X, y = await self._prepare_training_data()
            
            if len(X) < self.min_trades_for_learning:
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train success prediction model
            success_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            success_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = success_model.score(X_train_scaled, y_train)
            test_score = success_model.score(X_test_scaled, y_test)
            
            logger.info(f"Model performance - Train: {train_score:.3f}, Test: {test_score:.3f}")
            
            # Save models
            model_name = "success_predictor_general"
            self.models[model_name] = success_model
            self.scalers[f"{model_name}_scaler"] = scaler
            
            self._save_model(model_name, success_model)
            self._save_model(f"{model_name}_scaler", scaler)
            
            logger.info("ML models updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating models: {e}")

    async def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from trade history"""
        try:
            X = []
            y = []
            
            for trade in self.trade_history:
                if 'market_features' in trade.market_conditions:
                    features = trade.market_conditions['market_features']
                    
                    feature_vector = [
                        features.get('price', 0),
                        features.get('volume', 0),
                        features.get('volatility', 0),
                        features.get('rsi', 50),
                        features.get('macd', 0),
                        features.get('bollinger_position', 0.5),
                        features.get('volume_sma_ratio', 1.0),
                        features.get('price_change_1h', 0),
                        features.get('price_change_24h', 0),
                        features.get('sentiment_score', 0),
                        features.get('news_impact', 0)
                    ]
                    
                    X.append(feature_vector)
                    y.append(1 if trade.success else 0)
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return np.array([]), np.array([])

    def _background_learning(self):
        """Background thread for continuous learning"""
        while self.learning_active:
            try:
                # Perform periodic model updates
                if len(self.trade_history) >= self.min_trades_for_learning:
                    asyncio.run(self._update_models())
                
                # Sleep for 1 hour
                threading.Event().wait(3600)
                
            except Exception as e:
                logger.error(f"Error in background learning: {e}")
                threading.Event().wait(3600)

    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get AI learning statistics"""
        try:
            return {
                "total_trades_learned": len(self.trade_history),
                "market_features_collected": len(self.market_features_history),
                "active_models": len(self.models),
                "learning_status": "active" if self.learning_active else "inactive",
                "last_model_update": datetime.now().isoformat(),
                "model_performance": {
                    name: {
                        "type": type(model).__name__,
                        "features": getattr(model, 'n_features_in_', 'unknown')
                    } for name, model in self.models.items()
                }
            }
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}")
            return {"error": str(e)}

    def stop_learning(self):
        """Stop background learning"""
        self.learning_active = False

# Global instance
ai_learning_engine = AILearningEngine()
