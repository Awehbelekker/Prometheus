"""
Verify DeepSeek Integration with PROMETHEUS
Shows complete status and readiness
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def check_ollama_server():
    """Check if Ollama server is running"""
    print_header("1. OLLAMA SERVER STATUS")
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("   Status: RUNNING")
            print(f"   Models installed: {len(models)}")
            
            for model in models:
                name = model.get('name', 'unknown')
                size_gb = model.get('size', 0) / (1024**3)
                print(f"      - {name} ({size_gb:.1f} GB)")
            
            return True
        else:
            print("   Status: NOT RESPONDING")
            return False
    except Exception as e:
        print(f"   Status: NOT RUNNING")
        print(f"   Error: {e}")
        print("\n   To start: ollama serve")
        return False

def check_configuration():
    """Check PROMETHEUS configuration"""
    print_header("2. PROMETHEUS CONFIGURATION")
    
    config = {
        'GPT_OSS_ENABLED': os.getenv('GPT_OSS_ENABLED', 'false'),
        'DEEPSEEK_ENABLED': os.getenv('DEEPSEEK_ENABLED', 'false'),
        'DEEPSEEK_MODEL': os.getenv('DEEPSEEK_MODEL', 'not set'),
        'AI_PROVIDER': os.getenv('AI_PROVIDER', 'not set'),
        'USE_LOCAL_AI': os.getenv('USE_LOCAL_AI', 'false'),
        'OPENAI_FALLBACK': os.getenv('OPENAI_FALLBACK', 'true'),
    }
    
    for key, value in config.items():
        status = "OK" if value.lower() in ['true', 'deepseek', 'deepseek-r1:8b', 'deepseek-r1:14b'] else "INFO"
        print(f"   [{status}] {key} = {value}")
    
    return config.get('DEEPSEEK_ENABLED', 'false').lower() == 'true'

def check_adapter():
    """Check if DeepSeek adapter exists"""
    print_header("3. DEEPSEEK ADAPTER")
    
    adapter_path = Path("core/deepseek_adapter.py")
    if adapter_path.exists():
        lines = len(adapter_path.read_text().splitlines())
        print(f"   Status: INSTALLED")
        print(f"   Location: {adapter_path}")
        print(f"   Lines of code: {lines}")
        return True
    else:
        print(f"   Status: NOT FOUND")
        print(f"   Expected: {adapter_path}")
        return False

def check_unified_provider():
    """Check unified AI provider"""
    print_header("4. UNIFIED AI PROVIDER")
    
    provider_path = Path("core/unified_ai_provider.py")
    if provider_path.exists():
        lines = len(provider_path.read_text().splitlines())
        print(f"   Status: INSTALLED")
        print(f"   Location: {provider_path}")
        print(f"   Lines of code: {lines}")
        return True
    else:
        print(f"   Status: NOT FOUND")
        return False

def calculate_savings():
    """Calculate potential savings"""
    print_header("5. COST SAVINGS ANALYSIS")
    
    # Assumptions
    requests_per_hour = 100
    trading_hours_per_day = 6.5
    trading_days_per_month = 21
    
    # OpenAI costs
    openai_cost_per_request = 0.0002
    monthly_requests = requests_per_hour * trading_hours_per_day * trading_days_per_month
    openai_monthly_cost = monthly_requests * openai_cost_per_request
    openai_annual_cost = openai_monthly_cost * 12
    
    # DeepSeek costs
    deepseek_cost = 0.0
    
    print(f"   Estimated monthly requests: {monthly_requests:,.0f}")
    print(f"   OpenAI monthly cost: ${openai_monthly_cost:.2f}")
    print(f"   DeepSeek monthly cost: ${deepseek_cost:.2f}")
    print(f"\n   MONTHLY SAVINGS: ${openai_monthly_cost:.2f}")
    print(f"   ANNUAL SAVINGS: ${openai_annual_cost:.2f}")

def show_next_steps(all_ready):
    """Show next steps"""
    print_header("6. NEXT STEPS")
    
    if all_ready:
        print("\n   ALL SYSTEMS READY!")
        print("\n   To launch PROMETHEUS with DeepSeek:")
        print("      python launch_ultimate_prometheus_LIVE_TRADING.py")
        print("\n   Benefits:")
        print("      - $0 AI costs (was $30-700/year)")
        print("      - Unlimited requests (no rate limits)")
        print("      - Complete privacy (data stays local)")
        print("      - Faster responses (no network latency)")
    else:
        print("\n   SETUP INCOMPLETE")
        print("\n   Missing components:")
        if not check_ollama_server():
            print("      - Ollama server not running")
            print("        Fix: ollama serve")
        if not check_configuration():
            print("      - Configuration not set")
            print("        Fix: python integrate_deepseek_prometheus.py")
        if not check_adapter():
            print("      - DeepSeek adapter missing")
            print("        Fix: python integrate_deepseek_prometheus.py")

def main():
    """Main verification"""
    print("\n" + "=" * 70)
    print("DEEPSEEK INTEGRATION VERIFICATION FOR PROMETHEUS")
    print("=" * 70)
    
    # Run checks
    ollama_ok = check_ollama_server()
    config_ok = check_configuration()
    adapter_ok = check_adapter()
    provider_ok = check_unified_provider()
    
    # Calculate savings
    calculate_savings()
    
    # Show next steps
    all_ready = ollama_ok and config_ok and adapter_ok and provider_ok
    show_next_steps(all_ready)
    
    # Summary
    print_header("SUMMARY")
    
    status_items = [
        ("Ollama Server", ollama_ok),
        ("Configuration", config_ok),
        ("DeepSeek Adapter", adapter_ok),
        ("Unified AI Provider", provider_ok),
    ]
    
    for item, status in status_items:
        symbol = "OK" if status else "!!"
        print(f"   [{symbol}] {item}")
    
    if all_ready:
        print("\n   STATUS: READY TO LAUNCH")
        print("   COST: $0/month (FREE!)")
    else:
        print("\n   STATUS: SETUP INCOMPLETE")
        print("   Run: python integrate_deepseek_prometheus.py")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

