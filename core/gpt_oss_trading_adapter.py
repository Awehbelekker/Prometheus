"""
PROMETHEUS CPT-OSS Trading Integration Adapter
Connects to local Ollama instance running llama3.1:8b-trading
for real AI-powered trading signal generation.

Ollama API: http://localhost:11434/api/generate
Primary model: llama3.1:8b-trading (5.7GB, trading fine-tuned)
Fallback model: qwen2.5:7b (general purpose)
"""

import asyncio
import aiohttp
import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "GPT_OSS_API_ENDPOINT",
    os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
).strip().strip("'\"")

PRIMARY_MODEL = os.getenv("OLLAMA_TRADING_MODEL", "llama3.1:8b-trading")
FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5:7b")

# Timeout for Ollama requests (seconds).
# First call after cold-start can take 60-120s as model loads into RAM.
# Subsequent calls are much faster (2-15s).
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


class ModelSize(Enum):
    """Model size options - maps to Ollama model names"""
    SMALL = "small"   # Primary trading model (fast)
    LARGE = "large"   # Fallback / deeper analysis


@dataclass
class TradingPrompt:
    """Structured trading prompt for the AI"""
    market_data: Dict[str, Any]
    strategy_context: str = "general"
    analysis_type: str = "technical"
    time_horizon: str = "intraday"
    risk_tolerance: str = "moderate"


@dataclass
class AITradingInsight:
    """AI-generated trading insight"""
    symbol: str
    action: str          # "BUY", "SELL", "HOLD"
    confidence: float    # 0.0 to 1.0
    reasoning: str
    price_target: Optional[float]
    stop_loss: Optional[float]
    time_horizon: str
    risk_assessment: str
    market_sentiment: str


