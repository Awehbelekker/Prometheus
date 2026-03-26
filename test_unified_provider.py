"""Test the unified AI provider directly."""
import sys
sys.path.insert(0, '.')

# Force reload
import importlib
import core.deepseek_adapter
import core.unified_ai_provider
importlib.reload(core.deepseek_adapter)
importlib.reload(core.unified_ai_provider)

from core.unified_ai_provider import UnifiedAIProvider

print("=" * 60)
print("UNIFIED AI PROVIDER TEST")
print("=" * 60)

provider = UnifiedAIProvider()
print(f"DeepSeek Enabled: {provider.deepseek_adapter is not None}")
print(f"OpenAI Fallback: {provider.openai_fallback}")
print(f"OpenAI Client: {provider.openai_client is not None}")

# Test with simple prompt
print("\n1. Testing simple prompt...")
result = provider.generate("What is 2+2?", max_tokens=50)
print(f"   Success: {result.get('success')}")
print(f"   Source: {result.get('source', 'N/A')}")
print(f"   Response: {result.get('response', result.get('error', 'N/A'))[:100]}")

# Test with longer prompt
print("\n2. Testing longer prompt...")
result = provider.generate("What is the capital of France? Answer in one word.", max_tokens=50)
print(f"   Success: {result.get('success')}")
print(f"   Source: {result.get('source', 'N/A')}")
print(f"   Response: {result.get('response', result.get('error', 'N/A'))[:100]}")

# Test market analysis
print("\n3. Testing market analysis...")
market_data = {
    'symbol': 'AAPL',
    'price': 175.50,
    'volume': 50000000,
    'rsi': 65,
    'macd': 'bullish',
    'trend': 'upward'
}
result = provider.analyze_market(market_data)
print(f"   Action: {result.get('action')}")
print(f"   Confidence: {result.get('confidence')}")
print(f"   Source: {result.get('source', 'N/A')}")

print("\n" + "=" * 60)
print("Stats:", provider.get_stats())

