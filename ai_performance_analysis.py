#!/usr/bin/env python3
"""
AI PERFORMANCE ANALYSIS
Analyze current AI performance and recommend optimizations
"""

import requests
import time
import json
from datetime import datetime

def test_ai_performance():
    """Test AI performance across all available systems"""
    print("AI PERFORMANCE ANALYSIS")
    print("=" * 60)
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test GPT-OSS 20B
    print("TESTING GPT-OSS 20B PERFORMANCE")
    print("=" * 50)
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:5000/generate",
            json={
                "prompt": "Analyze AAPL stock for trading decision",
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_time = end_time - start_time
            print(f"[SUCCESS] GPT-OSS 20B Response Time: {response_time:.3f}s")
            print(f"[SUCCESS] Model: {data.get('model_name', 'unknown')}")
            print(f"[SUCCESS] Processing Time: {data.get('processing_time', 0):.3f}s")
            print(f"[SUCCESS] Memory Usage: {data.get('memory_usage', 0):.1f}%")
            print(f"[SUCCESS] CPU Usage: {data.get('cpu_usage', 0):.1f}%")
            print(f"[SUCCESS] Response Quality: {'Enhanced Fallback' if 'enhanced' in data.get('model_name', '') else 'Real Model'}")
        else:
            print(f"[ERROR] GPT-OSS 20B failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] GPT-OSS 20B test failed: {str(e)}")
    
    print()
    
    # Test GPT-OSS 120B
    print("TESTING GPT-OSS 120B PERFORMANCE")
    print("=" * 50)
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:5001/generate",
            json={
                "prompt": "Analyze AAPL stock for trading decision",
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_time = end_time - start_time
            print(f"[SUCCESS] GPT-OSS 120B Response Time: {response_time:.3f}s")
            print(f"[SUCCESS] Model: {data.get('model_name', 'unknown')}")
            print(f"[SUCCESS] Processing Time: {data.get('processing_time', 0):.3f}s")
            print(f"[SUCCESS] Memory Usage: {data.get('memory_usage', 0):.1f}%")
            print(f"[SUCCESS] CPU Usage: {data.get('cpu_usage', 0):.1f}%")
            print(f"[SUCCESS] Response Quality: {'Enhanced Fallback' if 'enhanced' in data.get('model_name', '') else 'Real Model'}")
        else:
            print(f"[ERROR] GPT-OSS 120B failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] GPT-OSS 120B test failed: {str(e)}")
    
    print()
    
    # Test Main Server AI Endpoints
    print("TESTING MAIN SERVER AI ENDPOINTS")
    print("=" * 50)
    
    ai_endpoints = [
        ("AI Coordinator", "/api/ai/coordinator/status"),
        ("SynergyCore Agent", "/api/ai/agents/synergycore/status"),
        ("Quantum Engine", "/api/quantum/status"),
        ("Market Oracle", "/api/market-oracle/status"),
        ("Continuous Learning", "/api/learning/continuous-learning/status")
    ]
    
    for name, endpoint in ai_endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                print(f"[SUCCESS] {name}: {response_time:.3f}s")
            else:
                print(f"[ERROR] {name}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)}")
    
    print()

def analyze_ai_configuration():
    """Analyze current AI configuration"""
    print("AI CONFIGURATION ANALYSIS")
    print("=" * 50)
    
    # Check environment variables
    import os
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI API Key: {'[CHECK] Configured' if openai_key else '[ERROR] Not configured'}")
    print(f"Anthropic API Key: {'[CHECK] Configured' if anthropic_key else '[ERROR] Not configured'}")
    
    if not openai_key and not anthropic_key:
        print("\n[WARNING]️  WARNING: No external AI APIs configured!")
        print("   Current setup relies on:")
        print("   - GPT-OSS 20B (Enhanced Fallback Mode)")
        print("   - GPT-OSS 120B (Enhanced Fallback Mode)")
        print("   - Mock AI responses")
        print("\n   For optimal performance, configure:")
        print("   - OPENAI_API_KEY for GPT-4 access")
        print("   - ANTHROPIC_API_KEY for Claude access")
    else:
        print("\n[CHECK] External AI APIs available for optimal performance")
    
    print()

def recommend_optimizations():
    """Recommend AI performance optimizations"""
    print("AI PERFORMANCE OPTIMIZATIONS")
    print("=" * 50)
    
    print("CURRENT SETUP:")
    print("- GPT-OSS 20B: Enhanced Fallback Mode (0.1s response)")
    print("- GPT-OSS 120B: Enhanced Fallback Mode (0.2s response)")
    print("- Main Server: Mock AI endpoints (instant response)")
    print("- Revolutionary Server: Not running (string formatting error)")
    
    print("\nOPTIMIZATION RECOMMENDATIONS:")
    print("1. Fix Revolutionary Server string formatting error")
    print("2. Configure OpenAI API key for real GPT-4 access")
    print("3. Configure Anthropic API key for Claude access")
    print("4. Enable real model loading (requires 240GB+ RAM for 120B)")
    print("5. Implement AI response caching")
    print("6. Add AI load balancing")
    print("7. Enable AI performance monitoring")
    
    print("\nPERFORMANCE TARGETS:")
    print("- Response Time: <100ms for trading decisions")
    print("- Accuracy: >85% for market predictions")
    print("- Uptime: >99.9% for AI services")
    print("- Memory Usage: <80% of available RAM")
    
    print()

def main():
    """Main analysis function"""
    print("PROMETHEUS AI PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Test AI performance
    test_ai_performance()
    
    # Analyze configuration
    analyze_ai_configuration()
    
    # Recommend optimizations
    recommend_optimizations()
    
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()


