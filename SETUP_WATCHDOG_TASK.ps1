# PROMETHEUS WATCHDOG - Windows Task Scheduler Setup
# Run this once as Administrator to register the watchdog as a startup task.
# After this, the watchdog auto-starts on Windows login and restarts trading
# if the process crashes. It will WAIT for IB Gateway login before restarting
# (so after a reboot you just log into IB Gateway normally, watchdog handles the rest).

$TaskName   = "PrometheusWatchdog"
$RootDir    = "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform"
$PythonExe  = "$RootDir\.venv_directml_test\Scripts\python.exe"
$Script     = "$RootDir\prometheus_watchdog.py"
$LogDir     = $RootDir

# Fall back to system python if venv not found
if (-not (Test-Path $PythonExe)) {
    $PythonExe = (Get-Command python).Source
    Write-Host "venv Python not found — using system Python: $PythonExe"
}

Write-Host ""
Write-Host "=== PROMETHEUS WATCHDOG TASK SETUP ===" -ForegroundColor Cyan
Write-Host "  Task name : $TaskName"
Write-Host "  Python    : $PythonExe"
Write-Host "  Script    : $Script"
Write-Host ""

# Remove old task if it exists
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $Script `
    -WorkingDirectory $RootDir

# Trigger: at user logon (so it starts whenever you log into Windows)
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Run as current user, highest privileges
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Settings $Settings `
    -Description "Prometheus Trading Platform watchdog — auto-restarts trading on crash, waits for IB Gateway before restart" `
    | Out-Null

Write-Host "Task registered successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "What happens after a PC reboot:" -ForegroundColor White
Write-Host "  1. You log into Windows"
Write-Host "  2. Watchdog starts automatically"
Write-Host "  3. Watchdog polls IB Gateway on 127.0.0.1:4002 every 60s"
Write-Host "  4. You open IB Gateway and log in manually"
Write-Host "  5. Watchdog detects IB is up -> launches trading immediately"
Write-Host "  6. If trading crashes -> watchdog restarts it (backoff: 30s, 60s, 120s...)"
Write-Host ""
Write-Host "To stop the watchdog:  Stop-ScheduledTask -TaskName PrometheusWatchdog"
Write-Host "To start manually:     Start-ScheduledTask -TaskName PrometheusWatchdog"
Write-Host "To remove entirely:    Unregister-ScheduledTask -TaskName PrometheusWatchdog"
Write-Host ""
Write-Host "Watchdog log: $RootDir\prometheus_watchdog.log" -ForegroundColor Cyan
