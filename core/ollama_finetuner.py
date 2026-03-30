"""
PROMETHEUS Ollama Context-Enriched Model Builder
=================================================
Periodically checks prometheus_learning.db for new successful live trade
outcomes and rebuilds the local Ollama trading model with those patterns
injected as few-shot examples in the system prompt.

This uses Ollama's FROM + SYSTEM + PARAMETER Modelfile format — not LoRA
weight training (Ollama doesn't support that natively). The result is a
context-enriched model that "remembers" what PROMETHEUS has learned from
real trades.

Trigger:  >= MIN_EXAMPLES new winning trades since last run
Schedule: called by AdaptiveLearningEngine._loop_model_retrain() every 1 hr
Output:   Modelfile.prometheus  +  ollama model 'prometheus-trader'
"""

import json
import logging
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

LEARNING_DB = Path("prometheus_learning.db")
BASE_MODEL = "llama3.1:8b-trading"          # Base model to extend
FALLBACK_BASE_MODEL = "llama3.1:8b"         # If trading variant not available
OUTPUT_MODEL = "prometheus-trader"           # Created/updated model name
MODELFILE_PATH = Path("Modelfile.prometheus")
LAST_FINETUNE_FILE = Path("last_ollama_finetune.json")
MIN_EXAMPLES = 50                            # Minimum new winning trades to trigger


def _read_last_state() -> dict:
    if LAST_FINETUNE_FILE.exists():
        try:
            return json.loads(LAST_FINETUNE_FILE.read_text())
        except Exception:
            pass
    return {"last_id": 0, "ran_at": None, "examples_used": 0}


def _fetch_winning_trades(since_id: int) -> list:
    """Fetch successful live trade outcomes from the learning DB."""
    if not LEARNING_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=10)
        rows = conn.execute("""
            SELECT id, symbol, side, entry_price, exit_price, pnl_pct,
                   ai_signals, captured_at
            FROM live_trade_outcomes
            WHERE pnl > 0 AND id > ?
            ORDER BY id DESC
            LIMIT 200
        """, (since_id,)).fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.warning(f"[OllamaFinetuner] DB read error: {e}")
        return []


def _base_model_available(name: str) -> bool:
    """Check if a given Ollama model is present locally."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        return name in result.stdout
    except Exception:
        return False


def _choose_base_model() -> str:
    if _base_model_available(BASE_MODEL):
        return BASE_MODEL
    if _base_model_available(FALLBACK_BASE_MODEL):
        logger.info(f"[OllamaFinetuner] {BASE_MODEL} not found, using {FALLBACK_BASE_MODEL}")
        return FALLBACK_BASE_MODEL
    # Return preferred name anyway — ollama create will fail with a clear error
    return BASE_MODEL


def _build_modelfile(examples: list, base_model: str) -> str:
    """Construct an Ollama Modelfile with trade examples as system context."""
    example_lines = []
    for row in examples[:40]:          # Cap at 40 to keep prompt size manageable
        _id, sym, side, entry, exit_, pnl_pct, ai_sig, ts = row
        pnl_str = f"{float(pnl_pct or 0)*100:.1f}%" if pnl_pct is not None else "n/a"
        sig_brief = str(ai_sig)[:80].replace('"', "'") if ai_sig else "mixed"
        example_lines.append(
            f"  - {sym} {str(side).upper()} @ {entry:.2f} -> {exit_:.2f}"
            f" | PnL {pnl_str} | signals: {sig_brief}"
        )
    examples_text = "\n".join(example_lines)

    system_prompt = (
        f"You are PROMETHEUS, an expert autonomous stock and crypto trader. "
        f"You have learned from {len(examples)} profitable live trades.\n\n"
        f"Recent winning trade patterns:\n{examples_text}\n\n"
        f"When asked to analyse a trade opportunity, respond with:\n"
        f"  ACTION: BUY | SELL | HOLD\n"
        f"  CONFIDENCE: 0.0–1.0\n"
        f"  REASONING: one concise sentence\n"
        f"Always prioritise capital preservation. Never chase momentum blindly."
    )

    return (
        f"FROM {base_model}\n"
        f"SYSTEM \"\"\"\n{system_prompt}\n\"\"\"\n"
        f"PARAMETER temperature 0.2\n"
        f"PARAMETER top_p 0.9\n"
        f"PARAMETER num_predict 256\n"
    )


def maybe_finetune() -> bool:
    """
    Run Ollama model rebuild if enough new winning trades have accumulated.
    Returns True if a new model was built, False otherwise.
    """
    state = _read_last_state()
    last_id = state.get("last_id", 0)

    examples = _fetch_winning_trades(since_id=last_id)
    if len(examples) < MIN_EXAMPLES:
        logger.info(
            f"[OllamaFinetuner] {len(examples)} new winning trades "
            f"(need {MIN_EXAMPLES}) — skipping rebuild"
        )
        return False

    base_model = _choose_base_model()
    modelfile_content = _build_modelfile(examples, base_model)
    MODELFILE_PATH.write_text(modelfile_content, encoding="utf-8")
    logger.info(
        f"[OllamaFinetuner] Modelfile written ({len(examples)} examples, "
        f"base={base_model})"
    )

    try:
        result = subprocess.run(
            ["ollama", "create", OUTPUT_MODEL, "-f", str(MODELFILE_PATH)],
            capture_output=True, text=True, timeout=300
        )
    except FileNotFoundError:
        logger.error("[OllamaFinetuner] 'ollama' command not found — is Ollama installed?")
        return False
    except subprocess.TimeoutExpired:
        logger.error("[OllamaFinetuner] ollama create timed out after 5 minutes")
        return False

    if result.returncode == 0:
        max_id = max(row[0] for row in examples)
        new_state = {
            "last_id": max_id,
            "ran_at": datetime.now().isoformat(),
            "examples_used": len(examples),
            "model": OUTPUT_MODEL,
            "base_model": base_model,
        }
        LAST_FINETUNE_FILE.write_text(json.dumps(new_state, indent=2))
        logger.info(
            f"[OllamaFinetuner] Model '{OUTPUT_MODEL}' rebuilt successfully "
            f"({len(examples)} examples, last_id={max_id})"
        )
        return True
    else:
        logger.error(
            f"[OllamaFinetuner] ollama create failed (rc={result.returncode}): "
            f"{result.stderr[:400]}"
        )
        return False
