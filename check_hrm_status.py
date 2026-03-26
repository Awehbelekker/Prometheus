#!/usr/bin/env python3
"""Quick status check for HRM integration"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("HRM Integration Status Check")
print("="*60)

# Check checkpoint manager
try:
    from core.hrm_checkpoint_manager import HRMCheckpointManager
    manager = HRMCheckpointManager()
    checkpoints = manager.list_checkpoints()
    
    print("\nCheckpoints:")
    for cp in checkpoints:
        status = "[OK]" if cp['downloaded'] else "[MISSING]"
        print(f"  {status} {cp['name']}: {cp['description']}")
        if cp['downloaded'] and cp['path']:
            print(f"      Path: {cp['path']}")
    
    downloaded = sum(1 for cp in checkpoints if cp['downloaded'])
    print(f"\nTotal: {downloaded}/{len(checkpoints)} checkpoints downloaded")
    
except Exception as e:
    print(f"[ERROR] Failed to check checkpoints: {e}")

# Check components
print("\nComponents:")
components = {
    'Full HRM Architecture': 'core.hrm_full_architecture',
    'Trading Adapter': 'core.hrm_trading_adapter',
    'Trading Encoder': 'core.hrm_trading_encoder',
    'Trading Decoder': 'core.hrm_trading_decoder',
    'Checkpoint Manager': 'core.hrm_checkpoint_manager',
    'Integration': 'core.hrm_integration'
}

for name, module in components.items():
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")

# Check official HRM
print("\nOfficial HRM:")
official_hrm_path = Path(__file__).parent / "official_hrm"
if official_hrm_path.exists():
    print(f"  [OK] Repository found at: {official_hrm_path}")
    
    # Check for key files
    key_files = [
        "models/hrm/hrm_act_v1.py",
        "models/layers.py",
        "pretrain.py"
    ]
    for file in key_files:
        if (official_hrm_path / file).exists():
            print(f"    [OK] {file}")
        else:
            print(f"    [MISSING] {file}")
else:
    print("  [MISSING] Official HRM repository not found")

print("\n" + "="*60)
print("Status check complete!")
print("="*60)

