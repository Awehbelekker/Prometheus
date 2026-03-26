# FlashAttention Setup Guide

## Status: ⚠️ CUDA Required

FlashAttention requires CUDA (NVIDIA GPU) to compile and run. The system detected:

- **PyTorch**: CPU-only version (`torch.__version__ = 2.8.0+cpu`)
- **CUDA**: Not available (`CUDA_HOME environment variable is not set`)

## Options

### Option 1: Install CUDA and PyTorch with CUDA (Recommended for Performance)

If you have an NVIDIA GPU:

1. **Install CUDA 12.6**:

   ```bash

   # Windows: Download from NVIDIA website
   # https://developer.nvidia.com/cuda-downloads

   ```

2. **Install PyTorch with CUDA**:

   ```bash

   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

   ```

3. **Install FlashAttention**:

   ```bash

   pip install flash-attn --no-build-isolation

   ```

### Option 2: Use CPU-Only (Current Setup)

The system will work without FlashAttention, but with reduced performance:

- ✅ HRM will work (slower inference)
- ✅ All systems functional
- ⚠️ Slower model inference

### Option 3: Use Pre-compiled FlashAttention (if available)

Some systems may have pre-compiled wheels:

```bash

pip install flash-attn --no-build-isolation --find-links https://github.com/Dao-AILab/flash-attention/releases

```

## Current Status

- **FlashAttention**: Not installed (CUDA required)
- **System Status**: ✅ Functional without FlashAttention
- **Performance Impact**: Moderate (inference will be slower)

## Recommendation

For production use with optimal performance:

1. Install CUDA toolkit
2. Install PyTorch with CUDA support
3. Install FlashAttention

For development/testing:

- Current CPU-only setup is sufficient
- All features work, just slower inference

## Note

The Official HRM integration works without FlashAttention. FlashAttention is an optimization that improves performance but is not required for functionality.

