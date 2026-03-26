"""
PROMETHEUS LLM CONFIGURATION CHECK
Display current LLM setup and providers
"""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def check_llm_config():
    """Check LLM configuration"""
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]PROMETHEUS LLM CONFIGURATION[/bold cyan]\n"
        "[dim]Current AI/LLM Provider Status[/dim]",
        style="bold white on blue"
    ))
    console.print()
    
    # Load from .env
    env_file = Path('.env')
    config = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value.strip("'\"")
    
    # Primary LLM Provider
    console.print("[bold green]🤖 PRIMARY LLM PROVIDER[/bold green]")
    console.print("="*70)
    
    ai_provider = config.get('AI_PROVIDER', 'unknown')
    use_local = config.get('USE_LOCAL_AI', 'false').lower() == 'true'
    deepseek_enabled = config.get('DEEPSEEK_ENABLED', 'false').lower() == 'true'
    deepseek_model = config.get('DEEPSEEK_MODEL', 'unknown')
    
    if deepseek_enabled and ai_provider == 'deepseek':
        console.print(f"  Provider: [yellow]DeepSeek-R1[/yellow] 🚀")
        console.print(f"  Model: [yellow]{deepseek_model}[/yellow]")
        console.print(f"  Type: [green]LOCAL, FREE, OPEN SOURCE[/green]")
        console.print(f"  Endpoint: [cyan]{config.get('GPT_OSS_API_ENDPOINT', 'http://localhost:11434')}[/cyan]")
        console.print()
        console.print("  [bold green]✅ DeepSeek-R1 is the PRIMARY provider[/bold green]")
        console.print("  [dim]• Revolutionary reasoning capabilities[/dim]")
        console.print("  [dim]• Zero API costs[/dim]")
        console.print("  [dim]• Full privacy (runs locally)[/dim]")
    else:
        console.print(f"  Provider: [yellow]{ai_provider}[/yellow]")
        console.print(f"  Local AI: [yellow]{use_local}[/yellow]")
    
    console.print()
    console.print()
    
    # Available LLM Providers
    console.print("[bold cyan]📚 AVAILABLE LLM PROVIDERS[/bold cyan]")
    console.print("="*70)
    
    table = Table(box=box.ROUNDED)
    table.add_column("Provider", style="cyan")
    table.add_column("Model/Version", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Cost", justify="right", style="green")
    table.add_column("Type", style="dim")
    
    # DeepSeek-R1
    deepseek_status = "✅ ACTIVE" if deepseek_enabled else "❌ DISABLED"
    table.add_row(
        "DeepSeek-R1",
        deepseek_model,
        deepseek_status,
        "FREE",
        "Local/Ollama"
    )
    
    # GPT-OSS / Llama
    gpt_oss_enabled = config.get('GPT_OSS_ENABLED', 'false').lower() == 'true'
    llama_model = config.get('LLAMA_MODEL', 'llama3.1:8b-trading')
    gpt_oss_status = "✅ AVAILABLE" if gpt_oss_enabled else "❌ DISABLED"
    table.add_row(
        "Llama 3.1",
        llama_model,
        gpt_oss_status,
        "FREE",
        "Local/Ollama"
    )
    
    # OpenAI
    openai_key = config.get('OPENAI_API_KEY', '')
    openai_fallback = config.get('OPENAI_FALLBACK', 'false').lower() == 'true'
    if openai_key and len(openai_key) > 20:
        openai_status = "🔄 FALLBACK" if openai_fallback else "⚠️ DISABLED"
        table.add_row(
            "OpenAI GPT-4",
            "gpt-4o-mini",
            openai_status,
            "$0.002/call",
            "Cloud/Paid"
        )
    else:
        table.add_row(
            "OpenAI GPT-4",
            "N/A",
            "❌ NO API KEY",
            "$$$",
            "Cloud/Paid"
        )
    
    # Anthropic Claude
    anthropic_key = config.get('ANTHROPIC_API_KEY', '')
    if anthropic_key and len(anthropic_key) > 20:
        table.add_row(
            "Anthropic Claude",
            "claude-3.5-sonnet",
            "✅ AVAILABLE",
            "$0.003/call",
            "Cloud/Paid (Visual AI)"
        )
    else:
        table.add_row(
            "Anthropic Claude",
            "N/A",
            "❌ NO API KEY",
            "$$$",
            "Cloud/Paid"
        )
    
    # Google Gemini
    gemini_key = config.get('GOOGLE_AI_API_KEY', '')
    if gemini_key and len(gemini_key) > 20:
        table.add_row(
            "Google Gemini",
            "gemini-pro",
            "✅ AVAILABLE",
            "FREE tier",
            "Cloud (Visual AI)"
        )
    else:
        table.add_row(
            "Google Gemini",
            "N/A",
            "❌ NO API KEY",
            "FREE tier",
            "Cloud"
        )
    
    console.print(table)
    console.print()
    console.print()
    
    # LLM Usage in Prometheus
    console.print("[bold magenta]🧠 HOW PROMETHEUS USES LLMs[/bold magenta]")
    console.print("="*70)
    
    usage_table = Table(box=box.SIMPLE)
    usage_table.add_column("Function", style="cyan")
    usage_table.add_column("LLM Used", style="yellow")
    usage_table.add_column("Purpose", style="dim")
    
    usage_table.add_row(
        "Market Analysis",
        "DeepSeek-R1",
        "Analyze market data, generate trading signals"
    )
    usage_table.add_row(
        "Reasoning Engine",
        "DeepSeek-R1",
        "Multi-step reasoning for complex decisions"
    )
    usage_table.add_row(
        "Visual Pattern Recognition",
        "Claude 3.5 Sonnet",
        "Chart pattern analysis and visual AI"
    )
    usage_table.add_row(
        "Sentiment Analysis",
        "Gemini Pro",
        "News and social media sentiment"
    )
    usage_table.add_row(
        "Fallback Intelligence",
        "GPT-4o-mini",
        "When DeepSeek unavailable (rarely used)"
    )
    
    console.print(usage_table)
    console.print()
    console.print()
    
    # Cost Analysis
    console.print("[bold yellow]💰 COST ANALYSIS[/bold yellow]")
    console.print("="*70)
    
    console.print("  [bold green]PRIMARY: DeepSeek-R1 (100% Free)[/bold green]")
    console.print("    • Zero API costs")
    console.print("    • Unlimited requests")
    console.print("    • Runs locally via Ollama")
    console.print()
    
    if openai_fallback and openai_key:
        console.print("  [yellow]FALLBACK: OpenAI GPT-4o-mini[/yellow]")
        console.print("    • ~$0.002 per market analysis")
        console.print("    • Only used if DeepSeek fails")
        console.print("    • Rarely triggered (< 1% of calls)")
        console.print()
    
    if anthropic_key:
        console.print("  [cyan]VISUAL AI: Claude 3.5 Sonnet[/cyan]")
        console.print("    • ~$0.003 per chart analysis")
        console.print("    • Used for visual pattern recognition")
        console.print("    • Optional enhancement feature")
        console.print()
    
    console.print()
    
    # Configuration Status
    console.print("[bold green]✅ CONFIGURATION STATUS[/bold green]")
    console.print("="*70)
    
    if deepseek_enabled and ai_provider == 'deepseek':
        console.print("  🚀 [bold green]Prometheus is using DeepSeek-R1 (FREE, LOCAL)[/bold green]")
        console.print("  📍 Running at: http://localhost:11434")
        console.print("  🧠 Model: " + deepseek_model)
        console.print()
        console.print("  [dim]DeepSeek-R1 provides:[/dim]")
        console.print("  [dim]  • Revolutionary reasoning capabilities[/dim]")
        console.print("  [dim]  • Zero API costs[/dim]")
        console.print("  [dim]  • Full data privacy[/dim]")
        console.print("  [dim]  • 14B parameter model (comparable to GPT-3.5)[/dim]")
    else:
        console.print("  ⚠️  [yellow]Warning: DeepSeek not active[/yellow]")
        console.print("  Current provider: " + ai_provider)
    
    console.print()
    console.print()
    
    # Recommendations
    console.print("[bold cyan]💡 RECOMMENDATIONS[/bold cyan]")
    console.print("="*70)
    
    if not deepseek_enabled:
        console.print("  ⚠️  Enable DeepSeek-R1 for FREE local AI")
        console.print("     Set: DEEPSEEK_ENABLED='true' in .env")
        console.print()
    
    if openai_fallback:
        console.print("  ℹ️  OpenAI fallback is enabled (costs money)")
        console.print("     Consider disabling: OPENAI_FALLBACK='false'")
        console.print()
    
    if deepseek_enabled and ai_provider == 'deepseek':
        console.print("  ✅ [green]Configuration is optimal![/green]")
        console.print("     Using FREE local AI with zero costs")
    
    console.print()
    console.print("="*70)
    console.print()


def main():
    check_llm_config()


if __name__ == "__main__":
    main()
