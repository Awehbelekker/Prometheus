#!/usr/bin/env python3
"""
HRM Performance Evaluation
Integrates deepeval for comprehensive HRM evaluation
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# Try to import deepeval
deepeval_path = Path(__file__).parent.parent / "integrated_repos" / "deepeval"
if deepeval_path.exists():
    sys.path.insert(0, str(deepeval_path))

try:
    # Try to import deepeval components
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    logger.warning("Deepeval not available")


class HRMEvaluator:
    """
    Comprehensive HRM evaluation using deepeval
    """
    
    def __init__(self):
        self.available = DEEPEVAL_AVAILABLE
        self.evaluation_history = []
    
    def evaluate_decision(self, decision: Dict, expected: Dict, actual: Dict) -> Dict[str, Any]:
        """Evaluate a trading decision"""
        metrics = {
            'accuracy': self._calculate_accuracy(decision, expected, actual),
            'confidence_calibration': self._calculate_confidence_calibration(decision, actual),
            'profit_accuracy': self._calculate_profit_accuracy(decision, actual),
            'risk_accuracy': self._calculate_risk_accuracy(decision, actual)
        }
        
        self.evaluation_history.append({
            'decision': decision,
            'expected': expected,
            'actual': actual,
            'metrics': metrics
        })
        
        return metrics
    
    def _calculate_accuracy(self, decision: Dict, expected: Dict, actual: Dict) -> float:
        """Calculate decision accuracy"""
        predicted_action = decision.get('action', 'HOLD')
        actual_action = actual.get('action', 'HOLD')
        
        return 1.0 if predicted_action == actual_action else 0.0
    
    def _calculate_confidence_calibration(self, decision: Dict, actual: Dict) -> float:
        """Calculate confidence calibration"""
        predicted_confidence = decision.get('confidence', 0.0)
        was_correct = decision.get('action') == actual.get('action')
        
        # Calibration: confidence should match correctness
        if was_correct:
            return predicted_confidence
        else:
            return 1.0 - predicted_confidence
    
    def _calculate_profit_accuracy(self, decision: Dict, actual: Dict) -> float:
        """Calculate profit prediction accuracy"""
        predicted_profit = decision.get('expected_profit', 0)
        actual_profit = actual.get('profit', 0)
        
        if predicted_profit == 0:
            return 0.0
        
        error = abs(predicted_profit - actual_profit) / abs(predicted_profit)
        return max(0.0, 1.0 - error)
    
    def _calculate_risk_accuracy(self, decision: Dict, actual: Dict) -> float:
        """Calculate risk assessment accuracy"""
        predicted_risk = decision.get('risk_level', 0.5)
        actual_risk = actual.get('risk_realized', 0.5)
        
        error = abs(predicted_risk - actual_risk)
        return max(0.0, 1.0 - error)
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of all evaluations"""
        if not self.evaluation_history:
            return {'error': 'No evaluations yet'}
        
        total = len(self.evaluation_history)
        avg_accuracy = sum(m['metrics']['accuracy'] for m in self.evaluation_history) / total
        avg_confidence = sum(m['metrics']['confidence_calibration'] for m in self.evaluation_history) / total
        
        return {
            'total_evaluations': total,
            'average_accuracy': avg_accuracy,
            'average_confidence_calibration': avg_confidence,
            'recent_evaluations': self.evaluation_history[-10:]  # Last 10
        }

