# External Terminal Restart - Updated ✅

## Changes Made

### ✅ Always Opens in External Terminal

The restart script now **always** opens the trading system in a **new external terminal window** so you can see all output.

### How It Works

1. **Stops all old processes** - Clean restart
2. **Verifies configuration** - Checks all API keys and settings
3. **Opens new terminal window** - External window titled "Prometheus Trading System"
4. **Shows all output** - You can see everything in real-time

### What You Should See

**A new terminal window** should open with the title:

```
```text
Prometheus Trading System

```

**In that window**, you'll see:

- System initialization messages
- All broker connection attempts
- Trading cycle activity
- Real-time status updates

### Quick Restart Options

#### Option 1: Python Script (Recommended)

```bash

python full_system_restart.py

```
```text

- Stops all processes
- Verifies configuration
- Opens in external terminal

#### Option 2: Batch File (Quick)

```bash

restart_external_terminal.bat

```
```text

- Double-click to run
- Quick restart in external terminal

### What to Look For in the Terminal

1. **Initialization** (0-30 seconds):

   ```
```text
   INITIALIZING ALL SYSTEMS
   TIER 1: CRITICAL SYSTEMS
   TIER 2: REVOLUTIONARY CORE
   TIER 3: DATA INTELLIGENCE SOURCES
   TIER 4: LIVE BROKER CONNECTIONS

   ```

2. **Broker Connections** (30-60 seconds):

   ```
```text
   ✅ Connected to Alpaca - Account Status: ACTIVE
   Connecting to IB at 127.0.0.1:7497
   Interactive Brokers Live (Account: U21922116)

   ```

3. **Trading Activity** (After initialization):

   ```
```text
   Starting trading cycle...
   Analyzing X crypto symbols (24/7 trading)
   AI Signal for SYMBOL: BUY (Confidence: 67%)
   Trade executed for SYMBOL

   ```

### If You Don't See the Window

1. **Check Taskbar** - Window might be minimized
2. **Check Alt+Tab** - Switch between windows
3. **Check Processes**:

   ```powershell

   Get-Process python | Where-Object {$_.MainWindowTitle -like "*Prometheus*"}

   ```

### Troubleshooting

**Window doesn't open:**

- Run: `python full_system_restart.py` again
- Or use: `restart_external_terminal.bat`

**Can't see output:**

- The window should be visible
- Check if it's behind other windows
- Look for "Prometheus Trading System" in taskbar

**Want to restart:**

- Close the terminal window
- Run restart script again
- New window will open

---

## Summary

✅ **External Terminal**: Always used  
✅ **Visible Output**: All messages shown  
✅ **Easy Monitoring**: Watch real-time activity  

**Status**: System configured to always restart in external terminal window!

