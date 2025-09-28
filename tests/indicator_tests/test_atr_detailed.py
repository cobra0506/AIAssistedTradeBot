"""
Detailed Indicator Tests - Average True Range (ATR)
==================================================
This test file provides comprehensive testing for the ATR indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import atr

class TestATRIndicator(unittest.TestCase):
    """Test cases for ATR indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for ATR")
        print("=" * 60)
        
        # Create simple test data with high, low, close
        self.simple_high = pd.Series([10, 12, 15, 14, 16, 18, 17, 19, 20, 18], name='high')
        self.simple_low = pd.Series([8, 9, 11, 10, 12, 14, 13, 15, 16, 14], name='low')
        self.simple_close = pd.Series([9, 11, 14, 13, 15, 17, 16, 18, 19, 17], name='close')
        self.period = 5
        
        # Create more realistic price data
        np.random.seed(42)  # For reproducible results
        base_prices = np.array([100, 102, 101, 103, 104, 103, 105, 106, 105, 107])
        # Generate realistic high-low-close data
        self.realistic_high = pd.Series(base_prices + np.random.uniform(1, 3, 10), name='high')
        self.realistic_low = pd.Series(base_prices - np.random.uniform(1, 3, 10), name='low')
        self.realistic_close = pd.Series(base_prices, name='close')
        
        # Create edge case data (constant prices)
        self.edge_high = pd.Series([100.0] * 10, name='high')
        self.edge_low = pd.Series([100.0] * 10, name='low')
        self.edge_close = pd.Series([100.0] * 10, name='close')
        
        # Create trending data for signal analysis
        self.trend_high = pd.Series([100, 105, 110, 115, 120, 118, 115, 110, 105, 100], name='high')
        self.trend_low = pd.Series([95, 100, 105, 110, 115, 113, 110, 105, 100, 95], name='low')
        self.trend_close = pd.Series([98, 103, 108, 113, 118, 116, 113, 108, 103, 98], name='close')
        
        print(f"Simple high data: {self.simple_high.tolist()}")
        print(f"Simple low data: {self.simple_low.tolist()}")
        print(f"Simple close data: {self.simple_close.tolist()}")
        print(f"Period: {self.period}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{x:.6f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_atr_basic_calculation(self):
        """Test basic ATR calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: ATR Basic Calculation")
        print("-" * 60)
        
        # Calculate ATR
        atr_result = atr(self.simple_high, self.simple_low, self.simple_close, self.period)
        
        # Debug information
        print(f"High data: {self.simple_high.tolist()}")
        print(f"Low data: {self.simple_low.tolist()}")
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"Period: {self.period}")
        print(f"ATR result: {self._format_series(atr_result)}")
        print(f"ATR type: {type(atr_result)}")
        print(f"ATR length: {len(atr_result)}")
        
        # Check that the first period-1 values are NaN
        print(f"\nChecking that first {self.period-1} values are NaN:")
        for i in range(self.period - 1):
            is_nan = pd.isna(atr_result.iloc[i])
            print(f"Index {i}: ATR = {float(atr_result.iloc[i]) if not is_nan else 'NaN'}, Is NaN: {is_nan}")
            self.assertTrue(
                is_nan, 
                f"ATR should be NaN at index {i} before period is reached"
            )
        
        # Manual calculation verification for first valid ATR value
        # True Range calculation for indices 0-4 (first valid value with period 5 at index 4)
        true_ranges = []
        print(f"\nCalculating True Ranges manually:")
        
        # For index 0, TR is just High - Low
        tr0 = self.simple_high.iloc[0] - self.simple_low.iloc[0]
        true_ranges.append(tr0)
        print(f"Index 0: TR = {tr0} (High - Low only)")
        
        # For indices 1-4, calculate full TR
        for i in range(1, 5):  # Indices 1-4
            tr1 = self.simple_high.iloc[i] - self.simple_low.iloc[i]
            tr2 = abs(self.simple_high.iloc[i] - self.simple_close.iloc[i-1])
            tr3 = abs(self.simple_low.iloc[i] - self.simple_close.iloc[i-1])
            tr = max(tr1, tr2, tr3)
            true_ranges.append(tr)
            print(f"Index {i}: TR1={tr1}, TR2={tr2}, TR3={tr3}, TR={tr}")
        
        # ATR is the average of True Ranges
        expected_atr = sum(true_ranges) / len(true_ranges)
        
        print(f"\nManual calculation for index 4:")
        print(f"True Ranges: {true_ranges}")
        print(f"Expected ATR: {expected_atr:.6f}")
        print(f"Actual ATR: {float(atr_result.iloc[4]):.6f}")
        
        # Check the calculation at index 4 (first valid value)
        self.assertAlmostEqual(
            float(atr_result.iloc[4]), 
            expected_atr, 
            places=5,
            msg=f"ATR calculation incorrect: got {float(atr_result.iloc[4])}, expected {expected_atr}"
        )
        print(f"✓ ATR calculation correct: {float(atr_result.iloc[4]):.6f} == {expected_atr:.6f}")
        
        # Verify that all values are positive (ATR should always be >= 0)
        for i in range(len(atr_result)):
            if not pd.isna(atr_result.iloc[i]):
                value = float(atr_result.iloc[i])
                self.assertTrue(
                    value >= 0,
                    f"ATR value {value} at index {i} should be non-negative"
                )
        print("✓ All ATR values are non-negative")
        
        print("✓ Test passed: Basic ATR calculation")

    def test_atr_edge_cases(self):
        """Test ATR with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: ATR Edge Cases")
        print("-" * 60)
        
        # Test with constant prices (all high, low, close values are the same)
        print(f"Constant price data - High: {self.edge_high.tolist()}")
        print(f"Constant price data - Low: {self.edge_low.tolist()}")
        print(f"Constant price data - Close: {self.edge_close.tolist()}")
        
        atr_result = atr(self.edge_high, self.edge_low, self.edge_close, period=5)
        
        print(f"ATR result: {self._format_series(atr_result)}")
        
        # With constant prices, ATR should be 0 (no volatility)
        for i in range(len(atr_result)):
            if not pd.isna(atr_result.iloc[i]):
                self.assertEqual(
                    float(atr_result.iloc[i]), 
                    0.0, 
                    f"With constant prices, ATR should be 0 at index {i}: got {float(atr_result.iloc[i])}"
                )
        
        # Test with period larger than data length
        atr_result = atr(self.simple_high, self.simple_low, self.simple_close, period=20)
        
        print(f"\nTesting with period (20) larger than data length ({len(self.simple_high)})")
        print(f"ATR result: {self._format_series(atr_result)}")
        
        # All values should be NaN when period > data length
        for i in range(len(atr_result)):
            self.assertTrue(
                pd.isna(atr_result.iloc[i]), 
                f"All values should be NaN when period > data length, but index {i} is {float(atr_result.iloc[i])}"
            )
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum period (1)
        print(f"\nTesting with minimum period (1):")
        atr_result = atr(self.simple_high, self.simple_low, self.simple_close, period=1)
        
        print(f"ATR result: {self._format_series(atr_result)}")
        
        # With period 1, ATR should equal True Range
        # For index 0: TR = High - Low = 10 - 8 = 2
        expected_atr_index0 = self.simple_high.iloc[0] - self.simple_low.iloc[0]
        
        print(f"Index 0: Expected ATR = {expected_atr_index0}, Actual ATR = {float(atr_result.iloc[0])}")
        self.assertEqual(
            float(atr_result.iloc[0]), 
            expected_atr_index0, 
            f"With period 1, ATR should equal High-Low at index 0: got {float(atr_result.iloc[0])}, expected {expected_atr_index0}"
        )
        print(f"✓ Index 0: ATR = {float(atr_result.iloc[0])} (period 1)")
        
        # For index 1: TR = max(12-9, |12-9|, |9-9|) = max(3, 3, 0) = 3
        expected_atr_index1 = max(
            self.simple_high.iloc[1] - self.simple_low.iloc[1],
            abs(self.simple_high.iloc[1] - self.simple_close.iloc[0]),
            abs(self.simple_low.iloc[1] - self.simple_close.iloc[0])
        )
        
        print(f"Index 1: Expected ATR = {expected_atr_index1}, Actual ATR = {float(atr_result.iloc[1])}")
        self.assertEqual(
            float(atr_result.iloc[1]), 
            expected_atr_index1, 
            f"With period 1, ATR should equal True Range at index 1: got {float(atr_result.iloc[1])}, expected {expected_atr_index1}"
        )
        print(f"✓ Index 1: ATR = {float(atr_result.iloc[1])} (period 1)")
        
        print("✓ Test passed: ATR edge cases")
    
    def test_atr_error_handling(self):
        """Test ATR error handling"""
        print("\n" + "-" * 60)
        print("TEST: ATR Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_high = pd.Series([], name='high')
        empty_low = pd.Series([], name='low')
        empty_close = pd.Series([], name='close')
        
        atr_empty = atr(empty_high, empty_low, empty_close)
        print(f"Empty data test - ATR type: {type(atr_empty)}")
        print(f"Empty data test - ATR length: {len(atr_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(atr_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with period 0
        try:
            atr_zero_period = atr(
                self.simple_high, self.simple_low, self.simple_close, period=0
            )
            print(f"Result with period 0:")
            print(f"ATR: {self._format_series(atr_zero_period)}")
            
            # All values should be NaN with period 0
            for i in range(len(atr_zero_period)):
                self.assertTrue(pd.isna(atr_zero_period.iloc[i]), f"Value at index {i} should be NaN with period 0")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Error with period 0: {e}")
            self.fail(f"Failed to handle period 0: {e}")
        
        # Test with negative period
        try:
            atr_neg_period = atr(
                self.simple_high, self.simple_low, self.simple_close, period=-1
            )
            print(f"Result with period -1:")
            print(f"ATR: {self._format_series(atr_neg_period)}")
            
            # All values should be NaN with negative period
            for i in range(len(atr_neg_period)):
                self.assertTrue(pd.isna(atr_neg_period.iloc[i]), f"Value at index {i} should be NaN with negative period")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Error with negative period: {e}")
            self.fail(f"Failed to handle negative period: {e}")
        
        print("✓ Test passed: ATR error handling")
    
    def test_atr_realistic_data(self):
        """Test ATR with realistic price data"""
        print("\n" + "-" * 60)
        print("TEST: ATR with Realistic Price Data")
        print("-" * 60)
        
        print(f"High data: {[f'{x:.2f}' for x in self.realistic_high.tolist()]}")
        print(f"Low data: {[f'{x:.2f}' for x in self.realistic_low.tolist()]}")
        print(f"Close data: {[f'{x:.2f}' for x in self.realistic_close.tolist()]}")
        
        atr_result = atr(self.realistic_high, self.realistic_low, self.realistic_close, self.period)
        
        print(f"ATR result: {self._format_series(atr_result)}")
        
        # Check that ATR values are reasonable for the data
        valid_atr_values = [float(x) for x in atr_result if not pd.isna(x)]
        if valid_atr_values:
            avg_atr = sum(valid_atr_values) / len(valid_atr_values)
            price_range = max(self.realistic_close) - min(self.realistic_close)
            
            print(f"Average ATR: {avg_atr:.6f}")
            print(f"Price range: {price_range:.6f}")
            
            # ATR should be positive
            self.assertTrue(avg_atr > 0, f"Average ATR should be positive: {avg_atr}")
            
            # ATR should be reasonable compared to price range
            self.assertTrue(
                avg_atr <= price_range,
                f"Average ATR ({avg_atr}) should be less than or equal to price range ({price_range})"
            )
            print("✓ ATR values are reasonable for the data")
        else:
            print("! No valid ATR values found")
        
        print("✓ Test passed: ATR with realistic data")
    
    def test_atr_volatility_analysis(self):
        """Test ATR behavior with different volatility regimes"""
        print("\n" + "-" * 60)
        print("TEST: ATR Volatility Analysis")
        print("-" * 60)
        
        # Create low volatility data
        low_vol_high = pd.Series([100, 100.5, 101, 100.8, 101.2, 100.9, 101.1, 101, 100.7, 101.3], name='high')
        low_vol_low = pd.Series([99.5, 99.8, 100.2, 99.9, 100.5, 100.3, 100.7, 100.1, 99.8, 100.8], name='low')
        low_vol_close = pd.Series([99.8, 100.2, 100.5, 100.3, 100.8, 100.6, 100.9, 100.4, 100.2, 101], name='close')
        
        # Create high volatility data
        high_vol_high = pd.Series([100, 105, 95, 110, 90, 115, 85, 120, 80, 125], name='high')
        high_vol_low = pd.Series([95, 90, 85, 80, 75, 70, 65, 60, 55, 50], name='low')
        high_vol_close = pd.Series([97, 98, 92, 95, 88, 93, 82, 90, 78, 85], name='close')
        
        print(f"Low volatility data - High: {[f'{x:.1f}' for x in low_vol_high.tolist()]}")
        print(f"Low volatility data - Low: {[f'{x:.1f}' for x in low_vol_low.tolist()]}")
        print(f"Low volatility data - Close: {[f'{x:.1f}' for x in low_vol_close.tolist()]}")
        
        print(f"High volatility data - High: {[f'{x:.1f}' for x in high_vol_high.tolist()]}")
        print(f"High volatility data - Low: {[f'{x:.1f}' for x in high_vol_low.tolist()]}")
        print(f"High volatility data - Close: {[f'{x:.1f}' for x in high_vol_close.tolist()]}")
        
        # Calculate ATR for both datasets
        low_vol_atr = atr(low_vol_high, low_vol_low, low_vol_close, period=5)
        high_vol_atr = atr(high_vol_high, high_vol_low, high_vol_close, period=5)
        
        print(f"Low volatility ATR: {self._format_series(low_vol_atr)}")
        print(f"High volatility ATR: {self._format_series(high_vol_atr)}")
        
        # Get average ATR values (excluding NaN)
        low_vol_avg = np.nanmean(low_vol_atr)
        high_vol_avg = np.nanmean(high_vol_atr)
        
        print(f"Low volatility average ATR: {low_vol_avg:.6f}")
        print(f"High volatility average ATR: {high_vol_avg:.6f}")
        
        # High volatility should have higher ATR
        self.assertTrue(
            high_vol_avg > low_vol_avg,
            f"High volatility ATR ({high_vol_avg}) should be greater than low volatility ATR ({low_vol_avg})"
        )
        print("✓ ATR correctly reflects volatility differences")
        
        print("✓ Test passed: ATR volatility analysis")

if __name__ == '__main__':
    print("🔍 Starting ATR Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)
