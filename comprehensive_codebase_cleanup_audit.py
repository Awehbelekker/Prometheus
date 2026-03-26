#!/usr/bin/env python3
"""
PROMETHEUS Comprehensive Codebase Cleanup Audit
================================================
Systematically audits all files in the repository to identify:
- Obsolete server files
- Duplicate/redundant documentation
- Temporary/backup files
- Files to preserve vs delete
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Production files that MUST be preserved
PRODUCTION_FILES = {
    # Core production servers
    'unified_production_server.py',
    'revolutionary_master_engine.py',
    
    # Revolutionary engines
    'revolutionary_options_engine.py',
    'revolutionary_advanced_engine.py',
    'revolutionary_market_maker.py',
    'revolutionary_crypto_engine.py',
    
    # Core systems
    'core/',
    'brokers/',
    'revolutionary_features/',
    
    # Databases
    'prometheus_learning.db',
    'agent_performance.db',
    'knowledge_base.db',
    'historical_data/',
    
    # AI/ML models
    'pretrained_models/',
    'ai_models/',
    
    # Configuration
    '.env',
    '.env.example',
    'requirements.txt',
    'package.json',
    
    # Enterprise package
    'PROMETHEUS-Enterprise-Package-COMPLETE/',
    
    # Frontend
    'prometheus-frontend/',
    
    # Essential scripts
    'verify_ai_ml_components.py',
    'launch_ultimate_prometheus_LIVE_TRADING.py',
}

# Keywords indicating obsolete/test files
OBSOLETE_KEYWORDS = [
    'test_', 'TEST_', 'demo_', 'DEMO_', 'check_', 'CHECK_',
    'simple_', 'quick_', 'minimal_', 'fix_', 'FIX_',
    'debug_', 'diagnose_', 'temp_', 'old_', 'backup_',
    'working_', 'fixed_', 'corrected_', 'enhanced_server_',
    'optimized_', 'aggressive_', 'ultra_fast_',
    'mock_', 'simple_test_', 'quick_test_',
]

# Keywords indicating launch/startup scripts (many are redundant)
LAUNCH_KEYWORDS = [
    'launch_', 'LAUNCH_', 'start_', 'START_', 'activate_',
    'ACTIVATE_', 'deploy_', 'DEPLOY_', 'restart_',
]

def categorize_python_files():
    """Categorize all Python files in root directory"""
    print("\n" + "="*80)
    print("PYTHON FILES AUDIT (Root Directory)")
    print("="*80)
    
    py_files = list(Path('.').glob('*.py'))
    
    categories = {
        'production': [],
        'obsolete_test': [],
        'obsolete_demo': [],
        'obsolete_check': [],
        'obsolete_fix': [],
        'launch_scripts': [],
        'server_files': [],
        'utility_scripts': [],
        'unknown': []
    }
    
    for py_file in py_files:
        name = py_file.name
        
        # Skip if in production list
        if name in PRODUCTION_FILES:
            categories['production'].append(name)
            continue
        
        # Categorize by keywords
        name_lower = name.lower()
        
        if 'server' in name_lower and name != 'unified_production_server.py':
            categories['server_files'].append(name)
        elif any(kw in name_lower for kw in ['test_', 'TEST_']):
            categories['obsolete_test'].append(name)
        elif any(kw in name_lower for kw in ['demo_', 'DEMO_']):
            categories['obsolete_demo'].append(name)
        elif any(kw in name_lower for kw in ['check_', 'CHECK_', 'diagnose_', 'debug_']):
            categories['obsolete_check'].append(name)
        elif any(kw in name_lower for kw in ['fix_', 'FIX_', 'corrected_', 'fixed_']):
            categories['obsolete_fix'].append(name)
        elif any(kw in name_lower for kw in LAUNCH_KEYWORDS):
            categories['launch_scripts'].append(name)
        elif any(kw in name_lower for kw in ['analyze_', 'monitor_', 'get_', 'view_']):
            categories['utility_scripts'].append(name)
        else:
            categories['unknown'].append(name)
    
    # Print summary
    print(f"\n📊 Total Python files in root: {len(py_files)}")
    print(f"\n[CHECK] Production files: {len(categories['production'])}")
    print(f"[ERROR] Obsolete test files: {len(categories['obsolete_test'])}")
    print(f"[ERROR] Obsolete demo files: {len(categories['obsolete_demo'])}")
    print(f"[ERROR] Obsolete check/debug files: {len(categories['obsolete_check'])}")
    print(f"[ERROR] Obsolete fix files: {len(categories['obsolete_fix'])}")
    print(f"[WARNING]️  Launch scripts (many redundant): {len(categories['launch_scripts'])}")
    print(f"[WARNING]️  Server files (likely obsolete): {len(categories['server_files'])}")
    print(f"📝 Utility scripts: {len(categories['utility_scripts'])}")
    print(f"❓ Unknown category: {len(categories['unknown'])}")
    
    return categories

def categorize_markdown_files():
    """Categorize all Markdown documentation files"""
    print("\n" + "="*80)
    print("MARKDOWN DOCUMENTATION AUDIT")
    print("="*80)
    
    md_files = list(Path('.').rglob('*.md'))
    
    # Exclude node_modules and other irrelevant directories
    md_files = [f for f in md_files if 'node_modules' not in str(f) and '.git' not in str(f)]
    
    categories = {
        'essential': [],
        'status_reports': [],
        'audit_reports': [],
        'implementation_docs': [],
        'session_reports': [],
        'duplicate_guides': [],
        'obsolete': [],
        'unknown': []
    }
    
    essential_docs = ['README.md', 'AI_ENHANCEMENTS_README.md', 'CHANGELOG.md']
    
    for md_file in md_files:
        name = md_file.name
        name_lower = name.lower()
        
        if name in essential_docs:
            categories['essential'].append(str(md_file))
        elif 'status' in name_lower or 'report' in name_lower:
            if 'audit' in name_lower:
                categories['audit_reports'].append(str(md_file))
            elif 'session' in name_lower or 'trading' in name_lower:
                categories['session_reports'].append(str(md_file))
            else:
                categories['status_reports'].append(str(md_file))
        elif 'implementation' in name_lower or 'integration' in name_lower:
            categories['implementation_docs'].append(str(md_file))
        elif 'guide' in name_lower or 'tutorial' in name_lower:
            categories['duplicate_guides'].append(str(md_file))
        else:
            categories['unknown'].append(str(md_file))
    
    print(f"\n📊 Total Markdown files: {len(md_files)}")
    print(f"\n[CHECK] Essential documentation: {len(categories['essential'])}")
    print(f"📋 Status reports (likely obsolete): {len(categories['status_reports'])}")
    print(f"📋 Audit reports (likely obsolete): {len(categories['audit_reports'])}")
    print(f"📋 Session reports (likely obsolete): {len(categories['session_reports'])}")
    print(f"📚 Implementation docs: {len(categories['implementation_docs'])}")
    print(f"[WARNING]️  Duplicate guides: {len(categories['duplicate_guides'])}")
    print(f"❓ Unknown category: {len(categories['unknown'])}")
    
    return categories

def identify_server_files_for_deletion():
    """Identify which server files can be safely deleted"""
    print("\n" + "="*80)
    print("SERVER FILES ANALYSIS")
    print("="*80)
    
    server_files = list(Path('.').glob('*server*.py'))
    
    # The ONE production server
    production_server = 'unified_production_server.py'
    
    print(f"\n[CHECK] PRODUCTION SERVER (KEEP):")
    print(f"   - {production_server}")
    
    print(f"\n[ERROR] OBSOLETE SERVER FILES (DELETE):")
    obsolete_count = 0
    for server_file in server_files:
        if server_file.name != production_server:
            size_kb = server_file.stat().st_size / 1024
            print(f"   - {server_file.name} ({size_kb:.1f} KB)")
            obsolete_count += 1
    
    print(f"\n📊 Total obsolete server files: {obsolete_count}")
    
    return [f.name for f in server_files if f.name != production_server]

def identify_launch_scripts_for_consolidation():
    """Identify redundant launch scripts"""
    print("\n" + "="*80)
    print("LAUNCH SCRIPTS ANALYSIS")
    print("="*80)
    
    launch_files = []
    for keyword in LAUNCH_KEYWORDS:
        launch_files.extend(list(Path('.').glob(f'{keyword}*.py')))
    
    # Remove duplicates
    launch_files = list(set(launch_files))
    
    # The ONE production launcher
    production_launcher = 'launch_ultimate_prometheus_LIVE_TRADING.py'
    
    print(f"\n[CHECK] PRODUCTION LAUNCHER (KEEP):")
    print(f"   - {production_launcher}")
    
    print(f"\n[ERROR] REDUNDANT LAUNCH SCRIPTS (DELETE):")
    redundant_count = 0
    for launch_file in launch_files:
        if launch_file.name != production_launcher:
            size_kb = launch_file.stat().st_size / 1024
            print(f"   - {launch_file.name} ({size_kb:.1f} KB)")
            redundant_count += 1
    
    print(f"\n📊 Total redundant launch scripts: {redundant_count}")
    
    return [f.name for f in launch_files if f.name != production_launcher]

def generate_cleanup_recommendations():
    """Generate comprehensive cleanup recommendations"""
    print("\n" + "="*80)
    print("CLEANUP RECOMMENDATIONS")
    print("="*80)
    
    recommendations = {
        'delete_immediately': [],
        'review_before_delete': [],
        'consolidate': [],
        'preserve': []
    }
    
    # Get all Python files
    py_files = list(Path('.').glob('*.py'))
    
    for py_file in py_files:
        name = py_file.name
        name_lower = name.lower()
        
        # Preserve production files
        if name in PRODUCTION_FILES or name == 'unified_production_server.py' or name == 'revolutionary_master_engine.py':
            recommendations['preserve'].append(name)
        # Delete test/demo/check files immediately
        elif any(kw in name_lower for kw in ['test_', 'demo_', 'check_', 'quick_', 'simple_test_']):
            recommendations['delete_immediately'].append(name)
        # Review fix/debug files
        elif any(kw in name_lower for kw in ['fix_', 'debug_', 'diagnose_']):
            recommendations['review_before_delete'].append(name)
        # Consolidate launch scripts
        elif any(kw in name_lower for kw in LAUNCH_KEYWORDS) and name != 'launch_ultimate_prometheus_LIVE_TRADING.py':
            recommendations['consolidate'].append(name)
        # Review server files
        elif 'server' in name_lower and name != 'unified_production_server.py':
            recommendations['review_before_delete'].append(name)
        else:
            recommendations['review_before_delete'].append(name)
    
    print(f"\n[CHECK] Files to PRESERVE: {len(recommendations['preserve'])}")
    print(f"[ERROR] Files to DELETE immediately: {len(recommendations['delete_immediately'])}")
    print(f"[WARNING]️  Files to REVIEW before delete: {len(recommendations['review_before_delete'])}")
    print(f"🔗 Files to CONSOLIDATE: {len(recommendations['consolidate'])}")
    
    return recommendations

def main():
    """Run comprehensive cleanup audit"""
    print("\n" + "="*80)
    print("🧹 PROMETHEUS COMPREHENSIVE CODEBASE CLEANUP AUDIT")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all audits
    py_categories = categorize_python_files()
    md_categories = categorize_markdown_files()
    obsolete_servers = identify_server_files_for_deletion()
    redundant_launchers = identify_launch_scripts_for_consolidation()
    recommendations = generate_cleanup_recommendations()
    
    # Save results to JSON
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'python_files': {k: v for k, v in py_categories.items()},
        'markdown_files': {k: v for k, v in md_categories.items()},
        'obsolete_servers': obsolete_servers,
        'redundant_launchers': redundant_launchers,
        'recommendations': recommendations
    }
    
    output_file = 'codebase_cleanup_audit_results.json'
    with open(output_file, 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f"\n[CHECK] Audit results saved to: {output_file}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 CLEANUP SUMMARY")
    print("="*80)
    
    total_py_files = sum(len(v) for v in py_categories.values())
    total_md_files = sum(len(v) for v in md_categories.values())
    total_deletable = len(recommendations['delete_immediately']) + len(obsolete_servers) + len(redundant_launchers)
    
    print(f"\n📁 Total Python files: {total_py_files}")
    print(f"📁 Total Markdown files: {total_md_files}")
    print(f"[ERROR] Estimated deletable files: {total_deletable}")
    print(f"[CHECK] Files to preserve: {len(recommendations['preserve'])}")
    
    print("\n" + "="*80)
    print("[CHECK] AUDIT COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review audit results in codebase_cleanup_audit_results.json")
    print("2. Confirm deletion list")
    print("3. Execute cleanup")
    print("4. Update documentation")
    print("5. Verify system integrity")

if __name__ == "__main__":
    main()

