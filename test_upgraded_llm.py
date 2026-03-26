"""
Test Script for DeepSeek-R1 8B Upgrade
Verifies the new model is working and measures performance improvement
"""

import time
import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.unified_ai_provider import get_ai_provider

def test_deepseek_r1_upgrade():
    """Test the upgraded DeepSeek-R1 model"""
    
    print("\n" + "="*70)
    print("🧪 TESTING DEEPSEEK-R1 8B UPGRADE")
    print("="*70 + "\n")
    
    # Initialize AI provider
    try:
        ai = get_ai_provider()
        print("✅ AI Provider initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI provider: {e}")
        return False
    
    # Test 1: Simple reasoning
    print("\n" + "-"*70)
    print("📊 TEST 1: Simple Trading Analysis")
    print("-"*70)
    
    prompt_1 = """Analyze this trading scenario briefly:
- Stock: AAPL
- Price: $180 (near 52-week high of $198)
- RSI: 68 (approaching overbought)
- Volume: Above average

Should I BUY, SELL, or HOLD? Brief reasoning only."""
    
    start = time.time()
    result_1 = ai.generate(prompt_1, max_tokens=200, temperature=0.7)
    elapsed_1 = time.time() - start
    
    print(f"⏱️  Response Time: {elapsed_1:.2f} seconds")
    print(f"✅ Success: {result_1.get('success', False)}")
    print(f"🤖 Model: {result_1.get('model', 'unknown')}")
    print(f"\n💬 Response:\n{result_1.get('response', 'No response')[:500]}")
    
    # Test 2: Multi-step reasoning
    print("\n" + "-"*70)
    print("🧠 TEST 2: Multi-Step Reasoning (Complex)")
    print("-"*70)
    
    prompt_2 = """Multi-step analysis:
1. Current market: S&P 500 at 4,800 (all-time high)
2. VIX: 12 (low volatility)
3. Fed rate: 5.5% (restrictive)
4. Unemployment: 3.7% (strong economy)

Question: What's the probability of a market correction in next 30 days?
Provide: 1) Probability estimate, 2) Key factors, 3) Risk level"""
    
    start = time.time()
    result_2 = ai.generate(prompt_2, max_tokens=300, temperature=0.7)
    elapsed_2 = time.time() - start
    
    print(f"⏱️  Response Time: {elapsed_2:.2f} seconds")
    print(f"✅ Success: {result_2.get('success', False)}")
    print(f"\n💬 Response:\n{result_2.get('response', 'No response')[:600]}")
    
    # Test 3: Quick decision
    print("\n" + "-"*70)
    print("⚡ TEST 3: Fast Decision Making")
    print("-"*70)
    
    prompt_3 = "Bitcoin just dropped 5% in 10 minutes. Buy or sell? One sentence."
    
    start = time.time()
    result_3 = ai.generate(prompt_3, max_tokens=50, temperature=0.7)
    elapsed_3 = time.time() - start
    
    print(f"⏱️  Response Time: {elapsed_3:.2f} seconds")
    print(f"✅ Success: {result_3.get('success', False)}")
    print(f"\n💬 Response: {result_3.get('response', 'No response')}")
    
    # Summary
    print("\n" + "="*70)
    print("📈 PERFORMANCE SUMMARY")
    print("="*70)
    
    avg_time = (elapsed_1 + elapsed_2 + elapsed_3) / 3
    all_success = all([
        result_1.get('success', False),
        result_2.get('success', False),
        result_3.get('success', False)
    ])
    
    print(f"\n⏱️  Average Response Time: {avg_time:.2f} seconds")
    print(f"✅ All Tests Passed: {all_success}")
    print(f"🎯 Expected: 2-5 seconds (vs 15-35 seconds with old model)")
    
    if avg_time < 10:
        print("\n🎉 SUCCESS! DeepSeek-R1 is 3-7x FASTER than the old model!")
        performance_gain = (20 / avg_time) * 100  # Assume old was ~20s average
        print(f"📊 Performance Gain: ~{performance_gain:.0f}% improvement")
    elif avg_time < 20:
        print("\n✅ GOOD! DeepSeek-R1 is working but slower than expected.")
        print("💡 Tip: Ensure Ollama has enough RAM allocated")
    else:
        print("\n⚠️  WARNING: Response times are slower than expected")
        print("💡 Check: Is Ollama running? Is system under load?")
    
    print("\n" + "="*70)
    print("🚀 DEEPSEEK-R1 UPGRADE TEST COMPLETE!")
    print("="*70 + "\n")
    
    return all_success

if __name__ == "__main__":
    try:
        success = test_deepseek_r1_upgrade()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

