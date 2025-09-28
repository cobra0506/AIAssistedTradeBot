"""
Detailed Indicator Tests - Lowest Value Over Period
=================================================
This test file provides comprehensive testing for the lowest value indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import lowest

class TestLowestIndicator(unittest.TestCase):
    """Test cases for Lowest Value indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for Lowest Value")
        print("=" * 60)
        
        # Create simple test data for lowest testing
        self.simple_data = pd.Series([10, 8, 12, 9, 11, 7, 13, 6, 14, 5], name='data')
        self.period = 5
        
        # Create more realistic price data
        np.random.seed(42)  # For reproducible results
        base_prices = np.array([100, 102, 101, 103, 104, 103, 105, 106, 105, 107])
        # Add some realistic variation
        self.realistic_data = pd.Series(base_prices + np.random.uniform(-2, 2, 10), name='realistic_data')
        
        # Create edge case data
        self.constant_data = pd.Series([100.0] * 10, name='constant')
        self.increasing_data = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], name='increasing')
        self.decreasing_data = pd.Series([109, 108, 107, 106, 105, 104, 103, 102, 101, 100], name='decreasing')
        self.volatile_data = pd.Series([100, 95, 105, 90, 110, 85, 115, 80, 120, 75], name='volatile')
        
        print(f"Simple data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{int(x)}" if not pd.isna(x) and x == int(x) else f"{x:.2f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_lowest_basic_calculation(self):
        """Test basic lowest calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: Lowest Basic Calculation")
        print("-" * 60)
        
        # Calculate lowest values
        lowest_result = lowest(self.simple_data, self.period)
        
        # Debug information
        print(f"Data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Lowest result: {self._format_series(lowest_result)}")
        print(f"Lowest type: {type(lowest_result)}")
        print(f"Lowest length: {len(lowest_result)}")
        
        # Manual calculation verification
        expected_lowest = []
        
        for i in range(len(self.simple_data)):
            # Determine the window
            start_idx = max(0, i - self.period + 1)
            end_idx = i + 1
            window = self.simple_data.iloc[start_idx:end_idx]
            
            # Calculate lowest for this window
            window_min = window.min()
            expected_lowest.append(window_min)
        
        print(f"Expected lowest values: {[f'{x:.1f}' for x in expected_lowest]}")
        
        # Verify all calculations
        for i in range(len(lowest_result)):
            self.assertAlmostEqual(
                float(lowest_result.iloc[i]), 
                expected_lowest[i], 
                places=5,
                msg=f"Lowest calculation incorrect at index {i}: got {float(lowest_result.iloc[i])}, expected {expected_lowest[i]}"
            )
        print("✓ All lowest calculations are correct")
        
        # Verify that lowest values are always <= the original values
        for i in range(len(lowest_result)):
            if not pd.isna(lowest_result.iloc[i]):
                lowest_val = float(lowest_result.iloc[i])
                original_val = float(self.simple_data.iloc[i])
                self.assertTrue(
                    lowest_val <= original_val,
                    f"Lowest value ({lowest_val}) should be <= original value ({original_val}) at index {i}"
                )
        print("✓ All lowest values are <= original values")
        
        print("✓ Test passed: Basic lowest calculation")
    
    def test_lowest_edge_cases(self):
        """Test lowest with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: Lowest Edge Cases")
        print("-" * 60)
        
        # Test with constant data
        print(f"Constant data: {self.constant_data.tolist()}")
        
        lowest_result = lowest(self.constant_data, self.period)
        print(f"Constant data lowest: {self._format_series(lowest_result)}")
        
        # With constant data, lowest should equal the constant value
        for i in range(len(lowest_result)):
            if not pd.isna(lowest_result.iloc[i]):
                self.assertEqual(
                    float(lowest_result.iloc[i]), 
                    100.0, 
                    f"With constant data, lowest should be 100 at index {i}: got {float(lowest_result.iloc[i])}"
                )
        print("✓ Constant data lowest equals constant value")
        
        # Test with increasing data
        print(f"\nIncreasing data: {self.increasing_data.tolist()}")
        
        lowest_result = lowest(self.increasing_data, self.period)
        print(f"Increasing data lowest: {self._format_series(lowest_result)}")
        
        # With increasing data, lowest should be the first value in each window
        for i in range(len(lowest_result)):
            if not pd.isna(lowest_result.iloc[i]):
                start_idx = max(0, i - self.period + 1)
                end_idx = i + 1
                expected_min = self.increasing_data.iloc[start_idx:end_idx].min()
                
                self.assertEqual(
                    float(lowest_result.iloc[i]), 
                    expected_min, 
                    f"With increasing data, lowest should be {expected_min} at index {i}: got {float(lowest_result.iloc[i])}"
                )
        print("✓ Increasing data lowest correctly identified")
        
        # Test with decreasing data
        print(f"\nDecreasing data: {self.decreasing_data.tolist()}")
        
        lowest_result = lowest(self.decreasing_data, self.period)
        print(f"Decreasing data lowest: {self._format_series(lowest_result)}")
        
        # With decreasing data, lowest should be the last value in each window
        for i in range(len(lowest_result)):
            if not pd.isna(lowest_result.iloc[i]):
                start_idx = max(0, i - self.period + 1)
                end_idx = i + 1
                expected_min = self.decreasing_data.iloc[start_idx:end_idx].min()
                
                self.assertEqual(
                    float(lowest_result.iloc[i]), 
                    expected_min, 
                    f"With decreasing data, lowest should be {expected_min} at index {i}: got {float(lowest_result.iloc[i])}"
                )
        print("✓ Decreasing data lowest correctly identified")
        
        # Test with period larger than data length
        lowest_result = lowest(self.simple_data, period=20)
        
        print(f"\nTesting with period (20) larger than data length ({len(self.simple_data)})")
        print(f"Lowest result: {self._format_series(lowest_result)}")
        
        # All values should be NaN when period > data length
        for i in range(len(lowest_result)):
            self.assertTrue(
                pd.isna(lowest_result.iloc[i]), 
                f"All values should be NaN when period > data length, but index {i} is {float(lowest_result.iloc[i])}"
            )
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum period (1)
        lowest_result = lowest(self.simple_data, period=1)
        
        print(f"\nTesting with minimum period (1):")
        print(f"Lowest result: {self._format_series(lowest_result)}")
        
        # With period 1, lowest should equal the original data
        for i in range(len(lowest_result)):
            self.assertEqual(
                float(lowest_result.iloc[i]), 
                float(self.simple_data.iloc[i]), 
                f"With period 1, lowest should equal original data at index {i}: got {float(lowest_result.iloc[i])}, expected {float(self.simple_data.iloc[i])}"
            )
        print("✓ With period 1, lowest equals original data")
        
        print("✓ Test passed: Lowest edge cases")
    
    def test_lowest_error_handling(self):
        """Test lowest error handling"""
        print("\n" + "-" * 60)
        print("TEST: Lowest Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_data = pd.Series([], name='empty')
        
        lowest_empty = lowest(empty_data)
        print(f"Empty data test - Lowest type: {type(lowest_empty)}")
        print(f"Empty data test - Lowest length: {len(lowest_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(lowest_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with period 0
        try:
            lowest_zero_period = lowest(self.simple_data, period=0)
            print(f"Result with period 0:")
            print(f"Lowest: {self._format_series(lowest_zero_period)}")
            
            # All values should be NaN with period 0
            for i in range(len(lowest_zero_period)):
                self.assertTrue(pd.isna(lowest_zero_period.iloc[i]), f"Value at index {i} should be NaN with period 0")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Error with period 0: {e}")
            self.fail(f"Failed to handle period 0: {e}")
        
        # Test with negative period
        try:
            lowest_neg_period = lowest(self.simple_data, period=-1)
            print(f"Result with period -1:")
            print(f"Lowest: {self._format_series(lowest_neg_period)}")
            
            # All values should be NaN with negative period
            for i in range(len(lowest_neg_period)):
                self.assertTrue(pd.isna(lowest_neg_period.iloc[i]), f"Value at index {i} should be NaN with negative period")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Error with negative period: {e}")
            self.fail(f"Failed to handle negative period: {e}")
        
        # Test with NaN values
        nan_data = pd.Series([10, np.nan, 12, 9, np.nan, 7], name='nan_data')
        
        print(f"\nTesting with NaN values:")
        print(f"Data with NaN: {self._format_series(nan_data)}")
        
        lowest_nan = lowest(nan_data, period=3)
        print(f"Lowest with NaN: {self._format_series(lowest_nan)}")
        
        # Should handle NaN values gracefully
        self.assertEqual(len(lowest_nan), len(nan_data))
        print("✓ Handles NaN values correctly")
        
        print("✓ Test passed: Lowest error handling")
    
    def test_lowest_realistic_data(self):
        """Test lowest with realistic price data"""
        print("\n" + "-" * 60)
        print("TEST: Lowest with Realistic Data")
        print("-" * 60)
        
        print(f"Realistic data: {[f'{x:.2f}' for x in self.realistic_data.tolist()]}")
        
        lowest_result = lowest(self.realistic_data, self.period)
        
        print(f"Lowest result: {self._format_series(lowest_result)}")
        
        # Verify that lowest values are reasonable for the data
        for i in range(len(lowest_result)):
            if not pd.isna(lowest_result.iloc[i]):
                lowest_val = float(lowest_result.iloc[i])
                original_val = float(self.realistic_data.iloc[i])
                
                # Lowest should be <= original value
                self.assertTrue(
                    lowest_val <= original_val,
                    f"Lowest value ({lowest_val}) should be <= original value ({original_val}) at index {i}"
                )
        
        # Check that lowest values are non-increasing (for expanding window)
        for i in range(1, min(self.period, len(lowest_result))):
            if not pd.isna(lowest_result.iloc[i]) and not pd.isna(lowest_result.iloc[i-1]):
                current_lowest = float(lowest_result.iloc[i])
                previous_lowest = float(lowest_result.iloc[i-1])
                
                # For the first few values (before period is reached), lowest should be non-increasing
                self.assertTrue(
                    current_lowest <= previous_lowest,
                    f"Lowest should be non-increasing at index {i}: {previous_lowest} -> {current_lowest}"
                )
        
        # Find the overall lowest in the data
        overall_lowest = self.realistic_data.min()
        print(f"Overall lowest in data: {overall_lowest:.2f}")
        
        # The lowest values should approach the overall lowest
        valid_lowest_values = [float(x) for x in lowest_result if not pd.isna(x)]
        if valid_lowest_values:
            min_calculated_lowest = min(valid_lowest_values)
            print(f"Minimum calculated lowest: {min_calculated_lowest:.2f}")
            
            self.assertAlmostEqual(
                min_calculated_lowest,
                overall_lowest,
                places=5,
                msg=f"Minimum calculated lowest should equal overall lowest: {min_calculated_lowest} vs {overall_lowest}"
            )
            print("✓ Minimum calculated lowest equals overall lowest")
        
        print("✓ Test passed: Lowest with realistic data")
    
    def test_lowest_different_periods(self):
        """Test lowest with different period values"""
        print("\n" + "-" * 60)
        print("TEST: Lowest with Different Periods")
        print("-" * 60)
        
        # Test with different periods
        periods_to_test = [1, 3, 5, 10]
        
        for period in periods_to_test:
            print(f"\nTesting with period {period}:")
            
            lowest_result = lowest(self.simple_data, period)
            print(f"Lowest result: {self._format_series(lowest_result)}")
            
            # Verify calculations for this period
            for i in range(len(lowest_result)):
                if not pd.isna(lowest_result.iloc[i]):
                    start_idx = max(0, i - period + 1)
                    end_idx = i + 1
                    expected_min = self.simple_data.iloc[start_idx:end_idx].min()
                    
                    self.assertEqual(
                        float(lowest_result.iloc[i]), 
                        expected_min, 
                        msg=f"Lowest calculation incorrect at index {i} with period {period}: got {float(lowest_result.iloc[i])}, expected {expected_min}"
                    )
            
            print(f"✓ Period {period} calculations are correct")
        
        # Test behavior with volatile data
        print(f"\nTesting with volatile data: {self.volatile_data.tolist()}")
        
        for period in [3, 5]:
            lowest_result = lowest(self.volatile_data, period)
            print(f"Period {period} lowest: {self._format_series(lowest_result)}")
            
            # Verify that lowest captures the troughs correctly
            expected_troughs = []
            for i in range(len(self.volatile_data)):
                start_idx = max(0, i - period + 1)
                end_idx = i + 1
                expected_troughs.append(self.volatile_data.iloc[start_idx:end_idx].min())
            
            for i in range(len(lowest_result)):
                if not pd.isna(lowest_result.iloc[i]):
                    self.assertEqual(
                        float(lowest_result.iloc[i]), 
                        expected_troughs[i], 
                        msg=f"Volatile data lowest incorrect at index {i} with period {period}"
                    )
            
            print(f"✓ Period {period} correctly captures troughs in volatile data")
        
        print("✓ Test passed: Lowest with different periods")
    
    def test_lowest_vs_highest_comparison(self):
        """Test lowest vs highest comparison"""
        print("\n" + "-" * 60)
        print("TEST: Lowest vs Highest Comparison")
        print("-" * 60)
        
        # Import highest function
        from simple_strategy.strategies.indicators_library import highest
        
        print(f"Data: {self.simple_data.tolist()}")
        
        # Calculate both highest and lowest
        highest_result = highest(self.simple_data, self.period)
        lowest_result = lowest(self.simple_data, self.period)
        
        print(f"Highest result: {self._format_series(highest_result)}")
        print(f"Lowest result: {self._format_series(lowest_result)}")
        
        # Verify that highest >= lowest for all valid values
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]) and not pd.isna(lowest_result.iloc[i]):
                highest_val = float(highest_result.iloc[i])
                lowest_val = float(lowest_result.iloc[i])
                
                self.assertTrue(
                    highest_val >= lowest_val,
                    f"Highest ({highest_val}) should be >= lowest ({lowest_val}) at index {i}"
                )
        print("✓ Highest is always >= lowest for all valid values")
        
        # Test with constant data
        print(f"\nTesting with constant data: {self.constant_data.tolist()}")
        
        highest_const = highest(self.constant_data, self.period)
        lowest_const = lowest(self.constant_data, self.period)
        
        print(f"Constant highest: {self._format_series(highest_const)}")
        print(f"Constant lowest: {self._format_series(lowest_const)}")
        
        # With constant data, highest should equal lowest
        for i in range(len(highest_const)):
            if not pd.isna(highest_const.iloc[i]) and not pd.isna(lowest_const.iloc[i]):
                self.assertEqual(
                    float(highest_const.iloc[i]),
                    float(lowest_const.iloc[i]),
                    f"With constant data, highest should equal lowest at index {i}"
                )
        print("✓ With constant data, highest equals lowest")
        
        print("✓ Test passed: Lowest vs Highest comparison")

if __name__ == '__main__':
    print("📊 Starting Lowest Value Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)