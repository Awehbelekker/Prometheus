@echo off
REM ============================================================================
REM PROMETHEUS ULTIMATE SYSTEM - $50M VALUE DEMONSTRATION
REM ============================================================================

title PROMETHEUS ULTIMATE - $50M SYSTEM

REM Set IB port
set IB_PORT=4002

echo.
echo ============================================================================
echo PROMETHEUS ULTIMATE SYSTEM - $50M VALUE DEMONSTRATION
echo ============================================================================
echo.
echo ALL REVOLUTIONARY SYSTEMS ACTIVATED:
echo   - 15+ AI Systems (DeepSeek, Qwen, HRM, MASS, ThinkMesh, etc.)
echo   - Visual AI (LLaVA Chart Analysis)
echo   - Continuous Learning
echo   - Self-Improvement
echo   - 1000+ Data Sources
echo   - Dual-Broker Integration
echo.
echo Starting ultimate system...
echo Press Ctrl+C anytime to stop safely
echo.
echo ============================================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Run the ultimate system
python LAUNCH_ULTIMATE_PROMETHEUS_50M.py

REM Keep window open if error occurs
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR OCCURRED - Check above for details
    echo ============================================================================
    echo.
    pause
)
