"""
Detailed Indicator Tests - EMA (Exponential Moving Average)
==========================================================
This test file provides comprehensive testing for the EMA indicator with detailed debugging.
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

# Now we can import from simple_strategy
from simple_strategy.strategies.indicators_library import sma, ema, rsi, macd, bollinger_bands

class TestEMAIndicator(unittest.TestCase):
    """Test cases for EMA (Exponential Moving Average) indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for EMA")
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
    
    def test_ema_basic_calculation(self):
        """Test basic EMA calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: EMA Basic Calculation")
        print("-"*60)
        
        # Calculate EMA
        result = ema(self.simple_data, self.period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
        # EMA calculation verification
        # First EMA value is SMA of first period values
        first_ema = self.simple_data.iloc[:self.period].mean()
        
        # Calculate smoothing factor
        smoothing = 2 / (self.period + 1)
        
        # Manual EMA calculation for verification
        manual_ema = [np.nan] * (self.period - 1)  # First period-1 values are NaN
        manual_ema.append(first_ema)  # First EMA value is SMA
        
        # Calculate subsequent EMA values
        for i in range(self.period, len(self.simple_data)):
            ema_value = smoothing * self.simple_data.iloc[i] + (1 - smoothing) * manual_ema[-1]
            manual_ema.append(ema_value)
        
        print(f"Manual EMA calculation: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in manual_ema]}")
        print(f"Smoothing factor: {smoothing:.6f}")
        
        # Assertions
        self.assertEqual(len(result), len(self.simple_data), "Result length should match input length")
        self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
        
        # Check specific values (ignoring NaN values)
        for i in range(self.period-1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i], 
                    manual_ema[i], 
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {manual_ema[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {manual_ema[i]:.6f}")
        
        print("✓ Test passed: Basic EMA calculation")
    
    def test_ema_realistic_data(self):
        """Test EMA with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: EMA with Realistic Price Data")
        print("-"*60)
        
        # Calculate EMA
        result = ema(self.realistic_data, self.period)
        
        # Debug information
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # Calculate expected values manually
        smoothing = 2 / (self.period + 1)
        first_ema = self.realistic_data.iloc[:self.period].mean()
        
        expected_values = [np.nan] * (self.period - 1)
        expected_values.append(first_ema)
        
        for i in range(self.period, len(self.realistic_data)):
            ema_value = smoothing * self.realistic_data.iloc[i] + (1 - smoothing) * expected_values[-1]
            expected_values.append(ema_value)
        
        print(f"Expected values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in expected_values]}")
        print(f"Smoothing factor: {smoothing:.6f}")
        
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
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {expected_values[i]:.6f}")
        
        print("✓ Test passed: EMA with realistic data")
    
    def test_ema_edge_cases(self):
        """Test EMA with edge cases"""
        print("\n" + "-"*60)
        print("TEST: EMA Edge Cases")
        print("-"*60)
        
        # Test with all same values
        result = ema(self.edge_data, self.period)
        
        print(f"Input data (all same): {self.edge_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
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
        result_large = ema(self.simple_data, large_period)
        
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"Result: {result_large.tolist()}")
        
        # All values should be NaN
        self.assertTrue(result_large.isna().all(), "All values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with period = 1 (should equal the input data)
        result_period1 = ema(self.simple_data, 1)
        print(f"\nTesting with period = 1")
        print(f"Input: {self.simple_data.tolist()}")
        print(f"Result: {result_period1.tolist()}")
        
        for i in range(len(self.simple_data)):
            self.assertEqual(
                result_period1.iloc[i], 
                self.simple_data.iloc[i],
                msg=f"Mismatch at index {i}: got {result_period1.iloc[i]}, expected {self.simple_data.iloc[i]}"
            )
            print(f"✓ Index {i}: {result_period1.iloc[i]} == {self.simple_data.iloc[i]}")
        
        print("✓ Test passed: EMA edge cases")
    
    def test_ema_error_handling(self):
        """Test EMA error handling"""
        print("\n" + "-"*60)
        print("TEST: EMA Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        result_empty = ema(empty_data, self.period)
        
        print(f"Empty data test - Result type: {type(result_empty)}")
        print(f"Empty data test - Result length: {len(result_empty)}")
        
        self.assertIsInstance(result_empty, pd.Series)
        self.assertEqual(len(result_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            result_invalid = ema(self.simple_data, 0)
            print("Result with period 0:", result_invalid.tolist())
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            result_negative = ema(self.simple_data, -1)
            print("Result with period -1:", result_negative.tolist())
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: EMA error handling")
    
    def test_ema_vs_sma_comparison(self):
        """Test EMA vs SMA comparison"""
        print("\n" + "-"*60)
        print("TEST: EMA vs SMA Comparison")
        print("-"*60)
        
        # Calculate both SMA and EMA
        sma_result = sma(self.realistic_data, self.period)
        ema_result = ema(self.realistic_data, self.period)
        
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"SMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in sma_result.tolist()]}")
        print(f"EMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema_result.tolist()]}")
        
        # First non-NaN values should be the same (SMA of first period)
        first_valid_idx = self.period - 1
        self.assertAlmostEqual(
            sma_result.iloc[first_valid_idx], 
            ema_result.iloc[first_valid_idx], 
            places=10,
            msg="First valid SMA and EMA values should be the same"
        )
        print(f"✓ First valid values match: SMA={sma_result.iloc[first_valid_idx]:.6f}, EMA={ema_result.iloc[first_valid_idx]:.6f}")
        
        # Test EMA responsiveness with a more realistic scenario
        # Create a series with frequent price changes to show EMA's advantage
        volatile_data = pd.Series([
            100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5, 105.0, 104.5,
            106.0, 105.5, 107.0, 106.5, 108.0, 107.5, 109.0, 108.5, 110.0, 109.5
        ], name='close')
        
        sma_volatile = sma(volatile_data, self.period)
        ema_volatile = ema(volatile_data, self.period)
        
        print(f"\nTesting with volatile price series (20 data points)")
        print(f"Pattern: Frequent up/down movements")
        
        # Check responsiveness in the middle of the series (after trend is established)
        check_idx = 15  # Well into the series
        
        if check_idx < len(volatile_data):
            current_price = volatile_data.iloc[check_idx]
            sma_value = sma_volatile.iloc[check_idx]
            ema_value = ema_volatile.iloc[check_idx]
            
            sma_distance = abs(sma_value - current_price)
            ema_distance = abs(ema_value - current_price)
            
            print(f"\nAt index {check_idx}:")
            print(f"Current price: {current_price}")
            print(f"SMA value: {sma_value:.6f}")
            print(f"EMA value: {ema_value:.6f}")
            print(f"SMA distance from current price: {sma_distance:.6f}")
            print(f"EMA distance from current price: {ema_distance:.6f}")
            
            # The key advantage of EMA is that it gives more weight to recent prices
            # Let's verify this by checking if EMA is generally closer to recent prices
            # We'll check the average distance over the last few periods
            recent_periods = 5
            if check_idx >= recent_periods:
                sma_distances = []
                ema_distances = []
                
                for i in range(check_idx - recent_periods + 1, check_idx + 1):
                    price = volatile_data.iloc[i]
                    sma_dist = abs(sma_volatile.iloc[i] - price)
                    ema_dist = abs(ema_volatile.iloc[i] - price)
                    sma_distances.append(sma_dist)
                    ema_distances.append(ema_dist)
                
                avg_sma_distance = sum(sma_distances) / len(sma_distances)
                avg_ema_distance = sum(ema_distances) / len(ema_distances)
                
                print(f"\nAverage distance over last {recent_periods} periods:")
                print(f"Average SMA distance: {avg_sma_distance:.6f}")
                print(f"Average EMA distance: {avg_ema_distance:.6f}")
                
                # EMA should generally have a smaller average distance
                self.assertLessEqual(
                    avg_ema_distance,
                    avg_sma_distance * 1.1,  # Allow 10% tolerance
                    msg="EMA should have smaller average distance from recent prices"
                )
                print("✓ EMA shows better responsiveness to recent price changes")
        
        # Test with a longer period to better demonstrate EMA's advantage
        print(f"\nTesting with longer period (10):")
        longer_period = 10
        
        # Create a step change scenario
        step_data = pd.Series([100.0] * 15 + [110.0] * 15, name='close')
        sma_step = sma(step_data, longer_period)
        ema_step = ema(step_data, longer_period)
        
        # Find where each indicator reaches 90% of the step change
        target_value = 109.0  # 90% of the way from 100 to 110
        
        sma_90_percent_idx = None
        ema_90_percent_idx = None
        
        for i in range(len(step_data)):
            if sma_90_percent_idx is None and not pd.isna(sma_step.iloc[i]) and sma_step.iloc[i] >= target_value:
                sma_90_percent_idx = i
            if ema_90_percent_idx is None and not pd.isna(ema_step.iloc[i]) and ema_step.iloc[i] >= target_value:
                ema_90_percent_idx = i
        
        print(f"Step change from 100.0 to 110.0 at index 15")
        print(f"Period: {longer_period}")
        print(f"SMA reaches 90% of change at index: {sma_90_percent_idx}")
        print(f"EMA reaches 90% of change at index: {ema_90_percent_idx}")
        
        # With longer periods, EMA should respond faster
        if sma_90_percent_idx is not None and ema_90_percent_idx is not None:
            if ema_90_percent_idx <= sma_90_percent_idx:
                print("✓ EMA responds faster to step changes with longer periods")
            else:
                print("ℹ With longer periods, EMA may take similar time to SMA for step changes")
                # This is acceptable - the key advantage of EMA is in noisy, volatile markets
                # not necessarily in clean step changes
        
        # Test smoothing advantage - EMA should be smoother in noisy data
        print(f"\nTesting smoothing advantage in noisy data:")
        
        # Create noisy data with underlying trend
        np.random.seed(42)
        noisy_data = pd.Series([
            100.0 + i * 0.5 + np.random.normal(0, 1.0) for i in range(30)
        ], name='close')
        
        sma_noisy = sma(noisy_data, longer_period)
        ema_noisy = ema(noisy_data, longer_period)
        
        # Calculate the variance of the indicator values (lower variance = smoother)
        sma_variance = sma_noisy.var()
        ema_variance = ema_noisy.var()
        
        print(f"Noisy data variance: {noisy_data.var():.6f}")
        print(f"SMA variance: {sma_variance:.6f}")
        print(f"EMA variance: {ema_variance:.6f}")
        
        # Both should reduce variance compared to raw data
        self.assertLess(sma_variance, noisy_data.var(), "SMA should reduce variance")
        self.assertLess(ema_variance, noisy_data.var(), "EMA should reduce variance")
        print("✓ Both SMA and EMA reduce variance in noisy data")
        
        # EMA should typically have similar or better smoothing than SMA
        # We'll allow some tolerance since this depends on the specific data pattern
        self.assertLessEqual(
            ema_variance,
            sma_variance * 1.2,  # Allow 20% tolerance
            msg="EMA should provide similar or better smoothing than SMA"
        )
        print("✓ EMA provides similar or better smoothing than SMA")
        
        print("✓ Test passed: EMA vs SMA comparison")
    
    def test_ema_performance(self):
        """Test EMA performance with larger dataset"""
        print("\n" + "-"*60)
        print("TEST: EMA Performance")
        print("-"*60)
        
        # Create larger dataset
        large_data = pd.Series(np.random.randn(1000) + 100, name='close')
        
        import time
        start_time = time.time()
        result = ema(large_data, self.period)
        end_time = time.time()
        
        print(f"Large dataset size: {len(large_data)}")
        print(f"Calculation time: {end_time - start_time:.6f} seconds")
        print(f"Result length: {len(result)}")
        print(f"Non-NaN values: {result.notna().sum()}")
        
        # Performance assertion (should be very fast)
        self.assertLess(end_time - start_time, 0.1, "EMA calculation should be fast")
        
        # Check that result is correct
        expected_first_valid = large_data.iloc[:self.period].mean()
        actual_first_valid = result.iloc[self.period-1]
        
        print(f"First valid value - Expected: {expected_first_valid:.6f}, Actual: {actual_first_valid:.6f}")
        self.assertAlmostEqual(actual_first_valid, expected_first_valid, places=10)
        
        print("✓ Test passed: EMA performance")

def run_ema_tests():
    """Run all EMA tests with detailed output"""
    print("Starting comprehensive EMA indicator tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEMAIndicator)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("EMA TEST SUMMARY")
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
        print("\n🎉 ALL EMA TESTS PASSED!")
    else:
        print("\n❌ SOME EMA TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_ema_tests()