@echo off
title PROMETHEUS LEARNING SYSTEMS
color 0B

echo ========================================================================
echo    PROMETHEUS LEARNING SYSTEMS LAUNCHER
echo ========================================================================
echo.
echo    This will start TWO background learning systems:
echo.
echo    1. VISUAL AI TRAINING - Train on 1,302 charts (2-3 hours)
echo    2. SCHOOL + PLAY - Continuous backtesting and evolution
echo.
echo    [OK] Live trading will CONTINUE running!
echo    [OK] These run in BACKGROUND - no interruption!
echo.
echo ========================================================================
echo.
pause

cd /d "%~dp0"

echo.
echo [1/2] Starting Visual AI Full Training...
start "Visual AI Training" cmd /k "python RUN_VISUAL_AI_FULL_TRAINING.py"

timeout /t 5 /nobreak > nul

echo [2/2] Starting School + Play Learning System...
start "School + Play" cmd /k "python PROMETHEUS_SCHOOL_AND_PLAY.py"

echo.
echo ========================================================================
echo.
echo    [OK] Both learning systems are now running!
echo.
echo    Visual AI Training: Window 1 (2-3 hours)
echo    School + Play: Window 2 (runs forever)
echo.
echo    Live trading continues in original window!
echo.
echo ========================================================================
echo.
pause
