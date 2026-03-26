"""
One-shot patch: add OVERLAY_SCALE env-var knob to
prometheus_50_year_competitor_benchmark.py so the tuning sweep can
scale all Phase-3/4 overlay multipliers proportionally without
editing the file for each run.
"""

SRC = 'prometheus_50_year_competitor_benchmark.py'
content = open(SRC, encoding='utf-8').read()

applied = []

# ── 1. Add `import os` and OVERLAY_SCALE constant ───────────────────────
OLD = "import sys\nsys.stdout.reconfigure(encoding='utf-8')\n\nimport asyncio\nimport logging"
NEW = (
    "import os\n"
    "import sys\n"
    "sys.stdout.reconfigure(encoding='utf-8')\n"
    "\n"
    "import asyncio\n"
    "import logging\n"
    "\n"
    "# ── Overlay tuning knob (set via PROMETHEUS_OVERLAY_SCALE env var) ────\n"
    "# Scales all Phase-3/4 overlay multipliers proportionally.\n"
    "# 1.0 = original values, 0.5 = half-strength, 0.0 = overlays disabled.\n"
    "OVERLAY_SCALE: float = float(os.environ.get('PROMETHEUS_OVERLAY_SCALE', '1.0'))"
)
if OLD in content:
    content = content.replace(OLD, NEW, 1)
    applied.append('import os + OVERLAY_SCALE constant')
else:
    print("WARNING: could not find import block — already patched or file changed")

# ── Helper: replace exactly one occurrence ──────────────────────────────
def patch(old, new, label):
    global content
    count = content.count(old)
    if count == 1:
        content = content.replace(old, new, 1)
        applied.append(label)
    elif count == 0:
        print(f"WARNING: '{label}' — string not found (already patched?)")
    else:
        print(f"WARNING: '{label}' — {count} occurrences found, skipping (ambiguous)")

# ── 2. Cross-asset boost (Legacy & Kelly share identical text) ───────────
patch(
    'raw_target = min(raw_target * (1 + cross_score * 0.15), 1.0)  # boost up to ~15%',
    'raw_target = min(raw_target * (1 + cross_score * (OVERLAY_SCALE * 0.15)), 1.0)  # boost up to ~15%',
    'cross-asset boost 0.15'
)
patch(
    'raw_target *= max(0.65, 1 + cross_score * 0.30)  # cut up to ~30%',
    'raw_target *= max(0.65, 1 + cross_score * (OVERLAY_SCALE * 0.30))  # cut up to ~30%',
    'cross-asset cut 0.30'
)

# ── 3. Sector rotation boost / cut ──────────────────────────────────────
patch(
    'raw_target = min(raw_target * (1 + rot_score * 0.08), 1.0)  # up to +8%',
    'raw_target = min(raw_target * (1 + rot_score * (OVERLAY_SCALE * 0.08)), 1.0)  # up to +8%',
    'sector rotation boost 0.08'
)
patch(
    'raw_target *= max(0.90, 1 + rot_score * 0.06)  # cut up to -6%',
    'raw_target *= max(0.90, 1 + rot_score * (OVERLAY_SCALE * 0.06))  # cut up to -6%',
    'sector rotation cut 0.06'
)

# ── 4. Volatility harvesting add ─────────────────────────────────────────
patch(
    'raw_target = min(raw_target + vh_score * 0.12, 0.55)  # cap at 55% in fear',
    'raw_target = min(raw_target + vh_score * (OVERLAY_SCALE * 0.12), 0.55)  # cap at 55% in fear',
    'vol harvest 0.12'
)

# ── 5. Multi-asset concentration boost ──────────────────────────────────
patch(
    'rot_alpha *= (1 + conc * 0.8)',
    'rot_alpha *= (1 + conc * (OVERLAY_SCALE * 0.8))',
    'multi-asset conc 0.8'
)

# ── 6. Momentum carry (Legacy backtest only — two separate lines) ────────
patch(
    'mom_carry = 0.00015  # 1.5 bps/day in strong trends (~3.8% annualized)',
    'mom_carry = OVERLAY_SCALE * 0.00015  # 1.5 bps/day in strong trends (~3.8% annualized)',
    'mom carry bull 0.00015'
)
patch(
    'mom_carry = 0.00006  # 0.6 bps/day in trending sideways',
    'mom_carry = OVERLAY_SCALE * 0.00006  # 0.6 bps/day in trending sideways',
    'mom carry sideways 0.00006'
)

open(SRC, 'w', encoding='utf-8').write(content)

print(f"\nPatch complete. Applied {len(applied)}/{9} changes:")
for i, name in enumerate(applied, 1):
    print(f"  {i}. {name}")

import subprocess, sys
result = subprocess.run(
    [sys.executable, '-c', f'import ast; ast.parse(open("{SRC}", encoding="utf-8").read()); print("Syntax OK")'],
    capture_output=True, text=True
)
print(result.stdout.strip() or result.stderr.strip())
