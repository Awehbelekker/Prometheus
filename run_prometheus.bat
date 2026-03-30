@echo off
title PROMETHEUS Trading Platform
cd /d "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform"

set "PROMETHEUS_PYTHON=C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\.venv_directml_test\Scripts\python.exe"
if not exist "%PROMETHEUS_PYTHON%" set "PROMETHEUS_PYTHON=C:\Users\Judy\AppData\Local\Programs\Python\Python313\python.exe"

echo ================================================================
echo   PROMETHEUS Trading Platform Launcher
echo   Mode: LIVE output (use "quiet" arg for log-only)
echo ================================================================
echo.

:: ---- Ollama GPU Environment ----
set OLLAMA_VULKAN=1
set OLLAMA_KEEP_ALIVE=30m
set "HIP_VISIBLE_DEVICES="
set "HSA_OVERRIDE_GFX_VERSION="
set "ROCR_VISIBLE_DEVICES="

:: ---- Check if Ollama is already running ----
set OLLAMA_RUNNING=0
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"') do set OLLAMA_RUNNING=1

if "%OLLAMA_RUNNING%"=="1" (
    echo [%date% %time%] Ollama already running on port 11434.
) else (
    echo [%date% %time%] Starting Ollama with Vulkan GPU acceleration...
    start "" "C:\Users\Judy\AppData\Local\Programs\Ollama\ollama.exe" serve
    echo [%date% %time%] Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
)

:: ---- Pre-load the trading AI model ----
echo [%date% %time%] Pre-loading AI model (llama3.1:8b-trading)...
echo [%date% %time%] This may take up to 60 seconds on first load...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:11434/api/generate' -Method POST -Body '{\"model\":\"llama3.1:8b-trading\",\"prompt\":\"ready\",\"stream\":false}' -ContentType 'application/json' -TimeoutSec 90 -UseBasicParsing -ErrorAction Stop; Write-Host 'AI model loaded successfully.' } catch { Write-Host 'WARNING: Model pre-load failed. PROMETHEUS will load it on first use.' }"
echo.

:: ---- Wait for IB Gateway to be reachable (non-blocking — just logs if not up) ----
:: IB Gateway must be manually logged in after a reboot. We poll here so that
:: the server starts AND the trading system inside it can connect to IB on first try.
echo [%date% %time%] Checking IB Gateway on 127.0.0.1:4002...
set IB_READY=0
for /f %%R in ('powershell -NoProfile -Command "try { $t = New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',4002); $t.Close(); Write-Host 1 } catch { Write-Host 0 }"') do set IB_READY=%%R

if "%IB_READY%"=="1" (
    echo [%date% %time%] IB Gateway is UP and reachable.
) else (
    echo [%date% %time%] IB Gateway not detected on port 4002.
    echo [%date% %time%] --> If you want IB trading: open IB Gateway and log in now.
    echo [%date% %time%] --> PROMETHEUS will start anyway and use Alpaca until IB comes up.
    echo [%date% %time%] Continuing in 10 seconds...
    timeout /t 10 /nobreak >nul
)
echo.

:: ---- Check if PROMETHEUS is already running ----
:loop
set PORT_OWNER=
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"') do set PORT_OWNER=%%P
if not "%PORT_OWNER%"=="" (
    echo [%date% %time%] Port 8000 already in use by PID %PORT_OWNER%. PROMETHEUS is already running.
    echo [%date% %time%] Port 8000 already in use by PID %PORT_OWNER%. PROMETHEUS is already running. >> prometheus_restart.log
    echo.
    echo   Dashboard: http://127.0.0.1:8000/admin-dashboard
    echo.
    if /I not "%~1"=="quiet" pause
    exit /b 0
)

echo [%date% %time%] Starting PROMETHEUS...
echo [%date% %time%] Starting PROMETHEUS... >> prometheus_restart.log

:: ALWAYS redirect stdout/stderr to log files to prevent Windows Console
:: QuickEdit freeze (clicking in console window blocks all stdout writes,
:: which deadlocks the entire Python async event loop).
echo [%date% %time%] Output logged to: prometheus_server.log + prometheus_server_err.log
echo [%date% %time%] Tail the log:  powershell Get-Content prometheus_server_err.log -Tail 20 -Wait
echo.

start /b "" "%PROMETHEUS_PYTHON%" unified_production_server.py >> prometheus_server.log 2>> prometheus_server_err.log

:: Wait for server to bind port 8000 (up to 5 minutes)
echo [%date% %time%] Waiting for server to start on port 8000...
set /a WAIT_COUNT=0
:wait_port
set PORT_READY=
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"') do set PORT_READY=%%P
if "%PORT_READY%"=="" goto wait_increment

:: Server is UP - print once and go to silent monitor
echo [%date% %time%] PROMETHEUS is UP on port 8000 - PID %PORT_READY%
echo.
echo   Dashboard: http://127.0.0.1:8000/admin-dashboard
echo   Logs:      prometheus_server.log / prometheus_server_err.log
echo.
goto monitor

:wait_increment
set /a WAIT_COUNT+=1
if %WAIT_COUNT% GEQ 60 goto wait_timeout
timeout /t 5 /nobreak >nul
goto wait_port

:wait_timeout
echo [%date% %time%] ERROR: Server did not start within 5 minutes.
goto restart

:: Monitor: silently check every 60s, restart if server dies
:monitor
timeout /t 60 /nobreak >nul
set PORT_ALIVE=
for /f %%P in ('powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"') do set PORT_ALIVE=%%P
if not "%PORT_ALIVE%"=="" goto monitor

:restart
echo [%date% %time%] PROMETHEUS stopped. Restarting in 10s...
echo [%date% %time%] PROMETHEUS stopped. Restarting in 10s... >> prometheus_restart.log
timeout /t 10 >nul
:: Re-check IB on each restart so we log its state
echo [%date% %time%] Re-checking IB Gateway before restart...
set IB_READY=0
for /f %%R in ('powershell -NoProfile -Command "try { $t = New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',4002); $t.Close(); Write-Host 1 } catch { Write-Host 0 }"') do set IB_READY=%%R
if "%IB_READY%"=="1" (
    echo [%date% %time%] IB Gateway is UP.
) else (
    echo [%date% %time%] IB Gateway is DOWN - trading will run Alpaca-only until you log in.
)
goto loop
