"""
COMPREHENSIVE SOLUTIONS FOR PROMETHEUS TRADING PLATFORM ISSUES
Fixes: 1) Alpaca broker issues  2) IB position analysis  3) Terminal display
"""

## ==============================================================================
## ISSUE 1: ALPACA BROKER PROBLEMS
## ==============================================================================

### DIAGNOSED PROBLEMS:
1. ❌ ALPACA_API_KEY not set in environment
2. ❌ ALPACA_SECRET_KEY not set in environment
3. ⚠️  Missing 'place_order' alias method in AlpacaBroker class
4. ⚠️  Current crypto positions showing losses (-7% to -13%)

### SOLUTION 1A: Set API Keys

```powershell
# Set Alpaca API keys in PowerShell (temporary - current session only)
$env:ALPACA_API_KEY = "YOUR_ALPACA_API_KEY_HERE"
$env:ALPACA_SECRET_KEY = "YOUR_ALPACA_SECRET_KEY_HERE"

# OR set permanently for user:
[System.Environment]::SetEnvironmentVariable('ALPACA_API_KEY', 'YOUR_KEY_HERE', 'User')
[System.Environment]::SetEnvironmentVariable('ALPACA_SECRET_KEY', 'YOUR_SECRET_HERE', 'User')

# Restart PowerShell after setting permanent variables
```

### SOLUTION 1B: Fix place_order Method

The AlpacaBroker class has `submit_order` but improved_dual_broker_trading.py calls `place_order`.

**OPTION 1: Add alias to AlpacaBroker (RECOMMENDED)**
Add this method to brokers/alpaca_broker.py:

```python
async def place_order(self, symbol: str, qty: float, side: str, 
                     order_type: str = 'market', time_in_force: str = 'gtc',
                     limit_price: float = None, stop_price: float = None) -> Any:
    """
    Alias for submit_order to maintain compatibility
    """
    # Create Order object
    from .universal_broker_interface import Order, OrderSide, OrderType
    
    order = Order(
        symbol=symbol,
        quantity=qty,
        side=OrderSide(side.lower()),
        order_type=OrderType(order_type.lower()),
        price=limit_price,
        stop_price=stop_price,
        time_in_force=time_in_force
    )
    
    # Use existing submit_order method
    return await self.submit_order(order)
```

**OPTION 2: Update improved_dual_broker_trading.py**
Change line ~870 from:
```python
order = await self.alpaca_broker.place_order(...)
```
To:
```python
order = await self.alpaca_broker.submit_order(Order(...))
```

### SOLUTION 1C: Crypto Position Management

Your Alpaca crypto positions are down:
- BTCUSD: -7.40%
- ETHUSD: -13.03%  
- SOLUSD: -12.93%

**Recommendations:**
1. **HOLD**: These are within normal crypto volatility. Your config has DCA enabled.
2. **SET ALERTS**: Stop losses are at -15%, monitor closely
3. **WAIT FOR RECOVERY**: Crypto markets are volatile, positions may recover
4. **REVIEW STRATEGY**: Consider tighter stop losses (e.g., -10%) for future trades

---

## ==============================================================================
## ISSUE 2: IB RANDOM POSITION
## ==============================================================================

### DIAGNOSED PROBLEMS:
1. ❌ Cannot connect to IB on port 7496 - TWS/Gateway not running
2. ⚠️  Unable to retrieve current positions (need IB connection)

### SOLUTION 2A: Start IB Gateway/TWS

**Step 1: Start IB Gateway or TWS**
1. Open IB Gateway (or Trader Workstation)
2. Login with your credentials
3. Go to Settings → API → Settings
4. Enable "Enable ActiveX and Socket Clients"
5. Set Socket port: 7496
6. Uncheck "Read-Only API"
7. Check "Allow connections from localhost only"
8. Click OK and restart Gateway

**Step 2: Verify Connection**
```powershell
# Test if port 7496 is listening
Test-NetConnection -ComputerName localhost -Port 7496
```

### SOLUTION 2B: Analyze IB Position (Once Connected)

