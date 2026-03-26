@echo off
title PROMETHEUS Live Trading - Debug Mode
cd /d "%~dp0"

echo.
echo ============================================================================
echo PROMETHEUS LIVE TRADING - DEBUG MODE
echo ============================================================================
echo.
echo Starting with detailed output...
echo If any errors occur, the window will stay open for review.
echo.
echo ============================================================================
echo.

python START_LIVE_TRADING_NOW.py

echo.
echo ============================================================================
echo Script ended - Press any key to close
echo ============================================================================
pause
