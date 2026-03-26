"""
AI Cost Comparison: OpenAI vs DeepSeek Local
Shows exactly how much money you'll save
"""

class AICostCalculator:
    """Calculate and compare AI costs"""
    
    def __init__(self):
        # OpenAI pricing (GPT-4o-mini)
        self.openai_input_cost = 0.00015  # per 1K tokens
        self.openai_output_cost = 0.0006  # per 1K tokens
        
        # Anthropic pricing (Claude 3.5 Sonnet)
        self.anthropic_input_cost = 0.003  # per 1K tokens
        self.anthropic_output_cost = 0.015  # per 1K tokens
        
        # DeepSeek pricing
        self.deepseek_cost = 0.0  # FREE!
        
        # Typical PROMETHEUS usage
        self.requests_per_hour = 100  # Market analysis, signals, etc.
        self.avg_input_tokens = 500
        self.avg_output_tokens = 200
        self.trading_hours_per_day = 6.5  # Market hours
        self.trading_days_per_month = 21
    
    def calculate_openai_cost(self, hours=1):
        """Calculate OpenAI cost"""
        total_requests = self.requests_per_hour * hours
        
        input_cost = (total_requests * self.avg_input_tokens / 1000) * self.openai_input_cost
        output_cost = (total_requests * self.avg_output_tokens / 1000) * self.openai_output_cost
        
        return input_cost + output_cost
    
    def calculate_anthropic_cost(self, hours=1):
        """Calculate Anthropic cost"""
        total_requests = self.requests_per_hour * hours
        
        input_cost = (total_requests * self.avg_input_tokens / 1000) * self.anthropic_input_cost
        output_cost = (total_requests * self.avg_output_tokens / 1000) * self.anthropic_output_cost
        
        return input_cost + output_cost
    
    def calculate_deepseek_cost(self, hours=1):
        """Calculate DeepSeek cost"""
        return 0.0  # Always FREE!
    
    def show_comparison(self):
        """Show detailed cost comparison"""
        print("\n" + "=" * 70)
        print("💰 AI COST COMPARISON: OpenAI vs Anthropic vs DeepSeek")
        print("=" * 70)
        
        print(f"\n📊 PROMETHEUS Usage Assumptions:")
        print(f"   • {self.requests_per_hour} AI requests per hour")
        print(f"   • {self.avg_input_tokens} input tokens per request")
        print(f"   • {self.avg_output_tokens} output tokens per request")
        print(f"   • {self.trading_hours_per_day} trading hours per day")
        print(f"   • {self.trading_days_per_month} trading days per month")
        
        # Hourly costs
        print("\n" + "-" * 70)
        print("⏱️  HOURLY COSTS:")
        print("-" * 70)
        openai_hour = self.calculate_openai_cost(1)
        anthropic_hour = self.calculate_anthropic_cost(1)
        deepseek_hour = self.calculate_deepseek_cost(1)
        
        print(f"   OpenAI (GPT-4o-mini):     ${openai_hour:.4f}/hour")
        print(f"   Anthropic (Claude 3.5):   ${anthropic_hour:.4f}/hour")
        print(f"   DeepSeek (Local):         ${deepseek_hour:.4f}/hour  ✅ FREE!")
        
        # Daily costs
        print("\n" + "-" * 70)
        print("📅 DAILY COSTS:")
        print("-" * 70)
        openai_day = self.calculate_openai_cost(self.trading_hours_per_day)
        anthropic_day = self.calculate_anthropic_cost(self.trading_hours_per_day)
        deepseek_day = self.calculate_deepseek_cost(self.trading_hours_per_day)
        
        print(f"   OpenAI:     ${openai_day:.2f}/day")
        print(f"   Anthropic:  ${anthropic_day:.2f}/day")
        print(f"   DeepSeek:   ${deepseek_day:.2f}/day  ✅ FREE!")
        
        # Monthly costs
        print("\n" + "-" * 70)
        print("📆 MONTHLY COSTS:")
        print("-" * 70)
        openai_month = openai_day * self.trading_days_per_month
        anthropic_month = anthropic_day * self.trading_days_per_month
        deepseek_month = deepseek_day * self.trading_days_per_month
        
        print(f"   OpenAI:     ${openai_month:.2f}/month")
        print(f"   Anthropic:  ${anthropic_month:.2f}/month")
        print(f"   DeepSeek:   ${deepseek_month:.2f}/month  ✅ FREE!")
        
        # Annual costs
        print("\n" + "-" * 70)
        print("📊 ANNUAL COSTS:")
        print("-" * 70)
        openai_year = openai_month * 12
        anthropic_year = anthropic_month * 12
        deepseek_year = deepseek_month * 12
        
        print(f"   OpenAI:     ${openai_year:.2f}/year")
        print(f"   Anthropic:  ${anthropic_year:.2f}/year")
        print(f"   DeepSeek:   ${deepseek_year:.2f}/year  ✅ FREE!")
        
        # Savings
        print("\n" + "=" * 70)
        print("💵 SAVINGS WITH DEEPSEEK:")
        print("=" * 70)
        print(f"   vs OpenAI:     ${openai_year:.2f}/year saved")
        print(f"   vs Anthropic:  ${anthropic_year:.2f}/year saved")
        
        # ROI
        print("\n" + "=" * 70)
        print("📈 RETURN ON INVESTMENT:")
        print("=" * 70)
        
        # Assume $10,000 portfolio
        portfolio = 10000
        openai_roi_impact = (openai_year / portfolio) * 100
        anthropic_roi_impact = (anthropic_year / portfolio) * 100
        
        print(f"\n   On a ${portfolio:,} portfolio:")
        print(f"   • OpenAI costs = {openai_roi_impact:.2f}% of portfolio")
        print(f"   • Anthropic costs = {anthropic_roi_impact:.2f}% of portfolio")
        print(f"   • DeepSeek costs = 0.00% of portfolio  ✅")
        
        print(f"\n   💡 To break even on OpenAI costs, you need:")
        print(f"      {openai_roi_impact:.2f}% annual return just to cover AI fees!")
        
        print(f"\n   💡 With DeepSeek, ALL profits are yours!")
        
        # Scaling
        print("\n" + "=" * 70)
        print("🚀 SCALING BENEFITS:")
        print("=" * 70)
        
        print("\n   With DeepSeek, you can run:")
        print("   • 80+ Revolutionary AI Systems simultaneously")
        print("   • Unlimited market analysis requests")
        print("   • Real-time sentiment analysis on 1000s of stocks")
        print("   • Continuous learning and optimization")
        print("   • All at $0 cost!")
        
        print("\n   With OpenAI/Anthropic:")
        print("   • Limited by budget")
        print("   • Rate limits restrict scaling")
        print("   • Each new feature = more costs")
        
        # Privacy
        print("\n" + "=" * 70)
        print("🔒 PRIVACY BENEFITS:")
        print("=" * 70)
        
        print("\n   OpenAI/Anthropic:")
        print("   ❌ Your trading data sent to cloud")
        print("   ❌ Potential data breaches")
        print("   ❌ Terms of service changes")
        print("   ❌ Requires internet connection")
        
        print("\n   DeepSeek (Local):")
        print("   ✅ Data never leaves your machine")
        print("   ✅ Complete privacy")
        print("   ✅ No terms of service")
        print("   ✅ Works offline")
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 SUMMARY:")
        print("=" * 70)
        
        print(f"\n   By switching to DeepSeek, you save:")
        print(f"   • ${openai_month:.2f}/month (vs OpenAI)")
        print(f"   • ${openai_year:.2f}/year (vs OpenAI)")
        print(f"   • {openai_roi_impact:.2f}% of your portfolio annually")
        
        print(f"\n   Plus you get:")
        print("   ✅ Unlimited requests (no rate limits)")
        print("   ✅ Complete privacy (data stays local)")
        print("   ✅ Faster responses (no network latency)")
        print("   ✅ Works offline (no internet required)")
        print("   ✅ Smarter AI (DeepSeek > GPT-4 for many tasks)")
        
        print("\n" + "=" * 70)
        print("🚀 READY TO SAVE MONEY?")
        print("=" * 70)
        print("\n   Run: python setup_deepseek_local.py")
        print("\n" + "=" * 70)

def main():
    calculator = AICostCalculator()
    calculator.show_comparison()

if __name__ == "__main__":
    main()

