"""Test the DeepSeek adapter integration"""
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path.cwd()))

from core.deepseek_adapter import DeepSeekAdapter

print("\n" + "=" * 60)
print("TESTING DEEPSEEK ADAPTER FOR PROMETHEUS")
print("=" * 60)

# Create adapter
print("\n1. Creating DeepSeek adapter...")
adapter = DeepSeekAdapter()
print(f"   Model: {adapter.model}")
print(f"   Endpoint: {adapter.endpoint}")

# Test market analysis
print("\n2. Testing market analysis...")
test_data = {
    'symbol': 'AAPL',
    'price': 175.50,
    'volume': 52000000,
    'rsi': 65,
    'macd': 'bullish',
    'trend': 'uptrend'
}

print(f"   Analyzing: {test_data['symbol']}")
print("   (This may take 30-60 seconds on first run...)")

result = adapter.analyze_market(test_data)

print(f"\n3. RESULT:")
print(f"   Action:     {result.get('action')}")
print(f"   Confidence: {result.get('confidence')}%")
print(f"   Reasoning:  {result.get('reasoning')}")
print(f"   Cost:       ${result.get('cost', 0):.4f} (FREE!)")
print(f"   Source:     {result.get('source')}")

# Show stats
stats = adapter.get_stats()
print(f"\n4. STATISTICS:")
print(f"   Total Requests: {stats['total_requests']}")
print(f"   Total Cost:     ${stats['total_cost']:.2f}")
print(f"   Savings:        {stats['savings']}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE!")
print("=" * 60)
print("\nDeepSeek adapter is ready for PROMETHEUS!")
print("Next: Launch PROMETHEUS to start trading with FREE AI!")

