#!/usr/bin/env python3
"""
Integrate Full HRM into Live Trading System
This script integrates the full HRM architecture into the live trading pipeline
"""

import sys
import os
from pathlib import Path
import logging

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n" + "="*60)
    print("Checking Dependencies")
    print("="*60)
    
    dependencies = {
        'torch': False,
        'official_hrm': False,
        'flash_attn': False,
        'huggingface_hub': False
    }
    
    # Check PyTorch
    try:
        import torch
        dependencies['torch'] = True
        print(f"[OK] PyTorch {torch.__version__}")
    except ImportError:
        print("[FAIL] PyTorch not installed")
    
    # Check official HRM
    official_hrm_path = Path(__file__).parent / "official_hrm"
    if official_hrm_path.exists():
        dependencies['official_hrm'] = True
        print("[OK] Official HRM repository found")
    else:
        print("[FAIL] Official HRM repository not found")
    
    # Check FlashAttention (optional)
    try:
        import flash_attn
        dependencies['flash_attn'] = True
        print("[OK] FlashAttention available (recommended for GPU)")
    except ImportError:
        print("[WARN] FlashAttention not available (will use slower attention on CPU)")
    
    # Check HuggingFace Hub
    try:
        import huggingface_hub
        dependencies['huggingface_hub'] = True
        print("[OK] HuggingFace Hub available")
    except ImportError:
        print("[WARN] HuggingFace Hub not available (checkpoint download may fail)")
    
    return dependencies


def check_components():
    """Check if all HRM components are available"""
    print("\n" + "="*60)
    print("Checking HRM Components")
    print("="*60)
    
    components = {}
    
    # Check full HRM architecture
    try:
        from core.hrm_full_architecture import FullHRMArchitecture
        components['full_architecture'] = True
        print("[OK] Full HRM Architecture module")
    except ImportError as e:
        components['full_architecture'] = False
        print(f"[FAIL] Full HRM Architecture: {e}")
    
    # Check trading adapter
    try:
        from core.hrm_trading_adapter import HRMTradingAdapter
        components['trading_adapter'] = True
        print("[OK] Trading Adapter module")
    except ImportError as e:
        components['trading_adapter'] = False
        print(f"[FAIL] Trading Adapter: {e}")
    
    # Check encoder/decoder
    try:
        from core.hrm_trading_encoder import HRMTradingEncoder
        from core.hrm_trading_decoder import HRMTradingDecoder
        components['encoder_decoder'] = True
        print("[OK] Encoder/Decoder modules")
    except ImportError as e:
        components['encoder_decoder'] = False
        print(f"[FAIL] Encoder/Decoder: {e}")
    
    # Check checkpoint manager
    try:
        from core.hrm_checkpoint_manager import HRMCheckpointManager
        components['checkpoint_manager'] = True
        print("[OK] Checkpoint Manager module")
    except ImportError as e:
        components['checkpoint_manager'] = False
        print(f"[FAIL] Checkpoint Manager: {e}")
    
    # Check integration
    try:
        from core.hrm_integration import FullHRMTradingEngine
        components['integration'] = True
        print("[OK] Trading Engine Integration")
    except ImportError as e:
        components['integration'] = False
        print(f"[FAIL] Trading Engine Integration: {e}")
    
    return components


def check_checkpoints():
    """Check downloaded checkpoints"""
    print("\n" + "="*60)
    print("Checking Checkpoints")
    print("="*60)
    
    try:
        from core.hrm_checkpoint_manager import HRMCheckpointManager
        
        manager = HRMCheckpointManager()
        checkpoints = manager.list_checkpoints()
        
        downloaded_count = sum(1 for cp in checkpoints if cp['downloaded'])
        total_count = len(checkpoints)
        
        print(f"Checkpoints: {downloaded_count}/{total_count} downloaded")
        
        for cp in checkpoints:
            status = "[OK]" if cp['downloaded'] else "[MISSING]"
            print(f"{status} {cp['name']}: {cp['description']}")
            if cp['downloaded'] and cp['path']:
                print(f"      Path: {cp['path']}")
        
        return downloaded_count, total_count
        
    except Exception as e:
        print(f"[ERROR] Failed to check checkpoints: {e}")
        return 0, 0


