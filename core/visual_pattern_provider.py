"""
Visual Pattern Provider for PROMETHEUS

Provides visual chart pattern data to the learning engine and trading intelligence.
Acts as a bridge between:
- Cloud Vision Analyzer (Gemini) 
- Local LLaVA (when hardware supports it)
- Stored pattern data (visual_ai_patterns.json)

This allows PROMETHEUS to use visual patterns in trading decisions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VisualPatternProvider:
    """
    Provides visual chart patterns to PROMETHEUS trading systems.
    
    Data Sources:
    1. visual_ai_patterns.json - Stored analysis results
    2. CloudVisionAnalyzer - Real-time cloud analysis
    3. MultimodalChartAnalyzer - Local LLaVA (if available)
    """
    
    def __init__(self, patterns_file: str = "visual_ai_patterns.json"):
        self.patterns_file = Path(patterns_file)
        self.patterns: Dict[str, Any] = {}
        self.pattern_summary: Dict[str, int] = {}
        self.last_updated: Optional[datetime] = None
        
        # Load stored patterns
        self._load_patterns()
        
        logger.info(f"📊 Visual Pattern Provider initialized with {len(self.patterns)} patterns")
    
    def _load_patterns(self):
        """Load patterns from JSON file"""
        if not self.patterns_file.exists():
            logger.warning(f"Patterns file not found: {self.patterns_file}")
            return
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
            
            self.patterns = data.get('patterns', {})
            self.pattern_summary = data.get('pattern_summary', {})
            
            if data.get('last_updated'):
                self.last_updated = datetime.fromisoformat(data['last_updated'])
            
            # Count successful analyses
            successful = sum(1 for p in self.patterns.values() 
                           if p.get('patterns') or p.get('confidence', 0) > 0.5)
            
            logger.info(f"Loaded {len(self.patterns)} patterns ({successful} with detections)")
            
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
    
    def reload(self):
        """Reload patterns from file"""
        self._load_patterns()
    
    def get_patterns_for_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all visual patterns for a specific symbol.
        
        Returns list of pattern data from analyzed charts.
        """
        results = []
        symbol_upper = symbol.upper()
        
        for filename, data in self.patterns.items():
            if filename.startswith(symbol_upper + "_"):
                results.append({
                    'chart': filename,
                    'patterns': data.get('patterns', []),
                    'trend': data.get('trend', 'neutral'),
                    'trend_strength': data.get('trend_strength', 'weak'),
                    'support': data.get('support', []),
                    'resistance': data.get('resistance', []),
                    'confidence': data.get('confidence', 0.0),
                    'signal': data.get('signal', 'weak'),
                    'analyzed_at': data.get('analyzed_at')
                })
        
        return sorted(results, key=lambda x: x.get('analyzed_at', ''), reverse=True)
    
    def get_latest_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the most recent visual signal for a symbol"""
        patterns = self.get_patterns_for_symbol(symbol)
        if patterns:
            return patterns[0]
        return None
    
    def get_trend_consensus(self, symbol: str) -> Dict[str, Any]:
        """
        Get trend consensus across all charts for a symbol.
        
        Useful for confirming text-based AI signals.
        """
        patterns = self.get_patterns_for_symbol(symbol)
        
        if not patterns:
            return {'trend': 'unknown', 'confidence': 0.0, 'charts_analyzed': 0}
        
        bullish = sum(1 for p in patterns if p['trend'] == 'bullish')
        bearish = sum(1 for p in patterns if p['trend'] == 'bearish')
        total = len(patterns)
        
        if bullish > bearish:
            trend = 'bullish'
            confidence = bullish / total
        elif bearish > bullish:
            trend = 'bearish'
            confidence = bearish / total
        else:
            trend = 'neutral'
            confidence = 0.5
        
        # Get common patterns
        all_patterns = []
        for p in patterns:
            all_patterns.extend(p.get('patterns', []))
        
        pattern_counts = {}
        for p in all_patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        
        top_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])[:5]
        
        return {
            'trend': trend,
            'confidence': confidence,
            'charts_analyzed': total,
            'bullish_charts': bullish,
            'bearish_charts': bearish,
            'top_patterns': top_patterns,
            'avg_confidence': sum(p['confidence'] for p in patterns) / total if patterns else 0
        }
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get overall pattern statistics"""
        return {
            'total_charts': len(self.patterns),
            'pattern_summary': self.pattern_summary,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'top_patterns': sorted(self.pattern_summary.items(), key=lambda x: -x[1])[:10]
        }

    def enhance_trading_signal(self, symbol: str, base_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a text-based AI trading signal with visual pattern data.

        Args:
            symbol: Trading symbol
            base_signal: Signal from text-based AI (DeepSeek, etc.)

        Returns:
            Enhanced signal with visual confirmation
        """
        visual_data = self.get_trend_consensus(symbol)

        if visual_data['charts_analyzed'] == 0:
            return base_signal  # No visual data available

        enhanced = base_signal.copy()

        # Add visual confirmation
        base_direction = base_signal.get('signal', 'HOLD').upper()
        visual_trend = visual_data['trend']

        # Check for confirmation
        confirmed = False
        if base_direction in ['BUY', 'STRONG_BUY'] and visual_trend == 'bullish':
            confirmed = True
        elif base_direction in ['SELL', 'STRONG_SELL'] and visual_trend == 'bearish':
            confirmed = True
        elif base_direction == 'HOLD' and visual_trend == 'neutral':
            confirmed = True

        # Adjust confidence based on visual confirmation
        base_confidence = base_signal.get('confidence', 0.5)

        if confirmed:
            # Boost confidence when visual confirms
            enhanced['confidence'] = min(0.95, base_confidence * 1.2)
            enhanced['visual_confirmed'] = True
        else:
            # Reduce confidence when visual contradicts
            enhanced['confidence'] = base_confidence * 0.8
            enhanced['visual_confirmed'] = False

        # Add visual data to signal
        enhanced['visual_analysis'] = {
            'trend': visual_trend,
            'visual_confidence': visual_data['confidence'],
            'charts_analyzed': visual_data['charts_analyzed'],
            'top_patterns': visual_data['top_patterns'],
            'confirmation': 'CONFIRMED' if confirmed else 'CONFLICTING'
        }

        # Add reasoning update
        if confirmed:
            enhanced['reasoning'] = enhanced.get('reasoning', '') + \
                f" [Visual AI confirms {visual_trend} trend from {visual_data['charts_analyzed']} charts]"
        else:
            enhanced['reasoning'] = enhanced.get('reasoning', '') + \
                f" [Visual AI shows {visual_trend} trend - potential conflict]"

        return enhanced

    def get_symbols_with_patterns(self) -> List[str]:
        """Get list of symbols that have visual pattern data"""
        symbols = set()
        for filename in self.patterns.keys():
            if '_' in filename:
                symbol = filename.split('_')[0]
                symbols.add(symbol)
        return sorted(symbols)

    def has_data_for_symbol(self, symbol: str) -> bool:
        """Check if visual data exists for a symbol"""
        symbol_upper = symbol.upper()
        for filename in self.patterns.keys():
            if filename.startswith(symbol_upper + "_"):
                return True
        return False


# Global instance for easy access
_provider_instance: Optional[VisualPatternProvider] = None

def get_visual_pattern_provider() -> VisualPatternProvider:
    """Get or create the global visual pattern provider"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = VisualPatternProvider()
    return _provider_instance


def enhance_signal_with_visual(symbol: str, signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to enhance a trading signal with visual data.

    Usage:
        signal = get_ai_trading_signal(symbol)
        enhanced = enhance_signal_with_visual(symbol, signal)
    """
    provider = get_visual_pattern_provider()
    return provider.enhance_trading_signal(symbol, signal)

