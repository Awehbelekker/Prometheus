#!/usr/bin/env python3
"""
PROMETHEUS Model Pre-Training Runner
=====================================
Executes the complete model pre-training pipeline.

Usage:
    python run_model_pretraining.py
"""

import asyncio
import logging
from datetime import datetime, timedelta
from core.model_pretraining_system import get_pretraining_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run the complete pre-training pipeline"""
    
    logger.info("="*80)
    logger.info("PROMETHEUS MODEL PRE-TRAINING")
    logger.info("="*80)
    
    # Initialize system
    system = get_pretraining_system()
    
    # Define training parameters
    symbols = [
        # Major indices
        'SPY', 'QQQ', 'DIA', 'IWM',
        # Tech giants
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        # Other major stocks
        'JPM', 'BAC', 'WMT', 'JNJ', 'V', 'MA',
        # Crypto (if available)
        'BTC-USD', 'ETH-USD'
    ]
    
    start_date = datetime.now() - timedelta(days=365*5)  # 5 years
    end_date = datetime.now()
    
    logger.info(f"\nTraining Configuration:")
    logger.info(f"  Symbols: {len(symbols)}")
    logger.info(f"  Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"  Duration: 5 years")
    
    # Pre-train all models
    report = await system.pretrain_all_models(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    # Print report
    print("\n" + "="*80)
    print("MODEL PRE-TRAINING REPORT")
    print("="*80)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Models Trained: {report['total_models']}")
    print(f"\nModels by Type:")
    for model_type, count in report['models_by_type'].items():
        print(f"  {model_type}: {count}")
    
    print(f"\nAverage Performance:")
    for metric, value in report['average_performance'].items():
        print(f"  {metric}: {value:.3f}")
    
    print("\n" + "="*80)
    print("[CHECK] PRE-TRAINING COMPLETE!")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review performance metrics in pretrained_models/performance_metrics.json")
    print("2. Models are automatically integrated with AI Learning Engine")
    print("3. Start trading system to use pre-trained models")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

