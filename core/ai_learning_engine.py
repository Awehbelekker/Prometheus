#!/usr/bin/env python3
"""
Background AI Learning Engine
Continuous learning system that processes market data and user patterns
to improve trading recommendations and strategies
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
import threading
import time
# from core.persistence_manager import get_persistence_manager  # Temporarily disabled

logger = logging.getLogger(__name__)

@dataclass
class MarketPattern:
    """Detected market pattern"""
    pattern_id: str
    pattern_type: str  # 'trend', 'reversal', 'breakout', 'consolidation'
    symbol: str
    confidence: float
    timeframe: str
    detected_at: datetime
    features: Dict[str, float]
    prediction: Dict[str, Any]

@dataclass
class UserBehaviorPattern:
    """User trading behavior pattern"""
    user_id: str
    pattern_type: str  # 'risk_preference', 'timing', 'sector_bias', 'strategy_success'
    confidence: float
    features: Dict[str, Any]
    recommendations: List[str]
    last_updated: datetime

@dataclass
class AIRecommendation:
    """AI-generated trading recommendation"""
    recommendation_id: str
    user_id: str
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float
    reasoning: str
    target_price: Optional[float]
    stop_loss: Optional[float]
    risk_score: float
    created_at: datetime
    expires_at: datetime

class AILearningEngine:
    """
    Advanced AI learning engine that continuously processes market data
    and user behavior to improve trading recommendations
    """
    
    def __init__(self):
        # self.persistence = get_persistence_manager()  # Temporarily disabled
        self.persistence = None  # Mock for now
        self.models = {}
        self.scalers = {}
        self.market_patterns = {}
        self.user_patterns = {}
        self.recommendations = {}
        self.is_learning = False
        self.learning_tasks = set()

        # Model paths
        self.model_dir = Path("ai_models")
        self.model_dir.mkdir(exist_ok=True)

        # Initialize models
        self._initialize_models()

        # Load existing patterns (disabled for now)
        # self._load_existing_patterns()
    
    def _initialize_models(self):
        """Initialize AI models for different tasks"""
        try:
            # Price prediction model
            self.models['price_predictor'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Market direction classifier
            self.models['direction_classifier'] = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Risk assessment model
            self.models['risk_assessor'] = RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            
            # User behavior classifier
            self.models['behavior_classifier'] = GradientBoostingClassifier(
                n_estimators=50,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            
            # Initialize scalers
            for model_name in self.models.keys():
                self.scalers[model_name] = StandardScaler()
            
            # Try to load pre-trained models
            self._load_trained_models()
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    def _load_trained_models(self):
        """Load pre-trained models if they exist"""
        try:
            for model_name in self.models.keys():
                model_path = self.model_dir / f"{model_name}.joblib"
                scaler_path = self.model_dir / f"{model_name}_scaler.joblib"
                
                if model_path.exists() and scaler_path.exists():
                    self.models[model_name] = joblib.load(model_path)
                    self.scalers[model_name] = joblib.load(scaler_path)
                    logger.info(f"Loaded pre-trained model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load pre-trained models: {e}")
    
    def _save_trained_models(self):
        """Save trained models to disk"""
        try:
            for model_name, model in self.models.items():
                if hasattr(model, 'feature_importances_') or hasattr(model, 'coef_'):
                    model_path = self.model_dir / f"{model_name}.joblib"
                    scaler_path = self.model_dir / f"{model_name}_scaler.joblib"
                    
                    joblib.dump(model, model_path)
                    joblib.dump(self.scalers[model_name], scaler_path)
                    logger.info(f"Saved trained model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to save trained models: {e}")
    
    def _load_existing_patterns(self):
        """Load existing patterns from database"""
        try:
            if not self.persistence:
                logger.info("Persistence manager not available, skipping pattern loading")
                return

            # Load market patterns
            market_patterns_data = self.persistence.load_system_state('market_patterns')
            if market_patterns_data:
                for pattern_data in market_patterns_data:
                    pattern = MarketPattern(**pattern_data)
                    self.market_patterns[pattern.pattern_id] = pattern

            # Load user patterns
            user_patterns_data = self.persistence.load_system_state('user_patterns')
            if user_patterns_data:
                for pattern_data in user_patterns_data:
                    pattern = UserBehaviorPattern(**pattern_data)
                    self.user_patterns[f"{pattern.user_id}_{pattern.pattern_type}"] = pattern

            logger.info(f"Loaded {len(self.market_patterns)} market patterns and {len(self.user_patterns)} user patterns")

        except Exception as e:
            logger.error(f"Failed to load existing patterns: {e}")
    
    async def start_learning(self):
        """Start the background AI learning process"""
        if self.is_learning:
            logger.warning("AI learning is already running")
            return
        
        self.is_learning = True
        logger.info("Starting AI learning engine...")
        
        # Start learning tasks
        tasks = [
            self._market_data_processor(),
            self._user_behavior_analyzer(),
            self._pattern_detector(),
            self._recommendation_generator(),
            self._model_trainer()
        ]
        
        for task_coro in tasks:
            task = asyncio.create_task(task_coro)
            self.learning_tasks.add(task)
            task.add_done_callback(self.learning_tasks.discard)
        
        logger.info("AI learning engine started successfully")
    
    async def stop_learning(self):
        """Stop the AI learning process"""
        logger.info("Stopping AI learning engine...")
        self.is_learning = False
        
        # Cancel all learning tasks
        for task in self.learning_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.learning_tasks:
            await asyncio.gather(*self.learning_tasks, return_exceptions=True)
        
        # Save models and patterns
        self._save_trained_models()
        await self._save_patterns()
        
        logger.info("AI learning engine stopped")
    
    async def _market_data_processor(self):
        """Process market data for pattern recognition"""
        logger.info("Starting market data processor...")
        
        while self.is_learning:
            try:
                # Get symbols from active trades (mock for now)
                symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'SPY']  # Default symbols
                if self.persistence:
                    try:
                        active_trades = self.persistence.load_user_trades("", status='active')
                        symbols = list(set(trade['symbol'] for trade in active_trades)) or symbols
                    except Exception:
                        pass  # Use default symbols

                for symbol in symbols:
                    await self._analyze_symbol_data(symbol)

                await asyncio.sleep(300)  # Process every 5 minutes

            except Exception as e:
                logger.error(f"Market data processor error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_symbol_data(self, symbol: str):
        """Analyze market data for a specific symbol"""
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d", interval="1h")
            
            if data.empty:
                return
            
            # Calculate technical indicators
            features = self._calculate_technical_indicators(data)
            
            # Detect patterns
            patterns = self._detect_market_patterns(symbol, features, data)
            
            # Store patterns
            for pattern in patterns:
                self.market_patterns[pattern.pattern_id] = pattern
                
                # Record learning event (if persistence available)
                if self.persistence:
                    try:
                        self.persistence.record_ai_learning_event(
                            user_id="system",
                            event_type="market_pattern_detected",
                            event_data=asdict(pattern),
                            confidence=pattern.confidence
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record learning event: {e}")
            
        except Exception as e:
            logger.error(f"Failed to analyze symbol data for {symbol}: {e}")
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators from price data"""
        try:
            features = {}
            
            # Price-based indicators
            features['sma_20'] = data['Close'].rolling(20).mean().iloc[-1]
            features['sma_50'] = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else features['sma_20']
            features['ema_12'] = data['Close'].ewm(span=12).mean().iloc[-1]
            features['ema_26'] = data['Close'].ewm(span=26).mean().iloc[-1]
            
            # Momentum indicators
            features['rsi'] = self._calculate_rsi(data['Close'])
            features['macd'] = features['ema_12'] - features['ema_26']
            
            # Volatility indicators
            features['volatility'] = data['Close'].pct_change().std() * np.sqrt(252)
            features['atr'] = self._calculate_atr(data)
            
            # Volume indicators
            features['volume_sma'] = data['Volume'].rolling(20).mean().iloc[-1]
            features['volume_ratio'] = data['Volume'].iloc[-1] / features['volume_sma']
            
            # Price position
            features['price_position'] = (data['Close'].iloc[-1] - data['Low'].rolling(20).min().iloc[-1]) / \
                                       (data['High'].rolling(20).max().iloc[-1] - data['Low'].rolling(20).min().iloc[-1])
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to calculate technical indicators: {e}")
            return {}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0  # Neutral RSI
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(period).mean()
            return atr.iloc[-1]
        except:
            return 0.0
    
    def _detect_market_patterns(self, symbol: str, features: Dict[str, float], data: pd.DataFrame) -> List[MarketPattern]:
        """Detect market patterns from technical indicators"""
        patterns = []
        
        try:
            current_price = data['Close'].iloc[-1]
            
            # Trend detection
            if features['sma_20'] > features['sma_50'] and features['rsi'] > 50:
                pattern = MarketPattern(
                    pattern_id=f"{symbol}_uptrend_{int(time.time())}",
                    pattern_type="uptrend",
                    symbol=symbol,
                    confidence=min(0.9, (features['rsi'] - 50) / 50 + 0.5),
                    timeframe="1h",
                    detected_at=datetime.now(),
                    features=features,
                    prediction={
                        "direction": "up",
                        "target_price": current_price * 1.05,
                        "probability": 0.7
                    }
                )
                patterns.append(pattern)
            
            elif features['sma_20'] < features['sma_50'] and features['rsi'] < 50:
                pattern = MarketPattern(
                    pattern_id=f"{symbol}_downtrend_{int(time.time())}",
                    pattern_type="downtrend",
                    symbol=symbol,
                    confidence=min(0.9, (50 - features['rsi']) / 50 + 0.5),
                    timeframe="1h",
                    detected_at=datetime.now(),
                    features=features,
                    prediction={
                        "direction": "down",
                        "target_price": current_price * 0.95,
                        "probability": 0.7
                    }
                )
                patterns.append(pattern)
            
            # Breakout detection
            if features['volume_ratio'] > 2.0 and features['price_position'] > 0.8:
                pattern = MarketPattern(
                    pattern_id=f"{symbol}_breakout_{int(time.time())}",
                    pattern_type="breakout",
                    symbol=symbol,
                    confidence=min(0.9, features['volume_ratio'] / 3.0),
                    timeframe="1h",
                    detected_at=datetime.now(),
                    features=features,
                    prediction={
                        "direction": "up",
                        "target_price": current_price * 1.08,
                        "probability": 0.8
                    }
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect market patterns: {e}")
            return []
    
    async def _user_behavior_analyzer(self):
        """Analyze user trading behavior patterns"""
        logger.info("Starting user behavior analyzer...")
        
        while self.is_learning:
            try:
                # Get recent learning events (if persistence available)
                events = []
                if self.persistence:
                    try:
                        events = self.persistence.get_unprocessed_learning_events(limit=100)
                    except Exception as e:
                        logger.warning(f"Failed to get learning events: {e}")

                if events:
                    await self._process_user_behavior_events(events)

                    # Mark events as processed
                    if self.persistence:
                        try:
                            event_ids = [event['id'] for event in events]
                            self.persistence.mark_learning_events_processed(event_ids)
                        except Exception as e:
                            logger.warning(f"Failed to mark events as processed: {e}")

                await asyncio.sleep(600)  # Process every 10 minutes

            except Exception as e:
                logger.error(f"User behavior analyzer error: {e}")
                await asyncio.sleep(600)
    
    async def _process_user_behavior_events(self, events: List[Dict[str, Any]]):
        """Process user behavior events to identify patterns"""
        try:
            # Group events by user
            user_events = {}
            for event in events:
                user_id = event['user_id']
                if user_id not in user_events:
                    user_events[user_id] = []
                user_events[user_id].append(event)
            
            # Analyze each user's behavior
            for user_id, user_event_list in user_events.items():
                await self._analyze_user_patterns(user_id, user_event_list)
            
        except Exception as e:
            logger.error(f"Failed to process user behavior events: {e}")
    
    async def _analyze_user_patterns(self, user_id: str, events: List[Dict[str, Any]]):
        """Analyze patterns for a specific user"""
        try:
            # Analyze risk preference
            risk_pattern = self._analyze_risk_preference(user_id, events)
            if risk_pattern:
                self.user_patterns[f"{user_id}_risk"] = risk_pattern
            
            # Analyze timing patterns
            timing_pattern = self._analyze_timing_patterns(user_id, events)
            if timing_pattern:
                self.user_patterns[f"{user_id}_timing"] = timing_pattern
            
            # Analyze strategy success
            strategy_pattern = self._analyze_strategy_success(user_id, events)
            if strategy_pattern:
                self.user_patterns[f"{user_id}_strategy"] = strategy_pattern
            
        except Exception as e:
            logger.error(f"Failed to analyze user patterns for {user_id}: {e}")
    
    def _analyze_risk_preference(self, user_id: str, events: List[Dict[str, Any]]) -> Optional[UserBehaviorPattern]:
        """Analyze user's risk preference pattern"""
        try:
            trade_events = [e for e in events if e['event_type'] == 'trade_completion']
            
            if len(trade_events) < 3:
                return None
            
            # Calculate risk metrics
            pnls = [e['event_data']['pnl'] for e in trade_events]
            avg_pnl = np.mean(pnls)
            volatility = np.std(pnls)
            
            # Determine risk preference
            if volatility > np.abs(avg_pnl) * 2:
                risk_level = "high"
                recommendations = ["Consider position sizing", "Use stop losses"]
            elif volatility < np.abs(avg_pnl) * 0.5:
                risk_level = "low"
                recommendations = ["Consider higher reward trades", "Diversify strategies"]
            else:
                risk_level = "moderate"
                recommendations = ["Maintain current risk level", "Monitor performance"]
            
            return UserBehaviorPattern(
                user_id=user_id,
                pattern_type="risk_preference",
                confidence=0.8,
                features={
                    "risk_level": risk_level,
                    "avg_pnl": avg_pnl,
                    "volatility": volatility,
                    "trade_count": len(trade_events)
                },
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze risk preference: {e}")
            return None
    
    def _analyze_timing_patterns(self, user_id: str, events: List[Dict[str, Any]]) -> Optional[UserBehaviorPattern]:
        """Analyze user's timing patterns"""
        try:
            trade_events = [e for e in events if e['event_type'] == 'trade_completion']
            
            if len(trade_events) < 5:
                return None
            
            # Analyze trade durations
            durations = []
            for event in trade_events:
                duration = event['event_data'].get('duration', 0)
                durations.append(duration)
            
            avg_duration = np.mean(durations)
            
            # Categorize timing preference
            if avg_duration < 3600:  # Less than 1 hour
                timing_style = "scalping"
                recommendations = ["Focus on high-frequency strategies", "Monitor spreads closely"]
            elif avg_duration < 86400:  # Less than 1 day
                timing_style = "day_trading"
                recommendations = ["Use intraday indicators", "Avoid overnight risk"]
            else:
                timing_style = "swing_trading"
                recommendations = ["Focus on trend following", "Use wider stop losses"]
            
            return UserBehaviorPattern(
                user_id=user_id,
                pattern_type="timing",
                confidence=0.7,
                features={
                    "timing_style": timing_style,
                    "avg_duration": avg_duration,
                    "trade_count": len(trade_events)
                },
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze timing patterns: {e}")
            return None
    
    def _analyze_strategy_success(self, user_id: str, events: List[Dict[str, Any]]) -> Optional[UserBehaviorPattern]:
        """Analyze which strategies work best for the user"""
        try:
            trade_events = [e for e in events if e['event_type'] == 'trade_completion']
            
            if len(trade_events) < 5:
                return None
            
            # Group by strategy
            strategy_performance = {}
            for event in trade_events:
                strategy = event['event_data'].get('strategy', 'manual')
                pnl = event['event_data']['pnl']
                
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = []
                strategy_performance[strategy].append(pnl)
            
            # Find best performing strategy
            best_strategy = None
            best_avg_pnl = float('-inf')
            
            for strategy, pnls in strategy_performance.items():
                if len(pnls) >= 3:  # Need at least 3 trades
                    avg_pnl = np.mean(pnls)
                    if avg_pnl > best_avg_pnl:
                        best_avg_pnl = avg_pnl
                        best_strategy = strategy
            
            if best_strategy:
                recommendations = [f"Focus on {best_strategy} strategy", "Avoid underperforming strategies"]
            else:
                recommendations = ["Try different strategies", "Track strategy performance"]
            
            return UserBehaviorPattern(
                user_id=user_id,
                pattern_type="strategy_success",
                confidence=0.8,
                features={
                    "best_strategy": best_strategy,
                    "best_avg_pnl": best_avg_pnl,
                    "strategy_performance": strategy_performance
                },
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze strategy success: {e}")
            return None

    async def _pattern_detector(self):
        """Detect complex patterns across market and user data"""
        logger.info("Starting pattern detector...")

        while self.is_learning:
            try:
                # Correlate market patterns with user behavior
                await self._correlate_patterns()

                # Generate insights
                await self._generate_insights()

                await asyncio.sleep(900)  # Process every 15 minutes

            except Exception as e:
                logger.error(f"Pattern detector error: {e}")
                await asyncio.sleep(900)

    async def _correlate_patterns(self):
        """Correlate market patterns with user behavior patterns"""
        try:
            # Find correlations between market conditions and user success
            for user_pattern in self.user_patterns.values():
                if user_pattern.pattern_type == "strategy_success":
                    # Find market patterns during successful trades
                    best_strategy = user_pattern.features.get('best_strategy')
                    if best_strategy:
                        # Record correlation for future recommendations
                        correlation_data = {
                            'user_id': user_pattern.user_id,
                            'strategy': best_strategy,
                            'market_conditions': self._get_current_market_conditions()
                        }

                        self.persistence.record_ai_learning_event(
                            user_id=user_pattern.user_id,
                            event_type="pattern_correlation",
                            event_data=correlation_data,
                            confidence=0.6
                        )

        except Exception as e:
            logger.error(f"Failed to correlate patterns: {e}")

    def _get_current_market_conditions(self) -> Dict[str, Any]:
        """Get current market conditions summary"""
        try:
            conditions = {
                'trend_patterns': len([p for p in self.market_patterns.values() if 'trend' in p.pattern_type]),
                'breakout_patterns': len([p for p in self.market_patterns.values() if p.pattern_type == 'breakout']),
                'volatility_level': 'moderate',  # Would calculate from actual data
                'market_sentiment': 'neutral'    # Would derive from patterns
            }
            return conditions
        except:
            return {}

    async def _generate_insights(self):
        """Generate actionable insights from patterns"""
        try:
            insights = []

            # Market insights
            uptrend_count = len([p for p in self.market_patterns.values() if p.pattern_type == 'uptrend'])
            downtrend_count = len([p for p in self.market_patterns.values() if p.pattern_type == 'downtrend'])

            if uptrend_count > downtrend_count * 2:
                insights.append({
                    'type': 'market_insight',
                    'message': 'Strong bullish sentiment detected across multiple symbols',
                    'confidence': 0.8,
                    'actionable': True
                })

            # User insights
            for user_pattern in self.user_patterns.values():
                if user_pattern.pattern_type == 'risk_preference':
                    risk_level = user_pattern.features.get('risk_level')
                    if risk_level == 'high':
                        insights.append({
                            'type': 'user_insight',
                            'user_id': user_pattern.user_id,
                            'message': 'High risk trading detected - consider position sizing',
                            'confidence': user_pattern.confidence,
                            'actionable': True
                        })

            # Store insights
            for insight in insights:
                self.persistence.record_ai_learning_event(
                    user_id=insight.get('user_id', 'system'),
                    event_type='ai_insight',
                    event_data=insight,
                    confidence=insight['confidence']
                )

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")

    async def _recommendation_generator(self):
        """Generate AI-powered trading recommendations"""
        logger.info("Starting recommendation generator...")

        while self.is_learning:
            try:
                # Generate recommendations for active users
                active_users = self._get_active_users()

                for user_id in active_users:
                    recommendations = await self._generate_user_recommendations(user_id)

                    for rec in recommendations:
                        self.recommendations[rec.recommendation_id] = rec

                await asyncio.sleep(1800)  # Generate every 30 minutes

            except Exception as e:
                logger.error(f"Recommendation generator error: {e}")
                await asyncio.sleep(1800)

    def _get_active_users(self) -> List[str]:
        """Get list of active users"""
        try:
            # Get users with recent activity
            recent_events = self.persistence.get_unprocessed_learning_events(limit=50)
            active_users = list(set(event['user_id'] for event in recent_events if event['user_id'] != 'system'))
            return active_users
        except:
            return []

    async def _generate_user_recommendations(self, user_id: str) -> List[AIRecommendation]:
        """Generate personalized recommendations for a user"""
        try:
            recommendations = []

            # Get user patterns
            user_risk_pattern = self.user_patterns.get(f"{user_id}_risk")
            user_strategy_pattern = self.user_patterns.get(f"{user_id}_strategy")

            # Get relevant market patterns
            strong_patterns = [p for p in self.market_patterns.values() if p.confidence > 0.7]

            for pattern in strong_patterns[:3]:  # Top 3 patterns
                # Generate recommendation based on pattern and user profile
                rec = self._create_recommendation(user_id, pattern, user_risk_pattern, user_strategy_pattern)
                if rec:
                    recommendations.append(rec)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations for user {user_id}: {e}")
            return []

    def _create_recommendation(self, user_id: str, market_pattern: MarketPattern,
                             risk_pattern: Optional[UserBehaviorPattern],
                             strategy_pattern: Optional[UserBehaviorPattern]) -> Optional[AIRecommendation]:
        """Create a specific recommendation"""
        try:
            # Determine action based on pattern
            if market_pattern.pattern_type in ['uptrend', 'breakout']:
                action = 'buy'
            elif market_pattern.pattern_type == 'downtrend':
                action = 'sell'
            else:
                action = 'hold'

            # Adjust for user risk preference
            risk_multiplier = 1.0
            if risk_pattern:
                risk_level = risk_pattern.features.get('risk_level', 'moderate')
                if risk_level == 'high':
                    risk_multiplier = 1.5
                elif risk_level == 'low':
                    risk_multiplier = 0.5

            # Calculate target and stop loss
            current_price = market_pattern.features.get('sma_20', 100)
            target_price = market_pattern.prediction.get('target_price')

            if action == 'buy':
                stop_loss = current_price * (1 - 0.05 * risk_multiplier)
            else:
                stop_loss = current_price * (1 + 0.05 * risk_multiplier)

            # Create recommendation
            rec_id = f"rec_{user_id}_{market_pattern.symbol}_{int(time.time())}"

            recommendation = AIRecommendation(
                recommendation_id=rec_id,
                user_id=user_id,
                symbol=market_pattern.symbol,
                action=action,
                confidence=market_pattern.confidence * 0.8,  # Slightly conservative
                reasoning=f"{market_pattern.pattern_type.title()} pattern detected with {market_pattern.confidence:.1%} confidence",
                target_price=target_price,
                stop_loss=stop_loss,
                risk_score=self._calculate_risk_score(market_pattern, risk_pattern),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24)
            )

            return recommendation

        except Exception as e:
            logger.error(f"Failed to create recommendation: {e}")
            return None

    def _calculate_risk_score(self, market_pattern: MarketPattern,
                            risk_pattern: Optional[UserBehaviorPattern]) -> float:
        """Calculate risk score for a recommendation"""
        try:
            base_risk = 1.0 - market_pattern.confidence

            # Adjust for volatility
            volatility = market_pattern.features.get('volatility', 0.2)
            volatility_risk = min(volatility * 2, 0.5)

            # Adjust for user risk tolerance
            user_risk_adjustment = 0.0
            if risk_pattern:
                risk_level = risk_pattern.features.get('risk_level', 'moderate')
                if risk_level == 'high':
                    user_risk_adjustment = -0.1  # High risk tolerance reduces perceived risk
                elif risk_level == 'low':
                    user_risk_adjustment = 0.1   # Low risk tolerance increases perceived risk

            total_risk = min(1.0, base_risk + volatility_risk + user_risk_adjustment)
            return total_risk

        except:
            return 0.5  # Default moderate risk

    async def _model_trainer(self):
        """Train and update AI models with new data"""
        logger.info("Starting model trainer...")

        while self.is_learning:
            try:
                # Train models with accumulated data
                await self._train_price_predictor()
                await self._train_direction_classifier()
                await self._train_risk_assessor()

                # Save updated models
                self._save_trained_models()

                await asyncio.sleep(3600)  # Train every hour

            except Exception as e:
                logger.error(f"Model trainer error: {e}")
                await asyncio.sleep(3600)

    async def _train_price_predictor(self):
        """Train the price prediction model"""
        try:
            # Get training data from market patterns
            if len(self.market_patterns) < 10:
                return

            # Prepare features and targets
            features = []
            targets = []

            for pattern in self.market_patterns.values():
                if pattern.prediction.get('target_price'):
                    feature_vector = [
                        pattern.features.get('sma_20', 0),
                        pattern.features.get('rsi', 50),
                        pattern.features.get('macd', 0),
                        pattern.features.get('volatility', 0),
                        pattern.features.get('volume_ratio', 1)
                    ]
                    features.append(feature_vector)
                    targets.append(pattern.prediction['target_price'])

            if len(features) >= 10:
                X = np.array(features)
                y = np.array(targets)

                # Scale features
                X_scaled = self.scalers['price_predictor'].fit_transform(X)

                # Train model
                self.models['price_predictor'].fit(X_scaled, y)
                logger.info("Price predictor model updated")

        except Exception as e:
            logger.error(f"Failed to train price predictor: {e}")

    async def _train_direction_classifier(self):
        """Train the market direction classifier"""
        try:
            # Similar implementation for direction classification
            # This would use pattern types as labels
            pass
        except Exception as e:
            logger.error(f"Failed to train direction classifier: {e}")

    async def _train_risk_assessor(self):
        """Train the risk assessment model"""
        try:
            # Train model to predict trade risk based on user patterns
            pass
        except Exception as e:
            logger.error(f"Failed to train risk assessor: {e}")

    async def _save_patterns(self):
        """Save patterns to database"""
        try:
            # Save market patterns
            market_patterns_data = [asdict(pattern) for pattern in self.market_patterns.values()]
            self.persistence.save_system_state('market_patterns', market_patterns_data)

            # Save user patterns
            user_patterns_data = [asdict(pattern) for pattern in self.user_patterns.values()]
            self.persistence.save_system_state('user_patterns', user_patterns_data)

            logger.info("Patterns saved to database")

        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def get_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get current recommendations for a user"""
        try:
            user_recs = [
                asdict(rec) for rec in self.recommendations.values()
                if rec.user_id == user_id and rec.expires_at > datetime.now()
            ]
            return user_recs
        except Exception as e:
            logger.error(f"Failed to get user recommendations: {e}")
            return []

    def get_market_insights(self) -> Dict[str, Any]:
        """Get current market insights"""
        try:
            insights = {
                'total_patterns': len(self.market_patterns),
                'pattern_types': {},
                'high_confidence_patterns': [],
                'market_sentiment': 'neutral'
            }

            # Count pattern types
            for pattern in self.market_patterns.values():
                pattern_type = pattern.pattern_type
                if pattern_type not in insights['pattern_types']:
                    insights['pattern_types'][pattern_type] = 0
                insights['pattern_types'][pattern_type] += 1

                # High confidence patterns
                if pattern.confidence > 0.8:
                    insights['high_confidence_patterns'].append({
                        'symbol': pattern.symbol,
                        'type': pattern.pattern_type,
                        'confidence': pattern.confidence
                    })

            # Determine market sentiment
            uptrend_count = insights['pattern_types'].get('uptrend', 0)
            downtrend_count = insights['pattern_types'].get('downtrend', 0)

            if uptrend_count > downtrend_count * 1.5:
                insights['market_sentiment'] = 'bullish'
            elif downtrend_count > uptrend_count * 1.5:
                insights['market_sentiment'] = 'bearish'

            return insights

        except Exception as e:
            logger.error(f"Failed to get market insights: {e}")
            return {}

# Global AI learning engine instance
ai_learning_engine = None

def get_ai_learning_engine() -> AILearningEngine:
    """Get the global AI learning engine instance"""
    global ai_learning_engine
    if ai_learning_engine is None:
        ai_learning_engine = AILearningEngine()
    return ai_learning_engine
