@echo off
REM ============================================================================
REM LAUNCH PROMETHEUS WITH VISUAL AI
REM Quick launcher that checks Visual AI status
REM ============================================================================

title PROMETHEUS with Visual AI

cd /d "%~dp0"

echo.
echo ============================================================================
echo PROMETHEUS - LAUNCHING WITH VISUAL AI
echo ============================================================================
echo.

REM Check if LLaVA is set up
echo Checking Visual AI status...
echo.

python -c "from core.multimodal_analyzer import MultimodalChartAnalyzer; a = MultimodalChartAnalyzer(); print('[OK] Visual AI available' if a.model_available else '[WARNING] Visual AI not available')"

echo.
echo If Visual AI not available, run: SETUP_VISUAL_AI_COMPLETE.bat
echo.
echo ============================================================================
echo.

pause

REM Set IB port
set IB_PORT=4002

REM Launch with Visual AI
python LAUNCH_ULTIMATE_PROMETHEUS_50M.py

pause
