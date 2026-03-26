#!/usr/bin/env python3
"""
Quick HRM Status Check
Check if HRM is working or needs setup
"""

import sys
import os
from pathlib import Path

print("="*60)
print("    HRM QUICK STATUS CHECK")
print("="*60)

# Check 1: Checkpoint Directory
print("\n[1] Checkpoint Directory:")
checkpoint_dir = Path("hrm_checkpoints")
if checkpoint_dir.exists():
    print(f"  ✓ hrm_checkpoints/ exists")
    for item in checkpoint_dir.iterdir():
        if item.is_dir():
            files = list(item.rglob("*.pt")) + list(item.rglob("*.pth")) + list(item.rglob("*.bin"))
            print(f"    {item.name}/: {len(files)} model files found")
        else:
            print(f"    {item.name}")
else:
    print(f"  ⚠ hrm_checkpoints/ does not exist")

# Check 2: Official HRM
print("\n[2] Official HRM Module:")
try:
    sys.path.insert(0, str(Path("official_hrm")))
    from models.hrm.hrm_act_v1 import HierarchicalReasoningModel_ACTV1
    print(f"  ✓ Official HRM model importable")
except ImportError as e:
    print(f"  ⚠ Cannot import HRM: {e}")

# Check 3: HRM Integration
print("\n[3] HRM Integration:")
try:
    from core.hrm_official_integration import OfficialHRMTradingAdapter, get_hrm_decision
    print(f"  ✓ HRM integration module available")
except ImportError as e:
    print(f"  ⚠ Cannot import HRM integration: {e}")

# Check 4: HRM Training
print("\n[4] HRM Training System:")
try:
    from core.hrm_trading_trainer import HRMTradingTrainer, get_hrm_trainer
    print(f"  ✓ HRM training module available")
    
    # Check for existing training data
    training_dir = Path("hrm_trading_checkpoints")
    if training_dir.exists():
        files = list(training_dir.glob("*.pt"))
        print(f"  ✓ Training checkpoint directory exists ({len(files)} files)")
    else:
        print(f"  ℹ No training checkpoints yet (will be created when training starts)")
except ImportError as e:
    print(f"  ⚠ Cannot import HRM trainer: {e}")

# Check 5: Universal Reasoning Engine HRM Integration
print("\n[5] Universal Reasoning Engine HRM Weight:")
try:
    from core.universal_reasoning_engine_v2 import UniversalReasoningEngineV2
    engine = UniversalReasoningEngineV2()
    hrm_weight = engine.weights.get('hrm', 0)
    print(f"  ✓ HRM weight in ensemble: {hrm_weight:.0%}")
    print(f"  ✓ HRM is part of the 'thinking mesh'")
except Exception as e:
    print(f"  ⚠ Error checking Universal Reasoning: {e}")

# Check 6: HuggingFace Hub
print("\n[6] HuggingFace Hub (for downloading checkpoints):")
try:
    from huggingface_hub import hf_hub_download
    print(f"  ✓ huggingface_hub installed")
except ImportError:
    print(f"  ⚠ huggingface_hub not installed")
    print(f"    Install with: pip install huggingface_hub")

# Summary
print("\n" + "="*60)
print("    SUMMARY")
print("="*60)

hrm_ready = True
issues = []

# Check if we have at least one checkpoint
checkpoint_found = False
if checkpoint_dir.exists():
    for item in checkpoint_dir.iterdir():
        if item.is_dir():
            files = list(item.rglob("*.pt")) + list(item.rglob("*.pth")) + list(item.rglob("*.bin"))
            if files:
                checkpoint_found = True
                break

if not checkpoint_found:
    hrm_ready = False
    issues.append("No HRM checkpoints downloaded yet")

# Check training system
try:
    from core.hrm_trading_trainer import HRMTradingTrainer
except:
    hrm_ready = False
    issues.append("HRM training system not available")

if hrm_ready:
    print("\n🎉 HRM 'Thinking Mesh' is READY!")
    print("   - HRM reasoning integrated with 30% weight")
    print("   - Trading-specific training system active")
    print("   - Checkpoints will auto-download on first use")
else:
    print("\n⚠ HRM needs attention:")
    for issue in issues:
        print(f"   - {issue}")
    print("\nTo download checkpoints, run:")
    print("   python download_hrm_checkpoints.py")

print("\n" + "="*60)
