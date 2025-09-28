"""
Detailed Indicator Tests - Crossover Signal Generator
====================================================
This test file provides comprehensive testing for the crossover signal generator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import crossover, sma

class TestCrossoverIndicator(unittest.TestCase):
    """Test cases for Crossover signal generator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for Crossover")
        print("=" * 60)
        
        # Create simple test data for crossover testing
        self.series1 = pd.Series([10, 12, 14, 13, 15, 17, 16, 18, 20, 19], name='series1')
        self.series2 = pd.Series([11, 11, 13, 14, 14, 16, 17, 17, 19, 20], name='series2')
        
        # Create moving average data for realistic crossover testing
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
    
    def test_crossover_basic_calculation(self):
        """Test basic crossover calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: Crossover Basic Calculation")
        print("-" * 60)
        
        # Calculate crossover signals
        crossover_result = crossover(self.series1, self.series2)
        
        # Debug information
        print(f"Series 1: {self.series1.tolist()}")
        print(f"Series 2: {self.series2.tolist()}")
        print(f"Crossover result: {self._format_series(crossover_result)}")
        print(f"Crossover type: {type(crossover_result)}")
        print(f"Crossover length: {len(crossover_result)}")
        
        # First value should always be 0 (no crossover on first day)
        self.assertEqual(
            float(crossover_result.iloc[0]), 
            0.0, 
            f"Crossover should start at 0: got {float(crossover_result.iloc[0])}"
        )
        print("✓ Crossover starts at 0")
        
        # Manual crossover detection
        expected_signals = [0]  # Start with 0
        
        for i in range(1, len(self.series1)):
            s1_curr = self.series1.iloc[i]
            s1_prev = self.series1.iloc[i-1]
            s2_curr = self.series2.iloc[i]
            s2_prev = self.series2.iloc[i-1]
            
            # Check for crossover: series1 was below series2, now above
            if (s1_prev <= s2_prev) and (s1_curr > s2_curr):
                expected_signals.append(1)
            else:
                expected_signals.append(0)
        
        print(f"Expected crossover signals: {expected_signals}")
        
        # Verify all calculations
        for i in range(len(crossover_result)):
            self.assertEqual(
                float(crossover_result.iloc[i]), 
                expected_signals[i], 
                msg=f"Crossover calculation incorrect at index {i}: got {float(crossover_result.iloc[i])}, expected {expected_signals[i]}"
            )
        print("✓ All crossover calculations are correct")
        
        # Count the number of crossovers
        actual_crossovers = sum(1 for x in crossover_result if x == 1)
        expected_crossovers = sum(expected_signals)
        
        print(f"Number of crossovers detected: {actual_crossovers}")
        self.assertEqual(actual_crossovers, expected_crossovers, "Crossover count mismatch")
        
        print("✓ Test passed: Basic crossover calculation")
    
    def test_crossover_moving_averages(self):
        """Test crossover with moving averages (realistic use case)"""
        print("\n" + "-" * 60)
        print("TEST: Crossover with Moving Averages")
        print("-" * 60)
        
        print(f"Prices: {self.prices.tolist()}")
        print(f"Fast MA (3): {self._format_series(self.fast_ma)}")
        print(f"Slow MA (5): {self._format_series(self.slow_ma)}")
        
        # Calculate crossover signals
        crossover_result = crossover(self.fast_ma, self.slow_ma)
        
        print(f"Crossover result: {self._format_series(crossover_result)}")
        
        # First value should always be 0
        self.assertEqual(float(crossover_result.iloc[0]), 0.0, "Crossover should start at 0")
        
        # Manual verification of crossovers
        print("\nManual crossover verification:")
        crossovers_found = []
        
        for i in range(1, len(self.fast_ma)):
            if pd.isna(self.fast_ma.iloc[i]) or pd.isna(self.slow_ma.iloc[i]):
                print(f"Index {i}: NaN values, skipping")
                continue
                
            fast_curr = float(self.fast_ma.iloc[i])
            fast_prev = float(self.fast_ma.iloc[i-1])
            slow_curr = float(self.slow_ma.iloc[i])
            slow_prev = float(self.slow_ma.iloc[i-1])
            
            crossover_detected = (fast_prev <= slow_prev) and (fast_curr > slow_curr)
            signal_value = float(crossover_result.iloc[i])
            
            expected_signal = 1 if crossover_detected else 0
            
            print(f"Index {i}: Fast {fast_prev:.2f}->{fast_curr:.2f}, Slow {slow_prev:.2f}->{slow_curr:.2f}, "
                  f"Crossover: {crossover_detected}, Signal: {signal_value}, Expected: {expected_signal}")
            
            self.assertEqual(signal_value, expected_signal, 
                           f"Crossover signal incorrect at index {i}")
            
            if crossover_detected:
                crossovers_found.append(i)
        
        print(f"Crossovers found at indices: {crossovers_found}")
        
        # Verify that signals are only 0 or 1
        for i in range(len(crossover_result)):
            if not pd.isna(crossover_result.iloc[i]):
                signal = float(crossover_result.iloc[i])
                self.assertIn(signal, [0, 1], 
                              f"Crossover signal should be 0 or 1, got {signal} at index {i}")
        
        print("✓ All crossover signals are valid (0 or 1)")
        print("✓ Test passed: Crossover with moving averages")
    
    def test_crossover_edge_cases(self):
        """Test crossover with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: Crossover Edge Cases")
        print("-" * 60)
        
        # Test with constant series (no crossovers expected)
        print(f"Constant series 1: {self.constant_series.tolist()}")
        print(f"Constant series 2: {self.constant_series.tolist()}")
        
        crossover_result = crossover(self.constant_series, self.constant_series)
        print(f"Constant series crossover: {self._format_series(crossover_result)}")
        
        # With constant equal series, no crossovers should occur
        for i in range(len(crossover_result)):
            self.assertEqual(
                float(crossover_result.iloc[i]), 
                0.0, 
                f"With constant equal series, crossover should be 0 at index {i}: got {float(crossover_result.iloc[i])}"
            )
        print("✓ No crossovers with constant equal series")
        
        # Test with series that never cross (series1 always above series2)
        always_above = pd.Series([110, 111, 112, 113, 114, 115, 116, 117, 118, 119], name='always_above')
        always_below = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], name='always_below')
        
        print(f"\nTesting with non-crossing series (always above vs always below):")
        print(f"Always above series: {always_above.tolist()}")
        print(f"Always below series: {always_below.tolist()}")
        
        crossover_result = crossover(always_above, always_below)
        print(f"Non-crossing crossover: {self._format_series(crossover_result)}")
        
        # These series should never cross (always above stays above always below)
        for i in range(len(crossover_result)):
            self.assertEqual(
                float(crossover_result.iloc[i]), 
                0.0, 
                f"Non-crossing series should have no crossovers at index {i}: got {float(crossover_result.iloc[i])}"
            )
        print("✓ No crossovers with non-crossing series")
        
        # Test with the original increasing vs decreasing series (they do cross)
        print(f"\nTesting with increasing vs decreasing series (they do cross):")
        print(f"Increasing series: {self.increasing_series.tolist()}")
        print(f"Decreasing series: {self.decreasing_series.tolist()}")
        
        crossover_result = crossover(self.increasing_series, self.decreasing_series)
        print(f"Increasing vs decreasing crossover: {self._format_series(crossover_result)}")
        
        # Let's manually verify where they cross
        print("Manual verification of crossover points:")
        for i in range(1, len(self.increasing_series)):
            s1_curr = self.increasing_series.iloc[i]
            s1_prev = self.increasing_series.iloc[i-1]
            s2_curr = self.decreasing_series.iloc[i]
            s2_prev = self.decreasing_series.iloc[i-1]
            
            crossover_detected = (s1_prev <= s2_prev) and (s1_curr > s2_curr)
            signal_value = float(crossover_result.iloc[i])
            
            if crossover_detected:
                print(f"  Crossover at index {i}: {s1_prev} -> {s1_curr} crosses {s2_prev} -> {s2_curr}")
            
            expected_signal = 1 if crossover_detected else 0
            self.assertEqual(signal_value, expected_signal, 
                            f"Crossover signal incorrect at index {i}")
        
        # Count the crossovers
        crossover_count = sum(1 for x in crossover_result if x == 1)
        print(f"Total crossovers detected: {crossover_count}")
        
        # Should have exactly one crossover
        self.assertEqual(crossover_count, 1, f"Should have exactly 1 crossover, got {crossover_count}")
        print("✓ Correctly detected the crossover between increasing and decreasing series")
        
        # Test with different length inputs
        long_series = pd.Series([10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32])
        short_series = pd.Series([11, 13, 15, 17, 19, 21, 23, 25, 27, 29])
        
        print(f"\nTesting with different length inputs:")
        print(f"Long series length: {len(long_series)}")
        print(f"Short series length: {len(short_series)}")
        
        crossover_result = crossover(long_series, short_series)
        print(f"Different length crossover: {self._format_series(crossover_result)}")
        print(f"Result length: {len(crossover_result)}")
        
        # Should use the minimum length
        self.assertEqual(len(crossover_result), min(len(long_series), len(short_series)))
        print("✓ Handles different length inputs correctly")
        
        print("✓ Test passed: Crossover edge cases")
    
    def test_crossover_error_handling(self):
        """Test crossover error handling"""
        print("\n" + "-" * 60)
        print("TEST: Crossover Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_series = pd.Series([], name='empty')
        
        crossover_empty = crossover(empty_series, empty_series)
        print(f"Empty data test - Crossover type: {type(crossover_empty)}")
        print(f"Empty data test - Crossover length: {len(crossover_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(crossover_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with one empty series
        crossover_one_empty = crossover(empty_series, self.series1)
        print(f"One empty series test - Crossover length: {len(crossover_one_empty)}")
        self.assertEqual(len(crossover_one_empty), 0, "One empty series should return an empty Series")
        print("✓ Handles one empty series correctly")
        
        # Test with NaN values
        nan_series = pd.Series([10, np.nan, 14, 13, np.nan, 17], name='nan_series')
        normal_series = pd.Series([11, 11, 13, 14, 14, 16], name='normal_series')
        
        print(f"\nTesting with NaN values:")
        print(f"Series with NaN: {self._format_series(nan_series)}")
        print(f"Normal series: {normal_series.tolist()}")
        
        crossover_nan = crossover(nan_series, normal_series)
        print(f"Crossover with NaN: {self._format_series(crossover_nan)}")
        
        # Should handle NaN values gracefully
        self.assertEqual(len(crossover_nan), min(len(nan_series), len(normal_series)))
        print("✓ Handles NaN values correctly")
        
        print("✓ Test passed: Crossover error handling")
    
    def test_crossover_multiple_scenarios(self):
        """Test crossover with multiple scenarios"""
        print("\n" + "-" * 60)
        print("TEST: Crossover Multiple Scenarios")
        print("-" * 60)
        
        # Scenario 1: Single crossover
        single_cross_s1 = pd.Series([10, 11, 12, 13, 14, 15])
        single_cross_s2 = pd.Series([15, 14, 13, 12, 11, 10])
        
        print(f"Single crossover scenario:")
        print(f"Series 1: {single_cross_s1.tolist()}")
        print(f"Series 2: {single_cross_s2.tolist()}")
        
        crossover_result = crossover(single_cross_s1, single_cross_s2)
        print(f"Crossover result: {self._format_series(crossover_result)}")
        
        # Should have exactly one crossover
        crossovers = sum(1 for x in crossover_result if x == 1)
        self.assertEqual(crossovers, 1, f"Should have exactly 1 crossover, got {crossovers}")
        print("✓ Single crossover detected correctly")
        
        # Scenario 2: Multiple crossovers
        multi_cross_s1 = pd.Series([10, 12, 10, 12, 10, 12])
        multi_cross_s2 = pd.Series([11, 11, 11, 11, 11, 11])
        
        print(f"\nMultiple crossover scenario:")
        print(f"Series 1: {multi_cross_s1.tolist()}")
        print(f"Series 2: {multi_cross_s2.tolist()}")
        
        crossover_result = crossover(multi_cross_s1, multi_cross_s2)
        print(f"Crossover result: {self._format_series(crossover_result)}")
        
        # Should have multiple crossovers
        crossovers = sum(1 for x in crossover_result if x == 1)
        self.assertGreater(crossovers, 1, f"Should have multiple crossovers, got {crossovers}")
        print(f"✓ Multiple crossovers detected: {crossovers}")
        
        # Scenario 3: No crossovers
        no_cross_s1 = pd.Series([10, 11, 12, 13, 14, 15])
        no_cross_s2 = pd.Series([20, 21, 22, 23, 24, 25])
        
        print(f"\nNo crossover scenario:")
        print(f"Series 1: {no_cross_s1.tolist()}")
        print(f"Series 2: {no_cross_s2.tolist()}")
        
        crossover_result = crossover(no_cross_s1, no_cross_s2)
        print(f"Crossover result: {self._format_series(crossover_result)}")
        
        # Should have no crossovers
        crossovers = sum(1 for x in crossover_result if x == 1)
        self.assertEqual(crossovers, 0, f"Should have no crossovers, got {crossovers}")
        print("✓ No crossovers detected correctly")
        
        print("✓ Test passed: Crossover multiple scenarios")

if __name__ == '__main__':
    print("📊 Starting Crossover Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)