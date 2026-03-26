@echo off
SETLOCAL EnableDelayedExpansion

REM ================================================================================
REM PROMETHEUS COMPLETE SYSTEM RELAUNCH
REM Handles: IB Gateway restart, process cleanup, and full system startup
REM ================================================================================

TITLE PROMETHEUS Complete System Relaunch

echo.
echo ================================================================================
echo     PROMETHEUS COMPLETE SYSTEM RELAUNCH
echo     Time: %date% %time%
echo ================================================================================
echo.
echo This script will:
echo   1. Stop ALL Python processes related to PROMETHEUS
echo   2. Wait for cleanup
echo   3. Start the PROMETHEUS Trading System in an external terminal
echo   4. Start the Backend Server in an external terminal  
echo   5. Start the Frontend (port 3002)
echo.
echo IMPORTANT: Please manually restart IB Gateway BEFORE running this script
echo            to clear stale API connections!
echo.
echo Press any key to continue (or Ctrl+C to cancel)...
pause >nul

echo.
echo [Step 1/6] Stopping ALL PROMETHEUS Python processes...
echo.

REM Kill specific PROMETHEUS processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Prometheus*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *prometheus*" 2>nul

REM Find and kill unified_production_server
for /f "tokens=2" %%a in ('tasklist /v /fi "imagename eq python.exe" ^| findstr /i "unified_production_server"') do (
    echo Killing PID %%a (unified_production_server)
    taskkill /F /PID %%a 2>nul
)

REM Find and kill launch_ultimate_prometheus
for /f "tokens=2" %%a in ('tasklist /v /fi "imagename eq python.exe" ^| findstr /i "launch_ultimate_prometheus"') do (
    echo Killing PID %%a (launch_ultimate_prometheus)
    taskkill /F /PID %%a 2>nul
)

echo.
echo [Step 2/6] Waiting 5 seconds for process cleanup...
timeout /t 5 /nobreak >nul

echo.
echo [Step 3/6] Checking IB Gateway port 4002...
netstat -ano | findstr ":4002" | findstr "LISTENING"
if %ERRORLEVEL% EQU 0 (
    echo    IB Gateway detected on port 4002 - OK
) else (
    echo    WARNING: IB Gateway NOT detected on port 4002!
    echo    Please start IB Gateway and enable API before continuing.
    echo.
    echo    Press any key when IB Gateway is ready...
    pause >nul
)

echo.
echo [Step 4/6] Starting PROMETHEUS Trading System in new terminal...
cd /d "%~dp0"
start "PROMETHEUS Trading System" cmd /k "cd /d "%~dp0" && color 0A && echo ================================================================================ && echo PROMETHEUS ULTIMATE LIVE TRADING SYSTEM && echo ================================================================================ && echo. && echo Starting with IB Gateway on port 4002... && echo Account: U21922116 && echo. && set IB_PORT=4002 && python launch_ultimate_prometheus_LIVE_TRADING.py"

timeout /t 3 /nobreak >nul

echo.
echo [Step 5/6] Starting PROMETHEUS Backend Server in new terminal...
start "PROMETHEUS Backend Server" cmd /k "cd /d "%~dp0" && color 0B && echo ================================================================================ && echo PROMETHEUS UNIFIED PRODUCTION SERVER && echo ================================================================================ && echo. && echo Starting backend on port 8000... && echo. && set IB_PORT=4002 && python unified_production_server.py"

timeout /t 5 /nobreak >nul

echo.
echo [Step 6/6] Starting Frontend on port 3002...
cd /d "%~dp0\frontend"
if exist "node_modules" (
    start "PROMETHEUS Frontend" cmd /k "cd /d "%~dp0frontend" && color 0E && echo ================================================================================ && echo PROMETHEUS FRONTEND && echo ================================================================================ && echo. && echo Starting frontend on port 3002... && echo. && npm run dev"
) else (
    echo    Frontend node_modules not found, skipping frontend startup.
    echo    You can manually start it later with: cd frontend ^&^& npm run dev
)

echo.
echo ================================================================================
echo     PROMETHEUS SYSTEM RELAUNCH COMPLETE!
echo ================================================================================
echo.
echo System Components Started:
echo   [1] Trading System   - New terminal window (Green)
echo   [2] Backend Server   - New terminal window (Blue) - Port 8000
echo   [3] Frontend         - New terminal window (Yellow) - Port 3002
echo.
echo IB Gateway Integration:
echo   - Port: 4002 (Gateway Live)
echo   - Account: U21922116
echo   - Positions: NOK, F, SIRI (will auto-manage when market opens)
echo.
echo Access Points:
echo   - Frontend:    http://localhost:3002
echo   - Backend API: http://localhost:8000
echo   - API Health:  http://localhost:8000/health
echo.
echo You can now CLOSE this window and VS Code.
echo The trading system will continue running in the external terminals.
echo.
echo Press any key to exit this launcher...
pause >nul

