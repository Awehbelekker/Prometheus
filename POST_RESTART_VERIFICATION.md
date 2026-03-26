# Post-Restart CUDA Verification

## After System Restart

Run these commands to verify CUDA is working:

### 1. Quick Check

```powershell

python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

```

**Expected**: `CUDA: True` and GPU name

### 2. Full Verification

```powershell

python verify_cuda_setup.py

```

### 3. Test Official HRM

```powershell

python test_hrm_integration.py

```

---

## If CUDA Still Not Available

### Check 1: NVIDIA Drivers

```powershell

# Run as Administrator

nvidia-smi

```

Should show GPU information.

### Check 2: Environment Variables

```powershell

echo $env:CUDA_PATH
echo $env:CUDA_HOME

```

Should show CUDA installation path.

### Check 3: Reinstall PyTorch

If needed:

```powershell

pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

```

---

## Success Indicators

✅ `torch.cuda.is_available()` returns `True`  
✅ GPU name is displayed  
✅ Official HRM uses `device="cuda"`  
✅ Faster inference times

---

**Status**: Ready for verification after restart

