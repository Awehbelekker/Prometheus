"""
Bootstrap SB3 PPO trading agent on SPY 5-year daily data.
Observation: [price_norm, change_pct, rsi_norm, vol_ratio, macd_norm, volatility]
Actions: 0=SELL, 1=HOLD, 2=BUY
Output: trained_models/sb3_ppo_trading.zip
"""
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
import yfinance as yf
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)

OUTPUT_PATH = Path('trained_models/sb3_ppo_trading.zip')
TIMESTEPS   = 200_000   # ~5-10 min on CPU, faster on CUDA


class PrometheusGymEnv(gym.Env):
    """
    6-feature trading env matching the signal loop observation:
    [price_norm, change_pct/10, rsi/100, vol_ratio, macd_norm, volatility]
    Actions: 0=SELL, 1=HOLD, 2=BUY
    """
    metadata = {'render_modes': []}

    def __init__(self, df: pd.DataFrame, initial_balance: float = 10_000.0):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.observation_space = spaces.Box(low=-5.0, high=5.0, shape=(6,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)  # 0=SELL, 1=HOLD, 2=BUY
        self._max_steps = len(df) - 1
        self.reset()

    def _val(self, row, col, default=0.0):
        v = row[col] if col in self.df.columns else default
        return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)

    def _get_obs(self):
        row = self.df.iloc[self._step]
        price = self._val(row, 'Close', 1.0)
        price_norm = price / self._ref_price - 1.0
        change = self._val(row, 'change_pct', 0.0)
        rsi = self._val(row, 'rsi', 50.0) / 100.0
        vol = self._val(row, 'volume_ratio', 1.0)
        macd = self._val(row, 'macd', 0.0) / max(price * 0.01, 1e-6)
        vola = self._val(row, 'volatility', 0.01)
        return np.array([price_norm, change / 10.0, rsi, vol, macd, vola], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._step = 0
        self._balance = self.initial_balance
        self._shares = 0.0
        v = self.df.iloc[0]['Close']
        self._ref_price = float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        self._prev_value = self.initial_balance
        return self._get_obs(), {}

    def step(self, action):
        row = self.df.iloc[self._step]
        price = self._val(row, 'Close', 1.0)

        # Execute action
        cost = price * 0.001  # 0.1% transaction cost
        if action == 2 and self._balance > price:  # BUY
            shares_to_buy = (self._balance * 0.25) / (price + cost)
            self._shares += shares_to_buy
            self._balance -= shares_to_buy * (price + cost)
        elif action == 0 and self._shares > 0:  # SELL
            self._balance += self._shares * (price - cost)
            self._shares = 0.0

        self._step += 1
        done = self._step >= self._max_steps

        next_row = self.df.iloc[min(self._step, self._max_steps)]
        next_price = self._val(next_row, 'Close', 1.0)
        portfolio_value = self._balance + self._shares * next_price

        # Reward: portfolio return vs previous step, penalise excessive trading
        reward = (portfolio_value - self._prev_value) / self.initial_balance * 100
        if action != 1:  # small penalty for non-HOLD to discourage overtrading
            reward -= 0.01
        self._prev_value = portfolio_value

        return self._get_obs(), reward, done, False, {}


def download_and_prepare(ticker='SPY', period='5y'):
    log.info(f"Downloading {ticker} {period} data...")
    df = yf.download(ticker, period=period, interval='1d', auto_adjust=True, progress=False)
    df = df.dropna()
    df['change_pct'] = df['Close'].pct_change() * 100
    df['rsi'] = _compute_rsi(df['Close'])
    df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df['macd'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['volatility'] = df['Close'].pct_change().rolling(20).std().fillna(0.01)
    df = df.dropna().reset_index(drop=True)
    log.info(f"  {len(df)} training bars loaded")
    return df


def _compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def train():
    df = download_and_prepare('SPY', '5y')

    # Split: 80% train, 20% eval
    split = int(len(df) * 0.8)
    train_df = df.iloc[:split]
    eval_df  = df.iloc[split:]

    def make_env(data):
        return lambda: PrometheusGymEnv(data)

    train_env = DummyVecEnv([make_env(train_df)])
    eval_env  = DummyVecEnv([make_env(eval_df)])

    log.info(f"Training PPO for {TIMESTEPS:,} timesteps...")
    model = PPO(
        'MlpPolicy', train_env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        device='auto',  # uses CUDA if available
    )

    stop_cb = StopTrainingOnRewardThreshold(reward_threshold=50, verbose=1)
    eval_cb = EvalCallback(
        eval_env,
        callback_on_new_best=stop_cb,
        eval_freq=10_000,
        best_model_save_path=str(OUTPUT_PATH.parent),
        verbose=1,
    )

    model.learn(total_timesteps=TIMESTEPS, callback=eval_cb)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(OUTPUT_PATH.with_suffix('')))
    log.info(f"Saved: {OUTPUT_PATH}")

    # Quick eval
    obs = eval_env.reset()
    portfolio = 10_000.0
    for _ in range(len(eval_df) - 1):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, _ = eval_env.step(action)
        portfolio += float(reward[0]) * 100
        if done[0]:
            break
    log.info(f"Eval portfolio: ${portfolio:,.0f} (started $10,000)")
    return model


if __name__ == '__main__':
    train()
    print("SB3 PPO training complete. Restart PROMETHEUS to activate.")
