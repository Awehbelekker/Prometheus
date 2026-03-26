#!/usr/bin/env pwsh
# Stop → start backend → start frontend → health check
param(
  [int]$ApiPort = 8000,
  [int]$WebPort = 3000
)

$ErrorActionPreference = 'Continue'
$here = $PSScriptRoot

Write-Host "=== PROMETHEUS START ALL ===" -ForegroundColor Cyan

& "$here/stop_all.ps1" -Ports @($ApiPort,8001,$WebPort,3001,3002)

& "$here/start_backend.ps1" -Port $ApiPort
Start-Sleep 2

& "$here/start_frontend.ps1" -Port $WebPort
Start-Sleep 3

& "$here/health_check.ps1" -ApiBase "http://127.0.0.1:$ApiPort" -WebBase "http://127.0.0.1:$WebPort"

Write-Host "=== START ALL DONE ===" -ForegroundColor Green

