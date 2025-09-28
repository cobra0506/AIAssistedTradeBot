"""
Detailed Indicator Tests - DEMA (Double Exponential Moving Average)
===================================================================
This test file provides comprehensive testing for the DEMA indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, wma, dema, rsi, macd, bollinger_bands


class TestDEMAIndicator(unittest.TestCase):
    """Test cases for DEMA (Double Exponential Moving Average) indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for DEMA")
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

    def test_dema_basic_calculation(self):
        """Test basic DEMA calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: DEMA Basic Calculation")
        print("-"*60)
        
        # Calculate DEMA
        result = dema(self.simple_data, self.period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {result.tolist()}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
        # DEMA calculation verification: DEMA = 2 * EMA1 - EMA2
        # Calculate intermediate steps manually
        ema1 = ema(self.simple_data, self.period)
        ema2 = ema(ema1, self.period)
        manual_dema = 2 * ema1 - ema2
        
        print(f"EMA1: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema1.tolist()]}")
        print(f"EMA2: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema2.tolist()]}")
        print(f"Manual DEMA: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in manual_dema.tolist()]}")
        
        # Assertions
        self.assertEqual(len(result), len(self.simple_data), "Result length should match input length")
        self.assertIsInstance(result, pd.Series, "Result should be a pandas Series")
        
        # Check specific values (ignoring NaN values)
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]) and not pd.isna(manual_dema.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i],
                    manual_dema.iloc[i],
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {manual_dema.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {manual_dema.iloc[i]:.6f}")
        
        print("✓ Test passed: Basic DEMA calculation")

    def test_dema_realistic_data(self):
        """Test DEMA with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: DEMA with Realistic Price Data")
        print("-"*60)
        
        # Calculate DEMA
        result = dema(self.realistic_data, self.period)
        
        # Debug information
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # Calculate expected values manually
        ema1 = ema(self.realistic_data, self.period)
        ema2 = ema(ema1, self.period)
        expected_values = 2 * ema1 - ema2
        
        print(f"EMA1: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema1.tolist()]}")
        print(f"EMA2: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema2.tolist()]}")
        print(f"Expected DEMA: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in expected_values.tolist()]}")
        
        # Assertions
        self.assertEqual(len(result), len(self.realistic_data))
        self.assertIsInstance(result, pd.Series)
        
        # Check non-NaN values
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]) and not pd.isna(expected_values.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i],
                    expected_values.iloc[i],
                    places=10,
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {expected_values.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {expected_values.iloc[i]:.6f}")
        
        print("✓ Test passed: DEMA with realistic data")

    def test_dema_edge_cases(self):
        """Test DEMA with edge cases"""
        print("\n" + "-"*60)
        print("TEST: DEMA Edge Cases")
        print("-"*60)
        
        # Test with all same values
        result = dema(self.edge_data, self.period)
        print(f"Input data (all same): {self.edge_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"Result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in result.tolist()]}")
        
        # All non-NaN values should equal the input value (since all values are the same)
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]):
                self.assertEqual(
                    result.iloc[i],
                    self.edge_data.iloc[i],
                    msg=f"Mismatch at index {i}: got {result.iloc[i]}, expected {self.edge_data.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]} == {self.edge_data.iloc[i]}")
        
        # Test with period larger than data length
        large_period = 20
        result_large = dema(self.simple_data, large_period)
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"Result: {result_large.tolist()}")
        
        # All values should be NaN
        self.assertTrue(result_large.isna().all(), "All values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with period = 1 (should equal the input data)
        result_period1 = dema(self.simple_data, 1)
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
        
        print("✓ Test passed: DEMA edge cases")

    def test_dema_error_handling(self):
        """Test DEMA error handling"""
        print("\n" + "-"*60)
        print("TEST: DEMA Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        result_empty = dema(empty_data, self.period)
        print(f"Empty data test - Result type: {type(result_empty)}")
        print(f"Empty data test - Result length: {len(result_empty)}")
        
        self.assertIsInstance(result_empty, pd.Series)
        self.assertEqual(len(result_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            result_invalid = dema(self.simple_data, 0)
            print("Result with period 0:", result_invalid.tolist())
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            result_negative = dema(self.simple_data, -1)
            print("Result with period -1:", result_negative.tolist())
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: DEMA error handling")

    def test_dema_vs_ema_comparison(self):
        """Test DEMA vs EMA comparison"""
        print("\n" + "-"*60)
        print("TEST: DEMA vs EMA Comparison")
        print("-"*60)
        
        # Calculate both EMA and DEMA
        ema_result = ema(self.realistic_data, self.period)
        dema_result = dema(self.realistic_data, self.period)
        
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"Period: {self.period}")
        print(f"EMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema_result.tolist()]}")
        print(f"DEMA result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in dema_result.tolist()]}")
        
        # Test that DEMA is more responsive than EMA
        # Create a series with a clear trend to show DEMA's responsiveness
        trend_data = pd.Series([
            100.0, 101.0, 102.0, 105.0, 108.0, 110.0, 112.0, 115.0, 118.0, 120.0
        ], name='close')
        
        ema_trend = ema(trend_data, self.period)
        dema_trend = dema(trend_data, self.period)
        
        print(f"\nTesting with trending price series:")
        print(f"Trend data: {trend_data.tolist()}")
        print(f"EMA trend: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema_trend.tolist()]}")
        print(f"DEMA trend: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in dema_trend.tolist()]}")
        
        # In an uptrend, DEMA should generally be higher than EMA because it's more responsive
        check_idx = len(trend_data) - 1  # Last value
        if check_idx >= self.period - 1:
            dema_value = dema_trend.iloc[check_idx]
            ema_value = ema_trend.iloc[check_idx]
            current_price = trend_data.iloc[check_idx]
            
            print(f"\nAt index {check_idx} (end of uptrend):")
            print(f"Current price: {current_price}")
            print(f"EMA value: {ema_value:.6f}")
            print(f"DEMA value: {dema_value:.6f}")
            
            # DEMA should be closer to the current price than EMA in a trending market
            dema_distance = abs(dema_value - current_price)
            ema_distance = abs(ema_value - current_price)
            
            print(f"DEMA distance from current price: {dema_distance:.6f}")
            print(f"EMA distance from current price: {ema_distance:.6f}")
            
            # In an uptrend, DEMA should generally be higher than EMA
            self.assertGreaterEqual(
                dema_value,
                ema_value,
                msg=f"In uptrend, DEMA ({dema_value}) should be >= EMA ({ema_value})"
            )
            print(f"✓ DEMA ({dema_value:.6f}) >= EMA ({ema_value:.6f}) in uptrend")
            
            # DEMA should be more responsive (closer to current price) than EMA
            self.assertLessEqual(
                dema_distance,
                ema_distance,
                msg=f"DEMA should be more responsive than EMA: DEMA distance={dema_distance}, EMA distance={ema_distance}"
            )
            print(f"✓ DEMA ({dema_distance:.6f}) is more responsive than EMA ({ema_distance:.6f})")
        
        print("✓ Test passed: DEMA vs EMA comparison")

    def test_dema_formula_verification(self):
        """Test DEMA formula verification"""
        print("\n" + "-"*60)
        print("TEST: DEMA Formula Verification")
        print("-"*60)
        
        # Create test data where we can easily verify the formula
        test_data = pd.Series([10, 20, 30, 40, 50], name='close')
        period = 3
        
        result = dema(test_data, period)
        
        print(f"Test data: {test_data.tolist()}")
        print(f"Period: {period}")
        print(f"Result: {result.tolist()}")
        
        # Manual calculation using the DEMA formula: DEMA = 2 * EMA1 - EMA2
        ema1 = ema(test_data, period)
        ema2 = ema(ema1, period)
        manual_dema = 2 * ema1 - ema2
        
        print(f"EMA1: {ema1.tolist()}")
        print(f"EMA2: {ema2.tolist()}")
        print(f"Manual DEMA (2*EMA1 - EMA2): {manual_dema.tolist()}")
        print(f"Actual DEMA: {result.tolist()}")
        
        # Verify the formula is correctly implemented
        for i in range(len(result)):
            if not pd.isna(result.iloc[i]) and not pd.isna(manual_dema.iloc[i]):
                self.assertAlmostEqual(
                    result.iloc[i],
                    manual_dema.iloc[i],
                    places=10,
                    msg=f"DEMA formula incorrect at index {i}: got {result.iloc[i]}, expected {manual_dema.iloc[i]}"
                )
                print(f"✓ Index {i}: {result.iloc[i]:.6f} == {manual_dema.iloc[i]:.6f}")
        
        # Test the mathematical property: DEMA should reduce lag compared to EMA
        # Create a step change to test responsiveness
        step_data = pd.Series([100, 100, 100, 100, 150, 150, 150, 150], name='close')
        
        ema_step = ema(step_data, period)
        dema_step = dema(step_data, period)
        
        print(f"\nTesting with step change data:")
        print(f"Step data: {step_data.tolist()}")
        print(f"EMA step: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in ema_step.tolist()]}")
        print(f"DEMA step: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in dema_step.tolist()]}")
        
        # After the step change, DEMA should be closer to the new value than EMA
        step_idx = 6  # Well after the step change
        if step_idx < len(step_data):
            current_value = step_data.iloc[step_idx]
            ema_value = ema_step.iloc[step_idx]
            dema_value = dema_step.iloc[step_idx]
            
            ema_diff = abs(ema_value - current_value)
            dema_diff = abs(dema_value - current_value)
            
            print(f"\nAt index {step_idx} (after step change):")
            print(f"Current value: {current_value}")
            print(f"EMA value: {ema_value:.6f} (diff: {ema_diff:.6f})")
            print(f"DEMA value: {dema_value:.6f} (diff: {dema_diff:.6f})")
            
            # DEMA should have less lag than EMA
            self.assertLessEqual(
                dema_diff,
                ema_diff,
                msg=f"DEMA should have less lag than EMA: DEMA diff={dema_diff}, EMA diff={ema_diff}"
            )
            print(f"✓ DEMA ({dema_diff:.6f}) has less lag than EMA ({ema_diff:.6f})")
        
        print("✓ Test passed: DEMA formula verification")

    def test_dema_lag_reduction_analysis(self):
        """Test DEMA lag reduction analysis"""
        print("\n" + "-"*60)
        print("TEST: DEMA Lag Reduction Analysis")
        print("-"*60)
        
        # Create a sinusoidal price series to test lag characteristics
        t = np.arange(0, 20)
        price_data = 100 + 10 * np.sin(t * np.pi / 5)  # Sinusoidal with period 10
        sinusoidal_data = pd.Series(price_data, name='close')
        
        period = 5
        sma_result = sma(sinusoidal_data, period)
        ema_result = ema(sinusoidal_data, period)
        dema_result = dema(sinusoidal_data, period)
        
        print(f"Testing with sinusoidal price data (period={period}):")
        print(f"Price data: {[f'{x:.2f}' for x in sinusoidal_data.tolist()]}")
        print(f"SMA: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in sma_result.tolist()]}")
        print(f"EMA: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in ema_result.tolist()]}")
        print(f"DEMA: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in dema_result.tolist()]}")
        
        # Calculate lag by measuring phase shift (correlation with original data)
        # We'll check the correlation at different lags to find the best fit
        valid_start = period * 2  # Wait for DEMA to stabilize
        
        if valid_start < len(sinusoidal_data):
            # Extract valid portions
            original = sinusoidal_data.iloc[valid_start:]
            sma_valid = sma_result.iloc[valid_start:]
            ema_valid = ema_result.iloc[valid_start:]
            dema_valid = dema_result.iloc[valid_start:]
            
            # Calculate correlation with original (higher correlation = less lag)
            sma_corr = original.corr(sma_valid)
            ema_corr = original.corr(ema_valid)
            dema_corr = original.corr(dema_valid)
            
            print(f"\nCorrelation with original price data:")
            print(f"SMA correlation: {sma_corr:.6f}")
            print(f"EMA correlation: {ema_corr:.6f}")
            print(f"DEMA correlation: {dema_corr:.6f}")
            
            # DEMA should generally have higher correlation than EMA, which should have higher correlation than SMA
            if not pd.isna(dema_corr) and not pd.isna(ema_corr):
                self.assertGreaterEqual(
                    dema_corr,
                    ema_corr,
                    msg=f"DEMA should have higher correlation than EMA: DEMA={dema_corr}, EMA={ema_corr}"
                )
                print(f"✓ DEMA correlation ({dema_corr:.6f}) >= EMA correlation ({ema_corr:.6f})")
            
            if not pd.isna(ema_corr) and not pd.isna(sma_corr):
                self.assertGreaterEqual(
                    ema_corr,
                    sma_corr,
                    msg=f"EMA should have higher correlation than SMA: EMA={ema_corr}, SMA={sma_corr}"
                )
                print(f"✓ EMA correlation ({ema_corr:.6f}) >= SMA correlation ({sma_corr:.6f})")
        
        print("✓ Test passed: DEMA lag reduction analysis")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting DEMA Indicator Tests")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)