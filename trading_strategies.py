#!/usr/bin/env python3
"""
🧠 PROMETHEUS TRADING STRATEGIES
Advanced trading strategies for overnight session
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"strategy.{name}")
    
    def analyze(self, symbol: str, data: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Analyze a symbol and return trading signal"""
        raise NotImplementedError

class MomentumStrategy(TradingStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self):
        super().__init__("Momentum")
        self.min_volume = 1000000
        self.momentum_threshold = 2.0
        self.strong_momentum_threshold = 4.0
    
    def analyze(self, symbol: str, data: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Analyze momentum signals"""
        price = data["price"]
        change_pct = data["change_percent"]
        volume = data.get("volume", 0)
        
        analysis = {
            "strategy": self.name,
            "symbol": symbol,
            "signal": "HOLD",
            "confidence": 0.0,
            "reason": "",
            "target_price": price,
            "stop_loss": price * 0.95,
            "take_profit": price * 1.08
        }
        
        # Strong upward momentum
        if change_pct > self.strong_momentum_threshold and volume > self.min_volume:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.9, change_pct / 6.0),
                "reason": f"Strong upward momentum (+{change_pct:.2f}%) with high volume ({volume:,})",
                "take_profit": price * 1.12  # Higher target for strong momentum
            })
        
        # Moderate upward momentum
        elif change_pct > self.momentum_threshold and volume > self.min_volume:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.7, change_pct / 4.0),
                "reason": f"Upward momentum (+{change_pct:.2f}%) with good volume ({volume:,})"
            })
        
        # Overbought condition
        elif change_pct > 8.0:
            analysis.update({
                "signal": "SELL",
                "confidence": 0.6,
                "reason": f"Overbought condition (+{change_pct:.2f}%)"
            })
        
        return analysis

class MeanReversionStrategy(TradingStrategy):
    """Mean reversion trading strategy"""
    
    def __init__(self):
        super().__init__("MeanReversion")
        self.oversold_threshold = -3.0
        self.strong_oversold_threshold = -5.0
        self.min_volume = 800000
    
    def analyze(self, symbol: str, data: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Analyze mean reversion signals"""
        price = data["price"]
        change_pct = data["change_percent"]
        volume = data.get("volume", 0)
        
        analysis = {
            "strategy": self.name,
            "symbol": symbol,
            "signal": "HOLD",
            "confidence": 0.0,
            "reason": "",
            "target_price": price,
            "stop_loss": price * 0.93,
            "take_profit": price * 1.06
        }
        
        # Strong oversold bounce opportunity
        if change_pct < self.strong_oversold_threshold and volume > self.min_volume:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.8, abs(change_pct) / 7.0),
                "reason": f"Strong oversold bounce opportunity ({change_pct:.2f}%) with high volume ({volume:,})",
                "take_profit": price * 1.10  # Higher target for strong oversold
            })
        
        # Moderate oversold condition
        elif change_pct < self.oversold_threshold and volume > self.min_volume:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.6, abs(change_pct) / 5.0),
                "reason": f"Oversold bounce opportunity ({change_pct:.2f}%) with good volume ({volume:,})"
            })
        
        return analysis

