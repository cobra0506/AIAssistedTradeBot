"""
Comprehensive Test Runner
Runs all tests to achieve 95% confidence in the system
Author: AI Assisted TradeBot Team
Date: 2025
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_comprehensive_tests():
    """Run all comprehensive tests and generate report"""
    
    print("🚀 COMPREHENSIVE TEST SUITE FOR 95% CONFIDENCE")
    print("=" * 70)
    print(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test suites to run
    test_suites = [
        ('Signal Functions', 'test_all_signals.py'),
        ('Integration Tests', 'test_integration.py'),
        ('Calculation Accuracy', 'test_calculation_accuracy.py'),
    ]
    
    results = {}
    total_start_time = time.time()
    
    for suite_name, test_file in test_suites:
        print(f"\n📊 Running {suite_name}...")
        print("-" * 50)
        
        try:
            # Import the test module
            module_name = test_file.replace('.py', '')
            spec = __import__(module_name)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(spec)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(suite)
            
            # Store results
            results[suite_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0
            }
            
            # Print summary
            print(f"\n📈 {suite_name} Results:")
            print(f"   Tests Run: {result.testsRun}")
            print(f"   Failures: {len(result.failures)}")
            print(f"   Errors: {len(result.errors)}")
            print(f"   Success Rate: {results[suite_name]['success_rate']:.1f}%")
            
            if result.failures:
                print(f"   ❌ Failures:")
                for test, traceback in result.failures:
                    print(f"      - {test}")
            
            if result.errors:
                print(f"   ⚠️  Errors:")
                for test, traceback in result.errors:
                    print(f"      - {test}")
                    
        except Exception as e:
            print(f"❌ Error running {suite_name}: {e}")
            results[suite_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success_rate': 0,
                'error': str(e)
            }
    
    # Generate final report
    total_time = time.time() - total_start_time
    total_tests = sum(r['tests_run'] for r in results.values())
    total_failures = sum(r['failures'] for r in results.values())
    total_errors = sum(r['errors'] for r in results.values())
    overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 70)
    print("🏆 COMPREHENSIVE TEST REPORT")
    print("=" * 70)
    print(f"Total Test Time: {total_time:.2f} seconds")
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Failures: {total_failures}")
    print(f"Total Errors: {total_errors}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    print("\n📊 Detailed Results:")
    
    for suite_name, result in results.items():
        status = "✅ PASS" if result['success_rate'] >= 95 else "⚠️  NEEDS ATTENTION" if result['success_rate'] >= 80 else "❌ FAIL"
        print(f"   {suite_name}: {result['success_rate']:.1f}% - {status}")
    
    # Confidence assessment
    print("\n🎯 CONFIDENCE ASSESSMENT:")
    if overall_success_rate >= 95:
        print("   ✅ 95%+ Confidence: System is ready for production")
        confidence_level = "HIGH"
    elif overall_success_rate >= 85:
        print("   ⚠️  85-94% Confidence: System is mostly ready but needs minor fixes")
        confidence_level = "MEDIUM-HIGH"
    elif overall_success_rate >= 70:
        print("   ⚠️  70-84% Confidence: System needs significant improvements")
        confidence_level = "MEDIUM"
    else:
        print("   ❌ <70% Confidence: System is not ready for production use")
        confidence_level = "LOW"
    
    print(f"\n📋 RECOMMENDATIONS:")
    if total_failures > 0:
        print(f"   • Fix {total_failures} failing tests")
    if total_errors > 0:
        print(f"   • Resolve {total_errors} test errors")
    if overall_success_rate < 95:
        print(f"   • Investigate tests with <95% success rate")
    
    if overall_success_rate >= 95:
        print("   ✅ System is ready for live trading with 95% confidence")
    else:
        print("   ⚠️  Address the issues above before deploying to production")
    
    print(f"\nTest Run Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return {
        'overall_success_rate': overall_success_rate,
        'confidence_level': confidence_level,
        'total_tests': total_tests,
        'total_failures': total_failures,
        'total_errors': total_errors,
        'detailed_results': results
    }

if __name__ == '__main__':
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    if results['overall_success_rate'] >= 95:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure