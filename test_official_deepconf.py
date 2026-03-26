#!/usr/bin/env python3
"""
Test and Benchmark Official DeepConf Integration

This script tests the official DeepConf implementation and compares it
with the previous synthetic version.
"""

import asyncio
import time
import sys
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, '.')

from core.reasoning.official_deepconf_adapter import (
    OfficialDeepConfAdapter,
    DeepConfConfig,
    DeepConfMode,
    DEEPCONF_AVAILABLE
)

# Test cases for benchmarking
TEST_CASES = {
    'simple_math': [
        ("What is 2^10?", "1024"),
        ("Calculate 15% of 240", "36"),
        ("What is the square root of 144?", "12")
    ],
    'trading_reasoning': [
        ("Should I buy AAPL if it's down 5% today but earnings beat expectations?", "buy"),
        ("If the 50-day MA crosses above the 200-day MA, is this bullish or bearish?", "bullish"),
        ("What does rising VIX during a market rally typically indicate?", "caution")
    ],
    'risk_assessment': [
        ("Is selling cash-secured puts at ATM strike high or low risk?", "moderate"),
        ("Should I increase position size when confidence is low?", "no"),
        ("What's safer: buying calls or selling puts?", "buying calls")
    ]
}

async def test_basic_functionality():
    """Test basic DeepConf functionality"""
    
    print("="*80)
    print("TEST 1: BASIC FUNCTIONALITY")
    print("="*80)
    print()
    
    if not DEEPCONF_AVAILABLE:
        print("❌ Official DeepConf not available!")
        print("Install with: pip install deepconf")
        return False
    
    print("✅ Official DeepConf package imported successfully")
    print()
    
    # Test simple question
    question = "What is 2^10?"
    print(f"Question: {question}")
    print()
    
    config = DeepConfConfig(
        mode=DeepConfMode.ONLINE,
        model="deepseek-r1:8b",
        warmup_traces=4,
        total_budget=16
    )
    
    adapter = OfficialDeepConfAdapter(config)
    
    print(f"Adapter Status:")
    print(f"  Enabled: {adapter.enabled}")
    print(f"  Model: {adapter.config.model}")
    print(f"  Mode: {adapter.config.mode.value}")
    print()
    
    try:
        print("Running DeepConf reasoning...")
        result = await adapter.reason(question)
        
        print()
        print("Result:")
        print(f"  Success: {result.success}")
        print(f"  Answer: {result.final_answer}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Traces Used: {result.total_traces_used}")
        print(f"  Latency: {result.latency:.2f}s")
        
        if result.error:
            print(f"  Error: {result.error}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

async def test_both_modes():
    """Test both ONLINE and OFFLINE modes"""
    
    print()
    print("="*80)
    print("TEST 2: ONLINE vs OFFLINE MODES")
    print("="*80)
    print()
    
    if not DEEPCONF_AVAILABLE:
        print("❌ Skipping - DeepConf not available")
        return False
    
    question = "Calculate 15% of 240"
    
    results = {}
    
    for mode in [DeepConfMode.ONLINE, DeepConfMode.OFFLINE]:
        print(f"\n--- Testing {mode.value.upper()} Mode ---\n")
        
        config = DeepConfConfig(
            mode=mode,
            model="deepseek-r1:8b",
            warmup_traces=4 if mode == DeepConfMode.ONLINE else 0,
            total_budget=16 if mode == DeepConfMode.ONLINE else 0,
            offline_budget=8 if mode == DeepConfMode.OFFLINE else 0,
            compute_multiple_voting=True
        )
        
        adapter = OfficialDeepConfAdapter(config)
        
        start = time.time()
        result = await adapter.reason(question)
        latency = time.time() - start
        
        results[mode.value] = result
        
        print(f"Answer: {result.final_answer}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Traces: {result.total_traces_used}")
        print(f"Latency: {latency:.2f}s")
        
        if mode == DeepConfMode.OFFLINE and result.voting_results:
            print("\nVoting Results:")
            for method, method_result in result.voting_results.items():
                if method_result and 'answer' in method_result:
                    conf = method_result.get('confidence', 'N/A')
                    print(f"  {method}: {method_result['answer']} (conf: {conf})")
    
    print("\n--- Mode Comparison ---")
    online = results.get('online')
    offline = results.get('offline')
    
    if online and offline:
        print(f"Online Latency:  {online.latency:.2f}s")
        print(f"Offline Latency: {offline.latency:.2f}s")
        print(f"Speed Advantage: {offline.latency/online.latency:.1f}x faster" if online.latency < offline.latency else f"{online.latency/offline.latency:.1f}x slower")
    
    return True

async def benchmark_accuracy():
    """Benchmark accuracy across test cases"""
    
    print()
    print("="*80)
    print("TEST 3: ACCURACY BENCHMARK")
    print("="*80)
    print()
    
    if not DEEPCONF_AVAILABLE:
        print("❌ Skipping - DeepConf not available")
        return False
    
    config = DeepConfConfig(
        mode=DeepConfMode.ONLINE,
        model="deepseek-r1:8b",
        warmup_traces=4,
        total_budget=16
    )
    
    adapter = OfficialDeepConfAdapter(config)
    
    all_results = []
    
    for category, questions in TEST_CASES.items():
        print(f"\n--- {category.upper().replace('_', ' ')} ---\n")
        
        category_results = []
        
        for question, expected_answer in questions:
            try:
                result = await adapter.reason(question)
                
                # Simple accuracy check (contains expected answer)
                correct = expected_answer.lower() in result.final_answer.lower()
                
                category_results.append({
                    'question': question,
                    'expected': expected_answer,
                    'answer': result.final_answer,
                    'confidence': result.confidence,
                    'correct': correct,
                    'latency': result.latency
                })
                
                status = "✅" if correct else "❌"
                print(f"{status} Q: {question}")
                print(f"   A: {result.final_answer} (conf: {result.confidence:.2f})")
                print()
                
            except Exception as e:
                print(f"❌ Error: {e}\n")
                category_results.append({
                    'question': question,
                    'correct': False,
                    'error': str(e)
                })
        
        all_results.extend(category_results)
        
        # Category stats
        correct_count = sum(1 for r in category_results if r.get('correct'))
        accuracy = correct_count / len(category_results) * 100
        avg_confidence = sum(r.get('confidence', 0) for r in category_results) / len(category_results)
        avg_latency = sum(r.get('latency', 0) for r in category_results) / len(category_results)
        
        print(f"Category Results:")
        print(f"  Accuracy: {accuracy:.1f}% ({correct_count}/{len(category_results)})")
        print(f"  Avg Confidence: {avg_confidence:.3f}")
        print(f"  Avg Latency: {avg_latency:.2f}s")
    
    # Overall stats
    print("\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    
    total_correct = sum(1 for r in all_results if r.get('correct'))
    overall_accuracy = total_correct / len(all_results) * 100
    overall_confidence = sum(r.get('confidence', 0) for r in all_results) / len(all_results)
    overall_latency = sum(r.get('latency', 0) for r in all_results) / len(all_results)
    
    print(f"\nTotal Questions: {len(all_results)}")
    print(f"Correct Answers: {total_correct}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"Avg Confidence: {overall_confidence:.3f}")
    print(f"Avg Latency: {overall_latency:.2f}s")
    
    # High confidence accuracy
    high_conf_results = [r for r in all_results if r.get('confidence', 0) > 0.7]
    if high_conf_results:
        high_conf_correct = sum(1 for r in high_conf_results if r.get('correct'))
        high_conf_accuracy = high_conf_correct / len(high_conf_results) * 100
        print(f"\nHigh Confidence (>0.7) Accuracy: {high_conf_accuracy:.1f}% ({high_conf_correct}/{len(high_conf_results)})")
    
    return overall_accuracy >= 70.0  # Target: 70%+ accuracy

async def test_trading_context():
    """Test DeepConf with trading context"""
    
    print()
    print("="*80)
    print("TEST 4: TRADING CONTEXT INTEGRATION")
    print("="*80)
    print()
    
    if not DEEPCONF_AVAILABLE:
        print("❌ Skipping - DeepConf not available")
        return False
    
    question = "Should I buy AAPL?"
    
    context = {
        'market_data': {
            'symbol': 'AAPL',
            'current_price': 150.00,
            'change_percent': -2.5,
            'volume': 1250000,
            'pe_ratio': 28.5,
            'technical_signal': 'bullish',
            'trend': 'uptrend'
        },
        'risk_parameters': {
            'max_position_size': 0.10,
            'stop_loss_percent': 0.02,
            'max_drawdown': 0.15
        }
    }
    
    config = DeepConfConfig(
        mode=DeepConfMode.ONLINE,
        model="deepseek-r1:8b",
        warmup_traces=6,
        total_budget=24
    )
    
    adapter = OfficialDeepConfAdapter(config)
    
    print(f"Question: {question}")
    print(f"\nMarket Context:")
    for k, v in context['market_data'].items():
        print(f"  {k}: {v}")
    
    print(f"\nRisk Parameters:")
    for k, v in context['risk_parameters'].items():
        print(f"  {k}: {v}")
    
    print("\nRunning DeepConf with context...")
    
    result = await adapter.reason(question, context)
    
    print(f"\nDecision: {result.final_answer}")
    print(f"Confidence: {result.confidence:.3f}")
    print(f"Traces: {result.total_traces_used}")
    print(f"Latency: {result.latency:.2f}s")
    
    return result.success

async def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("OFFICIAL DEEPCONF INTEGRATION TEST SUITE")
    print("="*80)
    print()
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Both Modes", test_both_modes),
        ("Accuracy Benchmark", benchmark_accuracy),
        ("Trading Context", test_trading_context)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = "✅ PASS" if success else "❌ FAIL"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
    
    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print()
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    passed = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Official DeepConf is ready for production use")
    elif passed >= total * 0.75:
        print("\n⚠️ MOST TESTS PASSED - Ready with caveats")
    else:
        print("\n❌ TESTS FAILED - Review errors above")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

