import json
d = json.load(open("MASTER_BENCHMARK_RESULTS_20260307_071905.json"))
print(f"TOTAL: {d['passed']}/{d['total_scripts']} PASSED, {d['failed']} FAILED")
print(f"Pass Rate: {d['pass_rate']}%")
print(f"Runtime: {d['total_runtime_seconds']/60:.1f} min")
print()
for tier in ["TIER-1", "TIER-2", "TIER-3", "TIER-4"]:
    tier_r = [r for r in d["results"] if r["tier"] == tier]
    if tier_r:
        print(f"  {tier}:")
        for r in tier_r:
            icon = {"PASS": "OK", "FAIL": "XX", "TIMEOUT": "TO"}.get(r["status"], "??")
            print(f"    [{icon}] {r['name']:<35s} {r['status']:<10s} {r['duration']:>8.1f}s")
        print()
