# PROMETHEUS — Server Migration Guide

Moving PROMETHEUS from current server (DirectML GPU) to new server (GTX 1080 Ti / CUDA).

---

## New Server Specs

| Component | Spec |
|-----------|------|
| CPU | Intel Core i9-7960X, 16C/32T @ 2.80GHz |
| GPU | MSI GTX 1080 Ti 11GB VRAM (CUDA 6.1) |
| RAM | Kingston HyperX DDR4-3733 32GB |
| Storage | Samsung EVO 500GB SSD |
| OS | Windows 10 Pro |

---

## What to Transfer

The `migration_bundle/` folder in the project root contains everything you need.

| Item | Why needed |
|------|-----------|
| `hrm_checkpoints_market_finetuned/` | 85-epoch trained model, ~100% accuracy — takes hours to retrain |
| `databases/` | 638+ trades, 198K attribution records, learned AI weights |
| `models_pretrained/` | Huggingface transformer weights (~252MB) |
| `trained_models/` | sklearn regime classifier |
| `.env` | All API keys |
| `*.json` configs | AI voter weights, broker configs |

Do NOT transfer: `.venv_directml_test/`, `.venv-gpu311/` — recreate fresh with CUDA PyTorch.

---

## Step 1 — Transfer migration_bundle/

Options (pick one):

**USB Drive:**
```
Copy migration_bundle/ folder to USB
Plug into new server
Copy to C:\Users\<NewUser>\Desktop\PROMETHEUS-migration\
```

**Local Network Share (current server):**
```
Right-click migration_bundle/ → Properties → Sharing → Share
Note the network path: \\CURRENT-PC\migration_bundle
On new server: open File Explorer → type \\CURRENT-PC\ → copy folder
```

**Cloud (if bundle fits):**
```
Upload migration_bundle/ to Google Drive / OneDrive
Download on new server
```

---

## Step 2 — New Server: Windows Setup

