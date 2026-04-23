"""
hrm_pretrain_watcher.py — Watches for SSL pre-training checkpoint, then auto-runs
the full post-pretrain pipeline:

  1. Waits for hrm_checkpoints/market_pretrained/checkpoint.pt to appear
  2. Updates SOURCE_CHECKPOINT in hrm_finetune.py to use market_pretrained
  3. Runs hrm_feature_extract.py  (extracts HRM hidden states for all 302 examples)
  4. Runs hrm_head_train.py        (trains Linear head ~30s, saves merged checkpoint)
  5. If best test accuracy >= 55%: uncomments market_finetuned in hrm_official_integration.py

Run once and leave it running alongside the pre-training:
    python official_hrm/hrm_pretrain_watcher.py

Logs to: hrm_watcher.log
"""

import sys
import time
import logging
import subprocess
import re
from pathlib import Path

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(_ROOT / "hrm_watcher.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("hrm_watcher")

PRETRAIN_CKPT = _ROOT / "hrm_checkpoints" / "market_pretrained" / "checkpoint.pt"
FINETUNE_PY   = _HERE / "hrm_finetune.py"
EXTRACT_PY    = _HERE / "hrm_feature_extract.py"
HEAD_PY       = _HERE / "hrm_head_train.py"
INTEGRATION   = _ROOT / "core" / "hrm_official_integration.py"
HEAD_RESULT   = _ROOT / "hrm_checkpoints" / "market_finetuned" / "finetune_meta.json"

# The DirectML venv python to use for extraction + head training
import shutil
_DML_PYTHON = str(_ROOT / ".venv_directml_test" / "Scripts" / "python.exe")
if not Path(_DML_PYTHON).exists():
    _DML_PYTHON = sys.executable   # fallback to current python


def _run(script: Path, label: str) -> int:
    """Run a script and stream output to log. Returns exit code."""
    log.info(f"Running {label}...")
    proc = subprocess.Popen(
        [_DML_PYTHON, "-u", str(script)],
        cwd=str(_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            log.info(f"  [{label}] {line}")
    proc.wait()
    log.info(f"{label} finished with exit code {proc.returncode}")
    return proc.returncode


def _patch_source_checkpoint():
    """Update SOURCE_CHECKPOINT in hrm_finetune.py to use market_pretrained."""
    text = FINETUNE_PY.read_text(encoding="utf-8")
    old = 'SOURCE_CHECKPOINT = CHECKPOINT_DIR / "sudoku_extreme" / "checkpoint"'
    new = 'SOURCE_CHECKPOINT = CHECKPOINT_DIR / "market_pretrained" / "checkpoint"'
    if old not in text:
        if "market_pretrained" in text:
            log.info("SOURCE_CHECKPOINT already points at market_pretrained — no patch needed")
            return
        log.warning("Could not find SOURCE_CHECKPOINT line to patch — check hrm_finetune.py")
        return
    FINETUNE_PY.write_text(text.replace(old, new), encoding="utf-8")
    log.info("Patched SOURCE_CHECKPOINT -> market_pretrained in hrm_finetune.py")


def _read_best_acc() -> float:
    """Read best test accuracy from head_train_results.json."""
    import json
    if not HEAD_RESULT.exists():
        return 0.0
    try:
        data = json.loads(HEAD_RESULT.read_text(encoding="utf-8"))
        return float(data.get("best_test_acc", 0.0))
    except Exception:
        return 0.0


def _activate_market_finetuned():
    """Uncomment the market_finetuned block in hrm_official_integration.py."""
    text = INTEGRATION.read_text(encoding="utf-8")

    # The commented-out block to uncomment:
    old = (
        "        # if 'market_finetuned' in self.models:\n"
        "        #     return 'market_finetuned'"
    )
    new = (
        "        if 'market_finetuned' in self.models:\n"
        "            return 'market_finetuned'  # SSL-pretrained + head-trained, acc>55%"
    )

    if "return 'market_finetuned'  # SSL-pretrained" in text:
        log.info("market_finetuned already activated in hrm_official_integration.py")
        return
    if old not in text:
        log.warning("Could not find the commented block in hrm_official_integration.py — manual activation needed")
        log.warning("  Uncomment lines ~555-556 to enable market_finetuned checkpoint")
        return

    INTEGRATION.write_text(text.replace(old, new), encoding="utf-8")
    log.info("ACTIVATED market_finetuned in hrm_official_integration.py")
    log.info("HRM will now use the SSL-pretrained + fine-tuned checkpoint for all signals")


def _get_ckpt_mtime() -> float:
    """Return checkpoint.pt modification time, or 0 if not exists."""
    try:
        return PRETRAIN_CKPT.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _run_pipeline() -> float:
    """Run extract + head train. Returns best_acc."""
    _patch_source_checkpoint()

    rc = _run(EXTRACT_PY, "feature_extract")
    if rc != 0:
        log.error(f"Feature extraction failed (exit {rc})")
        return 0.0

    rc = _run(HEAD_PY, "head_train")
    if rc != 0:
        log.error(f"Head training failed (exit {rc})")
        return 0.0

    return _read_best_acc()


def main():
    log.info("HRM pre-train watcher started")
    log.info(f"Watching for: {PRETRAIN_CKPT}")
    log.info("Will re-run pipeline after each new epoch checkpoint until accuracy >= 55%")

    poll_interval = 60  # seconds
    last_mtime = _get_ckpt_mtime()  # track when checkpoint was last updated

    # Wait for first checkpoint
    while not PRETRAIN_CKPT.exists():
        log.info(f"  Checkpoint not yet available — checking again in {poll_interval}s")
        time.sleep(poll_interval)

    # Loop: re-run pipeline whenever a newer checkpoint appears
    while True:
        current_mtime = _get_ckpt_mtime()
        if current_mtime > last_mtime:
            last_mtime = current_mtime
            log.info(f"New checkpoint detected (mtime updated) — running pipeline...")

            best_acc = _run_pipeline()
            log.info(f"Pipeline complete. Best OOD test accuracy: {best_acc:.1%}")

            if best_acc >= 0.55:
                log.info("Threshold met (>= 55%) — activating market_finetuned in live trading")
                _activate_market_finetuned()
                log.info("DONE — HRM is now using market-native SSL-pretrained representations")
                return  # exit watcher — job done
            else:
                log.info(f"Accuracy {best_acc:.1%} < 55% — waiting for next epoch checkpoint...")
        else:
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
