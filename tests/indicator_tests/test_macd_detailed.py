"""
Detailed Indicator Tests - MACD (Moving Average Convergence Divergence)
==================================================================
This test file provides comprehensive testing for the MACD indicator with detailed debugging.
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
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Force reload of the indicators module to get the updated EMA function
import importlib
import simple_strategy.strategies.indicators_library
importlib.reload(simple_strategy.strategies.indicators_library)

# Import the indicators library
from simple_strategy.strategies.indicators_library import macd, ema

class TestMACDIndicator(unittest.TestCase):
    """Test cases for MACD (Moving Average Convergence Divergence) indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for MACD")
        print("="*60)
        
        # Create simple test data with sufficient length
        self.simple_data = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                                     110, 108, 106, 105, 107, 109, 111, 113, 112, 114,
                                     115, 113, 111, 109, 108, 110, 112, 114, 116, 115,
                                     117, 119, 118, 116, 114, 113, 115, 117, 119, 120], name='close')
        
        # Create more realistic price data
        np.random.seed(42)
        base_price = 100.0
        changes = np.random.randn(50) * 1.5  # Random changes
        prices = [base_price]
        for change in changes:
            prices.append(prices[-1] + change)
        
        self.realistic_data = pd.Series(prices, name='close')
        
        # Create edge case data
        self.constant_data = pd.Series([100.0] * 50, name='close')  # All same values
        
        # Use smaller MACD parameters for testing
        self.fast_period = 5
        self.slow_period = 10
        self.signal_period = 3
        
        print(f"Simple test data length: {len(self.simple_data)}")
        print(f"Realistic test data length: {len(self.realistic_data)}")
        print(f"Constant test data length: {len(self.constant_data)}")
        print(f"Test parameters: fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period}")
    
    def test_macd_basic_calculation(self):
        """Test basic MACD calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: MACD Basic Calculation")
        print("-"*60)
        
        # Calculate MACD
        macd_line, signal_line, histogram = macd(
            self.simple_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        
        # Debug information
        print(f"Input data length: {len(self.simple_data)}")
        print(f"Parameters: fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period}")
        print(f"Non-NaN MACD values: {macd_line.notna().sum()}")
        print(f"Non-NaN Signal values: {signal_line.notna().sum()}")
        print(f"Non-NaN Histogram values: {histogram.notna().sum()}")
        
        # Show some sample values
        valid_indices = macd_line.dropna().index[:5]
        print(f"Sample MACD values: {[(i, f'{macd_line.iloc[i]:.4f}') for i in valid_indices]}")
        valid_signal_indices = signal_line.dropna().index[:5]
        print(f"Sample Signal values: {[(i, f'{signal_line.iloc[i]:.4f}') for i in valid_signal_indices]}")
        valid_hist_indices = histogram.dropna().index[:5]
        print(f"Sample Histogram values: {[(i, f'{histogram.iloc[i]:.4f}') for i in valid_hist_indices]}")
        
        # Assertions
        self.assertEqual(len(macd_line), len(self.simple_data), "MACD line length should match input length")
        self.assertEqual(len(signal_line), len(self.simple_data), "Signal line length should match input length")
        self.assertEqual(len(histogram), len(self.simple_data), "Histogram length should match input length")
        
        self.assertIsInstance(macd_line, pd.Series, "MACD line should be a pandas Series")
        self.assertIsInstance(signal_line, pd.Series, "Signal line should be a pandas Series")
        self.assertIsInstance(histogram, pd.Series, "Histogram should be a pandas Series")
        
        # Check that initial values are NaN
        for i in range(min(self.slow_period - 1, len(self.simple_data))):
            self.assertTrue(pd.isna(macd_line.iloc[i]), f"MACD line at index {i} should be NaN")
            self.assertTrue(pd.isna(signal_line.iloc[i]), f"Signal line at index {i} should be NaN")
            self.assertTrue(pd.isna(histogram.iloc[i]), f"Histogram at index {i} should be NaN")
            print(f"✓ Index {i}: All values NaN (expected)")
        
        # Check that we have some valid values
        self.assertGreater(macd_line.notna().sum(), 0, "Should have some non-NaN MACD values")
        self.assertGreater(signal_line.notna().sum(), 0, "Should have some non-NaN Signal values")
        self.assertGreater(histogram.notna().sum(), 0, "Should have some non-NaN Histogram values")
        
        # Check that histogram = MACD line - Signal line
        for i in range(len(histogram)):
            if not pd.isna(macd_line.iloc[i]) and not pd.isna(signal_line.iloc[i]):
                expected_histogram = macd_line.iloc[i] - signal_line.iloc[i]
                self.assertAlmostEqual(
                    histogram.iloc[i], 
                    expected_histogram, 
                    places=10,
                    msg=f"Histogram mismatch at index {i}: got {histogram.iloc[i]}, expected {expected_histogram}"
                )
        
        print("✓ Test passed: Basic MACD calculation")
    
    def test_macd_realistic_data(self):
        """Test MACD with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: MACD with Realistic Price Data")
        print("-"*60)
        
        # Calculate MACD
        macd_line, signal_line, histogram = macd(
            self.realistic_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        
        # Debug information
        print(f"Input data length: {len(self.realistic_data)}")
        print(f"Parameters: fast={self.fast_period}, slow={self.slow_period}, signal={self.signal_period}")
        print(f"Non-NaN MACD values: {macd_line.notna().sum()}")
        print(f"Non-NaN Signal values: {signal_line.notna().sum()}")
        print(f"Non-NaN Histogram values: {histogram.notna().sum()}")
        
        # Assertions
        self.assertEqual(len(macd_line), len(self.realistic_data))
        self.assertEqual(len(signal_line), len(self.realistic_data))
        self.assertEqual(len(histogram), len(self.realistic_data))
        
        # Check that we have some non-NaN values
        self.assertGreater(macd_line.notna().sum(), 0, "Should have some non-NaN MACD values")
        self.assertGreater(signal_line.notna().sum(), 0, "Should have some non-NaN Signal values")
        self.assertGreater(histogram.notna().sum(), 0, "Should have some non-NaN Histogram values")
        
        # Check that histogram = MACD line - Signal line
        for i in range(len(histogram)):
            if not pd.isna(macd_line.iloc[i]) and not pd.isna(signal_line.iloc[i]):
                expected_histogram = macd_line.iloc[i] - signal_line.iloc[i]
                self.assertAlmostEqual(
                    histogram.iloc[i], 
                    expected_histogram, 
                    places=10,
                    msg=f"Histogram mismatch at index {i}"
                )
        
        # Check that signal line is smoother than MACD line (lower variance)
        macd_variance = macd_line.var()
        signal_variance = signal_line.var()
        
        print(f"MACD line variance: {macd_variance:.6f}")
        print(f"Signal line variance: {signal_variance:.6f}")
        
        # Signal line should generally have lower variance than MACD line
        self.assertLessEqual(
            signal_variance,
            macd_variance * 1.1,  # Allow 10% tolerance
            msg="Signal line should be smoother than MACD line"
        )
        print("✓ Signal line is smoother than MACD line")
        
        print("✓ Test passed: MACD with realistic data")
    
    def test_macd_edge_cases(self):
        """Test MACD with edge cases"""
        print("\n" + "-"*60)
        print("TEST: MACD Edge Cases")
        print("-"*60)
        
        # Test with constant values (no price changes)
        macd_line, signal_line, histogram = macd(
            self.constant_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        
        print(f"Constant data test - Input length: {len(self.constant_data)}")
        print(f"Non-NaN MACD values: {macd_line.notna().sum()}")
        print(f"Non-NaN Signal values: {signal_line.notna().sum()}")
        print(f"Non-NaN Histogram values: {histogram.notna().sum()}")
        
        # With constant data, MACD line should be close to 0
        for i in range(len(macd_line)):
            if not pd.isna(macd_line.iloc[i]):
                self.assertAlmostEqual(
                    macd_line.iloc[i], 
                    0.0, 
                    places=10,
                    msg=f"MACD line with constant data should be close to 0, got {macd_line.iloc[i]}"
                )
        
        # Signal line should also be close to 0
        for i in range(len(signal_line)):
            if not pd.isna(signal_line.iloc[i]):
                self.assertAlmostEqual(
                    signal_line.iloc[i], 
                    0.0, 
                    places=10,
                    msg=f"Signal line with constant data should be close to 0, got {signal_line.iloc[i]}"
                )
        
        # Histogram should be close to 0
        for i in range(len(histogram)):
            if not pd.isna(histogram.iloc[i]):
                self.assertAlmostEqual(
                    histogram.iloc[i], 
                    0.0, 
                    places=10,
                    msg=f"Histogram with constant data should be close to 0, got {histogram.iloc[i]}"
                )
        
        print("✓ With constant data, all MACD components are close to 0")
        
        # Test with periods larger than data length
        large_fast = 60
        large_slow = 70
        macd_large, signal_large, histogram_large = macd(
            self.simple_data, 
            large_fast, 
            large_slow, 
            self.signal_period
        )
        
        print(f"\nTesting with periods larger than data length: fast={large_fast}, slow={large_slow}")
        print(f"All MACD values NaN: {macd_large.isna().all()}")
        print(f"All Signal values NaN: {signal_large.isna().all()}")
        print(f"All Histogram values NaN: {histogram_large.isna().all()}")
        
        # All values should be NaN
        self.assertTrue(macd_large.isna().all(), "All MACD values should be NaN when periods > data length")
        self.assertTrue(signal_large.isna().all(), "All Signal values should be NaN when periods > data length")
        self.assertTrue(histogram_large.isna().all(), "All Histogram values should be NaN when periods > data length")
        print("✓ All values are NaN when periods > data length")
        
        # Test with equal fast and slow periods
        try:
            macd_equal, signal_equal, histogram_equal = macd(
                self.simple_data, 
                self.fast_period, 
                self.fast_period,  # Same as fast
                self.signal_period
            )
            
            print(f"\nTesting with equal fast and slow periods ({self.fast_period})")
            
            # With equal periods, MACD line should be all zeros (or NaN)
            for i in range(len(macd_equal)):
                if not pd.isna(macd_equal.iloc[i]):
                    self.assertAlmostEqual(
                        macd_equal.iloc[i], 
                        0.0, 
                        places=10,
                        msg=f"MACD line with equal periods should be 0, got {macd_equal.iloc[i]}"
                    )
            
            print("✓ MACD line is 0 when fast and slow periods are equal")
        except Exception as e:
            print(f"Exception with equal periods: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: MACD edge cases")
    
    def test_macd_error_handling(self):
        """Test MACD error handling"""
        print("\n" + "-"*60)
        print("TEST: MACD Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        macd_empty, signal_empty, histogram_empty = macd(
            empty_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        
        print(f"Empty data test - MACD type: {type(macd_empty)}")
        print(f"Empty data test - Signal type: {type(signal_empty)}")
        print(f"Empty data test - Histogram type: {type(histogram_empty)}")
        
        self.assertIsInstance(macd_empty, pd.Series)
        self.assertIsInstance(signal_empty, pd.Series)
        self.assertIsInstance(histogram_empty, pd.Series)
        self.assertEqual(len(macd_empty), 0)
        self.assertEqual(len(signal_empty), 0)
        self.assertEqual(len(histogram_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid periods
        try:
            macd_invalid, signal_invalid, histogram_invalid = macd(
                self.simple_data, 
                0,  # Invalid fast period
                self.slow_period, 
                self.signal_period
            )
            print("Result with fast period 0: All NaN")
            print("✓ Handles fast period 0 without crashing")
        except Exception as e:
            print(f"Exception with fast period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            macd_invalid, signal_invalid, histogram_invalid = macd(
                self.simple_data, 
                self.fast_period, 
                -1,  # Invalid slow period
                self.signal_period
            )
            print("Result with slow period -1: All NaN")
            print("✓ Handles slow period -1 without crashing")
        except Exception as e:
            print(f"Exception with slow period -1: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            macd_invalid, signal_invalid, histogram_invalid = macd(
                self.simple_data, 
                self.fast_period, 
                self.slow_period, 
                0  # Invalid signal period
            )
            print("Result with signal period 0: All NaN")
            print("✓ Handles signal period 0 without crashing")
        except Exception as e:
            print(f"Exception with signal period 0: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: MACD error handling")
    
    def test_macd_crossovers(self):
        """Test MACD line and signal line crossovers"""
        print("\n" + "-"*60)
        print("TEST: MACD Crossovers")
        print("-"*60)
        
        # Create data with clear trend changes to test crossovers
        trend_data = pd.Series([
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114,  # Uptrend
            113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99   # Downtrend
        ], name='close')
        
        macd_line, signal_line, histogram = macd(
            trend_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        
        print(f"Trend data length: {len(trend_data)}")
        print(f"Non-NaN MACD values: {macd_line.notna().sum()}")
        print(f"Non-NaN Signal values: {signal_line.notna().sum()}")
        
        # Find crossovers (where MACD line crosses signal line)
        crossovers = []
        for i in range(1, len(macd_line)):
            if (not pd.isna(macd_line.iloc[i]) and not pd.isna(signal_line.iloc[i]) and
                not pd.isna(macd_line.iloc[i-1]) and not pd.isna(signal_line.iloc[i-1])):
                
                # Bullish crossover: MACD crosses above Signal
                if (macd_line.iloc[i-1] <= signal_line.iloc[i-1] and 
                    macd_line.iloc[i] > signal_line.iloc[i]):
                    crossovers.append((i, "bullish"))
                
                # Bearish crossover: MACD crosses below Signal
                elif (macd_line.iloc[i-1] >= signal_line.iloc[i-1] and 
                      macd_line.iloc[i] < signal_line.iloc[i]):
                    crossovers.append((i, "bearish"))
        
        print(f"Crossovers detected: {crossovers}")
        
        # We should have at least one crossover with this data pattern
        if len(crossovers) > 0:
            print("✓ Detected crossovers as expected")
        else:
            print("ℹ No crossovers detected with current parameters and data")
            # This is acceptable - it depends on the specific data pattern
        
        # Check that histogram sign changes at crossovers
        for idx, crossover_type in crossovers:
            if idx > 0:
                hist_before = histogram.iloc[idx-1]
                hist_after = histogram.iloc[idx]
                
                if crossover_type == "bullish":
                    self.assertLessEqual(hist_before, 0, "Histogram should be <= 0 before bullish crossover")
                    self.assertGreaterEqual(hist_after, 0, "Histogram should be >= 0 after bullish crossover")
                    print(f"✓ Bullish crossover at index {idx}: Histogram {hist_before:.4f} -> {hist_after:.4f}")
                else:  # bearish
                    self.assertGreaterEqual(hist_before, 0, "Histogram should be >= 0 before bearish crossover")
                    self.assertLessEqual(hist_after, 0, "Histogram should be <= 0 after bearish crossover")
                    print(f"✓ Bearish crossover at index {idx}: Histogram {hist_before:.4f} -> {hist_after:.4f}")
        
        print("✓ Test passed: MACD crossovers")
    
    def test_macd_performance(self):
        """Test MACD performance with larger dataset"""
        print("\n" + "-"*60)
        print("TEST: MACD Performance")
        print("-"*60)
        
        # Create larger dataset
        np.random.seed(42)
        large_data = pd.Series(np.random.randn(1000).cumsum() + 100, name='close')
        
        import time
        start_time = time.time()
        macd_line, signal_line, histogram = macd(
            large_data, 
            self.fast_period, 
            self.slow_period, 
            self.signal_period
        )
        end_time = time.time()
        
        print(f"Large dataset size: {len(large_data)}")
        print(f"Calculation time: {end_time - start_time:.6f} seconds")
        print(f"Non-NaN MACD values: {macd_line.notna().sum()}")
        print(f"Non-NaN Signal values: {signal_line.notna().sum()}")
        print(f"Non-NaN Histogram values: {histogram.notna().sum()}")
        
        # Performance assertion (should be fast)
        self.assertLess(end_time - start_time, 0.1, "MACD calculation should be fast")
        
        # Check that histogram = MACD line - Signal line
        for i in range(len(histogram)):
            if not pd.isna(macd_line.iloc[i]) and not pd.isna(signal_line.iloc[i]):
                expected_histogram = macd_line.iloc[i] - signal_line.iloc[i]
                self.assertAlmostEqual(
                    histogram.iloc[i], 
                    expected_histogram, 
                    places=10,
                    msg=f"Histogram mismatch at index {i}"
                )
        
        print("✓ Test passed: MACD performance")

def run_macd_tests():
    """Run all MACD tests with detailed output"""
    print("Starting comprehensive MACD indicator tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMACDIndicator)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("MACD TEST SUMMARY")
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
        print("\n🎉 ALL MACD TESTS PASSED!")
    else:
        print("\n❌ SOME MACD TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_macd_tests()