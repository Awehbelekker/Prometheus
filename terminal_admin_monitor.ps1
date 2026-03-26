param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [int]$RefreshSeconds = 30
)

$ErrorActionPreference = "SilentlyContinue"

function Get-Json([string]$Url) {
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 8
        if ($resp.StatusCode -eq 200 -and $resp.Content) {
            return $resp.Content | ConvertFrom-Json
        }
    }
    catch {
    }
    return $null
}

while ($true) {
    Clear-Host
    $now = Get-Date
    $health = Get-Json "$BaseUrl/health"
    $root = Get-Json "$BaseUrl/"

    Write-Host "================================================================="
    Write-Host " PROMETHEUS TERMINAL ADMIN MONITOR"
    Write-Host " Time: $($now.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host " Base URL: $BaseUrl"
    Write-Host "================================================================="

    if ($root) {
        Write-Host ("Platform: {0} v{1}" -f $root.name, $root.version)
        Write-Host ("Status:   {0}" -f $root.status)
    }
    else {
        Write-Host "Platform: [UNREACHABLE]"
    }

    Write-Host ""
    Write-Host "[Core Health]"
    if ($health) {
        Write-Host ("health.status:   {0}" -f $health.status)
        Write-Host ("uptime_seconds:  {0}" -f $health.uptime_seconds)
        if ($health.latency_ms) {
            Write-Host ("latency_latest:  {0} ms" -f $health.latency_ms.latest)
            Write-Host ("latency_avg1000: {0} ms" -f $health.latency_ms.avg_last_1000)
        }
        Write-Host ("errors_total:    {0}" -f $health.errors_total)

        if ($health.services) {
            Write-Host ""
            Write-Host "[Services]"
            $health.services.PSObject.Properties | ForEach-Object {
                $state = if ($_.Value -eq $true) { "OK" } elseif ($_.Value -eq $false) { "DOWN" } else { $_.Value }
                Write-Host (("{0,-20} {1}" -f $_.Name, $state))
            }
        }
    }
    else {
        Write-Host "health.status: [UNREACHABLE]"
    }

    Write-Host ""
    Write-Host "[Quick URLs]"
    Write-Host ("Admin Dashboard: {0}/admin-dashboard" -f $BaseUrl)
    Write-Host ("Health:          {0}/health" -f $BaseUrl)
    Write-Host ""
    Write-Host ("Refreshing every {0}s (Ctrl+C to stop)" -f $RefreshSeconds)

    Start-Sleep -Seconds $RefreshSeconds
}
