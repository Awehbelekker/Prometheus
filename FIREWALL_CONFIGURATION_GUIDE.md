# Windows Defender Firewall Configuration Guide

## Overview

This guide ensures Windows Defender Firewall doesn't block:

- **Prometheus Trading Platform** (Python processes)
- **Interactive Brokers (IB)** Gateway/TWS
- **Alpaca** API connections
- **All trading-related network traffic**

---

## Quick Setup (Automated)

### Option 1: Python Script (Recommended)

**Run as Administrator:**

```powershell

# Right-click PowerShell → Run as administrator

cd C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform
python configure_firewall_exceptions.py

```

### Option 2: PowerShell Script

**Run as Administrator:**

```powershell

# Right-click PowerShell → Run as administrator

cd C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform
.\configure_firewall_manual.ps1

```

---

## Manual Configuration

If automated scripts don't work, configure manually:

### Step 1: Open Windows Defender Firewall

1. Press `Win + R`
2. Type: `wf.msc`
3. Press Enter

### Step 2: Add Outbound Rules for Prometheus

1. Click **"Outbound Rules"** → **"New Rule..."**
2. Select **"Program"** → Next
3. Browse to: `C:\Users\Judy\AppData\Local\Programs\Python\Python313\python.exe`
   - (Or wherever your Python is installed)
4. Select **"Allow the connection"** → Next
5. Check all profiles (Domain, Private, Public) → Next
6. Name: **"Prometheus Trading Platform"** → Finish

### Step 3: Add Inbound Rules for Prometheus API

1. Click **"Inbound Rules"** → **"New Rule..."**
2. Select **"Port"** → Next
3. Select **"TCP"** → **"Specific local ports"**: `8000, 8001, 9090` → Next
4. Select **"Allow the connection"** → Next
5. Check all profiles → Next
6. Name: **"Prometheus API Server"** → Finish

### Step 4: Add Rules for Interactive Brokers

1. **Outbound Rule for IB Gateway:**
   - New Rule → Program
   - Browse to: `C:\Program Files\IB Gateway\ibgateway.exe`
     - (Or `C:\Jts\ibgateway\ibgateway.exe`)
   - Allow connection
   - Name: **"Interactive Brokers Gateway"**

2. **Inbound Rule for IB Ports:**
   - New Rule → Port
   - TCP → Ports: `7496, 7497`
   - Allow connection
   - Name: **"IB Gateway Ports"**

### Step 5: Verify Common Ports

Ensure these ports are allowed (usually already allowed):

- **Port 80** (HTTP) - Outbound
- **Port 443** (HTTPS) - Outbound
- **Port 8080** (Alternative HTTP) - Outbound

---

## Windows Defender Antivirus Exclusions

Windows Defender Antivirus may also block connections. Add exclusions:

### Step 1: Open Windows Security

1. Press `Win + I` → **"Privacy & Security"** → **"Windows Security"**
2. Click **"Virus & threat protection"**
3. Click **"Manage settings"** (under Virus & threat protection settings)
4. Scroll to **"Exclusions"** → Click **"Add or remove exclusions"**

### Step 2: Add Exclusions

Add these folders:

1. **Prometheus Project Folder:**

   ```
```text
   C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform

   ```

2. **Python Installation:**

   ```
```text
   C:\Users\Judy\AppData\Local\Programs\Python\Python313

   ```

3. **IB Gateway/TWS:**

   ```
```text
   C:\Program Files\IB Gateway
   C:\Jts

   ```

### Step 3: Add Process Exclusions

Add these processes:

- `python.exe`
- `ibgateway.exe`
- `tws.exe`

---

## Testing Firewall Configuration

### Test Prometheus Connection

```powershell

# Test Alpaca API

python -c "import requests; r = requests.get('https://api.alpaca.markets/v2/account', timeout=5); print('Alpaca:', 'OK' if r.status_code in [200, 401] else 'FAILED')"

# Test IB Gateway (if running)

python -c "import socket; s = socket.socket(); result = s.connect_ex(('127.0.0.1', 7497)); print('IB Gateway:', 'OK' if result == 0 else 'NOT RUNNING'); s.close()"

```

### Test Firewall Rules

```powershell

# List Prometheus rules

Get-NetFirewallRule -DisplayName "*Prometheus*" | Format-Table DisplayName, Enabled, Direction

# List IB rules

Get-NetFirewallRule -DisplayName "*IB*" | Format-Table DisplayName, Enabled, Direction

```

---

## Troubleshooting

### Issue: "Connection refused" or "Timeout"

**Solutions:**

1. Check if firewall rules are enabled:

   ```powershell

   Get-NetFirewallRule -DisplayName "*Prometheus*" | Select DisplayName, Enabled

   ```

2. Temporarily disable firewall to test:

   ```powershell

   # Test only - re-enable after!
   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

   ```

3. Check Windows Defender logs:
   - Windows Security → Virus & threat protection → Protection history

### Issue: IB Gateway can't connect

**Solutions:**

1. Ensure IB Gateway is running
2. Check port 7497 (live) or 7496 (paper) is open:

   ```powershell

   Test-NetConnection -ComputerName localhost -Port 7497

   ```

3. Verify IB Gateway firewall rule:

   ```powershell

   Get-NetFirewallRule -DisplayName "*IB*"

   ```

### Issue: Alpaca API blocked

**Solutions:**

1. Port 443 (HTTPS) should be allowed by default
2. Check Windows Defender exclusions
3. Verify network connectivity:

   ```powershell

   Test-NetConnection -ComputerName api.alpaca.markets -Port 443

   ```

---

## Advanced: PowerShell One-Liners

### Add All Rules at Once

```powershell

# Run as Administrator

$python = (Get-Command python).Source
New-NetFirewallRule -DisplayName "Prometheus" -Program $python -Direction Outbound -Action Allow
New-NetFirewallRule -DisplayName "Prometheus Inbound" -Program $python -Direction Inbound -Action Allow
New-NetFirewallRule -DisplayName "IB Port 7497" -Protocol TCP -LocalPort 7497 -Direction Inbound -Action Allow
New-NetFirewallRule -DisplayName "IB Port 7496" -Protocol TCP -LocalPort 7496 -Direction Inbound -Action Allow

```

### Remove All Rules

```powershell

# Run as Administrator

Remove-NetFirewallRule -DisplayName "*Prometheus*"
Remove-NetFirewallRule -DisplayName "*IB*"

```

---

## Verification Checklist

After configuration, verify:

- [ ] Prometheus can connect to Alpaca API
- [ ] Prometheus can connect to IB Gateway (if running)
- [ ] IB Gateway can connect to IB servers
- [ ] Prometheus API server is accessible (if running)
- [ ] No firewall warnings in Windows Security
- [ ] No connection timeouts in logs

---

## Summary

**Quick Setup:**

1. Run `python configure_firewall_exceptions.py` as Administrator
2. Add Windows Defender exclusions (folders + processes)
3. Test connections
4. Launch Prometheus

**Result:** All trading connections work without firewall interference!

---

**Need Help?** Check the troubleshooting section or review Windows Security logs.

