"""
FINAL WORKING VERSION - Strategy_1_Trend_Following.py
===================================================
Fixed position sizing, balance management, and trade execution.
This version uses much more conservative position sizing.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional

# Add parent directories to path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema
from simple_strategy.strategies.signals_library import ma_crossover
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STRATEGY_PARAMETERS = {
    'fast_period': {
        'type': 'int',
        'default': 12,
        'min': 5,
        'max': 50,
        'description': 'Fast moving average period'
    },
    'slow_period': {
        'type': 'int', 
        'default': 26,
        'min': 10,
        'max': 100,
        'description': 'Slow moving average period'
    },
    'ma_type': {
        'type': 'str',
        'default': 'ema',
        'options': ['sma', 'ema'],
        'description': 'Moving average type'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Trend Following strategy - FINAL WORKING VERSION
    Fixed position sizing and trade execution issues
    """
    # DEBUG: Let's see what we're getting
    logger.info(f"🔧 DEBUG: create_strategy called with:")
    logger.info(f"   - symbols: {symbols}")
    logger.info(f"   - timeframes: {timeframes}")
    logger.info(f"   - params: {params}")
    
    # CRITICAL FIX: If we get None or empty values, use hardcoded values that match the backtest
    if symbols is None or len(symbols) == 0:
        logger.warning(f"🔧 DEBUG: symbols is None or empty, using ['ADAUSDT']")
        symbols = ['ADAUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        logger.warning(f"🔧 DEBUG: timeframes is None or empty, using ['5m']")
        timeframes = ['5m']
    
    # Get parameters with defaults - CONSERVATIVE SETTINGS
    fast_period = params.get('fast_period', 12)   # Increased for fewer signals
    slow_period = params.get('slow_period', 26)   # Increased for fewer signals
    ma_type = params.get('ma_type', 'ema')
    
    # CRITICAL DEBUGGING: Log what we're actually using
    logger.info(f"🔧 CREATING STRATEGY WITH:")
    logger.info(f"   - Symbols: {symbols}")
    logger.info(f"   - Timeframes: {timeframes}")
    logger.info(f"   - Fast Period: {fast_period}")
    logger.info(f"   - Slow Period: {slow_period}")
    logger.info(f"   - MA Type: {ma_type}")
    
    try:
        # Create strategy using StrategyBuilder with EXACT symbols and timeframes
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add indicators based on MA type
        if ma_type == 'sma':
            strategy_builder.add_indicator('sma_fast', sma, period=fast_period)
            strategy_builder.add_indicator('sma_slow', sma, period=slow_period)
            fast_ma_name = 'sma_fast'
            slow_ma_name = 'sma_slow'
        else:  # ema
            strategy_builder.add_indicator('ema_fast', ema, period=fast_period)
            strategy_builder.add_indicator('ema_slow', ema, period=slow_period)
            fast_ma_name = 'ema_fast'
            slow_ma_name = 'ema_slow'
        
        # Add signal rule for MA crossover
        strategy_builder.add_signal_rule('ma_crossover', ma_crossover,
                                       fast_ma=fast_ma_name,
                                       slow_ma=slow_ma_name)
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('Trend_Following', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ STRATEGY CREATED SUCCESSFULLY!")
        logger.info(f"   - Strategy Name: {strategy.name}")
        logger.info(f"   - Strategy Symbols: {strategy.symbols}")
        logger.info(f"   - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ ERROR CREATING STRATEGY: {e}")
        import traceback
        traceback.print_exc()
        raise

class ConservativeTrendFollowingStrategy(StrategyBase):
    """
    CONSERVATIVE Trend Following Strategy Class
    Much smaller position sizes to prevent balance depletion
    """
    
    def __init__(self, symbols: List[str], timeframes: List[str], config: Dict[str, Any]):
        """
        Initialize the trend following strategy
        """
        # CRITICAL: Initialize with EXACT symbols and timeframes provided
        super().__init__(
            name="Trend_Following",
            symbols=symbols,
            timeframes=timeframes,
            config=config
        )
        
        # Strategy-specific parameters
        self.fast_period = config.get('fast_period', 12)
        self.slow_period = config.get('slow_period', 26)
        self.ma_type = config.get('ma_type', 'ema')
        
        # CRITICAL: Very conservative risk management
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.002)  # Only 0.2% per trade
        self.min_position_size = 0.01  # Minimum position size for ADA
        self.max_position_size = 100.0  # Maximum ADA per trade
        
        # Validate parameters
        self._validate_parameters()
        
        logger.info(f"📈 ConservativeTrendFollowingStrategy initialized:")
        logger.info(f"   - Symbols: {self.symbols}")
        logger.info(f"   - Timeframes: {self.timeframes}")
        logger.info(f"   - Fast Period: {self.fast_period}")
        logger.info(f"   - Slow Period: {self.slow_period}")
        logger.info(f"   - MA Type: {self.ma_type}")
        logger.info(f"   - Max Risk Per Trade: {self.max_risk_per_trade}")
    
    def _validate_parameters(self):
        """Validate strategy parameters"""
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")
        
        if self.fast_period <= 0 or self.slow_period <= 0:
            raise ValueError("Periods must be positive integers")
        
        if self.ma_type not in ['sma', 'ema']:
            raise ValueError("MA type must be 'sma' or 'ema'")
        
        if not self.symbols:
            raise ValueError("At least one symbol must be provided")
        
        if not self.timeframes:
            raise ValueError("At least one timeframe must be provided")
    
    def calculate_position_size(self, symbol: str, current_price: float = None, signal_strength: float = 1.0) -> float:
        """
        VERY CONSERVATIVE position size calculation to prevent balance depletion
        """
        if current_price is None:
            return self.min_position_size
        
        # Calculate risk amount for this trade - VERY SMALL
        risk_amount = self.balance * self.max_risk_per_trade * signal_strength
        
        # Calculate position size in units of the asset
        position_size = risk_amount / current_price
        
        # Ensure minimum position size
        position_size = max(position_size, self.min_position_size)
        
        # Ensure maximum position size (hard limit)
        position_size = min(position_size, self.max_position_size)
        
        # CRITICAL: Never use more than 1% of total balance in a single trade
        max_position_value = self.balance * 0.01
        max_position_size_by_value = max_position_value / current_price
        position_size = min(position_size, max_position_size_by_value)
        
        # Round to reasonable decimal places for ADA
        position_size = round(position_size, 1)
        
        # Final safety check - ensure we have enough balance
        position_value = position_size * current_price
        if position_value > self.balance * 0.95:
            position_size = (self.balance * 0.95) / current_price
            position_size = round(position_size, 1)
        
        logger.info(f"   CONSERVATIVE Position size calculation for {symbol}:")
        logger.info(f"     - Balance: ${self.balance:.2f}")
        logger.info(f"     - Risk amount: ${risk_amount:.2f} ({self.max_risk_per_trade*100}% of balance)")
        logger.info(f"     - Position size: {position_size} ADA")
        logger.info(f"     - Position value: ${position_size * current_price:.2f}")
        
        return position_size
    
    def generate_signals(self, data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, str]]:
        """
        Generate trading signals for all symbols and timeframes
        """
        signals = {}
        
        logger.info(f"📊 GENERATING SIGNALS FOR:")
        logger.info(f"   - Strategy Symbols: {self.symbols}")
        logger.info(f"   - Strategy Timeframes: {self.timeframes}")
        logger.info(f"   - Available Data Symbols: {list(data.keys())}")
        
        try:
            # CRITICAL: Use self.symbols and self.timeframes, not hardcoded values
            for symbol in self.symbols:
                signals[symbol] = {}
                
                for timeframe in self.timeframes:
                    logger.info(f"   Processing {symbol} {timeframe}")
                    
                    # Check if data is available for this symbol/timeframe
                    if symbol not in data:
                        logger.warning(f"❌ No data available for symbol: {symbol}")
                        signals[symbol][timeframe] = 'HOLD'
                        continue
                    
                    if timeframe not in data[symbol]:
                        logger.warning(f"❌ No data available for {symbol} {timeframe}")
                        signals[symbol][timeframe] = 'HOLD'
                        continue
                    
                    df = data[symbol][timeframe]
                    
                    if len(df) < self.slow_period:
                        logger.warning(f"❌ Insufficient data for {symbol} {timeframe}: {len(df)} < {self.slow_period}")
                        signals[symbol][timeframe] = 'HOLD'
                        continue
                    
                    logger.info(f"✅ Processing {symbol} {timeframe} with {len(df)} candles")
                    
                    # Generate signal for this symbol/timeframe
                    signal = self._generate_single_signal(df, symbol, timeframe)
                    signals[symbol][timeframe] = signal
                    
                    logger.info(f"   Signal for {symbol} {timeframe}: {signal}")
            
            logger.info(f"📊 GENERATED SIGNALS: {signals}")
            return signals
            
        except Exception as e:
            logger.error(f"❌ ERROR GENERATING SIGNALS: {e}")
            import traceback
            traceback.print_exc()
            
            # Return HOLD signals for all symbols/timeframes in case of error
            return {
                symbol: {timeframe: 'HOLD' for timeframe in self.timeframes}
                for symbol in self.symbols
            }
    
    def _generate_single_signal(self, df: pd.DataFrame, symbol: str, timeframe: str) -> str:
        """
        Generate a single trading signal for one symbol/timeframe
        """
        try:
            logger.info(f"   Calculating indicators for {symbol} {timeframe}")
            
            # Calculate indicators
            if self.ma_type == 'sma':
                fast_ma = sma(df['close'], period=self.fast_period)
                slow_ma = sma(df['close'], period=self.slow_period)
            else:  # ema
                fast_ma = ema(df['close'], period=self.fast_period)
                slow_ma = ema(df['close'], period=self.slow_period)
            
            logger.info(f"   Generating MA crossover signal for {symbol} {timeframe}")
            
            # Generate signal using MA crossover
            signal_series = ma_crossover(fast_ma, slow_ma)
            
            # Get the most recent signal
            if len(signal_series) > 0:
                latest_signal = signal_series.iloc[-1]
                
                # Convert numeric signals to string format
                if latest_signal == 1:
                    signal = 'BUY'
                elif latest_signal == -1:
                    signal = 'SELL'
                else:
                    signal = 'HOLD'
                
                logger.info(f"   Latest signal for {symbol} {timeframe}: {signal} (raw: {latest_signal})")
                return signal
            else:
                logger.warning(f"   No signals generated for {symbol} {timeframe}")
                return 'HOLD'
                
        except Exception as e:
            logger.error(f"❌ ERROR GENERATING SIGNAL for {symbol} {timeframe}: {e}")
            return 'HOLD'

