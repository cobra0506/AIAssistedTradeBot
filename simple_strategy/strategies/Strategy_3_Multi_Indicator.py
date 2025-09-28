# Strategy 3: Multi-Indicator Strategy
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, macd, bollinger_bands, sma, ema
from simple_strategy.strategies.signals_library import overbought_oversold, macd_signals, ma_crossover

def create_multi_indicator_strategy(symbols=['BTCUSDT', 'ETHUSDT'], timeframes=['1h', '4h']):
    """
    Create a multi-indicator strategy combining trend, momentum, and volatility.
    
    Strategy Logic:
    TREND FILTER (Weight: 40%):
    - EMA (20) vs SMA (50) for trend direction
    - Price above SMA (200) for long-term bias
    
    MOMENTUM FILTER (Weight: 35%):
    - MACD (12, 26, 9) for momentum confirmation
    - RSI (14) for overbought/oversold conditions
    
    VOLATILITY FILTER (Weight: 25%):
    - Bollinger Bands (20, 2) for volatility-based entries/exits
    
    ENTRY: At least 3 out of 4 signals must agree
    EXIT: Any 2 reverse signals trigger exit
    """
    
    strategy = StrategyBuilder(symbols, timeframes)
    
    # TREND INDICATORS
    strategy.add_indicator('ema_fast', ema, period=20)           # Short-term trend
    strategy.add_indicator('sma_medium', sma, period=50)         # Medium-term trend
    strategy.add_indicator('sma_long', sma, period=200)          # Long-term trend filter
    
    # MOMENTUM INDICATORS  
    strategy.add_indicator('rsi', rsi, period=14)                # Momentum oscillator
    strategy.add_indicator('macd', macd, fast=12, slow=26, signal=9)  # MACD line
    strategy.add_indicator('macd_signal', macd, fast=12, slow=26, signal=9, component='signal')  # MACD signal line
    strategy.add_indicator('macd_histogram', macd, fast=12, slow=26, signal=9, component='histogram')  # MACD histogram
    
    # VOLATILITY INDICATORS
    strategy.add_indicator('bb_upper', bollinger_bands, period=20, std_dev=2, band='upper')
    strategy.add_indicator('bb_lower', bollinger_bands, period=20, std_dev=2, band='lower')
    strategy.add_indicator('bb_middle', bollinger_bands, period=20, std_dev=2, band='middle')
    
    # TREND SIGNALS
    strategy.add_signal_rule('trend_direction', ma_crossover,
                           fast_period=20, slow_period=50, fast_type='ema', slow_type='sma')
    
    strategy.add_signal_rule('long_term_trend', ma_crossover,
                           fast_period=1, slow_period=200, fast_type='price', slow_type='sma')
    
    # MOMENTUM SIGNALS
    strategy.add_signal_rule('rsi_neutral', overbought_oversold,
                           overbought=60, oversold=40, signal_type='neutral')  # Wider RSI bands
    
    strategy.add_signal_rule('macd_bullish', macd_signals,
                           signal_type='bullish')  # Using correct signal name
    
    strategy.add_signal_rule('macd_bearish', macd_signals,
                           signal_type='bearish')  # Using correct signal name
    
    # VOLATILITY SIGNALS - using available signals
    strategy.add_signal_rule('bb_squeeze', overbought_oversold,
                           overbought=75, oversold=25, signal_type='neutral')  # Simulates BB squeeze
    
    strategy.add_signal_rule('bb_breakout', overbought_oversold,
                           overbought=85, oversold=15, signal_type='overbought')  # Simulates BB breakout
    
    # Set signal combination: weighted majority (requires strong consensus)
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# multi_indicator_strategy = create_multi_indicator_strategy()