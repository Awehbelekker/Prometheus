@echo off
title PROMETHEUS Live Trading System
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "PROMETHEUS_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PROMETHEUS_PYTHON%" set "PROMETHEUS_PYTHON=python"

echo ============================================
echo   PROMETHEUS LIVE TRADING SYSTEM
echo ============================================
echo.
echo   Alpaca LIVE: Account %ALPACA_ACCOUNT_ID%
echo   IB Gateway:  Account %IB_ACCOUNT%
echo   AI Models:   DeepSeek-R1, Qwen2.5, Llama3.1
echo.
echo   Starting live trading...
echo   Press Ctrl+C to stop
echo.
echo ============================================

"%PROMETHEUS_PYTHON%" launch_prometheus_live.py

echo.
echo Trading stopped.
pause
