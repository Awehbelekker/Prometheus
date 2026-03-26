"""
🚀 PROMETHEUS TRADING - AI-Powered Trading Intelligence
======================================================
Advanced AI integration using OpenAI GPT-4 for market analysis,
trading signals, risk assessment, and portfolio optimization.

Features:
- Real-time market sentiment analysis
- AI-powered trading signal generation
- Risk assessment and portfolio optimization
- News sentiment analysis and impact prediction
- Technical analysis with AI interpretation
- Market trend prediction and forecasting
"""

import asyncio
import aiohttp
import logging
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
from decimal import Decimal
from core.utils.time_utils import utc_now
from dotenv import load_dotenv

# Import local GPT-OSS adapter
try:
    from .local_gpt_oss_adapter import get_local_gpt_oss_adapter
    GPT_OSS_AVAILABLE = True
except ImportError:
    GPT_OSS_AVAILABLE = False

# Import real GPT-OSS integration
try:
    from .real_ai_trading_intelligence import RealGPTOSSTradingIntelligence
    REAL_GPT_OSS_AVAILABLE = True
except ImportError:
    REAL_GPT_OSS_AVAILABLE = False

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class AITradingSignal:
    """AI-generated trading signal with confidence and reasoning"""
    symbol: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 to 1.0
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str = ""
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    time_horizon: str = "SHORT"  # SHORT, MEDIUM, LONG
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = utc_now()

@dataclass
class MarketSentiment:
    """Market sentiment analysis result"""
    symbol: str
    sentiment_score: float  # -1.0 (very bearish) to 1.0 (very bullish)
    sentiment_label: str  # VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH
    news_impact: float  # 0.0 to 1.0
    social_sentiment: float  # -1.0 to 1.0
    technical_sentiment: float  # -1.0 to 1.0
    overall_confidence: float  # 0.0 to 1.0
    key_factors: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = utc_now()

