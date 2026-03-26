import json, glob

base = json.load(open('benchmark_50_year_20260309_225939.json'))
latest = sorted(glob.glob('benchmark_50_year_202603*.json'))[-1]
print('Latest file:', latest)
new = json.load(open(latest))

def pct(v): return round(float(v)*100, 2)
def r3(v):  return round(float(v), 3)

rows = [
    ('Rank',          base['prometheus_rank'],                              new['prometheus_rank'],                              new['prometheus_rank'] - base['prometheus_rank']),
    ('Legacy CAGR%',  pct(base['prometheus_results']['cagr']),              pct(new['prometheus_results']['cagr']),              round(pct(new['prometheus_results']['cagr'])              - pct(base['prometheus_results']['cagr']), 2)),
    ('Legacy Sharpe', r3(base['prometheus_results']['sharpe_ratio']),       r3(new['prometheus_results']['sharpe_ratio']),       round(r3(new['prometheus_results']['sharpe_ratio'])       - r3(base['prometheus_results']['sharpe_ratio']), 3)),
    ('Legacy MaxDD%', pct(base['prometheus_results']['max_drawdown']),      pct(new['prometheus_results']['max_drawdown']),      round(pct(new['prometheus_results']['max_drawdown'])      - pct(base['prometheus_results']['max_drawdown']), 2)),
    ('Legacy Win%',   pct(base['prometheus_results']['win_rate']),          pct(new['prometheus_results']['win_rate']),          round(pct(new['prometheus_results']['win_rate'])          - pct(base['prometheus_results']['win_rate']), 2)),
    ('Kelly CAGR%',   pct(base['kelly_results']['cagr']),                   pct(new['kelly_results']['cagr']),                   round(pct(new['kelly_results']['cagr'])                   - pct(base['kelly_results']['cagr']), 2)),
    ('Kelly Sharpe',  r3(base['kelly_results']['sharpe_ratio']),            r3(new['kelly_results']['sharpe_ratio']),            round(r3(new['kelly_results']['sharpe_ratio'])            - r3(base['kelly_results']['sharpe_ratio']), 3)),
    ('Kelly MaxDD%',  pct(base['kelly_results']['max_drawdown']),           pct(new['kelly_results']['max_drawdown']),           round(pct(new['kelly_results']['max_drawdown'])           - pct(base['kelly_results']['max_drawdown']), 2)),
    ('Blend CAGR%',   pct(base['blend_results']['cagr']),                   pct(new['blend_results']['cagr']),                   round(pct(new['blend_results']['cagr'])                   - pct(base['blend_results']['cagr']), 2)),
    ('Blend Sharpe',  r3(base['blend_results']['sharpe_ratio']),            r3(new['blend_results']['sharpe_ratio']),            round(r3(new['blend_results']['sharpe_ratio'])            - r3(base['blend_results']['sharpe_ratio']), 3)),
    ('Blend MaxDD%',  pct(base['blend_results']['max_drawdown']),           pct(new['blend_results']['max_drawdown']),           round(pct(new['blend_results']['max_drawdown'])           - pct(base['blend_results']['max_drawdown']), 2)),
]

print(f"{'Metric':<18} {'Baseline':>10} {'Tuned':>10} {'Delta':>10}")
print('-' * 52)
for m, b, n, d in rows:
    sig = ('+' if d > 0 else '') + str(d)
    print(f'{m:<18} {str(b):>10} {str(n):>10} {sig:>10}')
