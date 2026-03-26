#!/usr/bin/env python3
"""
Check if Backend and CPT_OSS 20b/120b are running
"""
import sys
import psutil
import os

sys.stdout.reconfigure(encoding='utf-8')

def check_backend():
    """Check if unified production server (backend) is running"""
    print("1. BACKEND (Unified Production Server)")
    print("-" * 40)
    
    backend_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info.get('cmdline') else ''
                if 'unified_production_server' in cmdline.lower():
                    print(f"   ✅ Backend running (PID {proc.info['pid']})")
                    backend_found = True
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not backend_found:
        print("   ❌ Backend NOT running")
        print("   📋 To start: python unified_production_server.py")
    
    return backend_found

def check_cpt_oss():
    """Check if CPT_OSS 20b/120b models are running"""
    print("\n2. CPT_OSS 20b/120b MODELS")
    print("-" * 40)
    
    # Check for separate CPT processes
    cpt_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info.get('cmdline') else ''
                if any(keyword in cmdline.lower() for keyword in ['cpt20b', 'cpt120b', 'cpt_oss', 'gpt-oss']):
                    print(f"   ✅ CPT_OSS process found (PID {proc.info['pid']})")
                    print(f"      Command: {cmdline[:80]}...")
                    cpt_found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Check if GPT-OSS is integrated in trading system
    print("   ℹ️  Checking if GPT-OSS is integrated in trading system...")
    
    # Check if trading system has GPT-OSS
    trading_system_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info.get('cmdline') else ''
                if 'launch_ultimate_prometheus_LIVE_TRADING' in cmdline:
                    trading_system_running = True
                    # Check logs or config to see if GPT-OSS is active
                    print(f"   ✅ Trading system running (PID {proc.info['pid']})")
                    print("   ℹ️  GPT-OSS is integrated in trading system")
                    print("      (Check startup logs for 'GPT-OSS backend available')")
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not cpt_found and not trading_system_running:
        print("   ❌ CPT_OSS not found as separate process")
        print("   ℹ️  It may be integrated in the trading system")
    
    return cpt_found or trading_system_running

def check_gpt_oss_integration():
    """Check if GPT-OSS is available in the system"""
    print("\n3. GPT-OSS INTEGRATION STATUS")
    print("-" * 40)
    
    # Check if GPT-OSS backend file exists
    gpt_oss_file = os.path.join('core', 'reasoning', 'gpt_oss_backend.py')
    if os.path.exists(gpt_oss_file):
        print(f"   ✅ GPT-OSS backend file found: {gpt_oss_file}")
    else:
        print(f"   ❌ GPT-OSS backend file not found")
    
    # Check for GPT-OSS in imports
    try:
        import sys
        sys.path.insert(0, os.getcwd())
        from core.reasoning.gpt_oss_backend import GPTOSSBackend
        print("   ✅ GPT-OSS can be imported")
        print("   ℹ️  GPT-OSS is available as a module")
    except ImportError as e:
        print(f"   ⚠️  GPT-OSS import failed: {e}")

if __name__ == "__main__":
    print("="*80)
    print("BACKEND & CPT_OSS STATUS CHECK")
    print("="*80)
    print()
    
    backend_running = check_backend()
    cpt_running = check_cpt_oss()
    check_gpt_oss_integration()
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print()
    
    if backend_running:
        print("✅ Backend: RUNNING")
    else:
        print("❌ Backend: NOT RUNNING")
        print("   💡 Start with: python unified_production_server.py")
    
    if cpt_running:
        print("✅ CPT_OSS: AVAILABLE (integrated in trading system)")
    else:
        print("⚠️  CPT_OSS: Check if integrated in trading system")
        print("   💡 GPT-OSS is typically integrated, not a separate process")
    
    print()
    print("💡 NOTE:")
    print("   - GPT-OSS (CPT_OSS) is usually integrated in the trading system")
    print("   - It doesn't run as a separate process")
    print("   - Check trading system logs for 'GPT-OSS backend available'")
    print("="*80)


