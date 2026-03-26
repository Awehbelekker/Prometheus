@echo off
title PROMETHEUS AUTONOMOUS TRADING - LIVE + SHADOW
color 0A
chcp 65001 >nul

echo.
echo ============================================================================
echo     PROMETHEUS FULLY AUTONOMOUS TRADING SYSTEM
echo     Live Trading + Parallel Shadow Trading + Full Learning
echo ============================================================================
echo.
echo Configuration:
echo   - Mode: LIVE TRADING (Real Capital) + SHADOW TRADING (Comparison)
echo   - AI: DeepSeek Cloud API + OpenAI Fallback + 20+ AI Systems
echo   - Learning: Continuous Learning, AI Attribution, Pattern Recognition
echo   - Logging: Database + File Logs
echo.
echo ============================================================================
echo.

cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

:: Create logs directory if not exists
if not exist "logs" mkdir logs

:: Set timestamp for log files
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

echo Starting PROMETHEUS Autonomous System...
echo Log file: logs\prometheus_autonomous_%TIMESTAMP%.log
echo.

:: Launch the main autonomous trading script in a new window
:: Note: Output is logged internally by the Python script
start "PROMETHEUS AUTONOMOUS" cmd /k "python prometheus_autonomous_launcher.py"

echo ============================================================================
echo.
echo PROMETHEUS LAUNCHED SUCCESSFULLY!
echo.
echo Monitor:
echo   - Window: "PROMETHEUS AUTONOMOUS" (minimized)
echo   - Log: logs\prometheus_autonomous_%TIMESTAMP%.log
echo.
echo To stop: 
echo   - Run STOP_PROMETHEUS.bat
echo   - Or press Ctrl+C in the PROMETHEUS window
echo.
echo ============================================================================
echo.
echo Press any key to close this launcher (PROMETHEUS continues running)...
pause >nul

