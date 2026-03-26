#!/usr/bin/env python3
"""
ANALYZE RAM USAGE AND AI INTEGRATION
Check what's using RAM and verify all AI features are integrated
"""

import psutil
import requests
import json
from datetime import datetime

def analyze_ram_usage():
    """Analyze what's using your RAM"""
    print("DETAILED RAM USAGE ANALYSIS")
    print("=" * 60)
    
    memory = psutil.virtual_memory()
    print(f"Total RAM: {memory.total / (1024**3):.1f} GB")
    print(f"Available RAM: {memory.available / (1024**3):.1f} GB")
    print(f"Used RAM: {memory.used / (1024**3):.1f} GB")
    print(f"Memory Usage: {memory.percent:.1f}%")
    
    print(f"\nTOP MEMORY CONSUMERS:")
    print("-" * 40)
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status']):
        try:
            memory_mb = proc.info['memory_info'].rss / (1024**2)
            if memory_mb > 50:  # Only show processes using >50MB
                processes.append((
                    proc.info['pid'], 
                    proc.info['name'], 
                    memory_mb, 
                    proc.info['cpu_percent'],
                    proc.info['status']
                ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory usage
    processes.sort(key=lambda x: x[2], reverse=True)
    
    total_analyzed = 0
    for i, (pid, name, memory_mb, cpu_percent, status) in enumerate(processes[:15]):
        print(f"{i+1:2d}. {name:<25} (PID {pid:>6}): {memory_mb:>8.1f} MB, CPU: {cpu_percent:>5.1f}%, Status: {status}")
        total_analyzed += memory_mb
    
    print(f"\nTotal analyzed: {total_analyzed:.1f} MB")
    print(f"Remaining usage: {(memory.used / (1024**2)) - total_analyzed:.1f} MB (system/kernel)")
    
    return memory.available / (1024**3)

def check_ai_integration():
    """Check if all AI features are integrated to main server"""
    print("\nAI INTEGRATION ANALYSIS")
    print("=" * 60)
    
    # Test main server AI endpoints
    ai_endpoints = [
        ("AI Coordinator", "/api/ai/coordinator/status"),
        ("AI Learning", "/api/ai/learning/status"),
        ("Hierarchical Agents", "/api/ai/agents/status"),
        ("SynergyCore Agent", "/api/ai/agents/synergycore/status"),
        ("CogniFlow Agent", "/api/ai/agents/cogniflow/status"),
        ("EdgeMind Agent", "/api/ai/agents/edgemind/status"),
        ("NeuralMesh Agent", "/api/ai/agents/neuralmesh/status"),
        ("CodeSwarm Agent", "/api/ai/agents/codeswarm/status"),
        ("Quantum Engine", "/api/quantum/status"),
        ("Think Mesh", "/api/think-mesh/status"),
        ("Market Oracle", "/api/market-oracle/status"),
        ("Continuous Learning", "/api/learning/continuous-learning/status"),
        ("Advanced Learning", "/api/learning/advanced-learning/status"),
        ("Autonomous Improvement", "/api/learning/autonomous-improvement/status"),
        ("AI Consciousness", "/api/ai/consciousness/status"),
        ("Crypto Engine", "/api/trading/crypto-engine/status"),
        ("Options Engine", "/api/trading/options-engine/status"),
        ("Advanced Engine", "/api/trading/advanced-engine/status"),
        ("Market Maker", "/api/trading/market-maker/status"),
        ("Master Engine", "/api/trading/master-engine/status"),
        ("HRM Engine", "/api/trading/hrm-engine/status")
    ]
    
    integrated_count = 0
    total_count = len(ai_endpoints)
    
    print("Testing AI endpoints on main server (port 8000):")
    print("-" * 50)
    
    for name, endpoint in ai_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"[INTEGRATED] {name}")
                integrated_count += 1
            else:
                print(f"[MISSING] {name}: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)}")
    
    print(f"\nIntegration Status: {integrated_count}/{total_count} AI features integrated")
    
    return integrated_count, total_count

def check_revolutionary_features():
    """Check if revolutionary features are working"""
    print("\nREVOLUTIONARY FEATURES ANALYSIS")
    print("=" * 60)
    
    # Check if revolutionary server is running
    try:
        response = requests.get("http://localhost:8002/health", timeout=3)
        if response.status_code == 200:
            print("[RUNNING] Revolutionary Server (Port 8002)")
            revolutionary_running = True
        else:
            print("[DOWN] Revolutionary Server (Port 8002)")
            revolutionary_running = False
    except Exception as e:
        print(f"[ERROR] Revolutionary Server: {str(e)}")
        revolutionary_running = False
    
    # Check GPT-OSS servers
    gpt_servers = [
        ("GPT-OSS 20B", "http://localhost:5000/health"),
        ("GPT-OSS 120B", "http://localhost:5001/health")
    ]
    
    gpt_running = 0
    for name, url in gpt_servers:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"[RUNNING] {name}")
                gpt_running += 1
            else:
                print(f"[DOWN] {name}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)}")
    
    return revolutionary_running, gpt_running

