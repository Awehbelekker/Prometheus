"""
hrm_market_pretrain.py — Market-native SSL pre-training for HRM.

Stage 1 of the two-stage fine-tuning approach:
  Stage 1 (this script): Self-supervised pre-training on raw OHLCV sequences.
                         No labels needed — learns to predict masked/next tokens.
  Stage 2 (hrm_finetune.py): Fine-tune the Stage-1 checkpoint on labeled trade outcomes.

Why this matters
----------------
The original HRM was trained on Sudoku/maze/ARC puzzles. Its representations
encode logical spatial reasoning, not financial sequential patterns. After Stage 1
pre-training on market data, the model's internal representations will reflect
OHLCV structure (momentum, volatility regimes, volume profiles) so that Stage 2
fine-tuning on trade outcomes can actually leverage them.

Self-supervised objective: Masked Token Prediction
---------------------------------------------------
Each OHLCV sequence has 15% of its tokens randomly masked (replaced with PAD_ID).
The model must predict the original token values at masked positions.
This is analogous to BERT's MLM — the model learns market sequence structure
without any labeled data.

Data source: yfinance hourly bars for the last 2 years on 20+ symbols.
One training example = one sliding window of 100 hourly bars.
With 2yr × 20 symbols × ~3400 trading hours = ~68,000 windows.

Usage (from project root):
    python official_hrm/hrm_market_pretrain.py

Output:
    hrm_checkpoints/market_pretrained/checkpoint.pt
    hrm_checkpoints/market_pretrained/pretrain_meta.json

After this completes, update hrm_finetune.py to use SOURCE_CHECKPOINT =
hrm_checkpoints/market_pretrained instead of sudoku_extreme.
"""

import sys
import logging
import json
import math
import time
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

_HERE = Path(__file__).parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE))

from official_hrm.hrm_finetune import (
    _build_model, SOURCE_CHECKPOINT, CHECKPOINT_DIR,
    SEQ_LEN, VOCAB_SIZE, PAD_ID,
)
from official_hrm.trading_dataset import (
    N_BARS, N_FEATURES, N_BINS, _quantise, _yf_ticker,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hrm_pretrain")

OUTPUT_DIR = CHECKPOINT_DIR / "market_pretrained"

# ── Hyper-parameters ──────────────────────────────────────────────────────────
EPOCHS = 10             # SSL pre-training — 10 passes over the data is enough
# batch_size=1 required: CastedSparseEmbedding.local_weights is sized to batch_size at init
# The model config sets batch_size=1, so the DataLoader must match.
BATCH_SIZE = 1
LR = 1e-4
LR_MIN = 1e-6
WARMUP_STEPS = 100
WEIGHT_DECAY = 0.01
GRAD_CLIP = 1.0
MASK_PROB = 0.15        # 15% of tokens masked (BERT-style)
EVAL_EVERY = 1          # Evaluate every epoch
# Auto-detect: DirectML (AMD GPU) > CUDA > CPU
try:
    import torch_directml as _dml
    DEVICE = str(_dml.device())
    _DML_DEVICE = _dml.device()
    import logging as _lg; _lg.getLogger("hrm_pretrain").info(f"Using DirectML GPU: {DEVICE}")
except ImportError:
    _DML_DEVICE = None
    if __import__("torch").cuda.is_available():
        DEVICE = "cuda"
    else:
        DEVICE = "cpu"

# Symbols for pre-training data
PRETRAIN_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "GOOGL", "META", "AMD", "SPY", "QQQ",
    "BTC-USD", "ETH-USD", "SOL-USD",
    "JPM", "GS", "XOM", "BA", "NFLX", "CRM",
    "DOGE-USD", "MATIC-USD", "LINK-USD",
]


# ── Dataset — sliding window over hourly bars ─────────────────────────────────

