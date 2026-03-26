@echo off
REM ============================================================================
REM PROMETHEUS LIVE TRADING LAUNCHER
REM External launch script - runs outside Cursor
REM ============================================================================

title PROMETHEUS Live Trading System

echo.
echo ============================================================================
echo PROMETHEUS AUTONOMOUS TRADING SYSTEM
echo ============================================================================
echo.
echo Starting live trading with real money...
echo Press Ctrl+C anytime to stop safely
echo.
echo ============================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Run the trading system
python START_LIVE_TRADING_NOW.py

REM Keep window open if error occurs
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR OCCURRED - Check above for details
    echo ============================================================================
    echo.
    pause
)
