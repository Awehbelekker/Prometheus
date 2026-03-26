#!/usr/bin/env pwsh
# Stop all PROMETHEUS platform processes and free key ports (Windows)
param(
  [int[]]$Ports = @(8000,8001,3000,3001,3002)
)

$ErrorActionPreference = 'SilentlyContinue'
Write-Host "=== STOP ALL: Killing Node/Python/cloudflared and freeing ports ===" -ForegroundColor Cyan

# Kill common processes
Get-Process node,npm,vite,python,python3,uvicorn,cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Free specific ports by PID
foreach ($p in $Ports) {
  $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
  if ($conns) {
    $pids = $conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
    foreach ($pid in $pids) {
      try { Stop-Process -Id $pid -Force -ErrorAction Stop; Write-Host "Killed PID $pid (port $p)" -ForegroundColor Yellow } catch {}
    }
  }
}

Start-Sleep 1
Write-Host "Post-check listeners:" -ForegroundColor Gray
foreach ($p in $Ports) { Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess }

Write-Host "=== STOP ALL: Complete ===" -ForegroundColor Green

