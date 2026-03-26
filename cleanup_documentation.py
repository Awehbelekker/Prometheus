#!/usr/bin/env python3
"""
PROMETHEUS Documentation Cleanup
=================================
Cleans up obsolete Markdown documentation files while preserving essential docs.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Essential documentation that MUST be preserved
ESSENTIAL_DOCS = {
    'README.md',
    'AI_ENHANCEMENTS_README.md',
    'AI_ML_COMPONENTS_VERIFICATION_REPORT.md',
    'COMPREHENSIVE_PRE_LAUNCH_VERIFICATION_AUDIT.md',
    'CODEBASE_CLEANUP_PLAN.md',
    'CODEBASE_CLEANUP_SUMMARY.md',
    'CHANGELOG.md',
    'LICENSE.md',
    'CONTRIBUTING.md',
}

# Keywords indicating obsolete documentation
OBSOLETE_DOC_KEYWORDS = [
    'STATUS_REPORT', 'status_report', 'Status_Report',
    'SESSION_REPORT', 'session_report', 'Session_Report',
    'AUDIT_REPORT', 'audit_report', 'Audit_Report',
    'TRADING_SESSION', 'trading_session', 'Trading_Session',
    'PERFORMANCE_REPORT', 'performance_report',
    'DAILY_REPORT', 'daily_report',
    'WEEKLY_REPORT', 'weekly_report',
    'ANALYSIS_REPORT', 'analysis_report',
]

# Directories to exclude from documentation cleanup
EXCLUDE_DIRS = {
    'node_modules',
    '.git',
    'cleanup_backup_20251018_003456',
    '__pycache__',
    '.vscode',
}

def find_all_markdown_files():
    """Find all Markdown files recursively"""
    print("\n" + "="*80)
    print("📋 SCANNING FOR MARKDOWN FILES")
    print("="*80)
    
    md_files = []
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                md_files.append(file_path)
    
    print(f"\n📊 Found {len(md_files)} Markdown files")
    return md_files

def categorize_markdown_files(md_files):
    """Categorize Markdown files"""
    print("\n" + "="*80)
    print("📂 CATEGORIZING MARKDOWN FILES")
    print("="*80)
    
    categories = {
        'essential': [],
        'obsolete_reports': [],
        'frontend_docs': [],
        'enterprise_package_docs': [],
        'unknown': []
    }
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        file_path_lower = md_file.lower()
        
        # Essential documentation
        if filename in ESSENTIAL_DOCS:
            categories['essential'].append(md_file)
        # Frontend documentation (preserve)
        elif 'prometheus-frontend' in file_path_lower or 'frontend' in file_path_lower:
            categories['frontend_docs'].append(md_file)
        # Enterprise package documentation (preserve)
        elif 'prometheus-enterprise-package' in file_path_lower:
            categories['enterprise_package_docs'].append(md_file)
        # Obsolete reports
        elif any(keyword in filename for keyword in OBSOLETE_DOC_KEYWORDS):
            categories['obsolete_reports'].append(md_file)
        else:
            categories['unknown'].append(md_file)
    
    print(f"\n[CHECK] Essential documentation: {len(categories['essential'])}")
    print(f"📋 Obsolete reports: {len(categories['obsolete_reports'])}")
    print(f"🎨 Frontend docs: {len(categories['frontend_docs'])}")
    print(f"📦 Enterprise package docs: {len(categories['enterprise_package_docs'])}")
    print(f"❓ Unknown category: {len(categories['unknown'])}")
    
    return categories

def delete_obsolete_reports(categories, backup_dir, dry_run=False):
    """Delete obsolete report files"""
    print("\n" + "="*80)
    print("🗑️  DELETING OBSOLETE REPORTS")
    print("="*80)
    
    deleted_count = 0
    
    for md_file in categories['obsolete_reports']:
        if os.path.basename(md_file) in ESSENTIAL_DOCS:
            print(f"[WARNING]️  PROTECTED: {md_file} (skipping)")
            continue
        
        file_path = Path(md_file)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {md_file}")
            else:
                try:
                    # Create backup
                    backup_path = Path(backup_dir) / md_file.lstrip('./')
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_path, backup_path)  # Use copy instead of copy2

                    # Delete
                    file_path.unlink()
                    print(f"[CHECK] Deleted: {md_file}")
                    deleted_count += 1
                except Exception as e:
                    print(f"[WARNING]️  Error deleting {md_file}: {e}")
                    continue
    
    print(f"\n📊 Deleted {deleted_count} obsolete report files")
    return deleted_count

def review_unknown_files(categories):
    """Review unknown files and categorize them"""
    print("\n" + "="*80)
    print("🔍 REVIEWING UNKNOWN FILES")
    print("="*80)
    
    to_delete = []
    to_preserve = []
    
    for md_file in categories['unknown']:
        filename = os.path.basename(md_file)
        filename_lower = filename.lower()
        
        # Check for date patterns (likely obsolete reports)
        if any(month in filename_lower for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            to_delete.append(md_file)
        # Check for version numbers (likely old versions)
        elif any(ver in filename_lower for ver in ['_v1', '_v2', '_v3', '_old', '_backup', '_copy']):
            to_delete.append(md_file)
        # Check for temporary markers
        elif any(temp in filename_lower for temp in ['temp', 'tmp', 'draft', 'wip']):
            to_delete.append(md_file)
        # Preserve everything else
        else:
            to_preserve.append(md_file)
    
    print(f"\n📊 Unknown files analysis:")
    print(f"   - To delete: {len(to_delete)}")
    print(f"   - To preserve: {len(to_preserve)}")
    
    return to_delete, to_preserve

def delete_reviewed_files(to_delete, backup_dir, dry_run=False):
    """Delete reviewed files"""
    print("\n" + "="*80)
    print("🗑️  DELETING REVIEWED FILES")
    print("="*80)
    
    deleted_count = 0
    
    for md_file in to_delete:
        if os.path.basename(md_file) in ESSENTIAL_DOCS:
            print(f"[WARNING]️  PROTECTED: {md_file} (skipping)")
            continue
        
        file_path = Path(md_file)
        if file_path.exists():
            if dry_run:
                print(f"[DRY RUN] Would delete: {md_file}")
            else:
                try:
                    # Create backup
                    backup_path = Path(backup_dir) / md_file.lstrip('./')
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file_path, backup_path)  # Use copy instead of copy2

                    # Delete
                    file_path.unlink()
                    print(f"[CHECK] Deleted: {md_file}")
                    deleted_count += 1
                except Exception as e:
                    print(f"[WARNING]️  Error deleting {md_file}: {e}")
                    continue
    
    print(f"\n📊 Deleted {deleted_count} reviewed files")
    return deleted_count

def generate_documentation_cleanup_report(categories, deleted_counts, backup_dir):
    """Generate documentation cleanup report"""
    print("\n" + "="*80)
    print("📊 DOCUMENTATION CLEANUP REPORT")
    print("="*80)
    
    total_deleted = sum(deleted_counts.values())
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'backup_location': backup_dir,
        'categories': {k: len(v) for k, v in categories.items()},
        'deleted_counts': deleted_counts,
        'total_deleted': total_deleted,
        'essential_docs_preserved': list(ESSENTIAL_DOCS)
    }
    
    report_file = f'documentation_cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[CHECK] Documentation cleanup report saved to: {report_file}")
    print(f"\n📊 Summary:")
    print(f"   - Obsolete reports deleted: {deleted_counts.get('reports', 0)}")
    print(f"   - Reviewed files deleted: {deleted_counts.get('reviewed', 0)}")
    print(f"\n   TOTAL DELETED: {total_deleted} Markdown files")
    print(f"\n📦 Backup location: {backup_dir}")
    
    return report_file

def main():
    """Execute documentation cleanup"""
    print("\n" + "="*80)
    print("📋 PROMETHEUS DOCUMENTATION CLEANUP")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find all Markdown files
    md_files = find_all_markdown_files()
    
    # Categorize files
    categories = categorize_markdown_files(md_files)
    
    # Review unknown files
    to_delete, to_preserve = review_unknown_files(categories)
    
    # Ask for confirmation
    print("\n[WARNING]️  WARNING: This will delete obsolete documentation files.")
    print("A backup will be created before deletion.")
    print("\nFiles to be deleted:")
    print(f"  - {len(categories['obsolete_reports'])} obsolete reports")
    print(f"  - {len(to_delete)} reviewed files (dates, versions, temp files)")
    
    total_to_delete = len(categories['obsolete_reports']) + len(to_delete)
    
    print(f"\nTOTAL: ~{total_to_delete} Markdown files")
    print(f"\nFiles to PRESERVE:")
    print(f"  - {len(categories['essential'])} essential docs")
    print(f"  - {len(categories['frontend_docs'])} frontend docs")
    print(f"  - {len(categories['enterprise_package_docs'])} enterprise package docs")
    print(f"  - {len(to_preserve)} other relevant docs")
    
    response = input("\nProceed with documentation cleanup? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n[ERROR] Documentation cleanup cancelled.")
        return
    
    # Use same backup directory as Python cleanup
    backup_dir = 'cleanup_backup_20251018_003456'
    
    # Execute cleanup
    deleted_counts = {}
    deleted_counts['reports'] = delete_obsolete_reports(categories, backup_dir)
    deleted_counts['reviewed'] = delete_reviewed_files(to_delete, backup_dir)
    
    # Generate report
    report_file = generate_documentation_cleanup_report(categories, deleted_counts, backup_dir)
    
    print("\n" + "="*80)
    print("[CHECK] DOCUMENTATION CLEANUP COMPLETE")
    print("="*80)
    print(f"\nTotal Markdown files deleted: {sum(deleted_counts.values())}")
    print(f"Backup location: {backup_dir}")
    print(f"Cleanup report: {report_file}")
    print("\nNext steps:")
    print("1. Review remaining documentation")
    print("2. Update Enterprise Package")
    print("3. Final system verification")

if __name__ == "__main__":
    main()

