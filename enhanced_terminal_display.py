#!/usr/bin/env python3
"""
Enhanced Terminal Display Module for PROMETHEUS Trading Platform
Provides rich, color-coded, real-time trading dashboard
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
import logging

# Configure Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)

console = Console()


class TradingDashboard:
    """Enhanced trading dashboard with Rich terminal UI"""
    
    def __init__(self):
        self.console = console
        self.last_update = datetime.now()
        
    def create_header(self) -> Panel:
        """Create dashboard header"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header_text = Text()
        header_text.append("🚀 PROMETHEUS", style="bold magenta")
        header_text.append(" TRADING PLATFORM ", style="bold white")
        header_text.append(f"| {current_time}", style="bold cyan")
        
        return Panel(header_text, box=box.DOUBLE, style="bold blue")
    
    def create_account_table(self, account_data: Dict[str, Any]) -> Table:
        """Create account status table"""
        table = Table(title="💰 Account Status", box=box.ROUNDED, show_header=True)
        table.add_column("Broker", style="cyan", width=15)
        table.add_column("Balance", style="green", justify="right", width=15)
        table.add_column("Equity", style="green", justify="right", width=15)
        table.add_column("Buying Power", style="yellow", justify="right", width=15)
        table.add_column("Positions", style="white", justify="center", width=10)
        
        # IB Account
        ib_data = account_data.get('ib', {})
        table.add_row(
            "Interactive Brokers",
            f"${ib_data.get('cash', 0):.2f}",
            f"${ib_data.get('equity', 0):.2f}",
            f"${ib_data.get('buying_power', 0):.2f}",
            str(ib_data.get('position_count', 0))
        )
        
        # Alpaca Account
        alpaca_data = account_data.get('alpaca', {})
        table.add_row(
            "Alpaca",
            f"${alpaca_data.get('cash', 0):.2f}",
            f"${alpaca_data.get('equity', 0):.2f}",
            f"${alpaca_data.get('buying_power', 0):.2f}",
            str(alpaca_data.get('position_count', 0))
        )
        
        # Total
        total_cash = ib_data.get('cash', 0) + alpaca_data.get('cash', 0)
        total_equity = ib_data.get('equity', 0) + alpaca_data.get('equity', 0)
        total_buying_power = ib_data.get('buying_power', 0) + alpaca_data.get('buying_power', 0)
        total_positions = ib_data.get('position_count', 0) + alpaca_data.get('position_count', 0)
        
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]${total_cash:.2f}[/bold]",
            f"[bold]${total_equity:.2f}[/bold]",
            f"[bold]${total_buying_power:.2f}[/bold]",
            f"[bold]{total_positions}[/bold]",
            style="bold white"
        )
        
        return table
    
    def create_positions_table(self, positions: List[Dict[str, Any]]) -> Table:
        """Create positions table"""
        table = Table(title="📈 Current Positions", box=box.ROUNDED, show_header=True)
        table.add_column("Broker", style="cyan", width=8)
        table.add_column("Symbol", style="cyan bold", width=10)
        table.add_column("Qty", style="white", justify="right", width=12)
        table.add_column("Entry", style="blue", justify="right", width=12)
        table.add_column("Current", style="blue", justify="right", width=12)
        table.add_column("P&L $", style="white", justify="right", width=12)
        table.add_column("P&L %", style="white", justify="right", width=10)
        
        if not positions:
            table.add_row("—", "No positions", "—", "—", "—", "—", "—")
            return table
        
        total_pnl = 0
        for pos in positions:
            broker = pos.get('broker', 'Unknown')
            symbol = pos.get('symbol', 'N/A')
            qty = pos.get('quantity', 0)
            entry = pos.get('entry_price', 0)
            current = pos.get('current_price', 0)
            
            if entry > 0 and current > 0:
                pnl_dollar = (current - entry) * qty
                pnl_pct = ((current - entry) / entry * 100)
                total_pnl += pnl_dollar
                
                # Color code based on P&L
                if pnl_pct > 5:
                    pnl_style = "bold green"
                elif pnl_pct > 0:
                    pnl_style = "green"
                elif pnl_pct > -5:
                    pnl_style = "yellow"
                else:
                    pnl_style = "bold red"
                
                table.add_row(
                    broker,
                    symbol,
                    f"{qty:.6f}" if qty < 1 else f"{qty:.2f}",
                    f"${entry:.2f}",
                    f"${current:.2f}",
                    f"[{pnl_style}]{pnl_dollar:+.2f}[/{pnl_style}]",
                    f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]"
                )
            else:
                table.add_row(broker, symbol, f"{qty:.4f}", f"${entry:.2f}", "—", "—", "—")
        
        # Add total row
        pnl_style = "bold green" if total_pnl > 0 else "bold red"
        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            "",
            "",
            "",
            f"[{pnl_style}]{total_pnl:+.2f}[/{pnl_style}]",
            "",
            style="bold white"
        )
        
        return table
    
    def create_trading_stats_table(self, stats: Dict[str, Any]) -> Table:
        """Create trading statistics table"""
        table = Table(title="📊 Trading Statistics", box=box.ROUNDED, show_header=False)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="white", width=20)
        table.add_column("Status", style="green", width=20)
        
        # Trades Today
        trades_today = stats.get('trades_today', 0)
        max_trades = stats.get('max_trades_per_day', 20)
        trade_pct = (trades_today / max_trades * 100) if max_trades > 0 else 0
        trade_status = "🟢 Active" if trades_today < max_trades else "🔴 Limit Reached"
        table.add_row("Trades Today", f"{trades_today}/{max_trades}", trade_status)
        
        # Win Rate
        win_rate = stats.get('win_rate', 0)
        win_status = "🟢 Good" if win_rate > 0.6 else "🟡 Fair" if win_rate > 0.4 else "🔴 Poor"
        table.add_row("Win Rate", f"{win_rate:.1%}", win_status)
        
        # Daily P&L
        daily_pnl = stats.get('daily_pnl', 0)
        pnl_status = "🟢 Profit" if daily_pnl > 0 else "🔴 Loss" if daily_pnl < 0 else "⚪ Flat"
        pnl_style = "green" if daily_pnl > 0 else "red"
        table.add_row("Daily P&L", f"[{pnl_style}]${daily_pnl:+.2f}[/{pnl_style}]", pnl_status)
        
        # Confidence Threshold
        confidence = stats.get('confidence_threshold', 0)
        table.add_row("Min Confidence", f"{confidence:.0%}", "")
        
        # Enhancements Status
        enhancements = stats.get('enhancements_active', 0)
        table.add_row("Enhancements Active", f"{enhancements}/6", "✅ All Systems Go" if enhancements == 6 else "⚠️  Some Inactive")
        
        return table
    
    def create_recent_signals_table(self, signals: List[Dict[str, Any]]) -> Table:
        """Create recent signals table"""
        table = Table(title="🎯 Recent Signals", box=box.ROUNDED, show_header=True)
        table.add_column("Time", style="cyan", width=10)
        table.add_column("Symbol", style="cyan bold", width=10)
        table.add_column("Action", style="white", width=8)
        table.add_column("Confidence", style="green", width=12)
        table.add_column("Reasons", style="white", width=40)
        
        if not signals:
            table.add_row("—", "No signals", "—", "—", "—")
            return table
        
        for signal in signals[-10:]:  # Last 10 signals
            action = signal.get('action', 'N/A')
            action_style = "bold green" if action == 'BUY' else "bold red" if action == 'SELL' else "yellow"
            
            confidence = signal.get('confidence', 0)
            conf_style = "bold green" if confidence > 0.75 else "green" if confidence > 0.65 else "yellow"
            
            table.add_row(
                signal.get('time', '—'),
                signal.get('symbol', 'N/A'),
                f"[{action_style}]{action}[/{action_style}]",
                f"[{conf_style}]{confidence:.1%}[/{conf_style}]",
                signal.get('reasons', '—')
            )
        
        return table
    
    def create_enhancements_panel(self, enhancements: Dict[str, bool]) -> Panel:
        """Create enhancements status panel"""
        text = Text()
        text.append("🚀 Active Enhancements\n\n", style="bold cyan")
        
        enhancement_list = [
            ("Trailing Stop", enhancements.get('trailing_stop', False)),
            ("DCA on Dips", enhancements.get('dca', False)),
            ("Time-Based Exit", enhancements.get('time_exit', False)),
            ("Sentiment Analysis", enhancements.get('sentiment', False)),
            ("Scale Out Strategy", enhancements.get('scale_out', False)),
            ("Correlation Filter", enhancements.get('correlation', False))
        ]
        
        for name, enabled in enhancement_list:
            status = "✅" if enabled else "❌"
            style = "green" if enabled else "red"
            text.append(f"{status} {name}\n", style=style)
        
        return Panel(text, box=box.ROUNDED, border_style="cyan")
    
    def display_full_dashboard(self, data: Dict[str, Any]):
        """Display complete trading dashboard"""
        self.console.clear()
        
        # Create header
        self.console.print(self.create_header())
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="top", size=12),
            Layout(name="middle", size=15),
            Layout(name="bottom")
        )
        
        # Top section: Account + Stats
        layout["top"].split_row(
            Layout(name="accounts", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        layout["top"]["accounts"].update(self.create_account_table(data.get('accounts', {})))
        layout["top"]["stats"].update(self.create_trading_stats_table(data.get('stats', {})))
        
        # Middle section: Positions
        layout["middle"].update(self.create_positions_table(data.get('positions', [])))
        
        # Bottom section: Signals + Enhancements
        layout["bottom"].split_row(
            Layout(name="signals", ratio=3),
            Layout(name="enhancements", ratio=1)
        )
        
        layout["bottom"]["signals"].update(self.create_recent_signals_table(data.get('signals', [])))
        layout["bottom"]["enhancements"].update(self.create_enhancements_panel(data.get('enhancements', {})))
        
        self.console.print(layout)
        
        # Update timestamp
        self.last_update = datetime.now()
    
    def print_log(self, level: str, message: str):
        """Print color-coded log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level.upper() == 'INFO':
            self.console.print(f"[cyan][{timestamp}][/cyan] [blue]ℹ️  {message}[/blue]")
        elif level.upper() == 'SUCCESS':
            self.console.print(f"[cyan][{timestamp}][/cyan] [green]✅ {message}[/green]")
        elif level.upper() == 'WARNING':
            self.console.print(f"[cyan][{timestamp}][/cyan] [yellow]⚠️  {message}[/yellow]")
        elif level.upper() == 'ERROR':
            self.console.print(f"[cyan][{timestamp}][/cyan] [red]❌ {message}[/red]")
        elif level.upper() == 'TRADE':
            self.console.print(f"[cyan][{timestamp}][/cyan] [bold magenta]💰 {message}[/bold magenta]")
        else:
            self.console.print(f"[cyan][{timestamp}][/cyan] {message}")
    
    def print_startup_banner(self):
        """Print startup banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗     ║
║   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║     ║
║   ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║     ║
║   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║     ║
║   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║     ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝     ║
║                                                                       ║
║              TRADING PLATFORM - Enhanced Terminal Display            ║
║                        Version 2.0 - 2026                            ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold cyan")
        self.console.print("\n[green]✅ Enhanced terminal display initialized[/green]\n")


# Global dashboard instance
dashboard = TradingDashboard()


def print_status(data: Dict[str, Any]):
    """Quick function to display dashboard"""
    dashboard.display_full_dashboard(data)


def log_info(message: str):
    """Log info message"""
    dashboard.print_log('INFO', message)


def log_success(message: str):
    """Log success message"""
    dashboard.print_log('SUCCESS', message)


def log_warning(message: str):
    """Log warning message"""
    dashboard.print_log('WARNING', message)


def log_error(message: str):
    """Log error message"""
    dashboard.print_log('ERROR', message)


def log_trade(message: str):
    """Log trade message"""
    dashboard.print_log('TRADE', message)


# Example usage
if __name__ == "__main__":
    dashboard.print_startup_banner()
    
    # Example data
    example_data = {
        'accounts': {
            'ib': {
                'cash': 17.98,
                'equity': 240.73,
                'buying_power': 17.98,
                'position_count': 1
            },
            'alpaca': {
                'cash': 36.91,
                'equity': 100.00,
                'buying_power': 36.91,
                'position_count': 3
            }
        },
        'positions': [
            {'broker': 'IB', 'symbol': 'AAPL', 'quantity': 1, 'entry_price': 225.50, 'current_price': 230.00},
            {'broker': 'Alpaca', 'symbol': 'BTCUSD', 'quantity': 0.000186, 'entry_price': 121640.22, 'current_price': 112639.35},
            {'broker': 'Alpaca', 'symbol': 'ETHUSD', 'quantity': 0.004109, 'entry_price': 4360.27, 'current_price': 3792.10},
        ],
        'stats': {
            'trades_today': 7,
            'max_trades_per_day': 20,
            'win_rate': 0.714,
            'daily_pnl': 45.32,
            'confidence_threshold': 0.65,
            'enhancements_active': 6
        },
        'signals': [
            {'time': '14:23:45', 'symbol': 'NVDA', 'action': 'BUY', 'confidence': 0.78, 'reasons': 'Uptrend + RSI oversold'},
            {'time': '14:15:12', 'symbol': 'TSLA', 'action': 'SELL', 'confidence': 0.72, 'reasons': 'Trailing stop triggered'}
        ],
        'enhancements': {
            'trailing_stop': True,
            'dca': True,
            'time_exit': True,
            'sentiment': True,
            'scale_out': True,
            'correlation': True
        }
    }
    
    dashboard.display_full_dashboard(example_data)
    
    import time
    time.sleep(2)
    
    log_info("System initialized successfully")
    log_success("Connected to both brokers")
    log_warning("Daily trade limit approaching (17/20)")
    log_trade("Executed BUY NVDA x 5 @ $950.25")
    log_error("Failed to get market data for GOOGL")
