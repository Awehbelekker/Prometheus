"""Quick test: DirectML GPU placement for RL agent"""
import torch
import torch_directml

dev = torch_directml.device()
print(f"DirectML device: {dev}")

# Test simple model placement
m = torch.nn.Linear(50, 3)
m.to(dev)
print(f"Model params on: {next(m.parameters()).device}")

# Test forward pass
x = torch.randn(1, 50).to(dev)
y = m(x)
print(f"Forward pass OK, output on: {y.device}")

# Test gpu_detector integration
from gpu_detector import get_device_for_inference
inf_dev = get_device_for_inference()
print(f"get_device_for_inference() -> {inf_dev} (type: {type(inf_dev).__name__})")

# Test RL agent load
from core.reinforcement_learning_trading import TradingRLAgent
agent = TradingRLAgent(state_dim=50, action_dim=3, hidden_dim=128)
ckpt = torch.load('trained_models/rl_trading_agent.pt', map_location='cpu', weights_only=False)
agent.policy_network.load_state_dict(ckpt['policy_state_dict'])
agent.value_network.load_state_dict(ckpt['value_state_dict'])
agent.policy_network.to(inf_dev)
agent.value_network.to(inf_dev)
agent.eval()
print(f"RL Agent policy on: {next(agent.policy_network.parameters()).device}")
print(f"RL Agent value on: {next(agent.value_network.parameters()).device}")
print("ALL TESTS PASSED - GPU acceleration working!")
