"""
🔗 PROMETHEUS LEARNING INTEGRATION EXAMPLE
Shows how to integrate the learning system into your trading bot

This demonstrates:
1. Loading learning insights before trading
2. Applying confidence adjustments
3. Recording trade outcomes
4. Periodic learning analysis
"""

import asyncio
import logging
from datetime import datetime
from position_manager import PositionManager
from prometheus_learning_engine import PrometheusLearningEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningEnhancedTrader:
    """
    Example trading bot with integrated learning system
    """
    
    def __init__(self):
        self.pm = PositionManager()
        self.learning_engine = PrometheusLearningEngine()
        self.last_learning_analysis = datetime.now()
    
    async def analyze_trade_signal(self, symbol: str, base_confidence: float, 
                                   indicators: dict) -> dict:
        """
        Analyze a trade signal with learning enhancement
        
        Returns:
            dict with adjusted_confidence, reasoning, and recommendation
        """
        logger.info(f"\n📊 Analyzing signal for {symbol}")
        logger.info(f"   Base confidence: {base_confidence:.2f}")
        
        # Apply learning insights
        adjusted_confidence, reasons = self.pm.apply_learning_to_decision(
            symbol=symbol,
            base_confidence=base_confidence,
            indicators=indicators
        )
        
        logger.info(f"   Adjusted confidence: {adjusted_confidence:.2f}")
        for reason in reasons:
            logger.info(f"   {reason}")
        
        # Get symbol-specific insights
        insights = self.pm.get_learning_insights(symbol=symbol)
        
        decision = {
            'symbol': symbol,
            'base_confidence': base_confidence,
            'adjusted_confidence': adjusted_confidence,
            'adjustment_reasons': reasons,
            'insights': insights,
            'recommendation': 'TRADE' if adjusted_confidence >= 0.65 else 'SKIP'
        }
        
        # Log insights
        if insights.get('top_performers'):
            for performer in insights['top_performers'][:3]:
                if performer['symbol'] == symbol:
                    logger.info(f"   📈 Historical: {performer['win_rate']:.0f}% win rate, "
                               f"{performer['avg_profit_pct']:.1f}% avg profit")
        
        return decision
    
    async def execute_trade(self, symbol: str, action: str, quantity: float, 
                          price: float, confidence: float):
        """
        Execute trade and record in database
        
        This is where you'd call your broker API (Alpaca, etc.)
        """
        logger.info(f"\n🔹 Executing {action} for {symbol}")
        logger.info(f"   Quantity: {quantity}")
        logger.info(f"   Price: ${price:.2f}")
        logger.info(f"   Confidence: {confidence:.2f}")
        
        # In real implementation, execute via broker API:
        # order = alpaca.submit_order(...)
        
        # For this example, simulate trade recording
        # (In real system, this happens in your trading executor)
        pass
    
    async def close_trade(self, trade_id: int, symbol: str, exit_price: float, 
                         exit_reason: str, indicators: dict):
        """
        Close trade and record detailed outcome for learning
        """
        logger.info(f"\n🔸 Closing trade {trade_id} for {symbol}")
        logger.info(f"   Exit price: ${exit_price:.2f}")
        logger.info(f"   Reason: {exit_reason}")
        
        # Record outcome for learning
        success = self.pm.record_trade_outcome(
            trade_id=trade_id,
            exit_price=exit_price,
            exit_reason=exit_reason,
            market_indicators=indicators
        )
        
        if success:
            logger.info("   ✅ Trade outcome recorded for learning")
        else:
            logger.warning("   ⚠️ Failed to record trade outcome")
    
    async def run_periodic_learning_analysis(self, force: bool = False):
        """
        Run learning analysis periodically (e.g., daily)
        """
        # Check if it's time for analysis
        hours_since_last = (datetime.now() - self.last_learning_analysis).total_seconds() / 3600
        
        if not force and hours_since_last < 24:
            logger.debug(f"Skipping learning analysis (last run {hours_since_last:.1f} hours ago)")
            return
        
        logger.info("\n" + "="*80)
        logger.info("🧠 RUNNING PERIODIC LEARNING ANALYSIS")
        logger.info("="*80)
        
        # Step 1: Analyze closed trades
        logger.info("\nStep 1: Analyzing trade optimization...")
        summary = self.learning_engine.analyze_all_closed_trades(limit=50)
        
        if summary.get('total_analyzed', 0) > 0:
            logger.info(f"✅ Analyzed {summary['total_analyzed']} trades")
            logger.info(f"   Optimal exits: {summary.get('optimal_exits', 0)} "
                       f"({summary.get('optimal_exit_rate', 0):.1f}%)")
            logger.info(f"   Avg missed opportunity: {summary.get('avg_missed_opportunity_pct', 0):.2f}%")
        
        # Step 2: Identify patterns
        logger.info("\nStep 2: Identifying successful patterns...")
        patterns = self.learning_engine.identify_successful_patterns(min_profit_pct=3.0)
        
        if patterns:
            logger.info(f"✅ Identified {len(patterns)} patterns:")
            for pattern in patterns[:5]:  # Top 5
                logger.info(f"   • {pattern.pattern_type}: "
                           f"{pattern.success_rate:.1f}% success, "
                           f"{pattern.avg_profit_pct:.2f}% avg profit")
        
        # Step 3: Get recommendations
        logger.info("\nStep 3: Generating recommendations...")
        recommendations = self.learning_engine.get_learning_recommendations()
        
        if recommendations.get('action_items'):
            logger.info("💡 Action Items:")
            for i, item in enumerate(recommendations['action_items'][:5], 1):
                logger.info(f"   {i}. {item}")
        
        self.last_learning_analysis = datetime.now()
        logger.info("\n✅ Learning analysis complete!")
    
    async def trading_loop_example(self):
        """
        Example main trading loop with learning integration
        """
        logger.info("🚀 Starting Learning-Enhanced Trading Bot")
        
        # Run initial learning analysis
        await self.run_periodic_learning_analysis(force=True)
        
        # Example symbols to trade
        symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
        
        # Simulate trading loop
        for iteration in range(5):
            logger.info(f"\n{'='*80}")
            logger.info(f"Trading Iteration {iteration + 1}")
            logger.info(f"{'='*80}")
            
            for symbol in symbols:
                # Simulate getting a trading signal
                # (In real system, this comes from your AI/indicators)
                base_confidence = 0.75  # Example confidence
                indicators = {
                    'rsi': 45,
                    'macd': 'bullish',
                    'volume': 'high'
                }
                
                # Analyze with learning enhancement
                decision = await self.analyze_trade_signal(
                    symbol=symbol,
                    base_confidence=base_confidence,
                    indicators=indicators
                )
                
                # Execute if recommended
                if decision['recommendation'] == 'TRADE':
                    logger.info(f"   ✅ Trade recommended")
                    # In real system: execute trade
                    # await self.execute_trade(...)
                else:
                    logger.info(f"   ⏭️  Skipping (confidence too low)")
            
            # Simulate time passing
            await asyncio.sleep(1)
            
            # Check if it's time for periodic analysis
            await self.run_periodic_learning_analysis()
        
        logger.info("\n✅ Example complete!")


