"""
PROMETHEUS Sentiment Analysis Training System
=============================================
Train models to understand financial news sentiment
and its impact on market movements
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


# Financial sentiment lexicon
FINANCIAL_LEXICON = {
    # Bullish terms
    'bullish': 2.0, 'rally': 1.5, 'surge': 1.5, 'soar': 1.8, 'boom': 1.7,
    'breakout': 1.5, 'upgrade': 1.3, 'outperform': 1.4, 'beat': 1.2,
    'growth': 1.0, 'profit': 1.0, 'gain': 1.0, 'rise': 0.8, 'up': 0.5,
    'strong': 0.8, 'robust': 0.9, 'momentum': 0.7, 'opportunity': 0.6,
    'optimistic': 1.2, 'confidence': 0.8, 'recovery': 1.0, 'expansion': 0.9,
    
    # Bearish terms
    'bearish': -2.0, 'crash': -2.0, 'plunge': -1.8, 'collapse': -1.9,
    'selloff': -1.5, 'downgrade': -1.3, 'underperform': -1.4, 'miss': -1.2,
    'loss': -1.0, 'decline': -0.8, 'drop': -0.8, 'fall': -0.7, 'down': -0.5,
    'weak': -0.8, 'concern': -0.7, 'risk': -0.6, 'warning': -0.9,
    'pessimistic': -1.2, 'fear': -1.0, 'recession': -1.5, 'contraction': -0.9,
    
    # Uncertainty terms
    'volatile': -0.3, 'uncertain': -0.4, 'mixed': 0.0, 'flat': 0.0,
    'cautious': -0.2, 'speculation': -0.2, 'rumor': -0.1,
    
    # Action terms
    'buy': 0.8, 'sell': -0.8, 'hold': 0.0, 'accumulate': 0.7, 'reduce': -0.6,
}

# News source weights (credibility)
SOURCE_WEIGHTS = {
    'reuters': 1.2, 'bloomberg': 1.2, 'wsj': 1.1, 'cnbc': 1.0,
    'marketwatch': 0.9, 'seekingalpha': 0.8, 'yahoo': 0.8,
    'benzinga': 0.7, 'motleyfool': 0.6, 'reddit': 0.4, 'twitter': 0.3
}


@dataclass
class SentimentSample:
    """Training sample for sentiment analysis"""
    text: str
    sentiment_score: float  # -1 to 1
    symbol: str
    source: str
    timestamp: str
    price_impact: Optional[float] = None  # Actual price change after news


class SentimentEncoder(nn.Module):
    """Neural network for encoding financial text sentiment"""
    
    def __init__(self, vocab_size: int = 10000, embed_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        
        self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=4, batch_first=True)
        
        self.sentiment_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Tanh()  # Output in [-1, 1]
        )
        
        self.impact_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        
        # Self-attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Global average pooling
        pooled = attn_out.mean(dim=1)
        
        return {
            'sentiment': self.sentiment_head(pooled),
            'impact': self.impact_head(pooled)
        }


class SentimentModelTraining:
    """
    Train sentiment analysis models for financial news
    Learns to predict market impact from news sentiment
    """
    
    def __init__(self, checkpoint_dir: str = 'trained_models/sentiment'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Vocabulary
        self.vocab = {'<PAD>': 0, '<UNK>': 1}
        self.vocab_size = 10000
        
        # Model
        self.model = SentimentEncoder(self.vocab_size).to(self.device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-4)
        
        # Training data
        self.training_samples: List[SentimentSample] = []
        
        # Training history
        self.training_history = {
            'losses': [],
            'sentiment_mae': [],
            'impact_mae': []
        }
        
        logger.info(f"📰 Sentiment Model Training initialized on {self.device}")
    
    def lexicon_sentiment(self, text: str) -> float:
        """Calculate sentiment using financial lexicon"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        total_score = 0
        count = 0
        
        for word in words:
            if word in FINANCIAL_LEXICON:
                total_score += FINANCIAL_LEXICON[word]
                count += 1
        
        if count == 0:
            return 0.0
        
        # Normalize to [-1, 1]
        raw_score = total_score / count
        return max(-1, min(1, raw_score / 2))
    
    def tokenize(self, text: str, max_length: int = 128) -> List[int]:
        """Tokenize text for model input"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        tokens = []
        for word in words[:max_length]:
            if word not in self.vocab and len(self.vocab) < self.vocab_size:
                self.vocab[word] = len(self.vocab)
            tokens.append(self.vocab.get(word, 1))  # 1 = <UNK>
        
        # Pad to max_length
        while len(tokens) < max_length:
            tokens.append(0)  # 0 = <PAD>
        
        return tokens[:max_length]
    
    def add_training_sample(
        self,
        text: str,
        sentiment_score: Optional[float] = None,
        symbol: str = 'GENERAL',
        source: str = 'unknown',
        price_impact: Optional[float] = None
    ):
        """Add a training sample"""
        if sentiment_score is None:
            sentiment_score = self.lexicon_sentiment(text)
        
        sample = SentimentSample(
            text=text,
            sentiment_score=sentiment_score,
            symbol=symbol,
            source=source,
            timestamp=datetime.now().isoformat(),
            price_impact=price_impact
        )
        
        self.training_samples.append(sample)
        return len(self.training_samples)
    
    def generate_training_data(self, num_samples: int = 1000):
        """Generate synthetic training data from templates"""
        
        bullish_templates = [
            "{symbol} shares surge {percent}% after strong earnings beat",
            "Analysts upgrade {symbol} citing strong growth momentum",
            "{symbol} announces record quarterly revenue, stock rallies",
            "Breaking: {symbol} secures major contract, shares soar",
            "Institutional investors accumulate {symbol} positions",
            "{symbol} beats expectations, raises full-year guidance",
            "Bull case for {symbol}: Multiple catalysts ahead",
            "{symbol} breakout confirmed as volume surges",
        ]
        
        bearish_templates = [
            "{symbol} shares plunge {percent}% on earnings miss",
            "Analysts downgrade {symbol} amid growth concerns",
            "{symbol} warns of slowdown, stock tumbles",
            "Breaking: {symbol} faces regulatory investigation",
            "Institutional investors reduce {symbol} holdings",
            "{symbol} cuts guidance, shares collapse",
            "Bear case: {symbol} faces multiple headwinds",
            "{symbol} breakdown as support levels fail",
        ]
        
        neutral_templates = [
            "{symbol} reports mixed results, shares flat",
            "Analysts maintain neutral rating on {symbol}",
            "{symbol} trading sideways amid market uncertainty",
            "Volume light as {symbol} consolidates recent gains",
        ]
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD']
        sources = list(SOURCE_WEIGHTS.keys())
        
        for _ in range(num_samples):
            symbol = np.random.choice(symbols)
            source = np.random.choice(sources)
            percent = np.random.randint(2, 15)
            
            # Choose template based on distribution
            rand = np.random.random()
            if rand < 0.4:
                template = np.random.choice(bullish_templates)
                sentiment = np.random.uniform(0.3, 1.0)
                impact = np.random.uniform(0.01, 0.08)
            elif rand < 0.8:
                template = np.random.choice(bearish_templates)
                sentiment = np.random.uniform(-1.0, -0.3)
                impact = np.random.uniform(-0.08, -0.01)
            else:
                template = np.random.choice(neutral_templates)
                sentiment = np.random.uniform(-0.2, 0.2)
                impact = np.random.uniform(-0.02, 0.02)
            
            text = template.format(symbol=symbol, percent=percent)
            
            self.add_training_sample(
                text=text,
                sentiment_score=sentiment,
                symbol=symbol,
                source=source,
                price_impact=impact
            )
        
        logger.info(f"  Generated {num_samples} training samples")
    
    def train(self, epochs: int = 10, batch_size: int = 32) -> Dict[str, Any]:
        """Train the sentiment model"""
        if len(self.training_samples) < 50:
            logger.warning("Not enough training samples")
            return {'success': False, 'error': 'insufficient_data'}
        
        logger.info(f"  Training on {len(self.training_samples)} samples...")
        
        # Prepare data
        X = []
        y_sentiment = []
        y_impact = []
        
        for sample in self.training_samples:
            tokens = self.tokenize(sample.text)
            X.append(tokens)
            y_sentiment.append(sample.sentiment_score)
            y_impact.append(sample.price_impact if sample.price_impact else 0)
        
        X = torch.tensor(X, dtype=torch.long).to(self.device)
        y_sentiment = torch.tensor(y_sentiment, dtype=torch.float32).to(self.device)
        y_impact = torch.tensor(y_impact, dtype=torch.float32).to(self.device)
        
        # Training loop
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0
            sentiment_errors = []
            impact_errors = []
            
            indices = torch.randperm(len(X))
            
            for i in range(0, len(X) - batch_size, batch_size):
                batch_idx = indices[i:i + batch_size]
                batch_X = X[batch_idx]
                batch_y_sent = y_sentiment[batch_idx]
                batch_y_imp = y_impact[batch_idx]
                
                self.optimizer.zero_grad()
                
                outputs = self.model(batch_X)
                
                sentiment_loss = nn.MSELoss()(outputs['sentiment'].squeeze(), batch_y_sent)
                impact_loss = nn.MSELoss()(outputs['impact'].squeeze(), batch_y_imp)
                
                loss = sentiment_loss + 0.5 * impact_loss
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
                
                with torch.no_grad():
                    sentiment_errors.append(
                        (outputs['sentiment'].squeeze() - batch_y_sent).abs().mean().item()
                    )
                    impact_errors.append(
                        (outputs['impact'].squeeze() - batch_y_imp).abs().mean().item()
                    )
            
            avg_loss = epoch_loss / (len(X) // batch_size)
            avg_sent_mae = np.mean(sentiment_errors)
            avg_imp_mae = np.mean(impact_errors)
            
            self.training_history['losses'].append(avg_loss)
            self.training_history['sentiment_mae'].append(avg_sent_mae)
            self.training_history['impact_mae'].append(avg_imp_mae)
            
            if (epoch + 1) % 2 == 0:
                logger.info(f"    Epoch {epoch + 1}/{epochs}: Loss={avg_loss:.4f}, "
                           f"Sentiment MAE={avg_sent_mae:.4f}, Impact MAE={avg_imp_mae:.4f}")
        
        self.save_checkpoint()
        
        return {
            'success': True,
            'final_loss': avg_loss,
            'sentiment_mae': avg_sent_mae,
            'impact_mae': avg_imp_mae,
            'samples_trained': len(self.training_samples)
        }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict sentiment and market impact from text"""
        self.model.eval()
        
        # Lexicon baseline
        lexicon_sentiment = self.lexicon_sentiment(text)
        
        # Model prediction
        with torch.no_grad():
            tokens = torch.tensor([self.tokenize(text)], dtype=torch.long).to(self.device)
            outputs = self.model(tokens)
            
            model_sentiment = outputs['sentiment'].item()
            predicted_impact = outputs['impact'].item()
        
        # Ensemble: combine lexicon and model
        final_sentiment = 0.3 * lexicon_sentiment + 0.7 * model_sentiment
        
        return {
            'sentiment': final_sentiment,
            'sentiment_label': 'bullish' if final_sentiment > 0.2 else 'bearish' if final_sentiment < -0.2 else 'neutral',
            'confidence': abs(final_sentiment),
            'predicted_impact': predicted_impact,
            'lexicon_sentiment': lexicon_sentiment,
            'model_sentiment': model_sentiment
        }
    
    def save_checkpoint(self):
        """Save model checkpoint"""
        checkpoint = {
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'vocab': self.vocab,
            'training_history': self.training_history,
            'timestamp': datetime.now().isoformat()
        }
        
        path = self.checkpoint_dir / 'sentiment_model.pt'
        torch.save(checkpoint, path)
        logger.info(f"  💾 Sentiment model saved to {path}")
    
    def load_checkpoint(self) -> bool:
        """Load model checkpoint"""
        path = self.checkpoint_dir / 'sentiment_model.pt'
        
        if path.exists():
            checkpoint = torch.load(path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state'])
            self.vocab = checkpoint['vocab']
            self.training_history = checkpoint['training_history']
            logger.info(f"  📂 Loaded sentiment model from {path}")
            return True
        return False


async def train_sentiment_model(num_samples: int = 1000) -> Dict[str, Any]:
    """Convenience function to train sentiment model"""
    trainer = SentimentModelTraining()
    trainer.generate_training_data(num_samples)
    return trainer.train()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(train_sentiment_model())
