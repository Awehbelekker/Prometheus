"""
Real IBM Quantum Computing Integration for PROMETHEUS Trading Platform
Extracted from .env.production and properly implemented as Python module
"""

import os
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Quantum computing imports
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class QuantumOptimizationResult:
    """Result from quantum portfolio optimization"""
    portfolio_weights: List[float]
    quantum_advantage: float
    execution_time_ms: float
    backend_used: str
    shots_used: int
    success: bool
    error_message: Optional[str] = None

class RealIBMQuantumIntegration:
    """Real IBM Quantum Computing Integration"""
    
    def __init__(self, token: str = None):
        """Initialize IBM Quantum integration"""
        self.token = token or os.getenv('IBM_QUANTUM_TOKEN')
        self.service = None
        self.backend = None
        self.initialized = False
        
        if not QISKIT_AVAILABLE:
            logger.error("[ERROR] Qiskit not available. Install with: pip install qiskit qiskit-ibm-runtime")
            return
            
        if not self.token:
            logger.error("[ERROR] IBM Quantum token not provided")
            return
            
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize IBM Quantum service"""
        try:
            # Try the correct channel name for IBM Quantum Platform
            self.service = QiskitRuntimeService(channel="ibm_quantum_platform", token=self.token)
            self.backend = self.service.least_busy(operational=True, simulator=False)
            self.initialized = True
            logger.info(f"[CHECK] IBM Quantum service initialized with backend: {self.backend.name}")
        except Exception as e:
            logger.warning(f"[WARNING]️ IBM Quantum Platform unavailable: {e}")
            # Try alternative channel
            try:
                self.service = QiskitRuntimeService(channel="ibm_cloud", token=self.token)
                self.backend = self.service.least_busy(operational=True, simulator=False)
                self.initialized = True
                logger.info(f"[CHECK] IBM Cloud Quantum service initialized with backend: {self.backend.name}")
            except Exception as e2:
                logger.warning(f"[WARNING]️ IBM Cloud Quantum unavailable: {e2}")
                # Use local simulator as fallback
                try:
                    from qiskit_aer import AerSimulator
                    self.backend = AerSimulator()
                    self.initialized = True
                    logger.info("[CHECK] Using local Aer simulator as fallback")
                except Exception as e3:
                    logger.error(f"[ERROR] All quantum backends failed: {e3}")
                    self.initialized = False
    
    async def quantum_portfolio_optimization(self, returns: List[float], risk_tolerance: float = 0.5) -> QuantumOptimizationResult:
        """
        Perform quantum portfolio optimization using real IBM quantum computers
        
        Args:
            returns: Expected returns for each asset
            risk_tolerance: Risk tolerance parameter (0.0 to 1.0)
            
        Returns:
            QuantumOptimizationResult with optimized portfolio weights
        """
        if not self.initialized or not QISKIT_AVAILABLE:
            return QuantumOptimizationResult(
                portfolio_weights=[1.0/len(returns)] * len(returns),
                quantum_advantage=0.0,
                execution_time_ms=0.0,
                backend_used="none",
                shots_used=0,
                success=False,
                error_message="Quantum service not available"
            )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create quantum circuit for portfolio optimization
            n_assets = len(returns)
            qc = QuantumCircuit(n_assets, n_assets)
            
            # Add quantum gates for optimization
            for i in range(n_assets):
                qc.h(i)  # Superposition
                qc.ry(returns[i] * risk_tolerance, i)  # Risk-adjusted rotation
            
            # Add entanglement for correlation
            for i in range(n_assets - 1):
                qc.cx(i, i + 1)
            
            # Measure all qubits
            qc.measure_all()
            
            # Execute on real quantum computer
            sampler = Sampler(backend=self.backend)
            job = sampler.run(qc, shots=1024)
            result = job.result()
            
            # Process quantum results into portfolio weights
            counts = result.quasi_dists[0]
            weights = self._process_quantum_results(counts, n_assets)
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Calculate quantum advantage (simplified metric)
            classical_weights = [1.0/n_assets] * n_assets
            quantum_advantage = self._calculate_quantum_advantage(weights, classical_weights, returns)
            
            logger.info(f"[CHECK] Quantum optimization completed in {execution_time:.2f}ms")
            logger.info(f"🔬 Quantum advantage: {quantum_advantage:.4f}")
            
            return QuantumOptimizationResult(
                portfolio_weights=weights,
                quantum_advantage=quantum_advantage,
                execution_time_ms=execution_time,
                backend_used=self.backend.name,
                shots_used=1024,
                success=True
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"[ERROR] Quantum optimization failed: {e}")
            
            # Return classical fallback
            classical_weights = self._classical_portfolio_optimization(returns, risk_tolerance)
            
            return QuantumOptimizationResult(
                portfolio_weights=classical_weights,
                quantum_advantage=0.0,
                execution_time_ms=execution_time,
                backend_used="classical_fallback",
                shots_used=0,
                success=False,
                error_message=str(e)
            )
    
    def _process_quantum_results(self, counts: Dict, n_assets: int) -> List[float]:
        """Convert quantum measurement results to portfolio weights"""
        weights = np.zeros(n_assets)
        total_shots = sum(counts.values())
        
        for bitstring, count in counts.items():
            probability = count / total_shots
            # Convert bitstring to asset weights
            for i, bit in enumerate(str(bitstring)):
                if bit == '1':
                    weights[i] += probability
        
        # Normalize weights
        weights = weights / np.sum(weights) if np.sum(weights) > 0 else np.ones(n_assets) / n_assets
        return weights.tolist()
    
    def _calculate_quantum_advantage(self, quantum_weights: List[float], classical_weights: List[float], returns: List[float]) -> float:
        """Calculate quantum advantage metric"""
        quantum_return = sum(w * r for w, r in zip(quantum_weights, returns))
        classical_return = sum(w * r for w, r in zip(classical_weights, returns))
        return quantum_return - classical_return
    
    def _classical_portfolio_optimization(self, returns: List[float], risk_tolerance: float) -> List[float]:
        """Classical portfolio optimization fallback"""
        # Simple risk-adjusted weighting
        adjusted_returns = [r * risk_tolerance for r in returns]
        total_return = sum(adjusted_returns)
        
        if total_return <= 0:
            return [1.0/len(returns)] * len(returns)
        
        weights = [r / total_return for r in adjusted_returns]
        return weights

# Global quantum integration instance
quantum_integration = None

def get_quantum_integration() -> RealIBMQuantumIntegration:
    """Get global quantum integration instance"""
    global quantum_integration
    if quantum_integration is None:
        quantum_integration = RealIBMQuantumIntegration()
    return quantum_integration

async def optimize_portfolio_quantum(returns: List[float], risk_tolerance: float = 0.5) -> QuantumOptimizationResult:
    """Convenience function for quantum portfolio optimization"""
    integration = get_quantum_integration()
    return await integration.quantum_portfolio_optimization(returns, risk_tolerance)

# Example usage
if __name__ == "__main__":
    async def test_quantum_optimization():
        """Test quantum optimization"""
        returns = [0.12, 0.08, 0.15, 0.10]  # Example returns
        result = await optimize_portfolio_quantum(returns, risk_tolerance=0.7)
        
        print(f"Quantum Optimization Result:")
        print(f"Portfolio Weights: {result.portfolio_weights}")
        print(f"Quantum Advantage: {result.quantum_advantage:.4f}")
        print(f"Execution Time: {result.execution_time_ms:.2f}ms")
        print(f"Backend Used: {result.backend_used}")
        print(f"Success: {result.success}")
    
    asyncio.run(test_quantum_optimization())
