import json
d = json.load(open('benchmark_50_year_20260305_184636.json'))
for k, v in d.items():
    if isinstance(v, dict) and 'cagr' in v:
        s = v.get('sharpe_ratio', v.get('sharpe', '?'))
        dd = v.get('max_drawdown', '?')
        print(f"  {k}: CAGR={v['cagr']:.2%}  Sharpe={s}  DD={dd}")
    elif isinstance(v, dict):
        for k2, v2 in v.items():
            if isinstance(v2, dict) and 'cagr' in v2:
                s = v2.get('sharpe_ratio', v2.get('sharpe', '?'))
                dd = v2.get('max_drawdown', '?')
                print(f"  {k}/{k2}: CAGR={v2['cagr']:.2%}  Sharpe={s}  DD={dd}")
