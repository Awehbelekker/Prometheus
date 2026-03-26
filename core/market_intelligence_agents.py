#!/usr/bin/env python3
"""
PROMETHEUS Market Intelligence Agents
======================================
Proactive market scanning and intelligence gathering agents.
Extends existing hierarchical_agent_coordinator.py with specialized intelligence agents.

Features:
- Gap Detection Agent: Identifies price gaps and market inefficiencies
- Opportunity Scanner Agent: Scans for high-probability trading opportunities
- Market Research Agent: Analyzes market conditions and provides intelligence
- Integration with existing agent coordinator
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Import existing systems
from core.real_time_market_data import RealTimeMarketDataOrchestrator, MarketDataPoint
from core.hierarchical_agent_coordinator import (
    BaseAgent,
    TradingDecision,
    AgentType,
    AgentPerformance
)

logger = logging.getLogger(__name__)


class OpportunityType(Enum):
    """Types of trading opportunities"""
    BREAKOUT = "breakout"
    MOMENTUM = "momentum"
    REVERSAL = "reversal"
    VOLUME_SPIKE = "volume_spike"
    SUPPORT_RESISTANCE = "support_resistance"
    GAP = "gap"
    ARBITRAGE = "arbitrage"


@dataclass
class MarketGap:
    """Detected market gap"""
    symbol: str
    gap_percent: float
    direction: str  # 'up' or 'down'
    current_price: float
    previous_close: float
    opportunity_score: float
    timestamp: datetime
    reasoning: str


@dataclass
class TradingOpportunity:
    """Trading opportunity detected by scanners"""
    opportunity_id: str
    symbol: str
    opportunity_type: OpportunityType
    score: float
    confidence: float
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasoning: str
    technical_indicators: Dict[str, Any]
    timestamp: datetime
    timeframe: str


@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence"""
    intelligence_id: str
    timestamp: datetime
    market_regime: str
    volatility_level: float
    sentiment_score: float
    correlation_matrix: Dict[str, Dict[str, float]]
    volume_analysis: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]


class GapDetectionAgent(BaseAgent):
    """
    Detects market gaps and inefficiencies
    """
    
    def __init__(self, agent_id: str = "gap_detector"):
        super().__init__(agent_id, AgentType.TECHNICAL)
        self.gap_threshold = 0.02  # 2% gap threshold
        self.market_data = RealTimeMarketDataOrchestrator()
        self.detected_gaps = []
        
        logger.info(f"🔍 Gap Detection Agent initialized: {agent_id}")
    
    async def scan_for_gaps(
        self,
        symbols: List[str]
    ) -> List[MarketGap]:
        """
        Scan multiple symbols for price gaps
        
        Args:
            symbols: List of symbols to scan
        
        Returns:
            List of detected gaps
        """
        gaps = []
        
        for symbol in symbols:
            try:
                # Get current and previous close
                current_data = await self.market_data.get_live_stock_data(symbol)
                
                if current_data:
                    # Calculate gap (simplified - in production would use actual previous close)
                    # For now, use a simple heuristic
                    gap_percent = current_data.change_percent / 100
                    
                    if abs(gap_percent) > self.gap_threshold:
                        gap = MarketGap(
                            symbol=symbol,
                            gap_percent=gap_percent,
                            direction='up' if gap_percent > 0 else 'down',
                            current_price=current_data.price,
                            previous_close=current_data.price / (1 + gap_percent),
                            opportunity_score=self._calculate_opportunity_score(gap_percent),
                            timestamp=datetime.now(),
                            reasoning=f"Price gap of {gap_percent:.2%} detected"
                        )
                        gaps.append(gap)
                        logger.info(f"🔍 Gap detected: {symbol} {gap_percent:.2%}")
                        
            except Exception as e:
                logger.debug(f"Error scanning {symbol} for gaps: {e}")
        
        self.detected_gaps = gaps
        return gaps
    
    def _calculate_opportunity_score(self, gap_percent: float) -> float:
        """Calculate opportunity score based on gap size"""
        # Larger gaps = higher opportunity score, but cap at 1.0
        score = min(abs(gap_percent) / 0.10, 1.0)  # 10% gap = max score
        return score
    
    async def analyze(self, market_data: Dict[str, Any]) -> TradingDecision:
        """Analyze market data for gap opportunities"""
        symbol = market_data.get('symbol', 'UNKNOWN')
        
        # Scan for gaps
        gaps = await self.scan_for_gaps([symbol])
        
        if gaps:
            gap = gaps[0]
            return TradingDecision(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                symbol=symbol,
                action="buy" if gap.direction == "up" else "sell",
                quantity=100,
                price=gap.current_price,
                confidence=gap.opportunity_score,
                reasoning=gap.reasoning,
                risk_score=0.3,
                expected_return=abs(gap.gap_percent),
                timeframe="intraday"
            )
        
        return TradingDecision(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            symbol=symbol,
            action="hold",
            quantity=0,
            price=None,
            confidence=0.2,
            reasoning="No significant gaps detected",
            risk_score=0.0,
            expected_return=0.0,
            timeframe="none"
        )


