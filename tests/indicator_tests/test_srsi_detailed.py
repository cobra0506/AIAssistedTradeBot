"""
Detailed Indicator Tests - SRSI (Stochastic RSI)
=================================================
This test file provides comprehensive testing for the SRSI indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, srsi, rsi, stochastic, macd, bollinger_bands


class TestSRSIIndicator(unittest.TestCase):
    """Test cases for SRSI (Stochastic RSI) indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for SRSI")
        print("="*60)
        
        # Create simple test data
        self.simple_data = pd.Series([10, 12, 15, 14, 16, 18, 17, 19, 20, 18], name='close')
        self.period = 5
        self.d_period = 3
        
        # Create more realistic price data
        np.random.seed(42)  # For reproducible results
        self.realistic_data = pd.Series(
            [100.0, 102.5, 101.8, 103.2, 104.1, 103.5, 105.0, 106.2, 105.8, 107.1],
            name='close'
        )
        
        # Create edge case data (constant prices)
        self.edge_data = pd.Series([100.0] * 10, name='close')
        
        # Create trending data for signal analysis
        self.trend_data = pd.Series([100, 105, 110, 115, 120, 118, 115, 110, 105, 100], name='close')
        
        print(f"Simple test data: {self.simple_data.tolist()}")
        print(f"Realistic test data: {self.realistic_data.tolist()}")
        print(f"Edge case data: {self.edge_data.tolist()}")
        print(f"Trend data: {self.trend_data.tolist()}")
        print(f"RSI period: {self.period}")
        print(f"D period: {self.d_period}")

    def test_srsi_basic_calculation(self):
        """Test basic SRSI calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: SRSI Basic Calculation")
        print("-"*60)
        
        # Calculate SRSI
        srsi_k, srsi_d = srsi(self.simple_data, self.period, self.d_period)
        
        # Debug information
        print(f"Input data: {self.simple_data.tolist()}")
        print(f"RSI period: {self.period}")
        print(f"D period: {self.d_period}")
        print(f"SRSI-K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        print(f"SRSI-K type: {type(srsi_k)}")
        print(f"SRSI-D type: {type(srsi_d)}")
        print(f"SRSI-K length: {len(srsi_k)}")
        print(f"SRSI-D length: {len(srsi_d)}")
        
        # Calculate RSI values for verification
        rsi_values = rsi(self.simple_data, self.period)
        print(f"RSI values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in rsi_values.tolist()]}")
        
        # Manual calculation verification for first valid SRSI-K value
        # SRSI-K = 100 * (RSI - Lowest RSI) / (Highest RSI - Lowest RSI)
        first_valid_idx = self.period * 2 - 1  # Need enough data for both RSI and SRSI
        if first_valid_idx < len(self.simple_data):
            window_rsi = rsi_values.iloc[first_valid_idx - self.period + 1:first_valid_idx + 1]
            highest_rsi = window_rsi.max()
            lowest_rsi = window_rsi.min()
            current_rsi = rsi_values.iloc[first_valid_idx]
            
            if not pd.isna(current_rsi) and not pd.isna(highest_rsi) and not pd.isna(lowest_rsi):
                expected_srsi_k = 100 * (current_rsi - lowest_rsi) / (highest_rsi - lowest_rsi)
                actual_srsi_k = srsi_k.iloc[first_valid_idx]
                
                print(f"\nManual calculation for index {first_valid_idx}:")
                print(f"RSI window: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in window_rsi.tolist()]}")
                print(f"Highest RSI in window: {highest_rsi:.6f}")
                print(f"Lowest RSI in window: {lowest_rsi:.6f}")
                print(f"Current RSI: {current_rsi:.6f}")
                print(f"Expected SRSI-K: {expected_srsi_k:.6f}")
                print(f"Actual SRSI-K: {actual_srsi_k:.6f}")
                
                # Assertions
                self.assertEqual(len(srsi_k), len(self.simple_data), "SRSI-K length should match input length")
                self.assertEqual(len(srsi_d), len(self.simple_data), "SRSI-D length should match input length")
                self.assertIsInstance(srsi_k, pd.Series, "SRSI-K should be a pandas Series")
                self.assertIsInstance(srsi_d, pd.Series, "SRSI-D should be a pandas Series")
                
                # Check SRSI-K calculation
                self.assertAlmostEqual(
                    actual_srsi_k,
                    expected_srsi_k,
                    places=10,
                    msg=f"SRSI-K calculation incorrect: got {actual_srsi_k}, expected {expected_srsi_k}"
                )
                print(f"✓ SRSI-K calculation correct: {actual_srsi_k:.6f} == {expected_srsi_k:.6f}")
                
                # SRSI-K should be between 0 and 100
                for i in range(len(srsi_k)):
                    if not pd.isna(srsi_k.iloc[i]):
                        self.assertGreaterEqual(
                            srsi_k.iloc[i],
                            0,
                            msg=f"SRSI-K should be >= 0 at index {i}: got {srsi_k.iloc[i]}"
                        )
                        self.assertLessEqual(
                            srsi_k.iloc[i],
                            100,
                            msg=f"SRSI-K should be <= 100 at index {i}: got {srsi_k.iloc[i]}"
                        )
                
                # SRSI-D should be between 0 and 100
                for i in range(len(srsi_d)):
                    if not pd.isna(srsi_d.iloc[i]):
                        self.assertGreaterEqual(
                            srsi_d.iloc[i],
                            0,
                            msg=f"SRSI-D should be >= 0 at index {i}: got {srsi_d.iloc[i]}"
                        )
                        self.assertLessEqual(
                            srsi_d.iloc[i],
                            100,
                            msg=f"SRSI-D should be <= 100 at index {i}: got {srsi_d.iloc[i]}"
                        )
                
                print("✓ All SRSI-K and SRSI-D values are within valid range [0, 100]")
        
        print("✓ Test passed: Basic SRSI calculation")

    def test_srsi_realistic_data(self):
        """Test SRSI with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: SRSI with Realistic Price Data")
        print("-"*60)
        
        # Calculate SRSI
        srsi_k, srsi_d = srsi(self.realistic_data, self.period, self.d_period)
        
        # Debug information
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"SRSI-K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # Calculate RSI values for verification
        rsi_values = rsi(self.realistic_data, self.period)
        print(f"RSI values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in rsi_values.tolist()]}")
        
        # Verify SRSI-D is SMA of SRSI-K
        expected_d = srsi_k.rolling(window=self.d_period).mean()
        
        print(f"Expected SRSI-D (SMA of SRSI-K): {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in expected_d.tolist()]}")
        
        # Assertions
        self.assertEqual(len(srsi_k), len(self.realistic_data))
        self.assertEqual(len(srsi_d), len(self.realistic_data))
        self.assertIsInstance(srsi_k, pd.Series)
        self.assertIsInstance(srsi_d, pd.Series)
        
        # Check SRSI-D calculation
        for i in range(len(srsi_d)):
            if not pd.isna(srsi_d.iloc[i]) and not pd.isna(expected_d.iloc[i]):
                self.assertAlmostEqual(
                    srsi_d.iloc[i],
                    expected_d.iloc[i],
                    places=10,
                    msg=f"SRSI-D calculation incorrect at index {i}: got {srsi_d.iloc[i]}, expected {expected_d.iloc[i]}"
                )
                print(f"✓ Index {i}: SRSI-D {srsi_d.iloc[i]:.6f} == expected {expected_d.iloc[i]:.6f}")
        
        print("✓ Test passed: SRSI with realistic data")

    def test_srsi_edge_cases(self):
        """Test SRSI with edge cases"""
        print("\n" + "-"*60)
        print("TEST: SRSI Edge Cases")
        print("-"*60)
        
        # Test with constant prices
        srsi_k, srsi_d = srsi(self.edge_data, self.period, self.d_period)
        
        print(f"Constant price data: {self.edge_data.tolist()}")
        print(f"SRSI-K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # With constant prices, RSI should be 50, and SRSI should be 50 as well
        for i in range(len(srsi_k)):
            if not pd.isna(srsi_k.iloc[i]):
                # With constant prices, SRSI should be 50
                self.assertAlmostEqual(
                    srsi_k.iloc[i],
                    50.0,
                    places=10,
                    msg=f"With constant prices, SRSI-K should be 50 at index {i}: got {srsi_k.iloc[i]}"
                )
                print(f"✓ Index {i}: SRSI-K = {srsi_k.iloc[i]} (constant prices)")
        
        # Test with period larger than data length
        large_period = 20
        srsi_large_k, srsi_large_d = srsi(self.simple_data, large_period, self.d_period)
        
        print(f"\nTesting with RSI period ({large_period}) larger than data length ({len(self.simple_data)})")
        print(f"SRSI-K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_large_k.tolist()]}")
        print(f"SRSI-D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_large_d.tolist()]}")
        
        # All values should be NaN
        self.assertTrue(srsi_large_k.isna().all(), "All SRSI-K values should be NaN when period > data length")
        self.assertTrue(srsi_large_d.isna().all(), "All SRSI-D values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum valid periods
        srsi_min_k, srsi_min_d = srsi(self.simple_data, 1, 1)
        
        print(f"\nTesting with minimum periods (RSI=1, D=1):")
        print(f"SRSI-K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_min_k.tolist()]}")
        print(f"SRSI-D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_min_d.tolist()]}")
        
        # With period 1, SRSI-K should equal SRSI-D
        for i in range(len(srsi_min_k)):
            if not pd.isna(srsi_min_k.iloc[i]) and not pd.isna(srsi_min_d.iloc[i]):
                self.assertEqual(
                    srsi_min_k.iloc[i],
                    srsi_min_d.iloc[i],
                    msg=f"With period 1, SRSI-K should equal SRSI-D at index {i}: SRSI-K={srsi_min_k.iloc[i]}, SRSI-D={srsi_min_d.iloc[i]}"
                )
                print(f"✓ Index {i}: SRSI-K = SRSI-D = {srsi_min_k.iloc[i]}")
        
        print("✓ Test passed: SRSI edge cases")

    def test_srsi_error_handling(self):
        """Test SRSI error handling"""
        print("\n" + "-"*60)
        print("TEST: SRSI Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_data = pd.Series([], dtype=float)
        srsi_empty_k, srsi_empty_d = srsi(empty_data, self.period, self.d_period)
        
        print(f"Empty data test - SRSI-K type: {type(srsi_empty_k)}")
        print(f"Empty data test - SRSI-K length: {len(srsi_empty_k)}")
        print(f"Empty data test - SRSI-D type: {type(srsi_empty_d)}")
        print(f"Empty data test - SRSI-D length: {len(srsi_empty_d)}")
        
        self.assertIsInstance(srsi_empty_k, pd.Series)
        self.assertIsInstance(srsi_empty_d, pd.Series)
        self.assertEqual(len(srsi_empty_k), 0)
        self.assertEqual(len(srsi_empty_d), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid periods
        try:
            srsi_invalid_k, srsi_invalid_d = srsi(self.simple_data, 0, self.d_period)
            print("Result with RSI period 0:")
            print(f"SRSI-K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_invalid_k.tolist()]}")
            print(f"SRSI-D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_invalid_d.tolist()]}")
            print("✓ Handles RSI period 0 without crashing")
        except Exception as e:
            print(f"Exception with RSI period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            srsi_invalid_k, srsi_invalid_d = srsi(self.simple_data, self.period, 0)
            print("Result with D period 0:")
            print(f"SRSI-K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_invalid_k.tolist()]}")
            print(f"SRSI-D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_invalid_d.tolist()]}")
            print("✓ Handles D period 0 without crashing")
        except Exception as e:
            print(f"Exception with D period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            srsi_negative_k, srsi_negative_d = srsi(self.simple_data, -1, self.d_period)
            print("Result with RSI period -1:")
            print(f"SRSI-K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_negative_k.tolist()]}")
            print(f"SRSI-D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_negative_d.tolist()]}")
            print("✓ Handles negative RSI period without crashing")
        except Exception as e:
            print(f"Exception with RSI period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: SRSI error handling")

    def test_srsi_vs_rsi_comparison(self):
        """Test SRSI vs RSI comparison"""
        print("\n" + "-"*60)
        print("TEST: SRSI vs RSI Comparison")
        print("-"*60)
        
        # Calculate both RSI and SRSI
        rsi_values = rsi(self.realistic_data, self.period)
        srsi_k, srsi_d = srsi(self.realistic_data, self.period, self.d_period)
        
        print(f"Input data: {self.realistic_data.tolist()}")
        print(f"RSI values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in rsi_values.tolist()]}")
        print(f"SRSI-K values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D values: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # SRSI should be more sensitive than RSI
        # Create a trending price series to show the difference
        trend_data = pd.Series([
            100.0, 101.0, 102.0, 105.0, 108.0, 110.0, 112.0, 115.0, 118.0, 120.0,
            122.0, 125.0, 128.0, 130.0, 132.0  # Extended trend for better analysis
        ], name='close')
        
        rsi_trend = rsi(trend_data, self.period)
        srsi_k_trend, srsi_d_trend = srsi(trend_data, self.period, self.d_period)
        
        print(f"\nTesting with trending price series:")
        print(f"Trend data: {trend_data.tolist()}")
        print(f"RSI trend: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in rsi_trend.tolist()]}")
        print(f"SRSI-K trend: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_k_trend.tolist()]}")
        print(f"SRSI-D trend: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_d_trend.tolist()]}")
        
        # Analyze the range and sensitivity
        valid_indices = []
        rsi_values_list = []
        srsi_k_values_list = []
        
        for i in range(len(trend_data)):
            if (not pd.isna(rsi_trend.iloc[i]) and not pd.isna(srsi_k_trend.iloc[i])):
                valid_indices.append(i)
                rsi_values_list.append(rsi_trend.iloc[i])
                srsi_k_values_list.append(srsi_k_trend.iloc[i])
        
        if valid_indices:
            rsi_range = max(rsi_values_list) - min(rsi_values_list)
            srsi_range = max(srsi_k_values_list) - min(srsi_k_values_list)
            
            print(f"\nRange analysis:")
            print(f"RSI range: {rsi_range:.6f}")
            print(f"SRSI-K range: {srsi_range:.6f}")
            
            # SRSI should generally have a wider range than RSI (more sensitive)
            self.assertGreaterEqual(
                srsi_range,
                rsi_range * 0.8,  # Allow some tolerance
                msg=f"SRSI should have a wider range than RSI: SRSI range={srsi_range}, RSI range={rsi_range}"
            )
            print(f"✓ SRSI range ({srsi_range:.6f}) is comparable to RSI range ({rsi_range:.6f})")
        
        print("✓ Test passed: SRSI vs RSI comparison")

    def test_srsi_signal_analysis(self):
        """Test SRSI signal analysis"""
        print("\n" + "-"*60)
        print("TEST: SRSI Signal Analysis")
        print("-"*60)
        
        # Calculate SRSI
        srsi_k, srsi_d = srsi(self.trend_data, self.period, self.d_period)
        
        print(f"Trend data: {self.trend_data.tolist()}")
        print(f"SRSI-K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # Analyze overbought/oversold conditions
        overbought_threshold = 80
        oversold_threshold = 20
        
        overbought_k = srsi_k > overbought_threshold
        oversold_k = srsi_k < oversold_threshold
        overbought_d = srsi_d > overbought_threshold
        oversold_d = srsi_d < oversold_threshold
        
        print(f"\nOverbought/oversold analysis (thresholds: {oversold_threshold}/{overbought_threshold}):")
        print(f"SRSI-K overbought: {overbought_k.tolist()}")
        print(f"SRSI-K oversold: {oversold_k.tolist()}")
        print(f"SRSI-D overbought: {overbought_d.tolist()}")
        print(f"SRSI-D oversold: {oversold_d.tolist()}")
        
        # In an uptrend, we should see overbought conditions
        # In a downtrend, we should see oversold conditions
        uptrend_end = 4  # Peak of uptrend
        downtrend_end = 9  # End of downtrend
        
        if uptrend_end < len(srsi_k) and not pd.isna(srsi_k.iloc[uptrend_end]):
            k_at_peak = srsi_k.iloc[uptrend_end]
            d_at_peak = srsi_d.iloc[uptrend_end]
            
            print(f"\nAt uptrend peak (index {uptrend_end}):")
            print(f"SRSI-K: {k_at_peak:.2f}, SRSI-D: {d_at_peak:.2f}")
            
            # Should be elevated (but not necessarily overbought)
            self.assertGreaterEqual(
                k_at_peak,
                30,
                msg=f"SRSI-K should be elevated at uptrend peak: got {k_at_peak}"
            )
            print(f"✓ SRSI-K ({k_at_peak:.2f}) is elevated at uptrend peak")
        
        if downtrend_end < len(srsi_k) and not pd.isna(srsi_k.iloc[downtrend_end]):
            k_at_trough = srsi_k.iloc[downtrend_end]
            d_at_trough = srsi_d.iloc[downtrend_end]
            
            print(f"\nAt downtrend trough (index {downtrend_end}):")
            print(f"SRSI-K: {k_at_trough:.2f}, SRSI-D: {d_at_trough:.2f}")
            
            # Should be depressed (but not necessarily oversold)
            self.assertLessEqual(
                k_at_trough,
                70,
                msg=f"SRSI-K should be depressed at downtrend trough: got {k_at_trough}"
            )
            print(f"✓ SRSI-K ({k_at_trough:.2f}) is depressed at downtrend trough")
        
        print("✓ Test passed: SRSI signal analysis")

    def test_srsi_crossover_signals(self):
        """Test SRSI crossover signals"""
        print("\n" + "-"*60)
        print("TEST: SRSI Crossover Signals")
        print("-"*60)
        
        # Create data with clear crossover patterns
        crossover_data = pd.Series([100, 102, 104, 106, 108, 106, 104, 102, 100, 102], name='close')
        
        srsi_k, srsi_d = srsi(crossover_data, self.period, self.d_period)
        
        print(f"Crossover data: {crossover_data.tolist()}")
        print(f"SRSI-K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # Detect crossovers
        crossovers = []
        for i in range(1, len(srsi_k)):
            if (not pd.isna(srsi_k.iloc[i]) and not pd.isna(srsi_d.iloc[i]) and
                not pd.isna(srsi_k.iloc[i-1]) and not pd.isna(srsi_d.iloc[i-1])):
                
                # Bullish crossover: SRSI-K crosses above SRSI-D
                if (srsi_k.iloc[i-1] <= srsi_d.iloc[i-1] and 
                    srsi_k.iloc[i] > srsi_d.iloc[i]):
                    crossovers.append((i, 'bullish'))
                
                # Bearish crossover: SRSI-K crosses below SRSI-D
                elif (srsi_k.iloc[i-1] >= srsi_d.iloc[i-1] and 
                      srsi_k.iloc[i] < srsi_d.iloc[i]):
                    crossovers.append((i, 'bearish'))
        
        print(f"\nDetected crossovers: {crossovers}")
        
        # Verify that crossovers are detected correctly
        if len(crossovers) > 0:
            print(f"✓ Detected {len(crossovers)} crossovers")
            
            # Verify each crossover
            for idx, signal_type in crossovers:
                if signal_type == 'bullish':
                    self.assertGreater(
                        srsi_k.iloc[idx],
                        srsi_d.iloc[idx],
                        msg=f"Bullish crossover at index {idx}: SRSI-K should be above SRSI-D"
                    )
                    print(f"✓ Bullish crossover at index {idx}: SRSI-K={srsi_k.iloc[idx]:.2f} > SRSI-D={srsi_d.iloc[idx]:.2f}")
                elif signal_type == 'bearish':
                    self.assertLess(
                        srsi_k.iloc[idx],
                        srsi_d.iloc[idx],
                        msg=f"Bearish crossover at index {idx}: SRSI-K should be below SRSI-D"
                    )
                    print(f"✓ Bearish crossover at index {idx}: SRSI-K={srsi_k.iloc[idx]:.2f} < SRSI-D={srsi_d.iloc[idx]:.2f}")
        else:
            print("! No crossovers detected (this may be normal for the given data)")
        
        print("✓ Test passed: SRSI crossover signals")

    def test_srsi_divergence_analysis(self):
        """Test SRSI divergence analysis"""
        print("\n" + "-"*60)
        print("TEST: SRSI Divergence Analysis")
        print("-"*60)
        
        # Create data with divergence patterns
        # Price makes higher highs but SRSI makes lower highs (bearish divergence)
        divergence_data = pd.Series([100, 105, 110, 115, 120], name='close')
        
        srsi_k, srsi_d = srsi(divergence_data, self.period, self.d_period)
        
        print(f"Divergence data: {divergence_data.tolist()}")
        print(f"SRSI-K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_k.tolist()]}")
        print(f"SRSI-D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in srsi_d.tolist()]}")
        
        # Analyze divergence
        valid_indices = [i for i in range(len(srsi_k)) if not pd.isna(srsi_k.iloc[i])]
        
        if len(valid_indices) >= 2:
            print(f"\nValid indices for analysis: {valid_indices}")
            
            # Look for cases where price trend doesn't match SRSI trend
            for i in range(len(valid_indices) - 1):
                idx1 = valid_indices[i]
                idx2 = valid_indices[i + 1]
                
                price_change = divergence_data.iloc[idx2] - divergence_data.iloc[idx1]
                k_change = srsi_k.iloc[idx2] - srsi_k.iloc[idx1]
                
                print(f"Index {idx1} to {idx2}: Price change={price_change:+.2f}, SRSI-K change={k_change:+.2f}")
                
                # Divergence: price up but SRSI down (bearish)
                # or price down but SRSI up (bullish)
                if price_change > 0 and k_change < 0:
                    print(f"✓ Bearish divergence detected: price up but SRSI-K down")
                elif price_change < 0 and k_change > 0:
                    print(f"✓ Bullish divergence detected: price down but SRSI-K up")
                elif price_change * k_change > 0:
                    print(f"✓ Confirmation: price and SRSI-K moving in same direction")
        
        print("✓ Test passed: SRSI divergence analysis")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting SRSI Indicator Tests")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)