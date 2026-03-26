# Schedule Daily Database Backups for Prometheus
# Run this script as Administrator to set up automatic daily backups

$scriptPath = Join-Path $PSScriptRoot "backup_databases.py"
$pythonPath = (Get-Command python).Source
$taskName = "PrometheusDailyBackup"
$description = "Daily backup of Prometheus trading databases"

Write-Host "=" * 80
Write-Host "SCHEDULING DAILY DATABASE BACKUPS"
Write-Host "=" * 80
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "[INFO] Task already exists. Updating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot

# Create trigger (daily at 2 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 2am

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $description | Out-Null
    
    Write-Host "[OK] Daily backup task scheduled successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:"
    Write-Host "  Name: $taskName"
    Write-Host "  Schedule: Daily at 2:00 AM"
    Write-Host "  Script: $scriptPath"
    Write-Host ""
    Write-Host "To view the task:"
    Write-Host "  Get-ScheduledTask -TaskName $taskName"
    Write-Host ""
    Write-Host "To remove the task:"
    Write-Host "  Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false"
    Write-Host ""
    Write-Host "To test the backup now:"
    Write-Host "  python backup_databases.py"
    Write-Host ""
} catch {
    Write-Host "[ERROR] Failed to schedule task: $_" -ForegroundColor Red
    exit 1
}

Write-Host "=" * 80

