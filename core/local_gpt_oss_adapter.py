
import asyncio
import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LocalGPTOSSAdapter:
    """Local GPT-OSS adapter with fallback capabilities"""

    def __init__(self):
        self.models_available = {
            "gpt_oss_20b": False,
            "gpt_oss_120b": False
        }
        self.fallback_enabled = True
        self.endpoints = {
            "gpt_oss_20b": "http://localhost:5000",
            "gpt_oss_120b": "http://localhost:5001"
        }
        
    async def initialize(self):
        """Initialize the adapter"""
        await self._check_model_availability()
        logger.info("Local GPT-OSS adapter initialized")
        
    async def _check_model_availability(self):
        """Check which models are available"""
        import requests
        
        endpoints = {
            "gpt_oss_20b": "http://localhost:5000/health",
            "gpt_oss_120b": "http://localhost:5001/health"
        }
        
        for model, endpoint in endpoints.items():
            try:
                response = requests.get(endpoint, timeout=2)
                self.models_available[model] = response.status_code == 200
            except:
                self.models_available[model] = False
                
    def is_available(self, model_size="20b"):
        """Check if a model is available"""
        if model_size == "20b":
            return self.models_available.get("gpt_oss_20b", False)
        elif model_size == "120b":
            return self.models_available.get("gpt_oss_120b", False)
        return False
        
    async def generate_trading_signal(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal using local models or enhanced fallback"""
        
        # Try GPT-OSS models first
        if self.is_available("20b"):
            return await self._call_gpt_oss_20b(symbol, market_data)
        elif self.is_available("120b"):
            return await self._call_gpt_oss_120b(symbol, market_data)
        else:
            # Enhanced fallback with better logic
            return await self._enhanced_fallback_signal(symbol, market_data)
            
    async def _call_gpt_oss_20b(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call GPT-OSS 20B model"""
        try:
            import requests
            
            prompt = f"Analyze {symbol} with price ${market_data.get('price', 0):.2f}, change {market_data.get('change_percent', 0):.2f}%. Provide BUY/SELL/HOLD recommendation with confidence."
            
            response = requests.post("http://localhost:5000/generate", 
                                   json={"prompt": prompt, "max_length": 200}, 
                                   timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_ai_response(result.get("text", ""), symbol, market_data)
            else:
                return await self._enhanced_fallback_signal(symbol, market_data)
                
        except Exception as e:
            logger.warning(f"GPT-OSS 20B call failed: {e}")
            return await self._enhanced_fallback_signal(symbol, market_data)
            
    async def _enhanced_fallback_signal(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback signal generation with better logic"""
        
        price = market_data.get('price', 0)
        change_percent = market_data.get('change_percent', 0)
        volume = market_data.get('volume', 0)
        
        # Enhanced decision logic
        buy_score = 0
        sell_score = 0
        confidence = 0.5
        
        # Price momentum analysis
        if change_percent > 3:
            buy_score += 2
        elif change_percent > 1:
            buy_score += 1
        elif change_percent < -3:
            sell_score += 2
        elif change_percent < -1:
            sell_score += 1
            
        # Volume analysis
        if volume > 1000000:  # High volume
            confidence += 0.2
            
        # Price level analysis
        if price > 100:  # Higher priced stocks
            buy_score += 1
            
        # Determine action
        if buy_score > sell_score and buy_score >= 2:
            action = "BUY"
            confidence = min(0.9, 0.6 + (buy_score * 0.1))
        elif sell_score > buy_score and sell_score >= 2:
            action = "SELL"
            confidence = min(0.9, 0.6 + (sell_score * 0.1))
        else:
            action = "HOLD"
            confidence = 0.5
            
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": f"Enhanced fallback analysis: price change {change_percent:.2f}%, volume {volume}",
            "target_price": price * 1.05 if action == "BUY" else price * 0.95,
            "stop_loss": price * 0.95 if action == "BUY" else price * 1.05
        }
        
    def _parse_ai_response(self, text: str, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        text_upper = text.upper()
        
        if "BUY" in text_upper and "SELL" not in text_upper:
            action = "BUY"
            confidence = 0.8
        elif "SELL" in text_upper and "BUY" not in text_upper:
            action = "SELL"
            confidence = 0.8
        else:
            action = "HOLD"
            confidence = 0.6
            
        price = market_data.get('price', 0)
        
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": f"GPT-OSS analysis: {text[:100]}...",
            "target_price": price * 1.05 if action == "BUY" else price * 0.95,
            "stop_loss": price * 0.95 if action == "BUY" else price * 1.05
        }

# Global instance
local_gpt_oss_adapter = LocalGPTOSSAdapter()
