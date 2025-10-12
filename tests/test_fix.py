# Create a simple test file test_fix.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import macd, bollinger_bands
from simple_strategy.strategies.signals_library import macd_signals, bollinger_bands_signals
import pandas as pd

# Create test data
data = pd.DataFrame({
    'open': [100, 101, 102, 103, 104],
    'high': [101, 102, 103, 104, 105],
    'low': [99, 100, 101, 102, 103],
    'close': [100, 101, 102, 103, 104],
    'volume': [1000, 1100, 1200, 1300, 1400]
})

print("🧪 Testing MACD integration...")
try:
    strategy = StrategyBuilder(['TEST'], ['1D'])
    strategy.add_indicator('macd', macd, fast_period=12, slow_period=26, signal_period=9)
    strategy.add_signal_rule('macd_signal', macd_signals, 
                           macd_line='macd_macd_line', signal_line='macd_signal_line')  # ← USE THESE NAMES
    built_strategy = strategy.build()
    
    # Test with the data format your system expects
    test_data = {'TEST': {'1D': data}}
    signals = built_strategy.generate_signals(test_data)
    print(f"✅ MACD integration works! Signal: {signals['TEST']['1D']}")
except Exception as e:
    print(f"❌ MACD integration failed: {e}")

print("\n🧪 Testing Bollinger Bands integration...")
try:
    strategy = StrategyBuilder(['TEST'], ['1D'])
    strategy.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
    strategy.add_signal_rule('bb_signal', bollinger_bands_signals, 
                           price='close', upper_band='bb_upper_band', lower_band='bb_lower_band')  # ← USE THESE NAMES
    built_strategy = strategy.build()
    
    # Test with the data format your system expects
    test_data = {'TEST': {'1D': data}}
    signals = built_strategy.generate_signals(test_data)
    print(f"✅ Bollinger Bands integration works! Signal: {signals['TEST']['1D']}")
except Exception as e:
    print(f"❌ Bollinger Bands integration failed: {e}")