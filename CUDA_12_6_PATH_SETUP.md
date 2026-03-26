# CUDA 12.6 PATH Setup Guide

## Current Status

✅ **CUDA 12.6**: Installed at `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6`  
✅ **CUDA 13.0**: Also installed (can coexist)  
❌ **Issue**: CUDA 13.0 is in PATH, CUDA 12.6 is NOT  
❌ **Result**: PyTorch cannot detect CUDA (needs CUDA 12.6)

---

## Solution: Add CUDA 12.6 to PATH

### Step-by-Step Instructions

1. **Open System Properties**
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter

2. **Open Environment Variables**
   - Click **"Advanced"** tab
   - Click **"Environment Variables"** button

3. **Edit PATH Variable**
   - Under **"System variables"**, find **"Path"**
   - Click **"Edit"**
   - Click **"New"** to add entries
   - Add these **AT THE BEGINNING** (order matters!):

     ```
```text
     C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin
     C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\lib\x64

     ```
```text

   - Click **"OK"** to save

4. **Add CUDA_HOME Variable**
   - Click **"New"** under System variables
   - Variable name: `CUDA_HOME`
   - Variable value: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6`
   - Click **"OK"**

5. **Add CUDA_PATH Variable** (Optional but recommended)
   - Click **"New"** under System variables
   - Variable name: `CUDA_PATH`
   - Variable value: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6`
   - Click **"OK"**

6. **Save All Changes**
   - Click **"OK"** on all dialogs
   - **RESTART YOUR SYSTEM** (required!)

---

## After Restart

Run this to verify:

```powershell

python verify_cuda_after_restart.py

```

**Expected Output:**

```
```text
[OK] CUDA Toolkit: Installed
[OK] PyTorch CUDA: Available
[OK] GPU: NVIDIA GeForce GTX 750 Ti
SUCCESS! CUDA IS WORKING

```

---

## Quick Reference

### Paths to Add
- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin`
- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\lib\x64`

### Environment Variables
- `CUDA_HOME` = `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6`
- `CUDA_PATH` = `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6`

### Important
- Add CUDA 12.6 paths **BEFORE** CUDA 13.0 paths in PATH
- **RESTART SYSTEM** after making changes
- Both CUDA versions can coexist

---

## Verification Commands

After restart, verify:

```powershell

# Check which CUDA is in PATH

where nvcc

# Should show CUDA 12.6 first

# C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe

# Check PyTorch CUDA

python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

```

---

## Troubleshooting

### If CUDA Still Not Available

1. **Check PATH order**: CUDA 12.6 must come BEFORE CUDA 13.0
2. **Verify restart**: System must be restarted after PATH changes
3. **Check environment variables**: Run `echo %CUDA_HOME%` in CMD
4. **Reinstall PyTorch** (if needed):

   ```powershell

   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

   ```

---

## Summary

**Current**: CUDA 12.6 installed but not in PATH  
**Action**: Add CUDA 12.6 to PATH (before CUDA 13.0)  
**Result**: PyTorch will detect CUDA after restart  
**Timeline**: ~5 minutes (PATH setup + restart)

---

**Next Step**: Follow the instructions above, then restart your system!

