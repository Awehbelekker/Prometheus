#!/usr/bin/env python3
"""
hrm_finetune_watcher.py

Monitors hrm_finetune_run.log and automatically promotes the fine-tuned
HRM checkpoint once test accuracy >= THRESHOLD.

Promotion actions:
  1. Adds 'market_finetuned' to the checkpoint list in
     core/hrm_official_integration.py _load_checkpoints()
  2. Raises HRM ensemble weight in the launcher from 0.3 to 0.7
  3. Writes a PROMOTION_COMPLETE marker file

Usage:
    python hrm_finetune_watcher.py
"""

import re
import sys
import time
import os

LOG_FILE        = "hrm_finetune_run.log"
INTEGRATION_FILE = "core/hrm_official_integration.py"
LAUNCHER_FILE   = "launch_ultimate_prometheus_LIVE_TRADING.py"
MARKER_FILE     = "hrm_checkpoints/market_finetuned/PROMOTION_COMPLETE.txt"
THRESHOLD       = 0.55   # 55% directional accuracy
POLL_INTERVAL   = 30     # seconds

# Patterns to match in the log
EPOCH_PATTERN = re.compile(
    r"Epoch\s+(\d+)/\d+.*test_acc=([\d.]+)%"
)
COMPLETE_PATTERN = re.compile(r"Fine-tuning complete")


def parse_best_acc(log_path: str) -> tuple[int, float]:
    """Return (epoch, best_acc) from the log so far."""
    best_acc = 0.0
    best_epoch = 0
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = EPOCH_PATTERN.search(line)
                if m:
                    epoch = int(m.group(1))
                    acc = float(m.group(2)) / 100.0
                    if acc > best_acc:
                        best_acc = acc
                        best_epoch = epoch
    except FileNotFoundError:
        pass
    return best_epoch, best_acc


def is_complete(log_path: str) -> bool:
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            return any(COMPLETE_PATTERN.search(line) for line in f)
    except FileNotFoundError:
        return False


def promote_checkpoint(best_acc: float, best_epoch: int):
    """Patch integration file and launcher to activate the fine-tuned checkpoint."""
    print(f"\n{'='*60}")
    print(f"THRESHOLD MET: {best_acc:.1%} >= {THRESHOLD:.0%} at epoch {best_epoch}")
    print(f"{'='*60}")
    errors = []

    # ── 1. Add market_finetuned to _load_checkpoints() ────────────────────────
    try:
        with open(INTEGRATION_FILE, encoding="utf-8") as f:
            src = f.read()

        old = "checkpoints = ['arc_agi_2', 'sudoku_extreme', 'maze_30x30']"
        new = "checkpoints = ['arc_agi_2', 'sudoku_extreme', 'maze_30x30', 'market_finetuned']"

        if old in src:
            src = src.replace(old, new)
            with open(INTEGRATION_FILE, "w", encoding="utf-8") as f:
                f.write(src)
            print(f"[OK] Added 'market_finetuned' to {INTEGRATION_FILE}")
        elif "market_finetuned" in src:
            print(f"[OK] 'market_finetuned' already present in {INTEGRATION_FILE}")
        else:
            errors.append(f"Could not find checkpoint list in {INTEGRATION_FILE} — patch manually")
    except Exception as e:
        errors.append(f"Failed to patch {INTEGRATION_FILE}: {e}")

    # ── 2. Raise HRM ensemble weight 0.3 → 0.7 in launcher ───────────────────
    try:
        with open(LAUNCHER_FILE, encoding="utf-8") as f:
            src = f.read()

        old_weight = (
            "                            # Weight is 0.3 (honest placeholder) until market-sequence\n"
            "                            # fine-tuning in Phase B replaces puzzle-game weights\n"
            "                            learned_weight = self._get_ai_weight('HRM')\n"
            "                            hrm_weight = 0.3 * learned_weight"
        )
        new_weight = (
            "                            # Weight raised to 0.7 after market_finetuned checkpoint\n"
            f"                            # validated at {best_acc:.1%} directional accuracy (epoch {best_epoch})\n"
            "                            learned_weight = self._get_ai_weight('HRM')\n"
            "                            hrm_weight = 0.7 * learned_weight"
        )

        if "hrm_weight = 0.3 * learned_weight" in src:
            src = src.replace(old_weight, new_weight)
            if "hrm_weight = 0.7 * learned_weight" in src:
                with open(LAUNCHER_FILE, "w", encoding="utf-8") as f:
                    f.write(src)
                print(f"[OK] Raised HRM weight 0.3 → 0.7 in {LAUNCHER_FILE}")
            else:
                errors.append("Weight replacement produced unexpected result — patch manually")
        elif "hrm_weight = 0.7 * learned_weight" in src:
            print(f"[OK] HRM weight already at 0.7 in {LAUNCHER_FILE}")
        else:
            errors.append(f"Could not find HRM weight line in {LAUNCHER_FILE} — patch manually")
    except Exception as e:
        errors.append(f"Failed to patch {LAUNCHER_FILE}: {e}")

    # ── 3. Write marker ───────────────────────────────────────────────────────
    try:
        os.makedirs(os.path.dirname(MARKER_FILE), exist_ok=True)
        with open(MARKER_FILE, "w") as f:
            f.write(
                f"Promoted at epoch {best_epoch}\n"
                f"Test accuracy: {best_acc:.1%}\n"
                f"Threshold: {THRESHOLD:.0%}\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
        print(f"[OK] Marker written: {MARKER_FILE}")
    except Exception as e:
        errors.append(f"Failed to write marker: {e}")

    if errors:
        print("\nManual steps needed:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\nPromotion complete. Restart the trading server to activate.")


def main():
    print(f"Watching {LOG_FILE} for test_acc >= {THRESHOLD:.0%} ...")
    print(f"Polling every {POLL_INTERVAL}s  |  Ctrl+C to stop\n")

    already_promoted = os.path.exists(MARKER_FILE)
    if already_promoted:
        print(f"Promotion already done ({MARKER_FILE} exists). Exiting.")
        return

    last_reported_epoch = 0

    while True:
        epoch, best_acc = parse_best_acc(LOG_FILE)

        if epoch > last_reported_epoch:
            last_reported_epoch = epoch
            print(f"  Epoch {epoch:4d} | best test acc so far: {best_acc:.1%}", flush=True)

        if best_acc >= THRESHOLD:
            promote_checkpoint(best_acc, epoch)
            return

        if is_complete(LOG_FILE):
            print(f"\nFine-tune finished. Best accuracy: {best_acc:.1%}")
            if best_acc >= THRESHOLD:
                promote_checkpoint(best_acc, epoch)
            else:
                print(
                    f"Did not reach {THRESHOLD:.0%} threshold.\n"
                    "Options:\n"
                    "  - Collect more trade data and re-run trading_dataset.py\n"
                    "  - Increase EPOCHS in hrm_finetune.py\n"
                    "  - Keep HRM weight at 0.3 and monitor paper trade performance"
                )
            return

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