async def main():
    """Main function demonstrating the learning system"""
    trader = LearningEnhancedTrader()
    
    print("\n" + "="*80)
    print("🔗 PROMETHEUS LEARNING INTEGRATION EXAMPLE")
    print("="*80)
    print("\nThis demonstrates how to integrate the learning system")
    print("into your trading bot for continuous improvement.\n")
    
    # Run the example
    await trader.trading_loop_example()
    
    print("\n" + "="*80)
    print("📚 KEY INTEGRATION POINTS")
    print("="*80)
    print("""
1. BEFORE TRADING:
   • Call analyze_trade_signal() to apply learning
   • Use adjusted_confidence for position sizing
   • Review insights for context

2. AFTER CLOSING:
   • Call record_trade_outcome() to save results
   • Include market indicators for pattern analysis
   • System learns automatically

3. PERIODICALLY:
   • Run learning analysis (daily/weekly)
   • Review patterns and recommendations
   • Adjust strategy based on insights

4. IN PRODUCTION:
   • Integrate with your broker API
   • Use real-time indicators
   • Monitor dashboard for performance
    """)
    
    print("\n" + "="*80)
    print("✅ INTEGRATION EXAMPLE COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Adapt this example to your trading bot")
    print("  2. Replace simulated trades with real broker API calls")
    print("  3. Run learning analysis after first 10+ closed trades")
    print("  4. Use prometheus_learning_dashboard.py to review insights")


if __name__ == '__main__':
    asyncio.run(main())
