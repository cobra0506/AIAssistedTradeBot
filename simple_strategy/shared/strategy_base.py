# strategy_base.py - Abstract base class and building blocks for strategies
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyBase(ABC):
    """
    Abstract base class for all trading strategies.
    Provides common functionality and enforces consistent interface.
    """
    
    def __init__(self, name: str, symbols: List[str], timeframes: List[str], config: Dict[str, Any]):
        """
        Initialize strategy with configuration.
        
        Args:
            name: Strategy name
            symbols: List of trading symbols
            timeframes: List of timeframes to analyze
            config: Strategy configuration parameters
        """
        self.name = name
        self.symbols = symbols
        self.timeframes = timeframes
        self.config = config
        
        # Strategy state
        self.positions = {}  # symbol -> position info
        self.balance = config.get('initial_balance', 10000.0)
        self.initial_balance = self.balance
        
        # Risk management parameters
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.01)  # 1% of balance
        self.max_positions = config.get('max_positions', 3)
        self.max_portfolio_risk = config.get('max_portfolio_risk', 0.10)  # 10% of balance
        
        # Performance tracking
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Strategy {name} initialized with symbols: {symbols}, timeframes: {timeframes}")
    
    @abstractmethod
    def generate_signals(self, data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, str]]:
        """
        Generate trading signals for all symbols and timeframes.
        Must be implemented by subclasses.
        
        Args:
            data: Nested dictionary {symbol: {timeframe: DataFrame}}
            
        Returns:
            Dictionary {symbol: {timeframe: signal}} where signal is 'BUY', 'SELL', or 'HOLD'
        """
        pass
    
    def calculate_position_size(self, symbol: str, signal_strength: float = 1.0) -> float:
        """
        Calculate position size based on risk management rules.
        Args:
            symbol: Trading symbol
            signal_strength: Strength of the signal (0.0 to 1.0)
        Returns:
            Position size in base currency
        """
        # FIX: Clamp signal_strength to be non-negative
        signal_strength = max(0.0, signal_strength)
        
        # Calculate risk amount
        risk_amount = self.balance * self.max_risk_per_trade * signal_strength
        
        # Get current price (would need to be passed in or fetched)
        # For now, use a placeholder - in practice, this would come from data
        current_price = self._get_current_price(symbol)
        
        # Calculate position size
        if current_price > 0:
            position_size = risk_amount / current_price
        else:
            position_size = 0
        
        # Apply maximum position limits
        max_position_size = self.balance * 0.2  # Max 20% of balance in single position
        position_size = min(position_size, max_position_size)
        
        logger.debug(f"Calculated position size for {symbol}: {position_size} (risk: {risk_amount})")
        return position_size
    
    def validate_signal(self, symbol: str, signal: str, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate signal against risk management rules.
        
        Args:
            symbol: Trading symbol
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            data: Current market data
            
        Returns:
            True if signal is valid, False otherwise
        """
        if signal == 'HOLD':
            return True
        
        # Check if we already have maximum positions
        if signal == 'BUY' and len(self.positions) >= self.max_positions:
            logger.warning(f"Signal validation failed: Maximum positions reached ({len(self.positions)}/{self.max_positions})")
            return False
        
        # Check portfolio risk
        if signal == 'BUY':
            portfolio_risk = self._calculate_portfolio_risk()
            if portfolio_risk >= self.max_portfolio_risk:
                logger.warning(f"Signal validation failed: Maximum portfolio risk reached ({portfolio_risk:.2%})")
                return False
        
        # Check if we have position to sell
        if signal == 'SELL' and symbol not in self.positions:
            logger.warning(f"Signal validation failed: No position to sell for {symbol}")
            return False
        
        return True
    
    def get_strategy_state(self) -> Dict[str, Any]:
        """
        Get current strategy state for logging and monitoring.
        
        Returns:
            Dictionary with strategy state information
        """
        return {
            'name': self.name,
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'total_return': (self.balance - self.initial_balance) / self.initial_balance,
            'open_positions': len(self.positions),
            'total_trades': len(self.trades),
            'symbols': self.symbols,
            'timeframes': self.timeframes,
            'config': self.config
        }
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        Placeholder method - should be overridden or data should be passed in.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price
        """
        # This is a placeholder - in practice, this would come from the data feeder
        logger.warning(f"Using placeholder price for {symbol}")
        return 50000.0  # Placeholder price
    
    def _calculate_portfolio_risk(self) -> float:
        """
        Calculate current portfolio risk.
        
        Returns:
            Portfolio risk as percentage of balance
        """
        # Simple calculation - in practice, this would be more sophisticated
        total_position_value = sum(pos.get('value', 0) for pos in self.positions.values())
        return total_position_value / self.balance if self.balance > 0 else 0

# ============================================================================
# INDICATOR BUILDING BLOCKS
# ============================================================================

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price series (typically closing prices)
        period: RSI period (default: 14)
        
    Returns:
        RSI values as pandas Series
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        data: Price series
        period: SMA period
        
    Returns:
        SMA values as pandas Series
    """
    return data.rolling(window=period).mean()

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        data: Price series
        period: EMA period
        
    Returns:
        EMA values as pandas Series
    """
    return data.ewm(span=period, adjust=False).mean()

def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> tuple:
    """
    Calculate Stochastic Oscillator.
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
        
    Returns:
        Tuple of (%K, %D) as pandas Series
    """
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    
    k_percent = 100 * ((data['close'] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d_period).mean()
    
    return k_percent, d_percent

def calculate_srsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Stochastic RSI.
    
    Args:
        data: Price series
        period: SRSI period (default: 14)
        
    Returns:
        SRSI values as pandas Series
    """
    rsi = calculate_rsi(data, period)
    srsi = calculate_stochastic(pd.DataFrame({'high': rsi, 'low': rsi, 'close': rsi}), period, 3)[0]
    return srsi

# ============================================================================
# SIGNAL BUILDING BLOCKS
# ============================================================================

def check_oversold(indicator_value: pd.Series, threshold: float = 20) -> pd.Series:
    """
    Check if indicator is in oversold territory.
    
    Args:
        indicator_value: Indicator values
        threshold: Oversold threshold (default: 20)
        
    Returns:
        Boolean series indicating oversold condition
    """
    return indicator_value <= threshold

def check_overbought(indicator_value: pd.Series, threshold: float = 80) -> pd.Series:
    """
    Check if indicator is in overbought territory.
    
    Args:
        indicator_value: Indicator values
        threshold: Overbought threshold (default: 80)
        
    Returns:
        Boolean series indicating overbought condition
    """
    return indicator_value >= threshold

def check_crossover(fast_ma: pd.Series, slow_ma: pd.Series) -> pd.Series:
    """
    Check for moving average crossover.
    Args:
        fast_ma: Fast moving average series
        slow_ma: Slow moving average series
    Returns:
        Boolean series indicating crossover (fast crosses above slow)
    """
    # FIXED: Complete the implementation that was missing
    # A crossover happens when:
    # 1. Current fast > current slow AND
    # 2. Previous fast <= previous slow
    
    # Create shifted series for comparison
    fast_prev = fast_ma.shift(1)
    slow_prev = slow_ma.shift(1)
    
    # Crossover condition
    crossover = (fast_ma > slow_ma) & (fast_prev <= slow_prev)
    
    # First value can never be a crossover (no previous data)
    crossover.iloc[0] = False
    
    return crossover

def check_crossunder(fast_ma: pd.Series, slow_ma: pd.Series) -> pd.Series:
    """
    Check for moving average crossunder.
    Args:
        fast_ma: Fast moving average series
        slow_ma: Slow moving average series
    Returns:
        Boolean series indicating crossunder (fast crosses below slow)
    """
    # FIXED: Simpler, more direct loop-based approach
    
    crossunder = pd.Series(False, index=fast_ma.index)
    
    # Start from index 1 (need at least one previous point)
    for i in range(1, len(fast_ma)):
        # Current values
        fast_current = fast_ma.iloc[i]
        slow_current = slow_ma.iloc[i]
        
        # Previous values
        fast_prev = fast_ma.iloc[i-1]
        slow_prev = slow_ma.iloc[i-1]
        
        # Check if we have a valid crossunder
        # 1. Current fast < current slow
        # 2. Previous fast >= previous slow
        if (fast_current < slow_current) and (fast_prev >= slow_prev):
            crossunder.iloc[i] = True
    
    return crossunder

# ============================================================================
# MULTI-TIMEFRAME BUILDING BLOCKS
# ============================================================================

def align_multi_timeframe_data(data_1m: pd.DataFrame, data_5m: pd.DataFrame, 
                             data_15m: pd.DataFrame, timestamp: datetime) -> Dict[str, pd.Series]:
    """
    Align data across multiple timeframes for a specific timestamp.
    
    Args:
        data_1m: 1-minute timeframe data
        data_5m: 5-minute timeframe data
        data_15m: 15-minute timeframe data
        timestamp: Target timestamp for alignment
        
    Returns:
        Dictionary with aligned data for each timeframe
    """
    aligned_data = {}
    
    for tf_name, df in [('1m', data_1m), ('5m', data_5m), ('15m', data_15m)]:
        if df is not None and len(df) > 0:
            # Find the most recent data point at or before the timestamp
            mask = df.index <= timestamp
            if mask.any():
                latest_data = df[mask].iloc[-1]
                aligned_data[tf_name] = latest_data
    
    return aligned_data

def check_multi_timeframe_condition(indicators_dict: Dict[str, Dict[str, pd.Series]],
                                  condition_func: callable) -> bool:
    """
    Check condition across multiple timeframes.
    Args:
        indicators_dict: Nested dictionary {timeframe: {indicator_name: values}}
        condition_func: Function to evaluate condition on indicator values
                       (takes dict of current values and returns boolean)
    Returns:
        Boolean indicating if condition is met
    """
    # FIXED: Handle both Series and scalar values properly
    current_values = {}
    
    for timeframe, indicators in indicators_dict.items():
        current_values[timeframe] = {}
        for indicator_name, values in indicators.items():
            # FIXED: Handle both pandas Series and scalar values
            if isinstance(values, pd.Series):
                if len(values) > 0:
                    # Get the latest value (last non-NaN value)
                    latest_value = values.dropna().iloc[-1] if values.dropna().any() else values.iloc[-1]
                    current_values[timeframe][indicator_name] = latest_value
                else:
                    # Empty series, use NaN
                    current_values[timeframe][indicator_name] = np.nan
            else:
                # Scalar value, use as-is
                current_values[timeframe][indicator_name] = values
    
    try:
        return condition_func(current_values)
    except Exception as e:
        logger.warning(f"Error evaluating multi-timeframe condition: {e}")
        return False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_data_format(data: pd.DataFrame) -> bool:
    """
    Validate that data has required columns and format.
    
    Args:
        data: DataFrame to validate
        
    Returns:
        True if data format is valid
    """
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    return all(col in data.columns for col in required_columns)

def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data by handling missing values and outliers.
    
    Args:
        data: Raw data DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Fix: Use ffill() instead of deprecated fillna(method='ffill')
    data = data.ffill()
    
    # Handle infinite values
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna()
    
    return data

def get_latest_data_point(data: pd.DataFrame, timestamp: datetime) -> pd.Series:
    """
    Get the latest data point at or before the specified timestamp.
    Args:
        data: DataFrame with datetime index
        timestamp: Target timestamp
    Returns:
        pandas Series with the latest data point, or None if no data available
    """
    if data is None or len(data) == 0:
        return None
    
    # Find data points at or before the timestamp
    mask = data.index <= timestamp
    if not mask.any():
        return None
    
    # Get the most recent data point
    latest_data = data[mask].iloc[-1]
    return latest_data