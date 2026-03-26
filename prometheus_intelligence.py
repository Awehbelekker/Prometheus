#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS v2.1 - UNIFIED INTELLIGENCE SYSTEM
================================================================================

Integrates all learning and knowledge systems:
- Knowledge Ingestion Pipeline (books, papers, articles)
- Advanced AI Models (DeepSeek-R1, Claude, GPT-4o)
- Live Trading Feedback Loop
- Visual Pattern Recognition
- Continuous Learning Backtest

This is the master control for PROMETHEUS's intelligence.

================================================================================
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


class PrometheusIntelligence:
    """
    Unified intelligence system for PROMETHEUS v2.1
    
    Combines:
    - Knowledge retrieval from ingested documents
    - Multi-model AI reasoning
    - Live trading feedback learning
    - Pattern recognition
    """
    
    VERSION = "2.1.0"
    
    def __init__(self):
        self.initialized = False
        self.knowledge_pipeline = None
        self.ai_models = None
        self.feedback_loop = None
        self.deepseek_reasoner = None
        self.long_context_analyzer = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize all subsystems"""
        logger.info(f"Initializing PROMETHEUS Intelligence v{self.VERSION}")
        
        # Load knowledge pipeline
        try:
            from knowledge_ingestion_pipeline import KnowledgeIngestionPipeline, EnhancedMarketOracle
            self.knowledge_pipeline = KnowledgeIngestionPipeline()
            self.market_oracle = EnhancedMarketOracle(self.knowledge_pipeline)
            logger.info(f"✓ Knowledge Pipeline: {len(self.knowledge_pipeline.index)} documents")
        except Exception as e:
            logger.warning(f"Knowledge Pipeline unavailable: {e}")
        
        # Load AI models
        try:
            from advanced_ai_models import AdvancedAIModels, DeepSeekR1Reasoner, FalconLongContextAnalyzer
            self.ai_models = AdvancedAIModels()
            self.deepseek_reasoner = DeepSeekR1Reasoner(self.ai_models)
            self.long_context_analyzer = FalconLongContextAnalyzer(self.ai_models)
            logger.info(f"✓ AI Models: {len(self.ai_models.available_models)} available")
        except Exception as e:
            logger.warning(f"AI Models unavailable: {e}")
        
        # Load feedback loop
        try:
            from live_trading_feedback import LiveTradingFeedbackLoop
            self.feedback_loop = LiveTradingFeedbackLoop()
            logger.info(f"✓ Feedback Loop: {len(self.feedback_loop.feedback)} trades tracked")
        except Exception as e:
            logger.warning(f"Feedback Loop unavailable: {e}")
        
        # Load pattern data
        self.patterns = self._load_patterns()
        
        self.initialized = True
        logger.info("PROMETHEUS Intelligence initialized successfully")
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load all pattern data"""
        patterns = {
            "visual": {},
            "learned": {},
            "statistics": {}
        }
        
        # Visual AI patterns
        visual_file = Path("visual_ai_patterns.json")
        if visual_file.exists():
            try:
                with open(visual_file, 'r') as f:
                    data = json.load(f)
                    patterns["visual"] = {
                        "successful": len(data.get("successful", [])),
                        "failed": len(data.get("failed", [])),
                        "patterns_detected": data.get("statistics", {}).get("patterns_detected", 0)
                    }
            except:
                pass
        
        # Learned patterns from continuous learning
        learned_files = list(Path(".").glob("learned_patterns_*.json"))
        if learned_files:
            latest = max(learned_files, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest, 'r') as f:
                    data = json.load(f)
                    total = sum(len(v) for v in data.values() if isinstance(v, list))
                    patterns["learned"] = {
                        "file": str(latest),
                        "total_patterns": total,
                        "categories": list(data.keys())
                    }
            except:
                pass
        
        # Learning results
        results_file = Path("CONTINUOUS_LEARNING_RESULTS_20Y.json")
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
                    patterns["statistics"] = {
                        "generations": data.get("generations", 0),
                        "final_fitness": data.get("final_fitness", 0),
                        "cagr": data.get("best_cagr", 0),
                        "sharpe": data.get("best_sharpe", 0)
                    }
            except:
                pass
        
        return patterns
    
    def analyze_opportunity(self, symbol: str, 
                           market_data: Dict[str, Any],
                           use_knowledge: bool = True,
                           use_deep_reasoning: bool = True) -> Dict[str, Any]:
        """
        Comprehensive analysis of a trading opportunity.
        
        Combines:
        - Knowledge base retrieval
        - Pattern matching
        - AI reasoning
        - Historical feedback
        """
        
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 1. Knowledge retrieval
        if use_knowledge and self.market_oracle:
            try:
                market_conditions = {
                    "trend": market_data.get("trend", "neutral"),
                    "patterns": market_data.get("patterns", []),
                    "volatility": market_data.get("volatility", "normal")
                }
                knowledge_context = self.market_oracle.get_trading_context(symbol, market_conditions)
                analysis["components"]["knowledge"] = {
                    "retrieved": True,
                    "context_length": len(knowledge_context),
                    "context_preview": knowledge_context[:500] if knowledge_context else ""
                }
            except Exception as e:
                analysis["components"]["knowledge"] = {"error": str(e)}
        
        # 2. Deep reasoning
        if use_deep_reasoning and self.deepseek_reasoner:
            try:
                signals = market_data.get("signals", {})
                reasoning = self.deepseek_reasoner.analyze_trade(symbol, market_data, signals)
                analysis["components"]["reasoning"] = reasoning
            except Exception as e:
                analysis["components"]["reasoning"] = {"error": str(e)}
        
        # 3. Pattern performance lookup
        if self.feedback_loop and self.feedback_loop.pattern_stats:
            detected_patterns = market_data.get("patterns", [])
            pattern_performance = {}
            for pattern in detected_patterns:
                if pattern in self.feedback_loop.pattern_stats:
                    stats = self.feedback_loop.pattern_stats[pattern]
                    pattern_performance[pattern] = {
                        "win_rate": stats["win_rate"],
                        "total_trades": stats["total_trades"]
                    }
            analysis["components"]["pattern_performance"] = pattern_performance
        
        # 4. Generate recommendation
        recommendation = self._generate_recommendation(analysis, market_data)
        analysis["recommendation"] = recommendation
        
        return analysis
    
    def _generate_recommendation(self, analysis: Dict[str, Any], 
                                 market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendation from analysis components"""
        
        confidence = 0.5  # Base confidence
        direction = "hold"
        reasons = []
        
        # Adjust based on reasoning
        reasoning = analysis.get("components", {}).get("reasoning", {})
        if reasoning and "analysis" in reasoning:
            analysis_text = reasoning["analysis"].lower()
            if "buy" in analysis_text or "bullish" in analysis_text:
                direction = "long"
                confidence += 0.1
                reasons.append("AI reasoning suggests bullish outlook")
            elif "sell" in analysis_text or "bearish" in analysis_text:
                direction = "short"
                confidence += 0.1
                reasons.append("AI reasoning suggests bearish outlook")
        
        # Adjust based on knowledge alignment
        knowledge = analysis.get("components", {}).get("knowledge", {})
        if knowledge.get("retrieved"):
            confidence += 0.05
            reasons.append("Knowledge base context retrieved")
        
        # Adjust based on pattern performance
        pattern_perf = analysis.get("components", {}).get("pattern_performance", {})
        if pattern_perf:
            avg_win_rate = sum(p["win_rate"] for p in pattern_perf.values()) / len(pattern_perf)
            if avg_win_rate > 60:
                confidence += 0.1
                reasons.append(f"Patterns have {avg_win_rate:.1f}% historical win rate")
            elif avg_win_rate < 40:
                confidence -= 0.1
                reasons.append(f"Warning: Patterns have low {avg_win_rate:.1f}% win rate")
        
        return {
            "direction": direction,
            "confidence": min(max(confidence, 0), 1),
            "reasons": reasons
        }
    
    def ingest_document(self, file_path: str, 
                        doc_type: str = "book",
                        title: str = None) -> Optional[str]:
        """Ingest a new document into the knowledge base"""
        
        if not self.knowledge_pipeline:
            logger.error("Knowledge pipeline not available")
            return None
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if file_path.suffix.lower() == ".pdf":
            return self.knowledge_pipeline.ingest_pdf(str(file_path), title, doc_type)
        elif file_path.suffix.lower() in [".txt", ".md"]:
            return self.knowledge_pipeline.ingest_text(str(file_path), title, doc_type)
        else:
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return None
    
    def query_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the knowledge base"""
        
        if not self.knowledge_pipeline:
            return []
        
        return self.knowledge_pipeline.query(query, n_results)
    
    def record_trade(self, symbol: str, direction: str,
                     entry_price: float, quantity: float,
                     signals: Dict[str, Any] = None,
                     patterns: List[str] = None) -> Optional[str]:
        """Record a trade entry for feedback learning"""
        
        if not self.feedback_loop:
            return None
        
        return self.feedback_loop.on_trade_entry(
            symbol, direction, entry_price, quantity, signals, patterns
        )
    
    def close_trade(self, trade_id: str, exit_price: float,
                    exit_reason: str = "manual") -> Optional[Dict[str, Any]]:
        """Record a trade exit"""
        
        if not self.feedback_loop:
            return None
        
        feedback = self.feedback_loop.on_trade_exit(trade_id, exit_price, exit_reason)
        if feedback:
            return {
                "pnl": feedback.pnl,
                "pnl_pct": feedback.pnl_pct,
                "pattern_success": feedback.pattern_success
            }
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        
        return {
            "version": self.VERSION,
            "initialized": self.initialized,
            "timestamp": datetime.now().isoformat(),
            "subsystems": {
                "knowledge_pipeline": {
                    "available": self.knowledge_pipeline is not None,
                    "documents": len(self.knowledge_pipeline.index) if self.knowledge_pipeline else 0,
                    "vectors": self.knowledge_pipeline.collection.count() if self.knowledge_pipeline and self.knowledge_pipeline.collection else 0
                },
                "ai_models": {
                    "available": self.ai_models is not None,
                    "models": list(self.ai_models.available_models.keys()) if self.ai_models else []
                },
                "feedback_loop": {
                    "available": self.feedback_loop is not None,
                    "trades_tracked": len(self.feedback_loop.feedback) if self.feedback_loop else 0,
                    "patterns_tracked": len(self.feedback_loop.pattern_stats) if self.feedback_loop else 0
                },
                "deepseek_reasoner": {
                    "available": self.deepseek_reasoner is not None and self.deepseek_reasoner.model_key is not None,
                    "model": self.deepseek_reasoner.model_key if self.deepseek_reasoner else None
                }
            },
            "patterns": self.patterns
        }


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("PROMETHEUS v2.1 - UNIFIED INTELLIGENCE SYSTEM")
    print("="*70)
    
    # Initialize
    prometheus = PrometheusIntelligence()
    
    # Show status
    status = prometheus.get_status()
    print(f"\nVersion: {status['version']}")
    print(f"Initialized: {status['initialized']}")
    
    print("\n[SUBSYSTEMS]")
    for name, info in status['subsystems'].items():
        available = info.get('available', False)
        icon = "✓" if available else "✗"
        print(f"  {icon} {name}")
        for key, value in info.items():
            if key != 'available':
                print(f"      {key}: {value}")
    
    print("\n[PATTERN DATA]")
    patterns = status.get('patterns', {})
    if patterns.get('visual'):
        v = patterns['visual']
        print(f"  Visual AI: {v.get('successful', 0)} charts analyzed, {v.get('patterns_detected', 0)} patterns")
    if patterns.get('learned'):
        l = patterns['learned']
        print(f"  Learned: {l.get('total_patterns', 0)} patterns in {len(l.get('categories', []))} categories")
    if patterns.get('statistics'):
        s = patterns['statistics']
        print(f"  Learning: {s.get('generations', 0)} generations, {s.get('cagr', 0):.1f}% CAGR, {s.get('sharpe', 0):.2f} Sharpe")
    
    # Demo analysis
    print("\n[DEMO ANALYSIS]")
    demo_data = {
        "price": 185.50,
        "change_pct": 1.2,
        "trend": "bullish",
        "patterns": ["support_bounce", "volume_spike"],
        "volatility": "normal",
        "rsi": 55,
        "macd": 0.5,
        "signals": {"rsi": 55, "macd": "bullish"}
    }
    
    print(f"  Analyzing AAPL with data: {json.dumps(demo_data, indent=2)[:200]}...")
    
    # Run analysis (skip deep reasoning for demo speed)
    analysis = prometheus.analyze_opportunity("AAPL", demo_data, 
                                              use_knowledge=True, 
                                              use_deep_reasoning=False)
    
    rec = analysis.get('recommendation', {})
    print(f"\n  Recommendation:")
    print(f"    Direction: {rec.get('direction', 'unknown')}")
    print(f"    Confidence: {rec.get('confidence', 0)*100:.1f}%")
    print(f"    Reasons: {', '.join(rec.get('reasons', []))}")
    
    print("\n" + "="*70)
    print("PROMETHEUS v2.1 READY")
    print("="*70)
    print("\nUsage:")
    print("  from prometheus_intelligence import PrometheusIntelligence")
    print("  prometheus = PrometheusIntelligence()")
    print("  analysis = prometheus.analyze_opportunity('AAPL', market_data)")
    print("  prometheus.ingest_document('trading_book.pdf', 'book')")
    print("  trade_id = prometheus.record_trade('AAPL', 'long', 185.50, 10)")
    print("="*70)


if __name__ == "__main__":
    main()
