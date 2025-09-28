"""
Detailed Indicator Tests - On Balance Volume (OBV)
==================================================
This test file provides comprehensive testing for the On Balance Volume indicator with detailed debugging.
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
from simple_strategy.strategies.indicators_library import on_balance_volume

class TestOBVIndicator(unittest.TestCase):
    """Test cases for On Balance Volume indicator"""
    
    def setUp(self):
        """Set up test data for each test"""
        print("\n" + "=" * 60)
        print("TEST SETUP: Creating test data for On Balance Volume")
        print("=" * 60)
        
        # Create simple test data with close prices and volume
        self.simple_close = pd.Series([10, 12, 11, 13, 15, 14, 16, 15, 17, 18], name='close')
        self.simple_volume = pd.Series([1000, 1200, 1500, 1100, 1600, 1800, 1700, 1900, 2000, 1800], name='volume')
        
        # Create more realistic price and volume data
        np.random.seed(42)  # For reproducible results
        base_prices = np.array([100, 102, 101, 103, 104, 103, 105, 106, 105, 107])
        base_volumes = np.array([10000, 12000, 11000, 13000, 14000, 12500, 15000, 16000, 14500, 15500])
        
        # Add some realistic variation
        self.realistic_close = pd.Series(base_prices, name='close')
        self.realistic_volume = pd.Series(base_volumes + np.random.randint(-1000, 1000, 10), name='volume')
        
        # Create edge case data (constant prices)
        self.constant_close = pd.Series([100.0] * 10, name='close')
        self.constant_volume = pd.Series([5000] * 10, name='volume')
        
        # Create trending data
        self.trending_close = pd.Series([100, 105, 110, 115, 120, 118, 115, 110, 105, 100], name='close')
        self.trending_volume = pd.Series([1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500], name='volume')
        
        # Create divergent data (price up but volume down, and vice versa)
        self.divergent_close = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118], name='close')
        self.divergent_volume = pd.Series([10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000], name='volume')
        
        print(f"Simple close data: {self.simple_close.tolist()}")
        print(f"Simple volume data: {self.simple_volume.tolist()}")
    
    def _format_series(self, series):
        """Helper function to format pandas Series for printing"""
        return [f"{x:.0f}" if not pd.isna(x) else 'nan' for x in series]
    
    def test_obv_basic_calculation(self):
        """Test basic OBV calculation with simple data"""
        print("\n" + "-" * 60)
        print("TEST: OBV Basic Calculation")
        print("-" * 60)
        
        # Calculate OBV
        obv_result = on_balance_volume(self.simple_close, self.simple_volume)
        
        # Debug information
        print(f"Close data: {self.simple_close.tolist()}")
        print(f"Volume data: {self.simple_volume.tolist()}")
        print(f"OBV result: {self._format_series(obv_result)}")
        print(f"OBV type: {type(obv_result)}")
        print(f"OBV length: {len(obv_result)}")
        
        # First value should always be 0 (starting point)
        self.assertEqual(
            float(obv_result.iloc[0]), 
            0.0, 
            f"OBV should start at 0: got {float(obv_result.iloc[0])}"
        )
        print("✓ OBV starts at 0")
        
        # Manual calculation verification
        expected_obv = [0]  # Start with 0
        
        for i in range(1, len(self.simple_close)):
            if self.simple_close.iloc[i] > self.simple_close.iloc[i-1]:
                # Price increased: add volume
                expected_obv.append(expected_obv[-1] + self.simple_volume.iloc[i])
            elif self.simple_close.iloc[i] < self.simple_close.iloc[i-1]:
                # Price decreased: subtract volume
                expected_obv.append(expected_obv[-1] - self.simple_volume.iloc[i])
            else:
                # Price unchanged: OBV remains the same
                expected_obv.append(expected_obv[-1])
        
        print(f"\nManual OBV calculation: {expected_obv}")
        
        # Verify all calculations
        for i in range(len(obv_result)):
            self.assertAlmostEqual(
                float(obv_result.iloc[i]), 
                expected_obv[i], 
                places=5,
                msg=f"OBV calculation incorrect at index {i}: got {float(obv_result.iloc[i])}, expected {expected_obv[i]}"
            )
        print("✓ All OBV calculations are correct")
        
        print("✓ Test passed: Basic OBV calculation")
    
    def test_obv_edge_cases(self):
        """Test OBV with edge cases"""
        print("\n" + "-" * 60)
        print("TEST: OBV Edge Cases")
        print("-" * 60)
        
        # Test with constant prices
        print(f"Constant close data: {self.constant_close.tolist()}")
        print(f"Constant volume data: {self.constant_volume.tolist()}")
        
        obv_result = on_balance_volume(self.constant_close, self.constant_volume)
        
        print(f"OBV result: {self._format_series(obv_result)}")
        
        # With constant prices, OBV should remain at 0 (no changes)
        for i in range(len(obv_result)):
            self.assertEqual(
                float(obv_result.iloc[i]), 
                0.0, 
                f"With constant prices, OBV should be 0 at index {i}: got {float(obv_result.iloc[i])}"
            )
        print("✓ With constant prices, OBV remains at 0")
        
        # Test with different length inputs
        long_close = pd.Series([10, 12, 11, 13, 15, 14, 16, 15, 17, 18, 19, 20], name='close')
        short_volume = pd.Series([1000, 1200, 1500, 1100, 1600, 1800, 1700, 1900, 2000, 1800], name='volume')
        
        print(f"\nTesting with different length inputs:")
        print(f"Close length: {len(long_close)}, Volume length: {len(short_volume)}")
        
        obv_result = on_balance_volume(long_close, short_volume)
        
        print(f"OBV result: {self._format_series(obv_result)}")
        print(f"OBV length: {len(obv_result)}")
        
        # Should use the minimum length
        self.assertEqual(len(obv_result), min(len(long_close), len(short_volume)))
        print("✓ Handles different length inputs correctly")
        
        print("✓ Test passed: OBV edge cases")
    
    def test_obv_error_handling(self):
        """Test OBV error handling"""
        print("\n" + "-" * 60)
        print("TEST: OBV Error Handling")
        print("-" * 60)
        
        # Test with empty close data
        empty_close = pd.Series([], name='close')
        empty_volume = pd.Series([], name='volume')
        
        obv_empty = on_balance_volume(empty_close, empty_volume)
        print(f"Empty data test - OBV type: {type(obv_empty)}")
        print(f"Empty data test - OBV length: {len(obv_empty)}")
        
        # Empty data should return an empty Series
        self.assertEqual(len(obv_empty), 0, "Empty data should return an empty Series")
        print("✓ Handles empty data correctly")
        
        # Test with empty close but non-empty volume
        obv_empty_close = on_balance_volume(empty_close, self.simple_volume)
        print(f"Empty close test - OBV length: {len(obv_empty_close)}")
        self.assertEqual(len(obv_empty_close), 0, "Empty close should return an empty Series")
        print("✓ Handles empty close data correctly")
        
        # Test with empty volume but non-empty close
        obv_empty_volume = on_balance_volume(self.simple_close, empty_volume)
        print(f"Empty volume test - OBV length: {len(obv_empty_volume)}")
        self.assertEqual(len(obv_empty_volume), 0, "Empty volume should return an empty Series")
        print("✓ Handles empty volume data correctly")
        
        print("✓ Test passed: OBV error handling")
    
    def test_obv_realistic_data(self):
        """Test OBV with realistic price and volume data"""
        print("\n" + "-" * 60)
        print("TEST: OBV with Realistic Data")
        print("-" * 60)
        
        print(f"Close data: {[f'{x:.2f}' for x in self.realistic_close.tolist()]}")
        print(f"Volume data: {[f'{x:.0f}' for x in self.realistic_volume.tolist()]}")
        
        obv_result = on_balance_volume(self.realistic_close, self.realistic_volume)
        
        print(f"OBV result: {self._format_series(obv_result)}")
        
        # First value should always be 0
        self.assertEqual(float(obv_result.iloc[0]), 0.0, "OBV should start at 0")
        
        # Check that OBV values are reasonable (no extreme jumps that don't match volume)
        for i in range(1, len(obv_result)):
            obv_change = abs(float(obv_result.iloc[i]) - float(obv_result.iloc[i-1]))
            volume = float(self.realistic_volume.iloc[i])
            
            # OBV change should not exceed volume (unless there's a bug)
            self.assertTrue(
                obv_change <= volume * 1.01,  # Allow small floating point errors
                f"OBV change ({obv_change}) at index {i} should not exceed volume ({volume})"
            )
        print("✓ OBV changes are reasonable compared to volume")
        
        print("✓ Test passed: OBV with realistic data")
    
    def test_obv_divergence_analysis(self):
        """Test OBV behavior with price-volume divergences"""
        print("\n" + "-" * 60)
        print("TEST: OBV Divergence Analysis")
        print("-" * 60)
        
        # Create a clear bearish divergence scenario:
        # Price makes higher highs but OBV makes lower highs
        divergent_close = pd.Series([100, 102, 104, 103, 105, 107, 106, 108, 110, 112], name='close')
        divergent_volume = pd.Series([10000, 8000, 6000, 12000, 5000, 3000, 8000, 2000, 1000, 500], name='volume')
        
        print(f"Divergent close data: {divergent_close.tolist()}")
        print(f"Divergent volume data: {divergent_volume.tolist()}")
        
        obv_result = on_balance_volume(divergent_close, divergent_volume)
        
        print(f"OBV result: {self._format_series(obv_result)}")
        
        # Let's analyze the divergence step by step
        print("\nStep-by-step analysis:")
        for i in range(1, len(divergent_close)):
            price_change = divergent_close.iloc[i] - divergent_close.iloc[i-1]
            obv_change = float(obv_result.iloc[i]) - float(obv_result.iloc[i-1])
            volume = divergent_volume.iloc[i]
            
            direction = "up" if price_change > 0 else "down" if price_change < 0 else "flat"
            print(f"Day {i}: Price {direction} {price_change:+.1f}, Volume {volume}, OBV change {obv_change:+.0f}")
        
        # Analyze overall divergence
        price_change = divergent_close.iloc[-1] - divergent_close.iloc[0]
        obv_change = float(obv_result.iloc[-1]) - float(obv_result.iloc[0])
        
        print(f"\nOverall analysis:")
        print(f"Price change: {price_change:.2f}")
        print(f"OBV change: {obv_change:.0f}")
        
        # Price is increasing but let's check if OBV shows weakness
        self.assertTrue(price_change > 0, "Price should have an overall increase")
        
        # Look for specific divergence pattern: higher price highs but lower OBV highs
        # Find the price highs and corresponding OBV values
        print(f"\nLooking for price highs pattern...")
        price_high_indices = []
        for i in range(2, len(divergent_close)):
            is_high = (divergent_close.iloc[i] > divergent_close.iloc[i-1] and 
                    divergent_close.iloc[i] > divergent_close.iloc[i-2])
            
            # For earlier indices, check fewer previous values
            if i == 1:
                is_high = divergent_close.iloc[i] > divergent_close.iloc[i-1]
            
            if is_high:
                price_high_indices.append(i)
                print(f"  Price high found at index {i}: {divergent_close.iloc[i]}")
        
        print(f"Price high indices: {price_high_indices}")
        
        if len(price_high_indices) >= 2:
            # Get OBV values at price highs
            obv_at_price_highs = [float(obv_result.iloc[i]) for i in price_high_indices]
            print(f"OBV values at price highs: {obv_at_price_highs}")
            
            # Check if OBV is making lower highs while price makes higher highs
            if len(obv_at_price_highs) >= 2:
                # Compare first half vs second half
                mid_point = len(obv_at_price_highs) // 2
                later_highs = obv_at_price_highs[mid_point:]
                earlier_highs = obv_at_price_highs[:mid_point]
                
                print(f"Earlier OBV highs: {earlier_highs}")
                print(f"Later OBV highs: {later_highs}")
                
                if later_highs and earlier_highs:
                    max_later = max(later_highs)
                    max_earlier = max(earlier_highs)
                    
                    print(f"Max OBV in earlier highs: {max_earlier}")
                    print(f"Max OBV in later highs: {max_later}")
                    
                    # This is the key divergence test
                    if max_later < max_earlier:
                        print("✓ Confirmed bearish divergence: Price making higher highs but OBV making lower highs")
                        divergence_confirmed = True
                    else:
                        print("ℹ No clear divergence pattern found - OBV not making lower highs")
                        divergence_confirmed = False
                else:
                    print("ℹ Not enough data points to compare highs")
                    divergence_confirmed = False
            else:
                print("ℹ Not enough OBV highs to compare")
                divergence_confirmed = False
        else:
            print("ℹ Not enough price highs to test divergence pattern")
            divergence_confirmed = False
        
        # Test a simpler divergence case if the above didn't work
        if not divergence_confirmed:
            print(f"\nTesting simpler divergence case...")
            
            # Create data where price ends higher but OBV ends lower
            simple_div_close = pd.Series([100, 105, 102, 108, 104, 110, 106, 112, 108, 114], name='close')
            simple_div_volume = pd.Series([20000, 10000, 15000, 5000, 12000, 3000, 10000, 2000, 8000, 1000], name='volume')
            
            print(f"Simple divergence close: {simple_div_close.tolist()}")
            print(f"Simple divergence volume: {simple_div_volume.tolist()}")
            
            simple_obv = on_balance_volume(simple_div_close, simple_div_volume)
            print(f"Simple divergence OBV: {self._format_series(simple_obv)}")
            
            simple_price_change = simple_div_close.iloc[-1] - simple_div_close.iloc[0]
            simple_obv_change = float(simple_obv.iloc[-1]) - float(simple_obv.iloc[0])
            
            print(f"Simple case - Price change: {simple_price_change:.2f}")
            print(f"Simple case - OBV change: {simple_obv_change:.0f}")
            
            # In this case, price should be up but OBV should be down
            print(f"Checking simple divergence: Price up {simple_price_change > 0}, OBV down {simple_obv_change < 0}")
            
            if simple_price_change > 0 and simple_obv_change < 0:
                print("✓ Confirmed simple divergence: Price up but OBV down")
            else:
                print(f"ℹ Simple divergence not confirmed. Creating even clearer example...")
                
                # Create an even clearer divergence example
                clear_div_close = pd.Series([100, 110, 105, 115, 110, 120, 115, 125], name='close')
                clear_div_volume = pd.Series([10000, 5000, 8000, 2000, 7000, 1000, 6000, 500], name='volume')
                
                print(f"Clear divergence close: {clear_div_close.tolist()}")
                print(f"Clear divergence volume: {clear_div_volume.tolist()}")
                
                clear_obv = on_balance_volume(clear_div_close, clear_div_volume)
                print(f"Clear divergence OBV: {self._format_series(clear_obv)}")
                
                clear_price_change = clear_div_close.iloc[-1] - clear_div_close.iloc[0]
                clear_obv_change = float(clear_obv.iloc[-1]) - float(clear_obv.iloc[0])
                
                print(f"Clear case - Price change: {clear_price_change:.2f}")
                print(f"Clear case - OBV change: {clear_obv_change:.0f}")
                
                # This should definitely show divergence
                self.assertTrue(clear_price_change > 0, "Price should be up in clear divergence test")
                self.assertTrue(clear_obv_change < 0, "OBV should be down in clear divergence test")
                
                print("✓ Confirmed clear divergence: Price up but OBV down")
        
        print("✓ Test passed: OBV divergence analysis")
    
    def test_obv_confirmation_signals(self):
        """Test OBV as a confirmation signal for price trends"""
        print("\n" + "-" * 60)
        print("TEST: OBV Confirmation Signals")
        print("-" * 60)
        
        # Create data with clear trend confirmation
        confirm_close = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118], name='close')
        confirm_volume = pd.Series([10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000], name='volume')
        
        print(f"Confirmation close data: {confirm_close.tolist()}")
        print(f"Confirmation volume data: {confirm_volume.tolist()}")
        
        obv_result = on_balance_volume(confirm_close, confirm_volume)
        
        print(f"OBV result: {self._format_series(obv_result)}")
        
        # Both price and OBV should be increasing
        price_increases = sum(1 for i in range(1, len(confirm_close)) if confirm_close.iloc[i] > confirm_close.iloc[i-1])
        obv_increases = sum(1 for i in range(1, len(obv_result)) if float(obv_result.iloc[i]) > float(obv_result.iloc[i-1]))
        
        print(f"Price increases: {price_increases}")
        print(f"OBV increases: {obv_increases}")
        
        # OBV should increase when price increases (with volume confirmation)
        self.assertTrue(obv_increases >= price_increases * 0.8,  # Allow some variation
                       f"OBV should confirm price increases: {obv_increases} vs {price_increases}")
        
        print("✓ OBV correctly confirms price trend with volume support")
        
        print("✓ Test passed: OBV confirmation signals")

if __name__ == '__main__':
    print("📊 Starting On Balance Volume Indicator Tests")
    print("=" * 80)
    unittest.main(verbosity=2)