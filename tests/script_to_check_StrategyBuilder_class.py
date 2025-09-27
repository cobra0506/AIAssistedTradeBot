"""
Debug script to see what's being passed to signal functions
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_strategy.strategies.strategy_builder import StrategyBuilder
    from simple_strategy.strategies.indicators_library import rsi
    from simple_strategy.strategies.signals_library import overbought_oversold
    
    print("🔍 Debug: What's being passed to signal functions")
    print("=" * 50)
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='1min')
    prices = np.random.normal(50000, 100, 100).cumsum()
    
    data = pd.DataFrame({
        'timestamp': (dates.astype(np.int64) // 10**9).values,
        'datetime': dates,
        'open': prices,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'volume': np.random.randint(100, 1000, 100)
    }).set_index('datetime')
    
    # Create strategy
    strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
    strategy.add_indicator('rsi', rsi, period=14)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    
    # Manually test what happens when we calculate indicators
    print("📊 Testing indicator calculation...")
    
    # Calculate RSI manually
    rsi_result = rsi(data['close'], period=14)
    print(f"📋 RSI result type: {type(rsi_result)}")
    print(f"📋 RSI result shape: {rsi_result.shape}")
    print(f"📋 RSI result head: {rsi_result.head()}")
    
    # Test what happens when we call overbought_oversold directly
    print("\n📈 Testing overbought_oversold directly...")
    try:
        signal_result = overbought_oversold(rsi_result, overbought=70, oversold=30)
        print(f"✅ Direct call successful: {type(signal_result)}")
    except Exception as e:
        print(f"❌ Direct call failed: {e}")
    
    # Test what happens when we pass a single value
    print("\n📈 Testing with single value...")
    try:
        single_value = rsi_result.iloc[-1]
        print(f"📋 Single value: {single_value} (type: {type(single_value)})")
        signal_result = overbought_oversold(single_value, overbought=70, oversold=30)
        print(f"✅ Single value call successful: {type(signal_result)}")
    except Exception as e:
        print(f"❌ Single value call failed: {e}")
    
    # Now let's see what the strategy builder does
    print("\n🏗️ Testing strategy builder process...")
    
    # Create a mock strategy instance to test the internal methods
    class MockStrategy:
        def __init__(self):
            self.indicators = {'rsi': rsi_result}
            self.signal_rules = {
                'rsi_signal': {
                    'function': overbought_oversold,
                    'params': {'overbought': 70, 'oversold': 30}
                }
            }
        
        def _generate_signals_from_indicators(self, indicators: Dict[str, Any]) -> Dict[str, pd.Series]:
            """Generate signals from calculated indicators"""
            signals = {}
            
            for rule_name, config in self.signal_rules.items():
                try:
                    func = config['function']
                    params = config['params']
                    
                    # Special handling for common signal functions
                    if func.__name__ == 'overbought_oversold':
                        # This function needs: indicator_series, overbought, oversold
                        if 'rsi' in indicators:
                            indicator_series = indicators['rsi']
                            # Handle multi-output indicators
                            if isinstance(indicator_series, tuple):
                                indicator_series = indicator_series[0]
                            
                            # Clean NaN values
                            indicator_series = indicator_series.fillna(50)
                            
                            args = [indicator_series, params.get('overbought', 70), params.get('oversold', 30)]
                        else:
                            continue
                            
                    elif func.__name__ == 'ma_crossover':
                        # This function needs: fast_ma, slow_ma
                        if 'sma_short' in indicators and 'sma_long' in indicators:
                            fast_ma = indicators['sma_short']
                            slow_ma = indicators['sma_long']
                            args = [fast_ma, slow_ma]
                        else:
                            continue
                            
                    elif func.__name__ == 'macd_signals':
                        # This function needs: macd_line, signal_line, histogram
                        if 'macd' in indicators:
                            macd_result = indicators['macd']
                            if isinstance(macd_result, tuple) and len(macd_result) >= 2:
                                args = [macd_result[0], macd_result[1]]
                                if len(macd_result) >= 3:
                                    args.append(macd_result[2])
                            else:
                                continue
                        else:
                            continue
                            
                    else:
                        # Default logic for other functions
                        args = []
                        for param_name, param_value in params.items():
                            if param_name in indicators:
                                args.append(indicators[param_name])
                            else:
                                args.append(param_value)
                    
                    # Generate signal
                    signal_result = func(*args)
                    signals[rule_name] = signal_result
                    
                    logger.debug(f"📈 Generated {rule_name} signal")
                    
                except Exception as e:
                    logger.error(f"❌ Error generating {rule_name} signal: {e}")
            
            return signals
    
    mock_strategy = MockStrategy()
    signals = mock_strategy._generate_signals_from_indicators(mock_strategy.indicators)
    
    print(f"\n🎯 Final signals: {signals}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()