#!/usr/bin/env python3
"""
Comprehensive test runner for AIAssistedTradeBot data feeder and strategy base
"""
import sys
import subprocess
import time
import os
from pathlib import Path

def run_tests():
    """Run all tests and generate report"""
    print("=" * 60)
    print("AIAssistedTradeBot - Comprehensive Test Suite")
    print("=" * 60)
    
    # Ensure we're in the tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)
    
    # Install test dependencies if not already installed
    print("\n1. Installing test dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio", "pytest-mock", "psutil", "pandas"], 
                      check=True, capture_output=True)
        print("   ✅ Test dependencies installed")
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install test dependencies")
        return False
    
    # Run tests with different markers
    test_results = {}
    
    print("\n2. Running Unit Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_optimized_data_fetcher.py",
            "test_websocket_handler.py", 
            "test_csv_manager.py",
            "-v", "--tb=short"
        ], check=True, capture_output=True, text=True)
        
        test_results['unit'] = {
            'success': True,
            'output': result.stdout,
            'errors': result.stderr
        }
        print("   ✅ Unit tests passed")
    except subprocess.CalledProcessError as e:
        test_results['unit'] = {
            'success': False,
            'output': e.stdout,
            'errors': e.stderr
        }
        print("   ❌ Unit tests failed")
        print(f"   Error output: {e.stderr}")
    
    print("\n3. Running Integration Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_hybrid_system.py",
            "-v", "--tb=short"
        ], check=True, capture_output=True, text=True)
        
        test_results['integration'] = {
            'success': True,
            'output': result.stdout,
            'errors': result.stderr
        }
        print("   ✅ Integration tests passed")
    except subprocess.CalledProcessError as e:
        test_results['integration'] = {
            'success': False,
            'output': e.stdout,
            'errors': e.stderr
        }
        print("   ❌ Integration tests failed")
        print(f"   Error output: {e.stderr}")
    
    print("\n4. Running Mock Strategy Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "test_mock_strategy.py",
            "-v", "--tb=short"
        ], check=True, capture_output=True, text=True)
        
        test_results['strategy'] = {
            'success': True,
            'output': result.stdout,
            'errors': result.stderr
        }
        print("   ✅ Mock strategy tests passed")
    except subprocess.CalledProcessError as e:
        test_results['strategy'] = {
            'success': False,
            'output': e.stdout,
            'errors': e.stderr
        }
        print("   ❌ Mock strategy tests failed")
        print(f"   Error output: {e.stderr}")
    
    # Generate report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_type, result in test_results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{test_type.upper():<15} {status}")
        if not result['success']:
            all_passed = False
            print(f"   Errors: {result['errors'][:500]}...")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your data feeder and strategy base work 100%!")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the output above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)