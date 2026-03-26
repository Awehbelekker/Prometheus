"""
CrewAI Integration for Multi-Agent HRM System
Orchestrates multiple HRM agents with specialized roles
"""

import sys
from pathlib import Path

# Add crewAI to path
crewai_path = Path(__file__).parent.parent / "integrated_repos" / "crewai"
if crewai_path.exists():
    sys.path.insert(0, str(crewai_path))

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI not available")

from core.hrm_integration import FullHRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
from core.hrm_checkpoint_manager import HRMCheckpointManager

class HRMAgent:
    """HRM Agent wrapper for CrewAI"""
    
    def __init__(self, name, role, checkpoint_name, hrm_engine):
        self.name = name
        self.role = role
        self.checkpoint_name = checkpoint_name
        self.hrm_engine = hrm_engine
        
    def reason(self, context: HRMReasoningContext) -> dict:
        """Make reasoning decision"""
        return self.hrm_engine.make_hierarchical_decision(context)

class MultiAgentHRMOrchestrator:
    """
    Multi-Agent HRM System using CrewAI
    Coordinates multiple specialized HRM agents
    """
    
    def __init__(self, device='cpu'):
        self.device = device
        self.checkpoint_manager = HRMCheckpointManager()
        self.agents = {}
        self.crew = None
        
        if CREWAI_AVAILABLE:
            self._initialize_crewai_agents()
        else:
            self._initialize_fallback_agents()
    
    def _initialize_crewai_agents(self):
        """Initialize CrewAI agents"""
        from crewai import Agent
        
        # Create specialized HRM engines
        arc_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        sudoku_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        maze_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        
        # Load specialized checkpoints
        # Note: This would require checkpoint switching capability
        
        # Create CrewAI agents
        self.arc_agent = Agent(
            role="General Reasoning Analyst",
            goal="Provide high-level strategic reasoning for trading decisions",
            backstory="Specialized in abstract reasoning and strategic planning",
            verbose=True
        )
        
        self.sudoku_agent = Agent(
            role="Pattern Recognition Specialist",
            goal="Identify patterns and trends in market data",
            backstory="Expert in pattern recognition and trend analysis",
            verbose=True
        )
        
        self.maze_agent = Agent(
            role="Optimization Expert",
            goal="Optimize trading paths and risk management",
            backstory="Specialized in path optimization and risk minimization",
            verbose=True
        )
        
        self.agents = {
            'arc': self.arc_agent,
            'sudoku': self.sudoku_agent,
            'maze': self.maze_agent
        }
    
    def _initialize_fallback_agents(self):
        """Fallback: Create simple agent wrappers"""
        logger.warning("CrewAI not available, using fallback agents")
        
        arc_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        sudoku_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        maze_engine = FullHRMTradingEngine(device=self.device, use_full_hrm=True)
        
        self.agents = {
            'arc': HRMAgent('ARC', 'General Reasoning', 'arc_agi_2', arc_engine),
            'sudoku': HRMAgent('Sudoku', 'Pattern Recognition', 'sudoku_extreme', sudoku_engine),
            'maze': HRMAgent('Maze', 'Optimization', 'maze_30x30', maze_engine)
        }
    
    def make_ensemble_decision(self, context: HRMReasoningContext) -> dict:
        """Make decision using ensemble of agents"""
        decisions = {}
        
        # Get decision from each agent
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, 'reason'):
                    # Fallback agent
                    decision = agent.reason(context)
                else:
                    # CrewAI agent - would need task creation
                    decision = self._get_crewai_decision(agent, context)
                
                decisions[name] = decision
            except Exception as e:
                logger.error(f"Agent {name} failed: {e}")
                decisions[name] = None
        
        # Synthesize ensemble decision
        return self._synthesize_decisions(decisions, context)
    
    def _get_crewai_decision(self, agent, context):
        """Get decision from CrewAI agent"""
        # This would use CrewAI's task system
        # For now, return placeholder
        return {'action': 'HOLD', 'confidence': 0.5, 'agent': agent.role}
    
    def _synthesize_decisions(self, decisions: dict, context: HRMReasoningContext) -> dict:
        """Synthesize decisions from multiple agents"""
        valid_decisions = {k: v for k, v in decisions.items() if v is not None}
        
        if not valid_decisions:
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': 'All agents failed'}
        
        # Weight by market regime
        market_data = context.market_data
        regime = self._detect_market_regime(market_data)
        
        if regime == 'pattern_recognition':
            weights = {'arc': 0.2, 'sudoku': 0.6, 'maze': 0.2}
        elif regime == 'optimization':
            weights = {'arc': 0.2, 'sudoku': 0.2, 'maze': 0.6}
        else:
            weights = {'arc': 0.5, 'sudoku': 0.3, 'maze': 0.2}
        
        # Weighted voting
        action_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_confidence = 0.0
        
        for agent_name, decision in valid_decisions.items():
            if decision and 'action' in decision:
                action = decision.get('action', 'HOLD')
                confidence = decision.get('confidence', 0.0)
                weight = weights.get(agent_name, 0.33)
                
                if action in action_scores:
                    action_scores[action] += confidence * weight
                total_confidence += confidence * weight
        
        # Select best action
        best_action = max(action_scores, key=action_scores.get)
        final_confidence = action_scores[best_action] / max(total_confidence, 0.001)
        
        return {
            'action': best_action,
            'confidence': min(final_confidence, 1.0),
            'agent_decisions': valid_decisions,
            'weights': weights,
            'regime': regime,
            'ensemble': True
        }
    
    def _detect_market_regime(self, market_data: dict) -> str:
        """Detect current market regime"""
        if 'indicators' in market_data:
            indicators = market_data['indicators']
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            
            if abs(rsi - 50) > 20:
                return 'pattern_recognition'
            elif abs(macd) > 1.0:
                return 'optimization'
        
        return 'general'
