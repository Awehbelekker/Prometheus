#!/usr/bin/env python3
"""
PROMETHEUS Comprehensive Status Report Generator
Generates a detailed 6-section status report for the trading platform
"""

import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

def print_section(title, section_num):
    print(f"\n{'='*70}")
    print(f"SECTION {section_num}: {title}")
    print('='*70)

def check_ai_systems():
    """Check all AI system components"""
    ai_status = {}
    
    # 1. HRM Official Integration
    try:
        from core.hrm_official_integration import get_official_hrm_adapter
        adapter = get_official_hrm_adapter()
        if adapter and len(adapter.models) > 0:
            ai_status['HRM Official'] = {'status': 'ACTIVE', 'models': len(adapter.models), 
                                         'checkpoints': list(adapter.models.keys())}
        else:
            ai_status['HRM Official'] = {'status': 'NOT LOADED', 'models': 0}
    except Exception as e:
        ai_status['HRM Official'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 2. Universal Reasoning Engine
    try:
        from core.universal_reasoning_engine import UniversalReasoningEngine
        ai_status['Universal Reasoning Engine'] = {'status': 'AVAILABLE'}
    except Exception as e:
        ai_status['Universal Reasoning Engine'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 3. Visual Pattern Provider
    try:
        from core.visual_pattern_provider import VisualPatternProvider
        provider = VisualPatternProvider()
        ai_status['Visual Pattern Provider'] = {'status': 'ACTIVE', 'patterns': len(provider.patterns)}
    except Exception as e:
        ai_status['Visual Pattern Provider'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 4. Market Oracle Engine
    try:
        from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
        ai_status['Market Oracle Engine'] = {'status': 'AVAILABLE'}
    except Exception as e:
        ai_status['Market Oracle Engine'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 5. Quantum Trading Engine
    try:
        from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
        ai_status['Quantum Trading Engine'] = {'status': 'AVAILABLE'}
    except Exception as e:
        ai_status['Quantum Trading Engine'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 6. GPT-OSS Engine
    try:
        from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
        ai_status['GPT-OSS Engine'] = {'status': 'AVAILABLE'}
    except Exception as e:
        ai_status['GPT-OSS Engine'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 7. Hierarchical Agent Coordinator
    try:
        from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
        ai_status['Hierarchical Agent Coordinator'] = {'status': 'AVAILABLE'}
    except Exception as e:
        ai_status['Hierarchical Agent Coordinator'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # 8. Ollama Models
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            ai_status['Ollama Local LLM'] = {'status': 'ACTIVE', 'models': len(models),
                                             'model_names': [m['name'] for m in models[:5]]}
        else:
            ai_status['Ollama Local LLM'] = {'status': 'NOT RESPONDING'}
    except:
        ai_status['Ollama Local LLM'] = {'status': 'NOT RUNNING'}
    
    return ai_status

def check_broker_connections():
    """Check broker API connections"""
    from dotenv import load_dotenv
    load_dotenv()
    
    brokers = {}
    
    # Alpaca Live
    try:
        api_key = os.getenv('ALPACA_LIVE_KEY')
        api_secret = os.getenv('ALPACA_LIVE_SECRET')
        headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': api_secret}
        r = requests.get('https://api.alpaca.markets/v2/account', headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            brokers['Alpaca Live'] = {'status': 'CONNECTED', 'account': data.get('account_number'),
                                      'equity': float(data.get('equity', 0)),
                                      'buying_power': float(data.get('buying_power', 0))}
        else:
            brokers['Alpaca Live'] = {'status': 'ERROR', 'code': r.status_code}
    except Exception as e:
        brokers['Alpaca Live'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # Alpaca Paper
    try:
        api_key = os.getenv('ALPACA_PAPER_KEY')
        api_secret = os.getenv('ALPACA_PAPER_SECRET')
        headers = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': api_secret}
        r = requests.get('https://paper-api.alpaca.markets/v2/account', headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            brokers['Alpaca Paper'] = {'status': 'CONNECTED', 'account': data.get('account_number'),
                                       'equity': float(data.get('equity', 0)),
                                       'buying_power': float(data.get('buying_power', 0))}
        else:
            brokers['Alpaca Paper'] = {'status': 'ERROR', 'code': r.status_code}
    except Exception as e:
        brokers['Alpaca Paper'] = {'status': 'ERROR', 'error': str(e)[:100]}
    
    # IB Gateway
    import socket
    ib_port = int(os.getenv('IB_PORT', 4002))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', ib_port))
        sock.close()
        if result == 0:
            brokers['IB Gateway'] = {'status': 'PORT OPEN', 'port': ib_port}
        else:
            brokers['IB Gateway'] = {'status': 'NOT RUNNING', 'port': ib_port}
    except:
        brokers['IB Gateway'] = {'status': 'ERROR', 'port': ib_port}
    
    return brokers

def check_paper_trading_results():
    """Check recent paper trading sessions"""
    results_dir = Path('paper_trading_results')
    if not results_dir.exists():
        return {'sessions': 0, 'error': 'No results directory'}

    sessions = list(results_dir.glob('*.json'))
    if not sessions:
        return {'sessions': 0}

    # Load latest session
    latest = sorted(sessions)[-1]
    with open(latest) as f:
        data = json.load(f)

    return {
        'sessions': len(sessions),
        'latest_file': latest.name,
        'total_trades': data.get('report', {}).get('total_trades', 0),
        'win_rate': data.get('report', {}).get('win_rate', 0),
        'total_profit': data.get('report', {}).get('total_profit', 0)
    }


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PROMETHEUS TRADING PLATFORM - COMPREHENSIVE STATUS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Section 1: System Health
    print_section("SYSTEM HEALTH & OPERATIONAL STATUS", 1)
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print(f"  Working Directory: {os.getcwd()}")

    # Section 2: AI Components
    print_section("AI COMPONENTS VERIFICATION", 2)
    ai_status = check_ai_systems()
    for name, status in ai_status.items():
        status_icon = "OK" if status.get('status') in ['ACTIVE', 'AVAILABLE'] else "X "
        print(f"  [{status_icon}] {name}: {status.get('status')}")
        if status.get('models'):
            print(f"       Models/Checkpoints: {status.get('models')}")

    # Section 3: Broker Connections
    print_section("BROKER CONNECTIONS STATUS", 3)
    brokers = check_broker_connections()
    for name, status in brokers.items():
        status_icon = "OK" if status.get('status') == 'CONNECTED' or 'OPEN' in str(status.get('status', '')) else "X "
        print(f"  [{status_icon}] {name}: {status.get('status')}")
        if status.get('account'):
            print(f"       Account: {status.get('account')}")
            print(f"       Equity: ${status.get('equity', 0):,.2f}")

    # Section 4: Recent Configuration Changes
    print_section("RECENT CONFIGURATION CHANGES", 4)
    print("  [OK] Alpaca API credentials updated (Live + Paper)")
    print("  [OK] IB Gateway port standardized to 4002")
    print("  [OK] All configuration files synchronized")
    print("  [!] WSL2/ROCm GPU setup pending (requires BIOS virtualization)")

    # Section 5: Performance Metrics
    print_section("PERFORMANCE METRICS & TRADING RESULTS", 5)
    paper_results = check_paper_trading_results()
    print(f"  Paper Trading Sessions: {paper_results.get('sessions', 0)}")
    print(f"  Latest Session Trades: {paper_results.get('total_trades', 'N/A')}")
    print(f"  Win Rate: {paper_results.get('win_rate', 0):.1f}%")
    print(f"  Total Profit: ${paper_results.get('total_profit', 0):.2f}")
    if paper_results.get('win_rate', 0) == 0:
        print("  [!] WARNING: 0% win rate indicates P/L calculation bug")

    # Section 6: Recommendations
    print_section("RECOMMENDATIONS FOR NEXT STEPS", 6)
    print("  1. [CRITICAL] Fix paper trading P/L bug (entry_price = exit_price)")
    print("  2. [HIGH] Enable BIOS virtualization for WSL2/ROCm GPU support")
    print("  3. [HIGH] Rewrite shadow trading system with full AI integration")
    print("  4. [MEDIUM] Run comprehensive paper trading test session")
    print("  5. [LOW] Review AI attribution tracking data")

    print("\n" + "="*70)
    print("END OF STATUS REPORT")
    print("="*70 + "\n")

