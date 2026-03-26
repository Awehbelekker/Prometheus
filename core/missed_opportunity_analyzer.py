"""
Missed Opportunity Analyzer for PROMETHEUS
Learns from opportunities that were NOT taken and analyzes what could have been
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class MissedOpportunity:
    """A trading opportunity that was scanned but not executed"""
    opportunity_id: str
    timestamp: datetime
    symbol: str
    scan_price: float
    peak_price: float  # Highest price reached after scan
    potential_profit: float
    potential_profit_pct: float
    why_missed: str  # Reason it wasn't taken
    ai_confidence_at_scan: float
    market_conditions: Dict[str, Any]
    what_happened_after: Dict[str, Any]
    lesson_learned: str

@dataclass
class OpportunityPattern:
    """Pattern of missed opportunities"""
    pattern_type: str
    frequency: int
    avg_missed_profit: float
    common_reasons: List[str]
    recommended_fix: str

class MissedOpportunityAnalyzer:
    """
    Analyzes opportunities that were scanned but not taken
    Learns from 'what could have been' to improve future decisions
    """
    
    def __init__(self):
        self.missed_opportunities = []
        self.scanned_symbols = {}  # Track all scanned symbols
        self.opportunity_patterns = {}
        self.learning_enabled = True
        
        logger.info("[LEARNING] Missed Opportunity Analyzer initialized")
    
    async def track_scanned_opportunity(
        self,
        symbol: str,
        price: float,
        ai_confidence: float,
        market_conditions: Dict[str, Any],
        decision: str,
        reason: str
    ):
        """
        Track every opportunity that was scanned
        Store it for later analysis to see if we missed profit
        """
        opportunity_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.scanned_symbols[opportunity_id] = {
            'symbol': symbol,
            'scan_time': datetime.now(),
            'scan_price': price,
            'ai_confidence': ai_confidence,
            'market_conditions': market_conditions,
            'decision': decision,  # 'executed' or 'skipped'
            'reason': reason
        }
        
        # Schedule follow-up analysis (check what happened 1 hour later)
        asyncio.create_task(
            self._analyze_opportunity_outcome(opportunity_id, hours_later=1)
        )
    
    async def _analyze_opportunity_outcome(
        self,
        opportunity_id: str,
        hours_later: int = 1
    ):
        """
        Check what happened to a scanned opportunity after X hours
        Did we miss out on profit?
        """
        # Wait for the specified time
        await asyncio.sleep(hours_later * 3600)
        
        if opportunity_id not in self.scanned_symbols:
            return
        
        opp = self.scanned_symbols[opportunity_id]
        
        # If we already executed this trade, skip analysis
        if opp['decision'] == 'executed':
            return
        
        # Get current price
        try:
            from core.real_time_market_data import RealTimeMarketData
            market_data = RealTimeMarketData()
            current_data = await market_data.get_real_time_price(opp['symbol'])
            current_price = current_data.get('price', opp['scan_price'])
        except Exception as e:
            logger.warning(f"[LEARNING] Could not get follow-up price for {opp['symbol']}: {e}")
            return
        
        # Calculate what profit we could have made
        potential_profit_pct = ((current_price - opp['scan_price']) / opp['scan_price']) * 100
        
        # If we missed significant profit (>2%), log it as a missed opportunity
        if potential_profit_pct > 2.0:
            missed = MissedOpportunity(
                opportunity_id=opportunity_id,
                timestamp=opp['scan_time'],
                symbol=opp['symbol'],
                scan_price=opp['scan_price'],
                peak_price=current_price,
                potential_profit=current_price - opp['scan_price'],
                potential_profit_pct=potential_profit_pct,
                why_missed=opp['reason'],
                ai_confidence_at_scan=opp['ai_confidence'],
                market_conditions=opp['market_conditions'],
                what_happened_after={
                    'price_change': current_price - opp['scan_price'],
                    'pct_change': potential_profit_pct,
                    'time_elapsed': f"{hours_later} hours"
                },
                lesson_learned=self._generate_lesson(opp, current_price, potential_profit_pct)
            )
            
            self.missed_opportunities.append(missed)
            
            logger.warning(
                f"[MISSED OPPORTUNITY] {opp['symbol']}: "
                f"Scanned at ${opp['scan_price']:.2f}, "
                f"now ${current_price:.2f} (+{potential_profit_pct:.1f}%) - "
                f"Reason: {opp['reason']}"
            )
            
            # Learn from this miss
            await self._learn_from_miss(missed)
    
    def _generate_lesson(
        self,
        opportunity: Dict[str, Any],
        actual_price: float,
        profit_pct: float
    ) -> str:
        """Generate a lesson learned from this missed opportunity"""
        reason = opportunity['reason']
        confidence = opportunity['ai_confidence']
        
        if 'confidence too low' in reason.lower():
            return f"AI confidence was {confidence:.2f} but trade would have gained {profit_pct:.1f}%. Consider lowering confidence threshold."
        
        elif 'risk too high' in reason.lower():
            return f"Risk assessment was too conservative. Trade would have gained {profit_pct:.1f}% safely."
        
        elif 'no clear signal' in reason.lower():
            return f"Signals were present but not detected. Improve pattern recognition for {opportunity['symbol']}."
        
        else:
            return f"Opportunity missed due to '{reason}'. Resulted in {profit_pct:.1f}% unrealized gain."
    
    async def _learn_from_miss(self, missed: MissedOpportunity):
        """
        Learn from a missed opportunity
        Adjust AI parameters to avoid similar misses
        """
        # Identify pattern
        pattern_key = f"{missed.why_missed}_{missed.symbol[:3]}"
        
        if pattern_key not in self.opportunity_patterns:
            self.opportunity_patterns[pattern_key] = OpportunityPattern(
                pattern_type=missed.why_missed,
                frequency=1,
                avg_missed_profit=missed.potential_profit_pct,
                common_reasons=[missed.why_missed],
                recommended_fix=self._suggest_fix(missed)
            )
        else:
            pattern = self.opportunity_patterns[pattern_key]
            pattern.frequency += 1
            pattern.avg_missed_profit = (
                (pattern.avg_missed_profit * (pattern.frequency - 1) + missed.potential_profit_pct)
                / pattern.frequency
            )
        
        # If we've missed this type of opportunity 3+ times, suggest adjustment
        if self.opportunity_patterns[pattern_key].frequency >= 3:
            logger.warning(
                f"[LEARNING] Pattern detected: {pattern_key} missed {self.opportunity_patterns[pattern_key].frequency} times. "
                f"Avg missed profit: {self.opportunity_patterns[pattern_key].avg_missed_profit:.1f}%. "
                f"Recommendation: {self.opportunity_patterns[pattern_key].recommended_fix}"
            )
    
    def _suggest_fix(self, missed: MissedOpportunity) -> str:
        """Suggest how to fix this type of miss"""
        if missed.ai_confidence_at_scan < 0.6:
            return "Lower AI confidence threshold from 0.6 to 0.5"
        
        elif 'risk' in missed.why_missed.lower():
            return "Increase risk tolerance by 10%"
        
        elif 'signal' in missed.why_missed.lower():
            return "Improve signal detection for this pattern type"
        
        else:
            return "Review and adjust decision criteria"
    
    def get_missed_opportunities_report(self, days: int = 7) -> Dict[str, Any]:
        """Get report of missed opportunities in last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_misses = [m for m in self.missed_opportunities if m.timestamp > cutoff]
        
        if not recent_misses:
            return {
                'total_missed': 0,
                'total_potential_profit': 0,
                'message': 'No significant missed opportunities detected'
            }
        
        total_potential = sum(m.potential_profit_pct for m in recent_misses)
        
        return {
            'total_missed': len(recent_misses),
            'total_potential_profit_pct': total_potential,
            'avg_missed_profit_pct': total_potential / len(recent_misses),
            'top_misses': sorted(recent_misses, key=lambda x: x.potential_profit_pct, reverse=True)[:5],
            'patterns': self.opportunity_patterns,
            'recommendations': [p.recommended_fix for p in self.opportunity_patterns.values()]
        }
    
    def get_learning_insights(self) -> List[str]:
        """Get actionable insights from missed opportunities"""
        insights = []
        
        # Analyze patterns
        for pattern_key, pattern in self.opportunity_patterns.items():
            if pattern.frequency >= 3 and pattern.avg_missed_profit > 5.0:
                insights.append(
                    f"[HIGH PRIORITY] {pattern.pattern_type}: "
                    f"Missed {pattern.frequency} times, "
                    f"avg {pattern.avg_missed_profit:.1f}% profit. "
                    f"Fix: {pattern.recommended_fix}"
                )
        
        # Overall stats
        if self.missed_opportunities:
            total_missed_profit = sum(m.potential_profit_pct for m in self.missed_opportunities)
            insights.append(
                f"[SUMMARY] Total missed opportunities: {len(self.missed_opportunities)}, "
                f"Total unrealized profit: {total_missed_profit:.1f}%"
            )
        
        return insights if insights else ["[OK] No significant missed opportunities detected"]


# Global instance
_missed_opportunity_analyzer = None

def get_missed_opportunity_analyzer() -> MissedOpportunityAnalyzer:
    """Get global missed opportunity analyzer instance"""
    global _missed_opportunity_analyzer
    if _missed_opportunity_analyzer is None:
        _missed_opportunity_analyzer = MissedOpportunityAnalyzer()
    return _missed_opportunity_analyzer
