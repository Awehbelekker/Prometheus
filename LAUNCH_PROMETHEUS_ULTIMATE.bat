@echo off
title PROMETHEUS ULTIMATE - THE LEADING TRADESMAN
color 0A

echo.
echo ======================================================================
echo     PROMETHEUS ULTIMATE - THE WORLD'S MOST PROFITABLE TRADING SYSTEM
echo ======================================================================
echo.
echo MISSION: Maximum Profitability Through Continuous Learning
echo.
echo Systems Starting:
echo   - Continuous Learning Engine
echo   - Strategy Evolution (Genetic Algorithm)
echo   - Market Regime Detection  
echo   - Kelly Position Sizing
echo   - Autonomous Trading Loop
echo.

cd /d "%~dp0"

:: Kill any existing Python processes
taskkill /F /IM python.exe 2>NUL
timeout /t 2 /nobreak >NUL

echo Starting Prometheus...
echo.

start "PROMETHEUS ULTIMATE" python PROMETHEUS_ULTIMATE_AUTONOMOUS.py

echo ======================================================================
echo PROMETHEUS LAUNCHED!
echo ======================================================================
echo.
echo Monitor progress:
echo   - Log file: prometheus_ultimate.log
echo   - Strategy data: ultimate_strategies.json
echo   - Run CHECK_PROMETHEUS_STATUS.bat for status
echo.
echo Press any key to exit this launcher (Prometheus continues running)...
pause >nul
