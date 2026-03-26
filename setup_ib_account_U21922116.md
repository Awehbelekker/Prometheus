# Setup IB Account U21922116 for PROMETHEUS

## Your IB Account
- **Account Number:** U21922116
- **Required Port:** 4002 (LIVE) or 7497 (PAPER)

## Step-by-Step Setup

### 1. Open IB Gateway
1. Find and launch: **IB Gateway** (or Trader Workstation)
2. Login with:
   - Username: Your IB username
   - Password: Your IB password
   - Complete 2FA if prompted

### 2. Configure API Settings

Once logged in:

**Option A: IB Gateway**
1. Click the **gear icon** (Configure) in top right
2. Go to: **Settings > API > Settings**

**Option B: Trader Workstation (TWS)**
1. Menu: **File > Global Configuration**
2. Navigate to: **API > Settings**

### 3. Required Settings

✅ **MUST CHECK THESE:**

```
[ ✓ ] Enable ActiveX and Socket Clients
      ↑ THIS IS CRITICAL!

Socket port: 4002
           ↑ For LIVE trading

[ ✓ ] Create API message log file (optional but helpful)

[   ] Read-Only API
      ↑ LEAVE UNCHECKED (to allow trading!)

Master API client ID: 0 (or leave blank)

[ ✓ ] Allow connections from localhost only
```

### 4. Trusted IPs (Important!)

In the same API Settings screen:

1. Find: **Trusted IP Addresses**
2. Add: `127.0.0.1`
3. Click **OK** or **Apply**

### 5. Save and Restart

1. Click **OK** to save all settings
2. **Close IB Gateway completely**
3. **Reopen IB Gateway**
4. **Login again**
5. Wait 30 seconds for full initialization

### 6. Verify Connection

Run this test:

```bash
python quick_ib_test.py
```

**Expected Output:**
```
[SUCCESS] IB Gateway Connected!
Account Details:
  Equity: $X,XXX.XX
  Cash: $X,XXX.XX
[OK] IB is ready for trading!
```

## Troubleshooting

### If Still Getting "connectionClosed"

1. **Check Gateway is fully logged in**
   - Green light/indicator showing connected
   - Account info visible in Gateway window

2. **Verify Port Number**
   - Port 4002 = LIVE account
   - Port 7497 = PAPER account
   - Check which mode you're logged into

3. **Windows Firewall**
   - Go to: Windows Firewall settings
   - Allow: `javaw.exe` (IB Gateway uses Java)
   - Allow port: 4002

4. **Antivirus**
   - Some antivirus blocks socket connections
   - Temporarily disable to test

5. **Restart Everything**
   - Close Gateway completely
   - Restart computer
   - Login to Gateway again
   - Test connection

## Live vs Paper Trading

### To Trade LIVE:
- Login to: **LIVE Trading** mode in Gateway
- Port: **4002**
- Account: **U21922116**

### To Trade PAPER (for testing):
- Login to: **Paper Trading** mode in Gateway  
- Port: **7497**
- Account: Will be different (DU number)

## After IB is Connected

Run the full system with both brokers:

```bash
python launch_full_system_maximum_performance.py
```

You'll get:
- ✅ Alpaca LIVE
- ✅ IB LIVE (U21922116)
- ✅ Dual-broker execution
- ✅ Maximum performance!

## Current Status

✅ **Alpaca:** Already working (Account 910544927)  
⏳ **IB:** Needs configuration (Account U21922116)

**Once IB is configured:**
- 2x execution power
- More trading opportunities
- Better fills
- Portfolio diversification

## Need Help?

If Gateway still won't connect:
1. Screenshot your API Settings
2. Check IB Gateway logs (File > Log Messages)
3. Ensure you're logged into LIVE mode (not Paper)
4. Try restarting your computer

**Remember:** System already trades with Alpaca!  
**IB is optional but gives you 2x power!**