class MarketSSLDataset(Dataset):
    """
    Generates masked-token-prediction examples from raw OHLCV hourly bars.

    Each example:
      - input_ids: (SEQ_LEN-1,) — 100 context tokens with 15% randomly masked
      - target_ids: (SEQ_LEN-1,) — original tokens (-1 = not masked = ignore)

    We use SEQ_LEN-1 (100 tokens) to leave the label position for fine-tuning.
    """

    CONTEXT_LEN = N_BARS * N_FEATURES  # 100 tokens

    def __init__(self, symbols: list, years: float = 2.0, stride: int = 5,
                 mask_prob: float = MASK_PROB, seed: int = 42):
        self.mask_prob = mask_prob
        self.rng = np.random.default_rng(seed)
        self.windows = []  # list of np arrays, each shape (100,)

        import yfinance as yf
        # yfinance hourly data only available within last 730 days from yesterday
        end = datetime.now() - timedelta(days=1)
        start = end - timedelta(days=min(int(years * 365), 720))  # cap at 720 days

        log.info(f"Fetching {years}yr hourly data for {len(symbols)} symbols...")
        fetched = 0
        for sym in symbols:
            try:
                df = yf.download(
                    _yf_ticker(sym),
                    start=start.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                    interval="1h",
                    progress=False,
                    auto_adjust=True,
                )
                if df is None or len(df) < self.CONTEXT_LEN + 10:
                    continue

                # Flatten MultiIndex
                if hasattr(df.columns, "levels"):
                    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

                needed = ["Open", "High", "Low", "Close", "Volume"]
                if not all(c in df.columns for c in needed):
                    continue

                # Quantise each feature column
                tokens_per_feature = []
                for col in needed:
                    vals = df[col].values.astype(float)
                    tokens_per_feature.append(_quantise(vals))

                # Interleave: [O0,H0,L0,C0,V0, O1,H1,L1,C1,V1, ...]
                flat = np.stack(tokens_per_feature, axis=1).flatten().astype(np.int16)

                # Sliding windows
                n_windows = 0
                for i in range(0, len(flat) - self.CONTEXT_LEN + 1, stride * N_FEATURES):
                    window = flat[i: i + self.CONTEXT_LEN]
                    if len(window) == self.CONTEXT_LEN:
                        self.windows.append(window)
                        n_windows += 1

                fetched += 1
                log.info(f"  {sym}: {len(df)} bars -> {n_windows} windows")

            except Exception as e:
                log.warning(f"  {sym}: skipped ({e})")

        log.info(f"Total windows: {len(self.windows)} from {fetched}/{len(symbols)} symbols")

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, idx):
        tokens = self.windows[idx].copy()  # (100,)

        # Apply random masking
        mask = self.rng.random(len(tokens)) < self.mask_prob
        targets = np.full(len(tokens), -1, dtype=np.int16)  # -1 = ignore
        targets[mask] = tokens[mask]                          # supervise only masked
        tokens[mask] = PAD_ID                                  # replace with PAD

        return (
            torch.from_numpy(tokens.astype(np.int64)),   # (100,)
            torch.from_numpy(targets.astype(np.int64)),  # (100,)
        )


def collate_ssl(batch):
    inputs, targets = zip(*batch)
    return torch.stack(inputs), torch.stack(targets)


# ── Training loop ─────────────────────────────────────────────────────────────

