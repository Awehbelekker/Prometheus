#!/usr/bin/env python3
"""
GPU Detection & Initialization for PROMETHEUS Trading Platform
Supports both CUDA (NVIDIA) and DirectML (AMD/Intel) backends
"""

import os
import sys
import logging
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DIRECTML_VENV_PATHS = [
    r"C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\.venv_directml_test\Scripts\python.exe",
    r".venv_directml_test\Scripts\python.exe",
    r".\.venv_directml_test\Scripts\python.exe",
]


def _normalize_python_path(python_executable: str) -> str:
    return os.path.normcase(os.path.abspath(python_executable))


def _subprocess_creation_flags() -> int:
    return subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0


def _python_supports_directml(python_executable: str, timeout: int = 10) -> bool:
    """Check whether a specific Python interpreter can create a DirectML device."""
    try:
        output = subprocess.run(
            [
                python_executable,
                "-c",
                "import torch_directml; device = torch_directml.device(); print('DIRECTML_OK')",
            ],
            capture_output=True,
            timeout=timeout,
            text=True,
            creationflags=_subprocess_creation_flags(),
        )
        return output.returncode == 0 and "DIRECTML_OK" in output.stdout
    except subprocess.TimeoutExpired:
        logger.debug("DirectML probe timed out for %s", python_executable)
    except Exception as exc:
        logger.debug("DirectML probe failed for %s: %s", python_executable, exc)
    return False


def get_preferred_runtime_python() -> Optional[str]:
    """Return the preferred DirectML-capable Python interpreter, if present."""
    for candidate in DIRECTML_VENV_PATHS:
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
    return None


def ensure_preferred_gpu_runtime(process_name: str = "PROMETHEUS") -> bool:
    """Re-exec the current script under the preferred DirectML runtime when needed.

    Returns True if the current process was replaced. Returns False when no action was needed.
    """
    preferred_python = get_preferred_runtime_python()
    if not preferred_python:
        return False

    current_python = os.path.abspath(sys.executable)
    if _normalize_python_path(current_python) == _normalize_python_path(preferred_python):
        return False

    if os.getenv("PROMETHEUS_GPU_RUNTIME_LOCK") == "1":
        return False

    if _python_supports_directml(current_python):
        return False

    if not _python_supports_directml(preferred_python):
        return False

    os.environ["PROMETHEUS_GPU_RUNTIME_LOCK"] = "1"
    print(f"{process_name}: switching Python runtime to DirectML environment: {preferred_python}")
    os.execv(preferred_python, [preferred_python, *sys.argv])


def detect_gpu_backend() -> Dict[str, Any]:
    """
    Detect available GPU backend: CUDA, DirectML, or None
    Returns structured info for admin dashboard
    Safe: includes timeouts to avoid hanging on GPU init
    """
    import subprocess
    import json
    
    result = {
        "available": False,
        "backend": None,
        "device_name": None,
        "memory_info": None,
        "status": "NOT_DETECTED",
        "current_python": os.path.abspath(sys.executable),
        "preferred_python": get_preferred_runtime_python(),
        "current_runtime_ready": False,
        "preferred_runtime_ready": False,
    }
    
    # Try CUDA first (NVIDIA GPUs)
    try:
        import torch
        if torch.cuda.is_available():
            result["available"] = True
            result["backend"] = "CUDA"
            result["device_name"] = torch.cuda.get_device_name(0)
            try:
                allocated = torch.cuda.memory_allocated() / (1024**3)
                reserved = torch.cuda.memory_reserved() / (1024**3)
                props = torch.cuda.get_device_properties(0)
                total = props.total_memory / (1024**3)
                result["memory_info"] = {
                    "allocated_gb": round(allocated, 2),
                    "reserved_gb": round(reserved, 2),
                    "total_gb": round(total, 2)
                }
            except Exception as e:
                logger.debug(f"Could not get CUDA memory info: {e}")
            result["status"] = "CUDA_DETECTED"
            result["current_runtime_ready"] = True
            return result
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"CUDA detection failed: {e}")
    
    current_directml_ready = _python_supports_directml(result["current_python"])
    result["current_runtime_ready"] = current_directml_ready

    preferred_python = result["preferred_python"]
    preferred_directml_ready = False
    if preferred_python and _normalize_python_path(preferred_python) != _normalize_python_path(result["current_python"]):
        preferred_directml_ready = _python_supports_directml(preferred_python)
    elif preferred_python and current_directml_ready:
        preferred_directml_ready = True
    result["preferred_runtime_ready"] = preferred_directml_ready

    if current_directml_ready:
        result["available"] = True
        result["backend"] = "DirectML"
        result["device_name"] = "AMD Radeon RX 580 Series"
        result["status"] = "DIRECTML_ACTIVE"
        return result

    if preferred_directml_ready:
        result["backend"] = "DirectML"
        result["device_name"] = "AMD Radeon RX 580 Series"
        result["status"] = "DIRECTML_RUNTIME_MISMATCH"
        return result
    
    # If no GPU detected
    result["status"] = "NO_GPU_DETECTED"
    return result


def get_device_for_inference():
    """
    Get the best available device for PyTorch model inference.
    
    Returns:
        torch.device('cuda') for NVIDIA GPUs via CUDA
        torch_directml.device() for AMD/Intel GPUs via DirectML
        torch.device('cpu') as fallback
    """
    info = detect_gpu_backend()
    
    # Check backend type from detect_gpu_backend() result
    if info.get("available", False):
        backend = info.get("backend", "").upper()
        if backend == "CUDA":
            import torch
            return torch.device('cuda')
        elif backend == "DIRECTML" and info.get("current_runtime_ready", False):
            import torch_directml
            return torch_directml.device()
    
    import torch
    return torch.device('cpu')


def initialize_gpu():
    """
    Initialize GPU backend if available
    Safe to call even if no GPU present
    """
    gpu_info = detect_gpu_backend()
    device = get_device_for_inference()
    
    if gpu_info["available"]:
        logger.info(f"GPU Detected: {gpu_info['backend']} - {gpu_info['device_name']} [device={device}]")
        
        if gpu_info["backend"] == "CUDA":
            logger.info(f"CUDA Memory: {gpu_info['memory_info']}")
        elif gpu_info["backend"] == "DirectML":
            logger.info("DirectML backend ready for AMD/Intel GPU acceleration")
        
        return True
    else:
        if gpu_info.get("status") == "DIRECTML_RUNTIME_MISMATCH":
            logger.info(
                "DirectML-capable environment exists but current runtime cannot use it. "
                "Current=%s Preferred=%s",
                gpu_info.get("current_python"),
                gpu_info.get("preferred_python"),
            )
        logger.info("No GPU detected - running on CPU")
        return False


if __name__ == "__main__":
    # Test script
    print("=" * 60)
    print("PROMETHEUS GPU Detection Test")
    print("=" * 60)
    
    gpu_info = detect_gpu_backend()
    print(f"\nGPU Available: {gpu_info['available']}")
    print(f"Backend: {gpu_info['backend']}")
    print(f"Device: {gpu_info['device_name']}")
    print(f"Status: {gpu_info['status']}")
    if gpu_info['memory_info']:
        print(f"Memory: {gpu_info['memory_info']}")
    
    device = get_device_for_inference()
    print(f"\nDevice for inference: {device}")
    print(f"Initialization successful: {initialize_gpu()}")
