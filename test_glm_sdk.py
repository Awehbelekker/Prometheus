"""Test GLM using official SDK"""
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  GLM-4 OFFICIAL SDK TEST")
print("=" * 60)

api_key = os.getenv('ZHIPUAI_API_KEY')
print(f"\nAPI Key: {api_key[:15]}...{api_key[-5:]}")

client = ZhipuAI(api_key=api_key)

# Test text model first
print("\n🔄 Testing GLM-4-Flash (text)...")
try:
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": "Say 'GLM works!' in exactly 3 words"}],
        max_tokens=20
    )
    print(f"✅ GLM-4-Flash Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ GLM-4-Flash Error: {e}")

# Test vision model
print("\n🔄 Testing GLM-4V (vision)...")
try:
    response = client.chat.completions.create(
        model="glm-4v",
        messages=[{"role": "user", "content": "Describe what a stock chart looks like in 20 words"}],
        max_tokens=50
    )
    print(f"✅ GLM-4V Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ GLM-4V Error: {e}")

# Try glm-4v-plus
print("\n🔄 Testing GLM-4V-Plus (enhanced vision)...")
try:
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[{"role": "user", "content": "Describe a candlestick chart in 10 words"}],
        max_tokens=30
    )
    print(f"✅ GLM-4V-Plus Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ GLM-4V-Plus Error: {e}")

print("\n" + "=" * 60)
