"""
Simple Test Strategy - Basic RSI Strategy
This is a simple strategy for testing the system.
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
    Create Simple RSI strategy
    Parameters:
    - rsi_period: RSI period (default: 14)
    - overbought: Overbought level (default: 70)
    - oversold: Oversold level (default: 30)
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    rsi_period = params.get('rsi_period', 14)
    overbought = params.get('overbought', 70)
    oversold = params.get('oversold', 30)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                           indicator='rsi',
                           overbought=overbought, 
                           oversold=oversold)
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('Simple_RSI', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 1, 'max': 50, 'description': 'RSI calculation period'},
    'overbought': {'type': 'int', 'default': 70, 'min': 50, 'max': 90, 'description': 'RSI overbought level'},
    'oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 50, 'description': 'RSI oversold level'}
}