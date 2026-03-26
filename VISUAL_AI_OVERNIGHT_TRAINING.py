"""
PROMETHEUS Visual AI Overnight Training
========================================
Runs Visual AI training when system load is low (overnight/weekends)

Features:
- Auto-detects low system load
- Pauses learning engine during training
- Processes all 1,320+ charts
- Saves results for live trading use
- Auto-restarts learning engine when done

Run manually: python VISUAL_AI_OVERNIGHT_TRAINING.py
Schedule: Use Windows Task Scheduler for 2 AM start
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visual_ai_overnight.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OvernightVisualAITrainer:
    """Overnight Visual AI training manager"""
    
    def __init__(self):
        self.charts_dir = Path('charts')
        self.results_file = 'visual_ai_patterns.json'
        self.learning_engine_script = 'PROMETHEUS_ULTIMATE_LEARNING_ENGINE.py'
        self.max_charts_per_session = 500  # Process in batches
        self.timeout_per_chart = 180  # 3 minutes per chart
        self.patterns_learned = {}
        self.total_analyzed = 0
        self.total_patterns = 0
        
    def is_good_time_to_train(self) -> bool:
        """Check if it's a good time for training (low market activity)"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Good times: 8 PM - 4 AM ET, or weekends
        is_overnight = (hour >= 20) or (hour < 4)
        is_weekend = weekday >= 5  # Saturday or Sunday
        
        return is_overnight or is_weekend
    
    def check_system_load(self) -> float:
        """Get current CPU usage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 50.0  # Assume moderate if can't check
    
    def pause_learning_engine(self):
        """Pause the learning engine to free resources"""
        logger.info("Pausing Learning Engine...")
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'LEARNING_ENGINE' in cmdline.upper():
                            proc.suspend()
                            logger.info(f"  Suspended PID {proc.info['pid']}")
                except:
                    pass
        except Exception as e:
            logger.warning(f"Could not pause learning engine: {e}")
    
    def resume_learning_engine(self):
        """Resume the learning engine"""
        logger.info("Resuming Learning Engine...")
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'LEARNING_ENGINE' in cmdline.upper():
                            proc.resume()
                            logger.info(f"  Resumed PID {proc.info['pid']}")
                except:
                    pass
        except Exception as e:
            logger.warning(f"Could not resume learning engine: {e}")
    
    def load_previous_results(self):
        """Load previously analyzed patterns"""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    self.patterns_learned = data.get('patterns', {})
                    self.total_analyzed = data.get('total_analyzed', 0)
                    logger.info(f"Loaded {self.total_analyzed} previously analyzed charts")
            except:
                pass
    
    def save_results(self):
        """Save analysis results"""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_analyzed': self.total_analyzed,
            'total_patterns': self.total_patterns,
            'patterns': self.patterns_learned,
            'pattern_summary': self._summarize_patterns()
        }
        with open(self.results_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved results: {self.total_analyzed} charts, {self.total_patterns} patterns")
    
    def _summarize_patterns(self) -> Dict[str, int]:
        """Summarize pattern frequencies"""
        summary = {}
        for symbol, data in self.patterns_learned.items():
            for pattern in data.get('patterns', []):
                summary[pattern] = summary.get(pattern, 0) + 1
        return dict(sorted(summary.items(), key=lambda x: -x[1]))
    
    def analyze_chart(self, chart_path: Path, analyzer) -> Dict[str, Any]:
        """Analyze a single chart"""
        try:
            symbol = chart_path.stem.split('_')[0]
            
            result = analyzer.analyze_chart(
                str(chart_path),
                context={'symbol': symbol, 'timeframe': '1D'}
            )
            
            if result:
                return {
                    'patterns': result.patterns_detected,
                    'trend': result.trend_direction,
                    'trend_strength': result.trend_strength,
                    'support': result.support_levels,
                    'resistance': result.resistance_levels,
                    'confidence': result.confidence,
                    'analyzed_at': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"Error analyzing {chart_path.name}: {e}")
        
        return None
    
    def run_training(self, max_charts: int = None):
        """Run the overnight training session"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("PROMETHEUS VISUAL AI OVERNIGHT TRAINING")
        logger.info("=" * 70)
        logger.info("")
        
        # Check timing
        if not self.is_good_time_to_train():
            logger.warning("Not optimal training time (market hours)")
            logger.info("Training anyway, but expect slower performance...")
        else:
            logger.info("Good time for training (low market activity)")
        
        # Check system load
        cpu_load = self.check_system_load()
        logger.info(f"Current CPU load: {cpu_load:.1f}%")
        
        if cpu_load > 70:
            logger.info("High CPU load - pausing learning engine...")
            self.pause_learning_engine()
            time.sleep(5)
        
        # Load previous results
        self.load_previous_results()
        
        # Get charts to process
        all_charts = list(self.charts_dir.glob('*.png'))
        logger.info(f"Total charts available: {len(all_charts)}")
        
        # Filter out already analyzed
        analyzed_files = set(self.patterns_learned.keys())
        charts_to_process = [c for c in all_charts if c.name not in analyzed_files]
        
        if max_charts:
            charts_to_process = charts_to_process[:max_charts]
        else:
            charts_to_process = charts_to_process[:self.max_charts_per_session]
        
        logger.info(f"Charts to process this session: {len(charts_to_process)}")
        logger.info("")
        
        if not charts_to_process:
            logger.info("All charts already analyzed!")
            return
        
        # Initialize analyzer
        try:
            from core.multimodal_analyzer import MultimodalChartAnalyzer
            analyzer = MultimodalChartAnalyzer()
            logger.info("Visual AI analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            return
        
        # Process charts
        session_patterns = 0
        session_analyzed = 0
        start_time = time.time()
        
        for i, chart_path in enumerate(charts_to_process):
            try:
                logger.info(f"[{i+1}/{len(charts_to_process)}] Analyzing: {chart_path.name}")
                
                result = self.analyze_chart(chart_path, analyzer)
                
                if result:
                    self.patterns_learned[chart_path.name] = result
                    patterns_found = len(result.get('patterns', []))
                    session_patterns += patterns_found
                    self.total_patterns += patterns_found
                    
                    if result['patterns']:
                        logger.info(f"  Patterns: {result['patterns']}")
                        logger.info(f"  Trend: {result['trend']} ({result['trend_strength']})")
                    else:
                        logger.info(f"  Trend: {result['trend']} (no specific patterns)")
                    
                    session_analyzed += 1
                    self.total_analyzed += 1
                else:
                    logger.info("  Analysis failed/timeout")
                
                # Save periodically
                if (i + 1) % 10 == 0:
                    self.save_results()
                    elapsed = time.time() - start_time
                    rate = session_analyzed / (elapsed / 60) if elapsed > 0 else 0
                    logger.info(f"  Progress: {session_analyzed} analyzed, {session_patterns} patterns, {rate:.1f} charts/min")
                
                # Check if we should stop (morning approaching)
                if datetime.now().hour >= 6 and datetime.now().hour < 8:
                    logger.info("Approaching market open - stopping training")
                    break
                    
            except KeyboardInterrupt:
                logger.info("Training interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error processing {chart_path.name}: {e}")
                continue
        
        # Final save
        self.save_results()
        
        # Summary
        elapsed = time.time() - start_time
        logger.info("")
        logger.info("=" * 70)
        logger.info("TRAINING SESSION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Charts analyzed this session: {session_analyzed}")
        logger.info(f"Patterns found this session: {session_patterns}")
        logger.info(f"Total charts analyzed: {self.total_analyzed}")
        logger.info(f"Total patterns learned: {self.total_patterns}")
        logger.info(f"Time elapsed: {elapsed/60:.1f} minutes")
        logger.info(f"Results saved to: {self.results_file}")
        logger.info("=" * 70)
        
        # Resume learning engine
        self.resume_learning_engine()


def main():
    """Main entry point"""
    trainer = OvernightVisualAITrainer()
    
    # Check for command line args
    max_charts = None
    if len(sys.argv) > 1:
        try:
            max_charts = int(sys.argv[1])
            print(f"Processing max {max_charts} charts")
        except:
            pass
    
    trainer.run_training(max_charts=max_charts)


if __name__ == '__main__':
    main()
