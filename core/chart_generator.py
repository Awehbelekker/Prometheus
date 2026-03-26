"""
Chart Generator for Visual AI Analysis
Generates high-quality chart images from Polygon.io data
for LLaVA visual analysis and historical learning
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import mplfinance as mpf
    import pandas as pd
    CHART_LIBS_AVAILABLE = True
    logger.info("Chart generation libraries available")
except ImportError as e:
    CHART_LIBS_AVAILABLE = False
    logger.warning(f"Chart generation libraries not available: {e}")
    logger.warning("Install with: pip install matplotlib mplfinance pandas")


class ChartGenerator:
    """
    Generates trading charts from market data for visual AI analysis
    """
    
    def __init__(self, output_dir: str = "charts"):
        """
        Initialize chart generator
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if not CHART_LIBS_AVAILABLE:
            logger.error("Chart generation unavailable - install matplotlib and mplfinance")
        
        logger.info(f"Chart generator initialized. Output: {self.output_dir}")
    
    def generate_candlestick_chart(self,
                                   symbol: str,
                                   ohlcv_data: pd.DataFrame,
                                   timeframe: str = "1D",
                                   indicators: Optional[List[str]] = None) -> Optional[str]:
        """
        Generate professional candlestick chart with indicators
        
        Args:
            symbol: Trading symbol
            ohlcv_data: DataFrame with columns: open, high, low, close, volume
            timeframe: Timeframe string (1D, 1H, etc.)
            indicators: List of indicators to add ['MA20', 'MA50', 'RSI', 'MACD', 'VOLUME']
        
        Returns:
            Path to generated chart image
        """
        if not CHART_LIBS_AVAILABLE:
            return None
        
        try:
            # Ensure datetime index
            if not isinstance(ohlcv_data.index, pd.DatetimeIndex):
                ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
            
            # Prepare data for mplfinance
            ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']].copy()
            
            # Configure style
            mc = mpf.make_marketcolors(
                up='#26a69a', down='#ef5350',
                edge='inherit',
                wick={'up': '#26a69a', 'down': '#ef5350'},
                volume={'up': '#26a69a', 'down': '#ef5350'}
            )
            
            s = mpf.make_mpf_style(
                marketcolors=mc,
                gridstyle='-',
                gridcolor='#e0e0e0',
                facecolor='white',
                figcolor='white',
                y_on_right=False
            )
            
            # Add indicators if requested
            add_plots = []
            
            if indicators:
                if 'MA20' in indicators:
                    ohlcv_data['MA20'] = ohlcv_data['close'].rolling(window=20).mean()
                    add_plots.append(mpf.make_addplot(ohlcv_data['MA20'], color='blue', width=1.5))
                
                if 'MA50' in indicators:
                    ohlcv_data['MA50'] = ohlcv_data['close'].rolling(window=50).mean()
                    add_plots.append(mpf.make_addplot(ohlcv_data['MA50'], color='orange', width=1.5))
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{timeframe}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            # Create chart
            kwargs = {
                'type': 'candle',
                'style': s,
                'volume': True,
                'title': f'{symbol} - {timeframe}',
                'ylabel': 'Price',
                'ylabel_lower': 'Volume',
                'savefig': str(filepath),
                'figsize': (12, 8),
                'tight_layout': True
            }
            
            if add_plots:
                kwargs['addplot'] = add_plots
            
            mpf.plot(ohlcv_data, **kwargs)
            
            logger.info(f"Generated chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating chart for {symbol}: {e}")
            return None
    
    def generate_pattern_chart(self,
                              symbol: str,
                              ohlcv_data: pd.DataFrame,
                              pattern_type: str,
                              highlight_zones: Optional[List[Tuple[float, float]]] = None) -> Optional[str]:
        """
        Generate chart highlighting specific patterns
        
        Args:
            symbol: Trading symbol
            ohlcv_data: OHLCV data
            pattern_type: Type of pattern to highlight
            highlight_zones: List of (start_idx, end_idx) tuples to highlight
        
        Returns:
            Path to generated chart
        """
        if not CHART_LIBS_AVAILABLE:
            return None
        
        try:
            # Generate base chart first
            chart_path = self.generate_candlestick_chart(
                symbol, ohlcv_data, 
                indicators=['MA20', 'MA50']
            )
            
            if chart_path and highlight_zones:
                # TODO: Add highlighting overlay
                # This would require custom matplotlib overlays
                pass
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating pattern chart: {e}")
            return None
    
    def generate_multi_timeframe_chart(self,
                                      symbol: str,
                                      data_1h: pd.DataFrame,
                                      data_4h: pd.DataFrame,
                                      data_1d: pd.DataFrame) -> Optional[str]:
        """
        Generate multi-timeframe analysis chart
        
        Args:
            symbol: Trading symbol
            data_1h: 1-hour OHLCV data
            data_4h: 4-hour OHLCV data
            data_1d: Daily OHLCV data
        
        Returns:
            Path to generated multi-panel chart
        """
        if not CHART_LIBS_AVAILABLE:
            return None
        
        try:
            fig, axes = plt.subplots(3, 1, figsize=(12, 12))
            fig.suptitle(f'{symbol} - Multi-Timeframe Analysis', fontsize=16)
            
            timeframes = [
                (data_1h, '1 Hour', axes[0]),
                (data_4h, '4 Hour', axes[1]),
                (data_1d, '1 Day', axes[2])
            ]
            
            for data, tf_label, ax in timeframes:
                # Simple line plot for multi-timeframe
                ax.plot(data.index, data['close'], linewidth=1.5)
                ax.set_title(f'{tf_label} Timeframe')
                ax.set_ylabel('Price')
                ax.grid(True, alpha=0.3)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_multi_timeframe_{timestamp}.png"
            filepath = self.output_dir / filename
            
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Generated multi-timeframe chart: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating multi-timeframe chart: {e}")
            return None
    
    def generate_support_resistance_chart(self,
                                         symbol: str,
                                         ohlcv_data: pd.DataFrame,
                                         support_levels: List[float],
                                         resistance_levels: List[float]) -> Optional[str]:
        """
        Generate chart with support/resistance levels marked
        
        Args:
            symbol: Trading symbol
            ohlcv_data: OHLCV data
            support_levels: List of support price levels
            resistance_levels: List of resistance price levels
        
        Returns:
            Path to generated chart
        """
        if not CHART_LIBS_AVAILABLE:
            return None
        
        try:
            # Generate base candlestick chart
            chart_path = self.generate_candlestick_chart(symbol, ohlcv_data)
            
            if chart_path:
                # Reopen and add S/R lines
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Plot candlesticks (simplified)
                ax.plot(ohlcv_data.index, ohlcv_data['close'], linewidth=1.5, color='#333')
                
                # Add support levels
                for level in support_levels:
                    ax.axhline(y=level, color='green', linestyle='--', 
                              linewidth=2, alpha=0.7, label=f'Support ${level:.2f}')
                
                # Add resistance levels
                for level in resistance_levels:
                    ax.axhline(y=level, color='red', linestyle='--', 
                              linewidth=2, alpha=0.7, label=f'Resistance ${level:.2f}')
                
                ax.set_title(f'{symbol} - Support & Resistance')
                ax.set_ylabel('Price')
                ax.legend(loc='best')
                ax.grid(True, alpha=0.3)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{symbol}_SR_{timestamp}.png"
                filepath = self.output_dir / filename
                
                plt.savefig(filepath, dpi=150, bbox_inches='tight')
                plt.close()
                
                return str(filepath)
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating S/R chart: {e}")
            return None
    
    def cleanup_old_charts(self, days_to_keep: int = 7):
        """
        Clean up chart files older than specified days
        
        Args:
            days_to_keep: Number of days to keep charts
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            for chart_file in self.output_dir.glob("*.png"):
                if chart_file.stat().st_mtime < cutoff_time.timestamp():
                    chart_file.unlink()
                    logger.debug(f"Deleted old chart: {chart_file}")
            
        except Exception as e:
            logger.error(f"Error cleaning up charts: {e}")


# Global instance
chart_generator = ChartGenerator()


def generate_chart_from_polygon(symbol: str, 
                                timeframe: str = "1D", 
                                days_back: int = 90) -> Optional[str]:
    """
    Convenience function to generate chart from Polygon data
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe (1D, 1H, etc.)
        days_back: Number of days of historical data
    
    Returns:
        Path to generated chart
    """
    try:
        from core.real_world_data_orchestrator import RealWorldDataOrchestrator
        
        orchestrator = RealWorldDataOrchestrator()
        
        # Get historical data
        # Note: This is a placeholder - you'd need to implement actual Polygon data fetching
        # For now, generate sample data
        
        logger.warning("Using sample data - integrate with actual Polygon.io API")
        
        # Generate sample data (replace with actual Polygon data)
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        data = pd.DataFrame({
            'open': np.random.randn(days_back).cumsum() + 100,
            'high': np.random.randn(days_back).cumsum() + 102,
            'low': np.random.randn(days_back).cumsum() + 98,
            'close': np.random.randn(days_back).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, days_back)
        }, index=dates)
        
        # Ensure high is highest, low is lowest
        data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
        data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
        
        return chart_generator.generate_candlestick_chart(
            symbol, data, timeframe, indicators=['MA20', 'MA50']
        )
        
    except Exception as e:
        logger.error(f"Error generating chart from Polygon: {e}")
        return None
