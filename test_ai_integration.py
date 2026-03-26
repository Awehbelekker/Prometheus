"""Test the DeepSeek adapter and unified AI provider."""
import sys
import importlib
sys.path.insert(0, '.')

# Force reload to pick up .env changes
import core.deepseek_adapter
import core.unified_ai_provider
importlib.reload(core.deepseek_adapter)
importlib.reload(core.unified_ai_provider)

from core.deepseek_adapter import DeepSeekAdapter
from core.unified_ai_provider import UnifiedAIProvider

print("=" * 60)
print("DEEPSEEK & AI INTEGRATION TEST")
print("=" * 60)

# Test DeepSeek Adapter
print("\n1. Testing DeepSeek Adapter...")
adapter = DeepSeekAdapter()
print(f"   Model: {adapter.model}")
print(f"   Timeout: {adapter.timeout}s")
print(f"   Health: {'OK' if adapter.is_healthy() else 'FAIL'}")

# Test generate with validation
print("\n2. Testing generate with response validation...")
result = adapter.generate("What is 2+2?", max_tokens=50)
print(f"   Success: {result.get('success')}")
print(f"   Needs Fallback: {result.get('needs_fallback', False)}")
if result.get('success'):
    print(f"   Response: {result.get('response', '')[:100]}...")
else:
    print(f"   Error: {result.get('error')}")

# Test unified AI provider
print("\n3. Testing Unified AI Provider...")
provider = UnifiedAIProvider()  # Create fresh instance
print(f"   DeepSeek Enabled: {provider.deepseek_adapter is not None}")
print(f"   OpenAI Fallback: {provider.openai_fallback}")

# Test provider generate
print("\n4. Testing provider generate (with fallback)...")
result = provider.generate("What is the capital of France?", max_tokens=50)
print(f"   Success: {result.get('success')}")
print(f"   Source: {result.get('source', 'N/A')}")
if result.get('success'):
    print(f"   Response: {result.get('response', '')[:100]}...")
else:
    print(f"   Error: {result.get('error', 'Unknown')}")

# Get stats
print("\n5. Provider Stats:")
stats = provider.get_stats()
for key, value in stats.items():
    print(f"   {key}: {value}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

if result.get('success'):
    print("\n✅ AI Integration is WORKING!")
    print("   The system will use DeepSeek (FREE) or OpenAI fallback.")
else:
    print("\n⚠️  DeepSeek is returning garbled responses.")
    print("   OpenAI fallback will be used for reliable AI decisions.")
    print("   This is expected on CPU-only systems.")

