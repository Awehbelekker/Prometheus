#!/bin/bash
# ============================================================
# PROMETHEUS ROCm + PyTorch Setup for Ubuntu (WSL2)
# Run this script INSIDE Ubuntu after WSL2 is working
# ============================================================

echo "============================================================"
echo "   PROMETHEUS ROCm + GPU ACCELERATION SETUP"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}[OK] System updated${NC}"

echo ""
echo -e "${YELLOW}[2/8] Installing essential build tools...${NC}"
sudo apt install -y build-essential cmake git wget curl python3 python3-pip python3-venv
echo -e "${GREEN}[OK] Build tools installed${NC}"

echo ""
echo -e "${YELLOW}[3/8] Adding ROCm repository...${NC}"
# Add ROCm repository
sudo mkdir --parents --mode=0755 /etc/apt/keyrings
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | gpg --dearmor | sudo tee /etc/apt/keyrings/rocm.gpg > /dev/null

# For Ubuntu 22.04
echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.0 jammy main' | sudo tee /etc/apt/sources.list.d/rocm.list

# Set ROCm version priority
echo 'Package: *
Pin: release o=repo.radeon.com
Pin-Priority: 600' | sudo tee /etc/apt/preferences.d/rocm-pin-600
echo -e "${GREEN}[OK] ROCm repository added${NC}"

echo ""
echo -e "${YELLOW}[4/8] Installing ROCm...${NC}"
sudo apt update
sudo apt install -y rocm-hip-libraries rocm-dev
echo -e "${GREEN}[OK] ROCm installed${NC}"

echo ""
echo -e "${YELLOW}[5/8] Setting up ROCm environment...${NC}"
# Add ROCm to PATH
echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rocm/lib' >> ~/.bashrc
echo 'export HSA_OVERRIDE_GFX_VERSION=8.0.3' >> ~/.bashrc  # For RX 580 (Polaris)
source ~/.bashrc
echo -e "${GREEN}[OK] ROCm environment configured${NC}"

echo ""
echo -e "${YELLOW}[6/8] Creating Python virtual environment...${NC}"
python3 -m venv ~/prometheus_gpu_env
source ~/prometheus_gpu_env/bin/activate
pip install --upgrade pip
echo -e "${GREEN}[OK] Virtual environment created${NC}"

echo ""
echo -e "${YELLOW}[7/8] Installing PyTorch with ROCm support...${NC}"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
echo -e "${GREEN}[OK] PyTorch with ROCm installed${NC}"

echo ""
echo -e "${YELLOW}[8/8] Installing additional ML libraries...${NC}"
pip install numpy pandas scikit-learn transformers accelerate
pip install bitsandbytes  # For quantization
pip install ollama  # For LLM interaction
echo -e "${GREEN}[OK] ML libraries installed${NC}"

echo ""
echo "============================================================"
echo -e "${GREEN}   SETUP COMPLETE!${NC}"
echo "============================================================"
echo ""
echo -e "${CYAN}Testing GPU access...${NC}"
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    # Quick test
    x = torch.randn(1000, 1000).cuda()
    y = torch.matmul(x, x)
    print('GPU matrix multiplication: SUCCESS')
else:
    print('WARNING: GPU not detected')
"

echo ""
echo "============================================================"
echo -e "${YELLOW}To use this environment, run:${NC}"
echo -e "${CYAN}   source ~/prometheus_gpu_env/bin/activate${NC}"
echo ""
echo -e "${YELLOW}To access PROMETHEUS from WSL2:${NC}"
echo -e "${CYAN}   cd /mnt/c/Users/Judy/Desktop/PROMETHEUS-Trading-Platform${NC}"
echo "============================================================"
