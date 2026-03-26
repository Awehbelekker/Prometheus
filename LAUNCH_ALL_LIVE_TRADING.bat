@echo off
REM PROMETHEUS LIVE TRADING LAUNCHER - Batch Version
REM Launches all trading systems with LIVE mode enabled on both brokers

echo ======================================================
echo   PROMETHEUS LIVE TRADING LAUNCHER
echo   Starting all trading systems with LIVE mode enabled
echo ======================================================
echo.

REM Set environment variables for LIVE trading
set ALWAYS_LIVE=1
set ENABLE_LIVE_ORDER_EXECUTION=1
set IB_LIVE_ENABLED=true
set IB_PORT=4002

echo [LIVE] Environment variables set:
echo   ALWAYS_LIVE = %ALWAYS_LIVE%
echo   ENABLE_LIVE_ORDER_EXECUTION = %ENABLE_LIVE_ORDER_EXECUTION%
echo   IB_LIVE_ENABLED = %IB_LIVE_ENABLED%
echo   IB_PORT = %IB_PORT%
echo.

REM Launch unified production server (main backend on port 8000)
echo [1/4] Starting Unified Production Server (port 8000)...
start "PROMETHEUS-Backend-8000" cmd /k "cd /d %~dp0 && set ALWAYS_LIVE=1 && set ENABLE_LIVE_ORDER_EXECUTION=1 && set IB_LIVE_ENABLED=true && set IB_PORT=4002 && python unified_production_server.py"

REM Wait for backend to initialize
timeout /t 5 /nobreak > nul

REM Launch Ultimate Prometheus Live Trading System
echo [2/4] Starting Ultimate Prometheus Live Trading System...
start "PROMETHEUS-Live-Trading" cmd /k "cd /d %~dp0 && set ALWAYS_LIVE=1 && set ENABLE_LIVE_ORDER_EXECUTION=1 && python launch_ultimate_prometheus_LIVE_TRADING.py"

REM Wait a moment
timeout /t 2 /nobreak > nul

REM Launch IB Live Trading Service (port 8001)
echo [3/4] Starting IB Live Trading Service (port 8001)...
start "PROMETHEUS-IB-8001" cmd /k "cd /d %~dp0 && set IB_LIVE_ENABLED=true && set IB_PORT=4002 && python ib_live_trading_service.py"

REM Wait a moment
timeout /t 2 /nobreak > nul

REM Launch Parallel Shadow Trading System
echo [4/4] Starting Parallel Shadow Trading System...
start "PROMETHEUS-Shadow-Trading" cmd /k "cd /d %~dp0 && python parallel_shadow_trading.py"

echo.
echo ======================================================
echo   ALL SYSTEMS LAUNCHED!
echo ======================================================
echo.
echo Services running:
echo   - Unified Production Server: http://localhost:8000
echo   - IB Live Trading Service:   http://localhost:8001
echo   - Live Trading Engine:       Running in separate window
echo   - Shadow Trading System:     Running in separate window
echo.
echo Trading Mode: LIVE (REAL MONEY)
echo Brokers: Alpaca (Live) + Interactive Brokers (Live)
echo.
echo Close this window or press any key to exit this launcher...
pause > nul

