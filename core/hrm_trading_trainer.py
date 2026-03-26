#!/usr/bin/env python3
"""
HRM Trading-Specific Training System
Trains Hierarchical Reasoning Model on trading decisions and market patterns
"""

import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json
import pickle

logger = logging.getLogger(__name__)


@dataclass
class TradingTrainingSample:
    """Single training sample for HRM trading"""
    market_features: np.ndarray  # Price, volume, indicators
    technical_indicators: np.ndarray  # RSI, MACD, etc.
    sentiment_score: float
    action: int  # 0=HOLD, 1=BUY, 2=SELL
    reward: float  # Profit/loss from this decision
    confidence: float
    symbol: str
    timestamp: str


class TradingDataset(Dataset):
    """Dataset for HRM trading training"""
    
    def __init__(self, samples: List[TradingTrainingSample], seq_len: int = 64):
        self.samples = samples
        self.seq_len = seq_len
        
        # Action vocabulary: HOLD=0, BUY=1, SELL=2
        self.action_vocab_size = 3
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]
        
        # Tokenize market features into sequence
        market_tokens = self._tokenize_market_data(sample.market_features)
        indicator_tokens = self._tokenize_indicators(sample.technical_indicators)
        
        # Combine into input sequence
        combined = np.concatenate([market_tokens, indicator_tokens])
        
        # Pad or truncate to seq_len
        if len(combined) < self.seq_len:
            combined = np.pad(combined, (0, self.seq_len - len(combined)), mode='constant')
        else:
            combined = combined[:self.seq_len]
        
        return {
            'inputs': torch.tensor(combined, dtype=torch.long),
            'labels': torch.tensor(sample.action, dtype=torch.long),
            'reward': torch.tensor(sample.reward, dtype=torch.float32),
            'confidence': torch.tensor(sample.confidence, dtype=torch.float32)
        }
    
    def _tokenize_market_data(self, features: np.ndarray) -> np.ndarray:
        """Convert market data to tokens (quantized)"""
        # Quantize to 256 levels (0-255)
        normalized = np.clip(features, -3, 3) / 3  # Assume normalized features
        tokens = ((normalized + 1) * 127.5).astype(np.int32)
        return np.clip(tokens, 0, 255)
    
    def _tokenize_indicators(self, indicators: np.ndarray) -> np.ndarray:
        """Convert technical indicators to tokens"""
        normalized = np.clip(indicators, 0, 100) / 100
        tokens = (normalized * 255).astype(np.int32)
        return np.clip(tokens, 0, 255)


