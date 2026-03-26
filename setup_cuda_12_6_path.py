#!/usr/bin/env python3
"""
Setup CUDA 12.6 PATH Configuration
This script helps configure CUDA 12.6 for PyTorch
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def check_cuda_12_6():
    """Check if CUDA 12.6 is installed"""
    cuda_12_6 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6")
    return cuda_12_6.exists()

def set_session_environment():
    """Set CUDA environment variables for current session"""
    cuda_12_6 = Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6")
    
    if not cuda_12_6.exists():
        print("[ERROR] CUDA 12.6 not found!")
        return False
    
    # Set for current session
    os.environ['CUDA_HOME'] = str(cuda_12_6)
    os.environ['CUDA_PATH'] = str(cuda_12_6)
    
    # Add to PATH for this session
    cuda_bin = str(cuda_12_6 / "bin")
    cuda_lib = str(cuda_12_6 / "lib" / "x64")
    
    current_path = os.getenv('PATH', '')
    if cuda_bin not in current_path:
        os.environ['PATH'] = f"{cuda_bin};{cuda_lib};{current_path}"
    
    print("[OK] Environment variables set for this session")
    print(f"     CUDA_HOME: {os.getenv('CUDA_HOME')}")
    print(f"     CUDA_PATH: {os.getenv('CUDA_PATH')}")
    return True

def test_pytorch_cuda():
    """Test if PyTorch can detect CUDA"""
    try:
        import torch
        if torch.cuda.is_available():
            print("[SUCCESS] CUDA is available in PyTorch!")
            print(f"     GPU: {torch.cuda.get_device_name(0)}")
            print(f"     CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("[WARNING] CUDA still not available in PyTorch")
            print("     This may require a system restart")
            return False
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False

def create_registry_script():
    """Create a .reg file to set system environment variables"""
    cuda_12_6 = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
    cuda_bin = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin"
    cuda_lib = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\lib\x64"
    
    reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment]
"CUDA_HOME"="{cuda_12_6}"
"CUDA_PATH"="{cuda_12_6}"

"""
    
    # Note: PATH modification via registry is complex, so we'll provide manual instructions
    reg_file = Path("set_cuda_environment.reg")
    reg_file.write_text(reg_content)
    print(f"[OK] Created registry file: {reg_file}")
    print("     WARNING: Only run this if you understand registry editing!")
    print("     Better to use System Properties method (see instructions)")

def main():
    print("=" * 80)
    print("CUDA 12.6 PATH SETUP")
    print("=" * 80)
    print()
    
    # Check CUDA 12.6
    if not check_cuda_12_6():
        print("[ERROR] CUDA 12.6 not found!")
        print("Expected: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
        return False
    
    print("[OK] CUDA 12.6 is installed")
    print()
    
    # Check admin
    is_admin = check_admin()
    if is_admin:
        print("[OK] Running with Administrator privileges")
    else:
        print("[INFO] Not running as Administrator")
        print("       Some operations may require admin rights")
    print()
    
    print_header("OPTION 1: SET FOR CURRENT SESSION (Quick Test)")
    print("This sets CUDA 12.6 for this Python session only")
    print("Good for testing, but won't persist after restart")
    print()
    
    response = input("Set CUDA 12.6 for current session? (y/n): ").strip().lower()
    if response == 'y':
        if set_session_environment():
            print()
            print("Testing PyTorch CUDA...")
            if test_pytorch_cuda():
                print()
                print("[SUCCESS] CUDA is working in this session!")
                print("Note: This is temporary - restart will reset")
                print("For permanent setup, use Option 2")
            else:
                print()
                print("[INFO] CUDA not detected yet")
                print("This may require a system restart")
    
    print()
    print_header("OPTION 2: PERMANENT SETUP (Recommended)")
    print("This requires manual steps but is permanent")
    print()
    print("STEPS:")
    print("1. Press Win + R, type: sysdm.cpl")
    print("2. Go to 'Advanced' tab -> 'Environment Variables'")
    print("3. Under 'System variables', click 'New'")
    print("   Variable name: CUDA_HOME")
    print(f"   Variable value: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
    print("4. Click 'New' again")
    print("   Variable name: CUDA_PATH")
    print(f"   Variable value: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6")
    print("5. Find 'Path' variable, click 'Edit'")
    print("6. Click 'New' and add (at the BEGINNING):")
    print(f"   C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6\\bin")
    print("7. Click 'New' again and add:")
    print(f"   C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6\\lib\\x64")
    print("8. IMPORTANT: Move CUDA 12.6 entries BEFORE CUDA 13.0 entries")
    print("9. Click OK on all dialogs")
    print("10. RESTART YOUR SYSTEM")
    print()
    
    print_header("AFTER RESTART")
    print("Run this to verify:")
    print("  python verify_cuda_after_restart.py")
    print()
    print("Expected output:")
    print("  [OK] CUDA Toolkit: Installed")
    print("  [OK] PyTorch CUDA: Available")
    print("  [OK] GPU: NVIDIA GeForce GTX 750 Ti")
    print("  SUCCESS! CUDA IS WORKING")
    print()
    
    print_header("SUMMARY")
    print("Current Status:")
    print("  [OK] CUDA 12.6 installed")
    print("  [ACTION NEEDED] Add to PATH and set CUDA_HOME")
    print("  [ACTION NEEDED] Restart system")
    print()
    print("Next Steps:")
    print("  1. Follow Option 2 instructions above")
    print("  2. Restart system")
    print("  3. Run: python verify_cuda_after_restart.py")
    print()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

