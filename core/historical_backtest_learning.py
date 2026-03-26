"""
PROMETHEUS Historical Backtest Learning System
==============================================
Train AI models on decades of historical trading data
Learns patterns from market crashes, bull runs, and consolidations
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import yfinance as yf
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import joblib
import json

logger = logging.getLogger(__name__)


@dataclass
class HistoricalEra:
    """Defines a historical market era for training"""
    name: str
    start_date: str
    end_date: str
    characteristics: List[str]
    regime: str  # bull, bear, volatile, sideways


MARKET_ERAS = [
    HistoricalEra("Dot-com Bubble", "1997-01-01", "2000-03-10", 
                  ["tech_mania", "high_valuations", "retail_frenzy"], "bull"),
    HistoricalEra("Dot-com Crash", "2000-03-11", "2002-10-09",
                  ["tech_collapse", "recession", "fear"], "bear"),
    HistoricalEra("Housing Boom", "2003-01-01", "2007-10-09",
                  ["real_estate", "low_rates", "leverage"], "bull"),
    HistoricalEra("Financial Crisis", "2007-10-10", "2009-03-09",
                  ["banking_collapse", "panic", "deleveraging"], "bear"),
    HistoricalEra("QE Recovery", "2009-03-10", "2015-12-31",
                  ["central_bank", "low_volatility", "steady_growth"], "bull"),
    HistoricalEra("Trade War Era", "2018-01-01", "2019-12-31",
                  ["tariffs", "uncertainty", "volatility"], "volatile"),
    HistoricalEra("COVID Crash", "2020-02-19", "2020-03-23",
                  ["pandemic", "flash_crash", "fear"], "bear"),
    HistoricalEra("COVID Recovery", "2020-03-24", "2021-12-31",
                  ["stimulus", "meme_stocks", "crypto_boom"], "bull"),
    HistoricalEra("Inflation Bear", "2022-01-01", "2022-10-12",
                  ["rate_hikes", "inflation", "tech_selloff"], "bear"),
    HistoricalEra("AI Bull Run", "2023-01-01", "2024-12-31",
                  ["ai_hype", "magnificent_7", "concentration"], "bull"),
]


class HistoricalPatternLearner(nn.Module):
    """Neural network that learns from historical market patterns"""
    
    def __init__(self, input_dim: int = 64, hidden_dim: int = 256, num_regimes: int = 4):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Regime classifier
        self.regime_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_regimes)
        )
        
        # Action predictor (BUY, HOLD, SELL)
        self.action_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 3)
        )
        
        # Return predictor
        self.return_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        encoded = self.encoder(x)
        return {
            'regime': self.regime_head(encoded),
            'action': self.action_head(encoded),
            'return': self.return_head(encoded)
        }


class HistoricalBacktestLearning:
    """
    Learn from decades of historical market data
    Extracts patterns from different market regimes
    """
    
    def __init__(self, checkpoint_dir: str = 'trained_models/historical'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = HistoricalPatternLearner().to(self.device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-4)
        
        self.scaler = StandardScaler()
        self.regime_encoder = {'bull': 0, 'bear': 1, 'volatile': 2, 'sideways': 3}
        
        # Training history
        self.training_history = {
            'losses': [],
            'regime_accuracy': [],
            'action_accuracy': [],
            'eras_trained': []
        }
        
        logger.info(f"📚 Historical Backtest Learning initialized on {self.device}")
    
    async def fetch_historical_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """Fetch historical data for multiple symbols"""
        data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if len(df) > 50:
                    data[symbol] = df
                    logger.info(f"  ✓ {symbol}: {len(df)} days")
                    
            except Exception as e:
                logger.warning(f"  ✗ {symbol}: {e}")
        
        return data
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features from OHLCV data"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['high_low_range'] = (df['High'] - df['Low']) / df['Close']
        features['close_to_high'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-8)
        
        # Moving averages
        for period in [5, 10, 20, 50, 200]:
            features[f'sma_{period}'] = df['Close'].rolling(period).mean() / df['Close']
            features[f'returns_sma_{period}'] = features['returns'].rolling(period).mean()
        
        # Volatility
        for period in [5, 10, 20]:
            features[f'volatility_{period}'] = features['returns'].rolling(period).std()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        features['rsi'] = 100 - (100 / (1 + gain / (loss + 1e-8)))
        
        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        features['macd'] = (ema12 - ema26) / df['Close']
        features['macd_signal'] = features['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        sma20 = df['Close'].rolling(20).mean()
        std20 = df['Close'].rolling(20).std()
        features['bb_position'] = (df['Close'] - sma20) / (2 * std20 + 1e-8)
        
        # Volume features
        features['volume_sma'] = df['Volume'].rolling(20).mean() / df['Volume']
        features['volume_change'] = df['Volume'].pct_change()
        
        # Momentum
        for period in [5, 10, 20]:
            features[f'momentum_{period}'] = df['Close'] / df['Close'].shift(period) - 1
        
        # Target: Next day's direction
        features['target_direction'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        features['target_return'] = df['Close'].shift(-1) / df['Close'] - 1
        
        return features.dropna()
    
    async def train_on_era(self, era: HistoricalEra, symbols: List[str]) -> Dict[str, Any]:
        """Train on a specific historical era"""
        logger.info(f"\n  Training on {era.name} ({era.start_date} to {era.end_date})")
        logger.info(f"  Regime: {era.regime}, Characteristics: {era.characteristics}")
        
        # Fetch data
        data = await self.fetch_historical_data(symbols, era.start_date, era.end_date)
        
        if not data:
            return {'success': False, 'error': 'No data'}
        
        # Combine all features
        all_features = []
        all_targets = []
        all_returns = []
        
        for symbol, df in data.items():
            features = self.engineer_features(df)
            
            if len(features) < 50:
                continue
            
            # Get feature columns (exclude targets)
            feature_cols = [c for c in features.columns if not c.startswith('target')]
            
            X = features[feature_cols].values
            y_direction = features['target_direction'].values
            y_return = features['target_return'].values
            
            all_features.append(X)
            all_targets.append(y_direction)
            all_returns.append(y_return)
        
        if not all_features:
            return {'success': False, 'error': 'Insufficient data'}
        
        # Combine data
        X = np.vstack(all_features)
        y_direction = np.concatenate(all_targets)
        y_return = np.concatenate(all_returns)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Pad/truncate to fixed size
        if X_scaled.shape[1] < 64:
            X_scaled = np.pad(X_scaled, ((0, 0), (0, 64 - X_scaled.shape[1])))
        else:
            X_scaled = X_scaled[:, :64]
        
        # Create regime labels
        regime_labels = np.full(len(X_scaled), self.regime_encoder[era.regime])
        
        # Convert to tensors
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        y_direction_tensor = torch.tensor(y_direction, dtype=torch.long).to(self.device)
        y_return_tensor = torch.tensor(y_return, dtype=torch.float32).to(self.device)
        regime_tensor = torch.tensor(regime_labels, dtype=torch.long).to(self.device)
        
        # Training loop
        self.model.train()
        batch_size = 64
        total_loss = 0
        correct = 0
        total = 0
        
        for i in range(0, len(X_tensor) - batch_size, batch_size):
            batch_X = X_tensor[i:i + batch_size]
            batch_y_dir = y_direction_tensor[i:i + batch_size]
            batch_y_ret = y_return_tensor[i:i + batch_size]
            batch_regime = regime_tensor[i:i + batch_size]
            
            self.optimizer.zero_grad()
            
            outputs = self.model(batch_X)
            
            # Multi-task loss
            action_loss = nn.CrossEntropyLoss()(outputs['action'], batch_y_dir)
            regime_loss = nn.CrossEntropyLoss()(outputs['regime'], batch_regime)
            return_loss = nn.MSELoss()(outputs['return'].squeeze(), batch_y_ret)
            
            loss = action_loss + 0.5 * regime_loss + 0.1 * return_loss
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            predictions = outputs['action'].argmax(dim=1)
            correct += (predictions == batch_y_dir).sum().item()
            total += batch_y_dir.size(0)
        
        accuracy = correct / total if total > 0 else 0
        avg_loss = total_loss / (total // batch_size + 1)
        
        self.training_history['eras_trained'].append(era.name)
        self.training_history['losses'].append(avg_loss)
        self.training_history['action_accuracy'].append(accuracy)
        
        return {
            'success': True,
            'era': era.name,
            'samples': total,
            'loss': avg_loss,
            'accuracy': accuracy
        }
    
    async def train_on_all_eras(
        self,
        symbols: List[str] = None,
        epochs_per_era: int = 3
    ) -> Dict[str, Any]:
        """Train on all historical market eras"""
        if symbols is None:
            symbols = ['SPY', 'QQQ', 'DIA', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']
        
        results = {}
        
        logger.info("\n" + "=" * 60)
        logger.info("  HISTORICAL BACKTEST LEARNING")
        logger.info("  Training on decades of market data")
        logger.info("=" * 60)
        
        for era in MARKET_ERAS:
            for epoch in range(epochs_per_era):
                result = await self.train_on_era(era, symbols)
                if result['success']:
                    logger.info(f"    Epoch {epoch + 1}: Loss={result['loss']:.4f}, "
                               f"Accuracy={result['accuracy']:.2%}")
            
            results[era.name] = result
        
        # Save checkpoint
        self.save_checkpoint()
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success', False))
        logger.info(f"\n  ✅ Trained on {successful}/{len(MARKET_ERAS)} eras")
        
        return results
    
    def save_checkpoint(self):
        """Save model checkpoint"""
        checkpoint = {
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'scaler': self.scaler,
            'training_history': self.training_history,
            'timestamp': datetime.now().isoformat()
        }
        
        path = self.checkpoint_dir / 'historical_pattern_learner.pt'
        torch.save(checkpoint, path)
        logger.info(f"  💾 Checkpoint saved to {path}")
    
    def load_checkpoint(self):
        """Load model checkpoint"""
        path = self.checkpoint_dir / 'historical_pattern_learner.pt'
        
        if path.exists():
            checkpoint = torch.load(path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state'])
            self.scaler = checkpoint['scaler']
            self.training_history = checkpoint['training_history']
            logger.info(f"  📂 Loaded checkpoint from {path}")
            return True
        return False
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Make predictions using learned historical patterns"""
        self.model.eval()
        
        with torch.no_grad():
            # Scale and pad features
            X = self.scaler.transform(features.reshape(1, -1))
            if X.shape[1] < 64:
                X = np.pad(X, ((0, 0), (0, 64 - X.shape[1])))
            else:
                X = X[:, :64]
            
            X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
            outputs = self.model(X_tensor)
            
            action_probs = torch.softmax(outputs['action'], dim=1).cpu().numpy()[0]
            regime_probs = torch.softmax(outputs['regime'], dim=1).cpu().numpy()[0]
            expected_return = outputs['return'].cpu().numpy()[0][0]
            
            actions = ['HOLD', 'BUY', 'SELL']
            regimes = ['bull', 'bear', 'volatile', 'sideways']
            
            return {
                'action': actions[action_probs.argmax()],
                'action_confidence': float(action_probs.max()),
                'action_probs': {a: float(p) for a, p in zip(actions, action_probs)},
                'regime': regimes[regime_probs.argmax()],
                'regime_confidence': float(regime_probs.max()),
                'expected_return': float(expected_return)
            }


async def train_historical_backtest(symbols: List[str] = None) -> Dict[str, Any]:
    """Convenience function to run historical training"""
    learner = HistoricalBacktestLearning()
    return await learner.train_on_all_eras(symbols)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(train_historical_backtest())
