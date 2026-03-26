#!/usr/bin/env python3
"""
🚀 GPT-OSS TRADING ENGINE - MAXIMUM PERFORMANCE
Optimized for local GPT-OSS models with real-time trading decisions
"""

import asyncio
import logging
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GPTOSSTradeSignal:
    """Enhanced trading signal from GPT-OSS AI"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: float = 0.01  # Default 1% position
    risk_score: float = 0.5
    ai_model: str = "gpt_oss_20b"
    response_time: float = 0.0
    timestamp: str = ""

class GPTOSSTradingEngine:
    """High-performance trading engine using local GPT-OSS models"""
    
    def __init__(self):
        self.gpt_oss_20b_endpoint = "http://localhost:5000"
        self.gpt_oss_120b_endpoint = "http://localhost:5001"
        self.decision_count = 0
        self.successful_decisions = 0
        self.total_response_time = 0.0
        self.is_active = True
        
        logger.info("🚀 GPT-OSS Trading Engine initialized")
    
    async def analyze_trading_opportunity(self, symbol: str, market_data: Dict[str, Any]) -> GPTOSSTradeSignal:
        """Analyze trading opportunity using GPT-OSS AI"""
        
        start_time = time.time()
        
        try:
            # Use 120B model for complex analysis
            prompt = self._create_trading_analysis_prompt(symbol, market_data)
            
            # Get AI analysis from GPT-OSS 120B
            ai_response = await self._query_gpt_oss_120b(prompt)
            
            # Parse response into trading signal
            signal = self._parse_trading_response(symbol, ai_response, market_data)
            
            # Update performance metrics
            response_time = time.time() - start_time
            signal.response_time = response_time
            signal.timestamp = datetime.now().isoformat()
            
            self.decision_count += 1
            self.total_response_time += response_time
            
            if signal.confidence > 0.7:
                self.successful_decisions += 1
            
            logger.info(f"🎯 GPT-OSS Trading Signal: {symbol} -> {signal.action} (confidence: {signal.confidence:.2f}, time: {response_time:.2f}s)")
            
            return signal
            
        except Exception as e:
            logger.error(f"[ERROR] GPT-OSS analysis error for {symbol}: {e}")
            return self._create_fallback_signal(symbol, market_data)
    
    def _create_trading_analysis_prompt(self, symbol: str, market_data: Dict[str, Any]) -> str:
        """Create optimized prompt for GPT-OSS trading analysis"""
        
        current_price = market_data.get('price', 0)
        change_percent = market_data.get('change_percent', 0)
        volume = market_data.get('volume', 0)
        
        prompt = f"""PROMETHEUS AI Trading Analysis - LIVE MONEY TRADING

MARKET DATA:
Symbol: {symbol}
Current Price: ${current_price:.2f}
Change: {change_percent:.2f}%
Volume: {volume:,}
Time: {datetime.now().strftime('%H:%M:%S')}

TRADING CONTEXT:
- Live trading with real money ($250 capital)
- Maximum position size: 1% ($2.50)
- Target daily return: 7%
- Conservative risk management active
- Stop loss: 1.5%

ANALYSIS REQUIREMENTS:
Provide immediate trading decision with:
1. ACTION: BUY/SELL/HOLD
2. CONFIDENCE: 0.0-1.0 (minimum 0.8 for live trades)
3. REASONING: Brief technical analysis
4. TARGET: Price target
5. STOP: Stop loss level
6. SIZE: Position size (0.5-1.0% of capital)

CONSTRAINTS:
- Only recommend trades with 80%+ confidence
- Consider current market volatility
- Account for transaction costs
- Prioritize capital preservation

RESPONSE FORMAT:
ACTION: [BUY/SELL/HOLD]
CONFIDENCE: [0.0-1.0]
REASONING: [Brief analysis]
TARGET: [Price level]
STOP: [Stop loss]
SIZE: [Position %]

