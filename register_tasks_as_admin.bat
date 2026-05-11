@echo off
:: Right-click this file and choose "Run as administrator"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; ^
$ROOT='C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform'; ^
$PYTHON=\"$ROOT\.venv_directml_test\Scripts\python.exe\"; ^
if (-not (Test-Path $PYTHON)) { Write-Host 'ERROR: Python not found at ' $PYTHON -ForegroundColor Red; Read-Host 'Press Enter'; exit 1 }; ^
$s2 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -StartWhenAvailable; ^
$s5 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -StartWhenAvailable; ^
$sW = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Days 0) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew -StartWhenAvailable; ^
Register-ScheduledTask -Force -RunLevel Highest -TaskName 'PROMETHEUS Watchdog' -Action (New-ScheduledTaskAction -Execute $PYTHON -Argument 'prometheus_watchdog.py' -WorkingDirectory $ROOT) -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings $sW; Write-Host '[OK] Watchdog' -ForegroundColor Green; ^
Register-ScheduledTask -Force -RunLevel Highest -TaskName 'PROMETHEUS Daily Report' -Action (New-ScheduledTaskAction -Execute $PYTHON -Argument 'prometheus_reporter.py' -WorkingDirectory $ROOT) -Trigger (New-ScheduledTaskTrigger -Daily -At '08:00') -Settings $s2; Write-Host '[OK] Daily Report' -ForegroundColor Green; ^
Register-ScheduledTask -Force -RunLevel Highest -TaskName 'PROMETHEUS Weekly Report' -Action (New-ScheduledTaskAction -Execute $PYTHON -Argument 'prometheus_reporter.py --weekly' -WorkingDirectory $ROOT) -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '08:00') -Settings $s2; Write-Host '[OK] Weekly Report' -ForegroundColor Green; ^
Register-ScheduledTask -Force -RunLevel Highest -TaskName 'PROMETHEUS Knowledge Update' -Action (New-ScheduledTaskAction -Execute $PYTHON -Argument 'knowledge_weekly_update.py' -WorkingDirectory $ROOT) -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '07:00') -Settings $s2; Write-Host '[OK] Knowledge Update' -ForegroundColor Green; ^
Register-ScheduledTask -Force -RunLevel Highest -TaskName 'PROMETHEUS PPO Retrain' -Action (New-ScheduledTaskAction -Execute $PYTHON -Argument 'nightly_ppo_retrain.py' -WorkingDirectory $ROOT) -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At '10:00PM') -Settings $s5; Write-Host '[OK] PPO Retrain' -ForegroundColor Green; ^
Write-Host ''; Write-Host 'All 5 tasks registered successfully.' -ForegroundColor Cyan"
pause
