# Windows Firewall Configuration for Prometheus Trading Platform
# Run this script as Administrator

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PROMETHEUS FIREWALL CONFIGURATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host "  3. Navigate to this directory" -ForegroundColor Yellow
    Write-Host "  4. Run: .\configure_firewall_manual.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Find Python executable
$pythonExe = (Get-Command python).Source
Write-Host "Python: $pythonExe" -ForegroundColor Cyan

# Find IB Gateway/TWS
$ibPaths = @(
    "C:\Program Files\IB Gateway\ibgateway.exe",
    "C:\Program Files\IBKR\IB Gateway\ibgateway.exe",
    "C:\Program Files (x86)\IB Gateway\ibgateway.exe",
    "C:\Jts\ibgateway\ibgateway.exe",
    "C:\Program Files\TWS\tws.exe",
    "C:\Program Files\IBKR\TWS\tws.exe",
    "C:\Jts\tws\tws.exe"
)

$ibGateway = $null
foreach ($path in $ibPaths) {
    if (Test-Path $path) {
        $ibGateway = $path
        Write-Host "IB Gateway: $ibGateway" -ForegroundColor Cyan
        break
    }
}

if (-not $ibGateway) {
    Write-Host "[WARNING] IB Gateway/TWS not found - will use port-based rules" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Adding firewall rules..." -ForegroundColor Cyan
Write-Host ""

# Function to add firewall rule
function Add-FirewallRule {
    param(
        [string]$Name,
        [string]$Description,
        [string]$Program = $null,
        [int]$Port = 0,
        [string]$Protocol = "TCP",
        [string]$Direction = "Outbound"
    )
    
    try {
        if ($Program -and (Test-Path $Program)) {
            # Program-based rule
            $rule = Get-NetFirewallRule -DisplayName $Name -ErrorAction SilentlyContinue
            if ($rule) {
                Write-Host "[OK] Rule already exists: $Name" -ForegroundColor Green
                return $true
            }
            
            New-NetFirewallRule -DisplayName $Name `
                -Description $Description `
                -Direction $Direction `
                -Program $Program `
                -Action Allow `
                -Enabled True | Out-Null
            
            Write-Host "[OK] Added: $Name" -ForegroundColor Green
            return $true
        }
        elseif ($Port -gt 0) {
            # Port-based rule
            $rule = Get-NetFirewallRule -DisplayName $Name -ErrorAction SilentlyContinue
            if ($rule) {
                Write-Host "[OK] Rule already exists: $Name" -ForegroundColor Green
                return $true
            }
            
            New-NetFirewallRule -DisplayName $Name `
                -Description $Description `
                -Direction $Direction `
                -Protocol $Protocol `
                -LocalPort $Port `
                -Action Allow `
                -Enabled True | Out-Null
            
            Write-Host "[OK] Added: $Name" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "[SKIP] $Name: Need Program or Port" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "[ERROR] Failed to add $Name : $_" -ForegroundColor Red
        return $false
    }
}

$rulesAdded = 0

# 1. Prometheus (Python)
Write-Host "Adding Prometheus rules..." -ForegroundColor Cyan
if ($pythonExe) {
    if (Add-FirewallRule -Name "Prometheus Trading Platform" `
        -Description "Allow Prometheus trading platform to connect to internet (outbound)" `
        -Program $pythonExe -Direction "Outbound") {
        $rulesAdded++
    }
    
    if (Add-FirewallRule -Name "Prometheus Trading Platform (Inbound)" `
        -Description "Allow Prometheus API server to receive connections (inbound)" `
        -Program $pythonExe -Direction "Inbound") {
        $rulesAdded++
    }
}

# 2. Interactive Brokers
Write-Host ""
Write-Host "Adding Interactive Brokers rules..." -ForegroundColor Cyan
if ($ibGateway) {
    if (Add-FirewallRule -Name "Interactive Brokers Gateway" `
        -Description "Allow IB Gateway/TWS to connect to IB servers (outbound)" `
        -Program $ibGateway -Direction "Outbound") {
        $rulesAdded++
    }
    
    if (Add-FirewallRule -Name "Interactive Brokers Gateway (Inbound)" `
        -Description "Allow IB Gateway/TWS to receive local connections (inbound)" `
        -Program $ibGateway -Direction "Inbound") {
        $rulesAdded++
    }
}

# 3. IB Ports
Write-Host ""
Write-Host "Adding IB port rules..." -ForegroundColor Cyan
foreach ($port in @(7496, 7497)) {
    if (Add-FirewallRule -Name "IB Gateway Port $port (Inbound)" `
        -Description "Allow local connections to IB Gateway on port $port" `
        -Port $port -Protocol "TCP" -Direction "Inbound") {
        $rulesAdded++
    }
    
    if (Add-FirewallRule -Name "IB Gateway Port $port (Outbound)" `
        -Description "Allow outbound connections to IB Gateway on port $port" `
        -Port $port -Protocol "TCP" -Direction "Outbound") {
        $rulesAdded++
    }
}

# 4. Common trading ports
Write-Host ""
Write-Host "Adding common trading API ports..." -ForegroundColor Cyan
foreach ($port in @(80, 443, 8080)) {
    if (Add-FirewallRule -Name "Trading API Port $port (Outbound)" `
        -Description "Allow outbound connections for trading APIs on port $port" `
        -Port $port -Protocol "TCP" -Direction "Outbound") {
        $rulesAdded++
    }
}

# 5. Prometheus API ports
Write-Host ""
Write-Host "Adding Prometheus API server ports..." -ForegroundColor Cyan
foreach ($port in @(8000, 8001, 9090)) {
    if (Add-FirewallRule -Name "Prometheus API Port $port (Inbound)" `
        -Description "Allow inbound connections to Prometheus API on port $port" `
        -Port $port -Protocol "TCP" -Direction "Inbound") {
        $rulesAdded++
    }
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Rules added/verified: $rulesAdded" -ForegroundColor Green
Write-Host ""
Write-Host "Firewall rules configured for:" -ForegroundColor Cyan
Write-Host "  ✅ Prometheus Trading Platform (Python)" -ForegroundColor Green
Write-Host "  ✅ Interactive Brokers Gateway/TWS" -ForegroundColor Green
Write-Host "  ✅ IB Gateway ports (7496 paper, 7497 live)" -ForegroundColor Green
Write-Host "  ✅ Common trading API ports (80, 443, 8080)" -ForegroundColor Green
Write-Host "  ✅ Prometheus API server ports (8000, 8001, 9090)" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Alpaca uses HTTPS (port 443) which is usually already allowed." -ForegroundColor Yellow
Write-Host ""