class GPTOSSTradingAdapter:
    """
    CPT-OSS / Ollama Trading Integration

    Connects PROMETHEUS to the local Ollama instance running
    llama3.1:8b-trading for real AI-powered trading decisions.

    Capabilities:
    - generate_trading_signal(symbol, market_data)  <- used by launch file
    - generate_trading_strategy(prompt)
    - analyze_market_sentiment(market_data, news)
    - analyze_technical_patterns(symbol, price_data, indicators)
    - assess_risk_exposure(portfolio, market_conditions)
    """

    def __init__(self):
        self.ollama_url = OLLAMA_BASE_URL.rstrip("/")
        self.primary_model = PRIMARY_MODEL
        self.fallback_model = FALLBACK_MODEL
        self.model_size = self.primary_model  # backwards compat attribute
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        self._available_models: List[str] = []

        # Legacy compat
        self.base_urls = {
            ModelSize.SMALL: self.ollama_url,
            ModelSize.LARGE: self.ollama_url,
        }
        self.health_status = {
            ModelSize.SMALL: False,
            ModelSize.LARGE: False,
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self):
        """Connect to Ollama and verify model availability."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=OLLAMA_TIMEOUT)
        )
        try:
            async with self.session.get(f"{self.ollama_url}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._available_models = [
                        m["name"] for m in data.get("models", [])
                    ]
                    has_primary = any(
                        self.primary_model in m for m in self._available_models
                    )
                    self.is_connected = True
                    self.health_status[ModelSize.SMALL] = has_primary
                    self.health_status[ModelSize.LARGE] = has_primary
                    if has_primary:
                        logger.info(
                            f"CPT-OSS connected to Ollama - "
                            f"primary model: {self.primary_model}"
                        )
                    else:
                        logger.warning(
                            f"Ollama reachable but {self.primary_model} "
                            f"not found. Available: {self._available_models}"
                        )
        except Exception as e:
            logger.warning(f"Ollama not reachable at {self.ollama_url}: {e}")

    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    def is_available(self, model_size: ModelSize = ModelSize.SMALL) -> bool:
        """Check if a specific model is available."""
        return self.is_connected and self.health_status.get(model_size, False)

    # ------------------------------------------------------------------
    # PRIMARY METHOD - called by launch_ultimate_prometheus_LIVE_TRADING.py
    # ------------------------------------------------------------------

    async def generate_trading_signal(
        self,
        symbol: str,
        market_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a trading signal for a symbol using the local AI model.

        Returns dict with keys: action, confidence, reasoning
        This is the method the launch file calls at L3381.
        """
        price = market_data.get("price") or market_data.get("current_price", 0)
        volume = market_data.get("volume", 0)
        change_pct = market_data.get("change_percent", market_data.get("change_pct", 0))
        rsi = market_data.get("rsi", "N/A")
        sma_20 = market_data.get("sma_20", "N/A")
        sma_50 = market_data.get("sma_50", "N/A")
        macd = market_data.get("macd", "N/A")
        bb_upper = market_data.get("bb_upper", "N/A")
        bb_lower = market_data.get("bb_lower", "N/A")

        prompt = (
            "You are a professional trading analyst. Analyze this stock and "
            "respond ONLY with valid JSON.\n\n"
            f"Symbol: {symbol}\n"
            f"Price: ${price}\n"
            f"Volume: {volume}\n"
            f"Daily Change: {change_pct}%\n"
            f"RSI: {rsi}\n"
            f"SMA-20: {sma_20}\n"
            f"SMA-50: {sma_50}\n"
            f"MACD: {macd}\n"
            f"Bollinger Upper: {bb_upper}\n"
            f"Bollinger Lower: {bb_lower}\n\n"
            "Based on these indicators, provide a trading recommendation.\n"
            'Respond with ONLY this JSON format, no extra text:\n'
            '{"action": "BUY or SELL or HOLD", "confidence": 0.75, '
            '"reasoning": "brief explanation"}'
        )

        try:
            raw = await self._ollama_generate(prompt, self.primary_model)
            parsed = self._extract_json(raw)
            if parsed and "action" in parsed:
                action = parsed["action"].upper().strip()
                if action not in ("BUY", "SELL", "HOLD"):
                    action = "HOLD"
                confidence = min(max(float(parsed.get("confidence", 0.5)), 0.0), 1.0)
                reasoning = parsed.get("reasoning", "AI analysis")
                return {
                    "action": action,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "model": self.primary_model,
                    "source": "ollama-live",
                }
        except Exception as e:
            logger.debug(f"CPT-OSS signal generation failed for {symbol}: {e}")

        # Fallback: simple heuristic when Ollama unavailable
        return self._heuristic_signal(symbol, market_data)

    # ------------------------------------------------------------------
    # Strategy generation (accepts TradingPrompt)
    # ------------------------------------------------------------------

    async def generate_trading_strategy(
        self,
        prompt: TradingPrompt,
        model_size: ModelSize = ModelSize.LARGE,
    ) -> AITradingInsight:
        """Generate a comprehensive trading strategy using the local AI."""
        symbol = prompt.market_data.get("symbol", "UNKNOWN")
        strategy_prompt = self._build_strategy_prompt(prompt)

        try:
            raw = await self._ollama_generate(strategy_prompt, self.primary_model)
            return self._parse_strategy_response(raw, prompt)
        except Exception as e:
            logger.debug(f"Strategy generation failed for {symbol}: {e}")
            return self._generate_fallback_insight(prompt)

    # ------------------------------------------------------------------
    # Sentiment analysis
    # ------------------------------------------------------------------

    async def analyze_market_sentiment(
        self,
        market_data: Dict[str, Any],
        news_headlines: List[str] = None,
        model_size: ModelSize = ModelSize.SMALL,
    ) -> Dict[str, Any]:
        """Analyze market sentiment using the local AI."""
        prompt = self._build_sentiment_prompt(market_data, news_headlines)
        try:
            raw = await self._ollama_generate(prompt, self.primary_model)
            parsed = self._extract_json(raw)
            if parsed and "sentiment" in parsed:
                return parsed
            return self._parse_sentiment_response(raw)
        except Exception as e:
            logger.debug(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "AI service unavailable",
                "bullish_factors": [],
                "bearish_factors": [],
            }

    # ------------------------------------------------------------------
    # Technical pattern analysis
    # ------------------------------------------------------------------

    async def analyze_technical_patterns(
        self,
        symbol: str,
        price_data: List[Dict[str, float]],
        indicators: Dict[str, float] = None,
        model_size: ModelSize = ModelSize.SMALL,
    ) -> Dict[str, Any]:
        """Analyze technical patterns using the local AI."""
        prompt = self._build_technical_prompt(symbol, price_data, indicators)
        try:
            raw = await self._ollama_generate(prompt, self.primary_model)
            parsed = self._extract_json(raw)
            if parsed and "recommendation" in parsed:
                return parsed
        except Exception as e:
            logger.debug(f"Technical analysis failed for {symbol}: {e}")

        return {
            "patterns": [],
            "signals": [],
            "strength": "weak",
            "confidence": 0.5,
            "recommendation": "HOLD",
        }

    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------

    async def assess_risk_exposure(
        self,
        portfolio: Dict[str, Any],
        market_conditions: Dict[str, Any],
        model_size: ModelSize = ModelSize.LARGE,
    ) -> Dict[str, Any]:
        """Risk assessment using the local AI."""
        prompt = self._build_risk_prompt(portfolio, market_conditions)
        try:
            raw = await self._ollama_generate(prompt, self.primary_model)
            parsed = self._extract_json(raw)
            if parsed and "risk_level" in parsed:
                return parsed
        except Exception as e:
            logger.debug(f"Risk assessment failed: {e}")

        return {
            "risk_level": "medium",
            "risk_score": 5.0,
            "risk_factors": ["Unable to assess"],
            "recommendations": ["Monitor closely"],
            "confidence": 0.5,
        }

    # ==================================================================
    # CORE: Ollama API call
    # ==================================================================

    async def _ollama_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 500,
        temperature: float = 0.4,
    ) -> str:
        """Send a prompt to Ollama and return the generated text."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=OLLAMA_TIMEOUT)
            )

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with self.session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("response", "")
            else:
                text = await resp.text()
                raise RuntimeError(
                    f"Ollama API error {resp.status}: {text[:200]}"
                )

    # ==================================================================
    # Legacy compat: _generate_completion
    # ==================================================================

    async def _generate_completion(
        self,
        prompt: str,
        model_size: ModelSize = ModelSize.SMALL,
        max_tokens: int = 500,
        temperature: float = 0.4,
    ) -> str:
        """Legacy interface - routes to _ollama_generate."""
        model = (
            self.primary_model
            if model_size == ModelSize.SMALL
            else self.fallback_model
        )
        return await self._ollama_generate(prompt, model, max_tokens, temperature)

    # ==================================================================
    # Prompt builders
    # ==================================================================

    def _build_sentiment_prompt(
        self, market_data: Dict[str, Any], news_headlines: List[str] = None
    ) -> str:
        prompt = (
            "You are a market sentiment analyst. Analyze the data and "
            "respond ONLY with valid JSON.\n\n"
            f"Market Data:\n"
            f"- Price: ${market_data.get('price', 'N/A')}\n"
            f"- Volume: {market_data.get('volume', 'N/A')}\n"
            f"- Daily Change: {market_data.get('change_percent', 'N/A')}%\n"
        )
        if news_headlines:
            prompt += "\nRecent Headlines:\n"
            for h in news_headlines[:5]:
                prompt += f"- {h}\n"
        prompt += (
            '\nRespond with ONLY this JSON:\n'
            '{"sentiment": "bullish or bearish or neutral", "confidence": 0.75, '
            '"reasoning": "brief", "bullish_factors": [], "bearish_factors": []}'
        )
        return prompt

    def _build_strategy_prompt(self, prompt: TradingPrompt) -> str:
        md = prompt.market_data
        return (
            "You are a professional trading strategist. Analyze and respond "
            "ONLY with valid JSON.\n\n"
            f"Symbol: {md.get('symbol', 'UNKNOWN')}\n"
            f"Price: ${md.get('price', 'N/A')}\n"
            f"Volume: {md.get('volume', 'N/A')}\n"
            f"Analysis Type: {prompt.analysis_type}\n"
            f"Time Horizon: {prompt.time_horizon}\n"
            f"Risk Tolerance: {prompt.risk_tolerance}\n\n"
            'Respond with ONLY this JSON:\n'
            '{"action": "BUY or SELL or HOLD", "confidence": 0.75, '
            '"reasoning": "analysis", "price_target": null, "stop_loss": null, '
            '"risk_assessment": "low or medium or high", '
            '"market_sentiment": "bullish or bearish or neutral"}'
        )

    def _build_technical_prompt(
        self,
        symbol: str,
        price_data: List[Dict[str, float]],
        indicators: Dict[str, float] = None,
    ) -> str:
        recent = price_data[-10:] if len(price_data) > 10 else price_data
        prompt = (
            "You are a technical analysis expert. Analyze and respond ONLY "
            "with valid JSON.\n\n"
            f"Symbol: {symbol}\n"
            f"Recent Prices: {json.dumps(recent, default=str)}\n"
        )
        if indicators:
            prompt += f"Indicators: {json.dumps(indicators, default=str)}\n"
        prompt += (
            '\nRespond with ONLY this JSON:\n'
            '{"patterns": [], "signals": [], "strength": "strong or medium '
            'or weak", "confidence": 0.75, "recommendation": "BUY or SELL '
            'or HOLD"}'
        )
        return prompt

    def _build_risk_prompt(
        self, portfolio: Dict[str, Any], market_conditions: Dict[str, Any]
    ) -> str:
        return (
            "You are a risk management expert. Assess portfolio risk and "
            "respond ONLY with valid JSON.\n\n"
            f"Portfolio: {json.dumps(portfolio, default=str)[:500]}\n"
            f"Market Conditions: "
            f"{json.dumps(market_conditions, default=str)[:500]}\n\n"
            'Respond with ONLY this JSON:\n'
            '{"risk_level": "low or medium or high", "risk_score": 5.0, '
            '"risk_factors": [], "recommendations": [], "confidence": 0.75}'
        )

    # ==================================================================
    # Response parsers
    # ==================================================================

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract the first JSON object from text."""
        if not text:
            return None
        # Try direct parse first
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            pass
        # Try regex extraction (single-level braces)
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        # Try more aggressive multi-level brace match
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    def _parse_sentiment_response(self, response: str) -> Dict[str, Any]:
        """Heuristic fallback when JSON parsing fails."""
        upper = (response or "").upper()
        if any(w in upper for w in ("BULLISH", "STRONG POSITIVE", "BREAKOUT", "SURGE")):
            return {
                "sentiment": "bullish",
                "confidence": 0.75,
                "reasoning": response[:150],
                "bullish_factors": ["AI detected bullish signal"],
                "bearish_factors": [],
            }
        if any(w in upper for w in ("BEARISH", "NEGATIVE", "DECLINE", "WEAK")):
            return {
                "sentiment": "bearish",
                "confidence": 0.70,
                "reasoning": response[:150],
                "bullish_factors": [],
                "bearish_factors": ["AI detected bearish signal"],
            }
        return {
            "sentiment": "neutral",
            "confidence": 0.55,
            "reasoning": response[:150] if response else "No clear signal",
            "bullish_factors": [],
            "bearish_factors": [],
        }

    def _parse_strategy_response(
        self, response: str, prompt: TradingPrompt
    ) -> AITradingInsight:
        """Parse AI strategy response into AITradingInsight."""
        parsed = self._extract_json(response)
        symbol = prompt.market_data.get("symbol", "UNKNOWN")

        if parsed and "action" in parsed:
            action = parsed["action"].upper().strip()
            if action not in ("BUY", "SELL", "HOLD"):
                action = "HOLD"
            return AITradingInsight(
                symbol=symbol,
                action=action,
                confidence=min(
                    max(float(parsed.get("confidence", 0.5)), 0.0), 1.0
                ),
                reasoning=parsed.get("reasoning", "AI analysis"),
                price_target=parsed.get("price_target"),
                stop_loss=parsed.get("stop_loss"),
                time_horizon=prompt.time_horizon,
                risk_assessment=parsed.get("risk_assessment", "medium"),
                market_sentiment=parsed.get("market_sentiment", "neutral"),
            )

        return self._generate_fallback_insight(prompt)

    # ==================================================================
    # Fallback / heuristic methods
    # ==================================================================

    def _heuristic_signal(
        self, symbol: str, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simple deterministic signal when AI is unavailable."""
        price = float(
            market_data.get("price", market_data.get("current_price", 0)) or 0
        )
        volume = float(market_data.get("volume", 0) or 0)
        change_pct = float(
            market_data.get(
                "change_percent", market_data.get("change_pct", 0)
            )
            or 0
        )
        rsi = market_data.get("rsi")

        action = "HOLD"
        confidence = 0.55
        reasoning = f"Heuristic analysis for {symbol}"

        # RSI-based
        if rsi is not None:
            rsi = float(rsi)
            if rsi < 30:
                action = "BUY"
                confidence = 0.72
                reasoning = (
                    f"{symbol} RSI={rsi:.0f} oversold - potential reversal"
                )
            elif rsi > 70:
                action = "SELL"
                confidence = 0.70
                reasoning = (
                    f"{symbol} RSI={rsi:.0f} overbought - potential pullback"
                )

        # Volume + momentum
        if volume > 2_000_000 and change_pct > 2.0:
            action = "BUY"
            confidence = max(confidence, 0.68)
            reasoning = f"{symbol} high volume surge +{change_pct:.1f}%"
        elif change_pct < -3.0:
            action = "SELL"
            confidence = max(confidence, 0.65)
            reasoning = f"{symbol} sharp decline {change_pct:.1f}%"

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "model": "heuristic-fallback",
            "source": "fallback",
        }

    def _generate_fallback_insight(
        self, prompt: TradingPrompt
    ) -> AITradingInsight:
        """Generate a conservative fallback insight."""
        symbol = prompt.market_data.get("symbol", "UNKNOWN")
        return AITradingInsight(
            symbol=symbol,
            action="HOLD",
            confidence=0.50,
            reasoning=f"AI service unavailable - conservative HOLD for {symbol}",
            price_target=None,
            stop_loss=None,
            time_horizon=prompt.time_horizon,
            risk_assessment="medium",
            market_sentiment="neutral",
        )

    # Legacy compat methods
    def _generate_mock_trading_decision(
        self, response: str, prompt: TradingPrompt
    ) -> AITradingInsight:
        """Legacy compat: route to fallback insight."""
        return self._generate_fallback_insight(prompt)

    def _parse_technical_response(self, response: str) -> Dict[str, Any]:
        """Legacy compat: parse technical response."""
        parsed = self._extract_json(response)
        if parsed and "recommendation" in parsed:
            return parsed
        return {
            "patterns": [],
            "signals": [],
            "strength": "weak",
            "confidence": 0.5,
            "recommendation": "HOLD",
        }

    def _parse_risk_response(self, response: str) -> Dict[str, Any]:
        """Legacy compat: parse risk response."""
        parsed = self._extract_json(response)
        if parsed and "risk_level" in parsed:
            return parsed
        return {
            "risk_level": "medium",
            "risk_score": 5.0,
            "risk_factors": ["Unable to assess"],
            "recommendations": ["Monitor closely"],
            "confidence": 0.5,
        }


# ==================================================================
# Singleton access
# ==================================================================

_gpt_oss_adapter: Optional[GPTOSSTradingAdapter] = None


async def get_gpt_oss_adapter() -> GPTOSSTradingAdapter:
    """Get or create the global CPT-OSS adapter instance."""
    global _gpt_oss_adapter
    if _gpt_oss_adapter is None:
        _gpt_oss_adapter = GPTOSSTradingAdapter()
        await _gpt_oss_adapter.initialize()
    return _gpt_oss_adapter


async def cleanup_gpt_oss_adapter():
    """Clean up the global adapter instance."""
    global _gpt_oss_adapter
    if _gpt_oss_adapter:
        await _gpt_oss_adapter.close()
        _gpt_oss_adapter = None