class OpenAITradingIntelligence:
    """
    🎯 OpenAI-Powered Trading Intelligence Engine
    Advanced AI analysis for trading decisions and market insights
    Now enhanced with Real GPT-OSS capabilities
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        self.base_url = "https://api.openai.com/v1"
        
        # Initialize Real GPT-OSS if available
        if REAL_GPT_OSS_AVAILABLE:
            self.real_gpt_oss = RealGPTOSSTradingIntelligence()
            logger.info("[CHECK] Real GPT-OSS Trading Intelligence initialized")
        else:
            self.real_gpt_oss = None
            logger.warning("[WARNING]️ Real GPT-OSS not available, using fallback")
        
        if self.api_key:
            logger.info("[CHECK] OpenAI Trading Intelligence initialized")
        else:
            logger.warning("[WARNING]️ OpenAI API key not found")
    
    async def analyze_market_data(self, symbol: str, market_data: Dict[str, Any],
                                 news_data: List[str] = None) -> AITradingSignal:
        """
        Generate AI-powered trading signal based on market data and news
        Now enhanced with Real GPT-OSS capabilities
        """
        try:
            # Try Real GPT-OSS first (highest priority)
            if self.real_gpt_oss:
                try:
                    logger.info(f"🧠 Using Real GPT-OSS for {symbol} analysis")
                    trading_signal = await self.real_gpt_oss.analyze_market_opportunity(market_data)
                    
                    # Convert to AITradingSignal format
                    return AITradingSignal(
                        symbol=trading_signal.symbol,
                        signal=trading_signal.signal,
                        confidence=trading_signal.confidence,
                        target_price=trading_signal.take_profit,
                        stop_loss=trading_signal.stop_loss,
                        reasoning=trading_signal.reasoning,
                        risk_level=trading_signal.risk_level,
                        time_horizon=trading_signal.time_horizon
                    )
                except Exception as e:
                    logger.warning(f"[WARNING]️ Real GPT-OSS failed, trying fallback: {e}")
            
            # Try GPT-OSS local models second
            if GPT_OSS_AVAILABLE:
                try:
                    gpt_oss_adapter = await get_local_gpt_oss_adapter()
                    gpt_oss_result = await gpt_oss_adapter.generate_trading_signal(symbol, market_data)
                    if gpt_oss_result and gpt_oss_result.get('confidence', 0) > 0.7:
                        return AITradingSignal(
                            symbol=symbol,
                            signal=gpt_oss_result.get('action', 'HOLD'),
                            confidence=gpt_oss_result.get('confidence', 0.5),
                            reasoning=gpt_oss_result.get('reasoning', 'GPT-OSS local analysis'),
                            target_price=gpt_oss_result.get('target_price'),
                            stop_loss=gpt_oss_result.get('stop_loss')
                        )
                except Exception as e:
                    logger.warning(f"GPT-OSS local model failed for {symbol}: {e}")

            if not self.api_key:
                return self._generate_fallback_signal(symbol, market_data)
            
            # Prepare market context
            context = self._prepare_market_context(symbol, market_data, news_data)
            
            # Generate AI analysis
            prompt = self._create_trading_analysis_prompt(context)
            response = await self._call_openai_api(prompt)
            
            # Parse AI response into trading signal
            signal = self._parse_trading_signal(symbol, response)
            
            logger.info(f"[CHECK] AI signal generated for {symbol}: {signal.signal} (confidence: {signal.confidence:.2f})")
            signal = self._apply_macro_overlay(signal)
            return signal
            
        except Exception as e:
            logger.error(f"[ERROR] AI analysis error for {symbol}: {e}")
            return self._generate_fallback_signal(symbol, market_data)
    
    async def analyze_market_sentiment(self, symbol: str, news_headlines: List[str],
                                     market_data: Dict[str, Any]) -> MarketSentiment:
        """
        Analyze market sentiment using AI-powered news and data analysis
        """
        try:
            if not self.api_key:
                return self._generate_fallback_sentiment(symbol)
            
            # Prepare sentiment analysis context
            context = {
                'symbol': symbol,
                'news_headlines': news_headlines[:10],  # Limit to recent news
                'price_data': market_data,
                'analysis_type': 'sentiment'
            }
            
            prompt = self._create_sentiment_analysis_prompt(context)
            response = await self._call_openai_api(prompt)
            
            # Parse sentiment analysis
            sentiment = self._parse_sentiment_analysis(symbol, response)
            
            logger.info(f"[CHECK] Sentiment analysis for {symbol}: {sentiment.sentiment_label} ({sentiment.sentiment_score:.2f})")
            return sentiment
            
        except Exception as e:
            logger.error(f"[ERROR] Sentiment analysis error for {symbol}: {e}")
            return self._generate_fallback_sentiment(symbol)
    
    async def generate_portfolio_recommendations(self, portfolio_data: Dict[str, Any],
                                               market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered portfolio optimization recommendations
        """
        try:
            if not self.api_key:
                return self._generate_fallback_portfolio_rec()
            
            context = {
                'portfolio': portfolio_data,
                'market_conditions': market_conditions,
                'analysis_type': 'portfolio_optimization'
            }
            
            prompt = self._create_portfolio_analysis_prompt(context)
            response = await self._call_openai_api(prompt)
            
            recommendations = self._parse_portfolio_recommendations(response)
            
            logger.info("[CHECK] Portfolio recommendations generated")
            return recommendations
            
        except Exception as e:
            logger.error(f"[ERROR] Portfolio analysis error: {e}")
            return self._generate_fallback_portfolio_rec()
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Make API call to OpenAI"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert financial analyst and trading advisor with deep knowledge of markets, technical analysis, and risk management.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': self.max_tokens,
            'temperature': 0.3  # Lower temperature for more consistent analysis
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/chat/completions", 
                                  headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
    
    def _prepare_market_context(self, symbol: str, market_data: Dict[str, Any], 
                               news_data: List[str] = None) -> Dict[str, Any]:
        """Prepare market context for AI analysis"""
        return {
            'symbol': symbol,
            'current_price': market_data.get('price', 0),
            'change_percent': market_data.get('change_percent', 0),
            'volume': market_data.get('volume', 0),
            'high_52w': market_data.get('high_52w', 0),
            'low_52w': market_data.get('low_52w', 0),
            'market_cap': market_data.get('market_cap', 0),
            'pe_ratio': market_data.get('pe_ratio', 0),
            'news_headlines': news_data[:5] if news_data else [],
            'timestamp': market_data.get('timestamp', utc_now().isoformat())
        }
    
    def _create_trading_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for trading signal analysis"""
        return f"""
        Analyze the following market data for {context['symbol']} and provide a trading recommendation:

        Current Market Data:
        - Price: ${context['current_price']:.2f}
        - Change: {context['change_percent']:.2f}%
        - Volume: {context['volume']:,}
        - 52W High: ${context['high_52w']:.2f}
        - 52W Low: ${context['low_52w']:.2f}
        - P/E Ratio: {context['pe_ratio']:.2f}
        - Market Cap: ${context['market_cap']:,}

        Recent News Headlines:
        {chr(10).join(context['news_headlines']) if context['news_headlines'] else 'No recent news available'}

        Please provide your analysis in the following JSON format:
        {{
            "signal": "BUY|SELL|HOLD",
            "confidence": 0.85,
            "target_price": 150.00,
            "stop_loss": 140.00,
            "reasoning": "Detailed explanation of the recommendation",
            "risk_level": "LOW|MEDIUM|HIGH",
            "time_horizon": "SHORT|MEDIUM|LONG"
        }}

        Consider technical indicators, fundamental analysis, market sentiment, and risk factors.
        """
    
    def _create_sentiment_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for sentiment analysis"""
        return f"""
        Analyze market sentiment for {context['symbol']} based on the following data:

        News Headlines:
        {chr(10).join(context['news_headlines']) if context['news_headlines'] else 'No news available'}

        Market Data:
        - Current Price: ${context['price_data'].get('price', 0):.2f}
        - Change: {context['price_data'].get('change_percent', 0):.2f}%
        - Volume: {context['price_data'].get('volume', 0):,}

        Provide sentiment analysis in JSON format:
        {{
            "sentiment_score": 0.3,
            "sentiment_label": "BULLISH",
            "news_impact": 0.7,
            "social_sentiment": 0.5,
            "technical_sentiment": 0.2,
            "overall_confidence": 0.8,
            "key_factors": ["Factor 1", "Factor 2", "Factor 3"]
        }}

        Sentiment score: -1.0 (very bearish) to 1.0 (very bullish)
        Labels: VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH
        """
    
    def _create_portfolio_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for portfolio analysis"""
        return f"""
        Analyze the following portfolio and provide optimization recommendations:

        Portfolio Data:
        {json.dumps(context['portfolio'], indent=2)}

        Market Conditions:
        {json.dumps(context['market_conditions'], indent=2)}

        Provide recommendations in JSON format:
        {{
            "overall_risk_score": 0.6,
            "diversification_score": 0.8,
            "recommendations": [
                {{"action": "REDUCE", "symbol": "AAPL", "reason": "Overweight position"}},
                {{"action": "ADD", "symbol": "SPY", "reason": "Increase diversification"}}
            ],
            "risk_adjustments": ["Suggestion 1", "Suggestion 2"],
            "market_outlook": "NEUTRAL"
        }}
        """
    
    def _parse_trading_signal(self, symbol: str, response: str) -> AITradingSignal:
        """Parse AI response into trading signal"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return AITradingSignal(
                    symbol=symbol,
                    signal=data.get('signal', 'HOLD'),
                    confidence=float(data.get('confidence', 0.5)),
                    target_price=data.get('target_price'),
                    stop_loss=data.get('stop_loss'),
                    reasoning=data.get('reasoning', 'AI analysis completed'),
                    risk_level=data.get('risk_level', 'MEDIUM'),
                    time_horizon=data.get('time_horizon', 'SHORT')
                )
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
        
        # Fallback parsing
        return AITradingSignal(
            symbol=symbol,
            signal='HOLD',
            confidence=0.5,
            reasoning='AI analysis completed with fallback parsing'
        )
    
    def _parse_sentiment_analysis(self, symbol: str, response: str) -> MarketSentiment:
        """Parse AI sentiment analysis response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return MarketSentiment(
                    symbol=symbol,
                    sentiment_score=float(data.get('sentiment_score', 0.0)),
                    sentiment_label=data.get('sentiment_label', 'NEUTRAL'),
                    news_impact=float(data.get('news_impact', 0.5)),
                    social_sentiment=float(data.get('social_sentiment', 0.0)),
                    technical_sentiment=float(data.get('technical_sentiment', 0.0)),
                    overall_confidence=float(data.get('overall_confidence', 0.5)),
                    key_factors=data.get('key_factors', [])
                )
        except Exception as e:
            logger.warning(f"Failed to parse sentiment response: {e}")
        
        return self._generate_fallback_sentiment(symbol)
    
    def _parse_portfolio_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse portfolio recommendations"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Failed to parse portfolio response: {e}")
        
        return self._generate_fallback_portfolio_rec()

    def _apply_macro_overlay(self, signal: AITradingSignal) -> AITradingSignal:
        """Apply Fed NLP + ML Regime as confidence adjusters on top of the base signal"""
        try:
            adjustment = 0.0
            reasons = []

            # Fed NLP adjustment
            try:
                from core.fed_nlp_analyzer import FedNLPAnalyzer
                if not hasattr(self, '_fed_analyzer_cached'):
                    self._fed_analyzer_cached = FedNLPAnalyzer()
                fed = self._fed_analyzer_cached
                fed_signal = fed.get_latest_signal()
                if fed_signal and fed_signal.get('tone_score') is not None:
                    tone = fed_signal['tone_score']
                    if signal.signal == 'BUY' and tone > 0.2:
                        adjustment += 0.05  # Dovish + BUY = boost
                        reasons.append(f"Fed dovish boost (+0.05)")
                    elif signal.signal == 'BUY' and tone < -0.3:
                        adjustment -= 0.08  # Hawkish + BUY = drag
                        reasons.append(f"Fed hawkish drag (-0.08)")
                    elif signal.signal == 'SELL' and tone < -0.2:
                        adjustment += 0.05  # Hawkish + SELL = confirms
                        reasons.append(f"Fed hawkish confirms SELL (+0.05)")
            except Exception:
                pass

            # ML Regime adjustment
            try:
                from core.ml_regime_detector import MLRegimeDetector
                regime = MLRegimeDetector()
                result = regime.predict_regime()
                if result and result.get('regime'):
                    r = result['regime']
                    r_conf = result.get('confidence', 0.5)
                    if signal.signal == 'BUY' and r == 'BULL':
                        adjustment += 0.05 * r_conf
                        reasons.append(f"Bull regime boost (+{0.05*r_conf:.3f})")
                    elif signal.signal == 'BUY' and r == 'BEAR':
                        adjustment -= 0.10 * r_conf
                        reasons.append(f"Bear regime drag (-{0.10*r_conf:.3f})")
                    elif signal.signal == 'SELL' and r == 'BEAR':
                        adjustment += 0.05 * r_conf
                        reasons.append(f"Bear regime confirms SELL (+{0.05*r_conf:.3f})")
                    elif signal.signal == 'BUY' and r == 'VOLATILE':
                        adjustment -= 0.05 * r_conf
                        reasons.append(f"Volatile regime caution (-{0.05*r_conf:.3f})")
            except Exception:
                pass

            if adjustment != 0:
                original = signal.confidence
                signal.confidence = max(0.0, min(1.0, signal.confidence + adjustment))
                overlay_detail = '; '.join(reasons)
                signal.reasoning = f"{signal.reasoning} [Macro overlay: {overlay_detail}]"
                logger.info(f"Macro overlay for {signal.symbol}: confidence {original:.2f} -> {signal.confidence:.2f} ({overlay_detail})")

        except Exception as e:
            logger.debug(f"Macro overlay failed: {e}")

        return signal
    
    def _generate_fallback_signal(self, symbol: str, market_data: Dict[str, Any]) -> AITradingSignal:
        """Generate enhanced fallback signal with BUY/SELL logic when AI is unavailable"""
        change_percent = market_data.get('change_percent', 0)
        price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)

        # Enhanced fallback logic with actual BUY/SELL signals
        buy_score = 0
        sell_score = 0

        # Price momentum analysis
        if change_percent > 3:
            buy_score += 3
        elif change_percent > 1:
            buy_score += 2
        elif change_percent > 0.5:
            buy_score += 1
        elif change_percent < -3:
            sell_score += 3
        elif change_percent < -1:
            sell_score += 2
        elif change_percent < -0.5:
            sell_score += 1

        # Volume analysis
        if volume > 1000000:  # High volume adds confidence
            if buy_score > sell_score:
                buy_score += 1
            elif sell_score > buy_score:
                sell_score += 1

        # Price level analysis
        if price > 200:  # High-priced stocks
            buy_score += 1
        elif price < 10:  # Low-priced stocks (more volatile)
            sell_score += 1

        # Determine signal and confidence
        if buy_score > sell_score and buy_score >= 2:
            signal = 'BUY'
            confidence = min(0.8, 0.5 + (buy_score * 0.1))
            reasoning = f'Enhanced fallback BUY: momentum {change_percent:.2f}%, score {buy_score}'
        elif sell_score > buy_score and sell_score >= 2:
            signal = 'SELL'
            confidence = min(0.8, 0.5 + (sell_score * 0.1))
            reasoning = f'Enhanced fallback SELL: momentum {change_percent:.2f}%, score {sell_score}'
        else:
            signal = 'HOLD'
            confidence = 0.5
            reasoning = f'Enhanced fallback HOLD: momentum {change_percent:.2f}%, balanced scores'

        return AITradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            target_price=price * 1.05 if signal == 'BUY' else price * 0.95 if signal == 'SELL' else None,
            stop_loss=price * 0.95 if signal == 'BUY' else price * 1.05 if signal == 'SELL' else None
        )
    
    def _generate_fallback_sentiment(self, symbol: str) -> MarketSentiment:
        """Generate fallback sentiment when AI is unavailable"""
        return MarketSentiment(
            symbol=symbol,
            sentiment_score=0.0,
            sentiment_label='NEUTRAL',
            news_impact=0.5,
            social_sentiment=0.0,
            technical_sentiment=0.0,
            overall_confidence=0.3,
            key_factors=['AI service unavailable']
        )
    
    def _generate_fallback_portfolio_rec(self) -> Dict[str, Any]:
        """Generate fallback portfolio recommendations"""
        return {
            'overall_risk_score': 0.5,
            'diversification_score': 0.5,
            'recommendations': [],
            'risk_adjustments': ['AI service unavailable - using conservative approach'],
            'market_outlook': 'NEUTRAL'
        }
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return bool(self.api_key)
    
    async def generate_trading_signal(self, symbol: str, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate trading signal for a symbol using AI analysis"""
        try:
            # Use the existing analyze_market_data method
            signal = await self.analyze_market_data(symbol, market_data)
            
            if signal and signal.confidence > 0.5:  # Only return signals with decent confidence
                return {
                    'symbol': symbol,
                    'action': signal.action,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'target_price': signal.target_price,
                    'stop_loss': signal.stop_loss,
                    'timestamp': datetime.now()
                }
            return None
            
        except Exception as e:
            logger.error(f"Error generating trading signal for {symbol}: {e}")
            return None

# Global instance
ai_trading_intelligence = OpenAITradingIntelligence()

async def get_ai_trading_signal(symbol: str, market_data: Dict[str, Any], 
                               news_data: List[str] = None) -> AITradingSignal:
    """
    🎯 Main function to get AI-powered trading signal
    """
    return await ai_trading_intelligence.analyze_market_data(symbol, market_data, news_data)

async def get_market_sentiment(symbol: str, news_headlines: List[str],
                              market_data: Dict[str, Any]) -> MarketSentiment:
    """
    🎯 Main function to get AI-powered market sentiment analysis
    """
    return await ai_trading_intelligence.analyze_market_sentiment(symbol, news_headlines, market_data)
