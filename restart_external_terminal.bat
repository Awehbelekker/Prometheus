@echo off
REM Quick restart script - opens in external terminal
echo ================================================================================
echo PROMETHEUS TRADING SYSTEM - RESTART
echo ================================================================================
echo.
echo Stopping any running processes...
taskkill /F /FI "WINDOWTITLE eq Prometheus Trading System*" 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting Prometheus Trading System in new window...
echo.
start "Prometheus Trading System" /d "%~dp0" cmd /k "python launch_ultimate_prometheus_LIVE_TRADING.py"
echo.
echo ================================================================================
echo System starting in external terminal window
echo Look for window titled "Prometheus Trading System"
echo ================================================================================
pause


