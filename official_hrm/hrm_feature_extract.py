"""
hrm_feature_extract.py — Extract HRM hidden representations for all training examples.

Runs all 295 training examples through the frozen HRM backbone ONCE,
saves the hidden states to disk, then trains only the output head on the
cached features. This makes each training epoch ~1000x faster.

Pipeline:
  1. Run this script (takes ~15 min on CPU for 295 examples)
  2. Run hrm_finetune.py --mode=head_only (uses cached features)
     Each epoch then takes ~0.1s instead of 15 min.

Output:
  hrm_trading_dataset/train/hrm_features.npy  shape (N_train, hidden_size)
  hrm_trading_dataset/train/hrm_targets.npy   shape (N_train,)  int labels 0/1/2
  hrm_trading_dataset/test/hrm_features.npy
  hrm_trading_dataset/test/hrm_targets.npy
"""

import sys
import logging
import time
from pathlib import Path

import numpy as np
import torch

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE))

from official_hrm.hrm_finetune import (
    _build_model, SOURCE_CHECKPOINT, DATASET_DIR, DEVICE,
    MarketTokenDataset, collate_fn, SEQ_LEN,
)
from torch.utils.data import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hrm_extract")


def extract_features(split: str, model, device: str) -> tuple:
    """
    Run all examples in split through the frozen HRM backbone.
    Returns (features, targets) numpy arrays.

    features: (N, hidden_size) — hidden state at the final position
    targets:  (N,) int — ground truth label 0/1/2
    """
    split_dir = DATASET_DIR / split
    ds = MarketTokenDataset(split_dir)
    loader = DataLoader(ds, batch_size=1, shuffle=False, collate_fn=collate_fn)

    log.info(f"Extracting {split} features ({len(ds)} examples)...")
    all_features = []
    all_targets = []

    from official_hrm.trading_dataset import PAD_ID, SEQ_LEN

    t0 = time.time()
    with torch.no_grad():
        for i, (inputs, labels, pids) in enumerate(loader):
            # CRITICAL: replace the label token at position -1 with PAD so the
            # model cannot see the answer. We want it to encode only the 100
            # market context tokens (positions 0-99).
            inputs_masked = inputs.clone()
            inputs_masked[:, -1] = PAD_ID   # mask the label position
            inputs_masked = inputs_masked.to(device)
            pids = pids.to(device)

            batch = {
                "inputs": inputs_masked,
                "targets": inputs_masked.clone(),
                "puzzle_identifiers": pids,
            }

            # Run backbone — collect hidden state at the last CONTEXT position
            # (position SEQ_LEN-2 = index 99), which summarises the market bars
            carry = model.initial_carry(batch)
            for _ in range(model.config.halt_max_steps):
                carry, outputs = model(carry, batch)
                if carry.halted.all():
                    break

            # z_H: (B, SEQ_LEN + puzzle_emb_len, hidden_size)
            # puzzle_emb_len tokens prepended — final context position is at
            # index (puzzle_emb_len + SEQ_LEN - 2) = last bar token, before the masked label.
            z_H = carry.inner_carry.z_H   # (1, total_seq, hidden_size)
            # Take the mean over the context window (exclude label position and puzzle prefix)
            puzzle_emb_len = z_H.shape[1] - SEQ_LEN
            context_repr = z_H[0, puzzle_emb_len:-1, :].mean(dim=0)  # mean-pool context
            all_features.append(context_repr.cpu().numpy())

            # Target: label at final position in the *labels* tensor (0/1/2)
            target = labels[0, -1].item()
            all_targets.append(target)

            if (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                eta = elapsed / (i + 1) * (len(ds) - i - 1)
                log.info(f"  {i+1}/{len(ds)} done, {elapsed:.0f}s elapsed, ETA {eta:.0f}s")

    features = np.stack(all_features).astype(np.float32)  # (N, hidden_size)
    targets = np.array(all_targets, dtype=np.int32)         # (N,)

    elapsed = time.time() - t0
    log.info(f"  Done! {len(ds)} examples in {elapsed:.0f}s ({elapsed/len(ds):.1f}s each)")
    log.info(f"  features: {features.shape}  targets: {targets.shape}")
    log.info(f"  label dist: SELL={int((targets==0).sum())} HOLD={int((targets==1).sum())} BUY={int((targets==2).sum())}")

    return features, targets


def main():
    log.info(f"Device: {DEVICE}")
    log.info(f"Loading HRM backbone from {SOURCE_CHECKPOINT}...")

    model = _build_model(SOURCE_CHECKPOINT.parent, DEVICE)
    model.eval()

    # Freeze everything — we only want representations, no training
    for p in model.parameters():
        p.requires_grad = False

    total_params = sum(p.numel() for p in model.parameters())
    log.info(f"Model loaded: {total_params:,} params (frozen)")

    for split in ["train", "test"]:
        features, targets = extract_features(split, model, DEVICE)

        out_dir = DATASET_DIR / split
        np.save(out_dir / "hrm_features.npy", features)
        np.save(out_dir / "hrm_targets.npy", targets)
        log.info(f"Saved {split} features/targets to {out_dir}")

    log.info("Feature extraction complete.")
    log.info("Next step: python hrm_head_train.py")


if __name__ == "__main__":
    main()
