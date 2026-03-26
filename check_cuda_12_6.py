#!/usr/bin/env python3
"""Check CUDA 12.6 installation and PATH configuration"""

import os
from pathlib import Path
import subprocess

print("=" * 80)
print("CUDA 12.6 INSTALLATION CHECK")
print("=" * 80)
print()

# Check if CUDA 12.6 is installed
cuda_12_6 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6")
cuda_13_0 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0")

print("Installation Status:")
print(f"  CUDA 12.6: {'[OK] INSTALLED' if cuda_12_6.exists() else '[ERROR] NOT FOUND'}")
print(f"  CUDA 13.0: {'[OK] INSTALLED' if cuda_13_0.exists() else '[ERROR] NOT FOUND'}")
print()

if cuda_12_6.exists():
    nvcc_12_6 = cuda_12_6 / "bin" / "nvcc.exe"
    print(f"CUDA 12.6 Path: {cuda_12_6}")
    print(f"nvcc.exe exists: {'[OK] YES' if nvcc_12_6.exists() else '[ERROR] NO'}")
    print()
    
    # Try to get version from CUDA 12.6
    if nvcc_12_6.exists():
        try:
            result = subprocess.run([str(nvcc_12_6), "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'release' in line.lower():
                        print(f"CUDA 12.6 Version: {line.strip()}")
        except:
            pass
    print()

# Check PATH
print("PATH Configuration:")
path = os.getenv('PATH', '')
if 'v12.6' in path:
    print("  [OK] CUDA 12.6 in PATH")
else:
    print("  [ERROR] CUDA 12.6 NOT in PATH")
    
if 'v13.0' in path:
    print("  [WARNING] CUDA 13.0 in PATH (may take precedence)")

print()

# Check which nvcc is being used
print("Current nvcc in PATH:")
try:
    result = subprocess.run(['where', 'nvcc'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0 and result.stdout.strip():
        nvcc_paths = result.stdout.strip().split('\n')
        for path in nvcc_paths:
            print(f"  {path}")
            if 'v12.6' in path:
                print("    [OK] This is CUDA 12.6")
            elif 'v13.0' in path:
                print("    [WARNING] This is CUDA 13.0 (wrong version)")
    else:
        print("  [ERROR] nvcc not found in PATH")
except:
    print("  ⚠️  Could not check")

print()

# Check PyTorch CUDA
print("PyTorch CUDA Status:")
try:
    import torch
    print(f"  PyTorch Version: {torch.__version__}")
    print(f"  PyTorch Built for: CUDA {torch.version.cuda}")
    print(f"  CUDA Available: {'[OK] YES' if torch.cuda.is_available() else '[ERROR] NO'}")
    
    if not torch.cuda.is_available():
        print()
        print("SOLUTION:")
        print("  1. Ensure system was restarted after CUDA 12.6 installation")
        print("  2. Check CUDA 12.6 is in PATH (before CUDA 13.0)")
        print("  3. Try setting CUDA_HOME:")
        print(f"     set CUDA_HOME={cuda_12_6}")
        print("  4. Restart system again")
except ImportError:
    print("  [ERROR] PyTorch not installed")

print()
print("=" * 80)

