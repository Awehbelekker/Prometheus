"""Show competitor rankings to understand what we need to beat"""
from prometheus_50_year_competitor_benchmark import CompetitorBenchmark
b = CompetitorBenchmark()
comps = b.competitors
print("=" * 80)
print("  COMPETITOR RANKINGS (what Prometheus must beat for Top 3)")
print("=" * 80)
for i, (name, data) in enumerate(sorted(comps.items(), key=lambda x: x[1].get('cagr', 0), reverse=True), 1):
    cagr = data.get('cagr', 0) * 100
    sharpe = data.get('sharpe', 0)
    dd = data.get('max_dd', 0) * 100
    style = data.get('style', '')
    print(f"  #{i:2d}  {cagr:6.2f}% CAGR | {sharpe:5.2f} Sharpe | {dd:6.1f}% DD | {name} ({style})")
print("=" * 80)
