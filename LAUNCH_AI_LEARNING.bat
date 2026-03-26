@echo off
REM ============================================================================
REM PROMETHEUS WITH AI LEARNING & SELF-HEALING
REM ============================================================================

title PROMETHEUS AI Learning Edition

REM Set IB port (4002 for IB Gateway paper, 7496 for TWS live)
set IB_PORT=4002

echo.
echo ============================================================================
echo PROMETHEUS - AI LEARNING EDITION
echo ============================================================================
echo.
echo Features:
echo   - Continuous Learning (learns from every trade)
echo   - AI Pattern Recognition
echo   - Self-Healing Systems
echo   - Adaptive Strategy Optimization
echo   - Dual-Broker Support (Alpaca + IB)
echo.
echo Starting...
echo Press Ctrl+C anytime to stop safely
echo.
echo ============================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Run the enhanced trading system
python START_WITH_AI_LEARNING.py

REM Keep window open if error occurs
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR OCCURRED - Check above for details
    echo ============================================================================
    echo.
    pause
)
