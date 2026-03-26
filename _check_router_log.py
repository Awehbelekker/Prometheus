#!/usr/bin/env python3
import glob
import os

patterns = [
    'ROUTER]',
    'ROUTER_SHADOW',
    'autonomous',
    'alpaca_24hr_hard_override',
    'ib_allocation_floor',
    'legacy_cash_compare',
    'Connected to Interactive Brokers',
]

logs = sorted(glob.glob('prometheus_live_trading_*.log'), key=os.path.getmtime, reverse=True)
if not logs:
    print('No prometheus_live_trading logs found')
    raise SystemExit(0)

latest = logs[0]
print(f'Latest log: {latest}')
print('=' * 80)

hits = []
with open(latest, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        if any(p.lower() in line.lower() for p in patterns):
            hits.append(line.rstrip('\n'))

if not hits:
    print('No matching routing lines yet.')
else:
    for line in hits[-120:]:
        print(line)