class OpportunityScannerAgent(BaseAgent):
    """
    Scans for high-probability trading opportunities
    """
    
    def __init__(self, agent_id: str = "opportunity_scanner"):
        super().__init__(agent_id, AgentType.TECHNICAL)
        self.market_data = RealTimeMarketDataOrchestrator()
        self.opportunities = []
        
        logger.info(f"🎯 Opportunity Scanner Agent initialized: {agent_id}")
    
    async def scan_all_opportunities(
        self,
        symbols: List[str]
    ) -> List[TradingOpportunity]:
        """
        Run all scanners and aggregate opportunities
        
        Args:
            symbols: List of symbols to scan
        
        Returns:
            List of trading opportunities
        """
        all_opportunities = []
        
        for symbol in symbols:
            try:
                # Get market data
                market_data = await self.market_data.get_live_stock_data(symbol)
                
                if market_data:
                    # Run different scanners
                    breakout_opp = await self._scan_breakout(symbol, market_data)
                    momentum_opp = await self._scan_momentum(symbol, market_data)
                    volume_opp = await self._scan_volume_spike(symbol, market_data)
                    
                    # Collect opportunities
                    for opp in [breakout_opp, momentum_opp, volume_opp]:
                        if opp and opp.score > 0.5:
                            all_opportunities.append(opp)
                            
            except Exception as e:
                logger.debug(f"Error scanning {symbol}: {e}")
        
        # Rank opportunities by score
        all_opportunities.sort(key=lambda x: x.score, reverse=True)
        
        self.opportunities = all_opportunities
        return all_opportunities
    
    async def _scan_breakout(
        self,
        symbol: str,
        market_data: MarketDataPoint
    ) -> Optional[TradingOpportunity]:
        """Scan for breakout opportunities"""
        # Simplified breakout detection
        # In production, would use historical price levels
        
        price_change = abs(market_data.change_percent)
        
        if price_change > 3.0:  # 3% move
            return TradingOpportunity(
                opportunity_id=f"{symbol}_breakout_{datetime.now().timestamp()}",
                symbol=symbol,
                opportunity_type=OpportunityType.BREAKOUT,
                score=min(price_change / 5.0, 1.0),
                confidence=0.7,
                entry_price=market_data.price,
                target_price=market_data.price * 1.05,
                stop_loss=market_data.price * 0.98,
                reasoning=f"Breakout detected with {price_change:.1f}% move",
                technical_indicators={'price_change': price_change},
                timestamp=datetime.now(),
                timeframe="intraday"
            )
        
        return None
    
    async def _scan_momentum(
        self,
        symbol: str,
        market_data: MarketDataPoint
    ) -> Optional[TradingOpportunity]:
        """Scan for momentum opportunities"""
        # Simplified momentum detection
        
        if market_data.change_percent > 2.0:
            return TradingOpportunity(
                opportunity_id=f"{symbol}_momentum_{datetime.now().timestamp()}",
                symbol=symbol,
                opportunity_type=OpportunityType.MOMENTUM,
                score=min(market_data.change_percent / 4.0, 1.0),
                confidence=0.65,
                entry_price=market_data.price,
                target_price=market_data.price * 1.03,
                stop_loss=market_data.price * 0.99,
                reasoning=f"Positive momentum: {market_data.change_percent:.1f}%",
                technical_indicators={'momentum': market_data.change_percent},
                timestamp=datetime.now(),
                timeframe="intraday"
            )
        
        return None
    
    async def _scan_volume_spike(
        self,
        symbol: str,
        market_data: MarketDataPoint
    ) -> Optional[TradingOpportunity]:
        """Scan for volume spike opportunities"""
        # Simplified volume spike detection
        # In production, would compare to average volume
        
        if market_data.volume > 1000000:  # Arbitrary threshold
            return TradingOpportunity(
                opportunity_id=f"{symbol}_volume_{datetime.now().timestamp()}",
                symbol=symbol,
                opportunity_type=OpportunityType.VOLUME_SPIKE,
                score=0.6,
                confidence=0.6,
                entry_price=market_data.price,
                target_price=market_data.price * 1.02,
                stop_loss=market_data.price * 0.99,
                reasoning=f"Volume spike detected: {market_data.volume:,}",
                technical_indicators={'volume': market_data.volume},
                timestamp=datetime.now(),
                timeframe="intraday"
            )
        
        return None
    
    async def analyze(self, market_data: Dict[str, Any]) -> TradingDecision:
        """Analyze market data for opportunities"""
        symbol = market_data.get('symbol', 'UNKNOWN')
        
        # Scan for opportunities
        opportunities = await self.scan_all_opportunities([symbol])
        
        if opportunities:
            opp = opportunities[0]  # Best opportunity
            return TradingDecision(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                symbol=symbol,
                action="buy",
                quantity=100,
                price=opp.entry_price,
                confidence=opp.confidence,
                reasoning=opp.reasoning,
                risk_score=0.4,
                expected_return=0.03,
                timeframe=opp.timeframe
            )
        
        return TradingDecision(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            symbol=symbol,
            action="hold",
            quantity=0,
            price=None,
            confidence=0.2,
            reasoning="No high-probability opportunities detected",
            risk_score=0.0,
            expected_return=0.0,
            timeframe="none"
        )


