#!/usr/bin/env python3
"""
COMPREHENSIVE AI AUDIT
Full audit of all Prometheus AI systems to ensure real AI intelligence
"""

import requests
import json
import time
from datetime import datetime
import subprocess
import psutil

def check_revolutionary_server():
    """Check if revolutionary server is running"""
    print("1. CHECKING REVOLUTIONARY SERVER")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("   [OK] Revolutionary Server: RUNNING on port 8002")
            return True
        else:
            print(f"   [ERROR] Revolutionary Server: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Revolutionary Server: {str(e)}")
        return False

def check_ai_servers():
    """Check all AI servers"""
    print("\n2. CHECKING AI SERVERS")
    print("=" * 50)
    
    ai_servers = {
        "GPT-OSS 20B": "http://localhost:5000/health",
        "GPT-OSS 120B": "http://localhost:5001/health",
        "Revolutionary Server": "http://localhost:8002/health"
    }
    
    all_running = True
    
    for name, url in ai_servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {name}: RUNNING")
            else:
                print(f"   [ERROR] {name}: {response.status_code}")
                all_running = False
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")
            all_running = False
    
    return all_running

def test_real_ai_intelligence():
    """Test if AI systems are providing real intelligence"""
    print("\n3. TESTING REAL AI INTELLIGENCE")
    print("=" * 50)
    
    test_prompts = [
        "Analyze the current market conditions for AAPL and provide a detailed trading recommendation",
        "What are the key technical indicators showing for TSLA right now?",
        "Provide a comprehensive risk assessment for NVDA based on current market volatility"
    ]
    
    real_ai_detected = 0
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n   Testing AI Intelligence {i}/3:")
        print(f"   Prompt: {prompt[:50]}...")
        
        try:
            # Test GPT-OSS 20B
            response = requests.post(
                "http://localhost:5000/generate",
                json={"prompt": prompt, "max_tokens": 200},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('generated_text', '')
                
                # Check if response contains real analysis (not just mock)
                real_indicators = [
                    "technical analysis", "RSI", "MACD", "moving average", 
                    "support", "resistance", "volatility", "trend", "momentum",
                    "risk assessment", "market conditions", "trading strategy"
                ]
                
                has_real_analysis = any(indicator in response_text.lower() for indicator in real_indicators)
                
                if has_real_analysis:
                    print(f"   [REAL AI] GPT-OSS 20B: {response_text[:100]}...")
                    real_ai_detected += 1
                else:
                    print(f"   [MOCK] GPT-OSS 20B: {response_text[:100]}...")
            else:
                print(f"   [ERROR] GPT-OSS 20B failed: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] GPT-OSS 20B error: {str(e)}")
    
    return real_ai_detected >= 2

def check_ai_coordinator():
    """Check AI Coordinator system"""
    print("\n4. CHECKING AI COORDINATOR")
    print("=" * 50)
    
    try:
        # Check if AI Coordinator is accessible
        response = requests.get("http://localhost:8000/api/ai/coordinator/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] AI Coordinator: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"   [ERROR] AI Coordinator: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] AI Coordinator: {str(e)}")
        return False

def check_hierarchical_agents():
    """Check Hierarchical Agent System"""
    print("\n5. CHECKING HIERARCHICAL AGENTS")
    print("=" * 50)
    
    agents = [
        "SynergyCore", "CogniFlow", "EdgeMind", "NeuralMesh", "CodeSwarm"
    ]
    
    active_agents = 0
    
    for agent in agents:
        try:
            response = requests.get(f"http://localhost:8000/api/ai/agents/{agent.lower()}/status", timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {agent}: ACTIVE")
                active_agents += 1
            else:
                print(f"   [ERROR] {agent}: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] {agent}: {str(e)}")
    
    return active_agents >= 3

def check_quantum_trading_engine():
    """Check Quantum Trading Engine"""
    print("\n6. CHECKING QUANTUM TRADING ENGINE")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/quantum/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Quantum Engine: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"   [ERROR] Quantum Engine: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Quantum Engine: {str(e)}")
        return False

def check_think_mesh():
    """Check Think Mesh system"""
    print("\n7. CHECKING THINK MESH")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/think-mesh/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Think Mesh: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"   [ERROR] Think Mesh: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Think Mesh: {str(e)}")
        return False

def check_market_oracle():
    """Check Market Oracle"""
    print("\n8. CHECKING MARKET ORACLE")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/market-oracle/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Market Oracle: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"   [ERROR] Market Oracle: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Market Oracle: {str(e)}")
        return False