def optimize_for_real_ai():
    """Optimize system for real AI performance"""
    print("\nOPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    
    # Check current memory
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    print(f"Current available memory: {available_gb:.1f} GB")
    
    if available_gb >= 20:
        print("SUFFICIENT MEMORY: Can run real AI models")
        print("Recommendations:")
        print("1. Configure OpenAI API key for GPT-4 access")
        print("2. Configure Anthropic API key for Claude access")
        print("3. Enable real model loading")
        print("4. Use external APIs for optimal performance")
    elif available_gb >= 10:
        print("GOOD MEMORY: Can run enhanced AI")
        print("Recommendations:")
        print("1. Use external APIs (OpenAI/Anthropic)")
        print("2. Optimize current enhanced AI")
        print("3. Consider cloud deployment for heavy models")
    else:
        print("LIMITED MEMORY: Need to free up RAM")
        print("Recommendations:")
        print("1. Close unnecessary applications")
        print("2. Restart system to free memory")
        print("3. Use external APIs instead of local models")
        print("4. Consider hardware upgrade")
    
    print("\nFOR REAL AI INTELLIGENCE:")
    print("1. Set environment variables:")
    print("   set OPENAI_API_KEY=your_key_here")
    print("   set ANTHROPIC_API_KEY=your_key_here")
    print("2. Restart servers to load real AI")
    print("3. Test with real market data")
    print("4. Monitor performance and accuracy")

def main():
    """Main analysis function"""
    print("PROMETHEUS RAM USAGE & AI INTEGRATION ANALYSIS")
    print("=" * 70)
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Analyze RAM usage
    available_ram = analyze_ram_usage()
    
    # Check AI integration
    integrated_count, total_count = check_ai_integration()
    
    # Check revolutionary features
    revolutionary_running, gpt_running = check_revolutionary_features()
    
    # Optimization recommendations
    optimize_for_real_ai()
    
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    
    print(f"Available RAM: {available_ram:.1f} GB")
    print(f"AI Features Integrated: {integrated_count}/{total_count}")
    print(f"Revolutionary Server: {'Running' if revolutionary_running else 'Down'}")
    print(f"GPT-OSS Servers: {gpt_running}/2 running")
    
    if integrated_count == total_count and gpt_running >= 1:
        print("\nSTATUS: FULLY INTEGRATED AND OPERATIONAL")
        print("All AI features are integrated to main server")
        print("System ready for real AI trading")
    elif integrated_count >= total_count * 0.8:
        print("\nSTATUS: MOSTLY INTEGRATED")
        print("Most AI features are integrated")
        print("Minor integration issues to resolve")
    else:
        print("\nSTATUS: NEEDS INTEGRATION")
        print("Many AI features not integrated")
        print("Need to complete integration")
    
    print(f"\nAnalysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

