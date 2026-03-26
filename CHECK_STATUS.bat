@echo off
title PROMETHEUS Status Check
cd /d "%~dp0"
python CHECK_TRADING_STATUS.py
pause
