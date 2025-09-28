# Strategy 1: Trend-Following (Moving Average Crossover)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema
from simple_strategy.strategies.signals_library import ma_crossover

def create_trend_following_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Create a trend-following strategy using moving average crossovers.
    Strategy Logic:
    - Use fast EMA (20) and slow EMA (50) for trend direction
    - Buy when fast EMA crosses above slow EMA
    - Sell when fast EMA crosses below slow EMA
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=20)
    strategy.add_indicator('ema_slow', ema, period=50)
    
    # Add signal rule - ma_crossover works with 2 series
    strategy.add_signal_rule('ema_cross', ma_crossover)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# trend_strategy = create_trend_following_strategy()
