"""
Detailed Indicator Tests - Crossunder Signal Generator
=====================================================
This test file provides comprehensive testing for the crossunder signal generator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import crossunder, sma

class TestCrossunderIndicator(unittest.TestCase):
    """Test cases for Crossunder signal generator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for Crossunder")
        print("=" * 60)
        
        # Create simple test data for crossunder testing
        self.series1 = pd.Series([15, 13, 11, 12, 10, 8, 9, 7, 5, 6], name='series1')
        self.series2 = pd.Series([14, 14, 12, 11, 11, 9, 8, 8, 6, 5], name='series2')
        
        # Create moving average data for realistic crossunder testing
        self.prices = pd.Series([100, 102, 101, 103, 104, 103, 105, 106, 105, 107], name='prices')
        self.fast_ma = sma(self.prices, period=3)  # Fast moving average
        self.slow_ma = sma(self.prices, period=5)  # Slow moving average
        
        # Create edge case data
        self.constant_series = pd.Series([100] * 10, name='constant')
        self.increasing_series = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], name='increasing')
        self.decreasing_series = pd.Series([109, 108, 107, 106, 105, 104, 103, 102, 101, 100], name='decreasing')
        
        print(f"Series 1: {self.series1.tolist()}")
        print(f"Series 2: {self.series2.tolist()}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{int(x)}" if not pd.isna(x) and x == int(x) else f"{x:.2f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_crossunder_basic_calculation(self):
        """Test basic crossunder calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: Crossunder Basic Calculation")
        print("-" * 60)
        
        # Calculate crossunder signals
        crossunder_result = crossunder(self.series1, self.series2)
        
        # Debug information
        print(f"Series 1: {self.series1.tolist()}")
        print(f"Series 2: {self.series2.tolist()}")
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        print(f"Crossunder type: {type(crossunder_result)}")
        print(f"Crossunder length: {len(crossunder_result)}")
        
        # First value should always be 0 (no crossunder on first day)
        self.assertEqual(
            float(crossunder_result.iloc[0]), 
            0.0, 
            f"Crossunder should start at 0: got {float(crossunder_result.iloc[0])}"
        )
        print("✓ Crossunder starts at 0")
        
        # Manual crossunder detection
        expected_signals = [0]  # Start with 0
        
        for i in range(1, len(self.series1)):
            s1_curr = self.series1.iloc[i]
            s1_prev = self.series1.iloc[i-1]
            s2_curr = self.series2.iloc[i]
            s2_prev = self.series2.iloc[i-1]
            
            # Check for crossunder: series1 was above series2, now below
            if (s1_prev >= s2_prev) and (s1_curr < s2_curr):
                expected_signals.append(1)
            else:
                expected_signals.append(0)
        
        print(f"Expected crossunder signals: {expected_signals}")
        
        # Verify all calculations
        for i in range(len(crossunder_result)):
            self.assertEqual(
                float(crossunder_result.iloc[i]), 
                expected_signals[i], 
                msg=f"Crossunder calculation incorrect at index {i}: got {float(crossunder_result.iloc[i])}, expected {expected_signals[i]}"
            )
        print("✓ All crossunder calculations are correct")
        
        # Count the number of crossunders
        actual_crossunders = sum(1 for x in crossunder_result if x == 1)
        expected_crossunders = sum(expected_signals)
        
        print(f"Number of crossunders detected: {actual_crossunders}")
        self.assertEqual(actual_crossunders, expected_crossunders, "Crossunder count mismatch")
        
        print("✓ Test passed: Basic crossunder calculation")
    
    def test_crossunder_moving_averages(self):
        """Test crossunder with moving averages (realistic use case)"""
        print("\n" + "-" * 60)
        print("TEST: Crossunder with Moving Averages")
        print("-" * 60)
        
        print(f"Prices: {self.prices.tolist()}")
        print(f"Fast MA (3): {self._format_series(self.fast_ma)}")
        print(f"Slow MA (5): {self._format_series(self.slow_ma)}")
        
        # Calculate crossunder signals
        crossunder_result = crossunder(self.fast_ma, self.slow_ma)
        
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        
        # First value should always be 0
        self.assertEqual(float(crossunder_result.iloc[0]), 0.0, "Crossunder should start at 0")
        
        # Manual verification of crossunders
        print("\nManual crossunder verification:")
        crossunders_found = []
        
        for i in range(1, len(self.fast_ma)):
            if pd.isna(self.fast_ma.iloc[i]) or pd.isna(self.slow_ma.iloc[i]):
                print(f"Index {i}: NaN values, skipping")
                continue
                
            fast_curr = float(self.fast_ma.iloc[i])
            fast_prev = float(self.fast_ma.iloc[i-1])
            slow_curr = float(self.slow_ma.iloc[i])
            slow_prev = float(self.slow_ma.iloc[i-1])
            
            crossunder_detected = (fast_prev >= slow_prev) and (fast_curr < slow_curr)
            signal_value = float(crossunder_result.iloc[i])
            
            expected_signal = 1 if crossunder_detected else 0
            
            print(f"Index {i}: Fast {fast_prev:.2f}->{fast_curr:.2f}, Slow {slow_prev:.2f}->{slow_curr:.2f}, "
                  f"Crossunder: {crossunder_detected}, Signal: {signal_value}, Expected: {expected_signal}")
            
            self.assertEqual(signal_value, expected_signal, 
                           f"Crossunder signal incorrect at index {i}")
            
            if crossunder_detected:
                crossunders_found.append(i)
        
        print(f"Crossunders found at indices: {crossunders_found}")
        
        # Verify that signals are only 0 or 1
        for i in range(len(crossunder_result)):
            if not pd.isna(crossunder_result.iloc[i]):
                signal = float(crossunder_result.iloc[i])
                self.assertIn(signal, [0, 1], 
                              f"Crossunder signal should be 0 or 1, got {signal} at index {i}")
        
        print("✓ All crossunder signals are valid (0 or 1)")
        print("✓ Test passed: Crossunder with moving averages")
    
    def test_crossunder_edge_cases(self):
        """Test crossunder with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: Crossunder Edge Cases")
        print("-" * 60)
        
        # Test with constant series (no crossunders expected)
        print(f"Constant series 1: {self.constant_series.tolist()}")
        print(f"Constant series 2: {self.constant_series.tolist()}")
        
        crossunder_result = crossunder(self.constant_series, self.constant_series)
        print(f"Constant series crossunder: {self._format_series(crossunder_result)}")
        
        # With constant equal series, no crossunders should occur
        for i in range(len(crossunder_result)):
            self.assertEqual(
                float(crossunder_result.iloc[i]), 
                0.0, 
                f"With constant equal series, crossunder should be 0 at index {i}: got {float(crossunder_result.iloc[i])}"
            )
        print("✓ No crossunders with constant equal series")
        
        # Test with series that never cross (series1 always below series2)
        always_below = pd.Series([90, 91, 92, 93, 94, 95, 96, 97, 98, 99], name='always_below')
        always_above = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], name='always_above')
        
        print(f"\nTesting with non-crossing series (always below vs always above):")
        print(f"Always below series: {always_below.tolist()}")
        print(f"Always above series: {always_above.tolist()}")
        
        crossunder_result = crossunder(always_below, always_above)
        print(f"Non-crossing crossunder: {self._format_series(crossunder_result)}")
        
        # These series should never cross (always below stays below always above)
        for i in range(len(crossunder_result)):
            self.assertEqual(
                float(crossunder_result.iloc[i]), 
                0.0, 
                f"Non-crossing series should have no crossunders at index {i}: got {float(crossunder_result.iloc[i])}"
            )
        print("✓ No crossunders with non-crossing series")
        
        # Test with the original decreasing vs increasing series (they do cross)
        print(f"\nTesting with decreasing vs increasing series (they do cross):")
        print(f"Decreasing series: {self.decreasing_series.tolist()}")
        print(f"Increasing series: {self.increasing_series.tolist()}")
        
        crossunder_result = crossunder(self.decreasing_series, self.increasing_series)
        print(f"Decreasing vs increasing crossunder: {self._format_series(crossunder_result)}")
        
        # Let's manually verify where they cross
        print("Manual verification of crossunder points:")
        for i in range(1, len(self.decreasing_series)):
            s1_curr = self.decreasing_series.iloc[i]
            s1_prev = self.decreasing_series.iloc[i-1]
            s2_curr = self.increasing_series.iloc[i]
            s2_prev = self.increasing_series.iloc[i-1]
            
            crossunder_detected = (s1_prev >= s2_prev) and (s1_curr < s2_curr)
            signal_value = float(crossunder_result.iloc[i])
            
            if crossunder_detected:
                print(f"  Crossunder at index {i}: {s1_prev} -> {s1_curr} crosses {s2_prev} -> {s2_curr}")
        
        # Count the crossunders
        crossunder_count = sum(1 for x in crossunder_result if x == 1)
        print(f"Total crossunders detected: {crossunder_count}")
        
        # Should have exactly one crossunder
        self.assertEqual(crossunder_count, 1, f"Should have exactly 1 crossunder, got {crossunder_count}")
        print("✓ Correctly detected the crossunder between decreasing and increasing series")
        
        # Test with different length inputs
        long_series = pd.Series([20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0, -2])
        short_series = pd.Series([19, 17, 15, 13, 11, 9, 7, 5, 3, 1])
        
        print(f"\nTesting with different length inputs:")
        print(f"Long series length: {len(long_series)}")
        print(f"Short series length: {len(short_series)}")
        
        crossunder_result = crossunder(long_series, short_series)
        print(f"Different length crossunder: {self._format_series(crossunder_result)}")
        print(f"Result length: {len(crossunder_result)}")
        
        # Should use the minimum length
        self.assertEqual(len(crossunder_result), min(len(long_series), len(short_series)))
        print("✓ Handles different length inputs correctly")
        
        print("✓ Test passed: Crossunder edge cases")
    
    def test_crossunder_error_handling(self):
        """Test crossunder error handling"""
        print("\n" + "-" * 60)
        print("TEST: Crossunder Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_series = pd.Series([], name='empty')
        
        crossunder_empty = crossunder(empty_series, empty_series)
        print(f"Empty data test - Crossunder type: {type(crossunder_empty)}")
        print(f"Empty data test - Crossunder length: {len(crossunder_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(crossunder_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with one empty series
        crossunder_one_empty = crossunder(empty_series, self.series1)
        print(f"One empty series test - Crossunder length: {len(crossunder_one_empty)}")
        self.assertEqual(len(crossunder_one_empty), 0, "One empty series should return an empty Series")
        print("✓ Handles one empty series correctly")
        
        # Test with NaN values
        nan_series = pd.Series([15, np.nan, 11, 12, np.nan, 8], name='nan_series')
        normal_series = pd.Series([14, 14, 12, 11, 11, 9], name='normal_series')
        
        print(f"\nTesting with NaN values:")
        print(f"Series with NaN: {self._format_series(nan_series)}")
        print(f"Normal series: {normal_series.tolist()}")
        
        crossunder_nan = crossunder(nan_series, normal_series)
        print(f"Crossunder with NaN: {self._format_series(crossunder_nan)}")
        
        # Should handle NaN values gracefully
        self.assertEqual(len(crossunder_nan), min(len(nan_series), len(normal_series)))
        print("✓ Handles NaN values correctly")
        
        print("✓ Test passed: Crossunder error handling")
    
    def test_crossunder_multiple_scenarios(self):
        """Test crossunder with multiple scenarios"""
        print("\n" + "-" * 60)
        print("TEST: Crossunder Multiple Scenarios")
        print("-" * 60)
        
        # Scenario 1: Single crossunder
        single_cross_s1 = pd.Series([15, 14, 13, 12, 11, 10])
        single_cross_s2 = pd.Series([10, 11, 12, 13, 14, 15])
        
        print(f"Single crossunder scenario:")
        print(f"Series 1: {single_cross_s1.tolist()}")
        print(f"Series 2: {single_cross_s2.tolist()}")
        
        crossunder_result = crossunder(single_cross_s1, single_cross_s2)
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        
        # Should have exactly one crossunder
        crossunders = sum(1 for x in crossunder_result if x == 1)
        self.assertEqual(crossunders, 1, f"Should have exactly 1 crossunder, got {crossunders}")
        print("✓ Single crossunder detected correctly")
        
        # Scenario 2: Multiple crossunders
        multi_cross_s1 = pd.Series([15, 13, 15, 13, 15, 13])
        multi_cross_s2 = pd.Series([14, 14, 14, 14, 14, 14])
        
        print(f"\nMultiple crossunder scenario:")
        print(f"Series 1: {multi_cross_s1.tolist()}")
        print(f"Series 2: {multi_cross_s2.tolist()}")
        
        crossunder_result = crossunder(multi_cross_s1, multi_cross_s2)
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        
        # Should have multiple crossunders
        crossunders = sum(1 for x in crossunder_result if x == 1)
        self.assertGreater(crossunders, 1, f"Should have multiple crossunders, got {crossunders}")
        print(f"✓ Multiple crossunders detected: {crossunders}")
        
        # Scenario 3: No crossunders
        no_cross_s1 = pd.Series([10, 11, 12, 13, 14, 15])
        no_cross_s2 = pd.Series([20, 21, 22, 23, 24, 25])
        
        print(f"\nNo crossunder scenario:")
        print(f"Series 1: {no_cross_s1.tolist()}")
        print(f"Series 2: {no_cross_s2.tolist()}")
        
        crossunder_result = crossunder(no_cross_s1, no_cross_s2)
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        
        # Should have no crossunders
        crossunders = sum(1 for x in crossunder_result if x == 1)
        self.assertEqual(crossunders, 0, f"Should have no crossunders, got {crossunders}")
        print("✓ No crossunders detected correctly")
        
        # Scenario 4: Comparison with crossover (opposite signals)
        from simple_strategy.strategies.indicators_library import crossover
        
        print(f"\nComparison with crossover (opposite signals):")
        print(f"Series 1: {self.series1.tolist()}")
        print(f"Series 2: {self.series2.tolist()}")
        
        crossover_result = crossover(self.series1, self.series2)
        crossunder_result = crossunder(self.series1, self.series2)
        
        print(f"Crossover result: {self._format_series(crossover_result)}")
        print(f"Crossunder result: {self._format_series(crossunder_result)}")
        
        # At any given index, both signals should not be 1
        for i in range(len(crossover_result)):
            if not pd.isna(crossover_result.iloc[i]) and not pd.isna(crossunder_result.iloc[i]):
                cross_sig = float(crossover_result.iloc[i])
                under_sig = float(crossunder_result.iloc[i])
                
                self.assertFalse(
                    cross_sig == 1 and under_sig == 1,
                    f"Both crossover and crossunder cannot be 1 at index {i}"
                )
        
        print("✓ Crossover and crossunder signals are mutually exclusive")
        print("✓ Test passed: Crossunder multiple scenarios")

if __name__ == '__main__':
    print("📊 Starting Crossunder Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)