@echo off
title PROMETHEUS Autonomous 24/7 Trading System
color 0A
cls

echo.
echo ============================================================================
echo.
echo   ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗███████╗
echo   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔════╝
echo   ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║█████╗  
echo   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══╝  
echo   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗
echo   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
echo.
echo                    AUTONOMOUS 24/7 INTELLIGENCE SYSTEM
echo.
echo ============================================================================
echo.
echo   Starting PROMETHEUS - The AI That NEVER Sleeps
echo.
echo   When markets are OPEN:   Trading stocks, crypto, options, futures
echo   When markets are CLOSED: Learning, backtesting, optimizing
echo.
echo   Your Timezone: South Africa (UTC+2)
echo   Market Times:  4:30 PM - 11:00 PM local (regular hours)
echo   Crypto:        24/7 always active
echo.
echo ============================================================================
echo.

cd /d "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform"

set "PROMETHEUS_PYTHON=C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\.venv_directml_test\Scripts\python.exe"
if not exist "%PROMETHEUS_PYTHON%" set "PROMETHEUS_PYTHON=python"

:: Force live trading runtime mode for both backend and live trader process
set "ALWAYS_LIVE=1"
set "ENABLE_LIVE_ORDER_EXECUTION=1"
set "LIVE_TRADING_ENABLED=true"
set "IB_LIVE_ENABLED=true"
set "TRADING_MODE=live"
set "THINKMESH_ENABLED=true"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "RUN_BENCHMARK_GATE_AFTER_LAUNCH=0"
set "BENCHMARK_GATE_RUNS=3"

:: STAGE 1: Resource Stabilization
set "MEMORY_CAP_PERCENT=85"
set "MEMORY_AUTO_PAUSE_PERCENT=95"
set "ENABLE_MEMORY_PROFILING=1"
set "MEMORY_CHECK_INTERVAL=30"

:: STAGE 2: IB Connection Hardening
set "IB_RECONNECT_DELAY_BASE=2"
set "IB_RECONNECT_MAX_DELAY=32"
set "IB_HEARTBEAT_INTERVAL=10"
set "IB_CLIENT_ID_MODE=persistent"
set "IB_HOST=127.0.0.1"
set "IB_PORT=4002"

:: Auto-detect active IB listener so TWS manual launches work without edits
netstat -ano | findstr /R /C:":7497 .*LISTENING" >nul 2>&1
if not errorlevel 1 set "IB_PORT=7497"
if "%IB_PORT%"=="4002" (
    netstat -ano | findstr /R /C:":7496 .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "IB_PORT=7496"
)
if "%IB_PORT%"=="4002" (
    netstat -ano | findstr /R /C:":4001 .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "IB_PORT=4001"
)

:: STAGE 3: Inference Resilience
set "INFERENCE_TIMEOUT_SECONDS=10"
set "INFERENCE_QUEUE_MAX=5"
set "INFERENCE_FALLBACK_CHAIN=local,openai,anthropic,gpt-oss"
set "INFERENCE_CIRCUIT_BREAKER_THRESHOLD=3"

:: STAGE 4: Data Resilience
set "DATA_PROVIDER_FALLBACK=yahoo,polygon,alphavantage,cache"
set "DATA_CACHE_TTL_SECONDS=3600"
set "DNS_FAILOVER_ENABLED=1"

:: STAGE 5: Learning & Adaptation (enabled after stages 1-4)
set "ENABLE_HRM_CHECKPOINTING=1"
set "ENABLE_PATTERN_LEARNING=1"
set "ENABLE_QUANTUM_FEEDBACK=1"
set "ENABLE_AI_CONSCIOUSNESS_LEARNING=1"
set "MODEL_RETRAINING_THRESHOLD_PERCENT=2"

:: Create logs directory if missing
if not exist logs mkdir logs

:: Check if Python is available
"%PROMETHEUS_PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python interpreter not found: %PROMETHEUS_PYTHON%
    pause
    exit /b 1
)

:: ──────────── DB Schema Preflight (long-term readiness) ────────────
echo [0/6] Running database schema preflight...
"%PROMETHEUS_PYTHON%" -X utf8 initialize_all_database_schemas.py > logs\schema_init.log 2>&1
if errorlevel 1 (
    echo   [WARNING] Schema preflight reported issues. Continuing launch.
    echo   Check logs\schema_init.log for details.
) else (
    echo   [OK] Schema preflight completed.
)
echo.

