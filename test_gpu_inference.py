#!/usr/bin/env python3
"""Test GPU Inference with AMD ROCm"""
import os
import requests
import time

# Set ROCm environment for RX 580
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "8.0.3"
os.environ["HIP_VISIBLE_DEVICES"] = "0"

print("="*60)
print("🎮 AMD RX 580 GPU Inference Test")
print("="*60)

def test_model(model_name: str, prompt: str):
    """Test a model and measure speed"""
    print(f"\n🧪 Testing: {model_name}")
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 50, "temperature": 0.1}
    }
    
    try:
        start = time.time()
        r = requests.post("http://localhost:11434/api/generate", 
                         json=payload, timeout=120)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            response = result.get("response", "").strip()
            
            # Check for valid response
            if response and len(response) > 0:
                # Check if response is readable ASCII
                if all(32 <= ord(c) < 127 or c in '\\n\\r\\t' for c in response[:100]):
                    print(f"   ✅ Response: {response[:100]}")
                    print(f"   ⏱️ Time: {elapsed:.1f}s")
                    
                    # GPU indicator: fast response = GPU, slow = CPU
                    if elapsed < 5:
                        print(f"   🚀 FAST - Likely using GPU!")
                    elif elapsed < 15:
                        print(f"   ⚡ Medium speed")
                    else:
                        print(f"   🐢 Slow - Likely CPU inference")
                    return True
                else:
                    print(f"   ⚠️ Garbled output detected")
                    return False
            else:
                print(f"   ⚠️ Empty response")
                return False
        else:
            print(f"   ❌ HTTP {r.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout after 120s")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

# Test models
print("\\n📋 Testing available models...")

# Test phi first (smallest, fastest)
test_model("phi", "What is the capital of France? Answer in one word.")

# Test qwen2.5:7b
test_model("qwen2.5:7b", "AAPL stock at $185, RSI 58. BUY, SELL, or HOLD?")

# Test mistral
test_model("mistral:7b", "What is 10 * 5? Just the number.")

print("\\n" + "="*60)
print("Test complete!")
print("="*60)

