#!/bin/bash
# ============================================================
# PROMETHEUS ROCm Installation Script for WSL2 Ubuntu 22.04
# Enables AMD RX 580 GPU acceleration for Ollama/LLMs
# ============================================================

set -e  # Exit on error

echo "=============================================="
echo "PROMETHEUS ROCm Installation for AMD RX 580"
echo "=============================================="

# Check if running in WSL2
if ! grep -q microsoft /proc/version; then
    echo "ERROR: This script must be run in WSL2"
    exit 1
fi

echo ""
echo "[1/6] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "[2/6] Installing prerequisites..."
sudo apt install -y wget gnupg2 software-properties-common curl

echo ""
echo "[3/6] Adding ROCm repository..."
# Add ROCm GPG key
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -

# Add ROCm repository for Ubuntu 22.04
echo "deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.0.2 jammy main" | sudo tee /etc/apt/sources.list.d/rocm.list

# Set ROCm version preference
echo 'Package: *
Pin: release o=repo.radeon.com
Pin-Priority: 600' | sudo tee /etc/apt/preferences.d/rocm-pin-600

echo ""
echo "[4/6] Installing ROCm packages..."
sudo apt update
sudo apt install -y rocm-hip-libraries rocm-hip-runtime rocm-dev

echo ""
echo "[5/6] Setting up environment variables..."
# Add ROCm to PATH
echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rocm/lib' >> ~/.bashrc
echo 'export HSA_OVERRIDE_GFX_VERSION=8.0.3' >> ~/.bashrc  # For RX 580 (Polaris)

# Apply changes
source ~/.bashrc

echo ""
echo "[6/6] Verifying ROCm installation..."
if command -v rocminfo &> /dev/null; then
    echo "ROCm installed successfully!"
    rocminfo | head -20
else
    echo "WARNING: rocminfo not found. ROCm may not be fully installed."
fi

echo ""
echo "=============================================="
echo "ROCm Installation Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Run: source ~/.bashrc"
echo "2. Verify GPU: rocminfo"
echo "3. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "4. Test: ollama run llama3.1:8b"
echo ""

