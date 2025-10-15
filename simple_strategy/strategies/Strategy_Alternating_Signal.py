"""
Fixed Working Strategy - Proper Error Handling
"""
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import rsi
from strategies.signals_library import overbought_oversold

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create strategy that handles None values properly
    """
    # Handle None or empty symbols
    if symbols is None or len(symbols) == 0:
        symbols = ['ADAUSDT']  # Default to ADAUSDT for testing
    
    # Handle None or empty timeframes
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['5m']
    
    # Get parameters with reasonable values
    rsi_period = params.get('rsi_period', 14)
    oversold = params.get('oversold', 40)
    overbought = params.get('overbought', 60)
    
    # Create strategy using the symbols
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add RSI indicator
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    
    # Add signal rule
    strategy.add_signal_rule('rsi_signal', overbought_oversold,
                           indicator='rsi',
                           overbought=overbought,
                           oversold=oversold)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy.set_strategy_info('Fixed_RSI_Strategy', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 50, 'description': 'RSI calculation period'},
    'oversold': {'type': 'int', 'default': 40, 'min': 30, 'max': 50, 'description': 'Oversold threshold (BUY signal)'},
    'overbought': {'type': 'int', 'default': 60, 'min': 50, 'max': 70, 'description': 'Overbought threshold (SELL signal)'}
}