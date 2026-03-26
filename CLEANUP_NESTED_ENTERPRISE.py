#!/usr/bin/env python3
"""
Clean up nested PROMETHEUS-Enterprise-Package directory
Since the main Enterprise Package has been moved out, this nested one should be archived
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_nested_enterprise():
    """Archive the nested Enterprise Package directory"""
    base_dir = Path(__file__).parent
    nested_ent = base_dir / "PROMETHEUS-Enterprise-Package"
    
    if not nested_ent.exists():
        print(f"[INFO] Nested Enterprise Package not found: {nested_ent}")
        return
    
    # Archive directory
    archive_dir = base_dir / "ARCHIVE_NESTED_ENTERPRISE" / datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("CLEANING UP NESTED ENTERPRISE PACKAGE")
    print("=" * 80)
    print()
    print(f"Source: {nested_ent.relative_to(base_dir)}")
    print(f"Archive: {archive_dir.relative_to(base_dir)}")
    print()
    
    # Count files
    file_count = sum(len(files) for _, _, files in os.walk(nested_ent))
    print(f"Files to archive: {file_count}")
    print()
    
    # Check if it's referenced anywhere
    print("Checking for references...")
    references = []
    for root, dirs, files in os.walk(base_dir):
        # Skip archive and the nested enterprise itself - modify dirs in-place to prevent recursion
        if 'ARCHIVE' in root or 'PROMETHEUS-Enterprise-Package' in root:
            dirs[:] = []  # Clear dirs list to prevent descending
            continue
        # Remove archive and nested enterprise directories from dirs list to prevent descending into them
        dirs[:] = [d for d in dirs if 'ARCHIVE' not in d and 'PROMETHEUS-Enterprise-Package' not in d]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'PROMETHEUS-Enterprise-Package' in content:
                            references.append(filepath.relative_to(base_dir))
                except:
                    pass
    
    if references:
        print(f"[WARNING] Found {len(references)} files referencing nested Enterprise Package:")
        for ref in references[:10]:
            print(f"  - {ref}")
        if len(references) > 10:
            print(f"  ... and {len(references) - 10} more")
        print()
        print("[WARNING] These files may need to be updated after archiving")
    else:
        print("[OK] No references found - safe to archive")
    
    print()
    
    # Archive it
    try:
        archive_path = archive_dir / "PROMETHEUS-Enterprise-Package"
        shutil.copytree(nested_ent, archive_path)
        print(f"[OK] Copied to archive: {archive_path.relative_to(base_dir)}")
        
        # Remove original
        shutil.rmtree(nested_ent)
        print(f"[OK] Removed original: {nested_ent.relative_to(base_dir)}")
        
        print()
        print("=" * 80)
        print("CLEANUP COMPLETE")
        print("=" * 80)
        print()
        print(f"Archived to: {archive_dir.relative_to(base_dir)}")
        print()
        print("Note: If any files referenced the nested Enterprise Package,")
        print("      they may need to be updated to use the main system.")
        
    except Exception as e:
        print(f"[ERROR] Failed to archive: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_nested_enterprise()

