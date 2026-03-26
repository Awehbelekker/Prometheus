#!/usr/bin/env python3
"""Quick test of Cloud Vision system"""

import json
from pathlib import Path

print("=" * 60)
print("Testing PROMETHEUS Cloud Vision System")
print("=" * 60)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig
    print("   OK: cloud_vision_analyzer")
except Exception as e:
    print(f"   FAIL: cloud_vision_analyzer - {e}")

try:
    from core.visual_pattern_provider import VisualPatternProvider
    print("   OK: visual_pattern_provider")
except Exception as e:
    print(f"   FAIL: visual_pattern_provider - {e}")

# Test 2: Check config
print("\n2. Testing CloudVisionConfig...")
config = CloudVisionConfig()
print(f"   Provider: {config.provider}")
print(f"   Model: {config.model}")
print(f"   API Key Set: {'YES' if config.api_key else 'NO - Need to set GOOGLE_AI_API_KEY'}")
print(f"   Pattern Categories: {len(config.pattern_categories)}")

# Test 3: Analyzer
print("\n3. Testing CloudVisionAnalyzer...")
analyzer = CloudVisionAnalyzer(config)
print(f"   API Available: {analyzer.api_available}")

# Test 4: Check patterns file
print("\n4. Checking patterns file...")
patterns_file = Path("visual_ai_patterns.json")
if patterns_file.exists():
    with open(patterns_file) as f:
        data = json.load(f)
    print(f"   Patterns: {len(data.get('patterns', {}))}")
    print(f"   Total patterns found: {data.get('total_patterns', 0)}")
else:
    print("   No patterns file yet (will be created during training)")

# Test 5: Check charts
print("\n5. Checking charts...")
charts = list(Path("charts").glob("*.png"))
print(f"   Charts available: {len(charts)}")

# Test 6: Pattern provider
print("\n6. Testing VisualPatternProvider...")
provider = VisualPatternProvider()
print(f"   Patterns loaded: {len(provider.patterns)}")
symbols = provider.get_symbols_with_patterns()[:5]
print(f"   Symbols with data: {symbols}")

if symbols:
    consensus = provider.get_trend_consensus(symbols[0])
    print(f"   {symbols[0]} trend: {consensus['trend']}")

print("\n" + "=" * 60)
print("SYSTEM READY!")
print("=" * 60)
print("\nNext step: Get a Gemini API key and run training:")
print("  1. Go to: https://aistudio.google.com/apikey")
print("  2. Create API key (free)")
print("  3. Set: $env:GOOGLE_AI_API_KEY='your_key'")
print("  4. Run: python CLOUD_VISION_TRAINING.py")

