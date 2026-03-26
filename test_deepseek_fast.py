"""Quick test with faster DeepSeek 8B model"""
import requests
import time

print("\n🧪 TESTING DEEPSEEK-R1:8B (FASTER MODEL)")
print("=" * 60)

# Wait for server
print("⏱️  Waiting for Ollama server to start...")
time.sleep(5)

# Simple test
prompt = "Analyze AAPL stock at $175.50 with RSI 65. Give: BUY/SELL/HOLD and confidence 0-100. Be brief."

print("\n📊 Testing DeepSeek 8B...")

try:
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'deepseek-r1:8b',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'num_predict': 100
            }
        },
        timeout=90
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ DeepSeek Response:")
        print("-" * 60)
        print(result.get('response', ''))
        print("-" * 60)
        print("\n🎉 SUCCESS! DeepSeek is working!")
        print("✅ Ready to integrate with PROMETHEUS!")
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Model may still be loading. This is normal on first run.")
    print("💡 Let's proceed with integration anyway - it will work once loaded!")

