@echo off
REM PROMETHEUS Market Hours Auto-Trader
REM Runs stock trading during US market hours (9:30 AM - 4:00 PM ET)
REM South Africa Time: 4:30 PM - 11:00 PM SAST

echo ============================================================
echo   PROMETHEUS MARKET HOURS TRADER
echo   Auto-started for US Stock Market Hours
echo ============================================================
echo.
echo Started at: %date% %time%
echo.

cd /d C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform

REM Set environment variables
set PYTHONIOENCODING=utf-8
set OLLAMA_MODELS=D:\Ollama\models

REM Log file for this session
set LOGFILE=logs\market_trading_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log

REM Create logs directory if needed
if not exist logs mkdir logs

echo Starting PROMETHEUS Dual Broker Trading...
echo Log file: %LOGFILE%
echo.

REM Run the trading system
python launch_prometheus_live.py --force 2>&1 | tee -a %LOGFILE%

echo.
echo Trading session ended at: %date% %time%
pause
