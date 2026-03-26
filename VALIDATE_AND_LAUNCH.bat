@echo off
REM ============================================================================
REM VALIDATE COMPLETE SYSTEM + RUN BENCHMARKS + LAUNCH
REM Get REAL performance data before launching
REM ============================================================================

title PROMETHEUS Validation & Launch

echo.
echo ============================================================================
echo PROMETHEUS - COMPLETE VALIDATION + BENCHMARKS + LAUNCH
echo ============================================================================
echo.
echo This will:
echo   1. Validate all 19 AI systems are properly implemented
echo   2. Run performance benchmarks (get REAL data)
echo   3. Check optimization opportunities
echo   4. Launch if everything checks out
echo.
echo Total time: 5-10 minutes
echo.
echo ============================================================================
echo.

pause

cd /d "%~dp0"

echo.
echo ============================================================================
echo [1/3] VALIDATING COMPLETE SYSTEM
echo ============================================================================
echo.

python validate_complete_system.py

if errorlevel 1 (
    echo.
    echo [WARNING] Some validation issues detected
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        echo Cancelled.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================================
echo [2/3] RUNNING PERFORMANCE BENCHMARKS
echo ============================================================================
echo.
echo Getting REAL performance measurements...
echo This will take 5-10 minutes...
echo.

python run_performance_benchmarks.py

echo.
echo ============================================================================
echo [3/3] LAUNCHING PROMETHEUS
echo ============================================================================
echo.
echo All checks complete!
echo.

set /p launch="Launch PROMETHEUS now? (y/n): "
if /i "%launch%"=="y" (
    set IB_PORT=4002
    python LAUNCH_ULTIMATE_PROMETHEUS_50M.py
) else (
    echo Launch cancelled.
)

pause
