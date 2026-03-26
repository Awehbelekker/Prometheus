# CUDA 12.6 PATH Setup Script
# Run this as Administrator to permanently set CUDA 12.6 environment variables

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "CUDA 12.6 PATH SETUP" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host "  3. Navigate to this directory" -ForegroundColor Yellow
    Write-Host "  4. Run: .\SETUP_CUDA_12_6.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# CUDA 12.6 paths
$cuda12_6 = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
$cuda12_6_bin = "$cuda12_6\bin"
$cuda12_6_lib = "$cuda12_6\lib\x64"

# Check if CUDA 12.6 exists
if (-not (Test-Path $cuda12_6)) {
    Write-Host "[ERROR] CUDA 12.6 not found at: $cuda12_6" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] CUDA 12.6 found at: $cuda12_6" -ForegroundColor Green
Write-Host ""

# Set CUDA_HOME
Write-Host "Setting CUDA_HOME..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("CUDA_HOME", $cuda12_6, "Machine")
Write-Host "[OK] CUDA_HOME set to: $cuda12_6" -ForegroundColor Green

# Set CUDA_PATH
Write-Host "Setting CUDA_PATH..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("CUDA_PATH", $cuda12_6, "Machine")
Write-Host "[OK] CUDA_PATH set to: $cuda12_6" -ForegroundColor Green

# Update PATH
Write-Host "Updating PATH..." -ForegroundColor Cyan
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$pathParts = $currentPath -split ';'

# Remove existing CUDA 12.6 entries (if any)
$pathParts = $pathParts | Where-Object { $_ -ne $cuda12_6_bin -and $_ -ne $cuda12_6_lib }

# Remove CUDA 13.0 entries temporarily
$cuda13_0_bin = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin"
$cuda13_0_lib = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\lib\x64"
$pathParts = $pathParts | Where-Object { $_ -ne $cuda13_0_bin -and $_ -ne $cuda13_0_lib }

# Add CUDA 12.6 at the beginning
$newPathParts = @($cuda12_6_bin, $cuda12_6_lib) + $pathParts

# Re-add CUDA 13.0 at the end (if it existed)
if ($currentPath -like "*v13.0*") {
    if (Test-Path $cuda13_0_bin) {
        $newPathParts += $cuda13_0_bin
    }
    if (Test-Path $cuda13_0_lib) {
        $newPathParts += $cuda13_0_lib
    }
}

$newPath = $newPathParts -join ';'
[Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")

Write-Host "[OK] PATH updated" -ForegroundColor Green
Write-Host "     CUDA 12.6 paths added at the beginning" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Environment variables set:" -ForegroundColor Green
Write-Host "  CUDA_HOME = $cuda12_6" -ForegroundColor White
Write-Host "  CUDA_PATH = $cuda12_6" -ForegroundColor White
Write-Host "  PATH updated (CUDA 12.6 at beginning)" -ForegroundColor White
Write-Host ""
Write-Host "NEXT STEP: RESTART YOUR SYSTEM" -ForegroundColor Yellow
Write-Host ""
Write-Host "After restart, verify with:" -ForegroundColor Cyan
Write-Host "  python verify_cuda_after_restart.py" -ForegroundColor White
Write-Host ""

