#!/usr/bin/env python3
"""
🎯 PROMETHEUS CLOSED-LOOP LEARNING SYSTEM
Master orchestrator for the complete autonomous learning cycle

FLOW:
1. Learn (Visual AI + Learning Engine + Paper Trading)
2. Trade (Enhanced Intelligence with 8 sources)
3. Test (Measure results)
4. Validate (Cross-check learnings)
5. Improve (Retrain Visual AI)
6. REPEAT!

Like practicing: Learn → Practice → Test → Learn from results → Get better!
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PrometheusClosedLoopSystem:
    """
    🔄 Complete closed-loop autonomous learning system
    """
    
    def __init__(self):
        self.session_id = f"closed_loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cycle_count = 0
        self.results = []
        
    async def run_learning_cycle(self):
        """
        🔄 Run one complete learning cycle
        
        Returns: Results from this cycle
        """
        self.cycle_count += 1
        logger.info("\n" + "="*80)
        logger.info(f"🔄 LEARNING CYCLE #{self.cycle_count}")
        logger.info("="*80)
        
        cycle_results = {
            'cycle_number': self.cycle_count,
            'start_time': datetime.now().isoformat(),
            'phases': {}
        }
        
        # PHASE 1: Check Visual AI Status
        logger.info("\n📊 PHASE 1: Visual AI Status Check")
        visual_ai_status = await self._check_visual_ai_status()
        cycle_results['phases']['visual_ai_status'] = visual_ai_status
        
        # PHASE 2: Check Learning Engine Status
        logger.info("\n🧠 PHASE 2: Learning Engine Status Check")
        learning_engine_status = await self._check_learning_engine_status()
        cycle_results['phases']['learning_engine_status'] = learning_engine_status
        
        # PHASE 3: Run Paper Trading with Enhanced Intelligence
        logger.info("\n📈 PHASE 3: Paper Trading with Full Intelligence")
        paper_trading_results = await self._run_paper_trading()
        cycle_results['phases']['paper_trading'] = paper_trading_results
        
        # PHASE 4: Validate Learnings (Cross-check)
        logger.info("\n🔬 PHASE 4: Validate Learnings")
        validation_results = await self._validate_learnings()
        cycle_results['phases']['validation'] = validation_results
        
        # PHASE 5: Retrain Visual AI on gaps
        if validation_results.get('gaps', []):
            logger.info("\n🎯 PHASE 5: Retrain Visual AI on Gaps")
            retrain_results = await self._retrain_visual_ai(validation_results['gaps'])
            cycle_results['phases']['retraining'] = retrain_results
        else:
            logger.info("\n✅ PHASE 5: No gaps found - System is aligned!")
            cycle_results['phases']['retraining'] = {'status': 'not_needed'}
        
        # PHASE 6: Update Learning Engine with Feedback
        logger.info("\n🔄 PHASE 6: Feed Results Back to Learning Engine")
        feedback_results = await self._feedback_to_learning_engine(cycle_results)
        cycle_results['phases']['feedback'] = feedback_results
        
        cycle_results['end_time'] = datetime.now().isoformat()
        cycle_results['cycle_complete'] = True
        
        self.results.append(cycle_results)
        
        return cycle_results
    
    async def _check_visual_ai_status(self) -> Dict:
        """Check Visual AI training status"""
        patterns_file = Path("visual_ai_patterns_cloud.json")
        
        if not patterns_file.exists():
            return {'status': 'not_trained', 'patterns': 0}
        
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        status = {
            'status': 'trained',
            'total_analyzed': data.get('total_analyzed', 0),
            'total_patterns': data.get('total_patterns', 0),
            'last_updated': data.get('last_updated', 'Unknown'),
            'provider': data.get('provider', 'Unknown'),
            'pattern_types': len(data.get('pattern_summary', {}))
        }
        
        logger.info(f"   ✅ Visual AI: {status['total_patterns']} patterns from {status['total_analyzed']} charts")
        logger.info(f"   Last updated: {status['last_updated']}")
        
        return status
    
    async def _check_learning_engine_status(self) -> Dict:
        """Check PROMETHEUS learning engine status"""
        strategies_file = Path("ultimate_strategies.json")
        
        if not strategies_file.exists():
            return {'status': 'not_running', 'strategies': 0}
        
        with open(strategies_file, 'r') as f:
            data = json.load(f)
        
        # Find best strategies
        best_strategies = []
        for strategy_id, strategy in data.items():
            if strategy.get('win_rate', 0) > 0.70 and strategy.get('total_trades', 0) > 100:
                best_strategies.append({
                    'name': strategy.get('name', 'Unknown'),
                    'generation': strategy.get('generation', 0),
                    'win_rate': strategy.get('win_rate', 0),
                    'total_trades': strategy.get('total_trades', 0)
                })
        
        status = {
            'status': 'running',
            'total_strategies': len(data),
            'best_strategies_count': len(best_strategies),
            'top_win_rate': max([s['win_rate'] for s in best_strategies]) if best_strategies else 0
        }
        
        logger.info(f"   ✅ Learning Engine: {status['total_strategies']} strategies")
        logger.info(f"   Best strategies: {status['best_strategies_count']} (>70% win rate)")
        if best_strategies:
            logger.info(f"   Top win rate: {status['top_win_rate']*100:.1f}%")
        
        return status
    
    async def _run_paper_trading(self) -> Dict:
        """Run paper trading session with enhanced intelligence"""
        try:
            from internal_realworld_paper_trading import InternalPaperTradingLoop
            
            loop = InternalPaperTradingLoop(starting_capital=10000.0)
            
            # Run trades for 3-5 symbols
            symbols = ['AAPL', 'MSFT', 'NVDA']
            
            for symbol in symbols:
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="1d", interval="5m")
                    
                    if not data.empty:
                        price = float(data['Close'].iloc[-1])
                        position_value = loop.current_capital * 0.10
                        quantity = int(position_value / price)
                        
                        if quantity > 0:
                            await loop.run_paper_trade(
                                symbol=symbol,
                                action='BUY',
                                entry_price=price,
                                quantity=quantity,
                                reasoning="Closed-loop learning cycle"
                            )
                except Exception as e:
                    logger.error(f"Trade error for {symbol}: {e}")
            
            # Get results
            report = loop.get_learned_patterns_report()
            loop.save_learnings()
            
            logger.info(f"   ✅ Paper Trading: {report['total_trades']} trades")
            logger.info(f"   Win rate: {report['win_rate']:.1f}%")
            logger.info(f"   Return: {report['total_return_pct']:+.2f}%")
            
            return report
            
        except Exception as e:
            logger.error(f"Paper trading error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _validate_learnings(self) -> Dict:
        """Validate that learnings match across systems"""
        try:
            from visual_ai_learning_validator import VisualAILearningValidator
            
            validator = VisualAILearningValidator()
            validator.load_visual_ai_patterns()
            validator.load_paper_trading_patterns()
            validator.load_learning_engine_performance()
            
            validation = validator.cross_validate()
            
            logger.info(f"   ✅ Validation Score: {validation['validation_score']:.1f}%")
            logger.info(f"   Pattern Matches: {len(validation['matches'])}")
            logger.info(f"   Gaps Found: {len(validation['gaps'])}")
            
            return validation
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def _retrain_visual_ai(self, gaps: List[Dict]) -> Dict:
        """Retrain Visual AI focusing on gap patterns"""
        logger.info(f"   🎯 Retraining on {len(gaps)} gap patterns...")
        
        # This would trigger CLOUD_VISION_TRAINING.py with focus on specific patterns
        # For now, log the intent
        retrain_targets = [gap['pattern'] for gap in gaps[:10]]
        
        logger.info(f"   Priority patterns: {', '.join(retrain_targets[:5])}")
        
        return {
            'status': 'triggered',
            'gap_count': len(gaps),
            'retrain_targets': retrain_targets,
            'message': 'Run CLOUD_VISION_TRAINING.py to complete retraining'
        }
    
    async def _feedback_to_learning_engine(self, cycle_results: Dict) -> Dict:
        """Feed cycle results back to learning engine"""
        
        # Extract key learnings
        paper_trading = cycle_results['phases'].get('paper_trading', {})
        validation = cycle_results['phases'].get('validation', {})
        
        feedback = {
            'cycle_number': self.cycle_count,
            'win_rate': paper_trading.get('win_rate', 0),
            'total_return_pct': paper_trading.get('total_return_pct', 0),
            'validation_score': validation.get('validation_score', 0),
            'patterns_discovered': paper_trading.get('patterns_discovered', 0),
            'improvement_areas': []
        }
        
        # Identify improvement areas
        if feedback['win_rate'] < 60:
            feedback['improvement_areas'].append('Improve signal quality')
        
        if feedback['validation_score'] < 50:
            feedback['improvement_areas'].append('Better pattern alignment')
        
        if validation.get('gaps', []):
            feedback['improvement_areas'].append('Address gap patterns')
        
        # Save feedback
        feedback_file = Path("learning_feedback.json")
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                all_feedback = json.load(f)
        else:
            all_feedback = {'cycles': []}
        
        all_feedback['cycles'].append(feedback)
        
        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
        
        logger.info(f"   ✅ Feedback saved: {len(feedback['improvement_areas'])} improvement areas")
        
        return feedback
    
    def print_cycle_summary(self, cycle_results: Dict):
        """Print beautiful cycle summary"""
        print("\n" + "="*80)
        print(f"📊 LEARNING CYCLE #{cycle_results['cycle_number']} SUMMARY")
        print("="*80)
        
        # Visual AI
        vai = cycle_results['phases']['visual_ai_status']
        print(f"\n👁️ Visual AI:")
        print(f"   Patterns: {vai.get('total_patterns', 0)} from {vai.get('total_analyzed', 0)} charts")
        
        # Learning Engine
        le = cycle_results['phases']['learning_engine_status']
        print(f"\n🧠 Learning Engine:")
        print(f"   Strategies: {le.get('total_strategies', 0)}")
        print(f"   Best win rate: {le.get('top_win_rate', 0)*100:.1f}%")
        
        # Paper Trading
        pt = cycle_results['phases']['paper_trading']
        print(f"\n📈 Paper Trading:")
        print(f"   Trades: {pt.get('total_trades', 0)}")
        print(f"   Win rate: {pt.get('win_rate', 0):.1f}%")
        print(f"   Return: {pt.get('total_return_pct', 0):+.2f}%")
        
        # Validation
        val = cycle_results['phases']['validation']
        print(f"\n🔬 Validation:")
        print(f"   Score: {val.get('validation_score', 0):.1f}%")
        print(f"   Matches: {len(val.get('matches', []))}")
        print(f"   Gaps: {len(val.get('gaps', []))}")
        
        # Feedback
        fb = cycle_results['phases']['feedback']
        print(f"\n🔄 Feedback:")
        if fb.get('improvement_areas'):
            print(f"   Improvement areas:")
            for area in fb['improvement_areas']:
                print(f"     - {area}")
        else:
            print(f"   ✅ System performing well!")
        
        print("\n" + "="*80)
    
    async def run_continuous_learning(self, max_cycles: int = 3):
        """
        🔄 Run multiple learning cycles continuously
        
        This is the FULL AUTONOMOUS SYSTEM!
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 PROMETHEUS CLOSED-LOOP LEARNING SYSTEM - STARTING")
        logger.info("="*80)
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Max cycles: {max_cycles}")
        
        for cycle in range(max_cycles):
            logger.info(f"\n⏳ Starting cycle {cycle + 1}/{max_cycles}...")
            
            cycle_results = await self.run_learning_cycle()
            
            self.print_cycle_summary(cycle_results)
            
            # Delay between cycles
            if cycle < max_cycles - 1:
                logger.info(f"\n⏸️ Waiting 10 seconds before next cycle...")
                await asyncio.sleep(10)
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary of all cycles"""
        print("\n" + "="*80)
        print("🏆 FINAL SUMMARY - ALL LEARNING CYCLES")
        print("="*80)
        
        print(f"\nTotal cycles completed: {self.cycle_count}")
        
        # Average metrics
        win_rates = [r['phases']['paper_trading'].get('win_rate', 0) for r in self.results]
        returns = [r['phases']['paper_trading'].get('total_return_pct', 0) for r in self.results]
        val_scores = [r['phases']['validation'].get('validation_score', 0) for r in self.results]
        
        if win_rates:
            print(f"\n📊 Average Performance:")
            print(f"   Win Rate: {sum(win_rates)/len(win_rates):.1f}%")
            print(f"   Total Return: {sum(returns)/len(returns):+.2f}%")
            print(f"   Validation Score: {sum(val_scores)/len(val_scores):.1f}%")
        
        # Improvement trend
        if len(win_rates) > 1:
            trend = "📈 Improving" if win_rates[-1] > win_rates[0] else "📉 Declining"
            print(f"\n{trend}")
            print(f"   First cycle: {win_rates[0]:.1f}%")
            print(f"   Last cycle: {win_rates[-1]:.1f}%")
        
        print("\n✅ CLOSED-LOOP LEARNING SYSTEM COMPLETE!")
        print("="*80)


async def main():
    """
    🎯 Run the complete closed-loop learning system
    """
    system = PrometheusClosedLoopSystem()
    
    # Run 3 learning cycles
    await system.run_continuous_learning(max_cycles=3)


if __name__ == "__main__":
    asyncio.run(main())
