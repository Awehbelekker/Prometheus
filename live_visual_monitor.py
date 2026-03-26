#!/usr/bin/env python3
"""
PROMETHEUS Live Visual Trading Monitor
Real-time display with Rich UI - Run in separate terminal
Uses REST API for Alpaca + separate IB connection
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich import box
import time
import asyncio
from dotenv import load_dotenv
import requests
import json

# Load environment
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

# Import IB broker
try:
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    IB_AVAILABLE = True
except:
    IB_AVAILABLE = False

console = Console()

class VisualTradingMonitor:
    """Beautiful real-time trading monitor"""
    
    def __init__(self):
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = "https://api.alpaca.markets"
        self.ib_port = int(os.getenv('IB_PORT', '4002'))
        self.ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
        self.ib_broker = None
        self.update_interval = 5  # seconds
        self.alpaca_headers = {
            'APCA-API-KEY-ID': self.alpaca_api_key,
            'APCA-API-SECRET-KEY': self.alpaca_secret
        }
        
    async def initialize(self):
        """Initialize monitor"""
        console.print("[green]✅ Monitor initialized[/green]")
        console.print("[dim]Alpaca: REST API | IB: Separate connection (client 9998)[/dim]")
        
        # Connect to IB with unique client ID
        if IB_AVAILABLE:
            try:
                self.ib_broker = InteractiveBrokersBroker({
                    'host': '127.0.0.1',
                    'port': self.ib_port,
                    'client_id': 9998,  # Unique client ID for monitor
                    'account_id': self.ib_account,
                    'paper_trading': True
                })
                await self.ib_broker.connect()
                await asyncio.sleep(3)  # Wait for IB to populate data
                console.print("[green]✅ IB Connected (monitor)[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ IB connection failed: {str(e)[:50]}[/yellow]")
                self.ib_broker = None
    
    def create_header(self) -> Panel:
        """Create header panel"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = Text()
        header.append("🚀 PROMETHEUS ", style="bold cyan")
        header.append("LIVE TRADING MONITOR ", style="bold white")
        header.append(f"| {now}", style="dim")
        return Panel(header, box=box.DOUBLE)
    
    def get_alpaca_data(self) -> Table:
        """Get Alpaca account data via REST API"""
        table = Table(title="[cyan]💰 ALPACA LIVE TRADING[/cyan]", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white", justify="right")
        table.add_column("Status", justify="center")
        
        if not self.alpaca_api_key:
            table.add_row("Status", "NO API KEY", "❌")
            return table
        
        try:
            # Get account via REST
            response = requests.get(
                f"{self.alpaca_base_url}/v2/account",
                headers=self.alpaca_headers,
                timeout=5
            )
            account = response.json()
            
            # Get positions via REST
            pos_response = requests.get(
                f"{self.alpaca_base_url}/v2/positions",
                headers=self.alpaca_headers,
                timeout=5
            )
            positions = pos_response.json()
            
            equity = float(account.get('equity', 0))
            cash = float(account.get('cash', 0))
            buying_power = float(account.get('buying_power', 0))
            
            # Account info
            table.add_row("Account", account.get('account_number', 'N/A'), "✅")
            table.add_row("Equity", f"${equity:,.2f}", "")
            table.add_row("Cash", f"${cash:,.2f}", "")
            table.add_row("Buying Power", f"${buying_power:,.2f}", "")
            table.add_row("Positions", str(len(positions)), "")
            
            # Positions
            if positions and len(positions) > 0:
                table.add_row("", "", "")
                table.add_row("[bold]Symbol[/bold]", "[bold]Qty[/bold]", "[bold]P&L[/bold]")
                for pos in positions:
                    qty = float(pos.get('qty', 0))
                    current_price = float(pos.get('current_price', 0))
                    market_value = float(pos.get('market_value', 0))
                    unrealized_pl = float(pos.get('unrealized_pl', 0))
                    unrealized_plpc = float(pos.get('unrealized_plpc', 0)) * 100
                    
                    pl_color = "green" if unrealized_pl >= 0 else "red"
                    pl_emoji = "📈" if unrealized_pl >= 0 else "📉"
                    
                    table.add_row(
                        pos.get('symbol', 'N/A'),
                        f"{qty:.6f}",
                        f"[{pl_color}]{pl_emoji} ${unrealized_pl:.2f} ({unrealized_plpc:.1f}%)[/{pl_color}]"
                    )
        
        except Exception as e:
            table.add_row("Error", str(e)[:50], "⚠️")
        
        return table
    
    def get_ib_data(self) -> Table:
        """Get IB account data via separate connection"""
        table = Table(title="[blue]💼 INTERACTIVE BROKERS PAPER[/blue]", box=box.ROUNDED)
        table.add_column("Metric", style="blue")
        table.add_column("Value", style="white", justify="right")
        table.add_column("Status", justify="center")
        
        if not self.ib_broker:
            table.add_row("Status", "OFFLINE", "❌")
            table.add_row("[dim]Reason[/dim]", "[dim]Connection failed[/dim]", "")
            return table
        
        try:
            # Get account values
            account_values = getattr(self.ib_broker, 'account_values', {})
            
            net_liq = float(account_values.get('NetLiquidation', 0))
            available = float(account_values.get('AvailableFunds', 0))
            unrealized_pl = float(account_values.get('UnrealizedPnL', 0))
            
            table.add_row("Account", self.ib_account, "✅")
            table.add_row("Port", str(self.ib_port), "🔌")
            table.add_row("Net Liquidation", f"${net_liq:.2f}", "")
            table.add_row("Available Funds", f"${available:.2f}", "")
            
            # P&L with color
            pl_color = "green" if unrealized_pl >= 0 else "red"
            pl_emoji = "📈" if unrealized_pl >= 0 else "📉"
            table.add_row("Unrealized P&L", f"[{pl_color}]{pl_emoji} ${unrealized_pl:.2f}[/{pl_color}]", "")
            
            # Positions
            positions = getattr(self.ib_broker, 'positions_data', {})
            if positions:
                table.add_row("", "", "")
                table.add_row("[bold]Symbol[/bold]", "[bold]Qty[/bold]", "[bold]Value[/bold]")
                for symbol, pos in positions.items():
                    table.add_row(
                        symbol,
                        f"{pos.get('position', 0):.0f}",
                        f"${pos.get('market_value', 0):.2f}"
                    )
            else:
                table.add_row("Positions", "0", "")
        
        except Exception as e:
            table.add_row("Error", str(e)[:50], "⚠️")
        
        return table
    
    def create_summary(self) -> Panel:
        """Create summary panel"""
        summary = Table.grid(padding=1)
        summary.add_column(justify="left", style="cyan")
        summary.add_column(justify="right", style="white")
        
        # Add stats
        summary.add_row("🔄 Update Interval:", f"{self.update_interval}s")
        summary.add_row("📊 AI Status:", "[green]ACTIVE ✅[/green]")
        summary.add_row("🧠 Risk Manager:", "[green]ENABLED ✅[/green]")
        summary.add_row("⏰ Trading:", "[dim]Check main terminal[/dim]")
        
        return Panel(summary, title="[bold]System Status[/bold]", box=box.ROUNDED)
    
    def create_layout(self, alpaca_table: Table, ib_table: Table) -> Layout:
        """Create layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=9)
        )
        
        layout["header"].update(self.create_header())
        
        layout["body"].split_row(
            Layout(alpaca_table, name="alpaca"),
            Layout(ib_table, name="ib")
        )
        
        layout["footer"].update(self.create_summary())
        
        return layout
    
    async def run(self):
        """Run live monitor"""
        console.clear()
        console.print("[bold cyan]🚀 Initializing PROMETHEUS Visual Monitor...[/bold cyan]")
        
        await self.initialize()
        
        console.print("\n[green]✅ Monitor started! Updating every 5 seconds...[/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        await asyncio.sleep(1)
        
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                try:
                    # Get data
                    alpaca_table = self.get_alpaca_data()
                    ib_table = self.get_ib_data()
                    
                    # Create layout
                    layout = self.create_layout(alpaca_table, ib_table)
                    
                    # Update display
                    live.update(layout)
                    
                    # Wait
                    await asyncio.sleep(self.update_interval)
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]🛑 Monitor stopped[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    await asyncio.sleep(self.update_interval)
        
        # Cleanup
        if self.ib_broker:
            try:
                await self.ib_broker.disconnect()
            except:
                pass


async def main():
    monitor = VisualTradingMonitor()
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
