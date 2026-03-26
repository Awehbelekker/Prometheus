# 🚀 Advanced Trading Monitor - Quick Start Guide

## What This System Does

The **Advanced Trading Monitor** is a sophisticated real-time monitoring system that:

✅ **Continuously monitors all open positions** (24/7 for crypto)  
✅ **Automatically closes positions** when conditions are met  
✅ **Records P&L accurately** for performance tracking  
✅ **Implements multiple exit strategies** (stop loss, take profit, trailing stops)  
✅ **Provides real-time analytics** and reporting  

---

## Quick Start

### 1. Start the Monitor (Primary System)

```bash
# Run the advanced monitor (runs forever until stopped)
python advanced_trading_monitor.py
```

**What it does:**
- Checks all positions every 5 seconds
- Executes exits when conditions met
- Logs everything to file and console
- Shows status report every 5 minutes

**Exit Conditions:**
- ❌ **Stop Loss:** -3% (closes immediately)
- ✅ **Take Profit:** +8% (closes immediately)
- 📈 **Trailing Stop:** 2.5% below highest price (after 4% profit)
- ⏰ **Time Exit:** After 48 hours in position
- 🛡️ **Risk Management:** Early exit if losing momentum

### 2. View Dashboard (Optional - Separate Terminal)

```bash
# Run the dashboard in a separate terminal
python trading_monitor_dashboard.py
```

**What it shows:**
- Real-time position count
- 24-hour P&L
- All-time performance
- Recent exits
- Top symbols
- Win rate statistics

---

## System Features

### Intelligent Exit Logic

The monitor uses **5 different exit strategies**:

#### 1. Stop Loss (-3%)
```
Position down 3% or more → CLOSE IMMEDIATELY
Protects against large losses
```

#### 2. Take Profit (+8%)
```
Position up 8% or more → CLOSE IMMEDIATELY
Locks in profits at target
```

#### 3. Trailing Stop (2.5%)
```
After position is up 4%:
- Tracks highest price seen
- If price drops 2.5% from high → CLOSE
- Protects profits while letting winners run
```

**Example:**
- Entry: $100
- Price rises to $108 (+8%)
- Take profit NOT hit yet (need +8% = $108)
- Price rises to $110 (+10%)
- Trailing stop activates at $107.25 (2.5% below $110)
- If price drops to $107.25 → CLOSE with +7.25% profit locked in

#### 4. Time Exit (48 hours)
```
Position held > 48 hours → CLOSE
Prevents capital being tied up too long
Exits regardless of profit/loss
```

#### 5. Risk Management (Early Exit)
```
Position losing between -1.5% and -2.5%:
- If momentum is against us → CLOSE EARLY
- Cuts losses before hitting full stop loss
- Prevents small losses becoming big losses
```

### Real-Time Monitoring

```
Every 5 seconds:
1. Fetch all open positions from database
2. Get current price for each
3. Check all 5 exit conditions
4. Close position if any condition met
5. Record P&L and update statistics
6. Log results
```

### Performance Tracking

The system tracks:
- Total positions closed
- Win rate
- Total P&L
- Average profit/loss per trade
- Best and worst trades
- Exit type breakdown (stop loss, take profit, etc.)
- Time in positions
- Errors encountered

---

## What This Fixes

### Problem Before
```
400 trades executed → ALL stuck in "pending" status
No exits, no P&L, can't measure performance
```

### Solution After
```
Monitor runs 24/7 → Exits execute automatically
P&L recorded → Win rate calculated
Performance visible → Can optimize system
```

---

## Usage Examples

### Run Monitor for 24 Hours
```python
# Edit advanced_trading_monitor.py, line 666:
await monitor.run(duration_hours=24)  # Run for 24 hours then stop
```

### Run Monitor Forever (Default)
```python
# Edit advanced_trading_monitor.py, line 666:
await monitor.run()  # Run until Ctrl+C
```

### Customize Settings
```python
monitor = AdvancedTradingMonitor(
    db_path='prometheus_learning.db',
    check_interval=3,  # Check every 3 seconds (faster)
    stop_loss_pct=0.04,  # 4% stop loss (wider)
    take_profit_pct=0.10,  # 10% take profit (wider)
    trailing_stop_pct=0.03,  # 3% trailing stop
    max_position_time_hours=72.0,  # Close after 3 days
    enable_trailing_stop=True,
    enable_time_exits=True,
    enable_risk_management=True
)
```

---

## Monitoring Output