def create_integration_config():
    """Create configuration for HRM integration"""
    print("\n" + "="*60)
    print("Creating Integration Configuration")
    print("="*60)
    
    config_content = """# HRM Integration Configuration
# This file configures the Full HRM integration for live trading

# Use Full HRM Architecture (True) or Legacy LSTM (False)
USE_FULL_HRM = True

# Device to run HRM on ('cpu' or 'cuda')
HRM_DEVICE = 'cpu'

# Checkpoint to use
# Options: 'arc_agi_2', 'sudoku_extreme', 'maze_30x30', or None for no checkpoint
ACTIVE_CHECKPOINT = 'arc_agi_2'

# HRM Configuration
HRM_CONFIG = {
    'H_cycles': 2,
    'L_cycles': 2,
    'H_layers': 4,
    'L_layers': 4,
    'hidden_size': 512,
    'num_heads': 8,
    'seq_len': 256,
    'halt_max_steps': 8
}

# Trading Configuration
TRADING_CONFIG = {
    'max_position_size': 0.1,
    'stop_loss_percent': 0.02,
    'take_profit_percent': 0.04
}
"""
    
    config_path = Path(__file__).parent / "hrm_integration_config.py"
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"[OK] Configuration file created: {config_path}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create config: {e}")
        return False


def update_trading_launcher():
    """Update trading launcher to use full HRM"""
    print("\n" + "="*60)
    print("Updating Trading Launcher")
    print("="*60)
    
    launcher_files = [
        "launch_ultimate_prometheus_LIVE_TRADING.py",
        "launch_ultimate_prometheus_with_enhanced_hrm.py"
    ]
    
    updated = []
    
    for launcher_file in launcher_files:
        launcher_path = Path(__file__).parent / launcher_file
        if not launcher_path.exists():
            continue
        
        try:
            content = launcher_path.read_text(encoding='utf-8')
            
            # Check if already has full HRM integration
            if 'FullHRMTradingEngine' in content:
                print(f"[SKIP] {launcher_file} already has Full HRM integration")
                continue
            
            # Add import if not present
            if 'from core.hrm_integration import' in content:
                # Update existing import
                content = content.replace(
                    'from core.hrm_integration import HRMTradingEngine',
                    'from core.hrm_integration import HRMTradingEngine, FullHRMTradingEngine'
                )
            else:
                # Add new import
                import_line = "from core.hrm_integration import FullHRMTradingEngine\n"
                # Find a good place to insert
                if 'import' in content:
                    lines = content.split('\n')
                    last_import = max(i for i, line in enumerate(lines) if 'import' in line)
                    lines.insert(last_import + 1, import_line)
                    content = '\n'.join(lines)
                else:
                    content = import_line + content
            
            launcher_path.write_text(content, encoding='utf-8')
            print(f"[OK] Updated {launcher_file}")
            updated.append(launcher_file)
            
        except Exception as e:
            print(f"[FAIL] Failed to update {launcher_file}: {e}")
    
    return updated


def main():
    """Main integration function"""
    print("\n" + "="*80)
    print("FULL HRM INTEGRATION INTO LIVE TRADING SYSTEM")
    print("="*80)
    
    # Check dependencies
    dependencies = check_dependencies()
    
    # Check components
    components = check_components()
    
    # Check checkpoints
    downloaded, total = check_checkpoints()
    
    # Create config
    config_created = create_integration_config()
    
    # Update launchers
    updated_launchers = update_trading_launcher()
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION SUMMARY")
    print("="*80)
    
    critical_ok = (
        dependencies.get('torch', False) and
        dependencies.get('official_hrm', False) and
        all(components.values())
    )
    
    if critical_ok:
        print("\n[SUCCESS] Full HRM is ready for integration!")
        print("\nNext steps:")
        print("1. Download checkpoints if needed: python download_hrm_checkpoints.py")
        print("2. Configure HRM settings in: hrm_integration_config.py")
        print("3. Update your trading scripts to use FullHRMTradingEngine")
        print("4. Test with: python test_full_hrm_trading.py")
        print("5. Monitor performance improvements")
    else:
        print("\n[WARNING] Some components are missing:")
        if not dependencies.get('torch'):
            print("  - Install PyTorch: pip install torch")
        if not dependencies.get('official_hrm'):
            print("  - Ensure official_hrm/ directory exists")
        if not all(components.values()):
            print("  - Some HRM components failed to import")
    
    if downloaded < total:
        print(f"\n[INFO] {total - downloaded} checkpoint(s) not downloaded")
        print("  Run: python download_hrm_checkpoints.py")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

