#!/usr/bin/env pwsh
# Start backend (FastAPI via uvicorn) in background on 127.0.0.1:8000
param(
  [string]$Host = '127.0.0.1',
  [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
Write-Host "=== START BACKEND: $Host:$Port ===" -ForegroundColor Cyan

$projRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
Set-Location $projRoot

$cmd = "python"
$args = @('-m','uvicorn','unified_production_server:app','--host', $Host, '--port', "$Port", '--log-level','info')

$proc = Start-Process -FilePath $cmd -ArgumentList $args -PassThru -WindowStyle Hidden
Write-Host "uvicorn started (PID: $($proc.Id))" -ForegroundColor Green

# simple health wait
Start-Sleep 2
try {
  $resp = Invoke-RestMethod -Uri "http://$Host:$Port/health" -TimeoutSec 5 -ErrorAction Stop
  Write-Host "Health OK: $($resp.status)" -ForegroundColor Green
} catch {
  Write-Host "Health check pending (backend starting)" -ForegroundColor Yellow
}

