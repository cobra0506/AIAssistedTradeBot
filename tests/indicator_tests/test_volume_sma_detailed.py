"""
Detailed Indicator Tests - Volume Simple Moving Average (Volume SMA)
==================================================================
This test file provides comprehensive testing for the Volume SMA indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import volume_sma

class TestVolumeSMAIndicator(unittest.TestCase):
    """Test cases for Volume SMA indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for Volume SMA")
        print("=" * 60)
        
        # Create simple test data for volume
        self.simple_volume = pd.Series([1000, 1200, 1500, 1100, 1600, 1800, 1700, 1900, 2000, 1800], name='volume')
        self.period = 5
        
        # Create more realistic volume data
        np.random.seed(42)  # For reproducible results
        base_volume = np.array([10000, 12000, 11000, 13000, 14000, 12500, 15000, 16000, 14500, 15500])
        # Add some realistic variation
        self.realistic_volume = pd.Series(base_volume + np.random.randint(-1000, 1000, 10), name='volume')
        
        # Create edge case data (constant volume)
        self.constant_volume = pd.Series([5000] * 10, name='volume')
        
        # Create trending volume data
        self.trending_volume = pd.Series([1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500], name='volume')
        
        # Create volatile volume data
        self.volatile_volume = pd.Series([1000, 5000, 500, 8000, 200, 10000, 300, 7000, 400, 9000], name='volume')
        
        print(f"Simple volume data: {self.simple_volume.tolist()}")
        print(f"Period: {self.period}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{x:.2f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_volume_sma_basic_calculation(self):
        """Test basic Volume SMA calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: Volume SMA Basic Calculation")
        print("-" * 60)
        
        # Calculate Volume SMA
        sma_result = volume_sma(self.simple_volume, self.period)
        
        # Debug information
        print(f"Volume data: {self.simple_volume.tolist()}")
        print(f"Period: {self.period}")
        print(f"Volume SMA result: {self._format_series(sma_result)}")
        print(f"Volume SMA type: {type(sma_result)}")
        print(f"Volume SMA length: {len(sma_result)}")
        
        # Check that the first period-1 values are NaN
        for i in range(self.period - 1):
            self.assertTrue(
                pd.isna(sma_result.iloc[i]), 
                f"Volume SMA should be NaN at index {i} before period is reached"
            )
        
        # Manual calculation verification for first valid SMA value
        # For period 5, first valid value is at index 4
        expected_sma = sum(self.simple_volume.iloc[:5]) / 5
        
        print(f"\nManual calculation for index 4:")
        print(f"Sum of first {self.period} volumes: {sum(self.simple_volume.iloc[:5])}")
        print(f"Expected Volume SMA: {expected_sma:.2f}")
        print(f"Actual Volume SMA: {float(sma_result.iloc[4]):.2f}")
        
        # Check the calculation at index 4 (first valid value)
        self.assertAlmostEqual(
            float(sma_result.iloc[4]), 
            expected_sma, 
            places=5,
            msg=f"Volume SMA calculation incorrect: got {float(sma_result.iloc[4])}, expected {expected_sma}"
        )
        print(f"✓ Volume SMA calculation correct: {float(sma_result.iloc[4]):.2f} == {expected_sma:.2f}")
        
        # Verify that all values are positive (Volume SMA should always be >= 0)
        for i in range(len(sma_result)):
            if not pd.isna(sma_result.iloc[i]):
                value = float(sma_result.iloc[i])
                self.assertTrue(
                    value >= 0,
                    f"Volume SMA value {value} at index {i} should be non-negative"
                )
        print("✓ All Volume SMA values are non-negative")
        
        print("✓ Test passed: Basic Volume SMA calculation")
    
    def test_volume_sma_edge_cases(self):
        """Test Volume SMA with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: Volume SMA Edge Cases")
        print("-" * 60)
        
        # Test with constant volume
        print(f"Constant volume data: {self.constant_volume.tolist()}")
        
        sma_result = volume_sma(self.constant_volume, period=5)
        
        print(f"Volume SMA result: {self._format_series(sma_result)}")
        
        # With constant volume, SMA should equal the constant value
        for i in range(len(sma_result)):
            if not pd.isna(sma_result.iloc[i]):
                self.assertEqual(
                    float(sma_result.iloc[i]), 
                    5000.0, 
                    f"With constant volume, SMA should be 5000 at index {i}: got {float(sma_result.iloc[i])}"
                )
        
        # Test with period larger than data length
        sma_result = volume_sma(self.simple_volume, period=20)
        
        print(f"\nTesting with period (20) larger than data length ({len(self.simple_volume)})")
        print(f"Volume SMA result: {self._format_series(sma_result)}")
        
        # All values should be NaN when period > data length
        for i in range(len(sma_result)):
            self.assertTrue(
                pd.isna(sma_result.iloc[i]), 
                f"All values should be NaN when period > data length, but index {i} is {float(sma_result.iloc[i])}"
            )
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum period (1)
        sma_result = volume_sma(self.simple_volume, period=1)
        
        print(f"\nTesting with minimum period (1):")
        print(f"Volume SMA result: {self._format_series(sma_result)}")
        
        # With period 1, SMA should equal the original volume data
        for i in range(len(sma_result)):
            self.assertEqual(
                float(sma_result.iloc[i]), 
                float(self.simple_volume.iloc[i]), 
                f"With period 1, SMA should equal volume at index {i}: got {float(sma_result.iloc[i])}, expected {float(self.simple_volume.iloc[i])}"
            )
        print("✓ With period 1, SMA equals original volume data")
        
        print("✓ Test passed: Volume SMA edge cases")
    
    def test_volume_sma_error_handling(self):
        """Test Volume SMA error handling"""
        print("\n" + "-" * 60)
        print("TEST: Volume SMA Error Handling")
        print("-" * 60)
        
        # Test with empty data
        empty_volume = pd.Series([], name='volume')
        
        sma_empty = volume_sma(empty_volume)
        print(f"Empty data test - Volume SMA type: {type(sma_empty)}")
        print(f"Empty data test - Volume SMA length: {len(sma_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(sma_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with period 0
        try:
            sma_zero_period = volume_sma(self.simple_volume, period=0)
            print(f"Result with period 0:")
            print(f"Volume SMA: {self._format_series(sma_zero_period)}")
            
            # All values should be NaN with period 0
            for i in range(len(sma_zero_period)):
                self.assertTrue(pd.isna(sma_zero_period.iloc[i]), f"Value at index {i} should be NaN with period 0")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Error with period 0: {e}")
            self.fail(f"Failed to handle period 0: {e}")
        
        # Test with negative period
        try:
            sma_neg_period = volume_sma(self.simple_volume, period=-1)
            print(f"Result with period -1:")
            print(f"Volume SMA: {self._format_series(sma_neg_period)}")
            
            # All values should be NaN with negative period
            for i in range(len(sma_neg_period)):
                self.assertTrue(pd.isna(sma_neg_period.iloc[i]), f"Value at index {i} should be NaN with negative period")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Error with negative period: {e}")
            self.fail(f"Failed to handle negative period: {e}")
        
        print("✓ Test passed: Volume SMA error handling")
    
    def test_volume_sma_realistic_data(self):
        """Test Volume SMA with realistic volume data"""
        print("\n" + "-" * 60)
        print("TEST: Volume SMA with Realistic Volume Data")
        print("-" * 60)
        
        print(f"Volume data: {[f'{x:.0f}' for x in self.realistic_volume.tolist()]}")
        
        sma_result = volume_sma(self.realistic_volume, self.period)
        
        print(f"Volume SMA result: {self._format_series(sma_result)}")
        
        # Check that Volume SMA values are reasonable for the data
        valid_sma_values = [float(x) for x in sma_result if not pd.isna(x)]
        if valid_sma_values:
            avg_sma = sum(valid_sma_values) / len(valid_sma_values)
            avg_volume = sum(self.realistic_volume) / len(self.realistic_volume)
            
            print(f"Average Volume SMA: {avg_sma:.2f}")
            print(f"Average Volume: {avg_volume:.2f}")
            
            # Volume SMA should be positive
            self.assertTrue(avg_sma > 0, f"Average Volume SMA should be positive: {avg_sma}")
            
            # Volume SMA should be reasonable compared to average volume
            self.assertTrue(
                abs(avg_sma - avg_volume) < avg_volume * 0.5,  # Within 50% of average volume
                f"Average Volume SMA ({avg_sma}) should be close to average volume ({avg_volume})"
            )
            print("✓ Volume SMA values are reasonable for the data")
        else:
            print("! No valid Volume SMA values found")
        
        print("✓ Test passed: Volume SMA with realistic data")
    
    def test_volume_sma_trend_analysis(self):
        """Test Volume SMA behavior with different volume trends"""
        print("\n" + "-" * 60)
        print("TEST: Volume SMA Trend Analysis")
        print("-" * 60)
        
        # Create trending volume data
        print(f"Trending volume data: {self.trending_volume.tolist()}")
        print(f"Volatile volume data: {self.volatile_volume.tolist()}")
        
        # Calculate Volume SMA for both datasets
        trending_sma = volume_sma(self.trending_volume, period=5)
        volatile_sma = volume_sma(self.volatile_volume, period=5)
        
        print(f"Trending Volume SMA: {self._format_series(trending_sma)}")
        print(f"Volatile Volume SMA: {self._format_series(volatile_sma)}")
        
        # Check trending behavior
        valid_trending_sma = [float(x) for x in trending_sma if not pd.isna(x)]
        if len(valid_trending_sma) >= 2:
            # SMA should generally follow the trend
            trend_direction = valid_trending_sma[-1] - valid_trending_sma[0]
            print(f"Trending SMA direction: {trend_direction:.2f}")
            self.assertTrue(
                trend_direction > 0,
                f"Trending Volume SMA should be increasing: {valid_trending_sma[0]} -> {valid_trending_sma[-1]}"
            )
            print("✓ Volume SMA correctly follows upward trend")
        
        # Check smoothing effect on volatile data
        original_volatility = np.std(self.volatile_volume)
        sma_volatility = np.std([float(x) for x in volatile_sma if not pd.isna(x)])
        
        print(f"Original volume volatility: {original_volatility:.2f}")
        print(f"Volume SMA volatility: {sma_volatility:.2f}")
        
        # SMA should reduce volatility
        self.assertTrue(
            sma_volatility < original_volatility,
            f"Volume SMA should reduce volatility: original {original_volatility:.2f} vs SMA {sma_volatility:.2f}"
        )
        print("✓ Volume SMA correctly smooths volatile data")
        
        print("✓ Test passed: Volume SMA trend analysis")

if __name__ == '__main__':
    print("📊 Starting Volume SMA Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)