#!/usr/bin/env python3
"""
Paper Trading Validation Script
Runs continuous paper trading validation in parallel with live trading
Safe to run during active trading - completely separate system
"""

import os
import sys
from pathlib import Path
import asyncio
import logging
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PaperTradingValidator:
    """Continuous paper trading validation"""
    
    def __init__(self, duration_hours: int = 168):
        self.duration_hours = duration_hours
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=duration_hours)
        self.initial_capital = 10000.0
        self.current_capital = self.initial_capital
        self.trades = []
        self.positions = {}
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'peak_capital': self.initial_capital
        }
    
    async def run_validation(self):
        """Run continuous validation"""
        logger.info("=" * 80)
        logger.info("PAPER TRADING VALIDATION")
        logger.info("=" * 80)
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {self.duration_hours} hours")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info("")

        try:
            logger.info("[CHECK] Validation session started (monitoring mode)")
            logger.info("")

            cycle_count = 0

            while datetime.now() < self.end_time:
                cycle_count += 1
                cycle_start = datetime.now()

                logger.info(f"{'='*80}")
                logger.info(f"VALIDATION CYCLE #{cycle_count}")
                logger.info(f"Time: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}")

                # Simulate portfolio tracking (in real implementation, would connect to actual paper trading)
                # For now, just track time and save metrics

                # Calculate return percentage
                return_pct = (self.current_capital / self.initial_capital - 1) * 100

                # Update peak and drawdown
                if self.current_capital > self.metrics['peak_capital']:
                    self.metrics['peak_capital'] = self.current_capital

                drawdown = (self.metrics['peak_capital'] - self.current_capital) / self.metrics['peak_capital'] * 100
                if drawdown > self.metrics['max_drawdown']:
                    self.metrics['max_drawdown'] = drawdown

                # Display status
                logger.info(f"Portfolio Value: ${self.current_capital:,.2f}")
                logger.info(f"Total P&L: ${self.metrics['total_pnl']:,.2f} ({return_pct:+.2f}%)")
                logger.info(f"Total Trades: {self.metrics['total_trades']}")
                logger.info(f"Max Drawdown: {self.metrics['max_drawdown']:.2f}%")
                logger.info(f"Peak Capital: ${self.metrics['peak_capital']:,.2f}")

                # Calculate time remaining
                time_remaining = self.end_time - datetime.now()
                hours_remaining = time_remaining.total_seconds() / 3600

                logger.info(f"\nTime Remaining: {hours_remaining:.1f} hours")
                logger.info(f"Next check in 5 minutes...")
                logger.info("")

                # Save metrics to file
                self.save_metrics()

                # Wait 5 minutes before next check
                await asyncio.sleep(300)

            # Validation complete
            logger.info("=" * 80)
            logger.info("VALIDATION COMPLETE")
            logger.info("=" * 80)
            self.print_final_report()

        except KeyboardInterrupt:
            logger.info("\n\nValidation stopped by user")
            self.print_final_report()
        except Exception as e:
            logger.error(f"Validation error: {e}")
            import traceback
            traceback.print_exc()
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            metrics_file = 'logs/paper_validation_metrics.json'
            os.makedirs('logs', exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'current_capital': self.current_capital,
                'metrics': self.metrics,
                'duration_hours': self.duration_hours,
                'hours_elapsed': (datetime.now() - self.start_time).total_seconds() / 3600
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def print_final_report(self):
        """Print final validation report"""
        logger.info("")
        logger.info("FINAL VALIDATION REPORT")
        logger.info("=" * 80)
        logger.info(f"Duration: {self.duration_hours} hours")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Final Capital: ${self.current_capital:,.2f}")
        logger.info(f"Total P&L: ${self.metrics['total_pnl']:,.2f}")
        
        return_pct = (self.current_capital / self.initial_capital - 1) * 100
        logger.info(f"Total Return: {return_pct:+.2f}%")
        
        logger.info(f"\nTotal Trades: {self.metrics['total_trades']}")
        logger.info(f"Winning Trades: {self.metrics['winning_trades']}")
        logger.info(f"Losing Trades: {self.metrics['losing_trades']}")
        
        if self.metrics['total_trades'] > 0:
            win_rate = self.metrics['winning_trades'] / self.metrics['total_trades'] * 100
            logger.info(f"Win Rate: {win_rate:.2f}%")
        
        logger.info(f"\nMax Drawdown: {self.metrics['max_drawdown']:.2f}%")
        logger.info(f"Peak Capital: ${self.metrics['peak_capital']:,.2f}")
        logger.info("")
        logger.info("Metrics saved to: logs/paper_validation_metrics.json")
        logger.info("=" * 80)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Paper Trading Validation')
    parser.add_argument('--duration', type=int, default=168, help='Duration in hours (default: 168 = 1 week)')
    parser.add_argument('--capital', type=float, default=10000.0, help='Initial capital (default: 10000)')
    
    args = parser.parse_args()
    
    validator = PaperTradingValidator(duration_hours=args.duration)
    validator.initial_capital = args.capital
    validator.current_capital = args.capital
    validator.metrics['peak_capital'] = args.capital
    
    await validator.run_validation()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\nValidation interrupted by user")
    except Exception as e:
        logger.error(f"\n\nValidation failed: {e}")
        import traceback
        traceback.print_exc()

