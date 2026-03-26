@echo off
REM CUDA 12.6 PATH Setup - Run as Administrator
REM This batch file will request admin privileges automatically

echo ================================================================================
echo CUDA 12.6 PATH SETUP
echo ================================================================================
echo.
echo This will configure CUDA 12.6 environment variables:
echo   - CUDA_HOME
echo   - CUDA_PATH
echo   - PATH (with CUDA 12.6 at the beginning)
echo.
echo Press any key to continue (or Ctrl+C to cancel)...
pause >nul

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0SETUP_CUDA_12_6.ps1"
) else (
    echo [INFO] Requesting Administrator privileges...
    echo.
    REM Re-run as admin
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo IMPORTANT: RESTART YOUR SYSTEM for changes to take effect
echo.
echo After restart, run: python verify_cuda_after_restart.py
echo.
pause