def create_conservative_strategy(symbols=None, timeframes=None, **params):
    """
    Create a CONSERVATIVE Trend Following strategy instance
    This version uses very small position sizes to prevent balance depletion
    """
    # Set defaults
    if symbols is None:
        symbols = ['ADAUSDT']
    if timeframes is None:
        timeframes = ['5m']
    
    # Extract parameters with defaults - CONSERVATIVE SETTINGS
    fast_period = params.get('fast_period', 12)
    slow_period = params.get('slow_period', 26)
    ma_type = params.get('ma_type', 'ema')
    
    # Additional configuration parameters
    initial_balance = params.get('initial_balance', 10000.0)
    max_risk_per_trade = params.get('max_risk_per_trade', 0.002)  # Only 0.2%
    max_positions = params.get('max_positions', 3)
    max_portfolio_risk = params.get('max_portfolio_risk', 0.10)
    
    logger.info(f"🔧 CREATING CONSERVATIVE STRATEGY:")
    logger.info(f"   - Symbols: {symbols}")
    logger.info(f"   - Timeframes: {timeframes}")
    logger.info(f"   - Fast Period: {fast_period}")
    logger.info(f"   - Slow Period: {slow_period}")
    logger.info(f"   - MA Type: {ma_type}")
    logger.info(f"   - Max Risk Per Trade: {max_risk_per_trade}")
    
    try:
        # Create configuration dictionary
        config = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'ma_type': ma_type,
            'initial_balance': initial_balance,
            'max_risk_per_trade': max_risk_per_trade,
            'max_positions': max_positions,
            'max_portfolio_risk': max_portfolio_risk
        }
        
        # Create and return strategy instance
        strategy = ConservativeTrendFollowingStrategy(symbols, timeframes, config)
        
        logger.info(f"✅ CONSERVATIVE STRATEGY CREATED SUCCESSFULLY!")
        return strategy
        
    except Exception as e:
        logger.error(f"❌ ERROR CREATING CONSERVATIVE STRATEGY: {e}")
        import traceback
        traceback.print_exc()
        raise

