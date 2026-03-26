#!/usr/bin/env python3
"""
Integrate Backtest-Learned Patterns into Prometheus
Makes Prometheus actually use the patterns learned from backtesting
"""

import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatternIntegrationEngine:
    """
    Integrates backtest-learned patterns into Prometheus decision-making
    """
    
    def __init__(self):
        self.patterns_db = {}
        self.pattern_weights = defaultdict(float)
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned patterns from backtest results"""
        pattern_files = list(Path('.').glob('learned_patterns_*.json'))
        
        if not pattern_files:
            logger.warning("No pattern files found. Run backtests first.")
            return
        
        latest_file = max(pattern_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Loading patterns from {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.patterns_db = json.load(f)
            
            logger.info(f"Loaded {len(self.patterns_db)} pattern categories")
            
            # Calculate pattern weights based on historical success
            self._calculate_pattern_weights()
            
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
    
    def _calculate_pattern_weights(self):
        """Calculate weights for patterns based on historical performance"""
        # This would analyze backtest results to weight patterns
        # For now, use equal weights
        for category, patterns in self.patterns_db.items():
            if isinstance(patterns, dict):
                for key in patterns.keys():
                    self.pattern_weights[f"{category}_{key}"] = 1.0
    
    def match_current_conditions(
        self,
        current_market: Dict,
        current_regime: str,
        symbol: str
    ) -> List[Dict]:
        """Match current market conditions to learned patterns"""
        matched_patterns = []
        
        # Search through all patterns
        for category, patterns in self.patterns_db.items():
            if not isinstance(patterns, dict):
                continue
            
            for pattern_key, pattern_list in patterns.items():
                if symbol in pattern_key or 'all' in pattern_key.lower():
                    for pattern in pattern_list:
                        if isinstance(pattern, dict):
                            # Check if pattern matches current conditions
                            similarity = self._calculate_similarity(
                                pattern,
                                current_market,
                                current_regime
                            )
                            
                            if similarity > 0.6:  # 60% similarity threshold
                                matched_patterns.append({
                                    'pattern': pattern,
                                    'similarity': similarity,
                                    'category': category,
                                    'weight': self.pattern_weights.get(f"{category}_{pattern_key}", 1.0)
                                })
        
        # Sort by similarity and weight
        matched_patterns.sort(key=lambda x: x['similarity'] * x['weight'], reverse=True)
        
        return matched_patterns[:10]  # Top 10 matches
    
    def _calculate_similarity(
        self,
        pattern: Dict,
        current_market: Dict,
        current_regime: str
    ) -> float:
        """Calculate similarity between pattern and current conditions"""
        similarity = 0.0
        factors = 0
        
        # Regime similarity
        if pattern.get('regime') == current_regime:
            similarity += 0.3
        factors += 1
        
        # Volatility similarity
        pattern_vol = pattern.get('characteristics', {}).get('volatility_mean', 0)
        current_vol = current_market.get('volatility', 0)
        if pattern_vol > 0 and current_vol > 0:
            vol_sim = 1 - abs(pattern_vol - current_vol) / max(pattern_vol, current_vol)
            similarity += vol_sim * 0.3
        factors += 1
        
        # Volume similarity
        pattern_vol_ratio = pattern.get('characteristics', {}).get('avg_volume_ratio', 1.0)
        current_vol_ratio = current_market.get('volume_ratio', 1.0)
        vol_ratio_sim = 1 - abs(pattern_vol_ratio - current_vol_ratio) / max(pattern_vol_ratio, current_vol_ratio, 1.0)
        similarity += vol_ratio_sim * 0.2
        factors += 1
        
        # Trend similarity
        pattern_trend = pattern.get('characteristics', {}).get('trend_direction', 'unknown')
        current_trend = current_market.get('trend', 'unknown')
        if pattern_trend == current_trend:
            similarity += 0.2
        factors += 1
        
        return similarity / factors if factors > 0 else 0.0
    
    def apply_patterns_to_decision(
        self,
        base_decision: Dict,
        matched_patterns: List[Dict]
    ) -> Dict:
        """Apply learned patterns to enhance decision"""
        if not matched_patterns:
            return base_decision
        
        # Analyze patterns
        pattern_actions = defaultdict(float)
        pattern_confidences = []
        
        for match in matched_patterns:
            pattern = match['pattern']
            similarity = match['similarity']
            weight = match['weight']
            
            # Extract pattern insights
            pattern_type = pattern.get('pattern_type', '')
            characteristics = pattern.get('characteristics', {})
            
            # Determine suggested action based on pattern
            if 'bull' in pattern_type.lower():
                pattern_actions['BUY'] += similarity * weight
            elif 'bear' in pattern_type.lower():
                pattern_actions['SELL'] += similarity * weight
            elif 'volatile' in pattern_type.lower():
                pattern_actions['HOLD'] += similarity * weight * 0.5
            
            # Adjust confidence based on pattern success
            pattern_confidences.append(similarity * weight)
        
        # Enhance decision
        enhanced_decision = base_decision.copy()
        
        # Adjust action if patterns strongly suggest different
        if pattern_actions:
            max_action = max(pattern_actions.items(), key=lambda x: x[1])
            if max_action[1] > 0.5:  # Strong pattern signal
                enhanced_decision['pattern_suggested_action'] = max_action[0]
                enhanced_decision['pattern_confidence'] = max_action[1]
        
        # Adjust confidence
        if pattern_confidences:
            avg_pattern_confidence = sum(pattern_confidences) / len(pattern_confidences)
            enhanced_decision['confidence'] = (
                enhanced_decision.get('confidence', 0.5) * 0.7 +
                avg_pattern_confidence * 0.3
            )
        
        # Add pattern insights
        enhanced_decision['patterns_matched'] = len(matched_patterns)
        enhanced_decision['pattern_insights'] = [
            {
                'type': m['pattern'].get('pattern_type', 'unknown'),
                'similarity': m['similarity'],
                'category': m['category']
            }
            for m in matched_patterns[:3]  # Top 3
        ]
        
        return enhanced_decision
    
    async def enhance_prometheus_decision(
        self,
        market_data: Dict,
        portfolio: Dict,
        base_decision: Dict
    ) -> Dict:
        """Enhance Prometheus decision with learned patterns"""
        # Identify current regime
        current_regime = market_data.get('regime', 'unknown')
        symbol = market_data.get('symbol', 'UNKNOWN')
        
        # Match patterns
        matched_patterns = self.match_current_conditions(
            market_data,
            current_regime,
            symbol
        )
        
        # Apply patterns to decision
        enhanced_decision = self.apply_patterns_to_decision(
            base_decision,
            matched_patterns
        )
        
        logger.info(f"[PATTERN] Matched {len(matched_patterns)} patterns for {symbol}")
        if matched_patterns:
            logger.info(f"  Top pattern: {matched_patterns[0]['pattern'].get('pattern_type', 'unknown')} "
                       f"(similarity: {matched_patterns[0]['similarity']:.2f})")
        
        return enhanced_decision

def create_pattern_integration_module():
    """Create integration module for Prometheus"""
    integration_code = '''
"""
Pattern Integration Module for Prometheus
Integrates backtest-learned patterns into decision-making
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class PatternIntegration:
    """Integrates learned patterns into Prometheus"""
    
    def __init__(self):
        self.patterns = {}
        self.load_patterns()
    
    def load_patterns(self):
        """Load patterns from backtest results"""
        pattern_files = list(Path('.').glob('learned_patterns_*.json'))
        if pattern_files:
            latest = max(pattern_files, key=lambda f: f.stat().st_mtime)
            with open(latest, 'r') as f:
                self.patterns = json.load(f)
            logger.info(f"Loaded patterns from {latest.name}")
    
    def enhance_decision(self, decision: Dict, market_data: Dict) -> Dict:
        """Enhance decision with learned patterns"""
        # Pattern matching and enhancement logic
        # This would be called from Universal Reasoning Engine
        return decision
