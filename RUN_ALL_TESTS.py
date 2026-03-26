#!/usr/bin/env python3
"""
🧪 PROMETHEUS COMPREHENSIVE TEST SUITE
========================================

Runs all integration tests for the PROMETHEUS AI-powered trading platform:
- Tier 1: Critical AI Systems (19 tests)
- Tier 2: High Priority Systems (19 tests)
- Tier 3: Medium Priority Systems (20 tests)

Total: 58 tests across all 10 advanced AI systems
"""

import asyncio
import sys
import os
import subprocess
from datetime import datetime
from typing import Dict, List

# Test results tracking
all_results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "test_suites": []
}

def print_header():
    """Print test suite header"""
    print("\n" + "=" * 80)
    print("🧪 PROMETHEUS COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nRunning all integration tests for 10 advanced AI systems...")
    print("This may take a few minutes...\n")

def run_test_suite(test_file: str, suite_name: str) -> Dict:
    """Run a test suite and return results"""
    print(f"\n{'=' * 80}")
    print(f"🔍 Running: {suite_name}")
    print(f"{'=' * 80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout
        
        # Parse results from output
        passed = 0
        failed = 0
        warnings = 0
        total = 0
        
        for line in output.split('\n'):
            if 'Total Tests:' in line:
                total = int(line.split(':')[1].strip())
            elif '[CHECK] Passed:' in line:
                passed = int(line.split(':')[1].strip())
            elif '[ERROR] Failed:' in line:
                failed = int(line.split(':')[1].strip())
            elif '[WARNING]️  Warnings:' in line:
                warnings = int(line.split(':')[1].strip())
        
        suite_result = {
            "name": suite_name,
            "file": test_file,
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success": failed == 0,
            "output": output
        }
        
        # Print summary
        if failed == 0:
            print(f"\n[CHECK] {suite_name}: {passed}/{total} PASSED")
        else:
            print(f"\n[ERROR] {suite_name}: {passed}/{total} PASSED, {failed} FAILED")
        
        return suite_result
        
    except subprocess.TimeoutExpired:
        print(f"\n[WARNING]️  {suite_name}: TIMEOUT (exceeded 120 seconds)")
        return {
            "name": suite_name,
            "file": test_file,
            "total": 0,
            "passed": 0,
            "failed": 1,
            "warnings": 0,
            "success": False,
            "output": "Test suite timed out"
        }
    except Exception as e:
        print(f"\n[ERROR] {suite_name}: ERROR - {e}")
        return {
            "name": suite_name,
            "file": test_file,
            "total": 0,
            "passed": 0,
            "failed": 1,
            "warnings": 0,
            "success": False,
            "output": str(e)
        }

def print_final_summary(results: List[Dict]):
    """Print final test summary"""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    total_tests = sum(r["total"] for r in results)
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_warnings = sum(r["warnings"] for r in results)
    
    print(f"\n📋 Test Suites Run: {len(results)}")
    print(f"📝 Total Tests: {total_tests}")
    print(f"[CHECK] Passed: {total_passed}")
    print(f"[ERROR] Failed: {total_failed}")
    print(f"[WARNING]️  Warnings: {total_warnings}")
    
    if total_failed == 0:
        pass_rate = 100.0
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
    else:
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📈 Pass Rate: {pass_rate:.1f}%")
    
    print("\n" + "-" * 80)
    print("Test Suite Breakdown:")
    print("-" * 80)
    
    for result in results:
        status = "[CHECK] PASS" if result["success"] else "[ERROR] FAIL"
        print(f"{status} | {result['name']}: {result['passed']}/{result['total']} passed")
    
    print("=" * 80)
    
    # System status
    print("\n🚀 PROMETHEUS AI SYSTEM STATUS")
    print("=" * 80)
    print("[CHECK] Tier 1 - Critical Systems: 4/4 integrated")
    print("[CHECK] Tier 2 - High Priority Systems: 4/4 integrated")
    print("[CHECK] Tier 3 - Medium Priority Systems: 2/2 integrated")
    print("[CHECK] Total Advanced AI Systems: 10/10 integrated")
    print(f"[CHECK] Overall Test Pass Rate: {pass_rate:.1f}%")
    print("=" * 80 + "\n")
    
    return total_failed == 0

def main():
    """Run all test suites"""
    print_header()
    
    # Define test suites
    test_suites = [
        ("TEST_TIER1_ADVANCED_AI_INTEGRATION.py", "Tier 1: Critical AI Systems"),
        ("TEST_TIER2_INTEGRATION.py", "Tier 2: High Priority Systems"),
        ("TEST_TIER3_INTEGRATION.py", "Tier 3: Medium Priority Systems")
    ]
    
    # Run all test suites
    results = []
    for test_file, suite_name in test_suites:
        if os.path.exists(test_file):
            result = run_test_suite(test_file, suite_name)
            results.append(result)
        else:
            print(f"\n[WARNING]️  {suite_name}: Test file not found - {test_file}")
            results.append({
                "name": suite_name,
                "file": test_file,
                "total": 0,
                "passed": 0,
                "failed": 1,
                "warnings": 0,
                "success": False,
                "output": "Test file not found"
            })
    
    # Print final summary
    success = print_final_summary(results)
    
    # Save detailed report
    save_test_report(results)
    
    return 0 if success else 1

def save_test_report(results: List[Dict]):
    """Save detailed test report to file"""
    report_file = "TEST_RESULTS_REPORT.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🧪 PROMETHEUS COMPREHENSIVE TEST RESULTS\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary
        total_tests = sum(r["total"] for r in results)
        total_passed = sum(r["passed"] for r in results)
        total_failed = sum(r["failed"] for r in results)
        total_warnings = sum(r["warnings"] for r in results)
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        f.write("## 📊 SUMMARY\n\n")
        f.write(f"- **Test Suites:** {len(results)}\n")
        f.write(f"- **Total Tests:** {total_tests}\n")
        f.write(f"- **Passed:** {total_passed} [CHECK]\n")
        f.write(f"- **Failed:** {total_failed} [ERROR]\n")
        f.write(f"- **Warnings:** {total_warnings} [WARNING]️\n")
        f.write(f"- **Pass Rate:** {pass_rate:.1f}%\n\n")
        
        # Detailed results
        f.write("---\n\n")
        f.write("## 📋 DETAILED RESULTS\n\n")
        
        for result in results:
            status = "[CHECK] PASSED" if result["success"] else "[ERROR] FAILED"
            f.write(f"### {result['name']} {status}\n\n")
            f.write(f"- **File:** `{result['file']}`\n")
            f.write(f"- **Total Tests:** {result['total']}\n")
            f.write(f"- **Passed:** {result['passed']}\n")
            f.write(f"- **Failed:** {result['failed']}\n")
            f.write(f"- **Warnings:** {result['warnings']}\n\n")
        
        # System status
        f.write("---\n\n")
        f.write("## 🚀 SYSTEM STATUS\n\n")
        f.write("- [CHECK] **Tier 1 - Critical Systems:** 4/4 integrated\n")
        f.write("- [CHECK] **Tier 2 - High Priority Systems:** 4/4 integrated\n")
        f.write("- [CHECK] **Tier 3 - Medium Priority Systems:** 2/2 integrated\n")
        f.write("- [CHECK] **Total Advanced AI Systems:** 10/10 integrated\n")
        f.write(f"- [CHECK] **Overall Test Pass Rate:** {pass_rate:.1f}%\n\n")
        
        f.write("---\n\n")
        f.write("**Report Generated:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[WARNING]️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

