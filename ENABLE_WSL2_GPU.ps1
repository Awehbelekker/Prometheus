# ============================================================
# PROMETHEUS WSL2 + GPU Acceleration Setup Script
# Run this script AS ADMINISTRATOR
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PROMETHEUS WSL2 + GPU ACCELERATION SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 1: Enable Virtual Machine Platform
Write-Host "[1/4] Enabling Virtual Machine Platform..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    Write-Host "[OK] Virtual Machine Platform enabled" -ForegroundColor Green
} catch {
    Write-Host "[WARN] May already be enabled: $_" -ForegroundColor Yellow
}

# Step 2: Enable Windows Subsystem for Linux
Write-Host ""
Write-Host "[2/4] Enabling Windows Subsystem for Linux..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    Write-Host "[OK] WSL enabled" -ForegroundColor Green
} catch {
    Write-Host "[WARN] May already be enabled: $_" -ForegroundColor Yellow
}

# Step 3: Set WSL 2 as default
Write-Host ""
Write-Host "[3/4] Setting WSL 2 as default version..." -ForegroundColor Yellow
wsl --set-default-version 2
Write-Host "[OK] WSL 2 set as default" -ForegroundColor Green

# Step 4: Enable Hypervisor
Write-Host ""
Write-Host "[4/4] Enabling Hypervisor launch..." -ForegroundColor Yellow
try {
    bcdedit /set hypervisorlaunchtype auto
    Write-Host "[OK] Hypervisor enabled" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Hypervisor setting: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE - RESTART REQUIRED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After restart, run these commands in PowerShell:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. Install Ubuntu:" -ForegroundColor White
Write-Host "      wsl --install Ubuntu-22.04" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. After Ubuntu installs, run inside Ubuntu:" -ForegroundColor White
Write-Host "      # Update system" -ForegroundColor Gray
Write-Host "      sudo apt update && sudo apt upgrade -y" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. Install ROCm for AMD GPU (RX 580):" -ForegroundColor White
Write-Host "      wget https://repo.radeon.com/amdgpu-install/6.0/ubuntu/jammy/amdgpu-install_6.0.60000-1_all.deb" -ForegroundColor Cyan
Write-Host "      sudo apt install ./amdgpu-install_6.0.60000-1_all.deb" -ForegroundColor Cyan
Write-Host "      sudo amdgpu-install --usecase=rocm" -ForegroundColor Cyan
Write-Host ""
Write-Host "   4. Install PyTorch with ROCm:" -ForegroundColor White
Write-Host "      pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$restart = Read-Host "Restart computer now? (Y/N)"
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host ""
    Write-Host "Please restart manually to complete setup." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
}
