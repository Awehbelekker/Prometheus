"""
PROMETHEUS SB3 PPO Training — Multi-Asset, 20-Year, 8-Feature
==============================================================
Trains an RL agent on 20 years of daily equities data across
SPY, QQQ, and IWM so it learns universal price-action patterns
from diverse market regimes (2008 crash, 2020 COVID, 2022 rate
hike cycle, high-inflation periods).

Observation (8 features — matches live voter in launch_ultimate):
  [price_norm, change/10, rsi/100, vol_ratio, macd_norm, volatility,
   regime, vix_norm]

  regime:   0=bear, 0.5=neutral, 1.0=bull  (50d return + MA cross)
  vix_norm: VIX / 40  (capped at 1.0; VIX 20 = 0.5 = neutral)

Actions: 0=SELL, 1=HOLD, 2=BUY
Output:  trained_models/sb3_ppo_trading.zip
         trained_models/best_model.zip  (best eval checkpoint)

Walk-forward validation:
  Train:    2004-01-01 to 2021-12-31  (includes 3 major crises)
  Validate: 2022-01-01 to 2023-12-31  (rate hike cycle — hardest regime)
  Test:     2024-01-01 to present     (never seen — final score)

Usage:
  python train_sb3_ppo.py [--timesteps 300000] [--fast]
"""

import argparse
import logging
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ppo_train")

OUTPUT_PATH = Path("trained_models/sb3_ppo_trading.zip")
BEST_PATH   = Path("trained_models/best_model.zip")

# Walk-forward date splits
TRAIN_START    = "2004-01-01"
TRAIN_END      = "2021-12-31"
VALIDATE_START = "2022-01-01"
VALIDATE_END   = "2023-12-31"
TEST_START     = "2024-01-01"
TEST_END       = datetime.now().strftime("%Y-%m-%d")

# Assets to train on (equities only — crypto gets a separate model later)
TRAIN_ASSETS = ["SPY", "QQQ", "IWM"]

DEFAULT_TIMESTEPS = 300_000


# ── Technical indicator helpers ──────────────────────────────────────────────

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _regime(close: pd.Series) -> pd.Series:
    """
    Deterministic regime proxy — no HMM needed for training data.
    0.0 = bear, 0.5 = neutral, 1.0 = bull
    Live inference uses the actual HMM detector output.
    """
    ma50  = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    ret50 = close.pct_change(50) * 100  # 50-day return

    regime = pd.Series(0.5, index=close.index)  # default neutral
    bull   = (close > ma200) & (ret50 > 2.0)
    bear   = (close < ma200) & (ret50 < -5.0)
    regime[bull] = 1.0
    regime[bear] = 0.0
    return regime.fillna(0.5)


# ── Data download and feature engineering ────────────────────────────────────

def download_asset(ticker: str, start: str, end: str, retries: int = 4) -> pd.DataFrame:
    log.info(f"  Downloading {ticker} {start} to {end}...")
    df = pd.DataFrame()
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(ticker, start=start, end=end, interval="1d",
                             auto_adjust=True, progress=False)
            if not df.empty:
                break
        except Exception as e:
            log.warning(f"    Attempt {attempt}/{retries} failed for {ticker}: {e}")
        if attempt < retries:
            time.sleep(5 * attempt)
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")

    df = df.dropna()
    close = df["Close"].squeeze()
    vol   = df["Volume"].squeeze()

    df["change_pct"]   = close.pct_change() * 100
    df["rsi"]          = _rsi(close)
    df["volume_ratio"] = (vol / vol.rolling(20).mean()).clip(0.1, 10.0)
    df["macd"]         = (close.ewm(span=12).mean() - close.ewm(span=26).mean())
    df["volatility"]   = close.pct_change().rolling(20).std().fillna(0.01).clip(0.001, 0.2)
    df["regime"]       = _regime(close)
    df["ticker"]       = ticker
    df = df.dropna().reset_index(drop=True)
    log.info(f"    {len(df):,} bars  ({df.shape[0]/252:.1f} years)")
    return df


