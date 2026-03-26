# PROMETHEUS Backend Server - Permanent Startup Script
# This script ensures the backend server starts correctly

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROMETHEUS Backend Server Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Change to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Kill existing processes on port 8000
Write-Host "Checking for existing processes on port 8000..." -ForegroundColor Yellow
$existing = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existing) {
    $pid = (Get-NetTCPConnection -LocalPort 8000).OwningProcess
    Write-Host "Killing existing process: PID $pid" -ForegroundColor Yellow
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

# Load environment variables from .env if it exists
if (Test-Path ".env") {
    Write-Host "Loading .env file..." -ForegroundColor Green
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"').Trim("'")
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Start backend server
Write-Host "Starting backend server on port 8000..." -ForegroundColor Green
$proc = Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "unified_production_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1") -PassThru -WindowStyle Normal -NoNewWindow

Write-Host "Backend server started (PID: $($proc.Id))" -ForegroundColor Green
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow

# Wait and check health
$maxAttempts = 20
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts -and -not $healthy) {
    Start-Sleep -Seconds 2
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend server is healthy and responding!" -ForegroundColor Green
            $healthy = $true
        }
    } catch {
        Write-Host "Attempt $attempt/$maxAttempts - Waiting for server..." -ForegroundColor Yellow
    }
}

if (-not $healthy) {
    Write-Host "⚠️ Backend server started but health check failed. Check logs for errors." -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend server startup complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
