#!/usr/bin/env python3
"""
PROMETHEUS Codebase Cleanup Execution
======================================
Safely deletes obsolete files while preserving production components.
Creates backup before deletion for safety.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Load audit results
with open('codebase_cleanup_audit_results.json', 'r') as f:
    audit_results = json.load(f)

# CRITICAL: Files that MUST NEVER be deleted
PROTECTED_FILES = {
    # Core production
    'unified_production_server.py',
    'revolutionary_master_engine.py',
    'revolutionary_options_engine.py',
    'revolutionary_advanced_engine.py',
    'revolutionary_market_maker.py',
    'revolutionary_crypto_engine.py',
    'launch_ultimate_prometheus_LIVE_TRADING.py',
    
    # AI/ML verification
    'verify_ai_ml_components.py',
    'comprehensive_codebase_cleanup_audit.py',
    'execute_codebase_cleanup.py',
    
    # Configuration
    '.env',
    '.env.example',
    'requirements.txt',
    'package.json',
    'package-lock.json',
    
    # Essential docs
    'README.md',
    'AI_ENHANCEMENTS_README.md',
    'AI_ML_COMPONENTS_VERIFICATION_REPORT.md',
    'COMPREHENSIVE_PRE_LAUNCH_VERIFICATION_AUDIT.md',
}

# Directories that MUST NEVER be deleted
PROTECTED_DIRS = {
    'core',
    'brokers',
    'revolutionary_features',
    'prometheus-frontend',
    'PROMETHEUS-Enterprise-Package-COMPLETE',
    'pretrained_models',
    'ai_models',
    'historical_data',
    'node_modules',
    '.git',
}

def create_backup():
    """Create backup of files before deletion"""
    print("\n" + "="*80)
    print("📦 CREATING BACKUP")
    print("="*80)
    
    backup_dir = f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nBackup directory: {backup_dir}")
    print("This allows you to restore files if needed.")
    
    # We'll just note the backup location, actual backup happens during deletion
    return backup_dir

def delete_obsolete_test_files(backup_dir, dry_run=False):
    """Delete obsolete test files"""
    print("\n" + "="*80)
    print("🗑️  PHASE 1: DELETING OBSOLETE TEST FILES")
    print("="*80)
    
    test_files = audit_results['python_files']['obsolete_test']
    deleted_count = 0
    
    for filename in test_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                # Create backup
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                # Delete
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} test files")
    return deleted_count

def delete_obsolete_demo_files(backup_dir, dry_run=False):
    """Delete obsolete demo files"""
    print("\n" + "="*80)
    print("🗑️  PHASE 2: DELETING OBSOLETE DEMO FILES")
    print("="*80)
    
    demo_files = audit_results['python_files']['obsolete_demo']
    deleted_count = 0
    
    for filename in demo_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} demo files")
    return deleted_count

def delete_obsolete_check_files(backup_dir, dry_run=False):
    """Delete obsolete check/debug files"""
    print("\n" + "="*80)
    print("🗑️  PHASE 3: DELETING OBSOLETE CHECK/DEBUG FILES")
    print("="*80)
    
    check_files = audit_results['python_files']['obsolete_check']
    deleted_count = 0
    
    for filename in check_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} check/debug files")
    return deleted_count

def delete_obsolete_fix_files(backup_dir, dry_run=False):
    """Delete obsolete fix files"""
    print("\n" + "="*80)
    print("🗑️  PHASE 4: DELETING OBSOLETE FIX FILES")
    print("="*80)
    
    fix_files = audit_results['python_files']['obsolete_fix']
    deleted_count = 0
    
    for filename in fix_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} fix files")
    return deleted_count

def delete_obsolete_server_files(backup_dir, dry_run=False):
    """Delete obsolete server files"""
    print("\n" + "="*80)
    print("🗑️  PHASE 5: DELETING OBSOLETE SERVER FILES")
    print("="*80)
    
    server_files = audit_results['obsolete_servers']
    deleted_count = 0
    
    for filename in server_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} obsolete server files")
    return deleted_count

def delete_redundant_launch_scripts(backup_dir, dry_run=False):
    """Delete redundant launch scripts"""
    print("\n" + "="*80)
    print("🗑️  PHASE 6: DELETING REDUNDANT LAUNCH SCRIPTS")
    print("="*80)
    
    launch_files = audit_results['redundant_launchers']
    deleted_count = 0
    
    for filename in launch_files:
        if filename in PROTECTED_FILES:
            print(f"[WARNING]️  PROTECTED: {filename} (skipping)")
            continue
        
        file_path = Path(filename)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename}")
            else:
                backup_path = Path(backup_dir) / filename
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                file_path.unlink()
                print(f"[CHECK] Deleted: {filename}")
                deleted_count += 1
    
    print(f"\n📊 Deleted {deleted_count} redundant launch scripts")
    return deleted_count

def generate_cleanup_report(deleted_counts, backup_dir):
    """Generate comprehensive cleanup report"""
    print("\n" + "="*80)
    print("📊 CLEANUP REPORT")
    print("="*80)
    
    total_deleted = sum(deleted_counts.values())
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'backup_location': backup_dir,
        'deleted_counts': deleted_counts,
        'total_deleted': total_deleted,
        'protected_files': list(PROTECTED_FILES),
        'protected_dirs': list(PROTECTED_DIRS)
    }
    
    report_file = f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[CHECK] Cleanup report saved to: {report_file}")
    print(f"\n📊 Summary:")
    print(f"   - Test files deleted: {deleted_counts.get('test', 0)}")
    print(f"   - Demo files deleted: {deleted_counts.get('demo', 0)}")
    print(f"   - Check/debug files deleted: {deleted_counts.get('check', 0)}")
    print(f"   - Fix files deleted: {deleted_counts.get('fix', 0)}")
    print(f"   - Server files deleted: {deleted_counts.get('server', 0)}")
    print(f"   - Launch scripts deleted: {deleted_counts.get('launch', 0)}")
    print(f"\n   TOTAL DELETED: {total_deleted} files")
    print(f"\n📦 Backup location: {backup_dir}")
    
    return report_file

def main():
    """Execute cleanup"""
    print("\n" + "="*80)
    print("🧹 PROMETHEUS CODEBASE CLEANUP EXECUTION")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ask for confirmation
    print("\n[WARNING]️  WARNING: This will delete obsolete files from your codebase.")
    print("A backup will be created before deletion.")
    print("\nFiles to be deleted:")
    print(f"  - {len(audit_results['python_files']['obsolete_test'])} test files")
    print(f"  - {len(audit_results['python_files']['obsolete_demo'])} demo files")
    print(f"  - {len(audit_results['python_files']['obsolete_check'])} check/debug files")
    print(f"  - {len(audit_results['python_files']['obsolete_fix'])} fix files")
    print(f"  - {len(audit_results['obsolete_servers'])} obsolete server files")
    print(f"  - {len(audit_results['redundant_launchers'])} redundant launch scripts")
    
    total_to_delete = (
        len(audit_results['python_files']['obsolete_test']) +
        len(audit_results['python_files']['obsolete_demo']) +
        len(audit_results['python_files']['obsolete_check']) +
        len(audit_results['python_files']['obsolete_fix']) +
        len(audit_results['obsolete_servers']) +
        len(audit_results['redundant_launchers'])
    )
    
    print(f"\nTOTAL: ~{total_to_delete} files")
    
    response = input("\nProceed with cleanup? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n[ERROR] Cleanup cancelled.")
        return
    
    # Create backup directory
    backup_dir = create_backup()
    os.makedirs(backup_dir, exist_ok=True)
    
    # Execute cleanup phases
    deleted_counts = {}
    deleted_counts['test'] = delete_obsolete_test_files(backup_dir)
    deleted_counts['demo'] = delete_obsolete_demo_files(backup_dir)
    deleted_counts['check'] = delete_obsolete_check_files(backup_dir)
    deleted_counts['fix'] = delete_obsolete_fix_files(backup_dir)
    deleted_counts['server'] = delete_obsolete_server_files(backup_dir)
    deleted_counts['launch'] = delete_redundant_launch_scripts(backup_dir)
    
    # Generate report
    report_file = generate_cleanup_report(deleted_counts, backup_dir)
    
    print("\n" + "="*80)
    print("[CHECK] CLEANUP COMPLETE")
    print("="*80)
    print(f"\nTotal files deleted: {sum(deleted_counts.values())}")
    print(f"Backup location: {backup_dir}")
    print(f"Cleanup report: {report_file}")
    print("\nNext steps:")
    print("1. Verify system integrity")
    print("2. Test production server startup")
    print("3. Clean up obsolete documentation")
    print("4. Update Enterprise Package")

if __name__ == "__main__":
    main()

