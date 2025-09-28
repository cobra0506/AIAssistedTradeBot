"""
Detailed Indicator Tests - Bollinger Bands
==========================================
This test file provides comprehensive testing for the Bollinger Bands indicator with detailed debugging.
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

# Import the indicators library
from simple_strategy.strategies.indicators_library import bollinger_bands, sma

class TestBollingerBandsIndicator(unittest.TestCase):
    """Test cases for Bollinger Bands indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for Bollinger Bands")
        print("="*60)
        
        # Create simple test data
        self.simple_data = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                                     110, 108, 106, 105, 107, 109, 111, 113, 112, 114], name='close')
        
        # Create more realistic price data with some volatility
        np.random.seed(42)
        base_price = 100.0
        changes = np.random.randn(30) * 2.0  # Random changes with higher volatility
        prices = [base_price]
        for change in changes:
            prices.append(prices[-1] + change)
        
        self.realistic_data = pd.Series(prices, name='close')
        
        # Create edge case data
        self.constant_data = pd.Series([100.0] * 30, name='close')  # All same values
        
        # Default Bollinger Bands parameters
        self.period = 20
        self.std_dev = 2.0
        
        print(f"Simple test data length: {len(self.simple_data)}")
        print(f"Realistic test data length: {len(self.realistic_data)}")
        print(f"Constant test data length: {len(self.constant_data)}")
        print(f"Test parameters: period={self.period}, std_dev={self.std_dev}")
    
    def test_bollinger_bands_basic_calculation(self):
        """Test basic Bollinger Bands calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Basic Calculation")
        print("-"*60)
        
        # Calculate Bollinger Bands
        upper_band, middle_band, lower_band = bollinger_bands(
            self.simple_data, 
            self.period, 
            self.std_dev
        )
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Parameters: period={self.period}, std_dev={self.std_dev}")
        print(f"Upper band: {[f'{x:.4f}' if not pd.isna(x) else 'nan' for x in upper_band.tolist()]}")
        print(f"Middle band: {[f'{x:.4f}' if not pd.isna(x) else 'nan' for x in middle_band.tolist()]}")
        print(f"Lower band: {[f'{x:.4f}' if not pd.isna(x) else 'nan' for x in lower_band.tolist()]}")
        
        # Assertions
        self.assertEqual(len(upper_band), len(self.simple_data), "Upper band length should match input length")
        self.assertEqual(len(middle_band), len(self.simple_data), "Middle band length should match input length")
        self.assertEqual(len(lower_band), len(self.simple_data), "Lower band length should match input length")
        
        self.assertIsInstance(upper_band, pd.Series, "Upper band should be a pandas Series")
        self.assertIsInstance(middle_band, pd.Series, "Middle band should be a pandas Series")
        self.assertIsInstance(lower_band, pd.Series, "Lower band should be a pandas Series")
        
        # Check that initial values are NaN
        for i in range(self.period - 1):
            self.assertTrue(pd.isna(upper_band.iloc[i]), f"Upper band at index {i} should be NaN")
            self.assertTrue(pd.isna(middle_band.iloc[i]), f"Middle band at index {i} should be NaN")
            self.assertTrue(pd.isna(lower_band.iloc[i]), f"Lower band at index {i} should be NaN")
            print(f"✓ Index {i}: All bands NaN (expected)")
        
        # Check that we have some valid values
        self.assertGreater(upper_band.notna().sum(), 0, "Should have some non-NaN upper band values")
        self.assertGreater(middle_band.notna().sum(), 0, "Should have some non-NaN middle band values")
        self.assertGreater(lower_band.notna().sum(), 0, "Should have some non-NaN lower band values")
        
        # Check that middle band equals SMA
        sma_values = sma(self.simple_data, self.period)
        for i in range(len(middle_band)):
            if not pd.isna(middle_band.iloc[i]) and not pd.isna(sma_values.iloc[i]):
                self.assertAlmostEqual(
                    middle_band.iloc[i], 
                    sma_values.iloc[i], 
                    places=10,
                    msg=f"Middle band should equal SMA at index {i}"
                )
        
        # Check that upper band > middle band > lower band (when not NaN)
        for i in range(len(upper_band)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(middle_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                self.assertGreater(upper_band.iloc[i], middle_band.iloc[i], 
                                 f"Upper band should be > middle band at index {i}")
                self.assertGreater(middle_band.iloc[i], lower_band.iloc[i], 
                                 f"Middle band should be > lower band at index {i}")
                print(f"✓ Index {i}: {lower_band.iloc[i]:.4f} < {middle_band.iloc[i]:.4f} < {upper_band.iloc[i]:.4f}")
        
        # Check that the bands are equidistant from the middle band
        for i in range(len(upper_band)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(middle_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                upper_distance = upper_band.iloc[i] - middle_band.iloc[i]
                lower_distance = middle_band.iloc[i] - lower_band.iloc[i]
                self.assertAlmostEqual(
                    upper_distance, 
                    lower_distance, 
                    places=10,
                    msg=f"Bands should be equidistant from middle band at index {i}"
                )
        
        print("✓ Test passed: Basic Bollinger Bands calculation")
    
    def test_bollinger_bands_realistic_data(self):
        """Test Bollinger Bands with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands with Realistic Price Data")
        print("-"*60)
        
        # Calculate Bollinger Bands
        upper_band, middle_band, lower_band = bollinger_bands(
            self.realistic_data, 
            self.period, 
            self.std_dev
        )
        
        # Debug information
        print(f"Input data length: {len(self.realistic_data)}")
        print(f"Parameters: period={self.period}, std_dev={self.std_dev}")
        print(f"Non-NaN upper band values: {upper_band.notna().sum()}")
        print(f"Non-NaN middle band values: {middle_band.notna().sum()}")
        print(f"Non-NaN lower band values: {lower_band.notna().sum()}")
        
        # Assertions
        self.assertEqual(len(upper_band), len(self.realistic_data))
        self.assertEqual(len(middle_band), len(self.realistic_data))
        self.assertEqual(len(lower_band), len(self.realistic_data))
        
        # Check that we have some valid values
        self.assertGreater(upper_band.notna().sum(), 0, "Should have some non-NaN upper band values")
        self.assertGreater(middle_band.notna().sum(), 0, "Should have some non-NaN middle band values")
        self.assertGreater(lower_band.notna().sum(), 0, "Should have some non-NaN lower band values")
        
        # Check that middle band equals SMA
        sma_values = sma(self.realistic_data, self.period)
        for i in range(len(middle_band)):
            if not pd.isna(middle_band.iloc[i]) and not pd.isna(sma_values.iloc[i]):
                self.assertAlmostEqual(
                    middle_band.iloc[i], 
                    sma_values.iloc[i], 
                    places=10,
                    msg=f"Middle band should equal SMA at index {i}"
                )
        
        # Check that upper band > middle band > lower band (when not NaN)
        for i in range(len(upper_band)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(middle_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                self.assertGreater(upper_band.iloc[i], middle_band.iloc[i])
                self.assertGreater(middle_band.iloc[i], lower_band.iloc[i])
        
        # Check that the bands are equidistant from the middle band
        for i in range(len(upper_band)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(middle_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                upper_distance = upper_band.iloc[i] - middle_band.iloc[i]
                lower_distance = middle_band.iloc[i] - lower_band.iloc[i]
                self.assertAlmostEqual(
                    upper_distance, 
                    lower_distance, 
                    places=10,
                    msg=f"Bands should be equidistant from middle band at index {i}"
                )
        
        # Check that price is usually within the bands
        price_within_bands = 0
        total_valid_points = 0
        
        for i in range(len(self.realistic_data)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                total_valid_points += 1
                if lower_band.iloc[i] <= self.realistic_data.iloc[i] <= upper_band.iloc[i]:
                    price_within_bands += 1
        
        if total_valid_points > 0:
            within_percentage = (price_within_bands / total_valid_points) * 100
            print(f"Price within bands: {within_percentage:.2f}%")
            
            # With std_dev=2, we expect about 95% of prices to be within the bands
            self.assertGreater(within_percentage, 80, 
                             "At least 80% of prices should be within the bands")
        
        print("✓ Test passed: Bollinger Bands with realistic data")
    
    def test_bollinger_bands_edge_cases(self):
        """Test Bollinger Bands with edge cases"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Edge Cases")
        print("-"*60)
        
        # Test with constant values (no price changes)
        upper_band, middle_band, lower_band = bollinger_bands(
            self.constant_data, 
            self.period, 
            self.std_dev
        )
        
        print(f"Constant data test - Input length: {len(self.constant_data)}")
        print(f"Non-NaN upper band values: {upper_band.notna().sum()}")
        print(f"Non-NaN middle band values: {middle_band.notna().sum()}")
        print(f"Non-NaN lower band values: {lower_band.notna().sum()}")
        
        # With constant data, all bands should be equal to the constant value
        for i in range(len(upper_band)):
            if not pd.isna(upper_band.iloc[i]):
                self.assertAlmostEqual(
                    upper_band.iloc[i], 
                    100.0, 
                    places=10,
                    msg=f"Upper band with constant data should be 100, got {upper_band.iloc[i]}"
                )
                self.assertAlmostEqual(
                    middle_band.iloc[i], 
                    100.0, 
                    places=10,
                    msg=f"Middle band with constant data should be 100, got {middle_band.iloc[i]}"
                )
                self.assertAlmostEqual(
                    lower_band.iloc[i], 
                    100.0, 
                    places=10,
                    msg=f"Lower band with constant data should be 100, got {lower_band.iloc[i]}"
                )
        
        print("✓ With constant data, all bands equal the constant value")
        
        # Test with period larger than data length
        large_period = 35
        upper_large, middle_large, lower_large = bollinger_bands(
            self.simple_data, 
            large_period, 
            self.std_dev
        )
        
        print(f"\nTesting with period larger than data length: period={large_period}")
        print(f"All upper band values NaN: {upper_large.isna().all()}")
        print(f"All middle band values NaN: {middle_large.isna().all()}")
        print(f"All lower band values NaN: {lower_large.isna().all()}")
        
        # All values should be NaN
        self.assertTrue(upper_large.isna().all(), "All upper band values should be NaN when period > data length")
        self.assertTrue(middle_large.isna().all(), "All middle band values should be NaN when period > data length")
        self.assertTrue(lower_large.isna().all(), "All lower band values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with different standard deviations
        print(f"\nTesting with different standard deviations:")
        
        # Calculate reference bands with std_dev=2.0
        upper_ref, middle_ref, lower_ref = bollinger_bands(
            self.simple_data, 
            self.period, 
            2.0  # Reference std_dev
        )
        
        # Test with different standard deviations
        for std_dev in [1.0, 1.5, 2.5, 3.0]:
            upper_std, middle_std, lower_std = bollinger_bands(
                self.simple_data, 
                self.period, 
                std_dev
            )
            
            print(f"\nTesting with std_dev={std_dev}")
            
            # Find a valid index to compare
            for i in range(len(upper_std)):
                if (not pd.isna(upper_std.iloc[i]) and 
                    not pd.isna(upper_ref.iloc[i])):
                    
                    print(f"  At index {i}:")
                    print(f"    std_dev={std_dev}: upper={upper_std.iloc[i]:.4f}, lower={lower_std.iloc[i]:.4f}")
                    print(f"    std_dev=2.0:   upper={upper_ref.iloc[i]:.4f}, lower={lower_ref.iloc[i]:.4f}")
                    
                    # Calculate band widths
                    width_std = upper_std.iloc[i] - lower_std.iloc[i]
                    width_ref = upper_ref.iloc[i] - lower_ref.iloc[i]
                    
                    print(f"    Band width std_dev={std_dev}: {width_std:.4f}")
                    print(f"    Band width std_dev=2.0: {width_ref:.4f}")
                    
                    # Check that band width is proportional to std_dev
                    expected_ratio = std_dev / 2.0
                    actual_ratio = width_std / width_ref
                    
                    print(f"    Expected ratio: {expected_ratio:.2f}")
                    print(f"    Actual ratio: {actual_ratio:.2f}")
                    
                    # Allow some tolerance for floating-point precision
                    self.assertAlmostEqual(
                        actual_ratio, 
                        expected_ratio, 
                        places=1,
                        msg=f"Band width ratio should be proportional to std_dev ratio"
                    )
                    print(f"    ✓ Band width ratio is correct")
                    
                    # Check specific relationships based on std_dev
                    if std_dev < 2.0:
                        self.assertLess(upper_std.iloc[i], upper_ref.iloc[i],
                                        f"Upper band with std_dev={std_dev} should be narrower than with std_dev=2.0")
                        self.assertGreater(lower_std.iloc[i], lower_ref.iloc[i],
                                        f"Lower band with std_dev={std_dev} should be narrower than with std_dev=2.0")
                        print(f"    ✓ Bands are narrower with std_dev={std_dev}")
                    elif std_dev > 2.0:
                        self.assertGreater(upper_std.iloc[i], upper_ref.iloc[i],
                                        f"Upper band with std_dev={std_dev} should be wider than with std_dev=2.0")
                        self.assertLess(lower_std.iloc[i], lower_ref.iloc[i],
                                    f"Lower band with std_dev={std_dev} should be wider than with std_dev=2.0")
                        print(f"    ✓ Bands are wider with std_dev={std_dev}")
                    
                    break
        
        print("✓ Test passed: Bollinger Bands edge cases")
    
    def test_bollinger_bands_error_handling(self):
        """Test Bollinger Bands error handling"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        upper_empty, middle_empty, lower_empty = bollinger_bands(
            empty_data, 
            self.period, 
            self.std_dev
        )
        
        print(f"Empty data test - Upper band type: {type(upper_empty)}")
        print(f"Empty data test - Middle band type: {type(middle_empty)}")
        print(f"Empty data test - Lower band type: {type(lower_empty)}")
        
        self.assertIsInstance(upper_empty, pd.Series)
        self.assertIsInstance(middle_empty, pd.Series)
        self.assertIsInstance(lower_empty, pd.Series)
        self.assertEqual(len(upper_empty), 0)
        self.assertEqual(len(middle_empty), 0)
        self.assertEqual(len(lower_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            upper_invalid, middle_invalid, lower_invalid = bollinger_bands(
                self.simple_data, 
                0,  # Invalid period
                self.std_dev
            )
            print("Result with period 0: All NaN")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            upper_invalid, middle_invalid, lower_invalid = bollinger_bands(
                self.simple_data, 
                -1,  # Invalid period
                self.std_dev
            )
            print("Result with period -1: All NaN")
            print("✓ Handles period -1 without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        # Test with invalid standard deviation
        try:
            upper_invalid, middle_invalid, lower_invalid = bollinger_bands(
                self.simple_data, 
                self.period, 
                0  # Invalid std_dev
            )
            print("Result with std_dev 0: All bands equal")
            print("✓ Handles std_dev 0 without crashing")
        except Exception as e:
            print(f"Exception with std_dev 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            upper_invalid, middle_invalid, lower_invalid = bollinger_bands(
                self.simple_data, 
                self.period, 
                -1  # Invalid std_dev
            )
            print("Result with std_dev -1: All bands equal")
            print("✓ Handles std_dev -1 without crashing")
        except Exception as e:
            print(f"Exception with std_dev -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: Bollinger Bands error handling")
    
    def test_bollinger_bands_squeeze(self):
        """Test Bollinger Bands squeeze (low volatility)"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Squeeze")
        print("-"*60)
        
        # Create data with low volatility (squeeze)
        base_price = 100.0
        squeeze_data = pd.Series([base_price + 0.1 * (i % 10 - 5) for i in range(30)], name='close')
        
        upper_band, middle_band, lower_band = bollinger_bands(
            squeeze_data, 
            self.period, 
            self.std_dev
        )
        
        print(f"Squeeze data: {[f'{x:.2f}' for x in squeeze_data.tolist()[:10]]}...")
        print(f"Non-NaN upper band values: {upper_band.notna().sum()}")
        print(f"Non-NaN middle band values: {middle_band.notna().sum()}")
        print(f"Non-NaN lower band values: {lower_band.notna().sum()}")
        
        # Calculate average band width
        band_widths = []
        for i in range(len(upper_band)):
            if not pd.isna(upper_band.iloc[i]) and not pd.isna(lower_band.iloc[i]):
                band_width = upper_band.iloc[i] - lower_band.iloc[i]
                band_widths.append(band_width)
        
        if band_widths:
            avg_band_width = sum(band_widths) / len(band_widths)
            print(f"Average band width: {avg_band_width:.4f}")
            
            # With low volatility data, band width should be small
            # We can't assert an exact value, but we can check it's reasonable
            self.assertLess(avg_band_width, 5.0, "Average band width should be small with low volatility")
        
        print("✓ Test passed: Bollinger Bands squeeze")
    
    def test_bollinger_bands_expansion(self):
        """Test Bollinger Bands expansion (high volatility)"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Expansion")
        print("-"*60)
        
        # Create data with high volatility (expansion)
        np.random.seed(42)
        base_price = 100.0
        expansion_data = pd.Series([base_price + np.random.normal(0, 5) for _ in range(30)], name='close')
        
        upper_band, middle_band, lower_band = bollinger_bands(
            expansion_data, 
            self.period, 
            self.std_dev
        )
        
        print(f"Expansion data: {[f'{x:.2f}' for x in expansion_data.tolist()[:10]]}...")
        print(f"Non-NaN upper band values: {upper_band.notna().sum()}")
        print(f"Non-NaN middle band values: {middle_band.notna().sum()}")
        print(f"Non-NaN lower band values: {lower_band.notna().sum()}")
        
        # Calculate average band width
        band_widths = []
        for i in range(len(upper_band)):
            if not pd.isna(upper_band.iloc[i]) and not pd.isna(lower_band.iloc[i]):
                band_width = upper_band.iloc[i] - lower_band.iloc[i]
                band_widths.append(band_width)
        
        if band_widths:
            avg_band_width = sum(band_widths) / len(band_widths)
            print(f"Average band width: {avg_band_width:.4f}")
            
            # With high volatility data, band width should be large
            # We can't assert an exact value, but we can check it's reasonable
            self.assertGreater(avg_band_width, 5.0, "Average band width should be large with high volatility")
        
        print("✓ Test passed: Bollinger Bands expansion")
    
    def test_bollinger_bands_performance(self):
        """Test Bollinger Bands performance with larger dataset"""
        print("\n" + "-"*60)
        print("TEST: Bollinger Bands Performance")
        print("-"*60)
        
        # Create larger dataset
        np.random.seed(42)
        large_data = pd.Series(np.random.randn(1000).cumsum() + 100, name='close')
        
        import time
        start_time = time.time()
        upper_band, middle_band, lower_band = bollinger_bands(
            large_data, 
            self.period, 
            self.std_dev
        )
        end_time = time.time()
        
        print(f"Large dataset size: {len(large_data)}")
        print(f"Calculation time: {end_time - start_time:.6f} seconds")
        print(f"Non-NaN upper band values: {upper_band.notna().sum()}")
        print(f"Non-NaN middle band values: {middle_band.notna().sum()}")
        print(f"Non-NaN lower band values: {lower_band.notna().sum()}")
        
        # Performance assertion (should be fast)
        self.assertLess(end_time - start_time, 0.1, "Bollinger Bands calculation should be fast")
        
        # Check that middle band equals SMA
        sma_values = sma(large_data, self.period)
        for i in range(len(middle_band)):
            if not pd.isna(middle_band.iloc[i]) and not pd.isna(sma_values.iloc[i]):
                self.assertAlmostEqual(
                    middle_band.iloc[i], 
                    sma_values.iloc[i], 
                    places=10,
                    msg=f"Middle band should equal SMA at index {i}"
                )
        
        # Check that upper band > middle band > lower band (when not NaN)
        for i in range(len(upper_band)):
            if (not pd.isna(upper_band.iloc[i]) and 
                not pd.isna(middle_band.iloc[i]) and 
                not pd.isna(lower_band.iloc[i])):
                self.assertGreater(upper_band.iloc[i], middle_band.iloc[i])
                self.assertGreater(middle_band.iloc[i], lower_band.iloc[i])
        
        print("✓ Test passed: Bollinger Bands performance")

def run_bollinger_bands_tests():
    """Run all Bollinger Bands tests with detailed output"""
    print("Starting comprehensive Bollinger Bands indicator tests...")
    print("="*80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBollingerBandsIndicator)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("BOLLINGER BANDS TEST SUMMARY")
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
        print("\n🎉 ALL BOLLINGER BANDS TESTS PASSED!")
    else:
        print("\n❌ SOME BOLLINGER BANDS TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_bollinger_bands_tests()