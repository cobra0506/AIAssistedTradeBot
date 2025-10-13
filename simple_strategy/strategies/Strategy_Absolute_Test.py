"""
Absolute Test Strategy - Always generates BUY/SELL signals for testing
"""
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import sma
from strategies.signals_library import overbought_oversold

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create a simple test strategy that always generates BUY/SELL signals
    """
    if symbols is None:
        symbols = ['SOLUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add a simple indicator (required for signal rules)
    strategy.add_indicator('sma', sma, period=10)
    
    # Add a signal rule (required for validation)
    strategy.add_signal_rule('test_signal', overbought_oversold, 
                           indicator='sma', 
                           overbought=999,  # Set impossibly high so it never triggers
                           oversold=1)    # Set impossibly low so it never triggers
    
    # Set strategy info
    strategy.set_strategy_info('Absolute_Test', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'test_param': {'type': 'int', 'default': 1, 'min': 1, 'max': 10, 'description': 'Test parameter'}
}