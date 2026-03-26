# How to Fix IB Gateway Connection

## Problem
IB Gateway is not responding to API connections (connectionClosed immediately)

## Solution Steps

### 1. **Open IB Gateway** (or Trader Workstation)
   - Launch: `IB Gateway` application
   - Or: `Trader Workstation (TWS)`

### 2. **Login**
   - Enter your IB credentials
   - Complete 2FA if required
   - Wait until fully logged in

### 3. **Enable API**
   - Click: **Configure** (gear icon)
   - Or: **File > Global Configuration**
   - Navigate to: **API > Settings**
   
   **MUST CHECK:**
   - ✅ **Enable ActiveX and Socket Clients** - CHECKED
   - ✅ **Socket port:** `4002` (for live) or `7497` (for paper)
   - ✅ **Read-Only API:** UNCHECKED (to allow trading)
   - ✅ **Master API client ID:** Leave blank or set to 0
   - ✅ **Allow connections from localhost only:** CHECKED
   
### 4. **Trusted IPs (if needed)**
   - In API Settings
   - Add: `127.0.0.1` to trusted IPs

### 5. **Restart IB Gateway**
   - Close completely
   - Reopen and login again

### 6. **Test Connection**
   ```bash
   python quick_ib_test.py
   ```
   
   Should see: `[SUCCESS] IB Gateway Connected!`

### 7. **Run Full System**
   ```bash
   python launch_full_system_maximum_performance.py
   ```

## Common Issues

### "connectionClosed" immediately
- Gateway not logged in
- API not enabled
- Wrong port

### "Timeout"
- Gateway not running
- Firewall blocking port 4002

### "Connection refused"
- Wrong port number
- API setting not saved

## Current Workaround

**System is running with ALPACA ONLY now!**

This gives you:
- ✅ Full autonomous trading
- ✅ All AI systems
- ✅ Maximum performance
- ✅ LIVE trading

IB can be added later once Gateway is configured.

## Questions?

If IB still won't connect after following these steps:
1. Check Windows Firewall (allow port 4002)
2. Try restarting computer
3. Reinstall IB Gateway
4. Contact IB support

**For now: Trade with Alpaca (it's working perfectly!)**
