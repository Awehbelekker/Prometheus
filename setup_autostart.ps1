# PROMETHEUS Auto-start + WhatsApp Reporter Setup
# Run once as Administrator: Right-click PowerShell > "Run as Administrator"
# Then: cd "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform" && .\setup_autostart.ps1

$ROOT   = "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform"
$PYTHON = "$ROOT\.venv_directml_test\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: Python not found at $PYTHON" -ForegroundColor Red
    Write-Host "Update the PYTHON variable in this script to your venv path."
    exit 1
}

Write-Host "Setting up PROMETHEUS scheduled tasks..." -ForegroundColor Cyan

# ── Task 1: Watchdog — starts at login, runs forever ─────────────────────────
$action1  = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "prometheus_watchdog.py" `
    -WorkingDirectory $ROOT

$trigger1 = New-ScheduledTaskTrigger -AtLogOn

$settings1 = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Days 0) `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName   "PROMETHEUS Watchdog" `
    -Action     $action1 `
    -Trigger    $trigger1 `
    -Settings   $settings1 `
    -RunLevel   Highest `
    -Force | Out-Null

Write-Host "  [OK] PROMETHEUS Watchdog — runs at login" -ForegroundColor Green

# ── Task 2: Daily report — 08:00 every day ───────────────────────────────────
$action2  = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "prometheus_reporter.py" `
    -WorkingDirectory $ROOT

$trigger2 = New-ScheduledTaskTrigger -Daily -At "08:00"

$settings2 = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName   "PROMETHEUS Daily Report" `
    -Action     $action2 `
    -Trigger    $trigger2 `
    -Settings   $settings2 `
    -RunLevel   Highest `
    -Force | Out-Null

Write-Host "  [OK] Daily WhatsApp report — 08:00 every morning" -ForegroundColor Green

# ── Task 3: Weekly report — Sunday 08:00 ─────────────────────────────────────
$action3  = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "prometheus_reporter.py --weekly" `
    -WorkingDirectory $ROOT

$trigger3 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "08:00"

Register-ScheduledTask `
    -TaskName   "PROMETHEUS Weekly Report" `
    -Action     $action3 `
    -Trigger    $trigger3 `
    -Settings   $settings2 `
    -RunLevel   Highest `
    -Force | Out-Null

Write-Host "  [OK] Weekly WhatsApp report — Sunday 08:00" -ForegroundColor Green

# ── Task 4: Weekly knowledge update — Sunday 07:00 (before report) ───────────
$action4  = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "knowledge_weekly_update.py" `
    -WorkingDirectory $ROOT

$trigger4 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "07:00"

Register-ScheduledTask `
    -TaskName   "PROMETHEUS Knowledge Update" `
    -Action     $action4 `
    -Trigger    $trigger4 `
    -Settings   $settings2 `
    -RunLevel   Highest `
    -Force | Out-Null

Write-Host "  [OK] Weekly knowledge update — Sunday 07:00 (arXiv pull)" -ForegroundColor Green

# ── Task 5: Nightly PPO retraining — 22:00 every weekday ─────────────────────
$action5  = New-ScheduledTaskAction `
    -Execute $PYTHON `
    -Argument "nightly_ppo_retrain.py" `
    -WorkingDirectory $ROOT

$trigger5 = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At "10:00PM"

$settings5 = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName   "PROMETHEUS PPO Retrain" `
    -Action     $action5 `
    -Trigger    $trigger5 `
    -Settings   $settings5 `
    -RunLevel   Highest `
    -Force | Out-Null

Write-Host "  [OK] Nightly PPO retraining — 22:00 Mon-Fri (RL learns from today's trades)" -ForegroundColor Green

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "All tasks registered. Verify in Task Scheduler:" -ForegroundColor Cyan
Write-Host "  taskschd.msc  →  Task Scheduler Library"
Write-Host ""
Write-Host "NEXT STEP — Get your CallMeBot API key:" -ForegroundColor Yellow
Write-Host "  1. Save +34 644 82 70 96 as a WhatsApp contact"
Write-Host "  2. Send: I allow callmebot to send me messages"
Write-Host "  3. You will receive your API key"
Write-Host "  4. Add to .env:  CALLMEBOT_API_KEY=your_key_here"
Write-Host ""
Write-Host "Test the reporter after adding the key:" -ForegroundColor Yellow
Write-Host "  python prometheus_reporter.py --test"
