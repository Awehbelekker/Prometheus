"""
INTELLIGENT DATA COMPRESSION FOR TRADING DATA
============================================

Trading-optimized data compression system that balances storage efficiency
with data integrity for financial time series and market data.

Features:
- Trading-specific compression strategies
- Importance-based compression levels
- Lossless compression for critical signals
- Minimal loss for price data (<0.1% loss)
- Moderate loss for news data (<5% loss)
- Aggressive compression for social data
- High-frequency data optimization
- Real-time compression/decompression
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import uuid
import json
import zlib
import lz4.frame
import gzip
import pickle
import math
import struct

logger = logging.getLogger(__name__)

class CompressionStrategy(Enum):
    LOSSLESS = "lossless"
    MINIMAL_LOSS = "minimal_loss"
    MODERATE_LOSS = "moderate_loss"
    AGGRESSIVE = "aggressive"

class DataImportance(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CompressionAlgorithm(Enum):
    LZ4 = "lz4"
    GZIP = "gzip"
    ZLIB = "zlib"
    CUSTOM_TRADING = "custom_trading"

@dataclass
class CompressionResult:
    """Compression result with metadata"""
    compressed_data: bytes
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionAlgorithm
    strategy: CompressionStrategy
    data_importance: DataImportance
    trading_metadata: Dict[str, Any]
    compression_time: float
    data_integrity_score: float

@dataclass
class TradingDataPacket:
    """Trading data packet structure"""
    packet_id: str
    timestamp: datetime
    data_type: str
    symbols: List[str]
    data: Dict[str, Any]
    importance: DataImportance
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntelligentCompressionEngine:
    """Base intelligent compression engine"""
    
    def __init__(self):
        self.compression_stats = {
            'total_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'average_ratio': 0.0,
            'compression_times': []
        }
        
        logger.info("🗜️ Intelligent Compression Engine initialized")
    
    def compress_data(self, data: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Base compression method"""
        
        start_time = datetime.now()
        
        # Serialize data
        serialized_data = pickle.dumps(data)
        original_size = len(serialized_data)
        
        # Apply compression based on strategy
        if strategy['type'] == 'lossless':
            compressed_data = self._apply_lossless_compression(serialized_data, strategy.get('algorithm', 'lz4'))
        elif strategy['type'] == 'minimal_loss':
            compressed_data = self._apply_minimal_loss_compression(data, strategy)
        elif strategy['type'] == 'moderate_loss':
            compressed_data = self._apply_moderate_loss_compression(data, strategy)
        else:  # aggressive
            compressed_data = self._apply_aggressive_compression(data, strategy)
        
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        compression_time = (datetime.now() - start_time).total_seconds()
        
        # Update stats
        self._update_compression_stats(original_size, compressed_size, compression_time)
        
        return {
            'compressed_data': compressed_data,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'compression_time': compression_time,
            'strategy': strategy
        }
    
    def _apply_lossless_compression(self, data: bytes, algorithm: str) -> bytes:
        """Apply lossless compression"""
        
        if algorithm == 'lz4':
            return lz4.frame.compress(data)
        elif algorithm == 'gzip':
            return gzip.compress(data)
        else:  # zlib
            return zlib.compress(data)
    
    def _apply_minimal_loss_compression(self, data: Dict[str, Any], strategy: Dict[str, Any]) -> bytes:
        """Apply minimal loss compression for price data"""
        
        # Quantize numerical data with minimal precision loss
        processed_data = self._quantize_numerical_data(data, strategy.get('precision_loss', 0.001))
        
        # Apply lossless compression to processed data
        serialized = pickle.dumps(processed_data)
        return lz4.frame.compress(serialized)
    
    def _apply_moderate_loss_compression(self, data: Dict[str, Any], strategy: Dict[str, Any]) -> bytes:
        """Apply moderate loss compression for news data"""
        
        # Reduce data variance while retaining key information
        processed_data = self._reduce_data_variance(data, strategy.get('variance_retention', 0.98))
        
        # Apply compression
        serialized = pickle.dumps(processed_data)
        return gzip.compress(serialized)
    
    def _apply_aggressive_compression(self, data: Dict[str, Any], strategy: Dict[str, Any]) -> bytes:
        """Apply aggressive compression for social data"""
        
        # Significant data reduction
        processed_data = self._aggressive_data_reduction(data, strategy.get('variance_retention', 0.85))
        
        # Apply high compression
        serialized = pickle.dumps(processed_data)
        return gzip.compress(serialized, compresslevel=9)
    
    def _quantize_numerical_data(self, data: Dict[str, Any], precision_loss: float) -> Dict[str, Any]:
        """Quantize numerical data with controlled precision loss"""
        
        processed = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # Quantize with precision loss
                if isinstance(value, float):
                    quantization_factor = 1.0 / precision_loss
                    processed[key] = round(value * quantization_factor) / quantization_factor
                else:
                    processed[key] = value
            elif isinstance(value, list) and value and isinstance(value[0], (int, float)):
                # Quantize numerical arrays
                if isinstance(value[0], float):
                    quantization_factor = 1.0 / precision_loss
                    processed[key] = [round(v * quantization_factor) / quantization_factor for v in value]
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed
    
    def _reduce_data_variance(self, data: Dict[str, Any], variance_retention: float) -> Dict[str, Any]:
        """Reduce data variance while retaining key information"""
        
        processed = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 10:
                # Apply variance reduction to large arrays
                if all(isinstance(v, (int, float)) for v in value):
                    # Statistical compression - keep key statistics
                    arr = np.array(value)
                    mean_val = np.mean(arr)
                    std_val = np.std(arr)
                    
                    # Reduce outliers based on variance retention
                    threshold = std_val * (2.0 - variance_retention)
                    clipped = np.clip(arr, mean_val - threshold, mean_val + threshold)
                    processed[key] = clipped.tolist()
                else:
                    processed[key] = value
            else:
                processed[key] = value
        
        return processed
    
    def _aggressive_data_reduction(self, data: Dict[str, Any], variance_retention: float) -> Dict[str, Any]:
        """Apply aggressive data reduction"""
        
        processed = {}
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                # Truncate long strings
                processed[key] = value[:int(len(value) * variance_retention)]
            elif isinstance(value, list) and len(value) > 20:
                # Sample large arrays
                sample_size = max(10, int(len(value) * variance_retention))
                step = len(value) // sample_size
                processed[key] = value[::step][:sample_size]
            else:
                processed[key] = value
        
        return processed
    
    def _update_compression_stats(self, original_size: int, compressed_size: int, compression_time: float):
        """Update compression statistics"""
        
        self.compression_stats['total_compressed'] += 1
        self.compression_stats['total_original_size'] += original_size
        self.compression_stats['total_compressed_size'] += compressed_size
        self.compression_stats['compression_times'].append(compression_time)
        
        # Calculate average ratio
        if self.compression_stats['total_original_size'] > 0:
            self.compression_stats['average_ratio'] = (
                self.compression_stats['total_compressed_size'] / 
                self.compression_stats['total_original_size']
            )

