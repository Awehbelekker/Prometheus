#!/usr/bin/env python3
"""PROMETHEUS Comprehensive Trading Status Report"""

import os
import json
import socket
from pathlib import Path
from datetime import datetime, timedelta

def main():
    print("=" * 80)
    print("PROMETHEUS COMPREHENSIVE TRADING STATUS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. MARKET STATUS
    print("\n[1] MARKET STATUS")
    print("-" * 40)
    try:
        import pytz
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        print(f"Current Time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        weekday = now_et.weekday()
        hour, minute = now_et.hour, now_et.minute
        current_time = hour * 60 + minute
        
        if weekday >= 5:
            print(f"Market Status: CLOSED (Weekend - {now_et.strftime('%A')})")
        elif current_time < 4 * 60:
            print("Market Status: CLOSED (Pre-Pre-Market)")
        elif current_time < 9 * 60 + 30:
            print("Market Status: PRE-MARKET")
        elif current_time < 16 * 60:
            print("Market Status: OPEN (Regular Hours)")
        elif current_time < 20 * 60:
            print("Market Status: AFTER-HOURS")
        else:
            print("Market Status: CLOSED")
        print("Crypto Markets: ALWAYS OPEN (24/7)")
    except Exception as e:
        print(f"Error: {e}")

    # 2. BROKER CONNECTIONS
    print("\n[2] BROKER CONNECTIONS & ACCOUNTS")
    print("-" * 40)
    
    # Alpaca
    print("\n--- ALPACA ---")
    try:
        from alpaca.trading.client import TradingClient
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
        secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
        paper = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'
        
        if api_key and secret_key:
            client = TradingClient(api_key, secret_key, paper=paper)
            account = client.get_account()
            mode = "PAPER" if paper else "LIVE"
            print(f"Status: CONNECTED ({mode})")
            print(f"Equity: ${float(account.equity):,.2f}")
            print(f"Buying Power: ${float(account.buying_power):,.2f}")
            print(f"Cash: ${float(account.cash):,.2f}")
            
            positions = client.get_all_positions()
            print(f"Open Positions: {len(positions)}")
            for p in positions[:5]:
                pnl = float(p.unrealized_pl)
                print(f"  {p.symbol}: {p.qty} @ ${float(p.avg_entry_price):.2f} | P/L: ${pnl:+,.2f}")
        else:
            print("Status: NOT CONFIGURED")
    except Exception as e:
        print(f"Status: ERROR - {e}")

    # IB Gateway
    print("\n--- INTERACTIVE BROKERS ---")
    try:
        for port in [7497, 4001]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            if sock.connect_ex(('127.0.0.1', port)) == 0:
                print(f"IB Gateway: CONNECTED (port {port})")
                sock.close()
                break
            sock.close()
        else:
            print("IB Gateway: NOT RUNNING")
    except Exception as e:
        print(f"IB Gateway: ERROR - {e}")

    # 3. RECENT TRADING ACTIVITY
    print("\n[3] RECENT TRADING ACTIVITY")
    print("-" * 40)
    
    paper_dir = Path('paper_trading_results')
    if paper_dir.exists():
        files = sorted(paper_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"Paper Trading Sessions: {len(files)}")
        if files:
            latest = files[0]
            print(f"Latest: {latest.name}")
            try:
                with open(latest) as f:
                    data = json.load(f)
                trades = data.get('trades', [])
                if trades:
                    wins = len([t for t in trades if t.get('pnl', 0) > 0])
                    print(f"  Trades: {len(trades)}, Win Rate: {wins/len(trades)*100:.1f}%")
            except:
                pass

    # Trade feedback
    fb_file = Path('trading_feedback/trade_feedback.json')
    if fb_file.exists():
        with open(fb_file) as f:
            data = json.load(f)
        print(f"Trade Feedback Records: {len(data)}")

    print("\n[4] AI SYSTEMS STATUS")
    print("-" * 40)
    
    # Check HRM
    hrm_dir = Path('hrm_checkpoints')
    if hrm_dir.exists():
        checkpoints = ['arc_agi_2', 'sudoku_extreme', 'maze_30x30']
        loaded = sum(1 for cp in checkpoints if (hrm_dir / cp / 'checkpoint').exists())
        print(f"HRM Checkpoints: {loaded}/3 available")

    # Check Ollama
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            models = len([l for l in result.stdout.strip().split('\n')[1:] if l.strip()])
            print(f"Ollama Models: {models} available")
    except:
        print("Ollama: Not responding")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

