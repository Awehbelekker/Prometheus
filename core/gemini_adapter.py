"""
Gemini 2.0 Flash Adapter for PROMETHEUS
Google's fastest frontier LLM — free tier via Google AI Studio.

Features:
  - 1M token context window (can read entire knowledge base in one call)
  - Native multimodal (text + vision)
  - Free API key at: https://aistudio.google.com/app/apikey
  - Sub-second latency on flash model

Setup:
  Set GOOGLE_AI_API_KEY in .env
  pip install google-generativeai
"""

import os
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a professional quantitative trading analyst with deep expertise
in technical analysis, fundamental analysis, and market microstructure. You provide precise,
concise trading signals backed by clear reasoning. Always respond in the exact format requested."""


class GeminiAdapter:
    """
    Adapter for Google Gemini 2.0 Flash via google-generativeai SDK.
    Circuit breaker protects the voting loop if Google AI is slow or unavailable.
    """

    CIRCUIT_BREAKER_THRESHOLD = 3
    CIRCUIT_BREAKER_RESET_SEC = 300  # 5 minutes

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.api_key = os.getenv("GOOGLE_AI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", model)
        self.client = None
        self.model = None

        self.consecutive_failures = 0
        self.circuit_open = False
        self.circuit_opened_at: Optional[float] = None

        self.total_requests = 0
        self.successful_requests = 0

        if not self.api_key:
            logger.warning("Gemini: No GOOGLE_AI_API_KEY set — voter disabled")
            return

        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            from google.genai import types as genai_types
            self._genai_types = genai_types
            self.client = genai.Client(api_key=self.api_key)
            self.model = True  # sentinel — client is the actual handle
            logger.info(f"Gemini {self.model_name} initialized (google-genai SDK)")
        except ImportError:
            logger.warning("Gemini: google-genai not installed — run: pip install google-genai")
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")

    def _check_circuit_breaker(self) -> bool:
        """Returns True if circuit is OPEN (i.e. we should skip)."""
        if not self.circuit_open:
            return False
        elapsed = time.time() - (self.circuit_opened_at or 0)
        if elapsed >= self.CIRCUIT_BREAKER_RESET_SEC:
            self.circuit_open = False
            self.consecutive_failures = 0
            logger.info("Gemini circuit breaker reset")
            return False
        return True

    def _record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            self.circuit_open = True
            self.circuit_opened_at = time.time()
            logger.warning(f"Gemini circuit breaker OPEN ({self.consecutive_failures} failures)")

    def _record_success(self):
        self.consecutive_failures = 0
        self.circuit_open = False
        self.successful_requests += 1

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and return a trading signal."""
        _hold = {"action": "HOLD", "confidence": 0, "reasoning": "Gemini unavailable"}

        if not self.model:
            return _hold
        if self._check_circuit_breaker():
            return _hold

        symbol  = market_data.get("symbol", "UNKNOWN")
        price   = market_data.get("price", market_data.get("current_price", 0))
        change  = market_data.get("change_percent", market_data.get("price_change_24h", 0))
        rsi     = market_data.get("rsi", 50)
        volume  = market_data.get("volume", 0)
        avg_vol = market_data.get("avg_volume", volume or 1)
        vol_ratio = volume / max(avg_vol, 1)
        macd    = market_data.get("macd", 0)
        regime  = market_data.get("regime", "unknown")

        prompt = f"""Analyze {symbol} and give a trading signal.

Market snapshot:
- Price: ${price:.2f}  Change: {change:+.2f}%
- RSI: {rsi:.1f}  MACD: {macd:.4f}
- Volume ratio vs avg: {vol_ratio:.2f}x
- Market regime: {regime}

Respond ONLY in this exact format (one line):
ACTION|CONFIDENCE|REASONING

Where ACTION is BUY, SELL, or HOLD; CONFIDENCE is 0-100; REASONING is under 20 words."""

        self.total_requests += 1
        try:
            from google.genai import types as _t
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=_SYSTEM_PROMPT + "\n\n" + prompt,
                config=_t.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=80,
                ),
            )
            text = response.text.strip()

            parts = text.split("|")
            if len(parts) >= 3:
                action = parts[0].strip().upper()
                if action not in ("BUY", "SELL", "HOLD"):
                    action = "HOLD"
                try:
                    confidence = max(0, min(100, int(parts[1].strip())))
                except ValueError:
                    confidence = 50
                reasoning = parts[2].strip()
                self._record_success()
                return {"action": action, "confidence": confidence, "reasoning": reasoning, "source": "Gemini"}

            # Fallback: keyword scan of raw response
            lower = text.lower()
            if "buy" in lower:
                action, confidence = "BUY", 55
            elif "sell" in lower:
                action, confidence = "SELL", 55
            else:
                action, confidence = "HOLD", 0
            self._record_success()
            return {"action": action, "confidence": confidence, "reasoning": text[:80], "source": "Gemini"}

        except Exception as e:
            self._record_failure()
            logger.debug(f"Gemini analyze_market failed: {e}")
            return _hold

    def get_stats(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "circuit_open": self.circuit_open,
            "available": self.model is not None,
        }
