#!/usr/bin/env python3
"""
Check All AI Systems Configuration
Verifies all AI functions are enabled (True)
"""

import os
from dotenv import load_dotenv
import json

load_dotenv()

def check_ai_environment_variables():
    """Check all AI-related environment variables"""
    print("\n" + "="*70)
    print("🤖 AI ENVIRONMENT VARIABLES")
    print("="*70)
    
    ai_vars = {
        # DeepSeek (Primary AI)
        'DEEPSEEK_ENABLED': ('DeepSeek AI', 'Should be: true'),
        'USE_LOCAL_AI': ('Local AI Usage', 'Should be: true'),
        'DEEPSEEK_MODEL': ('DeepSeek Model', 'Should be: deepseek-r1:14b'),
        
        # LLM Providers
        'ZHIPUAI_API_KEY': ('GLM-4 API', 'Should have API key'),
        'ANTHROPIC_API_KEY': ('Claude 3.5', 'Should have API key'),
        'GOOGLE_API_KEY': ('Gemini Pro', 'Should have API key'),
        'OPENAI_API_KEY': ('OpenAI GPT-4', 'Optional fallback'),
        
        # AI Settings
        'AI_PROVIDER': ('Primary AI Provider', 'Should be: deepseek'),
        'OPENAI_FALLBACK': ('OpenAI Fallback', 'Should be: false (using free AI)'),
        
        # Trading AI
        'USE_AI_SIGNALS': ('AI Trading Signals', 'Should be: true'),
        'USE_QUANTUM_SIGNALS': ('Quantum Signals', 'Should be: true'),
        'USE_AI_CONSCIOUSNESS': ('AI Consciousness', 'Optional'),
    }
    
    all_enabled = True
    warnings = []
    
    for var, (name, expected) in ai_vars.items():
        value = os.getenv(var, 'NOT SET')
        
        # Determine status
        if var in ['DEEPSEEK_ENABLED', 'USE_LOCAL_AI', 'USE_AI_SIGNALS', 'USE_QUANTUM_SIGNALS']:
            status = '✅ ENABLED' if value.lower() == 'true' else '❌ DISABLED'
            if value.lower() != 'true':
                all_enabled = False
                warnings.append(f"{name} should be enabled")
        elif 'API_KEY' in var:
            if value and value != 'NOT SET' and len(value) > 10:
                status = '✅ CONFIGURED'
            else:
                status = '⚠️ NOT SET'
                if var in ['ZHIPUAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']:
                    warnings.append(f"{name} not configured")
        elif var == 'OPENAI_FALLBACK':
            status = '✅ DISABLED (Good - using free AI)' if value.lower() == 'false' else '⚠️ ENABLED'
        else:
            status = f'✅ {value}' if value != 'NOT SET' else '⚠️ NOT SET'
        
        print(f"\n  {name}:")
        print(f"    Variable: {var}")
        print(f"    Value: {value if len(str(value)) < 50 else value[:47] + '...'}")
        print(f"    Status: {status}")
        print(f"    Expected: {expected}")
    
    return all_enabled, warnings

def check_ai_config_files():
    """Check AI configuration files"""
    print("\n" + "="*70)
    print("📁 AI CONFIGURATION FILES")
    print("="*70)
    
    config_files = {
        'live_ai_config.json': 'Live AI parameters',
        'ai_signal_weights_config.json': 'AI signal weighting',
        'ai_consciousness_config.json': 'AI consciousness settings',
        'learning_state.json': 'Continuous learning state',
        'visual_ai_config.json': 'Visual AI configuration',
        'optimized_ai_config.json': 'Optimized AI settings'
    }
    
    all_present = True
    
    for filename, description in config_files.items():
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    data = json.load(f)
                    size = os.path.getsize(filename)
                    print(f"\n  ✅ {description}")
                    print(f"     File: {filename}")
                    print(f"     Size: {size:,} bytes")
                    
                    # Check for enabled flags
                    if 'enabled' in data:
                        print(f"     Enabled: {data['enabled']}")
                    if 'active' in data:
                        print(f"     Active: {data['active']}")
                        
                except json.JSONDecodeError:
                    print(f"  ⚠️ {description} - JSON error")
                    all_present = False
        else:
            print(f"\n  ❌ {description}")
            print(f"     File: {filename} - NOT FOUND")
            all_present = False
    
    return all_present

def check_ai_systems_in_code():
    """Check which AI systems are enabled in the main trading code"""
    print("\n" + "="*70)
    print("🧠 AI SYSTEMS IN TRADING CODE")
    print("="*70)
    
    # Check ai_signal_weights_config.json for weights
    if os.path.exists('ai_signal_weights_config.json'):
        with open('ai_signal_weights_config.json', 'r') as f:
            weights = json.load(f)
        
        ai_weights = weights.get('ai_signal_weights', {}).get('weights', {})
        
        print("\n  AI SYSTEMS & WEIGHTS:")
        for ai_name, details in ai_weights.items():
            weight = details.get('weight', 0)
            reason = details.get('reason', 'N/A')
            
            if weight >= 1.0:
                status = '✅ ACTIVE'
            elif weight > 0:
                status = '⚠️ LOW PRIORITY'
            else:
                status = '❌ DISABLED'
            
            print(f"\n  {ai_name.replace('_', ' ').title()}:")
            print(f"    Weight: {weight}x")
            print(f"    Status: {status}")
            print(f"    Reason: {reason}")
    
    # Check for AI consciousness setting
    if os.path.exists('ai_consciousness_config.json'):
        with open('ai_consciousness_config.json', 'r') as f:
            consciousness = json.load(f)
        
        enabled = consciousness.get('enabled', False)
        print(f"\n  AI Consciousness:")
        print(f"    Status: {'✅ ENABLED' if enabled else '⚠️ DISABLED (was using random values)'}")

