"""Quick test to see raw LLaVA response"""
import requests
import base64
import json
from pathlib import Path

# Get a sample chart
charts = list(Path("charts").glob("*.png"))
if not charts:
    print("No charts found!")
    exit()

chart = charts[0]
print(f"Testing with: {chart.name}")

# Load image
with open(chart, 'rb') as f:
    img_data = base64.b64encode(f.read()).decode()

# Simple test prompt
prompt = """Look at this stock chart image. 

1. What is the overall price trend? (going up, going down, or sideways)
2. Do you see any chart patterns like triangles, head and shoulders, or double tops?
3. What price levels seem important?

Please describe what you see in the chart."""

print(f"\nTesting llama3.2-vision (better model)...")
print("-" * 50)

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2-vision:latest",  # Better model
            "prompt": prompt,
            "images": [img_data],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 500
            }
        },
        timeout=300
    )
    
    if response.status_code == 200:
        result = response.json()
        raw_response = result.get('response', 'No response')
        
        print("\n=== RAW llama3.2-vision RESPONSE ===\n")
        print(raw_response)
        print("\n" + "=" * 50)
        
        # Check for pattern keywords
        print("\n=== PATTERN KEYWORD CHECK ===")
        keywords = ['head', 'shoulder', 'triangle', 'double', 'top', 'bottom', 
                   'flag', 'channel', 'wedge', 'support', 'resistance', 'trend',
                   'bullish', 'bearish', 'neutral', 'uptrend', 'downtrend',
                   'up', 'down', 'sideways', 'price', 'level']
        
        response_lower = raw_response.lower()
        found = [kw for kw in keywords if kw in response_lower]
        print(f"Keywords found: {found}")
        
        if len(raw_response) > 50:
            print("\n✅ Model is providing meaningful responses!")
        else:
            print("\n❌ Response too short - model may not be working")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("TIMEOUT - model too slow")
except Exception as e:
    print(f"Error: {e}")
