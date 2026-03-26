@echo off
title PROMETHEUS Visual AI Overnight Training
color 0A

echo.
echo ======================================================================
echo         PROMETHEUS VISUAL AI OVERNIGHT TRAINING
echo ======================================================================
echo.
echo This script trains Visual AI on 1,320+ charts
echo Best run overnight when markets are closed
echo.
echo Press Ctrl+C to cancel, or wait 10 seconds to start...
timeout /t 10

cd /d "%~dp0"
python VISUAL_AI_OVERNIGHT_TRAINING.py

echo.
echo Training complete! Check visual_ai_overnight.log for details.
pause
