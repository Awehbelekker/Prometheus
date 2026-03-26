#!/usr/bin/env python3
"""
Set up comprehensive testing framework
Safe to run during active trading - just creates test infrastructure
"""

import os
import sys
from pathlib import Path
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create test directory structure"""
    logger.info("Creating test directory structure...")
    
    directories = [
        'tests',
        'tests/unit',
        'tests/integration',
        'tests/e2e',
        'tests/fixtures',
        'tests/mocks',
        'reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"  [CHECK] {directory}/")
    
    logger.info("")

def install_dependencies():
    """Install testing dependencies"""
    logger.info("Installing testing dependencies...")
    
    dependencies = [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'pytest-mock',
        'pytest-timeout',
        'pytest-xdist',  # Parallel testing
        'bandit',  # Security
        'safety',  # Security
        'pip-audit',  # Security
        'locust',  # Load testing
    ]
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install'] + dependencies,
            check=True,
            capture_output=True
        )
        logger.info("  [CHECK] All dependencies installed")
    except subprocess.CalledProcessError as e:
        logger.error(f"  [ERROR] Failed to install dependencies: {e}")
    
    logger.info("")

def create_pytest_config():
    """Create pytest configuration"""
    logger.info("Creating pytest configuration...")
    
    config = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --verbose
    --cov=core
    --cov=brokers
    --cov=services
    --cov-report=html
    --cov-report=term-missing
    --maxfail=5
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    security: Security tests
"""
    
    with open('pytest.ini', 'w') as f:
        f.write(config)
    
    logger.info("  [CHECK] pytest.ini created")
    logger.info("")

def create_example_tests():
    """Create example test files"""
    logger.info("Creating example test files...")
    
    # Unit test example
    unit_test = '''"""Example unit tests for PROMETHEUS"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestSystemImports:
    """Test that core systems can be imported"""
    
    def test_import_trading_engine(self):
        """Test trading engine import"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        assert AdvancedTradingEngine is not None
    
    def test_import_market_data(self):
        """Test market data import"""
        from core.real_time_market_data import RealTimeMarketDataOrchestrator
        assert RealTimeMarketDataOrchestrator is not None
    
    def test_import_brokers(self):
        """Test broker imports"""
        from brokers.alpaca_broker import AlpacaBroker
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        assert AlpacaBroker is not None
        assert InteractiveBrokersBroker is not None

class TestRiskManagement:
    """Test risk management functionality"""
    
    def test_risk_limits_exist(self):
        """Test that risk limits are defined"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        engine = AdvancedTradingEngine()
        
        assert hasattr(engine, 'risk_limits')
        assert 'max_position_size' in engine.risk_limits
        assert 'max_daily_risk' in engine.risk_limits
    
    def test_risk_limits_values(self):
        """Test risk limit values are reasonable"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        engine = AdvancedTradingEngine()
        
        assert 0 < engine.risk_limits['max_position_size'] <= 1.0
        assert 0 < engine.risk_limits['max_daily_risk'] <= 1.0

@pytest.mark.asyncio
class TestAsyncFunctions:
    """Test async functionality"""
    
    async def test_async_example(self):
        """Example async test"""
        import asyncio
        await asyncio.sleep(0.1)
        assert True
'''
    
    with open('tests/unit/test_example.py', 'w') as f:
        f.write(unit_test)
    
    logger.info("  [CHECK] tests/unit/test_example.py")
    
    # Integration test example
    integration_test = '''"""Example integration tests"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.mark.integration
class TestBrokerIntegration:
    """Test broker integration"""
    
    @pytest.mark.asyncio
    async def test_alpaca_connection(self):
        """Test Alpaca broker connection"""
        # This would test actual broker connection
        # For now, just a placeholder
        assert True
    
    @pytest.mark.asyncio
    async def test_market_data_fetch(self):
        """Test market data fetching"""
        # This would test actual market data retrieval
        assert True
'''
    
    with open('tests/integration/test_broker_integration.py', 'w') as f:
        f.write(integration_test)
    
    logger.info("  [CHECK] tests/integration/test_broker_integration.py")
    logger.info("")

