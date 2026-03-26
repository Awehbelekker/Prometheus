#!/usr/bin/env python3
"""
Install CUDA, PyTorch with CUDA, and FlashAttention
Complete setup for Official HRM with optimal performance
"""

import sys
import subprocess
import platform

def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    print("=" * 80)
    print("CHECKING SYSTEM CAPABILITIES")
    print("=" * 80)
    print()
    
    # Check for nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] NVIDIA GPU detected!")
            print()
            print("GPU Information:")
            # Extract GPU name from nvidia-smi output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'NVIDIA' in line or 'GeForce' in line or 'RTX' in line or 'GTX' in line or 'Tesla' in line or 'Quadro' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("[WARNING] nvidia-smi not found or failed")
            return False
    except FileNotFoundError:
        print("[ERROR] nvidia-smi not found")
        print("         NVIDIA GPU drivers may not be installed")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking GPU: {e}")
        return False

def check_pytorch():
    """Check current PyTorch installation"""
    print()
    print("Checking PyTorch installation...")
    try:
        import torch
        print(f"[OK] PyTorch installed: {torch.__version__}")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            print(f"[OK] CUDA available: {torch.version.cuda}")
            print(f"[OK] GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"     GPU {i}: {torch.cuda.get_device_name(i)}")
            return True, True  # PyTorch installed, CUDA available
        else:
            print("[WARNING] PyTorch installed but CUDA not available")
            print("          Current: CPU-only version")
            return True, False  # PyTorch installed, CUDA not available
    except ImportError:
        print("[WARNING] PyTorch not installed")
        return False, False  # PyTorch not installed

def install_cuda_instructions():
    """Provide CUDA installation instructions"""
    print()
    print("=" * 80)
    print("CUDA INSTALLATION INSTRUCTIONS")
    print("=" * 80)
    print()
    print("CUDA Toolkit needs to be installed manually:")
    print()
    print("1. Download CUDA Toolkit 12.6:")
    print("   https://developer.nvidia.com/cuda-downloads")
    print()
    print("2. Select:")
    print("   - Operating System: Windows")
    print("   - Architecture: x86_64")
    print("   - Version: 12.6")
    print("   - Installer Type: exe (local)")
    print()
    print("3. Run the installer and follow the prompts")
    print()
    print("4. After installation, restart your computer")
    print()
    print("5. Verify installation:")
    print("   nvidia-smi")
    print()
    input("Press Enter after CUDA is installed to continue...")

def install_pytorch_cuda():
    """Install PyTorch with CUDA support"""
    print()
    print("=" * 80)
    print("INSTALLING PYTORCH WITH CUDA")
    print("=" * 80)
    print()
    
    print("Uninstalling CPU-only PyTorch...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"], 
                      check=False)
        print("[OK] CPU-only PyTorch uninstalled")
    except Exception as e:
        print(f"[WARNING] Error uninstalling: {e}")
    
    print()
    print("Installing PyTorch with CUDA 12.6...")
    print("This may take several minutes...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
             "--index-url", "https://download.pytorch.org/whl/cu126"],
            check=True,
            capture_output=True,
            text=True
        )
        print("[OK] PyTorch with CUDA installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installation failed: {e.stderr}")
        return False

def install_flash_attention():
    """Install FlashAttention"""
    print()
    print("=" * 80)
    print("INSTALLING FLASH ATTENTION")
    print("=" * 80)
    print()
    print("Installing FlashAttention...")
    print("This may take 10-20 minutes (compiling from source)...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "flash-attn", "--no-build-isolation"],
            check=True,
            capture_output=True,
            text=True
        )
        print("[OK] FlashAttention installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installation failed: {e.stderr}")
        print()
        print("If installation fails, you may need:")
        print("1. Visual Studio Build Tools (C++ compiler)")
        print("2. CUDA toolkit properly installed")
        print("3. Set CUDA_HOME environment variable")
        return False

