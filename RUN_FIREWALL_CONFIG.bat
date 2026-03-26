@echo off
REM Run Firewall Configuration as Administrator
REM This batch file will request admin privileges automatically

echo ================================================================================
echo PROMETHEUS FIREWALL CONFIGURATION
echo ================================================================================
echo.
echo This will configure Windows Firewall to allow:
echo   - Prometheus Trading Platform
echo   - Interactive Brokers Gateway/TWS
echo   - Alpaca API connections
echo.
echo Press any key to continue (or Ctrl+C to cancel)...
pause >nul

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
    python configure_firewall_exceptions.py
) else (
    echo [INFO] Requesting Administrator privileges...
    echo.
    REM Re-run as admin
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ================================================================================
echo CONFIGURATION COMPLETE
echo ================================================================================
echo.
echo Press any key to exit...
pause >nul

