"""
OVERLAY_SCALE tuning sweep.

Runs the 50-year benchmark 8 times with PROMETHEUS_OVERLAY_SCALE set to
0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00 and reports the
efficiency-frontier point (best Sharpe where Legacy CAGR >= 41%).

Usage:
    .venv_directml_test\Scripts\python.exe _tune_overlay.py
"""

import glob
import json
import os
import subprocess
import sys
import time

PYTHON = sys.executable
BENCHMARK = 'prometheus_50_year_competitor_benchmark.py'
BASELINE_FILE = 'benchmark_50_year_20260309_225939.json'
SCALES = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
CAGR_FLOOR = 0.41  # 41% as decimal (matches JSON format)


# ── helpers ──────────────────────────────────────────────────────────────

def latest_json(before_mtime: float) -> str | None:
    """Return the newest benchmark JSON created after before_mtime."""
    files = [
        f for f in glob.glob('benchmark_50_year_*.json')
        if os.path.getmtime(f) > before_mtime
    ]
    return max(files, key=os.path.getmtime) if files else None


def load_metrics(path: str) -> dict:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    p = data.get('prometheus_results', {})
    k = data.get('kelly_results', {})
    b = data.get('blend_results', {})

    return {
        'L_cagr':    p.get('cagr'),
        'L_sharpe':  p.get('sharpe_ratio'),
        'L_maxdd':   p.get('max_drawdown'),
        'L_winrate': p.get('win_rate'),
        'K_sharpe':  k.get('sharpe_ratio'),
        'B_sharpe':  b.get('sharpe_ratio'),
        'rank':      data.get('prometheus_rank'),
    }


def fmt(v, pct=False):
    if v is None:
        return '  N/A  '
    if pct:
        return f'{v:+7.2f}%'
    return f'{v:7.3f}'


# ── load baseline ────────────────────────────────────────────────────────

if not os.path.exists(BASELINE_FILE):
    print(f"WARNING: baseline file not found: {BASELINE_FILE}")
    baseline = None
else:
    baseline = load_metrics(BASELINE_FILE)
    print(f"Baseline loaded: {BASELINE_FILE}")
    print(f"  L_CAGR={baseline['L_cagr']*100:.2f}%  L_Sharpe={baseline['L_sharpe']:.3f}"
          f"  L_MaxDD={baseline['L_maxdd']*100:.2f}%")
    print()

# ── sweep ────────────────────────────────────────────────────────────────

results = []

for i, scale in enumerate(SCALES, 1):
    env = os.environ.copy()
    env['PROMETHEUS_OVERLAY_SCALE'] = str(scale)

    print(f"[{i}/{len(SCALES)}] OVERLAY_SCALE={scale:.2f}  (running benchmark…)")
    t_before = time.time()
    ts_before = t_before - 1  # 1-second buffer

    proc = subprocess.run(
        [PYTHON, BENCHMARK],
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )

    elapsed = time.time() - t_before

    if proc.returncode != 0:
        print(f"  ERROR (exit {proc.returncode})")
        print(proc.stderr[-2000:])
        results.append({'scale': scale, 'error': True})
        continue

    json_file = latest_json(ts_before)
    if not json_file:
        print('  ERROR: no new benchmark JSON found')
        results.append({'scale': scale, 'error': True})
        continue

    m = load_metrics(json_file)
    m['scale'] = scale
    m['file'] = json_file
    m['elapsed_s'] = elapsed
    results.append(m)

    print(f"  -> L_CAGR={m['L_cagr']*100:.2f}%  L_Sharpe={m['L_sharpe']:.3f}"
          f"  L_MaxDD={m['L_maxdd']*100:.2f}%  ({elapsed:.0f}s)")

# ── results table ─────────────────────────────────────────────────────────

print()
print('=' * 90)
print(f"{'Scale':>6}  {'L_CAGR':>8} {'L_Sharpe':>9} {'L_MaxDD':>9} "
      f"{'K_Sharpe':>9} {'B_Sharpe':>9} {'Rank':>5}  Flag")
print('-' * 90)

eligible = []

for r in results:
    if r.get('error'):
        print(f"  {r['scale']:.2f}   ERROR")
        continue

    ok = (r['L_cagr'] or 0) >= CAGR_FLOOR
    flag = '<<< OK' if ok else ''

    print(f"  {r['scale']:.2f}   {r['L_cagr']*100:7.2f}%  {r['L_sharpe']:8.3f}"
          f"  {r['L_maxdd']*100:8.2f}%  {(r['K_sharpe'] or 0):8.3f}"
          f"  {(r['B_sharpe'] or 0):8.3f}  {(r['rank'] or 0):4}   {flag}")

    if ok:
        eligible.append(r)

print('=' * 90)

# ── recommendation ───────────────────────────────────────────────────────

if eligible:
    best = max(eligible, key=lambda r: r['L_sharpe'])
    print()
    print(f"BEST (Sharpe-maximising with CAGR >= {CAGR_FLOOR}%):")
    print(f"  OVERLAY_SCALE = {best['scale']:.2f}")
    print(f"  L_CAGR={best['L_cagr']*100:.2f}%  L_Sharpe={best['L_sharpe']:.3f}"
          f"  L_MaxDD={best['L_maxdd']*100:.2f}%")

    if baseline:
        print()
        print(f"  vs baseline:")
        print(f"    CAGR  : {best['L_cagr']*100:.2f}% vs {baseline['L_cagr']*100:.2f}%  ({(best['L_cagr']-baseline['L_cagr'])*100:+.2f}pp)")
        print(f"    Sharpe: {best['L_sharpe']:.3f} vs {baseline['L_sharpe']:.3f}  ({best['L_sharpe']-baseline['L_sharpe']:+.3f})")
        print(f"    MaxDD : {best['L_maxdd']*100:.2f}% vs {baseline['L_maxdd']*100:.2f}%  ({(best['L_maxdd']-baseline['L_maxdd'])*100:+.2f}pp)")
    print()
    print(f"  File: {best['file']}")
else:
    print()
    print(f"No run met the CAGR >= {CAGR_FLOOR*100:.0f}% floor. Lowering scale further is not recommended.")

print()
print("Sweep complete.")
