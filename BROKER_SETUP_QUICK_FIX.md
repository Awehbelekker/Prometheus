# 🔧 Broker Setup Quick Fix

## Issues Found:
1. **Alpaca**: "request is not authorized" - API keys issue
2. **IB**: Port 7497 not accessible - TWS/Gateway not running

---

## Fix Alpaca (2 minutes):

### Option 1: Check Your .env File
Open `.env` and verify:
```bash
ALPACA_API_KEY=PK...  # Should start with PK for paper trading
ALPACA_SECRET_KEY=...  # Your secret key
```

### Option 2: Get New API Keys (If Needed)
1. Go to: https://app.alpaca.markets/paper/dashboard/overview
2. Click "View" or "Generate" API Keys
3. Copy BOTH keys
4. Update `.env` file

### Option 3: Quick Test
```bash
# Check if keys are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('ALPACA_API_KEY')[:10] if os.getenv('ALPACA_API_KEY') else 'MISSING')"
```

---

## Fix IB (Interactive Brokers):

### If You Want to Use IB:
1. **Install TWS or IB Gateway**
   - Download: https://www.interactivebrokers.com/en/trading/tws.php
   
2. **Start TWS/Gateway**
   - Launch the application
   - Enable API connections: Configure > API > Settings
   - Check "Enable ActiveX and Socket Clients"
   - Note the port (usually 7497 for paper, 7496 for live)

3. **Update .env**
```bash
IB_HOST=127.0.0.1
IB_PORT=7497  # Paper trading
```

### If You Don't Need IB:
Just use Alpaca! It's simpler and supports stocks + crypto.

---

## Quick Action Plan:

### If You Have Valid Alpaca Keys:
```bash
# Just fix the .env and test again
python test_broker_connections.py
```

### If You Need New Alpaca Keys:
1. Go to Alpaca paper trading dashboard
2. Generate new API keys
3. Update .env
4. Run: `python test_broker_connections.py`

Once ONE broker shows "[OK] READY", you're good to go!

---

## After Brokers Are Ready:

I'll integrate the autonomous system with your existing broker code.
No new files needed - I'll just modify:
- `core/multi_strategy_executor.py` (add broker calls)
- `core/profit_maximization_engine.py` (add execution)

**Total: ~50 lines of code to connect everything!**
