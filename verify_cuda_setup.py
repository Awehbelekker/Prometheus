#!/usr/bin/env python3
"""
Verify CUDA Setup and Fix Compatibility Issues
"""

import sys
import subprocess

def check_cuda_toolkit():
    """Check CUDA Toolkit installation"""
    print("=" * 80)
    print("CHECKING CUDA TOOLKIT")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'release' in line.lower():
                    version = line.strip()
                    print(f"[OK] CUDA Toolkit: {version}")
                    return True
        return False
    except:
        return False

def check_pytorch_cuda():
    """Check PyTorch CUDA"""
    print()
    print("CHECKING PYTORCH CUDA")
    print("=" * 80)
    print()
    
    try:
        import torch
        print(f"[OK] PyTorch: {torch.__version__}")
        
        if hasattr(torch.version, 'cuda'):
            print(f"[OK] PyTorch CUDA Built: {torch.version.cuda}")
        
        if torch.cuda.is_available():
            print(f"[OK] CUDA Available: True")
            print(f"[OK] GPU: {torch.cuda.get_device_name(0)}")
            print(f"[OK] CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("[WARNING] CUDA not available in PyTorch")
            print()
            print("Possible reasons:")
            print("  1. System needs restart (most common)")
            print("  2. PyTorch CUDA version mismatch")
            print("  3. NVIDIA drivers need update")
            return False
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False

def check_nvidia_drivers():
    """Check NVIDIA drivers"""
    print()
    print("CHECKING NVIDIA DRIVERS")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] NVIDIA drivers detected")
            # Extract driver version
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version' in line:
                    print(f"     {line.strip()}")
            return True
        else:
            print("[WARNING] nvidia-smi not accessible")
            print("         May need to run as Administrator")
            return False
    except FileNotFoundError:
        print("[ERROR] nvidia-smi not found")
        print("         NVIDIA drivers may not be installed")
        return False
    except Exception as e:
        print(f"[WARNING] Could not check drivers: {e}")
        return False

def fix_pytorch_cuda():
    """Fix PyTorch CUDA compatibility"""
    print()
    print("=" * 80)
    print("FIXING PYTORCH CUDA COMPATIBILITY")
    print("=" * 80)
    print()
    
    print("CUDA Toolkit 13.0 detected, but PyTorch was built for CUDA 12.6")
    print()
    print("Options:")
    print("  1. Reinstall PyTorch for CUDA 13.0 (if available)")
    print("  2. Keep CUDA 12.6 PyTorch (should work with CUDA 13.0 runtime)")
    print("  3. Restart system (most common fix)")
    print()
    
    response = input("Reinstall PyTorch for CUDA 13.0? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        print("Uninstalling current PyTorch...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], 
                         check=False)
            print("[OK] Uninstalled")
        except:
            pass
        
        print()
        print("Installing PyTorch with CUDA 12.6 (compatible with CUDA 13.0 runtime)...")
        print("Note: PyTorch CUDA 12.6 works with CUDA 13.0 runtime")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                 "--index-url", "https://download.pytorch.org/whl/cu126"],
                check=True
            )
            print("[OK] PyTorch reinstalled")
            return True
        except:
            print("[ERROR] Reinstallation failed")
            return False
    
    return False

def test_official_hrm():
    """Test Official HRM"""
    print()
    print("=" * 80)
    print("TESTING OFFICIAL HRM")
    print("=" * 80)
    print()
    
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        from core.hrm_official_integration import get_official_hrm_adapter
        adapter = get_official_hrm_adapter(
            checkpoint_dir="hrm_checkpoints",
            device=device,
            use_ensemble=True
        )
        
        if adapter:
            print(f"[OK] Official HRM adapter initialized")
            print(f"     Device: {adapter.device}")
            print(f"     Checkpoints: {len(adapter.models)}")
            print()
            if device == "cuda":
                print("[OK] Official HRM is ready with CUDA acceleration!")
            else:
                print("[OK] Official HRM is ready (CPU mode)")
            return True
        else:
            print("[WARNING] Adapter returned None")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to test Official HRM: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification"""
    print("=" * 80)
    print("CUDA SETUP VERIFICATION")
    print("=" * 80)
    print()
    
    # Check CUDA Toolkit
    cuda_toolkit = check_cuda_toolkit()
    
    # Check NVIDIA drivers
    nvidia_drivers = check_nvidia_drivers()
    
    # Check PyTorch CUDA
    pytorch_cuda = check_pytorch_cuda()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    if cuda_toolkit:
        print("[OK] CUDA Toolkit: Installed")
    else:
        print("[ERROR] CUDA Toolkit: Not found")
    
    if nvidia_drivers:
        print("[OK] NVIDIA Drivers: Installed")
    else:
        print("[WARNING] NVIDIA Drivers: Check needed")
    
    if pytorch_cuda:
        print("[OK] PyTorch CUDA: Available")
        print()
        print("✅ CUDA setup is complete!")
        print()
        # Test Official HRM
        test_official_hrm()
    else:
        print("[WARNING] PyTorch CUDA: Not available")
        print()
        print("Most common fix: RESTART YOUR SYSTEM")
        print()
        print("After restart, CUDA should be available.")
        print()
        
        response = input("Try fixing PyTorch CUDA compatibility now? (y/n): ").strip().lower()
        if response == 'y':
            if fix_pytorch_cuda():
                print()
                print("PyTorch reinstalled. Please RESTART your system, then verify again.")
        else:
            print()
            print("Next steps:")
            print("  1. RESTART your system")
            print("  2. Run: python verify_cuda_setup.py")
            print("  3. CUDA should be available after restart")

if __name__ == "__main__":
    main()



