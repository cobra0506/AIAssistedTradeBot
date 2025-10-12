"""
Strategy 1: Trend Following Strategy
Uses moving averages to identify trends and follow them.
"""
import sys
import os

# Add parent directories to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import sma, ema
from .signals_library import ma_crossover

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Trend Following strategy
    Parameters:
    - fast_period: Fast MA period (default: 10)
    - slow_period: Slow MA period (default: 30)
    - ma_type: Moving average type - 'sma' or 'ema' (default: 'sma')
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    fast_period = params.get('fast_period', 10)
    slow_period = params.get('slow_period', 30)
    ma_type = params.get('ma_type', 'sma')
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators based on MA type
    if ma_type == 'sma':
        strategy.add_indicator('sma_fast', sma, period=fast_period)
        strategy.add_indicator('sma_slow', sma, period=slow_period)
    else:  # ema
        strategy.add_indicator('ema_fast', ema, period=fast_period)
        strategy.add_indicator('ema_slow', ema, period=slow_period)
    
    # Add signal rule
    if ma_type == 'sma':
        strategy.add_signal_rule('ma_crossover', ma_crossover, 
                               fast_ma='sma_fast', 
                               slow_ma='sma_slow')
    else:  # ema
        strategy.add_signal_rule('ma_crossover', ma_crossover, 
                               fast_ma='ema_fast', 
                               slow_ma='ema_slow')
    
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('Trend_Following', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'fast_period': {'type': 'int', 'default': 10, 'min': 1, 'max': 50, 'description': 'Fast moving average period'},
    'slow_period': {'type': 'int', 'default': 30, 'min': 10, 'max': 100, 'description': 'Slow moving average period'},
    'ma_type': {'type': 'str', 'default': 'sma', 'options': ['sma', 'ema'], 'description': 'Moving average type'}
}