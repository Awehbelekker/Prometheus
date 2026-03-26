@echo off
:: ============================================================================
:: PROMETHEUS AUTO-START INSTALLER
:: ============================================================================
:: This script creates Windows Scheduled Tasks to ensure PROMETHEUS
:: never misses a trading opportunity.
::
:: Tasks Created:
:: 1. Pre-Market Scan (4:00 PM local = 9:00 AM ET) - 30 min before market
:: 2. Market Open Alert (4:30 PM local = 9:30 AM ET)
:: 3. Market Close Alert (11:00 PM local = 4:00 PM ET)
:: ============================================================================

echo.
echo ============================================================
echo   PROMETHEUS AUTO-START INSTALLER
echo ============================================================
echo.

:: Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [1/4] Creating Pre-Market Scan Task (4:00 PM local / 9:00 AM ET)...
schtasks /create /tn "PROMETHEUS_PreMarket" /tr "python \"%SCRIPT_DIR%launch_prometheus_live.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 16:00 /f >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Pre-Market task created
) else (
    echo       [SKIP] Task may already exist or requires admin
)

echo.
echo [2/4] Creating Market Open Alert Task (4:30 PM local / 9:30 AM ET)...
schtasks /create /tn "PROMETHEUS_MarketOpen" /tr "msg * \"PROMETHEUS: US Market is NOW OPEN!\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 16:30 /f >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Market Open alert created
) else (
    echo       [SKIP] Task may already exist
)

echo.
echo [3/4] Creating Market Close Warning (10:45 PM local / 3:45 PM ET)...
schtasks /create /tn "PROMETHEUS_MarketCloseWarning" /tr "msg * \"PROMETHEUS: Market closes in 15 minutes!\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 22:45 /f >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Market Close warning created
) else (
    echo       [SKIP] Task may already exist
)

echo.
echo [4/4] Verifying scheduled tasks...
echo.
echo   Installed PROMETHEUS Tasks:
schtasks /query /tn "PROMETHEUS_PreMarket" 2>nul | findstr "PROMETHEUS"
schtasks /query /tn "PROMETHEUS_MarketOpen" 2>nul | findstr "PROMETHEUS"
schtasks /query /tn "PROMETHEUS_MarketCloseWarning" 2>nul | findstr "PROMETHEUS"

echo.
echo ============================================================
echo   INSTALLATION COMPLETE!
echo ============================================================
echo.
echo   Your Local Trading Schedule (South Africa Time):
echo.
echo   [4:00 PM]  Pre-Market scan starts (PROMETHEUS launches)
echo   [4:30 PM]  Regular market opens - Alert notification
echo   [10:45 PM] Market close warning - 15 min left
echo   [11:00 PM] Regular market closes
echo.
echo   PROMETHEUS will auto-start every weekday at 4:00 PM
echo   to catch pre-market opportunities!
echo.
echo   To remove tasks: schtasks /delete /tn "PROMETHEUS_*" /f
echo ============================================================
echo.
pause
