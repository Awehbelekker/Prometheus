#!/usr/bin/env python3
"""
PROMETHEUS COMPREHENSIVE FULL ASSESSMENT
Checks all systems, brokers, AI models, databases, and performance metrics
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import psutil

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def check_running_processes():
    """Check if PROMETHEUS trading processes are running"""
    print_section("🔄 RUNNING PROCESSES")
    
    prometheus_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['name'] == 'python.exe':
                cmdline = proc.info['cmdline']
                if cmdline and any('prometheus' in str(arg).lower() or 'trading' in str(arg).lower() 
                                  for arg in cmdline):
                    runtime = datetime.now() - datetime.fromtimestamp(proc.info['create_time'])
                    prometheus_processes.append({
                        'pid': proc.info['pid'],
                        'script': cmdline[-1] if cmdline else 'Unknown',
                        'runtime': str(runtime).split('.')[0]
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if prometheus_processes:
        print(f"✅ FOUND {len(prometheus_processes)} PROMETHEUS PROCESS(ES):\n")
        for p in prometheus_processes:
            print(f"  PID: {p['pid']}")
            print(f"  Script: {p['script']}")
            print(f"  Runtime: {p['runtime']}")
            print()
    else:
        print("❌ NO PROMETHEUS TRADING PROCESSES RUNNING")
        print("   System appears to be STOPPED")
    
    return len(prometheus_processes) > 0

def check_broker_connections():
    """Check Interactive Brokers and Alpaca connections"""
    print_section("💰 BROKER CONNECTIONS")
    
    results = {
        'ib': {'connected': False, 'balance': None, 'positions': []},
        'alpaca': {'connected': False, 'balance': None, 'positions': []}
    }
    
    # Check Interactive Brokers
    print("Interactive Brokers (IB):")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        ib_port = int(os.getenv('IB_PORT', '4002'))
        ib = InteractiveBrokersBroker(port=ib_port)
        ib.connect()
        
        account_info = ib.get_account_info()
        positions = ib.get_positions()
        
        results['ib']['connected'] = True
        results['ib']['balance'] = account_info.get('net_liquidation', 0)
        results['ib']['positions'] = positions
        
        print(f"  ✅ CONNECTED (Port {ib_port})")
        print(f"  Account: {account_info.get('account_id', 'N/A')}")
        print(f"  Balance: ${account_info.get('net_liquidation', 0):.2f}")
        print(f"  Cash: ${account_info.get('cash_balance', 0):.2f}")
        print(f"  Buying Power: ${account_info.get('buying_power', 0):.2f}")
        print(f"  Positions: {len(positions)}")
        
        if positions:
            print("\n  Current Positions:")
            for pos in positions:
                print(f"    {pos.get('symbol', 'N/A')}: {pos.get('quantity', 0)} @ ${pos.get('avg_cost', 0):.2f}")
                pnl = pos.get('unrealized_pnl', 0)
                pnl_symbol = "📈" if pnl > 0 else "📉" if pnl < 0 else "➖"
                print(f"      P&L: {pnl_symbol} ${pnl:.2f}")
        
        ib.disconnect()
    except Exception as e:
        print(f"  ❌ DISCONNECTED: {str(e)}")
    
    # Check Alpaca
    print("\n\nAlpaca Markets:")
    try:
        from brokers.alpaca_broker import AlpacaBroker
        alpaca = AlpacaBroker()
        
        account_info = alpaca.get_account_info()
        positions = alpaca.get_positions()
        
        results['alpaca']['connected'] = True
        results['alpaca']['balance'] = float(account_info.get('equity', 0))
        results['alpaca']['positions'] = positions
        
        print(f"  ✅ CONNECTED")
        print(f"  Account: {account_info.get('account_number', 'N/A')}")
        print(f"  Equity: ${float(account_info.get('equity', 0)):.2f}")
        print(f"  Cash: ${float(account_info.get('cash', 0)):.2f}")
        print(f"  Buying Power: ${float(account_info.get('buying_power', 0)):.2f}")
        print(f"  Positions: {len(positions)}")
        
        if positions:
            print("\n  Current Positions:")
            for pos in positions:
                qty = float(pos.get('qty', 0))
                current_price = float(pos.get('current_price', 0))
                avg_entry = float(pos.get('avg_entry_price', 0))
                pnl = (current_price - avg_entry) * qty
                pnl_pct = ((current_price / avg_entry) - 1) * 100 if avg_entry > 0 else 0
                pnl_symbol = "📈" if pnl > 0 else "📉" if pnl < 0 else "➖"
                
                print(f"    {pos.get('symbol', 'N/A')}: {qty} @ ${avg_entry:.2f}")
                print(f"      Current: ${current_price:.2f} | P&L: {pnl_symbol} ${pnl:.2f} ({pnl_pct:+.2f}%)")
    except Exception as e:
        print(f"  ❌ DISCONNECTED: {str(e)}")
    
    return results

def check_ai_systems():
    """Check AI model availability and configuration"""
    print_section("🤖 AI SYSTEMS & MODELS")
    
    ai_status = {}
    
    # Check environment variables
    print("Primary LLM Configuration:")
    deepseek_enabled = os.getenv('DEEPSEEK_ENABLED', 'false').lower() == 'true'
    use_local_ai = os.getenv('USE_LOCAL_AI', 'false').lower() == 'true'
    ollama_base = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    print(f"  DeepSeek Enabled: {'✅' if deepseek_enabled else '❌'} {deepseek_enabled}")
    print(f"  Use Local AI: {'✅' if use_local_ai else '❌'} {use_local_ai}")
    print(f"  Ollama URL: {ollama_base}")
    
    # Check Ollama
    print("\n\nOllama (Local AI):")
    try:
        import requests
        response = requests.get(f"{ollama_base}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"  ✅ RUNNING - {len(models)} models available")
            
            # Check for key models
            model_names = [m['name'] for m in models]
            key_models = ['deepseek-r1:14b', 'llava:7b', 'mistral', 'llama2']
            for model in key_models:
                found = any(model in m for m in model_names)
                print(f"    {'✅' if found else '❌'} {model}")
            
            ai_status['ollama'] = True
        else:
            print(f"  ⚠️ RESPONDED but status {response.status_code}")
            ai_status['ollama'] = False
    except Exception as e:
        print(f"  ❌ NOT RUNNING: {str(e)}")
        ai_status['ollama'] = False
    
    # Check Visual AI
    print("\n\nVisual AI Providers:")
    visual_ai_enabled = os.getenv('VISUAL_AI_ENABLED', 'false').lower() == 'true'
    print(f"  Visual AI Enabled: {'✅' if visual_ai_enabled else '❌'} {visual_ai_enabled}")
    
    # Claude
    claude_key = os.getenv('ANTHROPIC_API_KEY', '')
    use_claude = os.getenv('USE_CLAUDE_VISION', 'false').lower() == 'true'
    print(f"  Claude 3.5 Vision: {'✅ Configured' if claude_key and use_claude else '❌ Not configured'}")
    
    # Gemini
    gemini_key = os.getenv('GOOGLE_API_KEY', '')
    use_gemini = os.getenv('USE_GEMINI_VISION', 'false').lower() == 'true'
    print(f"  Gemini Pro Vision: {'✅ Configured' if gemini_key and use_gemini else '❌ Not configured'}")
    
    # GLM-4-V
    glm_key = os.getenv('ZHIPUAI_API_KEY', '')
    print(f"  GLM-4-V Vision: {'✅ Configured' if glm_key else '❌ Not configured'}")
    
    # LLaVA
    use_llava = os.getenv('USE_LLAVA_VISION', 'false').lower() == 'true'
    print(f"  LLaVA (Local): {'✅ Enabled' if use_llava and ai_status.get('ollama') else '❌ Disabled'}")
    
    # AI Trading Features
    print("\n\nAI Trading Features:")
    features = {
        'AI Signals': os.getenv('USE_AI_SIGNALS', 'false').lower() == 'true',
        'Quantum Signals': os.getenv('USE_QUANTUM_SIGNALS', 'false').lower() == 'true',
        'AI Consciousness': os.getenv('USE_AI_CONSCIOUSNESS', 'false').lower() == 'true',
    }
    
    for feature, enabled in features.items():
        print(f"  {feature}: {'✅ Enabled' if enabled else '❌ Disabled'}")
    
    return ai_status

def check_databases():
    """Check database health and recent activity"""
    print_section("💾 DATABASES & DATA")
    
    db_status = {}
    
    # Check learning database
    learning_db = Path('prometheus_learning.db')
    if learning_db.exists():
        print("Learning Database (prometheus_learning.db):")
        try:
            conn = sqlite3.connect(str(learning_db))
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"  ✅ EXISTS - {len(tables)} tables")
            
            # Check for trades table
            if 'trades' in tables:
                cursor.execute("SELECT COUNT(*) FROM trades")
                trade_count = cursor.fetchone()[0]
                print(f"    Trades recorded: {trade_count}")
                
                if trade_count > 0:
                    cursor.execute("SELECT COUNT(*) FROM trades WHERE timestamp >= datetime('now', '-24 hours')")
                    recent_trades = cursor.fetchone()[0]
                    print(f"    Trades (last 24h): {recent_trades}")
            else:
                print(f"    ⚠️ 'trades' table not found")
            
            # Check learning_metrics if exists
            if 'learning_metrics' in tables:
                cursor.execute("SELECT COUNT(*) FROM learning_metrics")
                metrics_count = cursor.fetchone()[0]
                print(f"    Learning metrics: {metrics_count}")
            
            conn.close()
            db_status['learning'] = True
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            db_status['learning'] = False
    else:
        print("Learning Database: ❌ NOT FOUND")
        db_status['learning'] = False
    
    # Check state file
    print("\n\nState Files:")
    state_file = Path('prometheus_live_trading_state.json')
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)
            print(f"  ✅ prometheus_live_trading_state.json")
            print(f"    Last updated: {state.get('last_update', 'Unknown')}")
            print(f"    Trading active: {state.get('trading_active', False)}")
            db_status['state'] = True
        except Exception as e:
            print(f"  ⚠️ File exists but error reading: {str(e)}")
            db_status['state'] = False
    else:
        print(f"  ⚠️ prometheus_live_trading_state.json NOT FOUND")
        db_status['state'] = False
    
    return db_status

def check_performance_metrics():
    """Check recent performance and learning progress"""
    print_section("📊 PERFORMANCE METRICS")
    
    metrics = {}
    
    # Check for recent backtest results
    print("Recent Backtests:")
    backtest_files = list(Path('.').glob('*backtest*.json')) + list(Path('.').glob('*benchmark*.json'))
    backtest_files = sorted(backtest_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    if backtest_files:
        for bf in backtest_files:
            mod_time = datetime.fromtimestamp(bf.stat().st_mtime)
            age_days = (datetime.now() - mod_time).days
            print(f"  📄 {bf.name}")
            print(f"     Age: {age_days} days ago")
    else:
        print("  ⚠️ No recent backtest files found")
    
    # Check learning results
    print("\n\nLearning Progress:")
    learning_files = list(Path('.').glob('*learning*.json'))
    learning_files = sorted(learning_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
    
    if learning_files:
        for lf in learning_files:
            mod_time = datetime.fromtimestamp(lf.stat().st_mtime)
            print(f"  📊 {lf.name}")
            print(f"     Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("  ⚠️ No learning result files found")
    
    return metrics

def check_configuration():
    """Check key configuration settings"""
    print_section("⚙️ CONFIGURATION")
    
    config = {}
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("Environment File (.env):")
        print(f"  ✅ EXISTS ({env_file.stat().st_size} bytes)")
        
        # Check key settings (without revealing secrets)
        key_vars = [
            'IB_PORT', 'ALPACA_LIVE_KEY', 'ANTHROPIC_API_KEY', 
            'GOOGLE_API_KEY', 'ZHIPUAI_API_KEY',
            'USE_AI_SIGNALS', 'DEEPSEEK_ENABLED', 'VISUAL_AI_ENABLED'
        ]
        
        print("\n  Key Variables:")
        for var in key_vars:
            value = os.getenv(var, '')
            if 'KEY' in var or 'SECRET' in var:
                status = '✅ Set' if value else '❌ Not set'
                print(f"    {var}: {status}")
            else:
                print(f"    {var}: {value if value else '❌ Not set'}")
        
        config['env'] = True
    else:
        print("Environment File: ❌ NOT FOUND")
        config['env'] = False
    
    return config


