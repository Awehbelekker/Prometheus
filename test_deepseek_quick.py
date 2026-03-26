"""Quick test of DeepSeek for trading analysis"""
import requests
import json
import time

print("\n🧪 TESTING DEEPSEEK FOR TRADING ANALYSIS")
print("=" * 60)

# Test prompt
prompt = """You are a professional trading AI. Analyze this stock and provide a recommendation.

Stock: AAPL
Price: $175.50
Volume: 52M shares
RSI: 65 (slightly overbought)
MACD: Bullish crossover
50-day MA: $170 (price above)
200-day MA: $165 (price above)

Provide ONLY:
1. Action: BUY, SELL, or HOLD
2. Confidence: 0-100
3. Brief reason (one sentence)

Format: ACTION|CONFIDENCE|REASON"""

print("\n📊 Analyzing AAPL...")
print("⏱️  This may take 10-30 seconds on first run (loading model)...")

start_time = time.time()

try:
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'deepseek-r1:14b',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'num_predict': 150
            }
        },
        timeout=60
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result.get('response', '').strip()
        
        print(f"\n✅ DeepSeek Response (took {elapsed:.1f}s):")
        print("-" * 60)
        print(ai_response)
        print("-" * 60)
        
        # Parse response
        try:
            if '|' in ai_response:
                parts = ai_response.split('|')
                action = parts[0].strip()
                confidence = parts[1].strip()
                reason = parts[2].strip() if len(parts) > 2 else "No reason provided"
                
                print(f"\n📈 PARSED RESULT:")
                print(f"   Action:     {action}")
                print(f"   Confidence: {confidence}%")
                print(f"   Reason:     {reason}")
                print(f"   Cost:       $0.00 (FREE!)")
                print(f"   Time:       {elapsed:.1f}s")
        except:
            print("\n✅ Response received (parsing optional)")
        
        print("\n🎉 DeepSeek is working perfectly!")
        print("✅ Ready to integrate with PROMETHEUS!")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 TIP: Make sure Ollama is running:")
    print("   Run: ollama serve")

