# Interactive Brokers Port Correction

## ✅ CORRECTED: Port 7497 is LIVE Trading

### Issue Found

The system was configured to use port **7496** for live trading, but the correct port for **LIVE trading** is **7497**.

### Port Configuration
- **Port 7496**: Paper Trading (TWS/Gateway)
- **Port 7497**: **LIVE Trading** ✅ (Correct)

### Changes Made

1. **Updated `launch_ultimate_prometheus_LIVE_TRADING.py`**:
   - Changed `self.ib_port = 7496` → `self.ib_port = 7497`
   - Updated comment: `# 7497 for LIVE trading`

2. **IB Broker Configuration**:
   - Now correctly uses port 7497 for live trading
   - Account: U21922116
   - Client ID: 7777

### Next Steps

1. **Ensure IB Gateway is running on port 7497**:
   - Start IB Gateway (not TWS)
   - Configure to listen on port 7497
   - Enable API connections
   - Log in with account U21922116

2. **Restart the trading system**:

   ```bash

   python launch_ultimate_prometheus_LIVE_TRADING.py

   ```

3. **Verify Connection**:
   - Check logs for "Connected to IB at 127.0.0.1:7497"
   - System should now connect to IB for live trading

### IB Gateway Configuration

**Settings to verify in IB Gateway:**

- **API Settings** → Enable ActiveX and Socket Clients
- **Socket Port**: 7497 (for LIVE trading)
- **Trusted IPs**: 127.0.0.1
- **Read-Only API**: Unchecked (for trading)

---

**Status**: ✅ Port corrected to 7497 for live trading

