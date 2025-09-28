# Strategy 2: Mean Reversion (RSI-based)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi
from simple_strategy.strategies.signals_library import overbought_oversold

def create_mean_reversion_strategy(symbols=['BTCUSDT'], timeframes=['60', '120']):
    """
    Create a mean reversion strategy using RSI.
    Strategy Logic:
    - Buy when RSI < 30 (oversold)
    - Sell when RSI > 70 (overbought)
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rule - overbought_oversold with RSI indicator
    # The StrategyBuilder will automatically pass the rsi series to the signal function
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# mean_reversion_strategy = create_mean_reversion_strategy()
