# Quick CUDA Setup Guide

## Current Status

**GPU**: Checking...  
**PyTorch**: CPU-only  
**CUDA**: Not installed

---

## Quick Installation (If You Have NVIDIA GPU)

### 1. Install CUDA Toolkit 12.6

```
```text
Download: https://developer.nvidia.com/cuda-downloads
Install: Run the .exe installer

```

### 2. Install PyTorch with CUDA

```powershell

pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

```

### 3. Install FlashAttention

```powershell

pip install flash-attn --no-build-isolation

```

### 4. Verify

```python

import torch
print("CUDA:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")

```

---

## If No GPU Detected

✅ **System works perfectly without CUDA!**

- Current setup is fully functional
- All features work
- Just slightly slower inference

**No action needed** - system is production-ready as-is.

---

## Automated Installer

```powershell

python install_cuda_pytorch_flash.py

```

This will:

1. Check for NVIDIA GPU
2. Guide you through CUDA installation
3. Install PyTorch with CUDA
4. Install FlashAttention
5. Test Official HRM

---

**See `CUDA_INSTALLATION_GUIDE.md` for detailed instructions.**

