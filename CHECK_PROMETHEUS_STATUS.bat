@echo off
title PROMETHEUS STATUS CHECK
color 0A

echo.
echo ======================================================================
echo                    PROMETHEUS SYSTEM STATUS
echo ======================================================================
echo.

:: Check if running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I "python.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [RUNNING] Prometheus is ACTIVE
) else (
    echo [STOPPED] Prometheus is NOT running
)

echo.
echo Latest Learning Results:
echo ------------------------
if exist "ultimate_strategies.json" (
    powershell -Command "$d = Get-Content 'ultimate_strategies.json' | ConvertFrom-Json; $d.PSObject.Properties | ForEach-Object { $s = $_.Value; if ($s.total_trades -gt 0) { Write-Host ('  ' + $s.name.PadRight(25) + ' | Win: ' + [math]::Round($s.win_rate*100,1).ToString().PadLeft(5) + '%%  | Trades: ' + $s.total_trades) } } | Sort-Object -Descending | Select-Object -First 10"
)

echo.
echo Latest Log Entries:
echo -------------------
if exist "prometheus_ultimate.log" (
    powershell -Command "Get-Content 'prometheus_ultimate.log' -Tail 10"
) else if exist "ultimate_learning.log" (
    powershell -Command "Get-Content 'ultimate_learning.log' -Tail 10"
)

echo.
echo ======================================================================
echo Press any key to exit...
pause >nul
