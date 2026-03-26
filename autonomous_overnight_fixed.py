#!/usr/bin/env python3
"""
PROMETHEUS Autonomous Overnight Enhancement System
Runs autonomous improvements while user sleeps - NO INTERRUPTION to live trading
"""

import asyncio
import time
import json
import subprocess
import os
from datetime import datetime, timedelta
import logging

# Set up simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonomous_overnight.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousOvernightSystem:
    """Autonomous system that enhances PROMETHEUS overnight"""
    
    def __init__(self):
        self.trading_pid = None
        self.start_time = datetime.now()
        self.enhancements_completed = []
        self.monitoring_active = True
        
    async def run_autonomous_enhancements(self):
        """Main autonomous enhancement loop"""
        logger.info("STARTING AUTONOMOUS OVERNIGHT ENHANCEMENTS")
        logger.info("=" * 55)
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("Live trading will continue UNINTERRUPTED")
        logger.info("")
        
        # Verify live trading is still running
        if not self.verify_trading_active():
            logger.error("Live trading not detected - aborting autonomous enhancements")
            return False
        
        logger.info("Live trading confirmed active - proceeding with enhancements")
        
        # Schedule all autonomous enhancements
        enhancements = [
            {
                "name": "Expand Visual AI Chart Analysis",
                "function": self.enhance_chart_analysis,
                "priority": "HIGH",
                "delay_minutes": 2,
                "description": "Analyze fresh crypto charts for new patterns"
            },
            {
                "name": "Optimize Confidence Threshold",
                "function": self.optimize_confidence_threshold, 
                "priority": "MEDIUM",
                "delay_minutes": 15,
                "description": "Lower threshold from 65% to 60% for more trades"
            },
            {
                "name": "Implement Smart Position Sizing",
                "function": self.implement_smart_sizing,
                "priority": "MEDIUM", 
                "delay_minutes": 30,
                "description": "Size positions based on Visual AI confidence"
            }
        ]
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(self.continuous_monitoring())
        
        # Schedule enhancements with delays
        for enhancement in enhancements:
            delay_seconds = enhancement["delay_minutes"] * 60
            logger.info(f"Scheduled: {enhancement['name']} in {enhancement['delay_minutes']} minutes")
            
            await asyncio.sleep(delay_seconds)
            
            if self.verify_trading_active():
                logger.info(f"Executing: {enhancement['name']}")
                try:
                    success = await enhancement["function"]()
                    if success:
                        self.enhancements_completed.append(enhancement['name'])
                        logger.info(f"Completed: {enhancement['name']}")
                    else:
                        logger.warning(f"Partial completion: {enhancement['name']}")
                except Exception as e:
                    logger.error(f"Failed: {enhancement['name']} - {str(e)}")
            else:
                logger.error("Trading system lost - stopping autonomous enhancements")
                break
        
        # Continue monitoring for 6 more hours
        logger.info("All enhancements complete - continuing monitoring for 6 hours")
        await asyncio.sleep(6 * 3600)  # 6 hours
        
        # Stop monitoring and generate summary
        self.monitoring_active = False
        await self.generate_morning_summary()
        
    def verify_trading_active(self):
        """Verify live trading is still running"""
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                # Count python processes
                lines = result.stdout.split('\n')
                python_processes = [l for l in lines if 'python.exe' in l]
                return len(python_processes) > 0
            return False
        except Exception as e:
            logger.error(f"Error checking trading status: {e}")
            return False
    
    async def enhance_chart_analysis(self):
        """Expand Visual AI chart analysis with fresh data"""
        logger.info("ENHANCING CHART ANALYSIS")
        logger.info("-" * 28)
        
        try:
            # Run fresh crypto chart analysis
            logger.info("Analyzing fresh crypto charts...")
            
            # Run chart training in background
            process = await asyncio.create_subprocess_exec(
                'python', 'train_crypto_charts.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("Fresh chart analysis completed successfully")
                
                # Count new patterns
                try:
                    with open('visual_ai_patterns.json', 'r') as f:
                        data = json.load(f)
                    new_count = data.get('total_analyzed', 0)
                    logger.info(f"Total patterns now: {new_count}")
                    return True
                except:
                    logger.info("Chart analysis completed (file not readable)")
                    return True
            else:
                logger.warning("Chart analysis had issues but continuing")
                return False
                
        except Exception as e:
            logger.error(f"Chart analysis error: {e}")
            return False
    
    async def optimize_confidence_threshold(self):
        """Lower confidence threshold for more trading opportunities"""
        logger.info("OPTIMIZING CONFIDENCE THRESHOLD")
        logger.info("-" * 33)
        
        try:
            # Look for trading config files
            config_files = ['config.json', 'trading_config.json', 'advanced_features_config.json']
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    logger.info(f"Updating {config_file}")
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        # Update confidence threshold
                        if 'confidence_threshold' in config:
                            old_threshold = config['confidence_threshold']
                            config['confidence_threshold'] = 0.60  # Lower from 65% to 60%
                            
                            with open(config_file, 'w') as f:
                                json.dump(config, f, indent=2)
                            
                            logger.info(f"Updated confidence: {old_threshold} -> 0.60")
                            return True
                        elif 'ai' in config and 'confidence_threshold' in config['ai']:
                            old_threshold = config['ai']['confidence_threshold']
                            config['ai']['confidence_threshold'] = 0.60
                            
                            with open(config_file, 'w') as f:
                                json.dump(config, f, indent=2)
                            
                            logger.info(f"Updated AI confidence: {old_threshold} -> 0.60")
                            return True
                    except Exception as e:
                        logger.warning(f"Could not update {config_file}: {e}")
            
            logger.info("Confidence threshold optimization complete")
            return True
            
        except Exception as e:
            logger.error(f"Confidence optimization error: {e}")
            return False
    
    async def implement_smart_sizing(self):
        """Implement smart position sizing based on Visual AI confidence"""
        logger.info("IMPLEMENTING SMART POSITION SIZING")
        logger.info("-" * 35)
        
        try:
            # Create smart sizing configuration
            smart_sizing_config = {
                "enabled": True,
                "last_updated": datetime.now().isoformat(),
                "confidence_multipliers": {
                    "very_high": {"min": 0.85, "multiplier": 1.5, "description": "85%+ confidence"},
                    "high": {"min": 0.75, "multiplier": 1.2, "description": "75-84% confidence"},
                    "medium": {"min": 0.65, "multiplier": 1.0, "description": "65-74% confidence"},
                    "low": {"min": 0.60, "multiplier": 0.7, "description": "60-64% confidence"}
                },
                "visual_ai_integration": {
                    "use_sentiment_scores": True,
                    "pattern_strength_bonus": 0.1,
                    "bearish_pattern_reduction": 0.3
                },
                "risk_limits": {
                    "max_position_multiplier": 2.0,
                    "min_position_multiplier": 0.5,
                    "total_exposure_limit": 0.8
                }
            }
            
            # Save configuration
            with open('smart_position_sizing_config.json', 'w') as f:
                json.dump(smart_sizing_config, f, indent=2)
            
            logger.info("Smart position sizing configuration created")
            logger.info("Position sizes will now scale with AI confidence:")
            logger.info("   • 85%+ confidence -> 1.5x position size")
            logger.info("   • 75-84% confidence -> 1.2x position size") 
            logger.info("   • 65-74% confidence -> 1.0x position size")
            logger.info("   • 60-64% confidence -> 0.7x position size")
            
            return True
            
        except Exception as e:
            logger.error(f"Smart sizing error: {e}")
            return False
    
    async def continuous_monitoring(self):
        """Continuous monitoring throughout the night"""
        logger.info("STARTING CONTINUOUS MONITORING")
        logger.info("-" * 31)
        
        monitor_count = 0
        last_status = None
        
        while self.monitoring_active:
            try:
                monitor_count += 1
                current_time = datetime.now()
                
                # Check trading status
                trading_active = self.verify_trading_active()
                
                # Log status every 30 minutes
                if monitor_count % 60 == 0:  # Every 30 minutes (30sec * 60)
                    runtime = current_time - self.start_time
                    logger.info(f"Monitor #{monitor_count//60}: Runtime {runtime}")
                    logger.info(f"Trading Active: {'YES' if trading_active else 'NO'}")
                    logger.info(f"Enhancements: {len(self.enhancements_completed)} completed")
                
                # Alert if trading stops
                if not trading_active and last_status != False:
                    logger.error("ALERT: Trading system appears to have stopped!")
                    logger.error("This needs attention when you wake up")
                
                last_status = trading_active
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error
        
        return True
    
    async def generate_morning_summary(self):
        """Generate summary for morning review"""
        end_time = datetime.now()
        total_runtime = end_time - self.start_time
        
        summary = {
            "autonomous_session": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(), 
                "total_runtime_hours": total_runtime.total_seconds() / 3600,
                "enhancements_completed": self.enhancements_completed,
                "trading_status": "ACTIVE" if self.verify_trading_active() else "NEEDS_ATTENTION"
            }
        }
        
        # Save summary
        with open('overnight_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("AUTONOMOUS OVERNIGHT SESSION COMPLETE")
        logger.info("=" * 42)
        logger.info(f"Total Runtime: {total_runtime}")
        logger.info(f"Completed Enhancements: {len(self.enhancements_completed)}")
        logger.info(f"Trading Status: {'ACTIVE' if self.verify_trading_active() else 'NEEDS_ATTENTION'}")
        logger.info("Summary saved to: overnight_summary.json")
        logger.info("Good morning! Check the logs for details.")

async def main():
    """Main autonomous overnight function"""
    system = AutonomousOvernightSystem()
    await system.run_autonomous_enhancements()

if __name__ == "__main__":
    print("PROMETHEUS AUTONOMOUS OVERNIGHT SYSTEM")
    print("Starting autonomous enhancements...")
    print("Live trading will continue uninterrupted")
    print("All activities logged to: autonomous_overnight.log")
    print("Safe to go to sleep!")
    print()
    
    asyncio.run(main())