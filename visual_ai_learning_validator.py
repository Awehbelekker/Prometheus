#!/usr/bin/env python3
"""
🔬 VISUAL AI LEARNING VALIDATOR
Cross-check what PROMETHEUS learned vs what Visual AI can see

This validates the closed-loop learning:
1. Check Visual AI patterns from 1,320 charts (452 patterns)
2. Check paper trading patterns learned
3. See if they match (validation!)
4. Find gaps (what we missed)
5. Retrain on gaps

Like a practice test to see if we actually learned!
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VisualAILearningValidator:
    """
    🎯 Validates that our learning loop is actually working
    """
    
    def __init__(self):
        self.visual_ai_patterns = {}
        self.paper_trading_patterns = {}
        self.learning_engine_patterns = {}
        
    def load_visual_ai_patterns(self):
        """Load patterns from Visual AI training (1,320 charts)"""
        patterns_file = Path("visual_ai_patterns_cloud.json")
        
        if not patterns_file.exists():
            logger.warning("❌ Visual AI patterns not found!")
            return
        
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        self.visual_ai_patterns = data.get('pattern_summary', {})
        
        logger.info(f"✅ Loaded Visual AI patterns: {sum(self.visual_ai_patterns.values())} total")
        logger.info(f"   Pattern types: {len(self.visual_ai_patterns)}")
        
    def load_paper_trading_patterns(self):
        """Load patterns from paper trading (learned from trades)"""
        learnings_file = Path("paper_trading_learnings.json")
        
        if not learnings_file.exists():
            logger.warning("⚠️ No paper trading learnings yet")
            return
        
        with open(learnings_file, 'r') as f:
            data = json.load(f)
        
        self.paper_trading_patterns = data.get('all_patterns', {})
        
        logger.info(f"✅ Loaded paper trading patterns: {len(self.paper_trading_patterns)}")
        
    def load_learning_engine_performance(self):
        """Load what learning engine discovered (Gen 359, 138K backtests)"""
        strategies_file = Path("ultimate_strategies.json")
        
        if not strategies_file.exists():
            logger.warning("⚠️ No learning engine strategies found")
            return
        
        with open(strategies_file, 'r') as f:
            data = json.load(f)
        
        # Extract successful strategies
        successful_strategies = []
        for strategy_id, strategy in data.items():
            if strategy.get('win_rate', 0) > 0.70 and strategy.get('total_trades', 0) > 100:
                successful_strategies.append({
                    'name': strategy.get('name', 'Unknown'),
                    'win_rate': strategy.get('win_rate', 0),
                    'total_trades': strategy.get('total_trades', 0),
                    'generation': strategy.get('generation', 0)
                })
        
        self.learning_engine_patterns = successful_strategies
        
        logger.info(f"✅ Found {len(successful_strategies)} successful strategies (>70% win rate, >100 trades)")
        
    def cross_validate(self) -> Dict:
        """
        🔬 Cross-check: Did we learn the same patterns?
        
        Returns validation report
        """
        logger.info("\n" + "="*80)
        logger.info("🔬 CROSS-VALIDATION: Visual AI vs Paper Trading vs Learning Engine")
        logger.info("="*80)
        
        validation = {
            'timestamp': datetime.now().isoformat(),
            'visual_ai_pattern_count': len(self.visual_ai_patterns),
            'visual_ai_total_detections': sum(self.visual_ai_patterns.values()),
            'paper_trading_pattern_count': len(self.paper_trading_patterns),
            'learning_engine_strategies': len(self.learning_engine_patterns),
            'matches': [],
            'gaps': [],
            'validation_score': 0.0
        }
        
        # Check Visual AI patterns
        print(f"\n📊 VISUAL AI PATTERNS (from 1,320 charts):")
        for pattern, count in sorted(self.visual_ai_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {pattern:<40} | Detected: {count:>4}x")
        
        # Check paper trading patterns
        if self.paper_trading_patterns:
            print(f"\n📈 PAPER TRADING LEARNED PATTERNS:")
            for pattern, stats in sorted(
                self.paper_trading_patterns.items(),
                key=lambda x: x[1].get('avg_profit', 0),
                reverse=True
            )[:10]:
                count = stats.get('count', 0)
                avg_profit = stats.get('avg_profit', 0)
                print(f"   {pattern[:40]:<40} | Seen: {count:>3}x | Avg: {avg_profit:>+6.2f}%")
                
                # Check if Visual AI also found this pattern
                for va_pattern in self.visual_ai_patterns.keys():
                    if pattern.lower() in va_pattern.lower() or va_pattern.lower() in pattern.lower():
                        validation['matches'].append({
                            'pattern': pattern,
                            'visual_ai_count': self.visual_ai_patterns[va_pattern],
                            'paper_trading_count': count,
                            'avg_profit': avg_profit
                        })
                        break
        else:
            print(f"\n⚠️ No paper trading patterns yet (run internal_realworld_paper_trading.py)")
        
        # Check learning engine strategies
        if self.learning_engine_patterns:
            print(f"\n🧠 LEARNING ENGINE TOP STRATEGIES:")
            for strategy in self.learning_engine_patterns[:10]:
                print(f"   {strategy['name']:<40} | Gen {strategy['generation']:>3} | "
                      f"Win: {strategy['win_rate']*100:>5.1f}% | Trades: {strategy['total_trades']:>4}")
        
        # Find gaps (patterns Visual AI found but paper trading didn't use)
        for va_pattern, va_count in self.visual_ai_patterns.items():
            if va_count > 20:  # Significant pattern
                found_in_trading = False
                for pt_pattern in self.paper_trading_patterns.keys():
                    if va_pattern.lower() in pt_pattern.lower():
                        found_in_trading = True
                        break
                
                if not found_in_trading:
                    validation['gaps'].append({
                        'pattern': va_pattern,
                        'visual_ai_count': va_count,
                        'opportunity': 'HIGH' if va_count > 50 else 'MEDIUM'
                    })
        
        # Calculate validation score
        if validation['matches']:
            # Score based on pattern overlap
            match_count = len(validation['matches'])
            total_patterns = max(len(self.visual_ai_patterns), len(self.paper_trading_patterns), 1)
            validation['validation_score'] = (match_count / total_patterns) * 100
        
        return validation
    
    def print_validation_report(self, validation: Dict):
        """📊 Print beautiful validation report"""
        print("\n" + "="*80)
        print("✅ VALIDATION RESULTS")
        print("="*80)
        
        print(f"\n📊 DATA SOURCES:")
        print(f"   Visual AI Patterns: {validation['visual_ai_pattern_count']} types, "
              f"{validation['visual_ai_total_detections']} detections")
        print(f"   Paper Trading Patterns: {validation['paper_trading_pattern_count']}")
        print(f"   Learning Engine Strategies: {validation['learning_engine_strategies']}")
        
        if validation['matches']:
            print(f"\n✅ PATTERN MATCHES (Visual AI ↔ Paper Trading):")
            for match in validation['matches'][:10]:
                print(f"   {match['pattern'][:50]:<50} | "
                      f"VA: {match['visual_ai_count']:>3}x | "
                      f"PT: {match['paper_trading_count']:>2}x | "
                      f"Profit: {match['avg_profit']:>+6.2f}%")
        else:
            print(f"\n⚠️ NO MATCHES YET - Need to run paper trading first!")
        
        if validation['gaps']:
            print(f"\n🔍 GAPS FOUND (Visual AI patterns not used in trading):")
            for gap in validation['gaps'][:10]:
                print(f"   {gap['pattern']:<50} | "
                      f"Seen: {gap['visual_ai_count']:>3}x | "
                      f"Opportunity: {gap['opportunity']}")
            
            print(f"\n💡 RECOMMENDATION: Retrain on these {len(validation['gaps'])} patterns!")
        
        print(f"\n📈 VALIDATION SCORE: {validation['validation_score']:.1f}%")
        
        if validation['validation_score'] > 50:
            print("   ✅ EXCELLENT - Learning loop is working!")
        elif validation['validation_score'] > 25:
            print("   ⚠️ GOOD - Some alignment, keep learning")
        else:
            print("   🔄 DEVELOPING - Keep trading and learning")
        
        print("\n" + "="*80)
    
    def save_validation_report(self, validation: Dict):
        """💾 Save validation report"""
        output_file = Path(f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(output_file, 'w') as f:
            json.dump(validation, f, indent=2)
        
        logger.info(f"💾 Validation report saved: {output_file}")
    
    def generate_retraining_list(self, validation: Dict) -> List[str]:
        """
        🎯 Generate list of patterns to focus on for retraining
        """
        retraining_targets = []
        
        # High-opportunity gaps
        for gap in validation['gaps']:
            if gap['opportunity'] == 'HIGH':
                retraining_targets.append(gap['pattern'])
        
        # Successful paper trading patterns (reinforce)
        for match in validation['matches']:
            if match['avg_profit'] > 2.0:  # >2% avg profit
                retraining_targets.append(match['pattern'])
        
        logger.info(f"\n🎯 RETRAINING TARGETS: {len(retraining_targets)} patterns")
        for target in retraining_targets[:10]:
            logger.info(f"   - {target}")
        
        return retraining_targets


def run_validation():
    """
    🔬 Run complete validation process
    """
    logger.info("🚀 Starting Visual AI Learning Validator")
    logger.info("   Goal: See if our learning loop is actually working!\n")
    
    validator = VisualAILearningValidator()
    
    # Load all data sources
    validator.load_visual_ai_patterns()
    validator.load_paper_trading_patterns()
    validator.load_learning_engine_performance()
    
    # Cross-validate
    validation = validator.cross_validate()
    
    # Print report
    validator.print_validation_report(validation)
    
    # Save report
    validator.save_validation_report(validation)
    
    # Generate retraining list
    retraining_targets = validator.generate_retraining_list(validation)
    
    # Save retraining targets
    with open('visual_ai_retraining_targets.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'targets': retraining_targets,
            'gaps': validation['gaps'],
            'matches': validation['matches']
        }, f, indent=2)
    
    logger.info(f"\n✅ Validation complete!")
    logger.info(f"📁 Retraining targets saved: visual_ai_retraining_targets.json")
    
    return validation


if __name__ == "__main__":
    run_validation()