### Console Output Example
```
2025-12-15 15:30:45 - INFO - 🚀 Starting Advanced Trading Monitor
2025-12-15 15:30:45 - INFO -    Check interval: 5 seconds
2025-12-15 15:30:45 - INFO -    Duration: Continuous (Ctrl+C to stop)
2025-12-15 15:30:50 - INFO - 🔍 Monitoring 12 positions...
2025-12-15 15:30:50 - INFO - 🎯 EXIT SIGNAL: BTCUSD
2025-12-15 15:30:50 - INFO - 💰 CLOSED: BTCUSD | TAKE_PROFIT
2025-12-15 15:30:50 - INFO -    Entry: $42000.00 → Exit: $45360.00
2025-12-15 15:30:50 - INFO -    P&L: $336.00 (+8.0%)
2025-12-15 15:30:50 - INFO -    Reason: Take profit triggered: 8.00% >= 8.0%
2025-12-15 15:30:50 - INFO -    Time in position: 4.2 hours
2025-12-15 15:30:50 - INFO - ✅ Successfully closed BTCUSD
```

### Status Report (Every 5 Minutes)
```
================================================================================
📊 ADVANCED TRADING MONITOR - STATUS REPORT
================================================================================
⏱️  Uptime: 2.5 hours (150 minutes)
🔄 Monitoring Cycles: 1800
📈 Positions Monitored: 12
🎯 Positions Closed: 45

💰 EXIT STATISTICS:
   Stop Losses: 12
   Take Profits: 28
   Trailing Stops: 3
   Time Exits: 1
   Risk Management Exits: 1

📊 PERFORMANCE:
   Total P&L: $234.50
   Winning Trades: 28
   Losing Trades: 17
   Win Rate: 62.2%
   Avg Win: $12.45

⚠️  Errors Encountered: 0
================================================================================
```

---

## Log Files

The monitor creates log files automatically:

```
trading_monitor_20251215.log  # Today's log
```

**Log contents:**
- All monitoring cycles
- Every position check
- All exits with details
- Errors and warnings
- Status reports

---

## Recommended Setup

### Option A: Single Screen
1. Open one terminal
2. Run: `python advanced_trading_monitor.py`
3. Let it run 24/7
4. Check log file for detailed history

### Option B: Two Screens (Recommended)
1. **Terminal 1:** Run monitor
   ```bash
   python advanced_trading_monitor.py
   ```

2. **Terminal 2:** Run dashboard
   ```bash
   python trading_monitor_dashboard.py
   ```

This gives you:
- Real-time exit execution (Terminal 1)
- Live performance dashboard (Terminal 2)

### Option C: Background Service
```bash
# Run monitor in background (Linux/Mac)
nohup python advanced_trading_monitor.py > monitor.out 2>&1 &

# Check if running
ps aux | grep advanced_trading_monitor

# View live output
tail -f monitor.out

# Stop monitor
pkill -f advanced_trading_monitor
```

---

## Testing the System

### 1. Check Current Positions
```bash
python -c "import sqlite3; conn = sqlite3.connect('prometheus_learning.db'); cursor = conn.cursor(); cursor.execute('SELECT symbol, side, quantity, entry_price, unrealized_pl FROM open_positions'); print('\n'.join([str(row) for row in cursor.fetchall()])); conn.close()"
```

### 2. Manually Close One Position (for testing)
```python
# test_close_position.py
import sqlite3
conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# Close first position for testing
cursor.execute("DELETE FROM open_positions WHERE id = (SELECT MIN(id) FROM open_positions)")
print(f"Deleted {cursor.rowcount} position")

conn.commit()
conn.close()
```

### 3. View Recent Exits
```bash
python -c "import sqlite3; conn = sqlite3.connect('prometheus_learning.db'); cursor = conn.cursor(); cursor.execute('SELECT symbol, exit_timestamp, profit_loss, status FROM trade_history WHERE status=\"closed\" ORDER BY exit_timestamp DESC LIMIT 10'); print('\n'.join([str(row) for row in cursor.fetchall()])); conn.close()"
```

---

## Troubleshooting

### Monitor Not Finding Positions
```
Problem: "No open positions to monitor"
Solution: 
- Check if positions exist: SELECT COUNT(*) FROM open_positions;
- Verify database path is correct
- Make sure trades are in 'pending' status
```

### Positions Not Closing
```
Problem: Exit conditions met but position stays open
Solution:
- Check log file for error messages
- Verify database permissions
- Check if prices are updating correctly
```

### High CPU Usage
```
Problem: Monitor using too much CPU
Solution:
- Increase check_interval from 5 to 10 seconds
- Reduce number of positions being monitored
```

---

## Next Steps

1. **Start the monitor** and let it run for 24 hours
2. **Check the logs** to see what's happening
3. **Review performance** after a day
4. **Adjust settings** based on results:
   - If too many stop losses → widen stop loss
   - If missing profits → tighten take profit
   - If positions held too long → reduce max_position_time_hours

---

## Support

If you encounter issues:
1. Check the log file: `trading_monitor_YYYYMMDD.log`
2. Look for error messages
3. Verify database structure is correct
4. Make sure positions table exists

---

**Ready to start? Run:** `python advanced_trading_monitor.py`
