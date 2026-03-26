#!/usr/bin/env pwsh
# Quick health check for backend/frontend
param(
  [string]$ApiBase = 'http://127.0.0.1:8000',
  [string]$WebBase = 'http://127.0.0.1:3000'
)

$ErrorActionPreference = 'SilentlyContinue'
Write-Host "=== HEALTH CHECK ===" -ForegroundColor Cyan

try { $h = Invoke-RestMethod -Uri "$ApiBase/health" -TimeoutSec 5; Write-Host "/health OK" -ForegroundColor Green } catch { Write-Host "/health FAIL" -ForegroundColor Red }
try { $s = Invoke-RestMethod -Uri "$ApiBase/api/system/status" -TimeoutSec 5; Write-Host "/api/system/status OK" -ForegroundColor Green } catch { Write-Host "/api/system/status FAIL" -ForegroundColor Red }
try { $u = Invoke-WebRequest -Uri $WebBase -TimeoutSec 5; Write-Host "Frontend root OK (status $($u.StatusCode))" -ForegroundColor Green } catch { Write-Host "Frontend root FAIL" -ForegroundColor Red }

Write-Host "=== HEALTH DONE ===" -ForegroundColor Green

