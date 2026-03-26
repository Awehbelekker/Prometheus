"""Quick Visual AI Test - Test LLaVA on a few charts"""

import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_visual_training():
    from core.multimodal_analyzer import MultimodalChartAnalyzer
    
    # Initialize with fixed settings
    analyzer = MultimodalChartAnalyzer()
    
    charts_dir = Path('charts')
    chart_files = list(charts_dir.glob('*.png'))
    
    logger.info(f'Starting Visual AI Test on {len(chart_files)} total charts')
    logger.info(f'Using model: llava:7b with 180s timeout')
    
    results = {
        'started': datetime.now().isoformat(),
        'total_charts': len(chart_files),
        'analyzed': 0,
        'patterns_found': [],
        'errors': 0
    }
    
    # Process first 3 charts as a test
    test_charts = chart_files[:3]
    
    for i, chart_path in enumerate(test_charts):
        try:
            logger.info(f'[{i+1}/{len(test_charts)}] Analyzing: {chart_path.name}')
            
            # Extract symbol from filename
            symbol = chart_path.stem.split('_')[0]
            
            # NOT async - direct call
            result = analyzer.analyze_chart(
                str(chart_path),
                context={'symbol': symbol, 'timeframe': '1D'}
            )
            
            if result and result.patterns_detected:
                results['patterns_found'].extend(result.patterns_detected)
                logger.info(f'  Patterns: {result.patterns_detected}')
                logger.info(f'  Trend: {result.trend_direction} ({result.trend_strength})')
                logger.info(f'  Confidence: {result.confidence:.2f}')
            else:
                logger.info(f'  No patterns detected')
                logger.info(f'  Trend: {result.trend_direction if result else "N/A"}')
                logger.info(f'  Confidence: {result.confidence if result else 0:.2f}')
            
            results['analyzed'] += 1
            
        except Exception as e:
            logger.error(f'  Error: {str(e)[:100]}')
            results['errors'] += 1
    
    results['completed'] = datetime.now().isoformat()
    results['unique_patterns'] = list(set(results['patterns_found']))
    
    logger.info('')
    logger.info('TEST RESULTS:')
    logger.info(f'  Analyzed: {results["analyzed"]}/{len(test_charts)}')
    logger.info(f'  Patterns found: {len(results["unique_patterns"])}')
    logger.info(f'  Errors: {results["errors"]}')
    
    # Save results
    with open('visual_ai_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == '__main__':
    run_visual_training()