def _ssl_loss(model, inputs, targets, device, puzzle_ids):
    """Masked token prediction loss — supervise only masked positions."""
    inputs = inputs.to(device)
    targets = targets.to(device)
    puzzle_ids = puzzle_ids.to(device)

    # Pad to full SEQ_LEN (add a dummy label position)
    B = inputs.shape[0]
    pad = torch.full((B, 1), PAD_ID, dtype=torch.long, device=device)
    full_inputs = torch.cat([inputs, pad], dim=1)  # (B, 101)

    batch = {
        "inputs": full_inputs,
        "targets": full_inputs.clone(),
        "puzzle_identifiers": puzzle_ids,
    }

    carry = model.initial_carry(batch)
    outputs = None
    for _ in range(model.config.halt_max_steps):
        carry, outputs = model(carry, batch)
        if carry.halted.all():
            break

    # logits: (B, 101, VOCAB_SIZE) — supervise context positions only (0:100)
    logits = outputs["logits"][:, :100, :]  # (B, 100, VOCAB_SIZE)
    logits_flat = logits.reshape(-1, VOCAB_SIZE)  # (B*100, VOCAB_SIZE)
    targets_flat = targets.reshape(-1)             # (B*100,)

    # Only compute loss on masked positions (targets != -1)
    valid = targets_flat != -1
    if not valid.any():
        return torch.tensor(0.0, device=device, requires_grad=True)

    loss = nn.functional.cross_entropy(
        logits_flat[valid],
        targets_flat[valid],
        label_smoothing=0.05,
    )
    return loss


@torch.no_grad()
def _eval_ssl(model, loader, device, n_batches=50):
    """Evaluate masked token prediction accuracy on a sample of batches."""
    model.eval()
    total, correct = 0, 0

    for i, (inputs, targets) in enumerate(loader):
        if i >= n_batches:
            break
        B = inputs.shape[0]
        puzzle_ids = torch.zeros(B, dtype=torch.long)
        inputs = inputs.to(device)
        targets = targets.to(device)
        puzzle_ids = puzzle_ids.to(device)

        pad = torch.full((B, 1), PAD_ID, dtype=torch.long, device=device)
        full_inputs = torch.cat([inputs, pad], dim=1)
        batch = {"inputs": full_inputs, "targets": full_inputs.clone(), "puzzle_identifiers": puzzle_ids}

        carry = model.initial_carry(batch)
        for _ in range(model.config.halt_max_steps):
            carry, outputs = model(carry, batch)
            if carry.halted.all():
                break

        logits = outputs["logits"][:, :100, :]
        preds = logits.argmax(dim=-1).reshape(-1)
        tgt = targets.reshape(-1)
        valid = tgt != -1
        if valid.any():
            correct += (preds[valid] == tgt[valid]).sum().item()
            total += valid.sum().item()

    return correct / max(total, 1)


