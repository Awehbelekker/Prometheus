#!/usr/bin/env python3
"""
🤖 Enhanced AI Trading Engine
Integrates real AI intelligence with Revolutionary Engines for live trading
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AITradingSignal:
    """Enhanced AI trading signal with full intelligence"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    risk_score: Optional[float] = None
    ai_source: str = "openai"  # openai, anthropic, gpt_oss, fallback

class EnhancedAITradingEngine:
    """Enhanced AI Trading Engine with real intelligence"""
    
    def __init__(self):
        self.is_initialized = False
        self.ai_service = None
        self.decision_count = 0
        self.last_decision_time = None
        
    async def initialize(self):
        """Initialize the AI trading engine"""
        try:
            # Import AI services
            from core.llm_service import LLMService, AIMessage
            from config.ai_config import ai_config_manager
            
            self.ai_service = LLMService()
            self.ai_config = ai_config_manager
            
            # Check if real AI providers are available
            available_providers = self.ai_config.get_available_providers()
            real_providers = [p for p in available_providers if p.value != 'mock']
            
            if real_providers:
                logger.info(f"[CHECK] Enhanced AI Trading Engine initialized with real providers: {[p.value for p in real_providers]}")
                self.is_initialized = True
            else:
                logger.warning("[WARNING]️ Enhanced AI Trading Engine initialized with fallback mode")
                self.is_initialized = True
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Enhanced AI Trading Engine: {e}")
            self.is_initialized = False
    
    async def analyze_market_opportunity(self, symbol: str, market_data: Dict[str, Any]) -> AITradingSignal:
        """Analyze market opportunity with enhanced AI intelligence"""
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Create enhanced market analysis prompt
            analysis_prompt = self._create_enhanced_analysis_prompt(symbol, market_data)
            
            # Get AI analysis
            ai_response = await self._get_ai_analysis(analysis_prompt)
            
            # Parse AI response into trading signal
            signal = self._parse_ai_response(symbol, ai_response, market_data)
            
            # Update decision tracking
            self.decision_count += 1
            self.last_decision_time = datetime.now()
            
            logger.info(f"🤖 AI Trading Signal Generated: {symbol} -> {signal.action} (confidence: {signal.confidence:.2f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"[ERROR] AI analysis error for {symbol}: {e}")
            return self._create_fallback_signal(symbol, market_data)
    
    def _create_enhanced_analysis_prompt(self, symbol: str, market_data: Dict[str, Any]) -> str:
        """Create enhanced analysis prompt for AI"""
        
        current_price = market_data.get('price', 0)
        change_percent = market_data.get('change_percent', 0)
        volume = market_data.get('volume', 0)
        
        prompt = f"""
PROMETHEUS AI Trading Analysis Request

Symbol: {symbol}
Current Price: ${current_price:.2f}
Change: {change_percent:.2f}%
Volume: {volume:,}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANALYSIS REQUIREMENTS:
1. Provide BUY, SELL, or HOLD recommendation
2. Confidence level (0.0 to 1.0)
3. Detailed reasoning based on:
   - Technical indicators
   - Market sentiment
   - Risk assessment
   - Current market conditions
4. Suggested position size (as percentage of capital)
5. Target price and stop loss levels

RISK CONSTRAINTS:
- Maximum position size: 1% of capital
- Conservative approach for live trading
- Account for current market volatility

RESPONSE FORMAT:
ACTION: [BUY/SELL/HOLD]
CONFIDENCE: [0.0-1.0]
REASONING: [Detailed analysis]
POSITION_SIZE: [Percentage]
TARGET_PRICE: [Price level]
STOP_LOSS: [Price level]
RISK_SCORE: [0.0-1.0]

Provide professional trading analysis with specific actionable recommendations.
"""
        return prompt
    
    async def _get_ai_analysis(self, prompt: str) -> Dict[str, Any]:
        """Get AI analysis using available providers"""
        
        try:
            from core.llm_service import AIMessage
            
            messages = [
                AIMessage(role="system", content="You are PROMETHEUS AI, an expert trading analyst providing professional market analysis."),
                AIMessage(role="user", content=prompt)
            ]
            
            # Try to use the configured model
            model = self.ai_config.config.chat_model
            response = await self.ai_service.generate_response(messages=messages, model=model)
            
            if response.success:
                return {
                    "content": response.content,
                    "success": True,
                    "ai_source": "openai",
                    "tokens_used": response.tokens_used,
                    "response_time": response.response_time
                }
            else:
                logger.warning(f"[WARNING]️ AI service error: {response.error}")
                return {"content": "", "success": False, "ai_source": "fallback"}
                
        except Exception as e:
            logger.error(f"[ERROR] AI analysis request failed: {e}")
            return {"content": "", "success": False, "ai_source": "fallback"}
    
    def _parse_ai_response(self, symbol: str, ai_response: Dict[str, Any], market_data: Dict[str, Any]) -> AITradingSignal:
        """Parse AI response into trading signal"""
        
        if not ai_response.get("success", False):
            return self._create_fallback_signal(symbol, market_data)
        
        content = ai_response.get("content", "")
        
        # Parse AI response (simple parsing - could be enhanced with structured output)
        action = "HOLD"
        confidence = 0.5
        reasoning = "AI analysis completed"
        position_size = 0.5  # 0.5% default
        target_price = None
        stop_loss = None
        risk_score = 0.5
        
        # Extract action
        if "ACTION: BUY" in content or "BUY" in content.upper():
            action = "BUY"
        elif "ACTION: SELL" in content or "SELL" in content.upper():
            action = "SELL"
        else:
            action = "HOLD"
        
        # Extract confidence (look for patterns like "CONFIDENCE: 0.8")
        import re
        confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', content)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            except:
                pass
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*([^\n]+)', content)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        else:
            reasoning = content[:200] + "..." if len(content) > 200 else content
        
        return AITradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            position_size=position_size,
            target_price=target_price,
            stop_loss=stop_loss,
            risk_score=risk_score,
            ai_source=ai_response.get("ai_source", "openai")
        )
    
    def _create_fallback_signal(self, symbol: str, market_data: Dict[str, Any]) -> AITradingSignal:
        """Create fallback signal when AI is not available"""
        
        # Simple technical analysis fallback
        change_percent = market_data.get('change_percent', 0)
        
        if change_percent > 2.0:
            action = "BUY"
            confidence = 0.6
            reasoning = "Fallback: Strong positive momentum detected"
        elif change_percent < -2.0:
            action = "SELL"
            confidence = 0.6
            reasoning = "Fallback: Strong negative momentum detected"
        else:
            action = "HOLD"
            confidence = 0.4
            reasoning = "Fallback: Neutral market conditions"
        
        return AITradingSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            position_size=0.5,
            ai_source="fallback"
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "initialized": self.is_initialized,
            "decision_count": self.decision_count,
            "last_decision": self.last_decision_time.isoformat() if self.last_decision_time else None,
            "ai_available": self.ai_config.is_real_provider_available() if self.ai_config else False,
            "available_providers": [p.value for p in self.ai_config.get_available_providers()] if self.ai_config else []
        }

# Global instance
_enhanced_ai_engine = None

async def get_enhanced_ai_engine() -> EnhancedAITradingEngine:
    """Get or create the global enhanced AI engine"""
    global _enhanced_ai_engine
    
    if _enhanced_ai_engine is None:
        _enhanced_ai_engine = EnhancedAITradingEngine()
        await _enhanced_ai_engine.initialize()
    
    return _enhanced_ai_engine

# Test function
async def test_enhanced_ai_engine():
    """Test the enhanced AI engine"""
    print("🧪 Testing Enhanced AI Trading Engine...")
    
    engine = await get_enhanced_ai_engine()
    
    # Test market data
    test_data = {
        'price': 150.25,
        'change_percent': 2.5,
        'volume': 1000000
    }
    
    signal = await engine.analyze_market_opportunity("AAPL", test_data)
    
    print(f"📊 Test Signal Generated:")
    print(f"   Symbol: {signal.symbol}")
    print(f"   Action: {signal.action}")
    print(f"   Confidence: {signal.confidence:.2f}")
    print(f"   Reasoning: {signal.reasoning}")
    print(f"   AI Source: {signal.ai_source}")
    
    status = engine.get_engine_status()
    print(f"📈 Engine Status: {status}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_ai_engine())
