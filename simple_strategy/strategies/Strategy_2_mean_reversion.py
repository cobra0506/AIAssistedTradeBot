"""
Strategy 2: Mean Reversion Strategy
Uses RSI to identify overbought/oversold conditions for mean reversion trades.
"""
import sys
import os

# Add parent directories to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import rsi, sma
from .signals_library import overbought_oversold

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Mean Reversion strategy
    Parameters:
    - rsi_period: RSI calculation period (default: 14)
    - rsi_overbought: RSI overbought level (default: 70)
    - rsi_oversold: RSI oversold level (default: 30)
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    rsi_period = params.get('rsi_period', 14)
    rsi_overbought = params.get('rsi_overbought', 70)
    rsi_oversold = params.get('rsi_oversold', 30)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                           indicator='rsi', 
                           overbought=rsi_overbought, 
                           oversold=rsi_oversold)
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('Mean_Reversion', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 1, 'max': 50, 'description': 'RSI calculation period'},
    'rsi_overbought': {'type': 'int', 'default': 70, 'min': 50, 'max': 90, 'description': 'RSI overbought level'},
    'rsi_oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 50, 'description': 'RSI oversold level'}
}