1. Update Windows to latest patches
2. Install [NVIDIA driver 537+](https://www.nvidia.com/drivers) for GTX 1080 Ti
3. Verify: open Command Prompt → `nvidia-smi` → should show GTX 1080 Ti, 11264MiB

---

## Step 3 — Install Python 3.11

Download Python 3.11.9 from python.org. During install:
- Check "Add Python to PATH"
- Install for all users

Verify: `python --version` → `Python 3.11.9`

---

## Step 4 — Install Git and Clone

```powershell
# Install Git (or download from git-scm.com)
winget install Git.Git

# Clone repo
git clone https://github.com/Awehbelekker/Prometheus.git "C:\Users\<YourUser>\Desktop\PROMETHEUS-Trading-Platform"
cd "C:\Users\<YourUser>\Desktop\PROMETHEUS-Trading-Platform"
git checkout main
```

---

## Step 5 — Create Virtual Environment

```bash
# Must use this exact name — scripts reference it
python -m venv .venv_directml_test
.venv_directml_test\Scripts\activate

# Install PyTorch with CUDA 12.1 (works with GTX 1080 Ti CUDA 6.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify GPU detected
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# Expected: True  NVIDIA GeForce GTX 1080 Ti

# Install all PROMETHEUS dependencies
pip install -r requirements.txt
```

Do NOT install `torch_directml` — CUDA replaces it automatically.

---

## Step 6 — Restore Migration Bundle

```bash
# Set paths
PROJ="C:\Users\<YourUser>\Desktop\PROMETHEUS-Trading-Platform"
BUNDLE="<path to migration_bundle>"

# Databases → project root
copy "$BUNDLE\databases\*" "$PROJ\"

# HRM checkpoint (CRITICAL)
xcopy /E "$BUNDLE\hrm_checkpoints_market_finetuned" "$PROJ\hrm_checkpoints\market_finetuned\"

# Pretrained models
xcopy /E "$BUNDLE\models_pretrained" "$PROJ\models_pretrained\"

# Trained sklearn models
xcopy /E "$BUNDLE\trained_models" "$PROJ\trained_models\"

# Config files + .env
copy "$BUNDLE\.env" "$PROJ\.env"
copy "$BUNDLE\*.json" "$PROJ\"
```

---

## Step 7 — Install Ollama + Models

1. Download Ollama from [ollama.com](https://ollama.com) — Windows installer
2. Run installer, then open new terminal:

```bash
# Verify Ollama sees the GPU
ollama serve &
# In another terminal:
ollama list

# Pull recommended models (fit in 11GB VRAM)
ollama pull llama3.1:8b          # Primary trading reasoning (~4.9GB)
ollama pull llava:7b             # Chart vision analysis (~4.5GB)
ollama pull deepseek-r1:8b       # Complex analysis (~4.0GB)
```

**Ollama environment variables** (add to Windows System Environment):
```
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_NUM_PARALLEL=2
OLLAMA_KEEP_ALIVE=10m
CUDA_VISIBLE_DEVICES=0
```

---

## Step 8 — Configure .env

Open `.env` and verify:
```bash
AI_PROVIDER=ollama
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
USE_LLAVA_VISION=true
PREFER_CLOUD_VISION=false

# Update if username changed on new server:
# (Most paths are relative — usually no changes needed)
```

---

## Step 9 — Interactive Brokers Gateway

1. Download IB Gateway from interactivebrokers.com (Gateway, not TWS)
2. Install and login with account `U21922116`
3. Configure: API Settings → Enable socket client → Port `4002` (live) / `4001` (paper)
4. "Allow connections from localhost only" → ON

---

## Step 10 — Setup Watchdog (Auto-start)

```powershell
# Run PowerShell as Administrator:
.\SETUP_WATCHDOG_TASK.ps1
```

This creates a Windows Task Scheduler job that starts the watchdog on login and auto-restarts PROMETHEUS on crash.

---

## Step 11 — Verification Checklist

Run these in order before going live:

```bash
# Activate venv first
.venv_directml_test\Scripts\activate

# 1. GPU
python -c "import torch; print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# → CUDA: True  NVIDIA GeForce GTX 1080 Ti

# 2. HRM checkpoint loads
python -c "
import torch
ckpt = torch.load('hrm_checkpoints/market_finetuned/checkpoint.pt', map_location='cpu')
print('HRM loaded, keys:', list(ckpt.keys())[:3])
"

# 3. Ollama responding
curl http://localhost:11434/api/tags

# 4. Learning DB intact
python -c "
import sqlite3
conn = sqlite3.connect('prometheus_learning.db')
count = conn.execute('SELECT COUNT(*) FROM live_trade_outcomes').fetchone()[0]
print(f'Trade history: {count} records')
"

# 5. Full system test (paper mode — no live trades)
python launch_ultimate_prometheus_LIVE_TRADING.py
# Watch logs — should show: CUDA GPU detected, HRM loaded, Ollama connected
# Dashboard: http://localhost:8000
```

---

## Expected Improvements (DirectML → CUDA)

| Area | Current (DirectML) | New (CUDA 1080 Ti) |
|------|-------------------|-------------------|
| HRM inference | ~5ms/signal | ~1-2ms/signal |
| HRM training stability | Crashes at epoch 86 | No errors |
| LLM throughput (8B model) | ~15-20 tok/s | ~35-40 tok/s |
| Training time (150 epochs) | ~10.5 hours | ~3-4 hours |
| Simultaneous LLMs | 1 at a time | 2 × 8B models |
| Chart vision (LLaVA) | Slow / crashes | Smooth at 7B |

---

## Troubleshooting

**GPU not detected after setup:**
```bash
python -c "import torch; print(torch.version.cuda)"
# If None: wrong PyTorch build — reinstall with cu121 index URL
```

**Ollama not using GPU:**
```bash
# Check: Task Manager → Performance → GPU → should show load when Ollama runs
# If CPU only: check CUDA_VISIBLE_DEVICES=0 in environment variables
```

**HRM checkpoint error on load:**
```bash
# Ensure checkpoint copied correctly
ls hrm_checkpoints/market_finetuned/
# Should see: checkpoint.pt (and possibly config.json, tokenizer files)
```

**DB "no such table" errors:**
```bash
# DB copied but WAL not flushed — run on OLD server before copying:
python -c "
import sqlite3
conn = sqlite3.connect('prometheus_learning.db')
conn.execute('PRAGMA wal_checkpoint(FULL)')
conn.close()
print('WAL flushed')
"
```
