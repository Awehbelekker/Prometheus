#!/usr/bin/env pwsh
# Start Cloudflare Tunnel for prometheus-trade.com using named config if available
param(
  [string]$Config = "cloudflare-tunnel-config.yml",
  [string]$TunnelName = "prometheus-unified",
  [switch]$Quick
)

$ErrorActionPreference = 'Continue'
$projRoot = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
Set-Location $projRoot

function Ensure-Cloudflared {
  if (Get-Command cloudflared -ErrorAction SilentlyContinue) { return $true }
  if (Test-Path "$projRoot/cloudflared.exe") { $env:PATH = "$projRoot;$env:PATH"; return $true }
  Write-Host "cloudflared not found; downloading..." -ForegroundColor Yellow
  try {
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "$projRoot/cloudflared.exe" -UseBasicParsing
    $env:PATH = "$projRoot;$env:PATH"
    return $true
  } catch {
    Write-Error "Failed to download cloudflared: $($_.Exception.Message)"
    return $false
  }
}

if (-not (Ensure-Cloudflared)) { exit 1 }

if ($Quick) {
  Write-Host "Starting quick tunnel to http://localhost:8000 (trycloudflare.com)" -ForegroundColor Yellow
  Start-Process -FilePath 'cloudflared' -ArgumentList @('tunnel','--url','http://localhost:8000') -NoNewWindow -PassThru | Out-Null
  return
}

if (-not (Test-Path (Join-Path $projRoot $Config))) {
  Write-Error "Config not found: $Config"
  exit 1
}

Write-Host "Starting named tunnel '$TunnelName' with $Config" -ForegroundColor Cyan
Start-Process -FilePath 'cloudflared' -ArgumentList @('tunnel','--config', $Config, 'run', $TunnelName) -NoNewWindow -PassThru | Out-Null

Write-Host "cloudflared started. Expected hostnames:" -ForegroundColor Green
Write-Host "  https://prometheus-trade.com" -ForegroundColor Green
Write-Host "  https://api.prometheus-trade.com" -ForegroundColor Green
Write-Host "  wss://ws.prometheus-trade.com/ws" -ForegroundColor Green

