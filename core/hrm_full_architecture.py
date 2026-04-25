#!/usr/bin/env python3
"""
Full HRM Architecture Integration for Prometheus Trading
Implements the true Hierarchical Reasoning Model with H/L modules using self-attention
"""

import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

# Add official_hrm to path
official_hrm_path = Path(__file__).parent.parent / "official_hrm"
if official_hrm_path.exists():
    sys.path.insert(0, str(official_hrm_path))

try:
    # Try to import official HRM
    # Note: FlashAttention may not be available on all systems, but we can still try
    from models.hrm.hrm_act_v1 import (
        HierarchicalReasoningModel_ACTV1,
        HierarchicalReasoningModel_ACTV1Config,
        HierarchicalReasoningModel_ACTV1Carry
    )
    OFFICIAL_HRM_AVAILABLE = True
except ImportError as e:
    # Check if it's just FlashAttention missing
    import_error_str = str(e)
    if 'flash_attn' in import_error_str.lower():
        logging.warning(f"FlashAttention not available: {e}")
        logging.warning("HRM will work but may be slower. Install with: pip install flash-attn")
        # Try to continue anyway - the model might work without it
        try:
            from models.hrm.hrm_act_v1 import (
                HierarchicalReasoningModel_ACTV1,
                HierarchicalReasoningModel_ACTV1Config,
                HierarchicalReasoningModel_ACTV1Carry
            )
            OFFICIAL_HRM_AVAILABLE = True
        except:
            OFFICIAL_HRM_AVAILABLE = False
            HierarchicalReasoningModel_ACTV1 = None
            HierarchicalReasoningModel_ACTV1Config = None
            HierarchicalReasoningModel_ACTV1Carry = None
    else:
        logging.warning(f"Official HRM not available: {e}")
        OFFICIAL_HRM_AVAILABLE = False
        HierarchicalReasoningModel_ACTV1 = None
        HierarchicalReasoningModel_ACTV1Config = None
        HierarchicalReasoningModel_ACTV1Carry = None

logger = logging.getLogger(__name__)


@dataclass
class HRMTradingConfig:
    """Configuration for HRM trading system"""
    # HRM Architecture
    H_cycles: int = 2  # Abstract strategy planning iterations
    L_cycles: int = 2  # Detailed execution iterations
    H_layers: int = 4  # High-level attention layers
    L_layers: int = 4  # Low-level attention layers
    
    # Model dimensions
    hidden_size: int = 512
    num_heads: int = 8
    expansion: float = 4.0
    
    # Sequence config
    seq_len: int = 256  # Maximum sequence length for market data
    batch_size: int = 1  # Default batch size
    
    # Trading-specific
    vocab_size: int = 1000  # Vocabulary size for trading actions
    num_market_regimes: int = 4  # bull, bear, sideways, volatile
    market_regime_emb_dim: int = 512  # Market regime embedding dimension
    
    # ACT Halting
    halt_max_steps: int = 8
    halt_exploration_prob: float = 0.1
    
    # Position encoding
    pos_encodings: str = "rope"  # "rope" or "learned"
    rope_theta: float = 10000.0
    
    # Other
    rms_norm_eps: float = 1e-5
    forward_dtype: str = "bfloat16"
    device: str = "cpu"


