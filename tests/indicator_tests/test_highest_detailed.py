"""
Detailed Indicator Tests - Highest Value Over Period
==================================================
This test file provides comprehensive testing for the highest value indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import highest

class TestHighestIndicator(unittest.TestCase):
    """Test cases for Highest Value indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for Highest Value")
        print("=" * 60)
        
        # Create simple test data for highest testing
        self.simple_data = pd.Series([10, 12, 15, 14, 16, 18, 17, 19, 20, 18], name='data')
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
        self.volatile_data = pd.Series([100, 105, 95, 110, 90, 115, 85, 120, 80, 125], name='volatile')
        
        print(f"Simple data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{int(x)}" if not pd.isna(x) and x == int(x) else f"{x:.2f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_highest_basic_calculation(self):
        """Test basic highest calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: Highest Basic Calculation")
        print("-" * 60)
        
        # Calculate highest values
        highest_result = highest(self.simple_data, self.period)
        
        # Debug information
        print(f"Data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Highest result: {self._format_series(highest_result)}")
        print(f"Highest type: {type(highest_result)}")
        print(f"Highest length: {len(highest_result)}")
        
        # Manual calculation verification
        expected_highest = []
        
        for i in range(len(self.simple_data)):
            # Determine the window
            start_idx = max(0, i - self.period + 1)
            end_idx = i + 1
            window = self.simple_data.iloc[start_idx:end_idx]
            
            # Calculate highest for this window
            window_max = window.max()
            expected_highest.append(window_max)
        
        print(f"Expected highest values: {[f'{x:.1f}' for x in expected_highest]}")
        
        # Verify all calculations
        for i in range(len(highest_result)):
            self.assertAlmostEqual(
                float(highest_result.iloc[i]), 
                expected_highest[i], 
                places=5,
                msg=f"Highest calculation incorrect at index {i}: got {float(highest_result.iloc[i])}, expected {expected_highest[i]}"
            )
        print("✓ All highest calculations are correct")
        
        # Verify that highest values are always >= the original values
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]):
                highest_val = float(highest_result.iloc[i])
                original_val = float(self.simple_data.iloc[i])
                self.assertTrue(
                    highest_val >= original_val,
                    f"Highest value ({highest_val}) should be >= original value ({original_val}) at index {i}"
                )
        print("✓ All highest values are >= original values")
        
        print("✓ Test passed: Basic highest calculation")
    
    def test_highest_edge_cases(self):
        """Test highest with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: Highest Edge Cases")
        print("-" * 60)
        
        # Test with constant data
        print(f"Constant data: {self.constant_data.tolist()}")
        
        highest_result = highest(self.constant_data, self.period)
        print(f"Constant data highest: {self._format_series(highest_result)}")
        
        # With constant data, highest should equal the constant value
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]):
                self.assertEqual(
                    float(highest_result.iloc[i]), 
                    100.0, 
                    f"With constant data, highest should be 100 at index {i}: got {float(highest_result.iloc[i])}"
                )
        print("✓ Constant data highest equals constant value")
        
        # Test with increasing data
        print(f"\nIncreasing data: {self.increasing_data.tolist()}")
        
        highest_result = highest(self.increasing_data, self.period)
        print(f"Increasing data highest: {self._format_series(highest_result)}")
        
        # With increasing data, highest should be the last value in each window
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]):
                start_idx = max(0, i - self.period + 1)
                end_idx = i + 1
                expected_max = self.increasing_data.iloc[start_idx:end_idx].max()
                
                self.assertEqual(
                    float(highest_result.iloc[i]), 
                    expected_max, 
                    f"With increasing data, highest should be {expected_max} at index {i}: got {float(highest_result.iloc[i])}"
                )
        print("✓ Increasing data highest correctly identified")
        
        # Test with decreasing data
        print(f"\nDecreasing data: {self.decreasing_data.tolist()}")
        
        highest_result = highest(self.decreasing_data, self.period)
        print(f"Decreasing data highest: {self._format_series(highest_result)}")
        
        # With decreasing data, highest should be the first value in each window
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]):
                start_idx = max(0, i - self.period + 1)
                end_idx = i + 1
                expected_max = self.decreasing_data.iloc[start_idx:end_idx].max()
                
                self.assertEqual(
                    float(highest_result.iloc[i]), 
                    expected_max, 
                    f"With decreasing data, highest should be {expected_max} at index {i}: got {float(highest_result.iloc[i])}"
                )
        print("✓ Decreasing data highest correctly identified")
        
        # Test with period larger than data length
        highest_result = highest(self.simple_data, period=20)
        
        print(f"\nTesting with period (20) larger than data length ({len(self.simple_data)})")
        print(f"Highest result: {self._format_series(highest_result)}")
        
        # All values should be NaN when period > data length
        for i in range(len(highest_result)):
            self.assertTrue(
                pd.isna(highest_result.iloc[i]), 
                f"All values should be NaN when period > data length, but index {i} is {float(highest_result.iloc[i])}"
            )
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum period (1)
        highest_result = highest(self.simple_data, period=1)
        
        print(f"\nTesting with minimum period (1):")
        print(f"Highest result: {self._format_series(highest_result)}")
        
        # With period 1, highest should equal the original data
        for i in range(len(highest_result)):
            self.assertEqual(
                float(highest_result.iloc[i]), 
                float(self.simple_data.iloc[i]), 
                f"With period 1, highest should equal original data at index {i}: got {float(highest_result.iloc[i])}, expected {float(self.simple_data.iloc[i])}"
            )
        print("✓ With period 1, highest equals original data")
        
        print("✓ Test passed: Highest edge cases")
    
    def test_highest_error_handling(self):
        """Test highest error handling"""
        print("\n" + "-" * 60)
        print("TEST: Highest Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_data = pd.Series([], name='empty')
        
        highest_empty = highest(empty_data)
        print(f"Empty data test - Highest type: {type(highest_empty)}")
        print(f"Empty data test - Highest length: {len(highest_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(highest_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with period 0
        try:
            highest_zero_period = highest(self.simple_data, period=0)
            print(f"Result with period 0:")
            print(f"Highest: {self._format_series(highest_zero_period)}")
            
            # All values should be NaN with period 0
            for i in range(len(highest_zero_period)):
                self.assertTrue(pd.isna(highest_zero_period.iloc[i]), f"Value at index {i} should be NaN with period 0")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Error with period 0: {e}")
            self.fail(f"Failed to handle period 0: {e}")
        
        # Test with negative period
        try:
            highest_neg_period = highest(self.simple_data, period=-1)
            print(f"Result with period -1:")
            print(f"Highest: {self._format_series(highest_neg_period)}")
            
            # All values should be NaN with negative period
            for i in range(len(highest_neg_period)):
                self.assertTrue(pd.isna(highest_neg_period.iloc[i]), f"Value at index {i} should be NaN with negative period")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Error with negative period: {e}")
            self.fail(f"Failed to handle negative period: {e}")
        
        # Test with NaN values
        nan_data = pd.Series([10, np.nan, 15, 14, np.nan, 18], name='nan_data')
        
        print(f"\nTesting with NaN values:")
        print(f"Data with NaN: {self._format_series(nan_data)}")
        
        highest_nan = highest(nan_data, period=3)
        print(f"Highest with NaN: {self._format_series(highest_nan)}")
        
        # Should handle NaN values gracefully
        self.assertEqual(len(highest_nan), len(nan_data))
        print("✓ Handles NaN values correctly")
        
        print("✓ Test passed: Highest error handling")
    
    def test_highest_realistic_data(self):
        """Test highest with realistic price data"""
        print("\n" + "-" * 60)
        print("TEST: Highest with Realistic Data")
        print("-" * 60)
        
        print(f"Realistic data: {[f'{x:.2f}' for x in self.realistic_data.tolist()]}")
        
        highest_result = highest(self.realistic_data, self.period)
        
        print(f"Highest result: {self._format_series(highest_result)}")
        
        # Verify that highest values are reasonable for the data
        for i in range(len(highest_result)):
            if not pd.isna(highest_result.iloc[i]):
                highest_val = float(highest_result.iloc[i])
                original_val = float(self.realistic_data.iloc[i])
                
                # Highest should be >= original value
                self.assertTrue(
                    highest_val >= original_val,
                    f"Highest value ({highest_val}) should be >= original value ({original_val}) at index {i}"
                )
        
        # Check that highest values are non-decreasing (for expanding window)
        for i in range(1, min(self.period, len(highest_result))):
            if not pd.isna(highest_result.iloc[i]) and not pd.isna(highest_result.iloc[i-1]):
                current_highest = float(highest_result.iloc[i])
                previous_highest = float(highest_result.iloc[i-1])
                
                # For the first few values (before period is reached), highest should be non-decreasing
                self.assertTrue(
                    current_highest >= previous_highest,
                    f"Highest should be non-decreasing at index {i}: {previous_highest} -> {current_highest}"
                )
        
        # Find the overall highest in the data
        overall_highest = self.realistic_data.max()
        print(f"Overall highest in data: {overall_highest:.2f}")
        
        # The highest values should approach the overall highest
        valid_highest_values = [float(x) for x in highest_result if not pd.isna(x)]
        if valid_highest_values:
            max_calculated_highest = max(valid_highest_values)
            print(f"Maximum calculated highest: {max_calculated_highest:.2f}")
            
            self.assertAlmostEqual(
                max_calculated_highest,
                overall_highest,
                places=5,
                msg=f"Maximum calculated highest should equal overall highest: {max_calculated_highest} vs {overall_highest}"
            )
            print("✓ Maximum calculated highest equals overall highest")
        
        print("✓ Test passed: Highest with realistic data")
    
    def test_highest_different_periods(self):
        """Test highest with different period values"""
        print("\n" + "-" * 60)
        print("TEST: Highest with Different Periods")
        print("-" * 60)
        
        # Test with different periods
        periods_to_test = [1, 3, 5, 10]
        
        for period in periods_to_test:
            print(f"\nTesting with period {period}:")
            
            highest_result = highest(self.simple_data, period)
            print(f"Highest result: {self._format_series(highest_result)}")
            
            # Verify calculations for this period
            for i in range(len(highest_result)):
                if not pd.isna(highest_result.iloc[i]):
                    start_idx = max(0, i - period + 1)
                    end_idx = i + 1
                    expected_max = self.simple_data.iloc[start_idx:end_idx].max()
                    
                    self.assertEqual(
                        float(highest_result.iloc[i]), 
                        expected_max, 
                        msg=f"Highest calculation incorrect at index {i} with period {period}: got {float(highest_result.iloc[i])}, expected {expected_max}"
                    )
            
            print(f"✓ Period {period} calculations are correct")
        
        # Test behavior with volatile data
        print(f"\nTesting with volatile data: {self.volatile_data.tolist()}")
        
        for period in [3, 5]:
            highest_result = highest(self.volatile_data, period)
            print(f"Period {period} highest: {self._format_series(highest_result)}")
            
            # Verify that highest captures the peaks correctly
            expected_peaks = []
            for i in range(len(self.volatile_data)):
                start_idx = max(0, i - period + 1)
                end_idx = i + 1
                expected_peaks.append(self.volatile_data.iloc[start_idx:end_idx].max())
            
            for i in range(len(highest_result)):
                if not pd.isna(highest_result.iloc[i]):
                    self.assertEqual(
                        float(highest_result.iloc[i]), 
                        expected_peaks[i], 
                        msg=f"Volatile data highest incorrect at index {i} with period {period}"
                    )
            
            print(f"✓ Period {period} correctly captures peaks in volatile data")
        
        print("✓ Test passed: Highest with different periods")

if __name__ == '__main__':
    print("📊 Starting Highest Value Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)