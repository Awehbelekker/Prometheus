# System Restart Instructions

## Step 1: Restart Your System

**Action Required**: Restart your computer now.

**Why**: After installing CUDA Toolkit, Windows needs to:

- Update environment variables
- Register CUDA libraries
- Initialize GPU drivers

**How**: 

1. Save all your work
2. Click Start → Power → Restart
3. Wait for system to fully restart

---

## Step 2: After Restart - Verify CUDA

Once your system has restarted, run this command:

```powershell

python verify_cuda_after_restart.py

```

This will:

- Check CUDA Toolkit installation
- Verify PyTorch can detect CUDA
- Test GPU operations
- Verify Official HRM with CUDA

---

## Expected Results

### Success (CUDA Working)

```
```text
[OK] CUDA Toolkit: Installed
[OK] NVIDIA Drivers: Installed
[OK] PyTorch CUDA: Available
[OK] GPU: NVIDIA GeForce GTX 750 Ti
[OK] Official HRM: Ready with CUDA

SUCCESS! CUDA IS WORKING

```

### If Issues

The script will provide troubleshooting steps.

---

## Quick Alternative Test

If you want a quick test:

```powershell

python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

```

**Expected**: `CUDA: True` and your GPU name

---

## After Verification

Once CUDA is verified:

1. **Launch Prometheus**:

   ```powershell

   python LAUNCH_PROMETHEUS.py

   ```

2. **Official HRM will automatically use CUDA**:
   - 10-50x faster inference
   - GPU-accelerated reasoning
   - All features functional

---

## Troubleshooting

### If CUDA Still Not Available

1. **Check NVIDIA Drivers** (run as Administrator):

   ```powershell

   nvidia-smi

   ```

2. **Check Environment Variables**:

   ```powershell

   echo $env:CUDA_PATH
   echo $env:CUDA_HOME

   ```

3. **Reinstall PyTorch** (if needed):

   ```powershell

   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

   ```

---

**Status**: Ready for restart and verification

