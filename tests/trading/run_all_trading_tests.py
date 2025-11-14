"""
Main test runner for Paper Trading System
Runs all trading tests in sequence
"""
import unittest
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def run_trading_tests():
    """Run all paper trading tests"""
    print("Paper Trading System - Test Suite")
    print("=" * 60)
    print("This will run all trading tests to verify the system works correctly.")
    print()
    
    # Test files to run in order
    test_files = [
        'test_01_api_connection.py',
        'test_02_trade_execution.py', 
        'test_03_performance_calculation.py'
    ]
    
    # Run each test file
    for test_file in test_files:
        print(f"\nRunning {test_file}...")
        print("-" * 40)
        
        # Load and run the test
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        suite = unittest.TestLoader().loadTestsFromName('__main__', globals())
        
        # Run the test
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print(f"✅ {test_file} - ALL TESTS PASSED")
        else:
            print(f"❌ {test_file} - SOME TESTS FAILED")
            print(f"   Failures: {len(result.failures)}")
            print(f"   Errors: {len(result.errors)}")
        
        print("\n" + "=" * 60)
    
    print("Test suite completed!")
    print("Review the results above to see what needs to be fixed.")

if __name__ == '__main__':
    run_trading_tests()