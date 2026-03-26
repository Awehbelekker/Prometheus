#!/usr/bin/env python3
"""
Clean up duplicate launch files
Archive old launchers and keep only the primary one
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_launch_files():
    """Archive duplicate launch files, keep primary"""
    base_dir = Path(__file__).parent
    
    # Primary launcher to keep
    primary_launcher = base_dir / "launch_ultimate_prometheus_LIVE_TRADING.py"
    unified_launcher = base_dir / "LAUNCH_PROMETHEUS.py"
    
    # Archive directory
    archive_dir = base_dir / "ARCHIVE_LAUNCHERS" / datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Launch files to keep (active)
    keep_files = {
        "launch_ultimate_prometheus_LIVE_TRADING.py",  # Primary
        "LAUNCH_PROMETHEUS.py",  # Unified entry point
    }
    
    # Find all launch files
    launch_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip archive directories - modify dirs in-place to prevent recursion
        if 'ARCHIVE' in root or '__pycache__' in root or '.git' in root:
            dirs[:] = []  # Clear dirs list to prevent descending
            continue
        # Remove archive directories from dirs list to prevent descending into them
        dirs[:] = [d for d in dirs if 'ARCHIVE' not in d and '__pycache__' not in d and '.git' not in d]
        
        for file in files:
            if file.startswith('launch_') and file.endswith('.py'):
                filepath = Path(root) / file
                rel_path = filepath.relative_to(base_dir)
                
                # Skip if already in ARCHIVE
                if 'ARCHIVE' in str(rel_path):
                    continue
                
                launch_files.append((filepath, rel_path))
    
    print(f"Found {len(launch_files)} launch files")
    print(f"Primary launcher: {primary_launcher.name}")
    print(f"Unified launcher: {unified_launcher.name}")
    print()
    
    archived = 0
    kept = 0
    
    for filepath, rel_path in launch_files:
        filename = filepath.name
        
        if filename in keep_files:
            print(f"[KEEP] {rel_path}")
            kept += 1
        else:
            # Archive it
            archive_path = archive_dir / filename
            if filepath.exists():
                shutil.copy2(filepath, archive_path)
                print(f"[ARCHIVE] {rel_path} -> {archive_path.relative_to(base_dir)}")
                archived += 1
    
    print()
    print(f"Kept: {kept} files")
    print(f"Archived: {archived} files")
    print(f"Archive location: {archive_dir.relative_to(base_dir)}")
    
    return archived, kept

if __name__ == "__main__":
    print("=" * 80)
    print("CLEANING UP LAUNCH FILES")
    print("=" * 80)
    print()
    
    archived, kept = cleanup_launch_files()
    
    print()
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print("To launch Prometheus, use:")
    print("  python LAUNCH_PROMETHEUS.py")
    print("  or")
    print("  python launch_ultimate_prometheus_LIVE_TRADING.py")