def create_security_scan_script():
    """Create security scanning script"""
    logger.info("Creating security scan script...")
    
    script = '''#!/usr/bin/env python3
"""Run security scans on the codebase"""
import subprocess
import sys
import json
from datetime import datetime

def run_bandit():
    """Run Bandit security scanner"""
    print("Running Bandit security scan...")
    try:
        result = subprocess.run(
            ['bandit', '-r', '.', '-f', 'json', '-o', 'reports/security_bandit.json'],
            capture_output=True,
            text=True
        )
        print("[CHECK] Bandit scan complete: reports/security_bandit.json")
    except Exception as e:
        print(f"[ERROR] Bandit scan failed: {e}")

def run_safety():
    """Run Safety dependency checker"""
    print("\\nRunning Safety dependency check...")
    try:
        result = subprocess.run(
            ['safety', 'check', '--json'],
            capture_output=True,
            text=True
        )
        with open('reports/security_safety.json', 'w') as f:
            f.write(result.stdout)
        print("[CHECK] Safety check complete: reports/security_safety.json")
    except Exception as e:
        print(f"[ERROR] Safety check failed: {e}")

def run_pip_audit():
    """Run pip-audit"""
    print("\\nRunning pip-audit...")
    try:
        result = subprocess.run(
            ['pip-audit', '--format', 'json'],
            capture_output=True,
            text=True
        )
        with open('reports/security_pip_audit.json', 'w') as f:
            f.write(result.stdout)
        print("[CHECK] pip-audit complete: reports/security_pip_audit.json")
    except Exception as e:
        print(f"[ERROR] pip-audit failed: {e}")

if __name__ == "__main__":
    print("="*80)
    print("PROMETHEUS SECURITY SCAN")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    run_bandit()
    run_safety()
    run_pip_audit()
    
    print()
    print("="*80)
    print("Security scan complete!")
    print("Review reports in: reports/")
    print("="*80)
'''
    
    with open('scripts/run_security_scan.py', 'w') as f:
        f.write(script)
    
    # Make executable
    os.chmod('scripts/run_security_scan.py', 0o755)
    
    logger.info("  [CHECK] scripts/run_security_scan.py")
    logger.info("")

def create_readme():
    """Create testing README"""
    logger.info("Creating testing README...")
    
    readme = """# PROMETHEUS Testing Framework

## Quick Start

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only
```

### Run with Coverage
```bash
pytest --cov=core --cov-report=html
# View coverage report: htmlcov/index.html
```

### Run in Parallel
```bash
pytest -n auto  # Use all CPU cores
```

### Run Security Scans
```bash
python scripts/run_security_scan.py
```

## Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
├── integration/       # Integration tests (slower, external deps)
├── e2e/              # End-to-end tests (full system)
├── fixtures/         # Test data and fixtures
└── mocks/            # Mock objects
```

## Writing Tests

### Unit Test Example
```python
import pytest

def test_example():
    assert 1 + 1 == 2

@pytest.mark.asyncio
async def test_async_example():
    import asyncio
    await asyncio.sleep(0.1)
    assert True
```

### Integration Test Example
```python
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_broker_connection():
    # Test actual broker connection
    pass
```

## Reports

- Coverage: `htmlcov/index.html`
- Security: `reports/security_*.json`
"""
    
    with open('tests/README.md', 'w') as f:
        f.write(readme)
    
    logger.info("  [CHECK] tests/README.md")
    logger.info("")

def main():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("PROMETHEUS TESTING FRAMEWORK SETUP")
    logger.info("=" * 80)
    logger.info("")
    
    create_directory_structure()
    install_dependencies()
    create_pytest_config()
    create_example_tests()
    create_security_scan_script()
    create_readme()
    
    logger.info("=" * 80)
    logger.info("SETUP COMPLETE!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Run example tests: pytest tests/unit/test_example.py -v")
    logger.info("2. Run all tests: pytest")
    logger.info("3. Run security scan: python scripts/run_security_scan.py")
    logger.info("4. Write more tests in tests/unit/ and tests/integration/")
    logger.info("")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()

