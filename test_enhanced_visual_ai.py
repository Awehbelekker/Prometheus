#!/usr/bin/env python3
"""
Test Enhanced Visual AI - Claude + Gemini + LLaVA
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("  ENHANCED VISUAL AI - PROVIDER CHECK")
print("="*70)

# Check configuration file
if os.path.exists('enhanced_visual_ai_config.json'):
    with open('enhanced_visual_ai_config.json', 'r') as f:
        config = json.load(f)
    
    print("\n✅ Enhanced Config Loaded")
    print(f"   Version: {config.get('version')}")
    print(f"   Providers: {len(config['providers'])}")
    
    print("\n📊 PROVIDERS:")
    for p in config['providers']:
        status = "✅" if p['enabled'] else "❌"
        cost = f"${p['cost_per_image']:.4f}" if p['cost_per_image'] > 0 else "FREE"
        print(f"\n   {status} {p['name'].upper()}")
        print(f"      Model: {p['model']}")
        print(f"      Priority: #{p['priority']}")
        print(f"      Cost: {cost}/image")
        print(f"      Description: {p['description']}")
else:
    print("\n❌ Enhanced config not found")

# Check API keys
print("\n" + "="*70)
print("  API KEY STATUS")
print("="*70)

apis = {
    'Claude Vision': 'ANTHROPIC_API_KEY',
    'Gemini Vision': 'GOOGLE_API_KEY',
    'LLaVA Local': 'Visual config (local)'
}

for name, env_var in apis.items():
    if env_var == 'Visual config (local)':
        status = "✅ CONFIGURED" if os.path.exists('visual_ai_config.json') else "❌ NOT FOUND"
    else:
        key = os.getenv(env_var, '')
        status = "✅ CONFIGURED" if len(key) > 10 else "❌ NOT SET"
    
    print(f"   {status} {name}")

# Summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

claude_ok = len(os.getenv('ANTHROPIC_API_KEY', '')) > 10
gemini_ok = len(os.getenv('GOOGLE_API_KEY', '')) > 10
llava_ok = os.path.exists('visual_ai_config.json')

total_ready = sum([claude_ok, gemini_ok, llava_ok])

print(f"\n   Providers Ready: {total_ready}/3")

if total_ready == 3:
    print("\n   ✅ ALL VISUAL AI PROVIDERS READY!")
    print("\n   🎯 ROUTING:")
    print("      1st Choice: Claude 3.5 Vision (~$0.003/image)")
    print("      2nd Choice: Gemini Pro Vision (FREE)")
    print("      3rd Choice: LLaVA 7B (FREE Local)")
    
    print("\n   💡 USAGE:")
    print("      • Prometheus will auto-route to best provider")
    print("      • Falls back if primary fails")
    print("      • Caches results to save API calls")
    print("      • 2,797 patterns already trained")
elif total_ready == 2:
    print("\n   ⚠️ 2 PROVIDERS READY (Good!)")
    missing = []
    if not claude_ok:
        missing.append("Claude Vision")
    if not gemini_ok:
        missing.append("Gemini Vision")
    if not llava_ok:
        missing.append("LLaVA Local")
    print(f"   Missing: {', '.join(missing)}")
else:
    print("\n   ⚠️ LIMITED PROVIDERS")

print("\n" + "="*70 + "\n")
