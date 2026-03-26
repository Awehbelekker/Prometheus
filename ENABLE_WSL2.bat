@echo off
:: Self-elevate to Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================
echo    ENABLING WSL2 FEATURES (Running as Administrator)
echo ============================================================
echo.

echo [1/4] Enabling Virtual Machine Platform...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

echo.
echo [2/4] Enabling Windows Subsystem for Linux...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

echo.
echo [3/4] Setting WSL 2 as default...
wsl --set-default-version 2

echo.
echo [4/4] Updating WSL...
wsl --update

echo.
echo ============================================================
echo    FEATURES ENABLED - RESTART REQUIRED
echo ============================================================
echo.
echo After restart, open PowerShell and run:
echo    wsl --install Ubuntu-22.04
echo.
echo ============================================================
pause

choice /C YN /M "Restart computer now"
if %errorlevel%==1 shutdown /r /t 10
