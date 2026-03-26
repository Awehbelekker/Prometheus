"""Analyze the Paper vs Shadow execution gap"""
import re

with open('prometheus_server.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total log lines: {len(lines)}")

# Confidence distribution
confs = []
for l in lines:
    m = re.search(r'@ (\d+\.\d+)% confidence', l)
    if m:
        confs.append(float(m.group(1)))

print(f"\n=== CONFIDENCE DISTRIBUTION ({len(confs)} signals) ===")
if confs:
    print(f"Min: {min(confs):.1f}%  Max: {max(confs):.1f}%  Avg: {sum(confs)/len(confs):.1f}%")
    for t in [50, 55, 60, 65, 70, 75, 80, 85]:
        c = sum(1 for x in confs if x >= t)
        print(f"  >= {t}%: {c}/{len(confs)} ({c*100/len(confs):.0f}%)")

# Count blocking reasons
print("\n=== BLOCKING REASONS ===")
patterns = {
    'Below confidence': 'signals below',
    'AI Timing Delay': 'Delay recommended',
    'Shadow Gate Block': 'SHADOW GATE',
    'Dead-End Block': 'DEAD.END',
    'Regime Exposure': 'regime.*exposure.*block',
    'Sentiment Filter': 'sentiment.*block',
    'No broker available': 'No broker available',
    'Trade EXECUTED': 'Trade EXECUTED',
    'Order placed': 'Order placed',
    'SELL executed': 'SOLD',
}
for name, pat in patterns.items():
    matches = [l for l in lines if re.search(pat, l, re.IGNORECASE)]
    print(f"  {name}: {len(matches)}")
    if matches and len(matches) <= 5:
        for m in matches:
            print(f"    -> {m.strip()[:150]}")

# Check if any signals above 70% exist and what blocked them
print("\n=== SIGNALS ABOVE 70% (last 20) ===")
above_70 = [(i, l.strip()) for i, l in enumerate(lines) if '@ ' in l and 'confidence' in l.lower()]
above_70_filtered = []
for idx, line in above_70:
    m = re.search(r'@ (\d+\.\d+)%', line)
    if m and float(m.group(1)) >= 70:
        above_70_filtered.append((idx, line, float(m.group(1))))

print(f"Total signals >= 70%: {len(above_70_filtered)}")
for idx, line, conf in above_70_filtered[-20:]:
    print(f"  [{idx}] {line[:120]}")
    # Check next 5 lines for blocking reason
    for j in range(idx+1, min(idx+6, len(lines))):
        l = lines[j].strip()
        if any(kw in l.lower() for kw in ['delay', 'shadow gate', 'dead', 'skip', 'block', 'timing', 'executing', 'executed']):
            print(f"    -> {l[:120]}")
            break

