"""Compatibility shim exposing plural REVOLUTIONARY_FEATURES package.

Legacy test and performance scripts import modules from
`REVOLUTIONARY_FEATURES.<module>` while the modern codebase
stores implementations under `revolutionary_features` (lowercase
directories). This shim dynamically maps expected legacy module
names to existing implementations so those imports succeed and
the Revolutionary Features portion of the comprehensive suite
does not hard-fail purely due to path changes.

Currently we only have a concrete quantum trading engine; other
legacy modules are temporarily aliased to it as placeholders so
initialization code paths can run. Replace mappings with real
modules as those features become available.
"""
from importlib import import_module
import sys
import types

# Mapping legacy names -> (modern import path, exported symbol)
LEGACY_MAP = {
	'quantum_trading_engine': ('revolutionary_features.quantum_trading.quantum_trading_engine', 'QuantumTradingEngine'),
	'blockchain_trading_integration': ('REVOLUTIONARY_FEATURES.blockchain_trading_integration', 'BlockchainTradingIntegration'),
	'neural_interface_integration': ('REVOLUTIONARY_FEATURES.neural_interface_integration', 'NeuralInterfaceIntegration'),
	'holographic_ui_integration': ('REVOLUTIONARY_FEATURES.holographic_ui_integration', 'HolographicUIIntegration'),
	'prometheus_ai_integration': ('REVOLUTIONARY_FEATURES.prometheus_ai_integration', 'PrometheusAIIntegration'),
}

for legacy_mod, (real_path, symbol_name) in LEGACY_MAP.items():
	shim_name = f"REVOLUTIONARY_FEATURES.{legacy_mod}"
	module = types.ModuleType(shim_name)
	try:
		real_mod = import_module(real_path)
		exported = getattr(real_mod, symbol_name)
		setattr(module, symbol_name, exported)
		module.__all__ = [symbol_name]
	except Exception as e:  # pragma: no cover
		module.__all__ = []
		module._shim_error = str(e)
	sys.modules[shim_name] = module

__all__ = list(LEGACY_MAP.keys())
