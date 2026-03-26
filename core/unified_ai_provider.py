"""
Unified AI Provider for PROMETHEUS
Routes AI requests through a multi-provider fallback chain:
  1. DeepSeek (Cloud API or Local Ollama) — primary
  2. Mercury 2 (Inception Labs diffusion LLM, 1k tok/s) — fast fallback
  3. OpenAI (GPT-4o-mini) — final fallback
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class UnifiedAIProvider:
    """
    Unified AI provider with triple-fallback chain:
      DeepSeek → Mercury 2 → OpenAI

    Mercury 2 (Inception Labs):
      - Diffusion LLM: 1,009 tok/s, 128K context, $0.25/$0.75 per M tokens
      - OpenAI-compatible API at https://api.inceptionlabs.ai/v1/
      - Ideal for real-time sentiment & fast agent loops
    """

    def __init__(self):
        self.use_local_ai = os.getenv('USE_LOCAL_AI', 'true').lower() == 'true'
        self.deepseek_enabled = os.getenv('DEEPSEEK_ENABLED', 'true').lower() == 'true'
        self.mercury_enabled = os.getenv('MERCURY_ENABLED', 'false').lower() == 'true'
        self.openai_fallback = os.getenv('OPENAI_FALLBACK', 'false').lower() == 'true'
        self.use_deepseek_api = os.getenv('USE_DEEPSEEK_API', 'false').lower() == 'true'

        self.deepseek_adapter = None
        self.mercury_adapter = None
        self.openai_client = None

        # Initialize DeepSeek (Cloud API or Local Ollama - handled internally by adapter)
        if self.deepseek_enabled:
            try:
                from core.deepseek_adapter import DeepSeekAdapter
                model = os.getenv('DEEPSEEK_MODEL', 'deepseek-r1:8b')
                endpoint = os.getenv('GPT_OSS_API_ENDPOINT', 'http://localhost:11434')
                self.deepseek_adapter = DeepSeekAdapter(endpoint=endpoint, model=model)

                # Log based on mode
                if self.deepseek_adapter.mode == 'cloud':
                    logger.info(f"DeepSeek Cloud API initialized: {self.deepseek_adapter.cloud_model}")
                else:
                    logger.info(f"DeepSeek Local (Ollama) initialized: {model}")
            except Exception as e:
                logger.warning(f"DeepSeek initialization failed: {e}")
                self.deepseek_adapter = None

        # Initialize Mercury 2 (Inception Labs — fast diffusion LLM)
        if self.mercury_enabled:
            try:
                from core.mercury2_adapter import Mercury2Adapter
                self.mercury_adapter = Mercury2Adapter()
                if self.mercury_adapter.is_available():
                    logger.info(f"Mercury 2 initialized: model={self.mercury_adapter.model}")
                else:
                    logger.warning("Mercury 2: no API key — disabled")
                    self.mercury_adapter = None
            except Exception as e:
                logger.warning(f"Mercury 2 initialization failed: {e}")
                self.mercury_adapter = None

        # Initialize OpenAI fallback (if enabled)
        if self.openai_fallback:
            try:
                import openai
                api_key = os.getenv('OPENAI_API_KEY', '')
                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI fallback enabled")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
                self.openai_client = None
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate AI response.
        Chain: DeepSeek → Mercury 2 → OpenAI → conservative fallback
        """
        use_fallback = False

        # 1) Try DeepSeek first (Cloud API or Local Ollama)
        if self.deepseek_adapter:
            try:
                result = self.deepseek_adapter.generate(prompt, max_tokens, temperature)
                if result.get('success'):
                    source = result.get('source', 'DeepSeek')
                    cost = result.get('cost', 0.0)
                    logger.info(f"AI response from {source} (cost: ${cost:.4f})")
                    return result
                else:
                    logger.warning(f"DeepSeek failed: {result.get('error')}")
                    use_fallback = result.get('needs_fallback', True)
            except Exception as e:
                logger.warning(f"DeepSeek exception: {e}")
                use_fallback = True
        else:
            use_fallback = True

        # 2) Try Mercury 2 (fast diffusion LLM — 1k tok/s)
        if use_fallback and self.mercury_adapter:
            try:
                logger.info("Trying Mercury 2 (fast fallback)...")
                result = self.mercury_adapter.generate(prompt, max_tokens, temperature)
                if result.get('success'):
                    logger.info(f"AI response from Mercury 2 (cost: ${result.get('cost', 0):.4f})")
                    return result
                else:
                    logger.warning(f"Mercury 2 failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Mercury 2 exception: {e}")

        # 3) Fallback to OpenAI (if enabled and needed)
        if use_fallback and self.openai_fallback and self.openai_client:
            try:
                logger.info("⚠️ Falling back to OpenAI")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                return {
                    'success': True,
                    'response': response.choices[0].message.content,
                    'model': 'gpt-4o-mini',
                    'cost': 0.002,  # Approximate
                    'source': 'OpenAI (Fallback)',
                    'tokens_used': response.usage.total_tokens
                }
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")

        # No AI available - return conservative response
        return {
            'success': False,
            'error': 'No AI provider available',
            'response': 'AI unavailable - using conservative HOLD strategy'
        }

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and provide trading signal"""
        # Try DeepSeek first
        if self.deepseek_adapter:
            try:
                result = self.deepseek_adapter.analyze_market(market_data)
                if result.get('action') != 'HOLD' or result.get('confidence', 0) > 0:
                    return result
                if result.get('needs_fallback') and (self.mercury_adapter or self.openai_fallback):
                    pass  # Fall through
                else:
                    return result
            except Exception as e:
                logger.warning(f"DeepSeek market analysis failed: {e}")

        # Try Mercury 2 (ideal for fast sentiment/market analysis loops)
        if self.mercury_adapter:
            try:
                result = self.mercury_adapter.analyze_market(market_data)
                if result.get('action') != 'HOLD' or result.get('confidence', 0) > 0:
                    return result
                if not result.get('needs_fallback'):
                    return result
            except Exception as e:
                logger.warning(f"Mercury 2 market analysis failed: {e}")

        # Fallback: conservative HOLD
        return {
            'action': 'HOLD',
            'confidence': 0,
            'reasoning': 'AI unavailable - conservative hold',
            'cost': 0.0,
            'source': 'Fallback'
        }

    def analyze_sentiment_fast(self, texts: list) -> Dict[str, Any]:
        """
        Fast batch sentiment analysis using Mercury 2 (preferred)
        or falling back to DeepSeek.
        Mercury 2's 1k tok/s throughput makes it ideal for real-time feeds.
        """
        if self.mercury_adapter:
            try:
                return self.mercury_adapter.analyze_sentiment(texts)
            except Exception as e:
                logger.warning(f"Mercury 2 sentiment failed: {e}")

        # Fallback: generate a sentiment prompt through the normal chain
        joined = "\n".join(t[:200] for t in texts[:10])
        result = self.generate(
            f"Rate overall market sentiment of these texts from -1 (bearish) to +1 (bullish). "
            f"Reply with just a number.\n\n{joined}",
            max_tokens=50,
            temperature=0.2,
        )
        try:
            score = float(result.get("response", "0").strip())
        except (ValueError, TypeError):
            score = 0.0
        return {"overall": score, "count": len(texts), "source": result.get("source", "Unknown")}

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all providers"""
        if self.deepseek_adapter:
            mode = self.deepseek_adapter.mode
            provider = f"DeepSeek ({mode.title()})"
        else:
            provider = 'None'
            mode = 'none'

        stats = {
            'provider': provider,
            'mode': mode,
            'mercury_enabled': self.mercury_adapter is not None,
            'fallback_enabled': self.openai_fallback
        }

        if self.deepseek_adapter:
            deepseek_stats = self.deepseek_adapter.get_stats()
            stats['deepseek'] = deepseek_stats

        if self.mercury_adapter:
            stats['mercury2'] = self.mercury_adapter.get_stats()

        return stats


# Global instance
_ai_provider = None

def get_ai_provider() -> UnifiedAIProvider:
    """Get global AI provider instance"""
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = UnifiedAIProvider()
    return _ai_provider

