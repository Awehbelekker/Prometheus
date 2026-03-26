@echo off
title STOP PROMETHEUS
color 0C

echo.
echo ============================================================================
echo     STOPPING PROMETHEUS TRADING SYSTEM
echo ============================================================================
echo.

:: Find and kill Python processes running PROMETHEUS scripts
echo Looking for PROMETHEUS processes...

:: Kill specific PROMETHEUS scripts
taskkill /F /FI "WINDOWTITLE eq PROMETHEUS*" 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *prometheus*" 2>nul

:: More targeted kill for our specific scripts
wmic process where "name='python.exe' and commandline like '%%unified_production_server%%'" delete 2>nul
wmic process where "name='python.exe' and commandline like '%%launch_ultimate_prometheus_LIVE_TRADING%%'" delete 2>nul
wmic process where "name='python.exe' and commandline like '%%prometheus%%'" delete 2>nul
wmic process where "name='python.exe' and commandline like '%%parallel_shadow%%'" delete 2>nul
wmic process where "name='python.exe' and commandline like '%%active_trading%%'" delete 2>nul

echo.
echo ============================================================================
echo PROMETHEUS STOPPED
echo ============================================================================
echo.
echo All PROMETHEUS trading processes have been terminated.
echo.
echo Press any key to close...
pause >nul

