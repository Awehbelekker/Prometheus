#!/usr/bin/env pwsh
# Start frontend React dev server on port 3000
param(
  [int]$Port = 3000
)

$ErrorActionPreference = 'Stop'
Write-Host "=== START FRONTEND: port $Port ===" -ForegroundColor Cyan

$projRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$frontend = Join-Path $projRoot 'frontend'

if (-not (Test-Path $frontend)) { throw "Frontend directory not found: $frontend" }

$env:PORT = "$Port"
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm','start' -WorkingDirectory $frontend -WindowStyle Hidden | Out-Null

Write-Host "npm start launched in background." -ForegroundColor Green

