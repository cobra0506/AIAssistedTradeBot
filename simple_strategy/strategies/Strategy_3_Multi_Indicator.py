# Strategy 3: Multi-Indicator Strategy
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, ema
from simple_strategy.strategies.signals_library import overbought_oversold

def create_multi_indicator_strategy(symbols=['BTCUSDT', 'ETHUSDT'], timeframes=['60', '240']):
    """
    Create a multi-indicator strategy combining trend and momentum.
    Strategy Logic:
    - Use EMA crossover for trend direction
    - Use RSI for momentum confirmation
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rules
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=60, oversold=40)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# multi_indicator_strategy = create_multi_indicator_strategy()
