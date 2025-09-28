# Strategy 2: Mean Reversion (RSI-based)
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, bollinger_bands, sma
from simple_strategy.strategies.signals_library import overbought_oversold, bollinger_bands_signals

def create_mean_reversion_strategy(symbols=['BTCUSDT'], timeframes=['1h', '2h']):
    """
    Create a mean reversion strategy using RSI and Bollinger Bands.
    
    Strategy Logic:
    - RSI (14) for overbought/oversold conditions
    - Bollinger Bands (20, 2) for volatility-based reversals
    - SMA (50) as mean reference
    - Buy when RSI < 30 AND price touches lower Bollinger Band
    - Sell when RSI > 70 AND price touches upper Bollinger Band
    """
    
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    strategy.add_indicator('rsi', rsi, period=14)                    # RSI for overbought/oversold
    strategy.add_indicator('bb_upper', bollinger_bands, period=20, std_dev=2, band='upper')
    strategy.add_indicator('bb_lower', bollinger_bands, period=20, std_dev=2, band='lower')
    strategy.add_indicator('bb_middle', bollinger_bands, period=20, std_dev=2, band='middle')
    strategy.add_indicator('sma_mean', sma, period=50)               # Mean reference
    
    # Add signal rules - using available signals
    strategy.add_signal_rule('rsi_oversold', overbought_oversold, 
                           overbought=70, oversold=30, signal_type='oversold')
    
    strategy.add_signal_rule('rsi_overbought', overbought_oversold,
                           overbought=70, oversold=30, signal_type='overbought')
    
    # Use the correct Bollinger Bands signal
    strategy.add_signal_rule('bb_oversold', bollinger_bands_signals,
                           signal_type='oversold')  # Lower band signal
    
    strategy.add_signal_rule('bb_overbought', bollinger_bands_signals,
                           signal_type='overbought')  # Upper band signal
    
    # Set signal combination: majority vote for confirmation
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# mean_reversion_strategy = create_mean_reversion_strategy()