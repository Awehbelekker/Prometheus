# optimization_engine.py
# Stub for optimization logic

from typing import Dict, Any
import statistics

class OptimizationEngine:
    def __init__(self):
        pass

    async def optimize(self, workflow_data):
        # Optimize workflow or agent actions
        pass

class SolutionOptimizationEngine:
    """
    Scores and ranks agent outputs to select the optimal solution.
    """
    def __init__(self):
        pass

    def score_outputs(self, agent_outputs: Dict[str, Any]) -> Dict[str, float]:
        scores = {}
        for agent_id, output in agent_outputs.items():
            score = 0.0
            if "innovation_score" in output:
                score += output["innovation_score"] * 0.4
            if "market_fit_score" in output:
                score += output["market_fit_score"] * 0.4
            if "performance_requirements" in output:
                perf = output["performance_requirements"]
                if isinstance(perf, dict) and "response_time" in perf:
                    try:
                        val = float(str(perf["response_time"]).replace("<", "").replace("ms", ""))
                        score += max(0, 10 - val / 100) * 0.2
                    except Exception:
                        pass
            scores[agent_id] = score
        return scores

    def select_best(self, agent_outputs: Dict[str, Any]) -> str:
        scores = self.score_outputs(agent_outputs)
        if not scores:
            return None
        return max(scores, key=scores.get)
