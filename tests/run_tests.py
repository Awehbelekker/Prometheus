#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Comprehensive Test Runner
Enterprise-grade test execution with detailed reporting
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class PrometheusTestRunner:
    """Comprehensive test runner for PROMETHEUS Trading Platform."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "overall_stats": {},
            "coverage_report": {},
            "performance_metrics": {}
        }
    
    def setup_test_environment(self):
        """Setup test environment and dependencies."""
        print("🔧 Setting up test environment...")
        
        # Set environment variables
        os.environ["TESTING"] = "true"
        os.environ["DATABASE_URL"] = "sqlite:///test_prometheus.db"
        os.environ["DISABLE_LIVE_TRADING"] = "true"
        os.environ["MOCK_MARKET_DATA"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        # Install test dependencies if needed
        try:
            import pytest
            import coverage
            import httpx
        except ImportError:
            print("📦 Installing test dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "pytest", "pytest-asyncio", "pytest-cov",
                "httpx", "coverage"
            ], check=True)
        
        print("[CHECK] Test environment ready")
    
    def run_unit_tests(self):
        """Run unit tests with coverage."""
        print("\n🧪 Running Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--cov=core",
            "--cov=api",
            "--cov=brokers",
            "--cov-report=json",
            "--cov-report=html:htmlcov",
            "--junit-xml=test_results/unit_tests.xml",
            "-m", "unit"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["test_suites"]["unit_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("[CHECK] Unit tests passed")
        else:
            print("[ERROR] Unit tests failed")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("\n🔗 Running Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "--junit-xml=test_results/integration_tests.xml",
            "-m", "integration"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["test_suites"]["integration_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("[CHECK] Integration tests passed")
        else:
            print("[ERROR] Integration tests failed")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_performance_tests(self):
        """Run performance tests."""
        print("\n[LIGHTNING] Running Performance Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-v",
            "--tb=short",
            "--junit-xml=test_results/performance_tests.xml",
            "-m", "performance"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["test_suites"]["performance_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("[CHECK] Performance tests passed")
        else:
            print("[ERROR] Performance tests failed")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_security_tests(self):
        """Run security tests."""
        print("\n🔒 Running Security Tests...")
        
        # Run security-focused tests
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/test_security_auth.py",
            "-v",
            "--tb=short",
            "--junit-xml=test_results/security_tests.xml",
            "-m", "security"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["test_suites"]["security_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0
        }
        
        if result.returncode == 0:
            print("[CHECK] Security tests passed")
        else:
            print("[ERROR] Security tests failed")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    
    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print("\n📊 Generating Coverage Report...")
        
        try:
            # Load coverage data
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                self.test_results["coverage_report"] = {
                    "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "files_covered": len(coverage_data.get("files", {})),
                    "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "lines_total": coverage_data.get("totals", {}).get("num_statements", 0)
                }
                
                coverage_percent = self.test_results["coverage_report"]["total_coverage"]
                print(f"📈 Code Coverage: {coverage_percent:.1f}%")
                
                if coverage_percent >= 80:
                    print("[CHECK] Coverage target achieved (≥80%)")
                else:
                    print("[WARNING]️  Coverage below target (<80%)")
            
        except Exception as e:
            print(f"[WARNING]️  Could not generate coverage report: {e}")
    
    def run_all_tests(self, test_types=None):
        """Run all test suites."""
        if test_types is None:
            test_types = ["unit", "integration", "performance", "security"]
        
        print("🚀 Starting PROMETHEUS Trading Platform Test Suite")
        print("=" * 60)
        
        # Setup
        self.setup_test_environment()
        
        # Create results directory
        results_dir = self.project_root / "test_results"
        results_dir.mkdir(exist_ok=True)
        
        # Run test suites
        all_passed = True
        
        if "unit" in test_types:
            all_passed &= self.run_unit_tests()
        
        if "integration" in test_types:
            all_passed &= self.run_integration_tests()
        
        if "performance" in test_types:
            all_passed &= self.run_performance_tests()
        
        if "security" in test_types:
            all_passed &= self.run_security_tests()
        
        # Generate reports
        self.generate_coverage_report()
        
        # Calculate overall stats
        total_suites = len(self.test_results["test_suites"])
        passed_suites = sum(1 for suite in self.test_results["test_suites"].values() if suite["passed"])
        
        self.test_results["overall_stats"] = {
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": total_suites - passed_suites,
            "success_rate": (passed_suites / total_suites) * 100 if total_suites > 0 else 0,
            "all_passed": all_passed
        }
        
        # Save results
        results_file = results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        self.print_summary()
        
        return all_passed
    
    def print_summary(self):
        """Print test execution summary."""
        print("\n" + "=" * 60)
        print("📋 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        stats = self.test_results["overall_stats"]
        
        print(f"Total Test Suites: {stats['total_suites']}")
        print(f"Passed: {stats['passed_suites']}")
        print(f"Failed: {stats['failed_suites']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        
        if "coverage_report" in self.test_results and self.test_results["coverage_report"]:
            coverage = self.test_results["coverage_report"]
            print(f"Code Coverage: {coverage['total_coverage']:.1f}%")
        
        print("\n📁 Test Reports Generated:")
        print("  - HTML Reports: test_results/*.html")
        print("  - XML Reports: test_results/*.xml")
        print("  - Coverage Report: htmlcov/index.html")
        
        if stats["all_passed"]:
            print("\n🎉 ALL TESTS PASSED! System ready for enterprise launch.")
        else:
            print("\n[WARNING]️  SOME TESTS FAILED. Review results before launch.")
        
        print("=" * 60)


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="PROMETHEUS Trading Platform Test Runner")
    parser.add_argument(
        "--tests",
        nargs="+",
        choices=["unit", "integration", "performance", "security"],
        default=["unit", "integration", "performance", "security"],
        help="Test types to run"
    )
    
    args = parser.parse_args()
    
    runner = PrometheusTestRunner()
    success = runner.run_all_tests(args.tests)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
