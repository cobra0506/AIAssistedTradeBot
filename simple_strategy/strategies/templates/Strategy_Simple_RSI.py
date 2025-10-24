"""
Simple RSI Strategy - Example Strategy
Uses RSI to identify overbought/oversold conditions for trading signals.
STANDARDIZED VERSION - Clean, consistent structure
"""
import sys
import os
import logging
from typing import Dict, List, Any

# Add parent directories to path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import rsi
from .signals_library import overbought_oversold

# Configure logging
logger = logging.getLogger(__name__)

# STRATEGY_PARAMETERS - GUI Configuration (AT TOP)
# This defines what parameters appear in the GUI for users to configure
STRATEGY_PARAMETERS = {
    'rsi_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 30,
        'description': 'RSI calculation period',
        'gui_hint': 'Standard values: 14, 21. Lower = more sensitive'
    },
    'overbought_level': {
        'type': 'int',
        'default': 70,
        'min': 60,
        'max': 90,
        'description': 'RSI overbought level (sell signal)',
        'gui_hint': 'Higher values = more conservative sell signals'
    },
    'oversold_level': {
        'type': 'int',
        'default': 30,
        'min': 10,
        'max': 40,
        'description': 'RSI oversold level (buy signal)',
        'gui_hint': 'Lower values = more conservative buy signals'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Simple RSI Strategy
    Uses RSI to identify overbought/oversold conditions for trading signals.
    
    Parameters:
    - symbols: List of trading symbols (default: ['BTCUSDT'])
    - timeframes: List of timeframes (default: ['1m'])
    - rsi_period: RSI calculation period (default: 14)
    - overbought_level: RSI overbought level (default: 70)
    - oversold_level: RSI oversold level (default: 30)
    """
    # DEBUG: Log what we receive
    logger.info(f"🔧 create_strategy called with:")
    logger.info(f"  - symbols: {symbols}")
    logger.info(f"  - timeframes: {timeframes}")
    logger.info(f"  - params: {params}")
    
    # Handle None/empty values with defaults
    if symbols is None or len(symbols) == 0:
        logger.warning("⚠️ No symbols provided, using default: ['BTCUSDT']")
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        logger.warning("⚠️ No timeframes provided, using default: ['1m']")
        timeframes = ['1m']
    
    # Get parameters with defaults from STRATEGY_PARAMETERS
    rsi_period = params.get('rsi_period', 14)
    overbought_level = params.get('overbought_level', 70)
    oversold_level = params.get('oversold_level', 30)
    
    logger.info(f"🎯 Creating Simple RSI strategy with parameters:")
    logger.info(f"  - Symbols: {symbols}")
    logger.info(f"  - Timeframes: {timeframes}")
    logger.info(f"  - RSI Period: {rsi_period}")
    logger.info(f"  - Overbought Level: {overbought_level}")
    logger.info(f"  - Oversold Level: {oversold_level}")
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add RSI indicator
        strategy_builder.add_indicator('rsi', rsi, period=rsi_period)
        
        # Add signal rule for RSI overbought/oversold
        strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi',
                                       overbought=overbought_level,
                                       oversold=oversold_level)
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('Simple_RSI', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ Simple RSI strategy created successfully!")
        logger.info(f"  - Strategy Name: {strategy.name}")
        logger.info(f"  - Strategy Symbols: {strategy.symbols}")
        logger.info(f"  - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ Error creating Simple RSI strategy: {e}")
        import traceback
        traceback.print_exc()
        raise

def simple_test():
    """Simple test to verify the strategy works"""
    try:
        # Test strategy creation
        strategy = create_strategy(
            symbols=['BTCUSDT'],
            timeframes=['1m'],
            rsi_period=14,
            overbought_level=70,
            oversold_level=30
        )
        
        print(f"✅ Simple RSI strategy created successfully: {strategy.name}")
        print(f"  - Symbols: {strategy.symbols}")
        print(f"  - Timeframes: {strategy.timeframes}")
        return True
    except Exception as e:
        print(f"❌ Error testing Simple RSI strategy: {e}")
        return False

# For testing
if __name__ == "__main__":
    simple_test()


'''"""
Simple RSI Strategy Template - Ready to Use
Based on Strategy_simple_RSI.py mentioned in your analysis
"""

import sys
import os
import logging
from typing import Dict, List, Any

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi
from simple_strategy.strategies.signals_library import overbought_oversold

logger = logging.getLogger(__name__)

# GUI Parameters
STRATEGY_PARAMETERS = {
    'rsi_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 30,
        'description': 'RSI calculation period'
    },
    'overbought': {
        'type': 'int',
        'default': 70,
        'min': 60,
        'max': 85,
        'description': 'RSI overbought level (sell signal)'
    },
    'oversold': {
        'type': 'int',
        'default': 30,
        'min': 15,
        'max': 40,
        'description': 'RSI oversold level (buy signal)'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """Create Simple RSI Strategy"""
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters
    rsi_period = params.get('rsi_period', 14)
    overbought = params.get('overbought', 70)
    oversold = params.get('oversold', 30)
    
    # Create strategy
    strategy_builder = StrategyBuilder(symbols, timeframes)
    strategy_builder.add_indicator('rsi', rsi, period=rsi_period)
    strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi',
                                   overbought=overbought,
                                   oversold=oversold)
    strategy_builder.set_signal_combination('majority_vote')
    strategy_builder.set_strategy_info('SimpleRSI', '1.0.0')
    
    return strategy_builder.build()'''