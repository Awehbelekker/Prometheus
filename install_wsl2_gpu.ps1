# ============================================================
# WSL2 + ROCm GPU Setup for PROMETHEUS Trading Platform
# Run this script as Administrator!
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  WSL2 + AMD ROCm GPU Setup for RX 580" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/4] Enabling Virtual Machine Platform..." -ForegroundColor Green
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host ""
Write-Host "[2/4] Enabling Windows Subsystem for Linux..." -ForegroundColor Green
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

Write-Host ""
Write-Host "[3/4] Setting WSL2 as default..." -ForegroundColor Green
wsl --set-default-version 2

Write-Host ""
Write-Host "[4/4] Installing Ubuntu 22.04..." -ForegroundColor Green
wsl --install -d Ubuntu-22.04

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  IMPORTANT: RESTART REQUIRED!" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After restart, run these commands in Ubuntu terminal:" -ForegroundColor White
Write-Host ""
Write-Host "# 1. Update system" -ForegroundColor Gray
Write-Host "sudo apt update && sudo apt upgrade -y" -ForegroundColor Green
Write-Host ""
Write-Host "# 2. Install ROCm for RX 580" -ForegroundColor Gray
Write-Host "wget https://repo.radeon.com/amdgpu-install/6.0/ubuntu/jammy/amdgpu-install_6.0.60000-1_all.deb" -ForegroundColor Green
Write-Host "sudo apt install ./amdgpu-install_6.0.60000-1_all.deb" -ForegroundColor Green
Write-Host "sudo amdgpu-install --usecase=rocm" -ForegroundColor Green
Write-Host ""
Write-Host "# 3. Install Ollama" -ForegroundColor Gray
Write-Host "curl -fsSL https://ollama.com/install.sh | sh" -ForegroundColor Green
Write-Host ""
Write-Host "# 4. Set GPU environment and run Ollama" -ForegroundColor Gray
Write-Host "export HSA_OVERRIDE_GFX_VERSION=8.0.3" -ForegroundColor Green
Write-Host "ollama serve &" -ForegroundColor Green
Write-Host "ollama run deepseek-r1:8b" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

$restart = Read-Host "Restart computer now? (Y/N)"
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "Restarting in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Restart-Computer -Force
} else {
    Write-Host "Please restart your computer manually to complete the installation." -ForegroundColor Yellow
}