```python
# Run this script to identify the random position
python -c "
import asyncio
from brokers.interactive_brokers_broker import InteractiveBrokersBroker

async def check_positions():
    config = {
        'account_id': 'U21922116',
        'host': '127.0.0.1',
        'port': 7496,
        'client_id': 7777
    }
    broker = InteractiveBrokersBroker(config)
    connected = await broker.connect()
    
    if connected:
        await asyncio.sleep(3)  # Wait for data
        
        if hasattr(broker, 'positions_data'):
            print('CURRENT IB POSITIONS:')
            for symbol, pos in broker.positions_data.items():
                print(f'{symbol}: {pos[\"quantity\"]} @ ${pos[\"avg_price\"]:.2f}')
        else:
            print('No positions found')
        
        await broker.disconnect()
    else:
        print('Cannot connect to IB')

asyncio.run(check_positions())
"
```

### SOLUTION 2C: Position Decision Matrix

**IF POSITION IS PROFITABLE (+5% or more):**
- ✅ HOLD and set trailing stop at -3% from high
- ✅ Scale out 50% at +10%, rest at +15%
- ✅ Let the system manage it automatically

**IF POSITION IS FLAT (-2% to +2%):**
- ⚠️  Review why it was bought (check logs)
- ⚠️  If not in watchlist, consider closing
- ⚠️  Set tight stop loss at -5%

**IF POSITION IS LOSING (-5% or more):**
- ❌ Close immediately if not in strategy
- ❌ Or set very tight stop at -3% more
- ❌ Review trading logs to prevent recurrence

---

## ==============================================================================
## ISSUE 3: TERMINAL DISPLAY & LOGGING
## ==============================================================================

### DIAGNOSED PROBLEMS:
1. ❌ Unicode/Emoji rendering issues (UnicodeDecodeError)
2. ⚠️  Poor logging format (not enough information)
3. ⚠️  No real-time status dashboard
4. ⚠️  Missing color-coded output
5. ⚠️  No position tracking in display

### SOLUTION 3A: Fix Unicode/Emoji Issues

**Fix 1: Update file reading to handle encoding**
```python
# When reading files, specify encoding:
with open('file.py', 'r', encoding='utf-8') as f:
    content = f.read()
```

**Fix 2: Set Windows terminal to UTF-8**
```powershell
# Run this before starting trading:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

### SOLUTION 3B: Enhanced Logging Format

**Install Rich Console Library:**
```powershell
pip install rich
```

**Enhanced Logging Code (add to improved_dual_broker_trading.py):**

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box

console = Console()

def print_status_dashboard(self):
    \"\"\"Print beautiful status dashboard\"\"\"
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    
    # Header
    header_text = Text(f"PROMETHEUS TRADING PLATFORM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       justify="center", style="bold magenta")
    layout["header"].update(Panel(header_text))
    
    # Body - Split into sections
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    # Left: Account Status
    account_table = Table(title="💰 Account Status", box=box.ROUNDED)
    account_table.add_column("Broker", style="cyan")
    account_table.add_column("Balance", style="green")
    account_table.add_column("Positions", style="yellow")
    
    account_table.add_row("IB", f"${self.ib_capital:.2f}", str(len(self.ib_positions)))
    account_table.add_row("Alpaca", f"${self.alpaca_capital:.2f}", str(len(self.alpaca_positions)))
    account_table.add_row("[bold]TOTAL", f"[bold]${self.total_capital:.2f}", 
                          f"[bold]{len(self.ib_positions) + len(self.alpaca_positions)}")
    
    layout["left"].update(account_table)
    
    # Right: Positions
    pos_table = Table(title="📈 Current Positions", box=box.ROUNDED)
    pos_table.add_column("Symbol", style="cyan")
    pos_table.add_column("Qty", style="white")
    pos_table.add_column("Entry", style="blue")
    pos_table.add_column("Current", style="blue")
    pos_table.add_column("P&L", style="white")
    
    for symbol, pos_data in self.all_positions.items():
        qty = pos_data['quantity']
        entry = pos_data['entry_price']
        current = pos_data['current_price']
        pnl_pct = ((current - entry) / entry * 100) if entry > 0 else 0
        
        pnl_style = "green" if pnl_pct > 0 else "red"
        pos_table.add_row(
            symbol,
            f"{qty:.4f}",
            f"${entry:.2f}",
            f"${current:.2f}",
            f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]"
        )
    
    layout["right"].update(pos_table)
    
    # Footer: Trading Stats
    stats_text = (f"Trades Today: {self.total_trades_today}/{self.max_trades_per_day} | "
                  f"Profit: ${self.today_profit:+.2f} | "
                  f"Win Rate: {self.win_rate:.1%} | "
                  f"Confidence Threshold: {self.min_confidence_threshold:.0%}")
    layout["footer"].update(Panel(Text(stats_text, justify="center", style="bold cyan")))
    
    console.print(layout)
```

