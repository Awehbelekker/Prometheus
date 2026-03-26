"""Verify Enhanced Visual AI with GLM-4V"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  ENHANCED VISUAL AI - ALL 4 PROVIDERS")
print("=" * 60)

# Load config
with open('enhanced_visual_ai_config.json', 'r') as f:
    config = json.load(f)

providers = sorted(config['providers'], key=lambda x: x['priority'])

print(f"\nTotal Providers: {len(providers)}")
print("-" * 60)

for p in providers:
    name = p['name'].upper()
    model = p['model']
    desc = p['description']
    cost = p['cost_per_image']
    priority = p['priority']
    
    # Check API key
    if name == 'CLAUDE':
        key = os.getenv('ANTHROPIC_API_KEY', '')
        has_key = len(key) > 10
    elif name == 'GEMINI':
        key = os.getenv('GOOGLE_API_KEY', '')
        has_key = len(key) > 10
    elif name == 'GLM-4V':
        key = os.getenv('ZHIPUAI_API_KEY', '')
        has_key = len(key) > 10
    else:
        has_key = True  # Local doesn't need key
    
    status = "READY" if has_key else "NO API KEY"
    cost_str = f"${cost:.4f}" if cost > 0 else "FREE"
    
    print(f"\n#{priority} {name}")
    print(f"   Model: {model}")
    print(f"   Cost: {cost_str}/image")
    print(f"   Status: {'✅' if has_key else '❌'} {status}")
    print(f"   Description: {desc}")

print("\n" + "=" * 60)
print("  ROUTING ORDER")
print("=" * 60)
print("\nClaude ($0.003) → Gemini (FREE) → GLM-4V (FREE) → LLaVA (FREE)")
print("\n• Best quality first (Claude)")
print("• Free cloud options as backup (Gemini, GLM-4V)")
print("• Local fallback always available (LLaVA)")

# Check GLM-4V API key
glm_key = os.getenv('ZHIPUAI_API_KEY', '')
print("\n" + "=" * 60)
print("  GLM-4V STATUS")
print("=" * 60)
if glm_key and len(glm_key) > 10:
    print(f"\n✅ GLM-4V API Key: {glm_key[:15]}...{glm_key[-5:]}")
    print("✅ GLM-4V READY for visual chart analysis!")
    print("   • 10,000 FREE requests/day")
    print("   • Chinese AI with excellent pattern recognition")
    print("   • Provides FREE alternative to Claude")
else:
    print("\n❌ GLM-4V API Key not found")
    print("   Key should be in .env as ZHIPUAI_API_KEY")
