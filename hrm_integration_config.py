# HRM Integration Configuration
# This file configures the Full HRM integration for live trading

# Use Full HRM Architecture (True) or Legacy LSTM (False)
USE_FULL_HRM = True

# Device to run HRM on - GPU-aware (auto-detects best available device)
try:
    from gpu_detector import get_device_for_inference
    HRM_DEVICE = get_device_for_inference()
except Exception:
    HRM_DEVICE = 'cpu'  # Fallback to CPU if GPU detector unavailable

# Checkpoint to use
# Options: 'arc_agi_2', 'sudoku_extreme', 'maze_30x30', or None for no checkpoint
ACTIVE_CHECKPOINT = 'arc_agi_2'

# HRM Configuration
HRM_CONFIG = {
    'H_cycles': 2,
    'L_cycles': 2,
    'H_layers': 4,
    'L_layers': 4,
    'hidden_size': 512,
    'num_heads': 8,
    'seq_len': 256,
    'halt_max_steps': 8
}

# Trading Configuration
TRADING_CONFIG = {
    'max_position_size': 0.1,
    'stop_loss_percent': 0.02,
    'take_profit_percent': 0.04
}
