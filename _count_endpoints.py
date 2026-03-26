"""Count endpoints and AI systems."""
import re
code = open('unified_production_server.py', 'r', encoding='utf-8').read()
endpoints = re.findall(r'@app\.(get|post|put|delete|patch)\(', code)
registry = re.findall(r'_ai_systems_registry\s*=\s*\{', code)
# Count entries in registry
block = code[code.index('_ai_systems_registry = {'):]
block = block[:block.index('}') + 1]
entries = re.findall(r'"(\w+)":\s*\{', block)
print(f'Total API endpoints: {len(endpoints)}')
print(f'AI subsystems in registry: {len(entries)}')
# Count new Phase 21 endpoints
new_eps = re.findall(r'@app\.(get|post)\("/api/(ai|data|system)/(langgraph|openbb|ccxt|gymnasium|mercury2|cache)', code)
print(f'New Phase 21 endpoints: {len(new_eps)}')
