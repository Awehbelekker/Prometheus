#!/usr/bin/env python3
"""
Intelligence Benchmark - Compare Reasoning Capabilities
Tests decision quality, confidence calibration, and reasoning depth
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from core.hrm_integration import HRMTradingEngine as OldHRMEngine
    from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
    OLD_AVAILABLE = True
except ImportError:
    OLD_AVAILABLE = False

try:
    from core.ultimate_trading_system import UltimateTradingSystem
    NEW_AVAILABLE = True
except ImportError:
    NEW_AVAILABLE = False


class IntelligenceBenchmark:
    """
    Benchmark intelligence and reasoning capabilities
    """
    
    def __init__(self):
        self.test_scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self) -> List[Dict]:
        """Create diverse test scenarios"""
        scenarios = [
            {
                'name': 'Bull Market',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 150.0,
                    'volume': 1000000,
                    'indicators': {'rsi': 70, 'macd': 1.5, 'volatility': 0.01}
                },
                'expected': 'BUY'
            },
            {
                'name': 'Bear Market',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 150.0,
                    'volume': 1000000,
                    'indicators': {'rsi': 30, 'macd': -1.5, 'volatility': 0.01}
                },
                'expected': 'SELL'
            },
            {
                'name': 'High Volatility',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 150.0,
                    'volume': 2000000,
                    'indicators': {'rsi': 50, 'macd': 0, 'volatility': 0.05}
                },
                'expected': 'HOLD'
            },
            {
                'name': 'Strong Trend',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 150.0,
                    'volume': 1500000,
                    'indicators': {'rsi': 65, 'macd': 1.2, 'volatility': 0.02}
                },
                'expected': 'BUY'
            },
            {
                'name': 'Uncertain Market',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 150.0,
                    'volume': 800000,
                    'indicators': {'rsi': 50, 'macd': 0.1, 'volatility': 0.015}
                },
                'expected': 'HOLD'
            }
        ]
        return scenarios
    
    async def benchmark_intelligence(self):
        """Benchmark intelligence capabilities"""
        logger.info("="*80)
        logger.info("INTELLIGENCE BENCHMARK")
        logger.info("Comparing Old vs Enhanced Prometheus Reasoning")
        logger.info("="*80)
        
        results = {}
        
        # Test Old System
        if OLD_AVAILABLE:
            old_results = await self._test_system("Old Prometheus", OldHRMEngine(device='cpu'))
            results['old'] = old_results
        
        # Test New System
        if NEW_AVAILABLE:
            new_results = await self._test_system("Enhanced Prometheus", UltimateTradingSystem())
            results['new'] = new_results
        
        # Compare
        if 'old' in results and 'new' in results:
            self._compare_intelligence(results['old'], results['new'])
        
        return results
    
    async def _test_system(self, system_name: str, system) -> Dict[str, Any]:
        """Test a system on all scenarios"""
        logger.info(f"\n{'='*80}")
        logger.info(f"TESTING: {system_name}")
        logger.info(f"{'='*80}")
        
        decisions = []
        confidences = []
        decision_times = []
        reasoning_sources = []
        
        for scenario in self.test_scenarios:
            market_data = scenario['market_data']
            expected = scenario['expected']
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                if system_name == "Old Prometheus":
                    context = HRMReasoningContext(
                        market_data=market_data,
                        user_profile={},
                        trading_history=[],
                        current_portfolio={},
                        risk_preferences={},
                        reasoning_level=HRMReasoningLevel.HIGH_LEVEL
                    )
                    decision = system.make_hierarchical_decision(context)
                    num_sources = 1  # Old system has single source
                else:
                    decision = system.make_ultimate_decision(
                        market_data=market_data,
                        portfolio={},
                        context={}
                    )
                    num_sources = decision.get('num_sources', 1)
                
                elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
                
                action = decision.get('action', 'HOLD')
                confidence = decision.get('confidence', 0.0)
                
                decisions.append({
                    'scenario': scenario['name'],
                    'action': action,
                    'expected': expected,
                    'correct': action == expected,
                    'confidence': confidence
                })
                
                confidences.append(confidence)
                decision_times.append(elapsed)
                reasoning_sources.append(num_sources)
                
                logger.info(f"  {scenario['name']}: {action} (confidence: {confidence:.3f}, "
                          f"expected: {expected}, correct: {action == expected}, "
                          f"sources: {num_sources}, time: {elapsed:.2f}ms)")
                
            except Exception as e:
                logger.warning(f"  {scenario['name']}: Failed - {e}")
                decisions.append({
                    'scenario': scenario['name'],
                    'action': 'ERROR',
                    'expected': expected,
                    'correct': False,
                    'confidence': 0.0
                })
        
        # Calculate metrics
        accuracy = sum(1 for d in decisions if d['correct']) / len(decisions) if decisions else 0
        avg_confidence = np.mean(confidences) if confidences else 0
        avg_decision_time = np.mean(decision_times) if decision_times else 0
        avg_sources = np.mean(reasoning_sources) if reasoning_sources else 1
        
        results = {
            'system_name': system_name,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'avg_decision_time_ms': avg_decision_time,
            'avg_reasoning_sources': avg_sources,
            'decisions': decisions
        }
        
        logger.info(f"\n{system_name} Results:")
        logger.info(f"  Accuracy: {accuracy*100:.2f}%")
        logger.info(f"  Avg Confidence: {avg_confidence:.3f}")
        logger.info(f"  Avg Decision Time: {avg_decision_time:.2f}ms")
        logger.info(f"  Avg Reasoning Sources: {avg_sources:.1f}")
        
        return results
    
    def _compare_intelligence(self, old_results: Dict, new_results: Dict):
        """Compare intelligence metrics"""
        logger.info("\n" + "="*80)
        logger.info("INTELLIGENCE COMPARISON")
        logger.info("="*80)
        
        print(f"\n{'Metric':<30} {'Old':>15} {'Enhanced':>15} {'Improvement':>15}")
        print("-"*80)
        
        metrics = {
            'Accuracy': {
                'old': old_results['accuracy'] * 100,
                'new': new_results['accuracy'] * 100,
                'improvement': (new_results['accuracy'] - old_results['accuracy']) / old_results['accuracy'] * 100 if old_results['accuracy'] > 0 else 0
            },
            'Avg Confidence': {
                'old': old_results['avg_confidence'],
                'new': new_results['avg_confidence'],
                'improvement': (new_results['avg_confidence'] - old_results['avg_confidence']) / old_results['avg_confidence'] * 100 if old_results['avg_confidence'] > 0 else 0
            },
            'Decision Time (ms)': {
                'old': old_results['avg_decision_time_ms'],
                'new': new_results['avg_decision_time_ms'],
                'improvement': ((old_results['avg_decision_time_ms'] - new_results['avg_decision_time_ms']) / old_results['avg_decision_time_ms'] * 100) if old_results['avg_decision_time_ms'] > 0 else 0
            },
            'Reasoning Sources': {
                'old': old_results['avg_reasoning_sources'],
                'new': new_results['avg_reasoning_sources'],
                'improvement': (new_results['avg_reasoning_sources'] - old_results['avg_reasoning_sources']) / old_results['avg_reasoning_sources'] * 100 if old_results['avg_reasoning_sources'] > 0 else 0
            }
        }
        
        for metric, data in metrics.items():
            old_val = data['old']
            new_val = data['new']
            improvement = data['improvement']
            
            if 'Time' in metric:
                sign = "↓" if improvement > 0 else "↑"
            else:
                sign = "↑" if improvement > 0 else "↓"
            
            print(f"{metric:<30} {old_val:>15.2f} {new_val:>15.2f} {sign}{abs(improvement):>14.2f}%")
        
        print("\n" + "="*80)
        print("INTELLIGENCE ASSESSMENT")
        print("="*80)
        
        accuracy_improvement = metrics['Accuracy']['improvement']
        confidence_improvement = metrics['Avg Confidence']['improvement']
        sources_improvement = metrics['Reasoning Sources']['improvement']
        
        if accuracy_improvement > 0 and confidence_improvement > 0:
            print("✅ Enhanced Prometheus shows SUPERIOR INTELLIGENCE!")
        elif accuracy_improvement > 0:
            print("✅ Enhanced Prometheus shows improved accuracy")
        else:
            print("⚠️ Results need further analysis")
        
        print(f"\nKey Improvements:")
        print(f"  Accuracy: {accuracy_improvement:+.2f}%")
        print(f"  Confidence: {confidence_improvement:+.2f}%")
        print(f"  Reasoning Sources: {sources_improvement:+.2f}% (from {old_results['avg_reasoning_sources']:.1f} to {new_results['avg_reasoning_sources']:.1f})")


async def main():
    """Main benchmark"""
    benchmark = IntelligenceBenchmark()
    results = await benchmark.benchmark_intelligence()
    return results


if __name__ == "__main__":
    asyncio.run(main())

