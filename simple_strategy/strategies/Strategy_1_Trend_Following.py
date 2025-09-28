# Strategy 1: Trend-Following (Moving Average Crossover)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema
from simple_strategy.strategies.signals_library import ma_crossover

def create_trend_following_strategy(symbols=['BTCUSDT'], timeframes=['1h', '4h']):
    """
    Create a trend-following strategy using moving average crossovers.
    
    Strategy Logic:
    - Use fast EMA (20) and slow EMA (50) for trend direction
    - Use SMA (200) as long-term trend filter
    - Buy when fast EMA crosses above slow EMA AND price is above SMA 200
    - Sell when fast EMA crosses below slow EMA OR price drops below SMA 200
    """
    
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('ema_fast', ema, period=20)      # Fast EMA for trend following
    strategy.add_indicator('ema_slow', ema, period=50)      # Slow EMA for trend following  
    strategy.add_indicator('sma_trend', sma, period=200)    # Long-term trend filter
    
    # Add signal rules
    strategy.add_signal_rule('ema_crossover', ma_crossover, 
                           fast_period=20, slow_period=50, 
                           fast_type='ema', slow_type='ema')
    
    strategy.add_signal_rule('trend_filter', ma_crossover,
                           fast_period=1, slow_period=200,  # Price vs SMA 200
                           fast_type='price', slow_type='sma')
    
    # Set signal combination: both signals must agree (AND logic)
    strategy.set_signal_combination('unanimous')
    
    return strategy.build()

# Usage example:
trend_strategy = create_trend_following_strategy()