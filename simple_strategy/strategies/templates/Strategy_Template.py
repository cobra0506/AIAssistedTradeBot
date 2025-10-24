"""
ULTIMATE STRATEGY TEMPLATE - Standardized Structure
This is the CORRECT pattern that all strategies should follow.
Combines the best of both approaches: Simple to use but powerful.
"""

import sys
import os
import logging
from typing import Dict, List, Any, Optional

# Add parent directories to path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, ema, macd
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: STRATEGY_PARAMETERS for GUI Configuration
# This dictionary defines what parameters the GUI will show and allow users to configure
STRATEGY_PARAMETERS = {
    'indicator_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 50,
        'description': 'Primary indicator period',
        'gui_hint': 'Standard values: 14 for RSI, 20/50 for SMAs'
    },
    'overbought_level': {
        'type': 'int', 
        'default': 70,
        'min': 60,
        'max': 90,
        'description': 'Overbought threshold for sell signals',
        'gui_hint': 'Higher values = more conservative sells'
    },
    'oversold_level': {
        'type': 'int',
        'default': 30,
        'min': 10,
        'max': 40,
        'description': 'Oversold threshold for buy signals',
        'gui_hint': 'Lower values = more conservative buys'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    CREATE STRATEGY FUNCTION - Required by GUI
    This function is called by the GUI to create strategy instances.
    
    Args:
        symbols: List of trading symbols (e.g., ['BTCUSDT'])
        timeframes: List of timeframes (e.g., ['1m', '5m'])
        **params: Strategy parameters from GUI/user input
    
    Returns:
        Built strategy instance ready for backtesting/trading
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
    indicator_period = params.get('indicator_period', 14)
    overbought_level = params.get('overbought_level', 70)
    oversold_level = params.get('oversold_level', 30)
    
    logger.info(f"🎯 Creating strategy with parameters:")
    logger.info(f"  - Symbols: {symbols}")
    logger.info(f"  - Timeframes: {timeframes}")
    logger.info(f"  - Indicator Period: {indicator_period}")
    logger.info(f"  - Overbought: {overbought_level}")
    logger.info(f"  - Oversold: {oversold_level}")
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add indicators (customize this section for your strategy)
        strategy_builder.add_indicator('rsi', rsi, period=indicator_period)
        strategy_builder.add_indicator('sma_fast', sma, period=indicator_period)
        strategy_builder.add_indicator('sma_slow', sma, period=indicator_period * 2)
        
        # Add signal rules (customize this section for your strategy)
        strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi',
                                       overbought=overbought_level,
                                       oversold=oversold_level)
        
        strategy_builder.add_signal_rule('ma_crossover', ma_crossover,
                                       fast_ma='sma_fast',
                                       slow_ma='sma_slow')
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('TemplateStrategy', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ Strategy created successfully!")
        logger.info(f"  - Name: {strategy.name}")
        logger.info(f"  - Symbols: {strategy.symbols}")
        logger.info(f"  - Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        import traceback
        traceback.print_exc()
        raise

class TemplateStrategy(StrategyBase):
    """
    OPTIONAL: Custom Strategy Class
    Only include this if you need custom logic beyond StrategyBuilder.
    For most strategies, the create_strategy function above is sufficient.
    """
    
    def __init__(self, symbols: List[str], timeframes: List[str], config: Dict[str, Any]):
        """
        Initialize the template strategy
        """
        super().__init__(
            name="TemplateStrategy",
            symbols=symbols,
            timeframes=timeframes,
            config=config
        )
        
        # Strategy-specific parameters
        self.indicator_period = config.get('indicator_period', 14)
        self.overbought_level = config.get('overbought_level', 70)
        self.oversold_level = config.get('oversold_level', 30)
        
        logger.info(f"🎯 TemplateStrategy initialized with custom parameters")