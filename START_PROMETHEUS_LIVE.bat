@echo off
title PROMETHEUS Live Trading System
cd /d C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform
set PYTHONIOENCODING=utf-8
set "PROMETHEUS_PYTHON=C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\.venv_directml_test\Scripts\python.exe"
if not exist "%PROMETHEUS_PYTHON%" set "PROMETHEUS_PYTHON=python"

echo ============================================
echo   PROMETHEUS LIVE TRADING SYSTEM
echo ============================================
echo.
echo   Alpaca LIVE: Account 910544927
echo   IB Gateway:  Account U21922116
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
