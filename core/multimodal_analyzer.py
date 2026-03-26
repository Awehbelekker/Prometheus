"""
Multimodal Chart Analyzer for PROMETHEUS Trading Platform

Uses LLaVA 7B (or other vision-language models) to analyze:
- Trading charts and candlestick patterns
- Financial reports with images
- News articles with charts/graphs
- Technical indicator visualizations
"""

import os
import logging
import base64
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import requests

logger = logging.getLogger(__name__)


@dataclass
class ChartAnalysisResult:
    """Result from multimodal chart analysis"""
    # Primary findings
    patterns_detected: List[str]
    support_levels: List[float]
    resistance_levels: List[float]
    trend_direction: str  # 'bullish', 'bearish', 'neutral'
    trend_strength: str  # 'strong', 'moderate', 'weak'
    
    # Confidence and reasoning
    confidence: float
    reasoning: str
    raw_response: str
    
    # Technical indicators (if visible in chart)
    indicators_present: List[str]
    signal_quality: str  # 'strong', 'moderate', 'weak', 'conflicting'
    
    # Metadata
    latency: float
    timestamp: float
    success: bool
    error: Optional[str] = None


@dataclass
class MultimodalConfig:
    """Configuration for multimodal analysis"""
    # Model settings
    model: str = "llava:7b"
    endpoint: str = "http://localhost:11434"
    
    # Analysis parameters
    temperature: float = 0.3  # Lower for more consistent pattern recognition
    max_tokens: int = 2048  # Increased for more detailed analysis
    timeout: int = 180  # Increased to 3 minutes for complex images
    
    # Pattern detection thresholds
    min_confidence: float = 0.6
    pattern_categories: List[str] = None
    
    def __post_init__(self):
        if self.pattern_categories is None:
            self.pattern_categories = [
                "Head and Shoulders",
                "Double Top/Bottom",
                "Triangle (Ascending/Descending/Symmetrical)",
                "Flag/Pennant",
                "Wedge (Rising/Falling)",
                "Channel (Up/Down)",
                "Cup and Handle",
                "Breakout/Breakdown"
            ]


