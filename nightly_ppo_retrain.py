"""
PROMETHEUS Nightly PPO Retraining
===================================
Runs at 22:00 daily via Task Scheduler (added by setup_autostart.ps1).
Fine-tunes the SB3 PPO trading agent on the last 30 days of closed live trades,
so the RL voter continuously adapts to current market conditions.

Each nightly run:
  1. Loads trained_models/sb3_ppo_trading.zip
  2. Pulls last 30 days of closed trades from prometheus_learning.db
  3. Converts trades to gym observations + shaped reward signal
  4. Runs 5,000 fine-tuning timesteps (~2 min on CPU)
  5. Atomic-saves updated model back to sb3_ppo_trading.zip
  6. Sends WhatsApp summary if CALLMEBOT_API_KEY is set

Usage:
  python nightly_ppo_retrain.py [--days 30] [--steps 5000]
"""

import argparse
import sqlite3
import sys
import time
import shutil
import os
import math
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ppo_retrain")

DB           = Path("prometheus_learning.db")
MODEL_PATH   = Path("trained_models/sb3_ppo_trading.zip")
BACKUP_PATH  = Path("trained_models/sb3_ppo_trading_backup.zip")


# ── WhatsApp notification ─────────────────────────────────────────────────

def _whatsapp(msg: str):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        import urllib.request, urllib.parse
        phone  = os.getenv("CALLMEBOT_PHONE", "")
        apikey = os.getenv("CALLMEBOT_API_KEY", "")
        if not phone or not apikey:
            return
        url = (f"https://api.callmebot.com/whatsapp.php"
               f"?phone={urllib.parse.quote(phone)}"
               f"&text={urllib.parse.quote(msg[:1000])}"
               f"&apikey={apikey}")
        urllib.request.urlopen(url, timeout=10)
    except Exception:
        pass


# ── Load recent closed trades ─────────────────────────────────────────────

def load_recent_trades(days: int = 30):
    if not DB.exists():
        log.error(f"Database not found: {DB}")
        return []
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(str(DB))
    rows = conn.execute("""
        SELECT symbol, price, exit_price, profit_loss,
               confidence, hold_duration_seconds,
               timestamp
        FROM trade_history
        WHERE exit_price > 0
          AND profit_loss IS NOT NULL
          AND timestamp >= ?
        ORDER BY timestamp
    """, (cutoff,)).fetchall()
    conn.close()
    log.info(f"Loaded {len(rows)} closed trades from last {days} days")
    return rows


# ── Convert trades to SB3 replay buffer ──────────────────────────────────

def trades_to_experiences(trades):
    """
    Convert raw trade rows to (obs, action, reward, next_obs, done) tuples.
    Observation matches the 8-feature space used by train_sb3_ppo.py:
      [price_norm, change_pct/10, rsi_proxy/100, vol_ratio, macd_proxy, volatility,
       regime (0.5=neutral), vix_norm (0.5=neutral)]
    """
    import numpy as np

    experiences = []
    for sym, entry_px, exit_px, pnl, conf, hold_sec, ts in trades:
        if entry_px <= 0 or exit_px is None:
            continue

        change_pct = (exit_px - entry_px) / entry_px * 100
        hold_hours = (hold_sec or 3600) / 3600

        # Approximate observation features from what we have
        price_norm  = min(entry_px / 500.0, 5.0)
        change_norm = max(-5.0, min(5.0, change_pct / 10.0))
        rsi_proxy   = max(0.0, min(1.0, 0.5 + change_pct / 40.0))  # rough proxy
        vol_ratio   = max(0.1, min(5.0, 1.0))                       # no vol data, neutral
        macd_proxy  = max(-5.0, min(5.0, change_pct / 20.0))
        volatility  = max(0.001, abs(change_pct / 100.0))

        obs = np.array([price_norm, change_norm, rsi_proxy, vol_ratio,
                        macd_proxy, volatility,
                        0.5,   # regime: neutral (unknown at exit time)
                        0.5,   # vix_norm: neutral default
                        ], dtype=np.float32)

        # Action: 2=BUY (we only log buys), 0=SELL, 1=HOLD
        action = 2  # BUY was taken

        # Shaped reward: profit as % of position, capped
        reward = max(-2.0, min(2.0, pnl / max(entry_px * 0.05, 1.0)))
        # Bonus for quick profitable trades, penalty for long losers
        if pnl > 0 and hold_hours < 4:
            reward *= 1.2
        elif pnl < 0 and hold_hours > 8:
            reward *= 1.3  # larger penalty for holding losers

        next_obs = obs.copy()  # terminal state — same obs is fine
        done = True

        experiences.append((obs, action, reward, next_obs, done))

    return experiences


