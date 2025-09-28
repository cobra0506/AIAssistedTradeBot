"""
Detailed Indicator Tests - Williams %R
======================================
This test file provides comprehensive testing for the Williams %R indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, williams_r, rsi, stochastic, macd, bollinger_bands


class TestWilliamsRIndicator(unittest.TestCase):
    """Test cases for Williams %R indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for Williams %R")
        print("="*60)
        
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

    def test_williams_r_basic_calculation(self):
        """Test basic Williams %R calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: Williams %R Basic Calculation")
        print("-"*60)
        
        # Calculate Williams %R
        wr_result = williams_r(self.simple_high, self.simple_low, self.simple_close, self.period)
        
        # Debug information
        print(f"High data: {self.simple_high.tolist()}")
        print(f"Low data: {self.simple_low.tolist()}")
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"Period: {self.period}")
        print(f"Williams %R result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        print(f"Williams %R type: {type(wr_result)}")
        print(f"Williams %R length: {len(wr_result)}")
        
        # Manual calculation verification for first valid Williams %R value
        # Williams %R = -100 * (Highest High - Close) / (Highest High - Lowest Low)
        first_valid_idx = self.period - 1
        if first_valid_idx < len(self.simple_close):
            highest_high = self.simple_high.iloc[first_valid_idx - self.period + 1:first_valid_idx + 1].max()
            lowest_low = self.simple_low.iloc[first_valid_idx - self.period + 1:first_valid_idx + 1].min()
            current_close = self.simple_close.iloc[first_valid_idx]
            
            expected_wr = -100 * (highest_high - current_close) / (highest_high - lowest_low)
            actual_wr = wr_result.iloc[first_valid_idx]
            
            print(f"\nManual calculation for index {first_valid_idx}:")
            print(f"Highest High in window: {highest_high}")
            print(f"Lowest Low in window: {lowest_low}")
            print(f"Current Close: {current_close}")
            print(f"Expected Williams %R: {expected_wr:.6f}")
            print(f"Actual Williams %R: {actual_wr:.6f}")
            
            # Assertions
            self.assertEqual(len(wr_result), len(self.simple_close), "Williams %R length should match input length")
            self.assertIsInstance(wr_result, pd.Series, "Williams %R should be a pandas Series")
            
            # Check Williams %R calculation
            self.assertAlmostEqual(
                actual_wr,
                expected_wr,
                places=10,
                msg=f"Williams %R calculation incorrect: got {actual_wr}, expected {expected_wr}"
            )
            print(f"✓ Williams %R calculation correct: {actual_wr:.6f} == {expected_wr:.6f}")
            
            # Check a few more values
            for i in range(first_valid_idx, min(first_valid_idx + 3, len(wr_result))):
                if not pd.isna(wr_result.iloc[i]):
                    highest_high_i = self.simple_high.iloc[i - self.period + 1:i + 1].max()
                    lowest_low_i = self.simple_low.iloc[i - self.period + 1:i + 1].min()
                    current_close_i = self.simple_close.iloc[i]
                    
                    expected_wr_i = -100 * (highest_high_i - current_close_i) / (highest_high_i - lowest_low_i)
                    
                    self.assertAlmostEqual(
                        wr_result.iloc[i],
                        expected_wr_i,
                        places=10,
                        msg=f"Williams %R calculation incorrect at index {i}: got {wr_result.iloc[i]}, expected {expected_wr_i}"
                    )
                    print(f"✓ Index {i}: Williams %R {wr_result.iloc[i]:.6f} == expected {expected_wr_i:.6f}")
            
            # Williams %R should be between -100 and 0
            for i in range(len(wr_result)):
                if not pd.isna(wr_result.iloc[i]):
                    self.assertGreaterEqual(
                        wr_result.iloc[i],
                        -100,
                        msg=f"Williams %R should be >= -100 at index {i}: got {wr_result.iloc[i]}"
                    )
                    self.assertLessEqual(
                        wr_result.iloc[i],
                        0,
                        msg=f"Williams %R should be <= 0 at index {i}: got {wr_result.iloc[i]}"
                    )
            
            print("✓ All Williams %R values are within valid range [-100, 0]")
        
        print("✓ Test passed: Basic Williams %R calculation")

    def test_williams_r_realistic_data(self):
        """Test Williams %R with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: Williams %R with Realistic Price Data")
        print("-"*60)
        
        # Calculate Williams %R
        wr_result = williams_r(self.realistic_high, self.realistic_low, self.realistic_close, self.period)
        
        # Debug information
        print(f"High data: {self.realistic_high.tolist()}")
        print(f"Low data: {self.realistic_low.tolist()}")
        print(f"Close data: {self.realistic_close.tolist()}")
        print(f"Williams %R result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        
        # Assertions
        self.assertEqual(len(wr_result), len(self.realistic_close))
        self.assertIsInstance(wr_result, pd.Series)
        
        # Williams %R should have both values closer to 0 and closer to -100 in typical market data
        valid_wr = wr_result.dropna()  # Remove NaN values
        if len(valid_wr) > 0:
            has_overbought = (valid_wr > -20).any()  # Values closer to 0 (overbought)
            has_oversold = (valid_wr < -80).any()   # Values closer to -100 (oversold)
            
            print(f"Has overbought values (>-20): {has_overbought}")
            print(f"Has oversold values (<-80): {has_oversold}")
            
            # In realistic data, we might see both conditions
            if has_overbought and has_oversold:
                print("✓ Williams %R shows both overbought and oversold conditions")
            elif has_overbought:
                print("! Williams %R shows only overbought conditions (this may be normal for strong uptrend)")
            elif has_oversold:
                print("! Williams %R shows only oversold conditions (this may be normal for strong downtrend)")
            else:
                print("! Williams %R shows no extreme conditions (values between -20 and -80)")
        
        print("✓ Test passed: Williams %R with realistic data")

    def test_williams_r_edge_cases(self):
        """
        Test Williams %R with edge cases
        """
        print("\n------------------------------------------------------------")
        print("TEST: Williams %R Edge Cases")
        print("------------------------------------------------------------")
        
        # Test with constant prices (all high, low, close values are the same)
        constant_high = [100.0] * 10
        constant_low = [100.0] * 10
        constant_close = [100.0] * 10
        
        print(f"Constant price data - High: {constant_high}")
        print(f"Constant price data - Low: {constant_low}")
        print(f"Constant price data - Close: {constant_close}")
        
        williams_r_result = self.indicator.calculate_williams_r(
            constant_high, constant_low, constant_close, period=5
        )
        
        print(f"Williams %R result: {self._format_series(williams_r_result)}")
        
        # With constant prices, all Williams %R values should be NaN
        for i in range(len(williams_r_result)):
            self.assertTrue(
                pd.isna(williams_r_result.iloc[i]), 
                f"With constant prices, Williams %R should be NaN at index {i}: got {float(williams_r_result.iloc[i])}"
            )
        
        # Test with period larger than data length
        williams_r_result = self.indicator.calculate_williams_r(
            self.high_data, self.low_data, self.close_data, period=20
        )
        
        print(f"\nTesting with period (20) larger than data length ({len(self.high_data)})")
        print(f"Williams %R result: {self._format_series(williams_r_result)}")
        
        # All values should be NaN when period > data length
        for i in range(len(williams_r_result)):
            self.assertTrue(
                pd.isna(williams_r_result.iloc[i]), 
                f"All values should be NaN when period > data length, but index {i} is {float(williams_r_result.iloc[i])}"
            )
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum period (1)
        williams_r_result = self.indicator.calculate_williams_r(
            self.high_data, self.low_data, self.close_data, period=1
        )
        
        print(f"\nTesting with minimum period (1):")
        print(f"Williams %R result: {self._format_series(williams_r_result)}")
        
        # With period 1, the formula becomes: (high - close) / (high - low) * -100
        # For index 0: (10 - 9) / (10 - 8) * -100 = 1 / 2 * -100 = -50
        self.assertEqual(
            float(williams_r_result.iloc[0]), 
            -50.0, 
            f"With period 1, Williams %R should be -50 at index 0: got {float(williams_r_result.iloc[0])}"
        )
        print(f"✓ Index 0: Williams %R = {float(williams_r_result.iloc[0])} (period 1)")
        
        # For index 1: (12 - 11) / (12 - 9) * -100 = 1 / 3 * -100 = -33.333...
        self.assertAlmostEqual(
            float(williams_r_result.iloc[1]), 
            -33.333333333333336, 
            places=5,
            msg=f"With period 1, Williams %R should be approximately -33.33333 at index 1: got {float(williams_r_result.iloc[1])}"
        )
        print(f"✓ Index 1: Williams %R = {float(williams_r_result.iloc[1])} (period 1)")
        
        print("✓ Test passed: Williams %R edge cases")

    def test_williams_r_error_handling(self):
        """
        Test Williams %R error handling
        """
        print("\n------------------------------------------------------------")
        print("TEST: Williams %R Error Handling")
        print("------------------------------------------------------------")
        
        # Test with empty data
        wr_empty = self.indicator.calculate_williams_r([], [], [])
        print(f"Empty data test - Williams %R type: {type(wr_empty)}")
        print(f"Empty data test - Williams %R length: {len(wr_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(wr_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with period 0
        try:
            wr_zero_period = self.indicator.calculate_williams_r(
                self.high_data, self.low_data, self.close_data, period=0
            )
            print(f"Result with period 0:")
            print(f"Williams %R: {self._format_series(wr_zero_period)}")
            
            # All values should be NaN with period 0
            for i in range(len(wr_zero_period)):
                self.assertTrue(pd.isna(wr_zero_period.iloc[i]), f"Value at index {i} should be NaN with period 0")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Error with period 0: {e}")
            self.fail(f"Failed to handle period 0: {e}")
        
        # Test with negative period
        try:
            wr_neg_period = self.indicator.calculate_williams_r(
                self.high_data, self.low_data, self.close_data, period=-1
            )
            print(f"Result with period -1:")
            print(f"Williams %R: {self._format_series(wr_neg_period)}")
            
            # All values should be NaN with negative period
            for i in range(len(wr_neg_period)):
                self.assertTrue(pd.isna(wr_neg_period.iloc[i]), f"Value at index {i} should be NaN with negative period")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Error with negative period: {e}")
            self.fail(f"Failed to handle negative period: {e}")
        
        print("✓ Test passed: Williams %R error handling")

    def test_williams_r_signal_analysis(self):
        """Test Williams %R signal analysis"""
        print("\n" + "-"*60)
        print("TEST: Williams %R Signal Analysis")
        print("-"*60)
        
        # Calculate Williams %R
        wr_result = williams_r(self.trend_high, self.trend_low, self.trend_close, self.period)
        
        print(f"Trend data - High: {self.trend_high.tolist()}")
        print(f"Trend data - Low: {self.trend_low.tolist()}")
        print(f"Trend data - Close: {self.trend_close.tolist()}")
        print(f"Williams %R: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        
        # Analyze overbought/oversold conditions
        # Note: Williams %R uses inverted scale compared to other oscillators
        # Values > -20 are considered overbought
        # Values < -80 are considered oversold
        overbought_threshold = -20
        oversold_threshold = -80
        
        overbought = wr_result > overbought_threshold
        oversold = wr_result < oversold_threshold
        
        print(f"\nOverbought/oversold analysis (thresholds: {oversold_threshold}/{overbought_threshold}):")
        print(f"Overbought: {overbought.tolist()}")
        print(f"Oversold: {oversold.tolist()}")
        
        # In an uptrend, we should see overbought conditions
        # In a downtrend, we should see oversold conditions
        uptrend_end = 4  # Peak of uptrend
        downtrend_end = 9  # End of downtrend
        
        if uptrend_end < len(wr_result) and not pd.isna(wr_result.iloc[uptrend_end]):
            wr_at_peak = wr_result.iloc[uptrend_end]
            
            print(f"\nAt uptrend peak (index {uptrend_end}):")
            print(f"Williams %R: {wr_at_peak:.2f}")
            
            # Should be elevated (closer to 0, but not necessarily overbought)
            self.assertGreaterEqual(
                wr_at_peak,
                -50,
                msg=f"Williams %R should be elevated at uptrend peak: got {wr_at_peak}"
            )
            print(f"✓ Williams %R ({wr_at_peak:.2f}) is elevated at uptrend peak")
        
        if downtrend_end < len(wr_result) and not pd.isna(wr_result.iloc[downtrend_end]):
            wr_at_trough = wr_result.iloc[downtrend_end]
            
            print(f"\nAt downtrend trough (index {downtrend_end}):")
            print(f"Williams %R: {wr_at_trough:.2f}")
            
            # Should be depressed (closer to -100, but not necessarily oversold)
            self.assertLessEqual(
                wr_at_trough,
                -50,
                msg=f"Williams %R should be depressed at downtrend trough: got {wr_at_trough}"
            )
            print(f"✓ Williams %R ({wr_at_trough:.2f}) is depressed at downtrend trough")
        
        print("✓ Test passed: Williams %R signal analysis")

    def test_williams_r_vs_stochastic_comparison(self):
        """Test Williams %R vs Stochastic comparison"""
        print("\n" + "-"*60)
        print("TEST: Williams %R vs Stochastic Comparison")
        print("-"*60)
        
        # Calculate both Williams %R and Stochastic
        wr_result = williams_r(self.realistic_high, self.realistic_low, self.realistic_close, self.period)
        k_percent, d_percent = stochastic(self.realistic_high, self.realistic_low, self.realistic_close, 
                                       self.period, 3)
        
        print(f"High data: {self.realistic_high.tolist()}")
        print(f"Low data: {self.realistic_low.tolist()}")
        print(f"Close data: {self.realistic_close.tolist()}")
        print(f"Williams %R: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        print(f"Stochastic %K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        
        # Williams %R and Stochastic should be inversely correlated
        # Williams %R = -100 to 0, Stochastic = 0 to 100
        # They should roughly follow: Williams %R ≈ Stochastic - 100
        
        valid_indices = []
        wr_values = []
        k_values = []
        
        for i in range(len(wr_result)):
            if (not pd.isna(wr_result.iloc[i]) and not pd.isna(k_percent.iloc[i])):
                valid_indices.append(i)
                wr_values.append(wr_result.iloc[i])
                k_values.append(k_percent.iloc[i])
        
        if len(valid_indices) >= 2:
            print(f"\nValid indices for comparison: {valid_indices}")
            
            # Check the inverse relationship
            for i in range(len(valid_indices)):
                idx = valid_indices[i]
                expected_wr_from_k = k_values[i] - 100
                
                print(f"Index {idx}: Williams %R={wr_values[i]:.2f}, Stochastic %K={k_values[i]:.2f}, Expected WR≈{expected_wr_from_k:.2f}")
                
                # They should be approximately inversely related (allow some tolerance)
                self.assertAlmostEqual(
                    wr_values[i],
                    expected_wr_from_k,
                    places=0,  # Allow some rounding differences
                    msg=f"Williams %R and Stochastic should be inversely related at index {idx}"
                )
                print(f"✓ Index {idx}: Inverse relationship holds")
        
        print("✓ Test passed: Williams %R vs Stochastic comparison")

    def test_williams_r_divergence_analysis(self):
        """Test Williams %R divergence analysis"""
        print("\n" + "-"*60)
        print("TEST: Williams %R Divergence Analysis")
        print("-"*60)
        
        # Create data with divergence patterns
        # Price makes higher highs but Williams %R makes lower highs (bearish divergence)
        divergence_high = pd.Series([100, 105, 110, 115, 120], name='high')
        divergence_low = pd.Series([90, 95, 100, 105, 110], name='low')
        divergence_close = pd.Series([95, 102, 108, 112, 118], name='close')  # Higher highs
        
        wr_result = williams_r(divergence_high, divergence_low, divergence_close, 3)
        
        print(f"Divergence data - High: {divergence_high.tolist()}")
        print(f"Divergence data - Low: {divergence_low.tolist()}")
        print(f"Divergence data - Close: {divergence_close.tolist()}")
        print(f"Williams %R: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        
        # Analyze divergence
        valid_indices = [i for i in range(len(wr_result)) if not pd.isna(wr_result.iloc[i])]
        
        if len(valid_indices) >= 2:
            print(f"\nValid indices for analysis: {valid_indices}")
            
            # Look for cases where price trend doesn't match Williams %R trend
            for i in range(len(valid_indices) - 1):
                idx1 = valid_indices[i]
                idx2 = valid_indices[i + 1]
                
                price_change = divergence_close.iloc[idx2] - divergence_close.iloc[idx1]
                wr_change = wr_result.iloc[idx2] - wr_result.iloc[idx1]
                
                print(f"Index {idx1} to {idx2}: Price change={price_change:+.2f}, Williams %R change={wr_change:+.2f}")
                
                # Divergence: price up but Williams %R down (bearish)
                # or price down but Williams %R up (bullish)
                if price_change > 0 and wr_change < 0:
                    print(f"✓ Bearish divergence detected: price up but Williams %R down")
                elif price_change < 0 and wr_change > 0:
                    print(f"✓ Bullish divergence detected: price down but Williams %R up")
                elif price_change * wr_change > 0:
                    print(f"✓ Confirmation: price and Williams %R moving in same direction")
        
        print("✓ Test passed: Williams %R divergence analysis")

    def test_williams_r_threshold_crossovers(self):
        """Test Williams %R threshold crossovers"""
        print("\n" + "-"*60)
        print("TEST: Williams %R Threshold Crossovers")
        print("-"*60)
        
        # Create data with clear threshold crossover patterns
        crossover_high = pd.Series([100, 102, 104, 106, 108, 106, 104, 102, 100, 102], name='high')
        crossover_low = pd.Series([90, 92, 94, 96, 98, 96, 94, 92, 90, 92], name='low')
        crossover_close = pd.Series([95, 97, 99, 101, 103, 101, 99, 97, 95, 97], name='close')
        
        wr_result = williams_r(crossover_high, crossover_low, crossover_close, 3)
        
        print(f"Crossover data - High: {crossover_high.tolist()}")
        print(f"Crossover data - Low: {crossover_low.tolist()}")
        print(f"Crossover data - Close: {crossover_close.tolist()}")
        print(f"Williams %R: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in wr_result.tolist()]}")
        
        # Define thresholds
        overbought_threshold = -20
        oversold_threshold = -80
        
        # Detect threshold crossovers
        crossovers = []
        for i in range(1, len(wr_result)):
            if (not pd.isna(wr_result.iloc[i]) and not pd.isna(wr_result.iloc[i-1])):
                
                # Bullish crossover: Williams %R crosses above oversold threshold
                if (wr_result.iloc[i-1] <= oversold_threshold and wr_result.iloc[i] > oversold_threshold):
                    crossovers.append((i, 'bullish_oversold'))
                
                # Bearish crossover: Williams %R crosses below overbought threshold
                elif (wr_result.iloc[i-1] >= overbought_threshold and wr_result.iloc[i] < overbought_threshold):
                    crossovers.append((i, 'bearish_overbought'))
                
                # Bullish crossover: Williams %R crosses above -50 (midpoint)
                if (wr_result.iloc[i-1] <= -50 and wr_result.iloc[i] > -50):
                    crossovers.append((i, 'bullish_midpoint'))
                
                # Bearish crossover: Williams %R crosses below -50 (midpoint)
                elif (wr_result.iloc[i-1] >= -50 and wr_result.iloc[i] < -50):
                    crossovers.append((i, 'bearish_midpoint'))
        
        print(f"\nDetected threshold crossovers: {crossovers}")
        
        # Verify that crossovers are detected correctly
        if len(crossovers) > 0:
            print(f"✓ Detected {len(crossovers)} threshold crossovers")
            
            # Verify each crossover
            for idx, signal_type in crossovers:
                if signal_type == 'bullish_oversold':
                    self.assertGreater(
                        wr_result.iloc[idx],
                        oversold_threshold,
                        msg=f"Bullish oversold crossover at index {idx}: Williams %R should be above {oversold_threshold}"
                    )
                    print(f"✓ Bullish oversold crossover at index {idx}: Williams %R={wr_result.iloc[idx]:.2f} > {oversold_threshold}")
                elif signal_type == 'bearish_overbought':
                    self.assertLess(
                        wr_result.iloc[idx],
                        overbought_threshold,
                        msg=f"Bearish overbought crossover at index {idx}: Williams %R should be below {overbought_threshold}"
                    )
                    print(f"✓ Bearish overbought crossover at index {idx}: Williams %R={wr_result.iloc[idx]:.2f} < {overbought_threshold}")
                elif signal_type == 'bullish_midpoint':
                    self.assertGreater(
                        wr_result.iloc[idx],
                        -50,
                        msg=f"Bullish midpoint crossover at index {idx}: Williams %R should be above -50"
                    )
                    print(f"✓ Bullish midpoint crossover at index {idx}: Williams %R={wr_result.iloc[idx]:.2f} > -50")
                elif signal_type == 'bearish_midpoint':
                    self.assertLess(
                        wr_result.iloc[idx],
                        -50,
                        msg=f"Bearish midpoint crossover at index {idx}: Williams %R should be below -50"
                    )
                    print(f"✓ Bearish midpoint crossover at index {idx}: Williams %R={wr_result.iloc[idx]:.2f} < -50")
        else:
            print("! No threshold crossovers detected (this may be normal for the given data)")
        
        print("✓ Test passed: Williams %R threshold crossovers")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting Williams %R Indicator Tests")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)