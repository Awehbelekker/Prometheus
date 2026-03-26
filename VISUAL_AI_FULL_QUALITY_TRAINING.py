"""
PROMETHEUS Visual AI - FULL QUALITY Training
=============================================
Maximum quality for best training data:
- Full resolution images
- Complete pattern detection prompts
- Extended timeout (5 minutes)
- Detailed analysis with support/resistance
- All pattern categories detected
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_file = f"visual_ai_full_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def run_full_quality_training():
    """Run full quality Visual AI training"""
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("PROMETHEUS VISUAL AI - FULL QUALITY TRAINING")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Quality Settings:")
    logger.info("  - Full resolution images (no resize)")
    logger.info("  - Complete pattern detection prompts")
    logger.info("  - 5 minute timeout per chart")
    logger.info("  - All pattern categories analyzed")
    logger.info("")
    
    # Initialize the full multimodal analyzer
    try:
        from core.multimodal_analyzer import MultimodalChartAnalyzer, MultimodalConfig
        
        # Full quality config
        config = MultimodalConfig(
            model="llava:7b",
            endpoint="http://localhost:11434",
            temperature=0.3,
            max_tokens=2048,
            timeout=300,  # 5 minutes
            min_confidence=0.5
        )
        
        analyzer = MultimodalChartAnalyzer(config)
        logger.info("Full quality analyzer initialized!")
        logger.info(f"  Model: {config.model}")
        logger.info(f"  Timeout: {config.timeout}s (5 minutes)")
        logger.info(f"  Max tokens: {config.max_tokens}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Find all charts
    charts_dir = Path("charts")
    if not charts_dir.exists():
        logger.error("Charts directory not found!")
        return
    
    all_charts = sorted(list(charts_dir.glob("*.png")))
    logger.info(f"Total charts available: {len(all_charts)}")
    
    # Load existing results (only keep high-quality ones)
    results_file = Path("visual_ai_patterns.json")
    existing_results = {}
    
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
                for name, result in data.get('patterns', {}).items():
                    # Only keep results that have actual patterns or high confidence
                    if (len(result.get('patterns', [])) > 0 or 
                        result.get('confidence', 0) >= 0.6):
                        existing_results[name] = result
            logger.info(f"Existing quality results: {len(existing_results)}")
        except Exception as e:
            logger.warning(f"Could not load existing results: {e}")
    
    # Filter to unprocessed charts
    charts_to_process = [c for c in all_charts if c.name not in existing_results]
    logger.info(f"Charts to process: {len(charts_to_process)}")
    logger.info("")
    
    if not charts_to_process:
        logger.info("All charts already processed with quality results!")
        return
    
    # Estimate time
    est_time = len(charts_to_process) * 2  # Assume 2 min average
    logger.info(f"Estimated time: {est_time // 60} hours {est_time % 60} minutes")
    logger.info("(Press Ctrl+C to stop - progress is saved)")
    logger.info("")
    logger.info("=" * 70)
    logger.info("STARTING FULL QUALITY ANALYSIS")
    logger.info("=" * 70)
    logger.info("")
    
    # Process charts
    results = existing_results.copy()
    start_time = time.time()
    success_count = 0
    pattern_count = 0
    error_count = 0
    
    for i, chart_path in enumerate(charts_to_process, 1):
        try:
            # Extract symbol from filename
            symbol = chart_path.stem.split('_')[0]
            
            logger.info(f"[{i}/{len(charts_to_process)}] {chart_path.name}")
            logger.info(f"  Symbol: {symbol}")
            
            # Full quality analysis
            analysis_start = time.time()
            context = {'symbol': symbol}
            result = analyzer.analyze_chart(str(chart_path), context)
            analysis_time = time.time() - analysis_start
            
            # Process result
            if result:
                patterns = result.patterns_detected if hasattr(result, 'patterns_detected') else []
                trend = result.trend if hasattr(result, 'trend') else 'neutral'
                trend_strength = result.trend_strength if hasattr(result, 'trend_strength') else 'weak'
                confidence = result.confidence if hasattr(result, 'confidence') else 0.5
                support = result.support_levels if hasattr(result, 'support_levels') else []
                resistance = result.resistance_levels if hasattr(result, 'resistance_levels') else []
                
                results[chart_path.name] = {
                    'patterns': patterns,
                    'trend': trend,
                    'trend_strength': trend_strength,
                    'support': support,
                    'resistance': resistance,
                    'confidence': confidence,
                    'analyzed_at': datetime.now().isoformat(),
                    'analysis_time': round(analysis_time, 1)
                }
                
                success_count += 1
                pattern_count += len(patterns)
                
                # Log results
                logger.info(f"  [OK] {analysis_time:.1f}s")
                logger.info(f"  Trend: {trend} ({trend_strength})")
                if patterns:
                    logger.info(f"  Patterns: {patterns}")
                logger.info(f"  Confidence: {confidence:.0%}")
                if support:
                    logger.info(f"  Support: {support[:3]}")
                if resistance:
                    logger.info(f"  Resistance: {resistance[:3]}")
            else:
                error_count += 1
                results[chart_path.name] = {
                    'patterns': [],
                    'trend': 'neutral',
                    'trend_strength': 'weak',
                    'support': [],
                    'resistance': [],
                    'confidence': 0.0,
                    'analyzed_at': datetime.now().isoformat(),
                    'error': 'No result returned'
                }
                logger.warning(f"  [WARN] No result ({analysis_time:.1f}s)")
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("Training interrupted by user!")
            break
            
        except Exception as e:
            error_count += 1
            error_msg = str(e)[:100]
            
            results[chart_path.name] = {
                'patterns': [],
                'trend': 'neutral',
                'trend_strength': 'weak',
                'support': [],
                'resistance': [],
                'confidence': 0.0,
                'analyzed_at': datetime.now().isoformat(),
                'error': error_msg
            }
            
            if 'timeout' in error_msg.lower():
                logger.error(f"  [TIMEOUT] {analysis_time:.1f}s")
            else:
                logger.error(f"  [ERROR] {error_msg}")
        
        # Save progress every 5 charts
        if i % 5 == 0:
            save_results(results, pattern_count)
            
            # Progress stats
            elapsed = time.time() - start_time
            rate = i / (elapsed / 60) if elapsed > 0 else 0
            remaining = len(charts_to_process) - i
            eta = remaining / rate if rate > 0 else 0
            
            logger.info("")
            logger.info(f"  === Progress: {i}/{len(charts_to_process)} ({i/len(charts_to_process)*100:.1f}%) ===")
            logger.info(f"  Success: {success_count} | Errors: {error_count} | Patterns: {pattern_count}")
            logger.info(f"  Rate: {rate:.1f} charts/min | ETA: {eta:.0f} min")
            logger.info("")
    
    # Final save
    save_results(results, pattern_count)
    
    # Summary
    elapsed = time.time() - start_time
    logger.info("")
    logger.info("=" * 70)
    logger.info("FULL QUALITY TRAINING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Charts processed: {i}")
    logger.info(f"Successful: {success_count} ({success_count/i*100:.1f}%)")
    logger.info(f"Errors: {error_count}")
    logger.info(f"Patterns detected: {pattern_count}")
    logger.info(f"Time elapsed: {elapsed/60:.1f} minutes")
    logger.info(f"Results saved to: visual_ai_patterns.json")
    logger.info(f"Log saved to: {log_file}")
    logger.info("=" * 70)


def save_results(results, total_patterns):
    """Save results to JSON file"""
    
    # Build pattern summary
    pattern_summary = {}
    for data in results.values():
        for pattern in data.get('patterns', []):
            pattern_name = pattern if isinstance(pattern, str) else str(pattern)
            pattern_summary[pattern_name] = pattern_summary.get(pattern_name, 0) + 1
    
    output = {
        'last_updated': datetime.now().isoformat(),
        'total_analyzed': len(results),
        'total_patterns': total_patterns,
        'patterns': results,
        'pattern_summary': pattern_summary
    }
    
    with open('visual_ai_patterns.json', 'w') as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("PROMETHEUS VISUAL AI - FULL QUALITY TRAINING")
    print("=" * 70)
    print("")
    print("This will run FULL QUALITY analysis:")
    print("  - Full resolution images")
    print("  - Complete pattern detection")
    print("  - 5 minute timeout per chart")
    print("  - Support/Resistance levels")
    print("")
    print("Expected time: 2-4 hours for ~1300 charts")
    print("Progress is saved every 5 charts")
    print("")
    print("Press Ctrl+C to stop anytime (progress is saved)")
    print("")
    print("Starting in 5 seconds...")
    time.sleep(5)
    
    try:
        run_full_quality_training()
    except KeyboardInterrupt:
        print("\n\nTraining stopped by user. Progress saved!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
