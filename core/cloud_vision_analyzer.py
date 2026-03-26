"""
Cloud Vision Analyzer for PROMETHEUS Trading Platform

Uses Google Gemini Vision API for high-quality chart analysis.
Replaces local LLaVA when hardware is insufficient.

Cost: ~$0.002 per image (Gemini 1.5 Flash)
Speed: 2-5 seconds per image
Quality: Excellent chart pattern recognition
"""

import os
import logging
import base64
import time
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
import re

logger = logging.getLogger(__name__)

# Import shared result class
from core.multimodal_analyzer import ChartAnalysisResult, MultimodalConfig


@dataclass
class CloudVisionConfig:
    """Configuration for cloud vision analysis"""
    # API Settings - Prefer GLM-4-Flash (fast + cheap), fall back to others
    provider: str = "glm"  # 'glm', 'gemini', 'claude', 'openai'
    api_key: Optional[str] = None
    model: str = "glm-4v-flash"  # Fast and cost-effective vision model

    # Analysis parameters
    temperature: float = 0.2  # Lower for consistent pattern recognition
    max_tokens: int = 1024
    timeout: int = 60

    # Rate limiting
    requests_per_minute: int = 50
    batch_delay: float = 1.0  # GLM-4-Flash is faster

    # Pattern categories to detect
    pattern_categories: List[str] = None

    def __post_init__(self):
        # Get API key from environment - respect manually set provider
        if not self.api_key:
            glm_key = os.getenv('ZHIPUAI_API_KEY')
            gemini_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')
            claude_key = os.getenv('ANTHROPIC_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')

            # If provider already set, get key for that provider
            if self.provider == "openai" and openai_key:
                self.api_key = openai_key
            elif self.provider == "claude" and claude_key:
                self.api_key = claude_key
            elif self.provider == "glm" and glm_key:
                self.api_key = glm_key
            elif self.provider == "gemini" and gemini_key:
                self.api_key = gemini_key
            # Otherwise auto-select: prefer OpenAI > GLM > Gemini > Claude
            elif openai_key:
                self.api_key = openai_key
                self.provider = "openai"
                self.model = "gpt-4o-mini"
            elif glm_key:
                self.api_key = glm_key
                self.provider = "glm"
                self.model = "glm-4v-flash"
            elif gemini_key:
                self.api_key = gemini_key
                self.provider = "gemini"
                self.model = "gemini-1.5-flash"
            elif claude_key:
                self.api_key = claude_key
                self.provider = "claude"
                self.model = "claude-sonnet-4-20250514"

        if self.pattern_categories is None:
            self.pattern_categories = [
                "Head and Shoulders", "Inverse Head and Shoulders",
                "Double Top", "Double Bottom",
                "Triple Top", "Triple Bottom",
                "Ascending Triangle", "Descending Triangle", "Symmetrical Triangle",
                "Bull Flag", "Bear Flag", "Pennant",
                "Rising Wedge", "Falling Wedge",
                "Cup and Handle", "Inverse Cup and Handle",
                "Channel Up", "Channel Down",
                "Support Bounce", "Resistance Rejection",
                "Breakout", "Breakdown",
                "Bullish Engulfing", "Bearish Engulfing",
                "Doji", "Hammer", "Shooting Star"
            ]


class CloudVisionAnalyzer:
    """
    Analyze trading charts using Google Gemini Vision API
    
    Benefits over local LLaVA:
    - Actually works on any hardware
    - 2-5 second response time
    - Higher quality analysis
    - Cost: ~$0.002 per image
    """
    
    def __init__(self, config: Optional[CloudVisionConfig] = None):
        self.config = config or CloudVisionConfig()
        self.api_available = self._check_api()
        self._last_request_time = 0
        self._request_count = 0
        
        # Stats tracking
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'total_latency': 0.0,
            'patterns_found': 0
        }
        
        if self.api_available:
            logger.info(f"☁️ Cloud Vision initialized with {self.config.provider}")
        else:
            logger.warning("⚠️ Cloud Vision API key not configured")
    
    def _check_api(self) -> bool:
        """Check if API is configured"""
        return bool(self.config.api_key)
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.batch_delay:
            time.sleep(self.config.batch_delay - elapsed)
        self._last_request_time = time.time()
    
    def _load_image(self, image_path: str) -> str:
        """Load and encode image as base64"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _build_prompt(self, symbol: str, timeframe: str) -> str:
        """Build analysis prompt for chart"""
        return f"""Analyze this {symbol} stock chart ({timeframe} timeframe) as an expert technical analyst.

IDENTIFY AND REPORT:

1. **PATTERNS** - Any chart patterns present:
{chr(10).join(f'   - {p}' for p in self.config.pattern_categories[:10])}

2. **TREND** - Overall price direction and strength

3. **SUPPORT/RESISTANCE** - Key price levels visible

