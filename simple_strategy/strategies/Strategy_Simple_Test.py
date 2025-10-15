"""
Simple RSI Strategy Test - PROPER IMPLEMENTATION
Uses the existing system WITHOUT core code changes
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
    Create Simple RSI Strategy using the EXISTING system
    """
    if symbols is None:
        symbols = ['SOLUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with MORE AGGRESSIVE values
    rsi_period = params.get('rsi_period', 14)
    oversold = params.get('oversold', 35)  # More aggressive
    overbought = params.get('overbought', 65)  # More aggressive
    
    # Create strategy using the EXISTING StrategyBuilder
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add RSI indicator using the EXISTING indicators library
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    
    # Add signal rule using the EXISTING signals library
    strategy.add_signal_rule('rsi_signal', overbought_oversold,
                           indicator='rsi',
                           overbought=overbought, 
                           oversold=oversold)
    
    # Set signal combination using the EXISTING system
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info using the EXISTING system
    strategy.set_strategy_info('Simple_RSI', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI - using the EXISTING system
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 50, 'description': 'RSI calculation period'},
    'oversold': {'type': 'int', 'default': 35, 'min': 20, 'max': 45, 'description': 'Oversold threshold (BUY signal)'},
    'overbought': {'type': 'int', 'default': 65, 'min': 55, 'max': 80, 'description': 'Overbought threshold (SELL signal)'}
}