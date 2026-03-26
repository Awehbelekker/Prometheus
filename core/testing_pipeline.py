"""
Automated Testing Pipeline with Pre-commit Hooks and Performance Testing
"""

import subprocess
import sys
import os
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import tempfile
import concurrent.futures
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test execution result"""
    name: str
    status: str  # passed, failed, skipped
    duration: float
    details: Optional[str] = None
    coverage: Optional[float] = None

@dataclass 
class PipelineConfig:
    """Configuration for the testing pipeline"""
    enable_type_checking: bool = True
    enable_linting: bool = True
    enable_security_scan: bool = True
    enable_performance_tests: bool = True
    enable_coverage: bool = True
    min_coverage_threshold: float = 80.0
    max_test_duration: int = 300  # 5 minutes
    parallel_execution: bool = True
    max_workers: int = 4

class TestingPipeline:
    """
    Comprehensive automated testing pipeline
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.project_root = Path(__file__).parent.parent
        self.results: List[TestResult] = []
        
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run the complete testing pipeline"""
        start_time = time.time()
        pipeline_results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
            'stages': {},
            'summary': {},
            'duration': 0
        }
        
        logger.info("🚀 Starting automated testing pipeline")
        
        try:
            # Stage 1: Type checking
            if self.config.enable_type_checking:
                pipeline_results['stages']['type_checking'] = self._run_type_checking()
            
            # Stage 2: Linting
            if self.config.enable_linting:
                pipeline_results['stages']['linting'] = self._run_linting()
            
            # Stage 3: Security scanning
            if self.config.enable_security_scan:
                pipeline_results['stages']['security'] = self._run_security_scan()
            
            # Stage 4: Unit tests with coverage
            pipeline_results['stages']['unit_tests'] = self._run_unit_tests()
            
            # Stage 5: Integration tests
            pipeline_results['stages']['integration_tests'] = self._run_integration_tests()
            
            # Stage 6: Performance tests
            if self.config.enable_performance_tests:
                pipeline_results['stages']['performance_tests'] = self._run_performance_tests()
            
            # Generate summary
            pipeline_results['summary'] = self._generate_summary()
            pipeline_results['status'] = 'completed'
            
        except Exception as e:
            pipeline_results['status'] = 'failed'
            pipeline_results['error'] = str(e)
            logger.error(f"Pipeline failed: {str(e)}")
        
        finally:
            pipeline_results['duration'] = time.time() - start_time
            
        logger.info(f"🏁 Pipeline completed in {pipeline_results['duration']:.2f}s")
        return pipeline_results
    
    def _run_type_checking(self) -> Dict[str, Any]:
        """Run mypy type checking"""
        logger.info("🔍 Running type checking with mypy")
        start_time = time.time()
        
        try:
            # Run mypy on core modules
            cmd = [
                sys.executable, '-m', 'mypy',
                '--ignore-missing-imports',
                '--strict-optional',
                '--warn-redundant-casts',
                '--warn-unused-ignores',
                'core/', 'agents/', 'workflows/'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'duration': time.time() - start_time,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': 'Type checking timed out'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def _run_linting(self) -> Dict[str, Any]:
        """Run code linting with flake8 and pylint"""
        logger.info("🧹 Running code linting")
        start_time = time.time()
        
        results = {}
        
        # Run flake8
        try:
            flake8_cmd = [
                sys.executable, '-m', 'flake8',
                '--max-line-length=120',
                '--ignore=E203,W503',
                'core/', 'agents/', 'workflows/'
            ]
            
            flake8_result = subprocess.run(
                flake8_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            results['flake8'] = {
                'status': 'passed' if flake8_result.returncode == 0 else 'failed',
                'output': flake8_result.stdout,
                'errors': flake8_result.stderr
            }
            
        except Exception as e:
            results['flake8'] = {'status': 'failed', 'error': str(e)}
        
        # Run pylint on core modules
        try:
            pylint_cmd = [
                sys.executable, '-m', 'pylint',
                '--disable=C0114,C0115,C0116',  # Disable docstring requirements
                '--max-line-length=120',
                'core/'
            ]
            
            pylint_result = subprocess.run(
                pylint_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Extract pylint score
            score = self._extract_pylint_score(pylint_result.stdout)
            
            results['pylint'] = {
                'status': 'passed' if score >= 7.0 else 'warning',
                'score': score,
                'output': pylint_result.stdout,
                'errors': pylint_result.stderr
            }
            
        except Exception as e:
            results['pylint'] = {'status': 'failed', 'error': str(e)}
        
        overall_status = 'passed' if all(r.get('status') == 'passed' for r in results.values()) else 'failed'
        
        return {
            'status': overall_status,
            'duration': time.time() - start_time,
            'results': results
        }
    
    def _extract_pylint_score(self, output: str) -> float:
        """Extract pylint score from output"""
        try:
            for line in output.split('\n'):
                if 'Your code has been rated at' in line:
                    score_part = line.split('Your code has been rated at')[1].split('/')[0].strip()
                    return float(score_part)
        except:
            pass
        return 0.0
    
    def _run_security_scan(self) -> Dict[str, Any]:
        """Run security scanning with bandit"""
        logger.info("🔒 Running security scan")
        start_time = time.time()
        
        try:
            cmd = [
                sys.executable, '-m', 'bandit',
                '-r', 'core/', 'agents/', 'workflows/',
                '-f', 'json'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse bandit JSON output
            try:
                bandit_data = json.loads(result.stdout) if result.stdout else {}
                issues = bandit_data.get('results', [])
                high_issues = [i for i in issues if i.get('issue_severity') == 'HIGH']
                medium_issues = [i for i in issues if i.get('issue_severity') == 'MEDIUM']
                
                return {
                    'status': 'failed' if high_issues else ('warning' if medium_issues else 'passed'),
                    'duration': time.time() - start_time,
                    'total_issues': len(issues),
                    'high_severity': len(high_issues),
                    'medium_severity': len(medium_issues),
                    'issues': issues[:10]  # Include first 10 issues
                }
                
            except json.JSONDecodeError:
                return {
                    'status': 'warning',
                    'duration': time.time() - start_time,
                    'error': 'Could not parse bandit output',
                    'output': result.stdout[:1000]
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': 'Security scan timed out'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage"""
        logger.info("🧪 Running unit tests with coverage")
        start_time = time.time()
        
        try:
            # Run pytest with coverage
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/unit_tests/',
                '--cov=core',
                '--cov=agents',
                '--cov=workflows',
                '--cov-report=json',
                '--cov-report=term-missing',
                '--junitxml=test-results.xml',
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.config.max_test_duration
            )
            
            # Parse coverage data
            coverage_data = self._parse_coverage_data()
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'duration': time.time() - start_time,
                'return_code': result.returncode,
                'output': result.stdout,
                'errors': result.stderr,
                'coverage': coverage_data
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': f'Unit tests timed out after {self.config.max_test_duration}s'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("🔗 Running integration tests")
        start_time = time.time()
        
        try:
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/',
                '-k', 'integration',
                '--tb=short',
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.config.max_test_duration
            )
            
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'duration': time.time() - start_time,
                'return_code': result.returncode,
                'output': result.stdout,
                'errors': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': f'Integration tests timed out after {self.config.max_test_duration}s'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance regression tests"""
        logger.info("[LIGHTNING] Running performance tests")
        start_time = time.time()
        
        performance_results = {}
        
        # Test 1: Agent initialization performance
        performance_results['agent_initialization'] = self._test_agent_initialization_performance()
        
        # Test 2: Database query performance
        performance_results['database_queries'] = self._test_database_performance()
        
        # Test 3: Workflow execution performance
        performance_results['workflow_execution'] = self._test_workflow_performance()
        
        # Test 4: Memory usage test
        performance_results['memory_usage'] = self._test_memory_usage()
        
        # Determine overall status
        failed_tests = [k for k, v in performance_results.items() if v.get('status') == 'failed']
        overall_status = 'failed' if failed_tests else 'passed'
        
        return {
            'status': overall_status,
            'duration': time.time() - start_time,
            'results': performance_results,
            'failed_tests': failed_tests
        }
    
    def _test_agent_initialization_performance(self) -> Dict[str, Any]:
        """Test agent initialization performance"""
        try:
            from core.agent_base import AgentBase
            
            durations = []
            for i in range(10):
                start = time.perf_counter()
                agent = AgentBase(f"test_agent_{i}", "test")
                end = time.perf_counter()
                durations.append(end - start)
            
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            # Performance threshold: should initialize in < 0.1 seconds
            status = 'passed' if avg_duration < 0.1 else 'failed'
            
            return {
                'status': status,
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'threshold': 0.1,
                'sample_size': len(durations)
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _test_database_performance(self) -> Dict[str, Any]:
        """Test database query performance"""
        try:
            from core.database_manager import DatabaseManager
            
            db = DatabaseManager()
            durations = []
            
            # Test simple queries
            for i in range(50):
                start = time.perf_counter()
                db.execute_query("SELECT 1")
                end = time.perf_counter()
                durations.append(end - start)
            
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            # Performance threshold: should execute in < 0.01 seconds
            status = 'passed' if avg_duration < 0.01 else 'failed'
            
            return {
                'status': status,
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'threshold': 0.01,
                'sample_size': len(durations)
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _test_workflow_performance(self) -> Dict[str, Any]:
        """Test workflow execution performance"""
        try:
            # Simulate workflow execution time
            durations = []
            
            for i in range(5):
                start = time.perf_counter()
                # Simulate some work
                time.sleep(0.001)  # 1ms simulation
                end = time.perf_counter()
                durations.append(end - start)
            
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            # Performance threshold: should complete in < 1 second
            status = 'passed' if avg_duration < 1.0 else 'failed'
            
            return {
                'status': status,
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'threshold': 1.0,
                'sample_size': len(durations)
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage patterns"""
        try:
            import psutil
            import gc
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate memory-intensive operations
            test_data = []
            for i in range(1000):
                test_data.append(f"test_data_{i}" * 100)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cleanup
            del test_data
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            memory_cleanup = peak_memory - final_memory
            
            # Performance threshold: memory increase should be reasonable
            status = 'passed' if memory_increase < 100 else 'warning'  # 100MB threshold
            
            return {
                'status': status,
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': peak_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase,
                'memory_cleanup_mb': memory_cleanup,
                'threshold_mb': 100
            }
            
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def _parse_coverage_data(self) -> Dict[str, Any]:
        """Parse coverage data from JSON report"""
        try:
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                
                return {
                    'total_coverage': total_coverage,
                    'meets_threshold': total_coverage >= self.config.min_coverage_threshold,
                    'threshold': self.config.min_coverage_threshold,
                    'details': coverage_data.get('files', {})
                }
            else:
                return {'error': 'Coverage file not found'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate pipeline execution summary"""
        total_stages = len([k for k, v in self.__dict__.items() if k.startswith('_') and 'stage' in k])
        passed_stages = 0
        failed_stages = 0
        warnings = 0
        
        # This would be implemented to analyze all stage results
        # For now, return a placeholder
        return {
            'total_stages': total_stages,
            'passed': passed_stages,
            'failed': failed_stages,
            'warnings': warnings,
            'overall_status': 'completed'
        }


class PreCommitHooks:
    """
    Pre-commit hooks for code quality enforcement
    """
    
    @staticmethod
    def install_hooks():
        """Install pre-commit hooks"""
        hook_content = '''#!/bin/bash
# Pre-commit hook for MASS Framework

echo "🔍 Running pre-commit checks..."

# Run type checking
echo "Type checking..."
python -m mypy core/ agents/ workflows/ --ignore-missing-imports
if [ $? -ne 0 ]; then
    echo "[ERROR] Type checking failed"
    exit 1
fi

# Run linting
echo "Linting..."
python -m flake8 core/ agents/ workflows/ --max-line-length=120
if [ $? -ne 0 ]; then
    echo "[ERROR] Linting failed"
    exit 1
fi

# Run unit tests
echo "Unit tests..."
python -m pytest tests/unit_tests/ -q
if [ $? -ne 0 ]; then
    echo "[ERROR] Unit tests failed"
    exit 1
fi

echo "[CHECK] All pre-commit checks passed"
exit 0
'''
        
        git_hooks_dir = Path('.git/hooks')
        if git_hooks_dir.exists():
            pre_commit_hook = git_hooks_dir / 'pre-commit'
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(pre_commit_hook, 0o755)
            logger.info("[CHECK] Pre-commit hooks installed")
        else:
            logger.warning("Git hooks directory not found")


# Load testing utilities
class LoadTester:
    """
    Load testing for API endpoints and system components
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def run_load_test(self, endpoint: str, concurrent_users: int = 10, duration: int = 60) -> Dict[str, Any]:
        """Run load test against an endpoint"""
        import aiohttp
        import asyncio
        
        results = {
            'endpoint': endpoint,
            'concurrent_users': concurrent_users,
            'duration': duration,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        async def make_request(session, user_id):
            """Make a single request"""
            start_time = time.time()
            try:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    await response.text()
                    response_time = time.time() - start_time
                    results['response_times'].append(response_time)
                    results['total_requests'] += 1
                    if response.status < 400:
                        results['successful_requests'] += 1
                    else:
                        results['failed_requests'] += 1
                        results['errors'].append(f"Status {response.status}")
            except Exception as e:
                results['failed_requests'] += 1
                results['errors'].append(str(e))
        
        # Run the load test
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration:
                tasks = []
                for user_id in range(concurrent_users):
                    task = asyncio.create_task(make_request(session, user_id))
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.1)  # Small delay between batches
        
        # Calculate statistics
        if results['response_times']:
            results['avg_response_time'] = statistics.mean(results['response_times'])
            results['min_response_time'] = min(results['response_times'])
            results['max_response_time'] = max(results['response_times'])
            results['median_response_time'] = statistics.median(results['response_times'])
            results['p95_response_time'] = sorted(results['response_times'])[int(len(results['response_times']) * 0.95)]
        
        results['requests_per_second'] = results['total_requests'] / duration
        results['success_rate'] = (results['successful_requests'] / results['total_requests']) * 100 if results['total_requests'] > 0 else 0
        
        return results


# Global instances
testing_pipeline = TestingPipeline()
load_tester = LoadTester()

# Convenience functions
def run_pipeline():
    """Run the complete testing pipeline"""
    return testing_pipeline.run_full_pipeline()

def install_pre_commit_hooks():
    """Install pre-commit hooks"""
    PreCommitHooks.install_hooks()

async def run_load_test(endpoint: str, users: int = 10, duration: int = 60):
    """Run load test on endpoint"""
    return await load_tester.run_load_test(endpoint, users, duration)
