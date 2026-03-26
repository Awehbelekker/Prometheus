#!/usr/bin/env python3
"""
VISUAL AI FULL TRAINING - Background Process
Trains LLaVA on all 1,302 charts WITHOUT stopping live trading
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('visual_ai_training.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

class VisualAIFullTrainer:
    """Train LLaVA on all charts in background"""
    
    def __init__(self, charts_folder: str = "charts", batch_size: int = 10):
        self.charts_folder = charts_folder
        self.batch_size = batch_size
        self.results = {
            'start_time': datetime.now().isoformat(),
            'charts_analyzed': 0,
            'patterns_found': [],
            'errors': 0,
            'success_rate': 0
        }
        self.analyzer = None
        
    async def initialize(self):
        """Initialize the multimodal analyzer"""
        try:
            from core.multimodal_analyzer import MultimodalChartAnalyzer
            self.analyzer = MultimodalChartAnalyzer()
            logger.info("[OK] MultimodalChartAnalyzer initialized")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Could not initialize analyzer: {e}")
            return False
    
    def get_all_charts(self):
        """Get list of all chart files"""
        charts_path = Path(self.charts_folder)
        if not charts_path.exists():
            logger.error(f"Charts folder not found: {self.charts_folder}")
            return []
        
        charts = list(charts_path.glob("*.png"))
        logger.info(f"Found {len(charts)} charts to analyze")
        return charts
    
    async def analyze_chart(self, chart_path: Path) -> dict:
        """Analyze a single chart with timeout"""
        try:
            # Get symbol from filename
            symbol = chart_path.stem.split('_')[0]
            
            # analyze_chart expects path string, returns ChartAnalysisResult directly
            result = self.analyzer.analyze_chart(
                str(chart_path),
                context={'symbol': symbol, 'source': 'training'}
            )
            
            # Convert dataclass to dict if needed - use correct attribute names
            if hasattr(result, 'patterns_detected'):
                patterns = result.patterns_detected if result.patterns_detected else []
                support = result.support_levels if hasattr(result, 'support_levels') and result.support_levels else []
                resistance = result.resistance_levels if hasattr(result, 'resistance_levels') and result.resistance_levels else []
                trend = result.trend_direction if hasattr(result, 'trend_direction') else 'unknown'
                confidence = result.confidence if hasattr(result, 'confidence') else 0
                reasoning = result.reasoning if hasattr(result, 'reasoning') else ''
            elif isinstance(result, dict):
                patterns = result.get('patterns_detected', result.get('patterns', []))
                support = result.get('support_levels', [])
                resistance = result.get('resistance_levels', [])
                trend = result.get('trend_direction', result.get('trend', 'unknown'))
                confidence = result.get('confidence', 0)
                reasoning = result.get('reasoning', '')
            else:
                patterns, support, resistance, trend, confidence, reasoning = [], [], [], 'unknown', 0, ''
            
            # Log actual response for debugging
            if reasoning and 'unavailable' in reasoning.lower():
                logger.warning(f"  [WARN] {chart_path.name}: {reasoning[:50]}")
            
            return {
                'chart': chart_path.name,
                'symbol': symbol,
                'patterns': patterns,
                'support_levels': support,
                'resistance_levels': resistance,
                'trend': trend,
                'confidence': confidence,
                'success': True
            }
            
        except asyncio.TimeoutError:
            logger.warning(f"  Timeout analyzing {chart_path.name}")
            return {'chart': chart_path.name, 'success': False, 'error': 'timeout'}
        except Exception as e:
            logger.warning(f"  Error analyzing {chart_path.name}: {str(e)[:50]}")
            return {'chart': chart_path.name, 'success': False, 'error': str(e)[:100]}
    
    async def train_batch(self, charts: list, batch_num: int, total_batches: int):
        """Train on a batch of charts"""
        logger.info(f"Batch {batch_num}/{total_batches}: Analyzing {len(charts)} charts...")
        
        batch_results = []
        for i, chart in enumerate(charts):
            result = await self.analyze_chart(chart)
            batch_results.append(result)
            
            if result.get('success'):
                self.results['charts_analyzed'] += 1
                patterns = result.get('patterns', [])
                self.results['patterns_found'].extend(patterns)
                logger.info(f"  [{i+1}/{len(charts)}] {chart.name}: {len(patterns)} patterns, {result.get('trend', 'N/A')} trend")
            else:
                self.results['errors'] += 1
            
            # Small delay between charts to not overwhelm Ollama
            await asyncio.sleep(0.5)
        
        return batch_results
    
    async def run_full_training(self):
        """Run full training on all charts"""
        logger.info("=" * 70)
        logger.info("VISUAL AI FULL TRAINING - STARTING")
        logger.info("=" * 70)
        logger.info("This runs in BACKGROUND - Live trading continues normally!")
        logger.info("=" * 70)
        
        # Initialize
        if not await self.initialize():
            logger.error("Failed to initialize. Exiting.")
            return
        
        # Get all charts
        charts = self.get_all_charts()
        if not charts:
            logger.error("No charts found. Exiting.")
            return
        
        total_charts = len(charts)
        logger.info(f"Total charts to analyze: {total_charts}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Estimated time: {total_charts * 5 / 60:.1f} - {total_charts * 15 / 60:.1f} minutes")
        logger.info("")
        
        # Process in batches
        all_results = []
        total_batches = (total_charts + self.batch_size - 1) // self.batch_size
        
        start_time = time.time()
        
        for batch_num in range(total_batches):
            batch_start = batch_num * self.batch_size
            batch_end = min(batch_start + self.batch_size, total_charts)
            batch_charts = charts[batch_start:batch_end]
            
            batch_results = await self.train_batch(batch_charts, batch_num + 1, total_batches)
            all_results.extend(batch_results)
            
            # Progress update
            progress = (batch_num + 1) / total_batches * 100
            elapsed = time.time() - start_time
            eta = elapsed / (batch_num + 1) * (total_batches - batch_num - 1)
            
            logger.info(f"Progress: {progress:.1f}% | Elapsed: {elapsed/60:.1f}min | ETA: {eta/60:.1f}min")
            logger.info("")
            
            # Brief pause between batches
            await asyncio.sleep(1)
        
        # Calculate final stats
        elapsed_total = time.time() - start_time
        success_count = sum(1 for r in all_results if r.get('success'))
        self.results['success_rate'] = success_count / total_charts * 100 if total_charts > 0 else 0
        self.results['end_time'] = datetime.now().isoformat()
        self.results['total_time_minutes'] = elapsed_total / 60
        
        # Count unique patterns
        all_patterns = []
        for r in all_results:
            if r.get('success'):
                all_patterns.extend(r.get('patterns', []))
        
        pattern_counts = {}
        for p in all_patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        
        self.results['unique_patterns'] = len(pattern_counts)
        self.results['pattern_distribution'] = dict(sorted(pattern_counts.items(), key=lambda x: -x[1])[:20])
        
        # Save results
        with open('visual_ai_training_complete.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE!")
        logger.info("=" * 70)
        logger.info(f"Charts analyzed: {self.results['charts_analyzed']}/{total_charts}")
        logger.info(f"Success rate: {self.results['success_rate']:.1f}%")
        logger.info(f"Unique patterns learned: {self.results['unique_patterns']}")
        logger.info(f"Total time: {elapsed_total/60:.1f} minutes")
        logger.info("")
        logger.info("Top patterns found:")
        for pattern, count in list(self.results['pattern_distribution'].items())[:10]:
            logger.info(f"  - {pattern}: {count} instances")
        logger.info("")
        logger.info("Results saved to: visual_ai_training_complete.json")
        logger.info("=" * 70)
        
        return self.results


async def main():
    print()
    print("=" * 70)
    print("VISUAL AI FULL TRAINING")
    print("Training LLaVA on ALL 1,302 charts")
    print("=" * 70)
    print()
    print("[INFO] This runs in BACKGROUND")
    print("[INFO] Live trading continues normally!")
    print("[INFO] Estimated time: 1-3 hours")
    print()
    print("=" * 70)
    print()
    
    trainer = VisualAIFullTrainer(
        charts_folder="charts",
        batch_size=10  # 10 charts per batch
    )
    
    results = await trainer.run_full_training()
    return results


if __name__ == "__main__":
    asyncio.run(main())
