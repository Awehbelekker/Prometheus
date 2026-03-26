#!/usr/bin/env python3
"""Quick AI Systems Check - HRM + DeepSeek + ThinkMesh"""
import sys
import time
import logging
logging.basicConfig(level=logging.WARNING)

print("="*60)
print("QUICK AI SYSTEMS CHECK")
print("="*60)

# Test 1: HRM
print("\n[1] HRM Official...")
try:
    from core.hrm_official_integration import get_official_hrm_adapter
    adapter = get_official_hrm_adapter()
    if adapter and len(adapter.models) > 0:
        print(f"    OK HRM LOADED: {len(adapter.models)} checkpoints")
        for name in adapter.models.keys():
            print(f"       - {name}")
    else:
        print("    FAIL HRM not loaded")
except Exception as e:
    print(f"    ERROR HRM: {e}")

# Test 2: DeepSeek Adapter
print("\n[2] DeepSeek Adapter...")
try:
    from core.deepseek_adapter import DeepSeekAdapter
    adapter = DeepSeekAdapter(model="deepseek-r1:14b")
    print(f"    OK DeepSeek Adapter initialized")
    print(f"       Model: {adapter.model}")
    print(f"       Endpoint: {adapter.endpoint}")
    print(f"       Timeout: {adapter.timeout}s")
except Exception as e:
    print(f"    ERROR DeepSeek: {e}")

# Test 3: ThinkMesh
print("\n[3] ThinkMesh Enhanced...")
try:
    from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter
    adapter = EnhancedThinkMeshAdapter(enabled=True)
    print(f"    OK ThinkMesh Adapter initialized")
    print(f"       Enabled: {adapter.enabled}")
    print(f"       ThinkMesh Available: {adapter.thinkmesh_available}")
except Exception as e:
    print(f"    ERROR ThinkMesh: {e}")

# Test 4: Ollama connectivity (quick)
print("\n[4] Ollama Connectivity...")
try:
    import requests
    start = time.time()
    r = requests.get("http://localhost:11434/api/version", timeout=5)
    elapsed = time.time() - start
    if r.status_code == 200:
        print(f"    OK Ollama responding in {elapsed*1000:.0f}ms")
        print(f"       Response: {r.text[:50]}")
    else:
        print(f"    WARN Ollama returned status {r.status_code}")
except requests.exceptions.Timeout:
    print("    WARN Ollama timeout (may be busy with model)")
except Exception as e:
    print(f"    ERROR Ollama: {e}")

# Test 5: HRM Runtime Metrics
print("\n[5] HRM Runtime Metrics...")
try:
    import json
    with open("hrm_checkpoints/hrm_runtime_metrics.json", "r") as f:
        metrics = json.load(f)
    print(f"    OK HRM Metrics file found")
    print(f"       Total Decisions: {metrics.get('total_decisions', 0)}")
    print(f"       Timestamp: {metrics.get('timestamp', 'N/A')}")
except Exception as e:
    print(f"    ERROR Metrics: {e}")

print("\n" + "="*60)
print("CHECK COMPLETE")
print("="*60)

