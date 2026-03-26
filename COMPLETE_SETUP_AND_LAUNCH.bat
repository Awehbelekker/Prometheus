@echo off
REM ============================================================================
REM COMPLETE PROMETHEUS SETUP AND LAUNCH
REM Full setup: Visual AI + Historical Training + Launch
REM ============================================================================

title PROMETHEUS Complete Setup

echo.
echo ============================================================================
echo PROMETHEUS COMPLETE SETUP AND LAUNCH
echo ============================================================================
echo.
echo This will:
echo   1. Install all dependencies
echo   2. Set up LLaVA Visual AI (~4GB download)
echo   3. Train on historical data (1-3 hours)
echo   4. Launch PROMETHEUS with all systems
echo.
echo Total time: 2-4 hours (mostly automated)
echo.
echo Recommended: Run overnight or during non-trading hours
echo.
echo ============================================================================
echo.

set /p continue="Continue with complete setup? (y/n): "
if /i not "%continue%"=="y" (
    echo Setup cancelled.
    pause
    exit /b 0
)

cd /d "%~dp0"

echo.
echo ============================================================================
echo [1/4] INSTALLING DEPENDENCIES
echo ============================================================================
echo.

pip install matplotlib mplfinance pandas numpy requests ollama

echo.
echo ============================================================================
echo [2/4] SETTING UP VISUAL AI (LLaVA)
echo ============================================================================
echo.

python setup_llava_system.py

if errorlevel 1 (
    echo.
    echo [WARNING] Visual AI setup had issues
    echo System can still run without Visual AI
    echo.
    set /p skip="Continue without Visual AI? (y/n): "
    if /i not "%skip%"=="y" (
        echo Setup cancelled.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================================
echo [3/4] TRAINING ON HISTORICAL DATA
echo ============================================================================
echo.
echo This will take 1-3 hours...
echo You can skip this and train later if needed.
echo.

set /p train="Train on historical data now? (y/n): "
if /i "%train%"=="y" (
    python train_llava_historical.py
) else (
    echo Skipping historical training
    echo You can run later: python train_llava_historical.py
)

echo.
echo ============================================================================
echo [4/4] LAUNCHING PROMETHEUS
echo ============================================================================
echo.

python test_visual_analysis.py

echo.
echo ============================================================================
echo LAUNCHING ULTIMATE SYSTEM
echo ============================================================================
echo.
echo All systems ready!
echo Press any key to start LIVE TRADING...
echo.

pause

set IB_PORT=4002
python LAUNCH_ULTIMATE_PROMETHEUS_50M.py

pause
