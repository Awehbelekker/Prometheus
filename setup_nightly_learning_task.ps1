param(
    [string]$TaskName = "PROMETHEUS-Nightly-Learning",
    [string]$StartTime = "01:15"
)

$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $workspace ".venv_directml_test\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$runner = Join-Path $workspace "run_nightly_learning_cycle.py"
if (-not (Test-Path $runner)) {
    throw "Missing runner: $runner"
}

$actionArgs = "/c cd /d `"$workspace`" ; `"$python`" `"$runner`" --iterations 2 --days 60"

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $actionArgs
$trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

Write-Host "Scheduled task created/updated: $TaskName"
Write-Host "Start time: $StartTime"
Write-Host "Command: $python $runner --iterations 2 --days 60"
