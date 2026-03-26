#!/usr/bin/env python3
"""Test DeepSeek-R1 Inference via Ollama"""
import requests
import json
import time

print("Testing DeepSeek-R1:8b Inference...")
print("="*50)

# Quick test prompt - using 8b model now
payload = {
    "model": "deepseek-r1:8b",
    "prompt": "AAPL at $185, RSI 58, MACD bullish. BUY, SELL, or HOLD? Answer briefly.",
    "stream": False,
    "options": {"num_predict": 100, "temperature": 0.1}
}

try:
    start = time.time()
    print("Sending request to Ollama... (this may take 30-90s on CPU)")
    r = requests.post("http://localhost:11434/api/generate", 
                      json=payload, timeout=180)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        response_text = result.get("response", "No response")
        print(f"\nResponse: {response_text[:500]}")
        print(f"\nTime: {elapsed:.1f}s")
        print(f"Model: {result.get('model', 'unknown')}")
        print(f"Status: SUCCESS")
    else:
        print(f"Error: HTTP {r.status_code}")
        print(f"Response: {r.text[:200]}")
except requests.exceptions.Timeout:
    print("Timeout: DeepSeek on CPU can be slow. Try again or check Ollama.")
except Exception as e:
    print(f"Error: {e}")

