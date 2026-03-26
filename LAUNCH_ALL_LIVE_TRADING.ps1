# PROMETHEUS LIVE TRADING LAUNCHER
# Launches all trading systems with LIVE mode enabled on both brokers

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  PROMETHEUS LIVE TRADING LAUNCHER" -ForegroundColor Yellow
Write-Host "  Starting all trading systems with LIVE mode enabled" -ForegroundColor Yellow  
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for LIVE trading
$env:ALWAYS_LIVE = "1"
$env:ENABLE_LIVE_ORDER_EXECUTION = "1"
$env:IB_LIVE_ENABLED = "true"
$env:IB_PORT = "4002"

Write-Host "[LIVE] Environment variables set:" -ForegroundColor Green
Write-Host "  ALWAYS_LIVE = $env:ALWAYS_LIVE" -ForegroundColor White
Write-Host "  ENABLE_LIVE_ORDER_EXECUTION = $env:ENABLE_LIVE_ORDER_EXECUTION" -ForegroundColor White
Write-Host "  IB_LIVE_ENABLED = $env:IB_LIVE_ENABLED" -ForegroundColor White
Write-Host "  IB_PORT = $env:IB_PORT" -ForegroundColor White
Write-Host ""

# Check if IB Gateway is running on port 4002
Write-Host "[CHECK] Checking IB Gateway connection on port 4002..." -ForegroundColor Yellow
$ibTest = Test-NetConnection -ComputerName 127.0.0.1 -Port 4002 -WarningAction SilentlyContinue
if ($ibTest.TcpTestSucceeded) {
    Write-Host "[OK] IB Gateway is accessible on port 4002" -ForegroundColor Green
} else {
    Write-Host "[WARN] IB Gateway not detected on port 4002. IB trading may not work." -ForegroundColor Red
}
Write-Host ""

# Launch unified production server (main backend on port 8000)
Write-Host "[1/4] Starting Unified Production Server (port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "unified_production_server.py" -WorkingDirectory $PWD -NoNewWindow

# Wait for backend to initialize
Start-Sleep -Seconds 5

# Launch Ultimate Prometheus Live Trading System
Write-Host "[2/4] Starting Ultimate Prometheus Live Trading System..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "launch_ultimate_prometheus_LIVE_TRADING.py" -WorkingDirectory $PWD -NoNewWindow

# Wait a moment
Start-Sleep -Seconds 2

# Launch IB Live Trading Service (port 8001)
Write-Host "[3/4] Starting IB Live Trading Service (port 8001)..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "ib_live_trading_service.py" -WorkingDirectory $PWD -NoNewWindow

# Wait a moment
Start-Sleep -Seconds 2

# Launch Parallel Shadow Trading System
Write-Host "[4/4] Starting Parallel Shadow Trading System..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "parallel_shadow_trading.py" -WorkingDirectory $PWD -NoNewWindow

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  ALL SYSTEMS LAUNCHED!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  - Unified Production Server: http://localhost:8000" -ForegroundColor White
Write-Host "  - IB Live Trading Service:   http://localhost:8001" -ForegroundColor White
Write-Host "  - Live Trading Engine:       Running in background" -ForegroundColor White
Write-Host "  - Shadow Trading System:     Running in background" -ForegroundColor White
Write-Host ""
Write-Host "Trading Mode: LIVE (REAL MONEY)" -ForegroundColor Red
Write-Host "Brokers: Alpaca (Live) + Interactive Brokers (Live)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop..." -ForegroundColor Gray

# Keep script running
while ($true) { Start-Sleep -Seconds 60 }

