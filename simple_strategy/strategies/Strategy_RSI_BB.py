"""
RSI + Bollinger Bands Strategy
Combines RSI oversold/overbought signals with Bollinger Bands breakout
"""
from .strategy_builder import StrategyBuilder
from .indicators_library import rsi, bollinger_bands
from .signals_library import overbought_oversold, bollinger_bands_signals

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create RSI + Bollinger Bands strategy
    Parameters:
    - rsi_period: RSI calculation period (default: 14)
    - bb_period: Bollinger Bands period (default: 20)
    - rsi_overbought: RSI overbought level (default: 70)
    - rsi_oversold: RSI oversold level (default: 30)
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    rsi_period = params.get('rsi_period', 14)
    bb_period = params.get('bb_period', 20)
    rsi_overbought = params.get('rsi_overbought', 70)
    rsi_oversold = params.get('rsi_oversold', 30)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    strategy.add_indicator('bb', bollinger_bands, period=bb_period)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                           indicator='rsi', 
                           overbought=rsi_overbought, 
                           oversold=rsi_oversold)
    strategy.add_signal_rule('bb_signal', bollinger_bands_signals,
                           price='close',
                           upper_band='bb_upper',
                           lower_band='bb_lower')
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('RSI_BB', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 1, 'max': 50, 'description': 'RSI calculation period'},
    'bb_period': {'type': 'int', 'default': 20, 'min': 5, 'max': 50, 'description': 'Bollinger Bands period'},
    'rsi_overbought': {'type': 'int', 'default': 70, 'min': 50, 'max': 90, 'description': 'RSI overbought level'},
    'rsi_oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 50, 'description': 'RSI oversold level'}
}