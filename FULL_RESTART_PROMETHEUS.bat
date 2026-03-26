@echo off
REM Full Prometheus System Restart
REM Stops all processes and starts fresh

echo ================================================================================
echo PROMETHEUS FULL SYSTEM RESTART
echo ================================================================================
echo.
echo This will:
echo   1. Stop all Prometheus processes
echo   2. Wait 5 seconds
echo   3. Start Prometheus in new terminal
echo   4. Start backend server in new terminal (optional)
echo.
echo Press any key to continue (or Ctrl+C to cancel)...
pause >nul

echo.
echo [1/4] Stopping existing Prometheus processes...
taskkill /F /FI "WINDOWTITLE eq *prometheus*" /T >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *launch_ultimate_prometheus*" /T >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *unified_production_server*" /T >nul 2>&1

echo [2/4] Waiting 5 seconds for cleanup...
timeout /t 5 /nobreak >nul

echo [3/4] Starting Prometheus Trading System...
start "Prometheus Trading System" powershell -NoExit -Command "cd '%~dp0'; Write-Host '================================================================================' -ForegroundColor Cyan; Write-Host 'PROMETHEUS ULTIMATE LIVE TRADING SYSTEM' -ForegroundColor Cyan; Write-Host '================================================================================' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Starting Prometheus...' -ForegroundColor Green; Write-Host ''; python launch_ultimate_prometheus_LIVE_TRADING.py"

echo [4/4] Starting Backend Server (optional)...
timeout /t 3 /nobreak >nul
start "Prometheus Backend Server" powershell -NoExit -Command "cd '%~dp0'; Write-Host '================================================================================' -ForegroundColor Magenta; Write-Host 'PROMETHEUS UNIFIED PRODUCTION SERVER' -ForegroundColor Magenta; Write-Host '================================================================================' -ForegroundColor Magenta; Write-Host ''; Write-Host 'Starting backend server...' -ForegroundColor Green; Write-Host ''; python unified_production_server.py"

echo.
echo ================================================================================
echo RESTART COMPLETE
echo ================================================================================
echo.
echo Prometheus has been started in new terminal windows.
echo.
echo Check the terminal windows for:
echo   - System initialization messages
echo   - Broker connection status (Alpaca and IB)
echo   - AI systems status
echo   - Trading cycle messages
echo.
echo Press any key to exit...
pause >nul