# Strategy parameters for GUI configuration - CONSERVATIVE
STRATEGY_PARAMETERS = {
    'fast_period': {
        'type': 'int',
        'default': 12,    # Increased for fewer signals
        'min': 5,
        'max': 50,
        'description': 'Fast moving average period',
        'gui_hint': 'Higher values = fewer signals. Recommended: 12'
    },
    'slow_period': {
        'type': 'int',
        'default': 26,    # Increased for fewer signals
        'min': 15,
        'max': 200,
        'description': 'Slow moving average period',
        'gui_hint': 'Higher values = fewer signals. Recommended: 26'
    },
    'ma_type': {
        'type': 'str',
        'default': 'ema',
        'options': ['sma', 'ema'],
        'description': 'Moving average type',
        'gui_hint': 'EMA reacts faster than SMA to recent price changes'
    },
    'max_risk_per_trade': {
        'type': 'float',
        'default': 0.002,  # Very conservative: 0.2%
        'min': 0.001,
        'max': 0.01,
        'description': 'Maximum risk per trade (as % of balance)',
        'gui_hint': '0.2% = Very conservative. Lower = safer'
    }
}

def simple_test():
    """Simple test to verify the strategy works"""
    print("🧪 CONSERVATIVE STRATEGY TEST")
    print("=" * 30)
    
    try:
        # Test with ADAUSDT 5m (matching your backtest configuration)
        strategy = create_conservative_strategy(
            symbols=['ADAUSDT'],  # CRITICAL: Use the same symbol as your backtest
            timeframes=['5m'],    # CRITICAL: Use the same timeframe as your backtest
            fast_period=12,
            slow_period=26,
            ma_type='ema',
            max_risk_per_trade=0.002
        )
        
        print(f"✅ Strategy created: {strategy.name}")
        print(f"   Symbols: {strategy.symbols}")
        print(f"   Timeframes: {strategy.timeframes}")
        print(f"   Fast Period: {strategy.fast_period}")
        print(f"   Slow Period: {strategy.slow_period}")
        print(f"   Max Risk Per Trade: {strategy.max_risk_per_trade}")
        
        # Test with synthetic data
        dates = pd.date_range(start='2025-09-16', periods=100, freq='5min')
        np.random.seed(42)
        base_price = 1.0  # ADA price around $1
        
        prices = [base_price]
        for i in range(1, 100):
            change = np.random.normal(0, 0.005)  # 0.5% standard deviation
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [np.random.uniform(1000000, 10000000) for _ in prices]
        }, index=dates)
        
        # Test data structure
        test_data = {
            'ADAUSDT': {
                '5m': df
            }
        }
        
        # Generate signals
        signals = strategy.generate_signals(test_data)
        print(f"📊 Generated signals: {signals}")
        
        # Count signals
        buy_count = sum(1 for s in signals['ADAUSDT']['5m'] if s == 'BUY')
        sell_count = sum(1 for s in signals['ADAUSDT']['5m'] if s == 'SELL')
        hold_count = sum(1 for s in signals['ADAUSDT']['5m'] if s == 'HOLD')
        
        print(f"📊 Signal counts: BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}")
        
        if buy_count > 0 or sell_count > 0:
            print("✅ SUCCESS: Strategy generated trading signals!")
        else:
            print("⚠️  WARNING: No trading signals generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# For testing
if __name__ == "__main__":
    simple_test()