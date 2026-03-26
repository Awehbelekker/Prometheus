# PROMETHEUS Trading Platform - Independent Runner
# Double-click this file or run from PowerShell

$Host.UI.RawUI.WindowTitle = "PROMETHEUS Trading Platform - LIVE"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PROMETHEUS TRADING PLATFORM" -ForegroundColor Green
Write-Host "  Running independently (24/7)" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform"

# Create logs folder if not exists
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }

$logFile = "logs\prometheus_$(Get-Date -Format 'yyyyMMdd').log"

Write-Host "Starting PROMETHEUS at $(Get-Date)" -ForegroundColor Yellow
Write-Host "Logging to: $logFile" -ForegroundColor Gray
Write-Host ""

while ($true) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting trading cycle..." -ForegroundColor Green
    
    # Run with output to both console and log file
    python improved_dual_broker_trading.py 2>&1 | Tee-Object -FilePath $logFile -Append
    
    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Cycle ended. Restarting in 10 seconds..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop completely." -ForegroundColor Red
    Start-Sleep -Seconds 10
}
