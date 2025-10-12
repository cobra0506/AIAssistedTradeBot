"""
Example Strategy - Simple Moving Average Crossover
This is a basic strategy that uses two moving averages to generate signals.
"""
import sys
import os

# Add parent directories to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import sma
from .signals_library import ma_crossover

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Simple Moving Average Crossover strategy
    Parameters:
    - fast_period: Fast MA period (default: 10)
    - slow_period: Slow MA period (default: 30)
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    fast_period = params.get('fast_period', 10)
    slow_period = params.get('slow_period', 30)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    strategy.add_indicator('sma_fast', sma, period=fast_period)
    strategy.add_indicator('sma_slow', sma, period=slow_period)
    strategy.add_signal_rule('ma_crossover', ma_crossover, 
                           fast_ma='sma_fast', 
                           slow_ma='sma_slow')
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('MA_Crossover', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'fast_period': {'type': 'int', 'default': 10, 'min': 1, 'max': 50, 'description': 'Fast moving average period'},
    'slow_period': {'type': 'int', 'default': 30, 'min': 10, 'max': 100, 'description': 'Slow moving average period'}
}