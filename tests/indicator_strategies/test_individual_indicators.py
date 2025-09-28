import sys
import os
import pandas as pd

# Robust path handling - this will work from any location
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))  # Go up two levels from tests/indicator_strategies
sys.path.insert(0, project_root)

print(f"Current file: {current_file}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[0]}")

# Now try the imports
try:
    from simple_strategy.strategies.strategy_builder import StrategyBuilder
    from simple_strategy.strategies.indicators_library import *
    from simple_strategy.strategies.signals_library import *
    from simple_strategy.backtester.backtester_engine import BacktestEngine
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative path
    alternative_root = os.path.dirname(project_root)  # Go up one more level
    sys.path.insert(0, alternative_root)
    print(f"Trying alternative root: {alternative_root}")
    try:
        from simple_strategy.strategies.strategy_builder import StrategyBuilder
        from simple_strategy.strategies.indicators_library import *
        from simple_strategy.strategies.signals_library import *
        from simple_strategy.backtester.backtester_engine import BacktestEngine
        print("✅ All imports successful with alternative path!")
    except ImportError as e2:
        print(f"❌ Still failing: {e2}")
        print("Please check your project structure")
        sys.exit(1)

def test_sma_strategy():
    """Simple SMA crossover strategy"""
    strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
    strategy.add_indicator('sma_short', sma, period=10)
    strategy.add_indicator('sma_long', sma, period=30)
    strategy.add_signal_rule('sma_crossover', ma_crossover, 
                           fast_ma='sma_short', slow_ma='sma_long')
    strategy.set_signal_combination('majority_vote')
    return strategy.build()

def test_rsi_strategy():
    """Simple RSI overbought/oversold strategy"""
    strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
    strategy.add_indicator('rsi', rsi, period=14)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                           overbought=70, oversold=30)
    strategy.set_signal_combination('majority_vote')
    return strategy.build()

def test_macd_strategy():
    """Simple MACD strategy"""
    strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
    strategy.add_indicator('macd', macd, fast=12, slow=26, signal=9)
    strategy.add_signal_rule('macd_signal', macd_signals)
    strategy.set_signal_combination('majority_vote')
    return strategy.build()

def test_bollinger_strategy():
    """Simple Bollinger Bands strategy"""
    strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
    strategy.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
    strategy.add_signal_rule('bb_signal', bollinger_bands_signals)
    strategy.set_signal_combination('majority_vote')
    return strategy.build()

def run_indicator_test(strategy_name, strategy_func, symbol='BTCUSDT', timeframe='1h'):
    """Run a simple test for an indicator strategy"""
    print(f"\n🧪 Testing {strategy_name}...")
    
    try:
        # Build strategy
        strategy = strategy_func()
        print(f"✅ Strategy built successfully")
        
        # Quick backtest (small date range for speed)
        backtest = BacktestEngine(
            strategy=strategy,
            start_date='2023-12-01',  # Small date range
            end_date='2023-12-31',    # for fast testing
            initial_capital=10000
        )
        
        # Run backtest
        results = backtest.run()
        print(f"✅ Backtest completed")
        print(f"   - Total trades: {results.get('total_trades', 0)}")
        print(f"   - Total return: {results.get('total_return', 0):.2f}%")
        print(f"   - No errors: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {strategy_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_indicators():
    """Test all indicators with simple strategies"""
    tests = [
        ("SMA Strategy", test_sma_strategy),
        ("RSI Strategy", test_rsi_strategy),
        ("MACD Strategy", test_macd_strategy),
        ("Bollinger Bands Strategy", test_bollinger_strategy),
    ]
    
    results = []
    for name, func in tests:
        success = run_indicator_test(name, func)
        results.append((name, success))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    test_all_indicators()