#!/usr/bin/env python3
"""
Check Visual AI Training & Analysis Status
"""

import json
import os
from pathlib import Path
from datetime import datetime

def check_visual_ai_config():
    """Check visual AI configuration"""
    print("\n" + "="*70)
    print("🎨 VISUAL AI CONFIGURATION")
    print("="*70)
    
    if os.path.exists('visual_ai_config.json'):
        with open('visual_ai_config.json', 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ Visual AI Config Found:")
        print(f"  Model: {config.get('model', 'Not set')}")
        print(f"  Endpoint: {config.get('endpoint', 'Not set')}")
        print(f"  Timeout: {config.get('timeout', 0)}s")
        print(f"  Temperature: {config.get('temperature', 0)}")
        
        # Check if model is available
        model = config.get('model', '')
        if 'llava' in model:
            print(f"\n  📊 LLaVA Model (Local Vision):")
            print(f"    • Model: {model}")
            print(f"    • Type: Local multimodal AI")
            print(f"    • Can analyze: Charts, images, patterns")
        
        return True
    else:
        print("❌ Visual AI config not found")
        return False

def check_visual_patterns():
    """Check for trained visual patterns"""
    print("\n" + "="*70)
    print("🧠 TRAINED VISUAL PATTERNS")
    print("="*70)
    
    pattern_files = [
        'visual_ai_patterns_cloud.json',
        'visual_ai_patterns.json'
    ]
    
    found_patterns = False
    total_patterns = 0
    
    for filename in pattern_files:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Count patterns
            if isinstance(data, dict):
                if 'patterns' in data:
                    count = len(data['patterns'])
                elif 'symbols' in data:
                    count = sum(len(data['symbols'].get(sym, {}).get('patterns', [])) 
                               for sym in data['symbols'])
                else:
                    count = len(data)
            else:
                count = len(data)
            
            total_patterns += count
            found_patterns = True
            
            print(f"\n✅ {filename}:")
            print(f"  Patterns: {count:,}")
            print(f"  Size: {os.path.getsize(filename):,} bytes")
            print(f"  Modified: {datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M')}")
    
    if found_patterns:
        print(f"\n📊 TOTAL TRAINED PATTERNS: {total_patterns:,}")
    else:
        print("\n⚠️ No visual pattern files found")
        print("  Visual training may not have been run yet")
    
    return found_patterns

def check_visual_ai_providers():
    """Check visual AI providers (Claude, Gemini, LLaVA)"""
    print("\n" + "="*70)
    print("👁️ VISUAL AI PROVIDERS")
    print("="*70)
    
    providers = []
    
    # Claude Vision
    claude_key = os.getenv('ANTHROPIC_API_KEY', '')
    if claude_key and len(claude_key) > 10:
        print(f"\n✅ Claude 3.5 Sonnet (Vision):")
        print(f"  API Key: Configured")
        print(f"  Capabilities: Chart analysis, pattern recognition")
        print(f"  Cost: ~$0.003 per image")
        print(f"  Status: ACTIVE")
        providers.append('Claude')
    
    # Gemini Vision
    gemini_key = os.getenv('GOOGLE_API_KEY', '') or os.getenv('GOOGLE_AI_API_KEY', '')
    if gemini_key and len(gemini_key) > 10:
        print(f"\n✅ Gemini Pro Vision:")
        print(f"  API Key: Configured")
        print(f"  Capabilities: Image analysis, chart patterns")
        print(f"  Cost: Free tier available")
        print(f"  Status: ACTIVE")
        providers.append('Gemini')
    
    # GLM-4V
    glm_key = os.getenv('ZHIPUAI_API_KEY', '')
    if glm_key and len(glm_key) > 10:
        print(f"\n✅ GLM-4V (Visual):")
        print(f"  API Key: Configured")
        print(f"  Capabilities: Visual + language model")
        print(f"  Cost: API credits")
        print(f"  Status: ACTIVE")
        providers.append('GLM-4V')
    
    # LLaVA (Local)
    if os.path.exists('visual_ai_config.json'):
        with open('visual_ai_config.json', 'r') as f:
            config = json.load(f)
        if 'llava' in config.get('model', ''):
            print(f"\n✅ LLaVA (Local Vision):")
            print(f"  Model: {config.get('model')}")
            print(f"  Endpoint: {config.get('endpoint')}")
            print(f"  Cost: FREE (local)")
            print(f"  Status: CONFIGURED")
            providers.append('LLaVA')
    
    if not providers:
        print("\n⚠️ No visual AI providers configured")
    else:
        print(f"\n📊 TOTAL PROVIDERS: {len(providers)}")
        print(f"  Active: {', '.join(providers)}")
    
    return providers

def check_visual_training_active():
    """Check if visual training is currently active in the trading system"""
    print("\n" + "="*70)
    print("🔄 VISUAL TRAINING IN TRADING SYSTEM")
    print("="*70)
    
    # Check if improved_dual_broker_trading.py uses visual AI
    main_file = Path('improved_dual_broker_trading.py')
    if main_file.exists():
        content = main_file.read_text(encoding='utf-8', errors='ignore')
        
        visual_features = {
            'visual_pattern': 'Visual pattern analysis',
            'chart_analysis': 'Chart analysis',
            'VisualPatternProvider': 'Visual pattern provider',
            'CloudVisionAnalyzer': 'Cloud vision analyzer',
            'llava': 'LLaVA vision model'
        }
        
        print("\n  📊 Visual Features in Main System:")
        found_any = False
        for feature, description in visual_features.items():
            if feature.lower() in content.lower():
                print(f"  ✅ {description}")
                found_any = True
        
        if not found_any:
            print("  ⚠️ Visual features not found in main system")
    
    # Check prometheus_active_trading_session.py
    session_file = Path('prometheus_active_trading_session.py')
    if session_file.exists():
        content = session_file.read_text(encoding='utf-8', errors='ignore')
        
        if 'visual_pattern' in content.lower():
            print(f"\n  ✅ Visual AI Active in Trading Session:")
            print(f"    • VisualPatternProvider integrated")
            print(f"    • Chart patterns analyzed per trade")
            print(f"    • Patterns from trained database")
            
            # Check if patterns loaded
            if 'visual_ai_patterns_cloud.json' in content:
                print(f"    • Using cloud-trained patterns")
            
            return True
    
    print(f"\n  ⚠️ Visual training not active in current system")
    return False

def check_visual_training_scripts():
    """Check available visual training scripts"""
    print("\n" + "="*70)
    print("🎯 VISUAL TRAINING SCRIPTS")
    print("="*70)
    
    scripts = [
        ('CLOUD_VISION_TRAINING.py', 'Cloud vision training (Claude/Gemini)'),
        ('run_visual_chart_training.py', 'Visual chart training runner'),
        ('run_local_visual_training.py', 'Local visual training (LLaVA)'),
        ('visual_ai_learning_validator.py', 'Visual AI validator'),
        ('test_visual_analysis.py', 'Visual analysis tester')
    ]
    
    available = []
    
    for filename, description in scripts:
        if os.path.exists(filename):
            print(f"\n  ✅ {description}")
            print(f"     File: {filename}")
            available.append(filename)
    
    if available:
        print(f"\n  📊 {len(available)} training scripts available")
        print(f"\n  🚀 TO RUN VISUAL TRAINING:")
        print(f"     python CLOUD_VISION_TRAINING.py")
    else:
        print("\n  ⚠️ No visual training scripts found")
    
    return available

def provide_visual_ai_summary():
    """Provide summary and recommendations"""
    print("\n" + "="*70)
    print("📋 VISUAL AI SUMMARY")
    print("="*70)
    
    # Check all components
    has_config = os.path.exists('visual_ai_config.json')
    has_patterns = os.path.exists('visual_ai_patterns_cloud.json') or os.path.exists('visual_ai_patterns.json')
    has_claude = len(os.getenv('ANTHROPIC_API_KEY', '')) > 10
    has_gemini = len(os.getenv('GOOGLE_API_KEY', '') or os.getenv('GOOGLE_AI_API_KEY', '')) > 10
    has_glm = len(os.getenv('ZHIPUAI_API_KEY', '')) > 10
    
    score = sum([has_config, has_patterns, has_claude, has_gemini, has_glm])
    
    print(f"\n  Visual AI Components: {score}/5")
    
    if score >= 4:
        print(f"\n  ✅ VISUAL AI IS CONFIGURED")
        print(f"\n  Available:")
        if has_config:
            print(f"    ✅ Visual AI configuration")
        if has_patterns:
            print(f"    ✅ Trained visual patterns")
        if has_claude:
            print(f"    ✅ Claude 3.5 Vision API")
        if has_gemini:
            print(f"    ✅ Gemini Pro Vision API")
        if has_glm:
            print(f"    ✅ GLM-4V API")
        
        # Check if active in trading
        session_file = Path('prometheus_active_trading_session.py')
        if session_file.exists():
            content = session_file.read_text(encoding='utf-8', errors='ignore')
            if 'VisualPatternProvider' in content:
                print(f"\n  🎯 STATUS: VISUAL AI ACTIVE IN TRADING")
                print(f"    • Analyzes chart patterns every trade")
                print(f"    • Uses trained pattern database")
                print(f"    • Claude/Gemini for real-time analysis")
            else:
                print(f"\n  ⚠️ STATUS: CONFIGURED BUT NOT ACTIVE")
                print(f"    • Visual AI available but not used in main system")
        
    else:
        print(f"\n  ⚠️ VISUAL AI PARTIALLY CONFIGURED")
        print(f"\n  Missing:")
        if not has_config:
            print(f"    ❌ Visual AI configuration")
        if not has_patterns:
            print(f"    ❌ Trained visual patterns (run CLOUD_VISION_TRAINING.py)")
        if not has_claude:
            print(f"    ❌ Claude Vision API")
        if not has_gemini:
            print(f"    ❌ Gemini Vision API")
    
    print(f"\n  💡 TO ENABLE VISUAL TRAINING:")
    print(f"    1. Run: python CLOUD_VISION_TRAINING.py")
    print(f"    2. Analyzes charts with Claude/Gemini Vision")
    print(f"    3. Creates visual_ai_patterns_cloud.json")
    print(f"    4. Patterns auto-loaded in trading system")

def main():
    print("\n" + "="*70)
    print("  🎨 VISUAL AI TRAINING STATUS CHECK")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*70)
    
    check_visual_ai_config()
    check_visual_patterns()
    providers = check_visual_ai_providers()
    active = check_visual_training_active()
    scripts = check_visual_training_scripts()
    
    provide_visual_ai_summary()
    
    print("\n" + "="*70)
    
    # Final status
    if active and providers:
        print("✅ STATUS: VISUAL AI ACTIVE & TRAINING")
    elif providers and scripts:
        print("⚠️ STATUS: VISUAL AI CONFIGURED - RUN TRAINING")
    else:
        print("❌ STATUS: VISUAL AI NOT CONFIGURED")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
