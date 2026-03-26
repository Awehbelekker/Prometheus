#!/usr/bin/env python3
"""
Predictive Regime Forecasting
Predicts market regime changes BEFORE they happen for proactive trading
"""

import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class RegimeForecastingModel(nn.Module):
    """
    Neural network to predict future market regimes
    """
    
    def __init__(self, input_dim: int = 30, hidden_dim: int = 128, num_regimes: int = 4):
        super().__init__()
        
        # Regime types: general, pattern_recognition, optimization, volatile
        self.num_regimes = num_regimes
        
        # LSTM for sequence modeling
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True, num_layers=2)
        
        # Regime prediction head
        self.regime_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_regimes),
            nn.Softmax(dim=-1)
        )
        
        # Transition probability head (predict regime changes)
        self.transition_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_regimes * num_regimes),
            nn.Softmax(dim=-1)
        )
        
        # Time horizon head (predict when regime will change)
        self.horizon_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()  # Output: 0-1 (0 = immediate, 1 = far future)
        )
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input sequence (batch, seq_len, features)
            
        Returns:
            (current_regime_probs, transition_probs, time_horizon)
        """
        # LSTM encoding
        lstm_out, (h_n, c_n) = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]  # Last timestep
        
        # Predictions
        regime_probs = self.regime_head(last_hidden)
        transition_probs = self.transition_head(last_hidden)
        time_horizon = self.horizon_head(last_hidden)
        
        return regime_probs, transition_probs, time_horizon


class PredictiveRegimeForecaster:
    """
    Predictive Regime Forecasting System
    Predicts market regime changes before they happen
    """
    
    def __init__(self, sequence_length: int = 20, forecast_horizon: int = 5):
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        
        # Regime types
        self.regime_types = ['general', 'pattern_recognition', 'optimization', 'volatile']
        self.regime_map = {r: i for i, r in enumerate(self.regime_types)}
        
        # Model
        self.model = RegimeForecastingModel(
            input_dim=30,
            hidden_dim=128,
            num_regimes=len(self.regime_types)
        )
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        
        # History buffer
        self.history_buffer = deque(maxlen=1000)
        
        # Regime history
        self.regime_history = deque(maxlen=100)
        
        logger.info("✅ Predictive Regime Forecaster initialized")
    
    def encode_features(self, market_data: Dict, indicators: Dict) -> np.ndarray:
        """
        Encode market data into feature vector
        
        Args:
            market_data: Market data
            indicators: Technical indicators
            
        Returns:
            Feature vector
        """
        features = []
        
        # Price features
        if 'price' in market_data:
            features.append(market_data['price'] / 1000.0)
        if 'volume' in market_data:
            features.append(market_data['volume'] / 1e6)
        
        # Indicator features
        features.append(indicators.get('rsi', 50) / 100.0)
        features.append(indicators.get('macd', 0) / 10.0)
        features.append(indicators.get('volatility', 0) * 100)
        features.append(indicators.get('momentum', 0) / 10.0)
        
        # Trend features
        features.append(indicators.get('trend_strength', 0))
        features.append(indicators.get('trend_direction', 0))
        
        # Volume features
        features.append(indicators.get('volume_trend', 0))
        features.append(indicators.get('volume_ratio', 1.0))
        
        # Market structure features
        features.append(indicators.get('support_level', 0) / 1000.0)
        features.append(indicators.get('resistance_level', 0) / 1000.0)
        
        # Pad to 30 features
        while len(features) < 30:
            features.append(0.0)
        features = features[:30]
        
        return np.array(features, dtype=np.float32)
    
    def detect_current_regime(self, market_data: Dict, indicators: Dict) -> str:
        """
        Detect current market regime
        
        Returns:
            Regime type
        """
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        volatility = indicators.get('volatility', 0)
        
        # Pattern recognition regime
        if abs(rsi - 50) > 25 or abs(macd) > 1.5:
            return 'pattern_recognition'
        
        # Optimization regime
        if 0.5 < abs(macd) < 1.5:
            return 'optimization'
        
        # Volatile regime
        if volatility > 0.03:
            return 'volatile'
        
        return 'general'
    
    def predict_future_regime(self, market_data: Dict, indicators: Dict, 
                             history: List[Dict] = None) -> Dict[str, Any]:
        """
        Predict future market regime
        
        Args:
            market_data: Current market data
            indicators: Current indicators
            history: Historical data (optional)
            
        Returns:
            Prediction with regime, probability, time horizon
        """
        # Build sequence from history
        if history is None:
            history = list(self.history_buffer)
        
        # Add current state
        current_features = self.encode_features(market_data, indicators)
        history.append({
            'features': current_features,
            'timestamp': datetime.now()
        })
        
        # Build sequence
        if len(history) < self.sequence_length:
            # Pad with zeros
            sequence = np.zeros((self.sequence_length, 30), dtype=np.float32)
            start_idx = self.sequence_length - len(history)
            for i, h in enumerate(history):
                sequence[start_idx + i] = h['features']
        else:
            # Use last sequence_length items
            sequence = np.array([h['features'] for h in history[-self.sequence_length:]])
        
        # Predict
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)  # Add batch dimension
        
        with torch.no_grad():
            regime_probs, transition_probs, time_horizon = self.model(sequence_tensor)
            
            regime_probs = regime_probs.squeeze().numpy()
            transition_probs = transition_probs.squeeze().numpy()
            time_horizon = time_horizon.squeeze().item()
        
        # Get predicted regime
        predicted_regime_idx = np.argmax(regime_probs)
        predicted_regime = self.regime_types[predicted_regime_idx]
        confidence = regime_probs[predicted_regime_idx]
        
        # Get current regime
        current_regime = self.detect_current_regime(market_data, indicators)
        
        # Check if regime change is predicted
        regime_change = predicted_regime != current_regime
        
        # Estimate time to change (in hours)
        time_to_change_hours = time_horizon * 24  # Scale to hours
        
        return {
            'current_regime': current_regime,
            'predicted_regime': predicted_regime,
            'regime_change_predicted': regime_change,
            'confidence': float(confidence),
            'time_to_change_hours': float(time_to_change_hours),
            'regime_probabilities': {
                self.regime_types[i]: float(regime_probs[i])
                for i in range(len(self.regime_types))
            },
            'transition_probabilities': transition_probs.tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    def update_history(self, market_data: Dict, indicators: Dict):
        """Update history buffer"""
        features = self.encode_features(market_data, indicators)
        regime = self.detect_current_regime(market_data, indicators)
        
        self.history_buffer.append({
            'features': features,
            'regime': regime,
            'timestamp': datetime.now()
        })
        
        self.regime_history.append({
            'regime': regime,
            'timestamp': datetime.now()
        })
    
    def train_on_history(self, epochs: int = 10):
        """
        Train model on historical data
        
        Args:
            epochs: Number of training epochs
        """
        if len(self.history_buffer) < self.sequence_length + 1:
            logger.warning("Not enough history for training")
            return
        
        # Prepare training data
        sequences = []
        targets_regime = []
        targets_transition = []
        targets_horizon = []
        
        for i in range(len(self.history_buffer) - self.sequence_length):
            # Input sequence
            seq = np.array([h['features'] for h in list(self.history_buffer)[i:i+self.sequence_length]])
            sequences.append(seq)
            
            # Target: next regime
            next_regime = list(self.history_buffer)[i+self.sequence_length]['regime']
            regime_idx = self.regime_map[next_regime]
            targets_regime.append(regime_idx)
            
            # Target: transition (simplified - 1 if regime changed)
            current_regime = list(self.history_buffer)[i+self.sequence_length-1]['regime']
            transition = 1.0 if next_regime != current_regime else 0.0
            targets_transition.append(transition)
            
            # Target: time horizon (simplified - based on actual time difference)
            time_diff = (list(self.history_buffer)[i+self.sequence_length]['timestamp'] - 
                        list(self.history_buffer)[i+self.sequence_length-1]['timestamp'])
            horizon = min(time_diff.total_seconds() / 3600 / 24, 1.0)  # Normalize to 0-1
            targets_horizon.append(horizon)
        
        if not sequences:
            return
        
        # Convert to tensors
        X = torch.tensor(np.array(sequences), dtype=torch.float32)
        y_regime = torch.tensor(targets_regime, dtype=torch.long)
        y_transition = torch.tensor(targets_transition, dtype=torch.float32)
        y_horizon = torch.tensor(targets_horizon, dtype=torch.float32)
        
        # Training loop
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            # Forward pass
            regime_probs, transition_probs, time_horizon = self.model(X)
            
            # Losses
            regime_loss = nn.CrossEntropyLoss()(regime_probs, y_regime)
            transition_loss = nn.MSELoss()(transition_probs[:, 0], y_transition)
            horizon_loss = nn.MSELoss()(time_horizon.squeeze(), y_horizon)
            
            total_loss = regime_loss + 0.5 * transition_loss + 0.5 * horizon_loss
            
            # Backward pass
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            
            if epoch % 5 == 0:
                logger.info(f"Training epoch {epoch}: Loss={total_loss.item():.4f}, "
                          f"Regime={regime_loss.item():.4f}, "
                          f"Transition={transition_loss.item():.4f}, "
                          f"Horizon={horizon_loss.item():.4f}")
    
    def save_model(self, path: str = "models/regime_forecaster.pt"):
        """Save model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'regime_types': self.regime_types
        }, path)
        logger.info(f"Saved regime forecaster to {path}")
    
    def load_model(self, path: str = "models/regime_forecaster.pt"):
        """Load model"""
        if Path(path).exists():
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            logger.info(f"Loaded regime forecaster from {path}")
            return True
        return False

