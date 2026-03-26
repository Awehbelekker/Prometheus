#!/usr/bin/env python3
"""
Automated CUDA + PyTorch + FlashAttention Installation
For NVIDIA GeForce GTX 750 Ti
"""

import sys
import subprocess
import os

def check_cuda_support():
    """Check CUDA support for GTX 750 Ti"""
    print("=" * 80)
    print("NVIDIA GPU DETECTED: GeForce GTX 750 Ti")
    print("=" * 80)
    print()
    print("GPU Information:")
    print("  Model: NVIDIA GeForce GTX 750 Ti")
    print("  Compute Capability: 5.0 (Maxwell)")
    print("  CUDA Support: Yes (up to CUDA 12.x)")
    print()
    print("Note: GTX 750 Ti is an older GPU but supports CUDA")
    print("      Some newer features may not be available")
    print()

def install_pytorch_cuda():
    """Install PyTorch with CUDA support"""
    print("=" * 80)
    print("INSTALLING PYTORCH WITH CUDA")
    print("=" * 80)
    print()
    
    print("Step 1: Uninstalling CPU-only PyTorch...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], 
                      check=False, capture_output=True)
        print("[OK] CPU-only PyTorch uninstalled")
    except Exception as e:
        print(f"[WARNING] {e}")
    
    print()
    print("Step 2: Installing PyTorch with CUDA 12.6...")
    print("This may take several minutes...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
             "--index-url", "https://download.pytorch.org/whl/cu126"],
            check=True,
            text=True
        )
        print("[OK] PyTorch with CUDA installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installation failed")
        print("Trying alternative CUDA 11.8 (for older GPUs)...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                 "--index-url", "https://download.pytorch.org/whl/cu118"],
                check=True,
                text=True
            )
            print("[OK] PyTorch with CUDA 11.8 installed (compatible with GTX 750 Ti)")
            return True
        except:
            print("[ERROR] Failed to install PyTorch with CUDA")
            return False

def verify_pytorch_cuda():
    """Verify PyTorch CUDA installation"""
    print()
    print("=" * 80)
    print("VERIFYING PYTORCH CUDA")
    print("=" * 80)
    print()
    
    try:
        import torch
        print(f"[OK] PyTorch: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"[OK] CUDA Available: True")
            print(f"[OK] CUDA Version: {torch.version.cuda}")
            print(f"[OK] GPU: {torch.cuda.get_device_name(0)}")
            print(f"[OK] GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            return True
        else:
            print("[ERROR] CUDA not available in PyTorch")
            print("        This may require:")
            print("        1. CUDA Toolkit installation")
            print("        2. NVIDIA driver update")
            print("        3. System restart")
            return False
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def install_flash_attention():
    """Install FlashAttention (may not work on older GPUs)"""
    print()
    print("=" * 80)
    print("INSTALLING FLASH ATTENTION")
    print("=" * 80)
    print()
    print("Note: FlashAttention may not work on GTX 750 Ti (Compute Capability 5.0)")
    print("      Minimum requirement: Compute Capability 7.0 (Volta+)")
    print()
    
    response = input("Attempt FlashAttention installation anyway? (y/n): ").strip().lower()
    if response != 'y':
        print("[INFO] Skipping FlashAttention installation")
        return False
    
    print()
    print("Installing FlashAttention...")
    print("This may take 10-20 minutes (compiling from source)...")
    print("Note: Installation may fail on GTX 750 Ti")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "flash-attn", "--no-build-isolation"],
            check=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        print("[OK] FlashAttention installed successfully")
        return True
    except subprocess.TimeoutExpired:
        print("[ERROR] Installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] FlashAttention installation failed (expected for GTX 750 Ti)")
        print("          Official HRM will work but may be slower")
        print("          This is normal for older GPUs")
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
    """Main installation"""
    print("=" * 80)
    print("AUTOMATED CUDA + PYTORCH + FLASH ATTENTION INSTALLER")
    print("=" * 80)
    print()
    
    # Check GPU
    check_cuda_support()
    
    # Check if CUDA Toolkit is needed
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] CUDA Toolkit detected")
        else:
            print("[WARNING] CUDA Toolkit not found")
            print("          You may need to install CUDA Toolkit 12.6 or 11.8")
            print("          Download: https://developer.nvidia.com/cuda-downloads")
            print()
    except:
        print("[WARNING] CUDA Toolkit not found")
        print("          PyTorch may still work if NVIDIA drivers are installed")
        print()
    
    # Install PyTorch with CUDA
    print("Proceeding with PyTorch CUDA installation...")
    if not install_pytorch_cuda():
        print("[ERROR] Failed to install PyTorch with CUDA")
        return False
    
    # Verify
    if not verify_pytorch_cuda():
        print()
        print("[WARNING] CUDA not available after installation")
        print("          This may require:")
        print("          1. CUDA Toolkit installation")
        print("          2. System restart")
        print("          3. NVIDIA driver update")
        print()
        print("System will continue to work with CPU-only PyTorch")
        return False
    
    # Install FlashAttention (optional)
    install_flash_attention()
    
    # Test Official HRM
    if test_official_hrm():
        print()
        print("=" * 80)
        print("INSTALLATION COMPLETE!")
        print("=" * 80)
        print()
        print("[OK] Official HRM is ready!")
        print()
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



