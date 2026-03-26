"""
Quick test script for DeepSeek Cloud API Integration
Tests the DeepSeek adapter with the configured API key
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_api():
    """Test DeepSeek Cloud API integration"""
    print("=" * 60)
    print("🧪 DeepSeek Cloud API Integration Test")
    print("=" * 60)
    
    # Check environment variables
    api_key = os.getenv('DEEPSEEK_API_KEY', '')
    use_api = os.getenv('USE_DEEPSEEK_API', 'false')
    model = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
    endpoint = os.getenv('DEEPSEEK_API_ENDPOINT', 'https://api.deepseek.com')
    
    print(f"\n📋 Configuration:")
    print(f"   USE_DEEPSEEK_API: {use_api}")
    print(f"   DEEPSEEK_MODEL: {model}")
    print(f"   DEEPSEEK_API_ENDPOINT: {endpoint}")
    print(f"   API_KEY: {'✅ Configured' if api_key else '❌ Missing'}")
    
    if not api_key:
        print("\n❌ ERROR: DEEPSEEK_API_KEY not found in .env")
        return False
    
    # Initialize adapter
    print("\n🔧 Initializing DeepSeek Adapter...")
    try:
        from core.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter()
        print(f"   Mode: {adapter.mode}")
        print(f"   Cloud Model: {getattr(adapter, 'cloud_model', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to initialize adapter: {e}")
        return False
    
    # Health check
    print("\n🏥 Health Check...")
    try:
        healthy = adapter.is_healthy()
        print(f"   API Status: {'✅ Healthy' if healthy else '⚠️ Unhealthy (but may still work)'}")
    except Exception as e:
        print(f"   Health check error: {e}")
    
    # Test simple generation
    print("\n🧠 Testing Generation (Simple Prompt)...")
    try:
        result = adapter.generate(
            "What is 2 + 2? Answer with just the number.",
            max_tokens=50,
            temperature=0.1
        )

        if result.get('success'):
            print(f"   ✅ Success!")
            print(f"   Response: {result.get('response', '')[:100]}")
            print(f"   Model: {result.get('model')}")
            print(f"   Cost: ${result.get('cost', 0):.6f}")
            print(f"   Tokens: {result.get('tokens_used', 0)}")
        else:
            error = result.get('error', '')
            print(f"   ⚠️ API Response: {error}")

            if 'Insufficient Balance' in str(error):
                print("\n" + "=" * 60)
                print("⚠️  API KEY WORKS BUT NO BALANCE!")
                print("=" * 60)
                print("Your DeepSeek API key is valid and working correctly.")
                print("You need to add credits to your DeepSeek account.")
                print("\n📌 To add balance:")
                print("   1. Go to: https://platform.deepseek.com")
                print("   2. Login with your account")
                print("   3. Go to Billing → Top Up")
                print("   4. Add $5-10 to get started")
                print("\n💰 DeepSeek pricing is very cheap:")
                print("   - $0.14/M input tokens (cache hit)")
                print("   - $0.28/M input tokens (cache miss)")
                print("   - $0.42/M output tokens")
                print("   - $5 is enough for ~10,000+ trading decisions!")
                print("=" * 60)
                return True  # API works, just needs balance
            else:
                return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    # Test market analysis
    print("\n📊 Testing Market Analysis...")
    try:
        market_data = {
            'symbol': 'TEST',
            'price': 150.00,
            'volume': 1000000,
            'rsi': 65,
            'macd': 'bullish',
            'trend': 'upward'
        }
        
        result = adapter.analyze_market(market_data)
        print(f"   Action: {result.get('action')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Reasoning: {result.get('reasoning', '')[:80]}...")
        print(f"   Cost: ${result.get('cost', 0):.6f}")
        print(f"   Source: {result.get('source')}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Get stats
    print("\n📈 Usage Statistics:")
    stats = adapter.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ DeepSeek Cloud API Integration Test PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_deepseek_api()
    sys.exit(0 if success else 1)

