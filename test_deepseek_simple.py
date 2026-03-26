#!/usr/bin/env python3
"""Simple DeepSeek-R1:8b Test"""
import requests
import time

print("="*60)
print("DeepSeek-R1:8b Simple Inference Test")
print("="*60)

# Test with a very simple prompt
payload = {
    "model": "deepseek-r1:8b",
    "prompt": "What is 2 + 2? Answer with just the number.",
    "stream": False,
    "options": {"num_predict": 50, "temperature": 0.1}
}

print("\nPrompt: What is 2 + 2? Answer with just the number.")
print("Sending request... (may take 20-60s on CPU)")

try:
    start = time.time()
    r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        response = result.get("response", "")
        print(f"\nResponse: '{response}'")
        print(f"Response bytes: {[ord(c) for c in response[:50]]}")
        print(f"Time: {elapsed:.1f}s")
        print(f"Model: {result.get('model', 'unknown')}")
        
        # Check for garbled output
        if response and all(32 <= ord(c) < 127 or c in '\n\r\t' for c in response):
            print("\n✅ Response looks VALID (ASCII text)")
        elif not response:
            print("\n⚠️ Response is EMPTY")
        else:
            print("\n❌ Response may be GARBLED (non-ASCII characters)")
    else:
        print(f"Error: HTTP {r.status_code}")
except requests.exceptions.Timeout:
    print("Timeout after 120s")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)

