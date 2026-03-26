#!/usr/bin/env python3
"""
Check all Prometheus-related processes and identify duplicates/unnecessary ones
"""
import sys
import psutil
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def get_all_prometheus_processes():
    """Find all Prometheus-related processes"""
    keywords = [
        'prometheus',
        'trading',
        'launch_ultimate',
        'unified_production_server',
        'backend',
        'alpaca',
        'ib',
        'interactive_brokers',
        'cpt20b',
        'cpt120b'
    ]
    
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info.get('cmdline') else ''
                if any(keyword.lower() in cmdline.lower() for keyword in keywords):
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline[:100] if len(cmdline) > 100 else cmdline,
                        'cpu': proc.info.get('cpu_percent', 0),
                        'memory': proc.info.get('memory_percent', 0),
                        'create_time': proc.info.get('create_time', 0)
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes

def analyze_processes(processes):
    """Analyze processes for duplicates and issues"""
    print("="*80)
    print("PROMETHEUS PROCESS ANALYSIS")
    print("="*80)
    print()
    
    if not processes:
        print("✅ No Prometheus-related processes found")
        return
    
    # Group by script name
    by_script = defaultdict(list)
    for proc in processes:
        cmdline = proc['cmdline']
        # Extract script name
        if 'launch_ultimate_prometheus_LIVE_TRADING' in cmdline:
            by_script['launch_ultimate_prometheus_LIVE_TRADING'].append(proc)
        elif 'unified_production_server' in cmdline:
            by_script['unified_production_server'].append(proc)
        elif 'check_' in cmdline or 'verify_' in cmdline or 'diagnose_' in cmdline:
            by_script['diagnostic_scripts'].append(proc)
        else:
            by_script['other'].append(proc)
    
    # Check for duplicates
    print("📊 PROCESS BREAKDOWN:")
    print("-" * 40)
    
    issues_found = False
    
    # Main trading system
    main_trading = by_script.get('launch_ultimate_prometheus_LIVE_TRADING', [])
    if len(main_trading) > 1:
        print(f"⚠️  WARNING: {len(main_trading)} instances of trading system running!")
        print("   Only ONE should be running at a time")
        issues_found = True
        for proc in main_trading:
            print(f"      PID {proc['pid']}: {proc['cmdline'][:60]}...")
    elif len(main_trading) == 1:
        print(f"✅ Trading System: 1 instance (PID {main_trading[0]['pid']})")
    else:
        print("❌ Trading System: NOT RUNNING")
        issues_found = True
    
    # Unified production server
    unified = by_script.get('unified_production_server', [])
    if unified:
        if len(unified) > 1:
            print(f"⚠️  WARNING: {len(unified)} instances of unified server running!")
            issues_found = True
        else:
            print(f"ℹ️  Unified Server: 1 instance (PID {unified[0]['pid']})")
            print("   Note: Can run alongside trading system or standalone")
    
    # Diagnostic scripts
    diagnostic = by_script.get('diagnostic_scripts', [])
    if diagnostic:
        print(f"ℹ️  Diagnostic Scripts: {len(diagnostic)} running (OK - temporary)")
        for proc in diagnostic:
            print(f"      PID {proc['pid']}: {proc['cmdline'][:60]}...")
    
    # Other processes
    other = by_script.get('other', [])
    if other:
        print(f"ℹ️  Other Processes: {len(other)}")
        for proc in other:
            print(f"      PID {proc['pid']}: {proc['cmdline'][:60]}...")
    
    print()
    
    # Detailed process list
    print("📋 DETAILED PROCESS LIST:")
    print("-" * 40)
    print(f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'Command'}")
    print("-" * 80)
    
    for proc in sorted(processes, key=lambda x: x['create_time'], reverse=True):
        cmdline_short = proc['cmdline'][:50] + '...' if len(proc['cmdline']) > 50 else proc['cmdline']
        print(f"{proc['pid']:<8} {proc['cpu']:<8.1f} {proc['memory']:<8.1f} {cmdline_short}")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if len(main_trading) > 1:
        print("⚠️  ACTION REQUIRED:")
        print("   1. Stop duplicate trading system instances")
        print("   2. Keep only the most recent one (highest PID)")
        print("   3. Restart if needed")
        issues_found = True
    
    if len(unified) > 1:
        print("⚠️  ACTION REQUIRED:")
        print("   1. Stop duplicate unified server instances")
        print("   2. Keep only one instance")
        issues_found = True
    
    if not issues_found:
        print("✅ All processes look good!")
        print("   - One trading system instance (correct)")
        print("   - No duplicate processes detected")
        print("   - Diagnostic scripts are temporary (OK)")
    
    print()
    print("="*80)
    
    return issues_found

if __name__ == "__main__":
    processes = get_all_prometheus_processes()
    issues = analyze_processes(processes)
    
    if issues:
        print("\n⚠️  Issues found - review recommendations above")
    else:
        print("\n✅ No issues detected - all processes look good!")


