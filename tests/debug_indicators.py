"""
Debug test for indicator calculation
This test focuses specifically on checking if indicators are calculated correctly
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.strategies.indicators_library import rsi, sma
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover

class TestIndicatorCalculation(unittest.TestCase):
    """Test class specifically for debugging indicator calculation"""
    
    def setUp(self):
        """Set up test data"""
        # Create simple test data
        np.random.seed(42)  # For reproducible results
        
        # Generate 100 price points
        base_price = 20000.0
        prices = [base_price]
        
        for i in range(99):
            # Random walk with slight upward trend
            change = np.random.normal(0, 0.01)  # 1% standard deviation
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Create DataFrame
        timestamps = [datetime(2023, 1, 1, 0, 0) + timedelta(minutes=i) for i in range(100)]
        
        self.test_data = pd.DataFrame({
            'timestamp': [int(t.timestamp() * 1000) for t in timestamps],
            'datetime': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
            'open': prices,
            'high': [p * 1.005 for p in prices],  # High is 0.5% above open
            'low': [p * 0.995 for p in prices],   # Low is 0.5% below open
            'close': prices,
            'volume': [np.random.randint(100, 1000) for _ in range(100)]
        })
        
        print(f"🔧 Created test data with {len(self.test_data)} rows")
        print(f"🔧 Price range: {min(prices):.2f} to {max(prices):.2f}")
    
    def test_rsi_calculation(self):
        """Test if RSI indicator calculates correctly"""
        print("\n🧪 Testing RSI calculation...")
        
        try:
            # Calculate RSI
            rsi_result = rsi(self.test_data['close'], period=14)
            
            print(f"🔧 RSI result type: {type(rsi_result)}")
            print(f"🔧 RSI result length: {len(rsi_result) if hasattr(rsi_result, '__len__') else 'N/A'}")
            
            if hasattr(rsi_result, 'iloc'):
                print(f"🔧 RSI first 5 values: {rsi_result.head().tolist()}")
                print(f"🔧 RSI last 5 values: {rsi_result.tail().tolist()}")
                
                # Check for NaN values
                nan_count = rsi_result.isna().sum()
                print(f"🔧 RSI NaN count: {nan_count}")
                
                # Check if we have valid values
                valid_count = rsi_result.notna().sum()
                print(f"🔧 RSI valid count: {valid_count}")
                
                if valid_count > 0:
                    last_valid_value = rsi_result[rsi_result.notna()].iloc[-1]
                    print(f"🔧 RSI last valid value: {last_valid_value}")
                    
                    # RSI should be between 0 and 100
                    self.assertGreaterEqual(last_valid_value, 0, "RSI should be >= 0")
                    self.assertLessEqual(last_valid_value, 100, "RSI should be <= 100")
                    print("✅ RSI calculation test PASSED")
                else:
                    self.fail("RSI has no valid values")
            else:
                print(f"🔧 RSI result: {rsi_result}")
                self.fail("RSI result is not a pandas Series")
                
        except Exception as e:
            print(f"❌ RSI calculation test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_sma_calculation(self):
        """Test if SMA indicator calculates correctly"""
        print("\n🧪 Testing SMA calculation...")
        
        try:
            # Calculate SMA
            sma_result = sma(self.test_data['close'], period=20)
            
            print(f"🔧 SMA result type: {type(sma_result)}")
            print(f"🔧 SMA result length: {len(sma_result) if hasattr(sma_result, '__len__') else 'N/A'}")
            
            if hasattr(sma_result, 'iloc'):
                print(f"🔧 SMA first 5 values: {sma_result.head().tolist()}")
                print(f"🔧 SMA last 5 values: {sma_result.tail().tolist()}")
                
                # Check for NaN values
                nan_count = sma_result.isna().sum()
                print(f"🔧 SMA NaN count: {nan_count}")
                
                # Check if we have valid values
                valid_count = sma_result.notna().sum()
                print(f"🔧 SMA valid count: {valid_count}")
                
                if valid_count > 0:
                    last_valid_value = sma_result[sma_result.notna()].iloc[-1]
                    print(f"🔧 SMA last valid value: {last_valid_value}")
                    
                    # SMA should be close to the average of recent prices
                    recent_prices = self.test_data['close'].tail(20).mean()
                    print(f"🔧 Recent price average: {recent_prices}")
                    
                    # Check if SMA is reasonable
                    self.assertGreater(last_valid_value, 0, "SMA should be > 0")
                    print("✅ SMA calculation test PASSED")
                else:
                    self.fail("SMA has no valid values")
            else:
                print(f"🔧 SMA result: {sma_result}")
                self.fail("SMA result is not a pandas Series")
                
        except Exception as e:
            print(f"❌ SMA calculation test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_signal_generation(self):
        """Test if signals are generated correctly from indicators"""
        print("\n🧪 Testing signal generation...")
        
        try:
            # Calculate indicators
            rsi_result = rsi(self.test_data['close'], period=14)
            sma_short = sma(self.test_data['close'], period=10)
            sma_long = sma(self.test_data['close'], period=30)
            
            # Generate signals
            rsi_signal = overbought_oversold(rsi_result, overbought=70, oversold=30)
            ma_signal = ma_crossover(sma_short, sma_long)
            
            print(f"🔧 RSI signal type: {type(rsi_signal)}")
            print(f"🔧 RSI signal unique values: {rsi_signal.unique()}")
            print(f"🔧 RSI signal value counts: {rsi_signal.value_counts().to_dict()}")
            
            print(f"🔧 MA signal type: {type(ma_signal)}")
            print(f"🔧 MA signal unique values: {ma_signal.unique()}")
            print(f"🔧 MA signal value counts: {ma_signal.value_counts().to_dict()}")
            
            # Check if signals are valid
            valid_rsi_signals = set(rsi_signal.unique())
            valid_ma_signals = set(ma_signal.unique())
            
            expected_signals = {'BUY', 'SELL', 'HOLD'}
            
            self.assertTrue(valid_rsi_signals.issubset(expected_signals), 
                           f"RSI signals should be in {expected_signals}, got {valid_rsi_signals}")
            self.assertTrue(valid_ma_signals.issubset(expected_signals), 
                           f"MA signals should be in {expected_signals}, got {valid_ma_signals}")
            
            # Check if we have non-HOLD signals
            rsi_non_hold = (rsi_signal != 'HOLD').sum()
            ma_non_hold = (ma_signal != 'HOLD').sum()
            
            print(f"🔧 RSI non-HOLD signals: {rsi_non_hold}")
            print(f"🔧 MA non-HOLD signals: {ma_non_hold}")
            
            # We should have some non-HOLD signals
            self.assertGreater(rsi_non_hold, 0, "Should have some non-HOLD RSI signals")
            self.assertGreater(ma_non_hold, 0, "Should have some non-HOLD MA signals")
            
            print("✅ Signal generation test PASSED")
            
        except Exception as e:
            print(f"❌ Signal generation test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    print("🚀 Starting Indicator Calculation Debug Test")
    print("=" * 50)
    
    unittest.main(verbosity=2)