#!/usr/bin/env python3
"""
Download HRM Checkpoints from HuggingFace
Downloads all three official HRM checkpoints for trading
"""

import os
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.hrm_checkpoint_manager import HRMCheckpointManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_all_checkpoints():
    """Download all HRM checkpoints"""
    print("=" * 80)
    print("DOWNLOADING HRM CHECKPOINTS")
    print("=" * 80)
    print()
    
    manager = HRMCheckpointManager(checkpoint_dir="hrm_checkpoints")
    
    checkpoints = ['arc_agi_2', 'sudoku_extreme', 'maze_30x30']
    
    print(f"Downloading {len(checkpoints)} checkpoints...")
    print()
    
    downloaded = []
    failed = []
    
    for checkpoint_name in checkpoints:
        print(f"Downloading {checkpoint_name}...")
        try:
            path = manager.download_checkpoint(checkpoint_name, force_download=False)
            if path:
                print(f"  [OK] Success: {path}")
                downloaded.append(checkpoint_name)
            else:
                print(f"  [INFO] Already exists or download failed")
                # Check if exists
                existing = manager.get_checkpoint_path(checkpoint_name)
                if existing and os.path.exists(existing):
                    print(f"  [OK] Found existing: {existing}")
                    downloaded.append(checkpoint_name)
                else:
                    failed.append(checkpoint_name)
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            failed.append(checkpoint_name)
        print()
    
    print("=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Downloaded: {len(downloaded)}/{len(checkpoints)}")
    print(f"Failed: {len(failed)}/{len(checkpoints)}")
    print()
    
    if downloaded:
        print("[OK] Successfully downloaded/verified:")
        for name in downloaded:
            print(f"  - {name}")
        print()
    
    if failed:
        print("[ERROR] Failed to download:")
        for name in failed:
            print(f"  - {name}")
        print()
        print("Note: Checkpoints may download automatically on first use")
    
    return len(downloaded) == len(checkpoints)

if __name__ == "__main__":
    success = download_all_checkpoints()
    sys.exit(0 if success else 1)
