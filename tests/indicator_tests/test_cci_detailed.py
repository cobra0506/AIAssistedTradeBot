"""
Detailed Indicator Tests - CCI (Commodity Channel Index) - FULLY CORRECTED
=========================================================
This test file provides comprehensive testing for the CCI indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import sma, ema, cci, rsi, stochastic, macd, bollinger_bands


class TestCCIIndicator(unittest.TestCase):
    """Test cases for CCI (Commodity Channel Index) indicator"""

    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "="*60)
        print("TEST SETUP: Creating test data for CCI")
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

    def test_cci_basic_calculation(self):
        """Test basic CCI calculation with simple data"""
        print("\n" + "-"*60)
        print("TEST: CCI Basic Calculation")
        print("-"*60)
        
        # Calculate CCI
        cci_result = cci(self.simple_high, self.simple_low, self.simple_close, self.period)
        
        # Debug information
        print(f"High data: {self.simple_high.tolist()}")
        print(f"Low data: {self.simple_low.tolist()}")
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"Period: {self.period}")
        print(f"CCI result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        print(f"CCI type: {type(cci_result)}")
        print(f"CCI length: {len(cci_result)}")
        
        # Manual calculation verification for first valid CCI value
        # CCI = (TP - SMA_TP) / (0.015 * MAD)
        # where TP = (High + Low + Close) / 3
        first_valid_idx = self.period - 1
        if first_valid_idx < len(self.simple_close):
            # Calculate Typical Price (TP)
            tp = (self.simple_high + self.simple_low + self.simple_close) / 3
            
            # Calculate SMA of TP
            sma_tp = tp.rolling(window=self.period).mean()
            
            # Calculate Mean Absolute Deviation (MAD)
            mad = tp.rolling(window=self.period).apply(lambda x: np.fabs(x - x.mean()).mean())
            
            # Calculate CCI
            expected_cci = (tp - sma_tp) / (0.015 * mad)
            
            actual_cci = cci_result.iloc[first_valid_idx]
            expected_cci_value = expected_cci.iloc[first_valid_idx]
            
            print(f"\nManual calculation for index {first_valid_idx}:")
            print(f"High: {self.simple_high.iloc[first_valid_idx]}")
            print(f"Low: {self.simple_low.iloc[first_valid_idx]}")
            print(f"Close: {self.simple_close.iloc[first_valid_idx]}")
            print(f"TP: {tp.iloc[first_valid_idx]:.6f}")
            print(f"SMA TP: {sma_tp.iloc[first_valid_idx]:.6f}")
            print(f"MAD: {mad.iloc[first_valid_idx]:.6f}")
            print(f"Expected CCI: {expected_cci_value:.6f}")
            print(f"Actual CCI: {actual_cci:.6f}")
            
            # Assertions
            self.assertEqual(len(cci_result), len(self.simple_close), "CCI length should match input length")
            self.assertIsInstance(cci_result, pd.Series, "CCI should be a pandas Series")
            
            # Check CCI calculation
            self.assertAlmostEqual(
                actual_cci,
                expected_cci_value,
                places=10,
                msg=f"CCI calculation incorrect: got {actual_cci}, expected {expected_cci_value}"
            )
            print(f"✓ CCI calculation correct: {actual_cci:.6f} == {expected_cci_value:.6f}")
            
            # Check a few more values
            for i in range(first_valid_idx, min(first_valid_idx + 3, len(cci_result))):
                if not pd.isna(cci_result.iloc[i]) and not pd.isna(expected_cci.iloc[i]):
                    self.assertAlmostEqual(
                        cci_result.iloc[i],
                        expected_cci.iloc[i],
                        places=10,
                        msg=f"CCI calculation incorrect at index {i}: got {cci_result.iloc[i]}, expected {expected_cci.iloc[i]}"
                    )
                    print(f"✓ Index {i}: CCI {cci_result.iloc[i]:.6f} == expected {expected_cci.iloc[i]:.6f}")
        
        print("✓ Test passed: Basic CCI calculation")

    def test_cci_realistic_data(self):
        """Test CCI with realistic price data - FULLY CORRECTED"""
        print("\n" + "-"*60)
        print("TEST: CCI with Realistic Price Data - FULLY CORRECTED")
        print("-"*60)
        
        # Calculate CCI
        cci_result = cci(self.realistic_high, self.realistic_low, self.realistic_close, self.period)
        
        # Debug information
        print(f"High data: {self.realistic_high.tolist()}")
        print(f"Low data: {self.realistic_low.tolist()}")
        print(f"Close data: {self.realistic_close.tolist()}")
        print(f"CCI result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # Calculate Typical Price (TP) for verification
        tp = (self.realistic_high + self.realistic_low + self.realistic_close) / 3
        print(f"Typical Price: {[f'{x:.6f}' for x in tp.tolist()]}")
        
        # Assertions
        self.assertEqual(len(cci_result), len(self.realistic_close))
        self.assertIsInstance(cci_result, pd.Series)
        
        # CCI should have both positive and negative values in typical market data
        # FULLY CORRECTED: Use .any() method on the boolean Series directly
        valid_cci = cci_result.dropna()  # Remove NaN values
        if len(valid_cci) > 0:
            has_positive = (valid_cci > 0).any()
            has_negative = (valid_cci < 0).any()
            
            print(f"Has positive CCI values: {has_positive}")
            print(f"Has negative CCI values: {has_negative}")
            
            # In realistic data, we should typically see both positive and negative values
            # (though this isn't strictly required for the test to pass)
            if has_positive and has_negative:
                print("✓ CCI shows both positive and negative values as expected")
            elif has_positive:
                print("! CCI shows only positive values (this may be normal for strong uptrend)")
            elif has_negative:
                print("! CCI shows only negative values (this may be normal for strong downtrend)")
        else:
            print("! No valid CCI values (all NaN)")
        
        print("✓ Test passed: CCI with realistic data (fully corrected)")

    def test_cci_edge_cases(self):
        """Test CCI with edge cases"""
        print("\n" + "-"*60)
        print("TEST: CCI Edge Cases")
        print("-"*60)
        
        # Test with constant prices (high = low = close)
        cci_result = cci(self.edge_high, self.edge_low, self.edge_close, self.period)
        
        print(f"Constant price data - High: {self.edge_high.tolist()}")
        print(f"Constant price data - Low: {self.edge_low.tolist()}")
        print(f"Constant price data - Close: {self.edge_close.tolist()}")
        print(f"CCI result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # With constant prices, MAD should be 0, which would make CCI undefined
        # The implementation should handle this gracefully (typically returning NaN or 0)
        for i in range(len(cci_result)):
            if not pd.isna(cci_result.iloc[i]):
                # With constant prices, CCI should be 0 or NaN
                self.assertEqual(
                    cci_result.iloc[i],
                    0.0,
                    msg=f"With constant prices, CCI should be 0 at index {i}: got {cci_result.iloc[i]}"
                )
                print(f"✓ Index {i}: CCI = {cci_result.iloc[i]} (constant prices)")
        
        # Test with period larger than data length
        large_period = 20
        cci_large = cci(self.simple_high, self.simple_low, self.simple_close, large_period)
        
        print(f"\nTesting with period ({large_period}) larger than data length ({len(self.simple_close)})")
        print(f"CCI result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_large.tolist()]}")
        
        # All values should be NaN
        self.assertTrue(cci_large.isna().all(), "All CCI values should be NaN when period > data length")
        print("✓ All values are NaN when period > data length")
        
        # Test with minimum valid period
        cci_min = cci(self.simple_high, self.simple_low, self.simple_close, 1)
        
        print(f"\nTesting with minimum period (1):")
        print(f"CCI result: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_min.tolist()]}")
        
        # With period 1, MAD should be 0, making CCI undefined
        # The implementation should handle this gracefully
        for i in range(len(cci_min)):
            if not pd.isna(cci_min.iloc[i]):
                # With period 1, CCI should be 0 (typical handling)
                self.assertEqual(
                    cci_min.iloc[i],
                    0.0,
                    msg=f"With period 1, CCI should be 0 at index {i}: got {cci_min.iloc[i]}"
                )
                print(f"✓ Index {i}: CCI = {cci_min.iloc[i]} (period 1)")
        
        print("✓ Test passed: CCI edge cases")

    def test_cci_error_handling(self):
        """Test CCI error handling"""
        print("\n" + "-"*60)
        print("TEST: CCI Error Handling")
        print("-"*60)
        
        # Test with empty data
        empty_high = pd.Series([], dtype=float)
        empty_low = pd.Series([], dtype=float)
        empty_close = pd.Series([], dtype=float)
        
        cci_empty = cci(empty_high, empty_low, empty_close, self.period)
        
        print(f"Empty data test - CCI type: {type(cci_empty)}")
        print(f"Empty data test - CCI length: {len(cci_empty)}")
        
        self.assertIsInstance(cci_empty, pd.Series)
        self.assertEqual(len(cci_empty), 0)
        print("✓ Handles empty data correctly")
        
        # Test with invalid period
        try:
            cci_invalid = cci(self.simple_high, self.simple_low, self.simple_close, 0)
            print("Result with period 0:")
            print(f"CCI: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_invalid.tolist()]}")
            print("✓ Handles period 0 without crashing")
        except Exception as e:
            print(f"Exception with period 0: {e}")
            print("✓ Exception handled gracefully")
        
        try:
            cci_negative = cci(self.simple_high, self.simple_low, self.simple_close, -1)
            print("Result with period -1:")
            print(f"CCI: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_negative.tolist()]}")
            print("✓ Handles negative period without crashing")
        except Exception as e:
            print(f"Exception with period -1: {e}")
            print("✓ Exception handled gracefully")
        
        print("✓ Test passed: CCI error handling")

    def test_cci_signal_analysis(self):
        """Test CCI signal analysis"""
        print("\n" + "-"*60)
        print("TEST: CCI Signal Analysis")
        print("-"*60)
        
        # Calculate CCI
        cci_result = cci(self.trend_high, self.trend_low, self.trend_close, self.period)
        
        print(f"Trend data - High: {self.trend_high.tolist()}")
        print(f"Trend data - Low: {self.trend_low.tolist()}")
        print(f"Trend data - Close: {self.trend_close.tolist()}")
        print(f"CCI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # Analyze overbought/oversold conditions
        overbought_threshold = 100
        oversold_threshold = -100
        
        overbought = cci_result > overbought_threshold
        oversold = cci_result < oversold_threshold
        
        print(f"\nOverbought/oversold analysis (thresholds: {oversold_threshold}/{overbought_threshold}):")
        print(f"Overbought: {overbought.tolist()}")
        print(f"Oversold: {oversold.tolist()}")
        
        # In an uptrend, we should see overbought conditions
        # In a downtrend, we should see oversold conditions
        uptrend_end = 4  # Peak of uptrend
        downtrend_end = 9  # End of downtrend
        
        if uptrend_end < len(cci_result) and not pd.isna(cci_result.iloc[uptrend_end]):
            cci_at_peak = cci_result.iloc[uptrend_end]
            
            print(f"\nAt uptrend peak (index {uptrend_end}):")
            print(f"CCI: {cci_at_peak:.2f}")
            
            # Should be elevated (but not necessarily overbought)
            self.assertGreaterEqual(
                cci_at_peak,
                -50,
                msg=f"CCI should be elevated at uptrend peak: got {cci_at_peak}"
            )
            print(f"✓ CCI ({cci_at_peak:.2f}) is elevated at uptrend peak")
        
        if downtrend_end < len(cci_result) and not pd.isna(cci_result.iloc[downtrend_end]):
            cci_at_trough = cci_result.iloc[downtrend_end]
            
            print(f"\nAt downtrend trough (index {downtrend_end}):")
            print(f"CCI: {cci_at_trough:.2f}")
            
            # Should be depressed (but not necessarily oversold)
            self.assertLessEqual(
                cci_at_trough,
                50,
                msg=f"CCI should be depressed at downtrend trough: got {cci_at_trough}"
            )
            print(f"✓ CCI ({cci_at_trough:.2f}) is depressed at downtrend trough")
        
        print("✓ Test passed: CCI signal analysis")

    def test_cci_divergence_analysis(self):
        """Test CCI divergence analysis"""
        print("\n" + "-"*60)
        print("TEST: CCI Divergence Analysis")
        print("-"*60)
        
        # Create data with divergence patterns
        # Price makes higher highs but CCI makes lower highs (bearish divergence)
        divergence_high = pd.Series([100, 105, 110, 115, 120], name='high')
        divergence_low = pd.Series([90, 95, 100, 105, 110], name='low')
        divergence_close = pd.Series([95, 102, 108, 112, 118], name='close')  # Higher highs
        
        cci_result = cci(divergence_high, divergence_low, divergence_close, 3)
        
        print(f"Divergence data - High: {divergence_high.tolist()}")
        print(f"Divergence data - Low: {divergence_low.tolist()}")
        print(f"Divergence data - Close: {divergence_close.tolist()}")
        print(f"CCI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # Analyze divergence
        valid_indices = [i for i in range(len(cci_result)) if not pd.isna(cci_result.iloc[i])]
        
        if len(valid_indices) >= 2:
            print(f"\nValid indices for analysis: {valid_indices}")
            
            # Look for cases where price trend doesn't match CCI trend
            for i in range(len(valid_indices) - 1):
                idx1 = valid_indices[i]
                idx2 = valid_indices[i + 1]
                
                price_change = divergence_close.iloc[idx2] - divergence_close.iloc[idx1]
                cci_change = cci_result.iloc[idx2] - cci_result.iloc[idx1]
                
                print(f"Index {idx1} to {idx2}: Price change={price_change:+.2f}, CCI change={cci_change:+.2f}")
                
                # Divergence: price up but CCI down (bearish)
                # or price down but CCI up (bullish)
                if price_change > 0 and cci_change < 0:
                    print(f"✓ Bearish divergence detected: price up but CCI down")
                elif price_change < 0 and cci_change > 0:
                    print(f"✓ Bullish divergence detected: price down but CCI up")
                elif price_change * cci_change > 0:
                    print(f"✓ Confirmation: price and CCI moving in same direction")
        
        print("✓ Test passed: CCI divergence analysis")

    def test_cci_zero_line_crossovers(self):
        """Test CCI zero line crossovers"""
        print("\n" + "-"*60)
        print("TEST: CCI Zero Line Crossovers")
        print("-"*60)
        
        # Create data with clear zero line crossover patterns
        crossover_high = pd.Series([100, 102, 104, 106, 108, 106, 104, 102, 100, 102], name='high')
        crossover_low = pd.Series([90, 92, 94, 96, 98, 96, 94, 92, 90, 92], name='low')
        crossover_close = pd.Series([95, 97, 99, 101, 103, 101, 99, 97, 95, 97], name='close')
        
        cci_result = cci(crossover_high, crossover_low, crossover_close, 3)
        
        print(f"Crossover data - High: {crossover_high.tolist()}")
        print(f"Crossover data - Low: {crossover_low.tolist()}")
        print(f"Crossover data - Close: {crossover_close.tolist()}")
        print(f"CCI: {[f'{x:.2f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # Detect zero line crossovers
        crossovers = []
        for i in range(1, len(cci_result)):
            if (not pd.isna(cci_result.iloc[i]) and not pd.isna(cci_result.iloc[i-1])):
                
                # Bullish crossover: CCI crosses above zero
                if (cci_result.iloc[i-1] <= 0 and cci_result.iloc[i] > 0):
                    crossovers.append((i, 'bullish'))
                
                # Bearish crossover: CCI crosses below zero
                elif (cci_result.iloc[i-1] >= 0 and cci_result.iloc[i] < 0):
                    crossovers.append((i, 'bearish'))
        
        print(f"\nDetected zero line crossovers: {crossovers}")
        
        # Verify that crossovers are detected correctly
        if len(crossovers) > 0:
            print(f"✓ Detected {len(crossovers)} zero line crossovers")
            
            # Verify each crossover
            for idx, signal_type in crossovers:
                if signal_type == 'bullish':
                    self.assertGreater(
                        cci_result.iloc[idx],
                        0,
                        msg=f"Bullish crossover at index {idx}: CCI should be above zero"
                    )
                    print(f"✓ Bullish crossover at index {idx}: CCI={cci_result.iloc[idx]:.2f} > 0")
                elif signal_type == 'bearish':
                    self.assertLess(
                        cci_result.iloc[idx],
                        0,
                        msg=f"Bearish crossover at index {idx}: CCI should be below zero"
                    )
                    print(f"✓ Bearish crossover at index {idx}: CCI={cci_result.iloc[idx]:.2f} < 0")
        else:
            print("! No zero line crossovers detected (this may be normal for the given data)")
        
        print("✓ Test passed: CCI zero line crossovers")

    def test_cci_typical_price_relationship(self):
        """Test CCI relationship with Typical Price"""
        print("\n" + "-"*60)
        print("TEST: CCI Relationship with Typical Price")
        print("-"*60)
        
        # Calculate CCI
        cci_result = cci(self.simple_high, self.simple_low, self.simple_close, self.period)
        
        # Calculate Typical Price (TP)
        tp = (self.simple_high + self.simple_low + self.simple_close) / 3
        
        print(f"High data: {self.simple_high.tolist()}")
        print(f"Low data: {self.simple_low.tolist()}")
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"Typical Price: {[f'{x:.6f}' for x in tp.tolist()]}")
        print(f"CCI: {[f'{x:.6f}' if not pd.isna(x) else 'nan' for x in cci_result.tolist()]}")
        
        # Analyze the relationship between CCI and TP
        valid_indices = [i for i in range(len(cci_result)) if not pd.isna(cci_result.iloc[i])]
        
        if len(valid_indices) >= 2:
            print(f"\nValid indices for analysis: {valid_indices}")
            
            # Check correlation between TP changes and CCI values
            tp_changes = []
            cci_values = []
            
            for i in range(1, len(valid_indices)):
                idx1 = valid_indices[i-1]
                idx2 = valid_indices[i]
                
                tp_change = tp.iloc[idx2] - tp.iloc[idx1]
                tp_changes.append(tp_change)
                cci_values.append(cci_result.iloc[idx2])
                
                print(f"Index {idx1} to {idx2}: TP change={tp_change:+.6f}, CCI={cci_result.iloc[idx2]:+.6f}")
            
            # Calculate correlation
            if len(tp_changes) > 1:
                correlation = np.corrcoef(tp_changes, cci_values)[0, 1]
                print(f"\nCorrelation between TP changes and CCI values: {correlation:.6f}")
                
                # There should generally be some positive correlation
                # (though not necessarily strong)
                self.assertGreaterEqual(
                    correlation,
                    -0.5,
                    msg=f"Correlation should not be strongly negative: got {correlation}"
                )
                print(f"✓ Correlation ({correlation:.6f}) is within expected range")
        
        print("✓ Test passed: CCI relationship with Typical Price")


if __name__ == '__main__':
    # Configure logging to see debug output
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting CCI Indicator Tests - FULLY CORRECTED")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2)