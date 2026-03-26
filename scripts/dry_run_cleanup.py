"""Dry run cleanup utility.
Scans repository and categorizes files into preserve / archive / remove based on cleanup_manifest.json.
No deletions performed; outputs report to cleanup_dry_run_report.json.
"""
import json
import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / 'scripts' / 'cleanup_manifest.json'
REPORT_PATH = ROOT / 'cleanup_dry_run_report.json'

with MANIFEST_PATH.open('r', encoding='utf-8') as f:
    manifest = json.load(f)

preserve_paths = manifest['preserve']['core_code'] + manifest['preserve']['configs'] + manifest['preserve']['infrastructure'] + manifest['preserve']['tests'] + manifest['preserve']['documentation']
archive_patterns = manifest['archive_patterns']
remove_patterns = manifest['remove_patterns']

preserve_abs = []
for item in preserve_paths:
    p = (ROOT / item).resolve()
    preserve_abs.append(p)

categories = {"preserve": [], "archive_candidate": [], "remove_candidate": []}

for path in ROOT.rglob('*'):
    if path.is_dir():
        continue
    rel = path.relative_to(ROOT).as_posix()

    # Check explicit preserve directories/files
    preserved = False
    for base in preserve_abs:
        try:
            path.relative_to(base)
            preserved = True
            break
        except ValueError:
            # not relative
            continue
    if any(str(path) == str(b) for b in preserve_abs):
        preserved = True
    if preserved:
        categories['preserve'].append(rel)
        continue

    # Pattern checks
    if any(fnmatch.fnmatch(rel, pat) for pat in archive_patterns):
        categories['archive_candidate'].append(rel)
        continue
    if any(fnmatch.fnmatch(rel, pat) for pat in remove_patterns):
        categories['remove_candidate'].append(rel)
        continue

    # Default to preserve (conservative)
    categories['preserve'].append(rel)

report = {"summary": {k: len(v) for k, v in categories.items()}, "files": categories}

with REPORT_PATH.open('w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print("Dry run cleanup report generated:", REPORT_PATH)
print(json.dumps(report['summary'], indent=2))
