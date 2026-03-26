#!/bin/bash
# ============================================================
# PROMETHEUS Ollama Installation Script with ROCm Support
# For WSL2 Ubuntu 22.04 with AMD RX 580
# ============================================================

set -e  # Exit on error

echo "=============================================="
echo "PROMETHEUS Ollama Installation with ROCm"
echo "=============================================="

# Check ROCm is installed
if ! command -v rocminfo &> /dev/null; then
    echo "ERROR: ROCm not found. Please run install_rocm.sh first."
    exit 1
fi

echo ""
echo "[1/4] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "[2/4] Configuring Ollama for ROCm..."
# Create Ollama service override for ROCm
sudo mkdir -p /etc/systemd/system/ollama.service.d/
echo '[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=8.0.3"
Environment="OLLAMA_HOST=0.0.0.0"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "[3/4] Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
sleep 5

echo ""
echo "[4/4] Pulling trading models..."
echo "Pulling llama3.1:8b (trading model)..."
ollama pull llama3.1:8b

echo "Pulling deepseek-r1:14b (reasoning model)..."
ollama pull deepseek-r1:14b

echo ""
echo "=============================================="
echo "Ollama Installation Complete!"
echo "=============================================="
echo ""
echo "GPU Status:"
ollama ps 2>/dev/null || echo "No models currently loaded"

echo ""
echo "Available models:"
ollama list

echo ""
echo "Test with: ollama run llama3.1:8b 'Hello, test GPU inference'"
echo ""
echo "To connect from Windows PROMETHEUS:"
echo "  Set OLLAMA_HOST=<WSL_IP>:11434 in your environment"
echo "  WSL IP: $(hostname -I | awk '{print $1}')"
echo ""

