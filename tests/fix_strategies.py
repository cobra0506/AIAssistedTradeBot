import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_strategy_1():
    """Fix Strategy 1 - Trend Following"""
    content = '''# Strategy 1: Trend-Following (Moving Average Crossover)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema
from simple_strategy.strategies.signals_library import ma_crossover

def create_trend_following_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Create a trend-following strategy using moving average crossovers.
    Strategy Logic:
    - Use fast EMA (20) and slow EMA (50) for trend direction
    - Use SMA (200) as long-term trend filter
    - Buy when fast EMA crosses above slow EMA AND price is above SMA 200
    - Sell when fast EMA crosses below slow EMA OR price drops below SMA 200
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=20)
    strategy.add_indicator('ema_slow', ema, period=50)
    strategy.add_indicator('sma_long', sma, period=200)
    
    # Add signal rules - CORRECTED PARAMETERS
    strategy.add_signal_rule('ema_crossover', ma_crossover)
    # Note: ma_crossover takes just 2 series, no additional parameters
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# trend_strategy = create_trend_following_strategy()
'''
    
    with open('simple_strategy/strategies/Strategy_1_Trend_Following.py', 'w') as f:
        f.write(content)
    print("✅ Fixed Strategy 1")

def fix_strategy_2():
    """Fix Strategy 2 - Mean Reversion"""
    content = '''# Strategy 2: Mean Reversion (RSI-based)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, bollinger_bands, sma
from simple_strategy.strategies.signals_library import overbought_oversold

def create_mean_reversion_strategy(symbols=['BTCUSDT'], timeframes=['60', '120']):
    """
    Create a mean reversion strategy using RSI and Bollinger Bands.
    Strategy Logic:
    - RSI (14) for overbought/oversold conditions
    - Bollinger Bands (20, 2) for volatility-based reversals
    - SMA (50) as mean reference
    - Buy when RSI < 30 AND price touches lower Bollinger Band
    - Sell when RSI > 70 AND price touches upper Bollinger Band
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('rsi', rsi, period=14)
    strategy.add_indicator('bb_upper', bollinger_bands, period=20, std_dev=2)
    strategy.add_indicator('bb_lower', bollinger_bands, period=20, std_dev=2)
    strategy.add_indicator('bb_middle', bollinger_bands, period=20, std_dev=2)
    strategy.add_indicator('sma_mean', sma, period=50)
    
    # Add signal rules - CORRECTED PARAMETERS
    strategy.add_signal_rule('rsi_oversold', overbought_oversold, oversold=30)
    strategy.add_signal_rule('rsi_overbought', overbought_oversold, overbought=70)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# mean_reversion_strategy = create_mean_reversion_strategy()
'''
    
    with open('simple_strategy/strategies/Strategy_2_mean_reversion.py', 'w') as f:
        f.write(content)
    print("✅ Fixed Strategy 2")

def fix_strategy_3():
    """Fix Strategy 3 - Multi-Indicator"""
    content = '''# Strategy 3: Multi-Indicator Strategy
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, macd, bollinger_bands, sma, ema
from simple_strategy.strategies.signals_library import overbought_oversold

def create_multi_indicator_strategy(symbols=['BTCUSDT', 'ETHUSDT'], timeframes=['60', '240']):
    """
    Create a multi-indicator strategy combining trend, momentum, and volatility.
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('sma_medium', sma, period=50)
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rules - CORRECTED PARAMETERS
    strategy.add_signal_rule('rsi_neutral', overbought_oversold, overbought=60, oversold=40)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# multi_indicator_strategy = create_multi_indicator_strategy()
'''
    
    with open('simple_strategy/strategies/Strategy_3_Multi_Indicator.py', 'w') as f:
        f.write(content)
    print("✅ Fixed Strategy 3")

if __name__ == '__main__':
    print("🔧 Fixing Strategy Parameters...")
    print("=" * 50)
    
    fix_strategy_1()
    fix_strategy_2()
    fix_strategy_3()
    
    print("\n🎉 All strategies fixed!")
    print("🚀 Ready for testing with real data!")