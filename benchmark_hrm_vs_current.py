#!/usr/bin/env python3
"""
Benchmark Full HRM vs Current LSTM-based Implementation
Compares performance of full HRM architecture vs legacy LSTM HRM
"""

import sys
import os
from pathlib import Path
import time
import numpy as np
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_context():
    """Create test trading context"""
    from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
    
    return HRMReasoningContext(
        market_data={
            'price': 150.0,
            'volume': 1000000,
            'indicators': {
                'rsi': 65.5,
                'macd': 0.8,
                'bollinger_upper': 155.0,
                'bollinger_lower': 145.0
            }
        },
        user_profile={'risk_tolerance': 'medium'},
        trading_history=[],
        current_portfolio={'cash': 10000, 'positions': {}},
        risk_preferences={'max_position_size': 0.1},
        reasoning_level=HRMReasoningLevel.HIGH_LEVEL
    )


def benchmark_legacy_hrm(num_iterations: int = 10):
    """Benchmark legacy LSTM-based HRM"""
    print("\n" + "="*60)
    print("BENCHMARK: Legacy LSTM-based HRM")
    print("="*60)
    
    try:
        from core.hrm_integration import HRMTradingEngine
        
        engine = HRMTradingEngine(device='cpu')
        context = create_test_context()
        
        latencies = []
        confidences = []
        
        for i in range(num_iterations):
            start = time.time()
            decision = engine.make_hierarchical_decision(context)
            latency = time.time() - start
            
            latencies.append(latency)
            confidences.append(decision.get('confidence', 0.0))
        
        avg_latency = np.mean(latencies)
        std_latency = np.std(latencies)
        avg_confidence = np.mean(confidences)
        
        print(f"[OK] Legacy HRM benchmark complete")
        print(f"   Iterations: {num_iterations}")
        print(f"   Avg latency: {avg_latency*1000:.2f}ms +/- {std_latency*1000:.2f}ms")
        print(f"   Avg confidence: {avg_confidence:.3f}")
        
        return {
            'avg_latency': avg_latency,
            'std_latency': std_latency,
            'avg_confidence': avg_confidence,
            'latencies': latencies,
            'confidences': confidences
        }
        
    except Exception as e:
        print(f"[FAIL] Legacy HRM benchmark failed: {e}")
        return None


def benchmark_full_hrm(num_iterations: int = 10):
    """Benchmark full HRM architecture"""
    print("\n" + "="*60)
    print("BENCHMARK: Full HRM Architecture")
    print("="*60)
    
    try:
        from core.hrm_integration import FullHRMTradingEngine
        
        engine = FullHRMTradingEngine(device='cpu', use_full_hrm=True)
        context = create_test_context()
        
        latencies = []
        confidences = []
        
        for i in range(num_iterations):
            start = time.time()
            decision = engine.make_hierarchical_decision(context)
            latency = time.time() - start
            
            latencies.append(latency)
            confidences.append(decision.get('confidence', 0.0))
        
        avg_latency = np.mean(latencies)
        std_latency = np.std(latencies)
        avg_confidence = np.mean(confidences)
        
        print(f"[OK] Full HRM benchmark complete")
        print(f"   Iterations: {num_iterations}")
        print(f"   Avg latency: {avg_latency*1000:.2f}ms +/- {std_latency*1000:.2f}ms")
        print(f"   Avg confidence: {avg_confidence:.3f}")
        
        return {
            'avg_latency': avg_latency,
            'std_latency': std_latency,
            'avg_confidence': avg_confidence,
            'latencies': latencies,
            'confidences': confidences
        }
        
    except Exception as e:
        print(f"[FAIL] Full HRM benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_results(legacy_results, full_results):
    """Compare benchmark results"""
    print("\n" + "="*60)
    print("COMPARISON: Legacy vs Full HRM")
    print("="*60)
    
    if legacy_results is None or full_results is None:
        print("[WARN] Cannot compare - one or both benchmarks failed")
        return
    
    # Latency comparison
    latency_improvement = ((legacy_results['avg_latency'] - full_results['avg_latency']) / 
                          legacy_results['avg_latency']) * 100
    
    # Confidence comparison
    confidence_improvement = ((full_results['avg_confidence'] - legacy_results['avg_confidence']) / 
                             legacy_results['avg_confidence']) * 100
    
    print(f"\nLatency:")
    print(f"   Legacy:  {legacy_results['avg_latency']*1000:.2f}ms")
    print(f"   Full:    {full_results['avg_latency']*1000:.2f}ms")
    print(f"   Change:  {latency_improvement:+.1f}%")
    
    print(f"\nConfidence:")
    print(f"   Legacy:  {legacy_results['avg_confidence']:.3f}")
    print(f"   Full:    {full_results['avg_confidence']:.3f}")
    print(f"   Change:  {confidence_improvement:+.1f}%")
    
    print(f"\nSummary:")
    if latency_improvement > 0:
        print(f"   [OK] Full HRM is {latency_improvement:.1f}% faster")
    else:
        print(f"   [WARN] Full HRM is {abs(latency_improvement):.1f}% slower")
    
    if confidence_improvement > 0:
        print(f"   [OK] Full HRM has {confidence_improvement:.1f}% higher confidence")
    else:
        print(f"   [WARN] Full HRM has {abs(confidence_improvement):.1f}% lower confidence")


def main():
    """Run benchmark comparison"""
    print("\n" + "="*80)
    print("HRM BENCHMARK: Legacy vs Full Architecture")
    print("="*80)
    
    num_iterations = 10
    
    # Benchmark legacy
    legacy_results = benchmark_legacy_hrm(num_iterations)
    
    # Benchmark full HRM
    full_results = benchmark_full_hrm(num_iterations)
    
    # Compare
    compare_results(legacy_results, full_results)
    
    print("\n" + "="*80)
    print("Benchmark complete!")
    print("="*80)


if __name__ == "__main__":
    main()

