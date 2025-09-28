"""
Building Block Indicators Library
=================================

This library contains ALL technical indicators that can be used in strategy building.
Each indicator is a standalone function that can be called independently.

Author: AI Assisted TradeBot Team
Date: 2025
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


# === TREND INDICATORS ===

def sma(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Simple Moving Average
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        SMA series
    """
    try:
        return data.rolling(window=period).mean()
    except Exception as e:
        logger.error(f"Error calculating SMA: {e}")
        return pd.Series(index=data.index, dtype=float)


def ema(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Exponential Moving Average
    Args:
        data: Price series
        period: Lookback period
    Returns:
        EMA series
    """
    try:
        # Handle edge case: period larger than data length
        if period > len(data):
            return pd.Series([np.nan] * len(data), index=data.index, dtype=float)
        
        # Handle edge case: period <= 0
        if period <= 0:
            return pd.Series([np.nan] * len(data), index=data.index, dtype=float)
        
        # Initialize result series with NaN values
        ema_series = pd.Series([np.nan] * len(data), index=data.index, dtype=float)
        
        # Find the first 'period' non-NaN values
        non_nan_indices = []
        non_nan_values = []
        for i, val in enumerate(data):
            if not pd.isna(val):
                non_nan_indices.append(i)
                non_nan_values.append(val)
                if len(non_nan_values) >= period:
                    break
        
        # If we don't have enough non-NaN values, return all NaN
        if len(non_nan_values) < period:
            return ema_series
        
        # First EMA value is the SMA of the first 'period' non-NaN values
        first_ema = sum(non_nan_values) / period
        ema_series.iloc[non_nan_indices[-1]] = first_ema
        
        # Calculate smoothing factor
        smoothing = 2 / (period + 1)
        
        # Calculate subsequent EMA values
        for i in range(non_nan_indices[-1] + 1, len(data)):
            if not pd.isna(data.iloc[i]):
                ema_series.iloc[i] = smoothing * data.iloc[i] + (1 - smoothing) * ema_series.iloc[i - 1]
        
        return ema_series
    except Exception as e:
        logger.error(f"Error calculating EMA: {e}")
        return pd.Series(index=data.index, dtype=float)


def wma(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Weighted Moving Average
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        WMA series
    """
    try:
        weights = np.arange(1, period + 1)
        weights = weights / weights.sum()
        return data.rolling(window=period).apply(lambda x: np.dot(x, weights), raw=True)
    except Exception as e:
        logger.error(f"Error calculating WMA: {e}")
        return pd.Series(index=data.index, dtype=float)


def dema(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Double Exponential Moving Average
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        DEMA series
    """
    try:
        ema1 = ema(data, period)
        ema2 = ema(ema1, period)
        return 2 * ema1 - ema2
    except Exception as e:
        logger.error(f"Error calculating DEMA: {e}")
        return pd.Series(index=data.index, dtype=float)


def tema(data: pd.Series, period: int = 20) -> pd.Series:
    """
    Triple Exponential Moving Average
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        TEMA series
    """
    try:
        ema1 = ema(data, period)
        ema2 = ema(ema1, period)
        ema3 = ema(ema2, period)
        return 3 * ema1 - 3 * ema2 + ema3
    except Exception as e:
        logger.error(f"Error calculating TEMA: {e}")
        return pd.Series(index=data.index, dtype=float)


# === MOMENTUM INDICATORS ===

def rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        RSI series
    """
    try:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return pd.Series(index=data.index, dtype=float)


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
              k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    Stochastic Oscillator
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        k_period: %K period
        d_period: %D period
        
    Returns:
        Tuple of (%K series, %D series)
    """
    try:
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    except Exception as e:
        logger.error(f"Error calculating Stochastic: {e}")
        return pd.Series(index=close.index, dtype=float), pd.Series(index=close.index, dtype=float)


def srsi(data: pd.Series, period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    Stochastic RSI
    
    Args:
        data: Price series
        period: RSI period
        d_period: %D period
        
    Returns:
        Tuple of (SRSI-K series, SRSI-D series)
    """
    try:
        rsi_values = rsi(data, period)
        lowest_low = rsi_values.rolling(window=period).min()
        highest_high = rsi_values.rolling(window=period).max()
        srsi_k = 100 * ((rsi_values - lowest_low) / (highest_high - lowest_low))
        srsi_d = srsi_k.rolling(window=d_period).mean()
        return srsi_k, srsi_d
    except Exception as e:
        logger.error(f"Error calculating SRSI: {e}")
        return pd.Series(index=data.index, dtype=float), pd.Series(index=data.index, dtype=float)


def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, 
         signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Moving Average Convergence Divergence
    
    Args:
        data: Price series
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
        
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    try:
        ema_fast = ema(data, fast_period)
        ema_slow = ema(data, slow_period)
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return (pd.Series(index=data.index, dtype=float), 
                pd.Series(index=data.index, dtype=float), 
                pd.Series(index=data.index, dtype=float))


def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """
    Commodity Channel Index
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period
        
    Returns:
        CCI series
    """
    try:
        tp = (high + low + close) / 3
        sma_tp = sma(tp, period)
        mad = tp.rolling(window=period).apply(lambda x: np.fabs(x - x.mean()).mean())
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci
    except Exception as e:
        logger.error(f"Error calculating CCI: {e}")
        return pd.Series(index=close.index, dtype=float)


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Williams %R
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period
        
    Returns:
        Williams %R series
    """
    try:
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr
    except Exception as e:
        logger.error(f"Error calculating Williams %R: {e}")
        return pd.Series(index=close.index, dtype=float)


# === VOLATILITY INDICATORS ===

def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands
    
    Args:
        data: Price series
        period: Lookback period
        std_dev: Standard deviation multiplier
        
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    try:
        middle_band = sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        return upper_band, middle_band, lower_band
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return (pd.Series(index=data.index, dtype=float), 
                pd.Series(index=data.index, dtype=float), 
                pd.Series(index=data.index, dtype=float))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Average True Range
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: Lookback period
        
    Returns:
        ATR series
    """
    try:
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    except Exception as e:
        logger.error(f"Error calculating ATR: {e}")
        return pd.Series(index=close.index, dtype=float)


# === VOLUME INDICATORS ===

def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Volume Simple Moving Average
    
    Args:
        volume: Volume series
        period: Lookback period
        
    Returns:
        Volume SMA series
    """
    try:
        return sma(volume, period)
    except Exception as e:
        logger.error(f"Error calculating Volume SMA: {e}")
        return pd.Series(index=volume.index, dtype=float)


def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On Balance Volume
    
    Args:
        close: Close price series
        volume: Volume series
        
    Returns:
        OBV series
    """
    try:
        obv = np.where(close > close.shift(1), volume, 
                      np.where(close < close.shift(1), -volume, 0))
        return pd.Series(obv, index=close.index).cumsum()
    except Exception as e:
        logger.error(f"Error calculating OBV: {e}")
        return pd.Series(index=close.index, dtype=float)


# === UTILITY FUNCTIONS ===

def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect crossover between two series
    
    Args:
        series1: First series
        series2: Second series
        
    Returns:
        Boolean series where crossover occurs
    """
    try:
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))
    except Exception as e:
        logger.error(f"Error detecting crossover: {e}")
        return pd.Series(index=series1.index, dtype=bool)


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect crossunder between two series
    
    Args:
        series1: First series
        series2: Second series
        
    Returns:
        Boolean series where crossunder occurs
    """
    try:
        return (series1 < series2) & (series1.shift(1) >= series2.shift(1))
    except Exception as e:
        logger.error(f"Error detecting crossunder: {e}")
        return pd.Series(index=series1.index, dtype=bool)


def highest(data: pd.Series, period: int) -> pd.Series:
    """
    Highest value over period
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        Highest value series
    """
    try:
        return data.rolling(window=period).max()
    except Exception as e:
        logger.error(f"Error calculating highest: {e}")
        return pd.Series(index=data.index, dtype=float)


def lowest(data: pd.Series, period: int) -> pd.Series:
    """
    Lowest value over period
    
    Args:
        data: Price series
        period: Lookback period
        
    Returns:
        Lowest value series
    """
    try:
        return data.rolling(window=period).min()
    except Exception as e:
        logger.error(f"Error calculating lowest: {e}")
        return pd.Series(index=data.index, dtype=float)


# === INDICATOR REGISTRY ===
# This makes it easy to get all available indicators

INDICATOR_REGISTRY = {
    'sma': sma,
    'ema': ema,
    'wma': wma,
    'dema': dema,
    'tema': tema,
    'rsi': rsi,
    'stochastic': stochastic,
    'srsi': srsi,
    'macd': macd,
    'cci': cci,
    'williams_r': williams_r,
    'bollinger_bands': bollinger_bands,
    'atr': atr,
    'volume_sma': volume_sma,
    'on_balance_volume': on_balance_volume,
    'crossover': crossover,
    'crossunder': crossunder,
    'highest': highest,
    'lowest': lowest,
}


def get_indicator(name: str):
    """
    Get indicator function by name
    
    Args:
        name: Indicator name
        
    Returns:
        Indicator function
    """
    if name in INDICATOR_REGISTRY:
        return INDICATOR_REGISTRY[name]
    else:
        raise ValueError(f"Indicator '{name}' not found. Available indicators: {list(INDICATOR_REGISTRY.keys())}")


def list_indicators() -> list:
    """
    List all available indicators
    
    Returns:
        List of indicator names
    """
    return list(INDICATOR_REGISTRY.keys())


if __name__ == "__main__":
    # Example usage
    print("📊 Available Indicators:")
    for indicator in list_indicators():
        print(f"  - {indicator}")