"""
Strategy: Working Example
This strategy demonstrates what we've confirmed to be working:
- GUI detection and parameter assignment
- Symbol and timeframe assignment
- Data loading
- Manual indicator calculation (for verification)

NOTE: This strategy does NOT generate trades because StrategyBuilder
indicator integration and signal generation are still broken.
"""
import sys
import os
import pandas as pd
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import sma

logger = logging.getLogger(__name__)

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Working example demonstrating confirmed functionality
    """
    # Use what we receive from GUI (this works!)
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['60m']
    
    # Get parameters from GUI (this works!)
    sma_period = params.get('sma_period', 20)
    
    logger.info("🔍 WORKING EXAMPLE - CONFIRMED FUNCTIONALITY:")
    logger.info(f"   - GUI Parameters received: {params}")
    logger.info(f"   - Using symbols: {symbols}")
    logger.info(f"   - Using timeframes: {timeframes}")
    logger.info(f"   - SMA period: {sma_period}")
    
    # Create strategy (this works!)
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicator (calculation works, but integration doesn't)
    strategy.add_indicator('working_sma', sma, period=sma_period)
    
    # Add a signal function (this will fail, but we demonstrate the structure)
    def working_signal_function(indicator_data):
        """
        This shows how signal functions should work.
        Currently fails due to StrategyBuilder integration issues.
        """
        logger.info(f"🔧 Signal function called with: {type(indicator_data)}")
        if isinstance(indicator_data, pd.Series):
            logger.info(f"🔧 Indicator data shape: {indicator_data.shape}")
            return pd.Series('BUY', index=indicator_data.index)
        else:
            logger.error(f"🔧 Expected pandas Series, got {type(indicator_data)}")
            return pd.Series('HOLD', index=range(10))
    
    strategy.add_signal_rule('working_signal', working_signal_function)
    strategy.set_signal_combination('majority_vote')
    strategy.set_strategy_info('Working_Example', '1.0.0')
    
    # Build strategy
    built_strategy = strategy.build()
    
    # Add verification of working parts
    original_generate_signals = built_strategy.generate_signals
    
    def debug_generate_signals(data):
        logger.info("🔍 WORKING PARTS VERIFICATION:")
        
        for symbol in data:
            for timeframe in data[symbol]:
                df = data[symbol][timeframe]
                logger.info(f"   - {symbol} {timeframe}:")
                logger.info(f"     - ✅ Data loaded: {df.shape} rows")
                logger.info(f"     - ✅ Columns: {list(df.columns)}")
                logger.info(f"     - ✅ Date range: {df.index.min()} to {df.index.max()}")
                
                # Verify manual indicator calculation works
                try:
                    manual_sma = sma(df['close'], period=sma_period)
                    logger.info(f"     - ✅ Manual SMA calculation works: {manual_sma.notna().sum()} valid values")
                except Exception as e:
                    logger.error(f"     - ❌ Manual SMA failed: {e}")
                
                # Check StrategyBuilder integration (this fails)
                if 'working_sma' in df.columns:
                    logger.info(f"     - ✅ StrategyBuilder SMA found in DataFrame")
                else:
                    logger.info(f"     - ❌ StrategyBuilder SMA NOT found in DataFrame")
                    logger.info(f"     -   Available columns: {list(df.columns)}")
        
        # Call original function
        result = original_generate_signals(data)
        
        # Check result format
        for symbol in result:
            for timeframe in result[symbol]:
                signals = result[symbol][timeframe]
                logger.info(f"   - Signal result type: {type(signals)}")
                if isinstance(signals, pd.Series):
                    logger.info(f"     - ✅ Signal is pandas Series (GOOD!)")
                    buy_count = (signals == 'BUY').sum()
                    logger.info(f"     - BUY signals: {buy_count}")
                else:
                    logger.info(f"     - ❌ Signal is string: {signals} (EXPECTED FAILURE)")
        
        return result
    
    built_strategy.generate_signals = debug_generate_signals
    return built_strategy

STRATEGY_PARAMETERS = {
    'sma_period': {
        'type': 'int', 
        'default': 20, 
        'min': 5, 
        'max': 50, 
        'description': 'SMA period (verified working parameter)'
    }
}

# DOCUMENTATION OF WHAT WORKS AND WHAT DOESN'T
"""
=================================================================
WORKING STRATEGY EXAMPLE - CURRENT STATUS
=================================================================

✅ CONFIRMED WORKING:
-------------------
1. GUI Strategy Detection
   - Files named Strategy_*.py are detected
   - STRATEGY_PARAMETERS dictionary is parsed correctly
   - Parameters appear in GUI with correct types

2. GUI Parameter Assignment
   - Parameters set in GUI are passed to create_strategy()
   - Custom parameter values work correctly

3. Symbol/Timeframe Assignment
   - GUI symbols (BTCUSDT) and timeframes (60m) are used correctly
   - Multiple symbols/timeframes would work

4. Data Loading
   - Data files are found and loaded correctly
   - Date range filtering works
   - Data has correct structure (timestamp, open, high, low, close, volume)

5. Manual Indicator Calculation
   - Indicator functions from indicators_library.py work
   - Manual calculation: sma(df['close'], period=20) returns valid Series

❌ CONFIRMED NOT WORKING:
-----------------------
1. StrategyBuilder Indicator Integration
   - Indicators are calculated but NOT added to DataFrame
   - Expected columns like 'working_sma' are missing
   - This breaks signal generation

2. Signal Function Integration
   - Signal functions receive wrong parameters
   - Error: "missing 1 required positional argument"
   - Functions don't get the indicator data they expect

3. Signal Output Format
   - Expected: pandas Series with 'BUY', 'SELL', 'HOLD'
   - Actual: Simple string 'HOLD'
   - Results in 0 trades in backtest

🎯 NEXT DEBUGGING STEPS:
---------------------
1. Fix StrategyBuilder._calculate_indicators() method
2. Fix signal function parameter passing
3. Fix signal output format handling

=================================================================
"""