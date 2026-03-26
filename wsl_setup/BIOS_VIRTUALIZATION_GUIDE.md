# Enable Virtualization in BIOS - Quick Guide

## Why This Is Needed
WSL2 requires hardware virtualization (VT-x/AMD-V) to run Linux.
Current status: **DISABLED** (error 0x80370102)

## On Your Next Restart:

### Step 1: Enter BIOS
As computer restarts, repeatedly press your BIOS key:
- **Dell**: F2 or F12
- **HP**: F10 or Esc
- **Lenovo**: F1 or F2
- **ASUS**: F2 or Del
- **Acer**: F2 or Del
- **MSI**: Del

### Step 2: Enable Virtualization
Find and ENABLE one of these settings:

**For Intel CPU:**
- Location: Advanced → CPU Configuration
- Setting: **Intel Virtualization Technology (VT-x)** → ENABLED

**For AMD CPU:**
- Location: Advanced → CPU Configuration  
- Setting: **SVM Mode** or **AMD-V** → ENABLED

### Step 3: Save and Exit
- Press F10 (Save & Exit)
- Confirm Yes

## After Reboot - Verify It Worked

Open PowerShell and run:
```powershell
systeminfo | Select-String "Virtualization"
```

Should show: `Virtualization Enabled In Firmware: Yes`

## Then Complete WSL2 Setup

1. Open Start Menu → "Ubuntu 22.04 LTS"
2. Create username/password when prompted
3. Run the ROCm setup scripts:
```bash
cd /mnt/c/Users/Judy/Desktop/PROMETHEUS-Trading-Platform/wsl_setup
chmod +x *.sh
./install_rocm.sh
./install_ollama_rocm.sh
```

## Files Ready for You
- `install_rocm.sh` - ROCm GPU drivers
- `install_ollama_rocm.sh` - Ollama with GPU support
- `SETUP_GUIDE.md` - Full setup instructions

