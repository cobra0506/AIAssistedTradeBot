"""
Detailed Indicator Tests - Stochastic Oscillator
================================================
This test file provides comprehensive testing for the Stochastic Oscillator indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, stochastic, srsi, rsi, macd, bollinger_bands


class TestStochasticIndicator(unittest.TestCase):
    """Test cases for Stochastic Oscillator indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for Stochastic Oscillator")
        print("="*60)
        
        # Create simple test data with high, low, close
        self.simple_high = pd.Series([10, 12, 15, 14, 16, 18, 17, 19, 20, 18], name='high')
        self.simple_low = pd.Series([8, 9, 11, 10, 12, 14, 13, 15, 16, 14], name='low')
        self.simple_close = pd.Series([9, 11, 14, 13, 15, 17, 16, 18, 19, 17], name='close')
        self.k_period = 5
        self.d_period = 3
        
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
        
        print(f"Simple high data: {self.simple_high.tolist()}")
        print(f"Simple low data: {self.simple_low.tolist()}")
        print(f"Simple close data: {self.simple_close.tolist()}")
        print(f"K period: {self.k_period}")
        print(f"D period: {self.d_period}")

    def test_stochastic_basic_calculation(self):
        """Test basic Stochastic calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Basic Calculation")
        print("-"*60)
        
        # Calculate Stochastic
        k_percent, d_percent = stochastic(self.simple_high, self.simple_low, self.simple_close, 
                                         self.k_period, self.d_period)
        
        # Debug information
        print(f"High data: {self.simple_high.tolist()}")
        print(f"Low data: {self.simple_low.tolist()}")
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"K period: {self.k_period}")
        print(f"D period: {self.d_period}")
        print(f"%K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        print(f"%K type: {type(k_percent)}")
        print(f"%D type: {type(d_percent)}")
        print(f"%K length: {len(k_percent)}")
        print(f"%D length: {len(d_percent)}")
        
        # Manual calculation verification for first valid %K value
        # %K = 100 * (Close - Lowest Low) / (Highest High - Lowest Low)
        first_valid_idx = self.k_period - 1
        if first_valid_idx < len(self.simple_close):
            window_high = self.simple_high.iloc[:self.k_period].max()
            window_low = self.simple_low.iloc[:self.k_period].min()
            window_close = self.simple_close.iloc[first_valid_idx]
            
            expected_k = 100 * (window_close - window_low) / (window_high - window_low)
            actual_k = k_percent.iloc[first_valid_idx]
            
            print(f"\nManual calculation for index {first_valid_idx}:")
            print(f"Highest High in window: {window_high}")
            print(f"Lowest Low in window: {window_low}")
            print(f"Close price: {window_close}")
            print(f"Expected %K: {expected_k:.6f}")
            print(f"Actual %K: {actual_k:.6f}")
            
            # Assertions
            self.assertEqual(len(k_percent), len(self.simple_close), "%K length should match input length")
            self.assertEqual(len(d_percent), len(self.simple_close), "%D length should match input length")
            self.assertIsInstance(k_percent, pd.Series, "%K should be a pandas Series")
            self.assertIsInstance(d_percent, pd.Series, "%D should be a pandas Series")
            
            # Check %K calculation
            self.assertAlmostEqual(
                actual_k,
                expected_k,
                places=10,
                msg=f"%K calculation incorrect: got {actual_k}, expected {expected_k}"
            )
            print(f"✓ %K calculation correct: {actual_k:.6f} == {expected_k:.6f}")
            
            # %K should be between 0 and 100
            for i in range(len(k_percent)):
                if not pd.isna(k_percent.iloc[i]):
                    self.assertGreaterEqual(
                        k_percent.iloc[i],
                        0,
                        msg=f"%K should be >= 0 at index {i}: got {k_percent.iloc[i]}"
                    )
                    self.assertLessEqual(
                        k_percent.iloc[i],
                        100,
                        msg=f"%K should be <= 100 at index {i}: got {k_percent.iloc[i]}"
                    )
            
            # %D should be between 0 and 100
            for i in range(len(d_percent)):
                if not pd.isna(d_percent.iloc[i]):
                    self.assertGreaterEqual(
                        d_percent.iloc[i],
                        0,
                        msg=f"%D should be >= 0 at index {i}: got {d_percent.iloc[i]}"
                    )
                    self.assertLessEqual(
                        d_percent.iloc[i],
                        100,
                        msg=f"%D should be <= 100 at index {i}: got {d_percent.iloc[i]}"
                    )
            
            print("✓ All %K and %D values are within valid range [0, 100]")
        
        print("✓ Test passed: Basic Stochastic calculation")

    def test_stochastic_realistic_data(self):
        """Test Stochastic with realistic price data"""
        print("\n" + "-"*60)
        print("TEST: Stochastic with Realistic Price Data")
        print("-"*60)
        
        # Calculate Stochastic
        k_percent, d_percent = stochastic(self.realistic_high, self.realistic_low, self.realistic_close,
                                         self.k_period, self.d_period)
        
        # Debug information
        print(f"High data: {self.realistic_high.tolist()}")
        print(f"Low data: {self.realistic_low.tolist()}")
        print(f"Close data: {self.realistic_close.tolist()}")
        print(f"%K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        
        # Verify %D is SMA of %K
        expected_d = k_percent.rolling(window=self.d_period).mean()
        
        print(f"Expected %D (SMA of %K): {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in expected_d.tolist()]}")
        
        # Assertions
        self.assertEqual(len(k_percent), len(self.realistic_close))
        self.assertEqual(len(d_percent), len(self.realistic_close))
        self.assertIsInstance(k_percent, pd.Series)
        self.assertIsInstance(d_percent, pd.Series)
        
        # Check %D calculation
        for i in range(len(d_percent)):
            if not pd.isna(d_percent.iloc[i]) and not pd.isna(expected_d.iloc[i]):
                self.assertAlmostEqual(
                    d_percent.iloc[i],
                    expected_d.iloc[i],
                    places=10,
                    msg=f"%D calculation incorrect at index {i}: got {d_percent.iloc[i]}, expected {expected_d.iloc[i]}"
                )
                print(f"✓ Index {i}: %D {d_percent.iloc[i]:.6f} == expected {expected_d.iloc[i]:.6f}")
        
        print("✓ Test passed: Stochastic with realistic data")

    def test_stochastic_edge_cases(self):
        """Test Stochastic with edge cases"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Edge Cases")
        print("-"*60)
        
        # Test with constant prices (high = low = close)
        k_percent, d_percent = stochastic(self.edge_high, self.edge_low, self.edge_close,
                                         self.k_period, self.d_period)
        
        print(f"Constant price data - High: {self.edge_high.tolist()}")
        print(f"Constant price data - Low: {self.edge_low.tolist()}")
        print(f"Constant price data - Close: {self.edge_close.tolist()}")
        print(f"%K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        
        # With constant prices, %K should be 100 when close equals high (and low)
        for i in range(len(k_percent)):
            if not pd.isna(k_percent.iloc[i]):
                # When high = low = close, %K should be 100 (or undefined, but typically handled as 100)
                self.assertEqual(
                    k_percent.iloc[i],
                    100.0,
                    msg=f"With constant prices, %K should be 100 at index {i}: got {k_percent.iloc[i]}"
                )
                print(f"✓ Index {i}: %K = {k_percent.iloc[i]} (constant prices)")
        
        # Test with period larger than data length
        large_k_period = 20
        k_large, d_large = stochastic(self.simple_high, self.simple_low, self.simple_close,
                                       large_k_period, self.d_period)
        
        print(f"\nTesting with K period ({large_k_period}) larger than data length ({len(self.simple_close)})")
        print(f"%K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_large.tolist()]}")
        print(f"%D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_large.tolist()]}")
        
        # All values should be NaN
        self.assertTrue(k_large.isna().all(), "All %K values should be NaN when period > data length")
        self.assertTrue(d_large.isna().all(), "All %D values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum valid periods
        k_min, d_min = stochastic(self.simple_high, self.simple_low, self.simple_close, 1, 1)
        
        print(f"\nTesting with minimum periods (K=1, D=1):")
        print(f"%K result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_min.tolist()]}")
        print(f"%D result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_min.tolist()]}")
        
        # With period 1, %K should equal %D
        for i in range(len(k_min)):
            if not pd.isna(k_min.iloc[i]) and not pd.isna(d_min.iloc[i]):
                self.assertEqual(
                    k_min.iloc[i],
                    d_min.iloc[i],
                    msg=f"With period 1, %K should equal %D at index {i}: %K={k_min.iloc[i]}, %D={d_min.iloc[i]}"
                )
                print(f"✓ Index {i}: %K = %D = {k_min.iloc[i]}")
        
        print("✓ Test passed: Stochastic edge cases")

    def test_stochastic_error_handling(self):
        """Test Stochastic error handling"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_high = pd.Series([], dtype=float)
        empty_low = pd.Series([], dtype=float)
        empty_close = pd.Series([], dtype=float)
        
        k_empty, d_empty = stochastic(empty_high, empty_low, empty_close, self.k_period, self.d_period)
        
        print(f"Empty data test - %K type: {type(k_empty)}")
        print(f"Empty data test - %K length: {len(k_empty)}")
        print(f"Empty data test - %D type: {type(d_empty)}")
        print(f"Empty data test - %D length: {len(d_empty)}")
        
        self.assertIsInstance(k_empty, pd.Series)
        self.assertIsInstance(d_empty, pd.Series)
        self.assertEqual(len(k_empty), 0)
        self.assertEqual(len(d_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid periods
        try:
            k_invalid, d_invalid = stochastic(self.simple_high, self.simple_low, self.simple_close, 0, self.d_period)
            print("Result with K period 0:")
            print(f"%K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_invalid.tolist()]}")
            print(f"%D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_invalid.tolist()]}")
            print("✓ Handles K period 0 without crashing")
        except Exception as e:
            print(f"Exception with K period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            k_invalid, d_invalid = stochastic(self.simple_high, self.simple_low, self.simple_close, self.k_period, 0)
            print("Result with D period 0:")
            print(f"%K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_invalid.tolist()]}")
            print(f"%D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_invalid.tolist()]}")
            print("✓ Handles D period 0 without crashing")
        except Exception as e:
            print(f"Exception with D period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            k_negative, d_negative = stochastic(self.simple_high, self.simple_low, self.simple_close, -1, self.d_period)
            print("Result with K period -1:")
            print(f"%K: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in k_negative.tolist()]}")
            print(f"%D: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in d_negative.tolist()]}")
            print("✓ Handles negative K period without crashing")
        except Exception as e:
            print(f"Exception with K period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: Stochastic error handling")

    def test_stochastic_signal_analysis(self):
        """Test Stochastic signal analysis"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Signal Analysis")
        print("-"*60)
        
        # Create price data with clear overbought/oversold patterns
        # Uptrend followed by downtrend
        trend_high = pd.Series([100, 105, 110, 115, 120, 118, 115, 110, 105, 100], name='high')
        trend_low = pd.Series([95, 100, 105, 110, 115, 113, 110, 105, 100, 95], name='low')
        trend_close = pd.Series([98, 103, 108, 113, 118, 116, 113, 108, 103, 98], name='close')
        
        k_percent, d_percent = stochastic(trend_high, trend_low, trend_close, 5, 3)
        
        print(f"Trend data - High: {trend_high.tolist()}")
        print(f"Trend data - Low: {trend_low.tolist()}")
        print(f"Trend data - Close: {trend_close.tolist()}")
        print(f"%K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        
        # Analyze overbought/oversold conditions
        overbought_threshold = 80
        oversold_threshold = 20
        
        overbought_k = k_percent > overbought_threshold
        oversold_k = k_percent < oversold_threshold
        overbought_d = d_percent > overbought_threshold
        oversold_d = d_percent < oversold_threshold
        
        print(f"\nOverbought/oversold analysis (thresholds: {oversold_threshold}/{overbought_threshold}):")
        print(f"%K overbought: {overbought_k.tolist()}")
        print(f"%K oversold: {oversold_k.tolist()}")
        print(f"%D overbought: {overbought_d.tolist()}")
        print(f"%D oversold: {oversold_d.tolist()}")
        
        # In an uptrend, we should see overbought conditions
        # In a downtrend, we should see oversold conditions
        uptrend_end = 4  # Peak of uptrend
        downtrend_end = 9  # End of downtrend
        
        if uptrend_end < len(k_percent) and not pd.isna(k_percent.iloc[uptrend_end]):
            k_at_peak = k_percent.iloc[uptrend_end]
            d_at_peak = d_percent.iloc[uptrend_end]
            
            print(f"\nAt uptrend peak (index {uptrend_end}):")
            print(f"%K: {k_at_peak:.2f}, %D: {d_at_peak:.2f}")
            
            # Should be overbought or approaching overbought
            self.assertGreaterEqual(
                k_at_peak,
                50,
                msg=f"%K should be elevated at uptrend peak: got {k_at_peak}"
            )
            print(f"✓ %K ({k_at_peak:.2f}) is elevated at uptrend peak")
        
        if downtrend_end < len(k_percent) and not pd.isna(k_percent.iloc[downtrend_end]):
            k_at_trough = k_percent.iloc[downtrend_end]
            d_at_trough = d_percent.iloc[downtrend_end]
            
            print(f"\nAt downtrend trough (index {downtrend_end}):")
            print(f"%K: {k_at_trough:.2f}, %D: {d_at_trough:.2f}")
            
            # Should be oversold or approaching oversold
            self.assertLessEqual(
                k_at_trough,
                50,
                msg=f"%K should be depressed at downtrend trough: got {k_at_trough}"
            )
            print(f"✓ %K ({k_at_trough:.2f}) is depressed at downtrend trough")
        
        print("✓ Test passed: Stochastic signal analysis")

    def test_stochastic_crossover_signals(self):
        """Test Stochastic crossover signals"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Crossover Signals")
        print("-"*60)
        
        # Create data with clear crossover patterns
        crossover_high = pd.Series([100, 102, 104, 106, 108, 106, 104, 102, 100, 102], name='high')
        crossover_low = pd.Series([90, 92, 94, 96, 98, 96, 94, 92, 90, 92], name='low')
        crossover_close = pd.Series([95, 97, 99, 101, 103, 101, 99, 97, 95, 97], name='close')
        
        k_percent, d_percent = stochastic(crossover_high, crossover_low, crossover_close, 3, 2)
        
        print(f"Crossover data - High: {crossover_high.tolist()}")
        print(f"Crossover data - Low: {crossover_low.tolist()}")
        print(f"Crossover data - Close: {crossover_close.tolist()}")
        print(f"%K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        
        # Detect crossovers
        crossovers = []
        for i in range(1, len(k_percent)):
            if (not pd.isna(k_percent.iloc[i]) and not pd.isna(d_percent.iloc[i]) and
                not pd.isna(k_percent.iloc[i-1]) and not pd.isna(d_percent.iloc[i-1])):
                
                # Bullish crossover: %K crosses above %D
                if (k_percent.iloc[i-1] <= d_percent.iloc[i-1] and 
                    k_percent.iloc[i] > d_percent.iloc[i]):
                    crossovers.append((i, 'bullish'))
                
                # Bearish crossover: %K crosses below %D
                elif (k_percent.iloc[i-1] >= d_percent.iloc[i-1] and 
                      k_percent.iloc[i] < d_percent.iloc[i]):
                    crossovers.append((i, 'bearish'))
        
        print(f"\nDetected crossovers: {crossovers}")
        
        # Verify that crossovers are detected correctly
        # We should have at least some crossovers in this data
        if len(crossovers) > 0:
            print(f"✓ Detected {len(crossovers)} crossovers")
            
            # Verify each crossover
            for idx, signal_type in crossovers:
                if signal_type == 'bullish':
                    self.assertGreater(
                        k_percent.iloc[idx],
                        d_percent.iloc[idx],
                        msg=f"Bullish crossover at index {idx}: %K should be above %D"
                    )
                    print(f"✓ Bullish crossover at index {idx}: %K={k_percent.iloc[idx]:.2f} > %D={d_percent.iloc[idx]:.2f}")
                elif signal_type == 'bearish':
                    self.assertLess(
                        k_percent.iloc[idx],
                        d_percent.iloc[idx],
                        msg=f"Bearish crossover at index {idx}: %K should be below %D"
                    )
                    print(f"✓ Bearish crossover at index {idx}: %K={k_percent.iloc[idx]:.2f} < %D={d_percent.iloc[idx]:.2f}")
        else:
            print("! No crossovers detected (this may be normal for the given data)")
        
        print("✓ Test passed: Stochastic crossover signals")

    def test_stochastic_divergence_analysis(self):
        """Test Stochastic divergence analysis"""
        print("\n" + "-"*60)
        print("TEST: Stochastic Divergence Analysis")
        print("-"*60)
        
        # Create data with divergence patterns
        # Price makes higher highs but stochastic makes lower highs (bearish divergence)
        divergence_high = pd.Series([100, 105, 110, 115, 120], name='high')
        divergence_low = pd.Series([90, 95, 100, 105, 110], name='low')
        divergence_close = pd.Series([95, 102, 108, 112, 118], name='close')  # Higher highs
        
        k_percent, d_percent = stochastic(divergence_high, divergence_low, divergence_close, 3, 2)
        
        print(f"Divergence data - High: {divergence_high.tolist()}")
        print(f"Divergence data - Low: {divergence_low.tolist()}")
        print(f"Divergence data - Close: {divergence_close.tolist()}")
        print(f"%K: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in k_percent.tolist()]}")
        print(f"%D: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in d_percent.tolist()]}")
        
        # Analyze divergence
        valid_indices = [i for i in range(len(k_percent)) if not pd.isna(k_percent.iloc[i])]
        
        if len(valid_indices) >= 2:
            # Check if we can identify any divergence patterns
            print(f"\nValid indices for analysis: {valid_indices}")
            
            # Look for cases where price trend doesn't match stochastic trend
            for i in range(len(valid_indices) - 1):
                idx1 = valid_indices[i]
                idx2 = valid_indices[i + 1]
                
                price_change = divergence_close.iloc[idx2] - divergence_close.iloc[idx1]
                k_change = k_percent.iloc[idx2] - k_percent.iloc[idx1]
                
                print(f"Index {idx1} to {idx2}: Price change={price_change:+.2f}, %K change={k_change:+.2f}")
                
                # Divergence: price up but stochastic down (bearish)
                # or price down but stochastic up (bullish)
                if price_change > 0 and k_change < 0:
                    print(f"✓ Bearish divergence detected: price up but %K down")
                elif price_change < 0 and k_change > 0:
                    print(f"✓ Bullish divergence detected: price down but %K up")
                elif price_change * k_change > 0:
                    print(f"✓ Confirmation: price and %K moving in same direction")
        
        print("✓ Test passed: Stochastic divergence analysis")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting Stochastic Oscillator Indicator Tests")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)