
"""
Pattern Integration Module for Prometheus
Integrates backtest-learned patterns into decision-making
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class PatternIntegration:
    """Integrates learned patterns into Prometheus"""
    
    def __init__(self):
        self.patterns = {}
        self.pattern_weights = defaultdict(float)
        self.load_patterns()
    
    def load_patterns(self):
        """Load patterns from backtest results"""
        pattern_files = list(Path('.').glob('learned_patterns_*.json'))
        if pattern_files:
            latest = max(pattern_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
                logger.info(f"✅ Loaded patterns from {latest.name}")
                self._calculate_pattern_weights()
            except Exception as e:
                logger.warning(f"⚠️ Failed to load patterns: {e}")
        else:
            logger.info("ℹ️ No pattern files found - will use patterns once backtests complete")
    
    def _calculate_pattern_weights(self):
        """Calculate weights for patterns based on historical performance"""
        # Initialize weights - can be enhanced with actual performance data
        for category, patterns in self.patterns.items():
            if isinstance(patterns, dict):
                for key in patterns.keys():
                    self.pattern_weights[f"{category}_{key}"] = 1.0
    
    def match_patterns(
        self,
        market_data: Dict,
        current_regime: str = 'unknown',
        symbol: str = 'UNKNOWN'
    ) -> List[Dict]:
        """Match current market conditions to learned patterns"""
        if not self.patterns:
            logger.debug("No patterns loaded - returning empty list")
            return []
        
        matched_patterns = []
        
        # Extract current market characteristics
        current_vol = market_data.get('volatility', 0)
        current_vol_ratio = market_data.get('volume_ratio', 1.0)
        current_trend = market_data.get('trend', 'unknown')
        
        # DEBUG: Log incoming data
        logger.info(f"  📊 Pattern Match Input: symbol={symbol}, trend={current_trend}, vol={current_vol:.4f}, vol_ratio={current_vol_ratio:.2f}")
        
        # Clean symbol for matching (remove -USD suffix for crypto)
        clean_symbol = symbol.replace('-USD', '').replace('=X', '').upper()
        
        # DEBUG: Show what categories we have
        pattern_counts = {k: len(v) if isinstance(v, dict) else 0 for k, v in self.patterns.items()}
        logger.debug(f"  Pattern categories: {pattern_counts}")
        
        # Search through all patterns
        for category, patterns in self.patterns.items():
            if not isinstance(patterns, dict):
                continue
            if not patterns:  # Skip empty categories
                continue
            
            logger.debug(f"  Searching category '{category}' with {len(patterns)} pattern sets")
            
            for pattern_key, pattern_list in patterns.items():
                # Check if pattern is relevant to current symbol
                # Pattern keys are like "AAPL_1", "AAPL_5", "SPY_1", etc.
                pattern_symbol = pattern_key.split('_')[0] if '_' in pattern_key else pattern_key
                
                # Match if: exact symbol match, or "all" pattern, or broad market pattern (SPY/QQQ for stocks)
                is_symbol_match = (
                    clean_symbol == pattern_symbol or
                    pattern_symbol in clean_symbol or
                    'all' in pattern_key.lower() or
                    (pattern_symbol in ['SPY', 'QQQ'] and clean_symbol not in ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA'])  # Market index patterns apply to stocks
                )
                
                if is_symbol_match:
                    if not isinstance(pattern_list, list):
                        pattern_list = [pattern_list]
                    
                    for pattern in pattern_list:
                        if isinstance(pattern, dict):
                            similarity = self._calculate_similarity(
                                pattern,
                                market_data,
                                current_regime,
                                current_vol,
                                current_vol_ratio,
                                current_trend
                            )
                            
                            # DEBUG: Log similarity calculation
                            logger.debug(f"    Pattern {pattern_key}: similarity={similarity:.3f} (threshold=0.3)")
                            
                            if similarity > 0.3:  # Lowered threshold for better matching
                                logger.info(f"    ✅ MATCHED: {pattern_key} (sim={similarity:.3f})")
                                matched_patterns.append({
                                    'pattern': pattern,
                                    'similarity': similarity,
                                    'category': category,
                                    'pattern_key': pattern_key,
                                    'weight': self.pattern_weights.get(f"{category}_{pattern_key}", 1.0)
                                })
        
        # Sort by similarity * weight
        matched_patterns.sort(key=lambda x: x['similarity'] * x['weight'], reverse=True)
        
        logger.info(f"  📈 Pattern Match Result: {len(matched_patterns)} patterns matched for {symbol}")
        
        return matched_patterns[:10]  # Top 10 matches
    
    def _calculate_similarity(
        self,
        pattern: Dict,
        market_data: Dict,
        regime: str,
        current_vol: float,
        current_vol_ratio: float,
        current_trend: str
    ) -> float:
        """Calculate similarity between pattern and current conditions"""
        similarity = 0.0
        factors = 0
        
        characteristics = pattern.get('characteristics', {})
        pattern_type = pattern.get('pattern_type', '').lower()
        
        logger.debug(f"      Calculating similarity for pattern_type={pattern_type}")
        
        # Handle trend_strength patterns from backtest
        if 'trend_strength' in pattern_type or 'trend' in pattern_type:
            uptrend_periods = characteristics.get('uptrend_periods', 0)
            downtrend_periods = characteristics.get('downtrend_periods', 0)
            trend_strength = characteristics.get('trend_strength_avg', 0)
            
            logger.debug(f"      Trend pattern: up={uptrend_periods}, down={downtrend_periods}, strength={trend_strength:.4f}")
            
            # Calculate trend bias
            total_periods = uptrend_periods + downtrend_periods
            if total_periods > 0:
                trend_bias = (uptrend_periods - downtrend_periods) / total_periods
                logger.debug(f"      trend_bias={trend_bias:.4f}, current_trend={current_trend}")
                
                # Match if current market aligns with historical trend bias
                if current_trend == 'up' and trend_bias > 0:
                    similarity += 0.6  # Strong match
                    factors += 1
                    logger.debug(f"      Added 0.6 for UP trend match")
                elif current_trend == 'down' and trend_bias < 0:
                    similarity += 0.6  # Strong match
                    factors += 1
                    logger.debug(f"      Added 0.6 for DOWN trend match")
                elif current_trend == 'sideways':
                    similarity += 0.4  # Partial match
                    factors += 1
                    logger.debug(f"      Added 0.4 for sideways")
                else:
                    similarity += 0.2  # Some credit for having trend data
                    factors += 1
                    logger.debug(f"      Added 0.2 for other")
            
            # Trend strength similarity - always add this for trend patterns
            if trend_strength > 0:
                strength_bonus = min(0.3, trend_strength * 5)
                similarity += strength_bonus
                factors += 1
                logger.debug(f"      Added {strength_bonus:.4f} for trend_strength")
        
        # Regime similarity - only count if it matches
        pattern_regime = pattern.get('regime', '')
        if regime and (regime in pattern_type or pattern_regime == regime):
            similarity += 0.3
            factors += 1
            logger.debug(f"      Added 0.3 for regime match")
        
        # Volatility similarity - only if both values exist
        pattern_vol = characteristics.get('volatility_mean', 0)
        if pattern_vol > 0 and current_vol > 0:
            vol_sim = 1 - abs(pattern_vol - current_vol) / max(pattern_vol, current_vol, 0.01)
            if vol_sim > 0.5:  # Only count as factor if reasonably similar
                similarity += vol_sim * 0.3
                factors += 1
                logger.debug(f"      Added {vol_sim * 0.3:.4f} for volatility match")
        
        # Volume ratio similarity - only if both values exist
        pattern_vol_ratio = characteristics.get('avg_volume_ratio', 1.0)
        if pattern_vol_ratio > 0 and current_vol_ratio > 0 and not (current_vol_ratio != current_vol_ratio):  # Check for NaN
            vol_ratio_sim = 1 - abs(pattern_vol_ratio - current_vol_ratio) / max(pattern_vol_ratio, current_vol_ratio, 1.0)
            if vol_ratio_sim > 0.3:  # Only count as factor if somewhat similar
                similarity += vol_ratio_sim * 0.2
                factors += 1
                logger.debug(f"      Added {vol_ratio_sim * 0.2:.4f} for volume ratio match")
        
        # Calculate final similarity - don't divide by factors, just use sum
        # This allows stronger matches to accumulate
        if factors == 0:
            logger.debug(f"      No factors matched, returning 0")
            return 0.0
        
        # Use the raw sum - more factors = more confidence, not less
        # Cap at 1.0 for normalization
        final_sim = min(similarity, 1.0)
        logger.debug(f"      Similarity: raw={similarity:.3f}, factors={factors}, final={final_sim:.3f}")
        return final_sim
    
    def enhance_decision(
        self,
        base_decision: Dict,
        market_data: Dict,
        current_regime: str = 'unknown'
    ) -> Dict:
        """Enhance decision with learned patterns"""
        symbol = market_data.get('symbol', base_decision.get('symbol', 'UNKNOWN'))
        
        # DEBUG: Log what we're matching
        logger.debug(f"Pattern matching for symbol={symbol}, trend={market_data.get('trend', 'N/A')}, volatility={market_data.get('volatility', 'N/A')}")
        
        # Match patterns
        matched_patterns = self.match_patterns(market_data, current_regime, symbol)
        
        # Log if patterns found
        if matched_patterns:
            logger.debug(f"Found {len(matched_patterns)} matching patterns for {symbol}")
        
        if not matched_patterns:
            return base_decision
        
        # Analyze patterns
        pattern_actions = defaultdict(float)
        pattern_confidences = []
        pattern_insights = []
        
        for match in matched_patterns:
            pattern = match['pattern']
            similarity = match['similarity']
            weight = match['weight']
            
            pattern_type = pattern.get('pattern_type', '').lower()
            characteristics = pattern.get('characteristics', {})
            
            # Determine suggested action based on pattern
            if 'bull' in pattern_type:
                pattern_actions['BUY'] += similarity * weight
            elif 'bear' in pattern_type:
                pattern_actions['SELL'] += similarity * weight
            elif 'volatile' in pattern_type:
                pattern_actions['HOLD'] += similarity * weight * 0.5
            
            pattern_confidences.append(similarity * weight)
            pattern_insights.append({
                'type': pattern_type,
                'similarity': similarity,
                'category': match['category']
            })
        
        # Enhance decision
        enhanced_decision = base_decision.copy()
        
        # Adjust action if patterns strongly suggest different
        if pattern_actions:
            max_action = max(pattern_actions.items(), key=lambda x: x[1])
            if max_action[1] > 0.4:  # Strong pattern signal
                enhanced_decision['pattern_suggested_action'] = max_action[0]
                enhanced_decision['pattern_confidence'] = max_action[1]
                
                # If pattern confidence is high, consider adjusting action
                if max_action[1] > 0.6 and max_action[0] != base_decision.get('action', 'HOLD'):
                    # Pattern suggests different action - add to reasoning
                    enhanced_decision['pattern_override'] = True
                    enhanced_decision['pattern_reasoning'] = f"Historical pattern suggests {max_action[0]} (confidence: {max_action[1]:.2f})"
        
        # Adjust confidence based on patterns
        if pattern_confidences:
            avg_pattern_confidence = sum(pattern_confidences) / len(pattern_confidences)
            base_confidence = enhanced_decision.get('confidence', 0.5)
            enhanced_decision['confidence'] = (
                base_confidence * 0.7 +
                avg_pattern_confidence * 0.3
            )
        
        # Add pattern metadata
        enhanced_decision['patterns_matched'] = len(matched_patterns)
        enhanced_decision['pattern_insights'] = pattern_insights[:3]  # Top 3
        
        return enhanced_decision
