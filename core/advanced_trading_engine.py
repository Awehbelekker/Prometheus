"""
Advanced Real-Time Trading Integration
Combines GPT-OSS reasoning with live market analysis for automated trading decisions
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Import our existing systems
from core.reasoning.thinkmesh_adapter import (
    ThinkMeshAdapter, 
    ThinkMeshConfig, 
    ReasoningStrategy,
    analyze_trading_decision
)

try:
    from core.reasoning.gpt_oss_backend import gpt_oss_backend
    GPT_OSS_AVAILABLE = True
except ImportError:
    GPT_OSS_AVAILABLE = False

logger = logging.getLogger(__name__)

class MarketCondition(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"

class TradingSignal(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class MarketData:
    """Real-time market data structure"""
    symbol: str
    price: float
    volume: int
    change_24h: float
    change_percent: float
    high_24h: float
    low_24h: float
    market_cap: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class TechnicalIndicators:
    """Technical analysis indicators"""
    rsi: float
    macd: float
    sma_20: float
    sma_50: float
    sma_200: float
    bollinger_upper: float
    bollinger_lower: float
    volume_sma: float
    momentum: float

@dataclass
class TradingRecommendation:
    """AI-generated trading recommendation"""
    symbol: str
    signal: TradingSignal
    confidence: float
    reasoning: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_score: float
    time_horizon: str
    market_condition: MarketCondition
    technical_analysis: Dict[str, Any]
    fundamental_factors: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class AdvancedTradingEngine:
    """
    Advanced trading engine that combines multiple AI reasoning strategies
    with real-time market analysis and GPT-OSS local inference
    """
    
    def __init__(self):
        self.reasoning_adapter = ThinkMeshAdapter(enabled=True)
        self.trading_history = []
        self.active_positions = {}
        self.risk_limits = {
            'max_position_size': 0.15,  # 15% of portfolio per position (3x increase for live trading)
            'max_daily_risk': 0.03,     # 3% max daily portfolio risk (1.5x increase)
            'max_correlation': 0.6,     # Max correlation between positions (reduced for diversification)
            'stop_loss_max': 0.05,      # Max 5% stop loss (tighter control for live trading)
            'max_single_position_risk': 0.15,  # 15% max single position risk
            'max_portfolio_risk': 0.20,        # 20% max total portfolio risk
            'max_daily_loss': 0.05,            # 5% max daily loss limit
            'max_drawdown': 0.10,              # 10% max drawdown limit
            'min_position_size': 0.05,         # 5% minimum position size
            'max_positions': 5,                # Maximum 5 concurrent positions
            'position_scaling': True,          # Enable position scaling based on confidence
            'default_stop_loss': 0.03,         # 3% default stop loss
            'default_take_profit': 0.09,       # 9% default take profit (3:1 risk-reward)
            'trailing_stop': True,             # Enable trailing stops
            'trailing_stop_distance': 0.02     # 2% trailing stop distance
        }
        
        # Initialize GPT-OSS if available
        if GPT_OSS_AVAILABLE:
            self.gpt_oss = gpt_oss_backend
            logger.info("GPT-OSS backend available for local inference")
        else:
            self.gpt_oss = None
            logger.info("GPT-OSS not available, using enhanced fallback")
    
    async def initialize(self):
        """Initialize the trading engine"""
        if self.gpt_oss:
            await self.gpt_oss.initialize()
        logger.info("Advanced Trading Engine initialized")
    
    async def analyze_market_opportunity(
        self, 
        market_data: MarketData,
        technical_indicators: TechnicalIndicators,
        news_sentiment: Optional[Dict[str, Any]] = None
    ) -> TradingRecommendation:
        """
        Comprehensive market opportunity analysis using multiple AI strategies
        """
        
        # Step 1: Multi-strategy reasoning analysis
        reasoning_results = await self._multi_strategy_analysis(
            market_data, technical_indicators, news_sentiment
        )
        
        # Step 2: Risk assessment
        risk_analysis = await self._assess_trading_risk(
            market_data, technical_indicators
        )
        
        # Step 3: Position sizing and entry/exit calculation
        position_details = await self._calculate_position_parameters(
            market_data, risk_analysis
        )
        
        # Step 4: Generate final recommendation
        recommendation = await self._generate_recommendation(
            market_data, 
            reasoning_results, 
            risk_analysis, 
            position_details,
            technical_indicators
        )
        
        return recommendation
    
    async def _multi_strategy_analysis(
        self,
        market_data: MarketData,
        technical_indicators: TechnicalIndicators,
        news_sentiment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run multiple reasoning strategies in parallel for comprehensive analysis
        """
        
        # Prepare context for AI reasoning
        context = {
            "market_data": {
                "symbol": market_data.symbol,
                "price": market_data.price,
                "volume": market_data.volume,
                "change_24h": market_data.change_24h,
                "change_percent": market_data.change_percent,
                "high_24h": market_data.high_24h,
                "low_24h": market_data.low_24h
            },
            "technical_indicators": {
                "rsi": technical_indicators.rsi,
                "macd": technical_indicators.macd,
                "sma_20": technical_indicators.sma_20,
                "sma_50": technical_indicators.sma_50,
                "sma_200": technical_indicators.sma_200,
                "bollinger_upper": technical_indicators.bollinger_upper,
                "bollinger_lower": technical_indicators.bollinger_lower,
                "momentum": technical_indicators.momentum
            },
            "news_sentiment": news_sentiment or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Define multiple reasoning strategies
        strategies = [
            (ReasoningStrategy.SELF_CONSISTENCY, "Technical Analysis Consensus"),
            (ReasoningStrategy.DEBATE, "Bull vs Bear Analysis"),
            (ReasoningStrategy.TREE_OF_THOUGHT, "Scenario Planning"),
            (ReasoningStrategy.DEEPCONF, "Confidence-Gated Decision")
        ]
        
        results = {}
        
        # Run all strategies in parallel
        tasks = []
        for strategy, description in strategies:
            task = self._run_strategy_analysis(
                strategy, description, market_data.symbol, context
            )
            tasks.append(task)
        
        strategy_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        for i, (strategy, description) in enumerate(strategies):
            if not isinstance(strategy_results[i], Exception):
                results[strategy.value] = {
                    "description": description,
                    "result": strategy_results[i],
                    "weight": self._get_strategy_weight(strategy)
                }
            else:
                logger.error(f"Strategy {strategy.value} failed: {strategy_results[i]}")
        
        return results
    
    async def _run_strategy_analysis(
        self,
        strategy: ReasoningStrategy,
        description: str,
        symbol: str,
        context: Dict[str, Any]
    ):
        """Run a specific reasoning strategy"""
        
        prompt = f"""
        Analyze the trading opportunity for {symbol} based on the following data:
        
        Market Data: {json.dumps(context['market_data'], indent=2)}
        Technical Indicators: {json.dumps(context['technical_indicators'], indent=2)}
        
        Focus: {description}
        
        Consider:
        1. Price action and momentum
        2. Technical indicator signals
        3. Volume analysis
        4. Risk/reward ratio
        5. Market sentiment
        
        Provide a clear trading recommendation: BUY, SELL, or HOLD
        Include confidence level and reasoning.
        """
        
        config = ThinkMeshConfig(
            strategy=strategy,
            parallel_paths=3 if strategy == ReasoningStrategy.SELF_CONSISTENCY else 2,
            debate_rounds=2 if strategy == ReasoningStrategy.DEBATE else 1,
            tree_branches=3 if strategy == ReasoningStrategy.TREE_OF_THOUGHT else 2,
            max_tokens=512,
            temperature=0.7,
            wall_clock_timeout_s=15,
            require_final_answer=True
        )
        
        result = await self.reasoning_adapter.reason(prompt, config, context)
        return result
    
    def _get_strategy_weight(self, strategy: ReasoningStrategy) -> float:
        """Get weighting for different strategies"""
        weights = {
            ReasoningStrategy.SELF_CONSISTENCY: 0.3,  # High weight for consensus
            ReasoningStrategy.DEBATE: 0.25,           # Good for balanced view
            ReasoningStrategy.TREE_OF_THOUGHT: 0.25,  # Good for scenario planning
            ReasoningStrategy.DEEPCONF: 0.2           # Conservative but reliable
        }
        return weights.get(strategy, 0.25)
    
    async def _assess_trading_risk(
        self,
        market_data: MarketData,
        technical_indicators: TechnicalIndicators
    ) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        # Volatility analysis
        price_volatility = abs(market_data.change_percent) / 100
        volume_ratio = market_data.volume / technical_indicators.volume_sma if technical_indicators.volume_sma > 0 else 1
        
        # Technical risk factors
        rsi_oversold = technical_indicators.rsi < 30
        rsi_overbought = technical_indicators.rsi > 70
        price_near_bollinger = (
            market_data.price < technical_indicators.bollinger_lower * 1.02 or
            market_data.price > technical_indicators.bollinger_upper * 0.98
        )
        
        # Trend strength
        sma_alignment = (
            technical_indicators.sma_20 > technical_indicators.sma_50 > technical_indicators.sma_200
        ) or (
            technical_indicators.sma_20 < technical_indicators.sma_50 < technical_indicators.sma_200
        )
        
        # Calculate composite risk score (0-1, higher = riskier)
        risk_factors = {
            'volatility': min(price_volatility * 10, 1.0),  # Cap at 1.0
            'volume_anomaly': min(abs(volume_ratio - 1) * 2, 1.0),
            'rsi_extreme': 1.0 if (rsi_oversold or rsi_overbought) else 0.0,
            'bollinger_extreme': 1.0 if price_near_bollinger else 0.0,
            'trend_uncertainty': 0.0 if sma_alignment else 0.5
        }
        
        # Weighted risk score
        weights = {
            'volatility': 0.3,
            'volume_anomaly': 0.2,
            'rsi_extreme': 0.2,
            'bollinger_extreme': 0.15,
            'trend_uncertainty': 0.15
        }
        
        composite_risk = sum(
            risk_factors[factor] * weights[factor] 
            for factor in risk_factors
        )
        
        return {
            'composite_risk': composite_risk,
            'risk_factors': risk_factors,
            'risk_level': 'HIGH' if composite_risk > 0.7 else 'MEDIUM' if composite_risk > 0.4 else 'LOW',
            'volatility': price_volatility,
            'volume_ratio': volume_ratio
        }
    
    async def _calculate_position_parameters(
        self,
        market_data: MarketData,
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate position sizing and entry/exit parameters"""
        
        current_price = market_data.price
        volatility = risk_analysis['volatility']
        risk_score = risk_analysis['composite_risk']
        
        # Dynamic position sizing based on risk
        base_position_size = self.risk_limits['max_position_size']
        risk_adjusted_size = base_position_size * (1 - risk_score * 0.5)  # Reduce size for higher risk
        
        # Stop loss calculation (volatility-adjusted)
        stop_loss_percent = max(0.02, min(volatility * 2, self.risk_limits['stop_loss_max']))
        
        # Take profit calculation (risk-reward ratio of at least 2:1)
        take_profit_percent = stop_loss_percent * 2.5  # 2.5:1 risk-reward
        
        # Entry price (current price with small buffer for market orders)
        entry_price = current_price
        stop_loss_price = current_price * (1 - stop_loss_percent)
        take_profit_price = current_price * (1 + take_profit_percent)
        
        return {
            'position_size': risk_adjusted_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'take_profit': take_profit_price,
            'stop_loss_percent': stop_loss_percent,
            'take_profit_percent': take_profit_percent,
            'risk_reward_ratio': take_profit_percent / stop_loss_percent
        }
    
    async def _generate_recommendation(
        self,
        market_data: MarketData,
        reasoning_results: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        position_details: Dict[str, Any],
        technical_indicators: TechnicalIndicators
    ) -> TradingRecommendation:
        """Generate final trading recommendation"""
        
        # Aggregate signals from different strategies
        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        total_confidence = 0
        weighted_confidence = 0
        
        reasoning_summary = []
        
        for strategy_name, result_data in reasoning_results.items():
            result = result_data['result']
            weight = result_data['weight']
            
            content = result.content.upper()
            confidence = result.confidence
            
            if 'BUY' in content and 'SELL' not in content:
                buy_signals += weight
            elif 'SELL' in content and 'BUY' not in content:
                sell_signals += weight
            else:
                hold_signals += weight
            
            weighted_confidence += confidence * weight
            reasoning_summary.append(f"{strategy_name}: {result.content[:100]}...")
        
        # Determine signal
        max_signal = max(buy_signals, sell_signals, hold_signals)
        
        if max_signal == buy_signals and buy_signals > 0.4:
            if buy_signals > 0.7:
                signal = TradingSignal.STRONG_BUY
            else:
                signal = TradingSignal.BUY
        elif max_signal == sell_signals and sell_signals > 0.4:
            if sell_signals > 0.7:
                signal = TradingSignal.STRONG_SELL
            else:
                signal = TradingSignal.SELL
        else:
            signal = TradingSignal.HOLD
        
        # Adjust for risk - reduce signal strength if high risk
        if risk_analysis['composite_risk'] > 0.7 and signal in [TradingSignal.STRONG_BUY, TradingSignal.STRONG_SELL]:
            signal = TradingSignal.BUY if signal == TradingSignal.STRONG_BUY else TradingSignal.SELL
        
        # Determine market condition
        if technical_indicators.momentum > 0.05 and technical_indicators.rsi < 70:
            market_condition = MarketCondition.BULLISH
        elif technical_indicators.momentum < -0.05 and technical_indicators.rsi > 30:
            market_condition = MarketCondition.BEARISH
        elif risk_analysis['volatility'] > 0.05:
            market_condition = MarketCondition.VOLATILE
        else:
            market_condition = MarketCondition.NEUTRAL
        
        # Time horizon based on technical setup
        if technical_indicators.rsi in range(40, 60) and abs(technical_indicators.momentum) < 0.02:
            time_horizon = "long_term"
        elif abs(technical_indicators.momentum) > 0.05:
            time_horizon = "short_term"
        else:
            time_horizon = "medium_term"
        
        return TradingRecommendation(
            symbol=market_data.symbol,
            signal=signal,
            confidence=weighted_confidence,
            reasoning="; ".join(reasoning_summary),
            entry_price=position_details['entry_price'],
            stop_loss=position_details['stop_loss'],
            take_profit=position_details['take_profit'],
            position_size=position_details['position_size'],
            risk_score=risk_analysis['composite_risk'],
            time_horizon=time_horizon,
            market_condition=market_condition,
            technical_analysis={
                'rsi': technical_indicators.rsi,
                'macd': technical_indicators.macd,
                'momentum': technical_indicators.momentum,
                'trend_alignment': technical_indicators.sma_20 > technical_indicators.sma_50 > technical_indicators.sma_200
            },
            fundamental_factors=[
                f"Price change 24h: {market_data.change_percent:.2f}%",
                f"Volume ratio: {risk_analysis['volume_ratio']:.2f}",
                f"Risk level: {risk_analysis['risk_level']}"
            ]
        )
    
    async def backtest_strategy(
        self,
        historical_data: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Backtest the trading strategy on historical data"""
        
        trades = []
        portfolio_value = 100000  # Start with $100k
        initial_value = portfolio_value
        
        for data_point in historical_data:
            if start_date <= data_point['timestamp'] <= end_date:
                # Convert to our data structures
                market_data = MarketData(**data_point['market_data'])
                technical_indicators = TechnicalIndicators(**data_point['technical_indicators'])
                
                # Generate recommendation
                recommendation = await self.analyze_market_opportunity(
                    market_data, technical_indicators
                )
                
                # Simulate trade execution
                if recommendation.signal in [TradingSignal.BUY, TradingSignal.STRONG_BUY]:
                    trade_value = portfolio_value * recommendation.position_size
                    shares = trade_value / recommendation.entry_price
                    
                    trades.append({
                        'type': 'BUY',
                        'symbol': recommendation.symbol,
                        'shares': shares,
                        'price': recommendation.entry_price,
                        'timestamp': market_data.timestamp,
                        'confidence': recommendation.confidence,
                        'stop_loss': recommendation.stop_loss,
                        'take_profit': recommendation.take_profit
                    })
        
        # Calculate performance metrics
        final_value = portfolio_value  # Would need to calculate based on trades
        total_return = (final_value - initial_value) / initial_value
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'number_of_trades': len(trades),
            'trades': trades,
            'period': f"{start_date} to {end_date}"
        }

# Global instance
advanced_trading_engine = AdvancedTradingEngine()
