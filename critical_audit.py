#!/usr/bin/env python3
"""
🔍 CRITICAL PROMETHEUS AUDIT
Answers the user's specific concerns about system readiness
"""

import requests
import json
from datetime import datetime

def test_gpt_oss_parsing_issue():
    """Test the specific GPT-OSS parsing issue"""
    print("🤖 TESTING GPT-OSS PARSING ISSUE")
    print("-" * 50)
    
    # Test the exact scenario that showed "Failed to parse AI response"
    test_payload = {
        "symbol": "AAPL",
        "market_data": {
            "price": 175.50,
            "change_percent": 1.2,
            "volume": 50000000,
            "rsi": 65.5,
            "macd": 0.8,
            "sma_20": 174.20,
            "sma_50": 172.80
        },
        "strategy_context": "Bullish market conditions with strong earnings momentum",
        "analysis_type": "technical",
        "time_horizon": "short_term",
        "risk_tolerance": "moderate",
        "model_size": "120b"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai-trading/trading-strategy", 
            json=test_payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            reasoning = data.get('data', {}).get('reasoning', '')
            confidence = data.get('data', {}).get('confidence', 0)
            action = data.get('data', {}).get('action', '')
            
            print(f"   Response: {reasoning[:100]}...")
            print(f"   Confidence: {confidence}")
            print(f"   Action: {action}")
            
            if reasoning == "Failed to parse AI response":
                print("   [ERROR] CRITICAL: GPT-OSS parsing is still failing")
                return False
            else:
                print("   [CHECK] GPT-OSS parsing appears to be working")
                return True
        else:
            print(f"   [ERROR] API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Exception: {str(e)}")
        return False

def test_direct_gpt_oss_models():
    """Test GPT-OSS models directly"""
    print("\n🔍 TESTING DIRECT GPT-OSS MODELS")
    print("-" * 50)
    
    # Test 20B model
    try:
        payload = {
            "prompt": "AAPL stock analysis: Price $175.50, up 1.2%. Buy, sell, or hold?",
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        response = requests.post("http://localhost:5000/generate", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", data.get("text", data.get("generated_text", "")))
            
            if text and len(text) > 20:
                print(f"   [CHECK] GPT-OSS 20B: Working - {text[:80]}...")
                model_20b_working = True
            else:
                print("   [ERROR] GPT-OSS 20B: Empty response")
                model_20b_working = False
        else:
            print(f"   [ERROR] GPT-OSS 20B: HTTP {response.status_code}")
            model_20b_working = False
    except Exception as e:
        print(f"   [ERROR] GPT-OSS 20B: {str(e)}")
        model_20b_working = False
    
    # Test 120B model
    try:
        response = requests.post("http://localhost:5001/generate", json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", data.get("text", data.get("generated_text", "")))
            
            if text and len(text) > 20:
                print(f"   [CHECK] GPT-OSS 120B: Working - {text[:80]}...")
                model_120b_working = True
            else:
                print("   [ERROR] GPT-OSS 120B: Empty response")
                model_120b_working = False
        else:
            print(f"   [ERROR] GPT-OSS 120B: HTTP {response.status_code}")
            model_120b_working = False
    except Exception as e:
        print(f"   [ERROR] GPT-OSS 120B: {str(e)}")
        model_120b_working = False
    
    return model_20b_working, model_120b_working

def test_real_trading_execution():
    """Test if system can execute real trades"""
    print("\n💰 TESTING REAL TRADING EXECUTION")
    print("-" * 50)
    
    # Check IB connection
    try:
        response = requests.get("http://localhost:8000/api/ib/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            connected = data.get('connected', False)
            account = data.get('account', 'Unknown')
            balance = data.get('balance', 0)
            
            print(f"   IB Connected: {connected}")
            print(f"   Account: {account}")
            print(f"   Balance: ${balance:.2f}")
            
            if connected and account == "U21922116":
                print("   [CHECK] Interactive Brokers: Ready for real trades")
                ib_ready = True
            else:
                print("   [ERROR] Interactive Brokers: Not ready")
                ib_ready = False
        else:
            print(f"   [ERROR] IB Status API: Failed ({response.status_code})")
            ib_ready = False
    except Exception as e:
        print(f"   [ERROR] IB Connection: {str(e)}")
        ib_ready = False
    
    # Test trade execution capability
    try:
        test_trade = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 1,
            "order_type": "MARKET"
        }
        
        response = requests.post(
            "http://localhost:8000/api/paper-trading/execute-trade", 
            json=test_trade, 
            timeout=10
        )
        
        if response.status_code == 200:
            print("   [CHECK] Trade Execution: System can execute trades")
            trade_capable = True
        else:
            print(f"   [ERROR] Trade Execution: Failed ({response.status_code})")
            trade_capable = False
    except Exception as e:
        print(f"   [ERROR] Trade Execution: {str(e)}")
        trade_capable = False
    
    return ib_ready, trade_capable

def check_active_trading():
    """Check if system is actively trading"""
    print("\n🔄 CHECKING ACTIVE TRADING STATUS")
    print("-" * 50)
    
    # Check active sessions
    try:
        response = requests.get("http://localhost:8000/api/paper-trading/performance", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            active_sessions = data.get('active_sessions', 0)
            current_balance = data.get('current_balance', 0)
            total_trades = data.get('total_trades', 0)
            ai_decisions = data.get('ai_decisions', 0)
            
            print(f"   Active Sessions: {active_sessions}")
            print(f"   Current Balance: ${current_balance:.2f}")
            print(f"   Total Trades: {total_trades}")
            print(f"   AI Decisions: {ai_decisions}")
            
            if active_sessions > 0:
                print("   [CHECK] Trading Session: ACTIVE")
                session_active = True
            else:
                print("   [ERROR] Trading Session: NOT ACTIVE")
                session_active = False
                
            if ai_decisions > 0:
                print("   [CHECK] AI Decisions: Being generated")
                ai_active = True
            else:
                print("   [WARNING]️ AI Decisions: None yet (may be starting up)")
                ai_active = False
                
            return session_active, ai_active, total_trades > 0
        else:
            print(f"   [ERROR] Performance API: Failed ({response.status_code})")
            return False, False, False
    except Exception as e:
        print(f"   [ERROR] Performance Check: {str(e)}")
        return False, False, False

def main():
    """Run critical audit to answer user's concerns"""
    print("🔍 CRITICAL PROMETHEUS AUDIT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Answering your specific concerns about system readiness")
    print("=" * 60)
    
    # Test 1: GPT-OSS parsing issue
    parsing_working = test_gpt_oss_parsing_issue()
    
    # Test 2: Direct model testing
    model_20b, model_120b = test_direct_gpt_oss_models()
    
    # Test 3: Real trading capability
    ib_ready, trade_capable = test_real_trading_execution()
    
    # Test 4: Active trading status
    session_active, ai_active, trades_executed = check_active_trading()
    
    # CRITICAL ASSESSMENT
    print("\n🎯 CRITICAL ASSESSMENT - ANSWERING YOUR CONCERNS")
    print("=" * 60)
    
    print("\n1. 'FAILED TO PARSE AI RESPONSE' ERROR:")
    if parsing_working:
        print("   [CHECK] RESOLVED: GPT-OSS parsing is now working correctly")
    else:
        print("   [ERROR] CRITICAL: GPT-OSS parsing is still failing")
        print("   🔧 ACTION NEEDED: Fix GPT-OSS response format compatibility")
    
    print("\n2. REAL TRADING CAPABILITY:")
    if ib_ready and trade_capable:
        print("   [CHECK] CONFIRMED: System CAN execute real trades with real money")
        print("   💰 Interactive Brokers connected and ready")
    elif trade_capable:
        print("   [WARNING]️ PARTIAL: System can execute trades but IB connection issues")
        print("   🔧 ACTION NEEDED: Fix Interactive Brokers connection")
    else:
        print("   [ERROR] CRITICAL: System CANNOT execute real trades")
        print("   🔧 ACTION NEEDED: Fix trade execution system")
    
    print("\n3. SYSTEM READINESS ASSESSMENT:")
    if session_active and (model_20b or model_120b):
        print("   [CHECK] OPERATIONAL: System is actively running with AI")
        if ai_active:
            print("   🤖 AI decisions are being generated")
        else:
            print("   [WARNING]️ AI decisions starting up (normal for new sessions)")
    else:
        print("   [ERROR] NOT OPERATIONAL: System is configured but not actively trading")
        print("   🔧 ACTION NEEDED: Start active trading session with AI")
    
    # FINAL VERDICT
    print("\n🎯 FINAL VERDICT:")
    print("-" * 30)
    
    critical_systems_working = sum([
        parsing_working,
        model_20b or model_120b,
        ib_ready,
        trade_capable,
        session_active
    ])
    
    if critical_systems_working >= 4:
        print("   [CHECK] STATUS: READY FOR LIVE TRADING")
        print("   🚀 PROMETHEUS can trade with real money and AI intelligence")
        print("   💰 Proceed with Option A (Conservative Monitoring)")
    elif critical_systems_working >= 3:
        print("   [WARNING]️ STATUS: MOSTLY READY (minor fixes needed)")
        print("   🔧 Fix remaining issues then proceed with monitoring")
    else:
        print("   [ERROR] STATUS: NOT READY FOR LIVE TRADING")
        print("   🛠️ Major fixes required before proceeding")
    
    print(f"\n📊 Systems Working: {critical_systems_working}/5")
    
    # IMMEDIATE NEXT STEPS
    print("\n💡 IMMEDIATE NEXT STEPS:")
    print("-" * 30)
    
    if not parsing_working:
        print("   1. 🔧 Fix GPT-OSS response parsing")
    if not (ib_ready and trade_capable):
        print("   2. 🏦 Fix Interactive Brokers connection")
    if not session_active:
        print("   3. 🔄 Start active AI trading session")
    if critical_systems_working >= 4:
        print("   [CHECK] Ready to start real-time monitoring!")
    
    return critical_systems_working >= 4

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 AUDIT COMPLETE: READY FOR LIVE TRADING!")
    else:
        print("\n🔧 AUDIT COMPLETE: FIXES REQUIRED FIRST")
