# Working Strategy with Manual Signal Logic
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold

def create_working_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Working strategy with manual signal logic
    Strategy Logic:
    - EMA crossover for trend following
    - RSI for overbought/oversold conditions
    - Manual signal generation to avoid parameter issues
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators that we KNOW work perfectly
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rules - let's try the correct way
    strategy.add_signal_rule('ema_cross', ma_crossover)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# working_strategy = create_working_strategy()
