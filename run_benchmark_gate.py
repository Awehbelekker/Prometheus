#!/usr/bin/env python3
"""
Benchmark gate for final comprehensive benchmark reliability.

Checks:
- Runs the final benchmark multiple times.
- Every run must exit with code 0.
- Every run must report required GPU backend (default: directml).
- No new final benchmark error artifact logs are created.

Exit code:
- 0: pass
- 1: fail
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run benchmark reliability gate")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs")
    parser.add_argument(
        "--python-exe",
        default=r".venv_directml_test\Scripts\python.exe",
        help="Python executable to run benchmark script",
    )
    parser.add_argument(
        "--script",
        default="run_final_comprehensive_benchmarks.py",
        help="Benchmark script to execute",
    )
    parser.add_argument(
        "--require-gpu-backend",
        default="directml",
        help="Required GPU backend string from benchmark output (case-insensitive)",
    )
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Directory for run output and artifact checks",
    )
    return parser.parse_args()


def resolve_python_exe(python_exe: str) -> str:
    candidate = Path(python_exe)
    if candidate.exists():
        return str(candidate)
    return sys.executable


def extract_gpu_line(text: str) -> Tuple[str, str]:
    for line in text.splitlines():
        if "Backend:" in line:
            backend = line.split("Backend:", 1)[1].strip().lower()
            return backend, line.strip()
        if "Status: CPU fallback" in line:
            return "cpu", line.strip()
    return "unknown", "GPU line not found"


def main() -> int:
    args = parse_args()

    logs_dir = Path(args.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    python_exe = resolve_python_exe(args.python_exe)
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"FAIL: benchmark script not found: {script_path}")
        return 1

    before_artifacts = {p.name for p in logs_dir.glob("final_comprehensive_benchmark_error_*.log")}

    print("=== BENCHMARK GATE START ===")
    print(f"Python: {python_exe}")
    print(f"Script: {script_path}")
    print(f"Runs: {args.runs}")
    print(f"Required GPU backend: {args.require_gpu_backend}")
    print()

    matrix: List[Tuple[int, int, str]] = []
    failed = False

    for idx in range(1, args.runs + 1):
        out_file = logs_dir / f"final_benchmark_gate_run_{idx}.out"
        proc = subprocess.run(
            [python_exe, str(script_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        combined_output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        out_file.write_text(combined_output, encoding="utf-8")

        backend, gpu_line = extract_gpu_line(combined_output)
        matrix.append((idx, proc.returncode, gpu_line))

        print(f"RUN {idx}: exit={proc.returncode} gpu='{gpu_line}'")

        if proc.returncode != 0:
            failed = True
        if backend != args.require_gpu_backend.lower():
            failed = True

    after_artifacts = {p.name for p in logs_dir.glob("final_comprehensive_benchmark_error_*.log")}
    new_artifacts = sorted(after_artifacts - before_artifacts)
    if new_artifacts:
        failed = True

    print()
    print("=== RUN MATRIX ===")
    for idx, code, gpu_line in matrix:
        print(f"{idx:>2} | exit={code:<2} | {gpu_line}")

    print()
    print("=== NEW ERROR ARTIFACTS ===")
    if new_artifacts:
        for name in new_artifacts:
            print(name)
    else:
        print("None")

    if failed:
        print()
        print("BENCHMARK GATE: FAIL")
        return 1

    print()
    print("BENCHMARK GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
