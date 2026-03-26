"""
Mercury 2 LLM Adapter for PROMETHEUS
Inception Labs' diffusion LLM — 1,009 tokens/sec on NVIDIA Blackwell
OpenAI-compatible drop-in: https://api.inceptionlabs.ai/v1/

Features:
  - 128K context window
  - Native tool use + schema-aligned JSON output
  - Streaming + tunable reasoning depth
  - $0.25/M input, $0.75/M output tokens (free 10M on signup)

Usage:
  Set MERCURY_API_KEY in .env (or INCEPTION_API_KEY)
  Set MERCURY_ENABLED=true
"""

import os
import logging
import time
import asyncio
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class Mercury2Adapter:
    """
    Adapter for Mercury 2 diffusion LLM via OpenAI-compatible API.
    Fastest commercial reasoning LLM — ideal for real-time sentiment loops.
    """

    # Pricing per million tokens (USD)
    INPUT_COST_PER_M = 0.25
    OUTPUT_COST_PER_M = 0.75

    MODELS = {
        "mercury-2": "Reasoning diffusion model (flagship)",
        "mercury": "Chat-optimised diffusion model",
        "mercury-coder-small": "Code-specialised (small)",
        "mercury-coder-mini": "Code-specialised (mini)",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mercury-2",
        base_url: str = "https://api.inceptionlabs.ai/v1/",
    ):
        self.api_key = api_key or os.getenv("MERCURY_API_KEY") or os.getenv("INCEPTION_API_KEY", "")
        self.base_url = os.getenv("MERCURY_API_ENDPOINT", base_url).rstrip("/") + "/"
        self.model = os.getenv("MERCURY_MODEL", model)

        # STAGE 3: Inference Resilience - Timeout & Circuit Breaker
        self.timeout_seconds = int(os.getenv('INFERENCE_TIMEOUT_SECONDS', '10'))
        self.circuit_breaker_threshold = int(os.getenv('INFERENCE_CIRCUIT_BREAKER_THRESHOLD', '3'))
        self.consecutive_failures = 0
        self.circuit_breaker_open = False

        # Stats tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        self.avg_latency_ms = 0.0

        self.client = None
        self._init_client()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_client(self):
        """Initialise the OpenAI-compatible client pointed at Mercury's endpoint."""
        if not self.api_key:
            logger.warning("Mercury 2: No API key configured — provider disabled")
            return

        try:
            from openai import OpenAI

            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
            logger.info(
                f"Mercury 2 initialised — model={self.model}, endpoint={self.base_url}"
            )
        except ImportError:
            logger.error("Mercury 2 requires the 'openai' package (pip install openai)")
        except Exception as exc:
            logger.error(f"Mercury 2 init failed: {exc}")

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a completion using Mercury 2.

        Returns dict with keys: success, response, model, cost, source, tokens_used, latency_ms
        STAGE 3: Includes timeout (10s default) and circuit breaker (3 failures → fallback)
        """
        # STAGE 3: Check circuit breaker
        if self.circuit_breaker_open:
            logger.warning(f"🔌 STAGE 3 CIRCUIT BREAKER OPEN - Mercury 2 disabled (>{self.circuit_breaker_threshold} failures)")
            return {
                "success": False,
                "error": f"Circuit breaker open after {self.consecutive_failures} consecutive failures",
                "needs_fallback": True,
            }

        if not self.client:
            return {
                "success": False,
                "error": "Mercury 2 client not initialised (missing API key?)",
                "needs_fallback": True,
            }

        self.total_requests += 1
        start = time.perf_counter()

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": self.timeout_seconds,  # STAGE 3: Enforce timeout (default 10s)
            }

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)

            elapsed_ms = (time.perf_counter() - start) * 1000
            content = response.choices[0].message.content or ""
            usage = response.usage

            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = prompt_tokens + completion_tokens

            cost = (
                (prompt_tokens / 1_000_000) * self.INPUT_COST_PER_M
                + (completion_tokens / 1_000_000) * self.OUTPUT_COST_PER_M
            )

            # Update stats
            self.successful_requests += 1
            self.consecutive_failures = 0  # STAGE 3: Reset on success
            self.total_cost += cost
            self.total_tokens += total_tokens
            self.avg_latency_ms = (
                (self.avg_latency_ms * (self.successful_requests - 1) + elapsed_ms)
                / self.successful_requests
            )

            logger.info(
                f"Mercury 2 response: {total_tokens} tokens in {elapsed_ms:.0f}ms "
                f"(${cost:.6f})"
            )

            return {
                "success": True,
                "response": content,
                "model": self.model,
                "cost": cost,
                "source": "Mercury 2 (Inception Labs)",
                "tokens_used": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency_ms": elapsed_ms,
            }

        except asyncio.TimeoutError:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.consecutive_failures += 1
            logger.warning(f"🔴 STAGE 3: Mercury 2 TIMEOUT after {elapsed_ms:.0f}ms (>{self.timeout_seconds}s)")
            if self.consecutive_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                logger.critical(f"🔌 STAGE 3: Circuit breaker opened after {self.consecutive_failures} timeouts")
            return {
                "success": False,
                "error": f"Mercury 2 timeout ({self.timeout_seconds}s)",
                "needs_fallback": True,
                "latency_ms": elapsed_ms,
            }
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.consecutive_failures += 1
            logger.error(f"Mercury 2 generation failed ({elapsed_ms:.0f}ms, failure #{self.consecutive_failures}): {exc}")
            if self.consecutive_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                logger.critical(f"🔌 STAGE 3: Circuit breaker opened after {self.consecutive_failures} failures")
            return {
                "success": False,
                "error": str(exc),
                "needs_fallback": True,
                "latency_ms": elapsed_ms,
            }

    # ------------------------------------------------------------------
    # Trading-specific helpers
    # ------------------------------------------------------------------

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse market data and return a trading signal."""
        symbol = market_data.get("symbol", "UNKNOWN")
        price = market_data.get("price", 0)
        change = market_data.get("change_percent", 0)
        volume = market_data.get("volume", 0)
        indicators = market_data.get("indicators", {})

        prompt = (
            f"You are an expert quantitative trader. Analyse this data and respond "
            f"with ONLY a JSON object: {{\"action\": \"BUY\"|\"SELL\"|\"HOLD\", "
            f"\"confidence\": 0.0-1.0, \"reasoning\": \"...\"}}\n\n"
            f"Symbol: {symbol}\n"
            f"Price: ${price:.2f}\n"
            f"Change: {change:+.2f}%\n"
            f"Volume: {volume:,.0f}\n"
            f"RSI: {indicators.get('rsi', 'N/A')}\n"
            f"MACD: {indicators.get('macd', 'N/A')}\n"
            f"Volatility: {indicators.get('volatility', 'N/A')}\n"
        )

        result = self.generate(prompt, max_tokens=200, temperature=0.3, json_mode=True)

        if result.get("success"):
            import json as _json

            try:
                parsed = _json.loads(result["response"])
                parsed["source"] = "Mercury 2"
                parsed["cost"] = result.get("cost", 0)
                parsed["latency_ms"] = result.get("latency_ms", 0)
                return parsed
            except _json.JSONDecodeError:
                pass

        return {
            "action": "HOLD",
            "confidence": 0,
            "reasoning": result.get("error", "Mercury 2 unavailable"),
            "cost": 0.0,
            "source": "Mercury 2 (Fallback)",
            "needs_fallback": True,
        }

    def analyze_sentiment(self, texts: list[str]) -> Dict[str, Any]:
        """
        Batch sentiment analysis — Mercury 2's speed (1k tok/s) makes it
        ideal for processing news/social feeds in real time.
        """
        joined = "\n---\n".join(t[:500] for t in texts[:20])  # Cap at 20 items
        prompt = (
            "Rate the market sentiment of each text below on a scale of -1.0 (very "
            "bearish) to +1.0 (very bullish). Return ONLY a JSON object: "
            '{"overall": float, "count": int, "bullish": int, "bearish": int, '
            '"neutral": int, "summary": "..."}\n\n'
            f"{joined}"
        )
        result = self.generate(prompt, max_tokens=300, temperature=0.2, json_mode=True)

        if result.get("success"):
            import json as _json

            try:
                parsed = _json.loads(result["response"])
                parsed["source"] = "Mercury 2"
                parsed["cost"] = result.get("cost", 0)
                return parsed
            except _json.JSONDecodeError:
                pass

        return {
            "overall": 0.0,
            "count": len(texts),
            "summary": "Sentiment unavailable",
            "source": "Mercury 2 (Fallback)",
        }

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        return {
            "provider": "Mercury 2 (Inception Labs)",
            "model": self.model,
            "enabled": self.client is not None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "total_cost": round(self.total_cost, 6),
            "total_tokens": self.total_tokens,
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "success_rate": (
                round(self.successful_requests / max(self.total_requests, 1) * 100, 1)
            ),
        }

    def is_available(self) -> bool:
        """Check if Mercury2 is available and not circuit-broken (STAGE 3)"""
        return self.client is not None and not self.circuit_breaker_open
