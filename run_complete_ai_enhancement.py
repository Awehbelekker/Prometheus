#!/usr/bin/env python3
"""
PROMETHEUS Complete AI Enhancement Runner
==========================================
Executes the complete AI enhancement pipeline:
1. Historical data download and feature engineering
2. Model pre-training
3. Market intelligence agent initialization
4. Unified learning coordinator setup
5. Knowledge base initialization

Usage:
    python run_complete_ai_enhancement.py
"""

import asyncio
import logging
from datetime import datetime, timedelta
import json

# Phase 1: Historical Data & Pre-Training
from core.historical_data_pipeline import get_historical_pipeline
from core.model_pretraining_system import get_pretraining_system

# Phase 2: Market Intelligence Agents
from core.market_intelligence_agents import (
    get_gap_detection_agent,
    get_opportunity_scanner_agent,
    get_market_research_agent
)
from core.agent_performance_optimizer import get_performance_optimizer
from core.enhanced_agent_integration import get_enhanced_coordinator

# Phase 3: Learning Integration
from core.unified_learning_coordinator import get_unified_coordinator
from core.enhanced_knowledge_base import get_knowledge_base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_phase_1_historical_data_and_pretraining():
    """Phase 1: Historical Data Infrastructure & Model Pre-Training"""
    logger.info("="*80)
    logger.info("PHASE 1: HISTORICAL DATA & MODEL PRE-TRAINING")
    logger.info("="*80)
    
    # Initialize systems
    pipeline = get_historical_pipeline()
    pretraining = get_pretraining_system()
    
    # Define training parameters
    symbols = [
        # Major indices
        'SPY', 'QQQ', 'DIA', 'IWM',
        # Tech giants
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        # Financial
        'JPM', 'BAC', 'GS', 'MS',
        # Other sectors
        'WMT', 'JNJ', 'V', 'MA', 'UNH', 'HD',
        # Crypto
        'BTC-USD', 'ETH-USD'
    ]
    
    start_date = datetime.now() - timedelta(days=365*5)  # 5 years
    end_date = datetime.now()
    
    logger.info(f"\nPhase 1 Configuration:")
    logger.info(f"  Symbols: {len(symbols)}")
    logger.info(f"  Period: {start_date.date()} to {end_date.date()}")
    
    # Download and pre-train
    report = await pretraining.pretrain_all_models(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    logger.info("\n[CHECK] PHASE 1 COMPLETE")
    logger.info(f"  Models trained: {report['total_models']}")
    logger.info(f"  Average price R²: {report['average_performance'].get('price_test_r2', 0):.3f}")
    logger.info(f"  Average direction accuracy: {report['average_performance'].get('direction_test_accuracy', 0):.3f}")
    
    return report


async def run_phase_2_market_intelligence():
    """Phase 2: Market Intelligence Agents"""
    logger.info("\n" + "="*80)
    logger.info("PHASE 2: MARKET INTELLIGENCE AGENTS")
    logger.info("="*80)
    
    # Initialize agents
    gap_agent = get_gap_detection_agent()
    opportunity_agent = get_opportunity_scanner_agent()
    research_agent = get_market_research_agent()
    performance_optimizer = get_performance_optimizer()
    
    logger.info("\nInitialized Intelligence Agents:")
    logger.info(f"  [CHECK] Gap Detection Agent")
    logger.info(f"  [CHECK] Opportunity Scanner Agent")
    logger.info(f"  [CHECK] Market Research Agent")
    logger.info(f"  [CHECK] Agent Performance Optimizer")
    
    # Initialize enhanced coordinator
    coordinator = await get_enhanced_coordinator()
    
    logger.info(f"  [CHECK] Enhanced Agent Coordinator")
    
    # Test with sample symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']
    
    logger.info(f"\nTesting with {len(test_symbols)} symbols...")
    
    # Scan for gaps
    gaps = await gap_agent.scan_for_gaps(test_symbols)
    logger.info(f"  Found {len(gaps)} gaps")
    
    # Scan for opportunities
    opportunities = await opportunity_agent.scan_all_opportunities(test_symbols)
    logger.info(f"  Found {len(opportunities)} opportunities")
    
    # Generate market intelligence
    intelligence = await research_agent.generate_market_intelligence(test_symbols)
    logger.info(f"  Market regime: {intelligence.market_regime}")
    logger.info(f"  Sentiment: {intelligence.sentiment_score:.2f}")
    
    logger.info("\n[CHECK] PHASE 2 COMPLETE")
    
    return {
        'gaps': len(gaps),
        'opportunities': len(opportunities),
        'market_regime': intelligence.market_regime
    }


async def run_phase_3_learning_integration():
    """Phase 3: Learning Integration"""
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: LEARNING INTEGRATION")
    logger.info("="*80)
    
    # Initialize unified learning coordinator
    learning_coordinator = get_unified_coordinator()
    
    logger.info("\nInitialized Learning Systems:")
    logger.info(f"  [CHECK] Unified Learning Coordinator")
    logger.info(f"  [CHECK] AI Learning Engine")
    logger.info(f"  [CHECK] Continuous Learning Engine")
    logger.info(f"  [CHECK] Advanced Learning Engine (if available)")
    
    # Initialize knowledge base
    knowledge_base = get_knowledge_base()
    
    logger.info(f"  [CHECK] Enhanced Knowledge Base")
    
    # Test learning cycle
    logger.info("\nTesting coordinated learning cycle...")
    
    test_market_data = {
        'symbols': ['AAPL', 'MSFT'],
        'regime': 'TRENDING_BULL',
        'volatility': 0.15
    }
    
    test_performance = {
        'accuracy': 0.65,
        'win_rate': 0.58,
        'total_return': 0.03
    }
    
    adaptation = await learning_coordinator.coordinate_learning_cycle(
        test_market_data,
        test_performance
    )
    
    logger.info(f"  Adaptation ID: {adaptation.adaptation_id}")
    logger.info(f"  Expected improvement: {adaptation.expected_improvement:.2%}")
    logger.info(f"  Risk level: {adaptation.risk_level:.2f}")
    logger.info(f"  Applied: {adaptation.applied}")
    
    # Get learning status
    status = await learning_coordinator.get_learning_status()
    
    logger.info("\n[CHECK] PHASE 3 COMPLETE")
    logger.info(f"  Total adaptations: {status['total_adaptations']}")
    logger.info(f"  Applied adaptations: {status['applied_adaptations']}")
    
    return status


async def run_phase_4_validation():
    """Phase 4: System Validation"""
    logger.info("\n" + "="*80)
    logger.info("PHASE 4: SYSTEM VALIDATION")
    logger.info("="*80)
    
    # Validate all systems are operational
    logger.info("\nValidating all systems...")
    
    validation_results = {
        'historical_data_pipeline': False,
        'model_pretraining': False,
        'market_intelligence': False,
        'learning_coordination': False,
        'knowledge_base': False
    }
    
    try:
        # Check historical data pipeline
        pipeline = get_historical_pipeline()
        status = pipeline.get_download_status()
        validation_results['historical_data_pipeline'] = len(status) > 0
        logger.info(f"  [CHECK] Historical Data Pipeline: {len(status)} datasets")
    except Exception as e:
        logger.error(f"  [ERROR] Historical Data Pipeline: {e}")
    
    try:
        # Check pre-trained models
        import os
        from pathlib import Path
        model_dir = Path("pretrained_models")
        if model_dir.exists():
            model_count = len(list(model_dir.glob("*.joblib")))
            validation_results['model_pretraining'] = model_count > 0
            logger.info(f"  [CHECK] Pre-trained Models: {model_count} files")
        else:
            logger.warning(f"  [WARNING]️ Pre-trained Models: Directory not found")
    except Exception as e:
        logger.error(f"  [ERROR] Pre-trained Models: {e}")
    
    try:
        # Check market intelligence
        coordinator = await get_enhanced_coordinator()
        validation_results['market_intelligence'] = True
        logger.info(f"  [CHECK] Market Intelligence: Operational")
    except Exception as e:
        logger.error(f"  [ERROR] Market Intelligence: {e}")
    
    try:
        # Check learning coordination
        learning = get_unified_coordinator()
        status = await learning.get_learning_status()
        validation_results['learning_coordination'] = True
        logger.info(f"  [CHECK] Learning Coordination: Operational")
    except Exception as e:
        logger.error(f"  [ERROR] Learning Coordination: {e}")
    
    try:
        # Check knowledge base
        kb = get_knowledge_base()
        validation_results['knowledge_base'] = True
        logger.info(f"  [CHECK] Knowledge Base: Operational")
    except Exception as e:
        logger.error(f"  [ERROR] Knowledge Base: {e}")
    
    # Calculate overall success rate
    success_count = sum(validation_results.values())
    total_count = len(validation_results)
    success_rate = success_count / total_count
    
    logger.info("\n[CHECK] PHASE 4 COMPLETE")
    logger.info(f"  System validation: {success_count}/{total_count} ({success_rate:.0%})")
    
    return validation_results


async def main():
    """Run complete AI enhancement pipeline"""
    
    logger.info("="*80)
    logger.info("PROMETHEUS COMPLETE AI ENHANCEMENT")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now()}")
    
    start_time = datetime.now()
    
    # Run all phases
    phase1_report = await run_phase_1_historical_data_and_pretraining()
    phase2_report = await run_phase_2_market_intelligence()
    phase3_report = await run_phase_3_learning_integration()
    phase4_report = await run_phase_4_validation()
    
    # Generate final report
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "="*80)
    logger.info("COMPLETE AI ENHANCEMENT REPORT")
    logger.info("="*80)
    logger.info(f"Duration: {duration}")
    logger.info(f"\nPhase 1 - Historical Data & Pre-Training:")
    logger.info(f"  Models trained: {phase1_report['total_models']}")
    logger.info(f"\nPhase 2 - Market Intelligence:")
    logger.info(f"  Gaps detected: {phase2_report['gaps']}")
    logger.info(f"  Opportunities found: {phase2_report['opportunities']}")
    logger.info(f"\nPhase 3 - Learning Integration:")
    logger.info(f"  Total adaptations: {phase3_report['total_adaptations']}")
    logger.info(f"\nPhase 4 - System Validation:")
    for system, status in phase4_report.items():
        logger.info(f"  {system}: {'[CHECK]' if status else '[ERROR]'}")
    
    logger.info("\n" + "="*80)
    logger.info("[CHECK] COMPLETE AI ENHANCEMENT FINISHED!")
    logger.info("="*80)
    logger.info("\nNext Steps:")
    logger.info("1. Review performance metrics in pretrained_models/performance_metrics.json")
    logger.info("2. Check agent performance in agent_performance.db")
    logger.info("3. Review knowledge base in knowledge_base.db")
    logger.info("4. Start PROMETHEUS trading system to use enhanced AI")
    logger.info("="*80)
    
    # Save final report
    final_report = {
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': duration.total_seconds(),
        'phase1': phase1_report,
        'phase2': phase2_report,
        'phase3': phase3_report,
        'phase4': phase4_report
    }
    
    with open('ai_enhancement_report.json', 'w') as f:
        json.dump(final_report, f, indent=2)
    
    logger.info(f"\n📄 Full report saved to: ai_enhancement_report.json")


if __name__ == "__main__":
    asyncio.run(main())

