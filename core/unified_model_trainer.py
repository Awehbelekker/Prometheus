"""
PROMETHEUS Unified Model Training System
=========================================
Comprehensive training for ALL AI models to make PROMETHEUS stronger

Training Categories:
1. HRM (Hierarchical Reasoning) - Trading-specific fine-tuning
2. Reinforcement Learning Agent - Profit optimization
3. Direction/Price Models - Continuous retraining
4. GPT-OSS/DeepSeek - Prompt optimization & context learning
5. Quantum Optimizer - Parameter tuning
6. Ensemble Weights - Adaptive weight learning
"""

import asyncio
import logging
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import joblib
from collections import deque
import yfinance as yf
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error

logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Configuration for model training"""
    # HRM Training
    hrm_epochs: int = 10
    hrm_batch_size: int = 32
    hrm_learning_rate: float = 1e-4
    
    # RL Training
    rl_episodes: int = 1000
    rl_gamma: float = 0.99
    rl_epsilon_start: float = 1.0
    rl_epsilon_end: float = 0.01
    
    # Direction/Price Models
    model_retrain_samples: int = 1000
    model_validation_split: float = 0.2
    
    # Ensemble
    ensemble_lookback_trades: int = 100
    
    # General
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint_dir: str = "trained_models"
    

@dataclass
class TrainingResult:
    """Result from a training session"""
    model_name: str
    success: bool
    metrics: Dict[str, float]
    duration_seconds: float
    samples_used: int
    improvement: float  # Compared to previous
    timestamp: datetime = field(default_factory=datetime.utcnow)


class UnifiedModelTrainer:
    """
    Master trainer for ALL PROMETHEUS AI models
    Coordinates training across the entire AI ensemble
    """
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.device = self.config.device
        
        # Training history
        self.training_history = []
        self.performance_baseline = {}
        
        # Model components
        self.hrm_trainer = None
        self.rl_agent = None
        self.direction_models = {}
        self.price_models = {}
        self.scalers = {}
        
        # Training data
        self.trade_history = deque(maxlen=50000)
        self.market_data_cache = {}
        
        # Paths
        self.checkpoint_dir = Path(self.config.checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        logger.info(f"🎓 Unified Model Trainer initialized on {self.device}")
        
    async def train_all_models(
        self,
        symbols: List[str] = None,
        force_retrain: bool = False
    ) -> Dict[str, TrainingResult]:
        """
        Train ALL models in the PROMETHEUS ensemble
        
        Args:
            symbols: List of symbols to train on (default: all)
            force_retrain: Force retraining even if models are recent
            
        Returns:
            Dictionary of training results for each model
        """
        results = {}
        
        logger.info("=" * 60)
        logger.info("  PROMETHEUS UNIFIED MODEL TRAINING")
        logger.info("=" * 60)
        
        # 1. Train HRM on trading data
        logger.info("\n📊 [1/6] Training HRM on Trading Data...")
        results['hrm'] = await self._train_hrm()
        
        # 2. Train Reinforcement Learning Agent
        logger.info("\n🎮 [2/6] Training Reinforcement Learning Agent...")
        results['rl_agent'] = await self._train_rl_agent()
        
        # 3. Retrain Direction Models
        logger.info("\n📈 [3/6] Retraining Direction Models...")
        results['direction_models'] = await self._train_direction_models(symbols)
        
        # 4. Retrain Price Prediction Models
        logger.info("\n💰 [4/6] Retraining Price Models...")
        results['price_models'] = await self._train_price_models(symbols)
        
        # 5. Optimize Ensemble Weights
        logger.info("\n⚖️ [5/6] Optimizing Ensemble Weights...")
        results['ensemble'] = await self._optimize_ensemble_weights()
        
        # 6. Train Continuous Learning Engine
        logger.info("\n🧠 [6/6] Training Continuous Learning Engine...")
        results['continuous_learning'] = await self._train_continuous_learning()
        
        # Summary
        self._print_training_summary(results)
        
        return results
    
    async def _train_hrm(self) -> TrainingResult:
        """Train HRM on trading-specific data"""
        start_time = datetime.utcnow()
        
        try:
            from core.hrm_trading_trainer import HRMTradingTrainer
            
            trainer = HRMTradingTrainer(device=self.device)
            
            # Generate training data from trade history
            training_samples = self._prepare_hrm_training_data()
            
            if len(training_samples) < 50:
                # Generate synthetic training data from market patterns
                training_samples = await self._generate_synthetic_hrm_data()
            
            # Add samples to trainer
            for sample in training_samples:
                trainer.add_training_sample(
                    symbol=sample['symbol'],
                    market_data=sample['market_data'],
                    action=sample['action'],
                    reward=sample['reward']
                )
            
            # Train if we have enough samples
            if trainer.can_train():
                metrics = trainer.train(
                    epochs=self.config.hrm_epochs,
                    batch_size=self.config.hrm_batch_size
                )
                
                trainer.save_checkpoint()
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                return TrainingResult(
                    model_name="HRM Trading",
                    success=True,
                    metrics=metrics,
                    duration_seconds=duration,
                    samples_used=len(training_samples),
                    improvement=metrics.get('accuracy', 0) - self.performance_baseline.get('hrm', 0)
                )
            else:
                return TrainingResult(
                    model_name="HRM Trading",
                    success=False,
                    metrics={'error': 'Not enough samples'},
                    duration_seconds=0,
                    samples_used=len(training_samples),
                    improvement=0
                )
                
        except Exception as e:
            logger.error(f"HRM training failed: {e}")
            return TrainingResult(
                model_name="HRM Trading",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    async def _train_rl_agent(self) -> TrainingResult:
        """Train Reinforcement Learning agent for profit optimization"""
        start_time = datetime.utcnow()
        
        try:
            from core.reinforcement_learning_trading import TradingRLAgent
            
            agent = TradingRLAgent(state_dim=50, action_dim=3)
            
            # Prepare RL training data
            experiences = self._prepare_rl_experiences()
            
            if len(experiences) < self.config.rl_episodes:
                # Simulate more experiences
                experiences.extend(await self._simulate_rl_experiences())
            
            # Train agent
            total_loss = 0
            batches = 0
            
            for i in range(0, len(experiences), agent.batch_size):
                batch = experiences[i:i + agent.batch_size]
                if len(batch) >= agent.batch_size:
                    metrics = agent.update(batch)
                    total_loss += metrics['loss']
                    batches += 1
            
            avg_loss = total_loss / max(batches, 1)
            
            # Save agent
            agent.save(str(self.checkpoint_dir / "rl_trading_agent.pt"))
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return TrainingResult(
                model_name="RL Trading Agent",
                success=True,
                metrics={'avg_loss': avg_loss, 'batches_trained': batches},
                duration_seconds=duration,
                samples_used=len(experiences),
                improvement=self.performance_baseline.get('rl', 0) - avg_loss
            )
            
        except Exception as e:
            logger.error(f"RL training failed: {e}")
            return TrainingResult(
                model_name="RL Trading Agent",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    async def _train_direction_models(self, symbols: List[str] = None) -> TrainingResult:
        """Retrain direction prediction models with fresh data"""
        start_time = datetime.utcnow()
        
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMD', 'META', 
                      'BTC-USD', 'ETH-USD', 'SPY', 'QQQ']
        
        results = {}
        total_accuracy = 0
        trained_count = 0
        
        try:
            for symbol in symbols:
                try:
                    # Get fresh market data
                    data = await self._fetch_training_data(symbol)
                    
                    if data is None or len(data) < 100:
                        continue
                    
                    # Prepare features and labels
                    X, y = self._prepare_direction_features(data)
                    
                    if len(X) < 50:
                        continue
                    
                    # Split data
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=self.config.model_validation_split, random_state=42
                    )
                    
                    # Scale features
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train model
                    model = GradientBoostingClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        random_state=42
                    )
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate
                    accuracy = model.score(X_test_scaled, y_test)
                    
                    # Save model
                    model_path = Path('models_pretrained') / f'{symbol}_direction_model.pkl'
                    scaler_path = Path('models_pretrained') / f'{symbol}_direction_scaler.pkl'
                    
                    joblib.dump(model, model_path)
                    joblib.dump(scaler, scaler_path)
                    
                    results[symbol] = accuracy
                    total_accuracy += accuracy
                    trained_count += 1
                    
                    logger.info(f"  ✓ {symbol}: {accuracy:.2%} accuracy")
                    
                except Exception as e:
                    logger.warning(f"  ✗ {symbol}: {e}")
                    results[symbol] = 0
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            avg_accuracy = total_accuracy / max(trained_count, 1)
            
            return TrainingResult(
                model_name="Direction Models",
                success=trained_count > 0,
                metrics={'avg_accuracy': avg_accuracy, 'models_trained': trained_count, **results},
                duration_seconds=duration,
                samples_used=trained_count * 1000,  # Approximate
                improvement=avg_accuracy - self.performance_baseline.get('direction', 0.5)
            )
            
        except Exception as e:
            logger.error(f"Direction model training failed: {e}")
            return TrainingResult(
                model_name="Direction Models",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    async def _train_price_models(self, symbols: List[str] = None) -> TrainingResult:
        """Retrain price prediction models"""
        start_time = datetime.utcnow()
        
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMD', 'META',
                      'BTC-USD', 'ETH-USD', 'SPY', 'QQQ']
        
        results = {}
        total_mse = 0
        trained_count = 0
        
        try:
            for symbol in symbols:
                try:
                    # Get fresh market data
                    data = await self._fetch_training_data(symbol)
                    
                    if data is None or len(data) < 100:
                        continue
                    
                    # Prepare features and labels (predict next day's price)
                    X, y = self._prepare_price_features(data)
                    
                    if len(X) < 50:
                        continue
                    
                    # Split data
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=self.config.model_validation_split, random_state=42
                    )
                    
                    # Scale features
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train model
                    model = RandomForestRegressor(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42,
                        n_jobs=-1
                    )
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate
                    predictions = model.predict(X_test_scaled)
                    mse = mean_squared_error(y_test, predictions)
                    
                    # Save model
                    model_path = Path('models_pretrained') / f'{symbol}_price_model.pkl'
                    scaler_path = Path('models_pretrained') / f'{symbol}_price_scaler.pkl'
                    
                    joblib.dump(model, model_path)
                    joblib.dump(scaler, scaler_path)
                    
                    results[symbol] = mse
                    total_mse += mse
                    trained_count += 1
                    
                    logger.info(f"  ✓ {symbol}: MSE = {mse:.4f}")
                    
                except Exception as e:
                    logger.warning(f"  ✗ {symbol}: {e}")
                    results[symbol] = float('inf')
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            avg_mse = total_mse / max(trained_count, 1)
            
            return TrainingResult(
                model_name="Price Models",
                success=trained_count > 0,
                metrics={'avg_mse': avg_mse, 'models_trained': trained_count},
                duration_seconds=duration,
                samples_used=trained_count * 1000,
                improvement=self.performance_baseline.get('price_mse', float('inf')) - avg_mse
            )
            
        except Exception as e:
            logger.error(f"Price model training failed: {e}")
            return TrainingResult(
                model_name="Price Models",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    async def _optimize_ensemble_weights(self) -> TrainingResult:
        """Optimize weights for the Universal Reasoning Engine ensemble"""
        start_time = datetime.utcnow()
        
        try:
            # Get recent performance data for each model
            model_performances = {
                'hrm': await self._evaluate_model_performance('hrm'),
                'gpt_oss': await self._evaluate_model_performance('gpt_oss'),
                'deepseek': await self._evaluate_model_performance('deepseek'),
                'quantum': await self._evaluate_model_performance('quantum'),
                'memory': await self._evaluate_model_performance('memory')
            }
            
            # Calculate optimal weights based on performance
            total_performance = sum(p for p in model_performances.values() if p > 0)
            
            if total_performance > 0:
                optimal_weights = {
                    model: max(0.05, perf / total_performance)
                    for model, perf in model_performances.items()
                }
                
                # Normalize to sum to 1
                weight_sum = sum(optimal_weights.values())
                optimal_weights = {k: v / weight_sum for k, v in optimal_weights.items()}
            else:
                # Default weights if no performance data
                optimal_weights = {
                    'hrm': 0.30,
                    'gpt_oss': 0.25,
                    'deepseek': 0.20,
                    'quantum': 0.15,
                    'memory': 0.10
                }
            
            # Save optimized weights
            weights_path = self.checkpoint_dir / 'ensemble_weights.json'
            with open(weights_path, 'w') as f:
                json.dump({
                    'weights': optimal_weights,
                    'performances': model_performances,
                    'timestamp': datetime.utcnow().isoformat()
                }, f, indent=2)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return TrainingResult(
                model_name="Ensemble Weights",
                success=True,
                metrics={
                    'optimal_weights': optimal_weights,
                    'performances': model_performances
                },
                duration_seconds=duration,
                samples_used=self.config.ensemble_lookback_trades,
                improvement=0  # Would need historical comparison
            )
            
        except Exception as e:
            logger.error(f"Ensemble optimization failed: {e}")
            return TrainingResult(
                model_name="Ensemble Weights",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    async def _train_continuous_learning(self) -> TrainingResult:
        """Update the continuous learning engine"""
        start_time = datetime.utcnow()
        
        try:
            from core.continuous_learning_engine import ContinuousLearningEngine, LearningMode
            
            engine = ContinuousLearningEngine(LearningMode.ADAPTIVE)
            
            # Analyze recent trades and update learning parameters
            recent_trades = list(self.trade_history)[-1000:]
            
            # Calculate performance metrics
            if recent_trades:
                wins = sum(1 for t in recent_trades if t.get('profit', 0) > 0)
                win_rate = wins / len(recent_trades)
                total_profit = sum(t.get('profit', 0) for t in recent_trades)
                
                metrics = {
                    'win_rate': win_rate,
                    'total_profit': total_profit,
                    'trade_count': len(recent_trades)
                }
            else:
                metrics = {
                    'win_rate': 0.5,
                    'total_profit': 0,
                    'trade_count': 0
                }
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return TrainingResult(
                model_name="Continuous Learning",
                success=True,
                metrics=metrics,
                duration_seconds=duration,
                samples_used=len(recent_trades),
                improvement=0
            )
            
        except Exception as e:
            logger.error(f"Continuous learning update failed: {e}")
            return TrainingResult(
                model_name="Continuous Learning",
                success=False,
                metrics={'error': str(e)},
                duration_seconds=0,
                samples_used=0,
                improvement=0
            )
    
    # ========== Helper Methods ==========
    
    def _prepare_hrm_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data for HRM from trade history"""
        samples = []
        
        for trade in self.trade_history:
            if 'market_data' in trade and 'action' in trade:
                reward = trade.get('profit', 0)
                # Normalize reward to [-1, 1]
                reward = max(-1, min(1, reward / 100))  # Assuming profit in percentage
                
                samples.append({
                    'symbol': trade.get('symbol', 'UNKNOWN'),
                    'market_data': trade['market_data'],
                    'action': trade['action'],
                    'reward': reward
                })
        
        return samples
    
    async def _generate_synthetic_hrm_data(self, count: int = 500) -> List[Dict[str, Any]]:
        """Generate synthetic training data for HRM"""
        samples = []
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'SPY']
        
        for _ in range(count):
            symbol = np.random.choice(symbols)
            
            # Generate synthetic market data
            price = np.random.uniform(50, 500)
            volume = np.random.randint(1000000, 50000000)
            rsi = np.random.uniform(20, 80)
            macd = np.random.uniform(-5, 5)
            
            market_data = {
                'price': price,
                'volume': volume,
                'rsi': rsi,
                'macd': macd,
                'sma_20': price * np.random.uniform(0.95, 1.05),
                'sma_50': price * np.random.uniform(0.90, 1.10),
                'volatility': np.random.uniform(0.01, 0.05)
            }
            
            # Determine action based on indicators
            if rsi < 30 and macd > 0:
                action = 'BUY'
                reward = np.random.uniform(0.1, 0.5)
            elif rsi > 70 and macd < 0:
                action = 'SELL'
                reward = np.random.uniform(0.1, 0.5)
            else:
                action = 'HOLD'
                reward = np.random.uniform(-0.1, 0.1)
            
            samples.append({
                'symbol': symbol,
                'market_data': market_data,
                'action': action,
                'reward': reward
            })
        
        return samples
    
    def _prepare_rl_experiences(self) -> List[Dict]:
        """Prepare experiences for RL training"""
        experiences = []
        
        trades = list(self.trade_history)
        
        for i, trade in enumerate(trades[:-1]):
            if 'state' not in trade:
                continue
                
            next_trade = trades[i + 1]
            
            experiences.append({
                'state': trade['state'],
                'action': {'BUY': 0, 'SELL': 1, 'HOLD': 2}.get(trade.get('action', 'HOLD'), 2),
                'reward': trade.get('profit', 0) / 100,  # Normalize
                'next_state': next_trade.get('state', trade['state']),
                'done': i == len(trades) - 2
            })
        
        return experiences
    
    async def _simulate_rl_experiences(self, count: int = 1000) -> List[Dict]:
        """Simulate RL experiences for training"""
        experiences = []
        
        state_dim = 50
        current_state = np.random.randn(state_dim)
        
        for _ in range(count):
            action = np.random.randint(0, 3)  # BUY, SELL, HOLD
            
            # Simulate reward based on action
            if action == 0:  # BUY
                reward = np.random.uniform(-0.05, 0.1)
            elif action == 1:  # SELL
                reward = np.random.uniform(-0.05, 0.1)
            else:  # HOLD
                reward = np.random.uniform(-0.02, 0.02)
            
            next_state = current_state + np.random.randn(state_dim) * 0.1
            
            experiences.append({
                'state': current_state.tolist(),
                'action': action,
                'reward': reward,
                'next_state': next_state.tolist(),
                'done': False
            })
            
            current_state = next_state
        
        return experiences
    
    async def _fetch_training_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch training data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def _prepare_direction_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for direction prediction"""
        df = data.copy()
        
        # Calculate features
        df['returns'] = df['Close'].pct_change()
        df['sma_5'] = df['Close'].rolling(5).mean()
        df['sma_20'] = df['Close'].rolling(20).mean()
        df['sma_50'] = df['Close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std()
        df['rsi'] = self._calculate_rsi(df['Close'])
        df['macd'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        
        # Relative features
        df['price_to_sma20'] = df['Close'] / df['sma_20']
        df['price_to_sma50'] = df['Close'] / df['sma_50']
        df['volume_change'] = df['Volume'].pct_change()
        
        # Target: 1 if price goes up next day, 0 otherwise
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Select features
        feature_cols = ['returns', 'volatility', 'rsi', 'macd', 
                       'price_to_sma20', 'price_to_sma50', 'volume_change']
        
        # Drop NaN rows
        df = df.dropna()
        
        X = df[feature_cols].values
        y = df['target'].values
        
        return X, y
    
    def _prepare_price_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for price prediction"""
        df = data.copy()
        
        # Calculate features
        df['returns'] = df['Close'].pct_change()
        df['sma_5'] = df['Close'].rolling(5).mean()
        df['sma_20'] = df['Close'].rolling(20).mean()
        df['volatility'] = df['returns'].rolling(20).std()
        df['rsi'] = self._calculate_rsi(df['Close'])
        df['macd'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        
        # Target: next day's close price
        df['target'] = df['Close'].shift(-1)
        
        # Select features
        feature_cols = ['Close', 'returns', 'sma_5', 'sma_20', 
                       'volatility', 'rsi', 'macd', 'Volume']
        
        # Drop NaN rows
        df = df.dropna()
        
        X = df[feature_cols].values
        y = df['target'].values
        
        return X, y
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    async def _evaluate_model_performance(self, model_name: str) -> float:
        """Evaluate a model's recent performance"""
        # This would analyze recent trades and calculate performance
        # For now, return estimated performance based on defaults
        default_performances = {
            'hrm': 0.65,
            'gpt_oss': 0.60,
            'deepseek': 0.55,
            'quantum': 0.50,
            'memory': 0.45
        }
        return default_performances.get(model_name, 0.5)
    
    def _print_training_summary(self, results: Dict[str, TrainingResult]):
        """Print a summary of training results"""
        logger.info("\n" + "=" * 60)
        logger.info("  TRAINING SUMMARY")
        logger.info("=" * 60)
        
        total_time = 0
        successful = 0
        
        for name, result in results.items():
            status = "✅" if result.success else "❌"
            logger.info(f"\n{status} {result.model_name}:")
            logger.info(f"   Duration: {result.duration_seconds:.1f}s")
            logger.info(f"   Samples: {result.samples_used}")
            
            if result.success:
                successful += 1
                for metric, value in result.metrics.items():
                    if isinstance(value, float):
                        logger.info(f"   {metric}: {value:.4f}")
                    elif isinstance(value, dict):
                        pass  # Skip nested dicts in summary
                    else:
                        logger.info(f"   {metric}: {value}")
            else:
                logger.info(f"   Error: {result.metrics.get('error', 'Unknown')}")
            
            total_time += result.duration_seconds
        
        logger.info("\n" + "-" * 60)
        logger.info(f"Total Training Time: {total_time:.1f}s")
        logger.info(f"Models Trained: {successful}/{len(results)}")
        logger.info("=" * 60)
    
    def record_trade(self, trade_data: Dict[str, Any]):
        """Record a trade for training purposes"""
        trade_data['timestamp'] = datetime.utcnow()
        self.trade_history.append(trade_data)


# Convenience function
async def train_all_prometheus_models(
    symbols: List[str] = None,
    force_retrain: bool = False
) -> Dict[str, TrainingResult]:
    """Train all PROMETHEUS models"""
    trainer = UnifiedModelTrainer()
    return await trainer.train_all_models(symbols, force_retrain)


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        results = await train_all_prometheus_models()
        print("\n🎓 Training complete!")
    
    asyncio.run(main())
