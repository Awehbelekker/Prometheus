# PROMETHEUS Master Startup Script (PowerShell)
# Starts all systems in the correct order

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROMETHEUS MASTER STARTUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Start backend server
Write-Host "`n[1/2] Starting backend server..." -ForegroundColor Yellow
$backendScript = Join-Path $scriptPath "start_backend_permanent.ps1"
if (Test-Path $backendScript) {
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$backendScript`"" -WindowStyle Normal
    Write-Host "✅ Backend server startup initiated" -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "⚠️ Backend startup script not found" -ForegroundColor Yellow
}

# Verify main trading system
Write-Host "`n[2/2] Checking main trading system..." -ForegroundColor Yellow
Write-Host "Note: Main trading system should be started separately with:" -ForegroundColor Cyan
Write-Host "  python launch_ultimate_prometheus_LIVE_TRADING.py" -ForegroundColor Cyan

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "STARTUP COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nBackend server should be starting..." -ForegroundColor Green
Write-Host "Check http://127.0.0.1:8000/health to verify" -ForegroundColor Cyan