def download_vix(start: str, end: str) -> pd.Series:
    """Download VIX as a date-indexed Series. Returns empty Series on failure."""
    log.info("  Downloading VIX...")
    try:
        vix = pd.DataFrame()
        for attempt in range(1, 4):
            try:
                vix = yf.download("^VIX", start=start, end=end, interval="1d",
                                  auto_adjust=True, progress=False)
                if not vix.empty:
                    break
            except Exception:
                pass
            if attempt < 3:
                time.sleep(5 * attempt)
        if vix is None or vix.empty:
            return pd.Series(dtype=float)
        # Handle multi-level columns from newer yfinance
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)
        close = vix["Close"].squeeze()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close.index = pd.to_datetime(close.index).normalize()
        return close.rename("vix")
    except Exception as e:
        log.warning(f"  VIX download failed ({e}) — using default vix_norm=0.5")
        return pd.Series(dtype=float)


def build_dataset(start: str, end: str, assets=None) -> dict[str, pd.DataFrame]:
    """Download + feature-engineer all assets and merge with VIX."""
    if assets is None:
        assets = TRAIN_ASSETS

    vix_series = download_vix(start, end)

    data = {}
    for ticker in assets:
        try:
            df = download_asset(ticker, start, end)
            # Re-attach the original DatetimeIndex for the VIX merge, then reset
            raw = yf.download(ticker, start=start, end=end, interval="1d",
                              auto_adjust=True, progress=False)
            if raw is not None and not raw.empty:
                dates = pd.to_datetime(raw.index).normalize()
                if len(dates) == len(df):
                    df.index = dates

            # Merge VIX by date alignment
            if not vix_series.empty and isinstance(df.index, pd.DatetimeIndex):
                vix_aligned = vix_series.reindex(df.index, method="ffill").fillna(20.0)
                df["vix_norm"] = (vix_aligned / 40.0).clip(0.0, 1.0).values
            else:
                df["vix_norm"] = 0.5

            df = df.reset_index(drop=True)
            data[ticker] = df
        except Exception as e:
            log.warning(f"  Skipping {ticker}: {e}")
    return data


# ── Gymnasium environment ────────────────────────────────────────────────────

