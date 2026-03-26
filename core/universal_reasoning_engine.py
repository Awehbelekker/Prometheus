#!/usr/bin/env python3
"""
Universal Reasoning Engine - The Game-Changer for #1
Combines ALL reasoning sources: HRM + GPT-OSS + Quantum + Consciousness + Memory
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UniversalReasoningEngine:
    """
    Universal Reasoning Engine - Combines ALL reasoning sources
    This is what would make Prometheus #1 in the world
    """
    
    def __init__(self):
        self.hrm_system = None
        self.official_hrm = None  # Official HRM adapter
        self.gpt_oss = None
        self.quantum = None
        self.consciousness = None
        self.memory = None
        self.pattern_integration = None  # Backtest pattern integration
        self.chart_vision = None  # Visual chart analysis (llava)
        
        # Reasoning source weights (optimized for best results)
        self.weights = {
            'hrm': 0.20,           # Hierarchical reasoning (strong foundation)
            'gpt_oss': 0.15,       # Language understanding (context)
            'quantum': 0.10,       # Optimization (efficiency)
            'consciousness': 0.07, # Meta-cognition (wisdom)
            'memory': 0.07,        # Experience (learning)
            'patterns': 0.15,      # Historical patterns (backtest-learned)
            'fed_nlp': 0.07,       # Fed policy tone (macro context)
            'ml_regime': 0.07,     # ML market regime (environment awareness)
            'chart_vision': 0.12   # Visual chart analysis (llava GPU-accelerated)
        }
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all reasoning components"""
        # Try Official HRM first (preferred)
        try:
            from core.hrm_official_integration import get_official_hrm_adapter
            self.official_hrm = get_official_hrm_adapter(
                checkpoint_dir="hrm_checkpoints",
                use_ensemble=True
            )
            if self.official_hrm:
                logger.info("✅ Official HRM initialized for Universal Reasoning")
                logger.info(f"   Loaded {len(self.official_hrm.models)} checkpoints")
            else:
                logger.warning("Official HRM adapter not available")
        except Exception as e:
            logger.warning(f"Official HRM not available: {e}")
        
        # Fallback to Revolutionary HRM if official not available
        if not self.official_hrm:
            try:
                from core.revolutionary_hrm_system import RevolutionaryHRMSystem
                self.hrm_system = RevolutionaryHRMSystem(
                    use_multi_agent=True,
                    use_ensemble=True,
                    use_memory=True
                )
                logger.info("✅ Revolutionary HRM System initialized (fallback)")
            except Exception as e:
                logger.warning(f"Revolutionary HRM System not available: {e}")
        
        try:
            # GPT-OSS
            from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
            self.gpt_oss = GPTOSSTradingAdapter()
            logger.info("✅ GPT-OSS initialized for Universal Reasoning")
        except Exception as e:
            logger.warning(f"GPT-OSS not available: {e}")
        
        try:
            # Quantum
            from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
            self.quantum = QuantumTradingEngine({'portfolio': {}, 'risk': {}, 'arbitrage': {}})
            logger.info("✅ Quantum Engine initialized for Universal Reasoning")
        except Exception as e:
            logger.warning(f"Quantum Engine not available: {e}")
        
        try:
            # Consciousness
            from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
            self.consciousness = AIConsciousnessEngine()
            logger.info("✅ AI Consciousness initialized for Universal Reasoning")
        except Exception as e:
            logger.warning(f"AI Consciousness not available: {e}")
        
        try:
            # Memory (from HRM system if available)
            if self.hrm_system and hasattr(self.hrm_system, 'memory') and self.hrm_system.memory:
                self.memory = self.hrm_system.memory
                logger.info("✅ Memory System initialized for Universal Reasoning")
        except Exception as e:
            logger.warning(f"Memory System not available: {e}")
        
        # Pattern Integration (backtest-learned patterns)
        try:
            from core.pattern_integration import PatternIntegration
            self.pattern_integration = PatternIntegration()
            logger.info("✅ Pattern Integration initialized (backtest-learned patterns)")
        except Exception as e:
            logger.warning(f"Pattern Integration not available: {e}")

        # Chart Vision Analyzer (llava visual AI)
        try:
            from core.chart_vision_analyzer import ChartVisionAnalyzer
            self.chart_vision = ChartVisionAnalyzer()
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.chart_vision.initialize())
            except RuntimeError:
                asyncio.run(self.chart_vision.initialize())
            if self.chart_vision.is_available():
                logger.info(f"✅ ChartVision initialized for Universal Reasoning ({self.chart_vision.vision_model})")
            else:
                self.chart_vision = None
                logger.warning("ChartVision model not available via Ollama")
        except Exception as e:
            logger.warning(f"ChartVision not available: {e}")
    
    def make_ultimate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make ultimate decision by combining ALL reasoning sources
        This is the game-changer that would make Prometheus #1
        """
        logger.info("🧠 Universal Reasoning Engine: Synthesizing ALL reasoning sources...")
        
        # Ensure market_data has the symbol from context
        market_data = context.get('market_data', {})
        if isinstance(market_data, dict) and 'symbol' not in market_data and context.get('symbol'):
            market_data['symbol'] = context['symbol']
        
        # Collect reasoning from all sources
        reasoning_sources = {}
        
        # 1. HRM Reasoning (30%) - Try Official HRM first, fallback to Revolutionary
        if self.official_hrm:
            try:
                from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
                hrm_context = HRMReasoningContext(
                    market_data=context.get('market_data', {}),
                    user_profile=context.get('user_profile', {}),
                    trading_history=context.get('trading_history', []),
                    current_portfolio=context.get('portfolio', {}),
                    risk_preferences=context.get('risk_preferences', {}),
                    reasoning_level=HRMReasoningLevel.HIGH_LEVEL
                )
                # Use ensemble reasoning if available
                if self.official_hrm.use_ensemble and len(self.official_hrm.models) > 1:
                    hrm_output = self.official_hrm.ensemble_reason(hrm_context)
                else:
                    hrm_output = self.official_hrm.reason(hrm_context)
                
                # Convert to decision format
                hrm_decision = {
                    'action': hrm_output.action.upper(),
                    'confidence': hrm_output.confidence,
                    'symbol': hrm_output.symbol,
                    'quantity': hrm_output.quantity,
                    'reasoning': hrm_output.reasoning,
                    'checkpoint': hrm_output.checkpoint_used,
                    'source': 'official_hrm'
                }
                reasoning_sources['hrm'] = {
                    'decision': hrm_decision,
                    'weight': self.weights['hrm'],
                    'confidence': hrm_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ Official HRM Reasoning: {hrm_decision.get('action', 'UNKNOWN')} "
                          f"(confidence: {hrm_decision.get('confidence', 0):.3f}, "
                          f"checkpoint: {hrm_decision.get('checkpoint', 'N/A')})")
            except Exception as e:
                logger.warning(f"  ⚠️ Official HRM Reasoning failed: {e}")
                # Fallback to revolutionary HRM
                if self.hrm_system:
                    try:
                        from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
                        hrm_context = HRMReasoningContext(
                            market_data=context.get('market_data', {}),
                            user_profile=context.get('user_profile', {}),
                            trading_history=context.get('trading_history', []),
                            current_portfolio=context.get('portfolio', {}),
                            risk_preferences=context.get('risk_preferences', {}),
                            reasoning_level=HRMReasoningLevel.HIGH_LEVEL
                        )
                        hrm_decision = self.hrm_system.make_revolutionary_decision(hrm_context)
                        reasoning_sources['hrm'] = {
                            'decision': hrm_decision,
                            'weight': self.weights['hrm'],
                            'confidence': hrm_decision.get('confidence', 0.5)
                        }
                        logger.info(f"  ✅ Revolutionary HRM Reasoning (fallback): {hrm_decision.get('action', 'UNKNOWN')} "
                                  f"(confidence: {hrm_decision.get('confidence', 0):.3f})")
                    except Exception as e2:
                        logger.warning(f"  ⚠️ Revolutionary HRM Reasoning also failed: {e2}")
        elif self.hrm_system:
            # Use revolutionary HRM if official not available
            try:
                from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
                hrm_context = HRMReasoningContext(
                    market_data=context.get('market_data', {}),
                    user_profile=context.get('user_profile', {}),
                    trading_history=context.get('trading_history', []),
                    current_portfolio=context.get('portfolio', {}),
                    risk_preferences=context.get('risk_preferences', {}),
                    reasoning_level=HRMReasoningLevel.HIGH_LEVEL
                )
                hrm_decision = self.hrm_system.make_revolutionary_decision(hrm_context)
                reasoning_sources['hrm'] = {
                    'decision': hrm_decision,
                    'weight': self.weights['hrm'],
                    'confidence': hrm_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ Revolutionary HRM Reasoning: {hrm_decision.get('action', 'UNKNOWN')} "
                          f"(confidence: {hrm_decision.get('confidence', 0):.3f})")
            except Exception as e:
                logger.warning(f"  ⚠️ HRM Reasoning failed: {e}")
        
        # 2. GPT-OSS Reasoning (25%)
        if self.gpt_oss:
            try:
                # Try different method names
                if hasattr(self.gpt_oss, 'analyze_market'):
                    gpt_oss_decision = self.gpt_oss.analyze_market(context.get('market_data', {}))
                elif hasattr(self.gpt_oss, 'get_trading_recommendation'):
                    gpt_oss_decision = self.gpt_oss.get_trading_recommendation(context.get('market_data', {}))
                else:
                    # Fallback: create decision from GPT-OSS context
                    gpt_oss_decision = {
                        'action': 'HOLD',
                        'confidence': 0.5,
                        'reasoning': 'GPT-OSS analysis',
                        'source': 'gpt_oss'
                    }
                reasoning_sources['gpt_oss'] = {
                    'decision': gpt_oss_decision,
                    'weight': self.weights['gpt_oss'],
                    'confidence': gpt_oss_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ GPT-OSS Reasoning: {gpt_oss_decision.get('action', 'UNKNOWN')} (confidence: {gpt_oss_decision.get('confidence', 0):.3f})")
            except Exception as e:
                logger.warning(f"  ⚠️ GPT-OSS Reasoning failed: {e}")
        
        # 3. Quantum Optimization (20%)
        if self.quantum:
            try:
                import asyncio
                # Quantum execute_quantum_trade is async
                # Check if event loop is running
                try:
                    loop = asyncio.get_running_loop()
                    # If loop is running, create task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(self.quantum.execute_quantum_trade({
                                'symbol': context.get('market_data', {}).get('symbol', ''),
                                'quantity': context.get('quantity', 0),
                                'price': context.get('market_data', {}).get('price', 0)
                            }))
                        )
                        quantum_result = future.result(timeout=5.0)
                except RuntimeError:
                    # No event loop, can use asyncio.run
                    quantum_result = asyncio.run(self.quantum.execute_quantum_trade({
                        'symbol': context.get('market_data', {}).get('symbol', ''),
                        'quantity': context.get('quantity', 0),
                        'price': context.get('market_data', {}).get('price', 0)
                    }))
                # Convert quantum result to decision format
                quantum_decision = {
                    'action': 'BUY' if quantum_result.get('quantum_advantage', 0) > 0.5 else 'HOLD',
                    'confidence': quantum_result.get('confidence', 0.5),
                    'quantum_advantage': quantum_result.get('quantum_advantage', 0)
                }
                reasoning_sources['quantum'] = {
                    'decision': quantum_decision,
                    'weight': self.weights['quantum'],
                    'confidence': quantum_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ Quantum Optimization: {quantum_decision.get('action', 'UNKNOWN')} (advantage: {quantum_result.get('quantum_advantage', 0):.3f})")
            except Exception as e:
                logger.warning(f"  ⚠️ Quantum Optimization failed: {e}")
        
        # 4. Consciousness Meta-Cognition (15%)
        if self.consciousness:
            try:
                import asyncio
                # Apply nest_asyncio first to handle nested loops
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    pass
                
                # Check if we're already in an event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context - schedule the coroutine properly
                    import concurrent.futures
                    future = asyncio.ensure_future(self.consciousness.make_conscious_decision(context))
                    # Run until complete within the existing loop
                    consciousness_decision = loop.run_until_complete(future)
                except RuntimeError:
                    # No running loop - safe to use asyncio.run()
                    consciousness_decision = asyncio.run(self.consciousness.make_conscious_decision(context))
                
                reasoning_sources['consciousness'] = {
                    'decision': consciousness_decision,
                    'weight': self.weights['consciousness'],
                    'confidence': consciousness_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ Consciousness Meta-Cognition: {consciousness_decision.get('action', 'UNKNOWN')} (confidence: {consciousness_decision.get('confidence', 0):.3f})")
            except Exception as e:
                logger.warning(f"  ⚠️ Consciousness Meta-Cognition failed: {e}")
        
        # 5. Memory Insights (10%)
        if self.memory:
            try:
                memory_insights = self.memory.recall_for_context(context.get('market_data', {}))
                # Extract best strategy from memory
                best_strategy = None
                if memory_insights.get('procedural'):
                    strategies = memory_insights['procedural']
                    if strategies:
                        best_strategy = strategies[0]
                
                memory_decision = {
                    'action': best_strategy.get('strategy_data', {}).get('action', 'HOLD') if best_strategy else 'HOLD',
                    'confidence': best_strategy.get('success_rate', 0.5) if best_strategy else 0.5,
                    'memory_based': True
                }
                reasoning_sources['memory'] = {
                    'decision': memory_decision,
                    'weight': self.weights['memory'],
                    'confidence': memory_decision.get('confidence', 0.5)
                }
                logger.info(f"  ✅ Memory Insights: {memory_decision.get('action', 'UNKNOWN')} (from {len(memory_insights.get('procedural', []))} strategies)")
            except Exception as e:
                logger.warning(f"  ⚠️ Memory Insights failed: {e}")
        
        # 6. Backtest-Learned Patterns (20%) - NEW!
        if self.pattern_integration:
            try:
                market_data = context.get('market_data', {})
                current_regime = market_data.get('regime', context.get('market_regime', 'unknown'))
                
                # Create base decision from other sources for pattern enhancement
                base_pattern_decision = {
                    'action': 'HOLD',
                    'confidence': 0.5,
                    'symbol': market_data.get('symbol', 'UNKNOWN')
                }
                
                # Enhance with patterns
                pattern_decision = self.pattern_integration.enhance_decision(
                    base_pattern_decision,
                    market_data,
                    current_regime
                )
                
                reasoning_sources['patterns'] = {
                    'decision': pattern_decision,
                    'weight': self.weights['patterns'],
                    'confidence': pattern_decision.get('confidence', 0.5)
                }
                
                patterns_matched = pattern_decision.get('patterns_matched', 0)
                if patterns_matched > 0:
                    logger.info(f"  ✅ Backtest Patterns: {pattern_decision.get('pattern_suggested_action', 'N/A')} "
                              f"({patterns_matched} patterns matched, confidence: {pattern_decision.get('confidence', 0):.3f})")
                else:
                    logger.info(f"  ℹ️ Backtest Patterns: No patterns matched (will use once backtests complete)")
            except Exception as e:
                logger.warning(f"  ⚠️ Backtest Patterns failed: {e}")
        
        # 7. Fed NLP Policy Signal (8%) - Macro monetary policy context
        try:
            from core.fed_nlp_analyzer import FedNLPAnalyzer
            if not hasattr(self, '_fed_analyzer_cached'):
                self._fed_analyzer_cached = FedNLPAnalyzer()
            fed_analyzer = self._fed_analyzer_cached
            fed_signal = fed_analyzer.get_latest_signal()
            if fed_signal and fed_signal.get('tone_score') is not None:
                tone = fed_signal['tone_score']  # -1.0 hawkish to +1.0 dovish
                fed_conf = min(abs(tone), 1.0) * 0.8 + 0.2

                if tone > 0.2:
                    fed_action = 'BUY'  # Dovish = bullish
                elif tone < -0.2:
                    fed_action = 'SELL'  # Hawkish = bearish
                else:
                    fed_action = 'HOLD'

                fed_decision = {
                    'action': fed_action,
                    'confidence': fed_conf,
                    'tone_score': tone,
                    'source': 'fed_nlp'
                }
                reasoning_sources['fed_nlp'] = {
                    'decision': fed_decision,
                    'weight': self.weights['fed_nlp'],
                    'confidence': fed_conf
                }
                logger.info(f"  Fed NLP: {fed_action} (tone: {tone:+.2f}, conf: {fed_conf:.3f})")
        except Exception as e:
            logger.warning(f"  Fed NLP failed: {e}")

        # 8. ML Regime Detector (8%) - Market environment awareness
        try:
            from core.ml_regime_detector import MLRegimeDetector
            import yfinance as _yf
            _sym = context.get('symbol', context.get('market_data', {}).get('symbol', 'SPY'))
            _hist = _yf.Ticker(_sym).history(period='3mo')
            # yfinance returns capitalized columns (Close, Open, etc.)
            # ML Regime Detector expects lowercase (close, open, etc.)
            _hist.columns = [c.lower() for c in _hist.columns]
            regime_detector = MLRegimeDetector()
            regime_result = regime_detector.predict_regime(_hist)
            if regime_result and regime_result.get('regime'):
                regime = regime_result['regime']
                regime_conf = regime_result.get('confidence', 0.5)

                if regime == 'BULL':
                    regime_action = 'BUY'
                elif regime == 'BEAR':
                    regime_action = 'SELL'
                else:
                    regime_action = 'HOLD'  # VOLATILE or SIDEWAYS

                regime_decision = {
                    'action': regime_action,
                    'confidence': regime_conf,
                    'regime': regime,
                    'source': 'ml_regime'
                }
                reasoning_sources['ml_regime'] = {
                    'decision': regime_decision,
                    'weight': self.weights['ml_regime'],
                    'confidence': regime_conf
                }
                logger.info(f"  ML Regime: {regime} -> {regime_action} ({regime_conf:.0%})")
        except Exception as e:
            logger.warning(f"  ML Regime failed: {e}")

        # 9. Chart Vision Analysis (12%) - Visual pattern recognition via llava
        if self.chart_vision:
            try:
                import asyncio
                import yfinance as _yf_cv
                _cv_sym = context.get('symbol', market_data.get('symbol', 'SPY'))
                _yf_sym = _cv_sym.replace('/', '-') if '/' in _cv_sym else _cv_sym
                _cv_hist = _yf_cv.Ticker(_yf_sym).history(period='3mo')
                if _cv_hist is not None and len(_cv_hist) >= 10:
                    _cv_hist.columns = [c.lower() for c in _cv_hist.columns]
                    try:
                        loop = asyncio.get_running_loop()
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            cv_result = executor.submit(
                                lambda: asyncio.run(self.chart_vision.analyze_chart(_cv_sym, _cv_hist))
                            ).result(timeout=45.0)
                    except RuntimeError:
                        cv_result = asyncio.run(self.chart_vision.analyze_chart(_cv_sym, _cv_hist))
                    if cv_result and cv_result.get('confidence', 0) > 0.4:
                        cv_action = cv_result.get('recommendation', 'HOLD').upper()
                        if cv_action not in ('BUY', 'SELL', 'HOLD'):
                            cv_action = 'HOLD'
                        cv_decision = {
                            'action': cv_action,
                            'confidence': cv_result.get('confidence', 0.5),
                            'trend': cv_result.get('trend', 'unknown'),
                            'patterns': cv_result.get('patterns', []),
                            'source': 'chart_vision'
                        }
                        reasoning_sources['chart_vision'] = {
                            'decision': cv_decision,
                            'weight': self.weights['chart_vision'],
                            'confidence': cv_decision['confidence']
                        }
                        logger.info(f"  ✅ ChartVision: {cv_action} (trend: {cv_result.get('trend', '?')}, conf: {cv_decision['confidence']:.3f})")
            except Exception as e:
                logger.warning(f"  ⚠️ ChartVision failed: {e}")

        # Synthesize ultimate decision
        ultimate_decision = self._synthesize_ultimate_decision(reasoning_sources, context)
        
        # Enhance final decision with patterns if available
        if self.pattern_integration and 'patterns' in reasoning_sources:
            pattern_decision = reasoning_sources['patterns']['decision']
            if pattern_decision.get('patterns_matched', 0) > 0:
                # Patterns found - enhance final decision
                if pattern_decision.get('pattern_override', False):
                    # Strong pattern signal - consider adjusting
                    pattern_action = pattern_decision.get('pattern_suggested_action')
                    pattern_conf = pattern_decision.get('pattern_confidence', 0)
                    
                    # Blend pattern suggestion with other sources
                    current_action_score = ultimate_decision.get('confidence', 0)
                    pattern_score = pattern_conf * self.weights['patterns']
                    
                    if pattern_score > current_action_score * 0.8:  # Pattern is strong
                        ultimate_decision['pattern_influenced'] = True
                        ultimate_decision['pattern_reasoning'] = pattern_decision.get('pattern_reasoning', '')
                        # Adjust confidence
                        ultimate_decision['confidence'] = (
                            ultimate_decision['confidence'] * 0.8 +
                            pattern_conf * 0.2
                        )
        
        logger.info(f"🎯 Universal Decision: {ultimate_decision['action']} (confidence: {ultimate_decision['confidence']:.3f})")
        logger.info(f"   Sources: {len(reasoning_sources)}/{9} reasoning sources")
        
        return ultimate_decision
    
    def _synthesize_ultimate_decision(self, reasoning_sources: Dict, context: Dict) -> Dict[str, Any]:
        """Synthesize ultimate decision from all reasoning sources"""
        if not reasoning_sources:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'No reasoning sources available',
                'universal': True
            }
        
        # Weighted voting for actions
        action_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        source_details = {}
        
        for source_name, source_data in reasoning_sources.items():
            decision = source_data['decision']
            weight = source_data['weight']
            confidence = source_data['confidence']
            
            action = decision.get('action', 'HOLD')
            if action in action_scores:
                action_scores[action] += confidence * weight
            
            total_weight += weight
            source_details[source_name] = {
                'action': action,
                'confidence': confidence,
                'weight': weight
            }
        
        # Select best action
        best_action = max(action_scores, key=action_scores.get)
        final_confidence = action_scores[best_action] / max(total_weight, 0.001)
        
        # Calculate position size
        position_size = min(final_confidence * 0.1, 0.1)  # Max 10%
        
        return {
            'action': best_action,
            'confidence': min(final_confidence, 1.0),
            'position_size': position_size,
            'reasoning_sources': source_details,
            'num_sources': len(reasoning_sources),
            'universal': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all reasoning components"""
        return {
            'official_hrm': self.official_hrm is not None,
            'hrm': self.hrm_system is not None,
            'gpt_oss': self.gpt_oss is not None,
            'quantum': self.quantum is not None,
            'consciousness': self.consciousness is not None,
            'memory': self.memory is not None,
            'weights': self.weights,
            'hrm_checkpoints': len(self.official_hrm.models) if self.official_hrm else 0,
            'pattern_integration': self.pattern_integration is not None,
            'chart_vision': self.chart_vision is not None,
            'total_sources': sum(1 for v in [self.official_hrm, self.hrm_system, self.gpt_oss, self.quantum, self.consciousness, self.memory, self.pattern_integration, self.chart_vision] if v is not None)
        }

