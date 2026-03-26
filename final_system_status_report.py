#!/usr/bin/env python3
"""
FINAL SYSTEM STATUS REPORT
Comprehensive status of all Prometheus systems
"""

import requests
import sqlite3
from datetime import datetime

def check_all_servers():
    """Check all server status"""
    print("PROMETHEUS COMPREHENSIVE SYSTEM STATUS")
    print("=" * 60)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("1. SERVER STATUS")
    print("=" * 30)
    
    servers = {
        "Main Server (Port 8000)": "http://localhost:8000/health",
        "GPT-OSS 20B (Port 5000)": "http://localhost:5000/health",
        "GPT-OSS 120B (Port 5001)": "http://localhost:5001/health",
        "Revolutionary Server (Port 8002)": "http://localhost:8002/health"
    }
    
    running_servers = 0
    
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [RUNNING] {name}")
                running_servers += 1
            else:
                print(f"   [ERROR] {name}: {response.status_code}")
        except Exception as e:
            print(f"   [DOWN] {name}: Connection failed")
    
    print(f"\n   Servers Running: {running_servers}/4")
    return running_servers

def check_portfolio_status():
    """Check portfolio status"""
    print("\n2. PORTFOLIO STATUS")
    print("=" * 30)
    
    try:
        # Check portfolio value
        response = requests.get("http://localhost:8000/api/portfolio/value", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_value = data.get('total_value', 0)
            cash_balance = data.get('cash_balance', 0)
            
            print(f"   Total Portfolio Value: ${total_value:,.2f}")
            print(f"   Cash Balance: ${cash_balance:,.2f}")
            
            if total_value <= 250:
                print(f"   [OK] Portfolio within $250 budget limit")
                return True
            else:
                print(f"   [WARNING] Portfolio exceeds $250 limit by ${total_value - 250:,.2f}")
                return False
        else:
            print(f"   [ERROR] Could not check portfolio: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Portfolio check failed: {str(e)}")
        return False

def check_ai_intelligence():
    """Check AI intelligence quality"""
    print("\n3. AI INTELLIGENCE STATUS")
    print("=" * 30)
    
    try:
        # Test AI with complex prompt
        response = requests.post(
            "http://localhost:5000/generate",
            json={
                "prompt": "Provide a detailed technical analysis of AAPL including RSI, MACD, support/resistance levels, and trading recommendation",
                "max_tokens": 200
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('generated_text', '')
            
            # Check for real analysis indicators
            real_indicators = [
                "RSI", "MACD", "support", "resistance", "technical analysis",
                "trading recommendation", "market conditions", "volatility"
            ]
            
            has_real_analysis = any(indicator in response_text for indicator in real_indicators)
            
            if has_real_analysis:
                print("   [REAL AI] GPT-OSS 20B providing sophisticated analysis")
                print(f"   Sample: {response_text[:100]}...")
                return True
            else:
                print("   [MOCK AI] GPT-OSS 20B using basic responses")
                print(f"   Sample: {response_text[:100]}...")
                return False
        else:
            print(f"   [ERROR] AI test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] AI test error: {str(e)}")
        return False

def check_trading_capabilities():
    """Check trading capabilities"""
    print("\n4. TRADING CAPABILITIES")
    print("=" * 30)
    
    try:
        # Test trade execution
        response = requests.post(
            "http://localhost:8000/api/trading/execute",
            json={
                "symbol": "TEST_SMALL",
                "side": "buy",
                "quantity": 1,
                "price": 10.0
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("   [OK] Trade execution working")
            
            # Check positions
            pos_response = requests.get("http://localhost:8000/api/portfolio/positions", timeout=5)
            if pos_response.status_code == 200:
                pos_data = pos_response.json()
                positions = pos_data.get('positions', [])
                print(f"   [OK] Position tracking: {len(positions)} active positions")
                return True
            else:
                print("   [ERROR] Position tracking failed")
                return False
        else:
            print(f"   [ERROR] Trade execution failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Trading test error: {str(e)}")
        return False

def check_missing_systems():
    """Check for missing revolutionary systems"""
    print("\n5. MISSING REVOLUTIONARY SYSTEMS")
    print("=" * 30)
    
    missing_systems = [
        "AI Coordinator",
        "Hierarchical Agents (SynergyCore, CogniFlow, EdgeMind, NeuralMesh, CodeSwarm)",
        "Quantum Trading Engine",
        "Think Mesh",
        "Market Oracle",
        "Advanced Learning Systems",
        "Autonomous Self-Improvement",
        "Advanced Trading Engines"
    ]
    
    print("   The following revolutionary systems are NOT operational:")
    for system in missing_systems:
        print(f"   [MISSING] {system}")
    
    print(f"\n   Missing Systems: {len(missing_systems)}")
    return len(missing_systems)

def main():
    """Main status report"""
    print("PROMETHEUS FINAL SYSTEM STATUS REPORT")
    print("=" * 60)
    
    # Run all checks
    servers_running = check_all_servers()
    portfolio_ok = check_portfolio_status()
    ai_working = check_ai_intelligence()
    trading_ok = check_trading_capabilities()
    missing_count = check_missing_systems()
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    print(f"Servers Running: {servers_running}/4")
    print(f"Portfolio Status: {'OK' if portfolio_ok else 'NEEDS ATTENTION'}")
    print(f"AI Intelligence: {'REAL AI' if ai_working else 'MOCK AI'}")
    print(f"Trading Capabilities: {'WORKING' if trading_ok else 'ISSUES'}")
    print(f"Missing Systems: {missing_count}")
    
    print("\nCRITICAL ISSUES:")
    if servers_running < 4:
        print(f"- {4 - servers_running} servers are down (Revolutionary Server missing)")
    if not portfolio_ok:
        print("- Portfolio exceeds $250 budget limit")
    if not ai_working:
        print("- AI systems using mock responses, not real intelligence")
    if not trading_ok:
        print("- Trading capabilities have issues")
    if missing_count > 0:
        print(f"- {missing_count} revolutionary systems are missing")
    
    print("\nRECOMMENDATIONS:")
    print("1. Start Revolutionary Server to enable advanced AI features")
    print("2. Adjust portfolio to stay within $250 budget")
    print("3. Implement real AI models instead of enhanced fallback")
    print("4. Deploy missing revolutionary systems")
    print("5. Test all trading capabilities thoroughly")
    
    overall_status = "NEEDS ATTENTION" if (servers_running < 4 or not portfolio_ok or missing_count > 0) else "OPERATIONAL"
    print(f"\nOVERALL STATUS: {overall_status}")

if __name__ == "__main__":
    main()