class PrometheusGymEnv(gym.Env):
    """
    8-feature trading environment aligned with the live voting loop.

    Observation:
      [price_norm, change/10, rsi/100, vol_ratio, macd_norm, volatility,
       regime, vix_norm]

    All features are clipped to [-5, 5] and normalised to be unit-free.
    Reward = risk-adjusted portfolio return with overtrading penalty.
    """
    metadata = {"render_modes": []}
    OBS_DIM  = 8

    def __init__(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        super().__init__()
        self.df              = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.observation_space = spaces.Box(
            low=-5.0, high=5.0, shape=(self.OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)  # 0=SELL 1=HOLD 2=BUY
        self._max_steps   = len(df) - 1
        self._returns     = []   # track for Sharpe calc in reset
        self.reset()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _scalar(self, row, col, default=0.0) -> float:
        v = row[col] if col in self.df.columns else default
        if hasattr(v, "iloc"):
            v = v.iloc[0]
        return float(v) if not (isinstance(v, float) and math.isnan(v)) else default

    def _get_obs(self) -> np.ndarray:
        row        = self.df.iloc[self._step]
        price      = self._scalar(row, "Close", 1.0)
        price_norm = np.clip((price / self._ref_price) - 1.0, -5.0, 5.0)
        change     = np.clip(self._scalar(row, "change_pct") / 10.0, -5.0, 5.0)
        rsi        = self._scalar(row, "rsi", 50.0) / 100.0
        vol        = np.clip(self._scalar(row, "volume_ratio", 1.0), 0.0, 5.0)
        macd_raw   = self._scalar(row, "macd", 0.0)
        macd_norm  = np.clip(macd_raw / max(price * 0.01, 1e-6), -5.0, 5.0)
        vola       = np.clip(self._scalar(row, "volatility", 0.01), 0.0, 1.0)
        regime     = np.clip(self._scalar(row, "regime", 0.5), 0.0, 1.0)
        vix_norm   = np.clip(self._scalar(row, "vix_norm", 0.5), 0.0, 1.0)

        return np.array(
            [price_norm, change, rsi, vol, macd_norm, vola, regime, vix_norm],
            dtype=np.float32,
        )

    # ── gym API ──────────────────────────────────────────────────────────────

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._step     = 0
        self._balance  = self.initial_balance
        self._shares   = 0.0
        v = self.df.iloc[0]["Close"]
        self._ref_price  = float(v.iloc[0]) if hasattr(v, "iloc") else float(v)
        self._prev_value = self.initial_balance
        self._returns    = []
        self._trade_count = 0
        return self._get_obs(), {}

    def step(self, action):
        row   = self.df.iloc[self._step]
        price = self._scalar(row, "Close", 1.0)
        cost  = price * 0.001   # 0.1% round-trip transaction cost

        if action == 2 and self._balance > price:   # BUY
            shares = (self._balance * 0.25) / (price + cost)
            self._shares   += shares
            self._balance  -= shares * (price + cost)
            self._trade_count += 1
        elif action == 0 and self._shares > 0:       # SELL
            self._balance += self._shares * (price - cost)
            self._shares   = 0.0
            self._trade_count += 1

        self._step += 1
        done = self._step >= self._max_steps

        nxt_row   = self.df.iloc[min(self._step, self._max_steps)]
        nxt_price = self._scalar(nxt_row, "Close", 1.0)
        portfolio = self._balance + self._shares * nxt_price

        # Risk-adjusted reward: step return minus overtrading penalty
        step_return = (portfolio - self._prev_value) / self.initial_balance * 100
        trade_penalty = 0.02 if action != 1 else 0.0   # stronger than before
        reward = step_return - trade_penalty
        self._returns.append(step_return)
        self._prev_value = portfolio

        return self._get_obs(), reward, done, False, {}


# ── Walk-forward evaluation ──────────────────────────────────────────────────

def evaluate_model(model: PPO, df: pd.DataFrame, label: str) -> dict:
    """Run model on a held-out dataframe, return performance metrics."""
    env   = PrometheusGymEnv(df)
    obs, _= env.reset()
    total_reward = 0.0
    returns      = []
    actions_taken = {0: 0, 1: 0, 2: 0}

    for _ in range(len(df) - 1):
        action, _ = model.predict(obs.reshape(1, -1), deterministic=True)
        obs, reward, done, _, _ = env.step(int(action))
        total_reward += reward
        returns.append(reward)
        actions_taken[int(action)] += 1
        if done:
            break

    # Buy-and-hold baseline
    first = float(df["Close"].iloc[0].iloc[0]) if hasattr(df["Close"].iloc[0], "iloc") else float(df["Close"].iloc[0])
    last  = float(df["Close"].iloc[-1].iloc[0]) if hasattr(df["Close"].iloc[-1], "iloc") else float(df["Close"].iloc[-1])
    bah_return = (last - first) / first * 100

    # Sharpe (annualised, assuming daily steps)
    if len(returns) > 1:
        mean_r = np.mean(returns)
        std_r  = np.std(returns, ddof=1)
        sharpe = (mean_r / std_r * np.sqrt(252)) if std_r > 0 else 0.0
    else:
        sharpe = 0.0

    # Max drawdown
    cumulative = np.cumsum(returns)
    peak       = np.maximum.accumulate(cumulative)
    drawdowns  = peak - cumulative
    max_dd     = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

    wins  = sum(1 for r in returns if r > 0)
    wr    = wins / len(returns) * 100 if returns else 0

    log.info(f"\n  [{label}]")
    log.info(f"  Total reward:  {total_reward:+.2f}  |  Buy&Hold: {bah_return:+.1f}%")
    log.info(f"  Sharpe:        {sharpe:.2f}")
    log.info(f"  Max drawdown:  {max_dd:.2f}")
    log.info(f"  Win rate:      {wr:.1f}%  ({wins}/{len(returns)} steps)")
    log.info(f"  Actions:       SELL={actions_taken[0]}  HOLD={actions_taken[1]}  BUY={actions_taken[2]}")

    return {
        "label": label, "total_reward": total_reward, "bah_return": bah_return,
        "sharpe": sharpe, "max_dd": max_dd, "win_rate": wr, "actions": actions_taken,
    }


def print_validation_verdict(results: list[dict]):
    print()
    print("=" * 65)
    print("  WALK-FORWARD VALIDATION RESULTS")
    print("=" * 65)
    print(f"  {'Period':<24}  {'Reward':>8}  {'BnH':>7}  {'Sharpe':>7}  {'MaxDD':>7}  {'WR':>5}")
    print(f"  {'-'*24}  {'-'*8}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*5}")
    for r in results:
        print(f"  {r['label']:<24}  {r['total_reward']:>+8.1f}  "
              f"{r['bah_return']:>+6.1f}%  {r['sharpe']:>7.2f}  "
              f"{r['max_dd']:>7.2f}  {r['win_rate']:>4.1f}%")
    print()

    # Overfitting check
    if len(results) >= 2:
        train_sharpe    = results[0]["sharpe"]
        validate_sharpe = results[1]["sharpe"]
        ratio = validate_sharpe / train_sharpe if train_sharpe > 0 else 0

        print("  OVERFITTING CHECK:")
        print(f"  Train Sharpe:    {train_sharpe:.2f}")
        print(f"  Validate Sharpe: {validate_sharpe:.2f}  (ratio: {ratio:.2f})")
        if ratio >= 0.6:
            print("  STATUS: PASS — validation Sharpe >= 60% of training (good generalisation)")
        elif ratio >= 0.3:
            print("  STATUS: WARN — moderate degradation; monitor live performance")
        else:
            print("  STATUS: FAIL — severe overfit; do not deploy without re-tuning")

    if len(results) >= 3:
        test_sharpe = results[2]["sharpe"]
        print(f"\n  Test Sharpe (2024-present, never seen): {test_sharpe:.2f}")
        if test_sharpe > 0.5:
            print("  DEPLOY DECISION: SAFE — positive Sharpe on unseen data")
        elif test_sharpe > 0.0:
            print("  DEPLOY DECISION: CAUTION — marginal; monitor closely")
        else:
            print("  DEPLOY DECISION: HOLD — negative Sharpe on unseen test set")

    print("=" * 65)


# ── Main training loop ───────────────────────────────────────────────────────

def train(timesteps: int = DEFAULT_TIMESTEPS, fast: bool = False):
    print("=" * 65)
    print("  PROMETHEUS SB3 PPO Training — Multi-Asset 20-Year")
    print(f"  Assets: {', '.join(TRAIN_ASSETS)}")
    print(f"  Train:    {TRAIN_START} to {TRAIN_END}")
    print(f"  Validate: {VALIDATE_START} to {VALIDATE_END}")
    print(f"  Test:     {TEST_START} to {TEST_END}")
    print(f"  Timesteps: {timesteps:,}")
    print("=" * 65)

    # ── Download data for all three windows ──────────────────────────────────
    log.info("\nDownloading TRAIN data (20 years)...")
    train_data = build_dataset(TRAIN_START, TRAIN_END)

    log.info("\nDownloading VALIDATE data (2022-2023 rate hike cycle)...")
    val_data   = build_dataset(VALIDATE_START, VALIDATE_END)

    log.info("\nDownloading TEST data (2024-present, never seen)...")
    test_data  = build_dataset(TEST_START, TEST_END)

    if not train_data:
        log.error("No training data downloaded. Check internet connection.")
        return None

    log.info(f"\nAssets loaded: {list(train_data.keys())}")

    # Fall back to train data slice if validate/test download failed
    if not val_data:
        log.warning("Validate download failed — using last 20% of SPY train as fallback")
        spy_train_full = train_data["SPY"] if "SPY" in train_data else next(iter(train_data.values()))
        split = int(len(spy_train_full) * 0.8)
        val_data = {"SPY": spy_train_full.iloc[split:].reset_index(drop=True)}

    if not test_data:
        log.warning("Test download failed — skipping final test evaluation")

    # ── Build training environments (one per asset, run in parallel) ──────────
    def make_train_env(df):
        return lambda: PrometheusGymEnv(df)

    train_envs = DummyVecEnv([make_train_env(df) for df in train_data.values()])

    # Eval on SPY validate set (primary benchmark)
    spy_val = val_data["SPY"] if "SPY" in val_data else next(iter(val_data.values()))
    eval_env = DummyVecEnv([lambda: PrometheusGymEnv(spy_val)])

    # ── PPO hyperparameters ───────────────────────────────────────────────────
    # Larger n_steps for longer episodes (daily candles, 4000+ steps per asset)
    # Higher ent_coef encourages exploration to avoid HOLD-always strategy
    n_steps = 1024 if fast else 2048
    model = PPO(
        "MlpPolicy", train_envs,
        learning_rate=2e-4,
        n_steps=n_steps,
        batch_size=256,
        n_epochs=10,
        gamma=0.995,        # high gamma values future rewards
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,      # entropy bonus prevents HOLD-always collapse
        vf_coef=0.5,
        max_grad_norm=0.5,
        policy_kwargs=dict(net_arch=[128, 128]),   # wider net for 8 features
        verbose=1,
        device="auto",      # CUDA on new server, CPU here
    )

    stop_cb = StopTrainingOnRewardThreshold(reward_threshold=100, verbose=1)
    eval_cb = EvalCallback(
        eval_env,
        callback_on_new_best=stop_cb,
        eval_freq=max(5_000, timesteps // 60),
        best_model_save_path=str(OUTPUT_PATH.parent),
        verbose=0,
    )

    log.info(f"\nTraining PPO for {timesteps:,} timesteps across {len(train_data)} assets...")
    log.info("(This takes ~5-15 min on CPU, ~2 min on CUDA)")
    model.learn(total_timesteps=timesteps, callback=eval_cb, progress_bar=True)

    # Save final model
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(OUTPUT_PATH.with_suffix("")))
    log.info(f"\nSaved: {OUTPUT_PATH}  ({OUTPUT_PATH.stat().st_size // 1024}KB)")

    # ── Walk-forward validation ───────────────────────────────────────────────
    log.info("\nRunning walk-forward validation...")
    results = []

    # Evaluate on each training asset (in-sample — just for reference)
    spy_train = train_data["SPY"] if "SPY" in train_data else next(iter(train_data.values()))
    results.append(evaluate_model(model, spy_train, f"TRAIN    SPY {TRAIN_START[:4]}-{TRAIN_END[:4]}"))

    for ticker, df in val_data.items():
        results.append(evaluate_model(model, df, f"VALIDATE {ticker} 2022-2023"))

    for ticker, df in test_data.items():
        results.append(evaluate_model(model, df, f"TEST     {ticker} 2024-now "))

    # Summary table — match on key substrings regardless of spacing
    print_validation_verdict([
        r for r in results
        if ("TRAIN" in r["label"] and "SPY" in r["label"])
        or ("VALIDATE" in r["label"] and "SPY" in r["label"])
        or ("TEST" in r["label"] and "SPY" in r["label"])
    ])

    return model


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=DEFAULT_TIMESTEPS,
                        help=f"Training timesteps (default {DEFAULT_TIMESTEPS:,})")
    parser.add_argument("--fast", action="store_true",
                        help="Faster settings for quick smoke-test (50K steps)")
    args = parser.parse_args()

    ts = 50_000 if args.fast else args.timesteps
    model = train(timesteps=ts, fast=args.fast)

    if model:
        print()
        print("Training complete.")
        print(f"Model saved: {OUTPUT_PATH}")
        print()
        print("NEXT STEPS:")
        print("  1. Review the validation verdict above")
        print("  2. If PASS/CAUTION: restart PROMETHEUS — the voter auto-loads the new model")
        print("  3. Nightly retraining (22:00) will continue fine-tuning on live trades")
        print()
        print("NOTE: The new model uses 8 features (was 6).")
        print("      The live voter is already updated to pass 8 features.")