class TradingHRMHead(nn.Module):
    """Trading-specific output head for HRM"""
    
    def __init__(self, hidden_size: int, num_actions: int = 3):
        super().__init__()
        
        self.action_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, num_actions)
        )
        
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
        self.value_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, 1)
        )
    
    def forward(self, hidden_states: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Pool over sequence dimension (mean pooling)
        pooled = hidden_states.mean(dim=1)
        
        return {
            'action_logits': self.action_head(pooled),
            'confidence': self.confidence_head(pooled).squeeze(-1),
            'value': self.value_head(pooled).squeeze(-1)
        }


class HRMTradingTrainer:
    """
    Trains HRM on trading decisions
    Uses the official HRM architecture with trading-specific heads
    """
    
    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        hidden_size: int = 512,
        device: str = 'cpu',
        learning_rate: float = 1e-4,
        checkpoint_dir: str = 'hrm_trading_checkpoints'
    ):
        self.device = device
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Training data storage
        self.training_samples: List[TradingTrainingSample] = []
        self.validation_samples: List[TradingTrainingSample] = []
        
        # Training history
        self.training_history = {
            'losses': [],
            'accuracies': [],
            'rewards': [],
            'epochs': 0
        }
        
        # Initialize trading head
        self.trading_head = TradingHRMHead(hidden_size).to(device)
        
        # Encoder for market data
        self.market_encoder = self._create_market_encoder()
        
        # Load base checkpoint if provided
        if checkpoint_path:
            self._load_base_checkpoint(checkpoint_path)
        
        # Optimizer
        self.optimizer = optim.AdamW(
            list(self.trading_head.parameters()) + list(self.market_encoder.parameters()),
            lr=learning_rate,
            weight_decay=0.01
        )
        
        # Scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100, eta_min=1e-6
        )
        
        logger.info(f"HRM Trading Trainer initialized on {device}")
    
    def _create_market_encoder(self) -> nn.Module:
        """Create encoder for market data"""
        encoder = nn.Sequential(
            nn.Embedding(256, self.hidden_size // 4),  # Token embedding
            nn.LSTM(
                input_size=self.hidden_size // 4,
                hidden_size=self.hidden_size,
                num_layers=2,
                batch_first=True,
                dropout=0.1,
                bidirectional=True
            )
        ).to(self.device)
        return encoder
    
    def _load_base_checkpoint(self, path: str):
        """Load base HRM checkpoint for transfer learning"""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            logger.info(f"Loaded base checkpoint from {path}")
            # Would extract and adapt weights here
        except Exception as e:
            logger.warning(f"Could not load base checkpoint: {e}")
    
    def add_training_sample(
        self,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, float],
        action: str,
        profit_loss: float,
        confidence: float,
        symbol: str
    ):
        """Add a training sample from a completed trade"""
        
        # Convert market data to features
        market_features = self._extract_market_features(market_data)
        indicator_features = self._extract_indicator_features(technical_indicators)
        
        # Map action to int
        action_map = {'HOLD': 0, 'BUY': 1, 'SELL': 2}
        action_int = action_map.get(action.upper(), 0)
        
        # Calculate reward (scaled profit/loss)
        reward = np.clip(profit_loss / 100, -1, 1)  # Normalize to [-1, 1]
        
        sample = TradingTrainingSample(
            market_features=market_features,
            technical_indicators=indicator_features,
            sentiment_score=market_data.get('sentiment', 0.5),
            action=action_int,
            reward=reward,
            confidence=confidence,
            symbol=symbol,
            timestamp=datetime.now().isoformat()
        )
        
        self.training_samples.append(sample)
        
        # Move some to validation (10%)
        if len(self.training_samples) % 10 == 0 and len(self.training_samples) > 10:
            self.validation_samples.append(self.training_samples.pop(-2))
        
        logger.info(f"Added training sample: {symbol} {action} (reward={reward:.3f})")
        
        return len(self.training_samples)
    
    def _extract_market_features(self, market_data: Dict) -> np.ndarray:
        """Extract features from market data"""
        features = []
        
        # Price features
        price = market_data.get('price', 0)
        features.append(np.log1p(price) if price > 0 else 0)
        
        # Volume
        volume = market_data.get('volume', 0)
        features.append(np.log1p(volume) if volume > 0 else 0)
        
        # Price changes
        features.append(market_data.get('change_percent', 0) / 10)
        
        # Bid/Ask spread
        bid = market_data.get('bid', price)
        ask = market_data.get('ask', price)
        spread = (ask - bid) / price if price > 0 else 0
        features.append(spread * 100)
        
        # Pad to fixed size
        while len(features) < 32:
            features.append(0)
        
        return np.array(features[:32], dtype=np.float32)
    
    def _extract_indicator_features(self, indicators: Dict) -> np.ndarray:
        """Extract technical indicator features"""
        features = []
        
        features.append(indicators.get('rsi', 50))
        features.append(indicators.get('macd', 0))
        features.append(indicators.get('macd_signal', 0))
        features.append(indicators.get('bb_upper', 0))
        features.append(indicators.get('bb_lower', 0))
        features.append(indicators.get('sma_20', 0))
        features.append(indicators.get('sma_50', 0))
        features.append(indicators.get('volume_sma', 0))
        
        # Pad to fixed size
        while len(features) < 16:
            features.append(0)
        
        return np.array(features[:16], dtype=np.float32)
    
    def train(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        min_samples: int = 100
    ) -> Dict[str, Any]:
        """Train HRM on collected trading data"""
        
        if len(self.training_samples) < min_samples:
            logger.warning(f"Not enough samples ({len(self.training_samples)} < {min_samples})")
            return {
                'status': 'insufficient_data',
                'samples': len(self.training_samples),
                'required': min_samples
            }
        
        logger.info(f"Starting training with {len(self.training_samples)} samples")
        
        # Create dataset and dataloader
        dataset = TradingDataset(self.training_samples)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
        )
        
        # Loss functions
        action_criterion = nn.CrossEntropyLoss()
        value_criterion = nn.MSELoss()
        
        # Training loop
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        self.trading_head.train()
        self.market_encoder.train()
        
        for epoch in range(epochs):
            epoch_loss = 0
            epoch_correct = 0
            epoch_total = 0
            
            for batch in dataloader:
                inputs = batch['inputs'].to(self.device)
                labels = batch['labels'].to(self.device)
                rewards = batch['reward'].to(self.device)
                
                self.optimizer.zero_grad()
                
                # Encode market data
                embedded = self.market_encoder[0](inputs)  # Embedding
                lstm_out, _ = self.market_encoder[1](embedded)  # LSTM
                
                # Bidirectional LSTM output needs reshaping
                hidden = lstm_out[:, :, :self.hidden_size] + lstm_out[:, :, self.hidden_size:]
                
                # Get trading predictions
                outputs = self.trading_head(hidden)
                
                # Action loss (classification)
                action_loss = action_criterion(outputs['action_logits'], labels)
                
                # Value loss (reward prediction)
                value_loss = value_criterion(outputs['value'], rewards)
                
                # Combined loss
                loss = action_loss + 0.5 * value_loss
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    list(self.trading_head.parameters()) + list(self.market_encoder.parameters()),
                    max_norm=1.0
                )
                self.optimizer.step()
                
                # Track metrics
                epoch_loss += loss.item()
                predictions = outputs['action_logits'].argmax(dim=1)
                epoch_correct += (predictions == labels).sum().item()
                epoch_total += labels.size(0)
            
            # Update learning rate
            self.scheduler.step()
            
            # Record history
            accuracy = epoch_correct / epoch_total if epoch_total > 0 else 0
            avg_loss = epoch_loss / len(dataloader)
            
            self.training_history['losses'].append(avg_loss)
            self.training_history['accuracies'].append(accuracy)
            self.training_history['epochs'] = epoch + 1
            
            logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2%}")
            
            total_loss += avg_loss
            correct_predictions += epoch_correct
            total_predictions += epoch_total
        
        # Save checkpoint
        self.save_checkpoint()
        
        return {
            'status': 'complete',
            'epochs': epochs,
            'final_loss': self.training_history['losses'][-1] if self.training_history['losses'] else 0,
            'final_accuracy': self.training_history['accuracies'][-1] if self.training_history['accuracies'] else 0,
            'total_samples': len(self.training_samples)
        }
    
    def predict(self, market_data: Dict, technical_indicators: Dict) -> Dict[str, Any]:
        """Make trading prediction using trained model"""
        
        self.trading_head.eval()
        self.market_encoder.eval()
        
        with torch.no_grad():
            # Extract features
            market_features = self._extract_market_features(market_data)
            indicator_features = self._extract_indicator_features(technical_indicators)
            
            # Tokenize
            market_tokens = TradingDataset._tokenize_market_data(None, market_features)
            indicator_tokens = TradingDataset._tokenize_indicators(None, indicator_features)
            
            combined = np.concatenate([market_tokens, indicator_tokens])
            if len(combined) < 64:
                combined = np.pad(combined, (0, 64 - len(combined)), mode='constant')
            else:
                combined = combined[:64]
            
            inputs = torch.tensor(combined, dtype=torch.long).unsqueeze(0).to(self.device)
            
            # Encode
            embedded = self.market_encoder[0](inputs)
            lstm_out, _ = self.market_encoder[1](embedded)
            hidden = lstm_out[:, :, :self.hidden_size] + lstm_out[:, :, self.hidden_size:]
            
            # Predict
            outputs = self.trading_head(hidden)
            
            action_probs = torch.softmax(outputs['action_logits'], dim=1)
            action = action_probs.argmax(dim=1).item()
            
            action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
            
            return {
                'action': action_map[action],
                'confidence': outputs['confidence'].item(),
                'expected_value': outputs['value'].item(),
                'action_probabilities': {
                    'HOLD': action_probs[0, 0].item(),
                    'BUY': action_probs[0, 1].item(),
                    'SELL': action_probs[0, 2].item()
                }
            }
    
    def save_checkpoint(self, name: str = 'latest'):
        """Save training checkpoint"""
        checkpoint_path = self.checkpoint_dir / f"hrm_trading_{name}.pt"
        
        checkpoint = {
            'trading_head': self.trading_head.state_dict(),
            'market_encoder': self.market_encoder.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'scheduler': self.scheduler.state_dict(),
            'training_history': self.training_history,
            'timestamp': datetime.now().isoformat()
        }
        
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved checkpoint to {checkpoint_path}")
        
        # Also save training samples
        samples_path = self.checkpoint_dir / f"training_samples_{name}.pkl"
        with open(samples_path, 'wb') as f:
            pickle.dump({
                'training': self.training_samples,
                'validation': self.validation_samples
            }, f)
        
        return str(checkpoint_path)
    
    def load_checkpoint(self, name: str = 'latest') -> bool:
        """Load training checkpoint"""
        checkpoint_path = self.checkpoint_dir / f"hrm_trading_{name}.pt"
        
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
            return False
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            self.trading_head.load_state_dict(checkpoint['trading_head'])
            self.market_encoder.load_state_dict(checkpoint['market_encoder'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.scheduler.load_state_dict(checkpoint['scheduler'])
            self.training_history = checkpoint['training_history']
            
            logger.info(f"Loaded checkpoint from {checkpoint_path}")
            
            # Load training samples
            samples_path = self.checkpoint_dir / f"training_samples_{name}.pkl"
            if samples_path.exists():
                with open(samples_path, 'rb') as f:
                    samples = pickle.load(f)
                    self.training_samples = samples.get('training', [])
                    self.validation_samples = samples.get('validation', [])
                logger.info(f"Loaded {len(self.training_samples)} training samples")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status"""
        return {
            'total_samples': len(self.training_samples),
            'validation_samples': len(self.validation_samples),
            'epochs_trained': self.training_history['epochs'],
            'latest_loss': self.training_history['losses'][-1] if self.training_history['losses'] else None,
            'latest_accuracy': self.training_history['accuracies'][-1] if self.training_history['accuracies'] else None,
            'ready_to_train': len(self.training_samples) >= 100,
            'device': self.device
        }


# Global instance
_hrm_trainer: Optional[HRMTradingTrainer] = None


def get_hrm_trainer() -> HRMTradingTrainer:
    """Get or create global HRM trainer instance"""
    global _hrm_trainer
    
    if _hrm_trainer is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        _hrm_trainer = HRMTradingTrainer(device=device)
        
        # Try to load existing checkpoint
        _hrm_trainer.load_checkpoint('latest')
    
    return _hrm_trainer


def record_trade_outcome(
    symbol: str,
    action: str,
    market_data: Dict,
    technical_indicators: Dict,
    profit_loss: float,
    confidence: float
):
    """Record a trade outcome for HRM training"""
    trainer = get_hrm_trainer()
    return trainer.add_training_sample(
        market_data=market_data,
        technical_indicators=technical_indicators,
        action=action,
        profit_loss=profit_loss,
        confidence=confidence,
        symbol=symbol
    )


def train_hrm_on_trading(epochs: int = 10, batch_size: int = 32) -> Dict[str, Any]:
    """Train HRM on collected trading data"""
    trainer = get_hrm_trainer()
    return trainer.train(epochs=epochs, batch_size=batch_size)


if __name__ == "__main__":
    # Test the training system
    logging.basicConfig(level=logging.INFO)
    
    trainer = HRMTradingTrainer(device='cpu')
    
    # Add some test samples
    for i in range(150):
        action = ['HOLD', 'BUY', 'SELL'][i % 3]
        profit = np.random.uniform(-50, 100)
        
        trainer.add_training_sample(
            market_data={
                'price': 100 + np.random.uniform(-10, 10),
                'volume': 1000000 + np.random.uniform(-100000, 100000),
                'change_percent': np.random.uniform(-5, 5),
                'bid': 99.5,
                'ask': 100.5
            },
            technical_indicators={
                'rsi': 50 + np.random.uniform(-30, 30),
                'macd': np.random.uniform(-2, 2),
                'macd_signal': np.random.uniform(-2, 2)
            },
            action=action,
            profit_loss=profit,
            confidence=0.7,
            symbol='TEST'
        )
    
    print(f"\nTraining status: {trainer.get_training_status()}")
    
    # Train
    result = trainer.train(epochs=5, batch_size=16)
    print(f"\nTraining result: {result}")
    
    # Make prediction
    prediction = trainer.predict(
        market_data={'price': 105, 'volume': 1100000, 'change_percent': 2.5},
        technical_indicators={'rsi': 65, 'macd': 0.5}
    )
    print(f"\nPrediction: {prediction}")