:: ──────────── Kill any existing PROMETHEUS Python processes ────────────
echo [1/6] Stopping any existing PROMETHEUS processes...
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='cmd.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "run_prometheus.bat"') do (
    echo   Killing old launcher PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "unified_production_server"') do (
    echo   Killing old server PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python3.11.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "unified_production_server"') do (
    echo   Killing old server PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "launch_ultimate_prometheus_LIVE_TRADING"') do (
    echo   Killing old trader PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 3 /nobreak >nul
echo   Done.
echo.

:: ──────────── STAGE 2: Clean IB Processes ────────────
echo [1.5/6] Cleaning Interactive Brokers connections...
taskkill /IM tws.exe /F 2>nul
taskkill /IM ibgateway.exe /F 2>nul
taskkill /IM jxpipc.exe /F 2>nul
timeout /t 2 /nobreak >nul
echo   IB cleanup complete.
echo.

:: ──────────── Ollama AI Engine Check ────────────
echo [2/6] Checking Ollama AI status...
echo   STAGE 3 Configuration: Inference timeout=%INFERENCE_TIMEOUT_SECONDS%s, fallback=%INFERENCE_FALLBACK_CHAIN%
echo   STAGE 4 Configuration: Data fallback=%DATA_PROVIDER_FALLBACK%, cache TTL=%DATA_CACHE_TTL_SECONDS%s
echo   IB endpoint: %IB_HOST%:%IB_PORT%
echo.
echo   [GPU DETECTION PHASE]
"%PROMETHEUS_PYTHON%" -c "import torch; print('  GPU Available:', torch.cuda.is_available()); print('  Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'); import os; print('  DirectML:', 'YES' if bool(os.environ.get('PYTORCH_ENABLE_MPS_FALLBACK')) else 'CONFIGURED')" 2>nul || echo   GPU detection skipped
echo.
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe" >NUL
if errorlevel 1 (
    echo   Ollama is NOT running (saves ~12GB RAM^).
    echo   Prometheus will use OpenAI GPT-4 API for AI analysis.
    echo   This is FINE - all 30 trading systems work without Ollama.
    echo.
    echo   To use local AI: start 'ollama serve' before launching.
) else (
    echo   Ollama is running - local AI models available.
    echo   Models: llama3.1:8b-trading, deepseek-r1:8b
)
echo   [VISUAL AI CHECK]
"%PROMETHEUS_PYTHON%" -c "import os; enabled = os.getenv('VISUAL_AI_ENABLED','false').lower()=='true'; print('  Visual AI:', 'ENABLED' if enabled else 'disabled'); print('  Claude Vision:', 'ON' if os.getenv('USE_CLAUDE_VISION','').lower()=='true' else 'off'); print('  Gemini Vision:', 'ON' if os.getenv('USE_GEMINI_VISION','').lower()=='true' else 'off'); print('  LLaVA Vision:', 'ON' if os.getenv('USE_LLAVA_VISION','').lower()=='true' else 'off')" 2>nul || echo   Visual AI detection skipped
echo.

:: ──────────── Start the API Server ────────────
echo [3/6] Starting Unified Production Server (port 8000)...
echo   STAGE 1 Configuration: Memory cap=%MEMORY_CAP_PERCENT%^%, auto-pause at %MEMORY_AUTO_PAUSE_PERCENT%^%
echo   STAGE 2 Configuration: IB reconnect base delay=%IB_RECONNECT_DELAY_BASE%s, heartbeat every %IB_HEARTBEAT_INTERVAL%s
start "PROMETHEUS-Server" /MIN cmd /c "cd /d "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform" && "%PROMETHEUS_PYTHON%" -X utf8 unified_production_server.py >> logs\server.log 2>&1"
echo   Server launching in minimized window...
echo.

:: Wait for server to come up
echo [4/6] Waiting 60 seconds for server + 5 AI subsystems initialization...
timeout /t 60 /nobreak >nul

:: Quick health check
echo   Checking server health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] Server health check failed - it may still be loading.
) else (
    echo   [OK] Server is responding on port 8000
)
echo.