def check_learning_systems():
    """Check AI Learning Systems"""
    print("\n9. CHECKING AI LEARNING SYSTEMS")
    print("=" * 50)
    
    learning_systems = [
        "continuous-learning", "advanced-learning", "autonomous-improvement"
    ]
    
    active_systems = 0
    
    for system in learning_systems:
        try:
            response = requests.get(f"http://localhost:8000/api/learning/{system}/status", timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {system.replace('-', ' ').title()}: ACTIVE")
                active_systems += 1
            else:
                print(f"   [ERROR] {system.replace('-', ' ').title()}: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] {system.replace('-', ' ').title()}: {str(e)}")
    
    return active_systems >= 2

def check_trading_engines():
    """Check Trading Engines"""
    print("\n10. CHECKING TRADING ENGINES")
    print("=" * 50)
    
    engines = [
        "crypto-engine", "options-engine", "advanced-engine", 
        "market-maker", "master-engine", "hrm-engine"
    ]
    
    active_engines = 0
    
    for engine in engines:
        try:
            response = requests.get(f"http://localhost:8000/api/trading/{engine}/status", timeout=5)
            if response.status_code == 200:
                print(f"   [OK] {engine.replace('-', ' ').title()}: ACTIVE")
                active_engines += 1
            else:
                print(f"   [ERROR] {engine.replace('-', ' ').title()}: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] {engine.replace('-', ' ').title()}: {str(e)}")
    
    return active_engines >= 3

def check_fund_limits():
    """Check and adjust fund limits for $250"""
    print("\n11. CHECKING FUND LIMITS")
    print("=" * 50)
    
    try:
        # Check current portfolio value
        response = requests.get("http://localhost:8000/api/portfolio/value", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_value = data.get('total_value', 0)
            cash_balance = data.get('cash_balance', 0)
            
            print(f"   [INFO] Current Portfolio Value: ${total_value:,.2f}")
            print(f"   [INFO] Cash Balance: ${cash_balance:,.2f}")
            
            if total_value > 250:
                print(f"   [WARNING] Portfolio value (${total_value:,.2f}) exceeds your $250 limit!")
                print(f"   [RECOMMENDATION] Adjust position sizes or close some positions")
                return False
            else:
                print(f"   [OK] Portfolio within $250 limit")
                return True
        else:
            print(f"   [ERROR] Could not check portfolio value: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Fund limit check failed: {str(e)}")
        return False

def start_revolutionary_server():
    """Start the revolutionary server"""
    print("\n12. STARTING REVOLUTIONARY SERVER")
    print("=" * 50)
    
    try:
        # Try to start revolutionary server
        subprocess.Popen([
            "python", "revolutionary_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("   [INFO] Revolutionary server startup initiated")
        time.sleep(5)  # Wait for startup
        
        # Check if it's running
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("   [SUCCESS] Revolutionary server is now running")
            return True
        else:
            print(f"   [ERROR] Revolutionary server failed to start: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Failed to start revolutionary server: {str(e)}")
        return False

def main():
    """Main audit function"""
    print("PROMETHEUS COMPREHENSIVE AI AUDIT")
    print("=" * 60)
    print(f"Audit started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all checks
    checks = [
        ("Revolutionary Server", check_revolutionary_server),
        ("AI Servers", check_ai_servers),
        ("Real AI Intelligence", test_real_ai_intelligence),
        ("AI Coordinator", check_ai_coordinator),
        ("Hierarchical Agents", check_hierarchical_agents),
        ("Quantum Trading Engine", check_quantum_trading_engine),
        ("Think Mesh", check_think_mesh),
        ("Market Oracle", check_market_oracle),
        ("Learning Systems", check_learning_systems),
        ("Trading Engines", check_trading_engines),
        ("Fund Limits", check_fund_limits)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
        except Exception as e:
            print(f"   [ERROR] {check_name} check failed: {str(e)}")
            results[check_name] = False
    
    # Try to start revolutionary server if not running
    if not results.get("Revolutionary Server", False):
        print("\n" + "=" * 60)
        print("ATTEMPTING TO START REVOLUTIONARY SERVER")
        print("=" * 60)
        revolutionary_started = start_revolutionary_server()
        results["Revolutionary Server"] = revolutionary_started
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE AI AUDIT SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"AI Systems Operational: {passed}/{total}")
    print()
    
    for check_name, result in results.items():
        status = "OPERATIONAL" if result else "NOT OPERATIONAL"
        print(f"   {status}: {check_name}")
    
    print()
    
    if passed >= total * 0.8:
        print("AI SYSTEMS ARE MOSTLY OPERATIONAL!")
        print("Most AI systems are running with real intelligence.")
    elif passed >= total * 0.5:
        print("AI SYSTEMS PARTIALLY OPERATIONAL")
        print("Some AI systems need attention.")
    else:
        print("AI SYSTEMS NEED SIGNIFICANT ATTENTION")
        print("Multiple AI systems are not operational.")
    
    # Fund limit warning
    if not results.get("Fund Limits", True):
        print("\n" + "!" * 60)
        print("FUND LIMIT WARNING")
        print("!" * 60)
        print("Your portfolio exceeds the $250 limit you mentioned.")
        print("Consider reducing position sizes or closing some positions.")
        print("!" * 60)
    
    print(f"\nAudit completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed >= total * 0.7

if __name__ == "__main__":
    success = main()
    print(f"\nFINAL RESULT: {'AI SYSTEMS READY' if success else 'AI SYSTEMS NEED ATTENTION'}")










