# Why IB Gateway Might Not Be Running

## Quick Check

1. **Is IB Gateway/TWS actually open on your desktop?**
   - Look for "IB Gateway" or "Trader Workstation" window
   - It must be running for the API to connect

2. **Are you logged in?**
   - Gateway must be logged into account U21922116
   - Can't just be open - must be authenticated

3. **Is API enabled in settings?**
   - Gateway: Configure > Settings > API > Enable ActiveX and Socket Clients
   - Port should be 4002 (paper) or 7496 (live)

## Common Reasons IB Doesn't Connect

### 1. **Gateway Not Running**
**Solution:** 
- Open IB Gateway application
- Login to account U21922116
- Keep it running in background

### 2. **Wrong Port**
**Solution:**
- IB Gateway Paper: Port **4002**
- IB Gateway Live: Port **7496**
- TWS Paper: Port **7497**
- TWS Live: Port **7496**

Our system tries port 4002 by default. To change:
```
set IB_PORT=7496
```

### 3. **API Not Enabled**
**Solution:**
- In Gateway/TWS: Configure > Settings > API
- Check "Enable ActiveX and Socket Clients"
- Check "Allow connections from localhost"
- Uncheck "Read-Only API" (we need to place orders)

### 4. **Firewall Blocking**
**Solution:**
- Windows Firewall might be blocking port 4002/7496
- Allow "javaw.exe" through firewall
- Allow "IB Gateway" through firewall

### 5. **Account Issues**
**Solution:**
- Verify account U21922116 is active
- Check if paper trading is enabled
- Verify API permissions are granted

## Do You Need IB Gateway?

**NO! Prometheus works perfectly with just Alpaca.**

IB Gateway is **optional**. If you prefer to trade only with Alpaca:
- System automatically detects IB is unavailable
- Continues with Alpaca only
- No functionality lost

Benefits of adding IB:
- More capital to deploy
- Options trading capability
- Extended hours access
- Diversified broker risk

## How To Fix IB Connection

### Option 1: Enable IB Gateway (Recommended for dual-broker)

1. **Open IB Gateway**
   - Find it in your Start Menu
   - Or download from: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php

2. **Login**
   - Username: Your IB credentials
   - Account: U21922116

3. **Configure API**
   - Click Configure (gear icon)
   - Settings > API
   - Enable ActiveX and Socket Clients: ✅
   - Socket port: 4002 (paper) or 7496 (live)
   - Allow connections from localhost: ✅
   - Read-Only API: ❌ (unchecked)

4. **Keep Running**
   - Don't close the Gateway window
   - It needs to stay open while Prometheus trades

5. **Relaunch Prometheus**
   - Double-click LAUNCH_AI_LEARNING.bat
   - Should now show "IB Gateway Connected"

### Option 2: Use Alpaca Only (Easiest)

Just ignore the IB messages. Prometheus will automatically:
- Detect IB is unavailable
- Use Alpaca for all trades
- Continue working perfectly

## Verification

After starting IB Gateway, test connection:
```
python check_ib_status.py
```

Should show:
```
[OK] IB Gateway Connected
     Account: U21922116
     Equity: $XXX.XX
```

## Current Status

Based on your setup:
- **Alpaca:** ✅ Working ($122.48)
- **IB Gateway:** ❌ Not connected ($13.54 shows in TWS but not accessible via API)

**Recommendation:** Either:
1. Start IB Gateway and login (for dual-broker)
2. Or just use Alpaca only (totally fine!)

Prometheus is designed to work with either configuration.

---

## Bottom Line

**IB Gateway is OPTIONAL.** 

If you want to use it:
1. Open IB Gateway
2. Login
3. Enable API in settings
4. Relaunch Prometheus

If not:
- Prometheus works great with just Alpaca
- No action needed
- System will auto-detect and adapt

**Both options are fully supported!**