Analyze and provide immediate trading recommendation:"""

        return prompt
    
    async def _query_gpt_oss_120b(self, prompt: str) -> Dict[str, Any]:
        """Query GPT-OSS 120B model for complex analysis"""
        
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.2,  # Low temperature for consistent trading decisions
                "top_p": 0.9,
                "frequency_penalty": 0.1
            }
            
            response = requests.post(
                f"{self.gpt_oss_120b_endpoint}/generate",
                json=payload,
                timeout=10  # 10 second timeout for real-time trading
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "content": data.get("response", data.get("text", "")),
                    "success": True,
                    "model": "gpt_oss_120b"
                }
            else:
                logger.warning(f"GPT-OSS 120B error: {response.status_code}")
                # Fallback to 20B model
                return await self._query_gpt_oss_20b(prompt)
                
        except Exception as e:
            logger.error(f"GPT-OSS 120B query failed: {e}")
            # Fallback to 20B model
            return await self._query_gpt_oss_20b(prompt)
    
    async def _query_gpt_oss_20b(self, prompt: str) -> Dict[str, Any]:
        """Query GPT-OSS 20B model as fallback"""
        
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": 300,
                "temperature": 0.3,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.gpt_oss_20b_endpoint}/generate",
                json=payload,
                timeout=5  # Faster timeout for 20B model
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "content": data.get("response", data.get("text", "")),
                    "success": True,
                    "model": "gpt_oss_20b"
                }
            else:
                return {"content": "", "success": False, "model": "none"}
                
        except Exception as e:
            logger.error(f"GPT-OSS 20B query failed: {e}")
            return {"content": "", "success": False, "model": "none"}
    
    def _parse_trading_response(self, symbol: str, ai_response: Dict[str, Any], market_data: Dict[str, Any]) -> GPTOSSTradeSignal:
        """Parse GPT-OSS response into trading signal"""
        
        if not ai_response.get("success", False):
            return self._create_fallback_signal(symbol, market_data)
        
        content = ai_response.get("content", "")
        model = ai_response.get("model", "gpt_oss_20b")
        
        # Parse structured response
        action = "HOLD"
        confidence = 0.5
        reasoning = "GPT-OSS analysis completed"
        target_price = None
        stop_loss = None
        position_size = 0.5
        
        # Extract action
        if "ACTION: BUY" in content:
            action = "BUY"
        elif "ACTION: SELL" in content:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Extract confidence
        import re
        confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))
            except:
                pass
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*([^\n]+)', content)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        # Extract target price
        target_match = re.search(r'TARGET:\s*([0-9.]+)', content)
        if target_match:
            try:
                target_price = float(target_match.group(1))
            except:
                pass
        
        # Extract stop loss
        stop_match = re.search(r'STOP:\s*([0-9.]+)', content)
        if stop_match:
            try:
                stop_loss = float(stop_match.group(1))
            except:
                pass
        
        # Extract position size
        size_match = re.search(r'SIZE:\s*([0-9.]+)', content)
        if size_match:
            try:
                position_size = float(size_match.group(1))
                position_size = max(0.1, min(1.0, position_size))  # Clamp to 0.1-1.0%
            except:
                pass
        
        return GPTOSSTradeSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=position_size,
            risk_score=1.0 - confidence,  # Higher confidence = lower risk
            ai_model=model
        )
    
    def _create_fallback_signal(self, symbol: str, market_data: Dict[str, Any]) -> GPTOSSTradeSignal:
        """Create fallback signal when GPT-OSS is unavailable"""
        
        change_percent = market_data.get('change_percent', 0)
        
        # Simple momentum-based fallback
        if change_percent > 2.0:
            action = "BUY"
            confidence = 0.6
            reasoning = "Fallback: Strong positive momentum"
        elif change_percent < -2.0:
            action = "SELL"
            confidence = 0.6
            reasoning = "Fallback: Strong negative momentum"
        else:
            action = "HOLD"
            confidence = 0.4
            reasoning = "Fallback: Neutral conditions"
        
        return GPTOSSTradeSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            position_size=0.5,
            ai_model="fallback"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get engine performance metrics"""
        
        avg_response_time = self.total_response_time / max(1, self.decision_count)
        success_rate = self.successful_decisions / max(1, self.decision_count)
        
        return {
            "total_decisions": self.decision_count,
            "successful_decisions": self.successful_decisions,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "decisions_per_minute": self.decision_count / max(1, self.total_response_time / 60),
            "is_active": self.is_active,
            "gpt_oss_20b_available": self._check_model_availability(self.gpt_oss_20b_endpoint),
            "gpt_oss_120b_available": self._check_model_availability(self.gpt_oss_120b_endpoint)
        }
    
    def _check_model_availability(self, endpoint: str) -> bool:
        """Check if GPT-OSS model is available"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

# Global instance
_gpt_oss_engine = None

async def get_gpt_oss_engine() -> GPTOSSTradingEngine:
    """Get or create the global GPT-OSS trading engine"""
    global _gpt_oss_engine
    
    if _gpt_oss_engine is None:
        _gpt_oss_engine = GPTOSSTradingEngine()
    
    return _gpt_oss_engine

# Test function
async def test_gpt_oss_engine():
    """Test the GPT-OSS trading engine"""
    print("🧪 Testing GPT-OSS Trading Engine...")
    
    engine = await get_gpt_oss_engine()
    
    # Test market data
    test_data = {
        'price': 175.50,
        'change_percent': 1.2,
        'volume': 50000000
    }
    
    signal = await engine.analyze_trading_opportunity("AAPL", test_data)
    
    print(f"📊 GPT-OSS Test Signal:")
    print(f"   Symbol: {signal.symbol}")
    print(f"   Action: {signal.action}")
    print(f"   Confidence: {signal.confidence:.2f}")
    print(f"   Reasoning: {signal.reasoning}")
    print(f"   AI Model: {signal.ai_model}")
    print(f"   Response Time: {signal.response_time:.2f}s")
    
    metrics = engine.get_performance_metrics()
    print(f"📈 Performance Metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(test_gpt_oss_engine())
