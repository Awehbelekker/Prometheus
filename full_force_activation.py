#!/usr/bin/env python3
"""
🚀 PROMETHEUS FULL-FORCE ACTIVATION SCRIPT
Activates maximum trading capacity with GPT-OSS AI intelligence
"""

import requests
import time
import json
from datetime import datetime

def check_system_status():
    """Check current system status before activation"""
    print("🔍 PRE-ACTIVATION SYSTEM STATUS CHECK")
    print("=" * 60)
    
    status = {}
    
    # Check backend server
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        status['backend'] = response.status_code == 200
        print(f"   Backend Server: {'[CHECK] RUNNING' if status['backend'] else '[ERROR] DOWN'}")
    except:
        status['backend'] = False
        print("   Backend Server: [ERROR] DOWN")
    
    # Check GPT-OSS models
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        status['gpt_oss_20b'] = response.status_code == 200
        print(f"   GPT-OSS 20B (Port 5000): {'[CHECK] RUNNING' if status['gpt_oss_20b'] else '[ERROR] DOWN'}")
    except:
        status['gpt_oss_20b'] = False
        print("   GPT-OSS 20B (Port 5000): [ERROR] DOWN")
    
    try:
        response = requests.get("http://localhost:5001/health", timeout=2)
        status['gpt_oss_120b'] = response.status_code == 200
        print(f"   GPT-OSS 120B (Port 5001): {'[CHECK] RUNNING' if status['gpt_oss_120b'] else '[ERROR] DOWN'}")
    except:
        status['gpt_oss_120b'] = False
        print("   GPT-OSS 120B (Port 5001): [ERROR] DOWN")
    
    # Check live trading session
    try:
        response = requests.get("http://localhost:8000/api/paper-trading/performance", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status['live_session'] = data.get('active_sessions', 0) > 0
            status['balance'] = data.get('current_balance', 0)
            status['ai_decisions'] = data.get('ai_decisions', 0)
            print(f"   Live Trading Session: {'[CHECK] ACTIVE' if status['live_session'] else '[ERROR] INACTIVE'}")
            print(f"   Account Balance: ${status['balance']:.2f}")
            print(f"   AI Decisions (Pre-activation): {status['ai_decisions']}")
        else:
            status['live_session'] = False
    except:
        status['live_session'] = False
        print("   Live Trading Session: [ERROR] UNKNOWN")
    
    # Check AI status
    try:
        response = requests.get("http://localhost:8000/api/ai/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status['ai_available'] = data.get('ai_available', False)
            status['models_count'] = len(data.get('available_models', []))
            print(f"   AI Available (Pre-activation): {'[CHECK] TRUE' if status['ai_available'] else '[ERROR] FALSE'}")
            print(f"   Available Models: {status['models_count']}")
        else:
            status['ai_available'] = False
    except:
        status['ai_available'] = False
        print("   AI Available: [ERROR] UNKNOWN")
    
    # Check Revolutionary Engines
    try:
        response = requests.get("http://localhost:8000/api/revolutionary/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            engines = data.get('engines', {})
            active_engines = sum(1 for engine_status in engines.values() if engine_status)
            status['engines_active'] = active_engines
            status['engines_total'] = len(engines)
            print(f"   Revolutionary Engines: {active_engines}/{len(engines)} ACTIVE")
        else:
            status['engines_active'] = 0
    except:
        status['engines_active'] = 0
        print("   Revolutionary Engines: [ERROR] UNKNOWN")
    
    return status

def validate_gpt_oss_readiness():
    """Validate GPT-OSS models are ready for full-force trading"""
    print("\n🤖 GPT-OSS READINESS VALIDATION")
    print("=" * 60)
    
    models_ready = 0
    
    # Test 20B model
    try:
        test_payload = {
            "prompt": "System: You are PROMETHEUS AI trading assistant.\n\nUser: Test connection - respond with 'GPT-OSS 20B READY'\n\nAssistant:",
            "max_tokens": 50,
            "temperature": 0.1
        }
        response = requests.post("http://localhost:5000/generate", json=test_payload, timeout=10)
        if response.status_code == 200:
            models_ready += 1
            print("   [CHECK] GPT-OSS 20B Model: READY FOR TRADING")
        else:
            print(f"   [ERROR] GPT-OSS 20B Model: ERROR {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] GPT-OSS 20B Model: CONNECTION FAILED - {str(e)[:50]}")
    
    # Test 120B model
    try:
        test_payload = {
            "prompt": "System: You are PROMETHEUS AI trading assistant.\n\nUser: Test connection - respond with 'GPT-OSS 120B READY'\n\nAssistant:",
            "max_tokens": 50,
            "temperature": 0.1
        }
        response = requests.post("http://localhost:5001/generate", json=test_payload, timeout=15)
        if response.status_code == 200:
            models_ready += 1
            print("   [CHECK] GPT-OSS 120B Model: READY FOR TRADING")
        else:
            print(f"   [ERROR] GPT-OSS 120B Model: ERROR {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] GPT-OSS 120B Model: CONNECTION FAILED - {str(e)[:50]}")
    
    print(f"\n   📊 MODELS READY: {models_ready}/2")
    return models_ready >= 1  # At least one model must be ready

def create_restart_instructions():
    """Create detailed restart instructions"""
    print("\n🔄 BACKEND SERVER RESTART REQUIRED")
    print("=" * 60)
    print("[WARNING]️  CRITICAL: Server restart needed to activate GPT-OSS provider")
    print("⏱️  Expected downtime: 30-60 seconds")
    print("🛡️  Live trading session will resume automatically")
    print("\n📋 RESTART INSTRUCTIONS:")
    print("   1. Go to the terminal running the backend server")
    print("   2. Press Ctrl+C to stop the server")
    print("   3. Wait for clean shutdown (5-10 seconds)")
    print("   4. Run: python PROMETHEUS-Enterprise-Package/backend/unified_production_server.py")
    print("   5. Wait for 'Server started' message")
    print("   6. Run this script again to validate activation")
    print("\n🚨 IMPORTANT: Keep Interactive Brokers TWS running during restart")

def post_restart_validation():
    """Validate system after restart"""
    print("\n[CHECK] POST-RESTART VALIDATION")
    print("=" * 60)
    
    # Wait for server to fully initialize
    print("   ⏳ Waiting for server initialization...")
    time.sleep(10)
    
    validation_passed = True
    
    # Check AI status
    try:
        response = requests.get("http://localhost:8000/api/ai/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            ai_available = data.get('ai_available', False)
            available_models = data.get('available_models', [])
            
            print(f"   🤖 AI Available: {'[CHECK] TRUE' if ai_available else '[ERROR] FALSE'}")
            print(f"   📊 Available Models: {len(available_models)}")
            
            # Check for GPT-OSS models
            gpt_oss_models = [m for m in available_models if 'gpt_oss' in m.lower()]
            if gpt_oss_models:
                print(f"   🚀 GPT-OSS Models: {gpt_oss_models}")
            else:
                print("   [WARNING]️ GPT-OSS Models: NOT DETECTED")
                validation_passed = False
        else:
            print("   [ERROR] AI Status: UNAVAILABLE")
            validation_passed = False
    except Exception as e:
        print(f"   [ERROR] AI Status Check Failed: {str(e)[:50]}")
        validation_passed = False
    
    # Check Revolutionary Engines
    try:
        response = requests.get("http://localhost:8000/api/revolutionary/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            engines = data.get('engines', {})
            active_engines = sum(1 for status in engines.values() if status)
            print(f"   [LIGHTNING] Revolutionary Engines: {active_engines}/{len(engines)} ACTIVE")
            
            if active_engines == len(engines):
                print("   [CHECK] All Revolutionary Engines: OPERATIONAL")
            else:
                print("   [WARNING]️ Some Revolutionary Engines: NOT FULLY OPERATIONAL")
        else:
            print("   [ERROR] Revolutionary Engines: STATUS UNAVAILABLE")
            validation_passed = False
    except Exception as e:
        print(f"   [ERROR] Revolutionary Engines Check Failed: {str(e)[:50]}")
        validation_passed = False
    
    # Check live trading session restoration
    try:
        response = requests.get("http://localhost:8000/api/paper-trading/performance", timeout=10)
        if response.status_code == 200:
            data = response.json()
            active_sessions = data.get('active_sessions', 0)
            ai_decisions = data.get('ai_decisions', 0)
            
            print(f"   💰 Live Trading Sessions: {active_sessions}")
            print(f"   🧠 AI Decisions (Post-restart): {ai_decisions}")
            
            if active_sessions > 0:
                print("   [CHECK] Live Trading Session: RESTORED")
            else:
                print("   [WARNING]️ Live Trading Session: MAY NEED RESTART")
        else:
            print("   [ERROR] Trading Status: UNAVAILABLE")
    except Exception as e:
        print(f"   [ERROR] Trading Status Check Failed: {str(e)[:50]}")
    
    return validation_passed

def main():
    """Main activation function"""
    print("🚀 PROMETHEUS FULL-FORCE ACTIVATION")
    print("=" * 60)
    print(f"⏰ Activation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: Maximum trading capacity with GPT-OSS AI")
    print("=" * 60)
    
    # Phase 1: Pre-activation checks
    status = check_system_status()
    
    if not status.get('backend', False):
        print("\n[ERROR] ACTIVATION FAILED: Backend server not running")
        print("   Please start the backend server first")
        return False
    
    # Phase 2: GPT-OSS readiness validation
    if not validate_gpt_oss_readiness():
        print("\n[ERROR] ACTIVATION FAILED: GPT-OSS models not ready")
        print("   Please ensure GPT-OSS models are running on ports 5000 and 5001")
        return False
    
    # Phase 3: Check if restart is needed
    if not status.get('ai_available', False):
        print("\n🔄 RESTART REQUIRED: AI not currently available")
        create_restart_instructions()
        print("\n⏸️  ACTIVATION PAUSED: Please restart server and run script again")
        return False
    else:
        print("\n[CHECK] AI ALREADY AVAILABLE: Proceeding with validation")
        return post_restart_validation()

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 PROMETHEUS FULL-FORCE ACTIVATION COMPLETE!")
            print("   System ready for maximum trading performance")
        else:
            print("\n[WARNING]️ ACTIVATION INCOMPLETE: Review issues above")
    except KeyboardInterrupt:
        print("\n[WARNING]️ Activation interrupted by user")
    except Exception as e:
        print(f"\n💥 Activation error: {e}")