class TradingDataCompressor(IntelligentCompressionEngine):
    """
    TRADING DATA COMPRESSION
    Optimized for financial time series and market data
    """
    
    def __init__(self):
        super().__init__()
        
        # Trading-specific compression strategies
        self.trading_strategies = {
            'critical_signals': CompressionStrategy.LOSSLESS,      # Trading signals - no loss allowed
            'market_data': CompressionStrategy.MINIMAL_LOSS,       # Price data - <0.1% loss
            'news_data': CompressionStrategy.MODERATE_LOSS,        # News - <5% loss acceptable
            'social_data': CompressionStrategy.AGGRESSIVE,         # Social data - higher compression
        }
        
        # Importance-based strategy mapping
        self.importance_strategies = {
            DataImportance.CRITICAL: {'type': 'lossless', 'algorithm': 'lz4'},
            DataImportance.HIGH: {'type': 'minimal_loss', 'precision_loss': 0.001},
            DataImportance.MEDIUM: {'type': 'moderate_loss', 'variance_retention': 0.98},
            DataImportance.LOW: {'type': 'aggressive', 'variance_retention': 0.85}
        }
        
        # Trading data type configurations
        self.data_type_configs = {
            'price_data': {'importance': DataImportance.HIGH, 'precision_critical': True},
            'volume_data': {'importance': DataImportance.HIGH, 'precision_critical': True},
            'order_book': {'importance': DataImportance.CRITICAL, 'precision_critical': True},
            'trading_signals': {'importance': DataImportance.CRITICAL, 'precision_critical': True},
            'technical_indicators': {'importance': DataImportance.HIGH, 'precision_critical': False},
            'news_data': {'importance': DataImportance.MEDIUM, 'precision_critical': False},
            'social_sentiment': {'importance': DataImportance.LOW, 'precision_critical': False},
            'market_analysis': {'importance': DataImportance.MEDIUM, 'precision_critical': False}
        }
        
        # Compression performance tracking
        self.trading_stats = {
            'data_types_compressed': {},
            'importance_levels': {},
            'compression_ratios_by_type': {},
            'data_integrity_scores': []
        }
        
        logger.info("🗜️ Trading Data Compressor initialized")
        logger.info(f"📊 Trading strategies: {len(self.trading_strategies)} configured")
        logger.info(f"🎯 Data type configs: {len(self.data_type_configs)} supported")
    
    async def compress_trading_data(self, 
                                  trading_data: Dict[str, Any],
                                  data_importance: Optional[DataImportance] = None) -> CompressionResult:
        """
        TRADING-OPTIMIZED COMPRESSION
        
        Strategy selection based on trading importance:
        - Critical: Trading signals, order data (lossless)
        - High: Price data, volume (minimal loss)
        - Medium: News, analysis (moderate loss)  
        - Low: Social sentiment, general market data (aggressive)
        """
        
        start_time = datetime.now()
        
        # Determine data importance if not provided
        if data_importance is None:
            data_importance = self._determine_data_importance(trading_data)
        
        logger.info(f"🗜️ Compressing trading data with importance: {data_importance.value}")
        
        # Get compression strategy
        strategy = self.importance_strategies[data_importance]
        
        # Apply trading-specific preprocessing
        preprocessed_data = await self._preprocess_trading_data(trading_data)
        
        # Compress with selected strategy
        compression_result = self.compress_data(preprocessed_data, strategy)
        
        # Calculate data integrity score
        data_integrity_score = await self._calculate_data_integrity(
            trading_data, preprocessed_data, strategy
        )
        
        # Create comprehensive result
        result = CompressionResult(
            compressed_data=compression_result['compressed_data'],
            original_size=compression_result['original_size'],
            compressed_size=compression_result['compressed_size'],
            compression_ratio=compression_result['compression_ratio'],
            algorithm=CompressionAlgorithm.LZ4 if strategy.get('algorithm') == 'lz4' else CompressionAlgorithm.GZIP,
            strategy=CompressionStrategy(strategy['type']),
            data_importance=data_importance,
            trading_metadata={
                'data_importance': data_importance.value,
                'market_timestamp': trading_data.get('timestamp'),
                'symbols': trading_data.get('symbols', []),
                'data_type': trading_data.get('data_type'),
                'preprocessing_applied': True,
                'compression_timestamp': datetime.now().isoformat()
            },
            compression_time=(datetime.now() - start_time).total_seconds(),
            data_integrity_score=data_integrity_score
        )
        
        # Update trading statistics
        await self._update_trading_stats(result)
        
        logger.info(f"[CHECK] Trading data compressed: {result.compression_ratio:.2f} ratio, {result.data_integrity_score:.2f} integrity")
        
        return result

    def _determine_data_importance(self, trading_data: Dict[str, Any]) -> DataImportance:
        """Determine data importance based on data type and content"""

        data_type = trading_data.get('data_type', 'unknown')

        # Check configured data types
        if data_type in self.data_type_configs:
            return self.data_type_configs[data_type]['importance']

        # Fallback logic based on content analysis
        if 'order' in data_type.lower() or 'signal' in data_type.lower():
            return DataImportance.CRITICAL
        elif 'price' in data_type.lower() or 'volume' in data_type.lower():
            return DataImportance.HIGH
        elif 'news' in data_type.lower() or 'analysis' in data_type.lower():
            return DataImportance.MEDIUM
        else:
            return DataImportance.LOW

    async def _preprocess_trading_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        TRADING-SPECIFIC PREPROCESSING
        Optimize data structure for trading use cases
        """

        # Separate high-frequency data from metadata
        hf_data = {}
        metadata = {}

        for key, value in data.items():
            if key in ['prices', 'volumes', 'timestamps', 'indicators', 'order_book', 'trades']:
                hf_data[key] = value
            else:
                metadata[key] = value

        # Optimize high-frequency data structure
        optimized_hf = await self._optimize_high_frequency_data(hf_data)

        return {
            'high_frequency': optimized_hf,
            'metadata': metadata,
            'structure_info': {
                'hf_fields': list(hf_data.keys()),
                'metadata_fields': list(metadata.keys()),
                'optimization_applied': True
            }
        }

    async def _optimize_high_frequency_data(self, hf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize high-frequency trading data"""

        optimized = {}

        for key, value in hf_data.items():
            if isinstance(value, list) and len(value) > 100:
                # Apply time-series specific optimizations
                if key in ['prices', 'volumes']:
                    # Delta encoding for price/volume data
                    optimized[key] = self._apply_delta_encoding(value)
                elif key == 'timestamps':
                    # Timestamp compression
                    optimized[key] = self._compress_timestamps(value)
                else:
                    optimized[key] = value
            else:
                optimized[key] = value

        return optimized

    def _apply_delta_encoding(self, values: List[float]) -> Dict[str, Any]:
        """Apply delta encoding to reduce data size"""

        if not values:
            return {'type': 'delta', 'base': 0, 'deltas': []}

        base_value = values[0]
        deltas = []

        for i in range(1, len(values)):
            delta = values[i] - values[i-1]
            deltas.append(delta)

        return {
            'type': 'delta',
            'base': base_value,
            'deltas': deltas,
            'original_length': len(values)
        }

    def _compress_timestamps(self, timestamps: List[Any]) -> Dict[str, Any]:
        """Compress timestamp data"""

        if not timestamps:
            return {'type': 'timestamp', 'base': 0, 'intervals': []}

        # Convert to seconds if needed
        if isinstance(timestamps[0], datetime):
            timestamp_seconds = [int(ts.timestamp()) for ts in timestamps]
        else:
            timestamp_seconds = timestamps

        base_time = timestamp_seconds[0]
        intervals = []

        for i in range(1, len(timestamp_seconds)):
            interval = timestamp_seconds[i] - timestamp_seconds[i-1]
            intervals.append(interval)

        return {
            'type': 'timestamp',
            'base': base_time,
            'intervals': intervals,
            'original_length': len(timestamps)
        }

    async def _calculate_data_integrity(self,
                                      original_data: Dict[str, Any],
                                      processed_data: Dict[str, Any],
                                      strategy: Dict[str, Any]) -> float:
        """Calculate data integrity score after compression"""

        if strategy['type'] == 'lossless':
            return 1.0  # Perfect integrity for lossless

        # Calculate integrity based on strategy type
        if strategy['type'] == 'minimal_loss':
            # High integrity for minimal loss
            precision_loss = strategy.get('precision_loss', 0.001)
            return max(0.99, 1.0 - precision_loss)
        elif strategy['type'] == 'moderate_loss':
            # Medium integrity for moderate loss
            variance_retention = strategy.get('variance_retention', 0.98)
            return max(0.95, variance_retention)
        else:  # aggressive
            # Lower integrity for aggressive compression
            variance_retention = strategy.get('variance_retention', 0.85)
            return max(0.80, variance_retention)

    async def _update_trading_stats(self, result: CompressionResult):
        """Update trading-specific compression statistics"""

        # Update data type stats
        data_type = result.trading_metadata.get('data_type', 'unknown')
        if data_type not in self.trading_stats['data_types_compressed']:
            self.trading_stats['data_types_compressed'][data_type] = 0
        self.trading_stats['data_types_compressed'][data_type] += 1

        # Update importance level stats
        importance = result.data_importance.value
        if importance not in self.trading_stats['importance_levels']:
            self.trading_stats['importance_levels'][importance] = 0
        self.trading_stats['importance_levels'][importance] += 1

        # Update compression ratios by type
        if data_type not in self.trading_stats['compression_ratios_by_type']:
            self.trading_stats['compression_ratios_by_type'][data_type] = []
        self.trading_stats['compression_ratios_by_type'][data_type].append(result.compression_ratio)

        # Update integrity scores
        self.trading_stats['data_integrity_scores'].append(result.data_integrity_score)

    async def decompress_trading_data(self, compressed_result: CompressionResult) -> Dict[str, Any]:
        """Decompress trading data"""

        start_time = datetime.now()

        try:
            # Decompress based on algorithm
            if compressed_result.algorithm == CompressionAlgorithm.LZ4:
                decompressed_bytes = zlib.decompress(compressed_result.compressed_data)
            elif compressed_result.algorithm == CompressionAlgorithm.GZIP:
                decompressed_bytes = gzip.decompress(compressed_result.compressed_data)
            else:  # ZLIB
                decompressed_bytes = zlib.decompress(compressed_result.compressed_data)

            # Deserialize data
            decompressed_data = pickle.loads(decompressed_bytes)

            # Apply post-processing if needed
            if compressed_result.trading_metadata.get('preprocessing_applied'):
                final_data = await self._postprocess_trading_data(decompressed_data)
            else:
                final_data = decompressed_data

            decompression_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"[CHECK] Trading data decompressed in {decompression_time:.3f}s")

            return final_data

        except Exception as e:
            logger.error(f"[ERROR] Decompression failed: {e}")
            raise

    async def _postprocess_trading_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process decompressed trading data"""

        if 'high_frequency' not in data:
            return data

        # Reconstruct high-frequency data
        hf_data = data['high_frequency']
        reconstructed_hf = {}

        for key, value in hf_data.items():
            if isinstance(value, dict) and value.get('type') == 'delta':
                # Reconstruct delta-encoded data
                reconstructed_hf[key] = self._reconstruct_delta_encoding(value)
            elif isinstance(value, dict) and value.get('type') == 'timestamp':
                # Reconstruct timestamp data
                reconstructed_hf[key] = self._reconstruct_timestamps(value)
            else:
                reconstructed_hf[key] = value

        # Merge back with metadata
        final_data = data['metadata'].copy()
        final_data.update(reconstructed_hf)

        return final_data

    def _reconstruct_delta_encoding(self, delta_data: Dict[str, Any]) -> List[float]:
        """Reconstruct delta-encoded data"""

        base_value = delta_data['base']
        deltas = delta_data['deltas']

        reconstructed = [base_value]
        current_value = base_value

        for delta in deltas:
            current_value += delta
            reconstructed.append(current_value)

        return reconstructed

    def _reconstruct_timestamps(self, timestamp_data: Dict[str, Any]) -> List[datetime]:
        """Reconstruct compressed timestamps"""

        base_time = timestamp_data['base']
        intervals = timestamp_data['intervals']

        reconstructed = [datetime.fromtimestamp(base_time)]
        current_time = base_time

        for interval in intervals:
            current_time += interval
            reconstructed.append(datetime.fromtimestamp(current_time))

        return reconstructed

    async def get_compression_report(self) -> Dict[str, Any]:
        """Generate comprehensive compression performance report"""

        # Calculate average compression ratios by data type
        avg_ratios_by_type = {}
        for data_type, ratios in self.trading_stats['compression_ratios_by_type'].items():
            avg_ratios_by_type[data_type] = sum(ratios) / len(ratios) if ratios else 0.0

        # Calculate average data integrity
        avg_integrity = (
            sum(self.trading_stats['data_integrity_scores']) /
            len(self.trading_stats['data_integrity_scores'])
            if self.trading_stats['data_integrity_scores'] else 0.0
        )

        # Calculate total space saved
        total_space_saved = (
            self.compression_stats['total_original_size'] -
            self.compression_stats['total_compressed_size']
        )

        space_saved_percentage = (
            (total_space_saved / self.compression_stats['total_original_size'] * 100)
            if self.compression_stats['total_original_size'] > 0 else 0.0
        )

        return {
            'compression_performance': {
                'total_files_compressed': self.compression_stats['total_compressed'],
                'total_original_size_mb': self.compression_stats['total_original_size'] / (1024 * 1024),
                'total_compressed_size_mb': self.compression_stats['total_compressed_size'] / (1024 * 1024),
                'average_compression_ratio': self.compression_stats['average_ratio'],
                'space_saved_mb': total_space_saved / (1024 * 1024),
                'space_saved_percentage': space_saved_percentage,
                'average_compression_time': (
                    sum(self.compression_stats['compression_times']) /
                    len(self.compression_stats['compression_times'])
                    if self.compression_stats['compression_times'] else 0.0
                )
            },
            'trading_specific_metrics': {
                'data_types_processed': self.trading_stats['data_types_compressed'],
                'importance_levels_distribution': self.trading_stats['importance_levels'],
                'average_compression_ratios_by_type': avg_ratios_by_type,
                'average_data_integrity': avg_integrity
            },
            'report_timestamp': datetime.now().isoformat(),
            'report_type': 'trading_data_compression'
        }


# Example usage and testing
async def test_trading_data_compressor():
    """Test the trading data compression system"""

    # Initialize compressor
    compressor = TradingDataCompressor()

    # Create test trading data
    test_data = {
        'data_type': 'price_data',
        'symbol': 'BTCUSD',
        'timestamp': datetime.now(),
        'prices': [45000.0 + i * 10.5 for i in range(1000)],  # Price series
        'volumes': [100.0 + i * 2.3 for i in range(1000)],   # Volume series
        'timestamps': [datetime.now() + timedelta(seconds=i) for i in range(1000)],
        'metadata': {
            'source': 'binance',
            'timeframe': '1m',
            'quality_score': 0.95
        }
    }

    # Test different importance levels
    importance_levels = [DataImportance.CRITICAL, DataImportance.HIGH, DataImportance.MEDIUM, DataImportance.LOW]

    for importance in importance_levels:
        print(f"\n🗜️ Testing compression with importance: {importance.value}")

        # Compress data
        result = await compressor.compress_trading_data(test_data, importance)

        print(f"📊 Original size: {result.original_size:,} bytes")
        print(f"📦 Compressed size: {result.compressed_size:,} bytes")
        print(f"🎯 Compression ratio: {result.compression_ratio:.3f}")
        print(f"[LIGHTNING] Compression time: {result.compression_time:.3f}s")
        print(f"🔒 Data integrity: {result.data_integrity_score:.3f}")
        print(f"🧠 Strategy: {result.strategy.value}")
        print(f"⚙️ Algorithm: {result.algorithm.value}")

        # Test decompression
        decompressed_data = await compressor.decompress_trading_data(result)
        print(f"[CHECK] Decompression successful: {len(decompressed_data)} fields recovered")

    # Generate compression report
    report = await compressor.get_compression_report()
    print(f"\n📈 Compression Report:")
    print(f"   Total files compressed: {report['compression_performance']['total_files_compressed']}")
    print(f"   Average compression ratio: {report['compression_performance']['average_compression_ratio']:.3f}")
    print(f"   Space saved: {report['compression_performance']['space_saved_percentage']:.1f}%")
    print(f"   Average data integrity: {report['trading_specific_metrics']['average_data_integrity']:.3f}")


if __name__ == "__main__":
    asyncio.run(test_trading_data_compressor())
