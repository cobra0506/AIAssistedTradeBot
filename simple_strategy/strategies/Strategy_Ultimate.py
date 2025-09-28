# Ultimate Working Strategy - Using Only Tested Components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover

def create_ultimate_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Ultimate working strategy using only tested components
    Strategy Logic:
    - Use EMA crossover for trend following
    - Simple, reliable, and tested
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators that we KNOW work perfectly
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    
    # Add signal rule that we KNOW works
    strategy.add_signal_rule('ema_cross', ma_crossover)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# ultimate_strategy = create_ultimate_strategy()