class FullHRMArchitecture:
    """
    Full HRM Architecture wrapper for trading
    Uses official HRM with proper H/L module cycles and ACT halting
    """
    
    def __init__(self, config: Optional[HRMTradingConfig] = None, device: str = "cpu"):
        if not OFFICIAL_HRM_AVAILABLE:
            raise ImportError("Official HRM not available. Please ensure official_hrm/ is properly set up.")
        
        self.device = device
        self.config = config or HRMTradingConfig()
        self.config.device = device
        
        # Create HRM config dict
        hrm_config_dict = {
            "batch_size": self.config.batch_size,
            "seq_len": self.config.seq_len,
            "puzzle_emb_ndim": self.config.market_regime_emb_dim,
            "num_puzzle_identifiers": self.config.num_market_regimes,
            "vocab_size": self.config.vocab_size,
            "H_cycles": self.config.H_cycles,
            "L_cycles": self.config.L_cycles,
            "H_layers": self.config.H_layers,
            "L_layers": self.config.L_layers,
            "hidden_size": self.config.hidden_size,
            "expansion": self.config.expansion,
            "num_heads": self.config.num_heads,
            "pos_encodings": self.config.pos_encodings,
            "rms_norm_eps": self.config.rms_norm_eps,
            "rope_theta": self.config.rope_theta,
            "halt_max_steps": self.config.halt_max_steps,
            "halt_exploration_prob": self.config.halt_exploration_prob,
            "forward_dtype": self.config.forward_dtype
        }
        
        # Initialize HRM model
        try:
            # Convert dict to dataclass config — use checkpoint-verified values
            if isinstance(hrm_config_dict, dict):
                hrm_cfg = HierarchicalReasoningModel_ACTV1Config(
                    vocab_size=20,       # checkpoint: embed_tokens [20, 512]
                    hidden_size=int(hrm_config_dict.get("hidden_size", 512)),
                    num_heads=int(hrm_config_dict.get("num_heads", 8)),
                    H_layers=int(hrm_config_dict.get("H_layers", 4)),
                    L_layers=int(hrm_config_dict.get("L_layers", 4)),
                    H_cycles=int(hrm_config_dict.get("H_cycles", 2)),
                    L_cycles=int(hrm_config_dict.get("L_cycles", 2)),
                    expansion=3,         # checkpoint: gate_up_proj [3072,512] → expansion=3
                    halt_max_steps=int(hrm_config_dict.get("halt_max_steps", 16)),
                    seq_len=int(hrm_config_dict.get("seq_len", 101)),
                )
            else:
                hrm_cfg = hrm_config_dict
            self.hrm_model = HierarchicalReasoningModel_ACTV1(hrm_cfg)
            self.hrm_model = self.hrm_model.to(device)
            self.hrm_model.eval()  # Set to eval mode for inference
            logger.info("✅ Full HRM Architecture initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize HRM model: {e}")
            raise
        
        # Track state
        self.current_carry = None
        self.performance_metrics = {
            'total_decisions': 0,
            'hrm_calls': 0,
            'average_confidence': 0.0,
            'halt_steps': []
        }
    
    def prepare_batch(self, inputs: torch.Tensor, market_regime_ids: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Prepare batch data for HRM
        
        Args:
            inputs: Tokenized market data [batch_size, seq_len]
            market_regime_ids: Market regime identifiers [batch_size]
        
        Returns:
            Batch dictionary for HRM
        """
        batch_size = inputs.shape[0]
        
        # Ensure inputs are int32
        if inputs.dtype != torch.int32:
            inputs = inputs.to(torch.int32)
        
        # Ensure market_regime_ids are int32
        if market_regime_ids.dtype != torch.int32:
            market_regime_ids = market_regime_ids.to(torch.int32)
        
        return {
            "inputs": inputs.to(self.device),
            "puzzle_identifiers": market_regime_ids.to(self.device)
        }
    
    def forward(self, batch: Dict[str, torch.Tensor], 
                carry: Optional[HierarchicalReasoningModel_ACTV1Carry] = None) -> Tuple[Dict[str, torch.Tensor], HierarchicalReasoningModel_ACTV1Carry]:
        """
        Forward pass through HRM
        
        Args:
            batch: Prepared batch data
            carry: Optional carry state from previous step
        
        Returns:
            (outputs, new_carry) tuple
        """
        if carry is None:
            carry = self.hrm_model.initial_carry(batch)
        
        # Forward through HRM
        new_carry, outputs = self.hrm_model(carry, batch)
        
        # Update metrics
        self.performance_metrics['hrm_calls'] += 1
        if 'q_halt_logits' in outputs and 'q_continue_logits' in outputs:
            # Track halting behavior
            halt_decision = outputs['q_halt_logits'] > outputs['q_continue_logits']
            self.performance_metrics['halt_steps'].append(new_carry.steps.cpu().numpy().tolist())
        
        return outputs, new_carry
    
    def make_decision(self, market_data_tokens: torch.Tensor, 
                     market_regime_id: int,
                     carry: Optional[HierarchicalReasoningModel_ACTV1Carry] = None) -> Dict[str, Any]:
        """
        Make trading decision using full HRM
        
        Args:
            market_data_tokens: Tokenized market data [seq_len] or [1, seq_len]
            market_regime_id: Market regime identifier (0-3)
            carry: Optional carry state
        
        Returns:
            Decision dictionary with action, confidence, etc.
        """
        # Ensure batch dimension
        if market_data_tokens.dim() == 1:
            market_data_tokens = market_data_tokens.unsqueeze(0)
        
        batch_size = market_data_tokens.shape[0]
        market_regime_ids = torch.full((batch_size,), market_regime_id, dtype=torch.int32)
        
        # Prepare batch
        batch = self.prepare_batch(market_data_tokens, market_regime_ids)
        
        # Forward pass
        outputs, new_carry = self.forward(batch, carry)
        
        # Extract logits
        logits = outputs['logits']  # [batch_size, seq_len, vocab_size]
        
        # Get prediction (last token)
        prediction_logits = logits[:, -1, :]  # [batch_size, vocab_size]
        predicted_token = torch.argmax(prediction_logits, dim=-1).item()
        
        # Calculate confidence (softmax probability)
        probs = torch.softmax(prediction_logits, dim=-1)
        confidence = probs[0, predicted_token].item()
        
        # Extract Q-values for halting
        q_halt = outputs.get('q_halt_logits', torch.tensor(0.0))
        q_continue = outputs.get('q_continue_logits', torch.tensor(0.0))
        
        # Update metrics
        self.performance_metrics['total_decisions'] += 1
        self.current_carry = new_carry
        
        return {
            'action': predicted_token,
            'confidence': confidence,
            'logits': logits.cpu().numpy().tolist(),
            'q_halt': q_halt.cpu().item() if isinstance(q_halt, torch.Tensor) else q_halt,
            'q_continue': q_continue.cpu().item() if isinstance(q_continue, torch.Tensor) else q_continue,
            'halt_steps': new_carry.steps.cpu().item() if hasattr(new_carry.steps, 'item') else int(new_carry.steps),
            'carry': new_carry
        }
    
    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """
        Load HRM checkpoint
        
        Args:
            checkpoint_path: Path to checkpoint file
        
        Returns:
            True if successful
        """
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model' in checkpoint:
                    state_dict = checkpoint['model']
                elif 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                else:
                    state_dict = checkpoint
            else:
                state_dict = checkpoint
            
            # Load state dict
            self.hrm_model.load_state_dict(state_dict, strict=False)
            logger.info(f"✅ Loaded HRM checkpoint from {checkpoint_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load checkpoint: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = self.performance_metrics.copy()
        
        # Calculate average halt steps
        if metrics['halt_steps']:
            all_steps = [step for sublist in metrics['halt_steps'] for step in (sublist if isinstance(sublist, list) else [sublist])]
            if all_steps:
                metrics['avg_halt_steps'] = sum(all_steps) / len(all_steps)
                metrics['max_halt_steps'] = max(all_steps)
                metrics['min_halt_steps'] = min(all_steps)
        
        return metrics
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.performance_metrics = {
            'total_decisions': 0,
            'hrm_calls': 0,
            'average_confidence': 0.0,
            'halt_steps': []
        }


def create_hrm_for_trading(device: str = "cpu", 
                          config: Optional[HRMTradingConfig] = None,
                          checkpoint_path: Optional[str] = None) -> FullHRMArchitecture:
    """
    Factory function to create HRM for trading
    
    Args:
        device: Device to run on
        config: Optional configuration
        checkpoint_path: Optional checkpoint to load
    
    Returns:
        FullHRMArchitecture instance
    """
    hrm = FullHRMArchitecture(config=config, device=device)
    
    if checkpoint_path and os.path.exists(checkpoint_path):
        hrm.load_checkpoint(checkpoint_path)
    
    return hrm

