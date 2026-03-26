#!/usr/bin/env python3
"""
Fix CUDA PATH to prioritize CUDA 12.6 over CUDA 13.0
This ensures PyTorch can find the correct CUDA version
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def main():
    print("=" * 80)
    print("CUDA PATH FIX - Prioritize CUDA 12.6")
    print("=" * 80)
    print()
    
    cuda_12_6 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6")
    cuda_13_0 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0")
    
    if not cuda_12_6.exists():
        print("[ERROR] CUDA 12.6 not found!")
        print("Expected: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
        return False
    
    print_header("CURRENT PATH STATUS")
    
    current_path = os.getenv('PATH', '')
    path_parts = current_path.split(os.pathsep)
    
    cuda_12_6_bin = str(cuda_12_6 / "bin")
    cuda_12_6_lib = str(cuda_12_6 / "lib" / "x64")
    cuda_13_0_bin = str(cuda_13_0 / "bin") if cuda_13_0.exists() else None
    
    print("Current PATH contains:")
    has_12_6 = cuda_12_6_bin in path_parts
    has_13_0 = cuda_13_0_bin and cuda_13_0_bin in path_parts
    
    print(f"  CUDA 12.6: {'[OK] YES' if has_12_6 else '[ERROR] NO'}")
    print(f"  CUDA 13.0: {'[WARNING] YES (taking precedence)' if has_13_0 else '[OK] NO'}")
    print()
    
    if has_12_6 and not has_13_0:
        print("[OK] PATH is already correct!")
        return True
    
    print_header("SOLUTION")
    
    print("To fix CUDA PATH, you need to:")
    print()
    print("OPTION 1: Set Environment Variables (Temporary - This Session)")
    print("-" * 60)
    print(f"set CUDA_HOME={cuda_12_6}")
    print(f"set CUDA_PATH={cuda_12_6}")
    print(f"set PATH={cuda_12_6_bin};{cuda_12_6_lib};%PATH%")
    print()
    print("OPTION 2: Set System Environment Variables (Permanent)")
    print("-" * 60)
    print("1. Press Win + R, type: sysdm.cpl")
    print("2. Go to 'Advanced' tab -> 'Environment Variables'")
    print("3. Under 'System variables', find 'PATH'")
    print("4. Edit PATH and:")
    print(f"   a. Add: {cuda_12_6_bin} (at the BEGINNING)")
    print(f"   b. Add: {cuda_12_6_lib} (at the BEGINNING)")
    print("   c. Move CUDA 12.6 entries BEFORE CUDA 13.0 entries")
    print("5. Add new variable 'CUDA_HOME':")
    print(f"   Value: {cuda_12_6}")
    print("6. Add new variable 'CUDA_PATH':")
    print(f"   Value: {cuda_12_6}")
    print("7. Click OK and RESTART your system")
    print()
    
    print_header("QUICK TEST (This Session Only)")
    
    response = input("Set CUDA 12.6 for this session? (y/n): ").strip().lower()
    if response == 'y':
        # Set for this session
        os.environ['CUDA_HOME'] = str(cuda_12_6)
        os.environ['CUDA_PATH'] = str(cuda_12_6)
        
        # Rebuild PATH with CUDA 12.6 first
        new_path_parts = [cuda_12_6_bin, cuda_12_6_lib]
        for part in path_parts:
            if part not in [cuda_12_6_bin, cuda_12_6_lib]:
                if cuda_13_0_bin and part == cuda_13_0_bin:
                    # Put CUDA 13.0 after CUDA 12.6
                    continue
                new_path_parts.append(part)
        
        if cuda_13_0_bin and cuda_13_0_bin in path_parts:
            new_path_parts.append(cuda_13_0_bin)
        
        os.environ['PATH'] = os.pathsep.join(new_path_parts)
        
        print()
        print("[OK] Environment variables set for this session")
        print()
        print("Testing PyTorch CUDA...")
        try:
            import torch
            if torch.cuda.is_available():
                print("[SUCCESS] CUDA is now available in PyTorch!")
                print(f"GPU: {torch.cuda.get_device_name(0)}")
                return True
            else:
                print("[WARNING] CUDA still not available")
                print("You may need to restart the system")
                return False
        except ImportError:
            print("[ERROR] PyTorch not installed")
            return False
    else:
        print("Skipped. Please set environment variables manually.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

