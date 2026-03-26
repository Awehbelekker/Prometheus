# PROMETHEUS WSL2 + ROCm GPU Setup Guide

## Overview
This guide enables AMD RX 580 GPU acceleration for PROMETHEUS AI models via WSL2 and ROCm.

## Prerequisites
- Windows 10/11 with WSL2 enabled ✅
- Ubuntu 22.04 LTS installed in WSL2
- AMD RX 580 8GB GPU

## Step 1: Initialize Ubuntu 22.04

1. Open Start Menu → Search "Ubuntu 22.04 LTS"
2. Click to launch
3. Wait for installation to complete
4. Create username and password when prompted

## Step 2: Install ROCm

Open Ubuntu terminal and run:

```bash
# Navigate to setup scripts (from Windows path)
cd /mnt/c/Users/Judy/Desktop/PROMETHEUS-Trading-Platform/wsl_setup

# Make scripts executable
chmod +x install_rocm.sh install_ollama_rocm.sh

# Run ROCm installation
./install_rocm.sh
```

## Step 3: Install Ollama with ROCm

```bash
# Run Ollama installation
./install_ollama_rocm.sh
```

## Step 4: Verify GPU Access

```bash
# Check ROCm sees the GPU
rocminfo

# Check Ollama GPU status
ollama ps
```

## Step 5: Connect PROMETHEUS to WSL Ollama

Get WSL IP address:
```bash
hostname -I
```

In Windows, set environment variable:
```powershell
$env:OLLAMA_HOST = "<WSL_IP>:11434"
```

Or add to PROMETHEUS config.

## Troubleshooting

### GPU Not Detected
```bash
# Set GFX version for RX 580 (Polaris)
export HSA_OVERRIDE_GFX_VERSION=8.0.3
```

### Ollama Connection Issues
```bash
# Ensure Ollama is listening on all interfaces
sudo systemctl stop ollama
OLLAMA_HOST=0.0.0.0 ollama serve
```

### Memory Issues
```bash
# Check available memory
free -h

# Limit WSL memory in .wslconfig (Windows side)
# C:\Users\Judy\.wslconfig
[wsl2]
memory=16GB
```

## Expected Performance

| Model | CPU (Current) | GPU (Expected) |
|-------|---------------|----------------|
| llama3.1:8b | ~30s | ~8-10s |
| deepseek-r1:14b | ~68s | ~15-20s |
| llava:7b | ~45s | ~12s |

## Files Created

- `install_rocm.sh` - ROCm driver installation
- `install_ollama_rocm.sh` - Ollama with GPU support
- `SETUP_GUIDE.md` - This guide

