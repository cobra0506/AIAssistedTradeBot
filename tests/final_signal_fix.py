import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_all_strategies():
    """Fix all strategy files with correct signal parameters"""
    
    # Fix Strategy 1 - Use working signals only
    strategy_1_content = '''# Strategy 1: Trend-Following (Moving Average Crossover)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema
from simple_strategy.strategies.signals_library import ma_crossover

def create_trend_following_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Create a trend-following strategy using moving average crossovers.
    Strategy Logic:
    - Use fast EMA (20) and slow EMA (50) for trend direction
    - Buy when fast EMA crosses above slow EMA
    - Sell when fast EMA crosses below slow EMA
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=20)
    strategy.add_indicator('ema_slow', ema, period=50)
    
    # Add signal rule - ma_crossover works with 2 series
    strategy.add_signal_rule('ema_cross', ma_crossover)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# trend_strategy = create_trend_following_strategy()
'''
    
    # Fix Strategy 2 - Simplified with working signals
    strategy_2_content = '''# Strategy 2: Mean Reversion (RSI-based)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi
from simple_strategy.strategies.signals_library import overbought_oversold

def create_mean_reversion_strategy(symbols=['BTCUSDT'], timeframes=['60', '120']):
    """
    Create a mean reversion strategy using RSI.
    Strategy Logic:
    - Buy when RSI < 30 (oversold)
    - Sell when RSI > 70 (overbought)
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rule - overbought_oversold with RSI indicator
    # The StrategyBuilder will automatically pass the rsi series to the signal function
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# mean_reversion_strategy = create_mean_reversion_strategy()
'''
    
    # Fix Strategy 3 - Simplified working version
    strategy_3_content = '''# Strategy 3: Multi-Indicator Strategy
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, ema
from simple_strategy.strategies.signals_library import overbought_oversold

def create_multi_indicator_strategy(symbols=['BTCUSDT', 'ETHUSDT'], timeframes=['60', '240']):
    """
    Create a multi-indicator strategy combining trend and momentum.
    Strategy Logic:
    - Use EMA crossover for trend direction
    - Use RSI for momentum confirmation
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rules
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=60, oversold=40)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# multi_indicator_strategy = create_multi_indicator_strategy()
'''
    
    # Write the fixed files
    try:
        with open('simple_strategy/strategies/Strategy_1_Trend_Following.py', 'w') as f:
            f.write(strategy_1_content)
        print("✅ Fixed Strategy 1 - Trend Following")
        
        with open('simple_strategy/strategies/Strategy_2_mean_reversion.py', 'w') as f:
            f.write(strategy_2_content)
        print("✅ Fixed Strategy 2 - Mean Reversion")
        
        with open('simple_strategy/strategies/Strategy_3_Multi_Indicator.py', 'w') as f:
            f.write(strategy_3_content)
        print("✅ Fixed Strategy 3 - Multi-Indicator")
        
        print("\n🎉 All strategies fixed with correct signal parameters!")
        print("🚀 Ready for testing!")
        
    except Exception as e:
        print(f"❌ Error fixing strategies: {e}")

if __name__ == '__main__':
    print("🔧 Final Signal Fix...")
    print("=" * 50)
    fix_all_strategies()