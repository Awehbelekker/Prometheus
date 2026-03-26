"""
PROMETHEUS Visual AI - Dedicated Training Session
==================================================
Maximum resources, longer timeout, process all charts
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Set high priority for this process
try:
    import psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    print("Set process to HIGH PRIORITY")
except:
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visual_ai_dedicated.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

def run_dedicated_training():
    """Run Visual AI training with maximum resources"""
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("PROMETHEUS VISUAL AI - DEDICATED TRAINING SESSION")
    logger.info("=" * 70)
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Mode: Maximum resources, extended timeout")
    logger.info("")
    
    # Find charts
    charts_dir = Path("charts")
    if not charts_dir.exists():
        logger.error("Charts directory not found!")
        return
    
    all_charts = list(charts_dir.glob("*.png"))
    logger.info(f"Total charts available: {len(all_charts)}")
    
    # Load existing results to skip already processed
    results_file = Path("visual_ai_patterns.json")
    existing_results = {}
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
                existing_results = data.get('patterns', {})
                logger.info(f"Already processed: {len(existing_results)} charts")
        except:
            pass
    
    # Filter to unprocessed charts
    charts_to_process = [c for c in all_charts if c.name not in existing_results]
    logger.info(f"Charts to process: {len(charts_to_process)}")
    logger.info("")
    
    if not charts_to_process:
        logger.info("All charts already processed!")
        return
    
    # Initialize analyzer with extended timeout
    try:
        from core.multimodal_analyzer import MultimodalChartAnalyzer, MultimodalConfig
        
        # Extended timeout for dedicated training
        config = MultimodalConfig(
            endpoint="http://localhost:11434",
            model="llava:7b",
            max_tokens=2048,
            timeout=300  # 5 minutes timeout!
        )
        
        analyzer = MultimodalChartAnalyzer(config)
        logger.info("Visual AI analyzer initialized with 300s timeout")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        return
    
    # Process charts
    results = existing_results.copy()
    total_patterns = sum(len(r.get('patterns', [])) for r in results.values())
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i, chart_path in enumerate(charts_to_process, 1):
        try:
            # Extract symbol
            symbol = chart_path.stem.split('_')[0]
            
            logger.info(f"[{i}/{len(charts_to_process)}] Analyzing: {chart_path.name}")
            logger.info(f"  Symbol: {symbol} (timeout: 300s)")
            
            # Analyze - pass symbol as context dict
            analysis_start = time.time()
            context = {'symbol': symbol}
            result = analyzer.analyze_chart(str(chart_path), context)
            analysis_time = time.time() - analysis_start
            
            # Store result
            if result:
                patterns_found = result.patterns_detected if hasattr(result, 'patterns_detected') else []
                trend = result.trend if hasattr(result, 'trend') else 'neutral'
                confidence = result.confidence if hasattr(result, 'confidence') else 0.5
                
                results[chart_path.name] = {
                    'patterns': patterns_found,
                    'trend': trend,
                    'trend_strength': getattr(result, 'trend_strength', 'weak'),
                    'support': getattr(result, 'support_levels', []),
                    'resistance': getattr(result, 'resistance_levels', []),
                    'confidence': confidence,
                    'analyzed_at': datetime.now().isoformat()
                }
                
                success_count += 1
                total_patterns += len(patterns_found)
                
                logger.info(f"  [OK] {len(patterns_found)} patterns, trend={trend}, conf={confidence:.2f}, {analysis_time:.1f}s")
                
                if patterns_found:
                    for p in patterns_found[:3]:
                        logger.info(f"    - {p}")
            else:
                results[chart_path.name] = {
                    'patterns': [],
                    'trend': 'neutral',
                    'trend_strength': 'weak',
                    'support': [],
                    'resistance': [],
                    'confidence': 0.0,
                    'analyzed_at': datetime.now().isoformat()
                }
                error_count += 1
                logger.warning(f"  [WARN] No result returned")
                
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            if 'timeout' in error_msg.lower():
                logger.error(f"  [TIMEOUT] Still too slow even with 300s timeout")
            else:
                logger.error(f"  [ERROR] {error_msg[:100]}")
            
            results[chart_path.name] = {
                'patterns': [],
                'trend': 'neutral',
                'trend_strength': 'weak',
                'support': [],
                'resistance': [],
                'confidence': 0.0,
                'analyzed_at': datetime.now().isoformat()
            }
        
        # Save every 5 charts
        if i % 5 == 0:
            save_results(results, total_patterns)
            elapsed = time.time() - start_time
            rate = i / (elapsed / 60) if elapsed > 0 else 0
            logger.info(f"  Progress: {i} analyzed, {success_count} success, {error_count} errors, {rate:.1f} charts/min")
            logger.info("")
    
    # Final save
    save_results(results, total_patterns)
    
    elapsed = time.time() - start_time
    logger.info("")
    logger.info("=" * 70)
    logger.info("DEDICATED TRAINING SESSION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Charts processed: {len(charts_to_process)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Errors/Timeouts: {error_count}")
    logger.info(f"Total patterns found: {total_patterns}")
    logger.info(f"Time elapsed: {elapsed/60:.1f} minutes")
    logger.info(f"Success rate: {success_count/len(charts_to_process)*100:.1f}%")
    logger.info("=" * 70)


def save_results(results, total_patterns):
    """Save results to JSON"""
    # Build pattern summary
    pattern_summary = {}
    for chart_name, data in results.items():
        for pattern in data.get('patterns', []):
            pattern_summary[pattern] = pattern_summary.get(pattern, 0) + 1
    
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
    print("VISUAL AI DEDICATED TRAINING - Starting...")
    print("=" * 70)
    print("")
    print("This will process ALL remaining charts with:")
    print("  - 300 second timeout (5 minutes per chart)")
    print("  - High process priority")
    print("  - All other processes at IDLE priority")
    print("")
    print("Press Ctrl+C to stop at any time (progress is saved)")
    print("")
    
    try:
        run_dedicated_training()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user. Progress saved.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