def verify_installation():
    """Verify all installations"""
    print()
    print("=" * 80)
    print("VERIFYING INSTALLATION")
    print("=" * 80)
    print()
    
    # Check PyTorch
    try:
        import torch
        print(f"[OK] PyTorch: {torch.__version__}")
        if torch.cuda.is_available():
            print(f"[OK] CUDA: {torch.version.cuda}")
            print(f"[OK] GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("[ERROR] CUDA not available in PyTorch")
            return False
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False
    
    # Check FlashAttention
    try:
        import flash_attn
        print("[OK] FlashAttention: Installed")
    except ImportError:
        print("[WARNING] FlashAttention not installed")
        print("          Official HRM will still work but may be slower")
    
    return True

def test_official_hrm():
    """Test Official HRM with CUDA"""
    print()
    print("=" * 80)
    print("TESTING OFFICIAL HRM WITH CUDA")
    print("=" * 80)
    print()
    
    try:
        from core.hrm_official_integration import get_official_hrm_adapter
        adapter = get_official_hrm_adapter(
            checkpoint_dir="hrm_checkpoints",
            device="cuda",
            use_ensemble=True
        )
        
        if adapter:
            print(f"[OK] Official HRM adapter initialized")
            print(f"     Device: {adapter.device}")
            print(f"     Checkpoints: {len(adapter.models)}")
            print()
            print("[OK] Official HRM is ready with CUDA acceleration!")
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
    """Main installation process"""
    print("=" * 80)
    print("PROMETHEUS CUDA + PYTORCH + FLASH ATTENTION INSTALLER")
    print("=" * 80)
    print()
    
    # Step 1: Check GPU
    has_gpu = check_nvidia_gpu()
    if not has_gpu:
        print()
        print("[ERROR] No NVIDIA GPU detected!")
        print("         This installation requires an NVIDIA GPU with CUDA support")
        print("         The system will continue to work with CPU-only PyTorch")
        return False
    
    # Step 2: Check PyTorch
    pytorch_installed, cuda_available = check_pytorch()
    
    # Step 3: Install CUDA if needed
    if not cuda_available:
        print()
        print("[INFO] CUDA not available in PyTorch")
        response = input("Install CUDA Toolkit? (y/n): ").strip().lower()
        if response == 'y':
            install_cuda_instructions()
        else:
            print("[INFO] Skipping CUDA installation")
            print("       You can install it later and rerun this script")
    
    # Step 4: Install PyTorch with CUDA
    if not cuda_available:
        print()
        response = input("Install PyTorch with CUDA support? (y/n): ").strip().lower()
        if response == 'y':
            if not install_pytorch_cuda():
                print("[ERROR] Failed to install PyTorch with CUDA")
                return False
        else:
            print("[INFO] Skipping PyTorch CUDA installation")
            return False
    
    # Step 5: Verify PyTorch CUDA
    import torch
    if not torch.cuda.is_available():
        print()
        print("[ERROR] CUDA still not available after installation")
        print("         Please check:")
        print("         1. CUDA Toolkit is installed")
        print("         2. NVIDIA drivers are up to date")
        print("         3. Restart your computer")
        return False
    
    # Step 6: Install FlashAttention
    print()
    response = input("Install FlashAttention? (y/n): ").strip().lower()
    if response == 'y':
        if not install_flash_attention():
            print("[WARNING] FlashAttention installation failed")
            print("          Official HRM will work but may be slower")
    
    # Step 7: Verify
    if verify_installation():
        print()
        print("[OK] All installations verified!")
        
        # Step 8: Test Official HRM
        if test_official_hrm():
            print()
            print("=" * 80)
            print("INSTALLATION COMPLETE!")
            print("=" * 80)
            print()
            print("[OK] Official HRM is now ready with CUDA acceleration!")
            print()
            print("The system will now use:")
            print("  - Official HRM (27M parameters)")
            print("  - CUDA acceleration")
            print("  - FlashAttention optimization")
            print("  - Multi-checkpoint ensemble")
            print()
            return True
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



