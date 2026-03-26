#!/usr/bin/env python3
"""
Fix System Components
Addresses CUDA, Backend Server, HRM FlashAttention issues
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

def check_cuda_status():
    """Check CUDA status and provide guidance"""
    print_header("CUDA STATUS")
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        pytorch_version = torch.__version__
        
        print(f"PyTorch Version: {pytorch_version}")
        print(f"CUDA Available: {cuda_available}")
        
        if 'cu' in pytorch_version:
            cuda_version = pytorch_version.split('cu')[1].split('+')[0]
            print(f"PyTorch CUDA Version: {cuda_version}")
        
        if cuda_available:
            print(f"CUDA Device Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  Device {i}: {torch.cuda.get_device_name(i)}")
            print()
            print("[OK] CUDA is working!")
            return True
        else:
            print()
            print("[WARNING] CUDA not available - running in CPU mode")
            print()
            print("Possible reasons:")
            print("  1. NVIDIA GPU not detected")
            print("  2. CUDA Toolkit not installed")
            print("  3. CUDA version mismatch")
            print("  4. GPU drivers not installed")
            print()
            print("To enable CUDA:")
            print("  1. Check if you have NVIDIA GPU: nvidia-smi")
            print("  2. Install CUDA Toolkit 12.6")
            print("  3. Restart system after installation")
            print("  4. Verify: python -c 'import torch; print(torch.cuda.is_available())'")
            print()
            print("NOTE: CPU mode works fine for most operations")
            print("      CUDA only needed for faster AI inference")
            return False
            
    except ImportError:
        print("[ERROR] PyTorch not installed")
        return False
    except Exception as e:
        print(f"[ERROR] CUDA check failed: {e}")
        return False

def check_flash_attention():
    """Check FlashAttention status"""
    print_header("FLASHATTENTION STATUS")
    
    try:
        import flash_attn
        print("[OK] FlashAttention is installed")
        print("   Official HRM can use FlashAttention for faster inference")
        return True
    except ImportError:
        print("[WARNING] FlashAttention not installed")
        print()
        print("FlashAttention is needed for Official HRM optimal performance")
        print()
        print("Installation:")
        print("  pip install flash-attn")
        print()
        print("Requirements:")
        print("  - CUDA 12.6+")
        print("  - NVIDIA GPU with Compute Capability 7.0+")
        print("  - PyTorch with CUDA support")
        print()
        print("NOTE: HRM works without FlashAttention (using LSTM fallback)")
        print("      FlashAttention just makes it faster")
        return False

def start_backend_server():
    """Start the backend server"""
    print_header("STARTING BACKEND SERVER")
    
    server_file = Path("unified_production_server.py")
    if not server_file.exists():
        print("[ERROR] unified_production_server.py not found")
        return False
    
    # Check if already running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("[INFO] Backend server already running on port 8000")
            print("   API: http://localhost:8000")
            print("   Docs: http://localhost:8000/docs")
            return True
    except:
        pass
    
    print("Starting backend server...")
    print()
    
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["cmd", "/k", "python", str(server_file)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print("[OK] Backend server starting in new terminal window")
            print()
            print("Server will be available at:")
            print("  API: http://localhost:8000")
            print("  Docs: http://localhost:8000/docs")
            print()
            print("Check the new terminal window for server status")
            return True
        else:
            subprocess.Popen(
                [sys.executable, str(server_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[OK] Backend server started in background")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

def main():
    print("=" * 80)
    print("FIXING PROMETHEUS SYSTEM COMPONENTS")
    print("=" * 80)
    print()
    
    # Check CUDA
    cuda_available = check_cuda_status()
    
    # Check FlashAttention
    flash_attn_available = check_flash_attention()
    
    # Start backend server
    backend_started = start_backend_server()
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"CUDA: {'[OK] Available' if cuda_available else '[INFO] CPU mode (optional)'}")
    print(f"FlashAttention: {'[OK] Installed' if flash_attn_available else '[INFO] Not installed (optional)'}")
    print(f"Backend Server: {'[OK] Starting' if backend_started else '[ERROR] Failed to start'}")
    print()
    
    if not cuda_available:
        print("NOTE: CUDA is optional - system works fine in CPU mode")
        print("      CUDA only needed for faster AI inference")
    print()
    
    if not flash_attn_available:
        print("NOTE: FlashAttention is optional - HRM works with LSTM fallback")
        print("      FlashAttention only needed for faster Official HRM")
    print()
    
    if backend_started:
        print("Backend server is starting...")
        print("Wait a few seconds, then check: http://localhost:8000/docs")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Operation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

