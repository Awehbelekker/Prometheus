# Starts the Unified Docker stack (prod-like)
param(
  [switch]$Rebuild
)

$composeFile = Join-Path $PSScriptRoot "..\docker-compose.unified.yml"
if (!(Test-Path $composeFile)) { Write-Error "compose file not found: $composeFile"; exit 1 }

$cmd = "docker compose -f `"$composeFile`" up -d";
if ($Rebuild) { $cmd += " --build" }
Write-Host "Running: $cmd"
Invoke-Expression $cmd