class BreakoutStrategy(TradingStrategy):
    """Breakout trading strategy"""
    
    def __init__(self):
        super().__init__("Breakout")
        self.volume_multiplier = 2.0
        self.price_change_threshold = 3.0
    
    def analyze(self, symbol: str, data: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Analyze breakout signals"""
        price = data["price"]
        change_pct = data["change_percent"]
        volume = data.get("volume", 0)
        
        analysis = {
            "strategy": self.name,
            "symbol": symbol,
            "signal": "HOLD",
            "confidence": 0.0,
            "reason": "",
            "target_price": price,
            "stop_loss": price * 0.96,
            "take_profit": price * 1.08
        }
        
        # Volume breakout with price movement
        if abs(change_pct) > self.price_change_threshold and volume > 1500000:
            if change_pct > 0:
                analysis.update({
                    "signal": "BUY",
                    "confidence": min(0.8, (change_pct + volume/1000000) / 10.0),
                    "reason": f"Upward breakout (+{change_pct:.2f}%) with volume spike ({volume:,})",
                    "take_profit": price * 1.12
                })
        
        return analysis

class AIEnhancedStrategy(TradingStrategy):
    """AI-enhanced strategy combining multiple signals"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__("AIEnhanced")
        self.base_url = base_url
        self.momentum_strategy = MomentumStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        self.breakout_strategy = BreakoutStrategy()
    
    def get_ai_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get AI sentiment analysis"""
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/sentiment-analysis",
                json={"symbol": symbol, "timeframe": "1D"},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.warning(f"AI sentiment failed for {symbol}: {e}")
        
        return {"sentiment": "neutral", "confidence": 0.0}
    
    def analyze(self, symbol: str, data: Dict[str, Any], historical_data: List[Dict] = None) -> Dict[str, Any]:
        """Analyze using combined AI and technical strategies"""
        
        # Get individual strategy signals
        momentum_signal = self.momentum_strategy.analyze(symbol, data, historical_data)
        mean_reversion_signal = self.mean_reversion_strategy.analyze(symbol, data, historical_data)
        breakout_signal = self.breakout_strategy.analyze(symbol, data, historical_data)
        
        # Get AI sentiment
        ai_sentiment = self.get_ai_sentiment(symbol)
        
        # Combine signals
        buy_signals = []
        sell_signals = []
        
        if momentum_signal["signal"] == "BUY":
            buy_signals.append(("Momentum", momentum_signal["confidence"]))
        elif momentum_signal["signal"] == "SELL":
            sell_signals.append(("Momentum", momentum_signal["confidence"]))
        
        if mean_reversion_signal["signal"] == "BUY":
            buy_signals.append(("MeanReversion", mean_reversion_signal["confidence"]))
        
        if breakout_signal["signal"] == "BUY":
            buy_signals.append(("Breakout", breakout_signal["confidence"]))
        
        # AI sentiment boost
        sentiment_boost = 0.0
        if ai_sentiment.get("sentiment") == "bullish":
            sentiment_boost = ai_sentiment.get("confidence", 0.0) * 0.2
        elif ai_sentiment.get("sentiment") == "bearish":
            sentiment_boost = -ai_sentiment.get("confidence", 0.0) * 0.2
        
        # Calculate combined signal
        if buy_signals:
            combined_confidence = statistics.mean([conf for _, conf in buy_signals]) + sentiment_boost
            combined_confidence = max(0.0, min(1.0, combined_confidence))
            
            if combined_confidence > 0.6:
                reasons = [f"{strategy} ({conf:.2f})" for strategy, conf in buy_signals]
                if sentiment_boost > 0:
                    reasons.append(f"AI Bullish (+{sentiment_boost:.2f})")
                
                return {
                    "strategy": self.name,
                    "symbol": symbol,
                    "signal": "BUY",
                    "confidence": combined_confidence,
                    "reason": f"Combined signals: {', '.join(reasons)}",
                    "target_price": data["price"] * 1.10,
                    "stop_loss": data["price"] * 0.95,
                    "take_profit": data["price"] * 1.08
                }
        
        elif sell_signals:
            combined_confidence = statistics.mean([conf for _, conf in sell_signals]) - sentiment_boost
            combined_confidence = max(0.0, min(1.0, combined_confidence))
            
            if combined_confidence > 0.5:
                return {
                    "strategy": self.name,
                    "symbol": symbol,
                    "signal": "SELL",
                    "confidence": combined_confidence,
                    "reason": f"Combined sell signals",
                    "target_price": data["price"],
                    "stop_loss": data["price"] * 1.05,
                    "take_profit": data["price"] * 0.95
                }
        
        # Default hold
        return {
            "strategy": self.name,
            "symbol": symbol,
            "signal": "HOLD",
            "confidence": 0.0,
            "reason": "No strong signals detected",
            "target_price": data["price"],
            "stop_loss": data["price"] * 0.95,
            "take_profit": data["price"] * 1.05
        }

class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.strategies = {
            "momentum": MomentumStrategy(),
            "mean_reversion": MeanReversionStrategy(),
            "breakout": BreakoutStrategy(),
            "ai_enhanced": AIEnhancedStrategy(base_url)
        }
        self.logger = logging.getLogger("StrategyManager")
    
    def analyze_symbol(self, symbol: str, data: Dict[str, Any], strategy_name: str = "ai_enhanced") -> Dict[str, Any]:
        """Analyze a symbol using specified strategy"""
        if strategy_name not in self.strategies:
            self.logger.error(f"Unknown strategy: {strategy_name}")
            return {"signal": "HOLD", "confidence": 0.0, "reason": "Unknown strategy"}
        
        strategy = self.strategies[strategy_name]
        return strategy.analyze(symbol, data)
    
    def get_best_opportunities(self, market_data: Dict[str, Any], strategy_name: str = "ai_enhanced", min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """Get best trading opportunities from market data"""
        opportunities = []
        
        for symbol, data in market_data.items():
            analysis = self.analyze_symbol(symbol, data, strategy_name)
            
            if analysis["signal"] == "BUY" and analysis["confidence"] >= min_confidence:
                opportunities.append(analysis)
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x["confidence"], reverse=True)
        return opportunities
    
    def analyze_portfolio_positions(self, positions: Dict[str, Any], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze existing positions for exit signals"""
        exit_signals = []
        
        for symbol, position in positions.items():
            if symbol in market_data:
                current_price = market_data[symbol]["price"]
                avg_price = position["avg_price"]
                pnl_pct = ((current_price - avg_price) / avg_price) * 100
                
                # Check for exit conditions
                exit_analysis = {
                    "symbol": symbol,
                    "action": "HOLD",
                    "confidence": 0.0,
                    "reason": "",
                    "shares_to_sell": 0.0
                }
                
                # Stop loss
                if pnl_pct <= -5.0:
                    exit_analysis.update({
                        "action": "SELL_ALL",
                        "confidence": 1.0,
                        "reason": f"Stop loss triggered ({pnl_pct:.2f}%)",
                        "shares_to_sell": position["shares"]
                    })
                
                # Take profit
                elif pnl_pct >= 8.0:
                    exit_analysis.update({
                        "action": "SELL_PARTIAL",
                        "confidence": 0.8,
                        "reason": f"Take profit ({pnl_pct:.2f}%)",
                        "shares_to_sell": position["shares"] * 0.5
                    })
                
                # Trailing stop
                elif pnl_pct >= 15.0:
                    exit_analysis.update({
                        "action": "SELL_PARTIAL",
                        "confidence": 0.9,
                        "reason": f"Trailing stop ({pnl_pct:.2f}%)",
                        "shares_to_sell": position["shares"] * 0.3
                    })
                
                if exit_analysis["action"] != "HOLD":
                    exit_signals.append(exit_analysis)
        
        return exit_signals

def test_strategies():
    """Test trading strategies with sample data"""
    print("🧠 Testing PROMETHEUS Trading Strategies")
    
    # Sample market data
    sample_data = {
        "AAPL": {"price": 180.50, "change_percent": 3.2, "volume": 2500000},
        "TSLA": {"price": 250.00, "change_percent": -4.1, "volume": 1800000},
        "SPY": {"price": 450.00, "change_percent": 1.5, "volume": 5000000}
    }
    
    manager = StrategyManager()
    
    for symbol, data in sample_data.items():
        print(f"\n📊 Analyzing {symbol}:")
        
        # Test each strategy
        for strategy_name in ["momentum", "mean_reversion", "breakout"]:
            analysis = manager.analyze_symbol(symbol, data, strategy_name)
            print(f"  {strategy_name}: {analysis['signal']} (confidence: {analysis['confidence']:.2f}) - {analysis['reason']}")
    
    # Test combined opportunities
    print(f"\n🎯 Best Opportunities:")
    opportunities = manager.get_best_opportunities(sample_data)
    for opp in opportunities:
        print(f"  {opp['symbol']}: {opp['signal']} (confidence: {opp['confidence']:.2f}) - {opp['reason']}")

if __name__ == "__main__":
    test_strategies()