def train():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Build dataset ─────────────────────────────────────────────────────────
    dataset = MarketSSLDataset(PRETRAIN_SYMBOLS, years=2.0, stride=5)
    if len(dataset) < 100:
        log.error(f"Too few windows ({len(dataset)}) — check yfinance connectivity")
        return

    n_test = min(500, len(dataset) // 10)
    n_train = len(dataset) - n_test
    train_ds, test_ds = torch.utils.data.random_split(
        dataset, [n_train, n_test],
        generator=torch.Generator().manual_seed(42)
    )
    log.info(f"Train windows: {n_train}  Test windows: {n_test}")

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              collate_fn=collate_ssl, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False,
                             collate_fn=collate_ssl)

    # ── Load model ────────────────────────────────────────────────────────────
    log.info(f"Loading source checkpoint: {SOURCE_CHECKPOINT}")
    model = _build_model(SOURCE_CHECKPOINT.parent, DEVICE)
    # Reduce ACT steps for SSL pre-training: 2 steps use ~half GPU memory vs 4.
    # SSL pre-training only needs coarse sequence representations; 2 steps is sufficient.
    model.config.halt_max_steps = 2
    total_params = sum(p.numel() for p in model.parameters())
    log.info(f"Model: {total_params:,} params on {DEVICE} (halt_max_steps=2 for memory)")

    # ── Optimiser ─────────────────────────────────────────────────────────────
    try:
        from adam_atan2 import AdamATan2
        optimiser = AdamATan2(model.parameters(), lr=LR,
                              betas=(0.9, 0.95), weight_decay=WEIGHT_DECAY)
    except ImportError:
        # foreach=False avoids aten::lerp.Scalar_out which is unsupported on DirectML
        # and causes per-step CPU fallback overhead. Element-wise ops work natively.
        optimiser = torch.optim.AdamW(model.parameters(), lr=LR,
                                      betas=(0.9, 0.95), weight_decay=WEIGHT_DECAY,
                                      foreach=False)

    total_steps = EPOCHS * len(train_loader)
    global_step = 0

    # Baseline
    baseline_acc = _eval_ssl(model, test_loader, DEVICE)
    log.info(f"[Baseline] masked token acc={baseline_acc:.1%}")

    best_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        for batch_idx, (inputs, targets) in enumerate(train_loader):
            # LR schedule
            lr_now = LR_MIN + 0.5 * (LR - LR_MIN) * (
                1 + math.cos(math.pi * max(global_step - WARMUP_STEPS, 0) /
                             max(total_steps - WARMUP_STEPS, 1))
            )
            if global_step < WARMUP_STEPS:
                lr_now = LR * global_step / max(WARMUP_STEPS, 1)
            for pg in optimiser.param_groups:
                pg["lr"] = lr_now

            B = inputs.shape[0]
            puzzle_ids = torch.zeros(B, dtype=torch.long)

            optimiser.zero_grad()
            try:
                loss = _ssl_loss(model, inputs, targets, DEVICE, puzzle_ids)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
                optimiser.step()
            except Exception as e:
                log.error(f"  Step {batch_idx+1} failed: {e}")
                continue

            epoch_loss += loss.item()
            global_step += 1

            if (batch_idx + 1) % 50 == 0:
                avg = epoch_loss / (batch_idx + 1)
                elapsed = time.time() - t0
                log.info(
                    f"  Epoch {epoch} step {batch_idx+1}/{len(train_loader)}  "
                    f"loss={avg:.4f}  lr={lr_now:.2e}  {elapsed:.0f}s"
                )

            # Save progress checkpoint every 500 steps so crashes don't lose all work
            if global_step % 500 == 0:
                mid_ckpt = OUTPUT_DIR / "checkpoint_mid.pt"
                torch.save(model.state_dict(), mid_ckpt)
                log.info(f"  Mid-epoch checkpoint saved at step {global_step}")

        avg_loss = epoch_loss / max(len(train_loader), 1)
        acc = _eval_ssl(model, test_loader, DEVICE)
        elapsed = time.time() - t0
        log.info(
            f"Epoch {epoch}/{EPOCHS}  train_loss={avg_loss:.4f}  "
            f"masked_token_acc={acc:.1%}  {elapsed:.0f}s"
        )

        if acc > best_acc:
            best_acc = acc
            ckpt = OUTPUT_DIR / "checkpoint.pt"
            torch.save(model.state_dict(), ckpt)
            # Also save as no-extension for hrm_checkpoint_manager
            import shutil
            shutil.copy(ckpt, OUTPUT_DIR / "checkpoint")
            log.info(f"  Saved best checkpoint (masked_acc={best_acc:.1%}) -> {ckpt}")

    # Save metadata
    meta = {
        "vocab_size": VOCAB_SIZE,
        "seq_len": SEQ_LEN,
        "pretrain_objective": "masked_token_prediction",
        "mask_prob": MASK_PROB,
        "epochs": EPOCHS,
        "train_windows": n_train,
        "best_masked_acc": float(best_acc),
        "source_checkpoint": "sudoku_extreme",
        "symbols": PRETRAIN_SYMBOLS,
    }
    with open(OUTPUT_DIR / "pretrain_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log.info(f"\nPre-training complete. Best masked token acc: {best_acc:.1%}")
    log.info(f"Checkpoint: {OUTPUT_DIR / 'checkpoint.pt'}")
    log.info("Next step:")
    log.info("  Update official_hrm/hrm_finetune.py SOURCE_CHECKPOINT to point at")
    log.info(f"  {OUTPUT_DIR}")
    log.info("  Then run: python official_hrm/hrm_finetune.py")


if __name__ == "__main__":
    train()
