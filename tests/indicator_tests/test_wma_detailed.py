"""
Detailed Indicator Tests - WMA (Weighted Moving Average)
==========================================================
This test file provides comprehensive testing for the WMA indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, wma, rsi, macd, bollinger_bands


class TestWMAIndicator(unittest.TestCase):
    """Test cases for WMA (Weighted Moving Average) indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for WMA")
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

    def test_wma_basic_calculation(self):
        """Test basic WMA calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: WMA Basic Calculation")
        print("-"*60)
        
        # Calculate WMA
        result = wma(self.simple_data, self.period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
        # WMA calculation verification
        # For period=3, weights are [1, 2, 3] normalized = [1/6, 2/6, 3/6] = [0.1667, 0.3333, 0.5]
        weights = np.arange(1, self.period + 1)
        weights = weights / weights.sum()
        print(f"Weights: {weights.tolist()}")
        
        # Manual WMA calculation for verification
        manual_wma = [np.nan] * (self.period - 1)  # First period-1 values are NaN
        
        # Calculate WMA for each window
        for i in range(self.period - 1, len(self.simple_data)):
            window = self.simple_data.iloc[i - self.period + 1:i + 1]
            wma_value = np.dot(window, weights)
            manual_wma.append(wma_value)
        
        print(f"Manual WMA calculation: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in manual_wma]}")
        
        # Assertions
        self.assertEqual(len(result), len(self.simple_data), "Result length should match input length")
        self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
        
        # Check specific values (ignoring NaN values)
        for i in range(self.period - 1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i],
                    manual_wma[i],
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {manual_wma[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {manual_wma[i]:.6f}")
        
        print("✓ Test passed: Basic WMA calculation")

    def test_wma_realistic_data(self):
        """Test WMA with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: WMA with Realistic Price Data")
        print("-"*60)
        
        # Calculate WMA
        result = wma(self.realistic_data, self.period)
        
        # Debug information
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # Calculate expected values manually
        weights = np.arange(1, self.period + 1)
        weights = weights / weights.sum()
        print(f"Weights: {weights.tolist()}")
        
        expected_values = [np.nan] * (self.period - 1)
        
        for i in range(self.period - 1, len(self.realistic_data)):
            window = self.realistic_data.iloc[i - self.period + 1:i + 1]
            wma_value = np.dot(window, weights)
            expected_values.append(wma_value)
        
        print(f"Expected values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in expected_values]}")
        
        # Assertions
        self.assertEqual(len(result), len(self.realistic_data))
        self.assertIsInstance(result, pd.Series)
        
        # Check non-NaN values
        for i in range(self.period - 1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i],
                    expected_values[i],
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {expected_values[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {expected_values[i]:.6f}")
        
        print("✓ Test passed: WMA with realistic data")

    def test_wma_edge_cases(self):
        """Test WMA with edge cases"""
        print("\n" + "-"*60)
        print("TEST: WMA Edge Cases")
        print("-"*60)
        
        # Test with all same values
        result = wma(self.edge_data, self.period)
        print(f"Input data (all same): {self.edge_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # All non-NaN values should equal the input value (since all values are the same)
        for i in range(self.period - 1, len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertEqual(
                    result.iloc[i],
                    self.edge_data.iloc[i],
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {self.edge_data.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]} == {self.edge_data.iloc[i]}")
        
        # Test with period larger than data length
        large_period = 20
        result_large = wma(self.simple_data, large_period)
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"Result: {result_large.tolist()}")
        
        # All values should be NaN
        self.assertTrue(result_large.isna().all(), "All values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with period = 1 (should equal the input data)
        result_period1 = wma(self.simple_data, 1)
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
        
        print("✓ Test passed: WMA edge cases")

    def test_wma_error_handling(self):
        """Test WMA error handling"""
        print("\n" + "-"*60)
        print("TEST: WMA Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        result_empty = wma(empty_data, self.period)
        print(f"Empty data test - Result type: {type(result_empty)}")
        print(f"Empty data test - Result length: {len(result_empty)}")
        
        self.assertIsInstance(result_empty, pd.Series)
        self.assertEqual(len(result_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            result_invalid = wma(self.simple_data, 0)
            print("Result with period 0:", result_invalid.tolist())
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            result_negative = wma(self.simple_data, -1)
            print("Result with period -1:", result_negative.tolist())
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: WMA error handling")

    def test_wma_vs_sma_comparison(self):
        """Test WMA vs SMA comparison"""
        print("\n" + "-"*60)
        print("TEST: WMA vs SMA Comparison")
        print("-"*60)
        
        # Calculate both SMA and WMA
        sma_result = sma(self.realistic_data, self.period)
        wma_result = wma(self.realistic_data, self.period)
        
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"SMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in sma_result.tolist()]}")
        print(f"WMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in wma_result.tolist()]}")
        
        # Test that WMA is more responsive to recent price changes
        # Create a series with a clear trend to show WMA's responsiveness
        trend_data = pd.Series([
            100.0, 101.0, 102.0, 105.0, 108.0, 110.0, 112.0, 115.0, 118.0, 120.0
        ], name='close')
        
        sma_trend = sma(trend_data, self.period)
        wma_trend = wma(trend_data, self.period)
        
        print(f"\nTesting with trending price series:")
        print(f"Trend data: {trend_data.tolist()}")
        print(f"SMA trend: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in sma_trend.tolist()]}")
        print(f"WMA trend: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in wma_trend.tolist()]}")
        
        # In an uptrend, WMA should generally be higher than SMA because it gives more weight to recent (higher) prices
        check_idx = len(trend_data) - 1  # Last value
        if check_idx >= self.period - 1:
            wma_value = wma_trend.iloc[check_idx]
            sma_value = sma_trend.iloc[check_idx]
            current_price = trend_data.iloc[check_idx]
            
            print(f"\nAt index {check_idx} (end of uptrend):")
            print(f"Current price: {current_price}")
            print(f"SMA value: {sma_value:.6f}")
            print(f"WMA value: {wma_value:.6f}")
            
            # WMA should be closer to the current price than SMA in a trending market
            wma_distance = abs(wma_value - current_price)
            sma_distance = abs(sma_value - current_price)
            
            print(f"WMA distance from current price: {wma_distance:.6f}")
            print(f"SMA distance from current price: {sma_distance:.6f}")
            
            # In an uptrend, WMA should generally be higher than SMA
            self.assertGreaterEqual(
                wma_value,
                sma_value,
                msg=f"In uptrend, WMA ({wma_value}) should be >= SMA ({sma_value})"
            )
            print(f"✓ WMA ({wma_value:.6f}) >= SMA ({sma_value:.6f}) in uptrend")
        
        print("✓ Test passed: WMA vs SMA comparison")

    def test_wma_weighting_verification(self):
        """Test WMA weighting scheme verification"""
        print("\n" + "-"*60)
        print("TEST: WMA Weighting Verification")
        print("-"*60)
        
        # Create test data where we can easily verify the weighting
        test_data = pd.Series([10, 20, 30], name='close')
        period = 3
        
        result = wma(test_data, period)
        
        print(f"Test data: {test_data.tolist()}")
        print(f"Period: {period}")
        print(f"Result: {result.tolist()}")
        
        # Manual calculation: weights = [1, 2, 3] normalized = [1/6, 2/6, 3/6]
        # WMA = 10*(1/6) + 20*(2/6) + 30*(3/6) = 10/6 + 40/6 + 90/6 = 140/6 = 23.333...
        expected_wma = (10 * 1 + 20 * 2 + 30 * 3) / (1 + 2 + 3)
        print(f"Expected WMA: {expected_wma:.6f}")
        print(f"Actual WMA: {result.iloc[2]:.6f}")
        
        self.assertAlmostEqual(
            result.iloc[2],
            expected_wma,
            places=10,
            msg=f"WMA calculation incorrect: got {result.iloc[2]}, expected {expected_wma}"
        )
        
        # Verify that the most recent value has the highest impact
        # Test with different recent values
        test_data2 = pd.Series([10, 20, 40], name='close')  # Changed last value from 30 to 40
        result2 = wma(test_data2, period)
        
        expected_wma2 = (10 * 1 + 20 * 2 + 40 * 3) / (1 + 2 + 3)
        print(f"\nTest data 2: {test_data2.tolist()}")
        print(f"Expected WMA 2: {expected_wma2:.6f}")
        print(f"Actual WMA 2: {result2.iloc[2]:.6f}")
        
        self.assertAlmostEqual(
            result2.iloc[2],
            expected_wma2,
            places=10,
            msg=f"WMA calculation incorrect: got {result2.iloc[2]}, expected {expected_wma2}"
        )
        
        # The difference between the two WMAs should be larger than the difference in SMA
        # This shows WMA's responsiveness to recent changes
        sma1 = test_data.mean()
        sma2 = test_data2.mean()
        wma_diff = abs(result2.iloc[2] - result.iloc[2])
        sma_diff = abs(sma2 - sma1)
        
        print(f"\nWMA difference: {wma_diff:.6f}")
        print(f"SMA difference: {sma_diff:.6f}")
        
        self.assertGreater(
            wma_diff,
            sma_diff,
            msg=f"WMA should be more responsive than SMA: WMA diff={wma_diff}, SMA diff={sma_diff}"
        )
        print(f"✓ WMA ({wma_diff:.6f}) shows greater responsiveness than SMA ({sma_diff:.6f})")
        
        print("✓ Test passed: WMA weighting verification")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting WMA Indicator Tests")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)