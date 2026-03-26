#!/usr/bin/env python3
"""
Reinforcement Learning for Trading - Profit Optimization
Learns from actual trading outcomes to maximize profit
"""

import logging
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TradingRLAgent(nn.Module):
    """
    Reinforcement Learning Agent for Trading
    Optimizes for actual profit, not just accuracy
    """
    
    def __init__(self, state_dim: int = 50, action_dim: int = 3, hidden_dim: int = 128):
        super().__init__()
        
        # State: market data, indicators, portfolio state
        # Action: BUY (0), SELL (1), HOLD (2)
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Policy network (actor)
        self.policy_network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # Value network (critic)
        self.value_network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Optimizer
        self.optimizer = torch.optim.Adam(self.parameters(), lr=3e-4)
        
        # Experience replay buffer
        self.replay_buffer = deque(maxlen=10000)
        
        # Hyperparameters
        self.gamma = 0.99  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        self.batch_size = 64
        
    def select_action(self, state: torch.Tensor, training: bool = True) -> Tuple[int, float]:
        """
        Select action using policy network
        
        Returns:
            (action, confidence)
        """
        with torch.no_grad():
            action_probs = self.policy_network(state)
            
            if training and np.random.random() < self.epsilon:
                # Exploration: random action
                action = np.random.randint(self.action_dim)
                confidence = action_probs[action].item()
            else:
                # Exploitation: best action
                action = torch.argmax(action_probs).item()
                confidence = action_probs[action].item()
        
        return action, confidence
    
    def update(self, batch: List[Dict]) -> Dict[str, float]:
        """
        Update policy using experience batch
        
        Args:
            batch: List of (state, action, reward, next_state, done) tuples
            
        Returns:
            Training metrics
        """
        if len(batch) < self.batch_size:
            return {'loss': 0.0, 'policy_loss': 0.0, 'value_loss': 0.0}
        
        # Sample batch
        batch = batch[:self.batch_size]
        
        states = torch.stack([torch.tensor(s['state'], dtype=torch.float32) for s in batch])
        actions = torch.tensor([s['action'] for s in batch], dtype=torch.long)
        rewards = torch.tensor([s['reward'] for s in batch], dtype=torch.float32)
        next_states = torch.stack([torch.tensor(s['next_state'], dtype=torch.float32) for s in batch])
        dones = torch.tensor([s['done'] for s in batch], dtype=torch.float32)
        
        # Compute value estimates
        values = self.value_network(states).squeeze()
        next_values = self.value_network(next_states).squeeze()
        
        # Compute returns (rewards + discounted future values)
        returns = rewards + self.gamma * next_values * (1 - dones)
        
        # Compute advantages
        advantages = returns - values
        
        # Policy loss (actor)
        action_probs = self.policy_network(states)
        log_probs = torch.log(action_probs + 1e-8)
        selected_log_probs = log_probs.gather(1, actions.unsqueeze(1)).squeeze()
        policy_loss = -(selected_log_probs * advantages.detach()).mean()
        
        # Value loss (critic)
        value_loss = nn.MSELoss()(values, returns.detach())
        
        # Total loss
        total_loss = policy_loss + 0.5 * value_loss
        
        # Update
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.parameters(), 1.0)
        self.optimizer.step()
        
        return {
            'loss': total_loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item()
        }
    
    def save(self, path: str):
        """Save model"""
        torch.save({
            'policy_state_dict': self.policy_network.state_dict(),
            'value_state_dict': self.value_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
        logger.info(f"Saved RL agent to {path}")
    
    def load(self, path: str):
        """Load model"""
        if Path(path).exists():
            checkpoint = torch.load(path)
            self.policy_network.load_state_dict(checkpoint['policy_state_dict'])
            self.value_network.load_state_dict(checkpoint['value_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            logger.info(f"Loaded RL agent from {path}")
            return True
        return False


class ReinforcementLearningTrading:
    """
    Reinforcement Learning System for Trading
    Learns from actual trading outcomes to maximize profit
    """
    
    def __init__(self, state_dim: int = 50):
        self.state_dim = state_dim
        self.agent = TradingRLAgent(state_dim=state_dim)
        self.replay_buffer = deque(maxlen=10000)
        self.training_history = []
        
        # Action mapping
        self.action_map = {0: 'BUY', 1: 'SELL', 2: 'HOLD'}
        self.reverse_action_map = {v: k for k, v in self.action_map.items()}
        
        logger.info("✅ Reinforcement Learning Trading System initialized")
    
    def encode_state(self, market_data: Dict, portfolio: Dict, context: Dict) -> np.ndarray:
        """
        Encode trading state into feature vector
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            context: Additional context
            
        Returns:
            State vector
        """
        features = []
        
        # Market data features
        if 'price' in market_data:
            features.append(market_data['price'] / 1000.0)  # Normalize
        if 'volume' in market_data:
            features.append(market_data['volume'] / 1e6)  # Normalize
        
        # Indicator features
        if 'indicators' in market_data:
            indicators = market_data['indicators']
            features.append(indicators.get('rsi', 50) / 100.0)
            features.append(indicators.get('macd', 0) / 10.0)
            features.append(indicators.get('volatility', 0) * 100)
        
        # Portfolio features
        if 'total_value' in portfolio:
            features.append(portfolio['total_value'] / 10000.0)  # Normalize
        if 'positions' in portfolio:
            features.append(len(portfolio['positions']) / 10.0)  # Normalize
        
        # Pad or truncate to state_dim
        while len(features) < self.state_dim:
            features.append(0.0)
        features = features[:self.state_dim]
        
        return np.array(features, dtype=np.float32)
    
    def calculate_reward(self, action: str, outcome: Dict) -> float:
        """
        Calculate reward from trading outcome
        
        Args:
            action: Trading action taken
            outcome: Trading outcome (profit, loss, etc.)
            
        Returns:
            Reward value
        """
        profit = outcome.get('profit', 0.0)
        loss = outcome.get('loss', 0.0)
        success = outcome.get('success', False)
        
        # Base reward: profit/loss
        reward = profit - loss
        
        # Bonus for successful trades
        if success:
            reward += 0.1
        
        # Penalty for failed trades
        if not success and loss > 0:
            reward -= 0.2
        
        # Scale reward
        reward = reward / 100.0  # Normalize
        
        return float(reward)
    
    def make_rl_decision(self, market_data: Dict, portfolio: Dict, context: Dict) -> Dict[str, Any]:
        """
        Make trading decision using RL agent
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            context: Additional context
            
        Returns:
            Trading decision
        """
        # Encode state
        state = self.encode_state(market_data, portfolio, context)
        state_tensor = torch.tensor(state, dtype=torch.float32)
        
        # Select action
        action_idx, confidence = self.agent.select_action(state_tensor, training=True)
        action = self.action_map[action_idx]
        
        return {
            'action': action,
            'confidence': confidence,
            'method': 'reinforcement_learning',
            'state': state.tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    def learn_from_outcome(self, state: np.ndarray, action: str, outcome: Dict, 
                          next_state: np.ndarray, done: bool = False):
        """
        Learn from trading outcome
        
        Args:
            state: State when action was taken
            action: Action taken
            outcome: Trading outcome
            next_state: Next state after action
            done: Whether episode is done
        """
        # Calculate reward
        reward = self.calculate_reward(action, outcome)
        
        # Convert action to index
        action_idx = self.reverse_action_map.get(action, 2)  # Default to HOLD
        
        # Store experience
        experience = {
            'state': state,
            'action': action_idx,
            'reward': reward,
            'next_state': next_state,
            'done': done
        }
        
        self.replay_buffer.append(experience)
        self.agent.replay_buffer.append(experience)
        
        # Update agent if enough experiences
        if len(self.replay_buffer) >= self.agent.batch_size:
            metrics = self.agent.update(list(self.replay_buffer))
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'buffer_size': len(self.replay_buffer)
            })
            
            # Log periodically
            if len(self.training_history) % 10 == 0:
                logger.info(f"RL Training: Loss={metrics.get('loss', 0):.4f}, "
                          f"Policy={metrics.get('policy_loss', 0):.4f}, "
                          f"Value={metrics.get('value_loss', 0):.4f}")
    
    def save_model(self, path: str = "models/rl_trading_agent.pt"):
        """Save RL model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.agent.save(path)
        
        # Save training history
        history_path = path.replace('.pt', '_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
    
    def load_model(self, path: str = "models/rl_trading_agent.pt"):
        """Load RL model"""
        return self.agent.load(path)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics"""
        if not self.training_history:
            return {'status': 'no_training_yet'}
        
        recent = self.training_history[-10:] if len(self.training_history) > 10 else self.training_history
        avg_loss = sum(m['metrics'].get('loss', 0) for m in recent) / len(recent)
        
        return {
            'total_episodes': len(self.training_history),
            'buffer_size': len(self.replay_buffer),
            'average_loss': avg_loss,
            'last_update': self.training_history[-1]['timestamp'] if self.training_history else None
        }