class MarketResearchAgent(BaseAgent):
    """
    Analyzes market conditions and provides intelligence
    """

    def __init__(self, agent_id: str = "market_researcher"):
        super().__init__(agent_id, AgentType.SUPERVISOR)
        self.market_data = RealTimeMarketDataOrchestrator()
        self.intelligence_reports = []

        logger.info(f"📊 Market Research Agent initialized: {agent_id}")

    async def generate_market_intelligence(
        self,
        symbols: List[str]
    ) -> MarketIntelligence:
        """
        Generate comprehensive market intelligence report

        Args:
            symbols: List of symbols to analyze

        Returns:
            Market intelligence report
        """
        logger.info(f"📊 Generating market intelligence for {len(symbols)} symbols...")

        # Collect market data
        market_data_points = []
        for symbol in symbols:
            data = await self.market_data.get_live_stock_data(symbol)
            if data:
                market_data_points.append((symbol, data))

        # Analyze market regime
        market_regime = await self._detect_market_regime(market_data_points)

        # Calculate volatility
        volatility = await self._calculate_market_volatility(market_data_points)

        # Analyze sentiment
        sentiment = await self._analyze_market_sentiment(market_data_points)

        # Volume analysis
        volume_analysis = await self._analyze_volume(market_data_points)

        # Trend analysis
        trend_analysis = await self._analyze_trends(market_data_points)

        # Generate insights
        insights = await self._generate_insights(
            market_regime,
            volatility,
            sentiment,
            volume_analysis,
            trend_analysis
        )

        # Generate recommendations
        recommendations = await self._generate_recommendations(insights)

        intelligence = MarketIntelligence(
            intelligence_id=f"intel_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            market_regime=market_regime,
            volatility_level=volatility,
            sentiment_score=sentiment,
            correlation_matrix={},  # Simplified
            volume_analysis=volume_analysis,
            trend_analysis=trend_analysis,
            insights=insights,
            recommendations=recommendations
        )

        self.intelligence_reports.append(intelligence)

        logger.info(f"[CHECK] Market intelligence generated: {market_regime} regime")

        return intelligence

    async def _detect_market_regime(
        self,
        market_data: List[Tuple[str, MarketDataPoint]]
    ) -> str:
        """Detect current market regime"""
        if not market_data:
            return "UNKNOWN"

        # Calculate average change
        avg_change = np.mean([data.change_percent for _, data in market_data])

        # Calculate volatility
        volatility = np.std([data.change_percent for _, data in market_data])

        # Determine regime
        if volatility > 3.0:
            return "HIGH_VOLATILITY"
        elif avg_change > 1.0:
            return "TRENDING_BULL"
        elif avg_change < -1.0:
            return "TRENDING_BEAR"
        else:
            return "SIDEWAYS"

    async def _calculate_market_volatility(
        self,
        market_data: List[Tuple[str, MarketDataPoint]]
    ) -> float:
        """Calculate overall market volatility"""
        if not market_data:
            return 0.0

        changes = [abs(data.change_percent) for _, data in market_data]
        return float(np.mean(changes))

    async def _analyze_market_sentiment(
        self,
        market_data: List[Tuple[str, MarketDataPoint]]
    ) -> float:
        """Analyze market sentiment (-1 to 1)"""
        if not market_data:
            return 0.0

        # Count positive vs negative movers
        positive = sum(1 for _, data in market_data if data.change_percent > 0)
        total = len(market_data)

        # Sentiment score: -1 (bearish) to 1 (bullish)
        sentiment = (positive / total - 0.5) * 2

        return float(sentiment)

    async def _analyze_volume(
        self,
        market_data: List[Tuple[str, MarketDataPoint]]
    ) -> Dict[str, Any]:
        """Analyze volume patterns"""
        if not market_data:
            return {}

        volumes = [data.volume for _, data in market_data]

        return {
            'average_volume': float(np.mean(volumes)),
            'total_volume': float(np.sum(volumes)),
            'high_volume_count': sum(1 for v in volumes if v > np.mean(volumes) * 1.5)
        }

    async def _analyze_trends(
        self,
        market_data: List[Tuple[str, MarketDataPoint]]
    ) -> Dict[str, Any]:
        """Analyze market trends"""
        if not market_data:
            return {}

        changes = [data.change_percent for _, data in market_data]

        return {
            'average_change': float(np.mean(changes)),
            'positive_movers': sum(1 for c in changes if c > 0),
            'negative_movers': sum(1 for c in changes if c < 0),
            'strong_movers': sum(1 for c in changes if abs(c) > 2.0)
        }

    async def _generate_insights(
        self,
        market_regime: str,
        volatility: float,
        sentiment: float,
        volume_analysis: Dict[str, Any],
        trend_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable insights"""
        insights = []

        # Market regime insights
        insights.append(f"Market regime: {market_regime}")

        # Volatility insights
        if volatility > 3.0:
            insights.append("High volatility detected - exercise caution")
        elif volatility < 1.0:
            insights.append("Low volatility - potential for breakout")

        # Sentiment insights
        if sentiment > 0.5:
            insights.append("Strong bullish sentiment across market")
        elif sentiment < -0.5:
            insights.append("Strong bearish sentiment across market")
        else:
            insights.append("Mixed market sentiment")

        # Volume insights
        if volume_analysis.get('high_volume_count', 0) > 3:
            insights.append("Multiple stocks showing high volume activity")

        return insights

    async def _generate_recommendations(
        self,
        insights: List[str]
    ) -> List[str]:
        """Generate trading recommendations"""
        recommendations = []

        for insight in insights:
            if "High volatility" in insight:
                recommendations.append("Reduce position sizes and tighten stop losses")
            elif "bullish sentiment" in insight:
                recommendations.append("Consider long positions in strong momentum stocks")
            elif "bearish sentiment" in insight:
                recommendations.append("Consider defensive positions or cash")
            elif "high volume" in insight:
                recommendations.append("Monitor high-volume stocks for breakout opportunities")

        if not recommendations:
            recommendations.append("Maintain current strategy and monitor for changes")

        return recommendations

    async def analyze(self, market_data: Dict[str, Any]) -> TradingDecision:
        """Analyze market data and provide decision"""
        symbol = market_data.get('symbol', 'UNKNOWN')

        # Generate intelligence
        intelligence = await self.generate_market_intelligence([symbol])

        # Make decision based on intelligence
        if intelligence.sentiment_score > 0.3:
            action = "buy"
            confidence = 0.6
            reasoning = f"Bullish market conditions: {intelligence.market_regime}"
        elif intelligence.sentiment_score < -0.3:
            action = "sell"
            confidence = 0.6
            reasoning = f"Bearish market conditions: {intelligence.market_regime}"
        else:
            action = "hold"
            confidence = 0.4
            reasoning = "Neutral market conditions"

        return TradingDecision(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            symbol=symbol,
            action=action,
            quantity=100,
            price=None,
            confidence=confidence,
            reasoning=reasoning,
            risk_score=intelligence.volatility_level / 10.0,
            expected_return=0.02,
            timeframe="swing"
        )


# Global instances
_gap_detection_agent = None
_opportunity_scanner_agent = None
_market_research_agent = None

def get_gap_detection_agent() -> GapDetectionAgent:
    """Get global gap detection agent instance"""
    global _gap_detection_agent
    if _gap_detection_agent is None:
        _gap_detection_agent = GapDetectionAgent()
    return _gap_detection_agent

def get_opportunity_scanner_agent() -> OpportunityScannerAgent:
    """Get global opportunity scanner agent instance"""
    global _opportunity_scanner_agent
    if _opportunity_scanner_agent is None:
        _opportunity_scanner_agent = OpportunityScannerAgent()
    return _opportunity_scanner_agent

def get_market_research_agent() -> MarketResearchAgent:
    """Get global market research agent instance"""
    global _market_research_agent
    if _market_research_agent is None:
        _market_research_agent = MarketResearchAgent()
    return _market_research_agent

