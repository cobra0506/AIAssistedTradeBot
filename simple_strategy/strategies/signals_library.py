"""
Building Block Signals Library
================================

This library contains ALL signal processing functions that can be used in strategy building.
Each function processes indicators and returns trading signals.

Author: AI Assisted TradeBot Team
Date: 2025
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Tuple  # ← FIXED: Added Tuple import
import logging

logger = logging.getLogger(__name__)


# === BASIC SIGNAL FUNCTIONS ===

def overbought_oversold(indicator, overbought=70, oversold=30):
    """
    Generate overbought/oversold signals
    Args:
        indicator: Indicator series (RSI, Stochastic, etc.)
        overbought: Overbought threshold
        oversold: Oversold threshold
    Returns:
        Series with 'BUY', 'SELL', or 'HOLD' signals
    """
    # Create a series with default HOLD values
    signals = pd.Series('HOLD', index=indicator.index)
    
    # Generate BUY signals when indicator is below oversold
    signals[indicator < oversold] = 'BUY'
    
    # Generate SELL signals when indicator is above overbought
    signals[indicator > overbought] = 'SELL'
    
    return signals


def ma_crossover(fast_ma, slow_ma):
    """
    Generate MA crossover signals
    Args:
        fast_ma: Fast moving average series
        slow_ma: Slow moving average series
    Returns:
        Series with 'BUY', 'SELL', or 'HOLD' signals
    """
    # Create a series with default HOLD valuesF
    signals = pd.Series('HOLD', index=fast_ma.index)
    
    # Generate BUY signals when fast MA crosses above slow MA
    buy_signals = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
    signals[buy_signals] = 'BUY'
    
    # Generate SELL signals when fast MA crosses below slow MA
    sell_signals = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
    signals[sell_signals] = 'SELL'
    
    return signals

def macd_signals(macd_line: pd.Series, signal_line: pd.Series, 
                 histogram: pd.Series = None) -> pd.Series:
    """
    Generate MACD-based signals
    
    Args:
        macd_line: MACD line
        signal_line: Signal line
        histogram: MACD histogram (optional)
        
    Returns:
        Signal series: 1=BUY, -1=SELL, 0=HOLD
    """
    try:
        signals = pd.Series(0, index=macd_line.index)
        
        # BUY when MACD crosses above signal line
        buy_signals = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        signals[buy_signals] = 1
        
        # SELL when MACD crosses below signal line
        sell_signals = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
        signals[sell_signals] = -1
        
        return signals
    except Exception as e:
        logger.error(f"Error in macd_signals: {e}")
        return pd.Series(0, index=macd_line.index)


def bollinger_bands_signals(price: pd.Series, upper_band: pd.Series, 
                           lower_band: pd.Series, middle_band: pd.Series = None) -> pd.Series:
    """
    Generate Bollinger Bands signals
    
    Args:
        price: Price series
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        middle_band: Middle Bollinger Band (optional)
        
    Returns:
        Signal series: 1=BUY, -1=SELL, 0=HOLD
    """
    try:
        signals = pd.Series(0, index=price.index)
        
        # BUY when price touches or crosses below lower band
        buy_signals = price <= lower_band
        signals[buy_signals] = 1
        
        # SELL when price touches or crosses above upper band
        sell_signals = price >= upper_band
        signals[sell_signals] = -1
        
        return signals
    except Exception as e:
        logger.error(f"Error in bollinger_bands_signals: {e}")
        return pd.Series(0, index=price.index)


def stochastic_signals(k_percent: pd.Series, d_percent: pd.Series,
                     overbought: float=80, oversold: float=20) -> pd.Series:
    """
    Generate Stochastic signals
    Args:
        k_percent: %K line
        d_percent: %D line
        overbought: Overbought threshold
        oversold: Oversold threshold
    Returns:
        Series with 'BUY', 'SELL', or 'HOLD' signals
    """
    try:
        # Create a series with default HOLD values
        signals = pd.Series('HOLD', index=k_percent.index)
        
        # Generate BUY signals when both %K and %D are below oversold
        buy_signals = (k_percent < oversold) & (d_percent < oversold)
        signals[buy_signals] = 'BUY'
        
        # Generate SELL signals when both %K and %D are above overbought
        sell_signals = (k_percent > overbought) & (d_percent > overbought)
        signals[sell_signals] = 'SELL'
        
        return signals
    except Exception as e:
        logger.error(f"Error in stochastic_signals: {e}")
        return pd.Series('HOLD', index=k_percent.index)


# === ADVANCED SIGNAL FUNCTIONS ===

def divergence_signals(price: pd.Series, indicator: pd.Series, 
                      lookback_period: int = 20) -> pd.Series:
    """
    Generate divergence signals
    
    Args:
        price: Price series
        indicator: Indicator series
        lookback_period: Period to check for divergence
        
    Returns:
        Signal series: 1=BULLISH_DIVERGENCE, -1=BEARISH_DIVERGENCE, 0=NO_DIVERGENCE
    """
    try:
        signals = pd.Series(0, index=price.index)
        
        for i in range(lookback_period, len(price)):
            price_window = price.iloc[i-lookback_period:i+1]
            indicator_window = indicator.iloc[i-lookback_period:i+1]
            
            # Bullish divergence: price makes lower low, indicator makes higher low
            if (price_window.iloc[-1] < price_window.iloc[0] and 
                indicator_window.iloc[-1] > indicator_window.iloc[0]):
                signals.iloc[i] = 1
            
            # Bearish divergence: price makes higher high, indicator makes lower high
            elif (price_window.iloc[-1] > price_window.iloc[0] and 
                  indicator_window.iloc[-1] < indicator_window.iloc[0]):
                signals.iloc[i] = -1
        
        return signals
    except Exception as e:
        logger.error(f"Error in divergence_signals: {e}")
        return pd.Series(0, index=price.index)


def multi_timeframe_confirmation(signals_dict: Dict[str, pd.Series], 
                               min_confirmations: int = 2) -> pd.Series:
    """
    Generate signals based on multi-timeframe confirmation
    
    Args:
        signals_dict: Dictionary of {timeframe: signals}
        min_confirmations: Minimum number of confirmations required
        
    Returns:
        Confirmed signal series
    """
    try:
        if not signals_dict:
            return pd.Series()
        
        # Get the index from the first signal series
        index = next(iter(signals_dict.values())).index
        confirmed_signals = pd.Series(0, index=index)
        
        for i in range(len(index)):
            timeframe_signals = []
            for tf, signals in signals_dict.items():
                if i < len(signals):
                    timeframe_signals.append(signals.iloc[i])
            
            # Count buy and sell signals
            buy_count = timeframe_signals.count(1)
            sell_count = timeframe_signals.count(-1)
            
            # Require minimum confirmations
            if buy_count >= min_confirmations:
                confirmed_signals.iloc[i] = 1
            elif sell_count >= min_confirmations:
                confirmed_signals.iloc[i] = -1
        
        return confirmed_signals
    except Exception as e:
        logger.error(f"Error in multi_timeframe_confirmation: {e}")
        return pd.Series()


def breakout_signals(price: pd.Series, resistance: pd.Series, 
                   support: pd.Series, penetration_pct: float = 0.01) -> pd.Series:
    """
    Generate breakout signals
    
    Args:
        price: Price series
        resistance: Resistance level series
        support: Support level series
        penetration_pct: Penetration percentage required
        
    Returns:
        Signal series: 1=BUY_BREAKOUT, -1=SELL_BREAKOUT, 0=NO_BREAKOUT
    """
    try:
        signals = pd.Series(0, index=price.index)
        
        # Buy breakout: price breaks above resistance
        buy_breakout = price > resistance * (1 + penetration_pct)
        signals[buy_breakout] = 1
        
        # Sell breakout: price breaks below support
        sell_breakout = price < support * (1 - penetration_pct)
        signals[sell_breakout] = -1
        
        return signals
    except Exception as e:
        logger.error(f"Error in breakout_signals: {e}")
        return pd.Series(0, index=price.index)


def trend_strength_signals(price: pd.Series, short_ma: pd.Series, 
                          long_ma: pd.Series, adx: pd.Series = None, 
                          adx_threshold: float = 25) -> pd.Series:
    """
    Generate trend strength signals
    
    Args:
        price: Price series
        short_ma: Short moving average
        long_ma: Long moving average
        adx: ADX indicator (optional)
        adx_threshold: ADX threshold for strong trend
        
    Returns:
        Signal series: 1=STRONG_UPTREND, -1=STRONG_DOWNTREND, 0=WEAK_TREND
    """
    try:
        signals = pd.Series(0, index=price.index)
        
        # Basic trend direction
        uptrend = short_ma > long_ma
        downtrend = short_ma < long_ma
        
        if adx is not None:
            # Strong uptrend: uptrend and ADX above threshold
            strong_uptrend = uptrend & (adx >= adx_threshold)
            signals[strong_uptrend] = 1
            
            # Strong downtrend: downtrend and ADX above threshold
            strong_downtrend = downtrend & (adx >= adx_threshold)
            signals[strong_downtrend] = -1
        else:
            # Without ADX, just use MA crossover
            signals[uptrend] = 1
            signals[downtrend] = -1
        
        return signals
    except Exception as e:
        logger.error(f"Error in trend_strength_signals: {e}")
        return pd.Series(0, index=price.index)


# === COMBINATION SIGNAL FUNCTIONS ===

def majority_vote_signals(signal_list: List[pd.Series]) -> pd.Series:
    """
    Generate majority vote combination of signals
    Args:
        signal_list: List of signal series to combine
    Returns:
        Combined signal series: 1=BUY, -1=SELL, 0=HOLD
    """
    try:
        if not signal_list:
            return pd.Series()
        
        # Find common index across all signal series
        common_index = signal_list[0].index
        for series in signal_list[1:]:
            common_index = common_index.intersection(series.index)
        
        if len(common_index) == 0:
            return pd.Series()
        
        # Count votes for each signal type
        buy_votes = pd.Series(0, index=common_index)
        sell_votes = pd.Series(0, index=common_index)
        hold_votes = pd.Series(0, index=common_index)
        
        for series in signal_list:
            aligned_series = series.reindex(common_index)
            buy_votes += (aligned_series == 1) | (aligned_series == 'BUY')
            sell_votes += (aligned_series == -1) | (aligned_series == 'SELL')
            hold_votes += (aligned_series == 0) | (aligned_series == 'HOLD')
        
        # Determine majority vote
        final_signals = pd.Series(0, index=common_index)
        total_signals = len(signal_list)
        majority_threshold = total_signals / 2
        
        final_signals[buy_votes > majority_threshold] = 1
        final_signals[sell_votes > majority_threshold] = -1
        # Hold is default (0)
        
        return final_signals
    except Exception as e:
        logger.error(f"Error in majority_vote_signals: {e}")
        return pd.Series()


def weighted_signals(signal_list: List[Tuple[pd.Series, float]]) -> pd.Series:
    """
    Generate weighted combination of signals
    Args:
        signal_list: List of (signal_series, weight) tuples
    Returns:
        Combined signal series: 1=BUY, -1=SELL, 0=HOLD
    """
    try:
        if not signal_list:
            return pd.Series()
        
        # Find common index across all signal series
        common_index = signal_list[0][0].index
        for series, weight in signal_list[1:]:
            common_index = common_index.intersection(series.index)
        
        if len(common_index) == 0:
            return pd.Series()
        
        # Calculate weighted sum
        weighted_sum = pd.Series(0.0, index=common_index)
        total_weight = 0
        
        for series, weight in signal_list:
            aligned_series = series.reindex(common_index)
            weighted_sum += aligned_series * weight
            total_weight += weight
        
        # Normalize and threshold
        if total_weight > 0:
            normalized_signals = weighted_sum / total_weight
            final_signals = pd.Series(0, index=common_index)
            final_signals[normalized_signals > 0.3] = 1
            final_signals[normalized_signals < -0.3] = -1
            return final_signals
        else:
            return pd.Series(0, index=common_index)
    except Exception as e:
        logger.error(f"Error in weighted_signals: {e}")
        return pd.Series()


# === SIGNAL REGISTRY ===

SIGNAL_REGISTRY = {
    'overbought_oversold': overbought_oversold,
    'ma_crossover': ma_crossover,
    'macd_signals': macd_signals,
    'bollinger_bands_signals': bollinger_bands_signals,
    'stochastic_signals': stochastic_signals,
    'divergence_signals': divergence_signals,
    'multi_timeframe_confirmation': multi_timeframe_confirmation,
    'breakout_signals': breakout_signals,
    'trend_strength_signals': trend_strength_signals,
    'majority_vote_signals': majority_vote_signals,
    'weighted_signals': weighted_signals,
}


def get_signal_function(name: str):
    """
    Get signal function by name
    
    Args:
        name: Signal function name
        
    Returns:
        Signal function
    """
    if name in SIGNAL_REGISTRY:
        return SIGNAL_REGISTRY[name]
    else:
        raise ValueError(f"Signal function '{name}' not found. Available functions: {list(SIGNAL_REGISTRY.keys())}")


def list_signal_functions() -> list:
    """
    List all available signal functions
    
    Returns:
        List of signal function names
    """
    return list(SIGNAL_REGISTRY.keys())


if __name__ == "__main__":
    # Example usage
    print("📊 Available Signal Functions:")
    for signal_func in list_signal_functions():
        print(f"  - {signal_func}")