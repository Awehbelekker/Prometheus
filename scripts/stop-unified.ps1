# Stops the Unified Docker stack
override
$composeFile = Join-Path $PSScriptRoot "..\docker-compose.unified.yml"
if (!(Test-Path $composeFile)) { Write-Error "compose file not found: $composeFile"; exit 1 }

$cmd = "docker compose -f `"$composeFile`" down -v"
Write-Host "Running: $cmd"
Invoke-Expression $cmd
