"""
🚀 REAL AI TRADING INTELLIGENCE
Replaces mock GPT-OSS responses with actual AI capabilities
Integrates with Prometheus trading system
"""

import asyncio
import os
import requests
import json
import time
import logging
import re
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import numpy as np
import psutil

logger = logging.getLogger(__name__)

# Global Ollama concurrency limiter — max 1 concurrent inference call
# Prevents CPU saturation from multiple simultaneous LLM generations
_ollama_semaphore = threading.Semaphore(1)
_CPU_OVERLOAD_THRESHOLD = 85.0  # Skip Ollama when CPU% exceeds this

@dataclass
class TradingSignal:
    """Structured trading signal from AI analysis"""
    symbol: str
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-1
    reasoning: str
    risk_level: str  # LOW, MEDIUM, HIGH
    position_size: float  # 0-1
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    time_horizon: str = "1-2 weeks"
    ai_model_used: str = "gpt-oss-real"

class RealGPTOSSTradingIntelligence:
    """
    Real AI Trading Intelligence using GPT-OSS models
    Replaces mock responses with actual AI capabilities
    """
    
    def __init__(self):
        # Use Ollama API (localhost:11434) instead of defunct GPT-OSS ports
        self.ollama_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        self.model_20b = os.getenv("OLLAMA_TRADING_MODEL", "llama3.1:8b-trading")
        self.model_120b = os.getenv("OLLAMA_LARGE_MODEL", "deepseek-r1:8b")
        self.model_selection_threshold = 0.7
        self.cache = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "model_usage": {"20b": 0, "120b": 0}
        }
        
        logger.info(f"🧠 Real AI Trading Intelligence initialized (Ollama @ {self.ollama_url})")
    
    async def analyze_market_opportunity(self, market_data: Dict[str, Any]) -> TradingSignal:
        """Analyze market opportunity using real AI"""
        start_time = time.time()
        
        try:
            # Determine model based on complexity
            complexity_score = self._calculate_complexity(market_data)
            model = self.model_120b if complexity_score > self.model_selection_threshold else self.model_20b
            model_name = "120b" if complexity_score > self.model_selection_threshold else "20b"
            
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(market_data)
            
            logger.info(f"🧠 Analyzing with Ollama {model} (complexity: {complexity_score:.2f})")
            
            # Make AI request via Ollama
            response = await self._make_ai_request(model, prompt, model_name)
            
            # Parse AI response
            trading_signal = self._parse_ai_response(response, market_data)
            
            # Update metrics
            self._update_metrics(time.time() - start_time, True, model_name)
            
            logger.info(f"[CHECK] AI analysis complete: {trading_signal.signal} (confidence: {trading_signal.confidence:.2f})")
            return trading_signal
            
        except Exception as e:
            logger.error(f"[ERROR] AI analysis failed: {e}")
            self._update_metrics(time.time() - start_time, False, "fallback")
            return self._fallback_analysis(market_data)
    
    def _calculate_complexity(self, market_data: Dict[str, Any]) -> float:
        """Calculate task complexity to select appropriate model"""
        complexity_factors = [
            len(market_data.get("symbols", [])),
            len(market_data.get("indicators", [])),
            market_data.get("volatility", 0),
            len(market_data.get("news_sentiment", [])),
            len(market_data.get("options_chain", [])),
            market_data.get("market_regime_complexity", 0)
        ]
        return min(sum(complexity_factors) / 10, 1.0)
    
    def _create_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt"""
        symbol = market_data.get("symbol", "UNKNOWN")
        current_price = market_data.get("current_price", 0)
        volume = market_data.get("volume", 0)
        rsi = market_data.get("rsi", 50)
        macd = market_data.get("macd", 0)
        volatility = market_data.get("volatility", 0)
        
        prompt = f"""
        Perform comprehensive trading analysis for {symbol}:
        
        Current Market Data:
        - Symbol: {symbol}
        - Current Price: ${current_price:.2f}
        - Volume: {volume:,} shares
        - RSI: {rsi}
        - MACD: {macd}
        - Volatility: {volatility:.2%}
        
        Additional Context:
        - Market Regime: {market_data.get('market_regime', 'Normal')}
        - Sector: {market_data.get('sector', 'Unknown')}
        - Market Cap: {market_data.get('market_cap', 'Unknown')}
        - News Sentiment: {market_data.get('news_sentiment', 'Neutral')}
        
        Analysis Requirements:
        1. Technical Analysis: RSI, MACD, support/resistance levels
        2. Fundamental Analysis: Company health, sector trends
        3. Risk Assessment: Volatility, market conditions
        4. Position Sizing: Optimal position size based on risk
        5. Entry/Exit Strategy: Specific price levels and timing
        
        Provide structured response with:
        - Trading Signal: BUY/SELL/HOLD
        - Confidence Level: 0.0-1.0
        - Risk Level: LOW/MEDIUM/HIGH
        - Position Size: 0.0-1.0 (percentage of portfolio)
        - Entry Price: Specific price level
        - Stop Loss: Risk management level
        - Take Profit: Profit target level
        - Reasoning: Detailed explanation
        - Time Horizon: Expected holding period
        
        Format as JSON for easy parsing.
        """
        
        return prompt
    
    async def _make_ai_request(self, model: str, prompt: str, model_name: str) -> Dict[str, Any]:
        """Make request to Ollama API at localhost:11434 with concurrency control"""
        # CPU guard: skip Ollama when system is overloaded
        cpu_pct = psutil.cpu_percent(interval=0)
        if cpu_pct > _CPU_OVERLOAD_THRESHOLD:
            logger.debug(f"CPU overloaded ({cpu_pct:.0f}%), skipping Ollama call for {model_name}")
            raise Exception(f"CPU overloaded ({cpu_pct:.0f}%), skipping LLM inference")

        acquired = _ollama_semaphore.acquire(timeout=5)
        if not acquired:
            logger.debug("Ollama semaphore busy, skipping concurrent call")
            raise Exception("Ollama concurrency limit reached")
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 400 if model_name == "20b" else 600,
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=60
            ))
            
            if response.status_code == 200:
                data = response.json()
                return {"generated_text": data.get("response", ""), "model_name": model}
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"[ERROR] AI request failed: {e}")
            raise
        finally:
            _ollama_semaphore.release()
    
    def _parse_ai_response(self, response: Dict[str, Any], market_data: Dict[str, Any]) -> TradingSignal:
        """Parse AI response into structured trading signal"""
        try:
            generated_text = response.get("generated_text", "")
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            
            if json_match:
                try:
                    ai_data = json.loads(json_match.group())
                    return TradingSignal(
                        symbol=market_data.get("symbol", "UNKNOWN"),
                        signal=ai_data.get("signal", "HOLD"),
                        confidence=float(ai_data.get("confidence", 0.5)),
                        reasoning=ai_data.get("reasoning", generated_text[:200]),
                        risk_level=ai_data.get("risk_level", "MEDIUM"),
                        position_size=float(ai_data.get("position_size", 0.05)),
                        entry_price=float(ai_data.get("entry_price", market_data.get("current_price", 0))),
                        stop_loss=ai_data.get("stop_loss"),
                        take_profit=ai_data.get("take_profit"),
                        time_horizon=ai_data.get("time_horizon", "1-2 weeks"),
                        ai_model_used=response.get("model_name", "gpt-oss-real")
                    )
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"[WARNING]️ JSON parsing failed: {e}")
            
            # Fallback: extract key information from text
            return self._extract_key_info(generated_text, market_data)
            
        except Exception as e:
            logger.error(f"[ERROR] Response parsing failed: {e}")
            return self._fallback_analysis(market_data)
    
    def _extract_key_info(self, text: str, market_data: Dict[str, Any]) -> TradingSignal:
        """Extract key information from unstructured response"""
        # Simple keyword extraction
        signal = "HOLD"
        confidence = 0.5
        
        if "BUY" in text.upper() or "BUYING" in text.upper():
            signal = "BUY"
            confidence = 0.7
        elif "SELL" in text.upper() or "SELLING" in text.upper():
            signal = "SELL"
            confidence = 0.7
        
        # Extract confidence from text
        confidence_match = re.search(r'confidence[:\s]*([0-9.]+)', text, re.IGNORECASE)
        if confidence_match:
            confidence = float(confidence_match.group(1))
        
        return TradingSignal(
            symbol=market_data.get("symbol", "UNKNOWN"),
            signal=signal,
            confidence=confidence,
            reasoning=text[:200],
            risk_level="MEDIUM",
            position_size=0.05,
            entry_price=market_data.get("current_price", 0),
            ai_model_used="gpt-oss-real-extracted"
        )
    
    def _fallback_analysis(self, market_data: Dict[str, Any]) -> TradingSignal:
        """Fallback analysis when AI fails"""
        symbol = market_data.get("symbol", "UNKNOWN")
        current_price = market_data.get("current_price", 0)
        rsi = market_data.get("rsi", 50)
        
        # Simple technical analysis fallback
        if rsi > 70:
            signal = "SELL"
            confidence = 0.6
        elif rsi < 30:
            signal = "BUY"
            confidence = 0.6
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Fallback analysis: RSI={rsi}, Price=${current_price}",
            risk_level="MEDIUM",
            position_size=0.05,
            entry_price=current_price,
            ai_model_used="fallback-technical"
        )
    
    def _update_metrics(self, response_time: float, success: bool, model_name: str):
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1
        if success:
            self.performance_metrics["successful_requests"] += 1
            self.performance_metrics["model_usage"][model_name] += 1
        
        # Update average response time
        total = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (current_avg * (total - 1) + response_time) / total
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = self.performance_metrics.copy()
        if metrics["total_requests"] > 0:
            metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"]
        else:
            metrics["success_rate"] = 0
        return metrics
    
    async def test_ai_capabilities(self) -> Dict[str, Any]:
        """Test AI capabilities with sample data"""
        test_data = {
            "symbol": "AAPL",
            "current_price": 150.0,
            "volume": 50000000,
            "rsi": 65,
            "macd": 0.5,
            "volatility": 0.25,
            "market_regime": "Bullish",
            "sector": "Technology"
        }
        
        try:
            signal = await self.analyze_market_opportunity(test_data)
            return {
                "test_data": test_data,
                "ai_signal": signal,
                "performance_metrics": self.get_performance_metrics(),
                "status": "success"
            }
        except Exception as e:
            return {
                "test_data": test_data,
                "error": str(e),
                "status": "failed"
            }

# Global instance
real_ai_intelligence = RealGPTOSSTradingIntelligence()
