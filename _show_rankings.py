import json, glob
files = sorted(glob.glob('benchmark_50_year_*.json'))
f = files[-1]
with open(f) as fh:
    r = json.load(fh)
print(f"Report: {f}")
print("Rankings:")
for item in r['rankings']:
    rank = item['rank']
    cagr = item['cagr'] * 100
    sharpe = item['sharpe']
    dd = item['max_drawdown'] * 100
    name = item['name']
    marker = " >>> " if name == 'prometheus' else "     "
    print(f"  #{rank:2d}{marker}{cagr:7.2f}%  Sharpe {sharpe:5.2f}  DD {dd:6.1f}%  {name}")
print()
print(f"Prometheus rank: #{r['prometheus_rank']}")
print(f"Beaten: {r['competitors_beaten']}/{r['total_competitors']}")
