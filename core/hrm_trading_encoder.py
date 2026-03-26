#!/usr/bin/env python3
"""
HRM Trading Encoder
Encodes trading data (prices, volumes, indicators) into HRM input token format
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class HRMTradingEncoder:
    """
    Encodes trading data into HRM token sequences
    Converts market data to discrete token representations
    """
    
    def __init__(self, vocab_size: int = 1000, seq_len: int = 256):
        self.vocab_size = vocab_size
        self.seq_len = seq_len
        
        # Token ranges for different features
        self.token_ranges = {
            'price': (0, 499),      # 500 tokens for price
            'volume': (500, 699),  # 200 tokens for volume
            'rsi': (700, 799),     # 100 tokens for RSI
            'macd': (800, 899),    # 100 tokens for MACD
            'bb': (900, 949),      # 50 tokens for Bollinger Bands
            'other': (950, 999)    # 50 tokens for other features
        }
    
    def encode_price(self, price: float, base_price: Optional[float] = None) -> int:
        """
        Encode price to token
        
        Args:
            price: Current price
            base_price: Optional base price for normalization
        
        Returns:
            Token ID
        """
        if base_price is None:
            base_price = price
        
        # Calculate price change percentage
        price_change = ((price - base_price) / base_price) * 100
        
        # Map to token range (0-499)
        # -50% to +50% mapped to 0-499
        normalized = (price_change + 50) / 100  # 0 to 1
        token = int(self.token_ranges['price'][0] + 
                   normalized * (self.token_ranges['price'][1] - self.token_ranges['price'][0]))
        
        return max(self.token_ranges['price'][0], 
                  min(self.token_ranges['price'][1], token))
    
    def encode_volume(self, volume: float, avg_volume: Optional[float] = None) -> int:
        """
        Encode volume to token
        
        Args:
            volume: Current volume
            avg_volume: Optional average volume for normalization
        
        Returns:
            Token ID
        """
        if avg_volume is None or avg_volume == 0:
            # Use log scale
            log_volume = np.log10(max(1, volume))
            normalized = (log_volume % 10) / 10  # 0 to 1
        else:
            # Relative to average
            volume_ratio = volume / avg_volume
            normalized = min(1.0, volume_ratio / 5.0)  # Cap at 5x average
        
        token = int(self.token_ranges['volume'][0] + 
                   normalized * (self.token_ranges['volume'][1] - self.token_ranges['volume'][0]))
        
        return max(self.token_ranges['volume'][0], 
                  min(self.token_ranges['volume'][1], token))
    
    def encode_rsi(self, rsi: float) -> int:
        """
        Encode RSI to token
        
        Args:
            rsi: RSI value (0-100)
        
        Returns:
            Token ID
        """
        # RSI is already 0-100, map to token range
        normalized = rsi / 100.0
        token = int(self.token_ranges['rsi'][0] + 
                   normalized * (self.token_ranges['rsi'][1] - self.token_ranges['rsi'][0]))
        
        return max(self.token_ranges['rsi'][0], 
                  min(self.token_ranges['rsi'][1], token))
    
    def encode_macd(self, macd: float) -> int:
        """
        Encode MACD to token
        
        Args:
            macd: MACD value
        
        Returns:
            Token ID
        """
        # Normalize MACD to -1 to 1 range
        normalized = np.tanh(macd)  # Tanh maps to -1 to 1
        normalized = (normalized + 1) / 2  # 0 to 1
        
        token = int(self.token_ranges['macd'][0] + 
                   normalized * (self.token_ranges['macd'][1] - self.token_ranges['macd'][0]))
        
        return max(self.token_ranges['macd'][0], 
                  min(self.token_ranges['macd'][1], token))
    
    def encode_bollinger_bands(self, price: float, upper: float, lower: float) -> int:
        """
        Encode Bollinger Band position to token
        
        Args:
            price: Current price
            upper: Upper band
            lower: Lower band
        
        Returns:
            Token ID
        """
        if upper == lower:
            return self.token_ranges['bb'][0] + 25  # Middle
        
        # Position within bands (0 = lower, 1 = upper)
        position = (price - lower) / (upper - lower)
        
        token = int(self.token_ranges['bb'][0] + 
                   position * (self.token_ranges['bb'][1] - self.token_ranges['bb'][0]))
        
        return max(self.token_ranges['bb'][0], 
                  min(self.token_ranges['bb'][1], token))
    
    def encode_market_data(self, market_data: Dict[str, Any], 
                          price_history: Optional[List[float]] = None) -> torch.Tensor:
        """
        Encode complete market data to token sequence
        
        Args:
            market_data: Market data dictionary
            price_history: Optional price history for context
        
        Returns:
            Token tensor [seq_len]
        """
        tokens = []
        
        # Encode current price
        if 'price' in market_data:
            price = float(market_data['price'])
            base_price = price_history[-20] if price_history and len(price_history) >= 20 else price
            tokens.append(self.encode_price(price, base_price))
        
        # Encode volume
        if 'volume' in market_data:
            volume = float(market_data['volume'])
            avg_volume = np.mean([float(v) for v in market_data.get('volume_history', [volume])]) if 'volume_history' in market_data else None
            tokens.append(self.encode_volume(volume, avg_volume))
        
        # Encode technical indicators
        if 'indicators' in market_data:
            indicators = market_data['indicators']
            
            if 'rsi' in indicators:
                tokens.append(self.encode_rsi(float(indicators['rsi'])))
            
            if 'macd' in indicators:
                tokens.append(self.encode_macd(float(indicators['macd'])))
            
            if 'bollinger_upper' in indicators and 'bollinger_lower' in indicators:
                price = float(market_data.get('price', 100))
                upper = float(indicators['bollinger_upper'])
                lower = float(indicators['bollinger_lower'])
                tokens.append(self.encode_bollinger_bands(price, upper, lower))
        
        # Encode price history if available
        if price_history:
            for price in price_history[-20:]:  # Last 20 prices
                base = price_history[-21] if len(price_history) > 20 else price
                tokens.append(self.encode_price(float(price), float(base)))
        
        # Pad or truncate to seq_len
        if len(tokens) < self.seq_len:
            tokens.extend([0] * (self.seq_len - len(tokens)))
        else:
            tokens = tokens[:self.seq_len]
        
        return torch.tensor(tokens, dtype=torch.int32)
    
    def encode_sequence(self, market_data_sequence: List[Dict[str, Any]]) -> torch.Tensor:
        """
        Encode a sequence of market data points
        
        Args:
            market_data_sequence: List of market data dictionaries
        
        Returns:
            Token tensor [len(sequence), seq_len]
        """
        encoded_sequences = []
        
        for i, market_data in enumerate(market_data_sequence):
            # Get price history up to current point
            price_history = [float(d.get('price', 100)) for d in market_data_sequence[:i+1]]
            
            encoded = self.encode_market_data(market_data, price_history)
            encoded_sequences.append(encoded)
        
        return torch.stack(encoded_sequences)

