@echo off
title PROMETHEUS Standalone Launcher
color 0A

echo ========================================
echo    PROMETHEUS STANDALONE LAUNCHER
echo ========================================
echo.
echo Checking system drives...
echo.

echo === Available Drives ===
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%d:\ (
        echo   [OK] %%d: drive found
    )
)

echo.
echo === D: Drive Contents ===
if exist D:\ (
    dir D:\ /b 2>nul
) else (
    echo D: drive not accessible
)

echo.
echo === Searching for GPT-OSS / AI Models ===
if exist D:\ (
    for /d %%f in (D:\*gpt*) do echo   Found: %%f
    for /d %%f in (D:\*GPT*) do echo   Found: %%f
    for /d %%f in (D:\*oss*) do echo   Found: %%f
    for /d %%f in (D:\*OSS*) do echo   Found: %%f
    for /d %%f in (D:\*llm*) do echo   Found: %%f
    for /d %%f in (D:\*LLM*) do echo   Found: %%f
    for /d %%f in (D:\*model*) do echo   Found: %%f
    for /d %%f in (D:\*Model*) do echo   Found: %%f
    for /d %%f in (D:\*ollama*) do echo   Found: %%f
    for /d %%f in (D:\*Ollama*) do echo   Found: %%f
    for /d %%f in (D:\*hugging*) do echo   Found: %%f
    for /d %%f in (D:\*Hugging*) do echo   Found: %%f
)

echo.
echo ========================================
echo Press any key to continue to AI Systems Check...
pause >nul

echo.
echo === Checking Ollama Models ===
ollama list 2>nul
if errorlevel 1 (
    echo Ollama not running
)

echo.
echo === PROMETHEUS AI Systems Status ===
cd /d C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform

python -c "
import sys
import os
sys.path.insert(0, '.')
os.environ['PROMETHEUS_QUIET'] = '1'

print()
print('Testing AI System Imports...')
print('-' * 40)

systems = [
    ('HRM Checkpoints', 'core.hierarchical_reasoning_machine'),
    ('Universal Reasoning', 'core.universal_reasoning_engine'),  
    ('Market Intelligence', 'core.market_intelligence_engine'),
    ('Meta Learning', 'core.meta_learning_optimizer'),
    ('Consciousness Core', 'core.consciousness_integration'),
    ('AI Trading', 'core.ai_trading_coordinator'),
    ('Pattern Recognizer', 'core.pattern_recognition_engine'),
    ('Multi-Agent', 'core.multi_agent_coordinator'),
    ('DRL Engine', 'core.drl_trading_engine'),
]

working = 0
for name, module in systems:
    try:
        __import__(module)
        print(f'  [OK] {name}')
        working += 1
    except Exception as e:
        print(f'  [X] {name}: {str(e)[:40]}')

print()
print(f'AI Systems: {working}/{len(systems)} operational')
print()
" 2>nul

echo.
echo ========================================
echo       PROMETHEUS TRADING LAUNCHER
echo ========================================
echo.
echo [1] Internal Paper Trading (Simulated - No Real Orders)
echo [2] DUAL BROKER LIVE TRADING (Alpaca + IB - REAL ORDERS!)
echo [3] Check All AI Functions
echo [4] Check Broker Status
echo [5] Exit
echo.
echo NOTE: Option 2 uses REAL MONEY with your connected brokers!
echo       Make sure IB Gateway is running for stock trades.
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting Internal Paper Trading (Simulated)...
    echo This does NOT connect to real brokers.
    echo.
    python prometheus_active_trading_session.py
)
if "%choice%"=="2" (
    echo.
    echo ==========================================
    echo WARNING: STARTING LIVE DUAL BROKER TRADING
    echo ==========================================
    echo.
    echo This will execute REAL ORDERS with:
    echo   - Alpaca (Crypto + Stocks) - LIVE MODE
    echo   - Interactive Brokers (Stocks) - LIVE MODE
    echo.
    echo Your account: IB Account U21922116
    echo Alpaca: LIVE (not paper)
    echo.
    set /p confirm="Type 'LIVE' to confirm: "
    if /i "%confirm%"=="LIVE" (
        echo.
        echo Starting Dual Broker Live Trading...
        python improved_dual_broker_trading.py
    ) else (
        echo Cancelled.
    )
)
if "%choice%"=="3" (
    echo Running AI Function Tests...
    python ai_systems_diagnostic.py
)
if "%choice%"=="4" (
    call CHECK_BROKER_STATUS.bat
)
if "%choice%"=="5" (
    echo Goodbye!
    exit
)

pause
