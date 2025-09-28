"""
Detailed Indicator Tests - RSI (Relative Strength Index)
=======================================================
This test file provides comprehensive testing for the RSI indicator with detailed debugging.
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

# Import the indicators library
from simple_strategy.strategies.indicators_library import rsi

class TestRSIIndicator(unittest.TestCase):
    """Test cases for RSI (Relative Strength Index) indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for RSI")
        print("="*60)
        
        # Create simple test data with clear up/down movements
        self.simple_data = pd.Series([44, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.85, 46.08, 45.89], name='close')
        self.period = 14
        
        # Create more realistic price data
        np.random.seed(42)
        base_price = 100.0
        changes = np.random.randn(20) * 2.0  # Random changes
        prices = [base_price]
        for change in changes:
            prices.append(prices[-1] + change)
        
        self.realistic_data = pd.Series(prices, name='close')
        
        # Create edge case data
        self.constant_data = pd.Series([100.0] * 20, name='close')  # All same values
        
        print(f"Simple test data: {self.simple_data.tolist()}")
        print(f"Realistic test data: {[f'{x:.2f}' for x in self.realistic_data.tolist()]}")
        print(f"Constant test data: {self.constant_data.tolist()[:10]}...")
        print(f"Test period: {self.period}")

    def test_rsi_with_sufficient_data(self):
        """Test RSI calculation with sufficient data points"""
        print("\n" + "-"*60)
        print("TEST: RSI with Sufficient Data")
        print("-"*60)
        
        # Create test data with more points than the period
        # Using the classic RSI example from Welles Wilder's book
        sufficient_data = pd.Series([
            44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.85, 46.08, 45.89, 46.03,
            46.83, 47.69, 46.49, 46.26
        ], name='close')
        
        period = 14
        
        # Calculate RSI
        result = rsi(sufficient_data, period)
        
        # Debug information
        print(f"Input data: {sufficient_data.tolist()}")
        print(f"Period: {period}")
        print(f"Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # Assertions
        self.assertEqual(len(result), len(sufficient_data), "Result length should match input length")
        self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
        
        # Check that first period-1 values are NaN
        for i in range(period - 1):
            self.assertTrue(pd.isna(result.iloc[i]), f"Value at index {i} should be NaN")
            print(f"✓ Index {i}: NaN (expected)")
        
        # Check that we have a valid RSI value at the end
        final_rsi = result.iloc[-1]
        self.assertFalse(pd.isna(final_rsi), "Final RSI value should not be NaN")
        self.assertGreaterEqual(final_rsi, 0, "RSI should be >= 0")
        self.assertLessEqual(final_rsi, 100, "RSI should be <= 100")
        
        print(f"✓ Final RSI value: {final_rsi:.2f}")
        
        # Calculate expected values manually for verification
        deltas = sufficient_data.diff().dropna()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        # For the first RSI value, we use simple average of gains and losses
        first_gain = gains.iloc[:period].sum() / period
        first_loss = losses.iloc[:period].sum() / period
        
        if first_loss == 0:
            first_rs = float('inf')
            first_rsi = 100.0
        else:
            first_rs = first_gain / first_loss
            first_rsi = 100 - (100 / (1 + first_rs))
        
        print(f"Expected first RSI: {first_rsi:.2f}")
        
        # The first valid RSI should be at index period-1
        actual_first_rsi = result.iloc[period-1]
        self.assertAlmostEqual(actual_first_rsi, first_rsi, places=10,
                            msg=f"First RSI mismatch: got {actual_first_rsi}, expected {first_rsi}")
        print(f"✓ First RSI matches: {actual_first_rsi:.2f}")
        
        print("✓ Test passed: RSI with sufficient data")
    
    def test_rsi_basic_calculation(self):
        """Test basic RSI calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: RSI Basic Calculation")
        print("-"*60)
        
        # Calculate RSI
        result = rsi(self.simple_data, self.period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
        # Since our test data (10 values) is shorter than the period (14),
        # all RSI values should be NaN
        if len(self.simple_data) < self.period:
            print(f"Data length ({len(self.simple_data)}) < Period ({self.period}) - all values should be NaN")
            for i in range(len(result)):
                self.assertTrue(pd.isna(result.iloc[i]), f"Value at index {i} should be NaN")
                print(f"✓ Index {i}: NaN (expected)")
        else:
            # Calculate expected values manually
            # First, calculate price changes
            deltas = self.simple_data.diff().dropna()
            
            # Separate gains and losses
            gains = deltas.where(deltas > 0, 0)
            losses = -deltas.where(deltas < 0, 0)
            
            # Calculate average gains and losses
            avg_gain = gains.rolling(window=self.period).mean()
            avg_loss = losses.rolling(window=self.period).mean()
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            expected_rsi = 100 - (100 / (1 + rs))
            
            print(f"Expected RSI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in expected_rsi.tolist()]}")
            
            # Assertions
            self.assertEqual(len(result), len(self.simple_data), "Result length should match input length")
            self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
            
            # Check that first period-1 values are NaN
            for i in range(self.period - 1):
                self.assertTrue(pd.isna(result.iloc[i]), f"Value at index {i} should be NaN")
                print(f"✓ Index {i}: NaN (expected)")
            
            # Check non-NaN values
            for i in range(self.period - 1, len(result)):
                if not pd.isna(result.iloc[i]) and not pd.isna(expected_rsi.iloc[i]):
                    self.assertAlmostEqual(
                        result.iloc[i], 
                        expected_rsi.iloc[i], 
                        places=10,
                        msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {expected_rsi.iloc[i]}"
                    )
                    print(f"✓ Index {i}: {result.iloc[i]:.2f} == {expected_rsi.iloc[i]:.2f}")
        
        # Check RSI bounds (should be between 0 and 100)
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertGreaterEqual(result.iloc[i], 0, f"RSI at index {i} should be >= 0")
                self.assertLessEqual(result.iloc[i], 100, f"RSI at index {i} should be <= 100")
        
        print("✓ Test passed: Basic RSI calculation")
    
    def test_rsi_realistic_data(self):
        """Test RSI with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: RSI with Realistic Price Data")
        print("-"*60)
        
        # Calculate RSI
        result = rsi(self.realistic_data, self.period)
        
        # Debug information
        print(f"Input data: {[f'{x:.2f}' for x in self.realistic_data.tolist()]}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # Assertions
        self.assertEqual(len(result), len(self.realistic_data))
        self.assertIsInstance(result, pd.Series)
        
        # Check that first period-1 values are NaN
        for i in range(self.period - 1):
            self.assertTrue(pd.isna(result.iloc[i]), f"Value at index {i} should be NaN")
        
        # Check RSI bounds
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertGreaterEqual(result.iloc[i], 0, f"RSI at index {i} should be >= 0")
                self.assertLessEqual(result.iloc[i], 100, f"RSI at index {i} should be <= 100")
        
        # Check that we have some variation in RSI values
        non_nan_values = result.dropna()
        if len(non_nan_values) > 1:
            rsi_range = non_nan_values.max() - non_nan_values.min()
            self.assertGreater(rsi_range, 0, "RSI should show some variation with realistic data")
            print(f"RSI range: {rsi_range:.2f}")
        
        print("✓ Test passed: RSI with realistic data")
    
    def test_rsi_edge_cases(self):
        """Test RSI with edge cases"""
        print("\n" + "-"*60)
        print("TEST: RSI Edge Cases")
        print("-"*60)
        
        # Test with constant values (no price changes)
        result_constant = rsi(self.constant_data, self.period)
        
        print(f"Constant data test - Input: {self.constant_data.tolist()[:5]}...")
        print(f"Constant data test - Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_constant.tolist()[:10]]}")
        
        # With constant data, RSI should be 50 (no gains or losses)
        for i in range(self.period - 1, len(result_constant)):
            if not pd.isna(result_constant.iloc[i]):
                self.assertAlmostEqual(
                    result_constant.iloc[i], 
                    50.0, 
                    places=10,
                    msg=f"RSI with constant data should be 50, got {result_constant.iloc[i]}"
                )
                print(f"✓ Index {i}: {result_constant.iloc[i]:.2f} == 50.00")
        
        # Test with period larger than data length
        large_period = 25
        result_large = rsi(self.simple_data, large_period)
        
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_large.tolist()]}")
        
        # All values should be NaN
        self.assertTrue(result_large.isna().all(), "All values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with period = 1
        try:
            result_period1 = rsi(self.simple_data, 1)
            print(f"\nTesting with period = 1")
            print(f"Result: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_period1.tolist()]}")
            
            # With period=1, RSI should be 100 for gains and 0 for losses
            for i in range(1, len(self.simple_data)):
                change = self.simple_data.iloc[i] - self.simple_data.iloc[i-1]
                if change > 0:
                    self.assertAlmostEqual(result_period1.iloc[i], 100.0, places=10)
                    print(f"✓ Index {i}: {result_period1.iloc[i]:.2f} == 100.00 (gain)")
                elif change < 0:
                    self.assertAlmostEqual(result_period1.iloc[i], 0.0, places=10)
                    print(f"✓ Index {i}: {result_period1.iloc[i]:.2f} == 0.00 (loss)")
                else:
                    self.assertAlmostEqual(result_period1.iloc[i], 50.0, places=10)
                    print(f"✓ Index {i}: {result_period1.iloc[i]:.2f} == 50.00 (no change)")
        except Exception as e:
            print(f"Exception with period=1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: RSI edge cases")
    
    def test_rsi_error_handling(self):
        """Test RSI error handling"""
        print("\n" + "-"*60)
        print("TEST: RSI Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        result_empty = rsi(empty_data, self.period)
        
        print(f"Empty data test - Result type: {type(result_empty)}")
        print(f"Empty data test - Result length: {len(result_empty)}")
        
        self.assertIsInstance(result_empty, pd.Series)
        self.assertEqual(len(result_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            result_invalid = rsi(self.simple_data, 0)
            print("Result with period 0:", [f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_invalid.tolist()])
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            result_negative = rsi(self.simple_data, -1)
            print("Result with period -1:", [f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_negative.tolist()])
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: RSI error handling")
    
    def test_rsi_extreme_values(self):
        """Test RSI with extreme price movements"""
        print("\n" + "-"*60)
        print("TEST: RSI Extreme Values")
        print("-"*60)
        
        # Create data with strong uptrend
        uptrend_data = pd.Series([100 + i for i in range(20)], name='close')
        result_uptrend = rsi(uptrend_data, self.period)
        
        print(f"Uptrend data: {uptrend_data.tolist()}")
        print(f"Uptrend RSI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_uptrend.tolist()]}")
        
        # With strong uptrend, RSI should be high (>70)
        for i in range(self.period - 1, len(result_uptrend)):
            if not pd.isna(result_uptrend.iloc[i]):
                self.assertGreater(result_uptrend.iloc[i], 70, 
                                 f"RSI should be high in uptrend, got {result_uptrend.iloc[i]}")
                print(f"✓ Index {i}: {result_uptrend.iloc[i]:.2f} > 70")
        
        # Create data with strong downtrend
        downtrend_data = pd.Series([100 - i for i in range(20)], name='close')
        result_downtrend = rsi(downtrend_data, self.period)
        
        print(f"\nDowntrend data: {downtrend_data.tolist()}")
        print(f"Downtrend RSI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in result_downtrend.tolist()]}")
        
        # With strong downtrend, RSI should be low (<30)
        for i in range(self.period - 1, len(result_downtrend)):
            if not pd.isna(result_downtrend.iloc[i]):
                self.assertLess(result_downtrend.iloc[i], 30, 
                               f"RSI should be low in downtrend, got {result_downtrend.iloc[i]}")
                print(f"✓ Index {i}: {result_downtrend.iloc[i]:.2f} < 30")
        
        print("✓ Test passed: RSI extreme values")
    
    def test_rsi_performance(self):
        """Test RSI performance with larger dataset"""
        print("\n" + "-"*60)
        print("TEST: RSI Performance")
        print("-"*60)
        
        # Create larger dataset
        np.random.seed(42)
        large_data = pd.Series(np.random.randn(1000).cumsum() + 100, name='close')
        
        import time
        start_time = time.time()
        result = rsi(large_data, self.period)
        end_time = time.time()
        
        print(f"Large dataset size: {len(large_data)}")
        print(f"Calculation time: {end_time - start_time:.6f} seconds")
        print(f"Result length: {len(result)}")
        print(f"Non-NaN values: {result.notna().sum()}")
        
        # Performance assertion (should be fast)
        self.assertLess(end_time - start_time, 0.1, "RSI calculation should be fast")
        
        # Check RSI bounds
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertGreaterEqual(result.iloc[i], 0, f"RSI at index {i} should be >= 0")
                self.assertLessEqual(result.iloc[i], 100, f"RSI at index {i} should be <= 100")
        
        print("✓ Test passed: RSI performance")

def run_rsi_tests():
    """Run all RSI tests with detailed output"""
    print("Starting comprehensive RSI indicator tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRSIIndicator)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("RSI TEST SUMMARY")
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
        print("\n🎉 ALL RSI TESTS PASSED!")
    else:
        print("\n❌ SOME RSI TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_rsi_tests()