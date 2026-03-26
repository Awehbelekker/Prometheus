#!/usr/bin/env python3
"""
Fix CUDA Version Mismatch
PyTorch needs CUDA 12.6, but CUDA Toolkit 13.0 is installed
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_current_setup():
    """Check current CUDA setup"""
    print_header("CURRENT SETUP")
    
    import torch
    print(f"PyTorch Version: {torch.__version__}")
    print(f"PyTorch Built for CUDA: {torch.version.cuda}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print()
    
    # Check installed CUDA
    cuda_path = os.getenv('CUDA_PATH', '')
    if cuda_path:
        print(f"CUDA Toolkit Installed: {cuda_path}")
        version = Path(cuda_path).name.replace('v', '')
        print(f"CUDA Toolkit Version: {version}")
    else:
        print("CUDA Toolkit: Not found in CUDA_PATH")
    
    print()
    print("ISSUE: Version mismatch - PyTorch needs CUDA 12.6, but 13.0 is installed")
    print()

def solution_1_install_cuda_12_6():
    """Solution 1: Install CUDA Toolkit 12.6"""
    print_header("SOLUTION 1: Install CUDA Toolkit 12.6")
    print()
    print("This will install CUDA Toolkit 12.6 alongside 13.0")
    print("PyTorch will use 12.6, which matches its build")
    print()
    print("Download URL:")
    print("https://developer.nvidia.com/cuda-12-6-0-download-archive")
    print()
    print("Steps:")
    print("1. Download CUDA Toolkit 12.6.0 for Windows")
    print("2. Run installer (choose 'Custom' installation)")
    print("3. Install to: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
    print("4. Restart system")
    print("5. Run verification script again")
    print()

def solution_2_reinstall_pytorch():
    """Solution 2: Try to reinstall PyTorch (may not work for CUDA 13.0)"""
    print_header("SOLUTION 2: Reinstall PyTorch")
    print()
    print("WARNING: PyTorch may not have official CUDA 13.0 builds yet")
    print()
    print("This will try to reinstall PyTorch with CUDA 12.6:")
    print()
    print("Commands:")
    print("  pip uninstall torch torchvision torchaudio -y")
    print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126")
    print()
    
    # Skip interactive reinstall - provide instructions instead
    print("Skipping automatic reinstall. Use manual commands if needed.")
    response = 'n'
    if response == 'y':
        print()
        print("Uninstalling PyTorch...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"])
        print()
        print("Installing PyTorch with CUDA 12.6...")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
                       "--index-url", "https://download.pytorch.org/whl/cu126"])
        print()
        print("Reinstallation complete. Please restart and verify.")
    else:
        print("Skipped.")

def solution_3_workaround():
    """Solution 3: Workaround - Try to make PyTorch find CUDA 13.0"""
    print_header("SOLUTION 3: Workaround (May Not Work)")
    print()
    print("Attempting to make PyTorch work with CUDA 13.0...")
    print("This may not work due to binary incompatibility")
    print()
    
    cuda_path = os.getenv('CUDA_PATH', r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0')
    bin_path = os.path.join(cuda_path, 'bin')
    lib_path = os.path.join(cuda_path, 'lib', 'x64')
    
    # Add to PATH for this session
    current_path = os.getenv('PATH', '')
    if bin_path not in current_path:
        os.environ['PATH'] = bin_path + os.pathsep + current_path
        print(f"Added to PATH: {bin_path}")
    
    if lib_path not in current_path:
        os.environ['PATH'] = lib_path + os.pathsep + os.getenv('PATH', '')
        print(f"Added to PATH: {lib_path}")
    
    # Set CUDA_HOME
    os.environ['CUDA_HOME'] = cuda_path
    os.environ['CUDA_PATH'] = cuda_path
    print(f"Set CUDA_HOME: {cuda_path}")
    
    print()
    print("Testing if PyTorch can now detect CUDA...")
    try:
        import torch
        if torch.cuda.is_available():
            print("[OK] CUDA is now available!")
            return True
        else:
            print("[ERROR] CUDA still not available")
            print("This workaround likely won't work due to binary incompatibility")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("CUDA VERSION MISMATCH FIX")
    print("=" * 80)
    print()
    
    check_current_setup()
    
    print("=" * 80)
    print("RECOMMENDED SOLUTIONS")
    print("=" * 80)
    print()
    
    solution_1_install_cuda_12_6()
    
    print()
    print("=" * 80)
    print("ALTERNATIVE SOLUTIONS")
    print("=" * 80)
    print()
    
    print("Option A: Install CUDA Toolkit 12.6 (RECOMMENDED)")
    print("  - Best compatibility with PyTorch")
    print("  - Can coexist with CUDA 13.0")
    print()
    
    print("Option B: Try workaround (UNLIKELY TO WORK)")
    print("  - May fail due to binary incompatibility")
    print()
    
    # Try workaround automatically
    print("Attempting workaround automatically...")
    response = 'y'  # Auto-try
    if response == 'y':
        if solution_3_workaround():
            print()
            print("SUCCESS! Workaround worked!")
            print("However, for stability, still recommend installing CUDA 12.6")
        else:
            print()
            print("Workaround failed. Please install CUDA Toolkit 12.6.")
    else:
        print()
        print("Skipping workaround. Please install CUDA Toolkit 12.6.")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Download CUDA Toolkit 12.6.0:")
    print("   https://developer.nvidia.com/cuda-12-6-0-download-archive")
    print()
    print("2. Install to: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
    print()
    print("3. Restart your system")
    print()
    print("4. Run: python verify_cuda_after_restart.py")
    print()

if __name__ == "__main__":
    main()