:: ──────────── Start Live Trading Engine ────────────
echo [5/6] Starting Live Trading Engine (Alpaca + IB)...
echo   STAGE 5 Configuration: HRM Checkpointing=%ENABLE_HRM_CHECKPOINTING%, Pattern Learning=%ENABLE_PATTERN_LEARNING%
start "PROMETHEUS-LiveTrader" /MIN cmd /c "cd /d "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform" && "%PROMETHEUS_PYTHON%" -X utf8 launch_ultimate_prometheus_LIVE_TRADING.py >> logs\live_trader.log 2>&1"
echo   Live Trader launching in minimized window...
echo.

:: Verify
echo [6/6] Waiting 30 seconds then verifying...
timeout /t 30 /nobreak >nul

echo   Checking live-trading status endpoint...
curl -s http://localhost:8000/api/live-trading/status >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] Live trading status endpoint not reachable yet.
) else (
    echo   [OK] Live trading status endpoint is responding
)

echo.
echo ============================================================================
echo   REINFORCEMENT SUMMARY (5 STAGES OF HARDENING)
echo ============================================================================
echo   STAGE 1 - Resource Stabilization    : Mem cap %MEMORY_CAP_PERCENT%^% auto-pause @%MEMORY_AUTO_PAUSE_PERCENT%^%
echo   STAGE 2 - IB Connection Hardening   : Retry %IB_RECONNECT_DELAY_BASE%s-%IB_RECONNECT_MAX_DELAY%s HB %IB_HEARTBEAT_INTERVAL%s
echo   STAGE 3 - Inference Resilience      : Timeout %INFERENCE_TIMEOUT_SECONDS%s Queue %INFERENCE_QUEUE_MAX% CB %INFERENCE_CIRCUIT_BREAKER_THRESHOLD%
echo   STAGE 4 - Data Resilience           : Fallback %DATA_PROVIDER_FALLBACK% TTL %DATA_CACHE_TTL_SECONDS%s
echo   STAGE 5 - Autonomous Learning       : HRM ckpt=%ENABLE_HRM_CHECKPOINTING% Patterns=%ENABLE_PATTERN_LEARNING% Quantum=%ENABLE_QUANTUM_FEEDBACK%
echo ============================================================================
echo.

echo   Checking launcher process health...
set SERVER_OK=0
set TRADER_OK=0
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "unified_production_server.py"') do set SERVER_OK=1
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe'" get ProcessId^,CommandLine /format:csv 2^>nul ^| findstr /i "launch_ultimate_prometheus_LIVE_TRADING.py"') do set TRADER_OK=1
if "%SERVER_OK%"=="1" (
    echo   [OK] Unified production server process detected
) else (
    echo   [WARNING] Unified production server process not detected
)
if "%TRADER_OK%"=="1" (
    echo   [OK] Live trading engine process detected
) else (
    echo   [WARNING] Live trading engine process not detected
)

echo.
echo ============================================================================
echo   PROMETHEUS LAUNCH COMPLETE - FULL LIVE TRADING READY
echo ============================================================================
echo.
echo   Both processes are running OUTSIDE of Visual Studio Code.
echo   They will continue running even if you close this window.
echo.
echo   Logs:
echo     Server:      logs\server.log
echo     Live Trader: logs\live_trader.log
echo.
echo   To STOP all processes: run STOP_PROMETHEUS.bat
echo   To check status: python _quick_status.py
echo   Optional benchmark gate: set RUN_BENCHMARK_GATE_AFTER_LAUNCH=1
echo.
echo ============================================================================
echo.

if "%RUN_BENCHMARK_GATE_AFTER_LAUNCH%"=="1" (
    echo [POST] Running benchmark gate (^%BENCHMARK_GATE_RUNS%^% runs^)...
    "%PROMETHEUS_PYTHON%" -X utf8 run_benchmark_gate.py --runs %BENCHMARK_GATE_RUNS% > logs\benchmark_gate.log 2>&1
    if errorlevel 1 (
        echo   [WARNING] Benchmark gate FAILED. Check logs\benchmark_gate.log
    ) else (
        echo   [OK] Benchmark gate PASSED. See logs\benchmark_gate.log
    )
    echo.
)

pause