# ── Fine-tune the SB3 model ───────────────────────────────────────────────

def retrain(experiences, timesteps: int = 5000):
    try:
        from stable_baselines3 import PPO
        import numpy as np
    except ImportError:
        log.error("stable-baselines3 not installed — run: pip install stable-baselines3")
        sys.exit(1)

    if not MODEL_PATH.exists():
        log.error(f"Model not found: {MODEL_PATH}")
        sys.exit(1)

    # Backup current model before modifying
    shutil.copy2(MODEL_PATH, BACKUP_PATH)
    log.info(f"Backup saved to {BACKUP_PATH}")

    # Load existing model
    model = PPO.load(str(MODEL_PATH))
    log.info(f"Loaded model: {MODEL_PATH}  ({MODEL_PATH.stat().st_size // 1024}KB)")

    # Inject experiences into replay via learn() with a custom environment
    # The simplest approach: create a mini replay and call learn() on it.
    # SB3 PPO does on-policy updates — we build a small wrapper env that
    # replays our historical data as step() transitions.

    import gymnasium as gym
    from gymnasium import spaces

    class ReplayEnv(gym.Env):
        """Wraps historical trade experiences as a gym environment for fine-tuning."""
        def __init__(self, experiences):
            super().__init__()
            self.experiences = experiences
            self.idx = 0
            obs_dim = len(experiences[0][0]) if experiences else 8
            self.observation_space = spaces.Box(low=-5.0, high=5.0, shape=(obs_dim,), dtype=np.float32)
            self.action_space = spaces.Discrete(3)

        def reset(self, **kwargs):
            self.idx = 0
            obs, _, _, _, _ = self.experiences[self.idx % len(self.experiences)]
            return obs, {}

        def step(self, action):
            obs, true_action, reward, next_obs, done = self.experiences[self.idx % len(self.experiences)]
            self.idx += 1
            # Use true reward (from actual trade outcome), not the policy's chosen action
            terminated = done
            truncated  = False
            return next_obs, reward, terminated, truncated, {}

    env = ReplayEnv(experiences)

    # Re-set the model's environment and run learn()
    model.set_env(env)

    log.info(f"Fine-tuning on {len(experiences)} experiences x {timesteps} timesteps...")
    t0 = time.time()
    model.learn(total_timesteps=timesteps, reset_num_timesteps=False)
    elapsed = time.time() - t0
    log.info(f"Fine-tuning complete in {elapsed:.0f}s")

    # Atomic save: write to temp then replace
    tmp_path = MODEL_PATH.with_suffix(".tmp.zip")
    model.save(str(tmp_path.with_suffix("")))  # SB3 adds .zip automatically
    tmp_path_actual = tmp_path.parent / (tmp_path.stem + ".zip")
    if tmp_path_actual.exists():
        tmp_path_actual.replace(MODEL_PATH)
    else:
        model.save(str(MODEL_PATH.with_suffix("")))
    log.info(f"Model saved: {MODEL_PATH}  ({MODEL_PATH.stat().st_size // 1024}KB)")

    return elapsed


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Nightly PPO fine-tuning")
    parser.add_argument("--days",  type=int, default=30,   help="Days of trades to use")
    parser.add_argument("--steps", type=int, default=5000, help="Fine-tuning timesteps")
    args = parser.parse_args()

    print("=" * 60)
    print("  PROMETHEUS Nightly PPO Retraining")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    trades = load_recent_trades(days=args.days)
    if len(trades) < 5:
        msg = f"PPO retrain skipped: only {len(trades)} closed trades in last {args.days} days"
        log.warning(msg)
        _whatsapp(f"PROMETHEUS PPO retrain: {msg}")
        return

    experiences = trades_to_experiences(trades)
    if not experiences:
        log.warning("No valid experiences generated from trades")
        return

    log.info(f"Built {len(experiences)} training experiences from {len(trades)} trades")

    # Calculate win rate and avg reward for the notification
    total_reward = sum(e[2] for e in experiences)
    wins = sum(1 for e in experiences if e[2] > 0)
    win_rate = wins / len(experiences) * 100

    elapsed = retrain(experiences, timesteps=args.steps)

    summary = (
        f"PROMETHEUS PPO retrain complete\n"
        f"Trades used: {len(experiences)} ({args.days}d)\n"
        f"Win rate: {win_rate:.0f}%  Avg reward: {total_reward/len(experiences):+.3f}\n"
        f"Timesteps: {args.steps}  Time: {elapsed:.0f}s\n"
        f"Model updated: {MODEL_PATH.stat().st_size // 1024}KB"
    )
    print()
    print(summary)
    print("=" * 60)
    _whatsapp(summary)


if __name__ == "__main__":
    main()
