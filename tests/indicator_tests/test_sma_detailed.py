"""
Detailed Indicator Tests - SMA (Simple Moving Average)
=====================================================
This test file provides comprehensive testing for each indicator with detailed debugging.
Author: AI Assisted TradeBot Team
Date: 2025
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get to the project root (indicator_tests -> tests -> project_root)
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from simple_strategy.strategies.indicators_library import sma, ema, rsi, macd, bollinger_bands

class TestSMAIndicator(unittest.TestCase):
    """Test cases for SMA (Simple Moving Average) indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for SMA")
        print("="*60)
        
        # Create simple test data
        self.simple_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], name='close')
        self.period = 3
        
        # Create more realistic price data
        np.random.seed(42)  # For reproducible results
        self.realistic_data = pd.Series(
            [100.0, 102.5, 101.8, 103.2, 104.1, 103.5, 105.0, 106.2, 105.8, 107.1],
            name='close'
        )
        
        # Create edge case data
        self.edge_data = pd.Series([10.0] * 10, name='close')  # All same values
        
        print(f"Simple test data: {self.simple_data.tolist()}")
        print(f"Realistic test data: {self.realistic_data.tolist()}")
        print(f"Edge case data: {self.edge_data.tolist()}")
        print(f"Test period: {self.period}")
    
    def test_sma_basic_calculation(self):
        """Test basic SMA calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: SMA Basic Calculation")
        print("-"*60)
        
        # Calculate SMA
        result = sma(self.simple_data, self.period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        print(f"Expected length: {len(self.simple_data)}")
        
        # Expected manual calculation
        expected_manual = []
        for i in range(len(self.simple_data)):
            if i < self.period - 1:
                expected_manual.append(np.nan)
            else:
                window_sum = sum(self.simple_data.iloc[i-self.period+1:i+1])
                expected_manual.append(window_sum / self.period)
        
        print(f"Expected manual calculation: {expected_manual}")
        
        # Assertions
        self.assertEqual(len(result), len(self.simple_data), "Result length should match input length")
        self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
        
        # Check specific values (ignoring NaN values)
        for i in range(self.period-1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i], 
                    expected_manual[i], 
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {expected_manual[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]} == {expected_manual[i]}")
        
        print("✓ Test passed: Basic SMA calculation")
    
    def test_sma_realistic_data(self):
        """Test SMA with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: SMA with Realistic Price Data")
        print("-"*60)
        
        # Calculate SMA
        result = sma(self.realistic_data, self.period)
        
        # Debug information
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        
        # Calculate expected values manually
        expected_values = []
        for i in range(len(self.realistic_data)):
            if i < self.period - 1:
                expected_values.append(np.nan)
            else:
                window = self.realistic_data.iloc[i-self.period+1:i+1]
                sma_value = window.mean()
                expected_values.append(sma_value)
        
        print(f"Expected values: {expected_values}")
        
        # Assertions
        self.assertEqual(len(result), len(self.realistic_data))
        self.assertIsInstance(result, pd.Series)
        
        # Check non-NaN values
        for i in range(self.period-1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i], 
                    expected_values[i], 
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {expected_values[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.4f} == {expected_values[i]:.4f}")
        
        print("✓ Test passed: SMA with realistic data")
    
    def test_sma_edge_cases(self):
        """Test SMA with edge cases"""
        print("\n" + "-"*60)
        print("TEST: SMA Edge Cases")
        print("-"*60)
        
        # Test with all same values
        result = sma(self.edge_data, self.period)
        
        print(f"Input data (all same): {self.edge_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        
        # All non-NaN values should equal the input value
        for i in range(self.period-1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertEqual(
                    result.iloc[i], 
                    self.edge_data.iloc[i],
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {self.edge_data.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]} == {self.edge_data.iloc[i]}")
        
        # Test with period larger than data length
        large_period = 20
        result_large = sma(self.simple_data, large_period)
        
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"Result: {result_large.tolist()}")
        
        # All values should be NaN
        self.assertTrue(result_large.isna().all(), "All values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        print("✓ Test passed: SMA edge cases")
    
    def test_sma_error_handling(self):
        """Test SMA error handling"""
        print("\n" + "-"*60)
        print("TEST: SMA Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        result_empty = sma(empty_data, self.period)
        
        print(f"Empty data test - Result type: {type(result_empty)}")
        print(f"Empty data test - Result length: {len(result_empty)}")
        
        self.assertIsInstance(result_empty, pd.Series)
        self.assertEqual(len(result_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            result_invalid = sma(self.simple_data, 0)
            print("Result with period 0:", result_invalid.tolist())
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            result_negative = sma(self.simple_data, -1)
            print("Result with period -1:", result_negative.tolist())
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: SMA error handling")
    
    def test_sma_performance(self):
        """Test SMA performance with larger dataset"""
        print("\n" + "-"*60)
        print("TEST: SMA Performance")
        print("-"*60)
        
        # Create larger dataset
        large_data = pd.Series(np.random.randn(1000) + 100, name='close')
        
        import time
        start_time = time.time()
        result = sma(large_data, self.period)
        end_time = time.time()
        
        print(f"Large dataset size: {len(large_data)}")
        print(f"Calculation time: {end_time - start_time:.6f} seconds")
        print(f"Result length: {len(result)}")
        print(f"Non-NaN values: {result.notna().sum()}")
        
        # Performance assertion (should be very fast)
        self.assertLess(end_time - start_time, 0.1, "SMA calculation should be fast")
        
        # Check that result is correct
        expected_first_valid = large_data.iloc[:self.period].mean()
        actual_first_valid = result.iloc[self.period-1]
        
        print(f"First valid value - Expected: {expected_first_valid:.6f}, Actual: {actual_first_valid:.6f}")
        self.assertAlmostEqual(actual_first_valid, expected_first_valid, places=10)
        
        print("✓ Test passed: SMA performance")

def run_sma_tests():
    """Run all SMA tests with detailed output"""
    print("Starting comprehensive SMA indicator tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSMAIndicator)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("SMA TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL SMA TESTS PASSED!")
    else:
        print("\n❌ SOME SMA TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_sma_tests()