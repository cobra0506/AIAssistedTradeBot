import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_signal_functions():
    """Debug how signal functions actually work in your system"""
    
    print("🔍 Debugging Signal Functions...")
    print("=" * 50)
    
    try:
        # Import the signals library
        from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold
        import inspect
        
        # Check ma_crossover signature
        ma_sig = inspect.signature(ma_crossover)
        print(f"📊 ma_crossover signature: {ma_sig}")
        
        # Check overbought_oversold signature  
        obos_sig = inspect.signature(overbought_oversold)
        print(f"📊 overbought_oversold signature: {obos_sig}")
        
        # Check what parameters each function expects
        print(f"\n📋 ma_crossover parameters:")
        for param_name, param in ma_sig.parameters.items():
            print(f"   - {param_name}: {param.annotation}")
            if param.default != inspect.Parameter.empty:
                print(f"     Default: {param.default}")
        
        print(f"\n📋 overbought_oversold parameters:")
        for param_name, param in obos_sig.parameters.items():
            print(f"   - {param_name}: {param.annotation}")
            if param.default != inspect.Parameter.empty:
                print(f"     Default: {param.default}")
        
        # Test the functions with dummy data
        import pandas as pd
        import numpy as np
        
        # Create dummy data
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        prices = [100 + i + np.random.normal(0, 1) for i in range(50)]
        
        fast_ma = pd.Series(prices).rolling(10).mean()
        slow_ma = pd.Series(prices).rolling(20).mean()
        rsi_series = pd.Series([50, 55, 60, 65, 70, 65, 60, 55, 50, 45, 40, 35, 30, 35, 40])
        
        print(f"\n🧪 Testing signal functions with dummy data...")
        
        # Test ma_crossover
        try:
            ma_signals = ma_crossover(fast_ma, slow_ma)
            print(f"✅ ma_crossover works! Signal types: {set(ma_signals.dropna())}")
        except Exception as e:
            print(f"❌ ma_crossover error: {e}")
        
        # Test overbought_oversold
        try:
            obos_signals = overbought_oversold(rsi_series, overbought=70, oversold=30)
            print(f"✅ overbought_oversold works! Signal types: {set(obos_signals.dropna())}")
        except Exception as e:
            print(f"❌ overbought_oversold error: {e}")
            
    except Exception as e:
        print(f"❌ Error debugging signals: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    debug_signal_functions()