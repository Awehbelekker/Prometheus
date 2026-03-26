@echo off
REM Run Database Backup Setup
REM This will schedule daily backups

echo ================================================================================
echo PROMETHEUS DATABASE BACKUP SETUP
echo ================================================================================
echo.
echo This will schedule daily backups at 2:00 AM
echo.
echo NOTE: This requires Administrator privileges
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0schedule_daily_backups.ps1"

pause