class MultimodalChartAnalyzer:
    """
    Analyze trading charts using vision-language models
    
    Capabilities:
    - Pattern recognition from chart images
    - Support/resistance level identification
    - Trend analysis
    - Technical indicator interpretation
    - Multi-timeframe analysis
    """
    
    def __init__(self, config: Optional[MultimodalConfig] = None):
        """
        Initialize multimodal analyzer
        
        Args:
            config: Analyzer configuration (uses defaults if None)
        """
        self.config = config or MultimodalConfig()
        self.model_available = self._check_model_availability()
        
        if self.model_available:
            logger.info(f"✅ Multimodal analyzer initialized with {self.config.model}")
        else:
            logger.warning(f"⚠️ Model {self.config.model} not available via Ollama")
    
    def _check_model_availability(self) -> bool:
        """Check if the multimodal model is available"""
        try:
            response = requests.get(f"{self.config.endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                # Check for exact match first
                if self.config.model in model_names:
                    logger.info(f"Found exact model match: {self.config.model}")
                    return True
                
                # Check for partial match (e.g., "llava" in "llava:7b")
                for name in model_names:
                    if 'llava' in name.lower() or 'vision' in name.lower():
                        logger.info(f"Found vision model: {name}, using it instead of {self.config.model}")
                        self.config.model = name  # Use the available model
                        return True
                
                logger.warning(f"No vision model found. Available: {model_names}")
                return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
        return False
    
    def analyze_chart(self, 
                     image_path: str, 
                     context: Optional[Dict[str, Any]] = None) -> ChartAnalysisResult:
        """
        Analyze a trading chart image
        
        Args:
            image_path: Path to chart image file
            context: Trading context (symbol, timeframe, etc.)
        
        Returns:
            ChartAnalysisResult with detected patterns and analysis
        """
        
        if not self.model_available:
            logger.warning("Model not available - attempting to re-check")
            self.model_available = self._check_model_availability()
            if not self.model_available:
                return self._fallback_result("Model not available after re-check")
        
        start_time = time.time()
        symbol = context.get('symbol', 'Unknown') if context else 'Unknown'
        
        try:
            # Load and encode image
            logger.info(f"Loading image: {image_path}")
            image_data = self._load_image(image_path)
            logger.info(f"Image loaded: {len(image_data)} bytes (base64)")
            
            # Build analysis prompt
            prompt = self._build_chart_analysis_prompt(context)
            
            # Call multimodal model
            logger.info(f"Calling LLaVA for {symbol}... (may take 30-120s)")
            response = self._call_model(prompt, image_data)
            
            if not response:
                logger.warning(f"Empty response from LLaVA for {symbol}")
                return self._fallback_result("Empty model response", time.time() - start_time)
            
            # Parse response
            result = self._parse_chart_analysis(response, context)
            
            result.latency = time.time() - start_time
            result.timestamp = time.time()
            result.raw_response = response[:500]  # Store first 500 chars for debugging
            result.success = True
            
            pattern_count = len(result.patterns_detected) if result.patterns_detected else 0
            logger.info(f"[OK] {symbol}: {pattern_count} patterns, trend={result.trend_direction}, conf={result.confidence:.2f}, {result.latency:.1f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Chart analysis failed for {symbol}: {e}")
            latency = time.time() - start_time
            return self._fallback_result(str(e), latency)
    
    def analyze_financial_report(self,
                                image_path: str,
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze financial report with charts/graphs
        
        Args:
            image_path: Path to report image
            context: Report context (company, quarter, etc.)
        
        Returns:
            Extracted financial data and insights
        """
        
        if not self.model_available:
            return {"error": "Model not available"}
        
        try:
            image_data = self._load_image(image_path)
            
            prompt = f"""Analyze this financial report image.
            
Extract:
1. Key financial metrics (revenue, profit, margins, etc.)
2. Trends visible in charts/graphs
3. Notable highlights or concerns
4. Year-over-year comparisons

Company: {context.get('company', 'Unknown') if context else 'Unknown'}
Period: {context.get('period', 'Unknown') if context else 'Unknown'}

Provide structured data extraction."""
            
            response = self._call_model(prompt, image_data)
            
            return {
                "success": True,
                "extracted_data": response,
                "context": context,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Financial report analysis failed: {e}")
            return {"error": str(e), "success": False}
    
    def analyze_news_image(self,
                          image_path: str,
                          article_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze charts/graphs in news articles
        
        Args:
            image_path: Path to news image
            article_text: Associated article text
        
        Returns:
            Analysis of visual content
        """
        
        if not self.model_available:
            return {"error": "Model not available"}
        
        try:
            image_data = self._load_image(image_path)
            
            prompt = """Analyze this news article image.

Identify:
1. Type of chart/graph shown
2. Key data points and trends
3. What story the visual is telling
4. Bullish or bearish implications

Provide concise analysis."""
            
            if article_text:
                prompt += f"\n\nRelated article context:\n{article_text[:500]}"
            
            response = self._call_model(prompt, image_data)
            
            return {
                "success": True,
                "analysis": response,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ News image analysis failed: {e}")
            return {"error": str(e), "success": False}
    
    def _load_image(self, image_path: str) -> str:
        """Load and encode image as base64"""
        
        path = Path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(path, 'rb') as f:
            image_bytes = f.read()
        
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _build_chart_analysis_prompt(self, context: Optional[Dict[str, Any]]) -> str:
        """Build comprehensive chart analysis prompt"""
        
        symbol = context.get('symbol', 'Unknown') if context else 'Unknown'
        timeframe = context.get('timeframe', 'Unknown') if context else 'Unknown'
        
        prompt = f"""You are an expert technical analyst. Analyze this trading chart for {symbol} on {timeframe} timeframe.

**ANALYZE AND IDENTIFY:**

1. **Chart Patterns** (if present):
{chr(10).join(f'   - {p}' for p in self.config.pattern_categories)}

2. **Support and Resistance Levels**:
   - Identify key price levels
   - Provide specific prices
   - Note strength (strong/weak)

3. **Trend Analysis**:
   - Direction: bullish/bearish/neutral
   - Strength: strong/moderate/weak
   - Consistency across timeframe

4. **Technical Indicators** (if visible):
   - Moving averages
   - RSI, MACD, Volume
   - Any other indicators shown

5. **Trading Signal Quality**:
   - Strong buy/sell signals
   - Conflicting signals
   - Wait-and-see zones

**FORMAT YOUR RESPONSE AS:**

PATTERNS: [List detected patterns or "None detected"]
SUPPORT: [Comma-separated price levels]
RESISTANCE: [Comma-separated price levels]
TREND: [bullish/bearish/neutral]
STRENGTH: [strong/moderate/weak]
INDICATORS: [List visible indicators]
SIGNAL: [strong/moderate/weak/conflicting]
CONFIDENCE: [0.0-1.0]
REASONING: [Brief explanation of analysis]

Be specific with price levels and pattern names. If uncertain, indicate confidence level."""
        
        return prompt
    
    def _call_model(self, prompt: str, image_data: str) -> str:
        """Call multimodal model via Ollama API"""
        
        url = f"{self.config.endpoint}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        logger.debug(f"Calling {self.config.model} with {len(image_data)} bytes image data")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            if response_text:
                logger.debug(f"LLaVA response length: {len(response_text)} chars")
            else:
                logger.warning("LLaVA returned empty response")
            
            return response_text
            
        except requests.exceptions.Timeout:
            logger.error(f"LLaVA timeout after {self.config.timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"LLaVA request failed: {e}")
            raise
    
    def _parse_chart_analysis(self, 
                             response: str, 
                             context: Optional[Dict[str, Any]]) -> ChartAnalysisResult:
        """Parse structured response from model"""
        
        # Extract structured fields
        patterns = self._extract_field(response, "PATTERNS")
        support = self._extract_prices(response, "SUPPORT")
        resistance = self._extract_prices(response, "RESISTANCE")
        trend = self._extract_field(response, "TREND")
        strength = self._extract_field(response, "STRENGTH")
        indicators = self._extract_field(response, "INDICATORS")
        signal = self._extract_field(response, "SIGNAL")
        confidence = self._extract_confidence(response)
        reasoning = self._extract_field(response, "REASONING")
        
        # Parse patterns list
        pattern_list = []
        if patterns and patterns.lower() != "none detected":
            pattern_list = [p.strip() for p in patterns.split(',') if p.strip()]
        
        # Parse indicators list
        indicator_list = []
        if indicators:
            indicator_list = [i.strip() for i in indicators.split(',') if i.strip()]
        
        return ChartAnalysisResult(
            patterns_detected=pattern_list,
            support_levels=support,
            resistance_levels=resistance,
            trend_direction=trend.lower() if trend else "neutral",
            trend_strength=strength.lower() if strength else "weak",
            confidence=confidence,
            reasoning=reasoning or "No reasoning provided",
            raw_response=response,
            indicators_present=indicator_list,
            signal_quality=signal.lower() if signal else "weak",
            latency=0.0,  # Set by caller
            timestamp=0.0,  # Set by caller
            success=True
        )
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field value from structured response"""
        
        import re
        pattern = rf"{field_name}:\s*(.+?)(?=\n[A-Z]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_prices(self, text: str, field_name: str) -> List[float]:
        """Extract price levels from response"""
        
        field_text = self._extract_field(text, field_name)
        
        if not field_text:
            return []
        
        import re
        # Extract numbers (price levels)
        prices = re.findall(r'\d+\.?\d*', field_text)
        
        return [float(p) for p in prices if p]
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score"""
        
        conf_text = self._extract_field(text, "CONFIDENCE")
        
        if not conf_text:
            return 0.5
        
        import re
        # Look for decimal number
        match = re.search(r'(\d+\.?\d*)', conf_text)
        
        if match:
            value = float(match.group(1))
            # Normalize to 0-1 range
            if value > 1.0:
                value = value / 100.0
            return min(1.0, max(0.0, value))
        
        return 0.5
    
    def _fallback_result(self, error: str, latency: float = 0.0) -> ChartAnalysisResult:
        """Create fallback result for errors"""
        
        return ChartAnalysisResult(
            patterns_detected=[],
            support_levels=[],
            resistance_levels=[],
            trend_direction="neutral",
            trend_strength="weak",
            confidence=0.0,
            reasoning=f"Analysis unavailable: {error}",
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
        
        return {
            'model': self.config.model,
            'available': self.model_available,
            'endpoint': self.config.endpoint,
            'patterns_supported': len(self.config.pattern_categories)
        }


# Convenience function for quick chart analysis
def analyze_trading_chart(image_path: str, 
                         symbol: str,
                         timeframe: str = "1D") -> ChartAnalysisResult:
    """
    Quick chart analysis with default configuration
    
    Args:
        image_path: Path to chart image
        symbol: Trading symbol (e.g., "AAPL")
        timeframe: Chart timeframe (e.g., "1D", "4H")
    
    Returns:
        ChartAnalysisResult with patterns and levels
    
    Example:
        >>> result = analyze_trading_chart("aapl_chart.png", "AAPL", "1D")
        >>> print(f"Patterns: {result.patterns_detected}")
        >>> print(f"Trend: {result.trend_direction} ({result.trend_strength})")
        >>> print(f"Support: {result.support_levels}")
        >>> print(f"Resistance: {result.resistance_levels}")
    """
    
    analyzer = MultimodalChartAnalyzer()
    
    context = {
        'symbol': symbol,
        'timeframe': timeframe
    }
    
    return analyzer.analyze_chart(image_path, context)


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("MULTIMODAL CHART ANALYZER - TEST")
    print("="*80)
    print()
    
    # Initialize analyzer
    analyzer = MultimodalChartAnalyzer()
    
    print(f"Analyzer Status:")
    stats = analyzer.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("Ready to analyze charts!")
    print("="*80)
    print()
    print("Usage:")
    print("  from core.multimodal_analyzer import analyze_trading_chart")
    print("  result = analyze_trading_chart('chart.png', 'AAPL', '1D')")
    print("  print(result.patterns_detected)")

