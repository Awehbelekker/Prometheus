"""
ENHANCED RELEVANCE SCORING FOR TRADING INTELLIGENCE
===================================================

Trading-specific relevance scoring system that enhances intelligence
gathering and processing for financial market decisions.

Features:
- Market context similarity analysis
- Temporal relevance with trading-specific decay
- Historical trading effectiveness scoring
- Source reliability assessment
- Data quality evaluation
- Market correlation strength analysis
- Volatility regime detection
- Trading-specific multipliers
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import uuid
import json
import math

# Enhanced ML imports for TF-IDF and similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - using fallback similarity")

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

class VolatilityRegime(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class DataType(Enum):
    PRICE_DATA = "price_data"
    NEWS = "news"
    SOCIAL_SENTIMENT = "social_sentiment"
    ECONOMIC_DATA = "economic_data"
    FED_ANNOUNCEMENT = "fed_announcement"
    EARNINGS = "earnings"
    TECHNICAL_INDICATOR = "technical_indicator"
    WHALE_MOVEMENT = "whale_movement"

@dataclass
class TradingIntelligenceData:
    """Trading intelligence data structure"""
    data_id: str
    data_type: DataType
    content: Dict[str, Any]
    source: str
    timestamp: datetime
    symbol: Optional[str] = None
    impact_score: float = 0.0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TradingContext:
    """Trading context for relevance scoring"""
    target_symbol: str
    trading_timeframe: str
    market_conditions: Dict[str, Any]
    volatility_regime: VolatilityRegime
    correlation_environment: Dict[str, Any]
    current_positions: Dict[str, Any]
    risk_parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RelevanceScore:
    """Relevance score result"""
    overall_score: float
    component_scores: Dict[str, float]
    trading_multiplier: float
    explanation: str
    confidence: float

class AdvancedRelevanceScorer:
    """Enhanced relevance scoring system with TF-IDF and ML algorithms"""

    def __init__(self):
        self.base_weights = {
            'content_similarity': 0.25,
            'temporal_relevance': 0.20,
            'source_reliability': 0.15,
            'data_quality': 0.10,
            'historical_effectiveness': 0.20,
            'correlation_strength': 0.10
        }

        self.temporal_decay_lambda = 0.1  # Exponential decay rate

        # TF-IDF vectorizer for content similarity
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)  # Unigrams and bigrams
            )
        else:
            self.tfidf_vectorizer = None

        # Historical effectiveness tracking
        self.historical_effectiveness = {}  # {source_type: {successful_uses: int, total_uses: int}}

        # Correlation matrix for correlation strength
        self.correlation_matrix = {}  # {data_type_context_type: correlation_coefficient}

        # Source reliability scores (updated from experience)
        self.source_reliability_scores = {
            'bloomberg': {'accuracy': 0.95, 'frequency': 0.90, 'completeness': 0.92, 'error_rate': 0.02},
            'reuters': {'accuracy': 0.93, 'frequency': 0.88, 'completeness': 0.90, 'error_rate': 0.03},
            'yahoo_finance': {'accuracy': 0.90, 'frequency': 0.95, 'completeness': 0.88, 'error_rate': 0.05},
            'twitter': {'accuracy': 0.60, 'frequency': 0.98, 'completeness': 0.50, 'error_rate': 0.25},
            'reddit': {'accuracy': 0.55, 'frequency': 0.95, 'completeness': 0.45, 'error_rate': 0.30},
            'binance': {'accuracy': 0.98, 'frequency': 0.99, 'completeness': 0.95, 'error_rate': 0.01},
            'coinbase': {'accuracy': 0.97, 'frequency': 0.98, 'completeness': 0.94, 'error_rate': 0.02},
        }

        logger.info("🎯 Enhanced Relevance Scorer initialized with TF-IDF and ML algorithms")
    
    def calculate_relevance_score(self, data: TradingIntelligenceData, context: TradingContext) -> RelevanceScore:
        """Calculate enhanced relevance score with TF-IDF and ML algorithms"""

        # Calculate component scores
        component_scores = {
            'content_similarity': self._calculate_content_similarity_tfidf(data, context),
            'temporal_relevance': self._calculate_temporal_relevance_enhanced(data, context),
            'source_reliability': self._calculate_source_reliability_enhanced(data),
            'data_quality': self._calculate_data_quality(data),
            'historical_effectiveness': self._calculate_historical_effectiveness_enhanced(data, context),
            'correlation_strength': self._calculate_correlation_strength(data, context)
        }

        # Calculate weighted overall score
        overall_score = sum(
            score * self.base_weights[component]
            for component, score in component_scores.items()
        )

        # Apply trading multiplier based on market conditions
        trading_multiplier = self._calculate_trading_multiplier(data, context)
        final_score = overall_score * trading_multiplier

        # Generate explanation
        explanation = self._generate_explanation(component_scores, final_score, trading_multiplier)

        return RelevanceScore(
            overall_score=final_score,
            component_scores=component_scores,
            trading_multiplier=trading_multiplier,
            explanation=explanation,
            confidence=np.mean(list(component_scores.values()))
        )
    
    def _calculate_content_similarity_tfidf(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate content similarity using TF-IDF and cosine similarity"""

        # Symbol matching (exact match gets high score)
        symbol_match = 1.0 if data.symbol == context.target_symbol else 0.3

        # Content relevance using TF-IDF + Cosine Similarity
        if SKLEARN_AVAILABLE and self.tfidf_vectorizer:
            try:
                # Extract text content from data
                data_text = self._extract_text_content(data)
                context_text = self._extract_context_text(context)

                if data_text and context_text:
                    # Compute TF-IDF vectors
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform([data_text, context_text])

                    # Compute cosine similarity
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                    content_relevance = float(similarity)
                else:
                    content_relevance = 0.5  # Neutral if no text
            except Exception as e:
                logger.warning(f"TF-IDF calculation error: {e}")
                content_relevance = 0.6  # Fallback
        else:
            # Fallback: keyword matching
            content_relevance = self._calculate_keyword_similarity(data, context)

        # Market sector alignment (check if same sector/category)
        sector_alignment = self._calculate_sector_alignment(data, context)

        # Weighted combination
        return (symbol_match * 0.4 + content_relevance * 0.4 + sector_alignment * 0.2)

    def _extract_text_content(self, data: TradingIntelligenceData) -> str:
        """Extract text content from trading intelligence data"""
        text_parts = []

        # Add symbol
        if data.symbol:
            text_parts.append(data.symbol)

        # Add content fields
        if isinstance(data.content, dict):
            for key, value in data.content.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, (int, float)):
                    text_parts.append(str(value))

        # Add metadata
        if data.metadata:
            for key, value in data.metadata.items():
                if isinstance(value, str):
                    text_parts.append(value)

        return " ".join(text_parts)

    def _extract_context_text(self, context: TradingContext) -> str:
        """Extract text from trading context"""
        text_parts = [
            context.target_symbol,
            context.trading_timeframe,
            str(context.volatility_regime.value)
        ]

        # Add market conditions
        if context.market_conditions:
            for key, value in context.market_conditions.items():
                if isinstance(value, str):
                    text_parts.append(value)

        return " ".join(text_parts)

    def _calculate_keyword_similarity(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Fallback keyword-based similarity"""
        data_text = self._extract_text_content(data).lower()
        context_text = self._extract_context_text(context).lower()

        # Simple keyword overlap
        data_words = set(data_text.split())
        context_words = set(context_text.split())

        if not data_words or not context_words:
            return 0.5

        overlap = len(data_words & context_words)
        total = len(data_words | context_words)

        return overlap / total if total > 0 else 0.5

    def _calculate_sector_alignment(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate sector/category alignment"""
        # Sector mapping (simplified)
        sector_map = {
            'AAPL': 'tech', 'MSFT': 'tech', 'GOOGL': 'tech', 'AMZN': 'tech', 'META': 'tech',
            'TSLA': 'auto', 'F': 'auto', 'GM': 'auto',
            'JPM': 'finance', 'BAC': 'finance', 'GS': 'finance',
            'BTC/USD': 'crypto', 'ETH/USD': 'crypto', 'SOL/USD': 'crypto'
        }

        data_sector = sector_map.get(data.symbol, 'unknown')
        context_sector = sector_map.get(context.target_symbol, 'unknown')

        if data_sector == context_sector and data_sector != 'unknown':
            return 0.9
        elif data_sector != 'unknown' and context_sector != 'unknown':
            return 0.4  # Different sectors
        else:
            return 0.6  # Unknown sector
    
    def _calculate_temporal_relevance_enhanced(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate temporal relevance with enhanced exponential decay"""

        time_diff = (context.timestamp - data.timestamp).total_seconds()
        hours_diff = time_diff / 3600

        # Data type specific decay rates (from MD file algorithm)
        decay_rates = {
            DataType.PRICE_DATA: 0.5,  # Fast decay (price changes quickly)
            DataType.NEWS: 0.2,  # Medium decay
            DataType.SOCIAL_SENTIMENT: 0.3,  # Medium-fast decay
            DataType.ECONOMIC_DATA: 0.05,  # Slow decay (economic data relevant longer)
            DataType.FED_ANNOUNCEMENT: 0.02,  # Very slow decay
            DataType.EARNINGS: 0.1,  # Slow decay
            DataType.TECHNICAL_INDICATOR: 0.4,  # Fast decay
            DataType.WHALE_MOVEMENT: 0.15  # Medium decay
        }

        # Get decay rate for this data type
        lambda_rate = decay_rates.get(data.data_type, self.temporal_decay_lambda)

        # Exponential temporal decay: exp(-λ × Δt)
        decay_factor = math.exp(-lambda_rate * hours_diff)

        # Apply minimum threshold
        return max(0.05, min(1.0, decay_factor))
    
    def _calculate_source_reliability_enhanced(self, data: TradingIntelligenceData) -> float:
        """Calculate enhanced source reliability using multi-factor scoring"""

        source_lower = data.source.lower()

        # Find matching source
        source_metrics = None
        for source, metrics in self.source_reliability_scores.items():
            if source in source_lower:
                source_metrics = metrics
                break

        if not source_metrics:
            # Default for unknown sources
            source_metrics = {
                'accuracy': 0.70,
                'frequency': 0.75,
                'completeness': 0.70,
                'error_rate': 0.15
            }

        # Multi-factor reliability score (from MD file algorithm)
        # R_source = (w1×accuracy + w2×frequency + w3×completeness) × (1 - error_rate)
        weights = {'accuracy': 0.5, 'frequency': 0.2, 'completeness': 0.3}

        base_score = (
            weights['accuracy'] * source_metrics['accuracy'] +
            weights['frequency'] * source_metrics['frequency'] +
            weights['completeness'] * source_metrics['completeness']
        )

        # Apply error rate penalty
        reliability_score = base_score * (1 - source_metrics['error_rate'])

        return max(0.1, min(1.0, reliability_score))
    
    def _calculate_data_quality(self, data: TradingIntelligenceData) -> float:
        """Calculate data quality score"""
        
        quality_factors = []
        
        # Completeness
        completeness = len(data.content) / 10  # Assume 10 fields is complete
        quality_factors.append(min(1.0, completeness))
        
        # Confidence score
        quality_factors.append(data.confidence)
        
        # Metadata richness
        metadata_richness = len(data.metadata) / 5  # Assume 5 metadata fields is rich
        quality_factors.append(min(1.0, metadata_richness))
        
        return np.mean(quality_factors)
    
    def _calculate_historical_effectiveness_enhanced(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate historical effectiveness using actual performance tracking"""

        # Create key for historical tracking
        effectiveness_key = f"{data.data_type.value}_{data.source}"

        # Check if we have historical data
        if effectiveness_key in self.historical_effectiveness:
            stats = self.historical_effectiveness[effectiveness_key]
            successful = stats.get('successful_uses', 0)
            total = stats.get('total_uses', 0)

            if total > 0:
                # Calculate effectiveness ratio
                effectiveness = successful / total

                # Apply confidence based on sample size
                confidence_factor = min(1.0, total / 100)  # Full confidence at 100+ samples

                # Blend with baseline
                baseline = self._get_baseline_effectiveness(data.data_type)
                return effectiveness * confidence_factor + baseline * (1 - confidence_factor)

        # Fallback to baseline effectiveness
        return self._get_baseline_effectiveness(data.data_type)

    def _get_baseline_effectiveness(self, data_type: DataType) -> float:
        """Get baseline effectiveness for data type"""
        effectiveness_map = {
            DataType.FED_ANNOUNCEMENT: 0.92,
            DataType.EARNINGS: 0.88,
            DataType.ECONOMIC_DATA: 0.85,
            DataType.WHALE_MOVEMENT: 0.82,
            DataType.NEWS: 0.75,
            DataType.SOCIAL_SENTIMENT: 0.65,
            DataType.TECHNICAL_INDICATOR: 0.78,
            DataType.PRICE_DATA: 0.90
        }
        return effectiveness_map.get(data_type, 0.70)

    def update_historical_effectiveness(self, data_type: DataType, source: str, was_successful: bool):
        """Update historical effectiveness tracking"""
        effectiveness_key = f"{data_type.value}_{source}"

        if effectiveness_key not in self.historical_effectiveness:
            self.historical_effectiveness[effectiveness_key] = {
                'successful_uses': 0,
                'total_uses': 0
            }

        self.historical_effectiveness[effectiveness_key]['total_uses'] += 1
        if was_successful:
            self.historical_effectiveness[effectiveness_key]['successful_uses'] += 1

    def _calculate_correlation_strength(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate correlation strength between data and context"""

        # Create correlation key
        correlation_key = f"{data.data_type.value}_{context.target_symbol}"

        # Check if we have correlation data
        if correlation_key in self.correlation_matrix:
            return abs(self.correlation_matrix[correlation_key])

        # Fallback to estimated correlation based on data type
        correlation_estimates = {
            DataType.PRICE_DATA: 0.95,
            DataType.TECHNICAL_INDICATOR: 0.85,
            DataType.EARNINGS: 0.80,
            DataType.NEWS: 0.70,
            DataType.ECONOMIC_DATA: 0.65,
            DataType.FED_ANNOUNCEMENT: 0.75,
            DataType.SOCIAL_SENTIMENT: 0.60,
            DataType.WHALE_MOVEMENT: 0.70
        }

        return correlation_estimates.get(data.data_type, 0.60)

    def update_correlation_matrix(self, data_type: DataType, symbol: str, correlation: float):
        """Update correlation matrix with observed correlations"""
        correlation_key = f"{data_type.value}_{symbol}"
        self.correlation_matrix[correlation_key] = correlation

    def _calculate_trading_multiplier(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate trading-specific multiplier based on market conditions"""
        multiplier = 1.0

        # Volatility regime multiplier
        if context.volatility_regime == VolatilityRegime.EXTREME:
            # In extreme volatility, news and sentiment matter more
            if data.data_type in [DataType.NEWS, DataType.SOCIAL_SENTIMENT, DataType.FED_ANNOUNCEMENT]:
                multiplier *= 1.3
            else:
                multiplier *= 0.9
        elif context.volatility_regime == VolatilityRegime.LOW:
            # In low volatility, technical indicators matter more
            if data.data_type in [DataType.TECHNICAL_INDICATOR, DataType.PRICE_DATA]:
                multiplier *= 1.2

        # Market condition multiplier
        market_condition = context.market_conditions.get('condition', MarketCondition.SIDEWAYS)
        if market_condition == MarketCondition.VOLATILE:
            if data.data_type in [DataType.NEWS, DataType.WHALE_MOVEMENT]:
                multiplier *= 1.2

        return max(0.5, min(2.0, multiplier))
    
    def _calculate_context_alignment(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate alignment with trading context"""
        
        alignment_factors = []
        
        # Timeframe alignment
        if context.trading_timeframe in ['1m', '5m', '15m']:  # Short-term
            if data.data_type in [DataType.PRICE_DATA, DataType.TECHNICAL_INDICATOR]:
                alignment_factors.append(0.9)
            else:
                alignment_factors.append(0.6)
        elif context.trading_timeframe in ['1h', '4h']:  # Medium-term
            alignment_factors.append(0.8)
        else:  # Long-term
            if data.data_type in [DataType.ECONOMIC_DATA, DataType.EARNINGS]:
                alignment_factors.append(0.9)
            else:
                alignment_factors.append(0.7)
        
        # Market condition alignment
        market_condition = context.market_conditions.get('condition', MarketCondition.SIDEWAYS)
        if market_condition == MarketCondition.VOLATILE:
            if data.data_type in [DataType.NEWS, DataType.SOCIAL_SENTIMENT]:
                alignment_factors.append(0.9)
            else:
                alignment_factors.append(0.7)
        else:
            alignment_factors.append(0.8)
        
        return np.mean(alignment_factors)
    
    def _generate_explanation(self, component_scores: Dict[str, float], overall_score: float, trading_multiplier: float = 1.0) -> str:
        """Generate enhanced explanation for relevance score"""

        explanation = f"📊 Final Relevance Score: {overall_score:.3f}\n"
        if trading_multiplier != 1.0:
            explanation += f"   (Base: {overall_score/trading_multiplier:.3f} × Multiplier: {trading_multiplier:.2f})\n"
        explanation += "\n"

        explanation += "Component Breakdown:\n"
        for component, score in sorted(component_scores.items(), key=lambda x: x[1], reverse=True):
            status = "[CHECK]" if score >= 0.8 else "[WARNING]️" if score >= 0.6 else "[ERROR]"
            bar = "█" * int(score * 10)
            explanation += f"{status} {component.replace('_', ' ').title():30s}: {score:.3f} {bar}\n"

        return explanation

class TradingRelevanceScorer(AdvancedRelevanceScorer):
    """
    TRADING-SPECIFIC RELEVANCE SCORING
    Enhanced for financial market intelligence
    """
    
    def __init__(self):
        super().__init__()
        
        # Trading-specific weights
        self.weights = {
            'market_context_similarity': 0.30,  # Higher weight for market context
            'temporal_relevance': 0.25,         # Time is critical in trading
            'historical_trading_effectiveness': 0.20,
            'source_reliability': 0.15,
            'data_quality': 0.05,
            'market_correlation_strength': 0.05,
        }
        
        # Trading-specific decay parameters
        self.temporal_decay_lambda = 0.5  # Faster decay for trading data
        
        # Market analysis cache
        self.market_analysis_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
        logger.info("🎯 Trading Relevance Scorer initialized")
        logger.info(f"📊 Trading-specific weights: {self.weights}")
        
    async def calculate_trading_relevance(self, 
                                        intelligence_data: TradingIntelligenceData, 
                                        trading_context: TradingContext) -> RelevanceScore:
        """
        TRADING INTELLIGENCE: Score relevance for trading decisions
        
        Enhanced for:
        - Market volatility context
        - Asset correlation analysis
        - News impact assessment
        - Social sentiment relevance
        """
        
        logger.info(f"🎯 Calculating trading relevance for {intelligence_data.data_id}")
        
        # Enhance context with real-time market analysis
        enhanced_context = await self._enhance_trading_context(trading_context)
        
        # Calculate component scores with trading-specific logic
        component_scores = {
            'market_context_similarity': await self._calculate_market_context_similarity(intelligence_data, enhanced_context),
            'temporal_relevance': self._calculate_trading_temporal_relevance(intelligence_data, enhanced_context),
            'historical_trading_effectiveness': self._calculate_historical_trading_effectiveness(intelligence_data, enhanced_context),
            'source_reliability': self._calculate_trading_source_reliability(intelligence_data),
            'data_quality': self._calculate_trading_data_quality(intelligence_data),
            'market_correlation_strength': await self._calculate_market_correlation_strength(intelligence_data, enhanced_context)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.weights[component]
            for component, score in component_scores.items()
        )
        
        # Apply trading-specific multipliers
        trading_multiplier = await self._calculate_trading_multiplier(intelligence_data, enhanced_context)
        final_score = overall_score * trading_multiplier
        
        # Ensure score is within bounds
        final_score = min(1.0, max(0.0, final_score))
        
        # Generate enhanced explanation
        explanation = self._generate_trading_explanation(component_scores, overall_score, trading_multiplier, final_score)
        
        result = RelevanceScore(
            overall_score=final_score,
            component_scores=component_scores,
            trading_multiplier=trading_multiplier,
            explanation=explanation,
            confidence=np.mean(list(component_scores.values()))
        )
        
        logger.info(f"[CHECK] Trading relevance calculated: {final_score:.2f} (multiplier: {trading_multiplier:.2f})")
        
        return result
    
    async def _enhance_trading_context(self, context: TradingContext) -> TradingContext:
        """Enhance trading context with real-time market analysis"""
        
        # Check cache
        cache_key = f"{context.target_symbol}_{context.trading_timeframe}"
        current_time = datetime.now()
        
        if cache_key in self.market_analysis_cache:
            cached_data, timestamp = self.market_analysis_cache[cache_key]
            if (current_time - timestamp).seconds < self.cache_expiry:
                context.market_conditions.update(cached_data['market_conditions'])
                context.volatility_regime = cached_data['volatility_regime']
                context.correlation_environment.update(cached_data['correlation_environment'])
                return context
        
        # Generate fresh market analysis
        market_conditions = await self._analyze_market_conditions(context)
        volatility_regime = await self._detect_volatility_regime(context)
        correlation_environment = await self._analyze_correlations(context)
        
        # Update context
        context.market_conditions.update(market_conditions)
        context.volatility_regime = volatility_regime
        context.correlation_environment.update(correlation_environment)
        
        # Cache the analysis
        self.market_analysis_cache[cache_key] = (
            {
                'market_conditions': market_conditions,
                'volatility_regime': volatility_regime,
                'correlation_environment': correlation_environment
            },
            current_time
        )
        
        return context
    
    async def _analyze_market_conditions(self, context: TradingContext) -> Dict[str, Any]:
        """Analyze current market conditions"""
        
        # Simulate market condition analysis
        conditions = {
            'condition': np.random.choice([MarketCondition.BULL, MarketCondition.BEAR, MarketCondition.SIDEWAYS, MarketCondition.VOLATILE]),
            'trend_strength': np.random.uniform(0.3, 0.9),
            'volume_percentile': np.random.uniform(0.2, 0.95),
            'momentum': np.random.uniform(-0.5, 0.8),
            'support_resistance_strength': np.random.uniform(0.4, 0.9)
        }
        
        return conditions
    
    async def _detect_volatility_regime(self, context: TradingContext) -> VolatilityRegime:
        """Detect current volatility regime"""
        
        # Simulate volatility analysis
        volatility_score = np.random.uniform(0.1, 0.9)
        
        if volatility_score > 0.8:
            return VolatilityRegime.EXTREME
        elif volatility_score > 0.6:
            return VolatilityRegime.HIGH
        elif volatility_score > 0.3:
            return VolatilityRegime.MEDIUM
        else:
            return VolatilityRegime.LOW
    
    async def _analyze_correlations(self, context: TradingContext) -> Dict[str, Any]:
        """Analyze asset correlations"""
        
        # Simulate correlation analysis
        correlations = {
            'btc_correlation': np.random.uniform(-0.3, 0.8),
            'spy_correlation': np.random.uniform(-0.2, 0.6),
            'gold_correlation': np.random.uniform(-0.4, 0.5),
            'dxy_correlation': np.random.uniform(-0.6, 0.3),
            'sector_correlation': np.random.uniform(0.2, 0.9)
        }
        
        return correlations

    async def _calculate_market_context_similarity(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate market context similarity with trading-specific logic"""

        similarity_factors = []

        # Symbol matching (highest priority)
        if data.symbol == context.target_symbol:
            similarity_factors.append(1.0)
        elif data.symbol and context.target_symbol:
            # Check correlation for related symbols
            correlation = context.correlation_environment.get(f"{data.symbol.lower()}_correlation", 0.3)
            similarity_factors.append(max(0.3, abs(correlation)))
        else:
            similarity_factors.append(0.5)  # Generic market data

        # Market condition alignment
        market_condition = context.market_conditions.get('condition', MarketCondition.SIDEWAYS)
        if data.data_type == DataType.NEWS and market_condition == MarketCondition.VOLATILE:
            similarity_factors.append(0.95)  # News is highly relevant in volatile markets
        elif data.data_type == DataType.TECHNICAL_INDICATOR and market_condition in [MarketCondition.BULL, MarketCondition.BEAR]:
            similarity_factors.append(0.90)  # Technical indicators are key in trending markets
        else:
            similarity_factors.append(0.75)

        # Timeframe alignment
        timeframe_alignment = self._calculate_timeframe_alignment(data, context)
        similarity_factors.append(timeframe_alignment)

        return np.mean(similarity_factors)

    def _calculate_timeframe_alignment(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate timeframe alignment score"""

        # Map data types to optimal timeframes
        data_timeframe_map = {
            DataType.PRICE_DATA: ['1m', '5m', '15m', '1h'],
            DataType.TECHNICAL_INDICATOR: ['5m', '15m', '1h', '4h'],
            DataType.NEWS: ['15m', '1h', '4h', '1d'],
            DataType.SOCIAL_SENTIMENT: ['5m', '15m', '1h'],
            DataType.ECONOMIC_DATA: ['1h', '4h', '1d', '1w'],
            DataType.FED_ANNOUNCEMENT: ['1h', '4h', '1d'],
            DataType.EARNINGS: ['1h', '4h', '1d'],
            DataType.WHALE_MOVEMENT: ['1m', '5m', '15m', '1h']
        }

        optimal_timeframes = data_timeframe_map.get(data.data_type, ['1h', '4h'])

        if context.trading_timeframe in optimal_timeframes:
            return 0.95
        else:
            # Calculate distance penalty
            timeframe_order = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
            try:
                context_idx = timeframe_order.index(context.trading_timeframe)
                optimal_indices = [timeframe_order.index(tf) for tf in optimal_timeframes if tf in timeframe_order]
                if optimal_indices:
                    min_distance = min(abs(context_idx - idx) for idx in optimal_indices)
                    return max(0.3, 1.0 - (min_distance * 0.15))
            except ValueError:
                pass

            return 0.6  # Default alignment

    def _calculate_trading_temporal_relevance(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate temporal relevance with trading-specific decay"""

        time_diff = (context.timestamp - data.timestamp).total_seconds()
        hours_diff = time_diff / 3600

        # Different decay rates for different data types
        decay_rates = {
            DataType.PRICE_DATA: 2.0,  # Very fast decay
            DataType.WHALE_MOVEMENT: 1.5,  # Fast decay
            DataType.SOCIAL_SENTIMENT: 1.0,  # Medium decay
            DataType.NEWS: 0.5,  # Slower decay
            DataType.TECHNICAL_INDICATOR: 0.8,  # Medium-fast decay
            DataType.ECONOMIC_DATA: 0.2,  # Very slow decay
            DataType.FED_ANNOUNCEMENT: 0.1,  # Extremely slow decay
            DataType.EARNINGS: 0.3  # Slow decay
        }

        decay_rate = decay_rates.get(data.data_type, self.temporal_decay_lambda)

        # Apply volatility adjustment
        if context.volatility_regime in [VolatilityRegime.HIGH, VolatilityRegime.EXTREME]:
            decay_rate *= 1.5  # Faster decay in high volatility

        # Exponential decay
        decay_factor = math.exp(-decay_rate * hours_diff)

        return max(0.05, decay_factor)

    def _calculate_historical_trading_effectiveness(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate historical trading effectiveness with context"""

        # Base effectiveness by data type
        base_effectiveness = {
            DataType.FED_ANNOUNCEMENT: 0.95,
            DataType.EARNINGS: 0.90,
            DataType.WHALE_MOVEMENT: 0.88,
            DataType.ECONOMIC_DATA: 0.85,
            DataType.PRICE_DATA: 0.82,
            DataType.TECHNICAL_INDICATOR: 0.80,
            DataType.NEWS: 0.75,
            DataType.SOCIAL_SENTIMENT: 0.65
        }

        effectiveness = base_effectiveness.get(data.data_type, 0.70)

        # Adjust based on market conditions
        market_condition = context.market_conditions.get('condition', MarketCondition.SIDEWAYS)

        if market_condition == MarketCondition.VOLATILE:
            if data.data_type in [DataType.NEWS, DataType.SOCIAL_SENTIMENT]:
                effectiveness *= 1.2  # More effective in volatile markets
            elif data.data_type == DataType.TECHNICAL_INDICATOR:
                effectiveness *= 0.9  # Less reliable in volatile markets

        # Adjust based on volatility regime
        if context.volatility_regime == VolatilityRegime.LOW:
            if data.data_type == DataType.TECHNICAL_INDICATOR:
                effectiveness *= 1.1  # More reliable in low volatility

        return min(1.0, effectiveness)

    def _calculate_trading_source_reliability(self, data: TradingIntelligenceData) -> float:
        """Calculate source reliability with trading-specific adjustments"""

        # Enhanced source reliability for trading
        trading_source_scores = {
            'bloomberg': 0.98,
            'reuters': 0.96,
            'marketwatch': 0.90,
            'cnbc': 0.88,
            'yahoo_finance': 0.85,
            'seeking_alpha': 0.82,
            'benzinga': 0.80,
            'twitter_verified': 0.75,
            'twitter': 0.60,
            'reddit_wsb': 0.55,
            'reddit': 0.50,
            'telegram': 0.45,
            'discord': 0.40,
            'internal_model': 0.92,
            'api_data': 0.95
        }

        source_lower = data.source.lower()
        for source, score in trading_source_scores.items():
            if source in source_lower:
                # Adjust based on data type
                if data.data_type in [DataType.FED_ANNOUNCEMENT, DataType.ECONOMIC_DATA] and 'bloomberg' in source_lower:
                    return min(1.0, score * 1.05)  # Bloomberg is especially reliable for official data
                return score

        return 0.65  # Default trading reliability

    def _calculate_trading_data_quality(self, data: TradingIntelligenceData) -> float:
        """Calculate data quality with trading-specific metrics"""

        quality_factors = []

        # Content completeness
        required_fields = ['timestamp', 'source', 'content']
        optional_fields = ['symbol', 'impact_score', 'confidence', 'metadata']

        completeness = len([f for f in required_fields if hasattr(data, f) and getattr(data, f)]) / len(required_fields)
        optional_completeness = len([f for f in optional_fields if hasattr(data, f) and getattr(data, f)]) / len(optional_fields)

        quality_factors.append(completeness)
        quality_factors.append(optional_completeness * 0.5)  # Optional fields have lower weight

        # Confidence score
        quality_factors.append(data.confidence)

        # Impact score availability
        if data.impact_score > 0:
            quality_factors.append(min(1.0, data.impact_score))
        else:
            quality_factors.append(0.5)

        # Metadata richness
        metadata_score = min(1.0, len(data.metadata) / 3) if data.metadata else 0.3
        quality_factors.append(metadata_score)

        return np.mean(quality_factors)

    async def _calculate_market_correlation_strength(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """Calculate market correlation strength"""

        if not data.symbol or data.symbol == context.target_symbol:
            return 1.0  # Perfect correlation for same symbol

        # Get correlation from context
        correlation_key = f"{data.symbol.lower()}_correlation"
        correlation = context.correlation_environment.get(correlation_key, 0.0)

        # Convert correlation to strength (absolute value)
        correlation_strength = abs(correlation)

        # Boost for strong correlations
        if correlation_strength > 0.8:
            return min(1.0, correlation_strength * 1.1)

        return correlation_strength

    async def _calculate_trading_multiplier(self, data: TradingIntelligenceData, context: TradingContext) -> float:
        """
        TRADING BOOST: Increase relevance for trading-critical data
        """
        multiplier = 1.0

        # Boost for market-moving events
        if data.data_type in [DataType.FED_ANNOUNCEMENT, DataType.EARNINGS, DataType.ECONOMIC_DATA]:
            multiplier *= 1.5

        # Boost for high-volume trading periods
        volume_percentile = context.market_conditions.get('volume_percentile', 0.5)
        if volume_percentile > 0.8:
            multiplier *= 1.3

        # Boost for high volatility periods
        if context.volatility_regime in [VolatilityRegime.HIGH, VolatilityRegime.EXTREME]:
            if data.data_type in [DataType.NEWS, DataType.SOCIAL_SENTIMENT, DataType.WHALE_MOVEMENT]:
                multiplier *= 1.4

        # Boost for strong momentum periods
        momentum = context.market_conditions.get('momentum', 0.0)
        if abs(momentum) > 0.6:
            if data.data_type in [DataType.TECHNICAL_INDICATOR, DataType.PRICE_DATA]:
                multiplier *= 1.2

        # Boost for breaking news during market hours
        if data.data_type == DataType.NEWS and data.impact_score > 0.8:
            multiplier *= 1.6

        # Boost for whale movements in low liquidity
        if data.data_type == DataType.WHALE_MOVEMENT:
            volume_percentile = context.market_conditions.get('volume_percentile', 0.5)
            if volume_percentile < 0.3:  # Low volume = higher whale impact
                multiplier *= 1.8

        return multiplier

    def _generate_trading_explanation(self, component_scores: Dict[str, float],
                                    overall_score: float,
                                    trading_multiplier: float,
                                    final_score: float) -> str:
        """Generate enhanced explanation for trading relevance score"""

        explanation = f"Trading Relevance Score: {final_score:.2f}\n"
        explanation += f"Base Score: {overall_score:.2f} × Trading Multiplier: {trading_multiplier:.2f}\n\n"

        explanation += "Component Breakdown:\n"
        for component, score in sorted(component_scores.items(), key=lambda x: x[1], reverse=True):
            status = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
            component_name = component.replace('_', ' ').title()
            explanation += f"{status} {component_name}: {score:.2f} (weight: {self.weights[component]:.0%})\n"

        # Add trading-specific insights
        explanation += f"\nTrading Multiplier Factors:\n"
        if trading_multiplier > 1.2:
            explanation += "🚀 High-impact trading conditions detected\n"
        elif trading_multiplier > 1.0:
            explanation += "📈 Favorable trading conditions\n"
        else:
            explanation += "📊 Standard trading conditions\n"

        return explanation


# Example usage and testing
async def test_trading_relevance_scorer():
    """Test the trading relevance scoring system"""

    # Initialize scorer
    scorer = TradingRelevanceScorer()

    # Create test trading intelligence data
    test_data = TradingIntelligenceData(
        data_id="test_001",
        data_type=DataType.FED_ANNOUNCEMENT,
        content={"announcement": "Fed raises rates by 0.25%", "impact": "hawkish"},
        source="bloomberg",
        timestamp=datetime.now() - timedelta(minutes=30),
        symbol="BTCUSD",
        impact_score=0.9,
        confidence=0.95,
        metadata={"category": "monetary_policy", "sentiment": "negative"}
    )

    # Create test trading context
    test_context = TradingContext(
        target_symbol="BTCUSD",
        trading_timeframe="1h",
        market_conditions={"condition": MarketCondition.VOLATILE, "volume_percentile": 0.85},
        volatility_regime=VolatilityRegime.HIGH,
        correlation_environment={"btc_correlation": 1.0, "spy_correlation": 0.6},
        current_positions={"BTCUSD": {"size": 1000, "side": "long"}},
        risk_parameters={"max_position_size": 5000, "stop_loss": 0.02}
    )

    # Calculate trading relevance
    relevance_result = await scorer.calculate_trading_relevance(test_data, test_context)

    # Print results
    print(f"\n🎯 Trading Relevance Scoring Results:")
    print(f"📊 Final Score: {relevance_result.overall_score:.2f}")
    print(f"🚀 Trading Multiplier: {relevance_result.trading_multiplier:.2f}")
    print(f"🎯 Confidence: {relevance_result.confidence:.2f}")

    print(f"\n📈 Component Scores:")
    for component, score in relevance_result.component_scores.items():
        print(f"   {component.replace('_', ' ').title()}: {score:.2f}")

    print(f"\n📝 Explanation:")
    print(relevance_result.explanation)


if __name__ == "__main__":
    asyncio.run(test_trading_relevance_scorer())