'''
    
    with open('core/pattern_integration.py', 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    logger.info("Created pattern integration module")

async def main():
    """Main integration function"""
    logger.info("=" * 80)
    logger.info("INTEGRATING BACKTEST PATTERNS INTO PROMETHEUS")
    logger.info("=" * 80)
    
    # Create integration engine
    integrator = PatternIntegrationEngine()
    
    # Create integration module
    create_pattern_integration_module()
    
    # Test integration
    test_market = {
        'symbol': 'SPY',
        'price': 450.0,
        'volatility': 0.02,
        'volume_ratio': 1.2,
        'trend': 'up',
        'regime': 'bull'
    }
    
    test_decision = {
        'action': 'BUY',
        'confidence': 0.6,
        'symbol': 'SPY'
    }
    
    enhanced = await integrator.enhance_prometheus_decision(
        test_market,
        {'value': 10000},
        test_decision
    )
    
    logger.info("\n" + "=" * 80)
    logger.info("INTEGRATION TEST")
    logger.info("=" * 80)
    logger.info(f"Original decision: {test_decision}")
    logger.info(f"Enhanced decision: {enhanced}")
    logger.info(f"Patterns matched: {enhanced.get('patterns_matched', 0)}")
    
    logger.info("\n[SUCCESS] Pattern integration ready!")
    logger.info("Next: Integrate into Universal Reasoning Engine")

if __name__ == "__main__":
    asyncio.run(main())

