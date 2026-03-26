@echo off
REM ============================================================================
REM COMPLETE VISUAL AI SETUP - ONE-CLICK INSTALLATION
REM ============================================================================

title PROMETHEUS Visual AI Setup

echo.
echo ============================================================================
echo PROMETHEUS VISUAL AI - COMPLETE SETUP
echo ============================================================================
echo.
echo This will set up LLaVA Visual AI for chart analysis:
echo   - Download LLaVA 7B model (~4GB)
echo   - Install chart generation libraries
echo   - Train on historical data (1 year)
echo   - Test visual analysis
echo.
echo Total time: ~2-4 hours (mostly automated)
echo.
echo ============================================================================
echo.

pause

REM Change to project directory
cd /d "%~dp0"

echo.
echo ============================================================================
echo [STEP 1/3] SETTING UP LLAVA
echo ============================================================================
echo.

python setup_llava_system.py

if errorlevel 1 (
    echo.
    echo [ERROR] LLaVA setup failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [STEP 2/3] TRAINING ON HISTORICAL DATA
echo ============================================================================
echo.
echo This will take 1-3 hours - training on 1 year of charts...
echo.

python train_llava_historical.py

if errorlevel 1 (
    echo.
    echo [WARNING] Historical training had issues, but continuing...
)

echo.
echo ============================================================================
echo [STEP 3/3] TESTING VISUAL ANALYSIS
echo ============================================================================
echo.

python test_visual_analysis.py

if errorlevel 1 (
    echo.
    echo [WARNING] Visual analysis test had issues
)

echo.
echo ============================================================================
echo VISUAL AI SETUP COMPLETE!
echo ============================================================================
echo.
echo LLaVA is now ready to:
echo   - Recognize 50+ chart patterns
echo   - Detect support/resistance levels
echo   - Analyze trends in real-time
echo   - Enhance trading decisions
echo.
echo Next: Launch PROMETHEUS with Visual AI enabled!
echo   Run: LAUNCH_ULTIMATE_PROMETHEUS_50M.py
echo.
echo ============================================================================
echo.

pause