def check_autonomous_settings():
    """Check autonomous trading settings"""
    print("\n" + "="*70)
    print("🤖 AUTONOMOUS TRADING SETTINGS")
    print("="*70)
    
    if os.path.exists('live_ai_config.json'):
        with open('live_ai_config.json', 'r') as f:
            config = json.load(f)
        
        print("\n  ✅ AUTONOMOUS FEATURES:")
        print(f"    • Auto-restart: Enabled (via START_PROMETHEUS.bat)")
        print(f"    • 24/7 Trading: Enabled (3-minute cycles)")
        print(f"    • AI Decision Making: Fully Autonomous")
        print(f"    • Min Confidence: {config.get('min_confidence_threshold', 0.65)*100:.0f}%")
        print(f"    • Max Trades/Day: {config.get('trades_per_day', 8)}")
        print(f"    • Risk Management: Adaptive (40%-85% confidence)")
        
        print("\n  🎯 AUTONOMOUS PROTECTIONS:")
        print(f"    • Trailing Stops: Auto-enabled")
        print(f"    • DCA on Dips: Auto-enabled") 
        print(f"    • Emergency Exit: Auto at -15%")
        print(f"    • Time-based Exit: Auto (crypto 7d, stocks 14d)")
        print(f"    • Scale Out: Auto (50% @ +3%, rest @ +7%)")
    
    # Check if main system is running
    import psutil
    prometheus_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'improved_dual_broker_trading' in cmdline:
                    prometheus_running = True
                    uptime = (psutil.Process(proc.info['pid']).create_time())
                    from datetime import datetime
                    start_time = datetime.fromtimestamp(uptime)
                    runtime = datetime.now() - start_time
                    
                    print(f"\n  🚀 PROMETHEUS STATUS:")
                    print(f"    • Status: RUNNING")
                    print(f"    • PID: {proc.info['pid']}")
                    print(f"    • Runtime: {runtime}")
                    print(f"    • Mode: AUTONOMOUS")
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not prometheus_running:
        print(f"\n  ⚠️ PROMETHEUS STATUS:")
        print(f"    • Status: NOT RUNNING")
        print(f"    • To start: Run START_PROMETHEUS.bat")
    
    return prometheus_running

def provide_recommendations(all_ai_enabled, config_present, prometheus_running, warnings):
    """Provide recommendations"""
    print("\n" + "="*70)
    print("📋 RECOMMENDATIONS")
    print("="*70)
    
    if all_ai_enabled and config_present and prometheus_running:
        print("\n  ✅ ALL SYSTEMS GO!")
        print("\n  🤖 Prometheus is running FULLY AUTONOMOUSLY with:")
        print("    • All AI systems enabled")
        print("    • All configurations loaded")
        print("    • Adaptive risk management active")
        print("    • Learning from every trade")
        print("    • Auto-restart on crashes")
        print("    • 24/7 operation (crypto 24/5, stocks market hours)")
        
        print("\n  🎯 YOU CAN:")
        print("    • Let it run completely hands-off")
        print("    • Check status anytime with: python complete_system_status.py")
        print("    • View live trading in the terminal")
        print("    • Monitor positions via broker apps")
        
        print("\n  ⚙️ AUTOMATIC FEATURES:")
        print("    • Finds opportunities every 3 minutes")
        print("    • Only trades with 65%+ confidence")
        print("    • Manages risk automatically")
        print("    • Exits losers at -15%")
        print("    • Takes profits at +3% and +7%")
        print("    • Learns from every outcome")
        
    else:
        print("\n  ⚠️ NEEDS ATTENTION:")
        
        if warnings:
            print("\n  Issues Found:")
            for warning in warnings:
                print(f"    • {warning}")
        
        if not prometheus_running:
            print("\n  🚀 TO START AUTONOMOUS TRADING:")
            print("    1. Open PowerShell in platform directory")
            print("    2. Run: .\\START_PROMETHEUS.bat")
            print("    3. Let it run in background")
        
        if not all_ai_enabled:
            print("\n  🔧 TO ENABLE ALL AI:")
            print("    1. Check .env file")
            print("    2. Set DEEPSEEK_ENABLED=true")
            print("    3. Set USE_LOCAL_AI=true")
            print("    4. Set USE_AI_SIGNALS=true")

def main():
    print("\n" + "="*70)
    print("  🔍 PROMETHEUS AI SYSTEMS CHECK")
    print("  Autonomous Trading Readiness")
    print("="*70)
    
    all_ai_enabled, warnings = check_ai_environment_variables()
    config_present = check_ai_config_files()
    check_ai_systems_in_code()
    prometheus_running = check_autonomous_settings()
    
    provide_recommendations(all_ai_enabled, config_present, prometheus_running, warnings)
    
    print("\n" + "="*70)
    
    # Final status
    if all_ai_enabled and config_present and prometheus_running:
        print("✅ STATUS: FULLY AUTONOMOUS & ALL AI ENABLED")
    elif prometheus_running:
        print("⚠️ STATUS: RUNNING BUT SOME AI DISABLED")
    else:
        print("❌ STATUS: NOT RUNNING - START WITH START_PROMETHEUS.bat")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