### SOLUTION 3C: Color-Coded Log Levels

```python
import logging
from rich.logging import RichHandler

# Setup Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

# Usage with colors:
logger.info("[green]✅ Trade executed successfully[/green]")
logger.warning("[yellow]⚠️  Position approaching stop loss[/yellow]")
logger.error("[red]❌ Connection failed[/red]")
```

### SOLUTION 3D: Real-Time Monitoring

```python
async def live_monitoring_loop(self):
    \"\"\"Real-time status updates with Rich Live Display\"\"\"
    from rich.live import Live
    
    with Live(self.generate_dashboard(), refresh_per_second=1, console=console) as live:
        while self.running:
            # Update dashboard every second
            live.update(self.generate_dashboard())
            await asyncio.sleep(1)

def generate_dashboard(self):
    \"\"\"Generate dashboard for live display\"\"\"
    # Return the layout object from print_status_dashboard
    # This refreshes every second with latest data
    return layout
```

---

## ==============================================================================
## IMPLEMENTATION CHECKLIST
## ==============================================================================

### Phase 1: Critical Fixes (Do First)
- [ ] Set Alpaca API keys in environment
- [ ] Add place_order alias to AlpacaBroker
- [ ] Start IB Gateway/TWS on port 7496
- [ ] Test both broker connections

### Phase 2: Position Management
- [ ] Connect to IB and identify random position
- [ ] Analyze position P&L and decision
- [ ] Set appropriate stop losses
- [ ] Review Alpaca crypto positions

### Phase 3: Terminal Display (Optional but Recommended)
- [ ] Install rich library
- [ ] Update logging configuration
- [ ] Add status dashboard function
- [ ] Implement color-coded output
- [ ] Add real-time monitoring display

### Phase 4: Testing
- [ ] Run diagnostic script again
- [ ] Verify all connections
- [ ] Test order placement
- [ ] Confirm dashboard displays correctly

---

## ==============================================================================
## QUICK START COMMANDS
## ==============================================================================

```powershell
# 1. Set API keys (replace with your actual keys)
$env:ALPACA_API_KEY = "YOUR_KEY_HERE"
$env:ALPACA_SECRET_KEY = "YOUR_SECRET_HERE"

# 2. Install rich library
pip install rich

# 3. Run diagnostic
python diagnose_all_issues.py

# 4. Start trading with enhanced display
python improved_dual_broker_trading.py

# 5. Monitor positions
python check_positions.py
```

## ==============================================================================
## SUPPORT & DEBUGGING
## ==============================================================================

If issues persist:
1. Check logs in: autonomous_overnight.log, background_trading.log
2. Review config files: dual_broker_config.json, alpaca_crypto_optimal_config.json
3. Verify network connectivity to both brokers
4. Ensure IB Gateway is running and configured properly
5. Check Windows terminal supports UTF-8 encoding

For detailed diagnostics, run: python diagnose_all_issues.py

---

## SUMMARY OF FIXES

✅ **Alpaca Issues**: Set API keys + add place_order alias
✅ **IB Position**: Start IB Gateway + analyze position when connected
✅ **Terminal Display**: Install Rich + add dashboard + fix encoding

**ESTIMATED FIX TIME**: 15-30 minutes
**IMPACT**: Resolves all three critical issues
**RISK**: Low - all changes are additions/configuration, no core logic changes
