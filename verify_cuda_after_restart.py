#!/usr/bin/env python3
"""
Post-Restart CUDA Verification Script
Run this after restarting your system to verify CUDA is working
"""

import sys
import subprocess

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()

def check_cuda_toolkit():
    """Check CUDA Toolkit"""
    print_header("CHECKING CUDA TOOLKIT")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'release' in line.lower():
                    print(f"[OK] CUDA Toolkit: {line.strip()}")
                    return True
        print("[ERROR] CUDA Toolkit not found")
        return False
    except FileNotFoundError:
        print("[ERROR] nvcc not found - CUDA Toolkit may not be installed")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def check_pytorch_cuda():
    """Check PyTorch CUDA"""
    print_header("CHECKING PYTORCH CUDA")
    
    try:
        import torch
        print(f"[OK] PyTorch: {torch.__version__}")
        
        if hasattr(torch.version, 'cuda'):
            print(f"[OK] PyTorch CUDA Built: {torch.version.cuda}")
        
        if torch.cuda.is_available():
            print(f"[OK] CUDA Available: True")
            print(f"[OK] CUDA Version: {torch.version.cuda}")
            print(f"[OK] GPU Count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"[OK] GPU {i}: {torch.cuda.get_device_name(i)}")
                props = torch.cuda.get_device_properties(i)
                print(f"     Memory: {props.total_memory / 1024**3:.2f} GB")
                print(f"     Compute Capability: {props.major}.{props.minor}")
            
            # Test CUDA operation
            try:
                x = torch.randn(3, 3).cuda()
                y = torch.randn(3, 3).cuda()
                z = torch.matmul(x, y)
                print(f"[OK] CUDA Operation Test: SUCCESS")
                return True
            except Exception as e:
                print(f"[ERROR] CUDA Operation Test Failed: {e}")
                return False
        else:
            print("[ERROR] CUDA not available in PyTorch")
            print()
            print("Troubleshooting:")
            print("  1. Did you restart your system? (Required after CUDA installation)")
            print("  2. Check NVIDIA drivers: nvidia-smi (run as Administrator)")
            print("  3. Verify CUDA_HOME environment variable is set")
            return False
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def check_nvidia_drivers():
    """Check NVIDIA drivers"""
    print_header("CHECKING NVIDIA DRIVERS")
    
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] NVIDIA drivers detected")
            # Extract key info
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Driver Version' in line or 'CUDA Version' in line:
                    print(f"     {line.strip()}")
            return True
        else:
            print("[WARNING] nvidia-smi returned error")
            print("         Try running as Administrator")
            return False
    except FileNotFoundError:
        print("[ERROR] nvidia-smi not found")
        print("         NVIDIA drivers may not be installed")
        return False
    except Exception as e:
        print(f"[WARNING] Could not check drivers: {e}")
        print("         Try running as Administrator")
        return False

def test_official_hrm():
    """Test Official HRM with CUDA"""
    print_header("TESTING OFFICIAL HRM WITH CUDA")
    
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Device: {device}")
        print()
        
        from core.hrm_official_integration import get_official_hrm_adapter
        
        print("Initializing Official HRM adapter...")
        adapter = get_official_hrm_adapter(
            checkpoint_dir="hrm_checkpoints",
            device=device,
            use_ensemble=True
        )
        
        if adapter:
            print(f"[OK] Official HRM adapter initialized")
            print(f"     Device: {adapter.device}")
            print(f"     Checkpoints: {len(adapter.models)}")
            
            if device == "cuda":
                print()
                print("[OK] Official HRM is ready with CUDA acceleration!")
                print("     Performance: 10-50x faster than CPU")
            else:
                print()
                print("[OK] Official HRM is ready (CPU mode)")
                print("     Note: CUDA not available, using CPU")
            
            return True
        else:
            print("[WARNING] Adapter returned None")
            return False
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("         Official HRM integration may not be set up")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to test Official HRM: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification"""
    print("=" * 80)
    print("POST-RESTART CUDA VERIFICATION")
    print("=" * 80)
    print()
    print("This script verifies CUDA is working after system restart")
    print()
    
    results = {}
    
    # Check CUDA Toolkit
    results['cuda_toolkit'] = check_cuda_toolkit()
    
    # Check NVIDIA drivers
    results['nvidia_drivers'] = check_nvidia_drivers()
    
    # Check PyTorch CUDA
    results['pytorch_cuda'] = check_pytorch_cuda()
    
    # Test Official HRM
    if results['pytorch_cuda']:
        results['official_hrm'] = test_official_hrm()
    else:
        print()
        print("Skipping Official HRM test (CUDA not available)")
        results['official_hrm'] = False
    
    # Summary
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    all_ok = True
    if results['cuda_toolkit']:
        print("[OK] CUDA Toolkit: Installed")
    else:
        print("[ERROR] CUDA Toolkit: Not found")
        all_ok = False
    
    if results['nvidia_drivers']:
        print("[OK] NVIDIA Drivers: Installed")
    else:
        print("[WARNING] NVIDIA Drivers: Check needed")
    
    if results['pytorch_cuda']:
        print("[OK] PyTorch CUDA: Available")
    else:
        print("[ERROR] PyTorch CUDA: Not available")
        all_ok = False
    
    if results.get('official_hrm'):
        print("[OK] Official HRM: Ready with CUDA")
    elif results['pytorch_cuda']:
        print("[WARNING] Official HRM: Check needed")
    
    print()
    
    if all_ok and results['pytorch_cuda']:
        print("=" * 80)
        print("SUCCESS! CUDA IS WORKING")
        print("=" * 80)
        print()
        print("Your system is ready for GPU-accelerated trading!")
        print()
        print("Next steps:")
        print("  1. Launch Prometheus: python LAUNCH_PROMETHEUS.py")
        print("  2. Official HRM will use CUDA acceleration")
        print("  3. Enjoy 10-50x faster inference!")
        print()
        return True
    else:
        print("=" * 80)
        print("ISSUES DETECTED")
        print("=" * 80)
        print()
        if not results['pytorch_cuda']:
            print("CUDA is not available in PyTorch.")
            print()
            print("Common fixes:")
            print("  1. Ensure you restarted your system")
            print("  2. Check NVIDIA drivers: nvidia-smi (run as Administrator)")
            print("  3. Verify CUDA_HOME environment variable")
            print("  4. Try: pip install torch --index-url https://download.pytorch.org/whl/cu126 --force-reinstall")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



