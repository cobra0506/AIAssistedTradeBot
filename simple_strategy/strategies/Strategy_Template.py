"""
Template for creating new strategies
Copy this file and rename it to Strategy_YourStrategyName.py
"""

STRATEGY_PARAMETERS = {
    'parameter1': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 50,
        'description': 'Description of parameter 1'
    },
    'parameter2': {
        'type': 'str',
        'default': 'option1',
        'options': ['option1', 'option2'],
        'description': 'Description of parameter 2'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create your strategy instance
    """
    from simple_strategy.strategies.strategy_builder import StrategyBuilder
    from simple_strategy.strategies.indicators_library import rsi, sma, ema
    from simple_strategy.strategies.signals_library import overbought_oversold
    
    # Set defaults if not provided
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1h']
    
    # Create strategy builder
    strategy_builder = StrategyBuilder(symbols, timeframes)
    
    # Add indicators using parameters
    param1 = params.get('parameter1', 14)
    strategy_builder.add_indicator('rsi', rsi, period=param1)
    
    # Add signal rules
    strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                   overbought=70, oversold=30)
    
    # Set signal combination
    strategy_builder.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy_builder.set_strategy_info('YourStrategyName', '1.0.0')
    
    # Build and return
    return strategy_builder.build()