4. **SIGNAL** - Trading signal quality (buy/sell/hold)

FORMAT YOUR RESPONSE EXACTLY AS:
PATTERNS: [list patterns found, or "None detected"]
TREND: [bullish/bearish/neutral]
TREND_STRENGTH: [strong/moderate/weak]
SUPPORT: [comma-separated price levels, or "None visible"]
RESISTANCE: [comma-separated price levels, or "None visible"]
SIGNAL: [strong_buy/buy/hold/sell/strong_sell]
CONFIDENCE: [0.0-1.0]
REASONING: [1-2 sentence explanation]

Be specific. If you see a pattern, name it. If you see price levels, list them."""

    def analyze_chart(self,
                     image_path: str,
                     symbol: str = "UNKNOWN",
                     timeframe: str = "1D") -> ChartAnalysisResult:
        """
        Analyze a chart image using Gemini Vision

        Args:
            image_path: Path to chart image
            symbol: Trading symbol
            timeframe: Chart timeframe

        Returns:
            ChartAnalysisResult with patterns and levels
        """
        start_time = time.time()

        if not self.api_available:
            return self._error_result("API key not configured", time.time() - start_time)

        try:
            # Rate limit
            self._rate_limit()

            # Load image
            image_data = self._load_image(image_path)

            # Build prompt
            prompt = self._build_prompt(symbol, timeframe)

            # Call appropriate API based on provider
            if self.config.provider == "glm":
                response = self._call_glm(prompt, image_data)
            elif self.config.provider == "claude":
                response = self._call_claude(prompt, image_data)
            elif self.config.provider == "openai":
                response = self._call_openai(prompt, image_data)
            else:
                response = self._call_gemini(prompt, image_data)

            # Parse response
            result = self._parse_response(response)
            result.latency = time.time() - start_time
            result.timestamp = time.time()

            # Update stats
            self.stats['total_requests'] += 1
            self.stats['successful'] += 1
            self.stats['total_latency'] += result.latency
            self.stats['patterns_found'] += len(result.patterns_detected)

            logger.info(f"✅ {symbol}: {len(result.patterns_detected)} patterns, "
                       f"{result.trend_direction} trend, {result.latency:.1f}s")

            return result

        except Exception as e:
            self.stats['total_requests'] += 1
            self.stats['failed'] += 1
            logger.error(f"❌ Chart analysis failed: {e}")
            return self._error_result(str(e), time.time() - start_time)

    def _call_glm(self, prompt: str, image_data: str) -> str:
        """Call GLM-4-Flash Vision API (Zhipu AI)"""
        import requests

        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

        payload = {
            "model": self.config.model,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', response.text)
            raise Exception(f"GLM API error: {error_msg}")

        result = response.json()

        # Extract text from response
        try:
            text = result['choices'][0]['message']['content']
            return text
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid GLM response format: {e}")

    def _call_gemini(self, prompt: str, image_data: str) -> str:
        """Call Gemini Vision API"""
        import requests

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
            }
        }

        response = requests.post(
            f"{url}?key={self.config.api_key}",
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        if response.status_code != 200:
            error_msg = response.json().get('error', {}).get('message', response.text)
            raise Exception(f"Gemini API error: {error_msg}")

        result = response.json()

        # Extract text from response
        try:
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid Gemini response format: {e}")

    def _call_claude(self, prompt: str, image_data: str) -> str:
        """Call Claude Vision API (Anthropic)"""
        import requests

        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', response.text)
            raise Exception(f"Claude API error: {error_msg}")

        result = response.json()

        # Extract text from response
        try:
            text = result['content'][0]['text']
            return text
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid Claude response format: {e}")

    def _call_openai(self, prompt: str, image_data: str) -> str:
        """Call OpenAI Vision API (GPT-4o/GPT-4o-mini)"""
        import requests

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

        payload = {
            "model": self.config.model,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )

        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', response.text)
            raise Exception(f"OpenAI API error: {error_msg}")

        result = response.json()

        # Extract text from response
        try:
            text = result['choices'][0]['message']['content']
            return text
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid OpenAI response format: {e}")

    def _parse_response(self, response: str) -> ChartAnalysisResult:
        """Parse structured response from Gemini"""

        # Extract fields using regex
        patterns = self._extract_field(response, "PATTERNS")
        trend = self._extract_field(response, "TREND")
        trend_strength = self._extract_field(response, "TREND_STRENGTH")
        support = self._extract_field(response, "SUPPORT")
        resistance = self._extract_field(response, "RESISTANCE")
        signal = self._extract_field(response, "SIGNAL")
        confidence = self._extract_confidence(response)
        reasoning = self._extract_field(response, "REASONING")

        # Parse patterns list
        pattern_list = []
        if patterns and patterns.lower() not in ["none detected", "none", "n/a", ""]:
            # Split by comma or newline
            for p in re.split(r'[,\n]', patterns):
                p = p.strip().strip('-').strip('*').strip()
                if p and len(p) > 2:
                    pattern_list.append(p)

        # Parse price levels
        support_levels = self._extract_prices(support)
        resistance_levels = self._extract_prices(resistance)

        # Map signal to quality
        signal_map = {
            'strong_buy': 'strong', 'buy': 'moderate',
            'hold': 'weak', 'sell': 'moderate', 'strong_sell': 'strong'
        }
        signal_quality = signal_map.get(signal.lower().replace(' ', '_'), 'weak') if signal else 'weak'

        return ChartAnalysisResult(
            patterns_detected=pattern_list,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            trend_direction=trend.lower() if trend else "neutral",
            trend_strength=trend_strength.lower() if trend_strength else "weak",
            confidence=confidence,
            reasoning=reasoning or "Analysis complete",
            raw_response=response,
            indicators_present=[],
            signal_quality=signal_quality,
            latency=0.0,
            timestamp=time.time(),
            success=True
        )

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field value from response"""
        pattern = rf"{field_name}:\s*(.+?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip().strip('[]')
        return ""

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score"""
        match = re.search(r"CONFIDENCE:\s*([\d.]+)", text, re.IGNORECASE)
        if match:
            try:
                return min(1.0, max(0.0, float(match.group(1))))
            except ValueError:
                pass
        return 0.5

    def _extract_prices(self, text: str) -> List[float]:
        """Extract price levels from text"""
        if not text or text.lower() in ["none visible", "none", "n/a"]:
            return []

        prices = []
        # Find all numbers that look like prices
        for match in re.finditer(r'\$?([\d,]+\.?\d*)', text):
            try:
                price = float(match.group(1).replace(',', ''))
                if 0.01 < price < 100000:  # Reasonable price range
                    prices.append(price)
            except ValueError:
                continue
        return prices

    def _error_result(self, error: str, latency: float) -> ChartAnalysisResult:
        """Create error result"""
        return ChartAnalysisResult(
            patterns_detected=[],
            support_levels=[],
            resistance_levels=[],
            trend_direction="neutral",
            trend_strength="weak",
            confidence=0.0,
            reasoning=f"Error: {error}",
            raw_response="",
            indicators_present=[],
            signal_quality="weak",
            latency=latency,
            timestamp=time.time(),
            success=False,
            error=error
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        avg_latency = (self.stats['total_latency'] / self.stats['successful']
                      if self.stats['successful'] > 0 else 0)
        return {
            'provider': self.config.provider,
            'model': self.config.model,
            'api_available': self.api_available,
            'total_requests': self.stats['total_requests'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'success_rate': (self.stats['successful'] / self.stats['total_requests'] * 100
                           if self.stats['total_requests'] > 0 else 0),
            'avg_latency': avg_latency,
            'patterns_found': self.stats['patterns_found']
        }

    def analyze_batch(self,
                     chart_paths: List[str],
                     symbol_extractor=None,
                     progress_callback=None) -> Dict[str, ChartAnalysisResult]:
        """
        Analyze multiple charts in batch

        Args:
            chart_paths: List of chart image paths
            symbol_extractor: Function to extract symbol from filename
            progress_callback: Function(current, total, result) for progress updates

        Returns:
            Dict mapping filename to ChartAnalysisResult
        """
        results = {}
        total = len(chart_paths)

        for i, path in enumerate(chart_paths, 1):
            filename = Path(path).name

            # Extract symbol from filename if extractor provided
            if symbol_extractor:
                symbol = symbol_extractor(filename)
            else:
                # Default: first part before underscore
                symbol = filename.split('_')[0] if '_' in filename else "UNKNOWN"

            # Analyze chart
            result = self.analyze_chart(path, symbol)
            results[filename] = result

            # Progress callback
            if progress_callback:
                progress_callback(i, total, result)

            logger.info(f"[{i}/{total}] {filename}: {result.trend_direction}, "
                       f"{len(result.patterns_detected)} patterns")

        return results


# Convenience function
def analyze_chart_cloud(image_path: str,
                        symbol: str = "UNKNOWN",
                        timeframe: str = "1D",
                        api_key: Optional[str] = None) -> ChartAnalysisResult:
    """
    Quick cloud chart analysis

    Args:
        image_path: Path to chart image
        symbol: Trading symbol
        timeframe: Chart timeframe
        api_key: Gemini API key (uses env var if not provided)

    Returns:
        ChartAnalysisResult

    Example:
        >>> result = analyze_chart_cloud("charts/AAPL_1D.png", "AAPL")
        >>> print(f"Patterns: {result.patterns_detected}")
        >>> print(f"Trend: {result.trend_direction}")
    """
    config = CloudVisionConfig(api_key=api_key)
    analyzer = CloudVisionAnalyzer(config)
    return analyzer.analyze_chart(image_path, symbol, timeframe)

