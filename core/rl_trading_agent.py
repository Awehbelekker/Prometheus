"""
RL Trading Agent — thin factory wrapper around TradingRLAgent.
Exposes get_rl_agent() used by parallel_shadow_trading and other modules.
"""
import logging
import torch
from pathlib import Path

logger = logging.getLogger(__name__)

_RL_AGENT_INSTANCE = None
_MODEL_PATH = Path("trained_models/rl_trading_agent.pt")


def get_rl_agent():
    """Return singleton TradingRLAgent loaded from checkpoint."""
    global _RL_AGENT_INSTANCE
    if _RL_AGENT_INSTANCE is not None:
        return _RL_AGENT_INSTANCE

    from core.reinforcement_learning_trading import TradingRLAgent

    agent = TradingRLAgent(state_dim=50, action_dim=3, hidden_dim=128)

    if _MODEL_PATH.exists():
        try:
            ckpt = torch.load(str(_MODEL_PATH), map_location="cpu", weights_only=False)
            if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
                agent.load_state_dict(ckpt["model_state_dict"], strict=False)
            elif isinstance(ckpt, dict) and "state_dict" in ckpt:
                agent.load_state_dict(ckpt["state_dict"], strict=False)
            elif hasattr(ckpt, "parameters"):
                agent = ckpt
            else:
                agent.load_state_dict(ckpt, strict=False)
            logger.info(f"✅ RL Trading Agent loaded from {_MODEL_PATH}")
        except Exception as e:
            logger.warning(f"RL agent checkpoint load failed ({e}) — using fresh weights")
    else:
        logger.warning(f"RL agent checkpoint not found at {_MODEL_PATH} — using fresh weights")

    agent.eval()
    _RL_AGENT_INSTANCE = agent
    return agent
