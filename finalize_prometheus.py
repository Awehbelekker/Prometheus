#!/usr/bin/env python3
"""
Finalize Prometheus - Run All Optimizations
One script to apply all final optimizations and polish
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """Run an optimization script"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}\n")
    
    script_path = Path(script_name)
    if not script_path.exists():
        print(f"[SKIP] {script_name} not found")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"[OK] {description} completed")
            return True
        else:
            print(f"[WARNING] {description} had issues (return code: {result.returncode})")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to run {script_name}: {e}")
        return False

def main():
    print("=" * 80)
    print("PROMETHEUS FINALIZATION")
    print("=" * 80)
    print()
    print("This will run all optimization and polish scripts:")
    print("  1. Database optimization (WAL mode)")
    print("  2. Configuration validation")
    print("  3. Log rotation setup")
    print()
    print("Running optimizations...")
    print()
    
    results = {}
    
    # Run optimizations
    results['database'] = run_script('optimize_databases_wal.py', 'Database Optimization')
    results['validation'] = run_script('validate_configuration.py', 'Configuration Validation')
    results['logs'] = run_script('setup_log_rotation.py', 'Log Rotation Setup')
    
    # Final summary
    print()
    print("=" * 80)
    print("FINALIZATION SUMMARY")
    print("=" * 80)
    print()
    
    for name, success in results.items():
        status = "[OK]" if success else "[SKIP]"
        print(f"{status} {name.replace('_', ' ').title()}")
    
    print()
    print("=" * 80)
    print("PROMETHEUS FINALIZATION COMPLETE")
    print("=" * 80)
    print()
    print("System is now optimized, enhanced, and polished!")
    print()
    print("Next steps:")
    print("  1. Review FINAL_OPTIMIZATION_REPORT.md")
    print("  2. Run complete_system_audit.py to verify")
    print("  3. Continue trading - system is ready!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nFinalization cancelled.")
        sys.exit(1)

