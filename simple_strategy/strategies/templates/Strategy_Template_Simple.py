"""
Simple Strategy Template - Copy this for basic strategies
This is the STANDARD starting point for all new strategies.
"""
import sys
import os
import logging
from typing import Dict, List, Any

# Add parent directories to path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder
from .indicators_library import rsi, sma, ema, macd  # Add what you need
from .signals_library import overbought_oversold, ma_crossover  # Add what you need

# Configure logging
logger = logging.getLogger(__name__)

# STRATEGY_PARAMETERS - GUI Configuration (AT TOP)
# This defines what parameters appear in the GUI for users to configure
# CUSTOMIZE THIS SECTION FOR YOUR STRATEGY
STRATEGY_PARAMETERS = {
    'your_parameter': {
        'type': 'int',  # 'int', 'str', 'float', 'bool'
        'default': 14,
        'min': 5,      # For numeric types
        'max': 30,     # For numeric types
        'options': [],  # For string types with choices
        'description': 'Your parameter description',
        'gui_hint': 'Additional help text for GUI users'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Your Strategy - Replace this description
    This function is called by the GUI to create strategy instances.
    
    Parameters:
    - symbols: List of trading symbols (default: ['BTCUSDT'])
    - timeframes: List of timeframes (default: ['1m'])
    - **params: Strategy parameters from GUI/user input
    """
    # DEBUG: Log what we receive (helpful for troubleshooting)
    logger.info(f"🔧 create_strategy called with:")
    logger.info(f"  - symbols: {symbols}")
    logger.info(f"  - timeframes: {timeframes}")
    logger.info(f"  - params: {params}")
    
    # CRITICAL: Handle None/empty values with sensible defaults
    if symbols is None or len(symbols) == 0:
        logger.warning("⚠️ No symbols provided, using default: ['BTCUSDT']")
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        logger.warning("⚠️ No timeframes provided, using default: ['1m']")
        timeframes = ['1m']
    
    # Get parameters with defaults from STRATEGY_PARAMETERS
    your_parameter = params.get('your_parameter', 14)
    
    logger.info(f"🎯 Creating strategy with parameters:")
    logger.info(f"  - Symbols: {symbols}")
    logger.info(f"  - Timeframes: {timeframes}")
    logger.info(f"  - Your Parameter: {your_parameter}")
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # CUSTOMIZE THIS SECTION: Add your indicators
        # Examples:
        # strategy_builder.add_indicator('rsi', rsi, period=your_parameter)
        # strategy_builder.add_indicator('sma_fast', sma, period=12)
        # strategy_builder.add_indicator('sma_slow', sma, period=26)
        
        # CUSTOMIZE THIS SECTION: Add your signal rules
        # Examples:
        # strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
        #                                indicator='rsi',
        #                                overbought=70,
        #                                oversold=30)
        # strategy_builder.add_signal_rule('ma_crossover', ma_crossover,
        #                                fast_ma='sma_fast',
        #                                slow_ma='sma_slow')
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information (CUSTOMIZE the name)
        strategy_builder.set_strategy_info('Your_Strategy_Name', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ Strategy created successfully!")
        logger.info(f"  - Strategy Name: {strategy.name}")
        logger.info(f"  - Strategy Symbols: {strategy.symbols}")
        logger.info(f"  - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        import traceback
        traceback.print_exc()
        raise

def simple_test():
    """Simple test to verify the strategy works"""
    try:
        # Test strategy creation with your parameters
        strategy = create_strategy(
            symbols=['BTCUSDT'],
            timeframes=['1m'],
            your_parameter=14  # Replace with your parameter
        )
        
        print(f"✅ Strategy created successfully: {strategy.name}")
        print(f"  - Symbols: {strategy.symbols}")
        print(f"  - Timeframes: {strategy.timeframes}")
        return True
    except Exception as e:
        print(f"❌ Error testing strategy: {e}")
        return False

# For testing - MUST EXIST
if __name__ == "__main__":
    simple_test()

